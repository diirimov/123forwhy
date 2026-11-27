// 03-06: the infestation and the chaos (day, the studio's sepia)
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
const K = require('../ink');
const PO = require('../post');
const { barT: b, clamp, lerp, ease, tween, BEAT, S16, HIT, W, H, TAU, hash, EV } = C;

const CLOUDS = [[200, 300, 1.2], [620, 190, .9]];

// ---------------------------------------------------------------- 03: rats pour out of the drain
function shot03(g, t, lt) {
  const V = new Wd.View({ cx: 0, cy: 170, cz: lerp(0, 120, ease.io(lt / 1.77)), f: 1050, hy: 1000 });
  ST.streetBackdrop(g, V, t, 'day', { clouds: CLOUDS });
  const items = Wd.streetItems({ mood: 'day', seed: 21, half: 820, z0: 900 });
  // market stalls + townsfolk in the distance
  items.push(Wd.propItem(-420, 2600, (g2, s) => E.stall(g2, -260, 0, 520, { lw: 4 / s, seed: 4 })));
  items.push(Wd.propItem(520, 3000, (g2, s) => E.stall(g2, -260, 0, 520, { lw: 4 / s, seed: 7, stripe: ['#53719a', '#e8dcbf'] })));
  const folks = ST.crowd(5, 3, { x0: -700, x1: 700, z0: 2300, z1: 3400 });
  for (const f of folks) items.push({ z: f.z, draw: (g2, V2) => ST.actor(g2, V2, f.ch, f.x, f.z, tt => R.merge(R.idle(tt, { seed: f.seed }), { yaw: f.r * 2 - 1, face: { mouth: 'o', eyes: 'wide' }, head: { yaw: -.4 } }), t) });
  // the drain grate
  const GZ = 640;
  items.push({ z: GZ + 60, draw: (g2, V2) => {
    const [sx, sy, s] = V2.p(0, 0, GZ); const rx = 150 * s, ry = 150 * s * (V2.cy / GZ) * .9 + 6;
    K.ellipse(g2, sx, sy, rx * 1.12, ry * 1.12, { fill: '#6a6258', lw: V2.lw(s) });
    K.ellipse(g2, sx, sy, rx, ry, { fill: '#120c08', lw: V2.lw(s) * .7 });
    g2.save(); g2.beginPath(); g2.ellipse(sx, sy, rx, ry, 0, 0, TAU); g2.clip();
    for (let i = -3; i <= 3; i++) K.line(g2, [[sx + i * rx * .28, sy - ry], [sx + i * rx * .28, sy + ry]], 5 * s + 2, '#4a4440', 1, false);
    g2.restore();
  } });
  // rats stream out of the grate on 32nd notes, fanning across the street
  const N = 46, t0 = b(2) + .04;
  for (let i = 0; i < N; i++) {
    const te = t0 + i * .036 + hash(i * 3.1) * .02;
    if (t < te) continue;
    const ang = (hash(i * 7.7) - .5) * 2.6 + (i % 3 === 0 ? Math.PI : 0) * (hash(i) < .35 ? 1 : 0);
    const sp = 520 + hash(i * 1.9) * 260;
    const d = (t - te) * sp;
    const x = Math.sin(ang) * d * 1.2, z = GZ - Math.cos(ang) * d * .9;
    const rise = clamp((t - te) / .12);
    items.push({ z: z - 1, draw: (g2, V2) => {
      if (z - V2.cz < 380) return;
      ST.ratAt(g2, V2, x, z, { dir: Math.sin(ang) >= 0 ? 1 : -1, phase: d / 120, speed: 1, t, size: 1.1 * (.4 + .6 * rise), y: -60 * (1 - rise) });
    } });
  }
  Wd.drawItems(g, V, items);
}

