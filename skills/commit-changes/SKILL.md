---
name: commit-changes
description: Use when the user asks to commit, save changes, or create a git commit. Handles staging, message formatting, and signoff.
allowed-tools: Bash(git add:*), Bash(git diff:*), Bash(git status:*), Bash(git log:*), Bash(git commit:*)
---

# Commit changes to the repository

The tagline of the commit should follow the following example:
area: An example commit tagline

Then a multiline paragraph explaining first why we're changing
things, what has been changed and further technical information.

CRITICAL: No line should be greater than 85 characters. Always
fill lines up to 85 characters before wrapping to the next line
— do not break early. If the tag line needs to exceed 85
characters then use ... suffixed.

CRITICAL: Use --signoff but DO NOT manually add ANY "Signed-off-by:" lines
in the commit message. Let git --signoff handle it automatically. This will
use the configured git user.name and user.email from .gitconfig.

CRITICAL: There is no co-authoring

CRITICAL: Never use "user@example.com" or any email addresses in the commit message.

CRITICAL: Do NOT chain `cd <path> && git ...` in a single Bash call — compound
commands with `cd` + `git` trigger bare-repository-attack permission prompts.
If the repo is not the current working directory, use `git -C <path> ...`
instead (e.g. `git -C /path/to/repo add ...`, `git -C /path/to/repo commit ...`).
Run each git invocation as its own Bash call.
