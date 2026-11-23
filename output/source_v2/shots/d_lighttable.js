// LIGHT TABLE quick cuts (30.91 -> 33.04): flipping sheets, tracing live footage, flipbook
const C = require('../core'); const I = require('../ink'); const Pr = require('../props'); const B = require('../body'); const Hn = require('../hand'); const E = require('../env'); const S = require('../scene');
const TL = require('../timeline');
const { key, clamp, lerp, inv, ss, eOut, eIn, add, sub, mul, norm, fx, frame, basisFrom } = C;
const T_A = TL.downNear(30.91), T_B = 31.62, T_C = 32.34, T_D = 33.04;
const TXW = 900, TXH = 1500, PXC = 6;
const O_LIE = basisFrom([0, 0, -1], [0, 1, 0]);
const orthoCam = new C.Cam({ pos: [0, 1e5, 0], look: [0, 0, 0], up: [0, 0, -1], vw: TXW, vh: TXH, F: PXC * 1e5 });
const POSES = [
  { hl: [27, -30, 44], hr: [-27, -30, 44], hy: 0, hp: .08 },
  { hl: [30, -22, 10], hr: [-28, -30, 42], hy: .2, hp: .1 },
  { hl: [24, -16, -18], hr: [-26, -28, 36], hy: -.15, hp: .02 },
  { hl: [12, -20, -30], hr: [-30, -24, 20], hy: .25, hp: -.05 },
  { hl: [32, -26, 26], hr: [-14, -18, -8], hy: -.25, hp: .12 },
];
const CACHE = {};
function drawing(i, photo = false) {
  const k = i + (photo ? 'p' : ''); if (CACHE[k]) return CACHE[k];
  const P = POSES[i]; const c = C.createCanvas(TXW, TXH); const g = c.getContext('2d');
  const R = B.rig('morten', '80s', { pelvis: [0, -19, 30], orient: O_LIE, hl: { p: P.hl }, hr: { p: P.hr }, head: { yaw: P.hy, pitch: P.hp, E: { mouth: { open: i === 3 ? .5 : 0 } } } });
  const save = { ...I.ST };
  if (photo) { // a "live-action frame": soft, sepia, photographic
    g.fillStyle = '#6a625a'; g.fillRect(0, 0, TXW, TXH); I.ST.mode = 'color'; I.ST.inkW = 0; B.drawRig(g, orthoCam, R, { lw: 0 });
    const out = I.blurCanvas(c, 5); const o2 = C.createCanvas(TXW, TXH); const x = o2.getContext('2d'); x.filter = 'grayscale(1) sepia(.35)'; x.drawImage(out, 0, 0); Object.assign(I.ST, save); CACHE[k] = o2; return o2;
  }
  g.drawImage(Pr.paperTex('animpaper2', TXW, TXH, (g2, w, h) => { g2.fillStyle = '#2c2a2e'; g2.fillRect(0, 0, w, 34); for (const x of [w / 2 - 200, w / 2, w / 2 + 200]) { g2.fillStyle = '#e9e3d6'; g2.beginPath(); g2.roundRect(x - 30, 10, 60, 16, 8); g2.fill(); } }), 0, 0);
  I.ST.mode = 'pencil'; I.ST.inkW = 2.2; I.ST.toLight = [-.5, -.85]; I.ST.pencilW = 1.9; I.ST.frame = i * 7;
  B.drawRig(g, orthoCam, R, { lw: 2.2 });
  g.fillStyle = 'rgba(60,60,70,.55)'; g.font = '28px CapSemi'; g.fillText('SC 12   ' + String(43 + i).padStart(2, '0'), TXW - 210, TXH - 30);
  Object.assign(I.ST, save); CACHE[k] = c; return c;
}
function table(g, cam) {
  g.fillStyle = '#0a0809'; g.fillRect(0, 0, C.W, C.H);
  E.quad(g, cam, [[-260, -1, -320], [260, -1, -320], [260, -1, 320], [-260, -1, 320]], '#2a221c');
  const c = cam.p([0, 0, 0]); I.glow(g, c.x, c.y, 1100 * c.s / 2.2, '#ffe6b8', .3, 'lighter');
  // pencil cup and eraser for scale
  Pr.drawFaces(g, cam, [...Pr.cyl(frame([118, -1, -90], 0), 9, 14, 14, '#7a3a2a'), ...Pr.box(frame([110, 1, 80], .4), 5, 1.5, 3, '#e98fa0')]);
}
const quadP = (cam, y = 0) => [[-75, y, -125], [75, y, -125], [75, y, 125], [-75, y, 125]].map(p => { const q = cam.p(p); return [q.x, q.y]; });
const UV = [[0, 0], [TXW, 0], [TXW, TXH], [0, TXH]];
function sheet(g, cam, tex, y = 0, alpha = 1) { g.save(); g.globalAlpha = alpha; Pr.texPoly(g, tex, quadP(cam, y), UV); g.restore(); }
function pencilIn(g, cam, tip, ang = -2.3, sc = 1) { // world tip
  const q = cam.p(tip); g.save(); g.translate(q.x, q.y); g.rotate(ang); g.scale(q.s * sc / 6, q.s * sc / 6);
  const save = I.ST.mode; I.ST.mode = 'color';
  I.shape(g, [[0, 0], [60, -18], [60, 18]], { fill: '#e9c79a', lw: 4, smooth: false }); I.shape(g, [[0, 0], [18, -5.5], [18, 5.5]], { fill: '#2b2b2b', lw: 3, smooth: false });
  I.shape(g, [[60, -18], [520, -18], [520, 18], [60, 18]], { fill: '#2f6a4a', lw: 4, smooth: false });
  I.ST.mode = save; g.restore();
}
function animHand(g, cam, w, fwd, nrm, th, pose) { const h = Hn.buildHand({ w, fwd: norm(fwd), nrm: norm(nrm), th: norm(th), scale: .9, side: -1 }, pose); Hn.drawHand(g, cam, h, { skin: '#f2cbb0', sleeve: { col: '#f2ece0', r: 4.0, len: 22, cuff: '#c4a385' } }); }
function lightTable() { I.ST.toLight = [-.4, -.9]; I.ST.shadowTint = '#3a2a30'; I.ST.shadeMix = .4; I.ST.rim = null; Pr.setLight([0, 1, .2]); }

