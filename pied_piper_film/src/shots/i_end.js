// 33-37: the disappearance and the legend -- empty bed, abandoned toys, the empty street, the Piper in the fog, title (loops)
'use strict';
const C = require('../core');
const R = require('../rig');
const PS = require('../person');
const CAST = require('../cast');
const E = require('../env');
const Wd = require('../world');
const ST = require('../stage');
const PP = require('../piper');
const IN = require('../interior');
const K = require('../ink');
const PO = require('../post');
const OPEN = require('./a_open').helpers;
const { barT: b, clamp, lerp, ease, BEAT, BAR, S16, HIT, W, H, TAU, hash, EV } = C;
const { PAL } = K;

// ---------------------------------------------------------------- 33: the mother finds the empty bed
function shot33(g, t, lt) {
  const t0 = b(32);
  const push = 1 + .06 * ease.io(lt / 1.77);
  g.save(); g.translate(W / 2, H * .6); g.scale(push, push); g.translate(-W / 2, -H * .6);
  IN.bedroom(g, t, { empty: 1, winX: 150, bedX: 560 });
  // the door (right edge) opens; warm candlelight spills in
  const open = ease.io(clamp((t - t0) / .5));
  K.shape(g, [[880, 1250], [1060, 1250], [1060, 760], [880, 760]], { fill: lerp(0, 1, open) > .2 ? '#e6a860' : '#5e3d27', lw: 6, smooth: false });
  // mother enters with the candle: hand to her mouth on the second beat
  const mp = tt => {
    const u = ease.o3(clamp((tt - b(32, 4) - HIT) / .3));
    const walkIn = clamp((tt - t0 - .2) / .8);
    const P = walkIn < 1 ? R.walk(ST.stridePh(tt, t0), { stride: 60, bob: 4, arm: .2 }) : R.idle(tt, { seed: 4 });
    return R.merge(P, { yaw: -.9, lean: .05 * u, head: { pitch: .15 * u, yaw: .1, roll: -.05 * u },
      arms: { l: { swing: lerp(1.3, 2.0, u), out: .1, elbow: lerp(1.2, 2.2, u) }, r: { swing: 1.15, out: .15, elbow: 1.0 } }, hands: { l: u > .5 ? 'open' : 'mitten' },
      face: { eyes: u > .3 ? 'wide' : 'open', mouth: u > .3 ? 'gasp' : 'closed', brow: 'worry', look: [-.8, .4], tear: u > .7 ? (tt - b(32, 4) - .7) * .8 % 1 : 0 } });
  };
  const mx = lerp(1080, 900, ease.io(clamp((t - t0 - .2) / .8)));
  const J = PS.drawPerson(g, CAST.mother, mp(t), { x: mx, y: 1640, s: 2.0, lw: 6.5, lagA: mp(t - .07), lagB: mp(t - .16), t });
  // the candle in her right hand
  const hand = R.proj(J, J.wrr); const cx = mx + hand[0] * 2.0, cy = 1640 + hand[1] * 2.0;
  K.shape(g, [[cx - 9, cy - 4], [cx + 9, cy - 4], [cx + 9, cy - 64], [cx - 9, cy - 64]], { fill: '#efe6d2', lw: 4, smooth: false });
  K.shape(g, [[cx, cy - 104 + Math.sin(t * 13) * 4], [cx + 8, cy - 76], [cx, cy - 64], [cx - 8, cy - 76]], { fill: '#f6c24a', lw: 3 });
  E.addLight(g, cx, cy - 80, 900, '#f3a64a', .85); E.addLight(g, cx, cy - 80, 160, '#ffe7a8', .9); E.addLight(g, 970, 1000, 700, '#e6a050', .5);
  g.restore();
}

// ---------------------------------------------------------------- 34: abandoned toys -- the horse still rocking
function shot34(g, t, lt) {
  const t0 = b(33);
  const V = new Wd.View({ cx: lerp(-40, 40, ease.io(lt / 1.77)), cy: 70, cz: 0, f: 1050, hy: 1080 });
  // a doorstep at floor level: the open door, the moonlit street beyond, out of focus
  PO.blurred(g, 8, (g2) => {
    ST.streetBackdrop(g2, new Wd.View({ cx: 0, cy: 300, f: 1100, hy: 1050 }), t, 'night', { moonX: 540, moonY: 420 });
    Wd.drawItems(g2, new Wd.View({ cx: 0, cy: 300, f: 1100, hy: 1050 }), Wd.streetItems({ mood: 'night', lit: .2, seed: 330, half: 700, z0: 900 }));
  });
  E.LIGHTS.length = 0;
  // door frame (dark interior edges)
  K.shape(g, [[-40, -40], [190, -40], [190, H + 40], [-40, H + 40]], { fill: '#3a2618', lw: 6, smooth: false });
  K.shape(g, [[890, -40], [W + 40, -40], [W + 40, H + 40], [890, H + 40]], { fill: '#3a2618', lw: 6, smooth: false });
  // wooden floor boards in perspective
  K.shape(g, [[-40, 1350], [W + 40, 1350], [W + 40, H + 40], [-40, H + 40]], { fill: '#6e4e34', lw: 5, smooth: false, inner: g2 => { g2.strokeStyle = 'rgba(30,15,5,.45)'; g2.lineWidth = 3; for (let i = -10; i < 12; i++) { g2.beginPath(); g2.moveTo(540 + i * 40, 1350); g2.lineTo(540 + i * 260, H); g2.stroke(); } } });
  // toys: the horse rocking down to rest, a spinning top wobbling, a doll fallen on its side
  const rock = Math.sin((t - t0) * 5.2) * .16 * Math.exp(-(t - t0) * .5);
  E.toyHorse(g, 560, 1600, 2.4, { lw: 7, rock });
  const wob = Math.sin((t - t0) * 9) * .3 * Math.exp(-(t - t0) * .9) + .25;
  E.spinTop(g, 860, 1720, 2.2, { lw: 7, tilt: wob });
  E.doll(g, 250, 1760, 2.4, { lw: 7, rot: -1.45 });
  E.addLight(g, 540, 900, 700, '#8fa6d8', .35);
}

