// 12-17 THE STRANGER (bars 7-11): the gate (build + silence), he strides through the market (the hurdy-gurdy
// calls, his flute answers), the offer, the agreement, he raises the flute, the rats freeze and turn.
'use strict';
const C = require('../core');
const R = require('../rig');
const PS = require('../person');
const CAST = require('../cast');
const E = require('../env');
const Wd = require('../world');
const ST = require('../stage');
const RT = require('../rats');
const PP = require('../piper');
const K = require('../ink');
const PO = require('../post');
const DP = require('../dp');
const CH = require('../chor');
const SETS = require('../sets');
const { barT: b, clamp, lerp, ease, BEAT, BAR, S16, HIT, W, H, TAU, hash } = C;
const { PAL } = K;
const GAP0 = C.BM.gaps[0];             // 12.132
const PB = CAST.piper.B;
const PSTRIDE = 104, PSPEED = PSTRIDE / (.6 * 2 * BEAT);
const piperWalk = (o = {}) => ST.walker(PB, { stride: PSTRIDE, bob: 2.6, arm: .2, lean: .02, sway: 2, ...o });

// ---------------------------------------------------------------- 12: the gate grinds open (ratchet); a silhouette steps through in the silence
function shot12(g, t, lt) {
  const t0 = b(6);
  const open = ease.io(clamp((t - b(6, 2)) / (GAP0 - b(6, 2) - .15)));
  const push = 1 + .1 * ease.io(clamp(lt / 1.77));
  g.save(); g.translate(W / 2, H * .55); g.scale(push, push); g.translate(-W / 2, -H * .55);
  E.sky(g, 'day', W, 1200, t); E.cloud(g, 180, 330, 1.2, 1); E.cloud(g, 860, 250, .9, 1);
  const gy = 1480;
  const beyond = (g2) => {
    const gr = g2.createLinearGradient(0, gy - 480, 0, gy); gr.addColorStop(0, '#fff4d8'); gr.addColorStop(1, '#f0d7a6'); g2.fillStyle = gr; g2.fillRect(0, gy - 600, W, 700);
    const appear = ease.o(clamp((t - b(6, 8)) / .5));
    const step = ease.io(clamp((t - GAP0) / .22));
    let P = R.merge(R.idle(t * .3, { B: PB, shift: .1 }), { yaw: 0, head: { pitch: .05 } });
    if (step > 0) P = R.merge(P, R.walk(step * .5, { B: PB, stride: 110, bob: 2, arm: .12 }));
    g2.save(); g2.globalAlpha = appear;
    PS.drawPerson(g2, CAST.piper, P, { x: W / 2, y: gy - 6 + step * 10, s: .64 + step * .06, sil: '#2a1a22', lw: 3, t, wind: .6 + step, shadow: false });
    g2.restore();
    E.addLight(g2, W / 2, gy - 260, 520, '#ffe2a8', .5 + .3 * open);
  };
  E.gate(g, W / 2, gy, { open, mood: 'day', inner: beyond, lw: 5 });
  const V = new Wd.View({ cx: 0, cy: 240, cz: 0, f: 1000, hy: gy - 100 });
  g.save(); g.beginPath(); g.rect(0, gy, W, 700); g.clip(); Wd.ground(g, V, { mood: 'day', zFar: 2400 }); g.restore();
  // rats fleeing out of the gateway toward us
  for (let i = 0; i < 26; i++) { const dt = t - t0 - hash(i) * 1.4; if (dt < 0) continue; const z = 2300 - dt * 900; if (z < 250) continue; const [sx, sy, s] = V.p((hash(i * 3) - .5) * 900, 0, z); if (sy > gy) RT.ratSide(g, sx, sy, { s: s * 1.1, dir: hash(i * 5) < .5 ? 1 : -1, phase: dt * 5, t, speed: 1 }); }
  // townsfolk seen from behind framing the gate, heads turning toward it on the beats
  const backs = [[110, 1980, 1.75, 7, b(6, 4)], [990, 2010, 1.85, 11, b(6, 8)], [330, 1840, 1.15, 13, b(6, 12)], [760, 1830, 1.1, 19, b(6, 10)]];
  for (const [x, y, s, sd, at] of backs) {
    const tw = ease.back(clamp((t - at) / .15));
    const P = R.merge(R.idle(t, { seed: sd }), { yaw: Math.PI + (x < W / 2 ? .45 : -.45) * (1 - tw * .7), head: { yaw: (x < W / 2 ? -.3 : .3) * tw } });
    PS.drawPerson(g, CAST.townsfolk(sd), P, { x, y, s, lw: 5.5, t });
  }
  E.fog(g, gy - 380, 420, t, { col: '#f3ead6', a: .45 * (.4 + .6 * open), speed: 30 });
  g.restore();
}

