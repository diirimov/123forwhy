# THE BRAZEN BULL — soundtrack

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
