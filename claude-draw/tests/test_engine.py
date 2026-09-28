# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow>=10.1"]
# ///
"""Engine tests: uv run --script tests/test_engine.py"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "server"))

from PIL import Image  # noqa: E402

from claude_draw.canvas import Canvas, DrawError, parse_color  # noqa: E402
from claude_draw.render import Reference, render_view, text_map  # noqa: E402
from claude_draw.session import Session  # noqa: E402

RED, BLUE, T = (255, 0, 0, 255), (0, 0, 255, 255), (0, 0, 0, 0)


def px(c: Canvas, x: int, y: int):
    return c.composite().getpixel((x, y))


class ColorTests(unittest.TestCase):
    def test_formats(self):
        self.assertEqual(parse_color("#f00"), RED)
        self.assertEqual(parse_color("ff0000"), RED)
        self.assertEqual(parse_color("#ff000080"), (255, 0, 0, 128))
        self.assertEqual(parse_color([0, 0, 255]), BLUE)
        self.assertEqual(parse_color("transparent"), T)
        self.assertEqual(parse_color("ink", {"ink": "#00f"}), BLUE)
        with self.assertRaises(DrawError):
            parse_color("reddish")


class DrawingTests(unittest.TestCase):
    def setUp(self):
        self.c = Canvas.new(16, 16)

    def test_line_endpoints_and_diagonal(self):
        r = self.c.apply({"op": "line", "points": [[0, 0], [5, 5]], "color": "#f00"})
        self.assertEqual(r["changed_pixels"], 6)
        self.assertEqual(r["changed_bbox"], [0, 0, 6, 6])
        self.assertEqual(px(self.c, 5, 5), RED)

    def test_rect_outline_vs_filled(self):
        self.assertEqual(self.c.apply({"op": "rect", "x": 1, "y": 1, "w": 4, "h": 3, "color": "#f00"})["changed_pixels"], 10)
        self.assertEqual(self.c.apply({"op": "rect", "x": 1, "y": 1, "w": 4, "h": 3, "color": "#f00",
                                       "filled": True})["changed_pixels"], 2)

    def test_ellipse_is_symmetric(self):
        self.c.apply({"op": "ellipse", "x": 2, "y": 3, "w": 11, "h": 9, "color": "#f00"})
        img = self.c.composite()
        for y in range(3, 12):  # box spans x 2..12, y 3..11
            for x in range(2, 13):
                self.assertEqual(img.getpixel((x, y)), img.getpixel((14 - x, y)))
                self.assertEqual(img.getpixel((x, y)), img.getpixel((x, 14 - y)))
        self.assertEqual(img.getpixel((7, 3)), RED)  # top centre
        self.assertEqual(img.getpixel((7, 7)), T)  # hollow

    def test_fill_contiguous_and_global(self):
        self.c.apply({"op": "rect", "x": 0, "y": 0, "w": 8, "h": 8, "color": "#f00"})
        r = self.c.apply({"op": "fill", "x": 3, "y": 3, "color": "#00f"})
        self.assertEqual(r["changed_pixels"], 36)
        self.assertEqual(px(self.c, 10, 10), T)
        r = self.c.apply({"op": "fill", "x": 0, "y": 0, "color": "#0f0", "contiguous": False})
        self.assertEqual(r["changed_pixels"], 28)

    def test_fill_sample_all_uses_other_layers_as_boundary(self):
        self.c.apply({"op": "rect", "x": 0, "y": 0, "w": 6, "h": 6, "color": "#f00"})
        self.c.apply({"op": "layer.add", "name": "color"})
        r = self.c.apply({"op": "fill", "x": 2, "y": 2, "color": "#00f", "sample_all": True})
        self.assertEqual((r["changed_pixels"], r["filled_region_pixels"]), (16, 16))
        self.assertEqual(self.c.layers[0].image.getpixel((2, 2)), T)  # line layer untouched
        r = self.c.apply({"op": "fill", "x": 10, "y": 10, "color": "#0f0"})  # layer-only: floods the empty layer
        self.assertEqual(r["filled_region_pixels"], 256 - 16)

    def test_selection_protects_outside(self):
        self.c.apply({"op": "select", "x": 0, "y": 0, "w": 4, "h": 4})
        r = self.c.apply({"op": "line", "points": [[0, 2], [15, 2]], "color": "#f00"})
        self.assertEqual(r["changed_pixels"], 4)
        self.assertTrue(any("protected" in w for w in r["warnings"]))

    def test_move_copy_and_flip_selection(self):
        self.c.apply({"op": "pixel", "points": [[0, 0]], "color": "#f00"})
        self.c.apply({"op": "select", "x": 0, "y": 0, "w": 2, "h": 1})
        self.c.apply({"op": "flip_selection", "axis": "horizontal"})
        self.assertEqual((px(self.c, 0, 0), px(self.c, 1, 0)), (T, RED))
        self.c.apply({"op": "move_selection", "dx": 4, "dy": 2, "duplicate": True})
        self.assertEqual((px(self.c, 1, 0), px(self.c, 5, 2)), (RED, RED))
        self.assertEqual(self.c.selection, (4, 2, 2, 1))
        self.c.apply({"op": "move_selection", "dx": 0, "dy": 1})
        self.assertEqual((px(self.c, 5, 2), px(self.c, 5, 3)), (T, RED))

    def test_erase(self):
        self.c.apply({"op": "rect", "x": 0, "y": 0, "w": 4, "h": 4, "color": "#f00", "filled": True})
        self.assertEqual(self.c.apply({"op": "erase", "x": 1, "y": 1, "w": 2, "h": 2})["changed_pixels"], 4)
        self.assertEqual(self.c.apply({"op": "erase", "points": [[0, 0]]})["changed_pixels"], 1)

    def test_layers_composite_and_opacity(self):
        self.c.apply({"op": "pixel", "points": [[0, 0]], "color": "#f00"})
        self.c.apply({"op": "layer.add", "name": "top"})
        self.c.apply({"op": "pixel", "points": [[0, 0]], "color": "#00f"})
        self.assertEqual(px(self.c, 0, 0), BLUE)
        self.c.apply({"op": "layer.update", "name": "top", "visible": False})
        self.assertEqual(px(self.c, 0, 0), RED)
        self.c.apply({"op": "layer.update", "name": "top", "visible": True, "opacity": 0.5})
        r, g, b, a = px(self.c, 0, 0)
        self.assertTrue(120 <= r <= 135 and 120 <= b <= 135 and a == 255)
        self.c.apply({"op": "layer.merge_down", "name": "top"})
        self.assertEqual(len(self.c.layers), 1)


class SessionTests(unittest.TestCase):
    def test_atomic_batch_undo_redo_and_replay(self):
        with tempfile.TemporaryDirectory() as home:
            s = Session.create(Path(home), "test", 8, 8, "transparent")
            s.run_actions([{"op": "pixel", "points": [[1, 1]], "color": "#f00"},
                           {"op": "line", "points": [[0, 7], [7, 7]], "color": "#00f"}])
            s.log("actions", {"actions": [{"op": "pixel", "points": [[1, 1]], "color": "#f00"},
                                          {"op": "line", "points": [[0, 7], [7, 7]], "color": "#00f"}]}, frame=True)
            before = s.canvas.digest()
            with self.assertRaises(DrawError):
                s.run_actions([{"op": "pixel", "points": [[2, 2]], "color": "#0f0"},
                               {"op": "fill", "x": 50, "y": 0, "color": "#0f0"}])
            self.assertEqual(s.canvas.digest(), before)
            self.assertEqual(len(s.history.undo_stack), 2)
            s.history.undo(s.canvas, 1)
            s.log("undo", {"steps": 1}, frame=True)
            self.assertEqual(px(s.canvas, 3, 7), T)
            reopened, check = Session.open(Path(home), s.id)
            self.assertTrue(check["deterministic"], check)
            self.assertEqual(reopened.canvas.digest(), s.canvas.digest())
            events = [json.loads(l)["event"] for l in (s.dir / "trajectory.jsonl").read_text().splitlines()]
            self.assertEqual(events, ["new_canvas", "actions", "undo", "resume"])


class RenderTests(unittest.TestCase):
    def test_views_and_text_map(self):
        c = Canvas.new(16, 16)
        c.apply({"op": "rect", "x": 0, "y": 0, "w": 16, "h": 16, "color": "#f00"})
        ref = Reference.fit(Image.new("RGBA", (64, 32), BLUE), "mem", c)
        self.assertEqual(ref.box, (0, 4.0, 16, 8.0))
        for view in ("canvas", "reference", "compare", "overlay"):
            img, meta = render_view(c, ref, view=view, region=(4, 4, 8, 8))
            self.assertEqual(meta["region"], [4, 4, 8, 8])
            self.assertGreater(img.width, 8 * meta["scale"])
        a, _ = render_view(c, ref, view="compare")
        b, _ = render_view(c, ref, view="compare")
        self.assertEqual(a.tobytes(), b.tobytes())
        self.assertEqual(ref.sampled(c).getpixel((5, 5)), BLUE)
        self.assertEqual(ref.sampled(c).getpixel((5, 1)), T)
        m = text_map(c.composite(), (0, 0, 3, 2))
        self.assertIn(" 0 AAA", m)
        self.assertIn(" 1 A..", m)
        self.assertIn("A = #ff0000", m)


if __name__ == "__main__":
    unittest.main(verbosity=1)
