#!/bin/bash
# review an encoded film: contact sheets at 5 fps per 13 s block, cut detection vs. the shot list, ffprobe
F=${1:-PIED_PIPER_V2_FINAL_1080P60.mp4}; O=${2:-review/watch}; mkdir -p $O
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,nb_frames,duration,sample_rate,channels -show_entries format=duration,bit_rate -of default=nw=1 "$F"
for s in 0 13 26 39 52; do ffmpeg -v error -y -ss $s -t 13.3 -i "$F" -vf "fps=5,scale=162:288,tile=11x6" -frames:v 1 $O/w_$s.jpg; done
ffmpeg -hide_banner -i "$F" -vf "scale=270:480,select='gt(scene,0.2)',metadata=print" -an -f null - 2>&1 | grep -oE "pts_time:[0-9.]+" | cut -d: -f2 > $O/cuts.txt
node -e "
const T=require('./data/PIED_PIPER_V2_SHOT_TIMELINE.json'); const cuts=require('fs').readFileSync('$O/cuts.txt','utf8').trim().split('\n').map(Number);
let miss=0; for (const s of T.shots.slice(1)) { const d=Math.min(...cuts.map(c=>Math.abs(c-s.start))); if (d>0.04) { miss++; console.log('cut not detected near', s.start.toFixed(3), s.id, 'nearest off by', d.toFixed(3)); } }
console.log('shots', T.shots.length, 'detected cuts', cuts.length, 'undetected', miss);"
