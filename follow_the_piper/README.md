# FOLLOW THE PIPER

A dark medieval dance track about the Pied Piper of Hamelin: a village dances to a tune it can't resist, without noticing where the musician is leading it.

| | |
|---|---|
| `FOLLOW_THE_PIPER_FINAL.wav` | 48 kHz / 24-bit stereo, **65.294 s** (exactly 37 bars), **−14.0 LUFS** integrated, **−1.3 dBTP** true peak (ffmpeg EBU R128), no clipping, LRA 3.5 LU |
| `FOLLOW_THE_PIPER_SYNC.json` | BPM, all 148 beats (with a 0–1 energy value per beat), 37 downbeats, 7 sections, 49 accents, per-instrument event times (kick, stomp, clap, snare, bell, chant, laugh, breath, boom), and all 242 flute notes with their pitch |
| `source/` | the generator: score, instruments, mix, master, QA |

**136 BPM · 4/4 · A minor (harmonic minor) with a tritone D♯ as the Piper's signature note · loops seamlessly**

## What made *Dancing Plague 1518* work, and what's different here

I analysed the uploaded Dancing Plague video audio and the reconstruction notes, transcription and stems on the `claude/epic-darwin-hshpai` branch. It worked because of:

1. **A short, singable pipe hook** (2 bars) that keeps coming back in different metric placements.
2. **A modal drone that feels familiar but wrong**: D with Phrygian E♭/B♭.
3. **A constant dance engine** underneath: four-on-the-floor kick with a long sub, offbeat riq, very heavy low end.
4. **Breakdown → re-drop architecture** with the hook always returning.

What I kept is the *principles*, not the material. This track uses a new key, a new mode, a new melody shape, a new groove and new instruments:

| | Dancing Plague | Follow the Piper |
|---|---|---|
| Tonality | D drone, Phrygian E♭/B♭ | A minor / harmonic minor, **tritone D♯** as the signature, B♭/E♭ only in the betrayal |
| Hook shape | descending, stepwise (D5 C5 A4 G4 …) | **rising tresillo leap** (A4 · E5 · A5, 3+3+2) that hangs on the tritone, then a written **pause and a "giggle"** |
| Bass | plucked D–F–C riff, legato glides | **galloping "rat-run" 16th pairs** on the offbeats, sidechained under the kick |
| Lead | synthesised pipe + fiddle | **real sampled baroque recorders** (alto lead, soprano octave, tenor low) with scoops, grace notes, vibrato and legato |
| Crowd | none | wordless chanting that **answers the flute's pause**, humming, synchronised breaths, distant laughter |

## The hook

16th-note grid, one bar per line. Harmony is `| Am | F | Am | F E |`.

```
CALL    A4 . . E5 . . A5 . G#5 A5 E5 . D#5 - - -     tresillo leap up, hangs on the tritone
GIGGLE  .  .  .  .  .  .  E6 . E6 . B5 - . . . .     the Piper laughs; the crowd answers in the gap ("hu-HA")
CALL 2  A4 . . E5 . . A5 . B5 C6 B5 . G#5 . E5 .
CADENCE F5 . . E5 . . C5 . B4 . C5 B4 G#4 - - -      open on G#  (closed version lands on A)
```

How it's built to stick: the tresillo rhythm repeats in three of the four bars; there is one memorable leap (the octave A4→A5); the hanging tritone D♯ is an unresolved question that the next bar's pause leaves hanging; and the call-and-response is a high "hee-hee-hoo" against a low group chant. Variations are written in rather than looped: an ornamented call, a chattering giggle, a "wrong-note" giggle (B♭ instead of B) in the return, an obsessive pass where the pause disappears, and a stutter bar.

## Arrangement

