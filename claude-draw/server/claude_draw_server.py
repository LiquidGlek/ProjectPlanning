# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp>=2.2,<3", "pillow>=10.1"]
# ///
"""claude-draw MCP server: explicit, inspectable drawing actions on a local canvas.

No image generation of any kind. Claude places pixels, lines, shapes and fills,
and every mutating call returns a rendered view so the next step is informed by
what is actually on the canvas.
"""

from __future__ import annotations

import os
import sys
from io import BytesIO
from pathlib import Path
from typing import Annotated, Any, Literal, Union

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mcp.server.mcpserver import Image as McpImage  # noqa: E402
from mcp.server.mcpserver import MCPServer  # noqa: E402
from mcp.server.mcpserver.exceptions import ToolError  # noqa: E402
from PIL import Image  # noqa: E402
from pydantic import BaseModel, ConfigDict, Field  # noqa: E402

from claude_draw import __version__  # noqa: E402
from claude_draw.canvas import DrawError, to_hex  # noqa: E402
from claude_draw.render import render_view, text_map  # noqa: E402
from claude_draw.session import Session, _slug, default_home, resolve_path  # noqa: E402

MAX_ACTIONS = int(os.environ.get("CLAUDE_DRAW_MAX_ACTIONS", "10"))
MAX_POINTS = 64
COMPARE_EVERY = int(os.environ.get("CLAUDE_DRAW_COMPARE_EVERY", "20"))

INSTRUCTIONS = f"""\
claude-draw is a manual drawing canvas. You draw with explicit actions; nothing is generated.
Loop: inspect reference + canvas -> at most {MAX_ACTIONS} actions per `draw` call -> read the returned
render -> name concrete errors (with coordinates) -> fix them surgically (erase/undo/small edits) -> continue.
Coordinates are integer pixels, origin top-left, x right, y down; rulers on every view show them.
With a reference loaded, `draw` refuses to go past {COMPARE_EVERY} actions without inspect(view='compare'|'overlay').
Use pixel_map=true on `inspect` for exact pixel values; vision on upscaled renders can mislead.
Prefer small targeted edits over redrawing; everything is logged to a replayable trajectory."""

mcp = MCPServer("claude-draw", instructions=INSTRUCTIONS, version=__version__)
HOME = default_home()
STATE: dict[str, Session | None] = {"session": None}

# ----------------------------------------------------------------- schemas
Point = Annotated[list[int], Field(min_length=2, max_length=2, description="[x, y] in canvas pixels")]
Color = Annotated[str, Field(description="'#rrggbb', '#rrggbbaa', a palette name, or 'transparent'")]
Label = Annotated[str | None, Field(description="Which part of the artwork this action draws, e.g. 'hat brim outline'")]


class _Action(BaseModel):
    model_config = ConfigDict(extra="forbid")
    label: Label = None


class PixelAction(_Action):
    """Set individual pixels to one color."""
    op: Literal["pixel"]
    points: Annotated[list[Point], Field(min_length=1, max_length=MAX_POINTS)]
    color: Color


class LineAction(_Action):
    """1px (or square-brush) Bresenham polyline through the points."""
    op: Literal["line"]
    points: Annotated[list[Point], Field(min_length=2, max_length=MAX_POINTS)]
    color: Color
    closed: bool = False
    width: Annotated[int, Field(ge=1, le=8)] = 1


class RectAction(_Action):
    """Axis-aligned rectangle with top-left (x, y) and size w x h; outline unless filled."""
    op: Literal["rect"]
    x: int
    y: int
    w: Annotated[int, Field(ge=1)]
    h: Annotated[int, Field(ge=1)]
    color: Color
    filled: bool = False


class EllipseAction(_Action):
    """Ellipse inscribed in the box (x, y, w, h); clean 1px outline unless filled."""
    op: Literal["ellipse"]
    x: int
    y: int
    w: Annotated[int, Field(ge=1)]
    h: Annotated[int, Field(ge=1)]
    color: Color
    filled: bool = False


