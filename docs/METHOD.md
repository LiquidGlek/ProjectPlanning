# ProjectPlanning method

## Outcome

ProjectPlanning converts uncertain product intent into a verified,
implementation-locked operating system for future agents. Its output is not a
brainstorm or backlog. It is the controlling contract for architecture, scope,
execution order, evidence, and completion.

## Operating modes

### Greenfield

Define product truth and a clean foundation where no implementation repository
exists.

### Clean rebuild

Preserve evidence from a failed implementation, classify reusable material, and
establish a new repository without inheriting broken architecture or Git
history.

### Repository transition

Identify, archive, verify, retire, publish, delete, or transfer a repository
only within precise user authorization and identity checks.

### Recovery

Inspect an active troubled project, preserve working architecture, identify
failed gates and contract drift, then create corrective stages before later
milestones resume.

## Planning pipeline

```text
Safety and source evidence
        ↓
Product truth and reference precedence
        ↓
Architecture, data, and pipeline decisions
        ↓
Dependency-ordered milestones
        ↓
Binary quality gates and Definition of Done
        ↓
Dormant goals and executor prompts
        ↓
Optional project-specific skills
        ↓
Mechanical plus semantic validation
        ↓
Transferable handoff with GOAL_LOCK still LOCKED
```

## Safety and source evidence

The skill first distinguishes verified facts, user decisions, reversible
assumptions, and unresolved questions. Existing repositories are identified by
resolved path, Git root, remotes, HEAD, refs, dirty state, submodules, LFS, and
neighbor exclusions before any mutation.

When retirement is requested, a complete archive outside the active workspace
must preserve Git history and the non-Git worktree. Hashes, file counts, refs,
dirty work, ignored assets, design references, tests, and verification results
are recorded. Online deletion is a separate destructive action and cannot be
inferred from archive authorization.

## Product truth

The package freezes the product promise, users, experience pillars, source
precedence, platforms, constraints, non-goals, deferred work, and measurable
outcomes. Screenshots and mockups control only explicitly assigned properties.
User corrections become decisions instead of being lost in chat history.

## Architecture

The architecture contract defines components, dependency direction,
authoritative state, commands and queries, infrastructure adapters, persistence
and migration, errors and recovery, security, observability, test seams, folder
ownership, and budgets. Durable changes require accepted architecture decision
records and regression evidence.

## Milestones and gates

Milestones are dependency layers, not dates. Each has exact preconditions,
preserved systems, implementation scope, forbidden scope, acceptance criteria,
automated tests, manual edge cases, running evidence, budgets, and a binary
gate.

The only gate states are `NOT RUN`, `PASS`, `FAIL`, and `BLOCKED`. A later
milestone cannot begin unless every preceding gate is `PASS`.

Compilation, a scene opening, placeholders, visual resemblance, or responsive
buttons cannot establish completion by themselves.

## Dormant goals

By default, every milestone or corrective stage receives exactly 20
independently verifiable goals. Every goal has a stable ID, dependency,
capability-specific purpose and scope, acceptance criteria, tests, manual cases,
evidence, and forbidden scope.

Goal catalogs remain `DORMANT`. Creating or approving a catalog never activates
the Codex goal mechanism.

## Executor handoff

Each stage receives one Sol Medium prompt with eleven fixed sections:

1. Objective
2. Preconditions
3. Systems to preserve
4. Exact implementation scope
5. Acceptance criteria
6. Tests
7. Manual validation
8. Evidence required
9. Forbidden scope
10. Definition of completion
11. Only stop when

Sol Medium owns integration and gate truth. Up to three Sol Low workers may
handle truly independent bounded work. A Sol Ultra clarification agent may
answer one narrow read-only question only after documents, code, tests, logs,
and competing interpretations are supplied.

## Visual planning

Visual products receive reference hashes and precedence, a blind-person visual
bible, stable item registers, composition and camera contracts, asset
provenance, animation catalogs, inclusive customization matrices, and
running-build evidence requirements. Concept art cannot become a flattened
runtime background or substitute for original implementation.

## Skill creation

When recurring high-risk workflows warrant automation, ProjectPlanning invokes
the official `$skill-creator`. It designs narrow executor, gate-closing, asset,
audit, or clarification skills with separate authority and fail-closed
preconditions. Creating those skills does not authorize their use.

## Validation

The bundled auditor checks required files, anti-placeholder depth floors,
required sections, prompt content, goal schemas, duplicate scopes, stable IDs,
milestone/catalog/prompt counts, ADRs, risks, links, lock state, and optional Git
scope. Sol Ultra then performs semantic review because mechanical length and
structure cannot prove a coherent plan.

Planning ends with a validation record, exact blockers, and the execution lock
still engaged.
