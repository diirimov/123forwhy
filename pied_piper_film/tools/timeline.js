// writes data/PIED_PIPER_SHOT_TIMELINE.json, SHOT_TIMELINE.md and data/PIED_PIPER_SYNC.json from the code itself
'use strict';
const fs = require('fs'), path = require('path');
const C = require('../src/core');
const F = require('../src/film');

const DESC = {
  '01_procession': ['Moonlit street: the procession of children walks in lockstep behind the Piper (heel strikes on the beats); every head snaps to camera on the D#5 hang', 'drum + bell + flute call at 0.000; D#5 hang 1.32'],
  '02_piper_closeup': ['Extreme close-up of the Piper playing; eyes open on the claves, fingers lift on the giggle notes (real fingering)', 'pause; claves 1.99/2.10; giggle E6 E6 B5'],
  '03_drain': ['Day, sepia (back in time): rats pour out of a drain grate on 32nd-note spacing across the street', 'groove enters: stomps, claps, bass'],
  '04_rooftops_sacks': ['Rats gallop along the roof ridges; grain sacks burst on the tambourine and rats spill under the stall', 'cadence + tambourine'],
  '05_barrel': ['The merchant yanks the barrel lid on the downbeat; rats burst out on the toms (3+3+2); he recoils', 'kick + toms enter 7.06'],
  '06_baker_table_cat': ['The baker recoils (stab 1), a merchant leaps onto a table (stab 2), a cat arches and backs away from the swarm', 'band answer 8.82 / 9.15'],
  '07_gate': ['The city gate grinds open on the ratchet; a backlit silhouette in the fog steps through in the silence', 'build, ratchet, roll, silence 12.13'],
  '08_market_stride': ['FIRST DROP: tracking shot as the Piper strides through the market; the crowd turns toward him in a wave on the beats', 'first drop 12.35'],
  '09_heads_snap': ['Heads snap to him on the two band stabs; he bows and tips his hat on the giggle', 'band answer 14.12 / 14.45'],
  '10_council': ['The council chamber (callback to the studio\'s council scene): he offers; the mayor nods on the beats; a rat runs over the table', 'call 2'],
  '11_raise_flute': ['He raises the recorder; the fingering follows the real cadence notes', 'cadence F E C B C B G#'],
  '12_rats_freeze': ['Rat\'s-eye view: scurrying rats freeze on the second note; ears twitch on each note; heads turn to camera on the hang', 'ornamented call'],
  '13_rats_rise': ['Rows of rats rise onto their hind legs on the two stabs and sway in time toward the Piper', 'band answer 21.18 / 21.51'],
  '14_overhead_rings': ['Overhead: three counter-rotating rings of rats pulse on the kick around the walking Piper; the stream behind tightens into lockstep', 'call 2'],
  '15_river_wide': ['Dusk on the Weser: the Piper on a rock, a river of rats flowing along the shore toward him', 'Bb + gong 24.71'],
  '16_into_water': ['The rats leap into the water; ripples ring out; big rings on the half-time hits', 'half-time Eb'],
  '17_still_water': ['Still water and his reflection; the last rings fade; small ripples on each stomp in the silence', 'hit + pause 28.24'],
  '18_celebration_burst': ['The town bursts out: bunting rises on the beats; people jump up one per note of the chromatic creep', 'regroove + creep'],
  '19_celebration_dance': ['The whole town in the studio\'s squat-dance, in perfect sync; the Piper watches, utterly still', 'hook returns, darker'],
  '20_chest_slam': ['He holds out his hand; the mayor slams the chest of gold shut on the flute\'s falling Bb bend', 'wrong-note giggle'],
  '21_refusal_laughter': ['Silent laughter shaking on the eighths; the councillor flicks him away on every beat', 'call 2, dissonant'],
  '22_smile_fades': ['Close-up: his hand lowers, the smile disappears, the light drains from warm to cold', 'cadence, dark'],
  '23_walk_into_night': ['He walks away; his shadow climbs the wall; the sky time-lapses from day to night into the silence', 'flute alone, 16ths, silence 40.37'],
  '24_windows_burst': ['FINAL DROP: the Piper alone in the moonlit street; shutters burst open and windows light up in an eighth-note cascade', 'final drop 40.59'],
  '25_toy_drops': ['Inside: a boy drops his wooden horse (stab 1), a girl turns (stab 2); the rat on the sill never moves', 'band answer 42.35 / 42.68'],
  '26_doors_open': ['Doors open on the beats; children step out of the glowing doorways in matching strides', 'call 2'],
  '27_procession_grows': ['Children join the line one per eighth note; in the silence everyone freezes and turns to camera', 'cadence, tom fill, silence 47.54'],
  '28_tracking_procession': ['Long tracking shot alongside the procession; lantern posts sweep past in the foreground; synchronised footsteps', 'second pass, trills'],
  '29_overhead_snake': ['Overhead: the procession snakes through the streets with long moon shadows', 'obsessive call'],
  '30_peaceful_faces': ['Six peaceful faces; one turns to camera on each tresillo accent', 'call 2 accents'],
  '31_moon_silhouettes': ['Silhouettes climb toward the mountain under a huge moon (the studio\'s silhouette style)', 'closed cadence'],
  '32_passage_closes': ['At the mountain passage the children vanish group by group on the stabs; the Piper steps in and it seals in the silence', 'stutter stabs, silence 56.03'],
  '33_empty_bed': ['A mother with a candle finds the empty bed', 'layers vanish'],
  '34_abandoned_toys': ['Abandoned toys on the floor at the open door; the horse still rocking', 'giggle, bass gone'],
  '35_empty_street': ['The empty street from the opening; a wooden toy on the cobbles; the legend card', 'kick gone'],
  '36_piper_in_fog': ['The Piper\'s silhouette appears far down the street in the fog', 'closed cadence'],
  '37_legend_title': ['He dissolves on the last giggle; the title; the frame settles on the opening composition (loop)', 'last giggle, G# pickup'],
};

