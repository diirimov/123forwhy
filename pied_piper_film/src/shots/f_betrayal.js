// 19-23: the celebration, the refusal, the change, the departure into night
'use strict';
const C = require('../core');
const R = require('../rig');
const PS = require('../person');
const CAST = require('../cast');
const E = require('../env');
const Wd = require('../world');
const ST = require('../stage');
const PP = require('../piper');
const K = require('../ink');
const PO = require('../post');
const CS = require('./c_stranger').helpers;
const { barT: b, clamp, lerp, ease, BEAT, BAR, S16, HIT, W, H, TAU, hash, EV } = C;
const { PAL } = K;
const PB = CAST.piper.B;
const GAP1 = C.BM.gaps[1];   // 40.368

// ---------------------------------------------------------------- 19: the celebration -- everyone in the same dance, too perfectly
function shot19(g, t, lt) {
  const t0 = b(18);
  const V = new Wd.View({ cx: lerp(-80, 60, ease.io(lt / 1.77)), cy: 300, cz: lerp(0, 160, ease.io(lt / 1.77)), f: 1150, hy: 1020 });
  ST.streetBackdrop(g, V, t, 'day', { sunX: 860, clouds: [[220, 300, 1.1]] });
  const items = Wd.streetItems({ mood: 'day', seed: 88, half: 950, z0: 1600 });
  const dancers = [[CAST.merchant, -380, 1150], [CAST.baker, 60, 1050], [CAST.guard, 430, 1180], [CAST.woman, -150, 1450], [CAST.farmer, 260, 1500],
    ...Array.from({ length: 11 }, (_, i) => [CAST.townsfolk(60 + i), -700 + (i % 6) * 280 + hash(i) * 60, 1750 + Math.floor(i / 6) * 330])];
  dancers.forEach(([ch, x, z], i) => {
    items.push({ z, draw: (g2, V2) => ST.actor(g2, V2, ch, x, z, tt => {
      const n = C.beatIndex(tt), ph = C.beatPhase(tt);
      const P = (i % 5 === 3) ? R.jig(ph, n, { amt: .8, handsUp: i % 2 === 0 }) : R.squatDance(ph, n, { amt: .95 });
      return R.merge(P, { yaw: (x > 0 ? -.25 : .25) + Math.sin(tt * .7 + i) * .05, face: { eyes: 'narrow', mouth: i % 3 ? 'laugh' : 'grin', brow: 'raised' } });
    }, t) });
  });
  // the Piper watching from the edge, utterly still
  items.push({ z: 760, draw: (g2, V2) => ST.actor(g2, V2, CAST.piper, -720, 760, tt => R.merge(R.idle(tt * .15, { B: PB, shift: .02 }), { yaw: .6, head: { yaw: .2, pitch: .08 }, face: { eyes: 'narrow', mouth: 'sly', brow: 'sly', look: [.5, 0] },
    arms: { l: { swing: .25, out: .05, elbow: 1.2 }, r: { swing: .25, out: .05, elbow: 1.2 } } }), t, { wind: .1 }) });
  Wd.drawItems(g, V, items);
  for (let i = 0; i < 3; i++) { const y = 300 + i * 180; E.bunting(g, -40, y, W + 40, y + 40, 90, t); }
}

