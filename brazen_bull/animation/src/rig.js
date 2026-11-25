// RIG: full-body articulated character (Nikias) for V2.
// 2D skeleton, 3/4 view facing screen-left. Units match head34 (head ~410 tall).
// Angle convention: a limb with angle a points along (sin a, cos a): a=0 straight down, a<0 toward -x (forward).
'use strict';

const RIG = { torso: 540, uarm: 330, farm: 300, thigh: 540, shin: 500, foot: 230, G: 1060 };
const dirv = (a) => [Math.sin(a), Math.cos(a)];
const addv = (p, a, L) => [p[0] + Math.sin(a) * L, p[1] + Math.cos(a) * L];
const ang = (A, B) => Math.atan2(B[0] - A[0], B[1] - A[1]);
// 2-bone IK: returns [absAngle1, absAngle2, elbow]
function ik2(B, T, L1, L2, bend) {
  let dx = T[0] - B[0], dy = T[1] - B[1]; let d = Math.hypot(dx, dy);
  const dmax = L1 + L2 - 0.5, dmin = Math.abs(L1 - L2) + 1;
  if (d > dmax) { dx *= dmax / d; dy *= dmax / d; d = dmax; } if (d < dmin) { dx *= dmin / d; dy *= dmin / d; d = dmin; }
  const th = Math.atan2(dx, dy);
  const al = Math.acos(clamp((L1 * L1 + d * d - L2 * L2) / (2 * L1 * d), -1, 1));
  const a1 = th + bend * al; const E = addv(B, a1, L1); const a2 = Math.atan2(B[0] + dx - E[0], B[1] + dy - E[1]);
  return [a1, a2, E];
}
// ---------------------------------------------------------------- pose model (targets + IK)
// pose: x,y root ; spine ; head ; headX
//  nT,fT : hand targets [x,y] in figure space (or {h:[x,y]} = point in head space, {c:[x,y]} = chest space)
//  nB,fB : elbow bend sign ; nF,fF : foot targets ; nKB,fKB knee bend ; nFa,fFa foot angle (abs)
//  nHand,fHand ; nWa,fWa hand angle offsets ; frontArm
const G = RIG.G;
const POSES = {
  stand: { spine: -0.03, head: 0.02, nT: { c: [250, 600] }, nB: -1, fT: { c: [-200, 600] }, fB: -1, nF: [40, G], fF: [-90, G], nFa: -1.5, fFa: -1.5, nHand: 'relax', fHand: 'relax' },
  push: { x: 60, spine: -0.3, head: 0.22, nT: [-560, -620], nB: 1, fT: [-600, -480], fB: 1, nF: [-30, G], fF: [260, G], nFa: -1.5, fFa: -1.15, nHand: 'press', fHand: 'press', nWa: 0.4, fWa: 0.5 },
  wipe: { spine: 0.05, head: -0.25, nT: { h: [-90, -150] }, nB: 1, fT: { c: [-160, 560] }, fB: -1, nF: [30, G], fF: [-120, G], nFa: -1.5, fFa: -1.5, nHand: 'flat', fHand: 'relax', frontArm: true, nWa: 1.4 },
  gasp: { spine: 0.18, head: -0.5, nT: { c: [330, 520] }, nB: -1, fT: { c: [-250, 520] }, fB: -1, nF: [60, G], fF: [-110, G], nFa: -1.5, fFa: -1.5, nHand: 'splay', fHand: 'splay' },
  brace: { x: 40, spine: -0.32, head: 0.3, nT: [-520, -380], nB: 1, fT: { c: [-40, 520] }, fB: -1, nF: [10, G], fF: [240, G], nFa: -1.5, fFa: -1.2, nHand: 'press', fHand: 'fist', nWa: 0.4 },
  kneel: { y: 500, spine: -0.55, head: 0.55, nT: [-260, 470], nB: -1, fT: [-470, G - 10], fB: 1, nF: [-330, G], fF: [470, G - 20], nKB: 1, fKB: 1, nFa: -1.5, fFa: -0.1, nHand: 'relax', fHand: 'press', fWa: 0.9 },
  temples: { spine: -0.1, head: 0.3, nT: { h: [-120, -60] }, nB: 1, fT: { h: [60, -80] }, fB: 1, nF: [70, G], fF: [-150, G], nFa: -1.5, fFa: -1.4, nHand: 'claw', fHand: 'claw', frontArm: true, nWa: 1.8, fWa: 1.5 },
  slump: { y: 930, x: 120, spine: 0.36, head: -0.4, nT: [-120, 1010], nB: -1, fT: [60, 1030], fB: -1, nF: [-760, G], fF: [-620, G - 10], nKB: 1, fKB: 1, nFa: -1.0, fFa: -1.1, nHand: 'relax', fHand: 'relax' },
  reach: { spine: 0.06, head: -0.6, nT: [-330, -1150], nB: 1, fT: { c: [-200, 600] }, fB: -1, nF: [40, G], fF: [-120, G], nFa: -1.5, fFa: -1.5, nHand: 'splay', fHand: 'relax', nWa: 0.2 },
  sink: { y: 260, spine: -0.35, head: 0.45, nT: [-300, 200], nB: -1, fT: [-80, 260], fB: -1, nF: [-150, G], fF: [160, G], nKB: 1, fKB: 1, nFa: -1.5, fFa: -1.4, nHand: 'relax', fHand: 'claw' },
};
const POSE_NUM = ['x', 'y', 'spine', 'head', 'headX', 'nB', 'fB', 'nKB', 'fKB', 'nFa', 'fFa', 'nWa', 'fWa'];
function poseOf(name) { return Object.assign({ x: 0, y: 0, headX: 0, nKB: 1, fKB: 1, nWa: 0, fWa: 0 }, typeof name === 'string' ? POSES[name] : name); }
// resolve a target spec into figure space for a given (root, spine, head)
function resolveT(T, p) {
  if (Array.isArray(T)) return T;
  const root = [p.x || 0, p.y || 0], chest = addv(root, Math.PI + p.spine, RIG.torso);
  const R = (base, a, v) => [base[0] + v[0] * Math.cos(a) + v[1] * Math.sin(a), base[1] - v[0] * Math.sin(a) + v[1] * Math.cos(a)];
  if (T.c) return R(chest, p.spine, T.c);
  if (T.h) { const neck = R(chest, p.spine, [30, -40]); return R(neck, p.spine + p.head, [T.h[0] - 40, T.h[1] - 250]); }
  return [0, 0];
}
function blendPose(a, b, k) {
  const A = poseOf(a), B = poseOf(b), o = Object.assign({}, k < 0.5 ? A : B);
  for (const key of POSE_NUM) o[key] = lerp(A[key] ?? 0, B[key] ?? 0, k);
  for (const key of ['nT', 'fT']) { const ta = resolveT(A[key], A), tb = resolveT(B[key], B); o[key] = [lerp(ta[0], tb[0], k), lerp(ta[1], tb[1], k)]; }
  for (const key of ['nF', 'fF']) o[key] = [lerp(A[key][0], B[key][0], k), lerp(A[key][1], B[key][1], k)];
  o.handMix = { n: [A.nHand, B.nHand, k], f: [A.fHand, B.fHand, k] };
  o.frontArm = k < 0.5 ? A.frontArm : B.frontArm;
  o.face = A.face || B.face; for (const kk of ['costume', 'spec', 'prop', 'prop2', 'propBehind']) o[kk] = A[kk] ?? B[kk];
  return o;
}
function poseAt(t, keysArr) {
  if (t <= keysArr[0][0]) return blendPose(keysArr[0][1], keysArr[0][1], 0);
  for (let i = 1; i < keysArr.length; i++) if (t < keysArr[i][0]) {
    const [t0, p0] = keysArr[i - 1], [t1, p1, e] = keysArr[i];
    return blendPose(p0, p1, (e || ease.io3)((t - t0) / (t1 - t0)));
  }
  const l = keysArr[keysArr.length - 1][1]; return blendPose(l, l, 1);
}
// secondary motion: breathing, tremble, head drift (pure function of t)
function secondary(p, t, o = {}) {
  const br = o.breath ?? 1, tr = o.tremble ?? 0, rate = o.rate ?? 2.6;
  const b = Math.sin(t * rate) * br;
  const q = Object.assign({}, p);
  q.spine += b * 0.014; q.head += -b * 0.025 + Math.sin(t * 1.3) * 0.02 * (o.drift ?? 1);
  const jit = (s) => [vnoise(t * 9 + s) * tr * 14, vnoise(t * 9 + s + 50) * tr * 14];
  const jn = jit(1), jf = jit(7);
  q.nT = [q.nT[0] + jn[0], q.nT[1] + jn[1] - b * 8]; q.fT = [q.fT[0] + jf[0], q.fT[1] + jf[1] - b * 6];
  q.y = (q.y || 0) - b * 4;
  q.breath = b; q.tremble = tr;
  return q;
}

