#!/bin/bash
# validate the final export
f="$1"
echo "== ffprobe"; ffprobe -v error -show_entries stream=index,codec_name,profile,width,height,pix_fmt,r_frame_rate,avg_frame_rate,nb_frames,duration,sample_rate,channels,bit_rate -show_entries format=duration,size,bit_rate -of default=nw=1 "$f"
echo "== decoded frame count"; ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 "$f"
echo "== loudness / true peak of the delivered audio"; ffmpeg -nostats -i "$f" -af ebur128=peak=true -f null - 2>&1 | grep -E "I:|Peak:" | tail -2
echo "== black segments (expected only in the three musical silences)"; ffmpeg -nostats -i "$f" -vf "blackdetect=d=0.05:pix_th=0.06" -an -f null - 2>&1 | grep blackdetect
echo "== frozen frames >0.3s"; ffmpeg -nostats -i "$f" -vf "freezedetect=n=0.0008:d=0.3" -an -f null - 2>&1 | grep freeze_ | head
