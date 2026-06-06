#!/usr/bin/env python3
"""PreToolUse(Bash) guard: route builds, tests, lints, and commits
through the claude-sweatshop skills instead of raw shell commands.

The hook fires for every Bash tool call — main agent and subagents
alike — and it cannot tell whether a command came from a skill's
instructions or from an agent improvising. So it discriminates on the
*shape* the skills emit:

  * /build, /test, /lint wrap their runner in `out=$(mktemp); ... >"$out"`.
    A command that contains `mktemp` is therefore skill-shaped and is
    allowed through; a bare `cargo test` is drift and is blocked.
  * /commit-changes always commits with `--signoff`. History-rewrite
    commits the framework performs directly (`--amend`, `--fixup`,
    `--squash`) are mechanical and also allowed. Everything else —
    `git commit -m ...`, bare `git commit` — is drift and is blocked.

Blocked calls return a deny decision naming the skill to use instead.
Anything that does not match a guarded pattern is left untouched
(exit 0, no output) so the normal permission flow still applies.

Known limitation: `/build --verbose` (and -v for test/lint) skips the
mktemp wrapper, so a deliberate verbose run is blocked too. Re-run
without --verbose, or invoke the runner inside the wrapper.

The hook fails open: any parse error or unexpected input exits 0 so a
bug here can never wedge an agent.
"""

import json
import re
import sys


def deny(reason: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


# Runner patterns per category. Order matters: the first category to
# match decides the redirect message, so the more specific make/gradle
# targets (test, lint) are listed before the generic build forms.
TEST_PATTERNS = [
    r"\bcargo\s+test\b",
    r"\bgo\s+test\b",
    r"\bdotnet\s+test\b",
    r"\bgradlew?\s+\S*test\b",
    r"\bmvn\s+\S*test\b",
    r"\bpytest\b",
    r"\bpython3?\s+-m\s+pytest\b",
    r"\bmake\s+test\b",
    r"\b(?:npm|yarn|pnpm)\s+(?:run\s+)?test\b",
]

LINT_PATTERNS = [
    r"\bcargo\s+clippy\b",
    r"\bgo\s+vet\b",
    r"\bgolangci-lint\b",
    r"\bdotnet\s+format\b",
    r"\bgradlew?\s+check\b",
    r"\bmvn\s+\S*checkstyle\S*\b",
    r"\bruff\s+check\b",
    r"\bflake8\b",
    r"\bpylint\b",
    r"\beslint\b",
    r"\bmake\s+(?:lint|check)\b",
    r"\b(?:npm|yarn|pnpm)\s+(?:run\s+)?lint\b",
]

BUILD_PATTERNS = [
    r"\bcargo\s+build\b",
    r"\bgo\s+build\b",
    r"\bdotnet\s+build\b",
    r"\bgradlew?\s+build\b",
    r"\bmvn\s+\S*compile\b",
    r"\bcmake\s+--build\b",
    r"\bmeson\s+compile\b",
    r"\bmake\b(?!\s+(?:test|lint|check)\b)",
    r"\b(?:npm|yarn|pnpm)\s+(?:run\s+)?build\b",
]

CATEGORIES = [
    ("test", TEST_PATTERNS, "/test"),
    ("lint", LINT_PATTERNS, "/lint"),
    ("build", BUILD_PATTERNS, "/build"),
]

# A command carrying the skills' output-capture wrapper is skill-shaped
# and exempt. mktemp is the distinctive marker /build, /test, /lint emit.
WRAPPER_MARKER = re.compile(r"\bmktemp\b")

# git commit forms the framework legitimately runs directly.
COMMIT_ALLOWED = re.compile(r"--amend\b|--fixup\b|--squash\b|--signoff\b|(?<!\w)-s\b")
COMMIT_CALL = re.compile(r"\bgit\b[^\n&|;]*\bcommit\b")


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    if payload.get("tool_name") != "Bash":
        sys.exit(0)

    command = (payload.get("tool_input") or {}).get("command")
    if not isinstance(command, str) or not command.strip():
        sys.exit(0)

    # Commit guard: block new commits that bypass /commit-changes, but
    # let the skill's --signoff form and mechanical history edits pass.
    if COMMIT_CALL.search(command) and not COMMIT_ALLOWED.search(command):
        deny(
            "Direct `git commit` is blocked. Create commits with the "
            "claude-sweatshop /commit-changes skill — it formats the "
            "message and adds --signoff. (Mechanical --amend/--fixup/"
            "--squash are exempt.)"
        )

    # Build/test/lint guard: bare runners must go through the skill;
    # the skill's mktemp-wrapped form is exempt.
    if not WRAPPER_MARKER.search(command):
        for name, patterns, skill in CATEGORIES:
            if any(re.search(p, command) for p in patterns):
                deny(
                    f"Direct {name} commands are blocked. Run {name} "
                    f"through the claude-sweatshop {skill} skill (or the "
                    f"verification skill, which runs build/test/lint as "
                    f"one pass). It captures output efficiently and keeps "
                    f"toolchain detection in one place."
                )

    sys.exit(0)


if __name__ == "__main__":
    main()
