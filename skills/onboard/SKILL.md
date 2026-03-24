---
name: onboard
description: Use when setting up claude-sweatshop in a project for the first time. Creates the .sweatshop/ directory, detects all toolchains, and populates memory.
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

## Step 3 — Write memory

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
  }
}
```

Omit any toolchain key that was not detected.

## Step 4 — Report

Show the user a summary of what was set up:

- `.sweatshop/` directory and `.gitignore`
- For each toolchain: the detected command and config file,
  or "not detected" if nothing matched
- Stage the new files with `git add -N .sweatshop/`
- Suggest `/commit-changes` to commit the scaffolding
