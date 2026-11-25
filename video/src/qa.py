"""Frame-by-frame QA of the final video: python3 src/qa.py out/final.mp4"""
import subprocess, sys, json
import numpy as np

path = sys.argv[1]
probe = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-count_frames', '-show_entries',
                                   'stream=width,height,r_frame_rate,nb_read_frames,duration', '-of', 'json', path], capture_output=True, text=True).stdout)['streams'][0]
print('video:', probe)
w, h = 108, 192
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-vf', f'scale={w}:{h}', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], capture_output=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(float) / 255
n = len(fr); print('frames decoded:', n)
mean = fr.mean((1, 2))
d = np.abs(np.diff(fr, axis=0)).mean((1, 2))
black = np.where(mean < 0.04)[0]; white = np.where(mean > 0.93)[0]
print('black frames:', list(black[:20]), 'white frames:', list(white[:20]))
# frozen spans: consecutive near-identical frames
frozen, run = [], 0
for i, v in enumerate(d):
    if v < 0.0008: run += 1
    else:
        if run >= 12: frozen.append((i - run, i, run))
        run = 0
if run >= 12: frozen.append((len(d) - run, len(d), run))
print('frozen spans >=12f (start,end,len):', frozen)
# single-frame pops: frame differs from both neighbours while neighbours match
pops = []
for i in range(1, n - 1):
    a = np.abs(fr[i] - fr[i - 1]).mean(); b = np.abs(fr[i + 1] - fr[i]).mean(); c = np.abs(fr[i + 1] - fr[i - 1]).mean()
    if a > 0.06 and b > 0.06 and c < 0.25 * min(a, b): pops.append((i, round(i / 60, 3)))
print('single-frame pops:', pops[:30])
print('mean luma: min %.3f median %.3f max %.3f' % (mean.min(), np.median(mean), mean.max()))
# visual change cadence: count "cuts" (big jumps)
cuts = [round((i + 1) / 60, 2) for i, v in enumerate(d) if v > 0.08]
print('hard changes:', len(cuts), 'max gap between visual changes (s): %.2f' % (np.diff([0] + cuts + [60]).max()))
