# THE PIED PIPER OF HAMELIN: premium 2D animated edit

| File | What |
|---|---|
| `PIED_PIPER_FINAL_1080P60.mp4` | The film: 1080×1920, 60 fps, 3,918 frames (65.30 s), H.264 High yuv420p (BT.709), 8.4 Mbps two-pass (SSIM 0.979 vs. the CRF 15 master), AAC 320 kbps. Audio checked against the approved soundtrack: 0-sample offset, r = 0.9998, −0.01 dB. English captions are burned in; no watermark or logos. |
| `audio/FOLLOW_THE_PIPER_V2.wav` | The approved V2 soundtrack, used unchanged (same sha1 as `follow_the_piper/FOLLOW_THE_PIPER_V2.wav`). No voices, effects or edits were added. |
| `data/PIED_PIPER_SYNC.json` | Beat synchronisation data: every beat and bar, sections, the 4 full-band silences, accents, instrument events (kick, toms, claps, stomps, snare, claves, bells, big drum, band answers), all 235 flute notes, shots and captions. Everything is given in seconds and in 60 fps frames. |
| `data/beatmap.json` | The director's beat map built from the waveform (`tools/beatmap.py`), including 60 fps band envelopes (low / mid / high / flute / onset). |
| `data/PIED_PIPER_SHOT_TIMELINE.json`, `SHOT_TIMELINE.md` | Final shot timeline: 37 shots with frame ranges, bar, picture and music cue. |
| `STORYBOARD.md` | The music-led storyboard. |
| `src/`, `render.js`, `tools/`, `assets/` | The complete, editable animation project. |

## How it was made

**The Dancing Plague study.** No source code for the Dancing Plague animation survives in any branch. The only copy is the uploaded 90 s render, so it was studied frame by frame (contact sheets, full-resolution stills, motion strips, a k-means palette). This film keeps its identity:

- **Characters:** flat cut-out characters with dark-brown ink outlines (#28170c); big egg-shaped heads with round white eyes, small pupils and pink blush; linen coifs with a coloured stripe; laced bodices; pleated skirts with belt pouches; puppet-segmented sleeves.
- **Grade:** the warm sepia/parchment grade with paper texture, heavy vignette and grain; purple dusk silhouettes; navy nights with warm windows.
- **Settings:** stacked timber-framed gables and oval cobblestones; the ink sun; the council chamber (leaded window, red banner, candles, green table).
- **Dance:** the knees-out squat dance.
- **Endings:** the lone object on night cobblestones at the end.

It improves on that rig with real articulation:

- **Rig (`src/rig.js`, `src/person.js`):** a 2.5D skeleton (3D local space → yaw → projection), so the same character turns correctly through front, three-quarter, profile and back views. Two-bone IK drives legs and arms. Walks plant their feet: the body advances exactly one stride per stride, and heel strikes land on the beats. Walks also have weight shift, hip roll, counter-swinging arms, anticipation and recoil.
- **Follow-through:** skirts, the cloak, hair, feathers and pouches swing by sampling the pose function at earlier times (t − 0.07 s, t − 0.16 s). It's deterministic, so frames can render in parallel, and it needs no simulation state.
- **Faces:** eyelids (open / half / sleepy / closed / narrow / wide), gaze, brows, mouths, blush, tears and sweat. The faces are yaw-aware, and the skull hair uses a "face window" so the back of the head is always correct.
- **The Piper:** pied doublet and hose (burgundy / dark green), a muted purple cloak with green lining, a feathered hat shadowing his eyes, pointed shoes, and a recorder whose fingers follow the real flute notes (MIDI → recorder fingering).
- **Rats (`src/rats.js`):** side and top views. Each rat has a trotting gait (diagonal leg pairs), a spine wave, a travelling-wave tail, ear twitches driven by flute onsets, a hind-leg standing pose and a frontal head turn. The swarms are choreographed paths (streams, rings, rows) that tighten into lockstep as the music takes hold.
- **World (`src/world.js`, `src/env.js`):** a one-point-perspective street space, with houses, props, characters and cobbles all in true perspective and parallax. Emissive lights (windows, torches, candles, the moon) are composited after the colour grade with depth-correct occlusion.

**Music as director.** `tools/beatmap.py` checked every event in the V2 sync file against the waveform (onsets within 9–25 ms, which is the attack-to-peak delay). Visual impacts lead by 12 ms so they land on the perceived transient. Every cut sits on a bar line, and the story follows the real structure:

- The soundtrack's B♭ / E♭ "betrayal" harmony is where the rats drown.
- The darker return of the hook carries the refusal to pay. The chest slams on the flute's falling B♭ bend.
- The final drop is the Piper's return at night.
- Each of the four full-band silences is used for a held breath: the stranger steps through the gate; he walks into the night; the procession freezes and turns to camera; the mountain closes.

**Loop.** The last frames settle on the exact framing of the first shot (the same street, moon, torch and fog), so the cut back to the procession is seamless.

## Rebuild

```
npm install            # @napi-rs/canvas (Skia)
python3 tools/beatmap.py
node render.js sheet out.jpg 0 65 60 6        # contact sheet
node render.js stills outdir 12.4 40.6       # stills
node render.js final 4                        # full film: 4 workers -> build/ -> PIED_PIPER_FINAL_1080P60.mp4
node tools/timeline.js                        # timeline + sync data
```

Rendering is deterministic: every frame is a pure function of time. It runs at about 0.5 s per frame per worker, roughly 9 minutes for the whole film on 4 cores, at about 300 MB per worker. A note for later projects: `@napi-rs/canvas` leaks about 8.6 MB per `drawImage()` under `destination-out`/`destination-in`, so the light occlusion uses multiply masks instead.

Fonts: Luckiest Guy and Cinzel Decorative (from the studio's earlier films), and IM FELL English (OFL).
