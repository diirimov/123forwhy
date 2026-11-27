// 01-05 THE HOOK (bars 1-2): the Piper in a moonlit street, an enormous procession of children behind him in
// perfect lockstep; every head snaps to camera on the plucked "ta-ta" (0.882 / 0.993); then rapid cuts on the
// beat: his fingers (real fingering of the taunt), his eyes, the synchronised feet, the procession from above.
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
const { barT: b, clamp, lerp, ease, BEAT, S16, HIT, W, H, TAU, hash } = C;

const SNAP1 = b(0, 8) + HIT, SNAP2 = b(0, 9) + HIT;           // the plucked answer's repeated notes
const KSTRIDE = 58, KSPEED = KSTRIDE / (.6 * 2 * BEAT);          // no foot sliding: body speed = stride / stance time
const DIRX = -.66, DIRZ = -.75;                                  // the line comes out of the fog behind him, toward camera-left
const DN = Math.hypot(DIRX, DIRZ), dx = DIRX / DN, dz = DIRZ / DN;
const KYAW = Math.atan2(dx, -dz);
// procession members: 3 abreast, spaced along the line
const KIDS = [];
for (let i = 0; i < 20; i++) for (let j = 0; j < 3; j++) KIDS.push({ ch: CAST.child(300 + i * 3 + j), s: i * 190 + (j === 1 ? 70 : 0) + hash(i * 7 + j) * 30, lat: (j - 1) * 135, idx: i * 3 + j });
// the opening camera (the last shot returns to exactly this frame)
const OPEN_CAM = { cx: 0, cy: 205, cz: 0, f: 1150, hy: 1000 };

function nightTown(g, t, o = {}) {
  return DP.town(g, t, { mood: 'night', cam: o.cam || OPEN_CAM, moonX: 790, moonY: 330, moonR: 120, lit: .7, seed: 8, zNear: 3000, zMid: 3900, zFar: 5000, sides: true, ...o });
}

// heads snap on the plucked accent; returns a procession walker for kid k
function kidPose(k, snap = true) {
  return CH.procWalk(k.ch.B, {
    yaw: KYAW, idx: k.idx % 6, stride: KSTRIDE,
    headYaw: tt => snap ? -KYAW * ease.back(clamp((tt - (k.lat < 0 ? SNAP1 : k.lat > 0 ? SNAP2 : (SNAP1 + SNAP2) / 2)) / .09)) : 0,
    pitch: tt => snap ? lerp(.22, -.02, ease.back(clamp((tt - SNAP1) / .09))) : .2,
    face: tt => (snap && tt > SNAP1) ? { eyes: 'open', mouth: 'peace', glint: 1.8, pupil: .65, look: [0, 0] } : { eyes: 'half', mouth: 'peace', glint: .5 },
  });
}
function procession(items, t, o = {}) {
  const base = o.base || [-330, 800];
  const travel = KSPEED * t;
  for (const k of KIDS) {
    const d = travel - k.s + (o.offset || 0);
    const X = base[0] + dx * d + (-dz) * k.lat, Z = base[1] + dz * d + dx * k.lat;
    if (Z < 260 || X < -0.47 * Z - 400) continue;            // only once they have walked out of frame (left edge)
    items.push({ z: Z, draw: (g2, V2) => ST.actor(g2, V2, k.ch, X, Z, kidPose(k, o.snap !== false), t) });
  }
}

// ---------------------------------------------------------------- 01: the Piper and the procession
function shot01(g, t, lt) {
  const u = ease.io(clamp(lt / 1.77));
  const cam = { ...OPEN_CAM, cz: lerp(0, 70, u), cx: lerp(0, -20, u) };
  const { V, items } = nightTown(g, t, { cam });
  procession(items, t);
  // the Piper, front and centre: playing, weight shifting, cloak in the night wind
  DP.actorAt(items, CAST.piper, 150, 640, tt => R.merge(PP.playPose(tt, { eyes: tt > SNAP1 ? 'narrow' : 'closed', glow: tt > SNAP1 ? .5 : 0 }), { yaw: -.18 }), t, { wind: .6 });
  items.push(Wd.propItem(-1150, 1150, (g2, s) => E.torch(g2, 0, -700, { t, s: 2.4, lw: 4 / s })));
  DP.flush(g, V, items);
  E.fog(g, 1020, 480, t, { col: '#aab9de', a: .38, speed: 22 });
  E.fog(g, 1330, 420, t, { col: '#9fb0d8', a: .2, speed: -14, off: 400 });
}

// ---------------------------------------------------------------- 02: his fingers -- the real fingering of the taunt
function shot02(g, t, lt) {
  const gr = g.createLinearGradient(0, 0, 0, H); gr.addColorStop(0, '#1b2036'); gr.addColorStop(1, '#2a2440'); g.fillStyle = gr; g.fillRect(0, 0, W, H);
  PO.blurred(g, 18, (g2) => { for (let i = 0; i < 14; i++) { g2.fillStyle = i % 3 ? '#f3b860' : '#8ea4d8'; g2.globalAlpha = .5; g2.beginPath(); g2.arc(hash(i) * W, 200 + hash(i * 3) * 1500, 30 + hash(i * 5) * 50, 0, TAU); g2.fill(); } g2.globalAlpha = 1; });
  E.LIGHTS.length = 0;
  // the cloak + doublet fill the frame behind the hands
  K.shape(g, [[-60, 380], [460, 300], [760, 520], [1160, 700], [1160, H + 60], [-60, H + 60]], { fill: '#4a2c45', lw: 8, tension: .4 });
  K.shape(g, [[260, 600], [700, 640], [820, H + 60], [140, H + 60]], { fill: K.PAL.burg, lw: 8, tension: .3 });
  const push = 1 + .05 * ease.io(lt / .44);
  g.save(); g.translate(W / 2, H / 2); g.scale(push, push); g.translate(-W / 2, -H / 2);
  PP.closeupFlute(g, 430, 330, 1.78, 2.05, t, { lw: 8 });
  g.restore();
  E.addLight(g, 900, 200, 900, '#8fa6d8', .4);
}

