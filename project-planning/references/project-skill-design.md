# Project-specific skill design

Use this specification only when the user requests reusable Codex skills or a
recurring, high-risk workflow clearly warrants one.

## Reuse the official creator

Invoke `$skill-creator` and read its current `SKILL.md` completely before
creating or modifying a skill. Do not copy or fork the system skill creator
into ProjectPlanning. Its official initializer, metadata generator, validator,
and packaging conventions remain authoritative.

ProjectPlanning owns the workflow contract and project boundaries. The system
skill creator owns skill structure and validation mechanics.

## Plan the suite before creating it

Create `docs/SKILL_PLAN.md` with one row per proposed skill:

- skill name and display name;
- recurring problem;
- exact trigger phrases and non-triggers;
- authorized model/reasoning level;
- preconditions and controlling documents;
- allowed actions and tools;
- forbidden scope;
- inputs and outputs;
- evidence obligation;
- whether it may edit or is read-only;
- whether it may approve a gate;
- dependencies on other skills;
- installation and portable source paths;
- validator and forward-test status.

Reject candidates that merely restate one prompt, overlap another skill, or
have no repeatable workflow.

## Prefer separated responsibilities

A robust project commonly benefits from a small suite such as:

- **run one milestone:** implementation from preflight through evidence;
- **close one gate:** independent test/build/evidence qualification;
- **produce constrained assets:** art/content under provenance and budgets;
- **audit visuals or behavior:** read-only, independent judgment;
- **clarify one blocker:** one narrow, read-only architecture/product answer.

Do not combine executor and independent auditor authority in one invocation.
No skill may self-approve its own output.

## Write fail-closed skills

Every project skill must:

- have a narrow, accurate description that includes triggers and non-triggers;
- read required project documents before acting;
- verify the tracker authorizes the exact stage;
- preserve architecture and unrelated user work;
- name allowed paths and destructive boundaries;
- state exact evidence and tests;
- report failure honestly;
- block later scope when a gate fails;
- avoid hidden implementation during planning;
- define the only legitimate stop conditions.

Use `policy.allow_implicit_invocation: false` for destructive, gate-closing,
clarification, or other high-risk skills. A model restriction is
instruction-level unless the current Codex skill schema explicitly supports an
enforceable model policy; document that limitation rather than pretending.

## Create, validate, and forward-test

For each authorized skill:

1. Run the official `init_skill.py`.
2. Keep `SKILL.md` concise and place detailed contracts in one-level
   `references/` files.
3. Add scripts only for repeated deterministic checks.
4. Generate matching `agents/openai.yaml`.
5. Run official `quick_validate.py`.
6. Compile and execute every bundled script on representative safe fixtures.
7. Forward-test complex skills with an independent agent using a realistic
   request and isolated test directory.
8. Review semantic quality; a mechanical PASS is insufficient.
9. Remove test residue and secret-scan the portable package.
10. Record exact results in `docs/SKILL_PLAN.md` and planning validation.

Keep an installed copy in the user's Codex skills directory only when
authorized. Keep a versioned portable copy in the project or a dedicated
private skills repository when requested. Verify the two copies are byte-for-
byte equivalent or document intentional differences.

## Preserve the execution lock

Creating skills does not authorize their use on the product. Leave:

```text
Lock state: LOCKED
Active implementation goal: NONE
```

Skill forward tests must use synthetic or isolated fixtures and must not edit
the real product runtime unless the user separately authorizes implementation.
