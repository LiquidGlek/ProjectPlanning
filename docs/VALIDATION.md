# Validation

## Layers

ProjectPlanning uses four validation layers. No single layer is sufficient.

### 1. Skill structure

Run the current official Codex skill validator:

```powershell
python "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" project-planning
```

This verifies required metadata and naming rules.

### 2. Script behavior

Compile the bundled auditor:

```powershell
python -m py_compile project-planning/scripts/audit_planning_package.py
```

Run its help path:

```powershell
python project-planning/scripts/audit_planning_package.py --help
```

Run it on a representative isolated planning package:

```powershell
python project-planning/scripts/audit_planning_package.py C:\path\to\fixture
```

The auditor checks:

- required documents and directories;
- explicit `LOCKED` and `NONE` state;
- unresolved placeholders;
- anti-placeholder document depth;
- required product, architecture, and testing sections;
- exact executor-prompt headings, order, and content floors;
- exact goal counts and schema fields;
- generic goal titles and duplicate scopes;
- milestone, prompt, and catalog count agreement;
- ADR structure and depth;
- stable risk count;
- relative Markdown links;
- optional Git planning-only scope.

Length thresholds are minimum floors, not quality scores.

### 3. Distribution integrity

Run:

```powershell
python scripts/validate_distribution.py
```

This validates repository structure, private-data patterns, version metadata,
skill metadata, Python syntax, release ZIP entries, and SHA-256 when a release
is present.

### 4. Sol Ultra semantic review

Manually verify:

- facts, decisions, assumptions, and questions are not conflated;
- architecture decisions are implementable and internally consistent;
- every goal owns a distinct capability;
- acceptance criteria prove outcomes rather than activity;
- test and evidence requirements can expose failure;
- visual descriptions are reconstructable;
- destructive actions have exact identity and authority;
- active documents agree with accepted ADRs;
- later scope is blocked;
- no runtime implementation occurred;
- goal lock remains engaged.

## Forward-test evidence

The sanitized GardenWatch fixture under `evidence/` exercises a greenfield
Python/Flutter/hardware product unrelated to the project that inspired the
method. The evidence report records:

- the initial mechanical pass that failed manual depth review;
- validator improvements that detected hollow documents and duplicate goals;
- the clean second run;
- exact counts, commands, results, and residual uncertainties.

## Failure policy

Never rewrite a failure as a partial pass. Use:

- `PASS` when every required check and semantic review succeeds;
- `FAIL` when a criterion is unmet;
- `BLOCKED` when external information or permission prevents the check;
- `NOT RUN` when no truthful execution occurred.

Skipped tests and unavailable runtime evidence must remain visible.
