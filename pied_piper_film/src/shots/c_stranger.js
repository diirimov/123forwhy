// 07-11: the stranger arrives, the crowd turns, the offer to the council, he raises the flute
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
const { barT: b, clamp, lerp, ease, tween, BEAT, BAR, S16, HIT, W, H, TAU, hash, EV } = C;
const { PAL } = K;

const GAP0 = C.BM.gaps[0];   // 12.132: the silence before the first drop
const PB = CAST.piper.B;
const piperWalk = (o = {}) => ST.walker(PB, { stride: 104, bob: 2.4, arm: .16, lean: .02, sway: 1.5, ...o });

// ---------------------------------------------------------------- 07: the gate
function shot07(g, t, lt) {
  const t0 = b(6);
  const open = ease.io(clamp((t - b(6, 6)) / (GAP0 - b(6, 6) - .1)));
  const push = 1 + .08 * ease.io(clamp(lt / 1.77));
  g.save(); g.translate(W / 2, H * .55); g.scale(push, push); g.translate(-W / 2, -H * .55);
  E.sky(g, 'day', W, 1200, t);
  E.cloud(g, 180, 330, 1.2, 1); E.cloud(g, 860, 250, .9, 1);
  const gy = 1500;
  // beyond the arch: bright haze and a road
  const beyond = (g2) => {
    const gr = g2.createLinearGradient(0, gy - 480, 0, gy); gr.addColorStop(0, '#fff4d8'); gr.addColorStop(1, '#f0d7a6'); g2.fillStyle = gr; g2.fillRect(0, gy - 600, W, 700);
    // the Piper's silhouette appearing in the gateway (backlit), stepping through in the silence
    const appear = ease.o(clamp((t - b(6, 8)) / .5));
    const step = ease.io(clamp((t - GAP0) / .22));
    const P = R.merge(R.idle(t * .3, { B: PB, shift: .1 }), { yaw: 0, head: { pitch: .05 } });
    if (step > 0) Object.assign(P, R.merge(P, R.walk(step * .5, { B: PB, stride: 110, bob: 2, arm: .12 })));
    g2.save(); g2.globalAlpha = appear;
    PS.drawPerson(g2, CAST.piper, P, { x: W / 2, y: gy - 6 + step * 8, s: .62 + step * .05, sil: '#2a1a22', lw: 3, t, wind: .6 + step, shadow: false });
    g2.restore();
    E.addLight(g2, W / 2, gy - 260, 520, '#ffe2a8', .5 + .3 * open);
  };
  E.gate(g, W / 2, gy, { open, mood: 'day', inner: beyond, lw: 5 });
  // road + cobbles in front of the gate
  const V = new Wd.View({ cx: 0, cy: 240, cz: 0, f: 1000, hy: gy - 240 * 1000 / 2400 });
  g.save(); g.beginPath(); g.rect(0, gy, W, 600); g.clip(); Wd.ground(g, V, { mood: 'day', zFar: 2400 }); g.restore();
  // townsfolk seen from behind framing the gate (they've noticed something)
  const backs = [[150, 1910, 1.5, 7], [960, 1950, 1.6, 11], [330, 1840, 1.05, 13]];
  for (const [x, y, s, sd] of backs) {
    const ch = CAST.townsfolk(sd);
    const tt = t; const P = R.merge(R.idle(tt, { seed: sd }), { yaw: Math.PI + (x < W / 2 ? .25 : -.25), head: { yaw: x < W / 2 ? -.3 : .3 } });
    PS.drawPerson(g, ch, P, { x, y, s, lw: 5, t });
  }
  // fog spilling through the gate
  E.fog(g, gy - 380, 420, t, { col: '#f3ead6', a: .45 * (.4 + .6 * open), speed: 30 });
  g.restore();
}

