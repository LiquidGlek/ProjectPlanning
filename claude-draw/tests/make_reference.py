# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow>=10.1"]
# ///
"""Generate the synthetic test reference (a smooth 240x240 cartoon mushroom).

This is only an *input* for forward tests: a hi-res, anti-aliased illustration
the drawing agent must translate into a low-res sprite by hand.
    uv run --script tests/make_reference.py examples/reference/mushroom_ref.png
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw

S = 4  # supersample
W = 240
OUT, CAP, CAP_DARK, SPOT, STEM, STEM_SHADE, GILL, EYE = (
    "#2b1b2e", "#d62d3a", "#9e1b32", "#fdf6e3", "#f1dcb5", "#c9a77c", "#e8b98a", "#2b1b2e")


def main(path: str) -> None:
    img = Image.new("RGBA", (W * S, W * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = lambda *v: [int(x * S) for x in v]  # noqa: E731
    # stem
    d.rounded_rectangle(s(80, 108, 160, 222), radius=26 * S, fill=OUT)
    d.rounded_rectangle(s(86, 108, 154, 216), radius=22 * S, fill=STEM)
    d.rounded_rectangle(s(134, 114, 154, 214), radius=10 * S, fill=STEM_SHADE)
    d.ellipse(s(100, 146, 112, 168), fill=EYE)
    d.ellipse(s(128, 146, 140, 168), fill=EYE)
    # cap underside (gills), then the dome over it
    d.ellipse(s(26, 96, 214, 140), fill=OUT)
    d.ellipse(s(32, 101, 208, 134), fill=GILL)
    d.pieslice(s(18, 16, 222, 220), 180, 360, fill=OUT)
    d.pieslice(s(25, 23, 215, 213), 180, 360, fill=CAP_DARK)
    d.pieslice(s(25, 23, 197, 213), 180, 360, fill=CAP)
    d.rectangle(s(18, 114, 222, 120), fill=OUT)
    for box in ((58, 50, 90, 76), (104, 34, 132, 56), (146, 60, 176, 88), (36, 90, 56, 108)):
        d.ellipse(s(*box), fill=SPOT)
    img = img.resize((W, W), Image.Resampling.LANCZOS)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "mushroom_ref.png")
