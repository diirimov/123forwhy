// Drawing kit: ink outlines, tubes, gouache texture, paper, light, particles.
const C = require('./core');
const { canvas, hash, rand, lerp, clamp } = C;

const INK = '#2a1912';
const PAL = {
  ink: INK, paper: '#ecdcb8', paperDark: '#d9c296', cream: '#f4e7c8', parch: '#e6cf9f',
  red: '#a3342b', redDark: '#6e1f1a', blood: '#9a2a25', mustard: '#cf9a2e', ochre: '#b97a33',
  olive: '#6d7438', oliveDark: '#4b5126', teal: '#2f5f5a', tealDark: '#1d3e3b', brown: '#7a4a2a',
  wood: '#8a5a32', woodDark: '#5c3a21', woodLight: '#b07e4b', stone: '#a79a85', stoneDark: '#7a6e5f',
  plaster: '#e8d8b4', beam: '#4a2f1e', roof: '#8e4a2c', roofDark: '#6b3420', sky: '#efd9a8', skyHi: '#f8e8c4',
  skin: '#f0c79f', skinShade: '#d9a47c', candle: '#ffd27a', glow: '#ffb85a', night: '#2a2233',
};

// gouache grain pattern used inside every filled shape
let GRAIN = null;
function grainTex() {
  if (GRAIN) return GRAIN;
  const n = 256, cv = canvas(n, n), x = cv.getContext('2d');
  const img = x.createImageData(n, n), r = rand(77);
  for (let i = 0; i < n * n; i++) {
    const px = i % n, py = (i / n) | 0;
    const v = 0.5 + 0.22 * (r() - 0.5) + 0.18 * Math.sin(px * 0.09 + py * 0.05) * Math.sin(py * 0.13 - px * 0.02);
    const c = clamp(v) * 255;
    img.data[i * 4] = c; img.data[i * 4 + 1] = c * 0.96; img.data[i * 4 + 2] = c * 0.9; img.data[i * 4 + 3] = 255;
  }
  x.putImageData(img, 0, 0);
  GRAIN = cv; return cv;
}

// ink-outlined filled shape. build(ctx) must only add path segments.
function shape(ctx, build, fill, o = {}) {
  const lw = o.lw === undefined ? 5 : o.lw;
  ctx.beginPath(); build(ctx);
  if (fill) {
    ctx.fillStyle = fill; ctx.fill(o.rule || 'nonzero');
    if (o.shade || o.tex !== false) {
      ctx.save(); ctx.clip(o.rule || 'nonzero');
      if (o.shade) {          // painted form shadow: gradient from one side
        const s = o.shade; // {x0,y0,x1,y1,a,c}
        const g = ctx.createLinearGradient(s.x0, s.y0, s.x1, s.y1);
        g.addColorStop(0, `rgba(${s.c || '70,35,20'},0)`); g.addColorStop(1, `rgba(${s.c || '70,35,20'},${s.a || 0.28})`);
        ctx.fillStyle = g; ctx.fillRect(-5000, -5000, 10000, 10000);
      }
      if (o.hi) {             // soft highlight blob
        const h = o.hi; const g = ctx.createRadialGradient(h.x, h.y, 0, h.x, h.y, h.r);
        g.addColorStop(0, `rgba(255,246,220,${h.a || 0.35})`); g.addColorStop(1, 'rgba(255,246,220,0)');
        ctx.fillStyle = g; ctx.fillRect(-5000, -5000, 10000, 10000);
      }
      if (o.tex !== false) {
        ctx.globalCompositeOperation = 'multiply'; ctx.globalAlpha = o.texA || 0.22;
        ctx.fillStyle = ctx.createPattern(grainTex(), 'repeat'); ctx.fillRect(-5000, -5000, 10000, 10000);
        ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over';
      }
      ctx.restore();
    }
  }
  if (lw > 0) {
    ctx.beginPath(); build(ctx);
    ctx.lineJoin = 'round'; ctx.lineCap = 'round'; ctx.lineWidth = lw; ctx.strokeStyle = o.ink || INK; ctx.stroke();
  }
}

