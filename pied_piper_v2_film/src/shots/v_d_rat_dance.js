// 18-24 DROP 1 -- THE RAT PROCESSION (bars 12-17). The melody controls the rats: lockstep gallop on the beat,
// tails swinging in unison, ripples on the hurdy-gurdy's 16th scurry, rings pulsing on the kick, hops on the
// rising plucked notes; out of the gate, down to the Weser, into the water (rings only), still water.
'use strict';
const C = require('../core');
const R = require('../rig');
const PS = require('../person');
const CAST = require('../cast');
const E = require('../env');
const Wd = require('../world');
const ST = require('../stage');
const RT = require('../rats');
const PP = require('../piper');
const TD = require('../topdown');
const K = require('../ink');
const PO = require('../post');
const DP = require('../dp');
const CH = require('../chor');
const SETS = require('../sets');
const { barT: b, clamp, lerp, ease, BEAT, BAR, S16, HIT, W, H, TAU, hash } = C;
const PB = CAST.piper.B;
const PSTRIDE = 100, PSPEED = PSTRIDE / (.6 * 2 * BEAT);
const lockPh = t => t / BEAT;                                   // one gallop per beat, every rat the same phase
const scurry = (t, bar, k) => { const s = (t - b(bar, 8)) / S16; if (s < 0 || s > 8) return 0; return Math.max(0, Math.sin(Math.PI * clamp(s - k))) ; };

// ---------------------------------------------------------------- 18: DROP -- tracking beside him; an ocean of rats in lockstep rows behind
function shot18(g, t, lt) {
  const t0 = b(11);
  const px = (t - t0) * PSPEED;
  const kp = C.kickPulse(t, 8);
  const { V, items } = DP.town(g, t, { mood: 'day', cam: { cx: px - 190, cy: 175, f: 1150 * (1 + .025 * kp), hy: 1010 }, sunX: 860, clouds: [[200, 260, 1.1]], seed: 71, shift: px * .9,
    zNear: 2900, zMid: 3900, zFar: 5000, nNear: 11, nMid: 13, nFar: 17 });
  // the rats: 8 rows deep x 12, all galloping on the beat; on the scurry, a hop runs through the rows (canon)
  for (let r = 0; r < 10; r++) for (let i = 0; i < 14; i++) {
    const z = 400 + r * 175, x = px - 230 - i * 140 - (r % 2) * 70 + Math.sin(r * 1.3) * 30 + Math.max(0, 700 - z) * .4;
    const hop = scurry(t, 11, r * .9 + (i % 3) * .2);
    items.push({ z, draw: (g2, V2) => ST.ratAt(g2, V2, x, z, { dir: 1, phase: lockPh(t), speed: 1, t, size: 1.2, y: hop * 55, tilt: -hop * .3, tail: 1.2, ear: C.decay(C.fluteOnsetSince(t + HIT), 10) }) });
  }
  // the Piper: elegant strides, playing as he walks
  DP.actorAt(items, CAST.piper, px, 760, CH.piperWalkPlay(PP, { t0, yaw: Math.PI / 2 - .35, stride: PSTRIDE, glow: .4 }), t, { wind: .5 });
  DP.flush(g, V, items);
}

// ---------------------------------------------------------------- 19: overhead -- counter-rotating rings breathing on the kick; the scurry ripples outward
function shot19(g, t, lt) {
  const t0 = b(12);
  const walkV = 70, py = -(t - t0) * walkV;
  const rot = lerp(-.12, .12, ease.io(lt / 1.77)), zoom = lerp(1.0, 1.18, ease.io(lt / 1.77));
  g.save(); g.translate(W / 2, H * .5); g.rotate(rot); g.scale(zoom, zoom); g.translate(-W / 2, -H * .5 - py);
  TD.cobblesTop(g, -600, py - 1600, W + 600, py + H + 1600);
  TD.roofsTop(g, -60, py - 1700, py + H + 1700, -1, { seed: 3 }); TD.roofsTop(g, W + 60, py - 1700, py + H + 1700, 1, { seed: 7 });
  const cx = W / 2, cy = H * .46 + py;
  const kp = C.kickPulse(t, 7);
  const rings = [[200, 8, 1], [300, 13, -1], [400, 18, 1], [500, 23, -1], [600, 28, 1]];
  rings.forEach(([r0, n, dir], ri) => {
    const rip = scurry(t, 12, ri * 1.3);
    const r = r0 * (1 + .06 * kp) + rip * 30;
    for (let i = 0; i < n; i++) {
      const a = i / n * TAU + dir * (t - t0) * (1.1 - r0 / 900);
      const x = cx + Math.cos(a) * r, y = cy + Math.sin(a) * r * .96;
      RT.ratTop(g, x, y, a + dir * Math.PI / 2, { s: 1.0 + .15 * rip, phase: lockPh(t), t, speed: 1 });
    }
  });
  // the tail of the procession behind: a sine ribbon three abreast
  for (let i = 0; i < 60; i++) for (const lat of [-40, 0, 40]) {
    const d = 700 + i * 40;
    const sx = cx + Math.sin(d * .01 - (t - t0) * 3) * 90 + lat, sy = cy + d;
    RT.ratTop(g, sx, sy, -Math.PI / 2 + Math.cos(d * .01 - (t - t0) * 3) * .4, { s: .95, phase: lockPh(t), t, speed: 1 });
  }
  TD.personTop(g, cx, cy, -Math.PI / 2, { ch: CAST.piper, s: 1.6, phase: (t - t0) / (2 * BEAT), t, flute: true, armAmt: .2, armFwd: true });
  g.restore();
}

