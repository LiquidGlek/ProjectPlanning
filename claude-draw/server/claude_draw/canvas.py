"""Deterministic layered raster canvas.

Every mutation is a plain JSON-able ``action`` dict so the same code path serves
live tool calls, undo/redo, and trajectory replay. Pixel operations write exact
RGBA values (no anti-aliasing, no blending) so results are reproducible
bit-for-bit and easy to reason about for pixel art.

Coordinates are integer pixels, origin at the top-left, x to the right, y down.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any, Iterable

from PIL import Image, ImageChops

RGBA = tuple[int, int, int, int]
TRANSPARENT: RGBA = (0, 0, 0, 0)
_HEX_RE = re.compile(r"^#?([0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")


class DrawError(ValueError):
    """A user-facing error: bad arguments or an impossible operation."""


def parse_color(value: Any, palette: dict[str, str] | None = None, _depth: int = 0) -> RGBA:
    """Accept '#rgb', '#rgba', '#rrggbb', '#rrggbbaa', [r,g,b(,a)], 'transparent', or a palette name."""
    if isinstance(value, (list, tuple)):
        if len(value) not in (3, 4) or not all(isinstance(v, int) and 0 <= v <= 255 for v in value):
            raise DrawError(f"color list must be 3 or 4 ints in 0..255, got {value!r}")
        return (value[0], value[1], value[2], value[3] if len(value) == 4 else 255)
    if not isinstance(value, str) or not value.strip():
        raise DrawError(f"invalid color {value!r}")
    text = value.strip()
    if text.lower() in ("transparent", "none", "clear"):
        return TRANSPARENT
    if palette and text in palette and _depth < 4:
        return parse_color(palette[text], palette, _depth + 1)
    match = _HEX_RE.match(text)
    if not match:
        known = ", ".join(sorted(palette)) if palette else "none defined"
        raise DrawError(f"unknown color {value!r} (use #rrggbb, #rrggbbaa, or a palette name; palette: {known})")
    digits = match.group(1)
    if len(digits) in (3, 4):
        digits = "".join(ch * 2 for ch in digits)
    if len(digits) == 6:
        digits += "ff"
    return tuple(int(digits[i : i + 2], 16) for i in range(0, 8, 2))  # type: ignore[return-value]


def to_hex(color: RGBA) -> str:
    r, g, b, a = color
    return f"#{r:02x}{g:02x}{b:02x}" + ("" if a == 255 else f"{a:02x}")


@dataclass
class Layer:
    name: str
    image: Image.Image
    visible: bool = True
    opacity: float = 1.0

    def copy(self) -> "Layer":
        return Layer(self.name, self.image.copy(), self.visible, self.opacity)


@dataclass
class Canvas:
    width: int
    height: int
    layers: list[Layer] = field(default_factory=list)
    active: int = 0
    selection: tuple[int, int, int, int] | None = None
    palette: dict[str, str] = field(default_factory=dict)

    @classmethod
    def new(cls, width: int, height: int, background: Any = "transparent") -> "Canvas":
        if not (1 <= width <= 1024 and 1 <= height <= 1024):
            raise DrawError("canvas width and height must be between 1 and 1024")
        bg = parse_color(background)
        name = "background" if bg[3] else "layer 1"
        return cls(width, height, [Layer(name, Image.new("RGBA", (width, height), bg))])

    # ---------------------------------------------------------------- state
    def snapshot(self) -> "Canvas":
        return Canvas(
            self.width,
            self.height,
            [layer.copy() for layer in self.layers],
            self.active,
            self.selection,
            dict(self.palette),
        )

    def restore(self, snap: "Canvas") -> None:
        fresh = snap.snapshot()
        self.layers, self.active = fresh.layers, fresh.active
        self.selection, self.palette = fresh.selection, fresh.palette

    def composite(self) -> Image.Image:
        out = Image.new("RGBA", (self.width, self.height), TRANSPARENT)
        for layer in self.layers:
            if not layer.visible or layer.opacity <= 0:
                continue
            img = layer.image
            if layer.opacity < 1:
                alpha = img.getchannel("A").point(lambda v, o=layer.opacity: int(round(v * o)))
                img = img.copy()
                img.putalpha(alpha)
            out.alpha_composite(img)
        return out

    def digest(self) -> str:
        return hashlib.sha256(self.composite().tobytes()).hexdigest()[:16]

    @property
    def layer(self) -> Layer:
        return self.layers[self.active]

    def describe(self) -> dict[str, Any]:
        return {
            "size": [self.width, self.height],
            "layers": [
                {"name": l.name, "visible": l.visible, "opacity": l.opacity, "active": i == self.active}
                for i, l in enumerate(self.layers)
            ],
            "selection": list(self.selection) if self.selection else None,
            "palette": dict(self.palette),
        }

    # ------------------------------------------------------------- dispatch
    def apply(self, action: dict[str, Any]) -> dict[str, Any]:
        """Apply one action. Returns a report: changed pixel count, bbox, warnings."""
        op = action.get("op")
        handler = _OPS.get(op)  # type: ignore[arg-type]
        if handler is None:
            raise DrawError(f"unknown op {op!r}; valid ops: {', '.join(sorted(_OPS))}")
        structural = op.startswith("layer.")
        before = self.composite() if structural else self.layer.image.copy()
        ctx = _Ctx(self)
        handler(self, action, ctx)
        changed, bbox = _diff(before, self.composite() if structural else self.layer.image)
        report: dict[str, Any] = {"op": op}
        if action.get("label"):
            report["label"] = action["label"]
        report["changed_pixels"] = changed
        if bbox:
            report["changed_bbox"] = [bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1]]
        if ctx.out_of_bounds:
            ctx.warnings.append(f"{ctx.out_of_bounds} pixel(s) fell outside the canvas and were skipped")
        if ctx.clipped:
            ctx.warnings.append(f"{ctx.clipped} pixel(s) outside the active selection were protected")
        if ctx.warnings:
            report["warnings"] = ctx.warnings
        if ctx.info:
            report.update(ctx.info)
        return report


def _diff(a: Image.Image, b: Image.Image) -> tuple[int, tuple[int, int, int, int] | None]:
    diff = ImageChops.difference(a, b)
    r, g, bl, al = diff.split()
    mask = ImageChops.lighter(ImageChops.lighter(r, g), ImageChops.lighter(bl, al))
    bbox = mask.getbbox()
    if not bbox:
        return 0, None
    return a.width * a.height - mask.histogram()[0], bbox


class _Ctx:
    """Per-action pixel writer that honours canvas bounds and the active selection."""

    def __init__(self, canvas: Canvas, clip: bool = True):
        self.canvas = canvas
        self.px = canvas.layer.image.load()
        self.sel = canvas.selection if clip else None
        self.out_of_bounds = 0
        self.clipped = 0
        self.warnings: list[str] = []
        self.info: dict[str, Any] = {}

    def put(self, x: int, y: int, color: RGBA) -> None:
        c = self.canvas
        if not (0 <= x < c.width and 0 <= y < c.height):
            self.out_of_bounds += 1
            return
        if self.sel:
            sx, sy, sw, sh = self.sel
            if not (sx <= x < sx + sw and sy <= y < sy + sh):
                self.clipped += 1
                return
        self.px[x, y] = color

    def stamp(self, x: int, y: int, color: RGBA, width: int) -> None:
        if width <= 1:
            self.put(x, y, color)
            return
        off = (width - 1) // 2
        for dy in range(width):
            for dx in range(width):
                self.put(x - off + dx, y - off + dy, color)


# ------------------------------------------------------------------ helpers
def _color(canvas: Canvas, action: dict[str, Any], key: str = "color") -> RGBA:
    if key not in action:
        raise DrawError(f"op {action.get('op')!r} requires '{key}'")
    return parse_color(action[key], canvas.palette)


def _points(action: dict[str, Any], minimum: int = 1) -> list[tuple[int, int]]:
    pts = action.get("points")
    if not isinstance(pts, list) or len(pts) < minimum:
        raise DrawError(f"op {action.get('op')!r} requires 'points' with at least {minimum} [x, y] pair(s)")
    out = []
    for p in pts:
        if not (isinstance(p, (list, tuple)) and len(p) == 2 and all(isinstance(v, int) for v in p)):
            raise DrawError(f"each point must be [x, y] integers, got {p!r}")
        out.append((p[0], p[1]))
    return out


def _rect(action: dict[str, Any]) -> tuple[int, int, int, int]:
    try:
        x, y, w, h = (int(action[k]) for k in ("x", "y", "w", "h"))
    except KeyError as exc:
        raise DrawError(f"op {action.get('op')!r} requires x, y, w, h") from exc
    if w < 1 or h < 1:
        raise DrawError("w and h must be >= 1")
    return x, y, w, h


def bresenham(x0: int, y0: int, x1: int, y1: int) -> Iterable[tuple[int, int]]:
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err = dx + dy
    while True:
        yield x0, y0
        if x0 == x1 and y0 == y1:
            return
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def ellipse_pixels(x: int, y: int, w: int, h: int, filled: bool) -> list[tuple[int, int]]:
    """Pixels whose centres lie inside the ellipse inscribed in the w*h box; outline is 8-connected."""
    cx, cy, rx, ry = x + w / 2, y + h / 2, w / 2, h / 2

    def inside(i: int, j: int) -> bool:
        return ((i + 0.5 - cx) / rx) ** 2 + ((j + 0.5 - cy) / ry) ** 2 <= 1.0

    cells = [(i, j) for j in range(y, y + h) for i in range(x, x + w) if inside(i, j)]
    if filled:
        return cells
    return [
        (i, j)
        for i, j in cells
        if not (inside(i - 1, j) and inside(i + 1, j) and inside(i, j - 1) and inside(i, j + 1))
    ]


# ----------------------------------------------------------------- drawing
def _op_pixel(c: Canvas, a: dict[str, Any], ctx: _Ctx) -> None:
    color = _color(c, a)
    for x, y in _points(a):
        ctx.put(x, y, color)


def _op_line(c: Canvas, a: dict[str, Any], ctx: _Ctx) -> None:
    color = _color(c, a)
    pts = _points(a, 2)
    if a.get("closed"):
        pts.append(pts[0])
    width = int(a.get("width", 1))
    if not 1 <= width <= 32:
        raise DrawError("line width must be 1..32")
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        for x, y in bresenham(x0, y0, x1, y1):
            ctx.stamp(x, y, color, width)


def _op_rect(c: Canvas, a: dict[str, Any], ctx: _Ctx) -> None:
    color = _color(c, a)
    x, y, w, h = _rect(a)
    for j in range(y, y + h):
        for i in range(x, x + w):
            if a.get("filled") or i in (x, x + w - 1) or j in (y, y + h - 1):
                ctx.put(i, j, color)


def _op_ellipse(c: Canvas, a: dict[str, Any], ctx: _Ctx) -> None:
    color = _color(c, a)
    x, y, w, h = _rect(a)
    for i, j in ellipse_pixels(x, y, w, h, bool(a.get("filled"))):
        ctx.put(i, j, color)


def _op_fill(c: Canvas, a: dict[str, Any], ctx: _Ctx) -> None:
    color = _color(c, a)
    x, y = int(a["x"]), int(a["y"])
    if not (0 <= x < c.width and 0 <= y < c.height):
        raise DrawError(f"fill seed ({x}, {y}) is outside the canvas")
    # sample_all: find the region on the visible composite (line art on another layer), paint the active layer
    px = c.composite().load() if a.get("sample_all") else ctx.px
    target = px[x, y]
    if target == color and not a.get("sample_all"):
        ctx.warnings.append("seed pixel already has the fill color; nothing changed")
        return
    if a.get("contiguous", True) is False:
        for j in range(c.height):
            for i in range(c.width):
                if px[i, j] == target:
                    ctx.put(i, j, color)
        return
    stack, seen, region = [(x, y)], {(x, y)}, 0
    while stack:
        i, j = stack.pop()
        if px[i, j] != target:
            continue
        region += 1
        ctx.put(i, j, color)
        for n in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
            if 0 <= n[0] < c.width and 0 <= n[1] < c.height and n not in seen:
                seen.add(n)
                stack.append(n)
    ctx.info["filled_region_pixels"] = region


def _op_erase(c: Canvas, a: dict[str, Any], ctx: _Ctx) -> None:
    if "points" in a and a["points"] is not None:
        for x, y in _points(a):
            ctx.put(x, y, TRANSPARENT)
    elif all(k in a and a[k] is not None for k in ("x", "y", "w", "h")):
        x, y, w, h = _rect(a)
        for j in range(y, y + h):
            for i in range(x, x + w):
                ctx.put(i, j, TRANSPARENT)
    else:
        raise DrawError("erase needs either 'points' or a rect 'x, y, w, h'")


# --------------------------------------------------------------- selection
def _op_select(c: Canvas, a: dict[str, Any], ctx: _Ctx) -> None:
    x, y, w, h = _rect(a)
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(c.width, x + w), min(c.height, y + h)
    if x1 <= x0 or y1 <= y0:
        raise DrawError("selection does not overlap the canvas")
    c.selection = (x0, y0, x1 - x0, y1 - y0)
    ctx.info["selection"] = list(c.selection)


def _op_deselect(c: Canvas, a: dict[str, Any], ctx: _Ctx) -> None:
    c.selection = None


def _require_selection(c: Canvas) -> tuple[int, int, int, int]:
    if not c.selection:
        raise DrawError("no active selection; use op 'select' first")
    return c.selection


def _op_move_selection(c: Canvas, a: dict[str, Any], ctx: _Ctx) -> None:
    x, y, w, h = _require_selection(c)
    dx, dy = int(a.get("dx", 0)), int(a.get("dy", 0))
    img = c.layer.image
    piece = img.crop((x, y, x + w, y + h))
    if not a.get("duplicate"):
        img.paste(Image.new("RGBA", (w, h), TRANSPARENT), (x, y))
    layer = Image.new("RGBA", img.size, TRANSPARENT)
    layer.paste(piece, (x + dx, y + dy))
    img.alpha_composite(layer)
    nx0, ny0 = max(0, x + dx), max(0, y + dy)
    nx1, ny1 = min(c.width, x + dx + w), min(c.height, y + dy + h)
    c.selection = (nx0, ny0, nx1 - nx0, ny1 - ny0) if nx1 > nx0 and ny1 > ny0 else None
    ctx.info["selection"] = list(c.selection) if c.selection else None


def _op_flip_selection(c: Canvas, a: dict[str, Any], ctx: _Ctx) -> None:
    x, y, w, h = _require_selection(c)
    axis = a.get("axis", "horizontal")
    if axis not in ("horizontal", "vertical"):
        raise DrawError("axis must be 'horizontal' (mirror left-right) or 'vertical' (mirror top-bottom)")
    img = c.layer.image
    piece = img.crop((x, y, x + w, y + h))
    flip = Image.Transpose.FLIP_LEFT_RIGHT if axis == "horizontal" else Image.Transpose.FLIP_TOP_BOTTOM
    img.paste(piece.transpose(flip), (x, y))


# ------------------------------------------------------------------ layers
def _find_layer(c: Canvas, name: Any) -> int:
    if name is None:
        return c.active
    for i, layer in enumerate(c.layers):
        if layer.name == name:
            return i
    raise DrawError(f"no layer named {name!r}; layers: {[l.name for l in c.layers]}")


def _op_layer_add(c: Canvas, a: dict[str, Any], ctx: _Ctx) -> None:
    name = a.get("name") or f"layer {len(c.layers) + 1}"
    if any(l.name == name for l in c.layers):
        raise DrawError(f"layer {name!r} already exists")
    c.layers.insert(c.active + 1, Layer(name, Image.new("RGBA", (c.width, c.height), TRANSPARENT)))
    c.active += 1


def _op_layer_select(c: Canvas, a: dict[str, Any], ctx: _Ctx) -> None:
    c.active = _find_layer(c, a.get("name"))


def _op_layer_update(c: Canvas, a: dict[str, Any], ctx: _Ctx) -> None:
    layer = c.layers[_find_layer(c, a.get("name"))]
    if a.get("new_name"):
        if any(l.name == a["new_name"] for l in c.layers if l is not layer):
            raise DrawError(f"layer {a['new_name']!r} already exists")
        layer.name = a["new_name"]
    if a.get("visible") is not None:
        layer.visible = bool(a["visible"])
    if a.get("opacity") is not None:
        opacity = float(a["opacity"])
        if not 0 <= opacity <= 1:
            raise DrawError("opacity must be 0..1")
        layer.opacity = opacity


def _op_layer_delete(c: Canvas, a: dict[str, Any], ctx: _Ctx) -> None:
    if len(c.layers) == 1:
        raise DrawError("cannot delete the only layer")
    idx = _find_layer(c, a.get("name"))
    del c.layers[idx]
    c.active = min(max(0, c.active - (1 if idx <= c.active else 0)), len(c.layers) - 1)


def _op_layer_move(c: Canvas, a: dict[str, Any], ctx: _Ctx) -> None:
    idx = _find_layer(c, a.get("name"))
    target = idx + (1 if a.get("direction", "up") == "up" else -1)
    if not 0 <= target < len(c.layers):
        raise DrawError("layer is already at that end of the stack")
    active_layer = c.layer
    c.layers[idx], c.layers[target] = c.layers[target], c.layers[idx]
    c.active = c.layers.index(active_layer)


def _op_layer_merge_down(c: Canvas, a: dict[str, Any], ctx: _Ctx) -> None:
    idx = _find_layer(c, a.get("name"))
    if idx == 0:
        raise DrawError("bottom layer has nothing to merge into")
    upper, lower = c.layers[idx], c.layers[idx - 1]
    if upper.visible:
        tmp = Canvas(c.width, c.height, [upper.copy()])
        lower.image.alpha_composite(tmp.composite())
    del c.layers[idx]
    c.active = idx - 1


def _op_palette(c: Canvas, a: dict[str, Any], ctx: _Ctx) -> None:
    colors = a.get("colors") or {}
    if not isinstance(colors, dict):
        raise DrawError("palette 'colors' must be an object of name -> color")
    if a.get("replace"):
        c.palette = {}
    for name, value in colors.items():
        if _HEX_RE.match(name):
            raise DrawError(f"palette name {name!r} looks like a hex color; use a word")
        c.palette[name] = to_hex(parse_color(value, c.palette))


_OPS = {
    "pixel": _op_pixel,
    "line": _op_line,
    "rect": _op_rect,
    "ellipse": _op_ellipse,
    "fill": _op_fill,
    "erase": _op_erase,
    "select": _op_select,
    "deselect": _op_deselect,
    "move_selection": _op_move_selection,
    "flip_selection": _op_flip_selection,
    "layer.add": _op_layer_add,
    "layer.select": _op_layer_select,
    "layer.update": _op_layer_update,
    "layer.delete": _op_layer_delete,
    "layer.move": _op_layer_move,
    "layer.merge_down": _op_layer_merge_down,
    "palette": _op_palette,
}

DRAW_OPS = tuple(k for k in _OPS if not k.startswith("layer.") and k != "palette")


class History:
    """Per-action undo/redo using whole-canvas snapshots (cheap at sprite sizes)."""

    def __init__(self, limit: int = 200):
        self.limit = limit
        self.undo_stack: list[Canvas] = []
        self.redo_stack: list[Canvas] = []

    def record(self, canvas: Canvas) -> None:
        self.undo_stack.append(canvas.snapshot())
        if len(self.undo_stack) > self.limit:
            self.undo_stack.pop(0)
        self.redo_stack.clear()

    def undo(self, canvas: Canvas, steps: int) -> int:
        done = 0
        while done < steps and self.undo_stack:
            self.redo_stack.append(canvas.snapshot())
            canvas.restore(self.undo_stack.pop())
            done += 1
        return done

    def redo(self, canvas: Canvas, steps: int) -> int:
        done = 0
        while done < steps and self.redo_stack:
            self.undo_stack.append(canvas.snapshot())
            canvas.restore(self.redo_stack.pop())
            done += 1
        return done
