---
name: project-planning
description: Create an exhaustive, evidence-backed, implementation-locked production planning package for a new project, clean rebuild, repository transition, or troubled project recovery. Use only when Codex is running the Sol model at Ultra reasoning and the user asks for deep project planning, architecture, milestones, quality gates, dormant goal catalogs, executor prompts, repository retirement planning, visual or asset direction, or permanent anti-shortcut guardrails. Do not use for implementation, ordinary task planning, small feature plans, or on any other model or reasoning level.
---

# ProjectPlanning

Create a transferable plan that another agent can execute without inventing
architecture, skipping foundations, silently expanding scope, or claiming
success without evidence. Finish the planning package; do not start its
implementation.

## Enforce the model gate

Before reading project files or taking task actions:

1. If runtime context identifies the active model or reasoning effort and either
   is not Sol at Ultra, stop and say: `ProjectPlanning is restricted to Sol
   Ultra. Switch this task to Sol with Ultra reasoning, then invoke
   $project-planning again.`
2. If runtime context confirms Sol at Ultra, proceed.
3. If Codex does not expose model or effort identity to the agent, proceed only
   when the user explicitly invoked `$project-planning`. State once that model
   selection could not be programmatically verified and that explicit
   invocation is being treated as confirmation.
4. Never invoke this skill implicitly or infer authorization from a generic
   request for a plan.
5. Do not weaken this gate because another agent can read the files.

This is the strongest enforcement available to a portable Codex skill:
explicit-invocation metadata plus fail-closed instructions when runtime identity
is known. Codex skills do not provide cryptographic model access control.

## Load the controlling specifications

Read these files completely before authoring:

- Always read [planning-package-spec.md](references/planning-package-spec.md).
- Read [repository-transition.md](references/repository-transition.md) when an
  existing repository may be archived, retired, replaced, deleted, or
  published.
- Read [visual-product-planning.md](references/visual-product-planning.md) when
  screenshots, mockups, art, characters, animation, rooms, 3D, UI, or other
  visual targets are in scope.
- Read [executor-handoff.md](references/executor-handoff.md) when future Codex
  agents will implement the plan, or when goals, prompts, skills, delegation,
  or acceleration are requested.
- Read [project-skill-design.md](references/project-skill-design.md) when the
  user requests reusable Codex skills or the plan identifies recurring,
  high-risk executor workflows.

## Establish the planning boundary

At the beginning of the package, record:

- project name and one-sentence intent;
- planning mode: greenfield, clean rebuild, transition, or recovery;
- authoritative input paths and source precedence;
- known facts, user decisions, assumptions, open questions, and conflicts;
- platforms, technology constraints, non-goals, and deferred work;
- authorized external or destructive actions;
- explicit statement: `Planning only. Implementation is not authorized.`

Create `docs/GOAL_LOCK.md` immediately with:

```text
Lock state: LOCKED
Active implementation goal: NONE
Unlock authority: the user
```

Do not call a goal-creation mechanism, start a milestone, edit product runtime
files, or produce implementation disguised as a prototype. Planning-only
reference visuals are allowed only when requested and must be labeled
non-runtime and non-canonical.

## Work continuously through planning

Inspect the real repository and existing instructions before deciding. Preserve
unrelated work. Ask only questions whose answers materially change product
scope, irreversible actions, architecture, legal rights, or acceptance
criteria. Make conservative, documented assumptions for non-blocking gaps.

Stop only when:

- repository identity is ambiguous;
- a destructive action cannot be verified safely;
- required permissions or credentials are unavailable;
- requirements irreconcilably conflict; or
- continuing risks data loss.

Otherwise complete all planning phases without approval after every section.
Never treat blanket approval as permission for an unidentified destructive
target.

## Build the package in dependency order

1. **Safety and evidence:** identify repository, preserve existing work, and
   complete any authorized transition procedure.
2. **Product truth:** freeze intent, audience, experience pillars, priorities,
   non-goals, reference precedence, and measurable target outcomes.
3. **Architecture:** define layers, dependency direction, authoritative state,
   adapters, data contracts, save/versioning strategy, error handling,
   observability, and decision records.
4. **Pipelines:** define source asset, art, content, data, build, test, and
   release workflows with provenance and acceptance.
5. **Milestones:** order vertical capability layers so later work cannot begin
   until every preceding gate passes.
