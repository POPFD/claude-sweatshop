---
name: build
description: "Use when the user asks to build or compile the project. Auto-detects the build system and runs the appropriate build command."
argument-hint: [args]
allowed-tools: Bash(make:*), Bash(cargo:*), Bash(npm:*), Bash(yarn:*), Bash(pnpm:*), Bash(go build:*), Bash(dotnet build:*), Bash(gradle:*), Bash(mvn:*), Bash(cmake:*), Bash(meson:*), Bash(cat:*), Bash(ls:*), Read, Glob
---

# Build the project

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

CRITICAL: If no build system is detected, report this clearly
and do NOT guess or run arbitrary commands.

CRITICAL: If the build fails, report the full error output so
the user can diagnose the issue. Do not attempt to fix build
errors unless asked.

If the user provides additional arguments, pass them through
to the underlying build command.
