---
name: test
description: Use when the user asks to run tests. Auto-detects the test framework and runs the appropriate test command.
---

# Run the project's tests

## Memory (toolchain cache)

Before detecting, check if `.sweatshop/memory.json` exists and
contains a `toolchain.test` entry. If it does:

1. Read the stored `config_file` and `config_hash`.
2. Hash the current config file: `sha256sum <config_file>`.
3. If the hash matches, use the stored `command` directly —
   skip all detection logic below.
4. If the hash differs or the config file no longer exists,
   the entry is stale — proceed with detection.

If `.sweatshop/memory.json` does not exist or has no
`toolchain.test` key, proceed with detection.

## Detection

Auto-detect the project's test framework by checking for the
presence of build/config files in the project root, then run
the appropriate test command.

Detection order (use the first match found):
1. Makefile / GNUmakefile -> make test
2. Cargo.toml -> cargo test
3. package.json -> npm test (or yarn/pnpm if lockfile present)
4. go.mod -> go test ./...
5. *.csproj / *.sln -> dotnet test
6. build.gradle / build.gradle.kts -> gradle test
7. pom.xml -> mvn test
8. pytest.ini / pyproject.toml / setup.cfg -> pytest
9. requirements.txt with test files -> pytest

## Write back to memory

After successful detection, write the result to
`.sweatshop/memory.json` under `toolchain.test`:

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

CRITICAL: If no test framework is detected, report this clearly
and do NOT guess or run arbitrary commands.

CRITICAL: Report test results clearly — number of tests passed,
failed, and skipped. If tests fail, include the failure output
so the user can diagnose.

If the user provides additional arguments, pass them through
to the underlying test command (e.g. a specific test file or
filter pattern).
