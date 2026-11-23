// THE CROSSING (33.75 -> 44.10): drawn Morten pushes through the sheet, pulls himself out onto the stage; crowd reveal on "Take"
const C = require('../core'); const I = require('../ink'); const B = require('../body'); const Hn = require('../hand'); const E = require('../env'); const Pr = require('../props');
const TL = require('../timeline');
const { key, keyOrient, basisFrom, clamp, lerp, inv, ss, s5, eOut, eIn, add, sub, mul, norm, dot } = C;
const T0 = TL.CUE.pre, TK = TL.CUE.take, T1 = 44.10;
const PW = 75, PL = 125; // paper half sizes (cm)
const TXW = 900, TXH = 1500, PXC = 6; // texture px per cm
const t1 = 35.17, t2 = 36.60, t3 = 38.01, t4 = 40.30;

const O_LIE = basisFrom([0, 0, -1], [0, 1, 0]);
const O_MID = basisFrom([.3, .5, -.8], [1, .1, .25]);
const O_STAND = basisFrom([0, 1, 0], [0, 0, -1]);

function pose(t) {
  const orient = keyOrient(t, [[T0, O_LIE], [38.15, O_LIE], [39.25, O_MID, 'io2'], [40.35, O_STAND, 'out2']]);
  const pelvis = key(t, [[T0, [0, -19, 30]], [37.9, [6, -19, 28]], [38.75, [52, -18, 20], 'in2'], [39.35, [95, -42, 8], 'lin'], [40.35, [104, -84, -8], 'out2'], [44.1, [104, -84, -8]]]);
  // breathing sway once standing
  const sway = t > 40.3 ? Math.sin((t - 40.3) * 2.2) * .6 : 0; pelvis[0] += sway;
  // left (reaching) hand
  const hlP = key(t, [[T0, [27, -30, 44]], [T0 + .25, [27, -30, 44]], [34.95, [20, -8, -8], 'io2'], [35.55, [23, -10.5, -6], 'io2'], [36.35, [27, -9.0, -7], 'io2'], [36.95, [52, -8.5, -9], 'io2'], [37.45, [74, -5, -10], 'io2'], [37.85, [83.5, 4.2, -10], 'out2'], [38.95, [84, 1.5, -10]], [39.45, [118, -30, -16], 'in2'], [40.35, [125, -40, -10], 'out2']]);
  const d1 = { fwd: [0, 0, 1], nrm: [0, 1, 0] };
  const d2 = { fwd: [0, .78, -.62], nrm: [.25, -.6, -.75] };
  const d3 = { fwd: [.12, 1, .05], nrm: [1, -.08, 0] };
  const d4 = { fwd: [-1, -.32, 0], nrm: [-.25, 1, 0] };
  const lerpD = (a, b, u) => ({ fwd: norm(C.lerp3(a.fwd, b.fwd, u)), nrm: norm(C.lerp3(a.nrm, b.nrm, u)) });
  let dirs;
  if (t < 34.95) dirs = lerpD(d1, d2, ss(inv(T0 + .2, 34.95, t)));
  else if (t < 35.55) dirs = lerpD(d2, d3, ss(inv(34.95, 35.55, t)));
  else if (t < 37.45) dirs = d3;
  else if (t < 37.85) dirs = lerpD(d3, d4, ss(inv(37.45, 37.85, t)));
  else if (t < 38.9) dirs = d4;
  else dirs = null;
  const curlL = key(t, [[T0, .35], [34.95, .05], [35.55, .18], [36.35, .28], [37.45, .2], [37.85, .62], [38.9, .66], [39.5, .3], [40.4, .35]]);
  const spread = key(t, [[T0, .2], [34.95, .85], [35.55, .5], [37.45, .4], [37.85, .25]]);
  const hl = { p: hlP, pose: { curl: [curlL, curlL * 1.05, curlL * 1.1, curlL * 1.15], spread, thumb: { curl: .25, out: t < 37.5 ? .6 : .3, opp: t > 37.6 && t < 39 ? .7 : .2 } } };
  if (dirs) hl.dirs = dirs; else hl.roll = .3;
  // right hand: at side, then grips the edge too, then relaxes; on "Take" it stays low
  const hrP = key(t, [[T0, [-27, -30, 44]], [38.2, [-25, -30, 40]], [38.7, [70, -4, 14], 'io2'], [38.95, [83, 3, 12], 'out2'], [39.3, [84, 2, 12]], [40.35, [84, -40, 2], 'out2']]);
  const hr = { p: hrP, pose: { curl: t > 38.9 && t < 39.5 ? [.6, .62, .65, .7] : .32, spread: .2 } };
  if (t > 38.9 && t < 39.45) hr.dirs = { fwd: [-1, -.3, .1], nrm: [-.2, 1, 0] };
  // E & F: standing poses (relative to final frame)
  if (t > 40.3) {
    const F = { o: pelvis, ...O_STAND };
    const up = eOut(inv(TK - .12, TK + .5, t)); const pre = ss(inv(41.4, 42.1, t));
    hl.p = C.fx(F, 24 + up * 6, lerp(-44, -44, 0) + pre * 6 + up * 78, 6 + up * 22); delete hl.dirs; hl.roll = lerp(.3, -1.4, up); hl.flex = up * -.3;
    hl.pose = { curl: lerp(.35, .12, up), spread: lerp(.2, .7, up), thumb: { curl: .2, out: .5 } };
    hr.p = C.fx(F, -22, -47 + pre * 3, 5); delete hr.dirs;
  }
  const head = {
    yaw: key(t, [[T0, 0], [39.2, 0], [40.3, -.15], [41.6, .05], [TK, .1]]), pitch: key(t, [[T0, .08], [38.5, .1], [40.3, -.18], [41.7, -.22], [TK, .12, 'out2'], [T1, .16]]),
    roll: key(t, [[T0, 0], [35.6, -.12], [37.5, .05], [39.2, -.1], [40.3, 0]]),
    E: { blink: blinkAt(t, [34.2, 37.2, 41.2, 43.4]), gaze: t < 39 ? [.15, .35] : [0, .2], brow: { frown: t < 38.5 ? .4 : .1, raise: t > TK ? .4 : 0 }, mouth: { open: t > 38.4 && t < 39.4 ? .25 : (t > TK - .15 ? .55 : 0), smile: 0 } },
  };
  const twist = key(t, [[T0, 0], [38.4, 0], [39.1, .45], [40.3, 0]]);
  const lean = key(t, [[T0, 0], [38.5, .15], [39.4, .25], [40.3, .02], [41.8, .06], [TK, -.05]]);
  return { pelvis, orient, hl, hr, head, twist, lean };
}
function blinkAt(t, list) { for (const b of list) { const u = (t - b) / .14; if (u > 0 && u < 1) return Math.sin(u * Math.PI); } return 0; }

