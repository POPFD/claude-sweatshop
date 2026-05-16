---
name: executing-plans
description: Use when you have an approved plan to execute step by step with TDD, review gates, and atomic commits.
---

# Executing Plans

Walk through an approved plan one step at a time. Each step
follows a test-first workflow, passes review, and lands as
its own commit.

## Plan directory layout

Plans live in their own directory:

```
.sweatshop/plans/<plan-name>/
  plan.md           # the plan file
  step-1.md         # step 1 notes (produced as step 1 lands)
  step-2.md         # step 2 notes
  ...
```

`<plan-name>` is the slug chosen when the plan was written
(e.g. `2026-04-15-add-auth`). The plan file is always named
`plan.md` inside that directory; step notes are siblings
named `step-<N>.md`.

## Preparation

1. **Locate the plan directory** — find
   `.sweatshop/plans/<plan-name>/` and read `plan.md`.
2. **Confirm step order** — plans are executed strictly in
   the order steps are listed. No skipping, no reordering.

## Orchestration model

The main thread is an **orchestrator**, not an implementer. The
heavyweight work per step (research, edits, test runs,
verification output) happens inside an implementation subagent
so it never enters the main thread's context. The main thread
handles review dispatch and the commit — Claude Code does not
allow subagents to spawn their own subagents, so review must
stay at this level.

The step-notes file is the durable handoff between subagent and
main thread, and between steps.

## Process per step

For each step in the plan:

1. **Verify orientation (cheap).** Confirm `plan.md` exists and
   identify the next pending step number. If you have lost
   track after compaction, list
   `.sweatshop/plans/<plan-name>/step-*.md` to find the highest
   N already on disk; the next step is N+1. Do NOT re-read
   prior step notes from the main thread — that is the
   subagent's job.

2. **Dispatch the implementation subagent.** Invoke the Agent
   tool (subagent_type: `claude`) using the prompt template
   below. The subagent owns: research, failing tests,
   implementation, verification, plan-file box flips, and the
   step-notes file. It stops before review and commit.

3. **Read the returned step notes.** Read only
   `.sweatshop/plans/<plan-name>/step-<N>.md` — not the diff,
   not test output, not prior notes. Run `git diff --stat` for
   a quick scope check.

4. **Review (risk-gated).** Invoke the `requesting-review`
   skill ONLY when the step is non-trivial. Skip review for:
   - Pure docs/comment changes.
   - Test-only additions where the test follows existing
     patterns.
   - Mechanical renames, formatting, or moves with no logic
     change.
   - Config/tooling edits with no runtime effect.

   Always review for: new logic, API/contract changes,
   security-sensitive code, anything the plan flags as
   high-risk, and any step where domain `paths` match.

5. **Apply fixes if review requests changes.** Dispatch a
   *fixup subagent* (subagent_type: `claude`) using the fixup
   prompt template below. It applies fixes, re-runs
   verification, and updates the step-notes "Review
   resolutions" section. Then re-dispatch `requesting-review`.
   Max 3 iterations before escalating to the user.

6. **Commit.** Invoke `/commit-changes`. The commit must
   include code changes, the updated `plan.md`, and the
   step-notes file as one atomic commit.

7. **Report progress.** One line: which step finished and
   what's next. Do NOT prompt the user about compaction —
   step notes survive it.

## Implementation subagent prompt template

The subagent starts with no conversation history. Everything it
needs must be in the prompt:

