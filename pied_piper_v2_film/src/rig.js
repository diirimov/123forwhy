// rig: 2.5D articulated skeleton (3D local space -> yaw -> projection), IK, and motion cycles
'use strict';
const C = require('./core');
const { clamp, lerp, TAU, noise, ss } = C;

// ---------------------------------------------------------------- vector helpers (3D)
const v = (x, y, z) => [x, y, z];
const add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const mul = (a, k) => [a[0] * k, a[1] * k, a[2] * k];
const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const len = a => Math.hypot(a[0], a[1], a[2]);
const norm = a => { const l = len(a) || 1; return [a[0] / l, a[1] / l, a[2] / l]; };
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const rotY = (p, a) => { const c = Math.cos(a), s = Math.sin(a); return [p[0] * c + p[2] * s, p[1], -p[0] * s + p[2] * c]; };
const rotX = (p, a) => { const c = Math.cos(a), s = Math.sin(a); return [p[0], p[1] * c - p[2] * s, p[1] * s + p[2] * c]; };
const rotZ = (p, a) => { const c = Math.cos(a), s = Math.sin(a); return [p[0] * c - p[1] * s, p[0] * s + p[1] * c, p[2]]; };

// two-bone IK: root a, target t, lengths l1 l2, pole direction -> [mid, end]
function ik(a, t, l1, l2, pole) {
  const d = sub(t, a); let L = len(d);
  const Lc = clamp(L, Math.abs(l1 - l2) + .5, l1 + l2 - .3);
  const dir = norm(d); const end = add(a, mul(dir, Lc));
  const cosA = clamp((l1 * l1 + Lc * Lc - l2 * l2) / (2 * l1 * Lc), -1, 1), sinA = Math.sqrt(1 - cosA * cosA);
  let pv = sub(pole, mul(dir, dot(pole, dir))); if (len(pv) < 1e-4) pv = [0, 0, 1]; pv = norm(pv);
  return [add(a, add(mul(dir, l1 * cosA), mul(pv, l1 * sinA))), end];
}

// ---------------------------------------------------------------- body proportions
const BODY = {
  adult: { hip: 182, hipW: 21, thigh: 90, shin: 84, foot: 13, waist: 30, chest: 92, shY: 126, shW: 42, neck: 16, headH: 122, headW: 106, ua: 72, fa: 66, slim: 1 },
  child: { hip: 116, hipW: 15, thigh: 57, shin: 53, foot: 10, waist: 20, chest: 60, shY: 82, shW: 28, neck: 10, headH: 104, headW: 92, ua: 46, fa: 43, slim: .9 },
  piper: { hip: 232, hipW: 18, thigh: 116, shin: 108, foot: 13, waist: 34, chest: 108, shY: 150, shW: 40, neck: 22, headH: 112, headW: 86, ua: 86, fa: 80, slim: .82 },
};

// ---------------------------------------------------------------- pose -> joints
// P: {yaw, bob, sway, hipRoll, lean, side, twist, head:{yaw,pitch,roll}, legs:{l:[x,y,z] foot target, r:...},
//     arms:{l:{swing,out,elbow,hand?:[x,y,z] chest-local target}, r:...}, knees:{l,r} extra outward knee}
function solve(B, P) {
  const yaw = P.yaw || 0;
  const pel = v(P.sway || 0, B.hip + (P.bob || 0), P.fwd || 0);
  const hipRoll = P.hipRoll || 0;
  const J = { B, P };
  // legs (local, before yaw)
  for (const s of ['l', 'r']) {
    const sg = s === 'l' ? 1 : -1;
    const H = add(pel, rotZ(v(sg * B.hipW, 0, 0), hipRoll));
    const F = (P.legs && P.legs[s]) || v(sg * (B.hipW + 3), B.foot, 0);
    const kneeOut = (P.knees && P.knees[s]) || 0;
    const pole = norm(v(sg * kneeOut, 0, 1));
    const [K, A] = ik(H, F, B.thigh, B.shin, pole);
    J['hip' + s] = H; J['knee' + s] = K; J['ankle' + s] = A;
    J['toe' + s] = add(A, v(sg * 2, -B.foot + 2, (P.toe && P.toe[s] != null ? P.toe[s] : 1) * B.foot * 1.9));
  }
  // spine: pelvis -> waist -> chest with lean (rot about X), side bend (Z), twist (Y)
  const lean = P.lean || 0, side = P.side || 0, twist = P.twist || 0;
  const bend = p => rotY(rotZ(rotX(p, lean), side), twist);
  J.pel = pel;
  J.waist = add(pel, bend(v(0, B.waist, 0)));
  J.chest = add(pel, bend(v(0, B.chest, 0)));
  J.shc = add(pel, bend(v(0, B.shY, 0)));
  J.chestFrame = { o: J.chest, bend };
  for (const s of ['l', 'r']) {
    const sg = s === 'l' ? 1 : -1;
    const S = add(pel, bend(v(sg * B.shW, B.shY - 4, 0)));
    J['sh' + s] = S;
    const A = (P.arms && P.arms[s]) || {};
    let E, Wr;
    if (A.hand) { // chest-local target
      const T = add(pel, bend(A.hand));
      const pole = A.pole ? bend(A.pole) : bend(v(sg * .6, -.3, -1));
      [E, Wr] = ik(S, T, B.ua, B.fa, pole);
    } else {
      const swing = A.swing || 0, out = (A.out == null ? .12 : A.out), el = A.elbow == null ? .25 : A.elbow;
      // upper arm direction: down, rotated forward by swing (about X), outward by out (about Z)
      let du = rotX(rotZ(v(0, -1, 0), sg * out), -swing);          // abduct first, then swing: correct at any elevation
      E = add(S, bend(mul(du, B.ua)));
      let df = rotX(rotZ(v(0, -1, 0), sg * out * .6), -(swing + el));
      Wr = add(E, bend(mul(df, B.fa)));
    }
    J['el' + s] = E; J['wr' + s] = Wr;
  }
  J.neck = add(J.shc, bend(v(0, B.neck, 0)));
  const H = P.head || {};
  J.head = { yaw: (H.yaw || 0) + twist * .5, pitch: (H.pitch || 0) - lean * .35, roll: (H.roll || 0) - side * .6 };
  J.headC = add(J.neck, bend(rotZ(v(0, B.headH * .46, 0), J.head.roll * .6)));
  J.yaw = yaw;
  return J;
}