function camAt(t) {
  const pos = key(t, [[T0, [10, 104, -10]], [34.95, [17, 80, -10], 'io2'], [35.95, [80, 30, 16], 'io2'], [36.6, [84, 27, 14], 'io2'], [37.35, [118, 24, 24], 'io2'], [37.95, [126, 30, 32], 'io2'], [38.9, [152, 6, 62], 'io2'], [40.35, [134, -2, 62], 'io2'], [TK, [130, -6, 50], 'io2'], [T1, [150, 18, 128], 'out2']]);
  const look = key(t, [[T0, [10, 0, -6]], [34.95, [18, 0, -8], 'io2'], [35.95, [25, 1, -7], 'io2'], [36.6, [30, 1, -8], 'io2'], [37.35, [74, 0, -10], 'io2'], [37.95, [77, 1, -10], 'io2'], [38.9, [96, -22, -6], 'io2'], [40.35, [60, -34, -300], 'io2'], [TK, [60, -40, -300], 'io2'], [T1, [60, -150, -900], 'out2']]);
  const up = key(t, [[T0, [0, 0, -1]], [34.95, [0, .05, -1]], [35.95, [0, 1, -.1], 'io2'], [36.6, [0, 1, 0]]]);
  const fov = key(t, [[T0, 50], [34.95, 50], [35.95, 42], [37.35, 40], [38.9, 46], [40.35, 50], [TK, 50], [T1, 57, 'out2']]);
  return new C.Cam({ pos, look, up: norm(up), fov });
}

