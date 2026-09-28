"""Drawing sessions: canvas + history + reference, persisted as a replayable trajectory.

Layout of one session directory::

    <home>/sessions/<id>/
        trajectory.jsonl   one JSON event per line (the training-data record)
        frames/NNNNN.png   native-resolution canvas after every mutating event
        views/NNNNN.png    the exact inspection image returned to the model
        references/        copies of loaded reference images
        exports/           exported PNGs (default location)

The canvas is fully determined by replaying ``new_canvas``, ``load_reference``,
``actions``, ``undo`` and ``redo`` events, which is how sessions are resumed.
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image

from .canvas import Canvas, DrawError, History
from .render import Reference

REPLAYED = ("new_canvas", "load_reference", "actions", "undo", "redo")


def default_home() -> Path:
    env = os.environ.get("CLAUDE_DRAW_HOME", "")
    if env and "${" not in env:
        return Path(env).expanduser()
    return project_dir() / ".claude-draw"


def project_dir() -> Path:
    env = os.environ.get("CLAUDE_DRAW_PROJECT_DIR", "")
    if env and "${" not in env:
        return Path(env).expanduser()
    return Path.cwd()


def resolve_path(path: str) -> Path:
    p = Path(path).expanduser()
    return p if p.is_absolute() else project_dir() / p


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:40] or "drawing"


class Session:
    def __init__(self, directory: Path, name: str, canvas: Canvas):
        self.dir = directory
        self.id = directory.name
        self.name = name
        self.canvas = canvas
        self.history = History()
        self.reference: Reference | None = None
        self.seq = 0
        self.actions_since_compare = 0
        self._recording = True

    # ------------------------------------------------------------ creation
    @classmethod
    def create(cls, home: Path, name: str, width: int, height: int, background: str) -> "Session":
        canvas = Canvas.new(width, height, background)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        base = home / "sessions" / f"{_slug(name)}-{stamp}"
        directory, n = base, 1
        while directory.exists():
            n += 1
            directory = base.with_name(f"{base.name}-{n}")
        for sub in ("frames", "views", "references", "exports"):
            (directory / sub).mkdir(parents=True, exist_ok=True)
        session = cls(directory, name, canvas)
        session.log("new_canvas", {"name": name, "width": width, "height": height, "background": background},
                    frame=True)
        return session

    @classmethod
    def open(cls, home: Path, session_id: str) -> tuple["Session", dict[str, Any]]:
        directory = home / "sessions" / session_id
        path = directory / "trajectory.jsonl"
        if not path.exists():
            raise DrawError(f"no session {session_id!r} under {home / 'sessions'}")
        events = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        head = events[0]
        session = cls(directory, head["name"], Canvas.new(head["width"], head["height"], head["background"]))
        session._recording = False
        last_sha = head.get("canvas_sha")
        for event in events[1:]:
            kind = event["event"]
            if kind == "load_reference":
                session.set_reference(directory / event["stored"], event["source"], event.get("fit", "contain"),
                                      event.get("box"))
            elif kind == "actions":
                session.run_actions(event["actions"])
            elif kind == "undo":
                session.history.undo(session.canvas, event["steps"])
            elif kind == "redo":
                session.history.redo(session.canvas, event["steps"])
            if event.get("canvas_sha"):
                last_sha = event["canvas_sha"]
        session.seq = events[-1]["seq"]
        session._recording = True
        check = {"events": len(events), "expected_sha": last_sha, "replayed_sha": session.canvas.digest()}
        check["deterministic"] = check["expected_sha"] == check["replayed_sha"]
        session.log("resume", {"replay_check": check})
        return session, check

    @staticmethod
    def list(home: Path) -> list[dict[str, Any]]:
        out = []
        for traj in sorted((home / "sessions").glob("*/trajectory.jsonl")):
            lines = traj.read_text().splitlines()
            head = json.loads(lines[0])
            out.append({"id": traj.parent.name, "name": head["name"], "size": [head["width"], head["height"]],
                        "events": len(lines), "created": head["time"]})
        return out

    # ------------------------------------------------------------- logging
    def log(self, event: str, payload: dict[str, Any], *, frame: bool = False,
            view: Image.Image | None = None) -> dict[str, Any]:
        if not self._recording:
            return {}
        self.seq += 1
        record: dict[str, Any] = {"seq": self.seq, "time": _now(), "event": event, **payload}
        if frame:
            rel = f"frames/{self.seq:05d}.png"
            self.canvas.composite().save(self.dir / rel)
            record["frame"] = rel
            record["canvas_sha"] = self.canvas.digest()
        if view is not None:
            rel = f"views/{self.seq:05d}.png"
            view.save(self.dir / rel)
            record["view"] = rel
        with open(self.dir / "trajectory.jsonl", "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, separators=(",", ":")) + "\n")
        return record

    # ------------------------------------------------------------- actions
    def run_actions(self, actions: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Apply a batch atomically: on any error the canvas and history are rolled back."""
        start = self.canvas.snapshot()
        depth = len(self.history.undo_stack)
        redo = list(self.history.redo_stack)
        reports = []
        try:
            for index, action in enumerate(actions):
                self.history.record(self.canvas)
                try:
                    reports.append(self.canvas.apply(action))
                except (DrawError, KeyError, TypeError, ValueError) as exc:
                    raise DrawError(f"action {index} ({action.get('op')}): {exc}") from exc
        except DrawError:
            self.canvas.restore(start)
            del self.history.undo_stack[depth:]
            self.history.redo_stack = redo
            raise
        return reports

    def set_reference(self, path: Path, source: str, fit: str, box: list[int] | None) -> Reference:
        with Image.open(path) as img:
            img.load()
            self.reference = Reference.fit(img, source, self.canvas, fit, tuple(box) if box else None)
        return self.reference

    def store_reference(self, path: Path) -> Path:
        n = len(list((self.dir / "references").glob("*.png"))) + 1
        stored = self.dir / "references" / f"ref-{n}.png"
        with Image.open(path) as img:
            img.convert("RGBA").save(stored)
        return stored
