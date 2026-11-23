// Core helpers: math, easing, noise, drawing pen (color / pencil-sketch modes), text.
const { GlobalFonts, createCanvas, Path2D } = require('@napi-rs/canvas');
const path = require('path');
const fd = path.join(__dirname, 'node_modules/@fontsource');
GlobalFonts.registerFromPath(path.join(fd, 'anton/files/anton-latin-400-normal.woff2'), 'Anton');
GlobalFonts.registerFromPath(path.join(fd, 'bebas-neue/files/bebas-neue-latin-400-normal.woff2'), 'Bebas');
GlobalFonts.registerFromPath('/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf', 'InterXB');
GlobalFonts.registerFromPath('/usr/share/fonts/opentype/inter/Inter-Bold.otf', 'InterB');

const W = 1080, H = 1920, FPS = 30;
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, t) => a + (b - a) * t;
const inv = (a, b, x) => clamp((x - a) / (b - a));
const ss = t => { t = clamp(t); return t * t * (3 - 2 * t); };
const sss = t => { t = clamp(t); return t * t * t * (t * (t * 6 - 15) + 10); };
const eo = t => 1 - Math.pow(1 - clamp(t), 3);
const ei = t => Math.pow(clamp(t), 3);
const eob = t => { t = clamp(t); const c = 1.7; return 1 + (c + 1) * Math.pow(t - 1, 3) + c * Math.pow(t - 1, 2); };
function rng(seed) { let s = seed >>> 0 || 1; return () => { s ^= s << 13; s >>>= 0; s ^= s >> 17; s ^= s << 5; s >>>= 0; return s / 4294967296; }; }
function hash(n) { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); }
function noise1(x) { const i = Math.floor(x), f = x - i; const u = f * f * (3 - 2 * f); return lerp(hash(i), hash(i + 1), u) * 2 - 1; }

// colour helpers
function hex(c) { c = c.replace('#', ''); return [parseInt(c.slice(0, 2), 16), parseInt(c.slice(2, 4), 16), parseInt(c.slice(4, 6), 16)]; }
function rgb(a, al = 1) { return `rgba(${a[0] | 0},${a[1] | 0},${a[2] | 0},${al})`; }
function mix(c1, c2, t) { const a = hex(c1), b = hex(c2); return '#' + [0, 1, 2].map(i => Math.round(lerp(a[i], b[i], t)).toString(16).padStart(2, '0')).join(''); }
function shade(c, k) { return k < 0 ? mix(c, '#000000', -k) : mix(c, '#ffffff', k); }
function alpha(c, a) { return rgb(hex(c), a); }

// ---------- global render state ----------
const S = { mode: 'color', frame: 0, T: 0, ink: '#17121c', paper: '#f2eee3', graphite: '#2b2a2e', tint: null, lwMul: 1 };

