---
name: test
description: "Use when the user asks to run tests. Auto-detects the test framework and runs the appropriate test command."
argument-hint: [args]
allowed-tools: Bash(make:*), Bash(cargo:*), Bash(npm:*), Bash(yarn:*), Bash(pnpm:*), Bash(go test:*), Bash(dotnet test:*), Bash(gradle:*), Bash(mvn:*), Bash(pytest:*), Bash(python:*), Bash(cat:*), Bash(ls:*), Read, Glob
---

# Run the project's tests

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

CRITICAL: If no test framework is detected, report this clearly
and do NOT guess or run arbitrary commands.

CRITICAL: Report test results clearly — number of tests passed,
failed, and skipped. If tests fail, include the failure output
so the user can diagnose.

If the user provides additional arguments, pass them through
to the underlying test command (e.g. a specific test file or
filter pattern).
