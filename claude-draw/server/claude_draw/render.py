"""Inspection views: what Claude looks at between drawing steps.

Borrowed from SketchAgent (MIT, Vinker et al.): give the model a labelled
coordinate grid so it can name exact locations instead of guessing from pixels.
Views are nearest-neighbour upscaled with a pixel grid, rulers in canvas
coordinates, and an optional reference shown side-by-side or underneath.
"""

from __future__ import annotations

import string
from dataclasses import dataclass
from functools import lru_cache
from typing import Literal

from PIL import Image, ImageDraw, ImageFont

from .canvas import Canvas, DrawError, to_hex

Region = tuple[int, int, int, int]
TARGET_PX = 640
RULER = 26
HEADER = 18
GAP = 12
MAP_CHARS = string.ascii_uppercase + string.ascii_lowercase + string.digits + "@$%&*+=?"


@lru_cache(maxsize=4)
def _font(size: int = 11) -> ImageFont.ImageFont | ImageFont.FreeTypeFont:
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # Pillow without FreeType
        return ImageFont.load_default()


@dataclass
class Reference:
    """A reference image mapped onto a box in canvas coordinates (floats)."""

    image: Image.Image
    source: str
    box: tuple[float, float, float, float]

    @classmethod
    def fit(cls, image: Image.Image, source: str, canvas: Canvas, mode: str = "contain",
            box: Region | None = None) -> "Reference":
        image = image.convert("RGBA")
        bx, by, bw, bh = box if box else (0, 0, canvas.width, canvas.height)
        if mode == "stretch":
            return cls(image, source, (bx, by, bw, bh))
        if mode != "contain":
            raise DrawError("fit must be 'contain' or 'stretch'")
        scale = min(bw / image.width, bh / image.height)
        w, h = image.width * scale, image.height * scale
        return cls(image, source, (bx + (bw - w) / 2, by + (bh - h) / 2, w, h))

    def in_view(self, region: Region, scale: int) -> Image.Image:
        """The reference as it lands inside `region`, rendered at `scale` display px per canvas px."""
        rx, ry, rw, rh = region
        out = Image.new("RGBA", (rw * scale, rh * scale), (0, 0, 0, 0))
        bx, by, bw, bh = self.box
        ix0, iy0 = max(rx, bx), max(ry, by)
        ix1, iy1 = min(rx + rw, bx + bw), min(ry + rh, by + bh)
        if ix1 <= ix0 or iy1 <= iy0:
            return out
        kx, ky = self.image.width / bw, self.image.height / bh
        W, H = self.image.size
        src = (max(0.0, (ix0 - bx) * kx), max(0.0, (iy0 - by) * ky),
               min(float(W), (ix1 - bx) * kx), min(float(H), (iy1 - by) * ky))
        dx0, dy0 = round((ix0 - rx) * scale), round((iy0 - ry) * scale)
        dw, dh = max(1, round((ix1 - rx) * scale) - dx0), max(1, round((iy1 - ry) * scale) - dy0)
        upscaling = dw >= (src[2] - src[0]) - 1e-9
        resample = Image.Resampling.NEAREST if upscaling else Image.Resampling.LANCZOS
        out.paste(self.image.resize((dw, dh), resample, box=src), (dx0, dy0))
        return out

    def sampled(self, canvas: Canvas) -> Image.Image:
        """Reference point-sampled at canvas pixel centres (what a 1:1 trace would look like)."""
        out = Image.new("RGBA", (canvas.width, canvas.height), (0, 0, 0, 0))
        bx, by, bw, bh = self.box
        src, dst = self.image.load(), out.load()
        for j in range(canvas.height):
            for i in range(canvas.width):
                u, v = (i + 0.5 - bx) / bw, (j + 0.5 - by) / bh
                if 0 <= u < 1 and 0 <= v < 1:
                    dst[i, j] = src[int(u * self.image.width), int(v * self.image.height)]
        return out


