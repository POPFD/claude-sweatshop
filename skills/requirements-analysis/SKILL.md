---
name: requirements-analysis
description: Use when starting new features or significant changes. Explores purpose, constraints, and approaches through structured dialogue before any implementation.
---

# Requirements Analysis

Understand what needs to be built before writing any code.
This skill drives a structured conversation to surface
requirements, evaluate options, and produce an approved
design. It is the entry point for new work.

## Process

1. **Survey the project** — read relevant source files,
   documentation, and recent git history to ground yourself
   in the current state of things.
2. **Evaluate the task** — read the task description and
   identify gaps or ambiguities. Consider:
   - Performance constraints (throughput, latency, memory)
   - Scalability requirements (data volume, concurrency)
   - Compatibility requirements (platforms, versions, APIs)
   - Security considerations
   - Error handling expectations
   - Target users or consumers of the change
3. **Gather context** — optionally invoke the `research`
   skill if deep codebase or external context is needed.
4. **Refine through dialogue** — ask the user focused
   questions to fill in gaps. Keep each message to a single
   question so the conversation stays manageable. Where
   practical, offer concrete options rather than open-ended
   prompts. If the task is already well-defined, move on.
5. **Follow-up on research** — if research surfaced new
   trade-offs or ambiguities, raise them with the user
   before committing to a direction.
6. **Compare alternatives** — lay out a small number of
   viable approaches with their trade-offs. State which
   one you recommend and why.
7. **Present design** — once you understand what to build,
   walk through the design piece by piece. After each
   section, confirm the user is aligned before continuing.
   Cover: architecture, components, data flow, error
   handling, testing.
8. **Get user approval** — the user must explicitly approve
   the design before proceeding.
9. **Hand off to planning** — invoke the `writing-plans`
   skill to create the implementation plan.

## Implementation boundary

No code, no scaffolding, and no implementation work of any
kind until the user has signed off on the design. This holds
even for tasks that seem trivial — unexamined assumptions
waste more time than a short design conversation.

## Rules

CRITICAL: Limit each message to a single question. Stacking
questions leads to incomplete answers and missed details.

CRITICAL: Do not assume constraints the user hasn't stated.
Ask rather than guess, but only ask about things that would
materially change the approach.

CRITICAL: Always research before proposing approaches. Bad
designs come from insufficient understanding.

CRITICAL: After approval, the next step is always
`writing-plans`. Do not invoke any other skill.
