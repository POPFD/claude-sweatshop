# claude-sweatshop

A Claude Code plugin that orchestrates multi-agent workflows for day-to-day development. It breaks large tasks into researched, planned, reviewed, and incrementally implemented steps — each committed atomically with test-driven development.

## How it works

When you invoke `@orchestrate` with a task, the plugin coordinates a pipeline of specialized agents:

1. **Research** — scans the codebase and the web to gather context about the task
2. **Plan** — produces a numbered list of small, incremental steps with acceptance criteria
3. **Review** — a principal-engineer reviewer evaluates the plan for design quality, scalability, and performance
4. **Implement** — executes each step using TDD (tests first, then implementation), running build/test/lint before committing
5. **Review (per step)** — each implementation step is reviewed before moving to the next

The orchestrator handles clarification with the user at two points: before research (to fill obvious gaps) and after research (when findings surface new ambiguities). Plans are saved to `.sweatshop/plans/` and committed before execution begins.

## Agents

| Agent | Role |
|-------|------|
| `orchestrate` | Coordinates the full pipeline: research, plan, review, implement |
| `research` | Deep-dives into the codebase and external sources to build task context |
| `plan` | Breaks work into small, ordered steps with acceptance criteria |
| `review` | Evaluates plans and implementations as a principal engineer reviewer |
| `implement` | Implements a single plan step using TDD, then commits atomically |

## Skills

| Skill | Description |
|-------|-------------|
| `/commit-changes` | Stages and commits with conventional message formatting and signoff |
| `/build` | Auto-detects the build system (Make, Cargo, npm, Go, etc.) and runs it |
| `/test` | Auto-detects the test framework and runs tests |
| `/lint` | Auto-detects the linter and runs it |

## Usage

```
@orchestrate Add pagination to the /users API endpoint
```

The orchestrator will research, plan, get your approval, then implement step by step. You can also invoke agents directly:

```
@research How does the auth middleware work?
@plan Refactor the database layer to use connection pooling
@review Check the last commit for issues
```

## Installation

Clone this repository and point your Claude Code plugin configuration at it, or install from the marketplace.

## License

MIT
