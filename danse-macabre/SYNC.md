# DANSE MACABRE: Everyone Must Dance (sync sheet)

**File:** `DANSE_MACABRE_FINAL.wav`. 60.000 s, stereo, 48 kHz, 24-bit PCM
**Tempo:** 136 BPM, 4/4. 1 beat = 0.4412 s, 1 bar = 1.7647 s, 34 bars total
**Key:** D harmonic minor (C♯ leading tone). Neapolitan E♭ chord used as a twist
**Master:** about −10.0 LUFS integrated, −1.0 dBTP true peak, no clipping
**Groove:** light 16th-note swing (off-16ths land about 8 ms late)

## Hook (4 bars, starts at 0.000 s)
`A–D E F–D A5(syncopated)–G F E–C♯ | same, peaking on B♭5 | G G B♭ A … | C♯ (leading tone) … E`
Chords: Dm | B♭ | Gm | A. The signature accent is the high syncopated note on the "e" of beat 2 (step 7).

## Sections
| Time (s) | Bars | Section |
|---|---|---|
| 0.000 | 1–2 | Hook straight away. Fiddle, Death's tritone double-stop (A+E♭), church bell, hurdy-gurdy drone, heartbeat kick, coffin knocks |
| 3.529 | 3–8 | **DROP 1**: galloping bass, four-on-the-floor kick, harpsichord oom-pah, woodblocks, organ hit, low bell |
| 14.118 | 9–12 | Call and response: fiddle calls, harpsichord answers (B♭–C–Dm–A) |
| 21.176 | 13–20 | **DROP 2**: rolling 16th bass, harpsichord arpeggios, bone xylophone, bone clicks/rattles, chains, string stabs |
| 31.765 | 19 | Unexpected Neapolitan E♭ bar with shawm stabs and a xylophone lick |
| 35.294 | 21–24 | Build: climbing tremolo fiddle, organ and strings crescendo, kick density rises |
| 41.912 | 24 beat 4 | One-beat breath before the drop: only coffin knocks and a reverse swell |
| 42.353 | 25–32 | **GRAND DANCE OF DEATH**: full ensemble, shawm and octave fiddles, organ, strings |
| 52.941 | 31 | Neapolitan E♭ twist (second time) |
| 56.471 | 33–34 | Ending: hook head, then the **final hit** |
| 57.794 | 33 beat 4 | **FINAL HIT**: tutti D minor, impact, bells |
| 59.559 | 34 beat 4 | Four rising coffin knocks and a reverse swell into the loop point |
| 60.000 | | Loops back to 0.000 |

## Major accents and impacts
- **Bell + hook start:** 0.000
- **Drop impacts (impact + low bell + organ):** 3.529, 21.176, 42.353 (the biggest), 57.794 (final)
- **Hook signature syncopated note** (bells double it in drop 2 and the grand dance): 0.780, 2.544, 4.309, 6.074, 21.956, 23.721, 29.015, 30.780, 43.133, 44.897, 50.192, 51.956
- **Kick roll** in the build: 40.588 to 41.912 (16th notes)
- **Snare/bone-rattle fills** at the end of phrases (last beat of bars 8, 12, 16, 20, 28, 32): 13.676, 20.735, 27.794, 34.853, 48.971, 56.029
- **Coffin "knock-knock"** on beat 4 "e" and "a" of every even bar during the grooves
- **Beat grid:** beat *n* (0-based) = n × 0.441176 s. Bar *b* (1-based) = (b−1) × 1.764706 s

## Source
`source/` holds the full synthesis, arrangement and mix code (numpy, scipy, numba, pedalboard). Every sound is synthesized from scratch: no samples and no voices.
Rebuild with `python3 compose.py && python3 mix.py g.json DANSE_MACABRE_FINAL.wav`, where `g.json` contains `{}`.