class FillAction(_Action):
    """Flood fill (4-connected, exact color match) from (x, y), painting the active layer.
    contiguous=false replaces that color everywhere instead. sample_all=true uses all visible layers as the boundary."""
    op: Literal["fill"]
    x: int
    y: int
    color: Color
    contiguous: bool = True
    sample_all: bool = Field(False, description="detect the region from all visible layers (fill a color layer "
                             "beneath separate line art) instead of the active layer only")


class EraseAction(_Action):
    """Make pixels transparent: either a list of points or a rect x, y, w, h."""
    op: Literal["erase"]
    points: Annotated[list[Point] | None, Field(max_length=MAX_POINTS)] = None
    x: int | None = None
    y: int | None = None
    w: int | None = None
    h: int | None = None


class SelectAction(_Action):
    """Select a rectangle. While a selection exists, painting ops only affect pixels inside it."""
    op: Literal["select"]
    x: int
    y: int
    w: Annotated[int, Field(ge=1)]
    h: Annotated[int, Field(ge=1)]


class DeselectAction(_Action):
    """Clear the selection."""
    op: Literal["deselect"]


class MoveSelectionAction(_Action):
    """Move (or copy) the selected pixels of the active layer by dx, dy; the selection follows."""
    op: Literal["move_selection"]
    dx: int = 0
    dy: int = 0
    duplicate: bool = Field(False, description="keep the original pixels in place (copy instead of move)")


class FlipSelectionAction(_Action):
    """Mirror the selected pixels in place: 'horizontal' = left/right, 'vertical' = top/bottom."""
    op: Literal["flip_selection"]
    axis: Literal["horizontal", "vertical"] = "horizontal"


Action = Annotated[
    Union[PixelAction, LineAction, RectAction, EllipseAction, FillAction, EraseAction, SelectAction,
          DeselectAction, MoveSelectionAction, FlipSelectionAction],
    Field(discriminator="op"),
]
Region = Annotated[list[int] | None, Field(min_length=4, max_length=4, description="[x, y, w, h] crop in canvas pixels")]
View = Literal["canvas", "reference", "compare", "overlay"]


# ----------------------------------------------------------------- helpers
def _session() -> Session:
    session = STATE["session"]
    if session is None:
        raise ToolError("no open canvas: call new_canvas (or open_session) first")
    return session


def _png(img: Image.Image) -> McpImage:
    buf = BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return McpImage(data=buf.getvalue(), format="png")


def _view(session: Session, *, view: View = "canvas", region: list[int] | None = None, scale: int | None = None,
          grid: bool = True, overlay_opacity: float = 0.6, caption: str = "") -> tuple[Image.Image, dict]:
    try:
        return render_view(session.canvas, session.reference, view=view, region=tuple(region) if region else None,
                           scale=scale, grid=grid, overlay_opacity=overlay_opacity, caption=caption)
    except DrawError as exc:
        raise ToolError(str(exc)) from exc


def _footer(session: Session) -> str:
    c = session.canvas
    sel = f" | selection {list(c.selection)}" if c.selection else ""
    return (f"layer '{c.layer.name}' ({c.active + 1}/{len(c.layers)}){sel} | undo {len(session.history.undo_stack)}"
            f" / redo {len(session.history.redo_stack)} | sha {c.digest()} | session {session.id}")


def _describe_report(i: int, r: dict[str, Any]) -> str:
    parts = [f"  [{i}] {r['op']}"]
    if r.get("label"):
        parts.append(f"'{r['label']}'")
    parts.append(f"changed {r['changed_pixels']} px")
    if r.get("changed_bbox"):
        parts.append(f"bbox {r['changed_bbox']}")
    for key in ("filled_region_pixels", "selection"):
        if key in r:
            parts.append(f"{key}={r[key]}")
    for w in r.get("warnings", []):
        parts.append(f"WARNING: {w}")
    return " ".join(parts)