// ---------------------------------------------------------------- 13: he strides through the market toward us; heads turn in a wave on the beats
function shot13(g, t, lt) {
  const t0 = b(7);
  const pz = 1950 - (t - t0) * PSPEED * 1.0;
  const punch = 1 + .03 * C.decay(t - t0 - HIT, 5);
  const { V, items } = DP.town(g, t, { mood: 'day', cam: { cz: pz - 820 - 60 * ease.io(lt / 1.77), f: 1150 * punch }, sunX: 880, clouds: [[260, 280, 1.1]], seed: 41, zNear: 3300, zMid: 4300, zFar: 5400,
    props: [['stall', -900, 2200, 1], ['stall', 950, 2300, 1], ['barrel', 760, 1150], ['sack', -800, 1050]] });
  // two hedges of villagers lining the street; each turns to him when he passes, quantised to the beat
  const side = [];
  for (let i = 0; i < 8; i++) for (const sd of [-1, 1]) side.push({ ch: CAST.townsfolk(60 + i * 2 + (sd > 0)), x: sd * (430 + hash(i * 3 + sd) * 140), z: 1350 + i * 200 + (sd > 0 ? 100 : 0), sd, i });
  for (const f of side) {
    const pass = t0 + (2150 - f.z) / PSPEED;
    const turnT = t0 + Math.max(0, Math.round((pass - t0 - .9) / BEAT)) * BEAT;
    DP.actorAt(items, f.ch, f.x, f.z, tt => {
      const u = ease.back(clamp((tt - turnT - HIT) / .12));
      const toward = -f.sd;
      return R.merge(R.idle(tt, { seed: f.i * 3 + (f.sd > 0) }), { yaw: lerp(-f.sd * .2, toward * 1.0, u * .8), head: { yaw: toward * .5 * u, pitch: -.05 * u },
        lean: -.05 * u, face: u > .5 ? { eyes: 'wide', mouth: f.i % 2 ? 'o' : 'closed', brow: 'raised', look: [toward * .8, 0] } : { eyes: 'open', mouth: 'flat' },
        arms: u > .5 && f.i % 3 === 0 ? { l: { swing: 1.9, out: .4, elbow: 1.7 }, r: { swing: 1.9, out: .4, elbow: 1.7 } } : undefined });
    }, t);
  }
  // rats scatter away from his feet to both sides
  for (let i = 0; i < 30; i++) { const dt = t - t0 - hash(i) * 1.5; if (dt < 0) continue; const sd = i % 2 ? 1 : -1; const z0 = 2000 - hash(i * 3) * 1000; const z = Math.min(z0, pz + 200 + (i % 5) * 60); const x = sd * (60 + dt * (300 + hash(i * 7) * 300)); items.push({ z, draw: (g2, V2) => ST.ratAt(g2, V2, x, z, { dir: sd, phase: dt * 5, t, speed: 1 }) }); }
  // the Piper: long elegant strides toward camera, heel strikes on the beats, cloak streaming
  DP.actorAt(items, CAST.piper, 30, pz, piperWalk({ t0, yaw: .05, head: tt => ({ yaw: .3 * Math.sin(TAU * (tt - t0) / (2 * BAR)), pitch: .06 }),
    face: { eyes: 'narrow', mouth: 'sly', brow: 'sly', look: [0, 0], glint: 1.4 } }), t, { wind: .4 });
  DP.flush(g, V, items);
}

