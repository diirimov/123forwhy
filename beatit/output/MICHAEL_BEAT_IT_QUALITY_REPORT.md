# "The Song That Changed Michael Jackson Forever" (the making of Beat It): quality report

## Deliverables

| File | What it is | In git |
|---|---|---|
| `MICHAEL_BEAT_IT_STORY_FINAL.mp4` | Final film with the supplied 60 s "Beat It" edit | No (copyrighted audio, kept local) |
| `MICHAEL_BEAT_IT_STORY_SILENT.mp4` | Identical picture master, no audio | Yes |
| `MICHAEL_BEAT_IT_PREVIEW.mp4` | 24 s preview (opening, Eddie, payoff dance, ending), rendered and reviewed before the final | No |
| `MICHAEL_BEAT_IT_STORYBOARD.md` | Shot-by-shot timeline, music map, captions, historical notes (generated from the code) | Yes |
| `MODEL_SHEET_BEAT_IT.png` | Cast sheet: Michael 1970 / 1982 studio / 1983 red jacket / stage; Quincy Jones; Eddie Van Halen; supporting cast | Yes |
| `../src/` | Editable project: 4 act modules, cast, set-dressing, timing, renderer | Yes |

Rebuild: put the edit at `beatit/audio/source.m4a` (and `ffmpeg -i source.m4a source.wav`), then
`python3 src/analyze_audio.py && python3 src/render.py final`. Shared engine: `jackson5/src` (characters, choreography, camera).

## Process

1. **Audio first.** I measured the supplied edit: exactly 60.000 s, AAC 44.1 kHz stereo, -8.0 LUFS, true peak +2.2 dBTP. The beat grid is continuous at about 138.4 BPM (bar 1.729 s), with no tempo jumps at splice points. Breaks fall at 8.3, 28.8-29.3, 43.5 and 56.5-57.3 s, and the strong vocal accent at 29.93 s.
2. **Structure locked to the music.**
   - The five acts start on downbeats 0, 9.185, 17.833, 29.933 and 42.036 s.
   - The entrance hit is at 43.770 s and the head raise at 57.591 s.
   - All 38 cuts land on downbeats or half-bars.
3. **Cast built and checked on a model sheet before any shot was made.**
   - The adult Michael is the same design that ends the Jackson 5 V3 film, and the child Michael and his brothers are the Jackson 5 models. That is the continuity with the previous episode.
   - New engine features, all off by default so earlier films are unchanged: glasses and beard, feathered rock hair, the zippered leather jacket, and a striped electric guitar.
4. **Each act built and inspected as stills.** I fixed:
   - five brothers too tightly spaced
   - a photograph too small to read
   - a caption covering the sheet-music title
   - characters' heads under a caption
   - neon guitars that did not read as guitars
   - three raised-hand poses that waved outward instead of reaching the ear
   - an amp jack off-frame
   - hands that looked like mittens
   - a muddy feet shot, rebuilt as neon silhouettes
   - a slate overlapping a caption
   - a crowded dance formation
   - onlookers covering the TV screens
   - a store sign hidden by a caption
5. **Preview rendered and reviewed** (`MICHAEL_BEAT_IT_PREVIEW.mp4`). One more pose fix: a hand crossed Michael's face in the playback shot.
6. **Full render.** The first attempt crashed on a TV-screen frame the stills had not sampled. I fixed it, then rendered every 7th frame of the whole film (514 frames) with no errors. The validator then flagged a 0.85 s static hold in the kids shot. I gave the kids a dance phrase that starts with their shot and rendered the film again.

## Validation of the final file

| Check | Result |
|---|---|
| Duration | 60.000 s (video and audio streams both 60.000 s) |
| Frames | 3600 at 60 fps (native: every frame is a real vector render, no interpolation) |
| Resolution / aspect | 1080 x 1920, 9:16, no bars |
| Codec | H.264 High, yuv420p, CRF 14; AAC-LC 320 kb/s, 48 kHz stereo |
| A/V start | 0.000 / 0.000 |
| Black frames | Only the intended fade to black in the last 0.13 s |
| Frozen picture over 0.6 s | None |
| Audio dropouts (below -50 dB for over 0.4 s) | None |
| Loudness / true peak | -11.6 LUFS integrated / -1.2 dBTP true peak (no clipping) |
| Watermark | None |

**Audio handling.** The song is unchanged in speed, pitch, EQ and arrangement. Two level changes were made:
- **Gain trim of -3.5 dB.** The supplied master already peaks at +2.2 dBTP, which would clip after AAC encoding.
- **A 1-second fade** at 59.0-60.0 s, after the last downbeat. The edit runs at full level into a hard stop at 60.000 s, so the fade and the picture fade end together instead of cutting off.

## Historical review

| Depiction | Basis |
|---|---|
| Child star with his brothers, then 1982 | The Jackson 5 era opening; the *Thriller* sessions were in 1982 |
| Quincy Jones wanted a rock song | Widely documented. He is shown suggesting it (air guitar); no words are quoted |
| Michael writes "Beat It" | Michael wrote the song; the sheet is a stylised prop |
| Eddie Van Halen plays the solo | Documented. The phone call is shown without dialogue, and nothing is invented about what was said |
| Eddie and Michael | Never shown in the same room: Eddie at home and recording, Michael later hearing a "PLAYBACK" tape labelled "GTR SOLO" |
| 1983 Los Angeles video with real gang members and dancers, message against violence | Documented. The two groups are not identified by gang colours |
| The red zippered leather jacket | Iconic costume, drawn as a stylised design |
| Billboard Hot 100 No. 1, 1983 | Documented. Other chart rows are anonymous bars, with no invented titles |
| Record stores, TVs, kids copying the dance | Impressionistic depiction of the song's cultural impact |
| Final concert | A generic, stylised concert; no specific date or venue is claimed |

No humiliating rejections, arguments, fictional quotes or scandals appear. The film tells the story of how the song was made; it does not recreate the music video's shots or choreography. Record sleeves are plain typographic designs, not the real cover art.

## Known limitations

- **Production method:** procedural 2D vector animation with rigged characters, not hand-drawn frames. Turns and spins are 2.5D cheats, and dance moves come from a beat-locked move library.
- **Faces and lips:** lip movement follows the vocal energy and is not phoneme-accurate. Close-ups favour acting such as eyes, brows and smiles.
- **Crowds:** cached silhouette rows that bounce and raise arms, not individually animated people.
- **Likeness:** costumes and likenesses are stylised impressions in the series' house style, not portraits.
- **Rights:** the song is copyrighted. The versions with audio stay out of git; the silent master is in the repository.