def _dominant_colors(img: Image.Image, limit: int = 12, min_distance: float = 40.0) -> list[str]:
    """Most frequent opaque colors, skipping near-duplicates (anti-aliasing blends, noise)."""
    raw = img.convert("RGBA").tobytes()
    counts: dict[tuple[int, int, int], int] = {}
    for i in range(0, len(raw), 4):
        if raw[i + 3] >= 128:
            key = (raw[i], raw[i + 1], raw[i + 2])
            counts[key] = counts.get(key, 0) + 1
    chosen: list[tuple[int, int, int]] = []
    for rgb, _ in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
        if all(sum((a - b) ** 2 for a, b in zip(rgb, c)) >= min_distance ** 2 for c in chosen):
            chosen.append(rgb)
            if len(chosen) == limit:
                break
    return [to_hex((*rgb, 255)) for rgb in chosen]


def _commit(session: Session, actions: list[dict[str, Any]], intent: str, tool: str,
            region: list[int] | None = None) -> list[Any]:
    counted = tool == "draw"
    if counted and session.reference is not None and session.actions_since_compare + len(actions) > COMPARE_EVERY:
        message = (f"{session.actions_since_compare} drawing actions since the last reference comparison "
                   f"(limit {COMPARE_EVERY}). Run inspect(view='compare') or inspect(view='overlay'), name the "
                   "differences you see, then continue. Nothing was applied.")
        session.log("rejected", {"tool": tool, "intent": intent, "actions": actions, "error": message})
        raise ToolError(message)
    try:
        reports = session.run_actions(actions)
    except DrawError as exc:
        session.log("rejected", {"tool": tool, "intent": intent, "actions": actions, "error": str(exc)})
        raise ToolError(f"{exc}. Nothing was applied (batches are atomic).") from exc
    if counted:
        session.actions_since_compare += len(actions)
    img, meta = _view(session, region=region)
    session.log("actions", {"tool": tool, "intent": intent, "actions": actions, "reports": reports, "view_meta": meta},
                frame=True, view=img)
    lines = [f"applied {len(actions)} action(s): {intent}"]
    lines += [_describe_report(i, r) for i, r in enumerate(reports)]
    if counted and session.reference is not None and session.actions_since_compare > COMPARE_EVERY // 2:
        lines.append(f"NOTE: {session.actions_since_compare}/{COMPARE_EVERY} drawing actions since the last "
                     "reference comparison; inspect(view='compare') is required at the limit.")
    lines.append(_footer(session))
    lines.append("Now look at the render: list concrete errors (with coordinates) before the next draw call.")
    return ["\n".join(lines), _png(img)]


# ------------------------------------------------------------------- tools
@mcp.tool(structured_output=False)
def new_canvas(name: str, width: int, height: int, background: Color = "transparent",
               palette: dict[str, str] | None = None) -> list[Any]:
    """Start a new drawing session with a native-resolution canvas (e.g. 16x16, 32x32 for sprites).
    Optionally define named palette colors, e.g. {"outline": "#1a1c2c", "skin": "#f4b41b"}."""
    try:
        session = Session.create(HOME, name, width, height, background)
    except DrawError as exc:
        raise ToolError(str(exc)) from exc
    STATE["session"] = session
    if palette:
        _commit(session, [{"op": "palette", "colors": palette}], "define palette", "new_canvas")
    img, _ = _view(session)
    session.log("view", {"tool": "new_canvas"}, view=img)
    return [f"new {width}x{height} canvas '{name}'\nsession dir: {session.dir}\n{_footer(session)}", _png(img)]


@mcp.tool(structured_output=False)
def load_reference(path: str, fit: Literal["contain", "stretch"] = "contain", box: Region = None) -> list[Any]:
    """Load a reference image (PNG/JPEG/GIF/WebP) and map it onto the canvas (whole canvas by default, or `box`).
    Returns the reference as it maps onto canvas coordinates plus its dominant colors."""
    session = _session()
    source = resolve_path(path)
    if not source.is_file():
        raise ToolError(f"reference not found: {source}")
    try:
        stored = session.store_reference(source)
        ref = session.set_reference(stored, str(path), fit, box)
    except (OSError, DrawError) as exc:
        raise ToolError(f"could not load reference: {exc}") from exc
    colors = _dominant_colors(ref.image)
    img, _ = _view(session, view="reference")
    session.log("load_reference", {"source": str(path), "stored": str(stored.relative_to(session.dir)), "fit": fit,
                                   "box": box, "size": list(ref.image.size), "colors": colors}, view=img)
    bx, by, bw, bh = ref.box
    text = (f"reference {ref.image.width}x{ref.image.height} mapped to canvas box "
            f"x={bx:.1f} y={by:.1f} w={bw:.1f} h={bh:.1f}\n"
            f"dominant colors: {', '.join(colors) or 'none'}\n"
            "Plan composition and proportions from this view before drawing.")
    return [text, _png(img)]


