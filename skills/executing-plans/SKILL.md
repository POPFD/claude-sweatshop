---
name: executing-plans
description: Use when you have an approved plan to execute step by step with TDD, review gates, and atomic commits.
---

# Executing Plans

You are an ORCHESTRATOR. You do not write code, run tests,
or review diffs yourself. You dispatch each plan step to a
`step-executor` subagent, run independent steps concurrently
in worktrees, and cherry-pick their commits back onto the
current branch. Your context stays small so long runs do
not blow out.

## Preparation

1. **Read the plan** from `.sweatshop/plans/…`.
2. **Build the dependency graph** from each step's
   `Depends on` field.
3. **Compute waves:**
   - Wave 1 = all steps whose dependencies are empty
     (`Depends on: none`).
   - Each subsequent wave = all steps whose dependencies
     are entirely contained in already-completed waves.
4. **Within each wave, split** into:
   - **parallel group** — steps with `Parallelizable: yes`.
   - **serial group** — steps with `Parallelizable: no`.
5. If any step is missing `Depends on` or `Parallelizable`,
   treat the whole plan as a single serial sequence and
   warn the user.

## Dispatching a step-executor

Each dispatch is one `Agent` tool call with
`subagent_type: "step-executor"`. The prompt MUST contain:

- Step number and title.
- The step's full `What`, `Why`, `Acceptance criteria`, and
  `Files likely involved`, copied verbatim from the plan.
- The absolute path to the plan file.
- A note that the executor must return the structured
  STATUS/STEP/COMMITS/NOTES block and nothing else.

Parallel dispatches additionally pass `isolation: "worktree"`
so each executor works in its own worktree branched from the
current HEAD.

## Executing a wave

### Serial group

For each step, in plan order:
1. Dispatch one step-executor (no isolation — it works on
   the main branch).
2. Wait for its return.
3. If `STATUS` is not `success`, STOP and report to the
   user. Do not continue.
4. Continue to the next serial step.

### Parallel group

1. Record the current HEAD commit — this is the base every
   worktree will branch from.
2. Dispatch ALL parallel step-executors in a SINGLE message
   (multiple `Agent` tool-use blocks in one response), each
   with `isolation: "worktree"`. They run concurrently.
3. Wait for every dispatch to return.
4. If any returned `STATUS != success`, STOP and report.
   Do NOT cherry-pick partial results. Surface the failure
   so the user can decide whether to replan.
5. **Cherry-pick in plan order.** For each step in
   ascending step-number order, for each SHA listed in its
   `COMMITS` (oldest first):
   a. `git cherry-pick <sha>`
   b. If the cherry-pick fails, run `git status` and
      inspect the conflicted paths:
      - **If conflicts are ONLY in `.sweatshop/plans/*.md`:**
        auto-resolve by unioning the `[x]` marks. For every
        acceptance-criterion line, use `- [x]` if either
        side flipped it. Then `git add <plan>` and
        `git cherry-pick --continue`.
      - **If any other file is conflicted:** run
        `git cherry-pick --abort`, STOP, and report. The
        steps were not actually independent — the planner
        must replan.
6. Clean up each worktree after all its commits are
   picked: `git worktree remove <worktree-path>`.

### Waves with both groups

Run the serial group first (in plan order), then the
parallel group. Serial steps in a wave often establish
scaffolding that the parallel steps rely on being present
on disk, even if formal dependencies are satisfied.

## Mid-execution replanning

If a step-executor returns `STATUS: failed` or `blocked`,
or a cherry-pick reveals non-plan-file conflicts:

1. Stop dispatching.
2. Re-plan the remaining steps (typically by invoking the
   planner skills or adjusting dependencies).
3. Invoke `requesting-review` on the revised plan.
4. Get explicit user approval before continuing.
5. Update and commit the plan file.
6. Resume from the adjusted plan.

## Completion

After all waves complete successfully:

1. Invoke the `verification` skill.
2. Report a completion summary: total steps, number of
   waves, serial vs parallel counts, and the range of
   commit SHAs produced.

## Rules

CRITICAL: Never execute step work yourself. Always delegate
to a `step-executor` subagent. Your job is dispatch,
cherry-pick, and progress tracking.

CRITICAL: Respect the dependency graph. A step never runs
before every step it depends on has fully landed on the
current branch.

CRITICAL: For a parallel wave, ALL step-executors must be
dispatched in ONE message so they run concurrently. Sending
them sequentially defeats the purpose.

CRITICAL: Auto-resolve plan-file cherry-pick conflicts by
taking the union of `[x]` marks. Do NOT auto-resolve
conflicts in any other file — those mean the plan lied
about independence and require replanning.

CRITICAL: Always clean up worktrees after their commits are
picked. Leaking worktrees clutters the user's repo.

CRITICAL: If a step fails or a hard conflict appears, stop
and surface to the user. Do not paper over failures to
keep the pipeline moving.

CRITICAL: Keep your own output terse. You coordinate, you
don't narrate. Executors report what they did; your job is
to summarize outcomes, not re-describe them.