6. **Execution contracts:** create dormant goals, ready-to-run executor
   prompts, delegation rules, clarification protocol, and reusable
   project-specific skills where justified.
7. **Validation:** mechanically audit the complete package, reconcile every
   cross-document reference, and record honest limitations.

Use accepted architecture decision records rather than silently revising
architecture. Mark superseded documents as historical; do not leave two active
sources of truth.

## Create permanent guardrails

At minimum create:

- `AGENTS.md`
- `docs/PRODUCT_INTENT.md`
- `docs/ARCHITECTURE.md`
- `docs/MILESTONES.md`
- `docs/MILESTONE_TRACKER.md`
- `docs/QUALITY_GATES.md`
- `docs/TESTING_POLICY.md`
- `docs/DEFINITION_OF_DONE.md`
- `docs/CODEX_WORKING_RULES.md`
- `docs/GOAL_LOCK.md`
- `docs/DATA_MODEL.md`
- `docs/ASSET_PIPELINE.md`
- `docs/RISK_REGISTER.md`
- `docs/DECISIONS/`
- `docs/GOALS/`
- `docs/SOL_MEDIUM_PROMPTS/`

Add `ART_PIPELINE.md`, `REFERENCE_INTERPRETATION.md`, `VISUAL_BIBLE.md`, and
stable visual/content registers when applicable. Replace names only when an
existing repository has an equally clear canonical structure; document the
mapping.

When project-specific skills are authorized, also create `docs/SKILL_PLAN.md`
and apply [project-skill-design.md](references/project-skill-design.md). Skill
creation remains planning infrastructure and must not execute a product
milestone or unlock a goal.

## Make gates fail closed

For each milestone define:

- objective and user-visible outcome;
- exact preconditions and preceding gate;
- in-scope and forbidden work;
- architecture and systems to preserve;
- acceptance criteria;
- automated tests and required commands;
- manual and edge-case validation;
- running-product evidence;
- performance, accessibility, security, or device checks as relevant;
- known-limitations recording;
- a binary PASS/FAIL gate.

Compilation, a scene opening, placeholders, a similar screenshot, or clickable
buttons are never sufficient alone. A failed or unverified gate blocks the next
milestone.

## Produce dormant execution units

Unless the user chooses another count, create exactly 20 dormant, independently
verifiable goals per milestone or corrective stage. These are plan records, not
active Codex goals. Each goal needs a stable ID, dependency, scope, acceptance
evidence, test obligation, and explicit forbidden scope.

Every goal must own a distinct, named capability. Generic numbered entries such
as `Foundation capability 1`, duplicated scopes with changed IDs, and repeated
boilerplate presented as separate goals are validation failures.

Create one ready-to-run Sol Medium prompt per milestone or stage using the exact
contract in [executor-handoff.md](references/executor-handoff.md). Sol Medium
owns integration and may use up to three non-overlapping Sol Low workers for
bounded tasks. Sol Ultra clarification is limited to one narrow, read-only
question after evidence and competing interpretations are supplied.

## Validate before handoff

Run [audit_planning_package.py](scripts/audit_planning_package.py) against the
project root. Also run repository-native Markdown/link checks, skill validators,
formatting checks, and `git diff --check` where available. Manually verify items
the script cannot prove:

- repository and archive identity;
- visual meaning and reference fidelity;
- architecture coherence;
- gate ordering and scope boundaries;
- destructive-action authorization;
- no runtime implementation changes;
- no implementation goal was activated.

Treat the validator's length and structure checks as minimum anti-placeholder
floors, not proof of quality. Reject padded prose, shallow one-paragraph
architecture, generic goal catalogs, tautological acceptance criteria, and
milestones that merely repeat the same text under different IDs.

Record commands, results, timestamps, hashes, versions, unresolved failures, and
skipped checks in `docs/PLANNING_VALIDATION.md`. Never convert NOT RUN into PASS.

## Complete the planning task

Finish only when the package is transferable, links resolve, IDs are unique,
goal and prompt counts match, every milestone has a gate, all active documents
agree, the tracker identifies no active implementation milestone, and the lock
remains `LOCKED`.

In the final handoff lead with:

1. what was planned;
2. where the package is;
3. validation results and exact counts;
4. archive, publication, or permission truth;
5. unresolved risks;
6. explicit confirmation that implementation did not start.

Do not unlock the goal, begin M01, or tell an executor to proceed unless the
user makes a separate later request.
