---
name: research
description: Use when you need deep context about a codebase area, external references, or prior art before planning or making decisions.
---

# Research

Gather thorough context before planning or implementation by
dispatching the researcher subagent.

## Process

1. **Define the scope** — identify what needs to be
   understood: specific codebase areas, external APIs,
   domain knowledge, prior art.
2. **Dispatch the researcher agent** — pass the task
   description, specific areas to investigate, and any
   known constraints.
3. **Receive the report** — the researcher returns a
   structured report covering:
   - Task understanding
   - Codebase findings (files, patterns, constraints, tests)
   - External findings (docs, best practices, pitfalls)
   - Recommendations (approach, risks, open questions)
4. **Surface questions** — if the research reveals
   ambiguities or decisions that need user input, present
   them before proceeding.

## When to use

- Before writing a plan, to understand the problem space
- During plan execution, when a step touches unfamiliar code
- When evaluating trade-offs between approaches
- When domain-specific knowledge is needed

## Rules

CRITICAL: Do not skip research to save time. Bad plans come
from insufficient understanding.

CRITICAL: If the research reveals that the task scope is
larger than expected, surface this to the user before
proceeding.
