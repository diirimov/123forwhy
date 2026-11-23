// env: stage, crowd, light beams, haze, rooms
const C = require('./core');
const I = require('./ink');
const { clamp, lerp, rng, hash, noise } = C;

// crowd as world-space grid of people (silhouettes, rim-lit). o: {x0,x1,z0,z1,y (floor), n, seed, rim, rimA, fill, arms, energy, t, lit}
function crowd(g, cam, o) {
  const r = rng(o.seed || 7); const items = [];
  const n = o.n || 2400;
  for (let i = 0; i < n; i++) {
    const x = lerp(o.x0, o.x1, r()), z = lerp(o.z0, o.z1, Math.pow(r(), o.zPow ?? 1.0)); const h = 150 + r() * 30;
    const p = cam.p([x, o.y + h, z]); if (p.z < 30) continue;
    if (p.x < -200 || p.x > 1280 || p.y > 2300) continue;
    items.push({ x, z, h, p, ph: r() * 6.28, up: r() < (o.arms ?? .55), side: r() < .5 ? -1 : 1, hue: r(), shirt: r() });
  }
  items.sort((a, b) => b.p.z - a.p.z);
  const t = o.t || 0, E = o.energy ?? 1;
  for (const it of items) {
    const s = it.p.s; const head = it.p; const jump = Math.max(0, Math.sin(t * (o.bounceF || 9.2) + it.ph)) * 7 * E;
    const hy = head.y - jump * s;
    const shoulder = cam.p([it.x, o.y + it.h - 24, it.z]); const sy = shoulder.y - jump * s;
    const fog = clamp((it.p.z - (o.fogNear || 400)) / (o.fogFar || 4000));
    const base = I.mix(o.fill || '#0a0810', o.fogCol || '#1a1430', fog * .85);
    g.fillStyle = base; g.strokeStyle = base; g.lineCap = 'round';
    if (s < .35) { // far: blob
      g.beginPath(); g.ellipse(head.x, hy + 6 * s, 15 * s, 26 * s, 0, 0, 7); g.fill();
      if (it.up && s > .12) { g.lineWidth = 6 * s; g.beginPath(); g.moveTo(head.x + it.side * 10 * s, hy + 10 * s); g.lineTo(head.x + it.side * (14 + Math.sin(t * 7 + it.ph) * 6) * s, hy - 48 * s); g.stroke(); }
      if (o.rim && s > .15) { g.fillStyle = I.rgba(o.rim, (o.rimA ?? .6) * (1 - fog) * .8); g.beginPath(); g.ellipse(head.x, hy - 9 * s, 8 * s, 3 * s, 0, 0, 7); g.fill(); }
      continue;
    }
    // near: head, shoulders, arms
    const armsUp = it.up; const sw = Math.sin(t * (o.waveF || 6.5) + it.ph);
    g.lineWidth = 11 * s;
    if (armsUp) {
      for (const sd of [-1, 1]) { if (it.shirt < .35 && sd === it.side) continue; const ex = head.x + sd * (22 + sw * 8 * sd) * s, ey = hy - 40 * s; g.beginPath(); g.moveTo(head.x + sd * 18 * s, sy); g.quadraticCurveTo(head.x + sd * 28 * s, (sy + ey) / 2, ex, ey); g.stroke(); g.beginPath(); g.ellipse(ex, ey - 4 * s, 6 * s, 7 * s, 0, 0, 7); g.fill(); }
    }
    g.beginPath(); g.ellipse(head.x, hy - 6 * s, 11.5 * s, 14 * s, 0, 0, 7); g.fill();
    g.beginPath(); g.moveTo(head.x - 25 * s, sy + 120 * s); g.quadraticCurveTo(head.x - 27 * s, sy, head.x - 10 * s, sy - 6 * s); g.lineTo(head.x + 10 * s, sy - 6 * s); g.quadraticCurveTo(head.x + 27 * s, sy, head.x + 25 * s, sy + 120 * s); g.fill();
    if (o.rim) {
      g.save(); g.globalAlpha = (o.rimA ?? .6) * (1 - fog); g.strokeStyle = o.rim; g.lineWidth = 2.6 * s;
      g.beginPath(); g.arc(head.x, hy - 6 * s, 12 * s, Math.PI * 1.1, Math.PI * 1.9); g.stroke();
      g.beginPath(); g.moveTo(head.x - 24 * s, sy + 10 * s); g.quadraticCurveTo(head.x, sy - 10 * s, head.x + 24 * s, sy + 10 * s); g.stroke();
      if (o.face && s > .9) { g.globalAlpha = .35 * (1 - fog); g.fillStyle = o.face; g.beginPath(); g.ellipse(head.x, hy - 2 * s, 8 * s, 10 * s, 0, 0, 7); g.fill(); }
      g.restore();
    }
  }
}
// volumetric beams from a source pointing at direction (screen space), additive
function beam(g, x, y, ang, len, wid, col, a = .5) {
  g.save(); g.globalCompositeOperation = 'lighter';
  const ex = x + Math.sin(ang) * len, ey = y + Math.cos(ang) * len;
  const gr = g.createLinearGradient(x, y, ex, ey); gr.addColorStop(0, I.rgba(col, a)); gr.addColorStop(.5, I.rgba(col, a * .35)); gr.addColorStop(1, I.rgba(col, 0));
  g.fillStyle = gr; g.beginPath(); g.moveTo(x, y);
  g.lineTo(x + Math.sin(ang - wid) * len, y + Math.cos(ang - wid) * len); g.lineTo(x + Math.sin(ang + wid) * len, y + Math.cos(ang + wid) * len); g.closePath(); g.fill();
  g.restore();
  I.glow(g, x, y, 70 * (len / 2000 + .4), col, a);
}
// world-space beam: from lamp (world) toward target (world)
function beam3(g, cam, from, to, wid, col, a) { const p = cam.p(from), q = cam.p(to); const ang = Math.atan2(q.x - p.x, q.y - p.y); beam(g, p.x, p.y, ang, Math.hypot(q.x - p.x, q.y - p.y) * 1.2, wid, col, a); }
function haze(g, col, a, y0 = 0, y1 = C.H) { const gr = g.createLinearGradient(0, y0, 0, y1); gr.addColorStop(0, I.rgba(col, 0)); gr.addColorStop(.5, I.rgba(col, a)); gr.addColorStop(1, I.rgba(col, 0)); g.save(); g.globalCompositeOperation = 'screen'; g.fillStyle = gr; g.fillRect(0, y0, C.W, y1 - y0); g.restore(); }
// world quad helper
function quad(g, cam, P, col) { const Q = P.map(p => cam.p(p)); g.fillStyle = col; g.beginPath(); I.poly(g, Q.map(q => [q.x, q.y])); g.fill(); return Q; }
// planks / lines on a plane
function lines3(g, cam, segs, col, w, a = 1) { g.save(); g.strokeStyle = col; g.globalAlpha = a; g.lineCap = 'round'; for (const [p0, p1] of segs) { const q0 = cam.p(p0), q1 = cam.p(p1); g.lineWidth = Math.max(.6, w * (q0.s + q1.s) / 2); g.beginPath(); g.moveTo(q0.x, q0.y); g.lineTo(q1.x, q1.y); g.stroke(); } g.restore(); }

