// Core toolkit: deterministic math, easing, smooth paths, lighting helpers, post effects.
'use strict';
const W = 1080, H = 1920, FPS = 60;
const TESTS = window.TESTS = {};
const BPM = 136, BEAT = 60 / BPM, BAR = BEAT * 4, STEP = BEAT / 4;

// ---------- math ----------
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a, b, t) => a + (b - a) * t;
const inv = (a, b, x) => clamp((x - a) / (b - a));
const smooth = t => t * t * (3 - 2 * t);
const ease = {
  in2: t => t * t, out2: t => 1 - (1 - t) * (1 - t), io2: t => t < .5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2,
  in3: t => t * t * t, out3: t => 1 - Math.pow(1 - t, 3), io3: t => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2,
  out5: t => 1 - Math.pow(1 - t, 5), in5: t => Math.pow(t, 5),
  io5: t => t < .5 ? 16 * Math.pow(t, 5) : 1 - Math.pow(-2 * t + 2, 5) / 2,
  outBack: (t, s = 1.4) => 1 + (s + 1) * Math.pow(t - 1, 3) + s * Math.pow(t - 1, 2),
  expo: t => t === 1 ? 1 : 1 - Math.pow(2, -10 * t),
  sine: t => -(Math.cos(Math.PI * t) - 1) / 2,
};
// animate value between keys: [[t, v, easeFn?], ...]
function keys(t, ks) {
  if (t <= ks[0][0]) return ks[0][1];
  for (let i = 1; i < ks.length; i++) {
    if (t < ks[i][0]) {
      const [t0, v0] = ks[i - 1], [t1, v1, e] = ks[i];
      const u = (e || ease.io3)((t - t0) / (t1 - t0));
      return Array.isArray(v0) ? v0.map((x, j) => lerp(x, v1[j], u)) : lerp(v0, v1, u);
    }
  }
  return ks[ks.length - 1][1];
}
// damped impulse: sharp attack, decaying oscillation (impacts, follow-through)
function kick(t, t0, decay = 6, freq = 0) {
  if (t < t0) return 0;
  const d = t - t0;
  return Math.exp(-d * decay) * (freq ? Math.cos(d * freq * Math.PI * 2) : 1);
}
function env(t, a, b, fi = 0.25, fo = 0.25) { return Math.min(inv(a, a + fi, t), 1 - inv(b - fo, b, t)); }

