// 06-11 THE RAT INVASION (bars 3-6): day, sepia, Hamelin 1284. Dense DP compositions, cuts on the half bar.
'use strict';
const C = require('../core');
const R = require('../rig');
const PS = require('../person');
const CAST = require('../cast');
const E = require('../env');
const Wd = require('../world');
const ST = require('../stage');
const RT = require('../rats');
const CR = require('../creatures');
const TD = require('../topdown');
const K = require('../ink');
const PO = require('../post');
const DP = require('../dp');
const CH = require('../chor');
const { barT: b, clamp, lerp, ease, BEAT, S16, HIT, W, H, TAU, hash } = C;
const { PAL } = K;
const CLOUDS = [[200, 300, 1.2], [640, 200, .9]];

// a frightened villager: idle until `at`, then a beat-locked startle (jump, arms up, wide eyes), then panic-shake
function startle(ch, at, o = {}) {
  return tt => {
    const u = clamp((tt - at - HIT) / .3);
    const jump = u > 0 && u < 1 ? Math.sin(Math.PI * u) : 0;
    const after = clamp((tt - at) / .2);
    let P = R.idle(tt, { seed: o.seed || 1 });
    if (tt > at) P = R.merge(P, { bob: jump * 46 - 10 * Math.exp(-(tt - at - .3) * 8) * (u >= 1 ? 1 : 0),
      legs: jump > .1 ? { l: [26, 30 * jump, 10], r: [-26, 50 * jump, -6] } : undefined,
      arms: { l: { swing: 2.4 + .1 * Math.sin(tt * 40), out: 1.0, elbow: .3 }, r: { swing: 2.3 - .1 * Math.sin(tt * 40), out: 1.1, elbow: .4 } }, hands: { l: 'open', r: 'open' },
      lean: -.15, head: { pitch: -.1, roll: .08 * Math.sin(tt * 30) * after },
      face: { eyes: 'wide', mouth: 'gasp', brow: 'worry', sweat: 1, look: o.look || [0, .6] } });
    else P = R.merge(P, { face: { eyes: 'open', mouth: o.mouth || 'smile', look: o.lookBefore || [.3, 0] } });
    if (o.yaw != null) P.yaw = o.yaw;
    return P;
  };
}

// ---------------------------------------------------------------- 06: the square floods -- villagers leap on the claps
function shot06(g, t, lt) {
  const t0 = b(2);
  const u = ease.io(clamp(lt / 1.77));
  const { V, items } = DP.town(g, t, { mood: 'day', cam: { cz: lerp(0, 80, u), cx: lerp(-30, 30, u) }, clouds: CLOUDS, sunX: 860, seed: 12, well: [-650, 1700],
    props: [['stall', 620, 1900, 1], ['barrel', -420, 1250], ['sack', -330, 1200], ['crate', 820, 1300]] });
  // villagers: big, foreground + midground, each startles on a clap (s4 / s12) or a riq offbeat
  const folks = [[CAST.woman, -330, 760, b(2, 4), .25, 1], [CAST.baker, 300, 820, b(2, 12), -.35, 2], [CAST.townsfolk(11), -60, 1250, b(2, 6), .1, 3],
    [CAST.townsfolk(14), 560, 1350, b(2, 10), -.4, 4], [CAST.townsfolk(17), -620, 1420, b(2, 14), .5, 5], [CAST.farmer, 150, 1600, b(2, 2), 0, 6]];
  for (const [ch, x, z, at, yaw, sd] of folks) DP.actorAt(items, ch, x, z, startle(ch, at, { yaw, seed: sd, look: [x > 0 ? -.4 : .4, .7] }), t);
  // the flood: rats pour from under the stall and the drain toward camera in waves on the 8ths
  for (let i = 0; i < 150; i++) {
    const te = t0 - .9 + (i % 50) * S16 * .35 + Math.floor(i / 50) * .45 + hash(i) * .1;
    if (t < te) continue;
    const src = i % 3 === 0 ? [620, 1900] : i % 3 === 1 ? [-200, 2300] : [-650, 1700];
    const ang = (hash(i * 7.3) - .5) * 1.6;
    const sp = 620 + hash(i * 1.9) * 360, d = (t - te) * sp;
    const x = src[0] + Math.sin(ang) * d, z = src[1] - Math.cos(ang) * d;
    if (z < 330) continue;
    items.push({ z, draw: (g2, V2) => ST.ratAt(g2, V2, x, z, { dir: Math.sin(ang) >= 0 ? 1 : -1, phase: d / 110, speed: 1, t, size: 1.15 }) });
  }
  DP.flush(g, V, items);
}