// ---------------------------------------------------------------- 20: rat's-eye view -- paws and tails pass the lens in lockstep
function shot20(g, t, lt) {
  const t0 = b(13);
  const V = new Wd.View({ cx: (t - t0) * 300, cy: 34, cz: 0, f: 900, hy: 1480 });
  ST.streetBackdrop(g, V, t, 'warm' === 'x' ? 'day' : 'day', { sunX: 300, sunY: 400 });
  const items = [];
  DP.wall(items, 1700, 11, { sp: 520, seed: 81, mood: 'day', x0: (t - t0) * 260 });
  for (let r = 0; r < 5; r++) for (let i = 0; i < 12; i++) {
    const z = [190, 290, 420, 600, 850][r], x = (t - t0) * 300 + 300 - i * (90 + r * 45) - r * 60;
    items.push({ z, draw: (g2, V2) => ST.ratAt(g2, V2, x + (t - t0) * 40, z, { dir: 1, phase: lockPh(t) + r * .0, speed: 1, t, size: 1.0, tail: 1.3, ear: C.decay(C.fluteOnsetSince(t + HIT), 10) }) });
  }
  // far behind: the Piper's legs striding
  items.push({ z: 1100, draw: (g2, V2) => ST.actor(g2, V2, CAST.piper, (t - t0) * 300 + 650, 1100, CH.piperWalkPlay(PP, { t0, yaw: Math.PI / 2 }), t, { wind: .4 }) });
  DP.flush(g, V, items);
}

// ---------------------------------------------------------------- 21: along the wall -- each rising plucked note lifts the next line of rats
function shot21(g, t, lt) {
  const t0 = b(13, 8);
  const pan = (t - t0) * 240;
  E.sky(g, 'day', W, 900, t); E.sun(g, 820, 220, 60, t);
  g.save(); g.translate(-pan * .4, 0);
  g.save(); g.translate(-200, 1150); g.scale(1.3, 1.3); let x = 0, i = 0; while (x < 1500) { const w = 190 + hash(i) * 60; E.house(g, x, 0, w, 360 + hash(i + 9) * 120, { seed: 220 + i, mood: 'day' }); x += w + 24; i++; } g.restore();
  g.restore();
  const V = new Wd.View({ cx: pan, cy: 260, cz: 0, f: 1100, hy: 1050 });
  g.save(); g.beginPath(); g.rect(0, 1150, W, 800); g.clip(); Wd.ground(g, V, { mood: 'day' }); g.restore();
  // 7 lines of rats, one per rising note; each note lifts its line onto the hind legs
  const notes = C.FL.filter(n => n.t >= t0 - .01 && n.t < b(14)).map(n => n.t);
  const plucks = (C.EV.pluck || []).filter(x => x >= t0 - .01 && x < b(14));
  const hits = (plucks.length ? plucks : notes).slice(0, 7);
  for (let r = 6; r >= 0; r--) {
    const yb = 1230 + r * 105, s = .9 + r * .14;
    const ht = hits[r] ?? (t0 + r * S16);
    const up = ease.back(clamp((t - ht - HIT) / .12)) * (1 - ease.io(clamp((t - ht - .35) / .2)));
    for (let k = 0; k < 9; k++) {
      const xx = ((k * 170 + (t - t0) * 560 + r * 60) % (W + 400)) - 200;
      RT.ratSide(g, xx, yb, { s, dir: 1, phase: lockPh(t), speed: 1 - up, t, stand: up * .9, look: up, tail: 1.2 });
    }
  }
}

