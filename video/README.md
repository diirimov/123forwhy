# 3 Scariest Diseases of the Middle Ages — animated short

- `3_Scariest_Diseases_Middle_Ages_1080x1920_60fps.mp4` — final video: 1080×1920 vertical, 60 fps, H.264 High / yuv420p, AAC 320 kbps, exactly 90.000 s (5,400 frames).
- Audio: the approved master `../music/Craziest_Medieval_Diseases_128BPM_48k24.wav`, unedited (no SFX added, no cuts, no level changes; only AAC-encoded for the MP4 container).
- `STORYBOARD.md` — scene-by-scene plan with bar/beat sync points.

## How it is built
All art is drawn procedurally in HTML5 Canvas (`src/`): a rigged cartoon character system (walk/run/panic/recoil/pray poses, expressions, sweat, fever flush), plague doctor, rats and fleas, timber-framed town, perspective alley, Europe map with a Black Death spread front (Natural Earth outlines), cathedral, city gate, interiors, clock/gears, and an illustrated medical book. Every frame is rendered deterministically at `t = frame / 60` in headless Chromium, so motion is locked to the 128 BPM grid (characters step on beats, cameras punch on kicks, slams land on the hook's 3-3-2 hits).

## Re-render
```
node render.js video out/part0.mp4 0 1350      # (and 1350-2700, 2700-4050, 4050-5400)
./mux.sh out final.mp4
node render.js stills out/stills 15.0 45.0     # spot-check any time
```
Fonts: Pirata One, Cinzel, IM Fell English (SIL Open Font License, from Google Fonts).
