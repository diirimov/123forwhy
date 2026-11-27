// 35-42 DROP 2 -- THE CHILDREN (bars 24-31). Peaceful, rhythmic, perfectly coordinated -- never zombies: the
// fear comes from the precision. Doors fly open on the beats; lockstep feet; the procession grows from every
// alley; faces tilt in a canon then freeze and stare in the break; the snake from above; quarter-bar trades
// (Piper / children) on the call and response; silhouettes against the moon; the mountain opens.
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
const DP = require('../dp');
const CH = require('../chor');
const HOOK = require('./v_a_hook').helpers;
const { barT: b, clamp, lerp, ease, BEAT, BAR, S16, HIT, W, H, TAU, hash } = C;
const { PAL } = K;
const KID = i => CAST.child(600 + i);
const KSTRIDE = HOOK.KSTRIDE, KSPEED = HOOK.KSPEED;
const BREAK = C.BM.gaps[3];      // 47.426
const calm = { eyes: 'half', mouth: 'peace', glint: 1.4 };

// ---------------------------------------------------------------- 35: DROP 2 -- every door opens on the beat; children step out in matching strides
function shot35(g, t, lt) {
  const t0 = b(23);
  const V = new Wd.View({ cx: lerp(-30, 30, ease.io(lt / 1.77)), cy: 230, cz: lerp(180, 420, ease.io(lt / 1.77)), f: 1150, hy: 1000 });
  ST.streetBackdrop(g, V, t, 'night', { moonX: 820, moonY: 260, moonR: 110 });
  const items = [];
  DP.wall(items, 4200, 11, { sp: 620, seed: 171, mood: 'night', lit: .7 });
  // the near facade row: 4 houses, each door opens on a beat, shutters too
  const homes = [[-930, 0], [-310, 1], [310, 2], [930, 3]].map(([x, k]) => [x * .95, k]);
  homes.forEach(([x, k], i) => {
    const td = t0 + k * BEAT + HIT;
    const open = ease.back(clamp((t - td) / .16));
    items.push(Wd.houseItem(x, 1750, 255, 440, { seed: 180 + i, mood: 'night', lit: 1, allWindows: true, litByShutter: true, shutter: () => open, doorOpen: open, doorX: .5 }));
    // children step out (one per 8th note after the door opens) and walk toward us in lockstep
    for (let j = 0; j < 3; j++) {
      const te = td + .2 + j * BEAT / 2;
      if (t < te) continue;
      const ch = KID(i * 3 + j);
      const zz = 1680 - (t - te) * KSPEED * 1.6 - 40, xx = x + (j - 1) * 110 * clamp((t - te) * 2);
      items.push({ z: zz, draw: (g2, V2) => ST.actor(g2, V2, ch, xx, zz, CH.procWalk(ch.B, { t0: te, idx: i * 3 + j, stride: KSTRIDE * 1.6, face: calm }), t) });
    }
  });
  // the Piper, back to us in the foreground, playing them out
  items.push({ z: 1080, draw: (g2, V2) => ST.actor(g2, V2, CAST.piper, 200, 1080, tt => R.merge(PP.playPose(tt, { glow: 0 }), { yaw: Math.PI - .5 }), t, { wind: .5 }) });
  Wd.drawItems(g, V, items);
  E.fog(g, 1120, 420, t, { col: '#aab9de', a: .3, speed: 20 });
}