// ---------- deterministic randomness / noise ----------
function mulberry(seed) { return function () { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
const hash = (n) => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
function vnoise(x) { const i = Math.floor(x), f = x - i; const u = f * f * (3 - 2 * f); return lerp(hash(i), hash(i + 1), u) * 2 - 1; }
function fbm(x, oct = 3) { let s = 0, a = 0.5, f = 1; for (let i = 0; i < oct; i++) { s += a * vnoise(x * f + i * 17.3); f *= 2.03; a *= 0.5; } return s; }
function noise2(x, y) { return vnoise(x + vnoise(y * 1.37 + 9.1) * 2.3); }

// ---------- color ----------
function rgba(hex, a = 1) { const n = parseInt(hex.slice(1), 16); return `rgba(${n >> 16 & 255},${n >> 8 & 255},${n & 255},${a})`; }
function mix(h1, h2, t) { const a = parseInt(h1.slice(1), 16), b = parseInt(h2.slice(1), 16); const c = (s) => Math.round(lerp(a >> s & 255, b >> s & 255, t)); return `rgb(${c(16)},${c(8)},${c(0)})`; }
const P = {
  black: '#07060a', char: '#121014', char2: '#1b1714', brownDk: '#24170e', bronzeDk: '#3a2414', bronze: '#7a4d27',
  bronzeLt: '#b7803f', gold: '#e0b062', hot: '#ffd99a', amber: '#e89a3c', ember: '#ff8a3a', red: '#8e2318', redDk: '#4a120c',
  ivory: '#f4ead8', stone: '#6a5f55', stoneDk: '#2e2824', stoneLt: '#a39584', sky: '#1a1820',
  // anatomy identity
  navy: '#070d18', navy2: '#0e1a2c', teal: '#1d4a5c', artery: '#d23a3e', vein: '#3d74c4', nerve: '#f1d08a', cyan: '#7fd6ff', pale: '#d8e6f2',
  skin: '#c08a66', skinDk: '#7a4a32', skinLt: '#e2b28c', hair: '#1a1210', cloth: '#d9cdb6', clothDk: '#8f8170', border: '#7a2a18',
};

// ---------- smooth paths ----------
// Catmull-Rom through points -> cubic beziers. pts: [[x,y],...]
function crPath(ctx, pts, closed = false, tension = 0.5, move = true) {
  const n = pts.length; if (n < 2) return;
  const g = (i) => closed ? pts[(i + n) % n] : pts[clamp(i, 0, n - 1)];
  if (move) ctx.moveTo(pts[0][0], pts[0][1]);
  const last = closed ? n : n - 1;
  for (let i = 0; i < last; i++) {
    const p0 = g(i - 1), p1 = g(i), p2 = g(i + 1), p3 = g(i + 2);
    const k = tension / 3 * 2;
    ctx.bezierCurveTo(p1[0] + (p2[0] - p0[0]) * k / 2, p1[1] + (p2[1] - p0[1]) * k / 2,
      p2[0] - (p3[0] - p1[0]) * k / 2, p2[1] - (p3[1] - p1[1]) * k / 2, p2[0], p2[1]);
  }
  if (closed) ctx.closePath();
}
function shape(ctx, pts, fill, closed = true) { ctx.beginPath(); crPath(ctx, pts, closed); if (fill) { ctx.fillStyle = fill; ctx.fill(); } }
// variable-width stroke (brush) along a polyline: widths per point
function brush(ctx, pts, w0, w1, color, taper = true) {
  if (pts.length < 2) return;
  const L = [], R = [];
  for (let i = 0; i < pts.length; i++) {
    const a = pts[Math.max(0, i - 1)], b = pts[Math.min(pts.length - 1, i + 1)];
    let dx = b[0] - a[0], dy = b[1] - a[1]; const d = Math.hypot(dx, dy) || 1; dx /= d; dy /= d;
    const u = i / (pts.length - 1);
    let w = lerp(w0, w1, u); if (taper) w *= Math.sin(Math.PI * clamp(u * 0.92 + 0.04)) * 0.85 + 0.15;
    L.push([pts[i][0] - dy * w / 2, pts[i][1] + dx * w / 2]); R.push([pts[i][0] + dy * w / 2, pts[i][1] - dx * w / 2]);
  }
  ctx.beginPath(); crPath(ctx, L, false); crPath(ctx, R.reverse(), false, 0.5, false); ctx.closePath();
  ctx.fillStyle = color; ctx.fill();
}
// sample points along quadratic-ish curve defined by control points (for organic strands)
function curvePts(pts, n = 24) {
  const out = [];
  for (let i = 0; i <= n; i++) {
    const t = i / n * (pts.length - 1), k = Math.min(Math.floor(t), pts.length - 2), u = t - k;
    const p0 = pts[Math.max(0, k - 1)], p1 = pts[k], p2 = pts[k + 1], p3 = pts[Math.min(pts.length - 1, k + 2)];
    const cr = (a, b, c, d) => 0.5 * ((2 * b) + (-a + c) * u + (2 * a - 5 * b + 4 * c - d) * u * u + (-a + 3 * b - 3 * c + d) * u * u * u);
    out.push([cr(p0[0], p1[0], p2[0], p3[0]), cr(p0[1], p1[1], p2[1], p3[1])]);
  }
  return out;
}

// ---------- canvases / effects ----------
function mk(w = W, h = H) { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; }
const _grain = [];
function initGrain() {
  for (let k = 0; k < 6; k++) {
    const c = mk(540, 960), g = c.getContext('2d'); const im = g.createImageData(540, 960); const r = mulberry(99 + k);
    for (let i = 0; i < im.data.length; i += 4) { const v = 128 + (r() + r() + r() - 1.5) * 70; im.data[i] = im.data[i + 1] = im.data[i + 2] = v; im.data[i + 3] = 255; }
    g.putImageData(im, 0, 0); _grain.push(c);
  }
}
function grain(ctx, frame, amt = 0.07) {
  ctx.save(); ctx.globalAlpha = amt; ctx.globalCompositeOperation = 'overlay';
  ctx.drawImage(_grain[frame % _grain.length], 0, 0, W, H); ctx.restore();
}
function vignette(ctx, s = 0.75, col = '#000') {
  const g = ctx.createRadialGradient(W / 2, H * 0.48, H * 0.18, W / 2, H * 0.5, H * 0.72);
  g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, rgba(col, s));
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
}
// bloom: blurred copy of bright content added on top
const _bloom = { c: null };
function bloom(ctx, src, amt = 0.5, radius = 28, threshold = 0.0) {
  if (!_bloom.c) { _bloom.c = mk(W / 4, H / 4); }
  const b = _bloom.c, g = b.getContext('2d');
  g.clearRect(0, 0, b.width, b.height);
  g.filter = `brightness(${1 - threshold}) contrast(${1 + threshold * 3}) blur(${radius / 4}px)`;
  g.drawImage(src, 0, 0, b.width, b.height); g.filter = 'none';
  ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.globalAlpha = amt; ctx.imageSmoothingQuality = 'high';
  ctx.drawImage(b, 0, 0, W, H); ctx.restore();
}
// radial glow
function glow(ctx, x, y, r, col, a = 1, mode = 'screen') {
  const g = ctx.createRadialGradient(x, y, 0, x, y, r);
  g.addColorStop(0, rgba(col, a)); g.addColorStop(0.35, rgba(col, a * 0.45)); g.addColorStop(1, rgba(col, 0));
  ctx.save(); ctx.globalCompositeOperation = mode; ctx.fillStyle = g; ctx.fillRect(x - r, y - r, 2 * r, 2 * r); ctx.restore();
}
function linGrad(ctx, x0, y0, x1, y1, stops) { const g = ctx.createLinearGradient(x0, y0, x1, y1); stops.forEach(([o, c]) => g.addColorStop(o, c)); return g; }
function radGrad(ctx, x, y, r0, r1, stops, x1, y1) { const g = ctx.createRadialGradient(x, y, r0, x1 ?? x, y1 ?? y, r1); stops.forEach(([o, c]) => g.addColorStop(o, c)); return g; }

// particles: closed-form drifting motes (deterministic in t)
function motes(ctx, t, n, seed, opt) {
  const o = Object.assign({ x0: 0, x1: W, y0: 0, y1: H, vy: -40, vx: 8, size: [1, 3.5], col: P.hot, a: 0.8, flick: 3, life: 4, mode: 'screen' }, opt);
  const r = mulberry(seed);
  ctx.save(); ctx.globalCompositeOperation = o.mode;
  for (let i = 0; i < n; i++) {
    const ph = r() * o.life, sx = r(), sy = r(), sz = lerp(o.size[0], o.size[1], r() ** 2), sp = 0.6 + r() * 0.8, wob = r() * 6.28;
    const tt = (t + ph) % o.life, u = tt / o.life;
    const x = lerp(o.x0, o.x1, sx) + o.vx * tt * sp + Math.sin(t * 1.3 + wob) * 14;
    let y = lerp(o.y0, o.y1, sy) + o.vy * tt * sp;
    const a = o.a * Math.sin(Math.PI * u) * (0.6 + 0.4 * Math.sin(t * o.flick + wob * 3));
    if (a <= 0.01) continue;
    ctx.globalAlpha = a; ctx.fillStyle = o.col;
    ctx.beginPath(); ctx.arc(x, y, sz, 0, 6.283); ctx.fill();
    if (sz > 2.2) { ctx.globalAlpha = a * 0.25; ctx.beginPath(); ctx.arc(x, y, sz * 3, 0, 6.283); ctx.fill(); }
  }
  ctx.restore();
}
// soft volumetric light shaft
function shaft(ctx, x0, y0, w0, x1, y1, w1, col, a) {
  ctx.save(); ctx.globalCompositeOperation = 'screen';
  const g = ctx.createLinearGradient(x0, y0, x1, y1); g.addColorStop(0, rgba(col, a)); g.addColorStop(1, rgba(col, 0));
  ctx.fillStyle = g; ctx.filter = 'blur(18px)';
  ctx.beginPath(); ctx.moveTo(x0 - w0 / 2, y0); ctx.lineTo(x0 + w0 / 2, y0); ctx.lineTo(x1 + w1 / 2, y1); ctx.lineTo(x1 - w1 / 2, y1); ctx.closePath(); ctx.fill();
  ctx.restore();
}
