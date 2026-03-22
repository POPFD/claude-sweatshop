#!/usr/bin/env bash
# Idempotently initialise the .sweatshop/ directory in the current project.
set -euo pipefail

SWEATSHOP_DIR=".sweatshop"
MEMORY_FILE="$SWEATSHOP_DIR/memory.json"
PLANS_DIR="$SWEATSHOP_DIR/plans"
GITIGNORE="$SWEATSHOP_DIR/.gitignore"

mkdir -p "$SWEATSHOP_DIR" "$PLANS_DIR"

# Seed memory.json if it doesn't exist
if [ ! -f "$MEMORY_FILE" ]; then
  printf '{\n  "version": 1\n}\n' > "$MEMORY_FILE"
fi

# Keep plans tracked but ignore runtime memory
if [ ! -f "$GITIGNORE" ]; then
  cat > "$GITIGNORE" << 'EOF'
# Runtime cache — not worth committing
memory.json
EOF
fi

echo "Initialised $SWEATSHOP_DIR/"
