// 28-32: the final hypnotic procession -- tracking, overhead, faces, silhouettes, the mountain closes
'use strict';
const C = require('../core');
const R = require('../rig');
const PS = require('../person');
const CAST = require('../cast');
const E = require('../env');
const Wd = require('../world');
const ST = require('../stage');
const PP = require('../piper');
const TD = require('../topdown');
const K = require('../ink');
const PO = require('../post');
const { barT: b, clamp, lerp, ease, BEAT, BAR, S16, HIT, W, H, TAU, hash, EV } = C;
const { PAL } = K;
const GAP3 = C.BM.gaps[3];   // 56.029
const KID = i => CAST.child(200 + i);

// ---------------------------------------------------------------- 28: tracking alongside the procession (strong parallax, synced steps)
function shot28(g, t, lt) {
  const t0 = b(27);
  const v = 62 / (2 * BEAT);
  const head = 400 + (t - t0) * v;                 // x of the Piper (leading, moving right)
  const V = new Wd.View({ cx: head - 380, cy: 280, cz: 0, f: 1200, hy: 1130 });
  ST.streetBackdrop(g, V, t, 'night', { moonX: 820, moonY: 300, moonR: 110 });
  const items = [];
  for (let i = -6; i < 8; i++) items.push(Wd.houseItem(i * 640 + 100, 2400, 250, 340 + hash(i + 40) * 120, { seed: 700 + i, mood: 'night', lit: .55 }));
  for (let i = -6; i < 8; i++) items.push(Wd.propItem(i * 900 + 300, 1700, (g2, s) => E.lamp(g2, 0, 0, 320, { lit: true, t, lw: 4 / s })));
  // the Piper leading, then the children in a line, all in step
  items.push({ z: 1050, draw: (g2, V2) => ST.actor(g2, V2, CAST.piper, head, 1050, tt => {
    const P = PP.playPose(tt, { eyes: 'narrow', glow: .5 });
    const Wk = R.walk(ST.stridePh(tt, t0), { B: CAST.piper.B, stride: 100, bob: 2.4, arm: 0 });
    return R.merge(P, { legs: Wk.legs, toe: Wk.toe, bob: Wk.bob * .6, yaw: Math.PI / 2 - .3 });
  }, t, { wind: .5 }) });
  for (let i = 0; i < 16; i++) {
    const ch = KID(i);
    const x = head - 230 - i * 175, z = 1050 + (i % 2 ? 60 : -40);
    items.push({ z, draw: (g2, V2) => ST.actor(g2, V2, ch, x, z, ST.hypnoWalker(ch.B, { yaw: Math.PI / 2, t0, headYaw: -.25 }), t) });
  }
  Wd.drawItems(g, V, items);
  E.fog(g, 1080, 520, t, { col: '#aab9de', a: .35, speed: 10 });
  // foreground: blurred lantern posts sweeping past (fast parallax)
  PO.blurred(g, 12, (g2) => {
    for (let i = -3; i < 6; i++) { const [sx, sy, s] = V.p(i * 700 + 200, 0, 520); g2.save(); g2.translate(sx, sy); g2.scale(s, s); E.lamp(g2, 0, 120, 900, { lit: true, t, lw: 5 / s }); g2.restore(); }
  });
}

// ---------------------------------------------------------------- 29: overhead -- the procession snakes through the streets
function shot29(g, t, lt) {
  const t0 = b(28);
  const scroll = (t - t0) * 120;
  const rot = lerp(.12, -.06, ease.io(lt / 1.77));
  g.save();
  g.translate(W / 2, H / 2); g.rotate(rot); g.scale(1.55, 1.55); g.translate(-W / 2, -H / 2 + scroll);
  TD.cobblesTop(g, -500, -scroll - 1500, W + 500, -scroll + H + 1500, { base: '#7b7f95', gap: '#3e4256' });
  TD.roofsTop(g, 80, -scroll - 1800, -scroll + H + 1800, -1, { seed: 11 }); TD.roofsTop(g, W - 80, -scroll - 1800, -scroll + H + 1800, 1, { seed: 13 });
  // snake path: each walker at distance d behind the Piper follows the same S-curve
  const leadY = H * .36 - scroll;
  const path = d => [W / 2 + Math.sin((leadY + d) * .008 + 1) * 150, leadY + d];
  const heading = d => { const a = path(d), c = path(d - 4); return Math.atan2(c[1] - a[1], c[0] - a[0]); };
  // long moon shadows first
  const items = [];
  for (let i = 0; i < 22; i++) items.push({ d: 120 + i * 82, ch: KID(i) });
  g.save(); g.globalAlpha = .28; g.fillStyle = '#0c0c18';
  for (const it of [{ d: 0 }, ...items]) { const [x, y] = path(it.d); g.save(); g.translate(x, y); g.rotate(.7); g.beginPath(); g.ellipse(70, 0, 95, 24, 0, 0, TAU); g.fill(); g.restore(); }
  g.restore();
  for (const it of items) { const [x, y] = path(it.d); TD.personTop(g, x, y, heading(it.d), { ch: it.ch, s: 1.15, phase: (t - t0) / (2 * BEAT), t, armAmt: .15 }); }
  const [px, py] = path(0);
  TD.personTop(g, px, py, heading(0), { ch: CAST.piper, s: 1.25, phase: (t - t0) / (2 * BEAT), t, flute: true, armAmt: .15, armFwd: true });
  g.restore();
}

