#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
FRAME_DIR="$ROOT_DIR/output/reel-frames"
AUDIO_DIR="$ROOT_DIR/content/audio/voiceovers"
OUT_DIR="$ROOT_DIR/content/assets/social/reels"
TMP_DIR="$ROOT_DIR/output/reel-build"

mkdir -p "$OUT_DIR" "$TMP_DIR"

build_reel() {
  local reel_id="$1"
  local audio="$2"
  local output="$3"
  shift 3
  local durations=("$@")
  local concat_file="$TMP_DIR/reel-${reel_id}.ffconcat"

  printf 'ffconcat version 1.0\n' > "$concat_file"
  local index=1
  for duration in "${durations[@]}"; do
    local padded
    padded=$(printf '%02d' "$index")
    printf "file '%s'\n" "$FRAME_DIR/reel-${reel_id}-scene-${padded}.png" >> "$concat_file"
    printf 'duration %s\n' "$duration" >> "$concat_file"
    index=$((index + 1))
  done
  local last
  last=$(printf '%02d' "${#durations[@]}")
  printf "file '%s'\n" "$FRAME_DIR/reel-${reel_id}-scene-${last}.png" >> "$concat_file"

  ffmpeg -y -hide_banner -loglevel error \
    -safe 0 -f concat -i "$concat_file" \
    -i "$AUDIO_DIR/$audio" \
    -vf "fps=30,format=yuv420p" \
    -c:v libx264 -preset medium -crf 18 \
    -c:a aac -b:a 192k -ar 48000 \
    -shortest -movflags +faststart \
    "$OUT_DIR/$output"
}

build_reel_language() {
  local reel_id="$1"
  local language="$2"
  local audio="$3"
  local output="$4"
  shift 4
  local durations=("$@")
  local concat_file="$TMP_DIR/reel-${reel_id}-${language}.ffconcat"

  printf 'ffconcat version 1.0\n' > "$concat_file"
  local index=1
  for duration in "${durations[@]}"; do
    local padded
    padded=$(printf '%02d' "$index")
    printf "file '%s'\n" "$FRAME_DIR/reel-${reel_id}-${language}-scene-${padded}.png" >> "$concat_file"
    printf 'duration %s\n' "$duration" >> "$concat_file"
    index=$((index + 1))
  done
  local last
  last=$(printf '%02d' "${#durations[@]}")
  printf "file '%s'\n" "$FRAME_DIR/reel-${reel_id}-${language}-scene-${last}.png" >> "$concat_file"

  ffmpeg -y -hide_banner -loglevel error \
    -safe 0 -f concat -i "$concat_file" \
    -i "$AUDIO_DIR/$audio" \
    -vf "fps=30,format=yuv420p" \
    -c:v libx264 -preset medium -crf 18 \
    -c:a aac -b:a 192k -ar 48000 \
    -shortest -movflags +faststart \
    "$OUT_DIR/$output"
}

build_reel 1 reel-01-manual-follow-up-en.wav sosa-tech-reel-01-manual-follow-up-en.mp4 3.1 4.0 4.0 4.0 5.0 4.0
build_reel 2 reel-02-whatsapp-flow-en.wav sosa-tech-reel-02-whatsapp-flow-en.mp4 3.2 4.3 3.2 3.8 4.0 3.3
build_reel 3 reel-03-systems-behind-sosa-en.wav sosa-tech-reel-03-systems-behind-sosa-en.mp4 3.0 3.4 3.3 3.4 4.0 2.6
build_reel_language 1 es reel-01-manual-follow-up-es.wav sosa-tech-reel-01-manual-follow-up-es.mp4 3.8 4.8 4.8 4.8 6.0 5.2
build_reel_language 2 es reel-02-whatsapp-flow-es.wav sosa-tech-reel-02-whatsapp-flow-es.mp4 3.6 4.7 3.6 4.1 4.8 3.2
build_reel_language 3 es reel-03-systems-behind-sosa-es.wav sosa-tech-reel-03-systems-behind-sosa-es.mp4 3.8 4.8 4.6 5.2 6.0 4.15

for video in "$OUT_DIR"/*.mp4; do
  ffprobe -v error -show_entries stream=width,height,r_frame_rate -show_entries format=duration \
    -of default=noprint_wrappers=1 "$video"
done
