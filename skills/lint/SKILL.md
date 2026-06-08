---
name: lint
description: Use when the user asks to lint or check code style. Auto-detects the linter and runs the appropriate lint command.
allowed-tools: Bash(make:*), Bash(cargo:*), Bash(npm:*), Bash(yarn:*), Bash(pnpm:*), Bash(go vet:*), Bash(golangci-lint:*), Bash(dotnet format:*), Bash(gradle:*), Bash(mvn:*), Bash(ruff:*), Bash(flake8:*), Bash(pylint:*), Bash(eslint:*), Bash(cat:*), Bash(ls:*), Bash(sha256sum:*), Bash(mkdir:*), Bash(mktemp:*), Bash(tail:*), Bash(rm:*), Read, Write, Glob
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

## Output handling

A clean lint run has no signal — the exit code is the
message. Violations are the value when they occur. Run the
resolved command through this wrapper to keep clean runs
cheap:

```bash
out=$(mktemp)
<resolved command> >"$out" 2>&1
ec=$?
if [ $ec -ne 0 ]; then
  tail -c 20000 "$out"
  echo "---"
  echo "Lint violations found (exit $ec)"
else
  echo "Lint OK — no violations"
fi
rm -f "$out"
exit $ec
```

On success the Bash result is a single `Lint OK` line. On
non-zero exit the tail of the output surfaces the violations.

### Verbose mode

If the user's invocation includes `--verbose` or `-v`, skip
the wrapper entirely and run the resolved command directly so
the full output streams into context. Strip the flag before
passing remaining arguments to the underlying lint command.

## Rules

CRITICAL: If no linter is detected, report this clearly and
do NOT guess or run arbitrary commands.

CRITICAL: Always use the output-handling wrapper unless the
user requested verbose mode. Do not invoke the lint command
raw — that defeats the token-reduction the wrapper provides.

CRITICAL: When the wrapper surfaces violations, report them
verbatim so the user can decide whether to fix or ignore.

If the user provides additional arguments, pass them through
to the underlying lint command (after stripping the
`--verbose` / `-v` flag if present).
