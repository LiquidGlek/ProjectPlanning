# Sol Ultra model policy

## Policy

ProjectPlanning is intended only for the Sol model at Ultra reasoning. Deep
planning requires sustained cross-document consistency, adversarial review,
architecture judgment, and the ability to notice when mechanically complete
output is semantically hollow.

The skill is not intended for:

- ordinary implementation;
- small feature planning;
- generic task lists;
- implicit invocation;
- lower reasoning settings;
- delegation of core planning judgment.

## Enforceable boundary

The skill's `agents/openai.yaml` sets:

```yaml
policy:
  allow_implicit_invocation: false
```

The skill body refuses execution when runtime context identifies a model or
reasoning effort other than Sol Ultra.

Some Codex execution surfaces do not expose the selected model and effort to
the agent. In that case, portable skills cannot cryptographically verify model
identity. ProjectPlanning requires an explicit `$project-planning` invocation
and treats that as the user's confirmation that Sol Ultra was selected.

This limitation must always be disclosed. Do not market the skill as
technically inaccessible to every other model.

## Subagents

Sol Ultra remains the planning owner. It may delegate bounded, independent,
mechanical work such as:

- repository inventories;
- link and ID audits;
- archive hash verification;
- read-only source extraction;
- synthetic fixture generation;
- independent semantic critique.

Subagents cannot decide architecture, reinterpret product intent, weaken a
gate, approve the final package, or use their own output as independent
evidence.

## Forward testing

Material changes are tested with a fresh Sol Ultra task on an unrelated
synthetic project in an isolated directory. If runtime metadata is hidden, the
test request must explicitly invoke `$project-planning`.

A forward test passes only when:

- the bundled validator passes;
- the package is project-specific rather than boilerplate;
- goals are distinct;
- architecture and ADRs are substantive;
- links and evidence contracts are usable;
- the goal lock remains engaged;
- no product implementation or external publication occurred.
