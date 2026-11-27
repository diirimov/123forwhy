// creatures: the cat that backs away from the swarm
'use strict';
const C = require('./core');
const K = require('./ink');
const { clamp, lerp, TAU } = C;
const { INK } = K;

// side-view cat facing +x (mirrored by dir). arch 0..1 (hissing arch), step phase for backing away
function cat(g, x, y, o = {}) {
  const s = o.s || 1, dir = o.dir || 1, arch = clamp(o.arch ?? 0), ph = (o.phase || 0) * TAU, t = o.t || 0;
  const lw = (o.lw ?? 4) / s;
  const col = o.col || '#3e3531', light = '#5a4e48';
  g.save(); g.translate(x, y); g.scale(dir * s, s);
  g.save(); g.globalAlpha *= .22; g.fillStyle = '#1b0f08'; g.beginPath(); g.ellipse(0, 2, 70, 9, 0, 0, TAU); g.fill(); g.restore();
  const bk = -38 - arch * 34;
  // tail (bristled when arched)
  const tail = []; for (let i = 0; i <= 8; i++) { const u = i / 8; tail.push([-52 - u * 30 * (1 - arch * .5), bk + 4 - u * (60 + arch * 30) + Math.sin(t * 6 + u * 3) * 6 * (1 - arch)]); }
  K.shape(g, K.tubePts(tail, tail.map((_, i) => 7 + arch * 5 - i * .4)), { fill: col, lw, tension: .4 });
  // legs: back away (stepping backward)
  const legs = [[-38, Math.PI], [-26, 0], [26, Math.PI * .5], [38, Math.PI * 1.5]];
  for (const [lx, off] of legs) {
    const a = Math.sin(ph + off) * .3; const lift = Math.max(0, Math.sin(ph + off)) * 6;
    K.shape(g, K.tubePts([[lx, -30 - arch * 18], [lx - Math.sin(a) * 6, -14 - lift], [lx - Math.sin(a) * 10, -lift]], [7, 5.5, 4.5]), { fill: col, lw: lw * .9, tension: .3 });
  }
  // body (arched)
  K.shape(g, [[-56, bk + 14], [-40, bk - 4], [0, bk - 12 - arch * 10], [36, bk - 2], [52, bk + 12], [44, -26], [0, -24 + arch * 4], [-46, -24]], { fill: col, lw, tension: .5 });
  // head with ears, hissing mouth
  g.save(); g.translate(56, bk + 6 + arch * 10);
  K.shape(g, [[-14, -6], [-10, -30], [0, -18], [14, -32], [22, -12], [30, 0], [22, 16], [0, 18], [-14, 10]], { fill: col, lw, tension: .45 });
  for (const ex of [6, 18]) { K.ellipse(g, ex, -2, 5, 6, { fill: '#e9d86a', lw: lw * .6 }); K.ellipse(g, ex + 1, -2, 1.6, 4.6, { fill: '#111', lw: 0 }); }
  if (arch > .3) K.shape(g, [[16, 10], [30, 8], [26, 16], [18, 17]], { fill: '#6a2a2a', lw: lw * .6, tension: .3 });
  for (const a of [-.15, .05, .2]) K.line(g, [[26, 6], [48, 4 + a * 40]], 1.6, '#d8d0c0', .7, false);
  g.restore();
  g.restore();
}
module.exports = { cat };