// ---------------------------------------------------------------- 30: close-ups of strangely peaceful faces, one per accent
function shot30(g, t, lt) {
  const t0 = b(29);
  const acc = [0, 3, 6, 8, 11, 14].map(s => b(29, s) + HIT);
  PO.blurred(g, 10, (g2) => {
    E.sky(g2, 'night', W, 1100, t); E.moon(g2, 300, 380, 120);
    g2.save(); g2.translate(-((t - t0) * 160) % 220, 1250); let x = -100; for (let i = 0; i < 9; i++) { E.house(g2, x, 0, 210, 400, { seed: 140 + i, mood: 'night', lit: .6, litAlways: true }); x += 230; } g2.restore();
    g2.fillStyle = '#4a4e66'; g2.fillRect(0, 1250, W, 700);
  });
  E.LIGHTS.length = 0;   // out-of-focus background: its windows are already lit in the art
  // two rows of children (back row smaller); one by one, on each accent, they turn to look at us
  const drift = -(t - t0) * 50;
  const slots = [[360, 1640, 2.2, 0], [180, 2080, 3.1, 1], [740, 1660, 2.2, 2], [560, 2120, 3.2, 3], [1010, 1630, 2.1, 4], [930, 2090, 3.0, 5]];
  slots.sort((a, c) => a[1] - c[1]);
  for (const [x0, y, s, i] of slots) {
    const ch = KID(40 + i);
    const pose = tt => R.merge(ST.hypnoWalker(ch.B, { yaw: -Math.PI / 2 + .3, t0 })(tt), { head: { yaw: (Math.PI / 2 - .3) * ease.back(clamp((tt - acc[i]) / .1)), pitch: .04, roll: 0 },
      face: { eyes: tt > acc[i] ? 'half' : 'sleepy', mouth: 'peace', glint: 1.8, look: [0, 0] } });
    PS.drawPerson(g, ch, pose(t), { x: x0 + drift, y, s, lw: 7, lagA: pose(t - .07), lagB: pose(t - .16), t });
  }
}

// ---------------------------------------------------------------- 31: silhouettes against a huge moon, toward the mountain
function shot31(g, t, lt) {
  const t0 = b(30);
  const gr = g.createLinearGradient(0, 0, 0, H); gr.addColorStop(0, '#2a2442'); gr.addColorStop(.55, '#5c4a74'); gr.addColorStop(1, '#8a6a88'); g.fillStyle = gr; g.fillRect(0, 0, W, H);
  K.glow(g, 600, 900, 900, '#e8d8f0', .35, 'source-over');
  K.ellipse(g, 600, 930, 330, 330, { fill: '#efe2d6', lw: 5 }); E.addLight(g, 600, 930, 900, '#d8c8f0', .5);
  E.mountain(g, 980, 1400, { mood: 'night', open: 1, lw: 5 });
  // the slope path (silhouette), rising to the right
  K.shape(g, [[-60, 1700], [300, 1610], [700, 1500], [1140, 1380], [1140, H + 50], [-60, H + 50]], { fill: '#1d1626', lw: 5, tension: .3 });
  // the procession climbing: black silhouettes, the Piper leading at the top
  const v = 62 / (2 * BEAT) * .55;
  const slope = x => lerp(1700, 1380, (x + 60) / 1200) - 6;
  const lead = 760 + (t - t0) * v;
  PS.drawPerson(g, CAST.piper, R.merge(R.walk(ST.stridePh(t, t0), { B: CAST.piper.B, stride: 100, bob: 2, arm: 0 }), { yaw: Math.PI / 2 - .2, arms: PP.playPose(t).arms, hands: { l: 'none', r: 'none' } }),
    { x: lead, y: slope(lead), s: .62, sil: '#120d18', lw: 3, t, wind: .6, shadow: false });
  for (let i = 0; i < 20; i++) {
    const ch = KID(60 + i);
    const x = lead - 95 - i * 62; if (x < -80) continue;
    PS.drawPerson(g, ch, ST.hypnoWalker(ch.B, { yaw: Math.PI / 2 - .2, t0 })(t), { x, y: slope(x) + (i % 2) * 6, s: .62, sil: '#120d18', lw: 3, t, shadow: false });
  }
  E.fog(g, 1420, 420, t, { col: '#b8a8d0', a: .3, speed: 14 });
}