// ---------- paper texture (pencil drawing of the rig, ortho top-down) ----------
let TX = null, TXG = null;
const orthoCam = new C.Cam({ pos: [0, 1e5, 0], look: [0, 0, 0], up: [0, 0, -1], vw: TXW, vh: TXH, F: PXC * 1e5 });
function paperTexture(t, R, tipsInfo) {
  if (!TX) { TX = C.createCanvas(TXW, TXH); TXG = TX.getContext('2d'); }
  const g = TXG; const base = Pr.paperTex('animpaper', TXW, TXH, (g2, w, h) => {
    const gr = g2.createRadialGradient(w / 2, h * .55, 50, w / 2, h * .55, h * .75); gr.addColorStop(0, 'rgba(255,248,230,0)'); gr.addColorStop(1, 'rgba(150,130,100,.18)'); g2.fillStyle = gr; g2.fillRect(0, 0, w, h);
    g2.fillStyle = '#2c2a2e'; g2.fillRect(0, 0, w, 34); for (const x of [w / 2 - 200, w / 2, w / 2 + 200]) { g2.fillStyle = '#e9e3d6'; g2.beginPath(); g2.roundRect(x - (x === w / 2 ? 14 : 34), 10, x === w / 2 ? 28 : 68, 16, 8); g2.fill(); }
    g2.fillStyle = 'rgba(60,60,70,.55)'; g2.font = '28px CapSemi'; g2.fillText('SC 12   47', w - 210, h - 30);
    g2.strokeStyle = 'rgba(80,110,160,.10)'; g2.lineWidth = 2; g2.strokeRect(60, 70, w - 120, h - 140);
  });
  g.drawImage(base, 0, 0);
  // backlit shadow of the hand approaching from beneath
  for (const tp of tipsInfo) {
    if (tp.y > 1) continue; const k = clamp(1 - (-tp.y) / 9) * .55; if (k <= 0) continue;
    const q = orthoCam.p([tp.x, 0, tp.z]); const r = 18 + (-tp.y) * 4;
    const gr = g.createRadialGradient(q.x, q.y, 0, q.x, q.y, r); gr.addColorStop(0, `rgba(70,55,50,${k})`); gr.addColorStop(1, 'rgba(70,55,50,0)'); g.fillStyle = gr; g.fillRect(q.x - r, q.y - r, 2 * r, 2 * r);
  }
  const save = { ...I.ST }; I.ST.mode = 'pencil'; I.ST.inkW = 2.2; I.ST.boil = 1.0; I.ST.toLight = [-.5, -.85]; I.ST.pencilW = 1.9;
  g.save(); g.globalAlpha = 1 - ss(inv(39.0, 39.9, t)); B.drawRig(g, orthoCam, R, { lw: 2.2 }); g.restore();
  Object.assign(I.ST, save);
  return TX;
}

// paper deformation
function paperY(x, z, t, tips, bow) {
  let y = 0;
  for (const tp of tips) { if (tp.push <= 0) continue; const r2 = (x - tp.x) ** 2 + (z - tp.z) ** 2; y += tp.push * Math.exp(-r2 / (2 * 2.6 * 2.6)); }
  if (bow.h > 0) { const r2 = (x - bow.x) ** 2 + (z - bow.z) ** 2; y += bow.h * Math.exp(-r2 / (2 * 26 * 26)); }
  return y;
}
function paperGeom(t, tips, bow) {
    return (x, z) => {
    let y = paperY(x, z, t, tips, bow);
    // edge lift where his hand pulls (local around grip), then peel
    const edgeK = clamp((x - 40) / 35) * Math.exp(-((z + 6) ** 2) / (2 * 40 * 40));
    const ov = clamp((x - 62) / 13); // overhang beyond the table edge
    const weight = key(t, [[37.75, 0], [37.95, 2.5], [38.4, 3], [38.95, 11, 'in2'], [39.3, 13]]) - (t > 39.3 ? 13 * (1 - Math.exp(-(t - 39.3) * 5) * Math.cos((t - 39.3) * 22)) : 0);
    y -= ov * ov * Math.max(-2, weight) * Math.exp(-((z + 6) ** 2) / (2 * 34 * 34));
    y += edgeK * key(t, [[37.6, 0], [38.0, 1.5], [38.6, 0]]);
    return [x, y, z];
  };
}
function samples(lo, hi, n, focus, fw, fn) { const s = new Set(); for (let i = 0; i <= n; i++) s.add(+(lo + (hi - lo) * i / n).toFixed(2)); if (focus != null) for (let i = 0; i <= fn; i++) { const v = focus - fw + 2 * fw * i / fn; if (v > lo && v < hi) s.add(+v.toFixed(2)); } return [...s].sort((a, b) => a - b); }

