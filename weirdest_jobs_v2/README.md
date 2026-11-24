# 3 Weirdest Jobs in History: V2 (character & animation overhaul)

V1 is preserved unchanged in `../weirdest_jobs_film/`.

## Deliverables

| File | |
|---|---|
| `WEIRDEST_JOBS_V2_FINAL_1080P60.mp4` | Native 1080×1920, 60 fps |
| `CHARACTER_MODEL_SHEETS.png` | All 9 main sheets in one image. Individual sheets are in `model_sheets/`, plus `lineup.jpg` for the whole cast |
| `REFERENCE_COMPARISON.png` | Reference frames vs V1 vs V2 |
| `WEIRDEST_JOBS_V2_THUMBNAIL.png` | 1080×1920 thumbnail |
| `WEIRDEST_JOBS_V2_SUBTITLES.srt` | Subtitles |
| `WEIRDEST_JOBS_V2_SYNC_MAP.json` | 44 shots with frame ranges, subtitles, narration, SFX cues, and the full music beat map |
| `STORYBOARD_V2.md` | The shot list as rendered |
| `src/`, `index.html`, `render.js`, `audio_mix.py` | Editable project |

**Video specs (verified with ffprobe):**
- H.264 High, yuv420p, 1080×1920, 60/1 fps.
- 3,900 decoded frames, exactly 65.000 s. Every frame is rendered individually: nothing is upscaled and no frames are duplicated.
- AAC LC 320 kbps, 48 kHz. Audio and video both start at 0.000.

**About the "512×910, 30 fps" file.** The V1 master in the repository is genuinely 1080×1920 at 60 fps. The low-resolution copy was a preview made when the file was delivered to the app. Use the file from the repository.

**Audio is unchanged.** It is the approved `medieval_v2/MEDIEVAL_JOBS_V2_FINAL.wav`, with the same one-line narration and the same 21 library SFX cues on their actions. The cue times still match the rebuilt action.

## What changed from V1

The reference uses tall, cut-out-style stylised humans:
- profile heads with strong noses, large almond eyes and jaws that drop open to show teeth and tongue;
- frontal or three-quarter torsos;
- shaped limb segments with cuffs over the joints;
- five-finger hands and patterned costumes;
- framing with ornamental top and bottom bands and slab captions on dark rounded plates.

V1's round-headed, tube-limbed rig was replaced completely.

### New character system (`src/rig2.js`, `src/cast2.js`)
- **Proportions:** about 6.5–7 heads tall, with per-character builds: lanky, stocky, slim, tall-gaunt, the king's padded Tudor bulk, women, and a child.
- **Four designed head views:** profile, three-quarter, front and back. The jaw is articulated in profile and three-quarter, so the mouth really opens to show teeth and tongue. Each character has their own nose design (long, roman, hook, button, bulb), almond eyes with lids and lashes, brows that move, ears, sideburn and hair systems, beards, moustaches and stubble.
- **Expressions:** 18 sets, including happy, grin, laugh, surprise, shout, anger, fear, confused, smug, sad, chew, sleep, relief and ooh.
- **Limbs:** upper arm, forearm, thigh and calf are drawn as shaped segments, with cuffs or elbow caps hiding the pivots. Shoes are drawn per view.
- **Hands:** five fingers in eight poses (open, spread, fist, point, grip, relaxed, palm, wave).
- **Costumes:** silhouettes are built from levels that adapt to the view, with period detail:
  - Ned: tweed frock coat, waistcoat, patch, flapping red neckerchief.
  - The king: fur-lined gown, puffed and slashed sleeves, gold chain.
  - Thomas: slashed doublet, pleated peplum, ruffled collar, feathered bonnet.
  - Yeomen guards with Tudor roses.
  - A lady in a gable hood.
  - The widow in a coif.
  - The sin-eater: a human face under a cowl, rope belt, ragged cloak.
- **Turns:** a character turning switches between the drawn views (profile → three-quarter → front → back) instead of stretching one drawing. This is used in Ned's spin, Thomas's transformation and the dances.
- **Walk cycle:** keyed contact, down, passing and up poses, with weight bob and counter-swinging arms.
- **Dances:** choreography is written as beat-keyed pose phrases, with eased anticipation and overshoot. Ned, Thomas, the sin-eater, the king and the chorus each have their own steps.

### Presentation (`src/style2.js`)
- Animated ornamental bands per story: cogs and clocks for the town, Tudor roses and crowns for the palace, knots and candles for the village.
- Navy caption pills with a gold rim and Alfa Slab One lettering (OFL licence), emphasis words in yellow.
- A 1-2-3 chapter medallion.
- Comic pop-words on the vocal accents: HEY, HA, KNOCK, HALT, OOOH, CRUNCH, TA-DA, HO HO HO.

### Rebuilt sequences (all 44 shots)
- **The knocker-up's strut:** in profile, with the pole on his shoulder, then a cap tip, a four-view spin and a shout and point on the vocal answers.
- **Alf's snore and wake-up:** a big profile head with a jaw that snores open; he bolts upright on "WHAT?!", shakes his fist, then waves "I'M UP!".
- **The palace:** a guard snaps to attention on each fanfare note, the court bows in a wave, Thomas presents the stool as a ceremony, and the reveal shows maids saying "OOOH". Then a back-view door flourish, the four-view transformation, a whisper and the king's "HO HO HO", the "HALT!" block, a strut and a wink to camera.
- **The sin-eater:** a large profile walk through the fog, a three-quarter close-up of his eyes, the offering, then both hands bringing the bread to his mouth: the jaw opens on the anticipation and closes on the crunch at 44.6 s, followed by chewing. His giant wall shadow is captioned as a belief.
- **The finale:**
  - a chorus phrase in four counts;
  - the trio's individual phrases;
  - the king's arms-up/arms-down bounce;
  - a five-person kick line on alternating legs;
  - the 1-2-3 medallion hits on the tutti chords;
  - a tail that eases back to the opening composition for the loop.

## Re-render
```
node render.js video out/part.mp4 <f0> <f1>      # 4 parallel chunks ≈ 6 min
node render.js eval model_sheets/x.jpg "sheetFor('knocker','NED')"
python3 audio_mix.py
```
