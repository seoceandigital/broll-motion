#!/usr/bin/env bash
# Preparacion inicial en el proyecto del usuario. Instala Playwright y Chromium en ./motion/node_modules.
set -e
MOTION_DIR="${1:-./motion}"
mkdir -p "$MOTION_DIR"/{clips,dist,out,work,inputs}
# Ruta absoluta: dentro del subshell se hace cd y una ruta relativa dejaria de resolver.
MOTION_DIR="$(cd "$MOTION_DIR" && pwd)"
missing=()
command -v node >/dev/null || missing+=("node (https://nodejs.org)")
command -v ffmpeg >/dev/null || missing+=("ffmpeg (macOS: brew install ffmpeg)")
command -v python3 >/dev/null || missing+=("python3")
if [ ${#missing[@]} -gt 0 ]; then echo "Faltan: ${missing[*]}"; exit 1; fi
python3 -c "import numpy" 2>/dev/null || python3 -m pip install --user numpy || python3 -m pip install --break-system-packages numpy
if [ ! -d "$MOTION_DIR/node_modules/playwright" ]; then
  [ -f "$MOTION_DIR/package.json" ] || echo '{"private":true}' > "$MOTION_DIR/package.json"
  (cd "$MOTION_DIR" && npm install --silent playwright && npx playwright install chromium)
fi
ffmpeg -hide_banner -encoders 2>/dev/null | grep -q prores_ks || echo "Aviso: tu ffmpeg no trae el codificador prores_ks; los paneles transparentes fallaran."
echo "Listo. Los clips van en $MOTION_DIR/clips y los renders en $MOTION_DIR/out."
