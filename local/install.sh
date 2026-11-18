#!/usr/bin/env bash
# Install the /idea and /mine-sessions commands into your personal Claude Code commands folder.
# Usage: bash local/install.sh [owner/repo]
set -euo pipefail

REPO="${1:-theboxer85/linkedin-content-pipeline}"
DEST="$HOME/.claude/commands"
HERE="$(cd "$(dirname "$0")" && pwd)"

mkdir -p "$DEST"
for f in "$HERE"/commands/*.md; do
  name="$(basename "$f")"
  sed "s#__REPO__#$REPO#g" "$f" > "$DEST/$name"
  echo "installed /${name%.md} -> $DEST/$name"
done
echo "Done. Restart Claude Code, then try /idea or /mine-sessions."