// ---------------------------------------------------------------- 14: the offer -- he gestures to the rats; the council leans in
function shot14(g, t, lt) {
  const t0 = b(8);
  const push = 1 + .05 * ease.io(lt / 1.77);
  g.save(); g.translate(W / 2, H * .6); g.scale(push, push); g.translate(-W / 2, -H * .6);
  SETS.councilRoom(g, t);
  const seat = [[300, CAST.councillor, .25, 41], [560, CAST.mayor, 0, 42], [820, CAST.clerk, -.25, 43]];
  for (const [x, ch, yaw, sd] of seat) {
    const pose = tt => {
      const n = C.beatIndex(tt), ph = C.beatPhase(tt);
      const lean = ease.io(clamp((tt - b(8, 8)) / .4));
      const nod = ch === CAST.mayor ? Math.sin(Math.PI * ph) * .12 * lean : 0;
      return R.merge(R.idle(tt, { seed: sd }), { yaw: yaw * (1 - lean * .5), lean: .15 * lean, head: { pitch: nod + .05, yaw: -yaw * .5 },
        arms: { l: { swing: .9, out: .2, elbow: .8 }, r: { swing: .9, out: .2, elbow: .8 } },
        face: { eyes: lean > .5 ? 'wide' : 'narrow', mouth: ch === CAST.clerk ? 'o' : lean > .5 ? 'smile' : 'flat', brow: 'raised', look: [-.4, .3] } });
    };
    PS.drawPerson(g, ch, pose(t), { x, y: 1500, s: 1.35, lw: 5, lagA: pose(t - .07), lagB: pose(t - .16), t });
  }
  K.shape(g, [[60, 1260], [W - 60, 1260], [W - 30, 1560], [30, 1560]], { fill: '#2f5a3c', lw: 6, smooth: false, inner: g2 => { g2.fillStyle = 'rgba(0,0,0,.15)'; g2.fillRect(0, 1400, W, 200); } });
  E.chest(g, 790, 1270, .9, { lid: 0, lw: 5 });
  K.shape(g, [[240, 1270], [430, 1262], [440, 1290], [250, 1300]], { fill: '#f1e9d6', lw: 4, smooth: false });
  for (const cx of [140, 980]) { K.shape(g, [[cx - 12, 1268], [cx + 12, 1268], [cx + 12, 1150], [cx - 12, 1150]], { fill: '#efe6d2', lw: 4, smooth: false }); K.shape(g, [[cx, 1100 + Math.sin(t * 9 + cx) * 4], [cx + 9, 1135], [cx, 1150], [cx - 9, 1135]], { fill: '#f6c24a', lw: 2.5 }); E.addLight(g, cx, 1130, 240, '#f3a64a', .5); }
  if (t > b(8, 5)) { const dt = t - b(8, 5); RT.ratSide(g, 60 + dt * 640, 1268, { s: 1.0, dir: 1, phase: dt * 5, t, shadow: false }); }
  // the Piper (back three-quarter, foreground left): palm up on the gurdy's call, sweeps to the window, then
  // taps the recorder on his flute answer
  const pose = tt => {
    const a1 = ease.o(clamp((tt - t0 - HIT) / .2)) * (1 - ease.io(clamp((tt - b(8, 3)) / .2)));
    const a2 = ease.io(clamp((tt - b(8, 3)) / .3)) * (1 - ease.io(clamp((tt - b(8, 8)) / .25)));
    const a3 = ease.io(clamp((tt - b(8, 8)) / .3));
    return R.merge(R.idle(tt * .4, { B: PB, shift: .15 }), { yaw: Math.PI - .55, head: { yaw: -.35 - .3 * a2, pitch: .05 }, lean: .05 * a1,
      arms: { r: { swing: lerp(.1, 1.3, a1) + 1.6 * a2, out: lerp(.1, .5, a1) - .3 * a2, elbow: .25 }, l: { swing: lerp(.1, 1.7, a3), out: .2, elbow: lerp(.3, 1.9, a3) } },
      hands: { r: a1 + a2 > .3 ? 'open' : 'mitten' } });
  };
  PS.drawPerson(g, CAST.piper, pose(t), { x: 190, y: 2050, s: 2.2, lw: 7, lagA: pose(t - .07), lagB: pose(t - .16), t, wind: .15 });
  g.restore();
}

