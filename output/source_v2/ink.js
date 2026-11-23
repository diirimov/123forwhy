// ink: hand-drawn rendering of screen-space shapes (cel colour or graphite pencil)
const C = require('./core');
const { clamp, lerp, noise, hash, W, H } = C;

const ST = {
  mode: 'color', frame: 0, toLight: [-0.55, -0.83], ink: '#1b1216', inkW: 3, boil: .7,
  shadeMix: .38, shadowTint: '#2a2350', hiTint: '#fff6e8', rim: null, // rim: {color, dir:[x,y], w}
  paper: '#f4efe3', graphite: '#34323a', pencilW: 1.5, global: 1,
};
// ---------- colour ----------
function hex(c) { if (c[0] !== '#') return [128, 128, 128]; c = c.slice(1); return [parseInt(c.slice(0, 2), 16), parseInt(c.slice(2, 4), 16), parseInt(c.slice(4, 6), 16)]; }
function toHex(a) { return '#' + a.map(x => Math.round(clamp(x, 0, 255)).toString(16).padStart(2, '0')).join(''); }
function mix(a, b, t) { const A = hex(a), B = hex(b); return toHex([0, 1, 2].map(i => lerp(A[i], B[i], t))); }
function mult(a, b) { const A = hex(a), B = hex(b); return toHex([0, 1, 2].map(i => A[i] * B[i] / 255)); }
function rgba(c, a) { const A = hex(c); return `rgba(${A[0]},${A[1]},${A[2]},${a})`; }
function lum(c) { const A = hex(c); return (0.299 * A[0] + 0.587 * A[1] + 0.114 * A[2]) / 255; }
function shadowOf(c, k = 1) { return mix(c, mult(c, ST.shadowTint === '#000000' ? '#000000' : mix(ST.shadowTint, '#ffffff', .25)), ST.shadeMix * 1.9 * k); }

// ---------- paths ----------
function smoothPath(g, P, closed = true, tension = .5) {
  const n = P.length; if (n < 2) return;
  if (n < 3) { g.moveTo(P[0][0], P[0][1]); g.lineTo(P[1][0], P[1][1]); return; }
  const get = i => closed ? P[(i + n) % n] : P[clamp(i, 0, n - 1)];
  g.moveTo(P[0][0], P[0][1]);
  const m = closed ? n : n - 1;
  for (let i = 0; i < m; i++) {
    const p0 = get(i - 1), p1 = get(i), p2 = get(i + 1), p3 = get(i + 2);
    const k = tension / 3;
    g.bezierCurveTo(p1[0] + (p2[0] - p0[0]) * k, p1[1] + (p2[1] - p0[1]) * k, p2[0] - (p3[0] - p1[0]) * k, p2[1] - (p3[1] - p1[1]) * k, p2[0], p2[1]);
  }
  if (closed) g.closePath();
}
function boilPts(P, seed, amt) {
  if (!amt) return P; const st = Math.floor(ST.frame / 2);
  return P.map((p, i) => [p[0] + noise(seed * 3.1 + i * .71 + st * 1.37) * amt, p[1] + noise(seed * 5.7 + i * .53 + st * 1.91 + 50) * amt]);
}
const shift = (P, v, k) => P.map(p => [p[0] + v[0] * k, p[1] + v[1] * k]);
function bbox(P) { let a = 1e9, b = 1e9, c = -1e9, d = -1e9; for (const p of P) { a = Math.min(a, p[0]); b = Math.min(b, p[1]); c = Math.max(c, p[0]); d = Math.max(d, p[1]); } return [a, b, c, d]; }

function clipOutside(g, P, smooth) { // clip region = everything except P
  g.beginPath(); g.rect(-4000, -4000, 9000, 9000); if (smooth) smoothPath(g, P, true); else poly(g, P); g.clip('evenodd');
}
function poly(g, P) { g.moveTo(P[0][0], P[0][1]); for (let i = 1; i < P.length; i++) g.lineTo(P[i][0], P[i][1]); g.closePath(); }

