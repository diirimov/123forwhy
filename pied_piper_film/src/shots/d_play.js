// 12-14: the first melody -- rats freeze, turn, rise, and dance around the Piper
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
const { barT: b, clamp, lerp, ease, BEAT, BAR, S16, HIT, W, H, TAU, hash, EV } = C;

const earAt = t => C.decay(C.fluteOnsetSince(t + HIT), 10);

// ---------------------------------------------------------------- 12: street level -- the rats freeze, ears twitch, heads turn
function shot12(g, t, lt) {
  const t0 = b(11), freeze = b(11, 3) + HIT, turn = b(11, 12) + HIT;
  const V = new Wd.View({ cx: lerp(-20, 20, ease.io(lt / 1.77)), cy: 62, cz: lerp(0, 50, ease.io(lt / 1.77)), f: 1000, hy: 1240 });
  // background (out of focus): street + the Piper playing far away
  PO.blurred(g, 6, (g2) => {
    ST.streetBackdrop(g2, V, t, 'day', { sunX: 830 });
    const items = Wd.streetItems({ mood: 'day', seed: 52, half: 900, z0: 1500 });
    items.push({ z: 2300, draw: (g3, V2) => ST.actor(g3, V2, CAST.piper, 0, 2300, tt => R.merge(PP.playPose(tt), { yaw: 0 }), t, { occlude: false }) });
    Wd.drawItems(g2, V, items);
  });
  // rows of rats: scurrying until the second note, then frozen mid-step
  const rows = [[330, 4], [430, 5], [560, 6], [720, 7], [900, 9], [1120, 10], [1400, 12]];
  const items = [];
  rows.forEach(([z, n], ri) => {
    for (let i = 0; i < n; i++) {
      const id = ri * 20 + i;
      const dir = (ri + i) % 2 ? 1 : -1;
      const sp = 260 + hash(id) * 200;
      const tm = Math.min(t, freeze);
      const span = 2200 * z / 1000;
      const x = ((-span / 2 + (i + .5) * span / n + dir * (tm - t0) * sp + hash(id * 3) * 120) % span + span * 1.5) % span - span / 2;
      const looking = ease.back(clamp((t - turn - hash(id) * .0) / .1));
      const ear = t > freeze ? earAt(t) : 0;
      items.push({ z, draw: (g2, V2) => ST.ratAt(g2, V2, x, z, { dir, phase: (tm - t0) * sp / 120, speed: t < freeze ? 1 : 0, t, ear, look: looking, eyeGlow: looking > .5, size: 1.2, tail: t < freeze ? 1 : .3 }) });
    }
  });
  Wd.drawItems(g, V, items);
}

// ---------------------------------------------------------------- 13: they rise onto their hind legs and sway in time
function shot13(g, t, lt) {
  const t0 = b(12), s1 = t0 + HIT, s2 = b(12, 3) + HIT;
  const V = new Wd.View({ cx: lerp(60, 0, ease.io(lt / 1.77)), cy: 150, cz: 0, f: 1100, hy: 1150 });
  ST.streetBackdrop(g, V, t, 'day', { sunX: 180 });
  const items = Wd.streetItems({ mood: 'day', seed: 61, half: 1000, z0: 2000 });
  for (let r = 0; r < 7; r++) for (let c = 0; c < 7; c++) {
    const z = 520 + r * 160, x = -60 + c * 150 + (r % 2) * 75 + hash(r * 9 + c) * 30;
    const stand = ease.back(clamp((t - (r < 4 ? s1 : s2)) / .14));
    const n = C.beatIndex(t), ph = C.beatPhase(t);
    const sway = Math.sin(TAU * (t / (2 * BEAT))) * .14 * stand;
    const headT = Math.sin(Math.PI * clamp(C.fluteOnsetSince(t) * 6)) * .2;
    items.push({ z, draw: (g2, V2) => ST.ratAt(g2, V2, x, z, { dir: -1, stand, speed: 0, t, tilt: sway, headTilt: -headT * stand, ear: earAt(t), size: 1.15, tail: .4 }) });
  }
  // the Piper, foreground left, seen from behind, playing
  items.push({ z: 760, draw: (g2, V2) => ST.actor(g2, V2, CAST.piper, -250, 760, tt => R.merge(PP.playPose(tt), { yaw: Math.PI - 1.05 }), t, { wind: .2 }) });
  Wd.drawItems(g, V, items);
}

// ---------------------------------------------------------------- 14: overhead -- rings of rats orbit the walking Piper, pulsing on the beat
function shot14(g, t, lt) {
  const t0 = b(13);
  const walkV = 70;                                  // px/s upward
  const py = -(t - t0) * walkV;
  const rot = lerp(-.08, .1, ease.io(lt / 1.77));
  const zoom = lerp(1.05, 1.2, ease.io(lt / 1.77));
  g.save();
  g.translate(W / 2, H * .5); g.rotate(rot); g.scale(zoom, zoom); g.translate(-W / 2, -H * .5 - py);
  TD.cobblesTop(g, -500, py - 1500, W + 500, py + H + 1500);
  TD.roofsTop(g, -40, py - 1600, py + H + 1600, -1, { seed: 3 }); TD.roofsTop(g, W + 40, py - 1600, py + H + 1600, 1, { seed: 7 });
  const cx = W / 2, cy = H * .5 + py;
  const kp = C.kickPulse(t, 7);
  const sync = clamp(lt / 1.4);
  // rings (alternating directions), radius pulses on the kick
  const rings = [[250, 9, 1], [380, 14, -1], [510, 19, 1]];
  for (const [r0, n, dir] of rings) {
    const r = r0 * (1 + .07 * kp);
    for (let i = 0; i < n; i++) {
      const a = i / n * TAU + dir * (t - t0) * (.9 - r0 / 1200) + (1 - sync) * hash(i + r0) * 1.5;
      const x = cx + Math.cos(a) * r, y = cy + Math.sin(a) * r * .95;
      RT.ratTop(g, x, y, a + dir * Math.PI / 2, { s: 1.05, phase: (t - t0) * 4 + (1 - sync) * hash(i * 3), t, speed: 1 });
    }
  }
  // the stream following behind (below), a sine wave tightening into lockstep
  for (let i = 0; i < 70; i++) {
    const d = 560 + i * 34;
    const lat = Math.sin(d * .012 - (t - t0) * 4) * (120 - 60 * sync) + (hash(i) - .5) * 140 * (1 - sync) + ((i % 3) - 1) * 46;
    const x = cx + lat, y = cy + d;
    const ang = -Math.PI / 2 + Math.cos(d * .012 - (t - t0) * 4) * .35;
    RT.ratTop(g, x, y, ang, { s: 1.0, phase: (t - t0) * 4 + (i % 2) * .5 * (1 - sync), t, speed: 1 });
  }
  // the Piper from above, playing as he walks
  TD.personTop(g, cx, cy, -Math.PI / 2, { ch: CAST.piper, s: 1.55, phase: (t - t0) / (2 * BEAT), t, flute: true, armAmt: .2, armFwd: true });
  g.restore();
}

module.exports = [
  { id: '12_rats_freeze', t0: b(11), mood: 'day', draw: shot12, flashIn: true },
  { id: '13_rats_rise', t0: b(12), mood: 'day', draw: shot13 },
  { id: '14_overhead_rings', t0: b(13), mood: 'warm', draw: shot14 },
];
