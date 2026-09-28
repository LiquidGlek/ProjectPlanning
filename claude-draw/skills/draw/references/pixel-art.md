# Pixel-art craft and self-review checklist

## Size and readability
- Pick the smallest canvas that holds the idea: 16x16 icons/items, 24x24-32x32 characters.
- Silhouette first: a sprite that is unreadable as a solid shape will not be fixed by detail.
- Judge readability at 1x-2x without grid (`inspect scale=2 grid=false`), not only zoomed in.
- Exaggerate: at 16px a head is often 40-50% of a character's height; eyes are 1-2px.

## Lines
- 1px outlines should be 8-connected with no **doubles**: a pixel that makes an L-corner
  (e.g. (5,3),(6,3),(6,4)) thickens the line; remove the corner pixel.
- **Jaggies**: step lengths along a curve should change monotonically (3,2,2,1,1 not 3,1,2,1,3).
  Uneven runs make curves look broken; fix with single-pixel moves.
- Straight 45-degree diagonals step 1:1; shallow lines use equal runs (2:1, 3:1).
- Close outlines fully before `fill`; a one-pixel gap floods the background.

## Color
- Limited palette: 3-5 hues, each a ramp of 2-4 values. Name them with `set_palette`
  (e.g. `red_dark`, `red`, `red_light`, `outline`).
- Hue-shift ramps: shadows cooler/more saturated, highlights warmer/lighter.
- Avoid near-duplicate colors; every color must earn its place.
- Selective outline (optional): outline pixels take a darker shade of the adjacent fill
  instead of pure black, especially on the lit side.

## Shading
- One light source (default top-left). Shadow on the opposite side and under overhangs.
- **Pillow shading** (dark ring around the edge, light center) is wrong - shade by form, not by outline.
- **Banding**: parallel stair-stepped rows of different tones that trace the outline read as noise; offset them.
- Keep noise low: isolated single pixels of a different tone ("orphans") are usually errors
  unless they are a deliberate highlight.
- Dithering sparingly, only for large gradients.

## Self-review checklist (use the words, give coordinates)
- Proportion: heights/widths vs reference, measured in pixels.
- Placement: features offset from reference by N px (which direction).
- Silhouette: missing or extra bumps, lost negative space (gaps between limbs, handle holes).
- Line quality: doubles, jaggies, gaps, orphan pixels.
- Color: wrong ramp, leaked fill, too many colors, low contrast between adjacent regions.
- Shading: inconsistent light direction, pillow shading, banding.
- Symmetry: intended symmetry broken (check with `pixel_map`), or unintended stiffness.

## Efficient correction
- Wrong last step -> `undo`.
- Right shape, wrong place -> `select` it and `move_selection` by dx/dy.
- Single wrong pixels -> `pixel` with the right color, or `erase`.
- Leaked fill -> `undo`, close the gap, fill again.
- Region repaint only when most of it is wrong; `select` it first so neighbours are protected.
