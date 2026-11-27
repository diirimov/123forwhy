// 31-34 THE RETURN (bar 23): the flute alone in 16ths -- four cuts, one per beat: his silhouette in the
// moonlit street raises the flute; a child stops playing and the wooden horse falls; a candle bends toward
// the window as a girl's eyes open; shutters burst open in a cascade, then the silence (40.37): a child in
// every window, perfectly still.
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
const DP = require('../dp');
const { barT: b, clamp, lerp, ease, BEAT, S16, HIT, W, H, TAU, hash } = C;
const { PAL } = K;
const GAP = C.BM.gaps[2];          // 40.368

// ---------------------------------------------------------------- 31: his silhouette in the empty moonlit street raises the flute
function shot31(g, t, lt) {
  const t0 = b(22);
  const { V, items } = DP.town(g, t, { mood: 'night', cam: { cz: lerp(0, 60, lt / .44), cy: 190 }, moonX: 540, moonY: 560, moonR: 170, lit: .85, seed: 120, sides: true });
  const raise = ease.io(clamp((t - t0 + .05) / .3));
  items.push({ z: 1050, draw: (g2, V2) => {
    const [sx, sy, s] = V2.p(0, 0, 1050);
    const P = PP.playPose(t, { eyes: 'narrow', glow: .8 });
    if (raise < 1) { P.arms.l.hand = R.v(16, 20 + 120 * raise, 30 + 10 * raise); P.arms.r.hand = R.v(-10, -10 + 85 * raise, 40 + 10 * raise); }
    PS.drawPerson(g2, CAST.piper, P, { x: sx, y: sy, s, sil: '#0e0c18', lw: 3, t, wind: .7, shadow: false });
    E.addLight(g2, sx, sy - 380 * s, 300, '#9fb4e6', .3);
  } });
  // his shadow stretched toward us by the moon
  DP.flush(g, V, items);
  g.save(); g.globalAlpha = .35; g.fillStyle = '#0b0a14'; g.beginPath(); const [sx, sy] = V.p(0, 0, 1050); g.moveTo(sx - 18, sy); g.lineTo(sx + 18, sy); g.lineTo(sx + 160, H); g.lineTo(sx - 160, H); g.closePath(); g.fill(); g.restore();
  E.fog(g, 1080, 420, t, { col: '#aab9de', a: .35, speed: 18 });
}

// ---------------------------------------------------------------- 32: a child stops playing; the wooden horse falls from his hand
function shot32(g, t, lt) {
  const t0 = b(22, 4), drop = b(22, 6) + HIT;
  IN.bedroom(g, t, { empty: 0, winX: 120, bedX: 600 });
  E.LIGHTS.length = 0; E.addLight(g, 250, 680, 520, '#9fb4e6', .5);
  const push = 1 + .05 * ease.io(lt / .44);
  g.save(); g.translate(W / 2, H * .7); g.scale(push, push); g.translate(-W / 2, -H * .7);
  const boy = tt => { const u = ease.o3(clamp((tt - drop) / .15)); return R.merge(R.idle(tt, { B: R.BODY.child, seed: 5 }), { yaw: -.35, bob: -36, knees: { l: .5, r: .5 },
    arms: { l: { swing: lerp(1.1, .2, u), out: .2, elbow: lerp(1.1, .2, u) }, r: { swing: lerp(1.0, .15, u), out: .2, elbow: lerp(1.0, .2, u) } },
    head: { yaw: .35 * u, pitch: lerp(.3, -.08, u) }, face: { eyes: u > .5 ? 'half' : 'open', mouth: u > .5 ? 'peace' : 'smile', glint: 1.6, look: [.2, -.1] } }); };
  PS.drawPerson(g, CAST.boy1, boy(t), { x: 600, y: 1760, s: 2.6, lw: 7, lagA: boy(t - .07), lagB: boy(t - .16), t });
  const d = clamp((t - drop) / .25);
  E.toyHorse(g, 470 + d * 20, 1560 + ease.i(d) * 220, 1.6, { lw: 7, rock: d < 1 ? d * .6 : Math.sin((t - drop - .25) * 10) * .15 });
  g.restore();
}