// ---------------------------------------------------------------- forward / inverse kinematics
function fk(p) {
  const root = [p.x || 0, p.y || 0];
  const chest = addv(root, Math.PI + p.spine, RIG.torso);
  const rot = (base, dx, dy) => [base[0] + dx * Math.cos(p.spine) + dy * Math.sin(p.spine), base[1] - dx * Math.sin(p.spine) + dy * Math.cos(p.spine)];
  const nSh = rot(chest, 215, 40), fSh = rot(chest, -165, 46), neck = rot(chest, 30, -40);
  const nHip = rot(root, 95, 10), fHip = rot(root, -80, 0);
  const [nS, nF2, nElb] = ik2(nSh, p.nT, RIG.uarm, RIG.farm, p.nB ?? -1);
  const [fS, fF2, fElb] = ik2(fSh, p.fT, RIG.uarm * 0.96, RIG.farm * 0.96, p.fB ?? -1);
  const nWr = addv(nElb, nF2, RIG.farm), fWr = addv(fElb, fF2, RIG.farm * 0.96);
  const [nH, nSn, nKn] = ik2(nHip, p.nF, RIG.thigh, RIG.shin, -(p.nKB ?? 1));
  const [fH, fSn, fKn] = ik2(fHip, p.fF, RIG.thigh * 0.97, RIG.shin * 0.97, -(p.fKB ?? 1));
  const nAn = addv(nKn, nSn, RIG.shin), fAn = addv(fKn, fSn, RIG.shin * 0.97);
  return { root, chest, neck, nSh, fSh, nElb, nWr, fElb, fWr, nHip, fHip, nKn, nAn, fKn, fAn, rot, a: { nS, nF2, fS, fF2, nH, nSn, fH, fSn } };
}

