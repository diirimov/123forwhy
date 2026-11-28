# DANSE MACABRE: Everyone Must Dance (animated music video)

60.000 s · 1080×1920 (9:16) · true 60 fps · 3,600 frames · H.264 + AAC 48 kHz

**Deliverable:** `DANSE_MACABRE_FINAL_1080P60.mp4`

This is a separate project. The Dancing Plague project was not touched. Its delivered video was used as the
visual reference: toon outlines, big-headed medieval cast, parchment grain, vignette, word-by-word narration
captions, and narration flowing into music.

## Pipeline
Everything is drawn procedurally with Skia (vector paths), graded in NumPy/OpenCV and encoded with FFmpeg.

| File | Role |
|---|---|
| `src/beatmap.py` | Analyses the actual WAV and writes `data/beatmap.json`: tempo, beat offset, downbeats, bars, kick and percussion onsets, sections, accents |
| `src/core.py` | Canvas helpers, easing, noise, and the beat-grid timing (`bar_t(bar, step)`) |
| `src/rig.py` | Front-view 2D rig with two-bone IK for arms and legs (planted feet), plus the choreography system: routines `macabre`, `shuffle`, `grand`, `fiddler`. Poses land on the beat with anticipation and follow-through; head and arms lag the body for overlapping action |
| `src/skel.py` | Articulated skeleton (skull, hinged jaw, ribcage, spine, pelvis, long bones, hands, feet) and **Death**: hood, flowing cloak with crimson lining, antique fiddle. Bow strokes follow the real fiddle notes of the soundtrack (`data/fiddle_notes.json`) |
| `src/humans.py` | King, knight (detachable armour pieces), merchant, bishop, peasant, jester, nobleman, townswoman, townsman |
| `src/env.py` | Painted gothic environments in parallax layers (cemetery, throne room, courtyard, treasure room, cathedral interior, field, street, town square, rooftops), plus live elements: candles, torches, fog, dust, bells, banners, music notes |
| `src/actors.py` | Placing characters, crowds, emerging hands, bone assembly, coins, sparkles |
| `src/scenes.py` | The 33-shot list, every cut on the beat grid |
| `src/captions.py` | Narration word reveal, gothic title reveal, story captions |
| `src/post.py` | Grade, bloom, vignette, paper texture, film grain |
| `src/render.py` | Frame renderer with whip-pan and wipe transitions and loop closure |
| `src/audio_mix.py` | Final audio mix |

## Rebuild
```
pip install skia-python numpy scipy opencv-python-headless soundfile pyloudnorm
python src/beatmap.py
python src/audio_mix.py
# render in chunks (Windows: run each in its own terminal)
cd src && python render.py 0 900 ../build/chunk0.mp4   (… 900-1800, 1800-2700, 2700-3600)
ffmpeg -f concat -i build/list.txt -i build/final_audio.wav -c:v copy -c:a aac -b:a 320k -ar 48000 DANSE_MACABRE_FINAL_1080P60.mp4
```
To check single frames: `python render.py --still 0,1200,2541 out_#.jpg`.

## Audio
- `DANSE_MACABRE_FINAL.wav` is unchanged in timing, pitch and content.
- Under the opening narration only (0 to 5.75 s), its volume is lowered: −14 dB, then −9 dB under the title, then back to unity.
- After 5.8 s the mix is bit-identical to the source (verified in `audio_mix.py`).
- The narration file is used exactly as provided, with a −1.2 dB gain only.

## Data
- `data/beatmap.json`: 136.000 BPM, offset 0.002 s, 34 bars, downbeats, beat frames, kick and percussion onsets, sections, accents.
- `data/scene_timing.json`: every shot (seconds and frames), narration word times, captions, key moments.
