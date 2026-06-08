---
name: build
description: Use when the user asks to build or compile the project. Auto-detects the build system and runs the appropriate build command.
allowed-tools: Bash(make:*), Bash(cargo:*), Bash(npm:*), Bash(yarn:*), Bash(pnpm:*), Bash(go build:*), Bash(dotnet build:*), Bash(gradle:*), Bash(mvn:*), Bash(cmake:*), Bash(meson:*), Bash(cat:*), Bash(ls:*), Bash(sha256sum:*), Bash(mkdir:*), Bash(mktemp:*), Bash(tail:*), Bash(rm:*), Read, Write, Glob
---

# Build the project

## Memory (toolchain cache)

Before detecting, check if `.sweatshop/memory.json` exists and
contains a `toolchain.build` entry. If it does:

1. Read the stored `config_file` and `config_hash`.
2. Hash the current config file: `sha256sum <config_file>`.
3. If the hash matches, use the stored `command` directly —
   skip all detection logic below.
4. If the hash differs or the config file no longer exists,
   the entry is stale — proceed with detection.

If `.sweatshop/memory.json` does not exist or has no
`toolchain.build` key, proceed with detection.

## Detection

Auto-detect the project's build system by checking for the
presence of build files in the project root, then run the
appropriate build command.

Detection order (use the first match found):
1. Makefile / GNUmakefile -> make
2. Cargo.toml -> cargo build
3. package.json -> npm run build (or yarn/pnpm if lockfile present)
4. go.mod -> go build ./...
5. *.csproj / *.sln -> dotnet build
6. build.gradle / build.gradle.kts -> gradle build
7. pom.xml -> mvn compile
8. CMakeLists.txt -> cmake --build build
9. meson.build -> meson compile -C build

## Write back to memory

After successful detection, write the result to
`.sweatshop/memory.json` under `toolchain.build`:

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

Build output is usually large and mostly worthless on
success — compiler progress, warnings, linker chatter. To
avoid burning tokens, run the resolved command through this
wrapper instead of invoking it directly:

```bash
out=$(mktemp)
<resolved command> >"$out" 2>&1
ec=$?
if [ $ec -ne 0 ]; then
  tail -c 20000 "$out"
  echo "---"
  echo "Build failed (exit $ec)"
else
  echo "Build OK"
fi
rm -f "$out"
exit $ec
```

On success the Bash result is a single `Build OK` line. On
failure the last ~20KB of output is surfaced so the error is
diagnosable. If the full log is ever needed, rerun in verbose
mode (below).

### Verbose mode

If the user's invocation includes `--verbose` or `-v`, skip
the wrapper entirely and run the resolved command directly so
the full output streams into context. Strip the flag before
passing remaining arguments to the underlying build command.

## Rules

CRITICAL: If no build system is detected, report this clearly
and do NOT guess or run arbitrary commands.

CRITICAL: If the build fails, the wrapper surfaces the tail
of the output automatically — report it and do not attempt to
fix build errors unless asked. If the tail is insufficient to
diagnose, suggest rerunning with `--verbose`.

CRITICAL: Always use the output-handling wrapper unless the
user requested verbose mode. Do not invoke the build command
raw — that defeats the token-reduction the wrapper provides.

If the user provides additional arguments, pass them through
to the underlying build command (after stripping the
`--verbose` / `-v` flag if present).