// ---------------------------------------------------------------- limb rendering
function limb(g, C, A, B, wA, wB, opt = {}) {
  const dx = B[0] - A[0], dy = B[1] - A[1], L = Math.hypot(dx, dy) || 1, ux = dx / L, uy = dy / L, nx = -uy, ny = ux;
  const bulge = opt.bulge ?? 0.1, bp = opt.bulgeAt ?? 0.38;
  const wm = lerp(wA, wB, bp) * (1 + bulge);
  const P = (u, w, s) => [A[0] + dx * u + nx * w / 2 * s, A[1] + dy * u + ny * w / 2 * s];
  const left = [P(0, wA, 1), P(bp, wm, 1), P(0.75, lerp(wA, wB, 0.75) * (1 + bulge * 0.4), 1), P(1, wB, 1)];
  const right = [P(1, wB, -1), P(0.72, lerp(wA, wB, 0.72) * (1 + bulge * (opt.bulge2 ?? 0.6)), -1), P(bp * 0.8, wm * 0.98, -1), P(0, wA, -1)];
  const pts = left.concat(right);
  g.fillStyle = opt.fill || C.skin; g.beginPath(); crPath(g, pts, true, 0.5); g.fill();
  g.beginPath(); g.arc(A[0], A[1], wA / 2, 0, 6.283); g.fill(); g.beginPath(); g.arc(B[0], B[1], wB / 2, 0, 6.283); g.fill();
  // form shading: shadow along the side away from the key light (screen-left key by default)
  const shadeSide = opt.shadeSide ?? (nx > 0 ? 1 : -1);
  softIn(g, pts, Math.max(4, wA * 0.18), () => {
    g.fillStyle = rgba(opt.dark || C.skinDk, opt.dk ?? 0.55);
    g.beginPath(); crPath(g, [P(0, wA, shadeSide * 1.1), P(0.5, wm, shadeSide * 1.1), P(1, wB, shadeSide * 1.1), P(1, wB * 0.2, shadeSide), P(0.5, wm * 0.25, shadeSide), P(0, wA * 0.2, shadeSide)], true); g.fill();
    g.fillStyle = rgba(opt.lite || C.skinLt, opt.lt ?? 0.4);
    g.beginPath(); crPath(g, [P(0.1, wA * 0.6, -shadeSide), P(0.5, wm * 0.7, -shadeSide), P(0.9, wB * 0.6, -shadeSide), P(0.5, wm * 0.15, -shadeSide)], true); g.fill();
  });
  if (opt.line !== false) { g.strokeStyle = rgba(C.line, 0.28); g.lineWidth = 2; g.beginPath(); crPath(g, left, false); g.stroke(); }
  return pts;
}