// ---------------------------------------------------------------- 07: the rooftops -- rats gallop the ridges, leaping gaps on the beats
function shot07(g, t, lt) {
  const t0 = b(3);
  g.save(); g.translate(0, lerp(-30, 30, ease.io(clamp(lt / .88))));
  E.sky(g, 'day', W, 1200, t); E.sun(g, 860, 240, 64, t); E.cloud(g, 240, 300, 1.1, 1);
  E.skyline(g, -100, 900, 1300, 'day', 9);
  g.fillStyle = '#5a4030'; g.fillRect(0, 1690, W, 400);
  const roofs = [];
  g.save(); g.translate(0, 1700); g.scale(1.45, 1.45);
  let x = -150, i = 0;
  while (x < W / 1.45 + 100) { const w = 170 + hash(i * 5) * 60, h = 330 + hash(i * 3) * 140; roofs.push(E.house(g, x, 0, w, h, { seed: 70 + i, mood: 'day' })); x += w + 30; i++; }
  g.restore();
  for (let k = 0; k < 16; k++) {
    const xx = ((k * 120 + (t - t0) * 420) % (W + 400)) - 200;
    let yy = 900, tilt = 0, best = null;
    for (const r of roofs) { const a = r.rx0 * 1.45, c = r.rx1 * 1.45, pk = 1700 + r.peak * 1.45, base = 1700 + r.topY * 1.45, mid = (a + c) / 2; if (xx >= a && xx <= c) { best = 1; yy = xx < mid ? lerp(base, pk, (xx - a) / (mid - a)) : lerp(pk, base, (xx - mid) / (c - mid)); tilt = xx < mid ? -.75 : .75; } }
    if (!best) { yy = 1700 - 520 - Math.sin(((xx + 200) % 60) / 60 * Math.PI) * 60; tilt = 0; }    // leaping the gap
    RT.ratSide(g, xx, yy + 6, { s: 1.15, dir: 1, phase: (t - t0) * 4.5 + k * .13, speed: 1, t, tilt: tilt * .9, shadow: false });
  }
  g.restore();
}

// ---------------------------------------------------------------- 08: grain sacks burst; the merchant recoils
function shot08(g, t, lt) {
  const t0 = b(3, 8);
  PO.blurred(g, 7, (g2) => {
    E.sky(g2, 'day', W, 900, t); E.sun(g2, 220, 200, 60, t);
    g2.save(); g2.translate(0, 1150); g2.scale(1.15, 1.15); let x = -60, i = 0; while (x < 1100) { const w = 200 + hash(i) * 60; E.house(g2, x, 0, w, 380 + hash(i + 4) * 100, { seed: 90 + i, mood: 'day' }); x += w + 20; i++; } g2.restore();
    g2.fillStyle = '#b39b78'; g2.fillRect(0, 1150, W, 800);
  });
  const V = new Wd.View({ cx: 0, cy: 230, cz: 0, f: 1100, hy: 1100 });
  Wd.ground(g, V, { mood: 'day', zNear: 300 });
  E.stall(g, 520, 1500, 620, { lw: 6, seed: 11 });
  const splits = [t0, b(3, 10), b(3, 13)];
  const sacks = [[250, 1640, 2.0, splits[0]], [470, 1690, 1.8, splits[1]], [90, 1720, 1.7, splits[2]]];
  // merchant: anticipation, then a big recoil on the first burst, arms up, then shaking
  const mp = startle(CAST.merchant, t0 - .02, { yaw: -.6, seed: 3, look: [-.6, .5] });
  PS.drawPerson(g, CAST.merchant, mp(t), { x: 820, y: 1780, s: 2.25, lw: 6.5, lagA: mp(t - .07), lagB: mp(t - .16), t });
  for (const [sx, sy, s, ts] of sacks) {
    E.sack(g, sx, sy, s, { torn: clamp((t - ts - HIT) / .12), lw: 6 });
    if (t > ts) for (let j = 0; j < 9; j++) {
      const dt = t - ts - j * .05; if (dt < 0) continue;
      const side = j % 2 ? 1 : -.6;
      const rx = sx + side * dt * (430 + j * 30), ry = sy - Math.max(0, Math.sin(Math.min(1, dt * 3) * Math.PI) * 90 * (1 - dt));
      RT.ratSide(g, rx, Math.min(sy + 40, ry + 30 + dt * 60), { s: 1.35, dir: side > 0 ? 1 : -1, phase: dt * 5 + j * .3, t, speed: 1 });
    }
    // grain spray
    if (t > ts) for (let j = 0; j < 22; j++) { const dt = t - ts; const a = -Math.PI / 2 + (hash(j + sx) - .5) * 2.2, v = 500 + hash(j * 3 + sx) * 500; const gx = sx + Math.cos(a) * v * dt, gy = sy - 60 + Math.sin(a) * v * dt + 1800 * dt * dt; if (gy < sy + 60) K.ellipse(g, gx, gy, 6, 4, { fill: '#e2c27a', lw: 2 }, a); }
  }
}

