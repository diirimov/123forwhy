# WEIRD MEDIEVAL JOBS (final soundtrack)

**Files:** `WEIRD_MEDIEVAL_JOBS_FINAL.wav` (24-bit / 44.1 kHz) and `WEIRD_MEDIEVAL_JOBS_FINAL.mp3` (320 kbps) are the same master.

* Length: 65.000 s
* Tempo: 132.92 BPM (144 beats)
* Loudness: about −10 LUFS integrated, −1 dBFS peak
* Loop: seamless when played from the WAV (MP3 adds about 45 ms of encoder padding)

## Musical identity
Medieval folk dance × medieval rave × modern bass.

* **Key:** D Dorian. Section 2 moves to F major ("royal") and section 3 to D Phrygian ("dark"). The finale returns to D Dorian.
* **Signature hook (wooden flute):** `A D F̲ · E D A̲ · G F E D C̲ · A`, sung as "da-da DUM, da-da DUM, da-da-da-da DUM DUM".
* **Answer (hurdy-gurdy):** `E̲ - - G E C · D̲ - - E C`, sung as "DUM . . da DUM DUM, DUM . . da DUMMM".
* **Development:** call-and-response rotates between the flute, hurdy-gurdy and bagpipes. The hook gets folk ornaments (cuts), a harmonised form, a royal F-major form, a dark Phrygian form, a whirlwind-tail form and a 3-3-2 stop-time form.

## Timeline (all transitions on the beat)
| Time | What you hear | Animation idea |
|---|---|---|
| 0:00.00 | Flute hook from frame 0, crowd stomps and claps, hurdy-gurdy drone | title / first character |
| 0:01.81 | Hurdy-gurdy answers; davul hits at 1.81, 2.14, 2.48; "HEY!" | three pose hits |
| **0:02.71** | **DROP 1:** kick, bouncy bass, stomps; zill and boom impact | camera punch |
| 0:04.5 / 6.3 / 8.1 / 9.9 … | Each bar alternates flute CALL and hurdy-gurdy ANSWER | character A / character B |
| 0:09.93 | Darbuka and doum enter | |
| 0:12.64 | Lute 16th notes, 16th tambourine, ornamented hook | |
| 0:17.15 | Turnaround fanfare plus riser | |
| **0:18.96** | **BREAK:** bagpipe "groan" (the bag inflating), squawk, "HEY!", tambourine shake | comic freeze / reaction |
| **0:19.86** | **SECTION 2 (royal):** boom and zill. Bagpipes take the hook over drones, with lute strums and processional davul | crown / castle reveal |
| 0:21.7 / 25.3 / 28.9 | Flute, hurdy-gurdy and flute+hurdy-gurdy answer the bagpipes | |
| 0:32.5 | Tutti royal cadence plus "HEY" | |
| 0:34.3 | Turnaround run, frame-drum roll, riser | |
| **0:36.11** | **FAKE-OUT:** the whole band winds down, a ghostly chant, two ticks | mystery beat |
| **0:37.01** | **IMPACT, then SECTION 3 (dark):** hypnotic hurdy-gurdy ostinato with buzzing "chien", distant chants, deep bass, tribal drums | dark / weird reveal |
| 0:40.6 / 44.2 | Dark version of the hook (low flute, then high flute) | |
| 0:51.45 | Build: "HEY HEY HEY HEY", flute run up, riser | |
| **0:53.26** | **FINAL DROP:** flute and bagpipes in unison, hurdy-gurdy harmony, everything in | biggest moment |
| 1:02.29 / 62.63 / 62.97 | **3-3-2 stop-time tutti hits** | three big poses |
| 1:04.10 | A-major hit plus "HEY", flute pickup loops straight into 0:00 | |

* Every beat falls at `n × 0.45139 s`, and every bar is 1.806 s, so something changes every 1.8 to 3.6 s.
* `WEIRD_MEDIEVAL_JOBS_FINAL_CUES.json` lists every cue with exact times: section changes, each call/answer switch, every shout, the davul and tutti hits, and all bar downbeats.

## How it was made
Every sound is synthesized from scratch in Python. No samples, soundfonts or General MIDI sounds are used.

* **Wooden flute:** breath noise tuned to each note, a chiff on the attack, folk "cuts" and delayed vibrato.
* **Bagpipe chanter:** a continuous reed tone with automatic grace notes on accented notes, plus drones and a bag-inflation groan.
* **Hurdy-gurdy:** a wheel-bowed melody string with tangent clicks, bourdon and mouche drones, and the rhythmic trompette "chien" buzz.
* **Lute:** a double-course plucked-string model.
* **Wordless group chant:** formant-synthesized voices in a detuned crowd with octave doubling.
* **Percussion:** davul, frame drums, darbuka doum and tek, crowd stomps and claps, tambourine, zills.
* **Modern layer:** punchy kick, sub plus growl bass, sidechain, reverb and delay, glue compression and a limiter.

The musical direction (D-minor modal folk, groove from frame 0, offbeat bouncing bass, call-and-response, a dark modal twist, stop-time hits) follows the earlier medieval-diseases dance track on branch `claude/funny-euler-j4pqk3`. The melody, harmony and instruments are all new.

To rebuild (about 50 s):

```bash
pip install numpy scipy
python3 medieval/src/render_medieval.py
```
