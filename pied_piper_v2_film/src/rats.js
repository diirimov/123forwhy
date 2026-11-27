// rats: articulated rats (side + top views), gait, tail waves, ear twitches, standing pose, head turn
'use strict';
const C = require('./core');
const K = require('./ink');
const { clamp, lerp, TAU } = C;
const { PAL, INK } = K;

// side view rat. local units: ~120 long (snout to rump), drawn facing +x then mirrored by dir.
// o: {dir:1|-1, s, phase (gait cycles), speed 0..1, stand 0..1, look 0..1 (head to camera), ear 0..1, tail, sil, lw, col}
function ratSide(g, x, y, o = {}) {
  const s = o.s || 1, dir = o.dir || 1, sp = o.speed ?? 1, ph = (o.phase || 0) * TAU;
  const stand = clamp(o.stand || 0), look = clamp(o.look || 0);
  const lw = (o.lw ?? 3.6) / s;
  const fill = o.sil || o.col || PAL.rat, dark = o.sil || PAL.ratD, pink = o.sil || PAL.ratPink, belly = o.sil || PAL.ratBelly;
  g.save(); g.translate(x, y); g.scale(dir * s, s);
  if (o.tilt) g.rotate(o.tilt * dir);
  // body pitch: standing rotates the torso up about the hips
  const pitch = -stand * 1.15;
  const bob = Math.abs(Math.sin(ph)) * 3 * sp;
  const und = Math.sin(ph) * .06 * sp;
  // ground shadow
  if (!o.sil && o.shadow !== false) { g.save(); g.globalAlpha *= .22; g.fillStyle = '#1b0f08'; g.beginPath(); g.ellipse(0, 2, 58, 8, 0, 0, TAU); g.fill(); g.restore(); }
  const hip = [-26, -26 - bob];
  const rot = (p, a, c = hip) => { const dx = p[0] - c[0], dy = p[1] - c[1]; const ca = Math.cos(a), sa = Math.sin(a); return [c[0] + dx * ca - dy * sa, c[1] + dx * sa + dy * ca]; };
  // tail (behind)
  const tl = o.tailLen || 1;
  const tail = []; const base = [-52, -22 - bob];
  for (let i = 0; i <= 10; i++) {
    const u = i / 10; const w = Math.sin(ph * .5 + u * 5 - (o.t || 0) * 4) * 9 * u * (o.tail ?? 1) + (stand ? u * u * 10 : 0);
    tail.push([base[0] - u * 105 * tl, base[1] + u * 18 + w + (stand ? 6 * u : 0)]);
  }
  K.shape(g, K.tubePts(tail, tail.map((_, i) => 5.5 - i * .45)), { fill: pink, lw, tension: .4 });
  // legs
  const leg = (bx, by, phase, front, near) => {
    const a = Math.sin(ph + phase) * .55 * sp; const lift = Math.max(0, Math.cos(ph + phase)) * 7 * sp;
    let k = [bx + Math.sin(a) * 10, by + 14 - lift * .5];
    let f = [bx + Math.sin(a) * 22 + (front ? 4 : -2), -lift];
    if (front && stand > .2) { const p0 = rot([bx, by], pitch); k = [p0[0] + 10, p0[1] + 10]; f = [p0[0] + 16, p0[1] + 2]; bx = p0[0]; by = p0[1]; }
    const col = near ? fill : dark;
    K.shape(g, K.tubePts([[bx, by], k, f], [7, 5, 3.5]), { fill: col, lw: lw * .9, tension: .3 });
    K.ellipse(g, f[0] + 4, f[1] + 1, 6, 3, { fill: pink, lw: lw * .7 });
  };
  leg(-30, -18 - bob, Math.PI, false, false);     // far hind
  leg(18, -16 - bob, 0, true, false);             // far front
  // body
  const bodyP = [[-58, -18], [-56, -40], [-36, -56], [-6, -58], [18, -52], [34, -40], [36, -24], [14, -14], [-20, -12], [-46, -10]]
    .map(p => [p[0], p[1] - bob + (p[0] > 0 ? und * p[0] : 0)]).map(p => rot(p, pitch));
  K.shape(g, bodyP, { fill, lw, tension: .55, inner: o.sil ? null : (g2) => {
    g2.fillStyle = belly; g2.beginPath(); const bp = [[-44, -14], [-10, -20], [24, -22], [34, -24], [14, -12], [-30, -8]].map(p => rot([p[0], p[1] - bob], pitch)); K.smooth(g2, bp, true); g2.fill();
    g2.strokeStyle = K.rgba(INK, .25); g2.lineWidth = lw * .5; for (let i = 0; i < 5; i++) { const p = rot([-40 + i * 14, -46 - bob], pitch); g2.beginPath(); g2.moveTo(p[0], p[1]); g2.lineTo(p[0] + 6, p[1] + 8); g2.stroke(); }
  } });
  leg(-30, -18 - bob, 0, false, true);            // near hind
  leg(18, -16 - bob, Math.PI, true, true);        // near front
  // head (profile or turned to camera)
  const neck = rot([30, -40 - bob], pitch);
  const earTw = (o.ear || 0) * Math.sin((o.t || 0) * 60) * .5;
  g.save(); g.translate(neck[0], neck[1]); g.rotate(pitch * .6 + (o.headTilt || 0));
  if (look < .5) {
    const sq = 1 - look * 1.2;
    // far ear
    K.ellipse(g, 4, -20, 10, 13, { fill: dark, lw }, -.3 + earTw);
    K.shape(g, [[-6, -14], [10, -24], [30, -16], [52, -4], [56, 2], [44, 8], [16, 12], [-4, 6]].map(p => [p[0] * sq + (1 - sq) * 8, p[1]]), { fill, lw, tension: .5 });
    K.ellipse(g, 56 * sq + (1 - sq) * 8, 1, 4.5, 4, { fill: pink, lw: lw * .7 });
    K.ellipse(g, 30 * sq + 4 * (1 - sq), -7, 4.2, 4.6, { fill: '#120c0a', lw: 0 });
    if (!o.sil) K.ellipse(g, 29 * sq, -8.5, 1.4, 1.4, { fill: '#fff', lw: 0 });
    // near ear (pink inner)
    g.save(); g.translate(14, -20); g.rotate(-.2 - earTw);
    K.ellipse(g, 0, -4, 12, 15, { fill, lw }); if (!o.sil) K.ellipse(g, 1, -3, 7, 9, { fill: pink, lw: 0 });
    g.restore();
    if (!o.sil) for (const a of [-.25, 0, .25]) K.line(g, [[48 * sq, 2], [72 * sq, 2 + a * 26]], 1.4, INK, .6, false);
  } else {
    // frontal head: two ears, two eyes, snout toward camera
    const k = (look - .5) * 2;
    for (const sd of [-1, 1]) {
      g.save(); g.translate(sd * 17 + 8, -24); g.rotate(sd * (.35 + earTw));
      K.ellipse(g, 0, -4, 12, 15, { fill, lw }); if (!o.sil) K.ellipse(g, 0, -3, 7, 9, { fill: pink, lw: 0 }); g.restore();
    }
    K.shape(g, [[-12, -18], [28, -18], [34, -4], [20, 16], [8, 22], [-4, 16], [-18, -4]], { fill, lw, tension: .5 });
    for (const sd of [-1, 1]) { K.ellipse(g, 8 + sd * 11, -6, 4.2, 4.8, { fill: '#120c0a', lw: 0 }); if (!o.sil) K.ellipse(g, 7 + sd * 11, -7.5, 1.4, 1.4, { fill: o.eyeGlow ? '#ffe6a8' : '#fff', lw: 0 }); }
    K.ellipse(g, 8, 17, 4.5, 3.6, { fill: pink, lw: lw * .7 });
    if (!o.sil) for (const sd of [-1, 1]) for (const a of [-.2, .15]) K.line(g, [[8 + sd * 6, 15], [8 + sd * 30, 13 + a * 30]], 1.4, INK, .6, false);
  }
  g.restore();
  g.restore();
}

