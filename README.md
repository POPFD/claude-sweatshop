# claude-sweatshop

A Claude Code plugin that orchestrates multi-agent workflows for day-to-day development. It breaks large tasks into researched, planned, reviewed, and incrementally implemented steps — each committed atomically with test-driven development.

## Installation

### From the Claude Code marketplace

```bash
claude plugin install POPFD/claude-sweatshop
```

### From source

```bash
git clone git@github.com:POPFD/claude-sweatshop.git
claude plugin install --source ./claude-sweatshop
```

## Examples

### Full orchestrated workflow

Hand off an entire feature — research, plan, review, and implement — in one command:

```
@orchestrate Add pagination to the /users API endpoint
@orchestrate Refactor the database layer to use connection pooling
@orchestrate Fix the race condition in the webhook handler
```

### Individual agents

Use agents directly when you only need a specific part of the pipeline:

```
@research How does the auth middleware work?
@plan Refactor the database layer to use connection pooling
@review Check the last commit for issues
@implement Step 3 from the current plan
```

### Skills

Run common dev tasks with auto-detection of your toolchain:

```
/build
/test
/lint
/commit-changes
```

## How it works

When you invoke `@orchestrate` with a task, the plugin coordinates a pipeline of specialized agents:

```mermaid
flowchart LR
    A["@orchestrate"] --> B["Research"] --> C["Plan"]
    C --> D["Review"]
    D -->|rework| C
    D -->|approved| E["Implement\n(TDD)"]
    E --> F["Review"]
    F -->|rework| E
    F -->|next step| E
    F -->|done| G["Done"]

    style A fill:#4a5568,color:#fff
    style G fill:#2f855a,color:#fff
```

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

## License

MIT
