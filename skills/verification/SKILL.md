---
name: verification
description: Use before claiming work is complete, fixed, or passing. Runs build, test, lint and confirms all acceptance criteria are met.
---

# Verification

Run all validation checks and confirm acceptance criteria
before claiming work is done. Prove it works — don't just
say it does.

## Process

1. **Run /build** — verify compilation succeeds.
2. **Run /test** — verify all tests pass (not just new ones).
3. **Run /lint** — verify code quality checks pass.
4. **Check acceptance criteria** — read the plan file and
   verify every acceptance criterion for completed steps
   is checked off (`- [x]`).
5. **Check git status** — verify no uncommitted changes
   remain.
6. **Report results** — present clear evidence of each
   check passing.

## If anything fails

- Report exactly what failed with full output.
- Do NOT claim work is complete.
- Do NOT paper over failures or retry silently.
- Surface the failure to the user with enough context to
  diagnose.

## Rules

CRITICAL: Never claim "all tests pass" without actually
running them and seeing the output.

CRITICAL: Never claim "build succeeds" without actually
building and seeing the output.

CRITICAL: If a check was skipped (e.g., no linter detected),
state that explicitly rather than omitting it.

CRITICAL: Run checks against the full project, not just the
changed files. Regressions happen in untouched code.
