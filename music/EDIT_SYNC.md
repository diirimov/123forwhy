# The Craziest Medieval Diseases — Instrumental · Edit-Sync Sheet

**128 BPM · 4/4 · 48 bars · exactly 90.000 s · 48 kHz / 24-bit stereo · −9.7 LUFS-I, −1.2 dBTP**

Grid math: 1 beat = 0.46875 s · 1 bar = **1.875 s** · 4 bars = 7.5 s · 8 bars = 15 s · 1/16 = 0.1171875 s.  
At 24 fps one bar is exactly 45 frames; at 30 fps it is 56.25 frames (use the CSV frame columns).

## Files

| File | Use |
|---|---|
| `..._48k24.wav` | Clean master (deliverable) |
| `..._MARKERS.wav` | Bit-identical audio + 65 embedded cue markers (every bar, sections, key events) — Reaper, Audition, Pro Tools import them |
| `..._CLICKGUIDE.wav` | Music −4 dB + metronome (high click = bar 1, double click = section start) for cutting |
| `..._BEATS.csv` | All 192 beats: seconds, sample, 30 fps timecode, frame @24/25/30/60, section, events |
| `..._MARKERS.json` | Same data + sections + event list, machine-readable |
| `..._BARS.srt` | Drop on the timeline as a subtitle track to see BAR n / SECTION while editing |
| `..._preview.mp3` | 320k listening copy (MP3 adds ~24 ms encoder padding — don't edit to it) |
| `src/` | Full source that renders the track (synthesis, arrangement, mix/master, export) |

## Sections

| Bars | Time | Section | What happens |
|---|---|---|---|
| 1–8 | 0.000–15.000 s | **INTRO HOOK** | Hook + groove from frame 0; fiddle, bass & hand drums join at bar 5 |
| 9–16 | 15.000–30.000 s | **DROP 1** | Full drop: kick + sub bass + fiddle/lute hook, bass answers in bars 10 & 14 |
| 17–24 | 30.000–45.000 s | **VARIATION** | Call & response: fiddle calls (17/19/21), lute+bass answer (18/20/22); percussive fill bar 24 |
| 25–32 | 45.000–60.000 s | **DROP 2** | Bigger drop: fiddle harmony, lute 16th drive, recorder counter-line, hurdy-gurdy drone+buzz, offbeat synth stabs, rolling bass |
| 33–40 | 60.000–75.000 s | **TWIST** | Mysterious Phrygian turn (Dm-Eb), hurdy-gurdy lead, 2-beat break bar 36, build 37-40 |
| 41–48 | 75.000–90.000 s | **FINAL** | Key lift to E minor, everything in; stop-time ending bar 48, final hit at 89.531 s |

## Key sync events

| Time (s) | Bar.step | 30 fps frame | Type | Description |
|---|---|---|---|---|
| 0.0000 | 1.0 | 0 | START | Hook + kick + stomp/clap groove start on frame 0 |
| 7.5000 | 5.0 | 225 | DEVELOPMENT | Fiddle doubles hook, bass & darbuka enter, light cymbal |
| 14.0625 | 8.8 | 422 | FILL | Darbuka roll + riser into drop |
| 14.7656 | 8.14 | 443 | GAP | Half-beat silence (pre-drop breath) - ideal hard cut |
| 15.0000 | 9.0 | 450 | DROP | DROP 1 impact (sub boom + crash) - camera punch |
| 18.2812 | 10.12 | 548 | ANSWER | Bass answer lick (call-and-response) |
| 22.5000 | 13.0 | 675 | DEVELOPMENT | Cymbal accent, hook variation |
| 25.7812 | 14.12 | 773 | ANSWER | Bass answer lick |
| 29.5312 | 16.12 | 886 | FILL | Kick/clap pickup into variation |
| 30.0000 | 17.0 | 900 | SECTION | Variation: fiddle CALL |
| 31.8750 | 18.0 | 956 | ANSWER | Lute + bass ANSWER |
| 33.7500 | 19.0 | 1012 | CALL | Fiddle CALL (higher) |
| 35.6250 | 20.0 | 1069 | ANSWER | Lute + bass ANSWER |
| 37.5000 | 21.0 | 1125 | CALL | Fiddle CALL + claps return, cymbal |
| 39.3750 | 22.0 | 1181 | ANSWER | Lute + bass ANSWER |
| 41.2500 | 23.0 | 1238 | ACCENT | Stomp hits on 3-3-2 rhythm (steps 0/3/6/8/11) - object transformations |
| 43.1250 | 24.0 | 1294 | FILL | Percussive fill: unison hits + clap/frame-drum roll |
| 44.7656 | 24.14 | 1343 | GAP | Half-beat silence - hard cut |
| 45.0000 | 25.0 | 1350 | DROP | DROP 2 impact - biggest camera punch so far |
| 48.2812 | 26.12 | 1448 | ANSWER | Bass answer lick |
| 52.5000 | 29.0 | 1575 | DEVELOPMENT | Cymbal accent, hook variation |
| 55.7812 | 30.12 | 1673 | ANSWER | Bass answer lick |
| 56.2500 | 31.0 | 1688 | ACCENT | Stomp hits on 3-3-2 |
| 60.0000 | 33.0 | 1800 | SECTION | TWIST: downlifter + impact, dark Phrygian harmony |
| 65.6250 | 36.0 | 1969 | BREAK | A-chord hit then 2-beat break with woodblock ticks (beats 2-3) |
| 67.0312 | 36.12 | 2011 | PICKUP | Lute pickup run back into the groove |
| 67.5000 | 37.0 | 2025 | BUILD | Build starts: claps + hats return, bass filter opens |
| 71.2500 | 39.0 | 2138 | BUILD | Clap 8th-note roll |
| 73.1250 | 40.0 | 2194 | BUILD | Clap 16th roll + rising pivot melody to B major |
| 74.5312 | 40.12 | 2236 | GAP | One-beat silence - hard cut |
| 75.0000 | 41.0 | 2250 | DROP | FINAL drop, key change up to E minor - biggest hit |
| 78.2812 | 42.12 | 2348 | ANSWER | Bass answer lick |
| 82.5000 | 45.0 | 2475 | DEVELOPMENT | Cymbal accent |
| 85.7812 | 46.12 | 2573 | ANSWER | Bass answer lick |
| 86.2500 | 47.0 | 2588 | ACCENT | Stomp hits on 3-3-2 |
| 88.1250 | 48.0 | 2644 | STOP-TIME | Ending hit 1 (C chord) |
| 88.4766 | 48.3 | 2654 | STOP-TIME | Ending hit 2 (C chord) |
| 88.8281 | 48.6 | 2665 | STOP-TIME | Ending hit 3 (B chord, tense hold) |
| 89.0625 | 48.8 | 2672 | FILL | Darbuka crescendo roll |
| 89.5312 | 48.12 | 2686 | FINAL HIT | Final E open-fifth hit, rings to the last frame |

## Recurring rhythmic hooks for animation

- **Every beat**: kick (head bobs / walk-cycle footfalls). Beats 2 & 4: clap + frame drum (body bounces).
- **Every bar downbeat**: tambourine accent hit; zills on odd bars in drops, every bar in the finale.
- **The hook rhythm 3-3-2** (16th steps 0, 3, 6 of each bar: 0.000 / 0.352 / 0.703 s into the bar) — the signature 'DA . . DA . . DA .' figure. Use it for object transformations and triple-punch zooms.
- **Tick-tock woodblocks** (intro & twist) on steps 2/10 (or 2/6/10/14), panned L/R — ideal for walking cycles and side-to-side looks.
- **Every 4 bars (7.5 s)**: cymbal/impact development. **Every 8 bars (15 s)**: section change with a gap or impact.
- **Hard-cut gaps**: 14.766 s, 44.766 s (half-beat silence) and 74.531 s (one beat) — cut on the silence, land the new shot on the downbeat that follows.

## Production notes & honest limitations

Built entirely in code in a cloud container — no DAW, no commercial sample libraries or VSTs were available. Drums, bass, lute (double-course Karplus-Strong physical model), hurdy-gurdy (drone + trompette 'dog' buzz), synth stabs/pads and FX are custom synthesis; fiddle, recorder and a nylon-string layer come from the free FluidR3 GM soundfont, with the fiddle layered under a synthesized bow-attack for tighter articulation. Mixed with sidechain, room/hall convolution reverbs, ping-pong delay, bus glue compression and a true-peak lookahead limiter.

The mix was verified objectively (tuning, timing, loudness per section, spectral balance versus the reference, true peak, mono-safe low end), but it **has not been auditioned by human ears**. The weakest link is sampled-fiddle realism: FluidR3 is a decent GM bank, not a modern solo-string library. If the fiddle reads as 'MIDI' on your monitors, the best upgrade is to re-render the `fiddle` part (MIDI is generated by `src/song.py`) through a real fiddle library or a live player and drop it into the same mix.
