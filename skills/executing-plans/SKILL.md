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

## Process per step

For each step in the plan, follow this exact sequence:

1. **Load prior context — only when needed.** Re-read
   `plan.md` and every existing `step-*.md` ONLY if one of
   these is true:
   - This is the first step you are executing in the current
     session.
   - Auto-compaction has fired since the last step (prior
     conversation no longer visible).
   - You are unsure whether a fact from an earlier step is
     still in your context.

   Otherwise skip this step — re-reading the same files every
   iteration is the largest token leak in this workflow. The
   notes are the authoritative source after compaction; before
   compaction, the conversation already has them.
2. **Gather additional context** — if this step touches
   unfamiliar code not covered by prior notes, invoke the
   `research` skill.
3. **Write tests first** — tests that verify the step's
   acceptance criteria. They should fail at this point.
4. **Implement** — minimum code to make the tests pass. Stay
   scoped to this step only.
5. **Verify** — invoke the `verification` skill once. It
   runs build, test, and lint as a single pass and is
   silent on success. Do NOT invoke `/build`, `/test`, and
   `/lint` separately — that triples the skill-load
   overhead for no extra signal.
6. **Update the plan file** — flip this step's
   acceptance-criteria boxes from `- [ ]` to `- [x]`. Do NOT
   modify any other step's boxes.
7. **Write step notes** — save
   `.sweatshop/plans/<plan-name>/step-<N>.md` using the
   format in the "Per-step notes" section below. These notes
   must survive context compaction and carry forward anything
   later steps will need to know.
8. **Review (risk-gated)** — invoke the `requesting-review`
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

    If review requests changes, apply fixes and re-review (max
    3 iterations before escalating).
9. **Commit** — invoke /commit-changes. The commit must
    include code changes, the updated plan file, AND the
    step notes file as one atomic commit.
10. **Report progress** — one line: which step finished and
    what's next. Do NOT prompt the user about compaction.
    Auto-compaction handles context pressure on its own, and
    step notes guarantee state survives whenever it fires.

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

CRITICAL: After auto-compaction (or when starting a fresh
session mid-plan), read `plan.md` and all prior `step-*.md`
notes before continuing. Within a single uncompacted session
do NOT re-read them every step — the conversation already
has them and re-reading is the dominant token cost.
