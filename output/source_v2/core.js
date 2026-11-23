// core: math, easing, keys, noise, vectors, perspective camera
const { createCanvas, GlobalFonts, Path2D } = require('@napi-rs/canvas');
GlobalFonts.registerFromPath('/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf', 'CapBold');
GlobalFonts.registerFromPath('/usr/share/fonts/opentype/inter/InterDisplay-SemiBold.otf', 'CapSemi');
GlobalFonts.registerFromPath('/usr/share/fonts/opentype/inter/InterDisplay-ExtraBold.otf', 'CapXB');
GlobalFonts.registerFromPath('/usr/share/fonts/opentype/inter/Inter-Bold.otf', 'InterB');

const W = 1080, H = 1920, FPS = 30;
const PI = Math.PI, TAU = Math.PI * 2;
const clamp = (x, a = 0, b = 1) => x < a ? a : x > b ? b : x;
const lerp = (a, b, t) => a + (b - a) * t;
const inv = (a, b, x) => clamp((x - a) / (b - a));
const ss = t => { t = clamp(t); return t * t * (3 - 2 * t); };
const s5 = t => { t = clamp(t); return t * t * t * (t * (t * 6 - 15) + 10); };
const eIn = (t, p = 3) => Math.pow(clamp(t), p);
const eOut = (t, p = 3) => 1 - Math.pow(1 - clamp(t), p);
const eIO = (t, p = 3) => { t = clamp(t); return t < .5 ? Math.pow(2 * t, p) / 2 : 1 - Math.pow(2 - 2 * t, p) / 2; };
const eBack = (t, k = 1.6) => { t = clamp(t) - 1; return 1 + (k + 1) * t * t * t + k * t * t; };
// damped spring step response (overshoot settle), t in seconds
const spring = (t, f = 3, d = 6) => t <= 0 ? 0 : 1 - Math.exp(-d * t) * Math.cos(TAU * f * t);
// impulse-like settle wobble (0 -> bump -> 0)
const wob = (t, f = 4, d = 7) => t <= 0 ? 0 : Math.exp(-d * t) * Math.sin(TAU * f * t);

const EASE = { lin: t => clamp(t), ss, s5, in: eIn, out: eOut, io: eIO, back: eBack, in2: t => eIn(t, 2), out2: t => eOut(t, 2), io2: t => eIO(t, 2), out5: t => eOut(t, 5), in5: t => eIn(t, 5), io5: t => eIO(t, 5) };
// keyed interpolation: keys = [[t, value, ease?], ...]; value number or array
function key(t, keys) {
  if (t <= keys[0][0]) return keys[0][1];
  for (let i = 1; i < keys.length; i++) {
    if (t <= keys[i][0]) {
      const [t0, v0] = keys[i - 1], [t1, v1, e] = keys[i];
      const u = (EASE[e || 'io2'])((t - t0) / (t1 - t0));
      return Array.isArray(v0) ? v0.map((x, j) => lerp(x, v1[j], u)) : lerp(v0, v1, u);
    }
  }
  return keys[keys.length - 1][1];
}

function hash(n) { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); }
function hash2(a, b) { return hash(a * 157.31 + b * 13.77); }
function noise(x) { const i = Math.floor(x), f = x - i; const u = f * f * (3 - 2 * f); return lerp(hash(i), hash(i + 1), u) * 2 - 1; }
function fbm(x) { return noise(x) * .6 + noise(x * 2.1 + 9) * .3 + noise(x * 4.3 + 3) * .1; }
function rng(seed) { let s = (seed * 2654435761) >>> 0 || 1; return () => { s ^= s << 13; s >>>= 0; s ^= s >> 17; s ^= s << 5; s >>>= 0; return s / 4294967296; }; }

// vectors
const v3 = (x = 0, y = 0, z = 0) => [x, y, z];
const add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const mul = (a, k) => [a[0] * k, a[1] * k, a[2] * k];
const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const len = a => Math.hypot(a[0], a[1], a[2]);
const norm = a => { const l = len(a) || 1; return [a[0] / l, a[1] / l, a[2] / l]; };
const lerp3 = (a, b, t) => [lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t)];
const madd = (p, ...terms) => { let r = p.slice(); for (let i = 0; i < terms.length; i += 2) r = add(r, mul(terms[i], terms[i + 1])); return r; };
function rotAxis(v, ax, a) { // Rodrigues
  const k = norm(ax), c = Math.cos(a), s = Math.sin(a);
  const kv = cross(k, v), kd = dot(k, v);
  return [v[0] * c + kv[0] * s + k[0] * kd * (1 - c), v[1] * c + kv[1] * s + k[1] * kd * (1 - c), v[2] * c + kv[2] * s + k[2] * kd * (1 - c)];
}
// frame = {o, L, U, F}: local (l,u,f) -> world
function frame(o, yaw = 0, pitch = 0, roll = 0) {
  let F = [Math.sin(yaw), 0, Math.cos(yaw)], U = [0, 1, 0]; let L = cross(U, F);
  if (pitch) { F = rotAxis(F, L, pitch); U = rotAxis(U, L, pitch); }
  if (roll) { L = rotAxis(L, F, roll); U = rotAxis(U, F, roll); }
  return { o, L, U, F };
}
function fx(fr, l, u, f) { return [fr.o[0] + fr.L[0] * l + fr.U[0] * u + fr.F[0] * f, fr.o[1] + fr.L[1] * l + fr.U[1] * u + fr.F[1] * f, fr.o[2] + fr.L[2] * l + fr.U[2] * u + fr.F[2] * f]; }
function fdir(fr, l, u, f) { return [fr.L[0] * l + fr.U[0] * u + fr.F[0] * f, fr.L[1] * l + fr.U[1] * u + fr.F[1] * f, fr.L[2] * l + fr.U[2] * u + fr.F[2] * f]; }
function frot(fr, axis, a) { return { o: fr.o, L: rotAxis(fr.L, axis, a), U: rotAxis(fr.U, axis, a), F: rotAxis(fr.F, axis, a) }; }