// ---------------------------------------------------------------- 20: he holds out his hand -- the chest slams shut on the falling bend
const BEND = C.FL.find(n => n.t > b(19, 9.5) && n.t < b(20)).t;   // the Bb5 that bends down
function shot20(g, t, lt) {
  const slam = BEND + .12;
  g.save();
  CS.councilRoom(g, t);
  const shake = C.springHit(t - slam, 9, 10) * 10;
  g.translate(0, shake);
  // mayor behind the table (right), smug -> slam -> stern
  const mp = tt => {
    const s = ease.o3(clamp((tt - slam + .25) / .25));
    return R.merge(R.idle(tt, { seed: 42 }), { yaw: -.35, lean: .25 * s, head: { pitch: .1 * s, yaw: .2 },
      arms: { l: { swing: lerp(.4, 1.25, s), out: .1, elbow: lerp(.5, .1, s) }, r: { swing: lerp(.4, 1.2, s), out: .1, elbow: lerp(.5, .1, s) } },
      face: tt < slam ? { eyes: 'narrow', mouth: 'sly', brow: 'raised', look: [-.6, .2] } : { eyes: 'narrow', mouth: 'frown', brow: 'angry', look: [-.7, 0] } });
  };
  PS.drawPerson(g, CAST.mayor, mp(t), { x: 760, y: 1540, s: 1.55, lw: 5.5, lagA: mp(t - .07), lagB: mp(t - .16), t });
  // table + chest
  K.shape(g, [[100, 1330], [W - 40, 1330], [W, 1600], [60, 1600]], { fill: '#2f5a3c', lw: 6, smooth: false });
  const lid = t < slam ? 1 - ease.i(clamp((t - slam + .1) / .1)) * 0 : 0;
  const lidAng = t < slam - .1 ? .9 : t < slam ? lerp(.9, 0, ease.i((t - slam + .1) / .1)) : 0;
  E.chest(g, 640, 1345, 1.6, { lid: lidAng, lw: 6 });
  if (t > slam) for (let i = 0; i < 6; i++) { const dt = t - slam; const x = 640 + (i - 2.5) * 70 + dt * (i - 2.5) * 260, y = 1180 - 380 * dt + 1900 * dt * dt; if (y < 1340) K.ellipse(g, x, y, 13, 8, { fill: PAL.gold, lw: 3 }, dt * 9 + i); }
  // the Piper (left, profile), palm out -- then the hand hesitates
  const pp = tt => {
    const reach = ease.io(clamp((tt - b(19) + .1) / .4));
    const drop = ease.io(clamp((tt - slam - .1) / .5)) * .3;
    return R.merge(R.idle(tt * .3, { B: PB, shift: .05 }), { yaw: 1.25, lean: .05,
      arms: { r: { swing: lerp(.1, 1.35 - drop, reach), out: .05, elbow: .15 }, l: { swing: .1, out: .05, elbow: .3 } }, hands: { r: reach > .4 ? 'open' : 'mitten' },
      head: { yaw: -.1, pitch: .05 }, face: tt < slam ? { eyes: 'open', mouth: 'sly', brow: 'sly', look: [.8, 0] } : { eyes: 'narrow', mouth: 'flat', brow: 'neutral', look: [.9, 0] } });
  };
  PS.drawPerson(g, CAST.piper, pp(t), { x: 170, y: 1900, s: 1.85, lw: 6, lagA: pp(t - .07), lagB: pp(t - .16), t, wind: .1 });
  g.restore();
}

