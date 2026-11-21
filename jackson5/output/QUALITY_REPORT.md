# The Jackson 5 - Story V2: quality report

## 1. Review of V1 (`FINAL_JACKSON5_ANIMATION.mp4`, kept unchanged)

I reviewed every second of V1 on a 1 fps contact sheet.

| Problem reported | Found in V1? | Where | V2 fix |
|---|---|---|---|
| Emotionally weak opening | Yes | 0-4.5 s: slow crane down to the house exterior | Opens on the rehearsal itself: slip, door light, Joe's shadow, his reveal and Michael's eyes, all inside 3.1 s |
| Empty scenes | Yes | 46-60 s: about 13 s of tiny, distant figures in the arena; 60-69 s: static title hold | Every 1.2-2.5 s brings a new story beat (34 shots, see STORY_TIMELINE.md) |
| Repetitive choreography | Yes | Club (11-19 s) and arena: groove and step-touch loops | New moves: stumble, freeze, walk-on, exhaustion, determination, jump-for-joy, mirror stare. Performance chapters vary spins, points, kicks, slides, arm rolls and shimmies per bar |
| Wrong number of brothers | Partly | Club medium shots: the five overlapped so tightly that guitar bodies and arms read as 6-7 people | Wider staging and framing, and a single cast helper; the continuity sheet and every shot show exactly five brothers. Joe and the DJ have short hair and kids appear only as silhouettes, so no one reads as a "sixth brother" |
| Models changing between shots | Minor | Michael's purple hat appeared only in the TV scene; spin frames collapsed to a 12%-wide sliver | Hat removed. Spin squash limited to 42% width plus blur |
| Non-story record transition | Yes | 21-24 s and 31-34 s: spinning record and color explosion | The record now appears only where it tells the story: the DJ drops the needle on air |
| Low resolution | **No** | ffprobe: V1 was already 1080x1920, 60 fps, 4152 frames. A 512x910/30 fps copy is likely a compressed playback preview | V2 is rendered natively from vector source at 1080x1920 and 60 fps, with no upscaling |

## 2. What was preserved

- The character design language, the warm vintage palette, cel shading with rim light, film grain and vignette.
- The strongest V1 sets, reused and restaged:
  - brick amateur-night club
  - gold proscenium theater
  - studio control room (its VU meters are driven by the real audio)
  - op-art TV stage
  - orange silhouette sequence
  - arena with crowd

## 3. New in V2

- **Joe Jackson character:** about 1.66× Michael's height, with a fedora, brown jacket, white shirt and dark tie, straight 1960s trousers and a heavy brow.
  - States: stern (folded arms or hands behind his back), clap, sharp point, reading and signing, a small approving nod, and a near-smile.
  - He is shown through low angles, doorway backlighting and cast shadows on the wall and floor. He does no violence and is not drawn as a villain.
- **New face and body states:** fear eyes (enlarged eyes with shrunken irises), sweat, panting, exhaustion, determination, disbelief and joy.
- **New sets:**
  - night rehearsal room (door with hallway light, wall clock with pendulum, window, photos, radio)
  - window onto kids playing at sunset
  - feet close-up
  - kitchen-table contract with five peeking heads
  - Apollo façade and marquee
  - radio booth with ON AIR sign
  - night city with radio tower
  - record-store window
  - the mirror
- **Documentary captions:** 12 titles, each 1-2 lines of tracked ivory serif caps with a soft shadow, eased in and out. They sit at y≈300 or y≈1450, inside TikTok's safe zones and clear of faces.
- **Audio:**
  - The recording is intact, with no pitch, tempo or EQ change.
  - A -12 dB hush runs while Joe is in the doorway, and the full band returns exactly on his clap at the 4.33 s downbeat.
  - A -6 dB dip plays under the mirror shot.
  - It ends with the same 1.22 s fade as V1.

## 4. Validation (measured on the exported files)

| Check | JACKSON5_STORY_V2_FINAL.mp4 | JACKSON5_STORY_V2_SILENT.mp4 | JACKSON5_STORY_V2_PREVIEW.mp4 |
|---|---|---|---|
| Resolution / aspect | 1080x1920, 9:16 | 1080x1920 | 1080x1920 |
| Frame rate / frames | 60 fps / 4152 | 60 fps / 4152 | 60 fps / 900 |
| Duration | 69.200 s | 69.200 s | 15.000 s |
| Video codec | H.264 High, yuv420p, about 8.2 Mb/s | same | same |
| Audio | AAC-LC 48 kHz stereo, 69.200 s | none (by design) | AAC 48 kHz |
| A/V start | both 0.000 s | - | - |
| Black frames (blackdetect, d=0.1 s) | 0 | 0 | - |
| Frozen picture over 0.6 s (freezedetect) | 0 | 0 | - |
| Audio dropouts over 0.4 s below -50 dB | 0 (the intended dip stays well above -50 dB) | - | - |
| Loudness / peak | -12.0 LUFS integrated, -0.6 dBTP | - | - |

- **Sync:** every cut and dance accent is placed on tracked beats from `timing.py` (beat grid smoothed by a local linear fit). The RMS trace of the preview confirms the hush and the return of the music on Joe's clap.
- **Character consistency:** see `CONTINUITY_SHEET_V2.png`. Exactly five brothers appear in every era, with fixed heights (Jackie 1.30, Tito 1.22, Jermaine 1.17, Marlon 1.10, Michael 1.00), fixed faces, hair and signature colors, and Joe at 1.66.
- **Inspection process:**
  1. Stills of every shot were checked before rendering.
  2. The 15 s preview was checked frame by frame across the hook.
  3. The final file was checked on a 1.5 s-interval contact sheet.
- **Fixed during QA:**
  - Joe missing from the over-the-shoulder and radio shots
  - Joe's folded arms showing through his back in back view
  - feet cropped in the feet close-up
  - peeking heads too large
  - Apollo sign colliding with its caption
  - "FIVE BROTHERS." colliding with the J5 disc
  - the slip being too subtle

## 5. Known limitations

- **Procedural 2D:** this is code-driven vector animation, not hand-drawn frame-by-frame work. Turns are 2.5D cheats with no true profile views, and the spin uses a squash-and-blur frame.
- **Faces:** mouth movement follows the vocal energy, not phonemes. Expressions are built from a fixed set of parameters.
- **Backgrounds:** they are richer than V1 but still stylized. Crowds are layered silhouettes.
- **Historical framing:** the dated captions are documented: Apollo Amateur Night 1967, Motown 1968, "I Want You Back" released 1969 as their first Motown single. The specific moments (the slip, the clock, the window, the kitchen-table signing, the radio) are dramatizations, not documented incidents. The film implies the fear Michael Jackson publicly described but shows no violence and invents no dialogue.
- **Rights:** the song is copyrighted. The version with audio stays local and is not committed. The silent master is provided for licensing or for re-scoring.
