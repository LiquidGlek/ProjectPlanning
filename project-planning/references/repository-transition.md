# Repository transition specification

Read this file only when ProjectPlanning involves an existing repository,
replacement, clean rebuild, archive, retirement, online deletion, publication,
or collaborator access.

## Identify before acting

Verify and record:

- resolved absolute repository path;
- repository name and product identity;
- Git root and worktree relationship;
- owner and every remote URL;
- HEAD commit and current branch;
- local branches and remote-tracking branches;
- tags;
- submodules, Git LFS, worktrees, and nested repositories;
- dirty, staged, untracked, and ignored state;
- expected sibling projects that must not be touched.

Stop if identity is ambiguous. Never identify a repository from its folder name
alone.

## Archive completely

Place the archive outside the active workspace. Preserve:

- complete Git object history and refs in a verified bundle or mirror;
- branches and tags;
- worktree contents including staged, unstaged, and untracked changes;
- ignored assets needed to reproduce the project;
- LFS objects and submodule identity where used;
- screenshots, design references, audits, documentation, tests, and build
  instructions;
- file names, timestamps where material, and permission metadata where needed.

Do not rely on a Git bundle alone to preserve dirty or ignored work.

Create an archive manifest containing:

- original repository path and name;
- owner and remote URLs;
- archive location and timestamp with timezone;
- HEAD commit and branch;
- branches and tags;
- dirty working-tree summary;
- submodule/LFS status;
- included auxiliary materials;
- file count and total bytes for the worktree payload;
- hashes for the manifest and major archive artifacts;
- verification commands and results;
- known omissions.

Verify before retirement:

- archive paths exist outside the active workspace;
- hashes recompute;
- Git bundle or mirror passes native verification;
- expected refs are present;
- extracted or enumerated payload matches file count and bytes;
- a representative sample includes dirty, ignored, design, and test artifacts.

## Treat online deletion as a separate destructive action

Delete an online repository only when the user explicitly authorizes deletion
and all of these are verified immediately before the call:

- owner;
- repository name;
- canonical remote URL;
- product identity;
- explicit exclusions named by the user;
- archive completeness;
- authenticated account;
- token permission required by the provider.

Use the provider's precise API/CLI target. Do not use a broad organization,
wildcard, or inferred repository. If permission is missing, record the exact
HTTP/provider error and required scope. Continue non-destructive planning if
safe. Never state or imply deletion succeeded when it did not.

## Retire the local project safely

After verified archive and only when authorized:

- resolve the exact active development path;
- verify it is not the archive and not a parent of the archive;
- verify no other worktree or project shares the target;
- prefer a recoverable move to a clearly named retired location when the user
  did not explicitly require permanent deletion;
- remove only the verified old project from the active development location;
- do not reuse the old repository as the new foundation.

Report what moved or was removed and whether it is recoverable.

## Establish a clean replacement

For a clean rebuild:

- create a new repository with no old Git ancestry;
- prevent the retired remote from being added accidentally;
- add product and agent guardrails before implementation;
- classify old material in an asset disposition register:
  `REUSE`, `RECREATE`, `REFERENCE_ONLY`, or `RETIRE`;
- require provenance, license, quality, format, and compatibility evidence for
  every `REUSE` decision;
- default broken, low-quality, generated-runtime, or architecture-coupled
  assets to `RECREATE` or `RETIRE`.

Create or publish a remote and invite collaborators only with explicit
authorization. Verify remote visibility, default branch, collaborator
permission, and exact pushed commit. A pending invitation is not accepted
access.