// ---------------------------------------------------------------- hands (back view, articulated fingers)
const HAND_POSES = {
  relax: { spread: 0.08, curl: [0.35, 0.42, 0.48, 0.55], thumb: 0.35 },
  flat: { spread: 0.04, curl: [0.05, 0.05, 0.06, 0.08], thumb: 0.2 },
  press: { spread: 0.2, curl: [-0.06, -0.04, -0.04, -0.02], thumb: 0.65 },
  splay: { spread: 0.28, curl: [0.12, 0.1, 0.12, 0.18], thumb: 0.8 },
  fist: { spread: 0.0, curl: [1.25, 1.3, 1.32, 1.35], thumb: 1.0 },
  point: { spread: 0.05, curl: [0.0, 1.2, 1.28, 1.32], thumb: 0.9 },
  grip: { spread: 0.0, curl: [1.0, 1.05, 1.1, 1.15], thumb: 0.9 },
  claw: { spread: 0.2, curl: [0.7, 0.75, 0.75, 0.8], thumb: 0.6 },
};
function handPose(mix) {
  const [a, b, k] = mix; const A = HAND_POSES[a] || HAND_POSES.relax, B = HAND_POSES[b] || HAND_POSES.relax;
  return { spread: lerp(A.spread, B.spread, k), curl: A.curl.map((c, i) => lerp(c, B.curl[i], k)), thumb: lerp(A.thumb, B.thumb, k) };
}
function hand(g, C, wrist, ang, hp, sc = 1, mirror = 1, tr = 0, t = 0) {
  g.save(); g.translate(wrist[0], wrist[1]); g.rotate(-ang); g.scale(sc * mirror, sc);
  const fingerL = [[50, 34, 26], [56, 38, 28], [52, 36, 27], [42, 28, 22]];
  const fw = [27, 28, 26, 22];
  const kx = [-36, -12, 12, 34];
  // palm (back of hand)
  const palm = [[-34, 0], [34, 0], [48, 60], [46, 112], [20, 124], [-12, 126], [-40, 116], [-50, 60]];
  // fingers
  for (let i = 3; i >= 0; i--) {
    let p = [kx[i], 112 + (i === 0 || i === 3 ? 4 : 10)], a = (i - 1.5) * hp.spread * -1;
    const curl = hp.curl[i] + vnoise(t * 13 + i * 3) * tr * 0.12;
    for (let s = 0; s < 3; s++) {
      a += curl * (s === 0 ? 0.6 : 0.85);
      const L = fingerL[i][s] * Math.max(0.35, 1 - Math.abs(curl) * 0.22 * (s + 1));
      const q = [p[0] + Math.sin(-a) * L, p[1] + Math.cos(a) * L];
      limb(g, C, p, q, fw[i] * (1 - s * 0.12), fw[i] * (0.88 - s * 0.12), { bulge: 0.02, line: false, dk: 0.4, lt: 0.3 });
      if (s === 2) { g.fillStyle = rgba('#f4d2b8', 0.6); g.beginPath(); g.ellipse(q[0] - Math.sin(-a) * 8, q[1] - Math.cos(a) * 8, fw[i] * 0.26, 7, -a, 0, 6.283); g.fill(); }
      p = q;
    }
  }
  g.fillStyle = C.skin; g.beginPath(); crPath(g, palm, true); g.fill();
  softIn(g, palm, 10, () => { g.fillStyle = rgba(C.skinLt, 0.5); g.beginPath(); g.ellipse(-8, 60, 30, 34, 0, 0, 6.283); g.fill();
    g.fillStyle = rgba(C.skinDk, 0.55); g.beginPath(); g.ellipse(46, 70, 14, 60, 0, 0, 6.283); g.fill(); });
  g.save(); g.globalAlpha = 0.35; for (const x of kx) brush(g, [[x * 0.5, 20], [x * 0.8, 70], [x, 110]], 5, 3, C.skinLt); g.restore();
  // thumb from the inner side
  const ta = 0.9 - hp.thumb * 0.9;
  let p = [-44, 44], a = ta;
  for (let s = 0; s < 2; s++) { const L = s ? 36 : 52; const q = [p[0] - Math.sin(a) * L, p[1] + Math.cos(a) * L]; limb(g, C, p, q, s ? 24 : 30, s ? 20 : 25, { bulge: 0.05, line: false, dk: 0.45 }); p = q; a += 0.35 + hp.thumb * 0.25; }
  g.restore();
}