// ---------------------------------------------------------------- 09: the kitchen -- rats across the table; the family leaps
function kitchen(g, t) {
  g.fillStyle = '#d9c4a0'; g.fillRect(0, 0, W, 1400);
  for (const x of [80, 540, 1000]) K.shape(g, [[x - 16, 0], [x + 16, 0], [x + 16, 1400], [x - 16, 1400]], { fill: PAL.beam, lw: 5, smooth: false });
  K.shape(g, [[0, 260], [W, 260], [W, 292], [0, 292]], { fill: PAL.beam, lw: 5, smooth: false });
  // hearth with fire (right)
  K.shape(g, [[660, 1400], [660, 820], [700, 760], [1040, 760], [1080, 820], [1080, 1400]], { fill: '#9a8a74', lw: 6, smooth: false });
  K.shape(g, [[720, 1400], [720, 960], [760, 900], [980, 900], [1020, 960], [1020, 1400]], { fill: '#1e140e', lw: 6, smooth: false });
  for (let i = 0; i < 5; i++) { const fx = 790 + i * 45, fh = 90 + 40 * Math.sin(t * 9 + i * 1.7); K.shape(g, [[fx - 26, 1380], [fx, 1380 - fh], [fx + 26, 1380]], { fill: i % 2 ? '#f6c24a' : '#e8823a', lw: 3, tension: .4 }); }
  E.addLight(g, 870, 1280, 700, '#f39a4a', .7);
  // shelf with pots
  K.shape(g, [[120, 560], [500, 560], [500, 586], [120, 586]], { fill: '#6b4428', lw: 5, smooth: false });
  for (let i = 0; i < 4; i++) K.shape(g, [[150 + i * 90, 560], [150 + i * 90 + 60, 560], [150 + i * 90 + 70, 490], [150 + i * 90 - 10, 490]], { fill: ['#a85a3a', '#c9a060', '#8a5a3c', '#5d6a4a'][i], lw: 4, tension: .3 });
  // window
  K.shape(g, [[170, 700], [430, 700], [430, 980], [170, 980]], { fill: '#f6ecd0', lw: 6, smooth: false });
  K.line(g, [[300, 700], [300, 980]], 7, PAL.beam, 1, false); K.line(g, [[170, 840], [430, 840]], 7, PAL.beam, 1, false);
  E.addLight(g, 300, 840, 500, '#fff0c8', .35);
  K.shape(g, [[-20, 1400], [W + 20, 1400], [W + 20, H + 20], [-20, H + 20]], { fill: '#8a6342', lw: 5, smooth: false, inner: g2 => { g2.strokeStyle = 'rgba(40,20,10,.4)'; g2.lineWidth = 3; for (let y = 1400; y < H; y += 80) { g2.beginPath(); g2.moveTo(0, y); g2.lineTo(W, y); g2.stroke(); } } });
}
function shot09(g, t, lt) {
  const t0 = b(4);
  const push = 1 + .05 * ease.io(lt / 1.77);
  g.save(); g.translate(W / 2, H * .6); g.scale(push, push); g.translate(-W / 2, -H * .6);
  kitchen(g, t);
  // father (left) grabs a stool and raises it on the clap at s12; mother (right) jumps onto the bench on s4
  const fp = tt => {
    const u = ease.o3(clamp((tt - b(4, 12) - HIT + .15) / .25));
    return R.merge(R.idle(tt, { seed: 21 }), { yaw: .5, lean: -.1 * u, arms: { l: { swing: lerp(.6, 2.7, u), out: .4, elbow: .4 }, r: { swing: lerp(.6, 2.6, u), out: .5, elbow: .5 } }, hands: { l: 'fist', r: 'fist' },
      head: { pitch: .15, yaw: .2 }, face: { eyes: 'wide', mouth: u > .2 ? 'gasp' : 'frown', brow: 'angry', look: [.6, .7] } });
  };
  const J = PS.drawPerson(g, CAST.father, fp(t), { x: 190, y: 1790, s: 1.95, lw: 6, lagA: fp(t - .07), lagB: fp(t - .16), t });
  // the stool in his hands
  const hl = R.proj(J, J.wrl), hr = R.proj(J, J.wrr);
  const sx = 190 + (hl[0] + hr[0]) / 2 * 1.95, sy = 1790 + (hl[1] + hr[1]) / 2 * 1.95;
  K.shape(g, [[sx - 70, sy - 20], [sx + 70, sy - 20], [sx + 70, sy - 44], [sx - 70, sy - 44]], { fill: '#7a5233', lw: 5, smooth: false });
  for (const lx of [-60, 50]) K.line(g, [[sx + lx, sy - 44], [sx + lx - 8, sy - 130]], 10, '#6b4428', 1, false);
  // the table + loaves + a running line of rats
  K.shape(g, [[260, 1430], [900, 1430], [900, 1470], [260, 1470]], { fill: '#8a5a36', lw: 6, smooth: false });
  for (const lx of [290, 850]) K.shape(g, [[lx, 1470], [lx + 26, 1470], [lx + 26, 1700], [lx, 1700]], { fill: '#6b4428', lw: 5, smooth: false });
  E.bread(g, 420, 1410, 1.1, { lw: 5 }); E.bread(g, 700, 1414, .9, { lw: 5 });
  K.ellipse(g, 560, 1418, 60, 16, { fill: '#c9b27a', lw: 4 });
  for (let k = 0; k < 9; k++) { const dt = t - t0 - k * .11; if (dt < 0) continue; const xx = 200 + dt * 520 + (k % 2) * 30; if (xx > 980) continue; RT.ratSide(g, xx, 1424 - Math.abs(Math.sin(dt * 10)) * 6, { s: .95, dir: 1, phase: dt * 5, t, speed: 1, shadow: false }); }
  for (let k = 0; k < 5; k++) { const dt = t - b(4, 6) - k * .1; if (dt < 0) continue; const xx = 980 - dt * 600; if (xx < 150) continue; RT.ratSide(g, xx, 1690, { s: 1.0, dir: -1, phase: dt * 5, t, speed: 1 }); }
  // mother leaps onto the bench (s4), skirt held up, shrieking silently
  const mp = tt => {
    const jt = b(4, 4) + HIT; const u = clamp((tt - jt) / .25);
    const y = tt < jt ? 0 : u < 1 ? Math.sin(Math.PI * u) * 60 + 110 * u : 110;
    let P = startle(CAST.woman, jt - .01, { yaw: -.5, seed: 8, look: [-.5, .8] })(tt);
    P = R.merge(P, { bob: (P.bob || 0) + y });
    if (tt > jt + .25) P = R.merge(P, { legs: { l: [26, 8 + 4 * Math.sin(tt * 30), 0], r: [-26, 8 + 4 * Math.sin(tt * 30 + 2), 0] }, arms: { l: { swing: .4, out: .6, elbow: 1.5 }, r: { swing: 2.6, out: .6, elbow: .4 } } });
    return P;
  };
  K.shape(g, [[700, 1640], [1040, 1640], [1040, 1600], [700, 1600]], { fill: '#7a5233', lw: 5, smooth: false });
  PS.drawPerson(g, CAST.woman, mp(t), { x: 870, y: 1820, s: 1.85, lw: 6, lagA: mp(t - .07), lagB: mp(t - .16), t });
  // a child hiding under the table, the cat arching away
  const cp = tt => R.merge(R.idle(tt, { B: R.BODY.child, seed: 4 }), { bob: -50, knees: { l: 1, r: 1 }, lean: .3, arms: { l: { swing: 2.2, out: .2, elbow: 2.0 }, r: { swing: 2.2, out: .2, elbow: 2.0 } }, hands: { l: 'open', r: 'open' }, face: { eyes: 'wide', mouth: 'o', brow: 'worry', look: [.3, .2] } });
  PS.drawPerson(g, CAST.boy1, cp(t), { x: 560, y: 1700, s: 1.5, lw: 6, t });
  CR.cat(g, 520 - Math.max(0, t - t0 - .4) * 180, 1830, { s: 1.6, dir: 1, arch: ease.o3(clamp((t - t0 - .3) / .3)), phase: (t - t0) * 1.6, t, lw: 6 });
  g.restore();
}

