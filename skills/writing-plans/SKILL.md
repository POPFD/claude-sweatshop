---
name: writing-plans
description: Use when you have a spec or requirements and need to break work into implementation steps with acceptance criteria.
---

# Writing Plans

Break work into small, incremental, decoupled steps with
clear acceptance criteria. Each step produces an atomic,
reviewable commit.

## Process

1. **Understand the goal** — read the spec, requirements, or
   design document carefully.
2. **Research the codebase** — explore relevant files,
   patterns, existing architecture. Optionally invoke the
   `research` skill for deeper context.
3. **Identify dependencies and constraints** — what must
   happen in what order.
4. **Produce a structured plan** — numbered steps following
   the format below.
5. **Save the plan** — each plan gets its own directory so
   the plan file and per-step notes stay grouped:
   `.sweatshop/plans/YYYY-MM-DD-short-summary/plan.md`
   The directory is created alongside the file. Step notes
   (produced later by `executing-plans`) will live as
   `step-<N>.md` siblings inside the same directory.
   Run the plugin's `scripts/init.sh` first to ensure
   `.sweatshop/` exists.
6. **Review the plan** — invoke `requesting-review` to have
   the reviewer evaluate the plan (code quality and, where in
   scope, domain). If changes requested, revise and re-review
   until approved.
7. **Present to user** — show the full approved plan
   including all steps, acceptance criteria, and files.
   Explicitly ask:
   - Whether the plan looks correct and complete
   - Whether they want to modify, reorder, add, or remove
     any steps
   - Whether there are additional constraints to consider
   Wait for explicit approval. Do NOT begin implementation
   until the user approves.
8. **Commit the plan** — invoke /commit-changes.
9. **Hand off to execution** — invoke the `executing-plans`
   skill.

## Step format

Each step MUST include:

```markdown
### Step N: [Short descriptive title]

**What:** A clear, concise description of what this step
does.

**Why:** Why this step is necessary and how it fits into the
overall goal.

**Acceptance criteria:**
- [ ] Criterion 1
- [ ] Criterion 2

**Files likely involved:**
- List of files that will probably be touched
```

## Rules

CRITICAL: Each step must be small enough that a human
reviewer can understand the resulting commit in isolation.

CRITICAL: Steps must be ordered so that each step builds on
the previous but is as decoupled as possible.

CRITICAL: Prefer many small steps over few large steps. Err
on the side of being too granular.

CRITICAL: Do NOT implement anything. This skill produces only
the plan.

CRITICAL: The plan must be reviewed before presenting to the
user. Do not show unreviewed plans.

CRITICAL: The plan must be saved and committed before
execution begins.

CRITICAL: After approval, the next step is always
`executing-plans`. Do not invoke any other skill.
