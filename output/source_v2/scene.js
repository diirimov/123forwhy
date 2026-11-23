// scene helpers shared by shots
const C = require('./core'); const I = require('./ink'); const Pr = require('./props'); const E = require('./env');
const { clamp, lerp } = C;
// offscreen layer for depth-of-field
function layer() { const c = C.createCanvas(C.W, C.H); return [c, c.getContext('2d')]; }
function drawBlurred(g, fn, amt) { if (amt < 1.2) { fn(g); return; } const [c, x] = layer(); fn(x); const b = I.blurCanvas(c, amt); g.drawImage(b, 0, 0); }
// world-space wall of vertical boards
function boards(g, cam, p0, p1, h, col, n, o = {}) { // p0,p1 floor endpoints; wall up to h
  const P = [p0, p1, C.add(p1, [0, h, 0]), C.add(p0, [0, h, 0])]; E.quad(g, cam, P, col);
  const segs = []; for (let i = 1; i < n; i++) { const a = C.lerp3(p0, p1, i / n); segs.push([a, C.add(a, [0, h, 0])]); }
  E.lines3(g, cam, segs, o.line || I.mix(col, '#000000', .45), o.w || .35, o.a ?? .8);
}
function floorPlanks(g, cam, x0, x1, z0, z1, y, col, n = 14, dirX = true) {
  E.quad(g, cam, [[x0, y, z0], [x1, y, z0], [x1, y, z1], [x0, y, z1]], col); const segs = [];
  for (let i = 1; i < n; i++) { if (dirX) { const z = lerp(z0, z1, i / n); segs.push([[x0, y, z], [x1, y, z]]); } else { const x = lerp(x0, x1, i / n); segs.push([[x, y, z0], [x, y, z1]]); } }
  E.lines3(g, cam, segs, I.mix(col, '#000000', .4), .3, .7);
}
// snow outside a window (screen space inside clip)
function snowfall(g, t, bb, n = 60, seed = 3) { const r = C.rng(seed); g.fillStyle = 'rgba(255,255,255,.85)'; for (let i = 0; i < n; i++) { const z = .4 + r(); const x = bb[0] + ((r() * (bb[2] - bb[0]) + t * 14 * z + Math.sin(t * .8 + i) * 8) % (bb[2] - bb[0])); const y = bb[1] + ((r() * (bb[3] - bb[1]) + t * 40 * z) % (bb[3] - bb[1])); g.beginPath(); g.ellipse(x, y, 2.2 * z, 2.2 * z, 0, 0, 7); g.fill(); } }
function shake(t, t0, amp = 10, dec = 9) { if (t < t0) return [0, 0]; const u = t - t0; const e = Math.exp(-u * dec) * amp; return [Math.sin(u * 70) * e, Math.cos(u * 57) * e * .7]; }
module.exports = { layer, drawBlurred, boards, floorPlanks, snowfall, shake };
