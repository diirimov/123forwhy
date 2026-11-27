// stage: shared staging helpers -- actors with follow-through, beat-locked walks, backdrops, crowds, swarms
'use strict';
const C = require('./core');
const R = require('./rig');
const PS = require('./person');
const CAST = require('./cast');
const E = require('./env');
const Wd = require('./world');
const RT = require('./rats');
const K = require('./ink');
const { clamp, lerp, TAU, ease, BEAT, BAR, noise, hash } = C;

const LAG_A = .07, LAG_B = .16;
// draw a character in world space; poseFn(t) -> pose. o passes through to drawPerson
function actor(g, V, ch, x, z, poseFn, t, o = {}) {
  const [sx, sy, s] = V.p(x, o.yOff || 0, z);
  if (sx < -500 || sx > C.W + 500) return;
  const P = poseFn(t);
  const opts = { x: sx, y: sy, s: s * (o.sMul || 1), lw: o.lw ?? V.lw(s), lagA: poseFn(t - LAG_A), lagB: poseFn(t - LAG_B), t, ...o };
  PS.drawPerson(g, ch, P, opts);
  if (o.occlude !== false) E.occlude(g, (g2) => PS.drawPerson(g2, ch, P, { ...opts, sil: '#000', shadow: false }));
}
function actorItem(V, ch, xf, zf, poseFn, o = {}) { // xf/zf may be functions of t
  return (t) => ({ z: typeof zf === 'function' ? zf(t) : zf, draw: (g, V2) => actor(g, V2, ch, typeof xf === 'function' ? xf(t) : xf, typeof zf === 'function' ? zf(t) : zf, poseFn, t, o) });
}
// stride phase locked to beats (heel strikes on beats when t0 is a beat)
const stridePh = (t, t0 = 0) => ((t - t0) / (2 * BEAT) % 1 + 1) % 1;
// walking pose with a given heading; stride S (world units) => speed S/(2 beats)
function walker(B, o = {}) {
  return t => {
    const ph = stridePh(t, o.t0 || 0);
    let P = R.walk(ph, { B, stride: o.stride ?? 70, bob: o.bob ?? 5, arm: o.arm ?? .4, lift: o.lift, lean: o.lean, sway: o.sway });
    P = R.merge(P, { yaw: typeof o.yaw === 'function' ? o.yaw(t) : (o.yaw ?? 0) });
    if (o.head) P.head = { ...P.head, ...(typeof o.head === 'function' ? o.head(t) : o.head) };
    if (o.face) P.face = typeof o.face === 'function' ? o.face(t) : o.face;
    if (o.arms) P.arms = { ...P.arms, ...(typeof o.arms === 'function' ? o.arms(t) : o.arms) };
    if (o.hands) P.hands = o.hands;
    return P;
  };
}
// hypnotised walk: synchronised, minimal arm swing, still head, slight uncanny tilt on each bar
function hypnoWalker(B, o = {}) {
  return t => {
    const ph = stridePh(t, o.t0 || 0);
    let P = R.walk(ph, { B, stride: o.stride ?? 56, bob: 3.5, arm: .06, lift: 10, sway: 1.5, twistAmt: .2, hipAmt: .5, lean: .02 });
    const barU = ((t / BAR) % 1 + 1) % 1;
    const tilt = (o.tilt ?? .14) * Math.sin(Math.PI * clamp(barU * 4 - 3)) ;
    P.head = { yaw: typeof o.headYaw === 'function' ? o.headYaw(t) : (o.headYaw || 0), pitch: typeof o.pitch === 'function' ? o.pitch(t) : (o.pitch ?? .06), roll: tilt };
    P.yaw = typeof o.yaw === 'function' ? o.yaw(t) : (o.yaw ?? 0);
    P.face = typeof o.face === 'function' ? o.face(t) : (o.face || { eyes: 'half', mouth: 'peace', glint: .4 });
    P.arms = { l: { swing: .05, out: .08, elbow: .15 }, r: { swing: .05, out: .08, elbow: .15 } };
    return P;
  };
}

// backdrop for street scenes
function streetBackdrop(g, V, t, mood, o = {}) {
  g.save();
  E.sky(g, mood, C.W, V.hy + 200, t);
  if (o.moon !== false && (mood === 'night' || o.moon)) E.moon(g, o.moonX ?? 780, o.moonY ?? 250, o.moonR ?? 92);
  if (mood !== 'night' && mood !== 'dusk' && o.sun !== false) E.sun(g, o.sunX ?? 820, o.sunY ?? 230, 66, t);
  if (o.clouds) for (const [x, y, s] of o.clouds) E.cloud(g, x + Math.sin(t * .2) * 10, y, s, .95);
  const sk = V.p(0, 0, 12000);
  E.skyline(g, -150 - V.cx * .02, sk[1] + 4, 1400, mood, o.skySeed || 4);
  g.restore();
  Wd.ground(g, V, { mood });
}

// townsfolk crowd for street scenes. returns array of {ch, x, z, seed}
function crowd(n, seed, area) {
  const r = C.rng(seed); const out = [];
  for (let i = 0; i < n; i++) out.push({ ch: CAST.townsfolk(seed * 7 + i), x: lerp(area.x0, area.x1, r()), z: lerp(area.z0, area.z1, r()), seed: i, r: r() });
  return out;
}

// world-space rat (side view) on the ground
function ratAt(g, V, x, z, o) { const [sx, sy, s] = V.p(x, o.y || 0, z); if (sx < -200 || sx > C.W + 200) return; RT.ratSide(g, sx, sy, { ...o, s: s * (o.size || 1.15), lw: clamp(V.lw(s) * .85, 1.4, 6) }); }

module.exports = { actor, actorItem, stridePh, walker, hypnoWalker, streetBackdrop, crowd, ratAt, LAG_A, LAG_B };