def clip_region(canvas: Canvas, region: Region | None) -> Region:
    if region is None:
        return (0, 0, canvas.width, canvas.height)
    x, y, w, h = region
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(canvas.width, x + w), min(canvas.height, y + h)
    if x1 <= x0 or y1 <= y0:
        raise DrawError(f"region {list(region)} does not overlap the {canvas.width}x{canvas.height} canvas")
    return (x0, y0, x1 - x0, y1 - y0)


def auto_scale(region: Region, panels: int = 1) -> int:
    _, _, w, h = region
    return max(1, min(48, (TARGET_PX // panels) // max(w, h)))


def _checker(size: tuple[int, int], cell: int) -> Image.Image:
    img = Image.new("RGBA", size, (236, 236, 236, 255))
    draw = ImageDraw.Draw(img)
    for y in range(0, size[1], cell):
        for x in range((y // cell) % 2 * cell, size[0], cell * 2):
            draw.rectangle([x, y, x + cell - 1, y + cell - 1], fill=(206, 206, 206, 255))
    return img


def _label_step(scale: int, max_coord: int) -> int:
    width = len(str(max_coord)) * 7 + 4
    for step in (1, 2, 4, 5, 8, 10, 16, 20, 25, 32, 50, 64, 100, 128):
        if step * scale >= width:
            return step
    return 256


def _panel(body: Image.Image, region: Region, scale: int, title: str, grid: bool,
           selection: Region | None = None) -> Image.Image:
    """Wrap a scaled body in a header and x/y rulers labelled in canvas coordinates."""
    rx, ry, rw, rh = region
    W, H = body.size
    if grid and scale >= 6:
        over = Image.new("RGBA", body.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(over)
        for i in range(rw + 1):
            major = (rx + i) % 8 == 0
            d.line([(i * scale, 0), (i * scale, H)], fill=(40, 40, 40, 130) if major else (90, 90, 90, 60))
        for j in range(rh + 1):
            major = (ry + j) % 8 == 0
            d.line([(0, j * scale), (W, j * scale)], fill=(40, 40, 40, 130) if major else (90, 90, 90, 60))
        body = Image.alpha_composite(body, over)
    if selection:
        sx, sy, sw, sh = selection
        x0, y0 = (sx - rx) * scale, (sy - ry) * scale
        d = ImageDraw.Draw(body)
        for k, color in ((0, (0, 190, 255, 255)), (1, (255, 255, 255, 255))):
            d.rectangle([x0 + k, y0 + k, x0 + sw * scale - 1 - k, y0 + sh * scale - 1 - k], outline=color)

    out = Image.new("RGBA", (W + RULER, H + RULER + HEADER), (250, 250, 250, 255))
    out.paste(body, (RULER, RULER + HEADER))
    d = ImageDraw.Draw(out)
    font = _font()
    d.text((4, 3), title, fill=(20, 20, 20, 255), font=font)
    step = _label_step(scale, max(rx + rw, ry + rh))
    for i in range(rw):
        x = rx + i
        if x % step == 0 or rw == 1:
            cx = RULER + i * scale + scale / 2
            d.text((cx, HEADER + RULER / 2), str(x), fill=(40, 40, 40, 255), font=font, anchor="mm")
    for j in range(rh):
        y = ry + j
        if y % step == 0 or rh == 1:
            cy = RULER + HEADER + j * scale + scale / 2
            d.text((RULER / 2, cy), str(y), fill=(40, 40, 40, 255), font=font, anchor="mm")
    d.rectangle([RULER - 1, RULER + HEADER - 1, RULER + W, RULER + HEADER + H], outline=(60, 60, 60, 255))
    return out


def _scaled(image: Image.Image, region: Region, scale: int) -> Image.Image:
    rx, ry, rw, rh = region
    crop = image.crop((rx, ry, rx + rw, ry + rh))
    return crop.resize((rw * scale, rh * scale), Image.Resampling.NEAREST)


def _hstack(panels: list[Image.Image]) -> Image.Image:
    width = sum(p.width for p in panels) + GAP * (len(panels) - 1)
    height = max(p.height for p in panels)
    out = Image.new("RGBA", (width, height), (250, 250, 250, 255))
    x = 0
    for p in panels:
        out.paste(p, (x, 0))
        x += p.width + GAP
    return out


View = Literal["canvas", "reference", "compare", "overlay"]


def render_view(canvas: Canvas, reference: Reference | None = None, *, view: View = "canvas",
                region: Region | None = None, scale: int | None = None, grid: bool = True,
                overlay_opacity: float = 0.6, caption: str = "") -> tuple[Image.Image, dict]:
    region = clip_region(canvas, region)
    if view != "canvas" and reference is None:
        raise DrawError(f"view {view!r} needs a reference; call load_reference first")
    panels = 2 if view == "compare" else 1
    scale = scale or auto_scale(region, panels)
    if not 1 <= scale <= 64:
        raise DrawError("scale must be 1..64")
    rx, ry, rw, rh = region
    size = (rw * scale, rh * scale)
    cell = max(4, scale // 2) if scale >= 8 else 8
    where = f"x {rx}..{rx + rw - 1}, y {ry}..{ry + rh - 1} @{scale}x"
    art = _scaled(canvas.composite(), region, scale)
    sel = canvas.selection if view in ("canvas", "overlay") else None

    def canvas_panel(title: str) -> Image.Image:
        return _panel(Image.alpha_composite(_checker(size, cell), art), region, scale, title, grid, sel)

    def reference_panel() -> Image.Image:
        body = Image.alpha_composite(_checker(size, cell), reference.in_view(region, scale))
        return _panel(body, region, scale, f"reference | {where}", grid)

    if view == "canvas":
        image = canvas_panel(f"canvas {canvas.width}x{canvas.height} | {where} {caption}".strip())
    elif view == "reference":
        image = reference_panel()
    elif view == "compare":
        image = _hstack([reference_panel(), canvas_panel(f"canvas | {where}")])
    elif view == "overlay":
        faded = art.copy()
        faded.putalpha(art.getchannel("A").point(lambda v: int(v * overlay_opacity)))
        body = Image.alpha_composite(_checker(size, cell), reference.in_view(region, scale))
        body = Image.alpha_composite(body, faded)
        image = _panel(body, region, scale, f"overlay (canvas {int(overlay_opacity * 100)}% over reference) | {where}",
                       grid, sel)
    else:
        raise DrawError("view must be canvas, reference, compare, or overlay")
    return image.convert("RGB"), {"region": list(region), "scale": scale, "view": view}


def text_map(image: Image.Image, region: Region, max_cells: int = 4096) -> str:
    """Exact per-pixel character map with a colour legend. Vision is lossy; this is not."""
    rx, ry, rw, rh = region
    if rw * rh > max_cells:
        raise DrawError(f"text map limited to {max_cells} pixels; pass a smaller region (e.g. 64x64 or less)")
    px = image.load()
    legend: dict[tuple, str] = {}
    rows = []
    for j in range(ry, ry + rh):
        row = []
        for i in range(rx, rx + rw):
            c = px[i, j]
            if c[3] == 0:
                row.append(".")
                continue
            if c not in legend:
                if len(legend) >= len(MAP_CHARS):
                    raise DrawError("too many distinct colors for a text map; use a smaller region")
                legend[c] = MAP_CHARS[len(legend)]
            row.append(legend[c])
        rows.append(row)
    width = max(len(str(ry + rh - 1)), 2)
    tens = " " * (width + 1) + "".join(str((rx + i) // 10 % 10) for i in range(rw))
    ones = " " * (width + 1) + "".join(str((rx + i) % 10) for i in range(rw))
    body = [f"{ry + j:>{width}} " + "".join(r) for j, r in enumerate(rows)]
    keys = ["  . = transparent"] + [f"  {ch} = {to_hex(c)}" for c, ch in legend.items()]
    return "\n".join([f"pixel map x {rx}..{rx + rw - 1}, y {ry}..{ry + rh - 1}", tens, ones, *body, "legend:", *keys])
