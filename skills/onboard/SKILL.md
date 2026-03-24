---
name: onboard
description: Use when setting up claude-sweatshop in a project for the first time. Creates the .sweatshop/ directory, detects all toolchains, and populates memory.
allowed-tools: Bash(bash:*), Bash(sha256sum:*), Bash(git add:*), Bash(git status:*), Read, Write, Glob
---

# Onboard this project

## Step 1 — Initialise the directory

Find the plugin's `scripts/init.sh` using Glob, then run it
with `bash <path>`. Confirm `.sweatshop/memory.json` exists
afterwards.

## Step 2 — Detect toolchains

Run the detection logic for each toolchain below. For each one,
check for config files in the project root using the detection
order listed. Use the **first match** found. If nothing matches,
skip that toolchain and note it as "not detected".

### Build

Detection order:
1. Makefile / GNUmakefile -> make
2. Cargo.toml -> cargo build
3. package.json -> npm run build (or yarn/pnpm if lockfile present)
4. go.mod -> go build ./...
5. *.csproj / *.sln -> dotnet build
6. build.gradle / build.gradle.kts -> gradle build
7. pom.xml -> mvn compile
8. CMakeLists.txt -> cmake --build build
9. meson.build -> meson compile -C build

### Test

Detection order:
1. Makefile / GNUmakefile -> make test
2. Cargo.toml -> cargo test
3. package.json -> npm test (or yarn/pnpm if lockfile present)
4. go.mod -> go test ./...
5. *.csproj / *.sln -> dotnet test
6. build.gradle / build.gradle.kts -> gradle test
7. pom.xml -> mvn test
8. pytest.ini / pyproject.toml / setup.cfg -> pytest
9. requirements.txt with test files -> pytest

### Lint

Detection order:
1. Makefile / GNUmakefile -> make lint
2. Cargo.toml -> cargo clippy
3. package.json -> npm run lint (or yarn/pnpm if lockfile present)
4. go.mod -> golangci-lint run (fallback: go vet ./...)
5. *.csproj / *.sln -> dotnet format --verify-no-changes
6. build.gradle / build.gradle.kts -> gradle check
7. pom.xml -> mvn checkstyle:check
8. ruff.toml / pyproject.toml with ruff -> ruff check .
9. .flake8 / setup.cfg with flake8 -> flake8 .
10. .pylintrc -> pylint .

## Step 3 — Detect project domain

Analyze the codebase to auto-detect the project's domain for
the domain-expert agent. Check: languages, frameworks, config
files, README, directory structure, and dependencies.

Detection examples:
- Solidity / Hardhat / Foundry → **crypto/DeFi**: smart
  contract security, gas optimization, reentrancy prevention
- C/C++ with perf configs, lock-free structures →
  **high-performance systems**: latency, memory management,
  concurrency
- React / Vue / Angular with CSS → **frontend/UX**:
  accessibility, responsive design, performance
- PyTorch / TensorFlow, dataset directories → **ML/data**:
  model accuracy, data pipeline reliability, reproducibility
- Go / gRPC / Kubernetes configs → **distributed systems**:
  fault tolerance, consistency, observability

Present the detected domain to the user:

> "I detected this project as **[domain type]** with focus
> areas: [list]. Does this look right, or would you like to
> adjust?"

If the user provides refinement, update accordingly. If no
domain is detected, ask the user to describe their project's
domain and focus areas.

## Step 4 — Write memory

For each detected toolchain, hash its config file with
`sha256sum` and write the result into `.sweatshop/memory.json`.
Merge all entries in a single write. The file structure is:

```json
{
  "version": 1,
  "toolchain": {
    "build": {
      "command": "<resolved command>",
      "config_file": "<file that triggered detection>",
      "config_hash": "sha256:<hash>",
      "detected_at": "<ISO 8601 timestamp>"
    },
    "test": { "..." },
    "lint": { "..." }
  },
  "domain": {
    "type": "<detected or user-specified domain>",
    "focus_areas": ["area1", "area2", "area3"],
    "review_criteria": ["criterion1", "criterion2", "criterion3"],
    "detected_at": "<ISO 8601 timestamp>",
    "user_refined": false
  }
}
```

Omit any toolchain key that was not detected. Set
`user_refined` to `true` if the user adjusted the domain
detection.

## Step 5 — Report

Show the user a summary of what was set up:

- `.sweatshop/` directory and `.gitignore`
- For each toolchain: the detected command and config file,
  or "not detected" if nothing matched
- Domain expert configuration: type, focus areas, and
  review criteria
- Stage the new files with `git add -N .sweatshop/`
- Suggest `/commit-changes` to commit the scaffolding
