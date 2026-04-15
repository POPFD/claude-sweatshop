---
name: requesting-review
description: Use when a plan or implementation step is ready for review. Dispatches code-reviewer and domain-expert agents in parallel.
---

# Requesting Review

Dispatch the code-reviewer agent, and optionally the
domain-expert agent, to evaluate plans or implementations.

## Process

1. **Determine review scope** — is this a plan review or a
   code review?
2. **Prepare context** for reviewers:
   - **Plan review:** the plan content, research findings,
     and the spec or task description.
   - **Code review:** the diff from the most recent commit,
     the step's acceptance criteria, and the plan context.
3. **Decide whether domain review is needed.** Skip
   domain-expert when the change is clearly outside its
   lane — running it anyway burns tokens for no signal.

   Read `.sweatshop/domain.json`. The decision depends on
   whether the `domain.paths` array is present:

   **If `domain.paths` is set** (authoritative, deterministic):
   - Match each changed file against the glob patterns.
   - If zero changed files match any pattern → skip
     domain-expert.
   - If one or more changed files match → dispatch
     domain-expert.
   - No further judgment needed; the path list is the
     contract.

   **If `domain.paths` is absent** (fallback, judgment-based):
   Skip only when *all* of the following hold:
   - Change is docs-only, test-only, a pure rename/format
     refactor, or tooling/config with no domain logic.
   - No domain-specific invariants (security, performance
     budgets, protocol correctness, etc.) are plausibly
     affected.
   - The `focus_areas` in `domain.json` clearly don't apply
     to the diff.

   When in doubt under the fallback, include the
   domain-expert. The bias is toward skipping only the
   obviously-trivial cases.
4. **Dispatch reviewers** (in parallel if both are running):
   - `code-reviewer` — always dispatched. Evaluates design
     quality, scalability, performance, technology choices,
     and alignment with research.
   - `domain-expert` — dispatched unless skipped per step 3.
     Evaluates domain-specific concerns, pitfalls, and best
     practices.
5. **Collect verdicts** from dispatched reviewers.
6. **If any reviewer requests changes:**
   - Present combined feedback (clearly attributed to each
     reviewer).
   - Apply fixes.
   - Re-dispatch for review.
   - Max 3 iterations before surfacing to user.
7. **If all dispatched reviewers approve:** report approval
   and proceed.

## Output

Present a combined review summary. Include only the sections
for reviewers that were actually dispatched. If domain-expert
was skipped, note that briefly with the reason.

```
## Review Result: [APPROVED / CHANGES REQUESTED]

### Code Review
**Verdict:** approve / request changes
- [feedback items]

### Domain Review
**Verdict:** approve / request changes
- [feedback items]

_Domain review skipped: <one-line reason>_   ← only if skipped
```

## Rules

CRITICAL: Always dispatch the code-reviewer. Only the
domain-expert is optional, per the step-3 heuristic.

CRITICAL: When in doubt about whether to skip domain review,
include it. The cost of an unnecessary domain pass is lower
than the cost of missing a domain-specific bug.

CRITICAL: Do not skip re-review after applying fixes. Changed
code needs fresh eyes. If domain-expert flagged something on
the first pass, include it on every re-review of that change.

CRITICAL: Keep reviewer feedback attributed. The user needs to
know which reviewer flagged what.