// ---------------------------------------------------------------- 36: the feet -- a forest of legs in lockstep, hems swinging, moon shadows
function shot36(g, t, lt) {
  const t0 = b(24);
  const V = new Wd.View({ cx: -(t - t0) * KSPEED * .5, cy: 120, cz: 0, f: 900, hy: 1100 });
  g.save(); g.translate(W / 2, 1371); g.scale(2.1, 2.1); g.translate(-W / 2, -1371);
  ST.streetBackdrop(g, V, t, 'night', { moonX: 820, moonY: 200, moonR: 100 });
  const items = [];
  DP.wall(items, 1500, 11, { sp: 520, seed: 191, mood: 'night', lit: .9, x0: -(t - t0) * 60 });
  for (let r = 0; r < 3; r++) for (let i = 0; i < 9; i++) {
    const ch = KID(40 + r * 9 + i);
    const x = 500 - i * 165 - r * 80 - (t - t0) * KSPEED, z = 330 + r * 120;
    items.push({ z, draw: (g2, V2) => ST.actor(g2, V2, ch, x, z, CH.procWalk(ch.B, { yaw: -Math.PI / 2, idx: i + r, stride: KSTRIDE, t0 }), t, { occlude: false, shadowA: .45 }) });
  }
  Wd.drawItems(g, V, items);
  g.restore();
}

// ---------------------------------------------------------------- 37: the procession grows -- he walks toward us; every alley feeds in children on the 8ths
function shot37(g, t, lt) {
  const t0 = b(25);
  const pz = 900 - (t - t0) * KSPEED * .5;
  const { V, items } = HOOK.nightTown(g, t, { cam: { cz: pz - 680, cy: 230, f: 1150 }, moonX: 300, moonY: 300, moonR: 130, sides: true });
  // rows of four behind him; children slide in from the side alleys one per 8th note
  const rows = 12;
  for (let r = 0; r < rows; r++) for (let c = 0; c < 6; c++) {
    const id = r * 6 + c;
    const join = t0 - 1.6 + id * BEAT / 6;
    const inU = ease.io(clamp((t - join) / .6));
    if (inU <= 0) continue;
    const ch = KID(80 + id);
    const x = (c - 2.5) * 140 + (1 - inU) * (c < 3 ? -900 : 900), z = pz + 220 + r * 160;
    items.push({ z, draw: (g2, V2) => ST.actor(g2, V2, ch, x, z, CH.procWalk(ch.B, { t0, idx: id % 8, stride: KSTRIDE * .5, yaw: (1 - inU) * (c < 3 ? 1.3 : -1.3), face: calm, swayAmt: 1.3 }), t) });
  }
  DP.actorAt(items, CAST.piper, 0, pz, CH.piperWalkPlay(PP, { t0, stride: KSTRIDE * .5 * 1.72, glow: .7 }), t, { wind: .6 });
  DP.flush(g, V, items);
  E.fog(g, 1120, 480, t, { col: '#aab9de', a: .3, speed: 22 });
}

// ---------------------------------------------------------------- 38: faces -- heads tilt in a canon on the cadence, then in the break they snap to us and freeze
function shot38(g, t, lt) {
  const t0 = b(26);
  const frozen = t >= BREAK - .005;
  PO.blurred(g, 10, (g2) => {
    E.sky(g2, 'night', W, 1100, t); E.moon(g2, 300, 380, 120);
    g2.save(); g2.translate(-((Math.min(t, BREAK) - t0) * 160) % 220, 1250); let x = -100; for (let i = 0; i < 9; i++) { E.house(g2, x, 0, 210, 400, { seed: 240 + i, mood: 'night', lit: .7, litAlways: true }); x += 230; } g2.restore();
    g2.fillStyle = '#4a4e66'; g2.fillRect(0, 1250, W, 700);
  });
  E.LIGHTS.length = 0;
  const drift = -(Math.min(t, BREAK) - t0) * 50;
  const slots = [[200, 1500, 2.4, 0], [520, 1530, 2.5, 1], [850, 1500, 2.4, 2], [360, 2060, 3.4, 3], [760, 2080, 3.5, 4], [1080, 2050, 3.3, 5], [-60, 2040, 3.3, 6]];
  const notes = C.FL.filter(n => n.t >= t0 && n.t < BREAK).map(n => n.t);
  for (const [x0, y, s, i] of slots) {
    const ch = KID(140 + i);
    const tm = frozen ? BREAK : t;
    const pose = tt => {
      const T = Math.min(tt, BREAK);
      const P = CH.procWalk(ch.B, { yaw: -Math.PI / 2 + .35, t0, idx: i, face: calm })(T);
      // canon: each child's head tilts on a successive note
      const nt = notes[i % Math.max(1, notes.length)] ?? t0;
      const tilt = Math.sin(Math.PI * clamp((T - nt) / .4)) * .3 * (i % 2 ? 1 : -1);
      P.head = { yaw: .2, pitch: .05, roll: tilt };
      if (tt >= BREAK) { const u = ease.back(clamp((tt - BREAK) / .07)); P.head = { yaw: (Math.PI / 2 - .35) * u, pitch: -.04, roll: 0 }; P.face = { eyes: 'open', mouth: 'flat', glint: 2, pupil: .6, look: [0, 0] }; }
      return P;
    };
    PS.drawPerson(g, ch, pose(t), { x: x0 + drift, y, s, lw: 7, lagA: pose(t - .07), lagB: pose(t - .16), t });
  }
}

