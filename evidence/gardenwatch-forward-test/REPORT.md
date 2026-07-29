# GardenWatch independent forward-test report

## Status

Final result: **PASS**

This evidence comes from a synthetic project unrelated to the source project
that motivated ProjectPlanning. It was executed by an independently spawned Sol
agent configured at Ultra reasoning in an isolated temporary directory. The
test explicitly invoked `$project-planning` because the agent runtime did not
expose its selected model and reasoning metadata.

No product code, hardware action, goal activation, repository publication,
deployment, credentials, or destructive external action occurred.

## Test scenario

GardenWatch is a fictional greenfield, local-first product:

- Raspberry Pi moisture and temperature sensing;
- Python service and SQLite persistence;
- landscape Flutter tablet dashboard;
- local LAN only;
- no cloud, accounts, subscriptions, telemetry, or automated watering;
- future implementation assigned milestone-by-milestone to Sol Medium.

The requested planning package required three dependency-ordered milestones,
exactly 20 dormant goals per milestone, fail-closed gates, architecture and data
contracts, testing and risk policy, agent guardrails, and one executor prompt
per milestone.

## Iteration 1: rejected despite the original count PASS

The first skill version mechanically counted:

- 25 Markdown documents;
- 3 milestones;
- 3 goal catalogs;
- 60 unique goal IDs;
- 3 executor prompts;
- 0 placeholder markers.

Manual Sol Ultra review rejected the result. Architecture, product intent,
testing policy, ADRs, and risks were compressed into shallow paragraphs. The
60 goals were generic numbered variants such as `Foundation capability 1`, and
their exact scopes were duplicated.

The validator was strengthened to enforce anti-placeholder document floors,
required semantic sections, executor-section depth, complete goal fields,
generic-title rejection, duplicate-scope rejection, milestone/prompt/catalog
agreement, substantive ADRs, stable risks, links, and lock state.

Running the strengthened validator against iteration 1 produced:

- exit code 1;
- 477 failure lines;
- 60 generic goal-title failures;
- 3 duplicate-scope failures, one per catalog;
- 47 anti-placeholder depth failures;
- 35 ADR depth/section failures;
- 1 cross-link floor failure.

This rejected iteration is evidence that the validator does not treat counts as
quality.

## Iteration 2: clean rerun

A fresh Sol Ultra agent received the same project request and the revised skill.
The prior fixture was not available at the original path.

Root verification reran:

```text
audit_planning_package.py [isolated GardenWatch planning directory]
```

Observed result:

```text
ProjectPlanning audit: PASS
Markdown files: 21
Unresolved placeholders: 0
Executor prompts: 3
Goal catalogs: 3
Unique goals: 60
Milestones: 3
ADRs: 1
Unique risks: 12
Stable IDs scanned: 0
Relative links checked: 6
```

Additional root inspection confirmed:

- all 60 goal titles are capability-specific;
- representative goal purposes, scopes, criteria, tests, manual cases,
  evidence, and forbidden scope are distinct and actionable;
- architecture defines boundaries, dependencies, state authority, persistence,
  recovery, security, observability, test seams, layout, and budgets;
- all three Sol Medium prompts contain the required eleven sections and
  fail-closed stop contract;
- no unresolved `TODO:`, `TBD:`, or `FIXME:` markers;
- no generic iteration-1 goal-title patterns;
- goal lock is `LOCKED`;
- active implementation goal is `NONE`.

The final fixture contained 21 files totaling 151,077 bytes. A SHA-256 digest
over the sorted relative-path and file-hash manifest was:

```text
EB91C46C0901FF134DD12DE685B7F84D160EF79440707B76A0822834E9996061
```

## Skill identity

Validated portable skill hashes:

```text
63AF2C266411F5F0FE33D7BDAE2230153C94259C07065443FD0FB661950A4F7F  SKILL.md
7482CDC9928D60048FD31DE5D07850FBC226730317F0BD809F4E75FF224429EC  scripts/audit_planning_package.py
```

The installed and repository copies contained eight files with zero missing,
extra, or hash-different files at freeze time.

## Residual uncertainty

The forward test proves planning workflow behavior, document structure, and
semantic specificity. It does not prove a Raspberry Pi sensor driver, Flutter
application, hardware calibration, device accessibility, or performance because
implementation was intentionally forbidden.

The synthetic plan correctly leaves sensor family/bus, Pi image, tablet model,
LAN addressing, retention duration, and release signing as explicit questions
or later milestone preconditions rather than invented facts.