// ---------------------------------------------------------------- 08: DROP -- he strides through the market, heads turn in a wave
function shot08(g, t, lt) {
  const t0 = b(7);
  const v = 104 / (2 * BEAT);
  const px = -360 + (t - t0) * v, pz = 1020;
  const punch = 1 + .035 * C.decay(t - t0 - HIT, 5);
  const V = new Wd.View({ cx: px + 150, cy: 300, cz: 0, f: 1250 * punch, hy: 1000 });
  ST.streetBackdrop(g, V, t, 'day', { sunX: 880, clouds: [[260, 280, 1.1]] });
  const items = [];
  // far side: houses + stalls
  for (let i = -4; i < 6; i++) items.push(Wd.houseItem(i * 600 + 80, 3000, 230, 360 + hash(i + 9) * 100, { seed: 300 + i, mood: 'day' }));
  for (let i = -3; i < 5; i++) items.push(Wd.propItem(i * 640 + 200, 2050, (g2, s) => E.stall(g2, -240, 0, 480, { lw: 4.5 / s, seed: 40 + i, stripe: i % 2 ? ['#b0402b', '#e8dcbf'] : ['#53719a', '#e8dcbf'] })));
  // townsfolk: each turns toward him as he approaches, quantised to the beat -> a wave on the beats
  const folks = ST.crowd(16, 71, { x0: -1400, x1: 1600, z0: 850, z1: 1900 });
  for (const f of folks) {
    if (Math.abs(f.z - pz) < 140) f.z += 300;
    const passT = t0 + (f.x - 200 - (-360)) / v;                     // when he is ~200 units before them
    const turnT = Math.round((passT - t0) / BEAT) * BEAT + t0;
    items.push({ z: f.z, draw: (g2, V2) => ST.actor(g2, V2, f.ch, f.x, f.z, tt => {
      const u = ease.back(clamp((tt - turnT - HIT) / .14));
      const toward = f.x > px ? -1 : 1;
      return R.merge(R.idle(tt, { seed: f.seed }), { yaw: lerp(f.r < .5 ? .6 : -.6, toward * 1.1, u * .7), head: { yaw: toward * .5 * u, pitch: -.05 * u },
        face: u > .5 ? { eyes: 'wide', mouth: f.r < .5 ? 'o' : 'closed', brow: 'raised', look: [toward * .8, 0] } : { eyes: 'open', mouth: 'flat' },
        arms: u > .5 && f.r > .7 ? { l: { swing: 1.4, out: .3, elbow: .1 } } : undefined, hands: u > .5 && f.r > .7 ? { l: 'point' } : undefined });
    }, t) });
  }
  // a few rats still scurrying around his feet
  for (let i = 0; i < 9; i++) { const rx = px + 400 - ((t - t0) * (300 + i * 30) + i * 170) % 1100, rz = 1000 + hash(i) * 600; items.push({ z: rz, draw: (g2, V2) => ST.ratAt(g2, V2, rx, rz, { dir: -1, phase: (t - t0) * 4 + i, t }) }); }
  // the Piper: long elegant strides, heel strikes on the beats, cloak streaming
  items.push({ z: pz, draw: (g2, V2) => ST.actor(g2, V2, CAST.piper, px, pz, piperWalk({ yaw: Math.PI / 2 - .25, head: { yaw: -.55, pitch: .05 }, face: { eyes: 'narrow', mouth: 'sly', brow: 'sly', look: [-.3, 0] }, t0 }), t, { wind: .3 }) });
  // foreground: out-of-focus posts and barrels sliding past (strong parallax)
  Wd.drawItems(g, V, items);
  PO.blurred(g, 10, (g2) => {
    for (let i = -2; i < 6; i++) { const [sx, sy, s] = V.p(i * 520 + 60, 0, 520); g2.save(); g2.translate(sx, sy); g2.scale(s, s); E.barrel(g2, 0, 0, 1.6, { lw: 4 / s }); E.sack(g2, 160, 0, 1.6, { lw: 4 / s }); g2.restore(); }
  });
}