// ---------------------------------------------------------------- 04: rooftops + bursting grain sacks
function shot04(g, t, lt) {
  const pan = ease.io(clamp(lt / 1.77));
  g.save();
  g.translate(0, lerp(-40, 40, pan));
  E.sky(g, 'day', W, 1100, t); E.sun(g, 860, 220, 62, t); E.cloud(g, 260, 260, 1, 1);
  E.skyline(g, -100, 760, 1300, 'day', 9);
  // row of houses (frontal), rats running the roof ridges
  const roofs = [];
  g.save(); g.translate(0, 1450); g.scale(1.25, 1.25);
  let x = -120; let i = 0;
  while (x < W / 1.25 + 100) { const w = 190 + hash(i * 5) * 70, h = 360 + hash(i * 3) * 120; const r = E.house(g, x, 0, w, h, { seed: 70 + i, mood: 'day' }); roofs.push(r); x += w + 22; i++; }
  g.restore();
  // ridge-running rats (synchronised gallop, they leap the gaps between gables on the beats)
  const n = 13;
  for (let k = 0; k < n; k++) {
    const sp = 330;
    const xx = ((k * 150 + (t - b(3)) * sp) % (W + 400)) - 200;
    // find roof under xx (screen) to ride the slope
    let yy = 900, tilt = 0;
    for (const r of roofs) { const a = r.rx0 * 1.25, c = r.rx1 * 1.25, pk = 1450 + r.peak * 1.25, base = 1450 + r.topY * 1.25, mid = (a + c) / 2; if (xx >= a && xx <= c) { yy = xx < mid ? lerp(base, pk, (xx - a) / (mid - a)) : lerp(pk, base, (xx - mid) / (c - mid)); tilt = xx < mid ? -.75 : .75; } }
    RT.ratSide(g, xx, yy + 6, { s: .95, dir: 1, phase: (t - b(3)) * 4 + k * .13, speed: 1, t, tilt: tilt * .9, shadow: false });
  }
  // street in front of the houses (cobbles), then the market stall + sacks
  { const V = new Wd.View({ cx: 0, cy: 200, cz: 0, f: 900, hy: 1290 }); g.save(); g.beginPath(); g.rect(0, 1450, W, 800); g.clip(); Wd.ground(g, V, { mood: 'day', zFar: 2600 }); g.restore(); }
  E.stall(g, 470, 1780, 520, { lw: 5, seed: 11 });
  const tambs = C.eventsIn(EV.clap || [], 0, 0); // (unused)
  const splits = [b(3, 2), b(3, 10)];
  const sacks = [[160, 1790, 1.6, splits[0]], [330, 1820, 1.45, splits[1]], [40, 1840, 1.3, Infinity]];
  for (const [sx, sy, s, ts] of sacks) {
    const torn = clamp((t - ts - HIT) / .15);
    E.sack(g, sx, sy, s, { torn, lw: 5 });
    if (t > ts) for (let j = 0; j < 7; j++) {
      const dt = t - ts - j * .07; if (dt < 0) continue;
      const rx = sx - 10 + dt * (380 + j * 40) * (j % 2 ? 1 : .8), ry = sy + 10 - Math.max(0, Math.sin(Math.min(1, dt * 3) * Math.PI) * 60 * (1 - dt));
      if (rx < W + 100) RT.ratSide(g, rx, Math.min(sy + 14, ry + 14), { s: 1.05, dir: 1, phase: dt * 5 + j * .3, t, speed: 1 });
    }
  }
  g.restore();
}