// perspective camera
class Cam {
  constructor({ pos, look, up = [0, 1, 0], fov = 40, roll = 0, shift = [0, 0], vw = W, vh = H, F = null }) {
    this.pos = pos; this.fov = fov; this.vw = vw; this.vh = vh;
    const f = norm(sub(look, pos)); let r = norm(cross(f, up)); let u = cross(r, f);
    if (roll) { r = rotAxis(r, f, roll); u = rotAxis(u, f, roll); }
    this.f = f; this.r = r; this.u = u; this.F = F || (vh / 2) / Math.tan(fov * PI / 360); this.shift = shift;
  }
  p(p) {
    const d = sub(p, this.pos); const zc = Math.max(0.5, dot(d, this.f));
    return { x: this.vw / 2 + this.shift[0] + this.F * dot(d, this.r) / zc, y: this.vh / 2 + this.shift[1] - this.F * dot(d, this.u) / zc, z: zc, s: this.F / zc };
  }
  toCam(p) { return norm(sub(this.pos, p)); }
}

// quaternions for orientation keys: q=[w,x,y,z]
function qFromBasis(L, U, F) { // columns L,U,F as rotation of world axes x,y,z
  const m00 = L[0], m01 = U[0], m02 = F[0], m10 = L[1], m11 = U[1], m12 = F[1], m20 = L[2], m21 = U[2], m22 = F[2];
  const tr = m00 + m11 + m22; let w, x, y, z;
  if (tr > 0) { const S = Math.sqrt(tr + 1) * 2; w = .25 * S; x = (m21 - m12) / S; y = (m02 - m20) / S; z = (m10 - m01) / S; }
  else if (m00 > m11 && m00 > m22) { const S = Math.sqrt(1 + m00 - m11 - m22) * 2; w = (m21 - m12) / S; x = .25 * S; y = (m01 + m10) / S; z = (m02 + m20) / S; }
  else if (m11 > m22) { const S = Math.sqrt(1 + m11 - m00 - m22) * 2; w = (m02 - m20) / S; x = (m01 + m10) / S; y = .25 * S; z = (m12 + m21) / S; }
  else { const S = Math.sqrt(1 + m22 - m00 - m11) * 2; w = (m10 - m01) / S; x = (m02 + m20) / S; y = (m12 + m21) / S; z = .25 * S; }
  return [w, x, y, z];
}
function qSlerp(a, b, t) { let d = a[0] * b[0] + a[1] * b[1] + a[2] * b[2] + a[3] * b[3]; if (d < 0) { b = b.map(v => -v); d = -d; } if (d > .9995) { const r = a.map((v, i) => v + (b[i] - v) * t); const l = Math.hypot(...r); return r.map(v => v / l); } const th = Math.acos(d), s = Math.sin(th); const wa = Math.sin((1 - t) * th) / s, wb = Math.sin(t * th) / s; return a.map((v, i) => v * wa + b[i] * wb); }
function qRot(q, v) { const [w, x, y, z] = q; const u = [x, y, z]; const t = mul(cross(u, v), 2); return add(add(v, mul(t, w)), cross(u, t)); }
function qBasis(q) { return { L: qRot(q, [1, 0, 0]), U: qRot(q, [0, 1, 0]), F: qRot(q, [0, 0, 1]) }; }
function basisFrom(U, F) { U = norm(U); F = norm(sub(F, mul(U, dot(F, U)))); return { L: cross(U, F), U, F }; }
function keyOrient(t, keys) { // keys: [[t, {L,U,F}, ease]]
  if (t <= keys[0][0]) return keys[0][1];
  for (let i = 1; i < keys.length; i++) if (t <= keys[i][0]) { const [t0, o0] = keys[i - 1], [t1, o1, e] = keys[i]; const u = (EASE[e || 'io2'])((t - t0) / (t1 - t0)); return qBasis(qSlerp(qFromBasis(o0.L, o0.U, o0.F), qFromBasis(o1.L, o1.U, o1.F), u)); }
  return keys[keys.length - 1][1];
}
module.exports = { qFromBasis, qSlerp, qRot, qBasis, basisFrom, keyOrient, createCanvas, Path2D, W, H, FPS, PI, TAU, clamp, lerp, inv, ss, s5, eIn, eOut, eIO, eBack, spring, wob, EASE, key, hash, hash2, noise, fbm, rng, v3, add, sub, mul, dot, cross, len, norm, lerp3, madd, rotAxis, frame, fx, fdir, frot, Cam };
