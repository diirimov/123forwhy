# THE PIED PIPER OF HAMELIN (V2): the animation rebuilt around the new soundtrack

| File | What |
|---|---|
| `PIED_PIPER_V2_FINAL_1080P60.mp4` | The film. 1080×1920 at 60 fps, 3,918 frames, 65.30 s. H.264 High (yuv420p, BT.709), two-pass 8.7 Mbps (71 MB). Audio checked against the approved WAV: 0-sample offset, r = 0.9998. Audio (AAC 320 kbps, 48 kHz) = `audio/PIED_PIPER_V2_MIX.wav`: the approved soundtrack, unchanged, with a short opening narration ("In twelve eighty-four... one hundred and thirty children vanished.", 0.10-4.11 s, Kokoro TTS voice am_onyx; music ducked 4 dB under it only; `tools/make_voiceover.py`). English captions are burned in; no added sound effects, no watermark. |
| `audio/PIED_PIPER_NEW_SOUNDTRACK.wav` | The approved new soundtrack, byte-identical to `pied_piper_soundtrack/PIED_PIPER_NEW_SOUNDTRACK.wav`. |
| `AUDIO_ANALYSIS.md`, `tools/analyze_audio.py` | The soundtrack measured from the waveform: tempo and beat phase, transients per band (checked against the score's event list), per-bar loudness, breaks, energy jumps (the drops), spectral novelty and flute phrases. |
| `data/beatmap.json` | The director's beat map the film runs on, including 60 fps band envelopes. |
| `data/PIED_PIPER_V2_SYNC.json` | Updated beat-sync data. It covers every beat, section, drop, break, chord, accent and instrument event, all flute notes and phrases, the measured transients, the shots and the captions. Every time is given in seconds and in 60 fps frames. |
| `data/PIED_PIPER_V2_SHOT_TIMELINE.json`, `SHOT_TIMELINE.md` | The updated shot timeline: 48 shots, each with frame range, bar, picture and music cue. |
| `STORYBOARD.md` | The music-led storyboard, including what changed from V1 and why. |
| `src/`, `render.js`, `tools/` | The complete editable project. |

The earlier film (`pied_piper_film/`) and all soundtracks are untouched.

## How it was made

**Dancing Plague study.** No animation source code for Dancing Plague exists in any branch (only its music source), so its uploaded render was studied frame by frame next to the V1 Pied Piper film. The main difference was staging:

- DP shoots from waist height. Its front characters fill about 45 % of the frame height, crowds are staggered in two or three rows, and a solid wall of stacked gables sits behind them.
- V1 shot tiny figures in deep, empty one-point streets.

V2 encodes the DP staging in `src/dp.js` and uses it for every street shot. It keeps the studio's character designs, palette, paper grade, vignette and grain, and adds the DP silhouette scenes and the red shoe.

**Choreography (`src/chor.js`).**

- The DP dance vocabulary is built from full-body poses: the knees-out squat, jig, knee-lift stomp, spin, clap on every beat, sway, and the betrayal's half-time squat. Each pose uses IK legs with planted feet, pelvis bob and roll, spine lean, side bend and twist, arms and head.
- Dancers take a `delay`, which makes canons and waves through a crowd possible.
- The procession walk is perfect lockstep with still arms, a shared slow sway, and heads that tilt in a canon on every bar. It is meant to look uncanny because it is too precise, never zombie-like.
- Walk speed is locked to stride (speed = stride / stance time), so feet never slide and heels land on the beats.
- Follow-through comes from lagged poses (t − 0.07 s and t − 0.16 s), as in V1.

**Music as director.** Cuts land on bars, half bars, beats and 16ths: four beat-cuts in the hook, four 16th-cuts on the flute's solo run, and four quarter-bar trades in the climax. Actions are locked to measured events:

- heads snap on the plucked answer;
- villagers leap on the claps;
- the rats hop through their rows on the 16th scurry, the rings pulse on the kick, and lines of rats rise on the plucked notes;
- the chest slams on the betrayal downbeat;
- the faces freeze in the break;
- four groups vanish on the four stutter stabs, and the rock seals in the silence.

## Rebuild

```
npm install                                      # @napi-rs/canvas (Skia); V2 links ../pied_piper_film/node_modules
python3 tools/analyze_audio.py                   # audio analysis -> data/beatmap.json + AUDIO_ANALYSIS.md
node render.js sheet out.jpg 0 65 60 6           # contact sheet
node render.js stills outdir 19.5 40.7           # single frames
node render.js final 4                           # 4 workers -> build/ -> PIED_PIPER_V2_FINAL_1080P60.mp4 (CRF 15 master)
node tools/timeline.js                           # shot timeline + sync data
tools/review.sh <film.mp4>                       # ffprobe, 5 fps review sheets, cut detection vs. the shot list
```

Frames are deterministic (each is a pure function of time). A full render takes about 9 minutes on 4 cores.
