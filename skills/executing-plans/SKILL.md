---
name: executing-plans
description: Use when you have an approved plan to execute step by step with TDD, review gates, and small atomic commits.
---

# Executing Plans

Drive an approved plan to completion one step at a time. You are
the **orchestrator**: you do not implement steps yourself. Each
step is handed to a fresh `step-executor` coordinator that loads
context, plans the step's commits one chunk at a time, and
dispatches a `step-implementer` subagent per chunk (each writes
tests, implements, verifies that one commit, and commits it),
reviewing every commit as it lands — then returns a compact
summary. You hold only the plan, those summaries, and review
verdicts. This is what keeps long plans from ballooning the main
context: per-step file reads, test output, and diffs never land
here.

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
   directory path and the step number. It is a **coordinator**:
   it loads context, then plans the step's commits **one chunk at
   a time**. For each chunk it dispatches a `step-implementer`
   subagent that writes the tests + code for that single commit
   and verifies it (build/test/lint) green before committing; the
   coordinator then dispatches the `reviewer` over that one
   commit and, if changes are needed, re-dispatches the
   implementer in **fix mode** to amend it in place. So the range
   you receive is already per-commit-verified and
   per-commit-reviewed (1–5 code commits). At this point it
   commits only code — the plan boxes and `step-<N>.md` are NOT
   written yet; they are added later in finalize mode (step 5), so
   the completeness gate reads pure code commits. The coordinator
   itself writes no source or test code.

   **Always end the dispatch prompt with the literal block
   below** (substituting the real step number for `<N>`). This is
   not optional framing — executors otherwise drift and return a
   truncated line like "Build succeeded." instead of a parseable
   summary, leaving you unable to gate review or detect that the
   step never landed. Paste it verbatim as the last thing the
   executor reads:

   ```
   Return the standard STEP summary block as your final message,
   and nothing else:

   STEP <N>: <done | blocked>
   range: <base-sha>..<head-sha>
   chunks: <K>
   changed: <files>
   review-needed: <yes | no — reason>
   summary: <one line>
   blocker: <none | description>
   ```

   It returns exactly that block. If a dispatched executor
   returns anything that is NOT this block — a prose status, a
   bare "Build succeeded.", an empty message — treat the step as
   **not verified**: do not advance. Check the working tree
   (`git status`, `git log`) and re-dispatch the executor to
   finish properly, again ending the prompt with the block above.

2. **If the executor reports `blocked`** — stop. Surface the
   `blocker:` line to the user and wait. Do not retry blindly or
   hand the same step to another executor.

3. **Final completeness gate (commit messages only).** Code
   quality was already covered per-commit inside the coordinator;
   this final pass is NOT a code review. Its only job is to
   confirm the step's commits, taken together, actually deliver
   the step's stated goal. **Read ONLY the commit messages** for
   the step's range — `git log <base>..<head>` subjects and
   bodies (the `range` from the summary). Do NOT read the diff,
   the changed files, or any source code. Compare those messages
   against the step's description and acceptance criteria in
   `plan.md`:
   - If every acceptance criterion for the step is accounted for
     by the commits → the step is complete; proceed.
   - If one or more criteria are not evidenced by any commit →
     the step is incomplete. List exactly which criteria/goals
     are still unmet and hand that list to step 4.

   This gate never inspects or judges code, and it never amends
   or rewrites commits — it only decides done-vs-not-done and
   reports the gaps.

4. **If the gate finds gaps** — re-dispatch the `step-executor`
   in **continue mode**: pass the plan directory, the step
   number, the step's base SHA, and the gap list verbatim. The
   coordinator **continues the step** — it implements the missing
   work as additional code commits (it does NOT amend existing
   commits to satisfy the gate, and it does NOT write notes yet).
   Use the new range it returns, then re-run the completeness gate
   (step 3) over it. Max 3 continue/gate iterations before
   escalating to the user.

5. **Finalize the step (gate approved).** Only once the gate
   passes, re-dispatch the `step-executor` in **finalize mode**:
   pass the plan directory, the step number, and the step's base
   SHA. It flips this step's acceptance boxes in `plan.md`, writes
   `step-<N>.md`, and **amends both into the step's final commit**
   (the last in the series) — never an earlier commit, never a new
   one. This is the only point where the plan and notes are
   committed, so they always ride on the approved final commit.
   Use the new head it returns.

6. **Report progress** — one line: which step finished and
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
the `step-executor` coordinator and the `step-implementer`
subagents it dispatches — never inline in this loop. Inlining
defeats the entire token-isolation design.

CRITICAL: Each step must pass the final completeness gate before
the next step is dispatched. The gate reads ONLY the commit
messages for the step's range and checks them against the step's
acceptance criteria — it never reads code and never amends
commits. Gaps go back to the coordinator in continue mode.

CRITICAL: If an executor reports `blocked`, or a step fails the
completeness gate 3 times, stop and surface to the user. Do not paper over
failures to keep the pipeline moving.

CRITICAL: After auto-compaction or when resuming in a fresh
session, re-read `plan.md` and check which steps' commits
already exist before dispatching — never re-run a step that has
already landed. The executors' `step-*.md` notes and commits are
the source of truth for progress.