// ---------------------------------------------------------------- 15: the agreement -- the chest opens, the handshake on his answer, the bow
function shot15(g, t, lt) {
  const t0 = b(9);
  const push = 1 + .07 * ease.io(lt / 1.77);
  g.save(); g.translate(W / 2, H * .55); g.scale(push, push); g.translate(-W / 2, -H * .55);
  PO.blurred(g, 8, (g2) => SETS.councilRoom(g2, t));
  E.LIGHTS.length = 0;
  E.addLight(g, 540, 1250, 700, '#f6c24a', .45 * ease.io(clamp((t - t0) / .3)));
  const shake = b(9, 8) + HIT;
  // the mayor (right): opens the chest on the downbeat, then reaches across to shake
  const mp = tt => {
    const o = ease.o3(clamp((tt - t0 - HIT) / .2)), r = ease.io(clamp((tt - b(9, 6)) / .3));
    const pump = tt > shake ? Math.sin(TAU * (tt - shake) / (BEAT / 2)) * .1 * Math.exp(-(tt - shake) * 2) : 0;
    return R.merge(R.idle(tt, { seed: 42 }), { yaw: -.75, lean: .1 + .1 * r,
      arms: { r: { swing: lerp(.4, 1.3, r) + pump, out: lerp(.2, -.15, r), elbow: lerp(.9, .2, r) }, l: { swing: lerp(1.0, .3, r), out: .3, elbow: .6 } }, hands: { r: r > .5 ? 'open' : 'mitten' },
      head: { pitch: .05, yaw: .1 }, face: { eyes: 'narrow', mouth: 'grin', brow: 'raised', look: [-.7, .1] } });
  };
  PS.drawPerson(g, CAST.mayor, mp(t), { x: 790, y: 1920, s: 2.4, lw: 7, lagA: mp(t - .07), lagB: mp(t - .16), t });
  // the chest on the table between them, coins glinting
  K.shape(g, [[-40, 1560], [W + 40, 1560], [W + 40, H + 40], [-40, H + 40]], { fill: '#2f5a3c', lw: 7, smooth: false });
  const lid = ease.o3(clamp((t - t0 - HIT) / .18));
  E.chest(g, 520, 1580, 1.9, { lid, lw: 7 });
  if (lid > .3) for (let i = 0; i < 5; i++) K.glow(g, 450 + i * 35, 1470 - (i % 2) * 20, 30, '#ffe08a', .5 * (.5 + .5 * Math.sin(t * 8 + i)), 'lighter');
  // the Piper (left): takes the hand on his answer, then bows and tips his hat on the long B5
  const pp = tt => {
    const r = ease.io(clamp((tt - b(9, 6)) / .3)), bow = ease.io(clamp((tt - b(9, 11)) / .25)) * (1 - ease.io(clamp((tt - b(9, 14)) / .25)));
    const pump = tt > shake ? Math.sin(TAU * (tt - shake) / (BEAT / 2)) * .1 * Math.exp(-(tt - shake) * 2) : 0;
    return R.merge(R.idle(tt * .4, { B: PB, shift: .1 }), { yaw: .8, lean: .25 * bow,
      arms: { l: { swing: lerp(.2, 1.3, r) - pump, out: lerp(.1, -.1, r), elbow: lerp(.3, .2, r) }, r: { swing: lerp(.1, 2.6, bow), out: lerp(.1, .5, bow), elbow: lerp(.3, 1.5, bow) } }, hands: { l: r > .5 ? 'open' : 'mitten', r: bow > .5 ? 'open' : 'mitten' },
      head: { yaw: .1, pitch: .25 * bow }, face: { eyes: 'narrow', mouth: 'sly', brow: 'sly', look: [.6, .1], glint: 1.5 } });
  };
  PS.drawPerson(g, CAST.piper, pp(t), { x: 250, y: 2000, s: 2.35, lw: 7, lagA: pp(t - .07), lagB: pp(t - .16), t, wind: .15 });
  g.restore();
}