// ---------------------------------------------------------------- 21: waved away; silent laughter shaking on the eighths
function shot21(g, t, lt) {
  const t0 = b(20);
  const V = new Wd.View({ cx: lerp(40, -20, ease.io(lt / 1.77)), cy: 300, cz: 0, f: 1250, hy: 1000 });
  ST.streetBackdrop(g, V, t, 'day', { sunX: 900 });
  const items = Wd.streetItems({ mood: 'day', seed: 91, half: 1000, z0: 1800 });
  // town hall steps behind the officials
  items.push(Wd.propItem(0, 1700, (g2, s) => { K.shape(g2, [[-700, 0], [700, 0], [660, -60], [-660, -60]], { fill: '#b9a684', lw: 4 / s, smooth: false }); K.shape(g2, [[-640, -60], [640, -60], [600, -120], [-600, -120]], { fill: '#c7b493', lw: 4 / s, smooth: false }); }));
  const laugh = (sd, x, z, ch, yaw, extra = {}) => items.push({ z, draw: (g2, V2) => ST.actor(g2, V2, ch, x, z, tt => {
    const e8 = Math.abs(Math.sin(TAU * tt / (BEAT / 2)));
    return R.merge(R.idle(tt, { seed: sd }), { yaw, bob: -e8 * 5, lean: -.12 - .05 * e8, head: { pitch: -.25 - .06 * e8, roll: .05 * Math.sin(tt * 9 + sd) },
      arms: { l: { swing: .6, out: .3, elbow: 1.5 }, r: extra.point ? { swing: 1.5, out: -.2, elbow: .1 } : { swing: .7, out: .3, elbow: 1.4 } }, hands: extra.point ? { r: 'point' } : {},
      face: { eyes: 'closed', mouth: 'laugh', brow: 'raised' } });
  }, t) });
  laugh(1, 200, 1050, CAST.clerk, -.5, { point: true });
  laugh(2, 480, 1180, CAST.mayor, -.4);
  laugh(3, -60, 1300, CAST.guard, -.2);
  laugh(4, 700, 1350, CAST.townsfolk(70), -.6, { point: true });
  laugh(5, 880, 1080, CAST.townsfolk(71), -.7);
  laugh(6, -300, 1550, CAST.townsfolk(72), .2);
  // the councillor waves him off -- a dismissive flick on every beat
  items.push({ z: 960, draw: (g2, V2) => ST.actor(g2, V2, CAST.councillor, 300, 960, tt => {
    const ph = C.beatPhase(tt);
    const flick = Math.sin(Math.PI * clamp(ph * 2.5));
    return R.merge(R.idle(tt, { seed: 7 }), { yaw: -.75, lean: -.05, head: { pitch: -.1, yaw: -.2 }, arms: { r: { swing: 1.2 + .3 * flick, out: .2 + .9 * flick, elbow: .8 - .6 * flick }, l: { swing: .1, out: .1, elbow: .3 } },
      hands: { r: 'open' }, face: { eyes: 'narrow', mouth: 'sly', brow: 'raised', look: [-.8, 0] } });
  }, t) });
  // the Piper's back, foreground left
  items.push({ z: 760, draw: (g2, V2) => ST.actor(g2, V2, CAST.piper, -230, 760, tt => R.merge(R.idle(tt * .2, { B: PB, shift: .03 }), { yaw: Math.PI - .6, head: { yaw: .15 },
    arms: { r: { swing: lerp(.9, .2, ease.io(clamp((tt - t0) / 1.2))), out: .05, elbow: .2 } } }), t, { wind: .15 }) });
  Wd.drawItems(g, V, items);
}

// ---------------------------------------------------------------- 22: close-up -- the smile disappears; the light drains cold
function shot22(g, t, lt) {
  const t0 = b(21);
  const u = ease.io(clamp(lt / 1.6));
  PO.blurred(g, 12, (g2) => { E.sky(g2, 'day', W, 1100, t); g2.save(); g2.translate(0, 1300); let x = -50; for (let i = 0; i < 7; i++) { E.house(g2, x, 0, 200, 420, { seed: 120 + i, mood: 'day' }); x += 220; } g2.restore(); g2.fillStyle = '#9c8463'; g2.fillRect(0, 1300, W, 700); });
  E.LIGHTS.length = 0;
  const push = 1 + .1 * ease.io(lt / 1.77);
  g.save(); g.translate(W / 2, H * .42); g.scale(push, push); g.translate(-W / 2, -H * .42);
  const P = R.merge(R.idle(t * .2, { B: PB, shift: .02 }), { yaw: .25, head: { yaw: -.15, pitch: .12 + .1 * u },
    arms: { r: { swing: lerp(1.1, .15, u), out: .05, elbow: lerp(.2, .4, u) }, l: { swing: .1, out: .05, elbow: .3 } }, hands: { r: u < .6 ? 'open' : 'fist' },
    face: { eyes: u > .5 ? 'narrow' : 'open', mouth: u < .35 ? 'sly' : u < .7 ? 'closed' : 'flat', brow: u > .5 ? 'angry' : 'sly', look: [-.1 * u, .1], glint: lerp(1, .4, u), glow: .5 * u } });
  PS.drawPerson(g, CAST.piper, P, { x: 560, y: 2900, s: 4.3, lw: 8, t, wind: .2, shadow: false });
  g.restore();
}

