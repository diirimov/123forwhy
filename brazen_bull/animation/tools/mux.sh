#!/bin/bash
# Re-attach audio to the rendered picture without re-rendering: tools/mux.sh video_noaudio.mp4 audio.wav out.mp4
set -e
ffmpeg -y -loglevel error -i "$1" -i "$2" -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 320k -ar 48000 -shortest -movflags +faststart "$3"