// ---------------------------------------------------------------- 10: the barrel bursts (s0 / s3 / s6)
function shot10(g, t, lt) {
  const t0 = b(5);
  PO.blurred(g, 7, (g2) => {
    E.sky(g2, 'day', W, 900, t); E.sun(g2, 200, 200, 60, t);
    g2.save(); g2.translate(0, 1180); g2.scale(1.1, 1.1); let x = -60, i = 0; while (x < 1100) { const w = 200 + hash(i) * 60; E.house(g2, x, 0, w, 380 + hash(i + 4) * 100, { seed: 190 + i, mood: 'day' }); x += w + 20; i++; } g2.restore();
    g2.fillStyle = '#b39b78'; g2.fillRect(0, 1270, W, 700);
  });
  const V = new Wd.View({ cx: 0, cy: 260, cz: 0, f: 1100, hy: 1080 });
  Wd.ground(g, V, { mood: 'day', zNear: 300 });
  const push = 1 + .06 * ease.io(lt / .88);
  g.save(); g.translate(W / 2, H * .62); g.scale(push, push); g.translate(-W / 2, -H * .62);
  const bx = 400, by = 1580, bs = 2.3;
  const lid = clamp((t - t0 - HIT) / .1);
  const bursts = [t0, b(5, 3), b(5, 6)];
  const fly = (front) => {
    bursts.forEach((tb, kk) => { for (let j = 0; j < 7; j++) {
      const dt = t - tb - j * .025 - HIT; if (dt < 0 || dt > 1.2 || (j < 3) !== front) continue;
      const side = (j % 2 ? 1 : -1) * (kk % 2 ? 1 : .7);
      const vx = side * (280 + hash(j * 3 + kk) * 380), vy = -(1000 + hash(j + kk * 7) * 500);
      const y = by - 260 + vy * dt + 2800 * dt * dt, gy = by + 60 + hash(j + 2) * 120;
      const landed = y > gy;
      RT.ratSide(g, bx + vx * dt * (landed ? 1.3 : 1), landed ? gy : y, { s: 1.6, dir: side > 0 ? 1 : -1, phase: dt * 5, t, speed: landed ? 1 : .2, tilt: landed ? 0 : -side * .5, stand: landed ? 0 : .4, shadow: landed });
    } });
  };
  fly(false);
  E.barrel(g, bx, by, bs, { lid, lw: 6 });
  const mp = startle(CAST.merchant, t0, { yaw: -.75, seed: 3, look: [-.6, .2] });
  PS.drawPerson(g, CAST.townsfolk(5), mp(t), { x: 790, y: 1730, s: 2.1, lw: 6, lagA: mp(t - .07), lagB: mp(t - .16), t });
  fly(true);
  g.restore();
}