const shots = F.SHOTS.map((s, i) => {
  const t1 = i + 1 < F.SHOTS.length ? F.SHOTS[i + 1].t0 : C.NFRAMES / C.FPS;
  return { n: i + 1, id: s.id, start: +s.t0.toFixed(4), end: +t1.toFixed(4), frame_start: Math.round(s.t0 * C.FPS), frame_end: Math.round(t1 * C.FPS),
    bar: +(s.t0 / C.BAR + 1).toFixed(2), lighting: (s.grade ? 'graded' : s.mood) || 'day', picture: (DESC[s.id] || [''])[0], music: (DESC[s.id] || ['', ''])[1] };
});
const caps = F.CAPS.map(c => ({ text: c.text.replace('\n', ' '), style: c.kind, start: +c.t0.toFixed(3), end: +c.t1.toFixed(3) }));
const out = path.join(C.ROOT, 'data');
fs.writeFileSync(path.join(out, 'PIED_PIPER_SHOT_TIMELINE.json'), JSON.stringify({ fps: C.FPS, frames: C.NFRAMES, duration: C.NFRAMES / C.FPS, shots, captions: caps }, null, 1));
let md = `# THE PIED PIPER OF HAMELIN: final shot timeline\n\n60 fps · ${C.NFRAMES} frames · ${(C.NFRAMES / C.FPS).toFixed(3)} s · 136 BPM (bar = ${C.BAR.toFixed(4)} s)\n\n| # | Shot | Start | End | Frames | Bar | Picture | Music cue |\n|---|---|---|---|---|---|---|---|\n`;
for (const s of shots) md += `| ${s.n} | ${s.id} | ${s.start.toFixed(2)} | ${s.end.toFixed(2)} | ${s.frame_start}–${s.frame_end} | ${s.bar} | ${s.picture} | ${s.music} |\n`;
md += `\n## Captions\n\n| Start | End | Style | Text |\n|---|---|---|---|\n`;
for (const c of caps) md += `| ${c.start.toFixed(2)} | ${Math.min(c.end, C.NFRAMES / C.FPS).toFixed(2)} | ${c.style} | ${c.text} |\n`;
fs.writeFileSync(path.join(C.ROOT, 'SHOT_TIMELINE.md'), md);
// animation sync data (frame-indexed)
const fr = t => Math.round(t * C.FPS);
const BM = C.BM;
const sync = {
  soundtrack: 'audio/FOLLOW_THE_PIPER_V2.wav (approved V2, unchanged)', bpm: BM.bpm, fps: C.FPS, frames: C.NFRAMES,
  beats: Array.from({ length: BM.bars * 4 }, (_, i) => ({ i, t: +(i * C.BEAT).toFixed(4), frame: fr(i * C.BEAT), bar: Math.floor(i / 4) + 1, beat: i % 4 + 1 })),
  sections: BM.sections, gaps: BM.gaps.map(t => ({ t, frame: fr(t) })),
  accents: BM.accents.map(a => ({ ...a, frame: fr(a.time) })),
  events: Object.fromEntries(Object.entries(BM.events).map(([k, v]) => [k, v.map(t => ({ t: +t.toFixed(4), frame: fr(t) }))])),
  flute_notes: BM.flute.map(n => ({ ...n, frame: fr(n.t) })),
  shots, captions: caps,
};
fs.writeFileSync(path.join(out, 'PIED_PIPER_SYNC.json'), JSON.stringify(sync));
console.log('shots', shots.length, 'captions', caps.length);