// a) flipping sheets: page curl from the bottom-right corner
function flip(g, t) {
  lightTable();
  const cam = new C.Cam({ pos: key(t, [[T_A, [10, 300, 30]], [T_B, [14, 280, 26]]]), look: [8, 0, 0], up: [0, 0, -1], fov: 50 });
  table(g, cam);
  const n = 2; const per = (T_B - T_A) / n; const k = Math.min(n - 1, Math.floor((t - T_A) / per)); const u = ss(((t - T_A) - k * per) / per);
  const under = drawing((k + 2) % POSES.length), top = drawing((k + 1) % POSES.length);
  sheet(g, cam, under);
  // fold line moves from the corner across the sheet
  const P = quadP(cam); const c0 = P[2]; // bottom-right corner (screen)
  const d = lerp(0, 1.25, u); const A = [lerp(c0[0], P[0][0], d * .9), c0[1]], Bp = [c0[0], lerp(c0[1], P[0][1], d * .9)];
  // top sheet minus the folded corner triangle
  g.save(); g.beginPath(); g.moveTo(P[0][0], P[0][1]); g.lineTo(P[1][0], P[1][1]); g.lineTo(Bp[0], Math.max(P[1][1], Bp[1])); g.lineTo(A[0], A[1]); g.lineTo(P[3][0], P[3][1]); g.closePath(); g.clip(); sheet(g, cam, top); g.restore();
  // flap (paper back) reflected over fold line
  const mx = (A[0] + Bp[0]) / 2, my = (A[1] + Bp[1]) / 2; const fx2 = A[0] - Bp[0], fy = A[1] - Bp[1]; const L2 = fx2 * fx2 + fy * fy || 1;
  const refl = p => { const t2 = ((p[0] - Bp[0]) * fx2 + (p[1] - Bp[1]) * fy) / L2; const px = Bp[0] + fx2 * t2, py = Bp[1] + fy * t2; return [2 * px - p[0], 2 * py - p[1]]; };
  const cr = refl(c0);
  if (d > .01) { I.shape(g, [A, Bp, cr], { fill: '#e9e2d2', lw: 2, smooth: false, shade: 10 }); I.glow(g, (A[0] + Bp[0]) / 2, (A[1] + Bp[1]) / 2, 120, '#000000', .15, 'source-over'); }
  // hand holding the flap corner
  const hw = [lerp(80, 20, u), 6 + u * 10, lerp(140, 40, u)];
  animHand(g, cam, hw, [-.6, -.2, -.8], [0, 1, 0], [1, 0, -.6], { curl: [.2, .3, .35, .4], spread: .2, thumb: { curl: .1, opp: .7 } });
  I.vignette(g, .55);
}
// b) tracing over live footage
function trace(g, t) {
  lightTable();
  const cam = new C.Cam({ pos: key(t, [[T_B, [26, 70, -38]], [T_C, [24, 64, -40]]]), look: [22, 0, -42], up: [0, 0, -1], fov: 46 });
  table(g, cam);
  sheet(g, cam, drawing(3, true));
  sheet(g, cam, Pr.paperTex('blank', TXW, TXH, (g2) => { }), 0, .78);
  // reveal the pencil drawing behind a growing window following the pencil
  const u = inv(T_B + .05, T_C - .05, t); const path = []; for (let i = 0; i <= 40; i++) { const a = -2.6 + i / 40 * 4.2; path.push([22 + Math.cos(a) * 15, 0, -42 + Math.sin(a) * 18]); }
  const n = Math.floor(u * 40); const tip = path[Math.min(40, n)];
  g.save(); g.beginPath(); for (let i = 0; i <= n; i++) { const q = cam.p(path[i]); g.moveTo(q.x + 70 * q.s / 6, q.y); g.arc(q.x, q.y, 70 * q.s / 6, 0, 7); } g.clip(); sheet(g, cam, drawing(3)); g.restore();
  pencilIn(g, cam, [tip[0], 1, tip[2]], -2.2, 1.4);
  animHand(g, cam, [tip[0] + 9, 7, tip[2] + 11], [-.55, -.35, -.75], [.1, 1, -.2], [.8, 0, -.5], { curl: [.5, .55, .75, .85], spread: .1, thumb: { curl: .35, opp: .9 } });
  I.vignette(g, .5);
}
// c) flipbook
function flipbook(g, t) {
  lightTable();
  const cam = new C.Cam({ pos: [10, 300, 30], look: [8, 0, 0], up: [0, 0, -1], fov: 50 });
  table(g, cam);
  const k = Math.floor((t - T_C) * 15) % POSES.length; sheet(g, cam, drawing(k));
  const ph = ((t - T_C) * 15) % 1; const P = quadP(cam);
  if (ph < .5) { g.save(); g.globalAlpha = .55 * (1 - ph * 2); g.fillStyle = '#f4efe3'; const y = lerp(P[3][1], P[0][1], ph * 2); g.fillRect(P[0][0], y - 40, P[1][0] - P[0][0], 80); g.restore(); }
  animHand(g, cam, [70, 8, 120], [-.5, -.2, -.85], [0, 1, 0], [1, 0, -.5], { curl: [.25, .3, .35, .4], spread: .2, thumb: { curl: .2, opp: .7 } });
  I.vignette(g, .55);
}
module.exports = [
  { t0: T_A, t1: T_B, name: 'flip', draw: flip },
  { t0: T_B, t1: T_C, name: 'trace', draw: trace },
  { t0: T_C, t1: T_D, name: 'flipbook', draw: flipbook },
];