// ---------------------------------------------------------------- 05: the merchant's barrel
function shot05(g, t, lt) {
  const t0 = b(4);
  // background: market, softened
  PO.blurred(g, 7, (g2) => {
    E.sky(g2, 'day', W, 900, t); E.sun(g2, 200, 200, 60, t);
    g2.save(); g2.translate(0, 1180); g2.scale(1.1, 1.1); let x = -60; let i = 0; while (x < 1100) { const w = 200 + hash(i) * 60; E.house(g2, x, 0, w, 380 + hash(i + 4) * 100, { seed: 90 + i, mood: 'day' }); x += w + 20; i++; } g2.restore();
    E.stall(g2, 520, 1280, 560, { lw: 5, seed: 2 });
    g2.fillStyle = '#b39b78'; g2.fillRect(0, 1270, W, 700);
  });
  const V = new Wd.View({ cx: 0, cy: 260, cz: 0, f: 1100, hy: 1080 });
  Wd.ground(g, V, { mood: 'day', zNear: 300 });
  const push = 1 + .05 * ease.io(lt / 1.77);
  g.save(); g.translate(W / 2, H * .62); g.scale(push, push); g.translate(-W / 2, -H * .62);
  // the barrel (left-centre) and its lid
  const bx = 380, by = 1560, bs = 2.1;
  const lid = clamp((t - t0 - HIT) / .12);
  // rats leap out in bursts on the toms (3+3+2)
  const toms = C.eventsIn(EV.tom, t0, b(5)).concat([t0 + .02]);
  const flyers = [];
  toms.forEach((tt, k) => { for (let j = 0; j < 6; j++) flyers.push({ t0: tt + j * .028, k, j }); });
  const drawFly = (front) => {
    for (const f of flyers) {
      const dt = t - f.t0 - HIT; if (dt < 0 || dt > 1.2) continue;
      const side = (f.j % 2 ? 1 : -1) * (f.k % 2 ? 1 : .7);
      const vx = side * (260 + hash(f.j * 3 + f.k) * 380), vy = -(900 + hash(f.j + f.k * 7) * 500);
      const x = bx + vx * dt, y = by - 240 + vy * dt + 2600 * dt * dt;
      const ground = by + 60 + hash(f.j + 2) * 120;
      const landed = y > ground;
      const yy = landed ? ground : y;
      const xx = landed ? x + side * (dt - (Math.sqrt(Math.max(0, (vy * vy) + 4 * 2600 * (ground - by + 240))) - vy) / 5200) * 500 : x;
      if ((f.j < 3) !== front) continue;
      RT.ratSide(g, xx, yy, { s: 1.5, dir: side > 0 ? 1 : -1, phase: dt * 5, t, speed: landed ? 1 : .2, tilt: landed ? 0 : -side * clamp(-vy * .0006 - dt * 1.5, -1, 1) * .8, stand: landed ? 0 : .4, shadow: landed });
    }
  };
  drawFly(false);
  E.barrel(g, bx, by, bs, { lid, lw: 6 });
  // merchant: anticipation (hands on the lid), yank on the downbeat, recoil on the first burst
  const recoil = ease.o3(clamp((t - toms[0] - HIT) / .2));
  const pose = tt => {
    const pull = clamp((tt - t0 - HIT) / .12);
    const rc = ease.o3(clamp((tt - toms[0] - HIT) / .2));
    const shake = Math.sin(tt * 38) * .04 * rc;
    let P = R.idle(tt, { seed: 3 });
    P = R.merge(P, {
      yaw: -.75, lean: lerp(.35, -.28, rc) + .1 * (1 - pull) * (tt < t0 ? ease.io(clamp((tt - t0 + .4) / .4)) : 1), bob: lerp(-14, -4, rc),
      arms: rc > .05 ? { l: { swing: 2.2 + shake * 4, out: 1.0, elbow: .35 }, r: { swing: 2.0 - shake * 4, out: 1.1, elbow: .45 } } : { l: { swing: 1.1 + pull * .5, out: .2, elbow: .4 }, r: { swing: 1.0 + pull * .5, out: .25, elbow: .4 } },
      hands: rc > .05 ? { l: 'open', r: 'open' } : {},
      head: { yaw: .1, pitch: lerp(.25, -.2, rc) + shake, roll: shake },
      face: rc > .05 ? { eyes: 'wide', mouth: 'gasp', brow: 'worry', sweat: 1, look: [-.6, .2] } : { eyes: 'open', mouth: 'closed', brow: 'raised', look: [-.7, .6] },
    });
    return P;
  };
  PS.drawPerson(g, CAST.merchant, pose(t), { x: 760 - recoil * 40, y: 1700, s: 2.05, lw: 6, lagA: pose(t - .07), lagB: pose(t - .16), t });
  drawFly(true);
  g.restore();
}

