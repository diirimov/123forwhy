# INSIDE THE BRAZEN BULL — animation

60 s · 1080×1920 · 60 fps · H.264 · AAC. Hand-built 2D illustration rendered from code: every frame is a pure function of
time on an HTML canvas (`index.html` + `src/`), rendered headless in parallel and encoded with ffmpeg.

## Audio (locked)
* Music: `audio/BRAZEN_BULL_FINAL_V3.wav` — the approved soundtrack, **never modified**.
* Narration: `audio/VO_brazen_bull_simulation.mp3` (supplied ElevenLabs line, "The Brazen Bull Simulation.").
* `audio/VO_aligned_60s.wav` — the narration alone on its own 60 s track, starting at 0.45 s (title words are timed to it).
* `audio/MIX_soundtrack_plus_VO.wav` — music + narration (−3 dB duck under the line only, inside the mix).
* Swap the narration without re-rendering: edit `VO_START` / the mp3 → `python3 tools/mix_audio.py` → `tools/mux.sh picture.mp4 audio/MIX_soundtrack_plus_VO.wav out.mp4`.

## Source
* `src/lib.js` math, easing, smooth paths, light helpers, grain/bloom · `src/character.js` protagonist (front/¾/profile heads, bust, hands, two-pass chiaroscuro renderer)
* `src/world.js` bronze bull, courtyard, interior · `src/anatomy.js` skin, vessel, heart, brain, nervous system, liver, kidneys, body figure
* `src/shots.js` the 20 shots · `src/timeline.js` shot table, transitions, title, captions, impact frames, post · `src/beatdata.js` kicks from the V3 beat map
* `design/` model sheet and key art. Preview a frame: `node tools/shot.mjs out.png frame:12.5`. Render: `node tools/render.mjs <dir> 3 60 0 3600`.

## Sync map (seconds, from BRAZEN_BULL_BEATMAP_V3.json)
| Shot | Time | Locked to |
|---|---|---|
| 01 eyes in the light streak → pull-back match-cut | 0.00 | bronze impact; title words on VO ("The" 0.55, "Brazen" 0.78, "Bull" 1.38, "Simulation" 1.84) |
| 02 low-angle bull · AN ANCIENT GREEK LEGEND | 3.53 | groove door slam (impact cut) |
| 03 EXTREME HEAT | 7.06 | wail (light transition) |
| 04 skin / sweat · YOUR BODY TRIES TO COOL DOWN | 10.59 | x-ray scan (scan wipe) |
| 05 vasodilation · BLOOD VESSELS WIDEN | 14.12 | fire ignition (iris dive into capillary) |
| 06 heart · YOUR HEART WORKS HARDER | 17.21 | door-slam break |
| 07 water & electrolytes | 20.96 | shriek break (whip) |
| 08 weakness | 22.94 | riser |
| 09 silhouette → anatomical figure · HEAT STRESS INCREASES | 24.71 | roar rise; burst at 26.03; black silence 26.28 |
| 10 DROP: nervous system ignites | 26.47 | drop |
| 11 dizziness POV (freezes on 33.09 slam) | 30.00 | wail |
| 12 thermoregulation / hypothalamus | 33.53 | scan |
| 13 HEATSTROKE | 37.06 | clank |
| 14 brain (pulses on recorded heartbeats) | 40.59 | breakdown door slam |
| 15 heart, liver, kidneys | 43.68 | wail; heartbeats; reverse roar → silence 47.43 |
| 16 FINAL DROP: character × anatomy fusion · MEDICAL EMERGENCY | 47.65 | roar identity hit |
| 17 consciousness fades | 50.96 | wail; shriek stutter 51.84 |
| 18 outline · EXTREME HEAT CAN BE FATAL | 54.71 | scan / Hijaz turn |
| 19 bull exterior, roar flare · THE BRAZEN BULL | 56.47 | roar climax 57.79; silence 58.10 |
| 20 bull's eye → light streak (loops to frame 1) | 58.24 | final impact |

## V4 — storytelling rebuild (`index_v4.html` → `BRAZEN_BULL_ANIMATION_V4_1080P60.mp4`)
Three acts on the same locked soundtrack + "The Brazen Bull Simulation." narration:
* **Act I — the legend (0–17.2 s):** bull face from darkness + title → engraved map Athens→Akragas → Akragas at sunset → Perillus at the anvil (strikes on the kicks) → statue reveal → Phalaris enthroned with guards → presentation shot/reverse shot → the bull's "roar" as symbolic sound rings → court reactions.
* **Act II — the simulation (17.2–47.4 s):** V3 medical shots re-timed (bar-aligned) under the new captions; HEATSTROKE title on the clank.
* **Act III — the inventor's fate (47.6–60 s):** golden courtyard → Phalaris turns and points → guards step in → Perillus's fear → bull silhouette → symbolic silhouette (no depiction of execution) → final title "THE BRAZEN BULL / HISTORY AND LEGEND" on the climax roar → back to the bull face for the loop.
* New code: `src/chars4.js` (Perillus, Phalaris, guards, citizens, props), `src/world4.js` (map, Akragas, workshop, throne room, golden courtyard), `src/shots4.js`, `src/timeline4.js`. Model sheets: `design/V4_cast_sheet.png`, `design/V4_world_sheet.png`.
* The inventor's fate is presented as legend (Diodorus Siculus, Book IX); medical captions are general statements with no temperatures, times or mechanisms.