// ---------------------------------------------------------------- 39: from above -- the snake through the moonlit roofs, four abreast, long shadows
function shot39(g, t, lt) {
  const t0 = b(27);
  const scroll = (t - t0) * 130;
  const rot = lerp(.16, -.08, ease.io(lt / 1.77));
  g.save(); g.translate(W / 2, H / 2); g.rotate(rot); g.scale(1.3, 1.3); g.translate(-W / 2, -H / 2 + scroll);
  TD.cobblesTop(g, -600, -scroll - 1600, W + 600, -scroll + H + 1600, { base: '#7b7f95', gap: '#3e4256' });
  TD.roofsTop(g, 60, -scroll - 1900, -scroll + H + 1900, -1, { seed: 11 }); TD.roofsTop(g, W - 60, -scroll - 1900, -scroll + H + 1900, 1, { seed: 13 });
  const leadY = H * .3 - scroll;
  const path = d => [W / 2 + Math.sin((leadY + d) * .007 + 1) * 170, leadY + d];
  const heading = d => { const a = path(d), c = path(d - 4); return Math.atan2(c[1] - a[1], c[0] - a[0]); };
  const members = [];
  for (let i = 0; i < 34; i++) for (const lat of [-45, -15, 15, 45]) members.push({ d: 110 + i * 62, lat, ch: KID(200 + i * 4 + (lat + 45) / 30) });
  g.save(); g.globalAlpha = .3; g.fillStyle = '#0c0c18';
  for (const m of members) { const [x, y] = path(m.d); g.save(); g.translate(x + m.lat, y); g.rotate(.7); g.beginPath(); g.ellipse(60, 0, 80, 20, 0, 0, TAU); g.fill(); g.restore(); }
  g.restore();
  for (const m of members) { const [x, y] = path(m.d); TD.personTop(g, x + m.lat, y, heading(m.d), { ch: m.ch, s: 1.0, phase: (t - t0) / (2 * BEAT), t, armAmt: .08 }); }
  const [px, py] = path(0);
  TD.personTop(g, px, py, heading(0), { ch: CAST.piper, s: 1.2, phase: (t - t0) / (2 * BEAT), t, flute: true, armAmt: .1, armFwd: true });
  g.restore();
}

