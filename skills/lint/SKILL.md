---
name: lint
description: Use when the user asks to lint or check code style. Auto-detects the linter and runs the appropriate lint command.
---

# Lint the project

## Memory (toolchain cache)

Before detecting, check if `.sweatshop/memory.json` exists and
contains a `toolchain.lint` entry. If it does:

1. Read the stored `config_file` and `config_hash`.
2. Hash the current config file: `sha256sum <config_file>`.
3. If the hash matches, use the stored `command` directly —
   skip all detection logic below.
4. If the hash differs or the config file no longer exists,
   the entry is stale — proceed with detection.

If `.sweatshop/memory.json` does not exist or has no
`toolchain.lint` key, proceed with detection.

## Detection

Auto-detect the project's linter by checking for the presence
of lint configuration and build files in the project root,
then run the appropriate lint command.

Detection order (use the first match found):
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

## Write back to memory

After successful detection, write the result to
`.sweatshop/memory.json` under `toolchain.lint`:

```json
{
  "command": "<resolved command>",
  "config_file": "<file that triggered detection>",
  "config_hash": "sha256:<hash>",
  "detected_at": "<ISO 8601 timestamp>"
}
```

Run the plugin's `scripts/init.sh` to ensure `.sweatshop/`
exists (use Glob to locate it, then `bash <path>`). If the file
already exists, merge — do not overwrite other keys.

## Rules

CRITICAL: If no linter is detected, report this clearly and
do NOT guess or run arbitrary commands.

CRITICAL: Report lint results clearly. If there are violations,
include them so the user can decide whether to fix or ignore.

If the user provides additional arguments, pass them through
to the underlying lint command.
