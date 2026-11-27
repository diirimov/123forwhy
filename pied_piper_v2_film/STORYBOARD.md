# THE PIED PIPER OF HAMELIN (V2): music-led storyboard

**Soundtrack:** `PIED_PIPER_NEW_SOUNDTRACK.wav`. 136 BPM, 37 bars, 65.294 s. Bar = 1.7647 s, beat = 0.4412 s.

The structure is measured from the audio in `AUDIO_ANALYSIS.md`. Every cut lands on a bar, a half bar, a beat or a 16th. Every musical change gets a visual change.

## What V1 got wrong, and what V2 does instead

| V1 weakness | V2 answer (from the Dancing Plague render) |
|---|---|
| Characters were tiny in deep one-point streets; half the frame was empty cobbles | DP staging (`src/dp.js`): a waist-height camera, front characters filling about 45 % of the frame, and a wall of stacked gables behind them (three depth layers) |
| Repetitive street angle | About 48 setups: frontal DP walls, backward tracking, side tracking, overheads, rat's-eye view, leg-level, extreme close-ups, interiors, silhouettes, the valley reveal |
| Walks slid and crowds were static | Stride-locked walks (body speed = stride / stance time, heels on the beats); the DP dance vocabulary in `src/chor.js` (squat, jig, stomp, spin, clap, sway, half-time); canons and waves through crowds |
| The procession was a single line | Rows of 3–6, children joining from the alleys, the lockstep-legs forest, the snake from above, quarter-bar trades, faces in a canon |
| The disappearance was quick and the ending was a title card | Four stabs make four groups vanish; the last child looks back; the sealed rock with footprints, a shoe and a feather; the empty bed; parents in the doorways; the deserted street returns to the opening frame (loop). No title screen |

## Sequences

| Time (s) | Music | Picture |
|---|---|---|
| 0.00–3.53 | **The taunt** (hook on beat 1), plucked answer | The Piper and a procession of children in lockstep. Every head snaps to camera on the plucked "ta-ta" (0.88 / 0.99). Then a cut on every beat: his fingers (real fingering), his eyes, the lockstep feet, the procession from above. Caption: **130 CHILDREN VANISHED.** |
| 3.53–10.59 | Full groove, claps, T2 lift, cadence | **HAMELIN, 1284.** The square floods with rats (villagers leap on the claps). Rats on the roof ridges. Sacks burst. The kitchen table (mother on the bench, father with a stool, boy hiding, cat). The barrel. A carpet of rats from above. Caption: **The town was overrun by rats.** |
| 10.59–12.35 | Ratchet build, silence 12.13 | The gate grinds open; a silhouette steps through in the silence |
| 12.35–17.65 | Hurdy-gurdy calls, flute answers | He strides toward us; heads turn in a wave on the beats. The offer (palm on the call, the recorder tapped on the answer). The agreement (the chest opens, a handshake, a bow). Caption: **A stranger offered to save them.** |
| 17.65–19.41 | The spell (rising run, trill, silence) | Low angle: he raises the flute. The rats freeze on the trill, turn their heads, and rise in the silence |
| **19.41–28.24** | **DROP 1** | Side tracking: an ocean of rats in lockstep rows, tails in unison, hops rippling through the rows on the 16th scurry. Overhead counter-rotating rings breathing on the kick. Rat's-eye view. Lines of rats hopping on the rising plucked notes. A ribbon down to the Weser. Into the water (rings only). Caption: **The rats followed his melody.** |
| 28.24–30.00 | Hit + gong, near-silence | Still water, his reflection |
| 30.00–33.53 | Celebration in D, claps on every beat | The whole town in the DP dance in canon, bunting and confetti. Spins and claps. He walks through them with his palm out |
| 33.53–38.82 | Betrayal (the taunt turns minor, half time) | The chest **slams** on the downbeat. Caption: **But they refused to pay him.** The town dances on in half time around his total stillness. His smile dies as day drains into night, and he turns to us on the C# tritone |
| 38.82–40.59 | The flute alone in 16ths, silence 40.37 | A cut on every beat: his silhouette raises the flute; the toy horse falls; the candle bends to the window; shutters burst open, then every window dims. Caption: **So he played again.** |
| **40.59–54.71** | **DROP 2** + climax | Doors open on the beats and the children step out. Lockstep legs. The procession grows from every alley. Faces tilt in a canon, then freeze and stare in the break (47.43). The snake from above. Quarter-bar trades (Piper / crowd). Silhouettes against the moon. The mountain reveal. Caption: **This time, the children followed.** |
| 54.71–56.47 | Stutter stabs, silence 56.03 | Four stabs, four groups gone into the light. The last girl looks back. He steps in. The rock seals |
| 56.47–65.29 | The hook with no band, the answer with no flute, the taunt with holes, the tenor in the fog, the last giggle and the pickup | The sealed rock: footprints, a shoe, a falling feather. The empty bed (**According to legend, 130 children vanished.**). Parents in the doorways at dawn. The deserted opening street (**They never returned.**). The horse rolls by itself on each giggle note; for a moment he is playing in the fog. The last frame is the first frame without the children |

## The fear

There is no gore, no zombies and no horror effects. The fear comes from precision:

- children who are peaceful and perfectly synchronised;
- heads that turn together;
- a town that keeps dancing while the betrayed man stands perfectly still;
- the girl who looks back;
- the street that is suddenly empty.