// projection of a local point: returns [sx, sy, depth] (sy screen-down, origin at root ground point)
function proj(J, p, k = 1) {
  const q = rotY(p, J.yaw);
  return [q[0] * k, -q[1] * k, q[2]];
}

// ---------------------------------------------------------------- motion cycles
// all cycles return a partial pose P; combine with Object.assign / blend
function walk(ph, o = {}) {
  // ph: stride phase (0..1, two steps). o: {stride, lift, bob, sway, arm, lean, style}
  const B = o.B || BODY.adult;
  const S = o.stride ?? 70, lift = o.lift ?? 18, bobA = o.bob ?? 7, swayA = o.sway ?? 4, armA = o.arm ?? .45;
  const P = { legs: {}, arms: {}, toe: {} };
  for (const s of ['l', 'r']) {
    const sg = s === 'l' ? 1 : -1;
    const u = (ph + (s === 'l' ? 0 : .5)) % 1;
    let z, y = B.foot, toe = 1;
    const st = o.stance ?? .6;
    if (u < st) { const w = u / st; z = S / 2 - S * w; if (w > .8) { y += (w - .8) * 20; toe = 1 - (w - .8) * 1.5; } } // heel-off at end of stance
    else { const w = (u - st) / (1 - st); const e = .5 - .5 * Math.cos(Math.PI * w); z = -S / 2 + S * e; y += lift * Math.sin(Math.PI * w) + (1 - w) * 4; toe = .7 + .3 * w; }
    P.legs[s] = [sg * (B.hipW + (o.spread ?? 2)), y, z];
    P.toe[s] = toe;
    const a = -armA * Math.sin(TAU * u - .4);
    P.arms[s] = { swing: a, out: o.armOut ?? .1, elbow: (o.elbow ?? .25) + Math.max(0, a) * .5 };
  }
  P.bob = -bobA * Math.cos(TAU * 2 * ph) - (o.crouch || 0);
  P.sway = swayA * Math.sin(TAU * ph);
  P.hipRoll = .06 * Math.sin(TAU * ph) * (o.hipAmt ?? 1);
  P.twist = .1 * Math.sin(TAU * ph) * (o.twistAmt ?? 1);
  P.lean = o.lean ?? .05;
  P.side = -.03 * Math.sin(TAU * ph);
  P.head = { yaw: 0, pitch: .02 * Math.cos(TAU * 2 * ph), roll: .02 * Math.sin(TAU * ph) };
  return P;
}

