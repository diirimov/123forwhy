// ===================================================================== core.js
// Canvas, music clock, easing/keyframes, seeded noise, paint helpers, textures.
'use strict';
const W = 1080, H = 1920, FPS = 60;
const BPM = 150, SPB = 60 / BPM, BAR = 4 * SPB, DUR = 65.0;
const INK = '#24160f';
const cv = document.getElementById('cv');
const ctx = cv.getContext('2d');

// ------------------------------------------------------------------ math
const PI = Math.PI, TAU = 2 * Math.PI;
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const lerp = (a, b, k) => a + (b - a) * k;
const inv = (a, b, v) => clamp((v - a) / (b - a));
const sm = k => k * k * (3 - 2 * k);
const E = {
  lin: k => k,
  io: k => sm(clamp(k)),
  io2: k => { k = clamp(k); return k < .5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2; },
  out: k => 1 - Math.pow(1 - clamp(k), 3),
  in: k => Math.pow(clamp(k), 3),
  back: k => { k = clamp(k); const c = 1.9; return 1 + (c + 1) * Math.pow(k - 1, 3) + c * Math.pow(k - 1, 2); },
  inback: k => { k = clamp(k); const c = 1.7; return (c + 1) * k * k * k - c * k * k; },
  el: k => { k = clamp(k); return k === 0 || k === 1 ? k : Math.pow(2, -9 * k) * Math.sin((k * 10 - .75) * TAU / 3) + 1; },
  bounce: k => { k = clamp(k); const n = 7.5625, d = 2.75;
    if (k < 1 / d) return n * k * k; if (k < 2 / d) return n * (k -= 1.5 / d) * k + .75;
    if (k < 2.5 / d) return n * (k -= 2.25 / d) * k + .9375; return n * (k -= 2.625 / d) * k + .984375; },
};
// keyframes: key(t, [[t0,v0],[t1,v1,ease],...])  values can be numbers or arrays
function key(t, ks) {
  if (t <= ks[0][0]) return ks[0][1];
  for (let i = 1; i < ks.length; i++) {
    if (t <= ks[i][0]) {
      const [ta, va] = ks[i - 1], [tb, vb, e] = ks[i];
      const k = (E[e || 'io'])((t - ta) / (tb - ta));
      if (Array.isArray(va)) return va.map((x, j) => lerp(x, vb[j], k));
      return lerp(va, vb, k);
    }
  }
  return ks[ks.length - 1][1];
}
// exponential hit envelope after the most recent hit time
function hit(t, times, dec = 0.18) {
  let v = 0;
  for (const h of times) if (t >= h) v = Math.max(v, Math.exp(-(t - h) / dec));
  return v;
}
// squash-stretch bounce envelope: positive spike then damped wobble
function wob(t, t0, dec = .25, f = 9) { if (t < t0) return 0; const u = t - t0; return Math.exp(-u / dec) * Math.cos(u * f * TAU / 2 * 0.5 * 2); }
const beat = t => t / SPB;
const bphase = t => (t / SPB) % 1;

