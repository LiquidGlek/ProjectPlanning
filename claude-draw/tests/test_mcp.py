# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp>=2.2,<3", "pillow>=10.1"]
# ///
"""End-to-end MCP test: spawns the server over stdio exactly as Claude Code does.

    uv run --script tests/test_mcp.py
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path

from mcp import Client, StdioServerParameters

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "server" / "claude_draw_server.py"
EXPECTED_TOOLS = {"new_canvas", "load_reference", "set_palette", "draw", "inspect", "undo", "redo", "layers",
                  "export_png", "status", "list_sessions", "open_session"}


def check(cond: bool, what: str) -> None:
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        raise SystemExit(1)


def text(result) -> str:
    return "\n".join(b.text for b in result.content if b.type == "text")


def images(result) -> int:
    return sum(b.type == "image" for b in result.content)


def pixels(n: int, y: int) -> dict:
    return {"op": "pixel", "points": [[n % 16, y]], "color": "#ff0000", "label": f"p{n}"}


async def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        env = {**os.environ, "CLAUDE_DRAW_HOME": f"{tmp}/home", "CLAUDE_DRAW_PROJECT_DIR": str(ROOT)}
        params = StdioServerParameters(command="uv", args=["run", "--quiet", "--script", str(SERVER)], env=env)
        async with Client(params) as client:
            tools = {t.name for t in (await client.list_tools()).tools}
            check(EXPECTED_TOOLS <= tools, f"tools exposed: {sorted(tools)}")
            draw_schema = json.dumps([t for t in (await client.list_tools()).tools if t.name == "draw"][0].input_schema)
            check('"maxItems": 10' in draw_schema, "draw caps a batch at 10 actions in its schema")

            r = await client.call_tool("new_canvas", {"name": "t", "width": 16, "height": 16})
            check(not r.is_error and images(r) == 1, "new_canvas returns a render")
            r = await client.call_tool("load_reference", {"path": "examples/reference/mushroom_ref.png"})
            check(not r.is_error and "dominant colors: #d62d3a" in text(r), "load_reference maps + reports colors")

            r = await client.call_tool("draw", {"intent": "too many", "actions": [pixels(i, 0) for i in range(11)]})
            check(r.is_error, "11 actions in one call is rejected")
            for batch in range(2):
                r = await client.call_tool("draw", {"intent": f"b{batch}",
                                                    "actions": [pixels(i, batch) for i in range(10)]})
                check(not r.is_error and images(r) == 1, f"batch {batch} of 10 applied with a render")
            r = await client.call_tool("draw", {"intent": "blind", "actions": [pixels(0, 5)]})
            check(r.is_error and "inspect(view='compare')" in text(r), "21st action blocked until a compare")
            r = await client.call_tool("inspect", {"view": "compare", "region": [0, 0, 8, 8], "pixel_map": True})
            check(not r.is_error and images(r) == 1 and "legend:" in text(r), "compare + zoom + pixel map")
            r = await client.call_tool("draw", {"intent": "after look", "actions": [pixels(0, 5)]})
            check(not r.is_error, "drawing resumes after the compare")

            r = await client.call_tool("draw", {"intent": "bad", "actions": [
                {"op": "pixel", "points": [[1, 9]], "color": "#00ff00"}, {"op": "fill", "x": 99, "y": 0, "color": "#000"}]})
            check(r.is_error and "Nothing was applied" in text(r), "invalid batch rejected atomically")
            r = await client.call_tool("inspect", {"region": [1, 9, 1, 1], "pixel_map": True})
            check(" 9 ." in text(r), "first action of the rejected batch was rolled back")

            r = await client.call_tool("undo", {"steps": 1})
            check("undid 1" in text(r), "undo")
            r = await client.call_tool("export_png", {"path": f"{tmp}/out.png", "scale": 2})
            check(not r.is_error and Path(f"{tmp}/out.png").exists(), "export_png writes a file")
            status = text(await client.call_tool("status", {}))
            session_id = status.split()[1]

        async with Client(params) as client:
            r = await client.call_tool("open_session", {"session_id": session_id})
            check(not r.is_error and "replay matches" in text(r), "resume in a new process reproduces the canvas")

        events = [json.loads(line)["event"] for line in
                  (Path(tmp) / "home" / "sessions" / session_id / "trajectory.jsonl").read_text().splitlines()]
        check(events.count("rejected") == 2 and "export" in events and events[-1] == "resume",
              f"trajectory records rejections, export and resume ({len(events)} events)")
    print("all MCP checks passed")


if __name__ == "__main__":
    asyncio.run(main())
    sys.exit(0)
