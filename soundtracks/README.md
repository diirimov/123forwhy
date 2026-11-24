# "3 Weirdest Jobs in History": soundtrack candidates

There are four original 65-second loopable tracks. All four share one arrangement grid, so the animation timing is the same whichever track you pick.

| # | File | Key / groove | Hook personality |
|---|------|--------------|------------------|
| 1 | `01_Pickpocket_Shuffle` | G minor, classic electro swing (swung 8ths, oom-pah bass, offbeat piano) | A descending **tresillo** clarinet line, "DA . . DA . . DA-da". The brass answers with a "BAP . BAP", then a pluck echoes it. |
| 2 | `02_Royal_Rat_Catcher` | F major to D minor, funky house (straight 16ths, disco-octave bass) | A pentatonic **"da-da DAH . da-da DAAH"** pluck riff with a blue note. A sassy clarinet answers with fall-offs, and the brass pushes on the "and of 4" in every bar. |
| 3 | `03_Leech_Collector_Garage` | A minor, UK garage 2-step to 4/4 (heavy 16th shuffle, gliding sub) | A staccato **"tip . tip TAP"** clarinet hook. Pitched **vocal chops** answer it, giving call and response between the clarinet and the vocal chops. |
| 4 | `04_Knocker_Upper_Charleston` | Eb major to C minor, Charleston electro swing with a tick-tock clock | A big-interval **"da-da DAAAH"** hook and a **"ring-ring-ring-ring"** alarm-clock answer. It also has Charleston brass hits and "hey!" vocal answers. |

Each track comes as a **24-bit / 44.1 kHz WAV** and a **320 kbps MP3**. Each master is at about **−10 LUFS integrated** with a −1 dBFS ceiling.

## Shared structure (132.92 BPM: 144 beats = exactly 65.0 s)

| Time | Beat | Section |
|------|------|---------|
| 0:00.00 | 0 | **Intro.** The hook plays immediately through a "gramophone" band-pass filter with vinyl crackle, which leaves room for the spoken intro. |
| 0:01.81 | 4 | Pickup: brass stab (with a fall-off), short riser and fill |
| **0:02.71** | 6 | **Drop 1.** The filter opens, the full groove comes in and the main hook plays (8 bars plus a turnaround bar) |
| **0:18.96** | 42 | **Rhythmic break** (a 2/4 stop-time bar). One brass hit, a vocal "hah!" and a solo pickup |
| **0:19.86** | 44 | **Section 2: "royal".** A harmonised trumpet fanfare, timpani, snare-corps ghosts and a heavier bass. The hook roles swap between instruments. |
| **0:36.11** | 80 | **Fake-out.** The build promises a drop, then a tape stop cuts it. A cheeky "uh-oh"/yawn follows, then a tip-toe pickup. |
| **0:37.01** | 82 | **Section 3: mystery.** A harmonic-minor / phrygian-dominant groove with unusual textures (theremin, musical saw, sitar, kalimba, music box, muted trumpet, marimba, tuba). The beat keeps going. |
| 0:51.45 | 114 | Turnaround: a scale run up, a snare roll and a riser |
| **0:53.26** | 118 | **Final drop.** Crash and impact. The hook comes back harmonised by brass, with vocal chops and the full kit |
| 1:04.10 | 142 | Stop-time pickup that leads straight back into 0:00 (**seamless loop**) |

You can use the bar downbeats as rhythmic accents every **1.8 s**. Beats fall every **0.451 s**, and brass stabs or vocal hits land between them.

* `cues/*_cues.json` lists every section change and every brass stab with its exact time. Each file also has the full bar-downbeat list. Feed it to After Effects or a script to keyframe the animation.
* Every beat falls at `n × 0.45139 s`.

### Loop note
The loop seam is mastered so it is continuous: the reverb tails from the ending are folded onto the start, and the master is processed circularly. **Use the WAV for looping.** MP3 encoding adds about 45 ms of decoder padding, so an MP3 will not loop sample-accurately.

## How it was made
Every sound is synthesised from scratch in Python (numpy/scipy). No samples, soundfonts or AI-generated audio were used.

* **Instruments:**
  * Clarinet: an additive odd-harmonic reed model with breath noise, scoops, grace notes, glides and jazz fall-offs.
  * Brass section: brightness follows loudness, with a lip rise, fall-offs, a harmon mute and diatonic harmoniser voices.
  * Strings: Karplus-Strong models for the upright bass, funk pluck, harpsichord, pizzicato and buzzing sitar.
  * Vintage detuned upright piano.
  * Formant-synthesised nonverbal vocal chops.
  * Mallets, a theremin and a musical saw.
* **Drums:** fully synthesised (kick, clap, hats, shaker, tambourine, rims, bongos, castanets, woodblock clock, timpani, crash).
* **Mix:** kick-keyed sidechain on bass, music and reverbs; convolution plate and room reverbs; a tempo-synced ping-pong delay; Haas widening; glue compression; a look-ahead limiter; LUFS targeting.

To regenerate (about 40 s per track):

```bash
pip install numpy scipy
cd soundtracks/src && python3 render.py        # or: python3 render.py 2
```

Melodies are written in a compact notation in each `songN_*.py` file, so they are easy to edit. For example, `"!G5:3 F5:3 D5:2 (E5)F5:1 ..."` means: `!` is an accent, `:3` is a length in 16th notes, `(E5)` is a grace note, `\` is a fall-off and `'` is staccato.