// ---------------------------------------------------------------- 22: out of the gate -- a living ribbon winding down to the Weser
function shot22(g, t, lt) {
  const t0 = b(14);
  const push = 1 + .05 * ease.io(lt / 1.77);
  g.save(); g.translate(W / 2, H * .5); g.scale(push, push); g.translate(-W / 2, -H * .5);
  SETS.duskSky(g, t, { horizon: 760, sunX: 760, sunY: 640 });
  SETS.hills(g, 720, '#5a4058', 120, 4); SETS.hills(g, 800, '#4a3550', 80, 8);
  // the town wall + gate at top left
  g.save(); g.translate(210, 820); g.scale(.42, .42); E.gate(g, 0, 0, { open: 1, mood: 'dusk', lw: 9 }); g.restore();
  // the hillside
  K.shape(g, [[-60, 800], [W + 60, 760], [W + 60, H + 60], [-60, H + 60]], { fill: '#7a5a4a', lw: 5, smooth: false });
  // the river at the bottom right
  K.shape(g, [[500, H + 60], [620, 1600], [900, 1420], [W + 60, 1360], [W + 60, H + 60]], { fill: '#5a4a6a', lw: 6, tension: .4 });
  for (let i = 0; i < 12; i++) { const yy = 1450 + i * 40; K.line(g, [[700 + i * 20, yy], [1000 + i * 10, yy - 10]], 3, '#e8b48a', .5, false); }
  // the road: an S-curve from the gate down to the bank
  const P = u => [lerp(210, 640, u) + Math.sin(u * 7.5) * 230 * (1 - u * .3), lerp(830, 1540, u)];
  g.save(); g.lineCap = 'round'; g.strokeStyle = '#c4a07a'; g.lineWidth = 90; g.beginPath(); for (let u = 0; u <= 1.001; u += .02) { const [x, y] = P(u); u === 0 ? g.moveTo(x, y) : g.lineTo(x, y); } g.stroke(); g.restore();
  // the ribbon of rats flowing along the road, three abreast, scale with depth
  const head = clamp(.55 + (t - t0) * .18, 0, .98);
  for (let i = 0; i < 160; i++) {
    const u = head - .08 - i * .0055; if (u < 0) break;
    const [x, y] = P(u); const [x2, y2] = P(u + .01);
    const s = .28 + u * .45, lat = ((i % 3) - 1) * 16 * (.5 + u);
    RT.ratSide(g, x + lat * .3, y + lat, { s, dir: x2 >= x ? 1 : -1, phase: lockPh(t) + (i % 2) * .5, speed: 1, t, shadow: false });
  }
  const [hx, hy] = P(head);
  PS.drawPerson(g, CAST.piper, R.merge(PP.playPose(t), { yaw: .3 }), { x: hx, y: hy, s: .42, lw: 3, t, wind: .6 });
  g.restore();
}

// ---------------------------------------------------------------- 23: into the water -- they leap from the bank in arcs; only rings remain
function shot23(g, t, lt) {
  const t0 = b(15);
  const hz = 820;
  SETS.duskSky(g, t, { horizon: hz, sunX: 300, sunY: 640 });
  SETS.hills(g, hz, '#3a2a44', 70, 5);
  SETS.water(g, hz, H, t, { sunX: 300, top: '#a87068' });
  K.shape(g, [[-40, 1180], [180, 1150], [330, 1210], [360, 1320], [-40, 1380]], { fill: '#4d3a35', lw: 5, tension: .4 });
  // a stream of rats along the bank to the edge, leaping two per 16th
  for (let i = 0; i < 18; i++) { const u = ((i / 18) + (t - t0) * .5) % 1; RT.ratSide(g, lerp(-80, 240, u), lerp(1300, 1180, u), { s: .85, dir: 1, phase: lockPh(t), t, speed: 1, shadow: false }); }
  const jumpers = [];
  for (let i = 0; i < 44; i++) jumpers.push({ tj: t0 - .3 + i * S16 * .5, x0: 220 + hash(i) * 100, land: 420 + hash(i * 3) * 520, ly: 1250 + hash(i * 7) * 380 });
  for (const J of jumpers) E.ripple(g, J.land, J.ly, t - J.tj - .38, 1 + (J.ly - 1200) / 900, { col: '#f2d7c0', life: 1.4, a: .7 });
  for (const J of jumpers) {
    const dt = t - J.tj; if (dt < 0 || dt > .5) continue;
    const u = clamp(dt / .38);
    const x = lerp(J.x0, J.land, u), y = lerp(1170, J.ly, u) - Math.sin(Math.PI * u) * 160;
    g.save(); if (u >= 1) { g.globalAlpha = 1 - (dt - .38) / .12; }
    RT.ratSide(g, x, y, { s: .8 + (J.ly - 1200) / 900, dir: 1, phase: dt * 4, t, speed: .2, tilt: lerp(-.6, 1.0, u), shadow: false });
    g.restore();
  }
  // the Piper on his rock (right), the tenor's low notes, cloak in the river wind
  K.shape(g, [[700, 1180], [740, 1090], [860, 1070], [960, 1100], [1000, 1180]], { fill: '#3a2c30', lw: 5, tension: .3 });
  PS.drawPerson(g, CAST.piper, R.merge(PP.playPose(t, { eyes: 'narrow', glow: .4 }), { yaw: -.65 }), { x: 860, y: 1085, s: 1.25, lw: 5, t, wind: .8 });
}

