# ProjectPlanning agent rules

These rules apply to every agent and every path in this repository.

## Purpose

Maintain a private, reusable Codex skill that produces deep planning packages
without implementing the planned product. Preserve the skill's Sol Ultra policy,
explicit invocation, evidence integrity, and fail-closed execution lock.

## Required preflight

Before changing behavior:

1. Read `README.md`.
2. Read `docs/METHOD.md`.
3. Read `docs/MODEL_POLICY.md`.
4. Read `docs/VALIDATION.md`.
5. Read the complete `project-planning/SKILL.md`.
6. Read every referenced specification affected by the change.
7. Inspect the current diff and preserve unrelated work.

## Model and authority

Planning-contract decisions must be designed or approved by Sol with Ultra
reasoning. Lower-tier agents may perform bounded, non-overlapping mechanical
checks, inventories, fixture generation, or read-only audits. They may not
weaken gates, redefine the method, approve their own output, or claim a forward
test passed.

The portable Codex schema cannot cryptographically restrict a skill to one
model. Preserve the explicit-invocation policy and honest limitation statement;
never claim stronger enforcement than exists.

## Scope rules

- Do not add project-specific secrets, user emails, credentials, private
  screenshots, archive paths, or proprietary product plans.
- Do not embed a source project's planning package in the skill.
- Sanitized synthetic fixtures are allowed under `evidence/`.
- Do not execute or activate goals in a repository being planned.
- Do not make destructive or external actions implicit.
- Do not allow a generated executor skill to self-approve a gate.
- Do not replace the official `$skill-creator`; integrate with it.
- Do not add dependencies without a clear recurring need.

## Change requirements

Every behavioral change must:

- update the controlling specification;
- keep `agents/openai.yaml` aligned;
- pass the official skill validator;
- compile and exercise bundled scripts;
- pass `scripts/validate_distribution.py`;
- forward-test material workflow changes on an isolated synthetic project;
- record exact commands, results, and limitations;
- update the version when packaging a release.

Mechanical checks are anti-placeholder floors, not semantic approval. Manually
reject padded prose, generic numbered goals, duplicated scopes, hollow ADRs,
weak acceptance criteria, missing evidence, and conflicting active documents.

## Git and release safety

- Keep this repository private unless the owner explicitly authorizes a public
  release.
- Stage only intended files.
- Secret-scan before every commit and release.
- Build the distribution ZIP from the validated `project-planning` folder.
- Verify ZIP entries and SHA-256 after creation.
- Never include `__pycache__`, editor state, temp fixtures, or credentials.
- Use immutable versioned names under `dist/`.

## Completion

A change is complete only when the installed skill and repository copy are
equivalent, validators pass, any required forward test passes both mechanical
and manual quality review, documentation matches behavior, and unresolved
limitations are stated honestly.