// Dancing-Plague squat dance: knees out, pelvis drops on the beat, arms flap; ph = beat phase, n = beat index
function squatDance(ph, n, o = {}) {
  const B = o.B || BODY.adult;
  const k = o.amt ?? 1;
  const down = Math.pow(Math.sin(Math.PI * ph), 1) ;          // 0 at beat, 1 mid-beat (upbeat lift)
  const hit = Math.exp(-ph * 6);                                // impact squash right on the beat
  const P = { legs: {}, arms: {}, knees: {}, toe: {} };
  const alt = n % 2 ? 1 : -1;
  for (const s of ['l', 'r']) {
    const sg = s === 'l' ? 1 : -1;
    const lifted = (sg === alt) ? Math.sin(Math.PI * clamp(ph * 1.6)) : 0;
    P.legs[s] = [sg * (B.hipW + 16 * k), B.foot + lifted * 22 * k, 6 * lifted];
    P.knees[s] = 1.1 * k;
    P.toe[s] = 1;
    const flap = (s === 'l' ? 1 : -1) * alt;
    P.arms[s] = { swing: .25 + .35 * flap * Math.sin(Math.PI * ph) * k, out: .55 + .35 * down * k, elbow: .9 - .4 * down };
  }
  P.bob = -(26 * hit + 6) * k + 8 * down * k;
  P.sway = alt * 8 * Math.sin(Math.PI * ph) * k;
  P.hipRoll = alt * .08 * k * Math.sin(Math.PI * ph);
  P.lean = .08 + .05 * hit;
  P.side = alt * .06 * k * Math.sin(Math.PI * ph);
  P.head = { roll: -alt * .1 * k * Math.sin(Math.PI * ph), pitch: .08 * hit, yaw: 0 };
  return P;
}

// jig: hop on each beat, alternate heel kicks, hands on hips or up
function jig(ph, n, o = {}) {
  const B = o.B || BODY.adult; const k = o.amt ?? 1;
  const alt = n % 2 ? 1 : -1;
  const hop = Math.sin(Math.PI * ph);
  const P = { legs: {}, arms: {}, knees: {}, toe: {} };
  for (const s of ['l', 'r']) {
    const sg = s === 'l' ? 1 : -1;
    const kick = sg === alt ? Math.sin(Math.PI * ph) : 0;
    P.legs[s] = [sg * (B.hipW + 6), B.foot + kick * 30 * k + hop * 10 * k, kick * 40 * k];
    P.knees[s] = .2;
    P.arms[s] = o.handsUp ? { swing: 2.3 + .25 * Math.sin(Math.PI * ph + (s === 'l' ? 0 : 1)), out: 1.05, elbow: .25 }
      : { swing: -.2, out: .95, elbow: 1.9 };                 // hands on hips
  }
  P.bob = hop * 16 * k - 6;
  P.lean = -.05; P.side = alt * .07 * hop;
  P.head = { roll: alt * .12 * hop, pitch: -.05, yaw: alt * .15 * hop };
  return P;
}

// stand / idle breathing with weight shift (t seconds)
function idle(t, o = {}) {
  const B = o.B || BODY.adult; const br = Math.sin(t * TAU * .25 + (o.seed || 0));
  const shift = noise(t * .3 + (o.seed || 0) * 7) * (o.shift ?? 1);
  return {
    legs: { l: [B.hipW + 5, B.foot, 2], r: [-(B.hipW + 5), B.foot, -2] },
    arms: { l: { swing: .05 + br * .02, out: .12, elbow: .3 }, r: { swing: .05 - br * .02, out: .12, elbow: .3 } },
    bob: br * 1.5 - 2, sway: shift * 5, hipRoll: shift * .05, lean: .03, side: -shift * .02,
    head: { yaw: noise(t * .4 + 3 + (o.seed || 0)) * .15, pitch: 0, roll: shift * .03 },
  };
}

// blend two poses (numbers, arrays and nested objects)
function blend(A, Bp, w) {
  if (w <= 0) return A; if (w >= 1) return Bp;
  const out = Array.isArray(A) ? [] : {};
  const keys = new Set([...Object.keys(A || {}), ...Object.keys(Bp || {})]);
  for (const k of keys) {
    const a = A ? A[k] : undefined, b = Bp ? Bp[k] : undefined;
    if (typeof a === 'number' || typeof b === 'number') out[k] = lerp(a ?? 0, b ?? 0, w);
    else if (a && b && typeof a === 'object') out[k] = blend(a, b, w);
    else out[k] = w < .5 ? (a ?? b) : (b ?? a);
  }
  return out;
}
function merge(A, Bp) { // deep override
  const out = Array.isArray(A) ? A.slice() : { ...A };
  for (const k of Object.keys(Bp || {})) {
    const b = Bp[k];
    out[k] = (b && typeof b === 'object' && !Array.isArray(b) && A && typeof A[k] === 'object' && !Array.isArray(A[k])) ? merge(A[k], b) : b;
  }
  return out;
}

module.exports = { v, add, sub, mul, dot, len, norm, cross, rotX, rotY, rotZ, ik, BODY, solve, proj, walk, squatDance, jig, idle, blend, merge };
