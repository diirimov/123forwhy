# THE BRAZEN BULL — soundtrack

## V3 (current) — ethnic vocal hook
* `BRAZEN_BULL_FINAL_V3.wav` + `BRAZEN_BULL_BEATMAP_V3.json` (+ `vocal_hook` section). Identical to V2 except every
  synthesised HA/HEY/HO chant is replaced by the ElevenLabs expressive male vocal (`samples_original/An_expressive_haunt_2.wav`),
  sliced into natural phrases and used as a call-and-response hook. Non-vocal stems are bit-identical to V2.
* `sfx_isolated_v3/` — all isolated one-shots incl. the vocal slices. Regenerate: `python3 src/compose_v3.py .`

## V2 — ElevenLabs sound-design upgrade
* `BRAZEN_BULL_FINAL_V2.wav` — 60.000 s, 48 kHz, 24-bit PCM stereo, -14.0 LUFS, -1.35 dBTP.
* `BRAZEN_BULL_BEATMAP_V2.json` — beats, sections, drops, silences, every event (time + 60 fps frame),
  `signature_motif` (all bull-roar moments) and `isolated_sfx`; sample events carry `sfx_file`.
* `sfx_isolated_v2/` — clean processed one-shots exactly as used (tuned roar, wail answers/choirs, shrieks,
  door, fire, scan, impacts, heartbeat) for animation sync.
* `samples_original/` — the supplied ElevenLabs files, untouched (backup). `v1_backup/` — the V1 master + beat map.
* Regenerate: `python3 src/compose_v2.py .` (needs `rubberband-cli` + `pip install pyrubberband librosa`).

## V1

* `BRAZEN_BULL_FINAL.wav` — final master, 60.000 s, 48 kHz, 24-bit PCM, stereo, -14.0 LUFS integrated, -1.35 dBTP.
* `BRAZEN_BULL_BEATMAP.json` — beats, downbeats, sections, drops, silences, breaks and every musical / sound-design event
  (time in seconds + 60 fps frame index), generated from the same render that produced the WAV.

136 BPM · 4/4 · 34 bars · E Phrygian (Phrygian-dominant twist in the final drop).

Everything is synthesised from scratch by the code in `src/` (no samples): physical-model bouzouki, double-reed aulos,
glottal/formant male voices, bronze bell/anvil modal synthesis, tribal percussion, driven bass, convolution reverbs,
sidechain, true-peak limiting and loudness normalisation.

Regenerate (deterministic):

```
pip install numpy scipy numba soundfile pyloudnorm matplotlib
cd brazen_bull && python3 src/compose.py .
python3 src/analyze.py BRAZEN_BULL_FINAL.wav spectrogram.png   # technical QC report
```