// ---------------------------------------------------------------- 40: call & response -- four quarter-bar cuts: Piper / children / Piper / children
function shot40(g, t, lt) {
  const t0 = b(28);
  const q = Math.min(3, Math.floor((t - t0 + 1e-6) / BEAT));
  const qt = t - t0 - q * BEAT;
  if (q === 0 || q === 2) {
    // the Piper, low angle against the moon (q0) / his playing hands and eyes from the side (q2)
    const gr = g.createLinearGradient(0, 0, 0, H); gr.addColorStop(0, '#141a30'); gr.addColorStop(1, '#2e3654'); g.fillStyle = gr; g.fillRect(0, 0, W, H);
    E.moon(g, q === 0 ? 540 : 260, q === 0 ? 620 : 420, q === 0 ? 330 : 180);
    E.addLight(g, 540, 620, 700, '#c8d4f0', .4);
    const P = R.merge(PP.playPose(t, { eyes: 'narrow', glow: 1 }), { yaw: q === 0 ? .05 : .9 });
    const S = q === 0 ? 3.1 : 4.6, push = 1 + .06 * qt / BEAT;
    g.save(); g.translate(W / 2, H * .55); g.scale(push, push); g.translate(-W / 2, -H * .55);
    PS.drawPerson(g, CAST.piper, P, { x: q === 0 ? 540 : 600, y: q === 0 ? 2160 : 2550, s: S, lw: 8, t, wind: 1, shadow: false });
    g.restore();
  } else {
    // the children answer: a wide crowd lifts its arms in unison (q1) / a row of heads tilts left together (q3)
    const { V, items } = HOOK.nightTown(g, t, { cam: { cz: q === 1 ? 0 : 420, cy: q === 1 ? 260 : 330, f: 1150 }, moonX: 760, moonY: 300 });
    const rows = q === 1 ? [[900, 5, 300], [1200, 6, 280], [1550, 7, 260], [1900, 8, 250]] : [[620, 4, 260], [840, 5, 240]];
    rows.forEach(([z, n, sp], r) => { for (let i = 0; i < n; i++) {
      const ch = KID(300 + r * 10 + i), x = (i - (n - 1) / 2) * sp + (r % 2) * sp * .5;
      items.push({ z, draw: (g2, V2) => ST.actor(g2, V2, ch, x, z, tt => {
        const P = CH.procWalk(ch.B, { t0, idx: i, stride: 0, face: { eyes: 'half', mouth: 'peace', glint: 1.6 }, armLift: q === 1 ? ease.io(clamp((tt - t0 - BEAT) / .18)) * .9 : 0 })(tt);
        P.legs = { l: [ch.B.hipW + 4, ch.B.foot, 0], r: [-(ch.B.hipW + 4), ch.B.foot, 0] };
        if (q === 3) P.head = { yaw: 0, pitch: .05, roll: .32 * ease.back(clamp((tt - t0 - 3 * BEAT - r * S16 * .5) / .12)) };
        return P;
      }, t) });
    } });
    DP.flush(g, V, items);
    E.fog(g, 1100, 460, t, { col: '#aab9de', a: .3, speed: 20 });
  }
}

// ---------------------------------------------------------------- 41: silhouettes against a huge moon, climbing toward the mountain (Em lift)
function shot41(g, t, lt) {
  const t0 = b(29);
  const gr = g.createLinearGradient(0, 0, 0, H); gr.addColorStop(0, '#2a2442'); gr.addColorStop(.55, '#5c4a74'); gr.addColorStop(1, '#8a6a88'); g.fillStyle = gr; g.fillRect(0, 0, W, H);
  const push = 1 + .05 * ease.io(lt / 1.77);
  g.save(); g.translate(W / 2, H * .6); g.scale(push, push); g.translate(-W / 2, -H * .6);
  K.glow(g, 560, 860, 950, '#e8d8f0', .35, 'source-over');
  K.ellipse(g, 560, 880, 400, 400, { fill: '#efe2d6', lw: 5 }); E.addLight(g, 560, 880, 900, '#d8c8f0', .5);
  E.mountain(g, 1000, 1280, { mood: 'night', open: 1, lw: 5 });
  K.shape(g, [[-60, 1560], [300, 1470], [700, 1360], [1140, 1240], [1140, H + 50], [-60, H + 50]], { fill: '#1d1626', lw: 5, tension: .3 });
  const slope = x => lerp(1560, 1240, (x + 60) / 1200) - 6;
  const v = KSPEED * .55 * .9;
  const lead = 790 + (t - t0) * v;
  PS.drawPerson(g, CAST.piper, CH.piperWalkPlay(PP, { t0, yaw: Math.PI / 2 - .2, stride: 70 })(t), { x: lead, y: slope(lead), s: .85, sil: '#120d18', lw: 3, t, wind: .8, shadow: false });
  for (let i = 0; i < 26; i++) {
    const ch = KID(400 + i);
    const x = lead - 110 - i * 64; if (x < -80) continue;
    PS.drawPerson(g, ch, CH.procWalk(ch.B, { yaw: Math.PI / 2 - .2, t0, idx: i, stride: 40 })(t), { x, y: slope(x) + (i % 2) * 8, s: .85, sil: '#120d18', lw: 3, t, shadow: false });
  }
  g.restore();
  E.fog(g, 1500, 420, t, { col: '#b8a8d0', a: .3, speed: 14 });
}