// seeded RNG + value noise
function rng(seed) { let a = seed >>> 0; return () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
const _nr = rng(99); const _np = Array.from({ length: 512 }, () => _nr());
function noise(x) { const i = Math.floor(x), f = x - i, a = _np[i & 511], b = _np[(i + 1) & 511]; return lerp(a, b, sm(f)) * 2 - 1; }
function fbm(x, o = 3) { let v = 0, a = .5, f = 1; for (let i = 0; i < o; i++) { v += a * noise(x * f + i * 37.1); a *= .5; f *= 2; } return v; }

// ------------------------------------------------------------------ canvas helpers
function mk(w, h) { const c = document.createElement('canvas'); c.width = w; c.height = h; return { c, x: c.getContext('2d') }; }
function lg(c, x0, y0, x1, y1, stops) { const g = c.createLinearGradient(x0, y0, x1, y1); stops.forEach(([o, col]) => g.addColorStop(o, col)); return g; }
function rg(c, x, y, r0, r1, stops, x1, y1) { const g = c.createRadialGradient(x, y, r0, x1 ?? x, y1 ?? y, r1); stops.forEach(([o, col]) => g.addColorStop(o, col)); return g; }
function hex2rgb(h) { const n = parseInt(h.slice(1), 16); return [n >> 16 & 255, n >> 8 & 255, n & 255]; }
function rgba(h, a) { const [r, g, b] = hex2rgb(h); return `rgba(${r},${g},${b},${a})`; }
function mix(h1, h2, k) { const a = hex2rgb(h1), b = hex2rgb(h2); return '#' + a.map((v, i) => Math.round(lerp(v, b[i], k)).toString(16).padStart(2, '0')).join(''); }
const shade = (h, k) => mix(h, '#0d0610', k);      // darker, slightly purple shadow
const tint = (h, k) => mix(h, '#fff4dc', k);       // warm highlight
// smooth closed/open path through points (Catmull-Rom -> Bezier)
function spline(c, pts, closed = true, ten = .5) {
  const n = pts.length; if (n < 2) return;
  c.moveTo(pts[0][0], pts[0][1]);
  const P = i => closed ? pts[(i + n) % n] : pts[clamp(i, 0, n - 1)];
  const last = closed ? n : n - 1;
  for (let i = 0; i < last; i++) {
    const p0 = P(i - 1), p1 = P(i), p2 = P(i + 1), p3 = P(i + 2);
    c.bezierCurveTo(p1[0] + (p2[0] - p0[0]) * ten / 3, p1[1] + (p2[1] - p0[1]) * ten / 3,
      p2[0] - (p3[0] - p1[0]) * ten / 3, p2[1] - (p3[1] - p1[1]) * ten / 3, p2[0], p2[1]);
  }
  if (closed) c.closePath();
}
function blob(c, pts, fill, lw = 0, stroke = INK, ten = .5) {
  c.beginPath(); spline(c, pts, true, ten);
  if (fill) { c.fillStyle = fill; c.fill(); }
  if (lw) { c.lineWidth = lw; c.strokeStyle = stroke; c.lineJoin = 'round'; c.stroke(); }
}
function ell(c, x, y, rx, ry, fill, lw = 0, rot = 0, stroke = INK) {
  c.beginPath(); c.ellipse(x, y, Math.abs(rx), Math.abs(ry), rot, 0, TAU);
  if (fill) { c.fillStyle = fill; c.fill(); }
  if (lw) { c.lineWidth = lw; c.strokeStyle = stroke; c.stroke(); }
}
function poly(c, pts, fill, lw = 0, stroke = INK) {
  c.beginPath(); pts.forEach((p, i) => i ? c.lineTo(p[0], p[1]) : c.moveTo(p[0], p[1])); c.closePath();
  if (fill) { c.fillStyle = fill; c.fill(); }
  if (lw) { c.lineWidth = lw; c.strokeStyle = stroke; c.lineJoin = 'round'; c.stroke(); }
}
function line(c, pts, lw, col = INK, cap = 'round') {
  c.beginPath(); pts.forEach((p, i) => i ? c.lineTo(p[0], p[1]) : c.moveTo(p[0], p[1]));
  c.lineWidth = lw; c.strokeStyle = col; c.lineCap = cap; c.lineJoin = 'round'; c.stroke();
}
function curve(c, pts, lw, col = INK) { c.beginPath(); spline(c, pts, false); c.lineWidth = lw; c.strokeStyle = col; c.lineCap = 'round'; c.stroke(); }
function rrect(c, x, y, w, h, r, fill, lw = 0, stroke = INK) {
  c.beginPath(); c.roundRect(x, y, w, h, r);
  if (fill) { c.fillStyle = fill; c.fill(); } if (lw) { c.lineWidth = lw; c.strokeStyle = stroke; c.stroke(); }
}
// draw with a shading clip: fill a gradient wash inside the current path shape
function withClip(c, pathFn, drawFn) { c.save(); c.beginPath(); pathFn(c); c.clip(); drawFn(c); c.restore(); }

// ------------------------------------------------------------------ textures (built once)
let GRAIN = null, PAPER = null;
function buildTextures() {
  const g = mk(512, 512), d = g.x.createImageData(512, 512), r = rng(7);
  for (let i = 0; i < d.data.length; i += 4) { const v = 128 + (r() - .5) * 70; d.data[i] = d.data[i + 1] = d.data[i + 2] = v; d.data[i + 3] = 255; }
  g.x.putImageData(d, 0, 0); GRAIN = g.c;
  const p = mk(1080, 1920);   // painterly paper/brush texture
  const rr = rng(11);
  p.x.fillStyle = '#808080'; p.x.fillRect(0, 0, 1080, 1920);
  for (let i = 0; i < 2600; i++) {
    const x = rr() * 1080, y = rr() * 1920, w = 30 + rr() * 160, a = rr() * PI;
    p.x.save(); p.x.translate(x, y); p.x.rotate(a);
    p.x.fillStyle = rr() < .5 ? 'rgba(255,255,255,0.035)' : 'rgba(0,0,0,0.035)';
    p.x.beginPath(); p.x.ellipse(0, 0, w, w * (.08 + rr() * .2), 0, 0, TAU); p.x.fill(); p.x.restore();
  }
  PAPER = p.c;
}
function finishFrame(c, t, vign = .55, grain = .05) {
  // paper/brush texture (overlay), vignette, film grain
  c.save();
  c.globalCompositeOperation = 'overlay'; c.globalAlpha = .55; c.drawImage(PAPER, 0, 0);
  c.globalCompositeOperation = 'source-over'; c.globalAlpha = 1;
  c.fillStyle = rg(c, W / 2, H * .46, H * .32, H * .78, [[0, 'rgba(10,4,18,0)'], [1, `rgba(10,4,18,${vign})`]]);
  c.fillRect(0, 0, W, H);
  c.globalCompositeOperation = 'overlay'; c.globalAlpha = grain;
  const ox = (Math.floor(t * 60) * 137) % 512, oy = (Math.floor(t * 60) * 251) % 512;
  c.fillStyle = c.createPattern(GRAIN, 'repeat'); c.translate(-ox, -oy); c.fillRect(0, 0, W + 512, H + 512);
  c.restore();
}

// ------------------------------------------------------------------ particles (deterministic, stateless)
// field(seed, n, fn) -> draws n particles whose state is a pure function of t
function particles(c, t, seed, n, fn) { const r = rng(seed); for (let i = 0; i < n; i++) fn(c, t, i, r(), r(), r(), r()); }
function glow(c, x, y, r, col, a = 1) {
  c.save(); c.globalCompositeOperation = 'lighter'; c.globalAlpha = a;
  c.fillStyle = rg(c, x, y, 0, r, [[0, col], [1, 'rgba(0,0,0,0)']]); c.fillRect(x - r, y - r, 2 * r, 2 * r); c.restore();
}
