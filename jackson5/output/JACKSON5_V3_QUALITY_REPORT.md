# The Jackson 5 - Story V3 "The Final Decision": quality report

## 1. Process

1. **Inspected V2:** reviewed its source and its 1 fps contact sheet, then built a 69-second plan that marked each V2 shot as keep or replace.
2. **Built the new characters first:**
   - Michael at four ages
   - the six-brother 1984 lineup
   - Joe in 1984
3. **Built the ending first:** rendered `JACKSON5_V3_ENDING_PREVIEW.mp4` (0:48-1:09). I inspected its contact sheet, its full-size frames and the audio RMS trace. I fixed:
   - the mic covering Michael's mouth during the announcement
   - a missing ellipsis glyph
   - the brothers bunching up in the corridor
4. **Integrated the new opening and middle:**
   - kept 13 strong V2 shots through a time-remap helper, so lip movement, VU meters and music-reactive lights stay synced to the real song
   - built 24 new shots
5. **Inspected every shot as a still before the final render.** I fixed:
   - an empty moonwalk shot (its move started at t=0, so Michael slid off-screen)
   - the cropped glove close-up
   - the shadow projection in the feet shot
   - the brothers overlapping teen Michael
6. **Rendered the full film and validated it** (below).

## 2. Issues raised about V2, and fixes

| Issue | V3 fix |
|---|---|
| No dramatic payoff | New spine: a frightened boy told to keep dancing (0:00) becomes a man who chooses when to walk away (1:03-1:09). Shoe match cut back to the empty childhood room, then the final lone spotlight. |
| Characters too small | Hook, announcement, Joe and glove shots are framed as close-ups. The arena wide is replaced by a Dodger Stadium wide that is followed by closer coverage. Only one shot (the "tiny figure, enormous crowd") is small on purpose. |
| Empty background areas | New dense sets: the 1984 corridor (road cases, cables, caged bulbs), the stadium (four tiers of fans, roofs, light standards, hills), the Victory-scale stage (towers, arched truss, bulb starburst), the TV wall and the studio. |
| Choreography too simple | Added moonwalk glide, toe-stand, the fedora pose, a walk-on and walk-off, a mic speech and lowering the mic, and restrained reactions (looking down, a slow nod, a hand to the chest). Performance shots mix spins, points, kicks and cheers with ripple timing. |
| Text blending into the background | Captions are now EB Garamond **Bold** with a dark stroke, a drop shadow and a soft dark scrim behind each block. They are auto-fitted to 920 px, kept to 1-2 lines, and sit at y≈300 or y≈1440 inside TikTok-safe zones. |
| Quality dips at transitions | Cuts sit on tracked downbeats or half-bars, and white-bloom accents are used only on deliberate cuts into stage worlds. The aging walk hides each costume change inside a light bloom, and the hook uses a same-eye-line graphic match cut. |
| Same child model for adult Michael | Four distinct Michael designs with different height, head proportion, face, hair, costume and movement style: child (1.00), 1972 (1.22, big afro), 1979 (1.52, tuxedo and socks), 1982-84 (1.62, curls, sequined military jacket, one glove). |
| Six-brother 1984 lineup | Jackie, Tito, Jermaine, Michael, Marlon and Randy, all as adult models. None of the child models is used in 1984 scenes, and each keeps his childhood signature color as an accent. |
| Joe aging | A separate Joe 1984 design with grey temples and mustache, a grey suit and a grey fedora. |

Character reference: `CONTINUITY_SHEET_V3.png` (Michael's ages, Joe in the 1960s and 1984, and the 1984 lineup). The V2 sheet still covers the child-era brothers.

## 3. Historical review

| Claim / depiction | Status |
|---|---|
| Rehearsals in Gary under Joe Jackson, who was strict and also managed the group | Well documented. Fear is implied through shadow, posture and reactions; no violence is shown and no dialogue is invented. |
| 1967 Apollo Amateur Night | Documented win (caption). |
| First four Motown singles all reached No. 1 | Documented: I Want You Back, ABC, The Love You Save, I'll Be There (1969-70). |
| Michael's own path before 1984 | Shown as growth across 1972, 1979 and 1982, and the captions place his fame before 1984. 1984 is never presented as the start of his solo career. |
| 1982: Thriller | The record is shown with a plain, generic label. No album artwork is reproduced. |
| 1984 Victory Tour as The Jacksons, six brothers including Randy | Shown with the corridor stencil "THE JACKSONS / VICTORY TOUR 84" and six performers. |
| December 9, 1984, Dodger Stadium, Los Angeles, final show of the tour | Location caption. The stadium is a stylized impression (tiers, outfield roofs, hills), not a survey-accurate model. |
| The announcement | The caption "THIS WILL BE OUR LAST TOUR TOGETHER." is a paraphrase. No speech audio is recreated and there are no quotation marks. The storyboard notes it was the end of that tour, not the last time the brothers ever reunited. |
| Reactions | Restrained and invented as visual storytelling; no confrontation is shown. Joe is only seen watching. |

## 4. Validation of the exported files

| Check | V3_FINAL | V3_SILENT | V3_ENDING_PREVIEW |
|---|---|---|---|
| Resolution / aspect | 1080x1920 (9:16) | 1080x1920 | 1080x1920 |
| Frame rate / frames | 60 fps / 4152 | 60 fps / 4152 | 60 fps / 1269 |
| Duration | 69.200 s | 69.200 s | 21.18 s (0:48.0-1:09.2) |
| Codec | H.264 High, yuv420p | same | same |
| Audio | AAC-LC 48 kHz stereo | none (clean picture master) | AAC 48 kHz |
| A/V start | 0.000 / 0.000 | - | 0.000 / 0.000 |
| Black frames (d≥0.1 s) | 0 | 0 | - |
| Frozen picture over 0.6 s | 0 | 0 | - |
| Audio dropouts (below -50 dB for over 0.4 s) | 0 | - | 0 |
| Loudness / true peak | -12.3 LUFS / -0.7 dBTP | - | - |
| Announcement dip | - | - | RMS about -23 dB for about 5 s against about -13 dB around it, with smooth ramps |

**Frame rate:** 60 fps is native. Every frame is a real vector render with no interpolation, so 60 fps adds smoothness without artifacts.

## 5. Known limitations

- **Production method:** procedural vector animation, not hand-drawn. Body turns are 2.5D cheats, the spin uses squash and blur, and the moonwalk is a stylized glide rather than a motion-captured one.
- **Faces:** lip movement follows vocal energy. The announcement mouth is acted, not synced to any recording.
- **Crowds:** they are layered silhouettes and dot fields, and they move by bouncing, raised arms and flash glints rather than as individual people.
- **Costumes:** the 1984 brothers' outfits are stylized uniforms in their signature colors, not exact copies of archival costumes.
- **Rights:** the song is copyrighted. The versions with audio stay local and out of git; the silent master is provided for licensing or re-scoring.