// outlined tube along points (limbs, ropes, tails)
function tube(ctx, pts, w, color, lw = 5, cap = 'round') {
  const go = () => { ctx.beginPath(); ctx.moveTo(pts[0][0], pts[0][1]); for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1]); };
  ctx.lineJoin = 'round'; ctx.lineCap = cap;
  go(); ctx.lineWidth = w + lw * 2; ctx.strokeStyle = INK; ctx.stroke();
  go(); ctx.lineWidth = w; ctx.strokeStyle = color; ctx.stroke();
}
// smooth tube via quadratic through mid points
function tubeCurve(ctx, pts, w, color, lw = 5) {
  const go = () => {
    ctx.beginPath(); ctx.moveTo(pts[0][0], pts[0][1]);
    for (let i = 1; i < pts.length - 1; i++) { const mx = (pts[i][0] + pts[i + 1][0]) / 2, my = (pts[i][1] + pts[i + 1][1]) / 2; ctx.quadraticCurveTo(pts[i][0], pts[i][1], mx, my); }
    const l = pts[pts.length - 1]; ctx.lineTo(l[0], l[1]);
  };
  ctx.lineJoin = 'round'; ctx.lineCap = 'round';
  go(); ctx.lineWidth = w + lw * 2; ctx.strokeStyle = INK; ctx.stroke();
  go(); ctx.lineWidth = w; ctx.strokeStyle = color; ctx.stroke();
}

function line(ctx, pts, lw = 4, color = INK) {
  ctx.beginPath(); ctx.moveTo(pts[0][0], pts[0][1]); for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1]);
  ctx.lineWidth = lw; ctx.strokeStyle = color; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.stroke();
}
function curve(ctx, a, c, b, lw = 4, color = INK) {
  ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.quadraticCurveTo(c[0], c[1], b[0], b[1]);
  ctx.lineWidth = lw; ctx.strokeStyle = color; ctx.lineCap = 'round'; ctx.stroke();
}
const ell = (x, y, rx, ry, rot = 0) => c => c.ellipse(x, y, Math.max(0.1, rx), Math.max(0.1, ry), rot, 0, Math.PI * 2);
const rrect = (x, y, w, h, r) => c => { c.roundRect ? c.roundRect(x, y, w, h, r) : c.rect(x, y, w, h); };
const poly = pts => c => { c.moveTo(pts[0][0], pts[0][1]); for (let i = 1; i < pts.length; i++) c.lineTo(pts[i][0], pts[i][1]); c.closePath(); };

function contactShadow(ctx, x, y, rx, a = 0.28) {
  const g = ctx.createRadialGradient(x, y, 0, x, y, rx);
  g.addColorStop(0, `rgba(50,25,15,${a})`); g.addColorStop(1, 'rgba(50,25,15,0)');
  ctx.save(); ctx.translate(x, y); ctx.scale(1, 0.22); ctx.translate(-x, -y);
  ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x, y, rx, 0, Math.PI * 2); ctx.fill(); ctx.restore();
}

// warm glow (candles, windows) - additive
function glow(ctx, x, y, r, color = '255,190,100', a = 0.5) {
  const g = ctx.createRadialGradient(x, y, 0, x, y, r);
  g.addColorStop(0, `rgba(${color},${a})`); g.addColorStop(0.4, `rgba(${color},${a * 0.35})`); g.addColorStop(1, `rgba(${color},0)`);
  ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.fillStyle = g; ctx.fillRect(x - r, y - r, 2 * r, 2 * r); ctx.restore();
}
function rays(ctx, x, y, ang, spread, len, n, a = 0.12, seed = 1) {
  ctx.save(); ctx.globalCompositeOperation = 'lighter';
  const r = rand(seed);
  for (let i = 0; i < n; i++) {
    const a0 = ang - spread / 2 + spread * (i + r() * 0.6) / n, w = spread / n * (0.3 + r() * 0.5);
    const g = ctx.createLinearGradient(x, y, x + Math.cos(a0) * len, y + Math.sin(a0) * len);
    g.addColorStop(0, `rgba(255,220,150,${a})`); g.addColorStop(1, 'rgba(255,220,150,0)');
    ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(x, y);
    ctx.lineTo(x + Math.cos(a0 - w) * len, y + Math.sin(a0 - w) * len); ctx.lineTo(x + Math.cos(a0 + w) * len, y + Math.sin(a0 + w) * len);
    ctx.closePath(); ctx.fill();
  }
  ctx.restore();
}

// floating dust motes in light
function motes(ctx, t, x0, y0, w, h, n, seed = 3, a = 0.5) {
  ctx.save(); ctx.globalCompositeOperation = 'lighter';
  for (let i = 0; i < n; i++) {
    const px = x0 + ((hash(i * 3 + seed) * 0.5 + 0.5) * w + Math.sin(t * 0.6 + i) * 20 + t * 8) % w;
    const py = y0 + ((hash(i * 7 + seed) * 0.5 + 0.5) * h - t * 14 * (0.5 + 0.5 * hash(i))) % h;
    const yy = py < y0 ? py + h : py;
    const s = 1.5 + 2.5 * (hash(i * 11) * 0.5 + 0.5);
    ctx.fillStyle = `rgba(255,230,180,${a * (0.4 + 0.6 * Math.abs(Math.sin(t * 1.3 + i)))})`;
    ctx.beginPath(); ctx.arc(px, yy, s, 0, Math.PI * 2); ctx.fill();
  }
  ctx.restore();
}

