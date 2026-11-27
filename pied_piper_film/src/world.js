// world: one-point perspective street space (the studio's stacked-gable street compositions)
'use strict';
const C = require('./core');
const K = require('./ink');
const E = require('./env');
const { clamp, lerp, TAU, hash, W, H } = C;
const { PAL, INK } = K;
const HS = 2.4;   // house-kit units -> world units (a person is ~436 world units tall)

// pinhole view. world: x lateral (right +), y up, z depth (into screen). camera at (cx, cy=height, cz)
class View {
  constructor(o = {}) { Object.assign(this, { cx: 0, cy: 260, cz: 0, f: 1100, hy: 760, roll: 0 }, o); }
  p(x, y, z) { const d = z - this.cz; const s = this.f / Math.max(d, 1); return [W / 2 + (x - this.cx) * s, this.hy + (this.cy - y) * s, s, d]; }
  lw(s) { return clamp(2.2 + 2.6 * s, 2.2, 7.5); }
}

// cobbled ground plane: rows of the studio's rounded cobbles in true perspective
function ground(g, V, o = {}) {
  const mood = o.mood;
  const base = o.base || (mood === 'night' ? '#6d7389' : mood === 'dusk' ? '#9c7f75' : PAL.cobble);
  const gap = o.gap || (mood === 'night' ? '#373b4e' : mood === 'dusk' ? '#5a4248' : '#8a7151');
  const zNear = Math.max(V.cz + 30, o.zNear || 0), zFar = o.zFar || 9000;
  const yFar = V.p(0, 0, zFar)[1];
  g.fillStyle = gap; g.fillRect(-50, yFar, W + 100, H - yFar + 50);
  const SW = o.sw || 118, SD = o.sd || 64;      // stone width / depth in world units
  // iterate rows from far to near
  const z0 = Math.ceil((V.cz + 40) / SD) * SD;
  const rows = [];
  for (let z = z0; z < zFar; z += SD) rows.push(z);
  rows.reverse();
  for (const z of rows) {
    const a = V.p(0, 0, z + SD * .92), b = V.p(0, 0, z + SD * .08);
    const y0 = a[1], y1 = b[1], rowH = y1 - y0;
    if (y1 < yFar - 2 || y0 > H + 20) continue;
    const s = b[2];
    const sw = SW * s;
    if (rowH < 1.2) { continue; }
    const rowI = Math.round(z / SD);
    const shift = (rowI % 2) * .5;
    const xw0 = V.cx - (W / 2 + 60) / s, xw1 = V.cx + (W / 2 + 60) / s;
    const i0 = Math.floor(xw0 / SW - shift), i1 = Math.ceil(xw1 / SW - shift);
    const rr = Math.min(rowH * .42, sw * .3);
    const lwS = clamp(rowH * .08, .6, 3.4);
    for (let i = i0; i <= i1; i++) {
      const xw = (i + shift) * SW;
      const k = hash(i * 13.17 + rowI * 7.31);
      const xa = W / 2 + (xw - V.cx) * s + sw * .05 + (k - .5) * sw * .08;
      g.fillStyle = K.cmix(base, k > .5 ? '#fff4de' : '#2a1a10', Math.abs(k - .5) * .2);
      g.beginPath(); g.roundRect(xa, y0, sw * .9, rowH, rr); g.fill();
      if (rowH > 3) { g.lineWidth = lwS; g.strokeStyle = K.rgba(INK, .6); g.stroke(); }
    }
  }
}

// draw a list of world items sorted far->near. item: {z, draw(g, V)}
function drawItems(g, V, items) {
  items.sort((a, b) => b.z - a.z);
  for (const it of items) { if (it.z - V.cz < 10) continue; it.draw(g, V); }
}

// helpers to create items
function houseItem(x, z, w, h, o = {}) {
  return { z, draw: (g, V) => { const [sx, sy, s0] = V.p(x, 0, z); const s = s0 * HS; if (sx + w * s < -300 || sx - w * s > W + 300) return; g.save(); g.translate(sx, sy); g.scale(s, s); E.house(g, -w / 2, 0, w, h, { ...o, lw: V.lw(s0) / s }); g.restore(); } };
}
function propItem(x, z, fn) { return { z, draw: (g, V) => { const [sx, sy, s] = V.p(x, 0, z); g.save(); g.translate(sx, sy); g.scale(s, s); fn(g, s, V); g.restore(); } }; }

// standard Hamelin street: frontal gables stacked along both sides, receding to the market church
function streetItems(o = {}) {
  const items = [];
  const half = o.half || 760;           // street half width (world units)
  const r = C.rng(o.seed || 11);
  for (const side of [-1, 1]) {
    let z = o.z0 || 600;
    let i = 0;
    while (z < (o.z1 || 7000)) {
      const w = 230 + r() * 120, h = 300 + r() * 160;
      const x = side * (half + w * HS / 2 + r() * 60);
      items.push(houseItem(x, z, w, h, { ...o.house, seed: (o.seed || 11) * 100 + side * 50 + i, mood: o.mood, lit: o.lit, shutter: o.shutter ? (idx) => o.shutter(side, i, idx) : null, doorOpen: o.doorOpen ? o.doorOpen(side, i) : 0 }));
      z += 420 + r() * 300; i++;
    }
  }
  // the far end: a cross street of houses facing us
  if (o.endWall !== false) for (let k = -3; k <= 3; k++) items.push(houseItem(k * 300 * HS + (o.endShift || 0), o.zEnd || 7600, 290, 330 + hash(k + 3) * 120, { seed: 900 + k, mood: o.mood, lit: o.lit, shutter: o.shutter ? (idx) => o.shutter(0, k + 10, idx) : null }));
  return items;
}

module.exports = { HS, View, ground, drawItems, houseItem, propItem, streetItems };
