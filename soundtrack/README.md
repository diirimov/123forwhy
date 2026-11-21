# Skybound: animation soundtrack pipeline

An original 60-second cinematic-electronic cue for Shorts and TikTok, generated as code. The pipeline composes, renders, mixes, masters, exports and verifies:

```bash
sudo apt-get install fluidsynth fluid-soundfont-gm ffmpeg
pip install -r requirements.txt
python3 build.py      # ~70 s, deterministic (seeded)
python3 analyze.py    # spectrogram + loudness curve -> output/analysis.png
```

## Deliverables (`output/`)

| File | Spec |
|---|---|
| `soundtrack_final.wav` | 60.000 s, 48 kHz, 24-bit, stereo, -14.0 LUFS integrated, -1.3 dBTP, 0 clipped samples |
| `soundtrack_preview.mp3` | 320 kbps, 48 kHz |
| `soundtrack_narration_bed.wav` | Same master, -6 dB, with a 1–2.5 kHz presence dip so voice-over sits on top |
| `soundtrack_project.mid` | 16-track editable MIDI with tempo, key, every part and CC automation |
| `stems/{drums,bass,synths,lead,orchestra,fx}` | 24-bit pre-master stems (`.flac` is committed; `.wav` is rebuilt by `build.py`) |
| `cue_sheet.md` / `.csv` | Sections, sync points (seconds, frames at 30 fps, bar.beat), narration windows |
| `verification.json` | Measured duration, sample rate, channels, peaks, LUFS and clipping for every file |

## Music

- **Key and tempo:** D minor, 144 BPM. 36 bars of 1.667 s each = exactly 60 s.
- **Hook:** a syncopated 3-3-2 pluck figure over i–VI–III–VII, stated on the first downbeat.
- **Form:**
  - HOOK (0–6.7 s)
  - MOMENTUM (6.7–13.3 s)
  - BUILD (13.3–26.7 s), ending with three stop-time band stabs
  - BREAKDOWN (26.7–33.3 s): piano and choir, a Neapolitan Eb chord, a timpani roll, then one silent 8th note
  - CLIMAX (33.3–50 s): ends with a C–D tom lift
  - FINALE (50–56.7 s): the hook returns a whole step up in E minor
  - ENDING: a Picardy-third E-major hit that decays to silence
- **Measured loudness arc (LUFS):** -19.4 → -15.1 → -14.1 → -16.2 → -12.6 → -12.7 → -14.0

## How it is built

| Layer | Source |
|---|---|
| Drums, bass, supersaw chords, pluck, lead, arp, risers, impacts | Synthesized from scratch (`engine/dsp.py`): PolyBLEP oscillators, numba TPT state-variable filters, synthesized 808-style metallic hats |
| Strings, tremolo, choir, brass, horns, timpani, piano, celesta | FluidSynth with the FluidR3_GM SoundFont (MIT license), humanized timing (±6 ms) and velocity |
| Mix | Loudness-based gain staging, per-track EQ, kick-keyed sidechain, synthetic-IR convolution hall/plate/room, tempo-synced ping-pong delay, bus compression |
| Master | Corrective EQ, glue compression, a custom 4×-oversampled lookahead true-peak limiter, LUFS-targeted gain |

The code is split into three parts:

- `engine/score.py` holds the composition as data.
- `engine/dsp.py` holds the sound engine.
- `build.py` holds the mix and master.

To make a variation, change `PROG`, `HOOK`, `MEL` or `TARGET` and rebuild.

## Honest quality assessment

- **Competitive:** the electronic half, meaning drums, bass, supersaws, plucks and FX. These sounds are synthetic by nature, and here they are designed rather than taken from GM presets.
- **The weak link:** the orchestral layer. FluidR3_GM is a 2008 General MIDI SoundFont. Its strings, brass and choir have no legato, no round-robin samples and no dynamic crossfades. In this mix they are kept as supporting texture, but a trained ear will hear the strings and brass as "MIDI orchestra".
- **Not checked by ear:** this prototype was checked with measurements (LUFS, true peak, spectrum, correlation, spectrogram), not by listening. A human listening pass is still needed.

### Recommended hybrid workflow for a studio-grade final

1. Use this pipeline for composition, arrangement, timing and synth/drum production.
2. Import `soundtrack_project.mid` into a DAW (Reaper, Logic or Ableton). Replace only the orchestral tracks with a sample library. Free options: Spitfire LABS, BBC Symphony Orchestra Discover, Orchestral Tools Layers. Paid: Spitfire, Cinesamples, Musio.
3. Keep `stems/drums`, `bass`, `synths`, `lead` and `fx` as rendered audio, and swap in the new orchestra stem.
4. Re-master to -14 LUFS / -1 dBTP. Alternatively, rerun `build.py` with the orchestral WAVs swapped into `render_orchestra()`.

## Syncing to a video

No reference video was provided, so the cue sheet gives sync points on musically strong moments. When you have an animation:

1. Use `ffprobe` and `ffmpeg -vf "select='gt(scene,0.3)',showinfo"` to get the duration and scene cuts.
2. Shift the section boundaries and `CUES` in `score.py` to land on those cuts. Small tempo nudges between 136 and 150 BPM let the drop (bar 21) land exactly on the main reveal.