// top-down rat for overhead swarm shots. ang = heading (radians). o: {s, phase, speed, sil, t}
function ratTop(g, x, y, ang, o = {}) {
  const s = o.s || 1, ph = (o.phase || 0) * TAU, sp = o.speed ?? 1;
  const lw = (o.lw ?? 3) / s;
  const fill = o.sil || o.col || PAL.rat, pink = o.sil || PAL.ratPink, dark = o.sil || PAL.ratD;
  g.save(); g.translate(x, y); g.rotate(ang); g.scale(s, s);
  const wig = Math.sin(ph) * .12 * sp;
  // tail
  const tail = []; for (let i = 0; i <= 9; i++) { const u = i / 9; tail.push([-40 - u * 90, Math.sin(ph * .5 + u * 5 - (o.t || 0) * 5) * 12 * u + wig * 40 * u]); }
  K.shape(g, K.tubePts(tail, tail.map((_, i) => 4.5 - i * .4)), { fill: pink, lw, tension: .4 });
  // legs (paddles)
  for (const [lx, side, off] of [[18, 1, 0], [18, -1, Math.PI], [-22, 1, Math.PI], [-22, -1, 0]]) {
    const a = Math.sin(ph + off) * .6 * sp;
    const fx = lx + Math.cos(a) * 14 * 0 + Math.sin(a) * 10, fy = side * (17 + Math.cos(a) * 3);
    K.shape(g, K.tubePts([[lx, side * 8], [fx, fy]], [4.5, 3]), { fill: dark, lw: lw * .8, tension: .3 });
  }
  // body + head
  g.rotate(wig);
  K.shape(g, [[-46, 0], [-38, -18], [-6, -22], [22, -16], [44, -9], [58, 0], [44, 9], [22, 16], [-6, 22], [-38, 18]], { fill, lw, tension: .5, inner: o.sil ? null : (g2) => { g2.fillStyle = K.rgba('#2a1a10', .18); g2.beginPath(); g2.ellipse(-8, 0, 30, 8, 0, 0, TAU); g2.fill(); } });
  for (const sd of [-1, 1]) K.ellipse(g, 30, sd * 13, 8, 6, { fill: pink, lw: lw * .8 });
  K.ellipse(g, 58, 0, 3.5, 3.5, { fill: pink, lw: 0 });
  if (!o.sil) for (const sd of [-1, 1]) K.ellipse(g, 44, sd * 6, 2.4, 2.4, { fill: '#120c0a', lw: 0 });
  g.restore();
}

module.exports = { ratSide, ratTop };
