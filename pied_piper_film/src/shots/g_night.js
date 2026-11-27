// 24-27: FINAL DROP -- the second melody at night; windows burst open; the children rise and follow
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
const IN = require('../interior');
const K = require('../ink');
const PO = require('../post');
const OPEN = require('./a_open').helpers;
const { barT: b, clamp, lerp, ease, BEAT, BAR, S16, HIT, W, H, TAU, hash, EV } = C;
const { PAL } = K;
const GAP2 = C.BM.gaps[2];   // 47.537

// ---------------------------------------------------------------- 24: the Piper alone in the moonlit square; windows burst open on the beat
function shot24(g, t, lt) {
  const t0 = b(23);
  const punch = 1 + .04 * C.decay(t - t0 - HIT, 4);
  const V = new Wd.View({ cx: 0, cy: lerp(250, 290, ease.io(lt / 1.77)), cz: lerp(-60, 90, ease.io(lt / 1.77)), f: 1150 * punch, hy: 1180 });
  ST.streetBackdrop(g, V, t, 'night', { moonX: 540, moonY: 420, moonR: 150 });
  // every window opens on an eighth note, cascading outward from the Piper
  const shutter = (side, i, idx) => {
    const order = Math.round((hash(idx * 1.7 + side * 3 + i * 7) * .8 + Math.min(i, 8) * .07) / (BEAT / 2));
    const to = t0 + order * BEAT / 2 + HIT;
    return ease.back(clamp((t - to) / .12));
  };
  const items = Wd.streetItems({ mood: 'night', seed: 240, half: 640, z0: 650, z1: 5200, shutter, house: { litByShutter: true, allWindows: true } });
  items.push({ z: 980, draw: (g2, V2) => ST.actor(g2, V2, CAST.piper, 0, 980, tt => R.merge(PP.playPose(tt, { eyes: 'narrow', glow: .7 }), { yaw: .15 }), t, { wind: .5 }) });
  Wd.drawItems(g, V, items);
  E.fog(g, 1120, 520, t, { col: '#aab9de', a: .38, speed: 24 });
  E.fog(g, 1380, 400, t, { col: '#9fb0d8', a: .22, speed: -16, off: 300 });
}

// ---------------------------------------------------------------- 25: inside -- a toy drops (stab 1), a girl turns (stab 2); the rat on the sill never moves
function shot25(g, t, lt) {
  const t0 = b(24), s1 = t0 + HIT, s2 = b(24, 3) + HIT;
  const push = 1 + .05 * ease.io(lt / 1.77);
  g.save(); g.translate(W / 2, H * .6); g.scale(push, push); g.translate(-W / 2, -H * .6);
  IN.bedroom(g, t, { empty: 0, winX: 180, bedX: 620 });
  // the rat on the windowsill: perfectly still, staring
  RT.ratSide(g, 300, 878, { s: 1.0, dir: 1, speed: 0, look: 1, t, shadow: false, tail: 0 });
  // girl at the window turns her head toward the sound on stab 2
  const girl = tt => { const u = ease.back(clamp((tt - s2) / .12)); return R.merge(R.idle(tt, { B: R.BODY.child, seed: 3 }), { yaw: lerp(2.6, .35, u), head: { yaw: lerp(.3, -.2, u), pitch: .05 }, face: { eyes: u > .5 ? 'half' : 'open', mouth: u > .5 ? 'peace' : 'closed', look: [-.3, 0], glint: 1.4 } }); };
  PS.drawPerson(g, CAST.girl1, girl(t), { x: 430, y: 1400, s: 1.6, lw: 6, lagA: girl(t - .07), lagB: girl(t - .16), t });
  // boy on the floor drops the wooden horse on stab 1, then rises
  const drop = clamp((t - s1) / .3);
  const boy = tt => { const u = ease.o3(clamp((tt - s1) / .18)); const rise = ease.io(clamp((tt - s1 - .6) / .7)); return R.merge(R.idle(tt, { B: R.BODY.child, seed: 5 }), { yaw: -.3 + .2 * u, bob: lerp(-34, 0, rise), knees: { l: .5 * (1 - rise), r: .5 * (1 - rise) },
    arms: { l: { swing: lerp(1.0, .1, u), out: .2, elbow: lerp(1.0, .2, u) }, r: { swing: lerp(1.0, .1, u), out: .2, elbow: lerp(1.0, .2, u) } }, head: { yaw: .3 * u, pitch: lerp(.3, -.05, u) },
    face: { eyes: u > .5 ? 'half' : 'open', mouth: u > .5 ? 'peace' : 'smile', glint: 1.3, look: [.2, 0] } }); };
  PS.drawPerson(g, CAST.boy1, boy(t), { x: 760, y: 1700, s: 1.9, lw: 6.5, lagA: boy(t - .07), lagB: boy(t - .16), t });
  E.toyHorse(g, 640 + drop * 20, 1560 + ease.i(drop) * 140, 1.3, { lw: 6, rock: drop < 1 ? drop * .5 : Math.sin((t - s1 - .3) * 8) * .15 * Math.exp(-(t - s1 - .3) * 2) });
  g.restore();
}

