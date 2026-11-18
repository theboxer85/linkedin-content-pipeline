#!/usr/bin/env bash
# Render diagram.drawio in each given post folder with draw.io's export server.
#   format image    -> diagram.png (first page, 1080 x 1350)
#   format document -> carousel.pdf (all pages, one per carousel page)
# Usage: scripts/render.sh posts/<folder> [posts/<folder> ...]
# Needs Docker and curl (GitHub's ubuntu runners have both).
set -euo pipefail

IMAGE="jgraph/export-server:latest"
NAME="drawio-export-$$"
PORT=8000

cleanup() { docker rm -f "$NAME" >/dev/null 2>&1 || true; }
trap cleanup EXIT

docker run -d --name "$NAME" -p "$PORT:8000" "$IMAGE" >/dev/null
for _ in $(seq 1 60); do
  code=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$PORT" || true)
  [ "$code" != "000" ] && break
  sleep 2
done

for folder in "$@"; do
  folder="${folder%/}"
  src="$folder/diagram.drawio"
  [ -f "$src" ] || { echo "skip $folder (no diagram.drawio)"; continue; }
  fmt=$(sed -n 's/^format:[[:space:]]*//p' "$folder/post.md" | head -1 | tr -d '"')
  if [ "$fmt" = "document" ]; then
    out="$folder/carousel.pdf"
    extra=(-d format=pdf -d allPages=1)
  else
    out="$folder/diagram.png"
    extra=(-d format=png -d scale=1 -d border=0)
  fi
  echo "render $src -> $out"
  status=$(curl -s -o "$out" -w "%{http_code}" --data-urlencode "xml@$src" "${extra[@]}" "http://localhost:$PORT")
  echo "export server answered HTTP $status, $(wc -c < "$out") bytes"
  if [ "$status" != "200" ] || [ ! -s "$out" ]; then
    echo "render failed for $src" >&2
    docker logs "$NAME" 2>&1 | tail -20 >&2
    rm -f "$out"
    exit 1
  fi
done
