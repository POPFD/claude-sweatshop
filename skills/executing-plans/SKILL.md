---
name: executing-plans
description: Use when you have an approved plan to execute step by step with TDD, review gates, and atomic commits.
---

# Executing Plans

You are an ORCHESTRATOR. You do not write code, run tests,
or review diffs yourself. You walk the plan one step at a
time and dispatch each step to a `step-executor` subagent.
Delegating keeps your context small — all the build, test,
lint, and review noise stays inside the subagent and only a
terse status block comes back.

## Preparation

1. **Read the plan** from `.sweatshop/plans/…`.
2. **Confirm step order** — plans are executed strictly in
   the order steps are listed. No skipping, no reordering.

## Dispatching a step-executor

Each step is one `Agent` tool call with
`subagent_type: "step-executor"`. The prompt MUST contain:

- Step number and title.
- The step's full `What`, `Why`, `Acceptance criteria`, and
  `Files likely involved`, copied verbatim from the plan.
- The absolute path to the plan file.
- A note that the executor must return the structured
  STATUS/STEP/COMMITS/NOTES block and nothing else.

Dispatches run on the main branch — no worktree isolation.
The executor commits directly onto the current branch.

## Execution loop

For each step, in plan order:

1. Dispatch one step-executor and wait for it to return.
2. If `STATUS` is not `success`, STOP and report to the
   user. Do not continue to the next step.
3. Briefly note which step finished and what's next, then
   move to the next step.

## Mid-execution replanning

If a step-executor returns `STATUS: failed` or `blocked`, or
if during execution it becomes clear the plan needs
adjustment:

1. Stop dispatching.
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

CRITICAL: Never execute step work yourself. Always delegate
to a `step-executor` subagent. Your job is dispatch and
progress tracking — the subagent keeps build/test/lint/review
output out of your context.

CRITICAL: Execute steps strictly in order. One step at a
time, no parallel dispatch, no skipping.

CRITICAL: If a step fails, stop and surface to the user. Do
not paper over failures to keep the pipeline moving.

CRITICAL: Keep your own output terse. You coordinate, you
don't narrate. Executors report what they did; your job is
to summarize outcomes, not re-describe them.
