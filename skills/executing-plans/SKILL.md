---
name: executing-plans
description: Use when you have an approved plan to execute step by step with TDD, review gates, and atomic commits.
---

# Executing Plans

Walk through an approved plan one step at a time. Each step
follows a test-first workflow, passes review, and lands as
its own commit.

## Preparation

1. **Read the plan** from `.sweatshop/plans/…`.
2. **Confirm step order** — plans are executed strictly in
   the order steps are listed. No skipping, no reordering.

## Process per step

For each step in the plan, follow this exact sequence:

1. **Gather context** — if the step touches unfamiliar code,
   invoke the `research` skill.
2. **Write tests first** — tests that verify the step's
   acceptance criteria. They should fail at this point.
3. **Implement** — minimum code to make the tests pass. Stay
   scoped to this step only.
4. **Build** — invoke /build.
5. **Test** — invoke /test (the full suite, not only new
   tests).
6. **Lint** — invoke /lint.
7. **Update the plan file** — flip this step's
   acceptance-criteria boxes from `- [ ]` to `- [x]`. Do NOT
   modify any other step's boxes.
8. **Review** — invoke the `requesting-review` skill on the
   step's changes. If changes are requested, apply fixes and
   re-review (max 3 iterations before escalating).
9. **Commit** — invoke /commit-changes. The commit must
   include both code changes and the updated plan file.
10. **Report progress** — one line: which step finished and
    what's next.

## Mid-execution replanning

If during implementation it becomes clear the plan needs
adjustment (step too large, assumptions wrong, new blocker):

1. Stop implementation.
2. Re-plan the remaining steps.
3. Invoke `requesting-review` on the revised plan.
4. Get explicit user approval before continuing.
5. Update and commit the plan file.
6. Resume from the adjusted plan.

## Completion

After every step finishes successfully:

1. Invoke the `verification` skill.
2. Report a completion summary: total steps executed and
   the range of commit SHAs produced.

## Rules

CRITICAL: Execute steps strictly in order. One step at a
time, no parallel execution, no skipping.

CRITICAL: Tests come first. No implementation code before
failing tests exist for it.

CRITICAL: If build, test, or lint fails, fix and re-run. Do
NOT commit broken code.

CRITICAL: Every step must pass review before moving to the
next step.

CRITICAL: If a step fails repeatedly and you cannot resolve
it, stop and surface to the user. Do not paper over failures
to keep the pipeline moving.

CRITICAL: Do NOT modify code unrelated to the current step.
No drive-by refactors, cleanups, or "while I'm here" changes.
