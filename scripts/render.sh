#!/usr/bin/env bash
# Render diagram.drawio in each given post folder.
#   format image    -> diagram.png (first page)
#   format document -> carousel.pdf (all pages, one per carousel page)
# Usage: scripts/render.sh posts/<folder> [posts/<folder> ...]
# Needs Docker (GitHub's ubuntu runners have it).
set -euo pipefail

IMAGE="rlespinasse/drawio-desktop-headless:latest"

for folder in "$@"; do
  folder="${folder%/}"
  src="$folder/diagram.drawio"
  [ -f "$src" ] || { echo "skip $folder (no diagram.drawio)"; continue; }
  fmt=$(sed -n 's/^format:[[:space:]]*//p' "$folder/post.md" | head -1 | tr -d '"')
  if [ "$fmt" = "document" ]; then
    out="$folder/carousel.pdf"
    args=(-x -f pdf -a -o "/data/$out" "/data/$src")
  else
    out="$folder/diagram.png"
    args=(-x -f png --border 40 -s 1 -o "/data/$out" "/data/$src")
  fi
  echo "render $src -> $out"
  set +e
  docker run --rm -v "$PWD:/data" -w /data -e DRAWIO_DISABLE_UPDATE=true -e DRAWIO_DESKTOP_COMMAND_TIMEOUT=180s "$IMAGE" "${args[@]}"
  rc=$?
  set -e
  echo "drawio exit code: $rc"
  ls -la "$folder"
  [ -s "$out" ] || { echo "render produced no output for $src" >&2; exit 1; }
done
