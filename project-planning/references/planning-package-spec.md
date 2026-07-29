# Planning package specification

Use this specification for every ProjectPlanning package. Adapt terminology to
the product, but preserve the contracts.

## Contents

1. Product truth
2. Architecture
3. Milestones and gates
4. Dormant goals
5. Tracking and decisions
6. Testing and evidence
7. Risk and completion

## 1. Product truth

`PRODUCT_INTENT.md` must state:

- the one-sentence product promise;
- target users and primary use situation;
- "product first, secondary utility second" priority if applicable;
- three to seven experience pillars;
- what success feels like to a user;
- supported platforms and input modes;
- current technology decisions and why;
- economic, privacy, accessibility, safety, legal, and content invariants;
- explicit non-goals and deferred capabilities;
- source/reference precedence;
- what may be simulated or placeholder-only, and until which gate.

Separate:

- **Fact:** verified from repository, running product, source, or user.
- **Decision:** explicitly chosen by the user or an accepted ADR.
- **Assumption:** necessary to proceed and reversible.
- **Question:** unresolved and material.

Never promote an assumption to a decision.

Write a substantive, project-specific contract. A compressed paragraph or a
list that merely repeats the user brief is not sufficient.

## 2. Architecture

`ARCHITECTURE.md` must make implementation choices sufficiently concrete that
an executor does not invent a competing structure. Include:

- context and component boundaries;
- dependency direction and forbidden references;
- domain state ownership;
- application commands, queries, and events;
- infrastructure adapters and composition root;
- persistence abstraction, schema versions, migrations, backups, and corrupt
  data recovery;
- stable identifiers and content definitions;
- concurrency, retries, idempotency, and error contracts where applicable;
- platform services and seams for later backend or cloud work;
- security and privacy boundaries;
- observability and diagnostics;
- test seams and assembly/module layout;
- folder tree with ownership explanations;
- performance budgets and likely hotspots;
- architecture-change rule requiring an accepted ADR plus regression evidence.

`DATA_MODEL.md` must define each durable entity or DTO with:

- stable ID;
- fields, types, constraints, and defaults;
- ownership and lifecycle;
- serialization representation;
- versioning and migration behavior;
- validation and failure handling;
- relationships and deletion semantics;
- examples that do not become hidden production data.

Do not collapse architecture or the data model into a summary paragraph. Use
explicit sections, dependency diagrams or compact mappings when helpful, and
resolve implementation-shaping decisions rather than restating desired
qualities.

## 3. Milestones and gates

Order milestones by dependency, not by visual excitement. A common shape is:

1. foundation;
2. world or primary surface;
3. core interaction;
4. gameplay or business loop;
5. presentation and platform polish;
6. ambient depth;
7. customization;
8. inclusive, social, or advanced content.

Change the names and count to match the product. Never implement a later layer
to make an earlier demo look impressive.

Every milestone section must contain:

1. stable milestone ID and name;
2. objective;
3. user-visible outcome;
4. preconditions;
5. systems to preserve;
6. exact in-scope work;
7. forbidden and deferred scope;
8. acceptance criteria;
9. automated tests;
10. manual and edge-case validation;
11. evidence artifacts and paths;
12. performance/security/accessibility checks where relevant;
13. known-limitations format;
14. binary gate requirements;
15. next milestone only if gate is PASS.

Gate status vocabulary is exactly:

- `NOT RUN`
- `PASS`
- `FAIL`
- `BLOCKED`

Do not use "mostly passed," "provisional pass," or similar ambiguity.

## 4. Dormant goals

Create one goal catalog per milestone or corrective stage. Unless overridden,
create exactly 20 goals.

Use this schema for every entry:

```text
ID:
Title:
Status: DORMANT
Depends on:
Purpose:
Exact scope:
Acceptance criteria:
Tests:
Manual validation:
Evidence:
Forbidden scope:
```

Rules:

- Use stable, sortable IDs such as `M03-G01`.
- Make every goal testable and bounded.
- Do not make goals so small that they are individual file edits.
- Do not duplicate acceptance criteria across goals without assigning an owner.
- The final goal closes the gate; it does not waive failed earlier goals.
- Catalog approval does not activate goals.
- Record `Active implementation goal: NONE` until a separate user request.
- Give every goal a capability-specific title, purpose, scope, tests, and
  evidence. Do not generate `Capability 1` through `Capability 20`.
- Do not duplicate a goal body and change only its ID, title number, or
  dependency.
- Do not use word-count padding or generic boilerplate to satisfy validation.

## 5. Tracking and decisions

`MILESTONE_TRACKER.md` must record:

- planning lock and active goal;
- current milestone or `NONE`;
- completed milestones;
- each gate status;
- automated test status;
- manual validation status;
- known issues;
- deferred work;
- next eligible milestone;
- evidence links;
- last verified commit/build/version;
- last update timestamp and author.

The tracker is a status index, not the place to redefine requirements.

Use one ADR per durable or controversial decision. Each ADR contains:

- status: Proposed, Accepted, Superseded, or Rejected;
- context;
- decision;
- alternatives;
- consequences and risks;
- migration/compatibility impact;
- evidence;
- supersedes/superseded-by links.

Only Accepted ADRs are controlling. Reconcile affected active documents when an
ADR becomes Accepted.

## 6. Testing and evidence

`TESTING_POLICY.md` defines the exact command, environment, and required result
for each relevant layer:

- unit;
- integration;
- contract/schema;
- migration/compatibility;
- end-to-end;
- device/platform;
- accessibility;
- security/privacy;
- performance/profiling;
- visual regression or independent visual audit.

Evidence must identify:

- commit or source revision;
- build identity;
- tool/editor/runtime version;
- target platform/device;
- command and exit result;
- timestamp;
- artifact path;
- hash for immutable captures/builds;
- expected versus observed result.

Screenshots alone do not prove behavior. Tests alone do not prove usability.
Placeholder-only evidence must be labeled as such.

## 7. Risk and completion

`RISK_REGISTER.md` uses stable IDs and records:

- risk;
- likelihood and impact;
- trigger or early warning;
- mitigation;
- contingency;
- owner;
- milestone affected;
- status and evidence.

`DEFINITION_OF_DONE.md` must reject weak completion claims. A milestone is done
only when:

- all acceptance criteria are met;
- required automated tests pass;
- manual and edge-case validation passes;
- evidence comes from the running product where relevant;
- performance, accessibility, security, and device checks pass where required;
- known limitations are documented;
- no forbidden or future scope was introduced;
- the tracker and gate say PASS;
- independent audit requirements, if any, are satisfied.

Planning itself is complete only when validation is recorded, all active
documents agree, and the goal lock remains engaged.

## Minimum anti-placeholder floors

The bundled validator enforces minimum word and section floors for core
documents, ADRs, prompts, and goal fields. These floors exist only to catch
hollow output. Passing them does not establish correctness. Sol Ultra must
still perform a semantic review for specificity, coherence, feasibility,
traceability, and cross-document agreement.