```
You are executing step <N> of an approved plan. Work entirely
within this step — no drive-by changes outside its scope.

Plan: .sweatshop/plans/<plan-name>/plan.md
Prior step notes (read all that exist):
  .sweatshop/plans/<plan-name>/step-1.md
  ...
  .sweatshop/plans/<plan-name>/step-<N-1>.md
Step to execute: step <N> in plan.md

Required sequence:
1. Read plan.md and every prior step-*.md listed above.
2. If the step touches unfamiliar code, invoke the `research`
   skill.
3. Write failing tests for this step's acceptance criteria.
4. Implement the minimum code to pass them.
5. Invoke the `verification` skill (single pass; do NOT run
   /build, /test, /lint separately).
6. Flip this step's `- [ ]` boxes to `- [x]` in plan.md. Touch
   no other step's boxes.
7. Write .sweatshop/plans/<plan-name>/step-<N>.md using the
   "Per-step notes" format from executing-plans.

Do NOT commit. Do NOT request review. The orchestrator handles
both. Stop after step 7.

Report back in ≤3 lines:
- Status: ready-for-review | blocked
- One-line summary of what changed
- Pointer to step-<N>.md
Do NOT paste the diff or test output — the notes file is the
handoff.
```

## Fixup subagent prompt template

Used in step 5 when review requests changes:

```
You are applying review fixes for step <N> of an approved plan.

Plan: .sweatshop/plans/<plan-name>/plan.md
Step notes: .sweatshop/plans/<plan-name>/step-<N>.md
Review feedback (verbatim from reviewer):
<paste reviewer's blocking findings here>

Required sequence:
1. Read plan.md, step-<N>.md, and the current diff
   (`git diff HEAD`).
2. Apply fixes that address every blocking finding. Stay
   scoped — no drive-bys.
3. Invoke the `verification` skill.
4. Append a "Review resolutions" entry to step-<N>.md
   summarising what changed and why for each finding.

Do NOT commit. Stop after step 4.

Report back in ≤3 lines:
- Status: ready-for-rereview | blocked
- One-line summary of fixes applied
- Pointer to step-<N>.md
```

## Per-step notes

Step notes are a durable handoff to future steps (and to
future-you after compaction). They are NOT a diff summary —
`git show` is authoritative for what changed. Capture only
what is non-obvious from reading the commit.

Path: `.sweatshop/plans/<plan-name>/step-<N>.md`
(e.g. plan at `.sweatshop/plans/2026-04-15-add-auth/plan.md`
→ step 1 notes at
`.sweatshop/plans/2026-04-15-add-auth/step-1.md`).

Format:

```markdown
# Step <N> notes: <step title>

## Decisions
- Non-obvious choices made during implementation, with the
  reasoning. (e.g. "Kept the retry loop synchronous because
  the downstream client is not thread-safe.")

## Constraints surfaced
- Invariants, edge cases, or gotchas discovered while
  implementing that later steps must respect.

## For later steps
- Anything a subsequent step will need to know: new helpers
  introduced, conventions established, pitfalls to avoid.
  Leave empty if nothing cross-cuts.

## Review resolutions
- If review requested changes, record the key points and how
  they were addressed. Omit the section if review passed
  clean.
```

Keep each section tight — bullets, not paragraphs. If a
section has nothing to record, write "None" rather than
deleting the heading, so the shape is predictable.

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

CRITICAL: Every step MUST produce a step-notes file and
include it in the step's commit. Skipping notes breaks the
compaction-safety contract that later steps rely on.

CRITICAL: Plans are transparent to code and commits. Do NOT
reference plan steps, gaps, step numbers, or the plan itself
in code comments or commit messages. Write commits and
comments as if the plan does not exist — describe the change
on its own terms. No "Step 3:", "addresses GAP-2", "as
planned in step-4.md", etc.

CRITICAL: The main thread orchestrates; it does NOT implement.
Per-step research, edits, tests, and verification all happen
inside the implementation subagent. The main thread reads only
the returned step-notes file and `git diff --stat` between
steps. Doing implementation work directly in the main thread is
the dominant token leak this skill is designed to prevent.

CRITICAL: After auto-compaction (or when starting a fresh
session mid-plan), the main thread re-establishes orientation
by listing existing `step-*.md` files to find the next pending
step number. Do NOT re-read `plan.md` or prior step notes from
the main thread — the implementation subagent reads them fresh
each invocation, which is the contract that makes compaction
recovery cheap.
