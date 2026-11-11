#!/usr/bin/env bash
# Builds the finished MP4s (video + music) from a concept JSON.
# Usage: build.sh concept.json out_dir [landscape] [vertical]   (default: both formats)
# Takes ~15 min per format. Run it in the background.
set -euo pipefail
CFG=$(realpath "$1"); OUT=$(realpath -m "$2"); shift 2
FORMATS=("$@"); [ ${#FORMATS[@]} -eq 0 ] && FORMATS=(landscape vertical)
DIR=$(cd "$(dirname "$0")" && pwd)
NAME=$(basename "$CFG" .json)
mkdir -p "$OUT"
for F in "${FORMATS[@]}"; do
  STYLE=$(python3 -c "import json,sys;m=json.load(open(sys.argv[1])).get('music',{});print(m.get(sys.argv[2],'upbeat') if isinstance(m,dict) else m)" "$CFG" "$F")
  echo "== $F (music: $STYLE)"
  node "$DIR/render.js" --config "$CFG" --format "$F" --out "$OUT/${NAME}_${F}_silent.mp4"
  python3 "$DIR/music.py" --style "$STYLE" "$OUT/${NAME}_${F}_raw.wav"
  ffmpeg -v error -y -i "$OUT/${NAME}_${F}_raw.wav" -af loudnorm=I=-14:TP=-1:LRA=11 -ar 44100 "$OUT/${NAME}_${F}_music.wav"
  ffmpeg -v error -y -i "$OUT/${NAME}_${F}_silent.mp4" -i "$OUT/${NAME}_${F}_music.wav" -c:v copy -c:a aac -b:a 192k -shortest "$OUT/${NAME}_${F}.mp4"
  ffmpeg -v error -y -i "$OUT/${NAME}_${F}.mp4" -vf "fps=1/2,scale=$([ "$F" = vertical ] && echo 270 || echo 480):-1,tile=$([ "$F" = vertical ] && echo 8x2 || echo 4x4)" -frames:v 1 "$OUT/${NAME}_${F}_sheet.png"
  rm -f "$OUT/${NAME}_${F}_raw.wav" "$OUT/${NAME}_${F}_silent.mp4"
  echo "done: $OUT/${NAME}_${F}.mp4"
done
