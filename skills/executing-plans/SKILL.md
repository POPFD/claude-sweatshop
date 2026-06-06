---
name: executing-plans
description: Use when you have an approved plan to execute step by step with TDD, review gates, and small atomic commits.
---

# Executing Plans

Drive an approved plan to completion one step at a time. You are
the **orchestrator**: you do not implement steps yourself. Each
step is handed to a fresh `step-executor` subagent that does the
reading, test-first implementation, verification, note-writing,
and commits in its own throwaway context — then returns a
compact summary. You hold only the plan, those summaries, and
review verdicts. This is what keeps long plans from ballooning
the main context: per-step file reads, test output, and diffs
never land here.

## Plan directory layout

```
.sweatshop/plans/<plan-name>/
  plan.md           # the plan file
  step-1.md         # step notes (written by the executor)
  step-2.md
  ...
```

`<plan-name>` is the slug chosen when the plan was written
(e.g. `2026-04-15-add-auth`). The plan file is always `plan.md`;
step notes are siblings named `step-<N>.md`.

## Preparation

1. **Locate the plan directory** — find
   `.sweatshop/plans/<plan-name>/` and read `plan.md` once.
2. **Confirm step order** — steps run strictly in listed order.
   No skipping, no reordering, no parallel execution.

You do not need to read the source files or the `step-*.md`
notes yourself — each executor reads what it needs into its own
context.

## Process per step

For each step `<N>` in order:

1. **Dispatch the `step-executor` agent.** Give it the plan
   directory path and the step number. Inside its own context it
   writes failing tests, implements, verifies once, updates the
   plan and notes, and lands the work as a coherent series of
   small commits (2–5 chunks; final chunk carries `plan.md` and
   `step-<N>.md`). It returns:

   ```
   STEP <N>: <done | blocked>
   range: <base-sha>..<head-sha>
   chunks: <K>
   changed: <files>
   review-needed: <yes | no — reason>
   summary: <one line>
   blocker: <none | description>
   ```

2. **If the executor reports `blocked`** — stop. Surface the
   `blocker:` line to the user and wait. Do not retry blindly or
   hand the same step to another executor.

3. **Review (risk-gated).** If `review-needed: yes`, invoke the
   `requesting-review` skill against the step's commit **range**
   (`<base>..<head>` from the summary), passing the `changed`
   files and the step's acceptance criteria. A step is several
   commits, so review the whole range, not just `HEAD`. Skip
   review entirely when the executor returned
   `review-needed: no`.

4. **If review requests changes** — re-dispatch the
   `step-executor` in **fix mode**: pass the plan directory, the
   step number, the step's base SHA, and the reviewer's feedback
   verbatim. It lands the fixes as additional small commits and
   returns the new head. Then re-invoke `requesting-review` over
   the updated range. Max 3 fix/review iterations before
   escalating to the user.

5. **Report progress** — one line: which step finished and
   what's next. Do NOT prompt the user about compaction; step
   notes carry state across it on their own.

## Mid-execution replanning

If an executor reports the plan itself is wrong (step too large,
assumptions invalid, a new blocker that changes scope):

1. Stop dispatching steps.
2. Re-plan the remaining steps.
3. Invoke `requesting-review` on the revised plan.
4. Get explicit user approval before continuing.
5. Commit the updated plan file.
6. Resume from the adjusted plan.

## Completion

After the last step finishes successfully:

1. Invoke the `verification` skill for a final full-project
   pass.
2. Report a completion summary: total steps executed and the
   overall range of commit SHAs produced.

## Rules

CRITICAL: Execute steps strictly in order. One step at a time,
no skipping, no parallel execution.

CRITICAL: You orchestrate; you do not implement. Every step's
code, tests, verification, notes, and commits are produced by
the `step-executor` subagent — never inline in this loop.
Inlining defeats the entire token-isolation design.

CRITICAL: Each step must pass review (when review-needed) before
the next step is dispatched. Review the full commit range the
executor reports, since a step lands as several commits.

CRITICAL: If an executor reports `blocked`, or a step fails
review 3 times, stop and surface to the user. Do not paper over
failures to keep the pipeline moving.

CRITICAL: After auto-compaction or when resuming in a fresh
session, re-read `plan.md` and check which steps' commits
already exist before dispatching — never re-run a step that has
already landed. The executors' `step-*.md` notes and commits are
the source of truth for progress.