// ---------------------------------------------------------------- 09: heads snap on the stabs; he tips his hat on the giggle
function shot09(g, t, lt) {
  const t0 = b(8);
  const stab1 = t0, stab2 = b(8, 3);
  const V = new Wd.View({ cx: lerp(40, 0, ease.io(lt / 1.77)), cy: 290, cz: 0, f: 1250, hy: 1020 });
  ST.streetBackdrop(g, V, t, 'day', { sunX: 150 });
  const items = Wd.streetItems({ mood: 'day', seed: 44, half: 1100, z0: 1700 });
  // crowd on the right, in two groups (one per stab)
  const crowdA = [[200, 1000, 3], [400, 1180, 8], [610, 1060, 14], [800, 1250, 19], [300, 1450, 22], [700, 1500, 27], [520, 1330, 31], [900, 1000, 36]];
  crowdA.forEach(([x, z, sd], i) => {
    const ch = CAST.townsfolk(sd);
    const st = i % 2 === 0 ? stab1 : stab2;
    items.push({ z, draw: (g2, V2) => ST.actor(g2, V2, ch, x, z, tt => {
      const u = ease.back(clamp((tt - st - HIT) / .1));
      return R.merge(R.idle(tt, { seed: sd }), { yaw: lerp(.5, -.75, u), head: { yaw: -.45 * u, pitch: lerp(.2, -.05, u) },
        face: { eyes: u > .5 ? 'wide' : 'open', mouth: u > .5 ? 'o' : 'flat', brow: 'raised', look: [-.9 * u, 0] } });
    }, t) });
  });
  // the Piper on the left: stands still, then bows and tips his hat on the giggle notes
  const gig = C.FL.filter(n => n.t >= t0 && n.t < b(9)).map(n => n.t);
  items.push({ z: 950, draw: (g2, V2) => ST.actor(g2, V2, CAST.piper, -260, 950, tt => {
    const bow = gig.length ? Math.max(0, ...gig.map(gt => Math.exp(-Math.max(0, tt - gt) * 3) * (tt >= gt ? 1 : 0))) : 0;
    const up = ease.io(clamp((tt - gig[0] + .25) / .25));
    return R.merge(R.idle(tt * .4, { B: PB, shift: .1 }), { yaw: .75, lean: .22 * bow * up, head: { yaw: .1, pitch: .2 * bow * up },
      arms: { l: { swing: lerp(.1, 2.75, up), out: lerp(.1, .55, up), elbow: lerp(.2, 1.5, up) }, r: { swing: -.1, out: .2, elbow: .4 } },
      hands: { l: up > .5 ? 'open' : 'mitten' }, face: { eyes: 'narrow', mouth: 'sly', brow: 'sly', look: [.7, 0] } });
  }, t, { wind: .25 }) });
  Wd.drawItems(g, V, items);
}

