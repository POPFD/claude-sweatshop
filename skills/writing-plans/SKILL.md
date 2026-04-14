---
name: writing-plans
description: Use when you have a spec or requirements and need to break work into implementation steps with acceptance criteria.
---

# Writing Plans

Break work into small, incremental, decoupled steps with
clear acceptance criteria. Each step produces an atomic,
reviewable commit. Mark dependencies and parallelizability
so the executor can run independent steps concurrently in
worktrees and cherry-pick them back.

## Process

1. **Understand the goal** — read the spec, requirements, or
   design document carefully.
2. **Research the codebase** — explore relevant files,
   patterns, existing architecture. Optionally invoke the
   `research` skill for deeper context.
3. **Identify dependencies and constraints** — what must
   happen in what order. Record this as per-step
   `Depends on` metadata.
4. **Identify parallelism** — steps that touch fully disjoint
   files and share no ordering requirement can run in
   parallel. Mark them `Parallelizable: yes`.
5. **Produce a structured plan** — numbered steps following
   the format below.
6. **Save the plan** — write to:
   `.sweatshop/plans/YYYY-MM-DD-short-summary.md`
   Run the plugin's `scripts/init.sh` first to ensure
   `.sweatshop/` exists.
7. **Review the plan** — invoke `requesting-review` to have
   both code-reviewer and domain-expert evaluate the plan.
   If changes requested, revise and re-review until
   approved.
8. **Present to user** — show the full approved plan
   including all steps, acceptance criteria, and files.
   Explicitly ask:
   - Whether the plan looks correct and complete
   - Whether they want to modify, reorder, add, or remove
     any steps
   - Whether there are additional constraints to consider
   Wait for explicit approval. Do NOT begin implementation
   until the user approves.
9. **Commit the plan** — invoke /commit-changes.
10. **Hand off to execution** — invoke the `executing-plans`
    skill.

## Step format

Each step MUST include:

```markdown
### Step N: [Short descriptive title]

**What:** A clear, concise description of what this step
does.

**Why:** Why this step is necessary and how it fits into the
overall goal.

**Depends on:** <comma-separated step numbers, or `none`>

**Parallelizable:** yes | no
  Default: `yes` when `Depends on: none`, otherwise `no`.
  Set `no` when the step touches files another concurrent
  step also touches, or when ordering matters for
  correctness even if dependencies are technically met.

**Acceptance criteria:**
- [ ] Criterion 1
- [ ] Criterion 2

**Files likely involved:**
- List of files that will probably be touched
```

## Parallelism guidance

Two steps in the same wave (same set of satisfied
dependencies) can safely run in parallel only if:

- Their `Files likely involved` lists do not overlap.
- Neither step's tests need the other's code to be present.
- No implicit ordering (migrations, schema changes, config
  that must load in order) couples them.

When in doubt, mark `Parallelizable: no`. A serial step that
could have been parallel costs a little wall time; a parallel
step that shouldn't have been costs a cherry-pick conflict
and a replanning round.

## Rules

CRITICAL: Each step must be small enough that a human
reviewer can understand the resulting commit in isolation.

CRITICAL: Steps must be ordered so that each step builds on
the previous but is as decoupled as possible.

CRITICAL: Prefer many small steps over few large steps. Err
on the side of being too granular.

CRITICAL: Every step must declare `Depends on` and
`Parallelizable` — the executor relies on both to compute
waves. Missing fields force it to fall back to fully serial
execution.

CRITICAL: Do NOT implement anything. This skill produces only
the plan.

CRITICAL: The plan must be reviewed before presenting to the
user. Do not show unreviewed plans.

CRITICAL: The plan must be saved and committed before
execution begins.

CRITICAL: After approval, the next step is always
`executing-plans`. Do not invoke any other skill.