// ---------------------------------------------------------------- 35-37: the empty street from the opening; the Piper in the fog; title; loop
const V0 = (lt, dur) => new Wd.View({ cx: 30, cy: 300, cz: -40, f: 1250, hy: 1190 });   // exactly shot 01's first frame
function emptyStreet(g, t, V, o = {}) {
  OPEN.nightStreet(g, V, t);
  const items = Wd.streetItems({ mood: 'night', lit: .3, seed: 8, half: 900, z0: 700 });
  items.push(Wd.propItem(-1250, 1300, (g2, s) => E.torch(g2, 0, -760, { t, s: 2.6, lw: 4 / s })));
  if (o.toy) items.push(Wd.propItem(-60, 760, (g2, s) => E.toyHorse(g2, 0, 0, 1.25, { lw: 5 / s, rock: 0 })));
  if (o.piper) items.push({ z: o.piperZ, draw: (g2, V2) => {
    const [sx, sy, s] = V2.p(o.piperX, 0, o.piperZ);
    g2.save(); g2.globalAlpha = o.piperA;
    PS.drawPerson(g2, CAST.piper, R.merge(R.idle(t * .2, { B: CAST.piper.B, shift: .02 }), { yaw: Math.PI * .15, arms: o.playing ? PP.playPose(t).arms : undefined, hands: o.playing ? { l: 'none', r: 'none' } : undefined }),
      { x: sx, y: sy, s, sil: '#151a2c', lw: 2.5, t, wind: .3, shadow: false });
    g2.restore();
    E.addLight(g2, sx, sy - 420 * s, 260 * s + 60, '#9fb4e6', .35 * o.piperA);
  } });
  Wd.drawItems(g, V, items);
  E.fog(g, 980, 520, t, { col: '#aab9de', a: .45, speed: 22 });
  E.fog(g, 1300, 460, t, { col: '#9fb0d8', a: .25, speed: -14, off: 400 });
}
function shot35(g, t, lt) {
  const V = new Wd.View({ cx: lerp(-30, 10, ease.io(lt / 1.77)), cy: 260, cz: lerp(-200, -120, ease.io(lt / 1.77)), f: 1250, hy: 1190 });
  emptyStreet(g, t, V, { toy: true });
}
function shot36(g, t, lt) {
  const t0 = b(35);
  const V = new Wd.View({ cx: lerp(10, 30, ease.io(lt / 1.77)), cy: lerp(260, 290, lt / 1.77), cz: lerp(-120, -60, ease.io(lt / 1.77)), f: 1250, hy: 1190 });
  const a = ease.io(clamp((t - t0 - .2) / .9));
  emptyStreet(g, t, V, { toy: true, piper: true, piperX: 120, piperZ: 2700, piperA: a * .92, playing: t > b(35, 8) });
}
function shot37(g, t, lt) {
  const t0 = b(36);
  // he dissolves into the fog on the last giggle; the camera settles exactly on the opening frame
  const gig = C.FL.filter(n => n.t >= t0).map(n => n.t);
  const fadeA = gig.length >= 3 ? 1 - ease.io(clamp((t - gig[0]) / (gig[2] + .25 - gig[0]))) : 1;
  const u = ease.io(clamp(lt / 1.6));
  const V = new Wd.View({ cx: lerp(30, 30, u), cy: lerp(290, 300, u), cz: lerp(-60, -40, u), f: 1250, hy: 1190 });
  emptyStreet(g, t, V, { toy: lt < 1.2, piper: true, piperX: 120, piperZ: 2700, piperA: .92 * fadeA, playing: true });
  // the toy slips away into the fog too (so the last frame equals the procession's street)
  if (lt >= 1.2 && lt < 1.6) { const [sx, sy, s] = V.p(-60, 0, 760); g.save(); g.globalAlpha = 1 - (lt - 1.2) / .4; g.translate(sx, sy); g.scale(s, s); E.toyHorse(g, 0, 0, 1.25, { lw: 5 / s }); g.restore(); }
}

module.exports = [
  { id: '33_empty_bed', t0: b(32), mood: 'night', draw: shot33 },
  { id: '34_abandoned_toys', t0: b(33), mood: 'night', draw: shot34 },
  { id: '35_empty_street', t0: b(34), mood: 'night', draw: shot35 },
  { id: '36_piper_in_fog', t0: b(35), mood: 'night', draw: shot36 },
  { id: '37_legend_title', t0: b(36), mood: 'night', draw: shot37, finish: () => ({ vig: .7 }) },
];
