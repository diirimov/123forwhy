// Core: canvas, fonts, timing (locked to the soundtrack), easing, noise, colour.
const path = require('path');
const { createCanvas, GlobalFonts } = require('@napi-rs/canvas');

const W = 1080, H = 1920, FPS = 60, DURATION = 60;
const NFRAMES = FPS * DURATION;

// ---- soundtrack grid: MEDIEVAL_MEDICINE_V3_MASTER.wav, 132 BPM, 33 bars = 60.000 s ----
const BPM = 132, BEAT = 60 / BPM, BAR = 4 * BEAT, S16 = BEAT / 4, SWING = 0.54;
function bt(bar, step = 0) {           // exact time of a 16th step (same swing as the music)
  const pair = Math.floor(step / 2), r = step - 2 * pair;
  const frac = r <= 1 ? r * SWING : SWING + (r - 1) * (1 - SWING);
  return bar * BAR + (pair + frac) * 2 * S16;
}

// ---- fonts ----
const FONT_DIR = path.join(__dirname, '..', 'node_modules', '@expo-google-fonts');
const reg = (f, name) => GlobalFonts.registerFromPath(path.join(FONT_DIR, f), name);
reg('archivo-black/400Regular/ArchivoBlack_400Regular.ttf', 'Archivo Black');
reg('unifrakturmaguntia/400Regular/UnifrakturMaguntia_400Regular.ttf', 'Unifraktur');
reg('im-fell-english-sc/400Regular/IMFellEnglishSC_400Regular.ttf', 'IM Fell SC');
reg('cinzel/900Black/Cinzel_900Black.ttf', 'Cinzel Black');
reg('cinzel/700Bold/Cinzel_700Bold.ttf', 'Cinzel Bold');
reg('luckiest-guy/400Regular/LuckiestGuy_400Regular.ttf', 'Luckiest Guy');

// ---- maths ----
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, t) => a + (b - a) * t;
const seg = (t, a, b) => clamp((t - a) / (b - a));
const smooth = t => { t = clamp(t); return t * t * (3 - 2 * t); };
const smoother = t => { t = clamp(t); return t * t * t * (t * (t * 6 - 15) + 10); };
const outQ = t => { t = clamp(t); return 1 - (1 - t) * (1 - t); };
const inQ = t => { t = clamp(t); return t * t; };
const outC = t => { t = clamp(t); return 1 - Math.pow(1 - t, 3); };
const inC = t => { t = clamp(t); return t * t * t; };
const outBack = (t, s = 1.70158) => { t = clamp(t) - 1; return t * t * ((s + 1) * t + s) + 1; };
const outElastic = t => { t = clamp(t); if (t === 0 || t === 1) return t; return Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * (2 * Math.PI / 3)) + 1; };
// damped spring 0 -> 1 with overshoot (for snappy poses)
const spring = (t, f = 14, d = 7) => t <= 0 ? 0 : 1 - Math.exp(-d * t) * Math.cos(f * t);
// decaying kick: sign flip shake, decays over ~n frames
const kick = (t, t0, amp, frames = 9) => {
  const k = (t - t0) * FPS; if (k < 0 || k > frames) return 0;
  return amp * (1 - k / frames) * (Math.floor(k) % 2 ? -1 : 1);
};
const pulse = (t, t0, len) => { const u = (t - t0) / len; return u < 0 || u > 1 ? 0 : Math.sin(Math.PI * u); };
const D2R = Math.PI / 180;

// deterministic randomness
function hash(n) { n = (n << 13) ^ n; return 1 - ((n * (n * n * 15731 + 789221) + 1376312589) & 0x7fffffff) / 1073741824; }
function rand(seed) { let s = seed >>> 0 || 1; return () => { s ^= s << 13; s >>>= 0; s ^= s >> 17; s ^= s << 5; s >>>= 0; return s / 4294967296; }; }
function noise1(x, seed = 0) { const i = Math.floor(x), f = x - i, u = f * f * (3 - 2 * f); return lerp(hash(i + seed * 101), hash(i + 1 + seed * 101), u); }
// "boil": hand-drawn line jitter that updates 12 times a second
const boilStep = t => Math.floor(t * 12);
function boil(t, seed, amp = 0.8) { const s = boilStep(t); return [hash(s * 7 + seed * 131) * amp, hash(s * 13 + seed * 71 + 5) * amp]; }

// ---- colour ----
function hex(c) { c = c.replace('#', ''); return [parseInt(c.slice(0, 2), 16), parseInt(c.slice(2, 4), 16), parseInt(c.slice(4, 6), 16)]; }
function rgb(a, alpha = 1) { return alpha >= 1 ? `rgb(${a[0] | 0},${a[1] | 0},${a[2] | 0})` : `rgba(${a[0] | 0},${a[1] | 0},${a[2] | 0},${alpha})`; }
function mix(c1, c2, t) { const a = hex(c1), b = hex(c2); return rgb([lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t)]); }
function mixh(c1, c2, t) { const a = hex(c1), b = hex(c2); const r = [lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t)].map(v => Math.round(v).toString(16).padStart(2, '0')); return '#' + r.join(''); }
const shadeC = (c, k) => mixh(c, k < 0 ? '#2a1610' : '#fff6e0', Math.abs(k));

const canvas = (w = W, h = H) => createCanvas(Math.ceil(w), Math.ceil(h));

module.exports = {
  W, H, FPS, DURATION, NFRAMES, BPM, BEAT, BAR, S16, bt,
  clamp, lerp, seg, smooth, smoother, outQ, inQ, outC, inC, outBack, outElastic, spring, kick, pulse, D2R,
  hash, rand, noise1, boil, boilStep, hex, rgb, mix, mixh, shadeC, canvas,
};
