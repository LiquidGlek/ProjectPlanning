# Community support plan

## Status and boundary

This is a plan only. No Reddit post, comment, vote, direct message, moderator
message, public repository, signup form, or public release is authorized by
this document.

The first public communication should invite a small private beta. It must not
expose this private repository, its release ZIP, source-project information, or
collaborator data.

## Positioning

ProjectPlanning should be positioned around one concrete problem:

> Coding agents can implement faster than an ambiguous project can safely absorb
> change. Trust the planning and evidence workflow, not a model's confidence.

It is not another task-list generator. Its differentiators are:

- implementation remains locked while planning is produced;
- product intent and source precedence become repository contracts;
- milestones are dependency layers with binary gates;
- goals and executor prompts are capability-specific and verifiable;
- visual references receive stable, reconstructable specifications;
- repository retirement and destructive actions are identity-checked;
- a deterministic validator rejects shallow documents and duplicated goals;
- a semantic Sol Ultra audit remains required after mechanical validation.

## Reddit compliance snapshot

Target: `r/codex`

Recommended flair: `Showcase`

Rules reviewed on 2026-07-29:

- the post must be directly related to Codex;
- use the correct flair;
- be respectful and avoid low-effort claims;
- check recent posts before posting;
- do not use bots;
- avoid spam and personal/confidential information.

Source: <https://www.reddit.com/r/codex/about/rules.json>

The owner should submit the final post manually. ProjectPlanning or another
agent must not automate submission because the community explicitly prohibits
bot activity. If moderators remove the post, do not repost it. Read the removal
reason and use modmail only if clarification is appropriate.

## Private beta cohort

Start with 5–10 testers rather than a broad release.

Select for diversity:

- greenfield, clean rebuild, transition, and recovery projects;
- desktop, web, mobile, game, hardware, and service stacks;
- solo and small-team workflows;
- projects with at least three meaningful dependency layers;
- users willing to report failures rather than only successful screenshots.

Do not ask testers to send proprietary source, credentials, customer data, or
private screenshots. They should run the skill locally and share sanitized
outputs or specific failure descriptions.

Distribution options, in order:

1. grant named trusted testers read access to a dedicated private beta
   repository;
2. send the versioned ZIP through an approved private channel;
3. later create a sanitized public repository only after explicit approval.

## Onboarding

Give each tester:

- the versioned ZIP and SHA-256;
- installation instructions;
- the Sol Ultra model-policy limitation;
- one copy-ready invocation prompt;
- the expected output tree;
- the planning-only and `LOCKED` boundary;
- the issue/feedback template;
- a reminder to keep their product secrets local.

Ask testers to use a fresh task and preserve their original repository.

## Feedback template

Collect:

- ProjectPlanning version;
- Codex surface, model, and reasoning level;
- project type and mode;
- existing repository or greenfield;
- number of milestones generated;
- validator result and exact failures;
- whether goals were distinct and executable;
- missing architecture or product decisions;
- unnecessary or excessive planning;
- scope drift caught or missed;
- incorrect assumptions;
- clarification count;
- total planning wall time and approximate usage;
- first implementation milestone outcome, if later authorized;
- sanitized evidence links;
- severity and reproducibility.

## Support loop

### First 48 hours

- answer every substantive question manually;
- group repeated questions into an FAQ;
- acknowledge confirmed defects without defensiveness;
- do not promise a fix date before reproducing the issue;
- invite detailed testers privately without soliciting sensitive data.

### First two weeks

- triage issues into model policy, triggering, planning depth, validation,
  repository safety, visuals, executor handoff, and documentation;
- reproduce each high-severity issue on a synthetic fixture;
- publish one evidence-based update only if subreddit rules and cadence support
  it;
- version every behavioral change;
- retain failed forward tests as sanitized learning evidence.

### Ongoing

- maintain a small compatibility matrix;
- run at least one unrelated forward test per material release;
- track false positives and false negatives from the validator;
- preserve an honest limitations section;
- keep private support sustainable before expanding the cohort.

## Success metrics

Use quality metrics, not post impressions alone:

- at least 5 completed independent planning runs;
- at least 4 different project categories;
- 100% of runs keep the goal lock engaged;
- zero destructive actions against ambiguous repositories;
- zero private-data leaks;
- every mechanical PASS receives semantic review;
- fewer than 10% generic or duplicated goals after validation;
- tester-reported architecture clarity of at least 4/5;
- documented resolution or disposition for every severe defect;
- evidence that at least two later Sol Medium milestones could execute without
  inventing core architecture.

Community metrics are secondary:

- substantive comments;
- qualified tester requests;
- completed feedback reports;
- repeat testers;
- issue-to-resolution time;
- percentage of feedback that changes the skill.

Do not buy votes, ask employees to astroturf, mass-message users, or repost the
same promotion.

## Public-release gate

Consider open source only after:

- private beta quality metrics pass;
- private identifiers and all reachable Git history are scrubbed;
- the generic package is separated from private evidence;
- an explicit license is selected;
- contribution and security policies exist;
- installation is tested on a clean account;
- the owner explicitly authorizes public visibility.

Until then, the Reddit call to action is private testing and discussion, not a
download or sales link.
