#!/usr/bin/env bash
# Render an HTML card to a PNG with headless Google Chrome.
# Usage: render-card.sh card.html out.png [WIDTHxHEIGHT]   (default 1200x630)
# Chrome 152's --headless=new --screenshot does not exit on its own; this
# waits until the PNG stops growing, then kills Chrome.
set -euo pipefail
html="$1"; out="$2"; size="${3:-1200x630}"; w="${size%x*}"; h="${size#*x}"
chrome="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
rm -f "$out"
"$chrome" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
  --window-size="$w,$h" --virtual-time-budget=6000 --screenshot="$out" "file://$(cd "$(dirname "$html")" && pwd)/$(basename "$html")" >/dev/null 2>&1 &
pid=$!
for _ in $(seq 1 60); do
  sleep 0.5
  if [ -s "$out" ]; then s1=$(stat -f %z "$out"); sleep 0.7; s2=$(stat -f %z "$out"); [ "$s1" = "$s2" ] && break; fi
done
kill "$pid" 2>/dev/null || true
pkill -f -- "--screenshot=$out" 2>/dev/null || true
sips -g pixelWidth -g pixelHeight "$out" | tail -2 | tr '\n' ' '; echo "$(stat -f %z "$out") bytes"
