---
name: requesting-review
description: Use when a plan or implementation step is ready for review. Dispatches code-reviewer and domain-expert agents in parallel.
---

# Requesting Review

Dispatch the code-reviewer and domain-expert agents in
parallel to evaluate plans or implementations.

## Process

1. **Determine review scope** — is this a plan review or a
   code review?
2. **Prepare context** for reviewers:
   - **Plan review:** the plan content, research findings,
     and the spec or task description.
   - **Code review:** the diff from the most recent commit,
     the step's acceptance criteria, and the plan context.
3. **Dispatch both agents in parallel:**
   - `code-reviewer` — evaluates design quality,
     scalability, performance, technology choices, and
     alignment with research.
   - `domain-expert` — evaluates domain-specific concerns,
     pitfalls, and best practices.
4. **Collect verdicts** from both reviewers.
5. **If either requests changes:**
   - Present combined feedback (clearly attributed to each
     reviewer).
   - Apply fixes.
   - Re-dispatch for review.
   - Max 3 iterations before surfacing to user.
6. **If both approve:** report approval and proceed.

## Output

Present a combined review summary:

```
## Review Result: [APPROVED / CHANGES REQUESTED]

### Code Review
**Verdict:** approve / request changes
- [feedback items]

### Domain Review
**Verdict:** approve / request changes
- [feedback items]
```

## Rules

CRITICAL: Always dispatch both reviewers. The domain expert
catches things the code reviewer cannot.

CRITICAL: Do not skip re-review after applying fixes. Changed
code needs fresh eyes.

CRITICAL: Keep reviewer feedback attributed. The user needs to
know which reviewer flagged what.
