# "The Evolution of a King": production report

## Deliverables (`beatit/output/`)

| File | Contents | In git |
|---|---|---|
| `MJ_EVOLUTION_OF_A_KING_FINAL.mp4` | Final edit: 1080x1920, 60 fps, H.264 + AAC, with the supplied Beat It edit | No (copyrighted audio) |
| `MJ_EVOLUTION_OF_A_KING_SILENT.mp4` | Identical picture master without audio | Yes |
| `MJ_EVOLUTION_PREVIEW_LOWRES.mp4` | Full-length 540x960 / 30 fps preview with the complete soundtrack, reviewed before the final render | No |
| `EVOLUTION_BEAT_MAP.md` / `.json` | Measured beat map: tempo, downbeats, kick, snare and guitar accents, vocal entries, chorus sections, breaks | Yes |
| `MJ_EVOLUTION_STORYBOARD.md` | 36-shot timeline with in/out times, generated from the code | Yes |
| `MODEL_SHEET_EVOLUTION.png` | Michael through 12 looks from Gary 1960s to 2009, plus the zombie | Yes |
| `../src/ev_*.py`, `timeline_ev.py` | Editable source; the shared engine is in `jackson5/src` | Yes |

Rebuild:
1. Put the edit at `beatit/audio/source.m4a` and decode it to `source.wav`.
2. Run `python3 src/analyze_audio.py`.
3. Run `TIMELINE=timeline_ev python3 src/render.py final_ev`. Use `preview_lr <name>` instead for the low-res preview.

## Achieved specification (measured with ffprobe / ffmpeg)

__SPECS__

## Music drives the cuts (measured, then used)

- **Tempo and grid:** 138.43 BPM, beat 0.433 s, bar 1.733 s, first downbeat at 0.534 s. All 36 shots start on a downbeat, a half-bar, or a named accent.
- **Strongest accents carry the biggest changes:**
  - break 8.13-9.19 s: child to adult spin, landing at 9.185 s
  - kick plus guitar at 12.585 s: the zombies turn
  - guitar at 13.886 s: Michael's head snap
  - accent at 14.745 s: the group claw pose
  - guitar at 19.563 s: the fedora goes on
  - strongest snare at 21.676 s, plus 22.535, 23.394, 24.253 and 25.124 s: camera flashes
  - break 28.79-29.16 s: Michael stops the two groups
  - vocal hit at 29.933 s: the dance starts
  - break 43.42-43.67 s: deepest point of the lean, with the camera roll
  - strongest guitar accent of the edit at 45.0 s: Dangerous pyro and stadium reveal
  - breaks 53.06 and 53.75 s: the mirror bulbs go dark
  - breaks 56.42 and 57.24 s: adult to child to adult inside the orbit
  - 57.591 s: the final pose; the picture fades after the last downbeat at 59.321 s
- **Smaller beats** drive foot strikes, flash pops on eighth notes, head nods, the light-up disco floor and bulb chases, and VU-style crowd bounce.

## Eras and signature transformations

| Era (edit time) | Transformation into it |
|---|---|
| Gary, Indiana, 1960s (0:00) | Profile close-up on the boy's shoes striking on every beat as his father's shadow crosses the floor. Then the night rehearsal: five brothers, Joe watching with arms folded, the clock late |
| Jackson 5 on TV (0:02.3) | A studio-light bloom on the vocal entry turns the room into a TV stage with cameras and an audience |
| **A** Off the Wall, 1979 (0:09.2) | The spin grows him up at each edge-on turn (1970, then 1972, then 1979) while the stage dissolves into a disco |
| **B** Thriller, 1982 (0:10.9) | His white spotlight turns red and rises into the moon over a foggy street; the red jacket turns to us |
| Record to the world (0:16.1) | The spinning *Thriller* record (plain typographic label) gives way to a ring of TVs orbiting the globe |
| **C** Motown 25, 1983 (0:17.8) | A zombie's shuffling foot match-cuts to the black loafer and glittering sock |
| Moonwalk (0:21.3) | Profile rig with real contact: the planted foot stays on its toe, the flat foot glides back past it, the heel drops and the weight swaps every beat, and the hips travel at constant speed. A full-body version follows |
| **D** Beat It, 1983 (0:26.5) | The gliding foot crosses the frame and wipes the stage into the LA street |
| **E** Bad, 1987 (0:33.4) | The red jacket spins round as black leather with buckles; the street becomes a subway |
| Bad World Tour (0:36.9) | A spin opens like an iris onto a stadium, then a long pull-back |
| **F** Smooth Criminal, 1988 (0:40.3) | The fedora is thrown at the lens, turns white as it fills the frame, and comes back into his hand in the white suit |
| Anti-gravity lean (0:42.4) | Rigid body pivoting at the ankles with the heels anchored (anchor glints); the dancers lean too, and the camera rolls at the deepest point |
| Dangerous, 1992 (0:43.8) | Match cut out of the camera roll: gold, sunglasses, standing still, then pyro on the guitar hit |
| **G** HIStory / fame (0:47.2) | A concert spotlight becomes a photographer's flash, followed by photographers, headlines, reflections in his glasses, alone backstage, and the mirror |
| **H** 2009 (0:54.1) | A rehearsal in an empty arena (never shown as a concert). One orbit with poses matched: he is the Jackson 5 boy for a breath, then the King again, and the audiences of forty years rise behind him |

## Historical care

- **Joe Jackson:** shown only as a watching, strict figure (folded arms, a shadow). No incident or dialogue is invented.
- **Thriller:** the album is captioned 1982. The video world is stylised (fog, moon, zombies) and inspired by the video, not a shot-for-shot remake.
- **This Is It:** shown as rehearsals with the stamp "2009 · REHEARSALS", an empty arena and crew at the desk. No concert is depicted.
- **Headlines:** neutral only ("KING OF POP: TOUR SELLS OUT WORLDWIDE", "FANS CAMP OUT FOR DAYS", "EVERY MOVE FOLLOWED BY CAMERAS"). There are no allegations and no real newspaper names.
- **Appearance:** his skin tone lightens gradually across the eras, reflecting his documented vitiligo. It is drawn as a change of tone only, with no other alteration.
- **Artwork:** record labels are plain text; no album artwork is reproduced.

## Sound

The supplied Beat It edit is the only audio. Tempo, pitch and arrangement are unchanged, and no effects or narration were added, so nothing masks the vocals or the solo. Two level changes:
- **Gain trim of -3.5 dB.** The master peaks at +2.2 dBTP and would clip as AAC.
- **A 1-second tail fade** from 59.0 s, together with the picture fade.

## Known limitations

- **Production method:** procedural 2D vector animation on rigged characters, not hand-drawn frames. Body turns are 2.5D (squash plus edge-on swaps), and the camera orbit is simulated with the character turn plus background parallax.
- **Moonwalk:** the full mechanics are shown in the profile shot. The front-view full-body moonwalk is a convincing approximation (toe foot raised, flat foot gliding), not a motion capture.
- **Faces:** lip movement follows vocal energy. Likeness is a stylised series design, not a portrait.
- **Crowds:** cached silhouette rows that bounce and raise arms with lights.