// ---------- hatching ----------
function hatchRect(g, bb, gap = 6.5, ang = -0.85, seed = 1, a = .55, w = 1.15) {
  const st = Math.floor(ST.frame / 2); const cx = (bb[0] + bb[2]) / 2, cy = (bb[1] + bb[3]) / 2, R = Math.hypot(bb[2] - bb[0], bb[3] - bb[1]) / 2 + 10;
  const ca = Math.cos(ang), sa = Math.sin(ang);
  g.save(); g.strokeStyle = ST.graphite; g.globalAlpha = a; g.lineWidth = w; g.lineCap = 'round'; g.beginPath();
  for (let d = -R; d < R; d += gap) {
    const j = (hash(seed * 13 + d * .7 + st) - .5) * 2.2;
    const x0 = cx + (-sa) * (d + j) + ca * -R, y0 = cy + ca * (d + j) + sa * -R;
    g.moveTo(x0, y0); g.lineTo(x0 + ca * 2 * R, y0 + sa * 2 * R);
  }
  g.stroke(); g.restore();
}

// ---------- main shape ----------
// o: {fill, lw (ink px), shade (px offset), shadow (colour), hi:[colour, px], rim:bool, smooth, seed, noInk, inkCol, alphaFill, pencilFill, hatch}
function shape(g, P0, o = {}) {
  if (!P0 || P0.length < 3) return;
  const sm = o.smooth !== false; const seed = o.seed || 1;
  const P = boilPts(P0, seed, o.boil ?? ST.boil);
  const L = ST.toLight; const sz = Math.max(4, Math.min(220, (o.shade ?? (() => { const b = bbox(P); return Math.min(b[2] - b[0], b[3] - b[1]) * .16; })())));
  const lw = (o.lw ?? ST.inkW) * ST.global;
  if (ST.mode === 'color') {
    const base = o.fill;
    if (o.noInk !== true && lw > 0) {
      g.fillStyle = o.inkCol || ST.ink; g.strokeStyle = o.inkCol || ST.ink; g.lineJoin = 'round';
      g.beginPath(); smoothOrPoly(g, shift(P, L, -lw * .55), sm); g.fill();
      g.lineWidth = lw * 1.6; g.beginPath(); smoothOrPoly(g, P, sm); g.stroke();
    }
    if (!base) return;
    g.save(); g.beginPath(); smoothOrPoly(g, P, sm); g.clip();
    const sh = o.shadow || shadowOf(base, o.shadowK ?? 1);
    g.fillStyle = sh; const bb = bbox(P); g.fillRect(bb[0] - 5, bb[1] - 5, bb[2] - bb[0] + 10, bb[3] - bb[1] + 10);
    g.fillStyle = base; g.beginPath(); smoothOrPoly(g, shift(P, L, sz), sm); g.fill();
    if (o.hi) { g.save(); clipOutside(g, shift(P, L, -o.hi[1]), sm); g.fillStyle = o.hi[0]; g.fillRect(bb[0] - 5, bb[1] - 5, bb[2] - bb[0] + 10, bb[3] - bb[1] + 10); g.restore(); }
    if (ST.rim && o.rim !== false) { const R = ST.rim; const rw = Math.min(R.w * (o.rimK ?? 1), sz * .45); g.save(); clipOutside(g, shift(P, R.dir, -rw), sm); g.fillStyle = R.color; g.globalAlpha = R.a ?? 1; g.fillRect(bb[0] - 5, bb[1] - 5, bb[2] - bb[0] + 10, bb[3] - bb[1] + 10); g.restore(); }
    if (o.after) o.after(g, P, bb);
    g.restore();
  } else { // pencil
    const v = o.fill ? lum(o.fill) : 1;
    g.save(); g.beginPath(); smoothOrPoly(g, P, sm);
    g.fillStyle = o.pencilFill || mix(ST.paper, '#c9c3b6', clamp((0.55 - v) * 0.5, 0, .35)); g.fill();
    if (o.hatch !== false && o.fill) {
      g.clip(); const bb = bbox(P);
      g.save(); clipOutside(g, shift(P, L, sz * 1.2), sm); hatchRect(g, bb, 7, -0.85, seed, .38, 1.0); g.restore();
      if (v < .3) hatchRect(g, bb, 13, -0.95, seed + 7, .16);
      if (o.after) o.after(g, P, bb);
    }
    g.restore();
    if (o.noInk !== true) pencilLine(g, P, sm, seed, true, o.pw);
  }
}
function smoothOrPoly(g, P, sm) { if (sm) smoothPath(g, P, true); else poly(g, P); }
function pencilLine(g, P, sm, seed, closed, pw) {
  g.save(); g.strokeStyle = ST.graphite; g.lineCap = 'round'; g.lineJoin = 'round';
  const st = Math.floor(ST.frame / 2);
  for (let k = 0; k < 2; k++) {
    const j = P.map((p, i) => [p[0] + noise(seed * 7 + i * .9 + st * 2.3 + k * 40) * 1.8, p[1] + noise(seed * 3 + i * .8 + st * 1.7 + k * 70) * 1.8]);
    g.globalAlpha = k ? .45 : .85; g.lineWidth = (pw || ST.pencilW) * (k ? .8 : 1.15);
    g.beginPath(); if (sm) smoothPath(g, j, closed); else { g.moveTo(j[0][0], j[0][1]); for (const p of j) g.lineTo(p[0], p[1]); if (closed) g.closePath(); }
    g.stroke();
  }
  g.restore();
}
// tapered stroke along polyline P with width w (px); taper fractions at ends
function brush(g, P0, w, o = {}) {
  if (!P0 || P0.length < 2) return;
  const P = boilPts(P0, o.seed || 3, o.boil ?? ST.boil * .6);
  if (ST.mode === 'pencil' && !o.forceInk) { pencilLine(g, P, true, o.seed || 3, false, o.pw || Math.max(1.2, w * .45)); return; }
  const n = P.length; const t0 = o.t0 ?? .35, t1 = o.t1 ?? .35;
  // resample along catmull for smoothness
  const S = [];
  for (let i = 0; i < n - 1; i++) {
    const p0 = P[Math.max(0, i - 1)], p1 = P[i], p2 = P[i + 1], p3 = P[Math.min(n - 1, i + 2)];
    for (let k = 0; k < 6; k++) { const t = k / 6, t2 = t * t, t3 = t2 * t; S.push([0, 1].map(d => .5 * ((2 * p1[d]) + (-p0[d] + p2[d]) * t + (2 * p0[d] - 5 * p1[d] + 4 * p2[d] - p3[d]) * t2 + (-p0[d] + 3 * p1[d] - 3 * p2[d] + p3[d]) * t3))); }
  }
  S.push(P[n - 1]);
  const m = S.length; const Lft = [], Rgt = [];
  for (let i = 0; i < m; i++) {
    const a = S[Math.max(0, i - 1)], b = S[Math.min(m - 1, i + 1)]; let dx = b[0] - a[0], dy = b[1] - a[1]; const l = Math.hypot(dx, dy) || 1; dx /= l; dy /= l;
    const u = i / (m - 1); let k = 1; if (u < t0) k = Math.sin(u / t0 * Math.PI / 2); if (u > 1 - t1) k = Math.min(k, Math.sin((1 - u) / t1 * Math.PI / 2));
    const ww = w * (o.min ?? .25) + w * (1 - (o.min ?? .25)) * k;
    Lft.push([S[i][0] - dy * ww / 2, S[i][1] + dx * ww / 2]); Rgt.push([S[i][0] + dy * ww / 2, S[i][1] - dx * ww / 2]);
  }
  g.save(); g.fillStyle = o.color || ST.ink; if (o.alpha != null) g.globalAlpha = o.alpha;
  g.beginPath(); poly(g, Lft.concat(Rgt.reverse())); g.fill(); g.restore();
}
// tube outline from 2D centerline with radii (px) -> closed polygon (round caps)
function tubePts(Cs, Rs, capA = true, capB = true, samples = 5) {
  const n = Cs.length; const S = [], R = [];
  for (let i = 0; i < n - 1; i++) {
    const p0 = Cs[Math.max(0, i - 1)], p1 = Cs[i], p2 = Cs[i + 1], p3 = Cs[Math.min(n - 1, i + 2)];
    for (let k = 0; k < samples; k++) {
      const t = k / samples, t2 = t * t, t3 = t2 * t;
      S.push([0, 1].map(d => .5 * ((2 * p1[d]) + (-p0[d] + p2[d]) * t + (2 * p0[d] - 5 * p1[d] + 4 * p2[d] - p3[d]) * t2 + (-p0[d] + 3 * p1[d] - 3 * p2[d] + p3[d]) * t3)));
      R.push(lerp(Rs[i], Rs[i + 1], t));
    }
  }
  S.push(Cs[n - 1]); R.push(Rs[n - 1]);
  const m = S.length, Lf = [], Rt = []; let d0 = [1, 0], d1 = [1, 0];
  for (let i = 0; i < m; i++) {
    const a = S[Math.max(0, i - 1)], b = S[Math.min(m - 1, i + 1)]; let dx = b[0] - a[0], dy = b[1] - a[1]; const l = Math.hypot(dx, dy) || 1; dx /= l; dy /= l;
    if (i === 0) d0 = [dx, dy]; if (i === m - 1) d1 = [dx, dy];
    Lf.push([S[i][0] - dy * R[i], S[i][1] + dx * R[i]]); Rt.push([S[i][0] + dy * R[i], S[i][1] - dx * R[i]]);
  }
  const out = [];
  if (capA) { const c = S[0], r = R[0], a0 = Math.atan2(d0[1], d0[0]); for (let k = 1; k < 6; k++) { const a = a0 - Math.PI / 2 - k / 6 * Math.PI; out.push([c[0] + Math.cos(a) * r, c[1] + Math.sin(a) * r]); } }
  out.push(...Lf);
  if (capB) { const c = S[m - 1], r = R[m - 1], a0 = Math.atan2(d1[1], d1[0]); for (let k = 1; k < 6; k++) { const a = a0 + Math.PI / 2 - k / 6 * Math.PI; out.push([c[0] + Math.cos(a) * r, c[1] + Math.sin(a) * r]); } }
  out.push(...Rt.reverse());
  return out;
}
function ellipsePts(cx, cy, rx, ry, rot = 0, n = 24) { const P = []; for (let i = 0; i < n; i++) { const a = i / n * Math.PI * 2; const x = Math.cos(a) * rx, y = Math.sin(a) * ry; P.push([cx + x * Math.cos(rot) - y * Math.sin(rot), cy + x * Math.sin(rot) + y * Math.cos(rot)]); } return P; }