// ---------------------------------------------------------------- chiton (cloth on the skeleton)
function chiton(g, C, J, p, t, lag) {
  const r = J.rot, sway = lag || 0;
  const belt = [lerp(J.root[0], J.chest[0], 0.2), lerp(J.root[1], J.chest[1], 0.2)];
  const rB = (dx, dy) => [belt[0] + dx * Math.cos(p.spine) + dy * Math.sin(p.spine), belt[1] - dx * Math.sin(p.spine) + dy * Math.cos(p.spine)];
  // skirt hangs with gravity from the hips; hem rides on the thighs and drapes over raised knees
  const hemOn = (hip, kn, side) => { const u = 0.7; const q = [lerp(hip[0], kn[0], u), lerp(hip[1], kn[1], u)]; return [q[0] + side * 70 + sway * 34, Math.max(q[1], belt[1] + 140) + 40]; };
  const hn = hemOn(J.nHip, J.nKn, 1), hf = hemOn(J.fHip, J.fKn, -1);
  const hmid = [(hn[0] + hf[0]) / 2 + sway * 40, Math.max(hn[1], hf[1]) + 26];
  const skirt = [rB(150, 20), [lerp(rB(170, 20)[0], hn[0], 0.5) + 30, lerp(rB(170, 20)[1], hn[1], 0.5)], hn, [lerp(hn[0], hmid[0], 0.5), lerp(hn[1], hmid[1], 0.5) + 14], hmid,
    [lerp(hf[0], hmid[0], 0.5), lerp(hf[1], hmid[1], 0.5) + 14], hf, [lerp(rB(-170, 20)[0], hf[0], 0.5) - 30, lerp(rB(-170, 20)[1], hf[1], 0.5)], rB(-160, 20)];
  const lit = linGrad(g, J.chest[0] - 260, J.chest[1], J.root[0] + 300, J.root[1] + 420, [[0, C.cloth], [1, C.clothDk]]);
  g.fillStyle = lit; g.beginPath(); crPath(g, skirt, true, 0.5); g.fill();
  g.save(); g.beginPath(); crPath(g, skirt, true, 0.5); g.clip();
  softIn(g, skirt, 22, () => { g.fillStyle = rgba(C.clothDk, 0.75); g.beginPath(); crPath(g, [rB(80, 60), hn, hmid, rB(0, 200)], true); g.fill(); });
  for (let i = 0; i < 7; i++) {
    const u = (i + 0.5) / 7, top = rB(lerp(-150, 150, u), 30), botx = lerp(hf[0], hn[0], u) + sway * 24, boty = lerp(hf[1], hn[1], u) + 30 + Math.sin(u * Math.PI) * 20;
    const mid = [lerp(top[0], botx, 0.5) + Math.sin(i * 2.1 + t * 0.6) * 8 + sway * 14, lerp(top[1], boty, 0.5)];
    g.filter = 'blur(6px)'; brush(g, curvePts([top, mid, [botx, boty]], 14), 24, 14, rgba(C.clothDk, 0.7), false);
    g.filter = 'blur(2px)'; brush(g, curvePts([top, mid, [botx, boty]], 14).map(([x, y]) => [x + 14, y]), 9, 5, rgba('#fff6e6', 0.16), false); g.filter = 'none';
  }
  g.restore();
  brush(g, curvePts([hf, [lerp(hf[0], hmid[0], 0.5), lerp(hf[1], hmid[1], 0.5) + 14], hmid, [lerp(hn[0], hmid[0], 0.5), lerp(hn[1], hmid[1], 0.5) + 14], hn], 30), 15, 15, C.border, false);
  // upper chiton: broad blouse with short sleeves over the upper arms, overhang (kolpos) above the belt
  const sleeve = (sh, el, side) => { const a = ang(sh, el), q = addv(sh, a, 150); const nx = Math.cos(a), ny = -Math.sin(a); return [[q[0] + nx * 92 * side, q[1] + ny * 92 * side], [q[0] - nx * 92 * side, q[1] - ny * 92 * side]]; };
  const [snA, snB] = sleeve(J.nSh, J.nElb, 1), [sfA, sfB] = sleeve(J.fSh, J.fElb, -1);
  const upper = [r(J.chest, -180, 10), r(J.chest, -70, -26), r(J.chest, 30, 4), r(J.chest, 140, -22), r(J.chest, 250, 30), snA, snB,
    r(J.chest, 200, 230), rB(190, -30), rB(200, 30), rB(0, 60), rB(-190, 30), rB(-180, -30), r(J.chest, -180, 230), sfB, sfA];
  g.fillStyle = lit; g.beginPath(); crPath(g, upper, true, 0.45); g.fill();
  g.save(); g.beginPath(); crPath(g, upper, true, 0.45); g.clip();
  softIn(g, upper, 22, () => { g.fillStyle = rgba(C.clothDk, 0.7); g.beginPath(); crPath(g, [r(J.chest, 140, 40), r(J.chest, 260, 60), r(J.chest, 200, 260), rB(160, 30)], true); g.fill();
    g.fillStyle = rgba('#ffffff', 0.14); g.beginPath(); crPath(g, [r(J.chest, -150, 40), r(J.chest, -20, 40), r(J.chest, -80, 200)], true); g.fill();
    g.fillStyle = rgba(C.clothDk, 0.6); g.beginPath(); g.ellipse(belt[0], belt[1] - 10, 220, 40, -p.spine, 0, 6.283); g.fill(); });
  for (let k = 0; k < 4; k++) { const a1 = r(J.chest, -150, 30), a2 = r(J.chest, 220, 34), m = r(J.chest, 40, 90 + k * 46);
    g.filter = 'blur(5px)'; brush(g, curvePts([a1, m, a2], 20), 20, 6, rgba(C.clothDk, 0.6)); g.filter = 'blur(2px)'; brush(g, curvePts([a1, m, a2], 20).map(([x, y]) => [x, y - 9]), 7, 2, rgba('#fff6e6', 0.14)); g.filter = 'none'; }
  g.restore();
  brush(g, curvePts([r(J.chest, -140, 22), r(J.chest, -40, 80), r(J.chest, 80, 84), r(J.chest, 210, 26)], 24), 12, 12, C.border, false);
  brush(g, curvePts([rB(-178, 4), rB(0, 18), rB(178, 4)], 20), 14, 14, '#5a3a1e', false);
  for (const [x, y] of [r(J.chest, -150, 28), r(J.chest, 220, 30)]) { g.fillStyle = '#9a6a2e'; g.beginPath(); g.arc(x, y, 12, 0, 6.283); g.fill(); g.fillStyle = '#e8b86a'; g.beginPath(); g.arc(x - 3, y - 3, 4, 0, 6.283); g.fill(); }
}

