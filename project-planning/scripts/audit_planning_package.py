#!/usr/bin/env python3
"""Mechanically audit a ProjectPlanning documentation package."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import unquote


REQUIRED_DOCS = (
    "AGENTS.md",
    "docs/PRODUCT_INTENT.md",
    "docs/ARCHITECTURE.md",
    "docs/MILESTONES.md",
    "docs/MILESTONE_TRACKER.md",
    "docs/QUALITY_GATES.md",
    "docs/TESTING_POLICY.md",
    "docs/DEFINITION_OF_DONE.md",
    "docs/CODEX_WORKING_RULES.md",
    "docs/GOAL_LOCK.md",
    "docs/DATA_MODEL.md",
    "docs/ASSET_PIPELINE.md",
    "docs/RISK_REGISTER.md",
    "docs/PLANNING_VALIDATION.md",
)

PROMPT_HEADINGS = (
    "Objective",
    "Preconditions",
    "Systems to preserve",
    "Exact implementation scope",
    "Acceptance criteria",
    "Tests",
    "Manual validation",
    "Evidence required",
    "Forbidden scope",
    "Definition of completion",
    "Only stop when",
)

PLACEHOLDER_RE = re.compile(
    r"(?im)(?:\b(?:TODO|TBD|FIXME)\s*:|\[PROJECT_[A-Z0-9_]+\])"
)
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
GOAL_ID_RE = re.compile(
    r"(?im)^\s*(?:ID:\s*|#{1,6}\s+)([A-Z][A-Z0-9-]*-G\d{2,3})\b"
)
STABLE_ID_RE = re.compile(
    r"(?im)^\s*(?:ID|Stable ID):\s*([A-Z][A-Z0-9._-]{2,})\s*$"
)

DOC_MIN_WORDS = {
    "AGENTS.md": 250,
    "docs/PRODUCT_INTENT.md": 450,
    "docs/ARCHITECTURE.md": 900,
    "docs/MILESTONES.md": 900,
    "docs/MILESTONE_TRACKER.md": 250,
    "docs/QUALITY_GATES.md": 500,
    "docs/TESTING_POLICY.md": 600,
    "docs/DEFINITION_OF_DONE.md": 350,
    "docs/CODEX_WORKING_RULES.md": 450,
    "docs/GOAL_LOCK.md": 25,
    "docs/DATA_MODEL.md": 700,
    "docs/ASSET_PIPELINE.md": 400,
    "docs/RISK_REGISTER.md": 450,
    "docs/PLANNING_VALIDATION.md": 300,
}

OPTIONAL_DOC_MIN_WORDS = {
    "docs/ART_PIPELINE.md": 700,
    "docs/REFERENCE_INTERPRETATION.md": 500,
    "docs/VISUAL_BIBLE.md": 1500,
}

REQUIRED_HEADING_GROUPS = {
    "docs/PRODUCT_INTENT.md": (
        ("promise", "intent"),
        ("user", "audience"),
        ("experience pillar", "product pillar"),
        ("fact",),
        ("decision",),
        ("assumption",),
        ("non-goal", "out of scope"),
        ("success", "target outcome"),
    ),
    "docs/ARCHITECTURE.md": (
        ("context", "system overview"),
        ("layer", "component"),
        ("dependency",),
        ("state ownership", "authority"),
        ("data", "persistence"),
        ("error", "recovery"),
        ("security", "privacy"),
        ("observability", "diagnostic"),
        ("test seam", "testability"),
        ("folder", "repository structure"),
        ("performance", "budget"),
        ("change control", "adr"),
    ),
    "docs/TESTING_POLICY.md": (
        ("test layer", "automated"),
        ("command",),
        ("manual",),
        ("edge",),
        ("evidence",),
        ("device", "platform"),
        ("performance", "profil"),
        ("security", "privacy"),
        ("accessibility",),
        ("failure", "blocked"),
    ),
}

ADR_REQUIRED_HEADINGS = (
    ("status",),
    ("context",),
    ("decision",),
    ("alternative",),
    ("consequence", "risk"),
    ("evidence",),
)

PROMPT_MIN_WORDS = {
    "Objective": 15,
    "Preconditions": 20,
    "Systems to preserve": 20,
    "Exact implementation scope": 40,
    "Acceptance criteria": 30,
    "Tests": 30,
    "Manual validation": 30,
    "Evidence required": 30,
    "Forbidden scope": 20,
    "Definition of completion": 25,
    "Only stop when": 25,
}

GOAL_FIELDS = (
    "ID",
    "Title",
    "Status",
    "Depends on",
    "Purpose",
    "Exact scope",
    "Acceptance criteria",
    "Tests",
    "Manual validation",
    "Evidence",
    "Forbidden scope",
)

GOAL_FIELD_MIN_WORDS = {
    "Title": 2,
    "Purpose": 8,
    "Exact scope": 18,
    "Acceptance criteria": 15,
    "Tests": 10,
    "Manual validation": 10,
    "Evidence": 6,
    "Forbidden scope": 8,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Audit required planning docs, locks, prompts, goals, links, and IDs."
        )
    )
    parser.add_argument("project_root", type=Path)
    parser.add_argument(
        "--goals-per-catalog",
        type=int,
        default=20,
        help=(
            "Expected unique goal IDs in every docs/GOALS Markdown file "
            "(default: 20)."
        ),
    )
    parser.add_argument(
        "--base-ref",
        help=(
            "Optional Git base ref used to detect changes outside docs/, "
            ".codex/, and AGENTS.md."
        ),
    )
    parser.add_argument(
        "--allow-prefix",
        action="append",
        default=[],
        help=(
            "Additional planning-only Git path prefix allowed by --base-ref. "
            "May be repeated."
        ),
    )
    return parser.parse_args()


def markdown_files(root: Path) -> list[Path]:
    files = []
    agents = root / "AGENTS.md"
    if agents.is_file():
        files.append(agents)
    docs = root / "docs"
    if docs.is_dir():
        files.extend(sorted(docs.rglob("*.md")))
    return files


def display(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w][\w'-]*\b", text, flags=re.UNICODE))


def headings(text: str) -> list[str]:
    return [
        re.sub(r"\s+", " ", match.group(1).strip().lower())
        for match in re.finditer(r"(?im)^#{1,6}\s+(.+?)\s*$", text)
    ]


def check_heading_groups(
    relative: str,
    text: str,
    groups: tuple[tuple[str, ...], ...],
    failures: list[str],
) -> None:
    found = headings(text)
    for alternatives in groups:
        if not any(
            any(alternative in heading for alternative in alternatives)
            for heading in found
        ):
            failures.append(
                f"{relative} lacks required section for: "
                + " or ".join(alternatives)
            )


def extract_prompt_sections(text: str) -> dict[str, str]:
    matches = []
    for heading in PROMPT_HEADINGS:
        match = re.search(
            rf"(?im)^#{{1,6}}\s+{re.escape(heading)}\s*$",
            text,
        )
        if match:
            matches.append((match.start(), match.end(), heading))
    matches.sort()
    sections = {}
    for index, (_, end, heading) in enumerate(matches):
        next_start = matches[index + 1][0] if index + 1 < len(matches) else len(text)
        sections[heading] = text[end:next_start].strip()
    return sections


def extract_goal_field(block: str, field: str) -> str | None:
    field_names = "|".join(re.escape(item) for item in GOAL_FIELDS)
    match = re.search(
        rf"(?ims)^{re.escape(field)}:\s*(.*?)"
        rf"(?=^(?:{field_names}):|\Z)",
        block,
    )
    return match.group(1).strip() if match else None


def normalize_scope(text: str) -> str:
    text = re.sub(r"\b[A-Z][A-Z0-9-]*-G\d{2,3}\b", "<goal>", text.upper())
    text = re.sub(r"\b\d+\b", "<n>", text)
    return re.sub(r"\s+", " ", text).strip()


def check_relative_links(path: Path, root: Path, failures: list[str]) -> int:
    checked = 0
    text = path.read_text(encoding="utf-8")
    for raw_target in MARKDOWN_LINK_RE.findall(text):
        target = raw_target.strip()
        if (
            not target
            or target.startswith(("#", "http://", "https://", "mailto:"))
            or "://" in target
        ):
            continue
        target = target.split("#", 1)[0].strip()
        if not target:
            continue
        if target.startswith("<") and target.endswith(">"):
            target = target[1:-1]
        target_path = Path(unquote(target))
        resolved = target_path if target_path.is_absolute() else path.parent / target_path
        checked += 1
        if not resolved.exists():
            failures.append(
                f"Unresolved link in {display(path, root)}: {raw_target}"
            )
    return checked


def git_scope_check(
    root: Path,
    base_ref: str,
    allowed_extra: list[str],
    failures: list[str],
) -> int:
    diff = subprocess.run(
        ["git", "diff", "--name-only", base_ref],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if diff.returncode != 0:
        failures.append(f"Git scope check failed: {diff.stderr.strip()}")
        return 0
    untracked_result = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if untracked_result.returncode != 0:
        failures.append(
            f"Git untracked-file check failed: {untracked_result.stderr.strip()}"
        )
        return 0
    changed = {
        line.strip()
        for output in (diff.stdout, untracked_result.stdout)
        for line in output.splitlines()
        if line.strip()
    }
    allowed_prefixes = ("docs/", ".codex/", *allowed_extra)
    outside = [
        item
        for item in sorted(changed)
        if not item.startswith(allowed_prefixes) and item != "AGENTS.md"
    ]
    for item in outside:
        failures.append(f"Planning-only scope changed non-planning path: {item}")
    return len(changed)


def main() -> int:
    args = parse_args()
    root = args.project_root.resolve()
    failures: list[str] = []
    warnings: list[str] = []
    metrics: dict[str, int] = {}

    if not root.is_dir():
        print(f"FAIL: project root does not exist: {root}")
        return 2

    for relative in REQUIRED_DOCS:
        if not (root / relative).is_file():
            failures.append(f"Missing required file: {relative}")

    for relative in ("docs/DECISIONS", "docs/GOALS", "docs/SOL_MEDIUM_PROMPTS"):
        if not (root / relative).is_dir():
            failures.append(f"Missing required directory: {relative}")

    all_markdown = markdown_files(root)
    metrics["Markdown files"] = len(all_markdown)

    for relative, minimum in {**DOC_MIN_WORDS, **OPTIONAL_DOC_MIN_WORDS}.items():
        path = root / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        count = word_count(text)
        if count < minimum:
            failures.append(
                f"{relative} has {count} words; anti-placeholder floor is {minimum}"
            )

    for relative, groups in REQUIRED_HEADING_GROUPS.items():
        path = root / relative
        if path.is_file():
            check_heading_groups(
                relative,
                path.read_text(encoding="utf-8"),
                groups,
                failures,
            )

    placeholder_hits = []
    for path in all_markdown:
        text = path.read_text(encoding="utf-8")
        for match in PLACEHOLDER_RE.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            placeholder_hits.append(f"{display(path, root)}:{line}:{match.group(0)}")
    if placeholder_hits:
        failures.extend(f"Unresolved placeholder: {item}" for item in placeholder_hits)
    metrics["Unresolved placeholders"] = len(placeholder_hits)

    lock_path = root / "docs/GOAL_LOCK.md"
    if lock_path.is_file():
        lock = lock_path.read_text(encoding="utf-8")
        if not re.search(r"(?im)Lock state:\s*(?:\*\*)?LOCKED\b", lock):
            failures.append("GOAL_LOCK.md does not declare Lock state: LOCKED")
        if not re.search(
            r"(?im)Active implementation goal:\s*(?:\*\*)?NONE\b", lock
        ):
            failures.append(
                "GOAL_LOCK.md does not declare Active implementation goal: NONE"
            )

    prompts_dir = root / "docs/SOL_MEDIUM_PROMPTS"
    prompt_files = (
        sorted(
            path
            for path in prompts_dir.glob("*.md")
            if path.name.lower() != "readme.md" and not path.name.startswith("_")
        )
        if prompts_dir.is_dir()
        else []
    )
    for path in prompt_files:
        text = path.read_text(encoding="utf-8")
        positions = []
        for heading in PROMPT_HEADINGS:
            matches = list(
                re.finditer(
                    rf"(?im)^#{{1,6}}\s+{re.escape(heading)}\s*$",
                    text,
                )
            )
            if len(matches) != 1:
                failures.append(
                    f"{display(path, root)} has {len(matches)} '{heading}' headings"
                )
            elif matches:
                positions.append(matches[0].start())
        if len(positions) == len(PROMPT_HEADINGS) and positions != sorted(positions):
            failures.append(f"Prompt headings out of order: {display(path, root)}")
        sections = extract_prompt_sections(text)
        for heading, minimum in PROMPT_MIN_WORDS.items():
            if heading in sections:
                count = word_count(sections[heading])
                if count < minimum:
                    failures.append(
                        f"{display(path, root)} section '{heading}' has {count} "
                        f"words; anti-placeholder floor is {minimum}"
                    )
    metrics["Executor prompts"] = len(prompt_files)

    goals_dir = root / "docs/GOALS"
    goal_files = (
        sorted(
            path
            for path in goals_dir.glob("*.md")
            if path.name.lower() != "readme.md" and not path.name.startswith("_")
        )
        if goals_dir.is_dir()
        else []
    )
    all_goal_ids: list[str] = []
    for path in goal_files:
        text = path.read_text(encoding="utf-8")
        ids = GOAL_ID_RE.findall(text)
        unique = set(ids)
        all_goal_ids.extend(ids)
        if len(unique) != args.goals_per_catalog:
            failures.append(
                f"{display(path, root)} has {len(unique)} unique goals; "
                f"expected {args.goals_per_catalog}"
            )
        if len(ids) != len(unique):
            failures.append(f"Duplicate goal ID inside {display(path, root)}")
        active = re.findall(r"(?im)^\s*Status:\s*(?!DORMANT\b)(\S.*)$", text)
        if active:
            failures.append(
                f"Non-dormant goal status in {display(path, root)}: {active[0]}"
            )
        id_matches = list(
            re.finditer(
                r"(?im)^ID:\s*([A-Z][A-Z0-9-]*-G\d{2,3})\b",
                text,
            )
        )
        normalized_scopes = []
        titles = []
        for index, id_match in enumerate(id_matches):
            block_end = (
                id_matches[index + 1].start()
                if index + 1 < len(id_matches)
                else len(text)
            )
            block = text[id_match.start():block_end]
            goal_id = id_match.group(1)
            values = {}
            for field in GOAL_FIELDS:
                value = extract_goal_field(block, field)
                if value is None:
                    failures.append(
                        f"{display(path, root)} {goal_id} lacks field '{field}'"
                    )
                else:
                    values[field] = value
            for field, minimum in GOAL_FIELD_MIN_WORDS.items():
                if field in values:
                    count = word_count(values[field])
                    if count < minimum:
                        failures.append(
                            f"{display(path, root)} {goal_id} field '{field}' "
                            f"has {count} words; floor is {minimum}"
                        )
            title = values.get("Title", "")
            if re.search(
                r"(?i)\b(?:capability|goal|task|stage)\s*\d+\s*$",
                title,
            ):
                failures.append(
                    f"{display(path, root)} {goal_id} has generic title: {title}"
                )
            titles.append(title.casefold())
            scope = values.get("Exact scope")
            if scope:
                normalized_scopes.append(normalize_scope(scope))
        for title, count in Counter(titles).items():
            if title and count > 1:
                failures.append(
                    f"{display(path, root)} repeats goal title {count} times: {title}"
                )
        for scope, count in Counter(normalized_scopes).items():
            if scope and count > 1:
                failures.append(
                    f"{display(path, root)} repeats normalized exact scope "
                    f"{count} times"
                )
    duplicate_goals = [
        key for key, count in Counter(all_goal_ids).items() if count > 1
    ]
    for goal_id in duplicate_goals:
        failures.append(f"Duplicate goal ID across catalogs: {goal_id}")
    metrics["Goal catalogs"] = len(goal_files)
    metrics["Unique goals"] = len(set(all_goal_ids))

    milestones_path = root / "docs/MILESTONES.md"
    milestone_ids = []
    if milestones_path.is_file():
        milestone_ids = re.findall(
            r"(?im)^##\s+(M\d{2}(?:[-_][A-Z0-9]+)*)\b",
            milestones_path.read_text(encoding="utf-8"),
        )
        if milestone_ids:
            required_words = max(900, len(set(milestone_ids)) * 250)
            actual_words = word_count(
                milestones_path.read_text(encoding="utf-8")
            )
            if actual_words < required_words:
                failures.append(
                    f"docs/MILESTONES.md has {actual_words} words for "
                    f"{len(set(milestone_ids))} milestones; floor is "
                    f"{required_words}"
                )
            if len(prompt_files) != len(set(milestone_ids)):
                failures.append(
                    "Executor prompt count does not match milestone count: "
                    f"{len(prompt_files)} vs {len(set(milestone_ids))}"
                )
            if len(goal_files) != len(set(milestone_ids)):
                failures.append(
                    "Goal catalog count does not match milestone count: "
                    f"{len(goal_files)} vs {len(set(milestone_ids))}"
                )
    metrics["Milestones"] = len(set(milestone_ids))

    decisions_dir = root / "docs/DECISIONS"
    adr_files = (
        sorted(decisions_dir.glob("*.md")) if decisions_dir.is_dir() else []
    )
    if not adr_files:
        failures.append("No architecture decision records found")
    for path in adr_files:
        text = path.read_text(encoding="utf-8")
        count = word_count(text)
        if count < 150:
            failures.append(
                f"{display(path, root)} has {count} words; ADR floor is 150"
            )
        check_heading_groups(
            display(path, root),
            text,
            ADR_REQUIRED_HEADINGS,
            failures,
        )
    metrics["ADRs"] = len(adr_files)

    risk_path = root / "docs/RISK_REGISTER.md"
    risk_ids = []
    if risk_path.is_file():
        risk_ids = re.findall(
            r"(?i)\b(?:RISK|R)-\d{2,3}\b",
            risk_path.read_text(encoding="utf-8"),
        )
        if len(set(item.upper() for item in risk_ids)) < 8:
            failures.append("RISK_REGISTER.md contains fewer than 8 stable risks")
    metrics["Unique risks"] = len(set(item.upper() for item in risk_ids))

    stable_ids: list[str] = []
    for path in all_markdown:
        if any(part in {"GOALS", "SOL_MEDIUM_PROMPTS"} for part in path.parts):
            continue
        stable_ids.extend(STABLE_ID_RE.findall(path.read_text(encoding="utf-8")))
    duplicates = [
        key for key, count in Counter(stable_ids).items() if count > 1
    ]
    for stable_id in duplicates:
        warnings.append(f"Repeated stable ID; inspect for collision: {stable_id}")
    metrics["Stable IDs scanned"] = len(stable_ids)

    links_checked = 0
    for path in all_markdown:
        links_checked += check_relative_links(path, root, failures)
    metrics["Relative links checked"] = links_checked
    if links_checked < 5:
        failures.append(
            f"Only {links_checked} relative links found; transferable package "
            "floor is 5"
        )

    if args.base_ref:
        metrics["Git paths checked"] = git_scope_check(
            root, args.base_ref, args.allow_prefix, failures
        )

    if not prompt_files:
        failures.append("No Sol Medium prompt files found")
    if not goal_files:
        failures.append("No goal catalog files found")

    status = "PASS" if not failures else "FAIL"
    print(f"ProjectPlanning audit: {status}")
    print(f"Root: {root}")
    for name, value in metrics.items():
        print(f"{name}: {value}")
    for warning in warnings:
        print(f"WARNING: {warning}")
    for failure in failures:
        print(f"FAIL: {failure}")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
