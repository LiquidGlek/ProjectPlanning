# Executor handoff specification

Use this file when ProjectPlanning prepares work for future Codex agents.

## Sol Medium milestone prompt

Create one self-contained prompt per milestone or corrective stage. Use these
headings exactly once and in this order:

1. `Objective`
2. `Preconditions`
3. `Systems to preserve`
4. `Exact implementation scope`
5. `Acceptance criteria`
6. `Tests`
7. `Manual validation`
8. `Evidence required`
9. `Forbidden scope`
10. `Definition of completion`
11. `Only stop when`

Every prompt must:

- name the repository and controlling documents;
- require preflight reading of product intent, architecture, milestones,
  tracker, working rules, goal lock, and accepted ADRs;
- require the tracker to authorize this milestone and all prior gates to PASS;
- authorize inspect, implement, test, fix discovered in-scope defects, validate,
  gather evidence, and finish the whole milestone;
- avoid approval requests after each small step;
- forbid later milestone work, architecture replacement, fake evidence, and
  silent scope expansion;
- require exact test commands, manual cases, performance/security/accessibility
  checks, and immutable running-build evidence;
- require honest FAIL/BLOCKED status if any gate criterion is unmet;
- keep the next milestone locked;
- state the only legitimate stop conditions.

Use this final stop contract:

```text
Only stop when:
- repository identity or safety becomes uncertain;
- requirements conflict and the controlling documents do not resolve them;
- credentials or permissions are required;
- an unauthorized destructive action would be necessary; or
- the milestone genuinely cannot be completed after in-scope diagnosis.
```

## Sol Medium ownership

Sol Medium is the milestone integrator and owns:

- architecture compliance;
- task decomposition;
- shared-file coordination;
- integration;
- defect correction;
- all required tests;
- running-product validation;
- evidence manifest;
- tracker and gate truth;
- final handoff.

It must inspect subagent output and rerun important checks itself. A subagent's
claim is not gate evidence.

## Sol Low worker protocol

Allow up to three Sol Low workers only when tasks are materially independent.
Each assignment must include:

- bounded objective;
- exact owned paths or read-only surfaces;
- inputs and controlling contracts;
- forbidden paths and scope;
- required checks;
- expected artifacts;
- instruction to report inspected/changed files, checks, and uncertainty.

Safe examples include independent asset inventories, isolated test fixtures,
read-only audits, documentation-link checks, or non-overlapping adapters.

Do not delegate:

- architecture decisions;
- shared-scene/shared-schema ownership;
- migration ordering;
- final integration;
- gate status;
- destructive actions;
- security acceptance;
- final visual approval.

Stop or re-scope workers whose paths overlap. More workers are not automatically
faster.

## Selective Turbo policy

Use Turbo only when a measured critical-path task is parallelizable and the
expected wall-clock saving justifies its usage multiplier. Do not use Turbo for
read-only orientation, waiting, broad exploration, integration, or final gate
judgment. Record why Turbo was chosen and compare expected versus observed
benefit.

## Sol Ultra clarification protocol

Allow one narrow, read-only clarification request only after Sol Medium has:

1. read the controlling documents;
2. inspected relevant code and tests;
3. reproduced or isolated the blocker;
4. gathered exact logs/evidence;
5. written two or more plausible interpretations;
6. explained why each interpretation changes implementation materially.

The clarification request must contain:

- one question;
- milestone and exact blocked criterion;
- relevant citations/paths;
- observed evidence;
- competing interpretations;
- consequences of each;
- recommended interpretation if any.

Sol Ultra may answer the question and identify the controlling source. It may
not implement, debug broadly, review the whole milestone, or approve the gate.
Repeated consultations on the same issue are forbidden unless new evidence
materially changes the question.

## Project-specific skills

Create a project-specific skill only for a recurring, high-risk workflow whose
instructions would otherwise be repeatedly reconstructed, such as:

- executing one milestone;
- closing a gate;
- producing assets under a visual bible;
- independent visual auditing;
- one-question blocker clarification.

Give each skill a narrow trigger, fail-closed preconditions, explicit forbidden
scope, and an official validator pass. Do not create a skill merely to restate
one prompt.