// ---------------------------------------------------------------- full figure
function legDraw(g, C, J, nearSide, footA) {
  const far = !nearSide;
  const hip = nearSide ? J.nHip : J.fHip, kn = nearSide ? J.nKn : J.fKn, an = nearSide ? J.nAn : J.fAn;
  const opt = far ? { dk: 0.75, lt: 0.2 } : {};
  limb(g, C, hip, kn, 200, 128, Object.assign({ bulge: 0.12 }, opt));
  limb(g, C, kn, an, 124, 76, Object.assign({ bulge: 0.2, bulgeAt: 0.28 }, opt));
  const toe = addv(an, footA, RIG.foot);
  limb(g, C, an, toe, 78, 50, Object.assign({ bulge: 0.04 }, opt));
  g.fillStyle = '#2e1a0c'; g.beginPath(); g.ellipse(lerp(an[0], toe[0], 0.45) + Math.cos(footA) * 0, lerp(an[1], toe[1], 0.45) + 34, RIG.foot * 0.66, 11, Math.atan2(toe[1] - an[1], toe[0] - an[0]), 0, 6.283); g.fill();
  brush(g, [[an[0] - 10, an[1] - 24], [lerp(an[0], toe[0], 0.5), lerp(an[1], toe[1], 0.5) - 2], [lerp(an[0], toe[0], 0.85), lerp(an[1], toe[1], 0.85) + 4]], 10, 8, '#4a2a14', false);
}
function armDraw(g, C, J, nearSide, hp, t, tr, wa, part = 'all') {
  const far = !nearSide;
  const sh = nearSide ? J.nSh : J.fSh, el = nearSide ? J.nElb : J.fElb, wr = nearSide ? J.nWr : J.fWr;
  const aF = nearSide ? J.a.nF2 : J.a.fF2;
  const opt = far ? { dk: 0.75, lt: 0.2 } : {};
  if (part !== 'fore') limb(g, C, sh, el, 150, 112, Object.assign({ bulge: 0.18, bulgeAt: 0.32 }, opt));
  limb(g, C, el, wr, 112, 74, Object.assign({ bulge: 0.16, bulgeAt: 0.25 }, opt));
  hand(g, far ? Object.assign({}, C, { skin: C.skin2 }) : C, wr, aF + (wa || 0), hp, 1.08, 1, tr, t);
}
function figure(g, C, p, t, opt = {}) {
  p = Object.assign({}, p);
  p.nT = resolveT(p.nT, p); p.fT = resolveT(p.fT, p);
  const J = fk(p);
  const lag = opt.lag ?? 0;
  const hpN = handPose(p.handMix ? p.handMix.n : [p.nHand, p.nHand, 0]), hpF = handPose(p.handMix ? p.handMix.f : [p.fHand, p.fHand, 0]);
  g.save(); g.lineJoin = 'round'; g.lineCap = 'round';
  if (p.costume === 'guard' && typeof guardCloak === 'function') guardCloak(g, C, J, p, t);
  armDraw(g, C, J, false, hpF, t, p.tremble || 0, p.fWa);
  if (p.prop2 && typeof drawProp === 'function') drawProp(g, C, p.prop2, J.fWr, J.a.fF2 + (p.fWa || 0), t);
  legDraw(g, C, J, false, p.fFa ?? -1.5);
  limb(g, C, J.chest, J.neck, 190, 170, { bulge: 0, line: false });
  legDraw(g, C, J, true, p.nFa ?? -1.5);
  chiton(g, C, J, p, t, lag);
  if (p.costume && typeof costumeOverlay === 'function') costumeOverlay(g, C, J, p, t, lag);
  const drawHead = () => { g.save(); g.translate(J.neck[0] + (p.headX || 0), J.neck[1]); g.rotate(-(p.spine + p.head)); g.translate(-40, -250);
    head34(g, C, Object.assign({ t }, p.face || {}, { spec: p.spec })); g.restore(); };
  const propN = () => { if (p.prop && typeof drawProp === 'function') drawProp(g, C, p.prop, J.nWr, J.a.nF2 + (p.propA || 0), t); };
  if (!p.frontArm) { drawHead(); if (p.propBehind) propN(); armDraw(g, C, J, true, hpN, t, p.tremble || 0, p.nWa); if (!p.propBehind) propN(); }
  else { armDraw(g, C, J, true, hpN, t, p.tremble || 0, p.nWa, 'upper'); drawHead(); armDraw(g, C, J, true, hpN, t, p.tremble || 0, p.nWa, 'fore'); }
  g.restore();
  return J;
}