// ---------------------------------------------------------------- 16: he raises the flute -- low angle, the run climbs
function shot16(g, t, lt) {
  const t0 = b(10);
  const V = new Wd.View({ cx: 0, cy: 40, cz: 0, f: 1000, hy: 1450 });
  ST.streetBackdrop(g, V, t, 'day', { sunX: 300, sunY: 330, clouds: [[700, 260, 1.2]] });
  const items = [];
  DP.wall(items, 2300, 7, { sp: 620, seed: 55, mood: 'day' });
  const raise = tt => ease.io(clamp((tt - t0 + .05) / .3));
  const pose = tt => {
    const P = PP.playPose(tt, { eyes: tt > t0 + .3 ? 'narrow' : 'open', glow: .3 * raise(tt) });
    const r = raise(tt);
    if (r < 1) { P.arms.l.hand = R.v(16, 20 + 120 * r, 30 + 10 * r); P.arms.r.hand = R.v(-10, -10 + 85 * r, 40 + 10 * r); }
    return R.merge(P, { yaw: .3, head: { yaw: -.12 } });
  };
  items.push({ z: 520, draw: (g2, V2) => ST.actor(g2, V2, CAST.piper, 0, 520, pose, t, { wind: .9 }) });
  const push = 1 + .06 * ease.io(lt / .88);
  g.save(); g.translate(W / 2, H * .7); g.scale(push, push); g.translate(-W / 2, -H * .7);
  DP.flush(g, V, items);
  g.restore();
  // leaves / dust blown across on the wind of the spell
  for (let i = 0; i < 14; i++) { const u = ((t - t0) * .9 + hash(i)) % 1; K.ellipse(g, -50 + u * 1200, 500 + hash(i * 3) * 1100 + Math.sin(u * 9 + i) * 40, 10, 5, { fill: '#8a6a3a', lw: 2 }, u * 9 + i); }
}

// ---------------------------------------------------------------- 17: the rats freeze on the trill, turn their heads, rise in the silence
function shot17(g, t, lt) {
  const t0 = b(10, 8);
  const freeze = t0 + HIT, turn = b(10, 12) + HIT, rise = C.BM.gaps[1] + HIT;
  const V = new Wd.View({ cx: lerp(-20, 20, ease.io(clamp(lt / .88))), cy: 70, cz: 0, f: 1000, hy: 1180 });
  PO.blurred(g, 6, (g2) => {
    ST.streetBackdrop(g2, V, t, 'day', { sunX: 830 });
    const it2 = []; DP.wall(it2, 2400, 7, { sp: 620, seed: 57, mood: 'day' });
    it2.push({ z: 1900, draw: (g3, V2) => ST.actor(g3, V2, CAST.piper, 0, 1900, tt => R.merge(PP.playPose(tt), { yaw: 0 }), t, { occlude: false }) });
    Wd.drawItems(g2, V, it2);
  });
  E.LIGHTS.length = 0;
  const items = [];
  const rows = [[300, 4], [400, 5], [520, 6], [680, 7], [880, 9], [1100, 10], [1400, 12]];
  rows.forEach(([z, n], ri) => {
    for (let i = 0; i < n; i++) {
      const id = ri * 20 + i, dir = (ri + i) % 2 ? 1 : -1;
      const sp = 300 + hash(id) * 220, tm = Math.min(t, freeze);
      const span = 2.3 * z;
      const x = ((-span / 2 + (i + .5) * span / n + dir * (tm - b(10)) * sp + hash(id * 3) * 120) % span + span * 1.5) % span - span / 2;
      const look = ease.back(clamp((t - turn) / .1));
      const stand = ease.back(clamp((t - rise - ri * .012) / .14));
      const ear = t > freeze ? C.decay(C.fluteOnsetSince(t + HIT), 10) : 0;
      const sway = stand * Math.sin(TAU * (t - rise) / (2 * BEAT)) * .12;
      items.push({ z, draw: (g2, V2) => ST.ratAt(g2, V2, x, z, { dir, phase: (tm - b(10)) * sp / 110, speed: t < freeze ? 1 : 0, t, ear, look, eyeGlow: look > .5, size: 1.25, stand, tilt: sway, tail: t < freeze ? 1 : .2 + .8 * stand }) });
    }
  });
  Wd.drawItems(g, V, items);
}

module.exports = [
  { id: '12_gate', t0: b(6), mood: 'warm', draw: shot12 },
  { id: '13_stranger_strides', t0: b(7), mood: 'day', draw: shot13, flashIn: true },
  { id: '14_the_offer', t0: b(8), mood: 'warm', draw: shot14 },
  { id: '15_the_agreement', t0: b(9), mood: 'warm', draw: shot15 },
  { id: '16_raises_flute', t0: b(10), mood: 'day', draw: shot16 },
  { id: '17_rats_freeze', t0: b(10, 8), mood: 'day', draw: shot17 },
];
module.exports.helpers = { piperWalk, PSPEED, PSTRIDE };