// ---------------------------------------------------------------- 32: the passage -- they vanish group by group on the stabs; it closes in the silence
function shot32(g, t, lt) {
  const t0 = b(31);
  const stabs = [b(31, 0), b(31, 4), b(31, 8)].map(x => x + HIT);
  const close = ease.io(clamp((t - GAP3) / .3));
  const gr = g.createLinearGradient(0, 0, 0, H); gr.addColorStop(0, '#141a30'); gr.addColorStop(1, '#2e3654'); g.fillStyle = gr; g.fillRect(0, 0, W, H);
  E.sky(g, 'night', W, 1200, t); E.moon(g, 860, 260, 80);
  const push = 1 + .08 * ease.io(lt / 1.77);
  g.save(); g.translate(W / 2, 1300); g.scale(push, push); g.translate(-W / 2, -1300);
  E.mountain(g, 540, 1500, { mood: 'night', open: 1 - close, glow: 1 - close, lw: 6 });
  // the cleft's inner light
  if (close < 1) { K.glow(g, 540, 1380, 220, '#bfd0ff', .28 * (1 - close), 'source-over'); }
  // ground
  K.shape(g, [[-60, 1500], [W + 60, 1500], [W + 60, H + 60], [-60, H + 60]], { fill: '#1b2034', lw: 5, smooth: false });
  // groups of silhouettes queued at the passage: each group vanishes on a stab (a breath of light)
  const groups = [[0, [[420, 1505], [470, 1520], [380, 1530], [520, 1512]]], [1, [[300, 1560], [250, 1580], [350, 1590], [200, 1600]]], [2, [[160, 1640], [100, 1660], [60, 1680], [210, 1690]]]];
  for (const [gi, members] of groups) {
    const gone = ease.o(clamp((t - stabs[gi]) / .18));
    members.forEach(([x, y], k) => {
      if (gone >= 1) return;
      const ch = KID(80 + gi * 4 + k);
      g.save(); g.globalAlpha = 1 - gone;
      PS.drawPerson(g, ch, ST.hypnoWalker(ch.B, { yaw: Math.PI - .6, t0 })(t), { x: x + gone * 30, y: y - gone * 20, s: .55 + (y - 1500) / 900, sil: '#0a0b14', lw: 3, t, shadow: false });
      g.restore();
      if (gone > 0) K.glow(g, x, y - 70, 70 * (1 - gone) + 15, '#bfd0ff', .25 * (1 - gone), 'lighter');
    });
  }
  // the Piper: last at the mouth, steps in as the silence begins
  const inside = ease.io(clamp((t - GAP3 + .25) / .35));
  if (inside < 1) { g.save(); g.globalAlpha = 1 - inside; PS.drawPerson(g, CAST.piper, R.merge(PP.playPose(t), { yaw: Math.PI - .2 }), { x: 560, y: 1500 - inside * 30, s: .62 * (1 - inside * .2), sil: '#06070d', lw: 3, t, wind: .4, shadow: false }); g.restore(); }
  g.restore();
}

module.exports = [
  { id: '28_tracking_procession', t0: b(27), mood: 'night', draw: shot28 },
  { id: '29_overhead_snake', t0: b(28), mood: 'night', draw: shot29 },
  { id: '30_peaceful_faces', t0: b(29), mood: 'night', draw: shot30 },
  { id: '31_moon_silhouettes', t0: b(30), mood: 'dusk', grade: () => ({ mood: 'night', amt: .45 }), draw: shot31 },
  { id: '32_passage_closes', t0: b(31), mood: 'night', draw: shot32, finish: (t) => ({ fade: t > GAP3 ? .3 * ease.io(clamp((t - GAP3) / .4)) : 0 }) },
];
