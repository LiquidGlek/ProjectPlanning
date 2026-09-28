# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp>=2.2,<3"]
# ///
"""Drive the claude-draw MCP server over stdio, the same way Claude Code does.

    uv run --script tests/mcp_call.py [--session ID] [--out DIR] TOOL 'JSON_ARGS' [TOOL 'JSON_ARGS' ...]

Each invocation starts a fresh server process; --session resumes a saved session
first (via open_session, i.e. trajectory replay). Returned images are written to
--out and their paths printed, so they can be viewed.
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
import os
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters

SERVER = Path(__file__).resolve().parents[1] / "server" / "claude_draw_server.py"


async def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--session")
    parser.add_argument("--out", default=os.environ.get("CLAUDE_DRAW_VIEWS", "views"))
    parser.add_argument("calls", nargs="+", help="TOOL JSON pairs")
    args = parser.parse_args()
    if len(args.calls) % 2:
        parser.error("calls must be TOOL 'JSON' pairs")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    params = StdioServerParameters(command="uv", args=["run", "--quiet", "--script", str(SERVER)],
                                   env={**os.environ})
    calls = [(args.calls[i], json.loads(args.calls[i + 1])) for i in range(0, len(args.calls), 2)]
    if args.session:
        calls.insert(0, ("open_session", {"session_id": args.session}))
    failed = 0
    async with Client(params) as client:
        for n, (tool, arguments) in enumerate(calls):
            result = await client.call_tool(tool, arguments)
            print(f"=== {tool} {'ERROR' if result.is_error else 'ok'}")
            failed += bool(result.is_error)
            for k, block in enumerate(result.content):
                if block.type == "text":
                    print(block.text)
                elif block.type == "image":
                    existing = len(list(out.glob("*.png")))
                    path = out / f"{existing:04d}-{tool}.png"
                    path.write_bytes(base64.b64decode(block.data))
                    print(f"[image] {path}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
