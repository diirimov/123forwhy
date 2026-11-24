# MEDIEVAL JOBS V2: "Hey-ya Village Dance"

This is one 65.000-second song for *3 Weirdest Jobs in History*. It is a medieval folk rave in **A minor at 150 BPM**: one bar is 1.6 s and one beat is 0.4 s.

## Deliverables
| File | What it is |
|---|---|
| `MEDIEVAL_JOBS_V2_FINAL.wav` / `.mp3` | Final master: 48 kHz / 24-bit WAV and 320 kbps MP3. About −11 LUFS, −1 dBFS peak. Light limiting only (typically 1–2 dB of gain reduction). Loops seamlessly from the WAV. |
| `stems/Drums.wav` | Kick, stomps, claps, tambourine, folk drums |
| `stems/Bass.wav` | Bouncy sub bass |
| `stems/Vocal_Chants.wav` | All village chants and shouts |
| `stems/Musical_SFX.wav` | The sound design used as music: window-tap and knock grooves, coins, church and hand bells, whispers, crow, door slam, risers and impacts |
| `stems/Instrumental.wav` | Flute, fiddle, hurdy-gurdy, lute, royal trumpets, drones |
| `stems/Mix_No_Vocals.wav` | Bonus: everything except the chants |
| `BEAT_MAP.json` | All 163 beats, 41 bars, sections, drops, transitions, impacts, 95 vocal accents, melody/fanfare cues, and SFX accents |
| `SFX_LIBRARY/` | 44 separate action sound effects for the three professions, plus `SFX_INDEX.json` (description and sync point for each file) |

All stems are synchronized, share the master gain stage and the same −5.4 dB trim, and sum to the pre-limiter mix.

## The hook: flute calls, the village answers
```
flute:    pa . pa-PA . pa PAAH    pa . pa-PA . pa PAAH        (A A E C A  |  G G D B G)
village:  HEY . ya-HEY . ya HOO   HEY . ya-HEY . ya HAA!      (same rhythm, shouted back)
chords:   Am        G           |  F          E
```
The village answers in the flute's own rhythm. That echo is what makes the hook easy to remember: after one pass the listener knows both halves. Here's how it develops:

* **Section 1:** the flute climbs, adds ornaments and gains a fiddle double, and the shouts grow ("HEY-HEY-HEY HO HEY-HA!").
* **Section 2:** the royal trumpet fanfare becomes the answer.
* **Section 3:** a ghost choir answers instead ("HO . HO . HMM . OOOH").
* **Climax:** the whole village sings the hook rhythm together with the flute.

## Timeline (every event is on the beat grid)
| Time | Bars | Section | Key moments |
|---|---|---|---|
| 0.0–3.2 | 0–1 | **Intro** | Village "HEY!" plus the flute hook at 0.0; window taps preview the groove at 1.6; "HA!" pickup at 3.0. Space for voice-over. |
| 3.2 | 2 | **Drop 1: KNOCKER-UP** | Impact. Flute call and village answer alternate every bar. Glass-tap and door-knock percussion become the hi-hat groove. |
| 16.0 | 10–11 | Fiddle reel B-part | "HO!" accents |
| 19.2 | 12 | Stop-time | "HEY! HA!" hits, knock-knock-knock, "HUH?", slide whistle up |
| 20.8 | 13 | **Drop 2: GROOM OF THE STOOL** | Palace doors slam, timpani. Coin percussion. A trumpet fanfare answers every hook. Crowd "OOOH", "OH-HO-HO", coin showers. |
| 33.6 | 21–22 | Royal procession theme | Trumpets and fiddle |
| 36.8 | 23 | "TA-DA!" | Fanfare; first church-bell toll at 37.6 |
| 38.4 | 24 | **Drop 3: SIN-EATER** | Bell and impact, crow caws. Hand bells play a 3-3-2 ostinato that works as a rhythmic hook. Whispers replace the hi-hats. The hook moves to fiddle and hurdy-gurdy (Phrygian, with Bb). Ghost-choir answers; bread crunch at 47.2. |
| 51.2 | 32–33 | Dark B-part | Low flute over the bells |
| 54.4 | 34 | Build | Bells accelerate, door creak, "HEY HEY HEY HEY" |
| 56.0 | 35 | **FINAL DROP** | Everything together: hook on flute, fiddle and hurdy-gurdy; the biggest village answers; fanfare, bells, taps and coins |
| 62.4 | 39 | Climax | The village sings the hook with the flute; tutti hits at 63.2 and 63.6 |
| 64.0–65.0 | | Tail | Final "HEY!" hit, then tap-tap-TAP leads back into 0:00 |

Reference analysis that shaped this: the reference is "10 Plagues of Egypt" (120 s), at exactly 150 BPM in D minor/Phrygian, with a four-on-the-floor kick, a heavy bass and a short repeating ornamented lead riff. Every one of its 61 picture cuts lands on the beat, at 1- or 2-bar spacing (half-bar spacing in its fast section). I copied its production approach (constant dance energy, a loop-friendly riff, every edit on the grid), not its melody. The key, mode, hook and vocals here are all new.

## How it's made
Every sound is synthesized from scratch in Python, with no samples and no text-to-speech.

* **Voices:** a physical voice model. It shapes a glottal pulse through formant filters, adds pitch jitter, shimmer and breath noise, and uses real consonant onsets (h, y, w, m). Pitch contours differ for shouts, sung notes and sighs. Each crowd is 7 to 16 singers, men and women, each with their own timing, tuning, voice size and stereo position.
* **Instruments:** bowed folk fiddle with body resonances, wooden flute, hurdy-gurdy with buzzing "chien", double-course lute, natural trumpets, tuned church and hand bells, and a glass/door percussion kit.

Rebuild everything (about 1.5 min):

```
pip install numpy scipy numba
python3 medieval_v2/src/render_v2.py && python3 medieval_v2/src/sfx_library.py
```
