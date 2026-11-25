// Props: tools, jars, leeches, book, diagrams, comic FX.
const C = require('./core');
const { clamp, lerp, hash, rand, D2R, mixh } = C;
const D = require('./draw');
const { INK, PAL, shape, tube, tubeCurve, line, curve, ell, poly, glow, star, sparkle } = D;

// ---- a single leech: wriggling body, PG (tiny eyes optional)
function leech(ctx, x, y, len, t, seed = 0, o = {}) {
  const n = 8, pts = [], amp = o.amp === undefined ? 1 : o.amp, fat = o.fat || 1;
  const ang = (o.ang || 0) * D2R;
  for (let i = 0; i < n; i++) {
    const u = i / (n - 1);
    const wv = Math.sin(t * 7 + seed * 1.7 - u * 4.5) * 12 * amp;
    const px = (u - 0.5) * len, py = wv;
    pts.push([x + px * Math.cos(ang) - py * Math.sin(ang), y + px * Math.sin(ang) + py * Math.cos(ang)]);
  }
  const w = len * 0.22 * fat;
  tubeCurve(ctx, pts, w, o.color || '#3b2b2c', 4);
  // back stripe highlight
  ctx.save(); ctx.globalAlpha = 0.5; tubeCurve(ctx, pts.map(p => [p[0], p[1] - w * 0.18]), w * 0.25, '#6a5050', 0); ctx.restore();
  for (let i = 1; i < n - 1; i += 1) { const p = pts[i]; ctx.save(); ctx.globalAlpha = 0.35; line(ctx, [[p[0], p[1] - w * 0.4], [p[0], p[1] + w * 0.4]], 2, '#1a1010'); ctx.restore(); }
  if (o.eyes) {
    const h = pts[n - 1];
    for (const s of [-1, 1]) { shape(ctx, ell(h[0] - 6, h[1] + s * w * 0.2 - 4, w * 0.16, w * 0.2), '#fffaf0', { lw: 2.5, tex: false }); ctx.fillStyle = INK; ctx.beginPath(); ctx.arc(h[0] - 4, h[1] + s * w * 0.2 - 3, w * 0.07, 0, 7); ctx.fill(); }
    if (o.smile) curve(ctx, [h[0] - w * 0.2, h[1] + w * 0.25], [h[0] + 2, h[1] + w * 0.42], [h[0] + w * 0.15, h[1] + w * 0.22], 2.5);
  }
}

// ---- glass jar full of leeches
function leechJar(ctx, x, y, s, t, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  const w = 120, h = 210;
  // back of glass
  shape(ctx, c => { c.moveTo(-w, 0); c.lineTo(-w, -h * 0.85); c.quadraticCurveTo(-w, -h, -w * 0.7, -h); c.lineTo(w * 0.7, -h); c.quadraticCurveTo(w, -h, w, -h * 0.85); c.lineTo(w, 0); c.quadraticCurveTo(0, 18, -w, 0); c.closePath(); }, '#8ec6b0', { lw: 6, tex: false });
  // water
  ctx.save(); ctx.beginPath(); ctx.moveTo(-w + 6, -4); ctx.lineTo(-w + 6, -h * 0.72); ctx.quadraticCurveTo(0, -h * 0.72 - 8 + Math.sin(t * 3) * 5, w - 6, -h * 0.72); ctx.lineTo(w - 6, -4); ctx.closePath(); ctx.clip();
  ctx.fillStyle = '#5f9c86'; ctx.fillRect(-w, -h, 2 * w, h);
  const n = o.n || 7;
  for (let i = 0; i < n; i++) leech(ctx, -w * 0.6 + (i % 4) * w * 0.4 + hash(i) * 10, -26 - Math.floor(i / 4) * 48 - hash(i * 3) * 30 + Math.sin(t * 2 + i) * 6, 70, t, i, { ang: hash(i * 5) * 50, amp: 1.2, eyes: o.eyes && i === 2, smile: true });
  // bubbles
  for (let i = 0; i < 5; i++) { const k = (t * 0.6 + i * 0.21) % 1; ctx.fillStyle = 'rgba(230,255,245,0.6)'; ctx.beginPath(); ctx.arc(-w * 0.6 + i * 50, -10 - k * h * 0.7, 5 + i % 3, 0, 7); ctx.fill(); }
  ctx.restore();
  // glass front: highlights
  ctx.save(); ctx.globalAlpha = 0.55; tube(ctx, [[-w * 0.7, -h * 0.75], [-w * 0.7, -h * 0.15]], 16, '#eafff8', 0); tube(ctx, [[-w * 0.5, -h * 0.75], [-w * 0.5, -h * 0.6]], 8, '#eafff8', 0); ctx.restore();
  shape(ctx, c => { c.moveTo(-w, 0); c.lineTo(-w, -h * 0.85); c.quadraticCurveTo(-w, -h, -w * 0.7, -h); c.lineTo(w * 0.7, -h); c.quadraticCurveTo(w, -h, w, -h * 0.85); c.lineTo(w, 0); c.quadraticCurveTo(0, 18, -w, 0); c.closePath(); }, null, { lw: 6 });
  // cloth lid with string
  shape(ctx, c => { c.moveTo(-w * 0.85, -h + 4); c.quadraticCurveTo(-w * 0.95, -h - 46, 0, -h - 52); c.quadraticCurveTo(w * 0.95, -h - 46, w * 0.85, -h + 4); c.lineTo(w * 0.95, -h + 30); c.lineTo(-w * 0.95, -h + 30); c.closePath(); }, '#d8c49a', { lw: 5, shade: { x0: w, y0: -h, x1: -w, y1: -h, a: 0.3 } });
  line(ctx, [[-w * 0.85, -h + 8], [w * 0.85, -h + 8]], 6, '#7a4a2a');
  ctx.restore();
}

