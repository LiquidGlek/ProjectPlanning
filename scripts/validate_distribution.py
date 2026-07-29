#!/usr/bin/env python3
"""Validate the private ProjectPlanning repository and release package."""

from __future__ import annotations

import hashlib
import py_compile
import re
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "project-planning"
REQUIRED = (
    "README.md",
    "AGENTS.md",
    "VERSION",
    "PROPRIETARY.md",
    "docs/METHOD.md",
    "docs/MODEL_POLICY.md",
    "docs/VALIDATION.md",
    "docs/SECURITY_AND_PRIVACY.md",
    "project-planning/SKILL.md",
    "project-planning/agents/openai.yaml",
    "project-planning/references/planning-package-spec.md",
    "project-planning/references/repository-transition.md",
    "project-planning/references/visual-product-planning.md",
    "project-planning/references/executor-handoff.md",
    "project-planning/references/project-skill-design.md",
    "project-planning/scripts/audit_planning_package.py",
)
PRIVATE_PATTERNS = {
    "personal email": re.compile(r"(?i)\b[\w.+-]+@(?:gmail|outlook|hotmail)\.com\b"),
    "source-project identifier": re.compile(
        r"(?i)\b" + "happy" + "home" + r"\b"
    ),
    "private archive path": re.compile(r"(?i)\bHH-" + r"archive-\d+"),
    "user-specific path": re.compile(r"(?i)C:\\Users\\" + r"Kai\\"),
    "GitHub OAuth token": re.compile(r"\bgh[opusr]_[A-Za-z0-9_]{20,}\b"),
    "generic secret assignment": re.compile(
        r"(?i)\b(?:password|api[_-]?key|secret|token)\s*[:=]\s*[\"'][^\"']+[\"']"
    ),
}


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def main() -> int:
    failures: list[str] = []
    for relative in REQUIRED:
        if not (ROOT / relative).is_file():
            fail(f"Missing required file: {relative}", failures)

    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        fail(f"VERSION is not semantic: {version}", failures)

    skill_text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    if not skill_text.startswith("---\nname: project-planning\n"):
        fail("SKILL.md frontmatter name is invalid", failures)
    if "Sol" not in skill_text or "Ultra" not in skill_text:
        fail("SKILL.md lacks the Sol Ultra policy", failures)

    metadata = (SKILL / "agents/openai.yaml").read_text(encoding="utf-8")
    if 'display_name: "ProjectPlanning"' not in metadata:
        fail("openai.yaml display name is invalid", failures)
    if "allow_implicit_invocation: false" not in metadata:
        fail("openai.yaml does not disable implicit invocation", failures)

    auditor = SKILL / "scripts/audit_planning_package.py"
    try:
        py_compile.compile(str(auditor), doraise=True)
    except py_compile.PyCompileError as error:
        fail(f"Auditor does not compile: {error.msg}", failures)

    scanned = 0
    for path in sorted(ROOT.rglob("*")):
        if (
            not path.is_file()
            or ".git" in path.parts
            or "dist" in path.parts
            or "__pycache__" in path.parts
        ):
            continue
        if path.suffix.lower() not in {".md", ".txt", ".yaml", ".yml", ".py", ""}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        scanned += 1
        relative = path.relative_to(ROOT).as_posix()
        for label, pattern in PRIVATE_PATTERNS.items():
            if pattern.search(text):
                fail(f"{label} found in {relative}", failures)

    zip_path = ROOT / "dist" / f"ProjectPlanning-Sol-Ultra-v{version}.zip"
    sums_path = ROOT / "dist" / "SHA256SUMS.txt"
    zip_entries = 0
    if zip_path.exists():
        with zipfile.ZipFile(zip_path) as archive:
            names = archive.namelist()
            zip_entries = len(names)
            if not names:
                fail("Release ZIP is empty", failures)
            if any("__pycache__" in name or name.endswith((".pyc", ".pyo")) for name in names):
                fail("Release ZIP contains Python cache files", failures)
            if not all(name.startswith("project-planning/") for name in names):
                fail("Release ZIP contains entries outside project-planning/", failures)
            required_entry = "project-planning/SKILL.md"
            if required_entry not in names:
                fail(f"Release ZIP lacks {required_entry}", failures)
        if not sums_path.is_file():
            fail("Release ZIP exists without dist/SHA256SUMS.txt", failures)
        else:
            expected = sums_path.read_text(encoding="utf-8").strip().split()[0]
            actual = sha256(zip_path)
            if expected.upper() != actual:
                fail(
                    f"Release ZIP SHA-256 mismatch: expected {expected}, actual {actual}",
                    failures,
                )

    print("ProjectPlanning distribution:", "PASS" if not failures else "FAIL")
    print(f"Root: {ROOT}")
    print(f"Version: {version}")
    print(f"Text files scanned: {scanned}")
    print(f"Release ZIP entries: {zip_entries}")
    for item in failures:
        print(f"FAIL: {item}")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
