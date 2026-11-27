// ink: the studio's drawing style (dark-brown ink outline, flat cel fills, soft paper shading)
'use strict';
const C = require('./core');
const { clamp, lerp } = C;

const INK = '#28170c';
const PAL = {
  ink: INK, skin: '#e8b48c', skinSh: '#c98d6b', blush: '#e88f86', white: '#f7efe0',
  coif: '#efe6d2', coifSh: '#cfc2a8', red: '#b0402b', redD: '#7e2a1d', mustard: '#cf9f45', mustardD: '#a17631',
  olive: '#75733f', oliveD: '#535129', blue: '#53719a', blueD: '#3b5374', green: '#4e7d4c', greenD: '#365a35',
  brown: '#6e4b33', brownD: '#4a3121', cream: '#e8dcbf', creamD: '#c9b994', grey: '#8a867c', greyD: '#5d5a53',
  black: '#2b2730', gold: '#e2b34a', goldD: '#a77a25', plaster: '#e3d3b3', plasterD: '#c7b391', beam: '#5a3b26',
  roof: '#8d4a32', roofD: '#6a3424', cobble: '#c0a985', cobbleD: '#9b8462', sky: '#d9cfb8',
  // Piper
  burg: '#6e1f2e', burgD: '#4b1220', pgreen: '#2f4b3a', pgreenD: '#1f3428', purple: '#4b3150', purpleD: '#33213a',
  pale: '#e7cfb6', paleSh: '#c4a68e', hair: '#2a1d1f',
  rat: '#77685d', ratD: '#544840', ratBelly: '#a39384', ratPink: '#d49a93',
};

// colour utils
function hex(c) { c = c.replace('#', ''); return [parseInt(c.slice(0, 2), 16), parseInt(c.slice(2, 4), 16), parseInt(c.slice(4, 6), 16)]; }
function toHex(a) { return '#' + a.map(x => Math.round(clamp(x, 0, 255)).toString(16).padStart(2, '0')).join(''); }
function cmix(a, b, t) { const A = hex(a), B = hex(b); return toHex(A.map((v, i) => lerp(v, B[i], t))); }
function rgba(c, a) { const A = hex(c); return `rgba(${A[0]},${A[1]},${A[2]},${a})`; }
function shade(c, k) { return k >= 0 ? cmix(c, '#fff6e6', k) : cmix(c, '#2a1810', -k); }

// ---------------------------------------------------------------- paths
function smooth(g, P, closed = true, tension = 0.5) {
  const n = P.length; if (n < 2) return;
  if (n === 2) { g.moveTo(P[0][0], P[0][1]); g.lineTo(P[1][0], P[1][1]); return; }
  const get = i => closed ? P[(i + n) % n] : P[clamp(i, 0, n - 1)];
  g.moveTo(P[0][0], P[0][1]);
  const m = closed ? n : n - 1, k = tension / 3;
  for (let i = 0; i < m; i++) {
    const p0 = get(i - 1), p1 = get(i), p2 = get(i + 1), p3 = get(i + 2);
    g.bezierCurveTo(p1[0] + (p2[0] - p0[0]) * k, p1[1] + (p2[1] - p0[1]) * k, p2[0] - (p3[0] - p1[0]) * k, p2[1] - (p3[1] - p1[1]) * k, p2[0], p2[1]);
  }
  if (closed) g.closePath();
}
function poly(g, P, closed = true) { g.moveTo(P[0][0], P[0][1]); for (let i = 1; i < P.length; i++) g.lineTo(P[i][0], P[i][1]); if (closed) g.closePath(); }