@mcp.tool(structured_output=False)
def set_palette(colors: dict[str, str], replace: bool = False) -> list[Any]:
    """Define or update named colors usable anywhere a color is accepted (e.g. "outline", "shadow")."""
    return _commit(_session(), [{"op": "palette", "colors": colors, "replace": replace}], "set palette", "set_palette")


DRAW_DESCRIPTION = f"""Apply up to {MAX_ACTIONS} explicit drawing actions to the active layer, then return a render.
Ops: pixel, line, rect, ellipse, fill, erase, select, deselect, move_selection, flip_selection.
The batch is atomic (all or nothing); each action is one undo step. Give every action a `label`.
`region` [x,y,w,h] returns a zoomed render of that area instead of the whole canvas.
After it returns, look at the render and name concrete errors before drawing more."""


@mcp.tool(description=DRAW_DESCRIPTION, structured_output=False)
def draw(actions: Annotated[list[Action], Field(min_length=1, max_length=MAX_ACTIONS)],
         intent: Annotated[str, Field(description="What these actions should achieve, e.g. 'block in helmet silhouette'")],
         region: Region = None) -> list[Any]:
    payload = [a.model_dump(exclude_none=True) for a in actions]
    return _commit(_session(), payload, intent, "draw", region)


@mcp.tool(structured_output=False)
def inspect(view: View = "canvas", region: Region = None, scale: Annotated[int | None, Field(ge=1, le=64)] = None,
            grid: bool = True, pixel_map: bool = False, overlay_opacity: float = 0.6) -> list[Any]:
    """Look at the work. view: 'canvas', 'reference', 'compare' (reference | canvas side by side),
    or 'overlay' (canvas at overlay_opacity over the reference). `region` [x,y,w,h] zooms/crops.
    pixel_map=true adds an exact character map of the canvas pixels in the region (with hex legend)."""
    session = _session()
    img, meta = _view(session, view=view, region=region, scale=scale, grid=grid, overlay_opacity=overlay_opacity)
    out: list[Any] = [f"{view} view region={meta['region']} scale={meta['scale']}x\n{_footer(session)}"]
    if pixel_map:
        try:
            source = session.reference.sampled(session.canvas) if view == "reference" else session.canvas.composite()
            out.append(text_map(source, tuple(meta["region"])))
        except DrawError as exc:
            raise ToolError(str(exc)) from exc
    if view in ("compare", "overlay"):
        session.actions_since_compare = 0
    session.log("inspect", {"view": view, "region": meta["region"], "scale": meta["scale"], "pixel_map": pixel_map},
                view=img)
    out.append(_png(img))
    return out


@mcp.tool(structured_output=False)
def undo(steps: Annotated[int, Field(ge=1, le=50)] = 1) -> list[Any]:
    """Undo the last `steps` actions (each drawing action is one step)."""
    session = _session()
    done = session.history.undo(session.canvas, steps)
    img, _ = _view(session)
    session.log("undo", {"steps": done}, frame=True, view=img)
    return [f"undid {done} action(s)\n{_footer(session)}", _png(img)]


@mcp.tool(structured_output=False)
def redo(steps: Annotated[int, Field(ge=1, le=50)] = 1) -> list[Any]:
    """Redo actions previously undone."""
    session = _session()
    done = session.history.redo(session.canvas, steps)
    img, _ = _view(session)
    session.log("redo", {"steps": done}, frame=True, view=img)
    return [f"redid {done} action(s)\n{_footer(session)}", _png(img)]


