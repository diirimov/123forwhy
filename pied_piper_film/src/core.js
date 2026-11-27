// core: constants, music clock (beat map), math, noise, easing
'use strict';
const path = require('path');
const fs = require('fs');

const W = 1080, H = 1920, FPS = 60;
const ROOT = path.resolve(__dirname, '..');
const BM = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/beatmap.json'), 'utf8'));
const BPM = BM.bpm, BEAT = BM.beat, BAR = BM.bar, S16 = BM.s16;
const DUR = BM.duration, NFRAMES = BM.frames;
const HIT = 0.012;   // visual lead so impacts land on the audible transient peak

// ---------------------------------------------------------------- math
const TAU = Math.PI * 2;
const clamp = (x, a = 0, b = 1) => x < a ? a : x > b ? b : x;
const lerp = (a, b, t) => a + (b - a) * t;
const inv = (a, b, x) => (x - a) / (b - a);
const ss = (a, b, x) => { const t = clamp((x - a) / (b - a)); return t * t * (3 - 2 * t); };
const mix = (a, b, t) => a.map((v, i) => v + (b[i] - v) * t);
const ease = {
  io: t => t < .5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2,
  o: t => 1 - (1 - t) * (1 - t),
  o3: t => 1 - Math.pow(1 - t, 3),
  i: t => t * t,
  i3: t => t * t * t,
  io3: t => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2,
  back: t => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); },
  elastic: t => t === 0 ? 0 : t === 1 ? 1 : Math.pow(2, -10 * t) * Math.sin((t * 10 - .75) * TAU / 3) + 1,
};
// ramp from a to b over [t0,t1] with easing
function tween(t, t0, t1, a, b, e = ease.io) { const u = clamp((t - t0) / (t1 - t0)); return a + (b - a) * e(u); }
// damped spring impulse response at time since trigger (overshoot "follow-through")
function springHit(dt, freq = 6, damp = 5) { if (dt < 0) return 0; return Math.exp(-damp * dt) * Math.sin(TAU * freq * dt); }
function decay(dt, k = 8) { return dt < 0 ? 0 : Math.exp(-k * dt); }
function pulse(dt, a = .02, r = .25) { if (dt < 0) return 0; return dt < a ? dt / a : Math.exp(-(dt - a) / r); }

// ---------------------------------------------------------------- noise / rng
function hash(n) { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453123; return s - Math.floor(s); }
function hash2(x, y) { return hash(x * 157.31 + y * 61.7); }
function noise(x) { const i = Math.floor(x), f = x - i; const u = f * f * (3 - 2 * f); return lerp(hash(i), hash(i + 1), u) * 2 - 1; }
function noise2(x, y) {
  const ix = Math.floor(x), iy = Math.floor(y), fx = x - ix, fy = y - iy;
  const u = fx * fx * (3 - 2 * fx), v = fy * fy * (3 - 2 * fy);
  const a = hash2(ix, iy), b = hash2(ix + 1, iy), c = hash2(ix, iy + 1), d = hash2(ix + 1, iy + 1);
  return lerp(lerp(a, b, u), lerp(c, d, u), v) * 2 - 1;
}
function fbm(x, y, o = 4) { let s = 0, a = .5, f = 1; for (let i = 0; i < o; i++) { s += a * noise2(x * f, y * f); f *= 2; a *= .5; } return s; }
function rng(seed) { let a = (seed * 2654435761) >>> 0 || 1; return () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }

// ---------------------------------------------------------------- music clock
const barT = (b, s = 0) => b * BAR + s * S16;
const beatPhase = t => ((t / BEAT) % 1 + 1) % 1;
const beatIndex = t => Math.floor(t / BEAT + 1e-6);
const EV = BM.events;
function lastEvent(list, t) { // time since the most recent event <= t (Infinity if none)
  let lo = 0, hi = list.length - 1, best = -1;
  while (lo <= hi) { const m = (lo + hi) >> 1; if (list[m] <= t + 1e-9) { best = m; lo = m + 1; } else hi = m - 1; }
  return best < 0 ? Infinity : t - list[best];
}
function eventsIn(list, t0, t1) { return list.filter(x => x >= t0 - 1e-6 && x < t1 - 1e-6); }
function envAt(key, t) {
  const a = BM.env[key]; const f = t * FPS; const i = Math.floor(f); const u = f - i;
  const v0 = a[clamp(i, 0, a.length - 1)], v1 = a[clamp(i + 1, 0, a.length - 1)];
  return v0 + (v1 - v0) * u;
}
// flute notes (main lead) -> currently sounding note at time t
const FL = BM.flute;
function fluteAt(t) {
  let best = null;
  for (const n of FL) { if (n.t <= t + 1e-6 && t < n.t + Math.max(n.d, 0.09)) best = n; if (n.t > t) break; }
  return best;
}
function fluteOnsetSince(t) { let last = Infinity; for (const n of FL) { if (n.t <= t) last = t - n.t; else break; } return last; }
// kick-driven pulse useful for environment "breathing"
function kickPulse(t, k = 9) { return decay(lastEvent(EV.kick, t + HIT), k); }

module.exports = {
  W, H, FPS, ROOT, BM, BPM, BEAT, BAR, S16, DUR, NFRAMES, HIT, TAU,
  clamp, lerp, inv, ss, mix, ease, tween, springHit, decay, pulse,
  hash, hash2, noise, noise2, fbm, rng,
  barT, beatPhase, beatIndex, EV, lastEvent, eventsIn, envAt, FL, fluteAt, fluteOnsetSince, kickPulse,
};
