# Security and privacy

## Private repository boundary

This repository is private. The release ZIP is for approved collaborators only.
Do not attach it to public posts, public issues, or untrusted file-sharing
services.

## Forbidden content

Never commit:

- API keys, OAuth tokens, passwords, cookies, session exports, or private keys;
- personal email addresses or account recovery data;
- private product screenshots or mockups;
- proprietary project plans, source, evidence, or archive manifests;
- absolute user-specific paths;
- customer, household, employee, or collaborator personal data;
- GitHub invitation URLs or access tokens.

Synthetic forward-test projects must use invented names and data.

## Pre-commit review

Before staging:

1. inspect `git status -sb`;
2. inspect every staged path;
3. search case-insensitively for project names, email patterns, token prefixes,
   home-directory paths, and common secret markers;
4. inspect archives by entry name and extract to an isolated directory when
   content verification is required;
5. run distribution validation;
6. verify the repository remains private after push.

Automated secret scanning supplements but does not replace manual review.

## Public-release preparation

If the owner later authorizes open source:

- create a separate sanitized public repository;
- add a deliberate open-source license;
- remove the proprietary notice and private evidence;
- replace internal paths and organization assumptions;
- add contribution and security policies;
- verify every commit in public history, not only the current tree;
- publish only after explicit final authorization.

Making a private repository public can expose its complete reachable history.
Do not change visibility as a shortcut.
