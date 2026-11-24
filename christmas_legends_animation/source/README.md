# 3 Dark Christmas Legends: animation project source

The whole animation is procedural vector art, drawn with Skia in Python. Each frame is computed from the soundtrack's bar/beat grid, so if you change the code and render again, everything stays in sync.

| File | What it contains |
|---|---|
| `gfx.py` | Drawing helpers: paints, gradients, glows, paths, text, film grain and vignette. |
| `human.py` | An articulated human rig: limbs, faces with 6 eye modes and 7 mouth shapes, brows, hats, hair, clothing, walk and run cycles. |
| `creatures.py` | The Krampus, Yule Cat and Mari Lwyd rigs: jaw, tongue, chains, ears, pupils, ribbons, sheet and tail. |
| `world.py` | Environment kit: sky and aurora, mountains, houses (chalet, half-timbered, stone, Icelandic), church, pines, lights, snow, snowman and fence. |
| `stages.py` | The seven stage sets, built as parallax layers, plus the camera. |
| `film.py` | The music clock and all 20 shots, with their choreography. |
| `main.py` | The timeline, transitions, captions and title cards, plus the parallel renderer. |
| `keys.py` | Renders a contact sheet of key frames, for reviewing the edit. |
| `write_timeline.py` | Generates `CHRISTMAS_LEGENDS_SYNC_TIMELINE.md`. |
| `fonts/` | Luckiest Guy, Cinzel Decorative and Fredoka, all SIL Open Font License. |

## Render

```bash
pip install skia-python numpy
python3 main.py out_dir            # writes 45 h264 chunks plus list.txt
ffmpeg -f concat -safe 0 -i out_dir/list.txt -i FINAL_MIX_SOUNDTRACK_PLUS_NARRATION.wav \
       -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -t 90 CHRISTMAS_LEGENDS_FINAL_90S.mp4
python3 keys.py sheet.png 10.0,20.0,30.0   # review any timestamps
```

The audio uses the `FINAL_CHRISTMAS_DANCE_MASTER.wav` soundtrack unchanged. The narration was generated with the Kokoro TTS model (voice `am_fenrir`).