function drawPaper(g, cam, tex, geo, t, focus) {
  const xs = samples(-PW, PW, 18, focus ? focus[0] : null, 12, 26), zs = samples(-PL, PL, 28, focus ? focus[1] : null, 12, 26);
  const V = zs.map(z => xs.map(x => { const p = geo(x, z); return { p, q: cam.p(p), u: (x + PW) * PXC, v: (z + PL) * PXC }; }));
  const L = norm([-.35, 1, .3]); const flat = dot([0, 1, 0], L);
  const alpha = 1 - ss(inv(39.9, 40.35, t));
  g.save(); g.globalAlpha = alpha;
  const tris = [];
  for (let j = 0; j < zs.length - 1; j++) for (let i = 0; i < xs.length - 1; i++) {
    const a = V[j][i], b = V[j][i + 1], c = V[j + 1][i + 1], d = V[j + 1][i];
    tris.push([a, b, c], [a, c, d]);
  }
  const shade = [];
  for (const T of tris) {
    const n = norm(C.cross(sub(T[1].p, T[0].p), sub(T[2].p, T[0].p))); const nn = n[1] < 0 ? mul(n, -1) : n;
    const facing = dot(n, sub(cam.pos, T[0].p));
    Pr.tri(g, tex, T.map(v => [v.q.x, v.q.y]), T.map(v => [v.u, v.v]));
    const dl = dot(nn, L) - flat; const under = facing < 0 ? 1 : 0;
    if (Math.abs(dl) > .01 || under) shade.push([T, dl, under]);
  }
  for (const [T, dl, under] of shade) {
    g.fillStyle = under ? 'rgba(40,30,40,.12)' : dl < 0 ? `rgba(60,40,50,${Math.min(.55, -dl * 1.6)})` : `rgba(255,250,235,${Math.min(.5, dl * 1.4)})`;
    g.beginPath(); g.moveTo(T[0].q.x, T[0].q.y); g.lineTo(T[1].q.x, T[1].q.y); g.lineTo(T[2].q.x, T[2].q.y); g.closePath(); g.fill();
  }
  g.restore();
  // outline of paper
  const edge = [];
  xs.forEach((x, i) => edge.push(V[0][i])); zs.forEach((z, j) => edge.push(V[j][xs.length - 1])); for (let i = xs.length - 1; i >= 0; i--) edge.push(V[zs.length - 1][i]); for (let j = zs.length - 1; j >= 0; j--) edge.push(V[j][0]);
  const poly = edge.map(v => [v.q.x, v.q.y]);
  if (alpha > .02) { g.save(); g.globalAlpha = alpha; g.strokeStyle = 'rgba(40,34,30,.55)'; g.lineWidth = 2; g.beginPath(); I.poly(g, poly); g.stroke(); g.restore(); }
  return { poly, alpha };
}

