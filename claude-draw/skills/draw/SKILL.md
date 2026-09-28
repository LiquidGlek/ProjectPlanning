---
name: draw
description: Draw game artwork by hand with the claude-draw canvas tools - pixel-art sprites, icons and tiles built from explicit pixels, lines, shapes and fills, inspected every few actions and corrected surgically. Use when the user asks to draw, sprite, pixel, sketch or recreate artwork (optionally from a reference image) without image-generation models.
argument-hint: "[subject] [WxH] [reference-path]"
allowed-tools: mcp__plugin_claude-draw_canvas__*
---

# Drawing by hand with claude-draw

You are the artist. Every mark is an explicit action you choose after looking at the canvas.
Never use image generation, and never write code that computes the artwork for you.

Request: $ARGUMENTS

## The loop (always)

1. **Look** - `inspect` the reference and the current canvas (`view="compare"`).
2. **Decide** one small goal: one part, or one fix.
3. **Act** - one `draw` call, 5-10 meaningful actions max, every action with a `label`, the call with an `intent`.
4. **Check** the returned render. Write down specific errors with coordinates, e.g.
   "left ear tip at (4,2) is 1px too high vs reference", "stray pixel (9,11)", "outline gap at (12,7)-(12,8)".
   Confirm each report's `changed_bbox` is where you meant to draw; if not, `undo`.
5. **Correct** surgically, then continue. Say "no errors found" only after actually checking.

Rules:
- Never queue actions you have not seen the result of. One `draw` call, then look.
- Preserve correct work. Fix with the smallest edit: `undo` a bad last step; `pixel`/`erase` single
  pixels; `select` + `move_selection` to shift a part that is right but misplaced. Do not redraw areas that are correct.
- Protect finished areas: an active `select` rectangle blocks painting outside it.
- Every stage change: `inspect view="compare"` at full canvas, then zoom (`region=[x,y,w,h]`) on problem
  areas. Use `view="overlay"` to check alignment. With a reference loaded the server refuses `draw`
  after 20 actions without a compare/overlay inspect.
- Upscaled renders can mislead; before claiming an exact position, colour or stray pixel, check with
  `inspect pixel_map=true` on a small region.

## Stages

Do them in order. End each with a short review against the reference: what passes, what to fix.
Do not start a stage while the previous one still has known errors.

1. **Composition** - pick the canvas size (16x16, 24x24, 32x32 typical), facing, where the mass sits,
   a 1px margin, a consistent ground line. `new_canvas`, `load_reference`, `set_palette` (4-12 named colors).
2. **Construction** - `layers add "construction"`: block big masses with light rect/ellipse/line in a
   neutral color. Keep it rough.
3. **Proportion review** - measure against the reference with the rulers: overall height/width, head vs
   body, limb lengths, feature positions. Fix construction now; it is cheapest here.
4. **Silhouette** - `layers add "line"`: outer contour in the outline color. Check it reads at small size:
   `inspect scale=2 grid=false`.
5. **Internal forms** - inner lines that separate parts (arm over torso, brim over face).
6. **Cleanup** - hide or delete the construction layer; remove jaggies (uneven line steps), doubles
   (L-shaped corners in 1px lines), orphan pixels. `pixel_map=true` on suspicious regions.
7. **Color** - `layers add "color"`, then `layers move direction=down` so it sits under the line layer.
   Flat base colors with `fill` + `sample_all: true` (the outline on the other layer bounds the region).
   Check `filled_region_pixels`: a huge number means it leaked through an outline gap - undo, close the gap.
8. **Shading** - one light direction (default top-left); 1-2 shadow tones and 1 highlight per material.
9. **Details** - eyes, highlights, accents, optional selective outline.
10. **Final review** - `inspect view="compare"`, `inspect scale=1 grid=false` and `scale=4 grid=false`;
    fix what you find; then `export_png` (scale 1, plus an upscaled preview) and report the paths and
    the trajectory file to the user.

Pixel-art essentials (full guide: [references/pixel-art.md](references/pixel-art.md), read it if you can):
- 1px lines are 8-connected with no doubles (L-shaped corner pixels) and monotone step lengths on curves.
- Close outlines before filling. One light direction. No pillow shading, no banding, no orphan pixels.
- Limited palette: a few hues, 2-4 values each; name them with `set_palette`.
- At 16-32px, exaggerate key features and keep 1px of negative space between features and outlines.

Without a reference, draw from a written plan: state the subject's proportions in pixels first, and
review each stage against that plan instead of `compare`.

## Tool quick reference

| Tool | Use |
|---|---|
| `new_canvas(name, width, height, background?, palette?)` | start a session |
| `load_reference(path, fit?, box?)` | map a reference onto the canvas; returns dominant colors |
| `set_palette(colors)` | named colors, usable anywhere a color is accepted |
| `draw(actions, intent, region?)` | <=10 actions: `pixel`, `line`, `rect`, `ellipse`, `fill`, `erase`, `select`, `deselect`, `move_selection`, `flip_selection` |
| `inspect(view, region?, scale?, grid?, pixel_map?)` | views: `canvas`, `reference`, `compare`, `overlay` |
| `undo(steps)` / `redo(steps)` | one step per action |
| `layers(action, name?, ...)` | `list`, `add`, `select`, `update`, `delete`, `move`, `merge_down` |
| `export_png(path?, scale?, layer?)` | write PNG; trajectory is saved automatically |
| `status`, `list_sessions`, `open_session` | session info and resume |

Coordinates: integer pixels, origin top-left, x right, y down; `rect`/`ellipse`/`select` take `x, y, w, h`.
Symmetric subjects: draw one half, then `select` it, `move_selection` with `duplicate: true`, and
`flip_selection` - then fix the centre column by hand.