@mcp.tool(structured_output=False)
def layers(action: Literal["list", "add", "select", "update", "delete", "move", "merge_down"] = "list",
           name: str | None = None, new_name: str | None = None, visible: bool | None = None,
           opacity: Annotated[float | None, Field(ge=0, le=1)] = None,
           direction: Literal["up", "down"] = "up") -> list[Any]:
    """Manage layers. add (new empty layer above the active one, becomes active), select, update
    (rename/visible/opacity), delete, move (up/down in the stack), merge_down. `name` defaults to the active layer."""
    session = _session()
    if action == "list":
        rows = [f"  {i}: {l['name']}{' (active)' if l['active'] else ''} visible={l['visible']} opacity={l['opacity']}"
                for i, l in enumerate(session.canvas.describe()["layers"])]
        return ["layers (bottom to top):\n" + "\n".join(rows)]
    fields = {"name": name, "new_name": new_name, "visible": visible, "opacity": opacity,
              "direction": direction if action == "move" else None}
    op = {"op": f"layer.{action}", **{k: v for k, v in fields.items() if v is not None}}
    return _commit(session, [op], f"layers: {action}", "layers")


@mcp.tool(structured_output=False)
def export_png(path: str | None = None, scale: Annotated[int, Field(ge=1, le=32)] = 1,
               layer: str | None = None) -> list[Any]:
    """Export the visible composite (or a single named layer) as PNG, optionally nearest-neighbour upscaled.
    Default path: <session dir>/exports/<name>.png. Relative paths resolve against the project directory."""
    session = _session()
    c = session.canvas
    if layer is not None:
        match = [l for l in c.layers if l.name == layer]
        if not match:
            raise ToolError(f"no layer named {layer!r}")
        img = match[0].image.copy()
    else:
        img = c.composite()
    if scale > 1:
        img = img.resize((c.width * scale, c.height * scale), Image.Resampling.NEAREST)
    target = resolve_path(path) if path else session.dir / "exports" / f"{_slug(session.name)}.png"
    target.parent.mkdir(parents=True, exist_ok=True)
    img.save(target)
    session.log("export", {"path": str(target), "scale": scale, "layer": layer, "canvas_sha": c.digest()})
    return [f"exported {img.width}x{img.height} PNG to {target}\ntrajectory: {session.dir / 'trajectory.jsonl'}"]


@mcp.tool(structured_output=False)
def status() -> str:
    """Canvas size, layers, palette, selection, history depth, reference, and session paths."""
    session = _session()
    d = session.canvas.describe()
    ref = session.reference
    lines = [
        f"session {session.id} ('{session.name}') at {session.dir}",
        f"canvas {d['size'][0]}x{d['size'][1]} | {_footer(session)}",
        "layers: " + ", ".join(f"{l['name']}{'*' if l['active'] else ''}" for l in d["layers"]),
        "palette: " + (", ".join(f"{k}={v}" for k, v in d["palette"].items()) or "(none)"),
        f"reference: {ref.source} {ref.image.width}x{ref.image.height}" if ref else "reference: (none)",
        f"trajectory events: {session.seq}",
    ]
    return "\n".join(lines)


@mcp.tool(structured_output=False)
def list_sessions() -> str:
    """List saved drawing sessions (id, name, size, event count)."""
    rows = Session.list(HOME)
    if not rows:
        return f"no sessions under {HOME / 'sessions'}"
    return "\n".join(f"{r['id']}  '{r['name']}' {r['size'][0]}x{r['size'][1]} events={r['events']}" for r in rows)


@mcp.tool(structured_output=False)
def open_session(session_id: str) -> list[Any]:
    """Resume a saved session by replaying its trajectory (verifies the replay reproduces the logged canvas)."""
    try:
        session, check = Session.open(HOME, session_id)
    except DrawError as exc:
        raise ToolError(str(exc)) from exc
    STATE["session"] = session
    img, _ = _view(session)
    verdict = "replay matches" if check["deterministic"] else "WARNING: replay differs from logged canvas"
    return [f"resumed {session_id}: {check['events']} events, {verdict}\n{_footer(session)}", _png(img)]


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
