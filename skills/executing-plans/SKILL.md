---
name: executing-plans
description: Use when you have an approved plan to execute step by step with TDD, review gates, and atomic commits.
---

# Executing Plans

Walk through an approved plan one step at a time. Each step
follows a test-first workflow, passes review, and lands as
its own commit.

## Process per step

For each step in the plan, follow this exact sequence:

1. **Gather context** — optionally invoke the `research`
   skill if the step touches unfamiliar code.
2. **Write tests first** — create tests that verify the
   step's acceptance criteria. The tests should fail at
   this point.
3. **Implement** — write the minimum code to make the tests
   pass. Keep changes focused on this step only.
4. **Build** — invoke /build to verify compilation.
5. **Test** — invoke /test to verify all tests pass (not
   just the new ones).
6. **Lint** — invoke /lint to verify code quality.
7. **Update the plan** — mark this step's acceptance
   criteria as complete: change `- [ ]` to `- [x]`. Only
   modify criteria for the current step.
8. **Review** — invoke `requesting-review` on the step's
   changes. If changes requested, fix and re-review.
9. **Commit** — invoke /commit-changes. The commit includes
   both code changes and the updated plan file.
10. **Report progress** — briefly state which step finished
    and what's next.
11. **Move to next step.**

## Execution rules

CRITICAL: Execute steps strictly in order. Do not skip steps
or execute steps in parallel.

CRITICAL: Tests come first. Do not write implementation code
before tests exist for it.

CRITICAL: If build, test, or lint fails, fix the issue and
re-run. Do not commit broken code.

CRITICAL: Every step must be reviewed before moving to the
next step.

CRITICAL: If a step fails repeatedly (build/test/lint won't
pass), stop and report the issue to the user. Do not continue
to the next step.

CRITICAL: Do not modify code unrelated to the current step.
No drive-by refactors, no cleanups, no "while I'm here"
changes.

## Mid-execution replanning

If during implementation it becomes clear the plan needs
adjustment (e.g., a step is too large or assumptions were
wrong):

1. Stop implementation.
2. Re-plan the remaining steps.
3. Invoke `requesting-review` on the revised plan.
4. Get user approval before continuing.
5. Update the plan file and commit.

## Completion

After all steps are complete:

1. Invoke the `verification` skill to confirm everything
   passes.
2. Report a completion summary — what was accomplished
   across all steps.
