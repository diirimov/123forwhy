# 3 Weirdest Jobs in History: animated music short

## Deliverables

| File | What it is |
|---|---|
| `WEIRDEST_JOBS_FINAL_1080P60.mp4` | Final video (details below) |
| `WEIRDEST_JOBS_THUMBNAIL.png` | 1080×1920 thumbnail: the trio on stage with the title |
| `WEIRDEST_JOBS_SUBTITLES.srt` | English subtitles and title cards, with the narration line noted |
| `WEIRDEST_JOBS_SYNC_MAP.json` | Everything time-aligned in one file. Frame formula: frame = seconds × 60 |
| `STORYBOARD.md` | The shot list as rendered |
| `MODEL_SHEET.jpg` | The cast |
| `audio/FINAL_MIX.wav` | Final mix (48 kHz / 24-bit) |
| `audio/NARRATION_OPENING.wav` | The one narration line on its own |
| `src/`, `index.html`, `render.js`, `audio_mix.py` | The complete, editable animation project |

The final video is 1080×1920 (9:16) at 60 fps: 3,900 frames, exactly 65.000 s. Video is H.264 High, yuv420p, about 8.4 Mbps. Audio is AAC LC at 320 kbps, 48 kHz. Audio and video both start at 0.

The sync map contains:
- 45 shots, with their frame ranges
- every subtitle
- the narration
- 21 sound-effect cues, each with the visual action it belongs to
- the soundtrack's sections, drops, impacts, 95 vocal accents, and every bar and beat

## Audio
- **Soundtrack:** `medieval_v2/MEDIEVAL_JOBS_V2_FINAL.wav`, used unchanged. Melody, tempo, arrangement, pitch and chants are all untouched.
- **Narration:** "Three of the weirdest jobs in history!" (0.20–1.86 s), generated with Kokoro TTS, voice `am_fenrir`. The music dips by 4.5 dB under it only.
- **Sound effects:** 21 cues from `medieval_v2/SFX_LIBRARY`, each placed on its visual action:
  - snore, wake-up gasp, window, neighbour reactions
  - coins landing, footsteps, crowd gasp
  - door creak, bread crunch, ghost breath, supernatural sting on the 48.0 s downbeat, crow
  
  They sit 10–26 dB below the music. Sounds the song already contains are not doubled: window taps, knocks, palace doors, fanfares, bells, crows and the "OOOH"s.
- **Level:** about −11 LUFS, peaks at −1 dBFS.

## Structure (150 BPM: a 1.6 s bar)

| Time | Section | Key beats |
|---|---|---|
| 0.0–3.2 | **Opening** | The trio jumps onto a theatre stage on the first "HEY!". The title animates letter by letter on the flute notes. On the window taps we cut to close-ups of the pole on glass, the royal close stool and the bread by candlelight. Everyone points at the camera on "HA!". |
| 3.2–20.8 | **1. The Human Alarm Clock** (industrial Britain, before dawn) | (see below) |
| 20.8–38.4 | **2. Groom of the Stool** (Tudor court) | (see below) |
| 38.4–56.0 | **3. The Sin-Eater** (Welsh-English border folklore, dusk) | (see below) |
| 56.0–65.0 | **Finale** | (see below) |

**1. The Human Alarm Clock (3.2–20.8)**
- Tracking walk through the terraced street, stepping on the beat.
- Snoring worker with a dream of sheep jumping on each beat.
- The pole taps the glass exactly on the song's tap rhythm; the worker jolts awake.
- Five windows fly open, one on each village shout, with five different reactions.
- Coins land in his palm, one per shout; he spins the pole like a dance partner; workers march to the mill.
- Stop-time hits, then KNOCK-KNOCK-KNOCK on the camera lens. The pole swings at the camera and match-cuts to the king's sceptre.

**2. Groom of the Stool (20.8–38.4)**
- The doors burst open on the slam and the king strides in.
- Guards snap their halberds up, one per fanfare note; the court bows in a wave on "HO HO HEY HA".
- The close stool is presented as a solemn ceremony, then revealed with a comic tilt down, "OOOH" maids and a lid fanfare.
- Ballet-like duties; a spin transformation into prestige clothing; a whispered secret, with the king laughing on "OH-HO-HO".
- Guards cross halberds against the nobles ("HALT!") but let the groom strut through, and he winks at the camera on "HEY".
- On "TA-DA" a coin flips at the camera and darkens into the funeral coin.

**3. The Sin-Eater (38.4–56.0)**
- Village with a swinging church bell, crows taking off and a slow funeral procession.
- He walks through the fog while villagers shrink back.
- His eyes open on the choir "HO"s; the family offers bread.
- **The bite lands exactly on the song's crunch at 44.6 s.**
- Symbolic smoke and a giant wall shadow, captioned as a folk *belief*.
- Payment, then he leaves alone: a silhouette against the moon.
- A door creaks; on the four "HEY!"s at 55.2–55.8 we whip through a hero montage.

**Finale (56.0–65.0)**
- The curtains fly open and every character dances: knocker-up, groom, sin-eater, king, guards, townsfolk and villagers. Coins and confetti fall.
- The village shouts burst onto the screen as text.
- A chorus line, then "WHICH JOB WOULD YOU CHOOSE?" from 62.3 s, with 1-2-3 medallions popping on the tutti hits.
- The tail (knock-knock) eases back to the opening composition, so the video loops seamlessly.

## History check (verified before rendering)
- **Knocker-ups:** a British industrial-era trade. Workers paid a small weekly sum, and long poles were used for upper windows. ([Wikipedia](https://en.wikipedia.org/wiki/Knocker-up), [BBC](https://bbc.in/2PJuxmo))
- **Groom of the Stool:** a Tudor post with prized private access to the king. Its political power is debated, so the "whisper" scene is staged as private access, not a council meeting. ([Wikipedia](https://en.wikipedia.org/wiki/Groom_of_the_Stool), [Tudor Society](https://tudorsociety.com/groom-stool-sarah-bryson/))
- **Sin-eating:** known mainly from John Aubrey's 17th-century note: bread (and beer) passed over the corpse, plus a small coin, around Herefordshire and the Welsh border. The evidence is thin, so every subtitle says "folklore", "believed" or "legend". ([Wikipedia](https://en.wikipedia.org/wiki/Sin-eater))
- No dates, salaries or other unsupported figures appear on screen.

## How it's built
Everything is procedural 2D vector art in an HTML5 Canvas, rendered frame by frame in headless Chromium. Each frame is computed from `t = frame / 60`, so motion stays locked to the beat map.

- `src/rig.js`: an articulated, auto-grounded character rig. Feet never float. It has tapered limbs, cel shading, a 3/4 head turn, 7 eye states, 11 mouth shapes, brows, clothing swing and held props.
- `src/cast.js`: 13 designed characters plus a generator for townsfolk crowds.
- `src/env.js`: 11 pre-painted sets: dawn mill town (parallax layers), bedroom, terrace facade, mill gate, Tudor great hall, privy chamber, dusk village, wake room, moon hill, and the theatre stage with proscenium.
- `src/fx.js`: subtitle and title typography, props (pole, sceptre, close stool, coins, bread, candles), smoke, sparkles, light shafts, fog and particles.
- `src/shots*.js`: the 45 shots. `src/film.js` assembles them with transitions (whip, punch, flash, match cut), then adds the paper texture, vignette and film grain.

To re-render:

```
node render.js video out/part.mp4 <frame0> <frame1>      # 4 chunks in parallel ≈ 4 min
node render.js stills review/x 12.0 44.6                 # spot-check any time
python3 audio_mix.py                                      # rebuild the mix
```