// ---- fleam / lancet (bloodletting knife), small and clean
function fleam(ctx, t, glint = 0) {
  shape(ctx, c => c.roundRect(-10, -18, 20, 70, 8), '#7a4a2a', { lw: 4 });
  shape(ctx, c => { c.moveTo(-8, -18); c.lineTo(8, -18); c.lineTo(10, -70); c.lineTo(40, -84); c.lineTo(10, -96); c.lineTo(-8, -96); c.closePath(); }, '#cfd6dc', { lw: 4, tex: false, hi: { x: 10, y: -70, r: 40, a: 0.6 } });
  if (glint > 0) { sparkle(ctx, 30, -86, 40 * glint, glint); }
}
function bowl(ctx, x, y, s = 1, covered = false) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  shape(ctx, c => { c.moveTo(-110, -60); c.quadraticCurveTo(-100, 10, 0, 14); c.quadraticCurveTo(100, 10, 110, -60); c.closePath(); }, '#c4c9cf', { lw: 5, tex: false, hi: { x: -50, y: -40, r: 60, a: 0.6 }, shade: { x0: -100, y0: 0, x1: 100, y1: 0, a: 0.3 } });
  shape(ctx, ell(0, -60, 110, 22), '#e2e6ea', { lw: 5, tex: false });
  if (covered) shape(ctx, c => { c.moveTo(-120, -58); c.quadraticCurveTo(-60, -110, 0, -100); c.quadraticCurveTo(70, -112, 122, -58); c.quadraticCurveTo(130, -30, 100, -20); c.lineTo(-104, -22); c.quadraticCurveTo(-130, -30, -120, -58); }, '#f0e8d6', { lw: 5, shade: { x0: 0, y0: -110, x1: 0, y1: -20, a: 0.25 } });
  ctx.restore();
}
function magnifier(ctx, t) {
  tube(ctx, [[0, 0], [0, 110]], 22, '#7a4a2a', 4);
  shape(ctx, c => { c.arc(0, -70, 72, 0, Math.PI * 2); c.arc(0, -70, 58, 0, Math.PI * 2, true); }, '#c9973a', { lw: 4, rule: 'evenodd', tex: false });
}
function tweezers(ctx) { tube(ctx, [[0, 0], [-4, -90]], 8, '#b0b6bc', 3); tube(ctx, [[0, 0], [6, -90]], 8, '#b0b6bc', 3); }
// brace & bit drill (auger), turning crank angle a
function braceDrill(ctx, a = 0, glint = 0) {
  const cx = Math.cos(a) * 60;
  tube(ctx, [[0, -150], [0, -110], [cx, -90], [cx, -30], [0, -10], [0, 20]], 12, '#8a6a4a', 4);
  shape(ctx, ell(cx, -60, 16, 30), '#a0703a', { lw: 4, tex: false });
  shape(ctx, c => c.roundRect(-34, -176, 68, 30, 12), '#a0703a', { lw: 4, tex: false });
  shape(ctx, c => { c.moveTo(-6, 20); c.lineTo(6, 20); c.lineTo(5, 120); c.lineTo(0, 140); c.lineTo(-5, 120); c.closePath(); }, '#c8ced4', { lw: 4, tex: false });
  for (let i = 0; i < 5; i++) line(ctx, [[-6, 40 + i * 18 + (a * 6) % 18], [6, 48 + i * 18 + (a * 6) % 18]], 2.5);
  if (glint > 0) sparkle(ctx, 0, 130, 46 * glint, glint);
}
function saw(ctx) { shape(ctx, c => { c.moveTo(0, 0); c.lineTo(150, -6); c.lineTo(150, 34); c.lineTo(0, 40); c.closePath(); }, '#c3c8ce', { lw: 4, tex: false }); for (let i = 0; i < 12; i++) line(ctx, [[i * 12, 40 - i * 0.15], [i * 12 + 6, 48]], 2.5); shape(ctx, c => c.roundRect(-60, -6, 64, 52, 14), '#7a4a2a', { lw: 4 }); }
function pliers(ctx) { tube(ctx, [[0, 0], [-20, 120]], 10, '#8a8c92', 4); tube(ctx, [[0, 0], [20, 120]], 10, '#8a8c92', 4); tube(ctx, [[0, 0], [-6, -50]], 10, '#8a8c92', 4); tube(ctx, [[0, 0], [6, -50]], 10, '#8a8c92', 4); shape(ctx, ell(0, 0, 10, 10), '#5a5c62', { lw: 3, tex: false }); }

