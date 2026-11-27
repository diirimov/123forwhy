# THE PIED PIPER OF HAMELIN: new original soundtrack

| File | What |
|---|---|
| `PIED_PIPER_NEW_SOUNDTRACK.wav` | The track: 48 kHz / 24-bit stereo, 65.294 s (37 bars at 136 BPM), −14.01 LUFS integrated, −1.92 dBTP. 100 % instrumental, loops seamlessly. |
| `PIED_PIPER_NEW_SOUNDTRACK_SYNC.json` | Beat sync data: every beat (seconds, 60 fps frame, bar/beat, energy), downbeats, sections, chords, the five full-band silences, both drops, accents, instrument events (kick, clap, riq, bass, pluck, gurdy, wood, toms, stabs, crashes, booms) and all 209 flute notes. |
| `source/` | `song.py` (score and arrangement), `render.py` (mix, master, exports), `qa.py`, `dp_engine.py` (Dancing Plague synth models, copied unchanged). The project also uses the sample and waveguide engine in `../follow_the_piper/source/` (read only, not modified). |

None of the earlier soundtracks (`follow_the_piper/`) or animation files (`pied_piper_film/`) were changed.

## The music

**The hook.** "The taunt" is new and original. It's half a bar of skipping long-short rhythm (2+1+2+1+2 sixteenths) on the alto recorder: **A5 · F#5 B5 · A5 F#5**. It's the sol-mi-la playground taunt, and it lands on the first downbeat at 0.000 s with kick, bass and riq. There is no intro. B5 and A5 fall on the off-16ths, which is what makes it skip.

**The flute never plays a whole bar of the hook.** The other half of every bar belongs to someone else:

- plucked psaltery and lute (repeated-note "ta-ta" answers);
- then the hurdy-gurdy (in the stranger's groove it calls and the flute answers);
- then a chromatic hurdy-gurdy and fiddle 16th "rat scurry";
- finally imitations that tighten from whole bars to half bars in the climax.

**A playful tune over disturbing ground.** The flute keeps playing the same innocent taunt while the harmony moves under it:

| Harmony | What it does to the taunt | Feel |
|---|---|---|
| B minor | — | Mysterious |
| C (Phrygian ♭II) | The F# becomes a tritone rub | Creepy |
| D major | Nothing clashes | Genuinely happy (celebration) |
| D minor / B♭ | The taunt turns minor (F, B♭) | Betrayal |
| G minor | Hangs on C# | The Piper's smile fades |

The hook cadence G → F# ends on a G5 pickup, a ♭9 over F#, which pulls straight back into the hook.

## Form (same bar grid as the film; every cut still lands on a bar line)

| Bars | Time (s) | Section | Music |
|---|---|---|---|
| 1–2 | 0.00 | hook | Taunt + plucked answers, kick, bouncy bass, riq, claves, drone |
| 3–6 | 3.53 | rats | Full groove (clap/tabor backbeat, shaker, frame-drum bounce, lute chops). The hook climbs a 4th, the fiddle doubles it below, and the cadence turns on G–F# |
| 7 | 10.59 | gate | The taunt in C, an F#5 tritone trill, ratchet, toms, roll, riser; silence at 12.13 |
| 8–10 | 12.35 | stranger | The hurdy-gurdy calls and the flute answers; darbuka maqsum, syncopated bass |
| 11 | 17.65 | spell | Rising harmonic-minor run, C#6 trill, tremolo strings, roll, riser; silence at 19.19 |
| **12–16** | **19.41** | **DROP 1: the rat procession** | Taunt + rat scurry, gliding growl bass pumping against the kick, woodblocks; the tenor recorder joins an octave below at the river |
| 17 | 28.24 | still water | One hit on C + gong, then near-silence and a falling F5 |
| 18–19 | 30.00 | celebration | The same taunt over D and G, happy; claps on every beat, tambourine 16ths |
| 20–22 | 33.53 | betrayal | Minor taunt, half-time drums, low fiddle answers, tremolo; C# over G minor |
| 23 | 38.82 | into the night | The flute alone in 16ths over a heartbeat; silence at 40.37 |
| **24–27** | **40.59** | **DROP 2: the children** | Soprano recorder doubles the taunt an octave up, biggest low end; tom fill and silence at 47.43 |
| 28–31 | 47.65 | climax | Gurdy imitation, half-bar trades, long fiddle line on top, Em lift, the chromatic tag A#–B–C–C#–D |
| 32 | 54.71 | mountain | The taunt chopped into unison stabs; the mountain seals in silence at 56.03 |
| 33–37 | 56.47 | disappearance | Layers vanish one by one: the hook with no band, the answer with no flute, the taunt with holes in it, the Piper low in the fog (tenor), the last giggle and a pickup back to bar 1 |

**Notes for resyncing the film.** The silences at 12.13, 40.37 and 56.03 s are where the film already holds its breath (the freeze at 47.43 s is 0.11 s earlier than the film's 47.54). The final drop is at 40.59 s, exactly where the film's final drop is. The first drop has moved from bar 8 (the market) to bar 12 (the rat procession); the market and the council now sit on the stranger's groove.

## Production: what came from the Dancing Plague source

From `dancing_plague_1518/source` (engine.py, song.py, render.py):

- **Drums and percussion:**
  - club kick (47 Hz bloom), four on the floor;
  - riq on the offbeat 8ths with ghost notes in the drops;
  - shaker 16ths (DP accent shape);
  - frame-drum bounce on 3/6/11/14;
  - clap + tabor backbeat;
  - woodblocks on 3/11 (and 7) in the drops.
- **Bass:** deep plucked bass with octave pops; legato gliding growl bass in the drops.
- **Strings and fills:**
  - lute power-chord chops on the offbeats;
  - drone with buzz on the offbeats;
  - tabor rolls (power-1.6 crescendo);
  - noise risers + reverse cymbal;
  - stop hits;
  - 52 % swing on the 16ths.
- **Mix:**
  - kick sidechain on bass/chops/drone;
  - room + plate with 15 ms pre-delay;
  - DP master EQ (sub-heavy, lean low-mids, warm top);
  - side width above 160 Hz;
  - 2:1 glue;
  - gentle tanh saturation;
  - 4× oversampled true-peak limiter, mastered here to −14 LUFS rather than DP's −10.

New sound sources:

- **Sampled (VCSL, CC0):** baroque alto/soprano/tenor recorders, psaltery, strumstick, and acoustic drums and percussion (bass drum, claps, rope snare, tambourine, shaker, frame drum, darbuka, mallet toms, woodblock, claves, ratchet, gong) layered with the DP synth hits.
- **Physical models:** a bowed-string waveguide hurdy-gurdy (keyed melody, drones, buzzing chien) and fiddle.

There are no human voices, choir, breathing, laughter or robotic sounds; the vocal models in the shared engine are not called.

**Hooks tried before this one:**

- A descending repeated-note giggle: dropped, too close to the Dancing Plague pipe hook.
- A leaping-6ths line on the 3+3+2 tresillo: dropped, too close to FOLLOW THE PIPER.

The taunt won because its rhythm is new to the studio's tracks, it's singable after one hearing, and its F# turns into a tritone over the ♭II without a note changing.

## QA (`source/qa.py`)

- **Loudness:** −14.01 LUFS integrated, −1.92 dBTP, no clipped samples.
- **Groove:** tempo locks at 136.0 BPM; pulse clarity 0.78 (Dancing Plague 0.73); the strongest onsets fall on the offbeat 8ths and the kick carries beat 1.
- **Drops:** each drop is 2.7–5.5 LU louder than the bar before it.
- **Balance:** the answering instruments sit within about 1–3 dB of the flute.
- **Tonal balance:** within 1 dB of the Dancing Plague reference in the 40 Hz–10 kHz octave bands, except 315 Hz (−4 dB) and 630 Hz (+3 dB). There is less energy below 40 Hz than in DP's master.
- **Mono and phone:** mono fold-down −0.26 LU; phone-speaker proxy −6.4 LU.
- **Flute pitch:** within 30 cents of the score, apart from deliberate trills and one octave-doubled phrase where the detector locks onto the tenor.

## Rebuild

```
cd source
python3 render.py .. [--stems] [--fresh]    # about 2 minutes; needs the VCSL samples (see follow_the_piper/source/samples.py)
python3 qa.py .. [reference.wav]            # QA (stem checks need --stems)
```