// ---------------------------------------------------------------- 03: his eyes open under the hat brim
function shot03(g, t, lt) {
  const gr = g.createLinearGradient(0, 0, 0, H); gr.addColorStop(0, '#161a2e'); gr.addColorStop(1, '#262036'); g.fillStyle = gr; g.fillRect(0, 0, W, H);
  E.moon(g, 900, 260, 160);
  const open = ease.o(clamp((t - b(1, 4) - .05) / .2));
  const P = R.merge(PP.playPose(t, { eyes: open > .5 ? 'narrow' : 'closed', glow: .9 * open }), {
    yaw: .12, head: { yaw: -.1, pitch: .12 - .04 * open, roll: .05 },
  });
  P.face = { ...P.face, look: [.15, .1], glint: 1.8, pupil: .6, brow: 'sly' };
  const S = 6.0, push = 1 + .05 * ease.io(lt / .44);
  g.save(); g.translate(W / 2, H * .4); g.scale(push, push); g.translate(-W / 2, -H * .4);
  PS.drawPerson(g, CAST.piper, P, { x: 600, y: 760 + 420 * S, s: S, lw: 10, t, shadow: false, wind: .3 });
  g.restore();
  E.addLight(g, 300, 800, 700, '#f09a4a', .3);
}

// ---------------------------------------------------------------- 04: the feet -- lockstep on the cobbles
function shot04(g, t, lt) {
  const t0 = b(1, 8);
  const V = new Wd.View({ cx: -(t - t0) * KSPEED * .35, cy: 120, cz: 0, f: 900, hy: 1100 });
  g.save(); g.translate(W / 2, 1371); g.scale(2.3, 2.3); g.translate(-W / 2, -1371);
  ST.streetBackdrop(g, V, t, 'night', { moonX: 820, moonY: 260, moonR: 100 });
  const items = [];
  DP.wall(items, 1500, 9, { sp: 520, seed: 31, mood: 'night', lit: .8, x0: 100 });
  // two rows of children crossing right -> left: legs, hems and shoes fill the screen, heels land on the beats
  for (let r = 0; r < 2; r++) for (let i = 0; i < 6; i++) {
    const ch = CAST.child(400 + r * 9 + i);
    const x = 420 - i * 170 - r * 85 - (t - t0) * KSPEED, z = 330 + r * 110;
    items.push({ z, draw: (g2, V2) => ST.actor(g2, V2, ch, x, z, CH.procWalk(ch.B, { yaw: -Math.PI / 2, idx: i, stride: KSTRIDE }), t, { occlude: false }) });
  }
  DP.flush(g, V, items);
  g.restore();
  E.LIGHTS.length = 0;
}

// ---------------------------------------------------------------- 05: from above -- the procession winds through the town, still growing
function shot05(g, t, lt) {
  const t0 = b(1, 12);
  const zoom = lerp(1.75, 1.5, ease.io(clamp(lt / .44)));
  g.save(); g.translate(W / 2, H / 2); g.rotate(-.18); g.scale(zoom, zoom); g.translate(-W / 2, -H / 2);
  TD.cobblesTop(g, -600, -600, W + 600, H + 600, { base: '#7b7f95', gap: '#3e4256' });
  TD.roofsTop(g, 60, -900, H + 900, -1, { seed: 21 }); TD.roofsTop(g, W - 60, -900, H + 900, 1, { seed: 23 });
  const lead = H * .12 - (t - t0) * 90;
  const path = d => [W / 2 + Math.sin((lead + d) * .006) * 170, lead + d];
  for (let i = 0; i < 46; i++) for (const lat of [-34, 0, 34]) {
    const d = 130 + i * 54; const [x, y] = path(d); const [x2, y2] = path(d - 5);
    if (y > H + 100) continue;
    TD.personTop(g, x + lat, y, Math.atan2(y2 - y, x2 - x), { ch: CAST.child(500 + i * 3 + (lat > 0 ? 2 : lat < 0 ? 0 : 1)), s: 1.0, phase: (t - t0) / (2 * BEAT), t, armAmt: .1 });
  }
  const [px, py] = path(0); const [qx, qy] = path(-5);
  TD.personTop(g, px, py, Math.atan2(qy - py, qx - px), { ch: CAST.piper, s: 1.15, phase: (t - t0) / (2 * BEAT), t, flute: true, armAmt: .1, armFwd: true });
  g.restore();
}

module.exports = [
  { id: '01_procession_hook', t0: 0, mood: 'night', draw: shot01, finish: () => ({ vig: .72 }) },
  { id: '02_fingers', t0: b(1), mood: 'night', draw: shot02, finish: () => ({ vig: .8 }) },
  { id: '03_eyes', t0: b(1, 4), mood: 'night', draw: shot03, finish: () => ({ vig: .85 }) },
  { id: '04_lockstep_feet', t0: b(1, 8), mood: 'night', draw: shot04, finish: () => ({ vig: .75 }) },
  { id: '05_procession_above', t0: b(1, 12), mood: 'night', draw: shot05, finish: () => ({ vig: .75 }) },
];
module.exports.helpers = { OPEN_CAM, nightTown, procession, KIDS, KSPEED, KSTRIDE, kidPose };