// ---- comic FX
function puff(ctx, x, y, r, a = 1, col = '#f4ecd8') {
  ctx.save(); ctx.globalAlpha = a;
  shape(ctx, c => { for (let i = 0; i < 7; i++) { const an = i * Math.PI * 2 / 7, rr = r * (0.55 + 0.15 * (i % 2)); c.moveTo(x + Math.cos(an) * rr + r * 0.45, y + Math.sin(an) * rr); c.arc(x + Math.cos(an) * rr, y + Math.sin(an) * rr, r * 0.45, 0, Math.PI * 2); } }, col, { lw: 4, tex: false });
  ctx.restore();
}
function dust(ctx, x, y, lt, n = 6, size = 60, seed = 1) {
  for (let i = 0; i < n; i++) {
    const k = clamp(lt / 0.6), a = (i / n) * Math.PI + Math.PI + hash(i + seed) * 0.3;
    const r = size * (0.5 + k * 1.4);
    puff(ctx, x + Math.cos(a) * size * 2.2 * C.outC(k), y + Math.sin(a) * size * 0.6 * C.outC(k) - k * 20, r * (1 - k * 0.6), 1 - k, '#d9c49e');
  }
}
function dizzy(ctx, x, y, t, rx = 110, n = 4) {
  for (let i = 0; i < n; i++) {
    const a = t * 5 + i * Math.PI * 2 / n, px = x + Math.cos(a) * rx, py = y + Math.sin(a) * rx * 0.3;
    if (i % 2) star(ctx, px, py, 22, t * 6, '#ffe27a', 3.5);
    else { // tiny bird
      shape(ctx, ell(px, py, 18, 13), '#f6e7b8', { lw: 3.5, tex: false }); shape(ctx, poly([[px + 16, py - 2], [px + 28, py + 2], [px + 16, py + 5]]), '#e8a33a', { lw: 2.5, tex: false });
      ctx.fillStyle = INK; ctx.beginPath(); ctx.arc(px + 6, py - 3, 2.5, 0, 7); ctx.fill();
    }
  }
}
// open old book (top-down insert)
function openBook(ctx, x, y, w, h, t, o = {}) {
  const open = clamp(o.open === undefined ? 1 : o.open);
  shape(ctx, c => c.roundRect(x - w / 2 - 24, y - h / 2 - 20, w + 48, h + 46, 18), '#6a2a24', { lw: 6, shade: { x0: 0, y0: y - h / 2, x1: 0, y1: y + h / 2, a: 0.3 } });
  const pg = (sx, flip) => shape(ctx, c => { c.moveTo(x, y - h / 2 + 8); c.quadraticCurveTo(x + sx * w * 0.25, y - h / 2 - 14, x + sx * w / 2, y - h / 2); c.lineTo(x + sx * w / 2, y + h / 2); c.quadraticCurveTo(x + sx * w * 0.25, y + h / 2 - 14, x, y + h / 2 + 8); c.closePath(); }, '#f0dfb4', { lw: 5, shade: { x0: x, y0: 0, x1: x + sx * w * 0.2, y1: 0, a: 0.35 } });
  pg(-1); if (open > 0.02) { ctx.save(); ctx.translate(x, 0); ctx.scale(open, 1); ctx.translate(-x, 0); pg(1); ctx.restore(); }
  return open;
}
// little stylized "patient" figure used on diagrams
function figure(ctx, x, y, s, col = '#f1c49b', hood = true) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  tube(ctx, [[-20, 40], [-26, 120]], 18, '#6e4c36', 3.5); tube(ctx, [[20, 40], [26, 120]], 18, '#6e4c36', 3.5);
  shape(ctx, c => { c.moveTo(-40, -50); c.lineTo(40, -50); c.lineTo(50, 50); c.lineTo(-50, 50); c.closePath(); }, '#7d8a3d', { lw: 4 });
  tube(ctx, [[-40, -40], [-62, 30]], 18, '#7d8a3d', 3.5); tube(ctx, [[40, -40], [62, 30]], 18, '#7d8a3d', 3.5);
  if (hood) shape(ctx, ell(0, -100, 52, 54), '#c98a2e', { lw: 4 });
  shape(ctx, ell(0, -96, 38, 42), col, { lw: 4, tex: false });
  ctx.restore();
}

module.exports = { leech, leechJar, fleam, bowl, magnifier, tweezers, braceDrill, saw, pliers, puff, dust, dizzy, openBook, figure };