// ---------------------------------------------------------------- 26: doors open on the beats; children step out in matching strides
function shot26(g, t, lt) {
  const t0 = b(25);
  const V = new Wd.View({ cx: lerp(-40, 40, ease.io(lt / 1.77)), cy: 300, cz: 0, f: 1150, hy: 1120 });
  ST.streetBackdrop(g, V, t, 'night', { moonX: 820, moonY: 330 });
  const items = Wd.streetItems({ mood: 'night', lit: .8, seed: 260, half: 1300, z0: 3200, z1: 6000, house: { allWindows: true } });
  // explicit facades facing us with known doors: one opens on each beat and a child steps out
  const homes = [[-330, 1300, 0], [350, 1500, 1], [-300, 2150, 2], [320, 2350, 3], [-180, 3000, 1.5], [200, 3150, 2.5]];
  homes.forEach(([x, z, k], i) => {
    const td = t0 + k * BEAT + HIT;
    const open = ease.io(clamp((t - td) / .22));
    items.push(Wd.houseItem(x + (x < 0 ? -1 : 1) * 200, z, 250, 330 + hash(i) * 80, { seed: 600 + i, mood: 'night', lit: .7, doorOpen: open, doorX: .5, allWindows: true }));
    const te = td + .28; if (t < te) return;
    const ch = CAST.child(30 + i);
    const out = clamp((t - te) / .55);
    const walk = Math.max(0, t - te - .55);
    const cx = lerp(x + (x < 0 ? -1 : 1) * 200, x * .15, clamp(walk * .9)), cz = z - 70 - out * 140 - walk * 60;
    const yaw = out < 1 ? 0 : (x < 0 ? 1.1 : -1.1) * clamp(walk * 3);
    items.push({ z: cz, draw: (g2, V2) => ST.actor(g2, V2, ch, cx, cz, ST.hypnoWalker(ch.B, { yaw, t0: te, face: { eyes: 'half', mouth: 'peace', glint: 1.4 } }), t) });
  });
  Wd.drawItems(g, V, items);
  E.fog(g, 1150, 500, t, { col: '#aab9de', a: .3, speed: 20 });
}

// ---------------------------------------------------------------- 27: the procession grows -- then freezes and turns to camera in the silence
function shot27(g, t, lt) {
  const t0 = b(26);
  const frozen = t >= GAP2 - .005;
  const tm = frozen ? GAP2 : t;                       // time stops for the walkers during the silence
  const V = new Wd.View({ cx: 0, cy: 300, cz: lerp(-30, 60, ease.io(lt / 1.77)), f: 1250, hy: 1190 });
  OPEN.nightStreet(g, V, t, { moonX: 330, moonY: 330 });
  const items = Wd.streetItems({ mood: 'night', lit: .4, seed: 270, half: 900, z0: 700 });
  const DIR = [.45, .89], SPEED = 62 / (2 * BEAT);
  const travel = SPEED * (tm - t0);
  const yawWalk = -Math.atan2(DIR[0], DIR[1]);
  const kids = OPEN.KIDS.slice(0, 16);
  kids.forEach((k, i) => {
    // children join one by one from the side alleys (one per eighth), sliding into the line
    const join = t0 + i * BEAT / 2 - .9;
    const sideIn = clamp((tm - join) / .7);
    const d = k.d - 330 + 240 - travel;
    const px = 40 + DIR[0] * d + k.lat * DIR[1] + (1 - ease.io(sideIn)) * (i % 2 ? 700 : -700), pz = 760 + DIR[1] * d - k.lat * DIR[0];
    if (sideIn <= 0) return;
    items.push({ z: pz, draw: (g2, V2) => ST.actor(g2, V2, k.ch, px, pz, tt => {
      const P = ST.hypnoWalker(k.ch.B, { stride: 62, yaw: yawWalk, t0, face: { eyes: 'half', mouth: 'peace', glint: 1.3 } })(Math.min(tt, GAP2));
      if (tt >= GAP2) { const u = ease.back(clamp((tt - GAP2) / .08)); P.head = { yaw: -yawWalk * u, pitch: -.05, roll: 0 }; P.face = { eyes: 'open', mouth: 'flat', glint: 1.8, pupil: .7 }; }
      return P;
    }, t) });
  });
  Wd.drawItems(g, V, items);
  E.fog(g, 1000, 520, t, { col: '#aab9de', a: .4, speed: frozen ? 0 : 22 });
}

module.exports = [
  { id: '24_windows_burst', t0: b(23), mood: 'night', draw: shot24, flashIn: true },
  { id: '25_toy_drops', t0: b(24), mood: 'night', draw: shot25 },
  { id: '26_doors_open', t0: b(25), mood: 'night', draw: shot26 },
  { id: '27_procession_grows', t0: b(26), mood: 'night', draw: shot27 },
];