// fill + ink outline. o: {fill, lw, ink, smooth(true), closed, alpha, shadeCol, shadeDir:[dx,dy], shadeAmt}
function shape(g, P, o = {}) {
  const closed = o.closed !== false;
  g.save();
  if (o.alpha != null) g.globalAlpha *= o.alpha;
  g.beginPath(); (o.smooth === false ? poly : smooth)(g, P, closed, o.tension ?? .5);
  if (o.fill && closed) { g.fillStyle = o.fill; g.fill(); }
  if (o.inner) { g.save(); g.clip(); o.inner(g); g.restore(); }
  if (o.shadeCol && closed) {         // cel shadow: the same shape offset, clipped to itself
    g.save(); g.clip(); g.beginPath();
    const d = o.shadeDir || [10, 0];
    (o.smooth === false ? poly : smooth)(g, P.map(p => [p[0] - d[0], p[1] - d[1]]), true, o.tension ?? .5);
    g.rect(-1e5, -1e5, 2e5, 2e5);
    g.fillStyle = o.shadeCol; g.fill('evenodd'); g.restore();
  }
  if (o.lw !== 0) {
    g.beginPath(); (o.smooth === false ? poly : smooth)(g, P, closed, o.tension ?? .5);
    g.lineJoin = 'round'; g.lineCap = 'round'; g.lineWidth = o.lw ?? 4; g.strokeStyle = o.ink || INK; g.stroke();
  }
  g.restore();
}
function ellipse(g, x, y, rx, ry, o = {}, rot = 0) {
  g.save(); if (o.alpha != null) g.globalAlpha *= o.alpha;
  g.beginPath(); g.ellipse(x, y, Math.max(.1, rx), Math.max(.1, ry), rot, 0, C.TAU);
  if (o.fill) { g.fillStyle = o.fill; g.fill(); }
  if (o.inner) { g.save(); g.clip(); o.inner(g); g.restore(); }
  if (o.lw !== 0) { g.lineWidth = o.lw ?? 4; g.strokeStyle = o.ink || INK; g.stroke(); }
  g.restore();
}
function line(g, P, lw = 3, col = INK, alpha = 1, smoothIt = true) {
  g.save(); g.globalAlpha *= alpha; g.beginPath(); (smoothIt ? smooth : poly)(g, P, false); g.lineWidth = lw; g.lineCap = 'round'; g.lineJoin = 'round'; g.strokeStyle = col; g.stroke(); g.restore();
}
// capsule between two points (puppet limb segment) with radii r0,r1
function capsulePts(a, b, r0, r1, n = 6) {
  const dx = b[0] - a[0], dy = b[1] - a[1], L = Math.hypot(dx, dy) || 1e-3, ux = dx / L, uy = dy / L, px = -uy, py = ux;
  const Q = [];
  for (let i = 0; i <= n; i++) { const t = -Math.PI / 2 + Math.PI * i / n; Q.push([b[0] + (ux * Math.cos(t) + px * Math.sin(t)) * r1, b[1] + (uy * Math.cos(t) + py * Math.sin(t)) * r1]); }
  for (let i = 0; i <= n; i++) { const t = Math.PI / 2 + Math.PI * i / n; Q.push([a[0] + (ux * Math.cos(t) + px * Math.sin(t)) * r0, a[1] + (uy * Math.cos(t) + py * Math.sin(t)) * r0]); }
  return Q;
}
function capsule(g, a, b, r0, r1, o = {}) { shape(g, capsulePts(a, b, r0, r1), { smooth: false, ...o }); }
// tube along a polyline with per-point radius
function tubePts(P, R) {
  const L = [], Rr = [];
  for (let i = 0; i < P.length; i++) {
    const a = P[Math.max(0, i - 1)], b = P[Math.min(P.length - 1, i + 1)];
    const dx = b[0] - a[0], dy = b[1] - a[1], l = Math.hypot(dx, dy) || 1, nx = -dy / l, ny = dx / l;
    L.push([P[i][0] + nx * R[i], P[i][1] + ny * R[i]]); Rr.push([P[i][0] - nx * R[i], P[i][1] - ny * R[i]]);
  }
  return L.concat(Rr.reverse());
}
// soft radial glow (additive)
function glow(g, x, y, r, col, a = 1, op = 'lighter') {
  g.save(); g.globalCompositeOperation = op; g.globalAlpha *= a;
  const gr = g.createRadialGradient(x, y, 0, x, y, r);
  gr.addColorStop(0, col); gr.addColorStop(1, rgba(col.startsWith('#') ? col : '#000000', 0));
  g.fillStyle = gr; g.beginPath(); g.arc(x, y, r, 0, C.TAU); g.fill(); g.restore();
}
// text with heavy outline (studio caption style)
function outlinedText(g, s, x, y, o = {}) {
  g.save();
  g.font = o.font; g.textAlign = o.align || 'center'; g.textBaseline = o.base || 'alphabetic';
  if (o.shadow) { g.fillStyle = rgba('#000000', .45); g.fillText(s, x + o.shadow, y + o.shadow * 1.4); g.lineWidth = o.lw; g.strokeStyle = rgba('#000000', .45); g.strokeText(s, x + o.shadow, y + o.shadow * 1.4); }
  g.lineJoin = 'round'; g.lineWidth = o.lw || 10; g.strokeStyle = o.ink || INK; g.strokeText(s, x, y);
  g.fillStyle = o.fill || '#fff'; g.fillText(s, x, y);
  g.restore();
}

module.exports = { INK, PAL, hex, toHex, cmix, rgba, shade, smooth, poly, shape, ellipse, line, capsule, capsulePts, tubePts, glow, outlinedText };
