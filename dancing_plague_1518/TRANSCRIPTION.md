# Dancing Plague 1518 (EP01): reconstruction notes

## Source search

No `EP01_ORIGINAL_SOUNDTRACK.wav`, project, MIDI or stems survive in this repository or any of its branches.
The only trace is a later commit (`8e15f16`, Medieval Medicine V3), which used the Dancing Plague track as a mix
reference for low-end weight and warmth. The other medieval soundtracks in the repo were checked against the
reference by chroma cross-correlation. None of them is this song, so everything here is rebuilt from the audio of the
uploaded animation (90.0 s, HE-AACv2 32 kbps).

## Analysis pipeline (`source/analysis/`)

1. **Narration removal:** UVR MDX-Net Inst HQ3 (ONNX). The narration occupies only 0–4 s ("In 1518, a …"), and the rest
   of the soundtrack is clean music.
2. **Grid:** beat tracking on the low band plus a least-squares fit gives **128.5 BPM** (period 0.4667 s, 16 ms residual),
   with bar 1 at 0.00 s. The reference spans 48 bars and was tuned to A440 (measured offset ±0.02 semitones).
3. **Structure:** a bar-level self-similarity matrix shows the hook bars (19 ≈ 37 ≈ 29, 20 ≈ 38).
4. **Melody:** basic-pitch (ONNX) on the separated music and on a drone-suppressed version (median-filter mask),
   plus drone-whitened CQT salience rolls on the 16th grid. Each phrase was confirmed in at least two occurrences.
5. **Bass:** raw low-band CQT read at the second half of every 16th step, so the kick transient doesn't mask it.
6. **Timbre:** harmonic profiles of sustained notes, an offbeat-hit spectrum, and octave-band balance and loudness
   of the loud section.

## What the original is

| Element | Finding |
|---|---|
| Tempo / metre | 128.5 BPM, 4/4, straight 16ths |
| Mode | D drone; melody in D with E natural on the hook and **E♭ / B♭ (Phrygian)** in the answer |
| Lead | recorder-like wooden pipe (fundamental-dominant; 2nd/3rd partials 13–25 dB down), doubled by fiddle |
| Drone | D3 + A3 (+D4), bagpipe/hurdy-gurdy style, under almost everything |
| Bass | deep plucked bass, D2 anchor, riff D–D3–D–F–F–C3–D; groove sections lean D→E→E♭; drop = legato glide D2→F2→C3 |
| Kick | four-on-the-floor, long low bloom (~47 Hz tail) |
| Offbeat | riq / frame drum with jingles: ~620 Hz skin "tak" + 4–9 kHz jingles on every offbeat 8th |
| Other | lute plucks, 16th shaker / ticks, re-bowed E♭4 "swell" before the hook (bars 12 and 18) |
| Mix | very sub-heavy (30–120 Hz dominant), lean low-mids, dark warm top; loud sections ≈ −11.8 LUFS |

### Hook (16th-note steps; D5 C5 A4 G4 A4 D4 F4 | G4 F4 E4 C4 D4)

```
step: 0   3  4   6   8       12  14 | 16  19 20  22  24 ...
      D5  C5 A4  G4  A4----  D4  F4 | G4  F4 E4  C4  D4-------
      3   1  2   2   4       2   2  | 3   1  2   2   8
```

It appears in four placements in the original: on the downbeat (bars 19, 37), with a pickup on beat 4 (bars 12–16),
shifted to beat 2 (opening, bars 1–4), and chained directly into the answer in the drop (bars 27–30).

### Answer (Phrygian): B♭4 G4 A4 – D4 E♭4 F4 E♭4 | D4 C4 B♭3 C4 D4

Drop variant: D5 C5 B♭4 G4 A4 D4 E♭4 | F4 E♭4 D4 C4 – B♭3 D4

### Tag (climax, bars 39–40): C♯5 D5 E♭5 | D5 B♭4 G4 D4

### Groove counter-line (bars 9–12): D5 – G4 | A4 – F4 | B♭4 | E♭4 swell → hook pickup

## Original form (48 bars)

| Bars | Time | Section |
|---|---|---|
| 1–8 | 0–15 s | intro under narration: hook on beat 2 ×2, B♭ answer, E♭ lead-in |
| 9–12 | 15 s | big hit, groove, D→E→E♭ bass, counter-line |
| 13–16 | 22 s | hook ×2 with pickup |
| 17–18 | 30 s | offbeat groove, E♭4 swell |
| 19–22 | 34 s | hook + answer |
| 23–25 | 41 s | transition / pre-drop dip |
| 26–30 | 47 s | drop: hook chained into the answer, gliding bass |
| 31–34 | 56 s | bass drop: sub D2↔E♭2, 16th ticks, A3 drone |
| 35–36 | 63 s | break on a C pedal |
| 37–40 | 67 s | climax hook + C♯–D–E♭ tag |
| 41–48 | 75 s | outro, fading (scored for the ending of the animation) |
