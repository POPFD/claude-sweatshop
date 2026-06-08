---
name: requesting-review
description: Use when a plan or implementation step is ready for review. Dispatches the reviewer agent with the right mode.
---

# Requesting Review

Dispatch the `reviewer` agent to evaluate a plan or
implementation. The same agent produces both the general code
review and (when in scope) the domain review in a single pass,
so we only pay for one exploration of the diff.

## Process

1. **Determine review scope** — is this a plan review or a
   code review?
2. **Prepare context** for the reviewer:
   - **Plan review:** the plan content, research findings,
     and the spec or task description.
   - **Code review:** the diff from the most recent commit,
     the step's acceptance criteria, and the plan context.
     Also pass the explicit changed-files list from
     `git diff --name-only HEAD~1` so the reviewer reads
     only those files instead of grepping the repo. Pin its
     scope: "review only these files; do not explore beyond
     them unless a finding requires it."
3. **Pick the mode.** The mode tells the reviewer which
   sections to produce. Skipping the domain section when the
   change is outside its lane avoids burning tokens for no
   signal.

   Read `.sweatshop/domain.json`. The decision depends on
   whether the `domain.paths` array is present:

   **If `domain.paths` is set** (authoritative, deterministic):
   - Match each changed file against the glob patterns.
   - If zero changed files match any pattern → mode is
     `code-only`.
   - If one or more changed files match → mode is
     `code+domain`.
   - No further judgment needed; the path list is the
     contract.

   **If `domain.paths` is absent** (fallback, judgment-based):
   Use `code-only` only when *all* of the following hold:
   - Change is docs-only, test-only, a pure rename/format
     refactor, or tooling/config with no domain logic.
   - No domain-specific invariants (security, performance
     budgets, protocol correctness, etc.) are plausibly
     affected.
   - The `focus_areas` in `domain.json` clearly don't apply
     to the diff.

   When in doubt under the fallback, use `code+domain`. The
   bias is toward skipping the domain section only in the
   obviously-trivial cases.
4. **Dispatch the reviewer.** Invoke the `reviewer` agent
   once with:
   - The prepared context from step 2.
   - The chosen `mode` (`code-only` or `code+domain`).
5. **Collect the verdict(s)** from the reviewer's response.
   In `code+domain` mode the reviewer produces two verdicts
   (one per section); in `code-only` mode, one.
6. **If any verdict requests changes:**
   - Present the feedback with section labels preserved.
   - Apply fixes.
   - Re-dispatch for review.
   - Max 3 iterations before surfacing to user.
7. **If all verdicts approve:** report approval and proceed.

## Output

Forward the reviewer's output verbatim — do not re-summarize
or re-list its bullets. The reviewer is already constrained
to terse, blocking-only output; wrapping it in extra
narration defeats that.

- All verdicts approve → reply with one line:
  `Review: APPROVED` (add `(domain skipped: <reason>)` only if
  applicable).
- Any verdict requests changes → paste the reviewer's
  sections as-is, with no additional commentary.

## Rules

CRITICAL: Dispatch the reviewer exactly once per review cycle.
The whole point of the merged agent is that both sections come
from a single exploration pass — do not split the review into
two agent invocations.

CRITICAL: When in doubt about whether to include the domain
section, use `code+domain`. The cost of an unnecessary domain
pass is lower than the cost of missing a domain-specific bug.

CRITICAL: Do not skip re-review after applying fixes. Changed
code needs fresh eyes. If the domain section flagged something
on the first pass, use `code+domain` on every re-review of
that change even if the path-match would now say otherwise.

CRITICAL: Keep section labels intact when presenting feedback
to the user. They need to know which lens produced which
finding.