// Pen: draw a closed shape described by fn(g) (path commands, no begin/fill)
function shape(g, fn, color, o = {}) {
  const lw = (o.lw ?? 6) * S.lwMul;
  g.beginPath(); fn(g);
  if (S.mode === 'color') {
    if (color) { g.fillStyle = color; g.fill(); }
    if (o.shadeFn) { g.save(); g.clip(); o.shadeFn(g); g.restore(); g.beginPath(); fn(g); }
    if (o.ink !== false && lw > 0) { g.lineWidth = lw; g.strokeStyle = o.inkColor || S.ink; g.lineJoin = 'round'; g.lineCap = 'round'; g.stroke(); }
  } else {
    // pencil sketch: paper fill (slight value from colour), boiling double line, hatching
    const v = color ? lum(color) : 1;
    if (color) { g.fillStyle = o.paperFill || mix('#3a3836', S.paper, clamp(0.55 + v * 0.6)); g.fill(); }
    if (color && v < 0.42 && o.hatch !== false) { g.save(); g.clip(); hatch(g, o.hb || [-1200, -1200, 2400, 2400], v); g.restore(); g.beginPath(); fn(g); }
    if (o.ink !== false) {
      const seed = Math.floor(S.frame / 2) * 7 + (o.seed || 0);
      g.save(); g.strokeStyle = S.graphite; g.lineJoin = 'round'; g.lineCap = 'round';
      for (let k = 0; k < 2; k++) {
        g.save(); g.translate((hash(seed + k * 3) - .5) * 5, (hash(seed + k * 5 + 1) - .5) * 5);
        g.rotate((hash(seed + k * 9) - .5) * 0.006);
        g.lineWidth = Math.max(2, lw * (k ? .45 : .7)); g.globalAlpha = k ? .55 : .9;
        g.beginPath(); fn(g); g.stroke(); g.restore();
      }
      g.restore();
    }
  }
}
function lum(c) { const a = hex(c); return (0.299 * a[0] + 0.587 * a[1] + 0.114 * a[2]) / 255; }
function hatch(g, b, v) {
  const gap = 9 + v * 30; g.save(); g.strokeStyle = S.graphite; g.lineWidth = 2.2; g.globalAlpha = 0.55;
  const seed = Math.floor(S.frame / 2);
  g.beginPath();
  for (let x = b[0]; x < b[0] + b[2] + b[3]; x += gap) { const j = (hash(seed + x) - .5) * 4; g.moveTo(x + j, b[1]); g.lineTo(x - b[3] + j, b[1] + b[3]); }
  g.stroke();
  if (v < .2) { g.beginPath(); for (let x = b[0] - b[3]; x < b[0] + b[2]; x += gap * 1.3) { g.moveTo(x, b[1]); g.lineTo(x + b[3], b[1] + b[3]); } g.stroke(); }
  g.restore();
}
// open stroke (lines like mouths, brows)
function line(g, fn, lw = 5, color) {
  g.save(); g.beginPath(); fn(g); g.lineCap = 'round'; g.lineJoin = 'round';
  g.lineWidth = lw * S.lwMul; g.strokeStyle = S.mode === 'color' ? (color || S.ink) : S.graphite;
  if (S.mode !== 'color') g.globalAlpha = .9;
  g.stroke(); g.restore();
}
// limb: thick rounded segment chain drawn as outline + fill
function limb(g, pts, w, color, o = {}) {
  const lw = (o.lw ?? 6) * S.lwMul;
  const draw = (wid, col) => { g.beginPath(); g.moveTo(pts[0][0], pts[0][1]); for (let i = 1; i < pts.length; i++) g.lineTo(pts[i][0], pts[i][1]); g.lineWidth = wid; g.strokeStyle = col; g.lineCap = 'round'; g.lineJoin = 'round'; g.stroke(); };
  if (S.mode === 'color') { draw(w + lw * 2, o.inkColor || S.ink); draw(w, color); if (o.hi) { g.save(); g.globalAlpha = .18; draw(w * .35, '#ffffff'); g.restore(); } }
  else {
    const v = lum(color); draw(w + lw * 1.2, S.graphite); draw(w, mix('#3a3836', S.paper, clamp(.55 + v * .6)));
  }
}

function ellipse(g, x, y, rx, ry, r = 0) { g.ellipse(x, y, Math.abs(rx), Math.abs(ry), r, 0, Math.PI * 2); }
function rrect(g, x, y, w, h, r) { g.roundRect(x, y, w, h, r); }

// ---------- text ----------
function text(g, str, x, y, size, o = {}) {
  g.save();
  g.font = `${size}px ${o.font || 'Anton'}`; g.textAlign = o.align || 'center'; g.textBaseline = 'alphabetic';
  if (o.track) g.letterSpacing = `${o.track}px`;
  const a = o.alpha ?? 1; g.globalAlpha = a;
  if (o.shadow !== false) { g.shadowColor = 'rgba(0,0,0,0.55)'; g.shadowBlur = o.shadowBlur ?? 24; g.shadowOffsetY = 6; }
  if (o.stroke) { g.lineWidth = o.stroke; g.strokeStyle = o.strokeColor || '#000'; g.lineJoin = 'round'; g.strokeText(str, x, y); g.shadowColor = 'transparent'; }
  g.fillStyle = o.color || '#fff'; g.fillText(str, x, y);
  g.restore();
}
function measure(g, str, size, font = 'Anton', track = 0) { g.save(); g.font = `${size}px ${font}`; if (track) g.letterSpacing = `${track}px`; const w = g.measureText(str).width; g.restore(); return w; }

// vignette & grain-free film look
function vignette(g, k = .55, col = '0,0,0') {
  const r = g.createRadialGradient(W / 2, H * .48, H * .25, W / 2, H * .5, H * .78);
  r.addColorStop(0, `rgba(${col},0)`); r.addColorStop(1, `rgba(${col},${k})`);
  g.fillStyle = r; g.fillRect(0, 0, W, H);
}
function glow(g, x, y, r, col, a = 1) {
  const gr = g.createRadialGradient(x, y, 0, x, y, r);
  gr.addColorStop(0, alpha(col, a)); gr.addColorStop(.4, alpha(col, a * .35)); gr.addColorStop(1, alpha(col, 0));
  g.fillStyle = gr; g.fillRect(x - r, y - r, r * 2, r * 2);
}
function vgrad(g, x, y, w, h, stops) { const gr = g.createLinearGradient(0, y, 0, y + h); stops.forEach(([o, c]) => gr.addColorStop(o, c)); g.fillStyle = gr; g.fillRect(x, y, w, h); }

module.exports = { W, H, FPS, clamp, lerp, inv, ss, sss, eo, ei, eob, rng, hash, noise1, hex, rgb, mix, shade, alpha, S, shape, line, limb, ellipse, rrect, text, measure, vignette, glow, vgrad, hatch, lum, createCanvas, Path2D };