// ---- paper & grain (post) ----
function makePaper(w, h, seed = 5) {
  const cv = canvas(w, h), x = cv.getContext('2d');
  const img = x.createImageData(w, h), d = img.data;
  const sm = 96, gw = Math.ceil(w / sm) + 2, gh = Math.ceil(h / sm) + 2, r = rand(seed);
  const grid = Array.from({ length: gw * gh }, () => r());
  const g2 = Array.from({ length: gw * gh * 9 }, () => r());
  const bil = (arr, gwid, X, Y) => { const i = Math.floor(X), j = Math.floor(Y), fx = X - i, fy = Y - j; const a = arr[j * gwid + i], b = arr[j * gwid + i + 1], c = arr[(j + 1) * gwid + i], e = arr[(j + 1) * gwid + i + 1]; const ux = fx * fx * (3 - 2 * fx), uy = fy * fy * (3 - 2 * fy); return a * (1 - ux) * (1 - uy) + b * ux * (1 - uy) + c * (1 - ux) * uy + e * ux * uy; };
  for (let py = 0; py < h; py++) for (let px = 0; px < w; px++) {
    const blot = bil(grid, gw, px / sm, py / sm), fine = bil(g2, gw * 3, px / 32, py / 32);
    const fib = Math.sin(px * 0.8 + Math.sin(py * 0.05) * 6) * 0.5 + 0.5;
    const v = 0.55 + (blot - 0.5) * 0.5 + (fine - 0.5) * 0.25 + (r() - 0.5) * 0.18 + (fib - 0.5) * 0.04;
    const i = (py * w + px) * 4, c = clamp(v) * 255;
    d[i] = c; d[i + 1] = c; d[i + 2] = c; d[i + 3] = 255;
  }
  x.putImageData(img, 0, 0);
  return cv;
}
function makeGrain(w, h, seed) {
  const cv = canvas(w, h), x = cv.getContext('2d'), img = x.createImageData(w, h), r = rand(seed);
  for (let i = 0; i < w * h; i++) { const v = 128 + (r() - 0.5) * 70; img.data[i * 4] = v; img.data[i * 4 + 1] = v; img.data[i * 4 + 2] = v; img.data[i * 4 + 3] = 255; }
  x.putImageData(img, 0, 0); return cv;
}

// sparkles / stars (comic accents)
function star(ctx, x, y, r, rot = 0, fill = '#ffe9a0', lw = 4) {
  shape(ctx, c => { for (let i = 0; i < 10; i++) { const a = rot + i * Math.PI / 5 - Math.PI / 2, rr = i % 2 ? r * 0.42 : r; c[i ? 'lineTo' : 'moveTo'](x + Math.cos(a) * rr, y + Math.sin(a) * rr); } c.closePath(); }, fill, { lw, tex: false });
}
function sparkle(ctx, x, y, r, a = 1) {
  ctx.save(); ctx.globalAlpha = a; ctx.fillStyle = '#fff7d6';
  ctx.beginPath(); ctx.moveTo(x, y - r); ctx.quadraticCurveTo(x, y, x + r, y); ctx.quadraticCurveTo(x, y, x, y + r); ctx.quadraticCurveTo(x, y, x - r, y); ctx.quadraticCurveTo(x, y, x, y - r); ctx.fill();
  ctx.restore();
}
// speed lines / action lines radiating
function speedLines(ctx, cx, cy, n, r0, r1, a, seed = 1, color = '42,25,18', lw = 6) {
  ctx.save(); const r = rand(seed);
  for (let i = 0; i < n; i++) {
    const an = r() * Math.PI * 2, rr0 = r0 * (0.8 + r() * 0.4);
    ctx.strokeStyle = `rgba(${color},${a * (0.5 + r() * 0.5)})`; ctx.lineWidth = lw * (0.4 + r());
    ctx.beginPath(); ctx.moveTo(cx + Math.cos(an) * rr0, cy + Math.sin(an) * rr0); ctx.lineTo(cx + Math.cos(an) * r1, cy + Math.sin(an) * r1); ctx.stroke();
  }
  ctx.restore();
}

module.exports = { INK, PAL, shape, tube, tubeCurve, line, curve, ell, rrect, poly, contactShadow, glow, rays, motes, makePaper, makeGrain, grainTex, star, sparkle, speedLines };