function drawBackdrop(g, cam, t) {
  // light-table room fading to the stage world
  const room = 1 - ss(inv(38.9, 40.0, t));
  const W = C.W, H = C.H;
  g.fillStyle = '#07060a'; g.fillRect(0, 0, W, H);
  if (room > 0) {
    g.save(); g.globalAlpha = room;
    const vq = cam.p([150, -170, -20]); I.glow(g, vq.x, vq.y, 1300, '#3f6fe0', .28 * ss(inv(35.5, 37.2, t)), 'lighter');
    const q = E.quad(g, cam, [[-260, -1, -320], [62, -1, -320], [62, -1, 320], [-260, -1, 320]], '#2a221c');
    E.quad(g, cam, [[62, -1, -320], [62, -1, 320], [62, -8, 320], [62, -8, -320]], '#140f0c');
    // glass glow around paper edges
    const c = cam.p([0, 0, 0]); I.glow(g, c.x, c.y, 900 * c.s / 2.2, '#ffe6b8', .25, 'lighter');
    E.lines3(g, cam, [[[-260, -.9, -140], [62, -.9, -140]], [[-260, -.9, 140], [62, -.9, 140]]], '#3a2f26', 2, .8);
    g.restore();
  }
  const stage = ss(inv(38.6, 40.0, t));
  if (stage > 0) stageWorld(g, cam, t, stage);
}
function stageWorld(g, cam, t, k) {
  const lit = t >= TK ? 1 : 0; const flash = t >= TK ? Math.exp(-(t - TK) / .35) : 0;
  const pre = ss(inv(41.3, 42.2, t)) * (1 - lit);
  g.save(); g.globalAlpha = k;
  const sky = g.createLinearGradient(0, 0, 0, C.H); sky.addColorStop(0, lit ? '#1a0f38' : '#04040a'); sky.addColorStop(.45, lit ? '#5a2c6e' : '#080a18'); sky.addColorStop(.7, lit ? '#2a1640' : '#05060e'); sky.addColorStop(1, '#040308');
  g.fillStyle = sky; g.fillRect(0, 0, C.W, C.H);
  if (lit) { // distant tiers of light points
    const r = C.rng(5); for (let i = 0; i < 500; i++) { const x = (r() - .5) * 9000, z = -5200 - r() * 800, y = -200 + r() * 900; const q = cam.p([x, y, z]); if (q.x < 0 || q.x > C.W) continue; g.fillStyle = `rgba(255,${200 + r() * 55 | 0},${170 + r() * 80 | 0},${.25 + .5 * Math.abs(Math.sin(t * 3 + i))})`; g.fillRect(q.x, q.y, 2.4, 2.4); }
  }
  const wash = (x, z) => { const a = Math.sin(x * .0011 + t * .9) * .5 + .5, b = Math.sin(x * .0007 - t * .6 + 2) * .5 + .5; return I.mix(I.mix('#ffb070', '#7fb4ff', a), '#ff6fa0', b * .4); };
  E.crowd2(g, cam, { x0: -3200, x1: 3400, z0: -430, z1: -5200, y: -330, n: 4200, seed: 21, zPow: 1.9, fogCol: lit ? '#7a4a90' : '#03040a', fogNear: 400, fogFar: 4800, lit: lit ? 1 : .07 + pre * .08, wash: lit ? wash : null, arms: lit ? .62 : .2, energy: lit ? 1 : .15, t, rim: lit ? '#ffe2b8' : '#5a7fc0', rimA: lit ? .45 : .14 + pre * .16, ink: true, faces: lit });
  // stage floor & front edge
  E.quad(g, cam, [[-480, -180, -60], [560, -180, -60], [560, -180, 460], [-480, -180, 460]], lit ? '#1a1420' : '#09080d');
  E.quad(g, cam, [[-480, -180, -60], [560, -180, -60], [560, -330, -60], [-480, -330, -60]], '#050407');
  E.lines3(g, cam, [[[-480, -179.5, -60], [560, -179.5, -60]]], lit ? '#ffcf9a' : '#3a5590', 1.4, lit ? .9 : .6);
  const lamps = [[-320, 150, -90], [-120, 165, -100], [80, 168, -100], [280, 165, -100], [460, 150, -90]];
  if (lit) {
    E.haze(g, '#b07ac8', .2, C.H * .2, C.H * .75);
    lamps.forEach((L, i) => { const sw = Math.sin(t * (1.1 + i * .23) + i * 1.7) * 700; E.beam3(g, cam, L, [L[0] * 3 + sw, -330, -1800 - i * 500], .06, ['#ffd7a0', '#9fd0ff', '#ff7aa8', '#ffe7c4', '#b49bff'][i], .3 + flash * .45); });
  } else {
    E.haze(g, '#1c2c55', .16 + pre * .2, C.H * .3, C.H * .85);
    const q = cam.p([104, 400, -10]); E.beam(g, q.x, q.y, 0, 1500, .12, '#5d86d8', .22 + pre * .12);
  }
  g.restore();
  return flash;
}
function draw(g, t) {
  const P = pose(t); const cam = camAt(t);
  const R = B.rig('morten', '80s', { pelvis: P.pelvis, orient: P.orient, hl: P.hl, hr: P.hr, head: P.head, twist: P.twist, lean: P.lean });
  // fingertip info for the paper (from left hand)
  const A = R.arms.l; const hand = Hn.buildHand({ w: A.W, fwd: A.fwd, nrm: A.nrm, th: A.th, scale: .95 * R.k, side: 1 }, A.pose);
  const tips = [0, 1, 2, 3, 4].map(i => { const p = Hn.tip(hand, i); return { x: p[0], y: p[1], z: p[2], push: (t > 35.2 && t < 37.3) ? clamp(p[1] + .9, 0, 2.3) : 0 }; });
  const pc = mul(tips.slice(0, 4).reduce((a, b) => add(a, [b.x, b.y, b.z]), [0, 0, 0]), .25);
  const bow = { x: pc[0], z: pc[2], h: key(t, [[35.2, 0], [35.9, 3.5], [36.6, 5.2], [37.3, 2.5], [37.9, 1.2]]) };
  drawBackdrop(g, cam, t);
  // blue stage light leaking in from beyond the edge
  const leak = ss(inv(36.7, 37.7, t)) * (1 - ss(inv(39.6, 40.3, t)));
  if (leak > 0) { const q = cam.p([140, -120, -20]); I.glow(g, q.x, q.y, 1000, '#4f8dff', .32 * leak, 'lighter'); }
  let paper = null;
  if (t < 40.35) {
    const tex = paperTexture(t, R, tips);
    paper = drawPaper(g, cam, tex, paperGeom(t, tips, bow), t, [pc[0], pc[2]]);
  }
  // colour Morten: hands above the paper always; body only outside the sheet
  const L2 = cam.p([140, -120, -20]);
  const lightDir = (q) => { const dx = L2.x - q.x, dy = L2.y - q.y, l = Math.hypot(dx, dy) || 1; return [dx / l, dy / l]; };
  const save = { ...I.ST };
  I.ST.mode = 'color'; I.ST.inkW = 3.2;
  const showHand = t > 37.42; const showBody = t > 38.05;
  const stageLit = t >= TK;
  if (t > 40.3) { I.ST.toLight = stageLit ? [-.25, -.97] : [.4, -.9]; I.ST.shadowTint = stageLit ? '#2a2350' : '#101a3a'; I.ST.shadeMix = stageLit ? .4 : .62; I.ST.rim = { color: stageLit ? '#ffd6a8' : '#6fb2ff', dir: stageLit ? [0, -1] : [.6, -.8], w: 3.5, a: .9 }; }
  else { const q = cam.p(A.W); I.ST.toLight = lightDir(q); I.ST.shadowTint = '#1a2550'; I.ST.shadeMix = .55; I.ST.rim = { color: '#7cc0ff', dir: I.ST.toLight, w: 4.5, a: .95 }; }
  if (showBody && t < 40.35 && paper) {
    g.save(); I.clipOutside(g, paper.poly, false); B.drawRig(g, cam, R, { noHands: true }); g.restore();
  } else if (t >= 40.35) {
    B.drawRig(g, cam, R, {});
  }
  if (showHand && t < 40.35) {
    // forearm beyond the edge in colour, then the hand
    if (!showBody && paper) { g.save(); I.clipOutside(g, paper.poly, false); B.drawRig(g, cam, R, { noHands: true, noLegs: true, noHead: true }); g.restore(); }
    Hn.drawHand(g, cam, hand, { skin: '#efc4a2' });
    if (t > 38.85) { const Ar = R.arms.r; const h2 = Hn.buildHand({ w: Ar.W, fwd: Ar.fwd, nrm: Ar.nrm, th: Ar.th, scale: .95 * R.k, side: -1 }, Ar.pose); Hn.drawHand(g, cam, h2, { skin: '#efc4a2' }); }
  }
  Object.assign(I.ST, save);
  // stage flash on "Take"
  if (t >= TK) { const f = Math.exp(-(t - TK) / .3); g.fillStyle = `rgba(255,240,225,${f * .55})`; g.fillRect(0, 0, C.W, C.H); }
  if (t < 33.62) { // the animator's hand settles the sheet and leaves frame
    const u = ss(inv(33.04, 33.6, t)); const w = [lerp(30, 70, u), lerp(5, 40, u), lerp(-20, 60, u)];
    const h = Hn.buildHand({ w, fwd: norm([-.5, -.25, -.8]), nrm: [0, 1, 0], th: norm([1, 0, -.6]), scale: .9, side: -1 }, { curl: [.25, .3, .35, .4], spread: .25, thumb: { curl: .2, opp: .6 } });
    const save = { ...I.ST }; I.ST.mode = 'color'; I.ST.rim = null; Hn.drawHand(g, cam, h, { skin: '#f2cbb0', sleeve: { col: '#f2ece0', r: 4.0, len: 22, cuff: '#c4a385' } }); Object.assign(I.ST, save);
  }
  I.vignette(g, t < 39 ? .55 : .62);
}
module.exports = { t0: 33.04, t1: T1, name: 'crossing', draw };
