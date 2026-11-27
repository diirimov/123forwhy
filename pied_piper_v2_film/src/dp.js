// dp: the Dancing Plague staging language -- low waist-height camera, big frontal characters, a dense wall of
// stacked gables behind them, flat cobbles, blurred foreground figures. Every V2 street shot is built with it.
'use strict';
const C = require('./core');
const R = require('./rig');
const PS = require('./person');
const E = require('./env');
const Wd = require('./world');
const ST = require('./stage');
const PO = require('./post');
const K = require('./ink');
const { clamp, lerp, hash, W, H } = C;

// standard DP camera: horizon low enough that a character at z=600 fills ~45 % of the frame height
function cam(o = {}) { return new Wd.View({ cx: 0, cy: 200, cz: 0, f: 1150, hy: 1010, ...o }); }

// a wall of frontal gables at depth z, centred on x0, n houses spaced sp world units
function wall(items, z, n, o = {}) {
  const sp = o.sp ?? 640, x0 = o.x0 ?? 0, seed = o.seed ?? 1;
  for (let i = 0; i < n; i++) {
    const w = (o.w ?? 230) + hash(i * 3.3 + seed) * (o.wv ?? 80);
    const h = (o.h ?? 360) + hash(i * 1.7 + seed * 9) * (o.hv ?? 150);
    const x = x0 + (i - (n - 1) / 2) * sp + (hash(i + seed * 3) - .5) * sp * .15;
    items.push(Wd.houseItem(x, z, w, h, { seed: seed * 50 + i, mood: o.mood, lit: o.lit, litAlways: o.litAlways, allWindows: o.allWindows,
      shutter: o.shutter ? (idx) => o.shutter(i, idx, x) : null, litByShutter: o.litByShutter, doorOpen: o.doorOpen ? o.doorOpen(i, x) : 0, doorX: o.doorX }));
  }
}

// the town: sky, sun/moon, skyline, two or three gable walls, optional side houses. Returns {V, items}.
function town(g, t, o = {}) {
  const V = o.V || cam(o.cam);
  const mood = o.mood || 'day';
  ST.streetBackdrop(g, V, t, mood, { sunX: o.sunX, sunY: o.sunY, moonX: o.moonX, moonY: o.moonY, moonR: o.moonR, clouds: o.clouds, moon: o.moon, sun: o.sun, skySeed: o.skySeed });
  const items = [];
  const seed = o.seed ?? 3;
  const sh = o.shift ?? 0;
  if (o.walls !== false) {
    wall(items, o.zFar ?? 4700, o.nFar ?? 13, { sp: 600, x0: sh * .5, seed: seed + 20, mood, lit: o.lit ?? .5, h: 380, hv: 200 });
    wall(items, o.zMid ?? 3500, o.nMid ?? 9, { sp: 620, x0: 300 + sh * .7, seed: seed + 10, mood, lit: o.lit ?? .5 });
    if (o.zNear !== null) wall(items, o.zNear ?? 2550, o.nNear ?? 7, { sp: 660, x0: sh, seed, mood, lit: o.lit ?? .5, shutter: o.shutter, litByShutter: o.litByShutter, doorOpen: o.doorOpen, allWindows: o.allWindows });
  }
  if (o.sides) for (const sd of [-1, 1]) for (let i = 0; i < 3; i++) {
    const z = 1300 + i * 650; items.push(Wd.houseItem(sd * (1250 + i * 60), z, 260, 420 + hash(i + sd) * 120, { seed: seed * 7 + i + (sd > 0 ? 30 : 0), mood, lit: o.lit ?? .5 }));
  }
  if (o.well) items.push(Wd.propItem(o.well[0], o.well[1], (g2, s) => well(g2, 0, 0, { lw: 4 / s })));
  if (o.props) for (const [kind, x, z, k] of o.props) items.push(Wd.propItem(x, z, (g2, s) => prop(g2, kind, k ?? 1, 4.5 / s, t)));
  return { V, items };
}
function flush(g, V, items) { Wd.drawItems(g, V, items); }

// little props in DP shots: barrels, sacks, crates, the well, signs
function prop(g, kind, k, lw, t) {
  if (kind === 'barrel') E.barrel(g, 0, 0, 1.3 * k, { lw });
  else if (kind === 'sack') E.sack(g, 0, 0, 1.3 * k, { lw });
  else if (kind === 'crate') E.crate(g, -70 * k, 0, 140 * k, 110 * k, { lw });
  else if (kind === 'stall') E.stall(g, -260 * k, 0, 520 * k, { lw, seed: 3 });
  else if (kind === 'lamp') E.lamp(g, 0, 0, 420 * k, { lit: true, t, lw });
  else if (kind === 'torch') E.torch(g, 0, -620 * k, { t, s: 2.2 * k, lw });
}
function well(g, x, y, o = {}) {
  const lw = o.lw ?? 4;
  K.shape(g, [[x - 110, y], [x + 110, y], [x + 110, y - 120], [x - 110, y - 120]], { fill: '#9c8a70', lw, smooth: false, inner: g2 => { g2.strokeStyle = 'rgba(40,25,15,.45)'; g2.lineWidth = 3; for (let i = 0; i < 4; i++) { g2.beginPath(); g2.moveTo(x - 110, y - 30 * i); g2.lineTo(x + 110, y - 30 * i); g2.stroke(); } } });
  for (const sd of [-1, 1]) K.shape(g, [[x + sd * 100 - 10, y - 120], [x + sd * 100 + 10, y - 120], [x + sd * 100 + 10, y - 320], [x + sd * 100 - 10, y - 320]], { fill: '#5b3a24', lw, smooth: false });
  K.shape(g, [[x - 140, y - 320], [x, y - 400], [x + 140, y - 320]], { fill: '#7c4030', lw, smooth: false });
  K.line(g, [[x, y - 320], [x, y - 200]], 3, '#3a2818', 1, false);
  E.barrel(g, x, y - 170, .45, { lw: lw / .45 });
}

// DP blurred foreground figures at the frame edges (depth + framing). list: [{ch, x(screen), y, s, pose(t)}]
function foreground(g, t, list, px = 9) {
  PO.blurred(g, px, (g2) => { for (const f of list) PS.drawPerson(g2, f.ch, f.pose(t), { x: f.x, y: f.y, s: f.s, lw: 7, t, lagA: f.pose(t - .07), lagB: f.pose(t - .16) }); });
}

// actor item helper with a static world position
function actorAt(items, ch, x, z, poseFn, t, o = {}) {
  items.push({ z, draw: (g2, V2) => ST.actor(g2, V2, ch, typeof x === 'function' ? x(t) : x, z, poseFn, t, o) });
}

module.exports = { cam, wall, town, flush, prop, well, foreground, actorAt };
