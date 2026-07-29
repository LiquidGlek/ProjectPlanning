# ProjectPlanning

ProjectPlanning is a private Codex skill for creating exhaustive,
implementation-locked production plans before an implementation agent touches
the product.

It turns a product idea, mockup, existing repository, or failed prototype into
a transferable package containing product intent, architecture, data contracts,
milestones, binary quality gates, dormant goals, executor prompts, risk
controls, evidence requirements, and permanent anti-shortcut guardrails.

## Why it exists

Coding agents are fast enough to amplify a vague plan into the wrong product.
They can also mistake compilation, placeholders, or a persuasive screenshot for
completion. ProjectPlanning moves the hard decisions in front of implementation
and gives every later milestone a fail-closed contract.

The skill is designed to prevent future agents from:

- inventing architecture while implementing;
- skipping foundations to chase visible polish;
- reinterpreting product intent without an accepted decision record;
- silently expanding scope;
- copying or flattening visual references;
- creating generic, duplicated goal catalogs;
- continuing after a failed or unverified gate;
- fabricating tests, builds, screenshots, or deployment evidence.

## Repository contents

```text
project-planning/                 Installable Codex skill
  SKILL.md
  agents/openai.yaml
  references/
  scripts/audit_planning_package.py
docs/                             Method, policy, validation, and operations
evidence/                         Sanitized forward-test reports and fixtures
dist/                             Versioned ZIP for sharing
scripts/validate_distribution.py Repository/package validator
```

## Model policy

ProjectPlanning is reserved for **Sol with Ultra reasoning**. It is configured
for explicit invocation only.

Codex's portable skill schema does not currently provide cryptographic model
access control. The skill therefore uses the strongest portable enforcement:

1. refuse when runtime context identifies a different model or effort;
2. proceed when runtime context confirms Sol Ultra;
3. when Codex hides model metadata, require explicit `$project-planning`
   invocation and treat that invocation as the user's confirmation.

See [Model policy](docs/MODEL_POLICY.md) for the exact boundary.

## Install

1. Download or receive
   `dist/ProjectPlanning-Sol-Ultra-v1.0.0.zip`.
2. Verify its SHA-256 against `dist/SHA256SUMS.txt`.
3. Extract it so the final folder is:

   ```text
   %USERPROFILE%\.codex\skills\project-planning
   ```

4. Start a new Codex task so the skill catalog refreshes.
5. Select Sol and Ultra reasoning.
6. Invoke the skill explicitly:

   ```text
   Use $project-planning to create a complete, implementation-locked
   production plan for [project].
   ```

Do not rename the inner `project-planning` directory; the skill name and folder
name must match.

## Use

Provide as much of this input as exists:

- project name and one-sentence promise;
- greenfield, transition, clean rebuild, or recovery mode;
- repository path and authoritative instructions;
- screenshots, mockups, specifications, and their priority;
- platforms and technology constraints;
- explicit non-goals;
- allowed repository, archive, GitHub, or collaborator actions;
- desired milestone boundaries;
- project-specific rules that must never be reinterpreted.

ProjectPlanning asks only materially blocking questions. Otherwise it works
continuously through the full planning package.

## Expected output

The default package includes:

- product intent and source-precedence contract;
- architecture, folder structure, state ownership, data model, save/migration,
  security, observability, and performance decisions;
- ordered milestones with binary gates;
- exactly 20 dormant goals per milestone or corrective stage unless the user
  selects another count;
- one ready-to-run Sol Medium prompt per stage;
- Sol Medium integrator and bounded Sol Low worker protocol;
- one-question, read-only Sol Ultra clarification protocol;
- art, asset, reference, and visual-bible plans when applicable;
- testing policy, evidence manifest requirements, risks, Definition of Done,
  tracker, ADRs, and permanent agent rules;
- optional project-specific Codex skills created through the official
  `$skill-creator`;
- `GOAL_LOCK.md` left `LOCKED` with active implementation goal `NONE`.

It does not implement the product or activate the first goal.

## Validate

Run the repository check:

```powershell
python scripts/validate_distribution.py
```

Run the official Codex validator against the installed skill:

```powershell
python "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" project-planning
```

The bundled planning-package auditor is run by the skill against every generated
project. See [Validation](docs/VALIDATION.md).

## Confidentiality

This repository is private and proprietary. Do not publish it, its release ZIP,
or its evidence outside approved collaborators. The generic skill contains no
source-project repository data, credentials, private mockups, personal email
addresses, or project archive paths.

See [Security and privacy](docs/SECURITY_AND_PRIVACY.md).
