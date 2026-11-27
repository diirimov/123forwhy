// 01-02: the hook -- moonlit procession, heads snap to camera; extreme close-up of the Piper
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
const { barT: b, clamp, lerp, ease, tween, BEAT, HIT, W, H, TAU } = C;

const HANG = C.BM.accents.find(a => a.description.startsWith('Tritone')).time;   // 1.3235: D#5 hang

// the procession: shared by the opening and (empty) by the ending street
const DIR = [0.45, 0.89];                        // procession line recedes to the right/back, into the fog
const SPEED = 62 / (2 * BEAT);                    // stride 62 per 2 beats
function processionKids(n = 22) {
  const r = C.rng(41); const out = [];
  for (let i = 0; i < n; i++) out.push({ ch: CAST.child(i + 1), d: 330 + i * 205 + (r() - .5) * 40, lat: (i % 2 ? 1 : -1) * (30 + r() * 25) });
  return out;
}
const KIDS = processionKids();
function nightStreet(g, V, t, o = {}) {
  ST.streetBackdrop(g, V, t, 'night', { moonX: o.moonX ?? 760, moonY: o.moonY ?? 300, moonR: 100 });
}

function shot01(g, t, lt) {
  const V = new Wd.View({ cx: lerp(30, -10, ease.io(lt / 1.77)), cy: 300, cz: lerp(-40, 40, ease.io(lt / 1.77)), f: 1250, hy: 1190 });
  nightStreet(g, V, t);
  const items = Wd.streetItems({ mood: 'night', lit: .3, seed: 8, half: 900, z0: 700 });
  // warm torch on the left foreground house
  items.push(Wd.propItem(-1250, 1300, (g2, s) => E.torch(g2, 0, -760, { t, s: 2.6, lw: 4 / s })));
  const x0 = -150, z0 = 700;
  const travel = SPEED * t;
  const pos = d => [x0 + DIR[0] * (d - travel), z0 + DIR[1] * (d - travel)];
  const yawWalk = -Math.atan2(DIR[0], DIR[1]);          // facing back along the line (toward camera-left)
  // Piper leads, playing while walking
  const pp = pos(0);
  items.push({ z: pp[1], draw: (g2, V2) => ST.actor(g2, V2, CAST.piper, pp[0], pp[1], (tt) => {
    const P = PP.playPose(tt, { eyes: 'narrow' });
    const Wk = R.walk(ST.stridePh(tt), { B: CAST.piper.B, stride: 100, bob: 2.5, arm: 0 });
    return R.merge(P, { legs: Wk.legs, toe: Wk.toe, bob: Wk.bob * .6, sway: Wk.sway * .5, hipRoll: Wk.hipRoll * .5, yaw: yawWalk + .25 });
  }, t, { wind: .4 }) });
  // children: synchronised, heads snap to camera on the D#5 hang
  for (const k of KIDS) {
    const p = pos(k.d);
    const px = p[0] + k.lat * DIR[1], pz = p[1] - k.lat * DIR[0];
    items.push({ z: pz, draw: (g2, V2) => ST.actor(g2, V2, k.ch, px, pz, ST.hypnoWalker(k.ch.B, {
      stride: 62, yaw: yawWalk, pitch: tt => lerp(.3, -.02, ease.back(clamp((tt - HANG + HIT) / .11))),
      headYaw: tt => -yawWalk * ease.back(clamp((tt - HANG + HIT) / .11)) * .95,
      face: tt => ({ eyes: tt > HANG ? 'half' : 'closed', mouth: 'peace', glint: tt > HANG ? 1.5 : .3, look: [0, 0] }),
    }), t) });
  }
  Wd.drawItems(g, V, items);
  E.fog(g, 980, 520, t, { col: '#aab9de', a: .4, speed: 22 });
  E.fog(g, 1300, 460, t, { col: '#9fb0d8', a: .22, speed: -14, off: 400 });
}

function shot02(g, t, lt) {
  const dur = b(2) - b(1);
  const push = 1 + .06 * ease.io(lt / dur);
  g.save();
  // background: night street out of focus (bokeh windows), moon rim
  const gr = g.createLinearGradient(0, 0, 0, H); gr.addColorStop(0, '#1a2138'); gr.addColorStop(1, '#2c3554'); g.fillStyle = gr; g.fillRect(0, 0, W, H);
  PO.blurred(g, 14, (g2) => {
    const r = C.rng(5);
    for (let i = 0; i < 26; i++) { const x = r() * W, y = 200 + r() * 1300; g2.fillStyle = r() < .5 ? '#f3b860' : '#8ea4d8'; g2.globalAlpha = .55; g2.beginPath(); g2.arc(x + Math.sin(t * .3 + i) * 6, y, 12 + r() * 26, 0, TAU); g2.fill(); }
    g2.globalAlpha = 1;
    for (let i = 0; i < 7; i++) E.house(g2, -200 + i * 220, 1500, 200, 360, { seed: 60 + i, mood: 'night', lit: .5, lw: 4 });
  });
  E.LIGHTS.length = 0;     // bokeh background: its windows are already bright in the art
  E.addLight(g, 900, 180, 700, '#8fa6d8', .45);
  E.addLight(g, 120, 900, 620, '#f09a4a', .35);     // warm torch key from frame left
  g.translate(W / 2, H * .52); g.scale(push, push); g.translate(-W / 2, -H * .52);
  // the Piper, very close: head + collar + cloak, recorder angled down-left
  const eyesOpen = t > 1.99 - .02;
  const P = R.merge(R.idle(t, { B: CAST.piper.B, shift: .2 }), {
    yaw: .18, lean: .02,
    head: { yaw: -.12 + (eyesOpen ? .08 : 0), pitch: .16 - (eyesOpen ? .06 : 0) * ease.o(clamp((t - 1.99) / .2)), roll: .08 + .04 * C.springHit(t - 2.43, 3, 6) },
    face: { mouth: 'flute', eyes: eyesOpen ? 'open' : 'closed', brow: 'sly', look: [-.1, .05], glint: 1.6, glow: eyesOpen ? .6 * ease.o(clamp((t - 1.99) / .25)) : 0, pupil: .8 },
    arms: { l: { swing: .4, out: .5, elbow: 1.4 }, r: { swing: .4, out: .5, elbow: 1.4 } }, hands: { l: 'none', r: 'none' },
  });
  const S = 4.6;
  PS.drawPerson(g, CAST.piper, P, { x: 560, y: 905 + 455 * S, s: S, lw: 7, t, wind: .3, shadow: false, noArms: true });
  // the recorder and articulated fingers (fingering follows the real giggle notes)
  PP.closeupFlute(g, 548, 1000, 2.02, 1.32, t, { lw: 6 });
  g.restore();
}

module.exports = [
  { id: '01_procession', t0: 0, mood: 'night', draw: shot01, finish: () => ({ vig: .7 }) },
  { id: '02_piper_closeup', t0: b(1), mood: 'night', draw: shot02, finish: () => ({ vig: .75 }) },
];
module.exports.helpers = { KIDS, DIR, SPEED, nightStreet, processionKids };