// ---------------------------------------------------------------- 06: baker, a leap onto the table, the cat
function shot06(g, t, lt) {
  const s1 = b(5), s2 = b(5, 3);
  const V = new Wd.View({ cx: lerp(-30, 30, ease.io(lt / 1.77)), cy: 250, cz: 0, f: 1150, hy: 1000 });
  ST.streetBackdrop(g, V, t, 'day', { clouds: CLOUDS, sunX: 160 });
  const items = Wd.streetItems({ mood: 'day', seed: 33, half: 900, z0: 1500 });
  // bakery front (left): big open counter window, baker inside
  items.push({ z: 1250, draw: (g2, V2) => {
    const [sx, sy, s] = V2.p(-430, 0, 1250); const S = s * Wd.HS;
    g2.save(); g2.translate(sx, sy); g2.scale(S, S);
    E.house(g2, -210, 0, 420, 420, { seed: 501, mood: 'day', door: false, lw: V2.lw(s) / S });
    // shop opening
    K.shape(g2, [[-150, -40], [150, -40], [150, -170], [-150, -170]], { fill: '#3a2618', lw: V2.lw(s) / S, smooth: false });
    g2.restore();
    // baker (behind the counter)
    const bp = tt => {
      const rc = ease.o3(clamp((tt - s1 - HIT) / .16));
      return R.merge(R.idle(tt, { seed: 5 }), { yaw: .25, lean: -.25 * rc, bob: -6 * rc,
        arms: rc > .05 ? { l: { swing: 2.3, out: 1.05, elbow: .3 }, r: { swing: 2.1, out: 1.15, elbow: .35 } } : { l: { swing: .9, out: .3, elbow: .9 }, r: { swing: .9, out: .3, elbow: .9 } },
        hands: rc > .05 ? { l: 'open', r: 'open' } : {},
        head: { pitch: -.15 * rc, roll: .1 * Math.sin(tt * 30) * rc },
        face: rc > .05 ? { eyes: 'wide', mouth: 'gasp', brow: 'worry', look: [.3, .5] } : { eyes: 'open', mouth: 'smile', look: [.4, .6] } });
    };
    ST.actor(g2, V2, CAST.baker, -440, 1300, bp, t, { yOff: 40 });
    // counter with loaves and the rats on it
    const [cx, cy, cs] = V2.p(-430, 0, 1180); const S2 = cs * Wd.HS;
    g2.save(); g2.translate(cx, cy); g2.scale(S2, S2);
    K.shape(g2, [[-160, -40], [160, -40], [160, -70], [-160, -70]], { fill: '#8a5a36', lw: V2.lw(cs) / S2, smooth: false });
    K.shape(g2, [[-150, 0], [150, 0], [150, -40], [-150, -40]], { fill: '#6b4428', lw: V2.lw(cs) / S2, smooth: false });
    for (let i = 0; i < 5; i++) E.bread(g2, -110 + i * 55, -82, .55, { lw: V2.lw(cs) / S2 / .55 });
    if (t > s1 - .1) for (let k = 0; k < 4; k++) { const dt = t - s1 + .1 - k * .1; if (dt < 0) continue; const xx = -170 + ((dt * 260 + k * 60) % 340); RT.ratSide(g2, xx, -72, { s: .42, dir: 1, phase: dt * 4 + k, t, speed: 1, shadow: false }); }
    g2.restore();
  } });
  // table + merchant leaping onto it on stab 2
  const TX = 360, TZ = 1250;
  items.push(Wd.propItem(TX, TZ + 20, (g2, s) => { const lw = 4.5 / s; K.shape(g2, [[-230, -170], [230, -170], [230, -195], [-230, -195]], { fill: '#8a5a36', lw, smooth: false }); for (const lx of [-200, 180]) K.shape(g2, [[lx, 0], [lx + 22, 0], [lx + 22, -172], [lx, -172]], { fill: '#6b4428', lw, smooth: false }); E.bread(g2, 120, -210, .9, { lw: lw / .9 }); }));
  const jumpT = s2 + HIT;
  const jp = tt => {
    const u = clamp((tt - jumpT) / .28);
    const crouch = tt < jumpT ? ease.io(clamp((tt - jumpT + .25) / .25)) : 0;
    const land = clamp((tt - jumpT - .28) / .25);
    let P = tt > jumpT + .28 ? R.jig(C.beatPhase(tt) , C.beatIndex(tt), { amt: .7, handsUp: true }) : R.idle(tt, { seed: 9 });
    P = R.merge(P, { yaw: -.5, bob: -crouch * 40 - (u > 0 && u < 1 ? -20 : 0) - Math.exp(-land * 8) * 25 * (land > 0 ? 1 : 0),
      face: { eyes: 'wide', mouth: u > 0 ? 'gasp' : 'o', brow: 'worry', look: [-.8, .7] } });
    if (u > 0 && u < 1) P = R.merge(P, { legs: { l: [24, 60, 10], r: [-24, 70, -6] }, arms: { l: { swing: 2.2, out: 1.1, elbow: .3 }, r: { swing: 2.2, out: 1.1, elbow: .3 } } });
    return P;
  };
  const jy = tt => { const u = clamp((tt - jumpT) / .28); return tt < jumpT ? 0 : u < 1 ? 195 * ease.o(u) + Math.sin(Math.PI * u) * 90 : 195; };
  items.push({ z: TZ - 30, draw: (g2, V2) => ST.actor(g2, V2, CAST.townsfolk(42), TX + 60, TZ - 30, jp, t, { yOff: jy(t) }) });
  // swarm flowing right -> left through the foreground
  for (let i = 0; i < 70; i++) {
    const te = s1 - .3 + hash(i * 2.3) * .9;
    if (t < te) continue;
    const z = 700 + hash(i * 5.1) * 800, sp = 650 + hash(i) * 250;
    const x = 1500 - (t - te) * sp;
    items.push({ z, draw: (g2, V2) => ST.ratAt(g2, V2, x, z, { dir: -1, phase: (t - te) * sp / 120, t, size: 1.05 }) });
  }
  // the cat backs away from the swarm, arching and hissing
  const ca = ease.o3(clamp((t - s1 - .25) / .3));
  const catX = 40 - Math.max(0, t - s1 - .2) * 140;
  items.push({ z: 640, draw: (g2, V2) => { const [sx, sy, s] = V2.p(catX, 0, 640); CR.cat(g2, sx, sy, { s: s * 1.5, dir: 1, arch: ca, phase: (t - s1) * 1.6, t, lw: V2.lw(s) }); } });
  Wd.drawItems(g, V, items);
}

module.exports = [
  { id: '03_drain', t0: b(2), mood: 'day', draw: shot03, flashIn: true },
  { id: '04_rooftops_sacks', t0: b(3), mood: 'day', draw: shot04 },
  { id: '05_barrel', t0: b(4), mood: 'day', draw: shot05 },
  { id: '06_baker_table_cat', t0: b(5), mood: 'day', draw: shot06 },
];
