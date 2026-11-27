// writes data/PIED_PIPER_V2_SHOT_TIMELINE.json, SHOT_TIMELINE.md and data/PIED_PIPER_V2_SYNC.json from the film code
'use strict';
const fs = require('fs'), path = require('path');
const C = require('../src/core');
const F = require('../src/film');

const DESC = {
  '01_procession_hook': ['Moonlit street, DP framing: the Piper playing in front; behind him a procession of children 3 abreast, perfect lockstep. Every head snaps to camera on the plucked "ta-ta"', 'Taunt hook A5 F#5 B5 A5 F#5 at 0.000; pluck answer 0.882 / 0.993'],
  '02_fingers': ['Extreme close-up: his fingers on the recorder (real fingering of each note)', 'Bar 2 flute call (Bm->C, the F# tritone rub)'],
  '03_eyes': ['Close-up under the hat brim: his eyes open, glowing', 'Flute A5 / F#5'],
  '04_lockstep_feet': ['Low and tight: children\'s legs and hems crossing in lockstep, heels on the beats', 'Pluck answer, 8ths'],
  '05_procession_above': ['From above: the procession winds through the moonlit town, three abreast, still growing', 'Last 16ths before the groove'],
  '06_square_floods': ['Day, sepia (Hamelin, 1284): rats flood the square from the stall, drain and well; villagers leap on the claps', 'Full groove enters; claps 4 / 12'],
  '07_rooftops': ['Rats gallop along the roof ridges, leaping the gaps', 'Hook over C'],
  '08_sacks_burst': ['Grain sacks burst one by one (s8 / s10 / s13); the merchant recoils', 'Pluck answer'],
  '09_kitchen': ['A family kitchen: rats run across the table; the mother leaps onto the bench (clap), the father raises a stool (clap), the boy hides, the cat backs away', 'T2 lift + fiddle'],
  '10_barrel': ['A barrel lid flies off; rats burst out in three waves (s0 / s3 / s6)', 'Cadence over G'],
  '11_carpet_above': ['From above: the street is a carpet of 240 rats; townsfolk flee against the flow', 'F# turnaround'],
  '12_gate': ['The town gate grinds open (the ratchet); townsfolk turn on the beats; a backlit silhouette; he steps through in the silence', 'Build, ratchet, roll, riser; silence 12.13'],
  '13_stranger_strides': ['Tracking backward: the stranger strides toward us through the market; villagers turn to him in a wave on the beats; rats scatter', 'Hurdy-gurdy calls, flute answers'],
  '14_the_offer': ['Council chamber: palm up on the gurdy call, a sweep to the window (the rats), the recorder tapped on his answer; the council leans in', 'Gurdy call / flute answer'],
  '15_the_agreement': ['The chest of gold opens on the downbeat; the handshake on his answer; he bows and tips his hat', 'Gurdy call / flute answer over C'],
  '16_raises_flute': ['Low angle: he raises the flute; wind; the rising run', 'Spell: F#5 G5 A#5 B5 C#6 D6'],
  '17_rats_freeze': ['Rat level: they scurry, freeze on the trill, turn their heads, and rise onto their hind legs in the silence', 'C#6 trill, A#5, silence 19.19'],
  '18_rat_ocean_tracking': ['DROP 1: tracking beside him; behind him 140 rats in lockstep rows, tails swinging together; a hop ripples through the rows on the 16th scurry', 'Drop 1 at 19.41; rat scurry 20.29'],
  '19_rings_overhead': ['Overhead: five counter-rotating rings pulse on the kick; the scurry ripples outward ring by ring', 'Hook over C; scurry'],
  '20_rats_eye': ['Rat\'s-eye: paws and tails pass the lens in lockstep; his legs stride behind', 'T2 lift'],
  '21_hopping_lines': ['Along the wall: each rising plucked note lifts the next line of rats', 'Rising pluck answer'],
  '22_out_of_the_gate': ['Dusk, wide: a living ribbon of rats winds out of the gate down to the Weser behind him', 'Cadence G-F#'],
  '23_into_the_water': ['They leap from the bank in arcs, two per 16th; only rings remain; he plays on his rock', 'River: tenor recorder below'],
  '24_still_water': ['The hit: one last ring; still water and his reflection', 'Hit + gong 28.24; falling F5'],
  '25_celebration_burst': ['The whole town springs up into the DP squat dance (rows in canon), bunting, confetti', 'Celebration in D at 30.00'],
  '26_spins_and_claps': ['Closer: spins, stomps, jigs; the front rows clap on every beat', 'Claps on every beat'],
  '27_to_the_officials': ['He walks through the dancers to the officials\' table, his palm held out', 'Pluck answer'],
  '28_chest_slam': ['The chest SLAMS shut on the betrayal downbeat (coins, dust); the mayor wags "no" in half time; his hand stays out', 'Betrayal 33.53: the taunt turns minor'],
  '29_stillness': ['The town keeps dancing in half time with frozen grins around the perfectly still Piper; the officials laugh silently', 'Bb; half-time drums'],
  '30_smile_dies': ['Close-up: his smile dies; the sun sets across his face, the moon rises; on the C# hang he turns to us, eyes glowing', 'Gm, C# tritone hang 37.94'],
  '31_he_returns': ['Night: his silhouette in the empty moonlit street raises the flute; a long moon shadow', 'Flute alone in 16ths'],
  '32_toy_falls': ['A boy stops playing; the wooden horse falls from his hand', '16ths'],
  '33_candle_bends': ['A candle flame bends toward the window; a girl\'s eyes open', '16ths'],
  '34_shutters_burst': ['Shutters burst open in a cascade; in the silence every window dims at once', 'Silence 40.37'],
  '35_doors_open': ['DROP 2: doors fly open on the beats; children step out in matching strides toward the Piper', 'Drop 2 at 40.59 (soprano 8va)'],
  '36_lockstep_legs': ['A forest of legs in lockstep, hems swinging, moon shadows', 'Hook over C'],
  '37_procession_grows': ['He walks toward us playing; rows of six behind him; children slide in from both sides on every 16th', 'T2 lift'],
  '38_faces_freeze': ['Close faces: heads tilt in a canon on the cadence notes; in the break they snap to camera and freeze', 'Break 47.43'],
  '39_snake_above': ['From above: the procession snakes four abreast through the moonlit roofs, long shadows', 'Climax: gurdy imitates the taunt'],
  '40_trades': ['Quarter-bar call and response: Piper against the moon / the crowd lifts its arms / Piper close / a row of heads tilts together', 'Half-bar trades flute / gurdy'],
  '41_moon_ridge': ['Silhouettes against a huge moon, climbing toward the mountain', 'Em lift; fiddle descant'],
  '42_mountain_reveal': ['The reveal: the whole procession winds across the valley into the glowing passage; it flares on the stab', 'TAG A#-B-C-C#-D; stab 54.26'],
  '43_passage_swallows': ['At the passage: four stabs, four groups gone into the light; the last girl looks back; he steps in; the rock seals in the silence', 'Stutter stabs 54.71 / 55.04 / 55.37 / 55.81; silence 56.03'],
  '44_sealed_mountain': ['The sealed mountain: footprints into solid rock, one small shoe, his feather falling', 'Hook alone, no band'],
  '45_empty_bed': ['A mother with a candle finds the empty bed; the wooden horse on the floor', 'Pluck answer only'],
  '46_parents_doorways': ['Dawn: parents in the empty doorways turn toward the mountain on the heartbeat; toys on the steps', 'Taunt with holes; heartbeat kick'],
  '47_deserted_street': ['The opening street, deserted: fog, the torch, a wooden horse', 'Tenor low in the fog'],
  '48_loop': ['The horse rolls by itself on each giggle note; for a moment he is playing in the fog; the frame settles exactly on the opening composition', 'Last giggle; F#5-G5 pickup loops into bar 1'],
};