// ---------- painterly helpers ----------
function vgrad(g, x, y, w, h, stops) { const gr = g.createLinearGradient(0, y, 0, y + h); stops.forEach(([o, c]) => gr.addColorStop(o, c)); g.fillStyle = gr; g.fillRect(x, y, w, h); }
function glow(g, x, y, r, col, a = 1, mode = 'lighter') {
  g.save(); if (mode) g.globalCompositeOperation = mode; const gr = g.createRadialGradient(x, y, 0, x, y, r);
  gr.addColorStop(0, rgba(col, a)); gr.addColorStop(.35, rgba(col, a * .45)); gr.addColorStop(1, rgba(col, 0)); g.fillStyle = gr; g.fillRect(x - r, y - r, r * 2, r * 2); g.restore();
}
let GRAIN = null;
function grain(g, a = .07, seed = 0) {
  if (!GRAIN) { GRAIN = []; for (let k = 0; k < 4; k++) { const c = C.createCanvas(540, 960); const x = c.getContext('2d'); const id = x.createImageData(540, 960); const r = C.rng(k + 5); for (let i = 0; i < id.data.length; i += 4) { const v = 128 + (r() - .5) * 120; id.data[i] = id.data[i + 1] = id.data[i + 2] = v; id.data[i + 3] = 255; } x.putImageData(id, 0, 0); GRAIN.push(c); } }
  g.save(); g.globalCompositeOperation = 'overlay'; g.globalAlpha = a; g.drawImage(GRAIN[Math.floor(ST.frame / 2) % 4], 0, 0, W, H); g.restore();
}
function vignette(g, k = .5, col = '0,0,0', r0 = .3) {
  const r = g.createRadialGradient(W / 2, H * .47, H * r0, W / 2, H * .5, H * .8);
  r.addColorStop(0, `rgba(${col},0)`); r.addColorStop(1, `rgba(${col},${k})`); g.fillStyle = r; g.fillRect(0, 0, W, H);
}
// blurred copy of a canvas region (cheap multi-step downsample)
function blurCanvas(src, amt) {
  let c = src; let w = src.width, h = src.height; const steps = Math.max(1, Math.round(Math.log2(amt)));
  for (let i = 0; i < steps; i++) { const nw = Math.max(2, w >> 1), nh = Math.max(2, h >> 1); const n = C.createCanvas(nw, nh); const x = n.getContext('2d'); x.imageSmoothingQuality = 'high'; x.drawImage(c, 0, 0, nw, nh); c = n; w = nw; h = nh; }
  const out = C.createCanvas(src.width, src.height); const x = out.getContext('2d'); x.imageSmoothingQuality = 'high'; x.drawImage(c, 0, 0, src.width, src.height); return out;
}

module.exports = { ST, hex, toHex, mix, mult, rgba, lum, shadowOf, smoothPath, poly, boilPts, shift, bbox, clipOutside, hatchRect, shape, brush, pencilLine, tubePts, ellipsePts, vgrad, glow, grain, vignette, blurCanvas };