// ---------------------------------------------------------------- 24: still water -- the hit, the last ring, his reflection
function shot24(g, t, lt) {
  const t0 = b(16);
  const hz = 1000;
  const pull = 1.06 - .06 * ease.io(lt / 1.77);
  g.save(); g.translate(W / 2, H * .5); g.scale(pull, pull); g.translate(-W / 2, -H * .5);
  SETS.duskSky(g, t, { horizon: hz, sunX: 540, sunY: 900 });
  SETS.hills(g, hz - 30, '#4a3550', 120, 7); SETS.hills(g, hz, '#3a2a44', 60, 2);
  SETS.water(g, hz, H + 100, t, { sunX: 540 });
  K.shape(g, [[620, 1004], [650, 960], [760, 950], [830, 975], [850, 1004]], { fill: '#2a1f28', lw: 4, tension: .3 });
  const P = R.merge(PP.playPose(t, { eyes: 'narrow' }), { yaw: -.3 });
  g.save(); g.globalAlpha = .35; g.translate(0, 2 * 960); g.scale(1, -1);
  PS.drawPerson(g, CAST.piper, P, { x: 735, y: 960, s: .5, sil: '#1a1220', lw: 3, t, shadow: false });
  g.restore();
  PS.drawPerson(g, CAST.piper, P, { x: 735, y: 960, s: .5, sil: '#1a1220', lw: 3, t, wind: .3, shadow: false });
  // the hit: one last big ring; then small rings fade; bubbles
  for (let k = 0; k < 3; k++) E.ripple(g, 540 + (k - 1) * 180, 1450 + k * 30, t - t0 - HIT - k * .06, 2.6, { col: '#ffe6cc', life: 1.8, a: .9 });
  for (const [i, x, y] of [[0, 360, 1350], [1, 760, 1520], [2, 820, 1300]]) E.ripple(g, x, y, t - t0 + .6 + i * .25, 2.0, { col: '#f2d7c0', life: 2.4, a: .5 });
  for (let i = 0; i < 7; i++) { const u = ((t - t0) * .7 + hash(i)) % 1; K.ellipse(g, 400 + hash(i * 3) * 400, 1650 - u * 220, 6, 6, { fill: null, lw: 2.5, ink: '#f2d7c0', alpha: 1 - u }); }
  g.restore();
}

module.exports = [
  { id: '18_rat_ocean_tracking', t0: b(11), mood: 'day', draw: shot18, flashIn: true },
  { id: '19_rings_overhead', t0: b(12), mood: 'warm', draw: shot19 },
  { id: '20_rats_eye', t0: b(13), mood: 'day', draw: shot20 },
  { id: '21_hopping_lines', t0: b(13, 8), mood: 'day', draw: shot21 },
  { id: '22_out_of_the_gate', t0: b(14), mood: 'dusk', grade: () => ({ mood: 'dusk', amt: .5 }), draw: shot22 },
  { id: '23_into_the_water', t0: b(15), mood: 'dusk', grade: () => ({ mood: 'dusk', amt: .55 }), draw: shot23 },
  { id: '24_still_water', t0: b(16), mood: 'dusk', grade: () => ({ mood: 'dusk', amt: .6 }), draw: shot24 },
];