// ---------------------------------------------------------------- 33: the candle bends toward the window; a girl's eyes open
function shot33(g, t, lt) {
  const t0 = b(22, 8);
  g.fillStyle = '#2a2236'; g.fillRect(0, 0, W, H);
  // window (right) with the moon, the sill with the candle
  K.shape(g, [[560, 300], [1000, 300], [1000, 1000], [560, 1000]], { fill: '#33416e', lw: 8, smooth: false, inner: g2 => { g2.fillStyle = '#f3ead2'; g2.beginPath(); g2.arc(860, 470, 80, 0, TAU); g2.fill(); g2.strokeStyle = 'rgba(30,30,40,.7)'; g2.lineWidth = 5; for (let i = -800; i < 800; i += 60) { g2.beginPath(); g2.moveTo(560 + i, 300); g2.lineTo(1260 + i, 1000); g2.stroke(); g2.beginPath(); g2.moveTo(1260 + i, 300); g2.lineTo(560 + i, 1000); g2.stroke(); } } });
  K.shape(g, [[520, 1000], [1060, 1000], [1060, 1040], [520, 1040]], { fill: '#8a6a4a', lw: 7, smooth: false });
  const bend = ease.io(clamp((t - t0 - .05) / .25));
  const fx = 700, fy = 1000;
  K.shape(g, [[fx - 22, fy], [fx + 22, fy], [fx + 22, fy - 160], [fx - 22, fy - 160]], { fill: '#efe6d2', lw: 6, smooth: false });
  const tipX = fx + 70 * bend + Math.sin(t * 30) * 4 * bend, tipY = fy - 250 + 40 * bend;
  K.shape(g, [[fx - 18, fy - 175], [tipX, tipY], [fx + 18, fy - 175], [fx, fy - 160]], { fill: '#f6c24a', lw: 4, tension: .5 });
  E.addLight(g, fx + 20 * bend, fy - 200, 700 * (1 - .4 * bend), '#f3a64a', .9 - .3 * bend);
  // the girl sits up in bed in the foreground: eyes open half-lidded, head turning toward the window
  const open = ease.o(clamp((t - t0 - .1) / .18));
  const turn = ease.io(clamp((t - t0 - .15) / .25));
  const P = R.merge(R.idle(t, { B: R.BODY.child, seed: 3 }), { yaw: .35, lean: .05,
    arms: { l: { swing: .3, out: .15, elbow: .4 }, r: { swing: .3, out: .15, elbow: .4 } },
    head: { yaw: lerp(-.1, .45, turn), pitch: .02, roll: .06 }, face: { eyes: open > .5 ? 'half' : 'closed', mouth: 'peace', glint: 2, look: [.5, -.2], pupil: .6 } });
  K.ellipse(g, 340, 1450, 300, 105, { fill: '#efe6d2', lw: 7 });                        // pillow behind her
  PS.drawPerson(g, CAST.girl1, P, { x: 340, y: 2230, s: 4.0, lw: 8, t, shadow: false });
  // the blanket pulled up to her waist, the bed frame
  K.shape(g, [[-40, 1640], [300, 1600], [700, 1620], [1000, 1660], [1000, H + 40], [-40, H + 40]], { fill: '#53719a', lw: 8, tension: .3,
    inner: g2 => { g2.strokeStyle = 'rgba(20,30,60,.35)'; g2.lineWidth = 5; for (let i = 0; i < 6; i++) { g2.beginPath(); g2.moveTo(80 + i * 160, 1660); g2.lineTo(120 + i * 160, H); g2.stroke(); } } });
}

// ---------------------------------------------------------------- 34: shutters burst open in a cascade -- then silence: a child in every window
function shot34(g, t, lt) {
  const t0 = b(22, 12);
  const V = new Wd.View({ cx: 0, cy: 860, cz: 0, f: 1150, hy: 760 });
  E.sky(g, 'night', W, H, t); E.moon(g, 880, 220, 110);
  Wd.ground(g, V, { mood: 'night' });
  const items = [];
  const order = (i, idx) => Math.floor(hash(i * 7.3 + idx * 1.9) * 6);
  const shutter = (i, idx) => { const k = order(i, idx); const ts = t0 + k * S16 * .33 + HIT; return ease.back(clamp((t - ts) / .1)); };
  DP.wall(items, 1250, 4, { sp: 640, seed: 140, mood: 'night', lit: 1, allWindows: true, litByShutter: true, shutter, h: 520, hv: 60 });
  DP.wall(items, 2200, 6, { sp: 600, seed: 150, mood: 'night', lit: .4, x0: 300 });
  Wd.drawItems(g, V, items);
  // in the silence every lit window dims at once, as if everyone inside stopped breathing
  if (t > GAP) { g.save(); g.globalAlpha = .35 * ease.o(clamp((t - GAP) / .1)); g.fillStyle = '#0a0a16'; g.fillRect(0, 0, W, H); g.restore(); }
}

module.exports = [
  { id: '31_he_returns', t0: b(22), mood: 'night', draw: shot31, flashIn: false, finish: () => ({ vig: .8 }) },
  { id: '32_toy_falls', t0: b(22, 4), mood: 'night', draw: shot32 },
  { id: '33_candle_bends', t0: b(22, 8), mood: 'night', draw: shot33, finish: () => ({ vig: .8 }) },
  { id: '34_shutters_burst', t0: b(22, 12), mood: 'night', draw: shot34, finish: (t) => ({ vig: .75, fade: t > GAP ? .25 : 0 }) },
];
