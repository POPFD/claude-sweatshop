#!/usr/bin/env bash
# Idempotently initialise the .sweatshop/ directory in the current project.
set -euo pipefail

SWEATSHOP_DIR=".sweatshop"
MEMORY_FILE="$SWEATSHOP_DIR/memory.json"
DOMAIN_FILE="$SWEATSHOP_DIR/domain.json"
PLANS_DIR="$SWEATSHOP_DIR/plans"
GITIGNORE="$SWEATSHOP_DIR/.gitignore"

mkdir -p "$SWEATSHOP_DIR" "$PLANS_DIR"

# Seed memory.json (toolchain cache) if it doesn't exist
if [ ! -f "$MEMORY_FILE" ]; then
  printf '{\n  "version": 1\n}\n' > "$MEMORY_FILE"
fi

# Seed domain.json (project metadata, checked in) if it doesn't exist
if [ ! -f "$DOMAIN_FILE" ]; then
  printf '{\n  "version": 1\n}\n' > "$DOMAIN_FILE"
fi

# Keep plans and domain.json tracked but ignore runtime cache
if [ ! -f "$GITIGNORE" ]; then
  cat > "$GITIGNORE" << 'EOF'
# Toolchain cache — changes on every config edit
memory.json
EOF
fi

echo "Initialised $SWEATSHOP_DIR/"
