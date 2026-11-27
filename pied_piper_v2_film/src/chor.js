// chor: choreography -- the DP dance vocabulary and the hypnotic procession walk.
// Every move is a full-body pose (legs by IK with planted feet, pelvis bob + roll, spine lean/side/twist,
// arms, head) driven by the beat clock; `delay` shifts a dancer in time (canon / waves), `amt` scales it.
'use strict';
const C = require('./core');
const R = require('./rig');
const { clamp, lerp, TAU, BEAT, BAR, ease } = C;

const ph = (t) => C.beatPhase(t);
const bi = (t) => C.beatIndex(t);

// knee-lift stomp: one leg rises through the off-beat and slams on the beat; fists pump, torso punches down
function stomp(t, o = {}) {
  const B = o.B || R.BODY.adult, k = o.amt ?? 1;
  const p = ph(t), n = bi(t);
  const alt = n % 2 ? 1 : -1;
  const lift = Math.sin(Math.PI * clamp((p - .35) / .65));          // rises in the second half of the beat
  const hit = Math.exp(-p * 9);
  const P = { legs: {}, arms: {}, knees: {}, toe: {} };
  for (const s of ['l', 'r']) {
    const sg = s === 'l' ? 1 : -1;
    const up = sg === alt ? lift : 0;
    P.legs[s] = [sg * (B.hipW + 10 * k), B.foot + up * 70 * k, up * 40 * k];
    P.knees[s] = .5 * k;
    const pump = sg === alt ? 1 : -1;
    P.arms[s] = { swing: .5 + .6 * pump * (lift - .3) * k, out: .35, elbow: 1.6 };
  }
  P.hands = { l: 'fist', r: 'fist' };
  P.bob = -(20 * hit + 4) * k + 6 * lift * k;
  P.lean = .12 + .1 * hit;
  P.side = alt * .05 * lift * k;
  P.twist = alt * .12 * lift * k;
  P.head = { pitch: .1 * hit, roll: alt * .05 * lift, yaw: 0 };
  return P;
}

// spin: a full turn over two beats with arms flung out, landing on the beat with a dip
function spin(t, o = {}) {
  const B = o.B || R.BODY.adult, k = o.amt ?? 1;
  const u = ((t / (2 * BEAT)) % 1 + 1) % 1;
  const turn = ease.io(clamp(u / .8));
  const hop = Math.sin(Math.PI * clamp(u / .8));
  const P = R.jig(ph(t), bi(t), { B, amt: .5 * k, handsUp: false });
  P.yaw = (o.yaw0 || 0) + turn * TAU * (o.dir || 1);
  P.arms = { l: { swing: .4, out: 1.25 - .4 * (1 - hop), elbow: .2 }, r: { swing: .4, out: 1.25 - .4 * (1 - hop), elbow: .2 } };
  P.hands = { l: 'open', r: 'open' };
  P.bob = hop * 14 * k - 10 * Math.exp(-u * 12) * k;
  P.head = { roll: .12 * Math.sin(TAU * u), pitch: -.1, yaw: 0 };
  return P;
}

// clap on every beat: hands meet in front of the chest on the beat, bounce at the knees
function clapDance(t, o = {}) {
  const B = o.B || R.BODY.adult, k = o.amt ?? 1;
  const p = ph(t), n = bi(t);
  const meet = Math.exp(-p * 10), open = Math.sin(Math.PI * p);
  const P = R.squatDance(p, n, { B, amt: .45 * k });
  const y = B.shY - 30, z = 52;
  const gap = 8 + 52 * open;
  P.arms = { l: { hand: R.v(gap, y + 10 * open, z), pole: R.v(1, -.6, -.2) }, r: { hand: R.v(-gap, y + 10 * open, z), pole: R.v(-1, -.6, -.2) } };
  P.hands = { l: 'open', r: 'open' };
  P.head.pitch = -.06 + .06 * meet;
  return P;
}

// hypnotic sway: hips and arms drift side to side across two beats, eyes half shut
function sway(t, o = {}) {
  const B = o.B || R.BODY.adult, k = o.amt ?? 1;
  const u = Math.sin(TAU * t / (2 * BEAT));
  const P = R.idle(t, { B, shift: 0 });
  P.sway = 14 * u * k; P.side = -.09 * u * k; P.hipRoll = .1 * u * k;
  P.legs = { l: [B.hipW + 8, B.foot, 0], r: [-(B.hipW + 8), B.foot, 0] };
  P.arms = { l: { swing: .35 + .15 * u, out: .55 + .25 * u, elbow: .5 }, r: { swing: .35 - .15 * u, out: .55 - .25 * u, elbow: .5 } };
  P.head = { roll: .16 * u * k, pitch: .05, yaw: 0 };
  return P;
}

