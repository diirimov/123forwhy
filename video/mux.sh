#!/bin/bash
# Concatenate rendered chunks and mux with the approved master WAV (unchanged, encoded to AAC only for MP4).
set -e
D=${1:?parts dir}; OUT=${2:-final.mp4}
WAV=../music/Craziest_Medieval_Diseases_128BPM_48k24.wav
printf "file '%s'\n" $D/part0.mp4 $D/part1.mp4 $D/part2.mp4 $D/part3.mp4 > $D/list.txt
ffmpeg -y -loglevel error -f concat -safe 0 -i $D/list.txt -i "$WAV" -map 0:v:0 -map 1:a:0 \
  -c:v libx264 -preset slow -crf 17 -profile:v high -pix_fmt yuv420p -r 60 -movflags +faststart \
  -c:a aac -b:a 320k -ar 48000 "$OUT"
