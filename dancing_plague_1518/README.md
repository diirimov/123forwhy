# Dancing Plague 1518: Extended Dance Version

This is a reconstruction of the EP01 soundtrack, extended to about 2:45 as a standalone dance track.
It keeps the same hook, tempo (128.5 BPM), D drone with Phrygian E♭/B♭ colour, pipe + fiddle lead, riq offbeats
and gliding D–F–C bass. See `TRANSCRIPTION.md` for how the original was recovered from the animation's audio.

## Deliverables

| File | What |
|---|---|
| `DANCING_PLAGUE_1518_EXTENDED.mp3` | 320 kbps CBR, 48 kHz |
| `DANCING_PLAGUE_1518_EXTENDED.wav` | lossless master, 48 kHz / 24-bit, about −10 LUFS, −1 dBTP |
| `stems/DP1518_STEM_*.flac` | 8 lossless 24-bit stems: drums, percussion, bass, drone, lute, strings, lead, fx. They are post-fader with their reverb, at master gain and pre-limiter, so summing them gives the pre-master mix |
| `DANCING_PLAGUE_1518_BEATS.json` | every beat and downbeat, sections and accent hits, in seconds (grid includes the light 52 % swing) |
| `DANCING_PLAGUE_1518_CUES.md` | arrangement sheet |
| `source/` | generator code |

## Rebuild

```
pip install numpy scipy soundfile pyloudnorm librosa
cd source
python3 render.py ..            # ~2.5 min on 4 cores; writes everything above
python3 qa.py ../DANCING_PLAGUE_1518_EXTENDED.wav <reference_music.wav>
```

- `engine.py`: instrument models and DSP (pipe, fiddle, hurdy-gurdy, lute, drones, deep/growl/sub bass, kick, riq, …)
- `song.py`: transcribed motifs, bass riffs, drum styles, the 87-bar arrangement
- `render.py`: mix (sidechain, room and plate), master chain, exports
- `qa.py`: compares a render with the reference (tonal balance, loudness per 4 bars, hook chroma match, mono, phone speaker)
- `analysis/`: the scripts used to recover the original (MDX separation, beat grid, self-similarity, melody isolation,
  salience rolls, bass roll, basic-pitch roll)
