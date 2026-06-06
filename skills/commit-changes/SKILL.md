---
name: commit-changes
description: Use when the user asks to commit, save changes, or create a git commit. Handles staging, message formatting, and signoff.
allowed-tools: Bash(git add:*), Bash(git diff:*), Bash(git status:*), Bash(git log:*), Bash(git commit:*)
---

# Commit changes

Format:
```
area: short tagline (use "..." suffix if it must exceed 85 chars)

Why-then-what paragraph(s). Wrap at 85 chars; fill lines fully
before wrapping.
```

Rules:
- Use `git commit --signoff`. Do NOT add manual `Signed-off-by:`
  lines or any email addresses; signoff handles it.
- No co-authoring trailers.
- If the repo isn't cwd, use `git -C <path> ...` as separate
  Bash calls. Never chain `cd <path> && git ...` — it triggers
  bare-repo permission prompts.
- `--signoff` is load-bearing, not just policy: a routing hook
  blocks any `git commit` that creates a commit without it, so
  that direct commits are forced through this skill. (Mechanical
  history edits — `--amend`, `--fixup`, `--squash` — are exempt.)