// ---------------------------------------------------------------- 23: he turns away; his shadow climbs the wall; day becomes night
function shot23(g, t, lt) {
  const t0 = b(22);
  const night = ease.io(clamp((t - b(22, 6)) / (GAP1 - b(22, 6))));
  const V = new Wd.View({ cx: 0, cy: 300, cz: 0, f: 1150, hy: 1060 });
  // sky time-lapse: the sun sinks, the moon rises
  E.sky(g, 'day', W, V.hy + 200, t);
  g.save(); g.globalAlpha = night; E.sky(g, 'night', W, V.hy + 200, t); g.restore();
  E.sun(g, 820, lerp(240, 1100, night), 60, t);
  if (night > .3) { g.save(); g.globalAlpha = clamp((night - .3) / .5); E.moon(g, 300, lerp(1000, 300, night), 90); g.restore(); }
  E.skyline(g, -150, V.p(0, 0, 12000)[1] + 4, 1400, night > .5 ? 'night' : 'day', 4);
  Wd.ground(g, V, { mood: night > .5 ? 'night' : 'day' });
  const items = Wd.streetItems({ mood: night > .55 ? 'night' : 'day', lit: .5, seed: 97, half: 820, z0: 900 });
  // he turns (on the first beat) and walks away down the street; footsteps on the beats
  const turn = ease.io(clamp((t - t0) / .45));
  const walkStart = b(22, 4);
  const v = 104 / (2 * BEAT);
  const z = 900 + Math.max(0, t - walkStart) * v * 1.4;
  const pose = tt => {
    const tr = ease.io(clamp((tt - t0) / .45));
    if (tt < walkStart) return R.merge(R.idle(tt * .2, { B: PB, shift: .02 }), { yaw: lerp(.2, Math.PI, tr), head: { yaw: lerp(0, .4, tr) * (1 - tr) } });
    return R.merge(R.walk(ST.stridePh(tt, walkStart), { B: PB, stride: 104, bob: 2.4, arm: .14 }), { yaw: Math.PI });
  };
  items.push({ z, draw: (g2, V2) => {
    // the giant shadow on the right-hand wall grows as he moves away from the low sun / toward the moon
    const [sx, sy, s] = V2.p(0, 0, z);
    const grow = 1 + 2.2 * ease.i(clamp((t - t0) / 1.6));
    g2.save(); g2.globalAlpha = .55 * (1 - night * .3); g2.translate(sx + 160 + 120 * grow, sy); g2.transform(1, 0, -.35, 1, 0, 0);
    PS.drawPerson(g2, CAST.piper, pose(t), { x: 0, y: 0, s: s * grow, sil: '#1d1218', lw: 0, t, shadow: false, wind: .4 });
    g2.restore();
    ST.actor(g2, V2, CAST.piper, 0, z, pose, t, { wind: .4 });
  } });
  Wd.drawItems(g, V, items);
  E.fog(g, 980, 420, t, { col: night > .5 ? '#aab9de' : '#efe2c4', a: .25 + .2 * night, speed: 20 });
}

module.exports = [
  { id: '19_celebration_dance', t0: b(18), mood: 'day', draw: shot19, grade: () => ({ mood: 'day' }) },
  { id: '20_chest_slam', t0: b(19), mood: 'warm', draw: shot20 },
  { id: '21_refusal_laughter', t0: b(20), mood: 'day', draw: shot21 },
  { id: '22_smile_fades', t0: b(21), draw: shot22, grade: (t, lt) => ({ mood: 'warm', mood2: 'cold', mix: ease.io(clamp(lt / 1.6)) }) },
  { id: '23_walk_into_night', t0: b(22), draw: shot23, grade: (t, lt) => ({ mood: 'day', mood2: 'night', mix: ease.io(clamp((t - b(22, 6)) / (GAP1 - b(22, 6)))) }),
    finish: (t) => ({ fade: t > GAP1 ? .55 : 0 }) },
];
