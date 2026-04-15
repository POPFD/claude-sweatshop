---
name: onboard
description: Use when setting up claude-sweatshop in a project for the first time. Creates the .sweatshop/ directory, detects all toolchains, and populates memory.
allowed-tools: Bash(bash:*), Bash(sha256sum:*), Bash(git add:*), Bash(git status:*), Read, Write, Glob
---

# Onboard this project

## Step 1 — Initialise the directory

Find the plugin's `scripts/init.sh` using Glob, then run it
with `bash <path>`. The script is idempotent: it only creates
files that do not already exist, so running it on an already-
onboarded project is safe. Confirm `.sweatshop/memory.json`
and `.sweatshop/domain.json` exist afterwards.

## Step 2 — Check for existing onboarding

Before detecting anything, read the two JSON files written by
init.sh and decide whether this project is already onboarded.
The data in these files persists across dev sessions and is
authoritative — do NOT clobber it without explicit user
consent.

A project is considered **already onboarded** if EITHER:
- `memory.json` contains a non-empty `toolchain` object, OR
- `domain.json` contains a `domain` object with a `type`
  field set.

### If already onboarded

1. Summarise the existing configuration to the user:
   - Toolchain commands currently cached (build / test /
     lint) and the config file each was detected from.
   - Domain type, focus areas, and whether it was
     `user_refined`.
2. Ask the user to choose one of:
   - **(a) keep as-is (default)** — skip remaining steps,
     report and exit. Nothing is written.
   - **(b) fill missing sections only** — run detection for
     toolchains/domain entries that are absent, leave
     populated entries untouched.
   - **(c) re-detect everything (overwrite)** — run the
     full detection flow and overwrite existing entries.
     Preserve `domain.user_refined: true` across the
     overwrite if it was set previously, unless the user
     explicitly refines the new detection again.
3. Wait for an explicit choice before continuing. Do not
   assume.

### If not yet onboarded

Proceed directly to Step 3.

## Step 3 — Detect toolchains

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

## Step 4 — Ask the user for the domain expert

The user drives this step. Before doing any analysis yourself,
ask them what kind of domain expert this project needs. A
short, open question works best:

> "What should the domain expert for this project be? For
> example: crypto/DeFi, high-performance systems, frontend/UX,
> ML/data, distributed systems, embedded, game engines, etc.
> You can also describe it in your own words — I'll shape the
> focus areas and review criteria around your answer."

Wait for an explicit answer. Do not guess. Treat whatever the
user says as authoritative for `domain.type`. Common shapes
of answers and how to handle them:

- **A named domain** (e.g. "crypto/DeFi", "frontend/UX") —
  use it directly as `type`. Derive sensible `focus_areas`
  and `review_criteria` for that domain (see examples below).
- **A free-form description** (e.g. "low-latency trading
  engine, care about allocator behaviour and lock
  contention") — use a short label for `type` and lift the
  user's own phrasing into `focus_areas` / `review_criteria`.
- **"Not sure" / "you pick"** — only then fall back to
  auto-detecting from languages, frameworks, config files,
  README, directory structure, and dependencies. Present your
  best guess back to the user for confirmation before writing.

Reference examples for deriving focus areas and review
criteria from a named domain:

- crypto/DeFi → smart contract security, gas optimization,
  reentrancy prevention
- high-performance systems → latency, memory management,
  concurrency
- frontend/UX → accessibility, responsive design, performance
- ML/data → model accuracy, data pipeline reliability,
  reproducibility
- distributed systems → fault tolerance, consistency,
  observability

Once the domain is settled, identify the **domain-relevant
paths** — glob patterns covering the files whose domain
semantics matter. Infer these from the actual directory
structure of *this* project, not a generic template. Prefer a
small list of 2–5 globs that together cover where the domain
logic actually lives. Reference shapes:

- crypto/DeFi → `["contracts/**/*.sol", "scripts/deploy/**"]`
- frontend/UX → `["src/**/*.{tsx,jsx,vue,css,scss}", "public/**"]`
- ML/data → `["models/**", "pipelines/**", "data/**/*.py"]`
- distributed systems → `["internal/**/*.go", "proto/**", "deploy/**"]`
- high-perf systems → `["src/**/*.{c,cc,cpp,h,hpp,rs}"]`

Show the user the final assembled configuration (type, focus
areas, review criteria, paths) and ask if they want to tweak
anything before it is written. Because the user supplied the
`type` themselves, set `domain.user_refined: true` when
writing the file.

## Step 5 — Write memory and domain config

Two files are written — toolchain cache and domain config are
kept separate so domain metadata can be checked into version
control while the volatile toolchain cache stays gitignored.

**Respect the mode chosen in Step 2:**

- **keep as-is** — you should not have reached this step.
  Abort and report.
- **fill missing only** — read each file first, then merge:
  only write entries whose key is absent. Never replace an
  existing entry. If a `toolchain.build` already exists,
  leave it alone even if re-detection would pick a different
  command. This applies to sub-fields too: if
  `domain.paths` is absent from an otherwise-populated
  `domain` object (e.g. the project was onboarded before the
  field was introduced), detect and add it without touching
  the other fields.
- **re-detect everything** — overwrite every entry with
  fresh detection results. Carry over
  `domain.user_refined: true` from the previous file if it
  was set, unless the user just refined the new detection
  (in which case leave it `true` from the new run).

### Toolchain cache (`.sweatshop/memory.json`)

For each detected toolchain, hash its config file with
`sha256sum` and write the result into `.sweatshop/memory.json`.
Merge all entries in a single write:

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
  }
}
```

Omit any toolchain key that was not detected.

### Domain config (`.sweatshop/domain.json`)

Write the domain configuration into `.sweatshop/domain.json`:

```json
{
  "version": 1,
  "domain": {
    "type": "<detected or user-specified domain>",
    "focus_areas": ["area1", "area2", "area3"],
    "review_criteria": ["criterion1", "criterion2", "criterion3"],
    "paths": ["<glob1>", "<glob2>"],
    "detected_at": "<ISO 8601 timestamp>",
    "user_refined": false
  }
}
```

Set `user_refined` to `true` if the user adjusted the domain
detection.

The `paths` field is used by the `requesting-review` skill to
decide when to skip the domain review section on changes that
don't touch domain-relevant code. Omit the field only if no
meaningful subset of the repo can be identified — in that case
domain review will run unconditionally.

## Step 6 — Report

Show the user a summary of what was set up:

- `.sweatshop/` directory and `.gitignore`
- For each toolchain: the detected command and config file,
  or "not detected" if nothing matched
- Domain expert configuration: type, focus areas, review
  criteria, and domain-relevant paths
- Stage the new files with `git add -N .sweatshop/`
- Suggest `/commit-changes` to commit the scaffolding