// ---------------------------------------------------------------- 10: the council chamber (callback to the studio's council scene)
function councilRoom(g, t, o = {}) {
  // panelled walls, leaded arched window, red banner with Hamelin's millwheel, candles
  g.fillStyle = '#e3d2ae'; g.fillRect(0, 0, W, H);
  g.fillStyle = 'rgba(80,50,25,.12)'; for (let i = 0; i < 8; i++) g.fillRect(0, i * 240 + 120, W, 4);
  K.shape(g, [[0, 1080], [W, 1080], [W, 1200], [0, 1200]], { fill: '#6b4428', lw: 5, smooth: false });
  for (let i = 0; i < 6; i++) K.shape(g, [[20 + i * 180, 1110], [180 + i * 180, 1110], [180 + i * 180, 1180], [20 + i * 180, 1180]], { fill: '#7b5233', lw: 3.5, smooth: false });
  // window
  const wx = 110, wy = 230, ww = 300, wh = 560;
  const P = [[wx, wy + wh], [wx, wy + ww / 2]]; for (let i = 0; i <= 10; i++) { const a = Math.PI + Math.PI * i / 10; P.push([wx + ww / 2 + Math.cos(a) * ww / 2, wy + ww / 2 + Math.sin(a) * ww / 2]); } P.push([wx + ww, wy + wh]);
  K.shape(g, P, { fill: o.night ? '#33406a' : '#fbf1d6', lw: 6, smooth: false, inner: g2 => { g2.strokeStyle = 'rgba(70,60,50,.55)'; g2.lineWidth = 3; for (let i = -600; i < 600; i += 46) { g2.beginPath(); g2.moveTo(wx + i, wy); g2.lineTo(wx + i + 700, wy + 700); g2.stroke(); g2.beginPath(); g2.moveTo(wx + i + 700, wy); g2.lineTo(wx + i, wy + 700); g2.stroke(); } } });
  K.line(g, [[wx + ww / 2, wy], [wx + ww / 2, wy + wh]], 8, PAL.ink, 1, false);
  K.shape(g, [[wx - 20, wy + wh], [wx + ww + 20, wy + wh], [wx + ww + 20, wy + wh + 22], [wx - 20, wy + wh + 22]], { fill: '#b9a98a', lw: 5, smooth: false });
  if (!o.night) E.addLight(g, wx + ww / 2, wy + wh / 2, 520, '#fff0c8', .35);
  // banner
  const bx = 560, by = 150;
  K.line(g, [[bx - 30, by], [bx + 330, by]], 10, '#3a2418', 1, false);
  K.shape(g, [[bx, by], [bx + 300, by], [bx + 300, by + 520], [bx + 150, by + 600], [bx, by + 520]], { fill: '#9a2a25', lw: 6, smooth: false, inner: g2 => { g2.strokeStyle = '#d6a845'; g2.lineWidth = 5; g2.strokeRect(bx + 14, by + 14, 272, 480); } });
  K.shape(g, [[bx + 60, by + 120], [bx + 240, by + 120], [bx + 240, by + 300], [bx + 150, by + 400], [bx + 60, by + 300]], { fill: '#efe6d2', lw: 5, tension: .3 });
  g.save(); g.translate(bx + 150, by + 245); for (let i = 0; i < 8; i++) { g.rotate(Math.PI / 4); K.line(g, [[0, 0], [0, 60]], 8, '#9a2a25', 1, false); } K.ellipse(g, 0, 0, 62, 62, { fill: null, lw: 0 }); g.strokeStyle = '#9a2a25'; g.lineWidth = 10; g.beginPath(); g.arc(0, 0, 58, 0, TAU); g.stroke(); g.restore();
  // candle sconce
  K.shape(g, [[960, 620], [990, 620], [990, 760], [960, 760]], { fill: '#2a2420', lw: 4, smooth: false });
  K.shape(g, [[965, 520], [985, 520], [985, 620], [965, 620]], { fill: '#efe6d2', lw: 3.5, smooth: false });
  K.shape(g, [[975, 470 + Math.sin(t * 11) * 4], [985, 505], [975, 520], [965, 505]], { fill: '#f6c24a', lw: 2.5 });
  E.addLight(g, 975, 500, 260, '#f3a64a', .45);
}
function shot10(g, t, lt) {
  const t0 = b(9);
  const push = 1 + .04 * ease.io(lt / 1.77);
  g.save(); g.translate(W / 2, H * .6); g.scale(push, push); g.translate(-W / 2, -H * .6);
  councilRoom(g, t);
  // council behind the green table: mayor (centre), councillor, clerk -- nodding on the beats
  const seat = [[300, CAST.councillor, .25, 41], [560, CAST.mayor, 0, 42], [820, CAST.clerk, -.25, 43]];
  for (const [x, ch, yaw, sd] of seat) {
    const pose = tt => {
      const n = C.beatIndex(tt), ph = C.beatPhase(tt);
      const nod = ch === CAST.mayor ? Math.sin(Math.PI * ph) * .12 * (n % 2 ? 1 : .6) : 0;
      const point = ch === CAST.councillor ? ease.o(clamp((tt - b(9, 8)) / .2)) : 0;
      return R.merge(R.idle(tt, { seed: sd }), { yaw, head: { pitch: nod + .05, yaw: -yaw * .5 },
        arms: point > 0 ? { r: { swing: lerp(.3, 1.45, point), out: lerp(.15, -.25, point), elbow: .15 } } : { l: { swing: .9, out: .2, elbow: .8 }, r: { swing: .9, out: .2, elbow: .8 } },
        hands: point > 0 ? { r: 'point' } : {}, face: ch === CAST.mayor ? { eyes: 'narrow', mouth: 'flat', brow: 'raised', look: [-.2, .3] } : { eyes: 'open', mouth: ch === CAST.clerk ? 'closed' : 'o', brow: 'raised', look: [-.3, .3] } });
    };
    PS.drawPerson(g, ch, pose(t), { x, y: 1500, s: 1.35, lw: 5, lagA: pose(t - .07), lagB: pose(t - .16), t });
  }
  // the green table with candles, papers, quill and the chest of gold
  K.shape(g, [[60, 1260], [W - 60, 1260], [W - 30, 1560], [30, 1560]], { fill: '#2f5a3c', lw: 6, smooth: false, inner: g2 => { g2.fillStyle = 'rgba(0,0,0,.15)'; g2.fillRect(0, 1400, W, 200); } });
  for (let i = 0; i < 9; i++) K.line(g, [[80 + i * 115, 1560], [80 + i * 115, 1578]], 4, '#c9a03c', 1, false);
  E.chest(g, 760, 1270, .9, { lid: .85, lw: 5 });
  K.shape(g, [[240, 1270], [430, 1262], [440, 1290], [250, 1300]], { fill: '#f1e9d6', lw: 4, smooth: false });
  for (const cx of [140, 980]) { K.shape(g, [[cx - 12, 1268], [cx + 12, 1268], [cx + 12, 1150], [cx - 12, 1150]], { fill: '#efe6d2', lw: 4, smooth: false }); K.shape(g, [[cx, 1100 + Math.sin(t * 9 + cx) * 4], [cx + 9, 1135], [cx, 1150], [cx - 9, 1135]], { fill: '#f6c24a', lw: 2.5 }); E.addLight(g, cx, 1130, 240, '#f3a64a', .5); }
  // a rat scurries across the table on the second half of the bar
  if (t > b(9, 6)) { const dt = t - b(9, 6); RT.ratSide(g, 60 + dt * 620, 1268, { s: 1.0, dir: 1, phase: dt * 5, t, shadow: false }); }
  // the Piper (back three-quarter, foreground left): gestures at the rat, then lifts the flute
  const pose = tt => {
    const g1 = ease.o(clamp((tt - b(9, 2)) / .25)) * (1 - ease.io(clamp((tt - b(9, 10)) / .3)));
    const lift = ease.io(clamp((tt - b(9, 12)) / .4));
    return R.merge(R.idle(tt * .4, { B: PB, shift: .15 }), { yaw: Math.PI - .55, head: { yaw: -.35, pitch: .05 },
      arms: { r: { swing: lerp(.1, 1.5, g1), out: lerp(.1, .5, g1), elbow: .2 }, l: { swing: lerp(.1, 1.7, lift), out: .2, elbow: lerp(.3, 1.8, lift) } },
      hands: { r: g1 > .3 ? 'open' : 'mitten' } });
  };
  PS.drawPerson(g, CAST.piper, pose(t), { x: 190, y: 2050, s: 2.2, lw: 7, lagA: pose(t - .07), lagB: pose(t - .16), t, wind: .15 });
  g.restore();
}

