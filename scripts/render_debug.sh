#!/usr/bin/env bash
# Temporary: compare draw.io renderers on one file and report what works.
set -u
src="$1"
mkdir -p .work/debug
cp "$src" .work/debug/d.drawio
U=(-u "$(id -u):$(id -g)" -e HOME=/tmp -v /etc/passwd:/etc/passwd:ro)

echo "== A1 desktop-headless --version"
timeout 90 docker run --rm "${U[@]}" -v "$PWD:/data" -w /data -e DRAWIO_DESKTOP_COMMAND_TIMEOUT=60s \
  rlespinasse/drawio-desktop-headless --version; echo "rc=$?"

echo "== A2 desktop-headless pdf"
timeout 120 docker run --rm "${U[@]}" -v "$PWD:/data" -w /data -e DRAWIO_DESKTOP_COMMAND_TIMEOUT=90s \
  rlespinasse/drawio-desktop-headless -x -f pdf -o /data/.work/debug/a2.pdf /data/.work/debug/d.drawio; echo "rc=$?"

echo "== A3 desktop-headless png, relative paths, root"
timeout 120 docker run --rm -v "$PWD/.work/debug:/data" -w /data -e DRAWIO_DESKTOP_COMMAND_TIMEOUT=90s \
  rlespinasse/drawio-desktop-headless -x -f png -o a3.png d.drawio; echo "rc=$?"

echo "== B drawio-export --help"
timeout 120 docker run --rm rlespinasse/drawio-export --help 2>&1 | head -40; echo "rc=$?"

echo "== B2 drawio-export png"
timeout 180 docker run --rm -v "$PWD/.work/debug:/data" rlespinasse/drawio-export --format png 2>&1 | tail -15; echo "rc=$?"

echo "== C export-server"
docker run -d --name exp -p 8000:8000 jgraph/export-server >/dev/null 2>&1; echo "start rc=$?"
for i in $(seq 1 30); do curl -s -o /dev/null http://localhost:8000 && break; sleep 2; done
curl -s -o .work/debug/c.png -w "http=%{http_code} bytes=%{size_download}\n" \
  --data-urlencode "xml@.work/debug/d.drawio" -d format=png -d border=40 -d scale=1 http://localhost:8000
docker logs exp 2>&1 | tail -5
echo "== results"
find .work/debug -type f -exec ls -la {} \;