// ---------------------------------------------------------------- 11: from above -- the streets are a carpet of rats
function shot11(g, t, lt) {
  const t0 = b(5, 8);
  const rot = lerp(.1, -.05, ease.io(clamp(lt / .88)));
  g.save(); g.translate(W / 2, H / 2); g.rotate(rot); g.scale(1.35, 1.35); g.translate(-W / 2, -H / 2);
  TD.cobblesTop(g, -500, -500, W + 500, H + 500);
  TD.roofsTop(g, 40, -800, H + 800, -1, { seed: 5 }); TD.roofsTop(g, W - 40, -800, H + 800, 1, { seed: 9 });
  // the carpet: 240 rats streaming down the street, each with its own speed and wander
  for (let i = 0; i < 240; i++) {
    const lane = 140 + hash(i * 1.3) * (W - 280);
    const sp = 260 + hash(i * 2.9) * 220;
    const y = ((hash(i * 7.1) * (H + 600) + (t - t0) * sp) % (H + 600)) - 300;
    const x = lane + Math.sin(y * .02 + i) * 26;
    RT.ratTop(g, x, y, Math.PI / 2 + Math.cos(y * .02 + i) * .25, { s: .85, phase: (t - t0) * 5 + hash(i), t, speed: 1 });
  }
  // townsfolk fleeing up the street against the flow
  for (let i = 0; i < 5; i++) { const y = 1500 - (t - t0) * 420 - i * 230, x = 300 + i * 120 + Math.sin(i * 3) * 60; TD.personTop(g, x, y, -Math.PI / 2 + Math.sin(t * 6 + i) * .2, { ch: CAST.townsfolk(30 + i), s: 1.25, phase: (t - t0) * 2.2 + i * .3, t, armAmt: .9 }); }
  g.restore();
}

module.exports = [
  { id: '06_square_floods', t0: b(2), mood: 'day', draw: shot06, flashIn: true },
  { id: '07_rooftops', t0: b(3), mood: 'day', draw: shot07 },
  { id: '08_sacks_burst', t0: b(3, 8), mood: 'day', draw: shot08 },
  { id: '09_kitchen', t0: b(4), mood: 'warm', draw: shot09 },
  { id: '10_barrel', t0: b(5), mood: 'day', draw: shot10 },
  { id: '11_carpet_above', t0: b(5, 8), mood: 'day', draw: shot11 },
];
module.exports.helpers = { startle, kitchen };
