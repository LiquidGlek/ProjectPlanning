# r/codex launch draft

## Status

**DRAFT ONLY — DO NOT PUBLISH**

Target: `r/codex`

Suggested flair: `Showcase`

The owner should post manually after rereading the current subreddit rules.
Automated posting is intentionally forbidden.

## Suggested title

I built a Sol Ultra planning skill that keeps Codex out of the code until the project is actually executable

## Copy-ready body

Disclosure: I built this. It is a private beta right now—there is no paid
product, public download, or sales link in this post.

I kept running into the same failure mode with long Codex projects: the agent
could write code faster than the project could resolve its own intent. A vague
plan turned into plausible architecture, later features started early, and a
milestone was called "done" because it compiled or produced a convincing
screenshot.

So I built **ProjectPlanning**, a Codex skill reserved for Sol at Ultra
reasoning. It does one job: turn a project idea, mockup, failed prototype, or
existing repository into a complete execution contract—and then leave
implementation locked.

It is not a normal to-do-list generator. It produces:

- product intent, non-goals, and source/reference precedence;
- architecture, state ownership, data contracts, persistence, migrations,
  security, observability, folder ownership, and performance budgets;
- dependency-ordered milestones with binary `PASS / FAIL / BLOCKED / NOT RUN`
  gates;
- 20 dormant, independently verifiable goals per milestone by default;
- one ready-to-run Sol Medium implementation prompt per milestone;
- strict test, manual-validation, edge-case, and running-evidence requirements;
- ADRs, risk register, tracker, Definition of Done, and permanent `AGENTS.md`
  guardrails;
- visual bibles that describe every object, position, silhouette, material,
  light, animation, and UI state when concept art is involved;
- safe archive/rebuild rules when replacing a failed repository;
- optional project-specific executor/auditor skills created through the
  official skill creator.

The important part is that it writes:

```text
Lock state: LOCKED
Active implementation goal: NONE
```

Creating the plan does not start M01.

I know an Agent Skill is ultimately instructions in files. The useful part here
is the contract plus the validator and the way it fails closed.

That validator caught me cutting a corner during its own independent test. The
first synthetic Raspberry Pi + Flutter project had the right counts—3
milestones, 60 goal IDs, and 3 executor prompts—but manual review found
one-paragraph architecture and 60 generic numbered "capabilities." After I
strengthened the checks, that same output failed with 477 specific validation
errors.

A clean rerun then passed with:

- 21 planning documents;
- 3 dependency-ordered milestones;
- 60 distinct dormant goals;
- 3 full Sol Medium prompts;
- 1 substantive ADR;
- 12 stable risks;
- 0 unresolved placeholders;
- 6 verified internal links;
- implementation still locked and untouched.

The validator now rejects shallow core documents, missing architecture/testing
sections, generic goal titles, duplicated scopes, weak prompt sections, hollow
ADRs, missing risk depth, broken links, and an unlocked goal state. Sol Ultra
still has to perform a semantic review because word counts can never prove a
good plan.

I am looking for **5–10 private testers** with genuinely different projects:
greenfield apps, rebuilds, games, hardware, services, or troubled repositories.
I am especially interested in where it over-plans, what it fails to specify,
and whether a later Sol Medium agent can execute a milestone without inventing
core architecture.

If you would test it, comment with:

1. your stack;
2. greenfield, rebuild, transition, or recovery;
3. the planning failure you most want it to prevent.

Please do not post private code, credentials, customer information, or
proprietary screenshots. I can provide selected testers a private ZIP or
repository access after we agree on a safe test.

The biggest design question I still have for the community: should the generic
core eventually be open-source, while project-specific plans and evidence stay
private?

## Pre-post checklist

- Reopen <https://www.reddit.com/r/codex/about/rules.json>.
- Confirm `Showcase` is still the correct flair.
- Search recent posts for a duplicate ProjectPlanning announcement.
- Ensure the body contains no private repository URL or personal data.
- Post manually; do not use a bot or browser automation.
- Do not ask for upvotes.
- Do not publish the private ZIP in comments.
- If removed, do not repost without moderator guidance.