// dance by name with a time offset (canon) and per-dancer variety
function dance(kind, t, o = {}) {
  const tt = t - (o.delay || 0);
  let P;
  if (kind === 'squat') P = R.squatDance(ph(tt), bi(tt), { B: o.B, amt: o.amt ?? 1 });
  else if (kind === 'jig') P = R.jig(ph(tt), bi(tt), { B: o.B, amt: o.amt ?? 1, handsUp: o.handsUp });
  else if (kind === 'stomp') P = stomp(tt, o);
  else if (kind === 'spin') P = spin(tt, o);
  else if (kind === 'clap') P = clapDance(tt, o);
  else if (kind === 'sway') P = sway(tt, o);
  else if (kind === 'half') {          // half-time squat: the same dance at half speed (the betrayal)
    const h = tt / 2; P = R.squatDance(ph(h), bi(h), { B: o.B, amt: (o.amt ?? 1) * .85 });
  } else P = R.idle(tt, { B: o.B, seed: o.seed });
  if (o.yaw != null && kind !== 'spin') P.yaw = o.yaw;
  if (o.face) P.face = typeof o.face === 'function' ? o.face(t) : o.face;
  return P;
}

// hypnotised procession walk: perfect lockstep, still arms, a slow shared body sway, and heads that tilt in a
// canon (each child `idx` steps later) on every bar -- uncanny because it is too precise, never zombie-like
function procWalk(B, o = {}) {
  return t => {
    const t0 = o.t0 || 0;
    const ph_ = ((t - t0) / (2 * BEAT) % 1 + 1) % 1;
    const P = R.walk(ph_, { B, stride: o.stride ?? 58, bob: 4, arm: .05, lift: o.lift ?? 12, sway: 2, twistAmt: .15, hipAmt: .6, lean: .03 });
    const sw = Math.sin(TAU * (t - t0) / (4 * BEAT));
    P.side = (P.side || 0) + .05 * sw * (o.swayAmt ?? 1);
    P.sway = (P.sway || 0) + 6 * sw * (o.swayAmt ?? 1);
    const d = (o.idx || 0) * (o.canon ?? C.S16);
    const barU = (((t - d) / BAR) % 1 + 1) % 1;
    const tilt = (o.tilt ?? .16) * Math.sin(Math.PI * clamp(barU * 4 - 2.8)) * (o.tiltSign ?? 1);
    P.yaw = typeof o.yaw === 'function' ? o.yaw(t) : (o.yaw ?? 0);
    P.head = { yaw: typeof o.headYaw === 'function' ? o.headYaw(t) : (o.headYaw || 0), pitch: typeof o.pitch === 'function' ? o.pitch(t) : (o.pitch ?? .05), roll: tilt + .05 * sw };
    const lift = typeof o.armLift === 'function' ? o.armLift(t) : (o.armLift || 0);
    P.arms = { l: { swing: .08 + .9 * lift, out: .1 + .35 * lift, elbow: .15 + .2 * lift }, r: { swing: .08 + .9 * lift, out: .1 + .35 * lift, elbow: .15 + .2 * lift } };
    if (lift > .2) P.hands = { l: 'open', r: 'open' };
    P.face = typeof o.face === 'function' ? o.face(t) : (o.face || { eyes: 'half', mouth: 'peace', glint: 1.2 });
    return P;
  };
}

// the Piper walking while playing (legs from the walk, arms + face + recorder from playPose)
function piperWalkPlay(PP, o = {}) {
  return t => {
    const P = PP.playPose(t, { eyes: o.eyes || 'narrow', glow: o.glow || 0 });
    const ph_ = ((t - (o.t0 || 0)) / (2 * BEAT) % 1 + 1) % 1;
    const Wk = R.walk(ph_, { B: R.BODY.piper, stride: o.stride ?? 100, bob: 2.6, arm: 0, sway: 2.5, hipAmt: 1.2 });
    return R.merge(P, { legs: Wk.legs, toe: Wk.toe, bob: Wk.bob * .7 + P.bob, sway: Wk.sway, hipRoll: Wk.hipRoll * 1.2, twist: Wk.twist * .4,
      yaw: typeof o.yaw === 'function' ? o.yaw(t) : (o.yaw ?? 0) });
  };
}

module.exports = { stomp, spin, clapDance, sway, dance, procWalk, piperWalkPlay };