| Bars | Time | Section | What happens |
|---|---|---|---|
| 1–2 | 0.00–3.53 | **The hypnotic hook** | flute alone from 0.000 s, distant bell, low drone, soft heartbeat drum; the written pause leaves room for narration |
| 3–7 | 3.53–12.35 | **The rats awaken** | crowd stomps + claps, strumstick, shaker, bass → tambourine → filtered kick + darbuka → first crowd answer and psaltery chops → build: hook cut off mid-bar, rope-snare roll, group inhale |
| 8–14 | 12.35–24.71 | **First drop** | full kick, galloping bass, claps/rope snare, tambourine 16ths, darbuka, psaltery offbeat chops, buzzing hurdy-gurdy, band stops in each pause while the crowd chants; from bar 12: soprano octave, tresillo stomps, anvil, choir swell |
| 15–18 | 24.71–31.76 | **The betrayal** | the expected cadence turns: B♭ (♭II) and then E♭ (the tritone) under an A drone that refuses to move; half-time; a unison hit, then a pause with only stomps (laughter and an echo of the giggle); the groove re-ignites on E with a chromatic creep up to A |
| 19–23 | 31.76–40.59 | **The Piper returns** | the same hook, darker: breathier flute with a ghost tenor 28 cents flat, A against B♭ rub (drone + high bowed psaltery), crowd humming the tune, wrong-note giggle answered by children's laughter, slowly opening kick; bar 23: the Piper alone, then 16th stomps, roll and inhale |
| 24–32 | 40.59–56.47 | **Final hypnotic drop** | the loudest section: hook + soprano octave + hurdy-gurdy counter-line, choir pads, crowd chant, panting breaths; the second pass loses its pause (the call repeats where the giggle was), doubled stomps and claps, a high eerie choir, then a stutter bar |
| 33–37 | 56.47–65.29 | **The disappearance** | one bar at a time the layers vanish (choir/gurdy/strings → bass → kick → claps) while the stomps keep walking; the flute ends alone with its giggle and a G♯4 pickup into the opening A4 |

**Looping:** the file is exactly 37 bars long. The ending's reverb tail is folded onto the start, and the last note resolves into the first, so the loop seam is sample-accurate.

Section levels (LUFS): intro −15.9 · awaken −14.3 · first drop −13.8 · betrayal −15.2 · return −14.4 · **final drop −12.7** · disappearance −15.7.

## Sound sources

- **Lead and supporting samples:** VCSL (Versilian Community Sample Library, CC0 public domain, github.com/sgossner/VCSL). These cover the baroque alto/soprano/tenor recorders, the bowed/spiccato/plucked psaltery, the strumstick, rope-tension snare, frame drum, darbuka, concert bass drum, timpani, tambourines, shaker, group and solo claps, gong, anvil and tubular bells. Every pitched sample was measured, because VCSL names these an octave below their sounding pitch, then retuned to within a few cents (flute vs. score: median −3 cents, worst 16 cents).
- **Physically modelled:** the hurdy-gurdy is a bowed-string waveguide with a friction junction (numba), with a wheel-driven drone, keyed melody string and a trompette string whose crank accents make the "chien" bridge buzz on the offbeats.
- **Synthesised:** kick (sine body with beater click), galloping bass (sine core, harmonics, gentle saturation), crowd stomps (several dancers, each with its own timing and position).
- **Human voices:** source-filter synthesis (glottal pulses with jitter/shimmer and aspiration, through a five-formant Klatt cascade), with many singers per part, each with its own vibrato, drift and timing. These make the choir, humming, chant, breaths and laughter. They're kept subtle and distant, as the brief asked.

## Mix and master

Per-track EQ, compression and kick sidechain; sends to a room, plate and dark hall (convolution) plus a dotted-8th ping-pong delay; an octave-up "shimmer" ghost of the flute in the hall; gentle section-level automation for the energy arc. Master: EQ → glue compressor → 4× oversampled look-ahead true-peak limiter (at most about 3 dB on 12 coincident hits) → −14 LUFS → TPDF dither to 24-bit.

QA checks (`source/qa.py`): no samples at or near full scale; mono fold-down −0.3 LU; phone-speaker proxy (350 Hz–9 kHz) −3.9 LU against full-range; a beat tracker reads exactly **136.0 BPM**, locked to the kick grid; pulse clarity is 0.84 (the Dancing Plague reference measures 0.73).

## Rebuild

```
pip install numpy scipy soundfile pyloudnorm librosa numba pedalboard
# VCSL samples (CC0), only the folders used:
git clone --filter=blob:none --no-checkout https://github.com/sgossner/VCSL vcsl && cd vcsl
git sparse-checkout init --no-cone   # then add the folders listed in source/samples.py / song.py kits()
git checkout master && cd ..
export VCSL_DIR=$PWD/vcsl
cd follow_the_piper/source
python3 render.py ..            # ~2 min on 4 cores; add --stems for 8 stems
python3 qa.py ..                # loudness, balance, spectrum, mono, loop seam, flute tuning
```

The render is deterministic (seeded), so the same code and samples give the same file.