const shots = F.SHOTS.map((s, i) => {
  const t1 = i + 1 < F.SHOTS.length ? F.SHOTS[i + 1].t0 : C.NFRAMES / C.FPS;
  return { n: i + 1, id: s.id, start: +s.t0.toFixed(4), end: +t1.toFixed(4), frame_start: Math.round(s.t0 * C.FPS), frame_end: Math.round(t1 * C.FPS),
    bar: +(s.t0 / C.BAR + 1).toFixed(3), picture: (DESC[s.id] || [''])[0], music: (DESC[s.id] || ['', ''])[1] };
});
const caps = F.CAPS.map(c => ({ text: c.text.replace('\n', ' '), style: c.kind, start: +c.t0.toFixed(3), end: +Math.min(c.t1, C.DUR).toFixed(3) }));
const out = path.join(C.ROOT, 'data');
fs.writeFileSync(path.join(out, 'PIED_PIPER_V2_SHOT_TIMELINE.json'), JSON.stringify({ fps: C.FPS, frames: C.NFRAMES, duration: C.NFRAMES / C.FPS, shots, captions: caps }, null, 1));
let md = `# THE PIED PIPER OF HAMELIN (V2): shot timeline\n\nRebuilt around PIED_PIPER_NEW_SOUNDTRACK.wav · 60 fps · ${C.NFRAMES} frames · ${(C.NFRAMES / C.FPS).toFixed(3)} s · 136 BPM (bar = ${C.BAR.toFixed(4)} s, beat = ${C.BEAT.toFixed(4)} s)\n\n| # | Shot | Start | End | Frames | Bar | Picture | Music cue |\n|---|---|---|---|---|---|---|---|\n`;
for (const s of shots) md += `| ${s.n} | ${s.id} | ${s.start.toFixed(2)} | ${s.end.toFixed(2)} | ${s.frame_start}–${s.frame_end} | ${s.bar} | ${s.picture} | ${s.music} |\n`;
md += `\n## Captions\n\n| Start | End | Style | Text |\n|---|---|---|---|\n`;
for (const c of caps) md += `| ${c.start.toFixed(2)} | ${c.end.toFixed(2)} | ${c.style} | ${c.text} |\n`;
fs.writeFileSync(path.join(C.ROOT, 'SHOT_TIMELINE.md'), md);
const fr = t => Math.round(t * C.FPS);
const BM = C.BM;
const sync = {
  soundtrack: 'audio/PIED_PIPER_NEW_SOUNDTRACK.wav (approved, unchanged)', bpm: BM.bpm, fps: C.FPS, frames: C.NFRAMES, duration: C.NFRAMES / C.FPS,
  beats: Array.from({ length: BM.bars * 4 }, (_, i) => ({ i, t: +(i * C.BEAT).toFixed(4), frame: fr(i * C.BEAT), bar: Math.floor(i / 4) + 1, beat: i % 4 + 1 })),
  sections: BM.sections.map(s => ({ ...s, frame_start: fr(s.start), frame_end: fr(s.end) })), drops: BM.drops.map(d => ({ ...d, frame: fr(d.time) })),
  gaps: BM.gap_spans.map(g => ({ ...g, frame_start: fr(g.start), frame_end: fr(g.end) })), harmony: BM.harmony,
  accents: BM.accents.map(a => ({ ...a, frame: fr(a.time) })),
  events: Object.fromEntries(Object.entries(BM.events).map(([k, v]) => [k, v.map(t => ({ t: +t.toFixed(4), frame: fr(t) }))])),
  flute_notes: BM.flute.map(n => ({ ...n, frame: fr(n.t) })), flute_phrases: BM.phrases,
  measured_transients: { kick: BM.measured.kick, backbeat: BM.measured.backbeat, hats: BM.measured.hats, breaks: BM.measured.breaks, low_breaks: BM.measured.low_breaks },
  shots, captions: caps,
};
fs.writeFileSync(path.join(out, 'PIED_PIPER_V2_SYNC.json'), JSON.stringify(sync));
console.log('shots', shots.length, 'captions', caps.length);