module.exports = { crowd, beam, beam3, haze, quad, lines3 };

// crowd v2: front-lit audience with varied clothes, raised hands, haze depth
const SHIRTS = ['#2b3550', '#6a2a34', '#3d5a80', '#1f1f24', '#d9d2c2', '#8c6a2e', '#2f5d5a', '#5a4a6a', '#b4483c', '#44464f'];
const SKINS = ['#f0c8a8', '#e2b08c', '#c98f6b', '#a8704e', '#f4d2b8', '#8a5a40'];
const HAIRS = ['#1d1612', '#3a2618', '#6a4a2a', '#c9a35a', '#2a2a2a', '#8a3a22'];
function crowd2(g, cam, o) {
  const r = rng(o.seed || 7); const items = []; const n = o.n || 3000;
  for (let i = 0; i < n; i++) {
    const x = lerp(o.x0, o.x1, r()), z = lerp(o.z0, o.z1, Math.pow(r(), o.zPow ?? 1.6)); const h = 152 + r() * 34;
    const p = cam.p([x, o.y + h, z]); if (p.z < 25 || p.x < -250 || p.x > 1330 || p.y > 2400 || p.y < -400) continue;
    items.push({ x, z, h, p, ph: r() * 6.28, up: r(), side: r() < .5 ? -1 : 1, shirt: SHIRTS[(r() * SHIRTS.length) | 0], skin: SKINS[(r() * SKINS.length) | 0], hair: HAIRS[(r() * HAIRS.length) | 0], w: .9 + r() * .25 });
  }
  items.sort((a, b) => b.p.z - a.p.z);
  const t = o.t || 0, En = o.energy ?? 1, lit = o.lit ?? 1;
  for (const it of items) {
    const s = it.p.s * it.w; const fog = clamp((it.p.z - (o.fogNear || 500)) / (o.fogFar || 4500));
    const wash = o.wash ? o.wash(it.x, it.z) : '#ffffff';
    const L = (c) => I.mix(I.mix(I.mult(c, I.mix('#303040', wash, lit)), o.fogCol || '#2a1d40', fog * .92), '#000000', 0);
    const jump = Math.max(0, Math.sin(t * (o.bounceF || 9.6) + it.ph)) * 6 * En;
    const hx = it.p.x, hy = it.p.y - jump * s;
    const armsUp = it.up < (o.arms ?? .55), oneArm = it.up < (o.arms ?? .55) * .45;
    if (s < .3) { g.fillStyle = L(it.shirt); g.beginPath(); g.ellipse(hx, hy + 14 * s, 15 * s, 22 * s, 0, 0, 7); g.fill(); g.fillStyle = L(it.skin); g.beginPath(); g.ellipse(hx, hy - 6 * s, 9 * s, 10 * s, 0, 0, 7); g.fill();
      if (armsUp && s > .1) { g.strokeStyle = L(it.skin); g.lineWidth = 5 * s; g.beginPath(); g.moveTo(hx + it.side * 12 * s, hy + 6 * s); g.lineTo(hx + it.side * (16 + Math.sin(t * 6 + it.ph) * 5) * s, hy - 42 * s); g.stroke(); } continue; }
    const sw = Math.sin(t * (o.waveF || 6.3) + it.ph) * En;
    // arms (behind body for raised)
    if (armsUp) for (const sd of [-1, 1]) { if (oneArm && sd !== it.side) continue; const ex = hx + sd * (24 + sw * 7 * sd) * s, ey = hy - (52 + sw * 4) * s; g.strokeStyle = L(it.shirt); g.lineWidth = 11 * s; g.lineCap = 'round'; g.beginPath(); g.moveTo(hx + sd * 18 * s, hy + 24 * s); g.quadraticCurveTo(hx + sd * 30 * s, hy - 10 * s, ex, ey); g.stroke(); g.fillStyle = L(it.skin); g.beginPath(); g.ellipse(ex, ey - 5 * s, 6.5 * s, 8 * s, 0, 0, 7); g.fill(); }
    g.fillStyle = L(it.shirt); g.beginPath(); g.moveTo(hx - 27 * s, hy + 150 * s); g.quadraticCurveTo(hx - 29 * s, hy + 20 * s, hx - 12 * s, hy + 14 * s); g.lineTo(hx + 12 * s, hy + 14 * s); g.quadraticCurveTo(hx + 29 * s, hy + 20 * s, hx + 27 * s, hy + 150 * s); g.fill();
    g.fillStyle = L(it.skin); g.beginPath(); g.ellipse(hx, hy, 11 * s, 13.5 * s, 0, 0, 7); g.fill();
    g.fillStyle = L(it.hair); g.beginPath(); g.ellipse(hx, hy - 6 * s, 12 * s, 9.5 * s, 0, Math.PI, 0); g.fill();
    if (s > .7 && o.faces) { g.fillStyle = I.rgba('#2a1410', .55 * (1 - fog)); g.beginPath(); g.ellipse(hx - 4 * s, hy - 1 * s, 1.5 * s, 1.8 * s, 0, 0, 7); g.ellipse(hx + 4 * s, hy - 1 * s, 1.5 * s, 1.8 * s, 0, 0, 7); g.fill(); g.fillStyle = I.rgba('#5a1e22', .85 * (1 - fog)); g.beginPath(); g.ellipse(hx, hy + 6 * s, 3 * s, (2.5 + Math.max(0, sw) * 2) * s, 0, 0, 7); g.fill(); }
    if (s > .8 && o.ink) { g.strokeStyle = I.rgba('#120c10', .6 * (1 - fog)); g.lineWidth = 1.6; g.beginPath(); g.ellipse(hx, hy, 11 * s, 13.5 * s, 0, 0, 7); g.stroke(); }
    if (o.rim) { g.save(); g.globalAlpha = (o.rimA ?? .5) * (1 - fog); g.strokeStyle = o.rim; g.lineWidth = 2.2 * s; g.beginPath(); g.arc(hx, hy - 2 * s, 12.5 * s, Math.PI * 1.15, Math.PI * 1.85); g.stroke(); g.restore(); }
  }
}
module.exports.crowd2 = crowd2;
