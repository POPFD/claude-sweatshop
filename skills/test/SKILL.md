---
name: test
description: Use when the user asks to run tests. Auto-detects the test framework and runs the appropriate test command.
allowed-tools: Bash(make:*), Bash(cargo:*), Bash(npm:*), Bash(yarn:*), Bash(pnpm:*), Bash(go test:*), Bash(dotnet test:*), Bash(gradle:*), Bash(mvn:*), Bash(pytest:*), Bash(python:*), Bash(cat:*), Bash(ls:*), Bash(sha256sum:*), Bash(mkdir:*), Bash(mktemp:*), Bash(tail:*), Bash(rm:*), Read, Write, Glob
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

## Output handling

Unlike build and lint, a successful test run has a useful
summary (`42 passed, 3 skipped`) that should survive. On
failure the assertion output and stack traces are what the
user needs. Run the resolved command through this wrapper:

```bash
out=$(mktemp)
<resolved command> >"$out" 2>&1
ec=$?
if [ $ec -ne 0 ]; then
  tail -c 20000 "$out"
  echo "---"
  echo "Tests failed (exit $ec)"
else
  tail -n 20 "$out"
fi
rm -f "$out"
exit $ec
```

On success only the last 20 lines are surfaced (enough for
the summary line across all common frameworks). On failure
the tail of the output surfaces the failing assertions.

### Verbose mode

If the user's invocation includes `--verbose` or `-v`, skip
the wrapper entirely and run the resolved command directly so
the full output streams into context. Strip the flag before
passing remaining arguments to the underlying test command.

## Rules

CRITICAL: If no test framework is detected, report this clearly
and do NOT guess or run arbitrary commands.

CRITICAL: Always use the output-handling wrapper unless the
user requested verbose mode. Do not invoke the test command
raw — that defeats the token-reduction the wrapper provides.

CRITICAL: When reporting, quote the summary line from the
wrapper output verbatim (counts of passed/failed/skipped). If
the wrapper's 20-line tail doesn't contain the summary for an
unusual framework, suggest rerunning with `--verbose`.

If the user provides additional arguments, pass them through
to the underlying test command (e.g. a specific test file or
filter pattern), after stripping the `--verbose` / `-v` flag
if present.