// ---------------------------------------------------------------- 11: he raises the flute -- fingers follow the real cadence notes
function shot11(g, t, lt) {
  const t0 = b(10);
  // blurred square behind him (the council at the town hall steps)
  PO.blurred(g, 9, (g2) => { councilRoom(g2, t); });
  const raise = ease.io(clamp((t - t0 + .1) / .32));
  const pose = tt => {
    const P = PP.playPose(tt, { eyes: tt > t0 + .3 ? 'narrow' : 'open', glow: .15 });
    const r = ease.io(clamp((tt - t0 + .1) / .32));
    if (r < 1) { P.arms.l.hand = R.v(16, 20 + 120 * r, 30 + 10 * r); P.arms.r.hand = R.v(-10, -10 + 85 * r, 40 + 10 * r); }
    return R.merge(P, { yaw: .35, head: { yaw: -.15 } });
  };
  const push = 1 + .07 * ease.io(lt / 1.77);
  g.save(); g.translate(W / 2, H * .45); g.scale(push, push); g.translate(-W / 2, -H * .45);
  PS.drawPerson(g, CAST.piper, pose(t), { x: 520, y: 2150 + 0, s: 3.3, lw: 7.5, lagA: pose(t - .07), lagB: pose(t - .16), t, wind: .2 });
  g.restore();
}

module.exports = [
  { id: '07_gate', t0: b(6), mood: 'warm', draw: shot07 },
  { id: '08_market_stride', t0: b(7), mood: 'day', draw: shot08, flashIn: true },
  { id: '09_heads_snap', t0: b(8), mood: 'day', draw: shot09 },
  { id: '10_council', t0: b(9), mood: 'warm', draw: shot10 },
  { id: '11_raise_flute', t0: b(10), mood: 'warm', draw: shot11 },
];
module.exports.helpers = { councilRoom, piperWalk };