// ---------------------------------------------------------------- tests: pose sheet
TESTS.poses = (ctx, t) => {
  ctx.fillStyle = linGrad(ctx, 0, 0, 0, H, [[0, '#2a1d14'], [1, '#0e0a08']]); ctx.fillRect(0, 0, W, H);
  const names = ['stand', 'push', 'wipe', 'gasp', 'brace', 'kneel', 'temples', 'slump', 'reach'];
  names.forEach((n, i) => {
    const x = 200 + (i % 3) * 350, y = 250 + Math.floor(i / 3) * 620, sc = 0.2;
    const p = secondary(blendPose(n, n, 0), t, { breath: 0.5 });
    p.face = { brow: 0.5, sweat: 0.6, look: [-0.3, 0] };
    litRender(ctx, (g, C) => { g.save(); g.translate(x, y); g.scale(sc, sc); figure(g, C, p, t); g.restore(); },
      (m) => radialMask(m, x - 60, y - 120, 30, 340, 0.95), { rim: { dx: 3, dy: 0, col: '#ffa860', a: 0.8 } });
    ctx.font = '700 22px Inter'; ctx.fillStyle = '#e8c9a0'; ctx.textAlign = 'center'; ctx.fillText(n.toUpperCase(), x, y + 300);
  });
};