// ---------------------------------------------------------------- 42: the reveal -- the whole procession winds across the valley into the glowing passage
function shot42(g, t, lt) {
  const t0 = b(30), stab = b(30, 12) + HIT;
  const flare = C.decay(t - stab, 3) * (t > stab ? 1 : 0);
  const gr = g.createLinearGradient(0, 0, 0, H); gr.addColorStop(0, '#121830'); gr.addColorStop(1, '#2c3452'); g.fillStyle = gr; g.fillRect(0, 0, W, H);
  E.sky(g, 'night', W, 900, t); E.moon(g, 860, 230, 90);
  const pull = 1.12 - .12 * ease.io(lt / 1.77);
  g.save(); g.translate(W / 2, 900); g.scale(pull, pull); g.translate(-W / 2, -900);
  E.mountain(g, 540, 980, { mood: 'night', open: 1, glow: 1 + 2 * flare, lw: 6 });
  K.glow(g, 540, 880, 260 + 200 * flare, '#c8d8ff', .35 + .4 * flare, 'source-over');
  // the valley floor and the winding road
  K.shape(g, [[-60, 980], [W + 60, 980], [W + 60, H + 60], [-60, H + 60]], { fill: '#232a44', lw: 5, smooth: false });
  const P = u => [540 + Math.sin(u * 9) * 320 * u, lerp(985, 1880, u * u)];
  g.save(); g.lineCap = 'round'; g.strokeStyle = '#3a4466'; g.lineWidth = 60; g.beginPath(); for (let u = 0; u <= 1.001; u += .02) { const [x, y] = P(u); u === 0 ? g.moveTo(x, y) : g.lineTo(x, y); } g.stroke(); g.restore();
  const head = .02 + (t - t0) * .012;
  for (let i = 0; i < 150; i++) {
    const u = head + i * .0062; if (u > 1) break;
    const [x, y] = P(u);
    const s = .1 + u * .55;
    PS.drawPerson(g, KID(500 + (i % 40)), CH.procWalk(R.BODY.child, { t0, idx: i, stride: 40, yaw: Math.PI })(t), { x: x + ((i % 2) - .5) * 30 * s, y, s, sil: '#0b0d18', lw: 2, t, shadow: false });
  }
  const [hx, hy] = P(head - .004);
  PS.drawPerson(g, CAST.piper, R.merge(PP.playPose(t), { yaw: Math.PI }), { x: hx, y: hy, s: .12, sil: '#05060c', lw: 1.5, t, shadow: false });
  g.restore();
  E.fog(g, 1000, 360, t, { col: '#aab9de', a: .3, speed: 12 });
}

module.exports = [
  { id: '35_doors_open', t0: b(23), mood: 'night', draw: shot35, flashIn: true },
  { id: '36_lockstep_legs', t0: b(24), mood: 'night', draw: shot36, finish: () => ({ vig: .75 }) },
  { id: '37_procession_grows', t0: b(25), mood: 'night', draw: shot37 },
  { id: '38_faces_freeze', t0: b(26), mood: 'night', draw: shot38 },
  { id: '39_snake_above', t0: b(27), mood: 'night', draw: shot39, flashIn: true },
  { id: '40_trades', t0: b(28), mood: 'night', draw: shot40 },
  { id: '41_moon_ridge', t0: b(29), mood: 'dusk', grade: () => ({ mood: 'night', amt: .45 }), draw: shot41 },
  { id: '42_mountain_reveal', t0: b(30), mood: 'night', draw: shot42 },
];
