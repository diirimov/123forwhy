// 43-48 THE DISAPPEARANCE + AFTERMATH (bars 32-37). The passage swallows the children group by group on the
// stutter stabs; the last child looks back; the Piper steps in; the rock seals in the silence. Then: the
// mountain with nothing but footprints, a shoe and a falling feather; the empty bed; parents in empty
// doorways at dawn; the opening street, deserted; the wooden horse rolls by itself toward the fog where, for
// a moment, he is still playing -- and the last frame is the first frame without the children (the loop).
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
const CH = require('../chor');
const HOOK = require('./v_a_hook').helpers;
const { barT: b, clamp, lerp, ease, BEAT, BAR, S16, HIT, W, H, TAU, hash } = C;
const { PAL } = K;
const SEAL = C.BM.gaps[4];      // 56.029
const KID = i => CAST.child(700 + i);

// ---------------------------------------------------------------- 43: the passage -- four stabs, four groups gone; the last child looks back
function shot43(g, t, lt) {
  const t0 = b(31);
  const stabs = [0, 3, 6, 10].map(s => b(31, s) + HIT);
  const close = ease.io(clamp((t - SEAL) / .25));
  const gr = g.createLinearGradient(0, 0, 0, H); gr.addColorStop(0, '#10152a'); gr.addColorStop(1, '#2a3150'); g.fillStyle = gr; g.fillRect(0, 0, W, H);
  E.sky(g, 'night', W, 1100, t); E.moon(g, 880, 240, 85);
  const push = 1 + .1 * ease.io(lt / 1.77);
  g.save(); g.translate(W / 2, 1250); g.scale(push, push); g.translate(-W / 2, -1250);
  // the mountain wall, huge, with the glowing cleft
  K.shape(g, [[-100, 1400], [-100, 500], [200, 300], [520, 180], [820, 260], [1180, 420], [1180, 1400]], { fill: '#2b3352', lw: 6, tension: .35 });
  K.shape(g, [[700, 300], [1180, 460], [1180, 1400], [760, 1400], [640, 900]], { fill: '#222842', lw: 0, tension: .35, alpha: .7 });
  const op = 1 - close;
  if (op > .01) {
    const pw = 210 * op;
    K.shape(g, [[540 - pw, 1400], [540 - pw * .9, 1100], [540 - pw * .4, 900], [540 + pw * .35, 910], [540 + pw * .9, 1120], [540 + pw, 1400]], { fill: '#dfe6ff', lw: 6, tension: .4 });
    const fl = Math.max(0, ...stabs.map(s => C.decay(t - s, 6) * (t > s ? 1 : 0)));
    K.glow(g, 540, 1180, 420 + 260 * fl, '#c8d6ff', (.45 + .5 * fl) * op, 'source-over');
    E.addLight(g, 540, 1180, 700 + 400 * fl, '#bfd0ff', (.6 + .5 * fl) * op);
  } else K.shape(g, [[400, 1400], [430, 1120], [520, 960], [640, 1110], [680, 1400]], { fill: '#262d4a', lw: 6, tension: .4 });
  // ground
  K.shape(g, [[-100, 1400], [1180, 1400], [1180, H + 100], [-100, H + 100]], { fill: '#1b2036', lw: 6, smooth: false });
  // four groups queued toward the light; each vanishes on its stab (a step into the glow and gone)
  const groups = [[0, [[500, 1420], [570, 1430], [450, 1440], [610, 1445]]], [1, [[380, 1500], [460, 1520], [540, 1510], [620, 1530]]],
    [2, [[300, 1610], [400, 1640], [500, 1620], [600, 1650], [700, 1630]]], [3, [[420, 1780], [560, 1800], [690, 1790]]]];
  for (const [gi, members] of groups) {
    const gone = ease.o(clamp((t - stabs[gi]) / .16));
    members.forEach(([x, y], k) => {
      if (gone >= 1) return;
      const ch = KID(gi * 6 + k);
      const last = gi === 3 && k === 1;
      const look = last ? ease.back(clamp((t - b(31, 8)) / .15)) * (1 - gone) : 0;
      const s = .55 + (y - 1400) / 520;
      const P = R.merge(CH.procWalk(ch.B, { yaw: Math.PI, t0, idx: k, stride: 20 })(t), { head: { yaw: Math.PI * .92 * look, pitch: .05, roll: 0 },
        face: { eyes: look > .5 ? 'open' : 'half', mouth: 'peace', glint: 2, pupil: .6, look: [0, 0] } });
      g.save(); g.globalAlpha = 1 - gone;
      PS.drawPerson(g, ch, P, { x: x + (540 - x) * gone * .5, y: y - gone * 60, s: s * (1 - gone * .3), sil: last && look > .3 ? null : '#0a0c16', lw: 3, t, shadow: false });
      g.restore();
    });
  }
  // the Piper: last, at the mouth; turns his head to us, then steps in as the silence falls
  const inside = ease.io(clamp((t - SEAL + .3) / .3));
  if (inside < 1) {
    const P = R.merge(PP.playPose(t, { eyes: 'narrow', glow: 1 }), { yaw: Math.PI - .5 * (1 - inside) });
    g.save(); g.globalAlpha = 1 - inside;
    PS.drawPerson(g, CAST.piper, P, { x: 560 - 40 * inside, y: 1410, s: .78, sil: '#06070d', lw: 3, t, wind: .6, shadow: false });
    g.restore();
  }
  g.restore();
}

// ---------------------------------------------------------------- 44: the sealed mountain -- footprints into solid rock, one small shoe, a falling feather
function shot44(g, t, lt) {
  const t0 = b(32);
  const gr = g.createLinearGradient(0, 0, 0, H); gr.addColorStop(0, '#0f1328'); gr.addColorStop(1, '#262c48'); g.fillStyle = gr; g.fillRect(0, 0, W, H);
  E.sky(g, 'night', W, 1000, t); E.moon(g, 260, 300, 100);
  const push = 1 + .08 * ease.io(lt / 1.77);
  g.save(); g.translate(W / 2, 1300); g.scale(push, push); g.translate(-W / 2, -1300);
  K.shape(g, [[-100, 1300], [-100, 560], [260, 380], [560, 300], [860, 380], [1180, 520], [1180, 1300]], { fill: '#2b3352', lw: 6, tension: .35 });
  K.shape(g, [[400, 1300], [430, 1040], [520, 900], [640, 1030], [680, 1300]], { fill: '#262d4a', lw: 5, tension: .4 });       // the scar of the cleft
  K.shape(g, [[-100, 1300], [1180, 1300], [1180, H + 100], [-100, H + 100]], { fill: '#1b2036', lw: 6, smooth: false });
  // footprints converging on the rock
  for (let i = 0; i < 40; i++) { const u = i / 40, lane = (i % 5) - 2; const x = 540 + lane * (40 + 200 * u) + (i % 2 ? 12 : -12), y = 1310 + u * u * 560; K.ellipse(g, x, y, 10 + 14 * u, 5 + 7 * u, { fill: '#121628', lw: 0, alpha: .8 }); }
  // the shoe
  K.shape(g, [[470, 1700], [600, 1690], [640, 1660], [610, 1640], [520, 1650], [480, 1670]], { fill: '#8a3a2a', lw: 5, tension: .4 });
  // a feather from his hat drifting down
  const u = clamp((t - t0) / 1.76);
  const fx = 700 - 180 * u + Math.sin(u * 9) * 60, fy = 300 + 1300 * ease.o(u);
  g.save(); g.translate(fx, fy); g.rotate(-.6 + Math.sin(u * 9) * .5); K.shape(g, [[0, 0], [16, -60], [6, -130], [-8, -60]], { fill: '#efe6d2', lw: 4, tension: .5 }); K.line(g, [[0, 0], [4, -120]], 2, '#8a8070', 1, false); g.restore();
  g.restore();
  E.fog(g, 1200, 460, t, { col: '#9fb0d8', a: .4, speed: 10 });
}

// ---------------------------------------------------------------- 45: the empty bed (the legend card)
function shot45(g, t, lt) {
  const t0 = b(33);
  const push = 1 + .06 * ease.io(lt / 1.77);
  g.save(); g.translate(W / 2, H * .6); g.scale(push, push); g.translate(-W / 2, -H * .6);
  IN.bedroom(g, t, { empty: 1, winX: 150, bedX: 560 });
  const open = ease.io(clamp((t - t0) / .5));
  K.shape(g, [[880, 1250], [1060, 1250], [1060, 760], [880, 760]], { fill: open > .2 ? '#e6a860' : '#5e3d27', lw: 6, smooth: false });
  const mp = tt => {
    const u = ease.o3(clamp((tt - b(33, 4) - HIT) / .3));
    const walkIn = clamp((tt - t0 - .2) / .8);
    const P = walkIn < 1 ? R.walk(ST.stridePh(tt, t0), { stride: 60, bob: 4, arm: .2 }) : R.idle(tt, { seed: 4 });
    return R.merge(P, { yaw: -.9, lean: .05 * u, head: { pitch: .15 * u, yaw: .1, roll: -.05 * u },
      arms: { l: { swing: lerp(1.3, 2.0, u), out: .1, elbow: lerp(1.2, 2.2, u) }, r: { swing: 1.15, out: .15, elbow: 1.0 } }, hands: { l: u > .5 ? 'open' : 'mitten' },
      face: { eyes: u > .3 ? 'wide' : 'open', mouth: u > .3 ? 'gasp' : 'closed', brow: 'worry', look: [-.8, .4], tear: u > .7 ? ((tt - b(33, 4) - .7) * .8) % 1 : 0 } });
  };
  const mx = lerp(1080, 900, ease.io(clamp((t - t0 - .2) / .8)));
  const J = PS.drawPerson(g, CAST.mother, mp(t), { x: mx, y: 1640, s: 2.0, lw: 6.5, lagA: mp(t - .07), lagB: mp(t - .16), t });
  const hand = R.proj(J, J.wrr); const cx = mx + hand[0] * 2.0, cy = 1640 + hand[1] * 2.0;
  K.shape(g, [[cx - 9, cy - 4], [cx + 9, cy - 4], [cx + 9, cy - 64], [cx - 9, cy - 64]], { fill: '#efe6d2', lw: 4, smooth: false });
  K.shape(g, [[cx, cy - 104 + Math.sin(t * 13) * 4], [cx + 8, cy - 76], [cx, cy - 64], [cx - 8, cy - 76]], { fill: '#f6c24a', lw: 3 });
  E.addLight(g, cx, cy - 80, 900, '#f3a64a', .85); E.addLight(g, cx, cy - 80, 160, '#ffe7a8', .9); E.addLight(g, 970, 1000, 700, '#e6a050', .5);
  // the wooden horse on the floor where it fell
  E.toyHorse(g, 380, 1700, 1.6, { lw: 6, rock: 0 });
  g.restore();
}

// ---------------------------------------------------------------- 46: dawn -- parents in every doorway; heads turn toward the mountain on the heartbeat
function shot46(g, t, lt) {
  const t0 = b(34);
  const V = new Wd.View({ cx: lerp(-40, 40, ease.io(lt / 1.77)), cy: 250, cz: lerp(640, 780, ease.io(lt / 1.77)), f: 1150, hy: 980 });
  ST.streetBackdrop(g, V, t, 'dusk', { sun: false, moon: false });
  const items = [];
  DP.wall(items, 4100, 11, { sp: 620, seed: 261, mood: 'dusk' });
  const homes = [-930, -310, 310, 930];
  const parents = [[CAST.father, 0], [CAST.mother, 0], [CAST.townsfolk(201), 8], [CAST.woman, 4]];
  homes.forEach((x, i) => {
    items.push(Wd.houseItem(x, 1750, 255, 440, { seed: 280 + i, mood: 'dusk', doorOpen: 1, doorX: .5 }));
    const [ch, s] = parents[i];
    const turnT = b(34, s) + HIT;
    items.push({ z: 1700, draw: (g2, V2) => ST.actor(g2, V2, ch, x, 1700, tt => {
      const u = ease.io(clamp((tt - turnT) / .8));
      return R.merge(R.idle(tt, { seed: i + 3 }), { yaw: lerp(0, i < 2 ? -.6 : .6, u), head: { yaw: lerp(0, i < 2 ? -.5 : .5, u), pitch: .1 },
        arms: i === 1 ? { l: { swing: 1.4, out: .2, elbow: 1.9 }, r: { swing: 1.3, out: .2, elbow: 1.9 } } : undefined,
        face: { eyes: 'open', mouth: 'flat', brow: 'worry', look: [i < 2 ? -.6 : .6, 0], tear: i === 1 ? ((tt - t0) * .6) % 1 : 0 } });
    }, t) });
  });
  // toys left on the doorsteps
  items.push(Wd.propItem(-300, 1450, (g2, s) => E.toyHorse(g2, 0, 0, 1.2, { lw: 5 / s })));
  items.push(Wd.propItem(330, 1400, (g2, s) => E.doll(g2, 0, 0, 1.4, { lw: 5 / s, rot: -1.4 })));
  items.push(Wd.propItem(900, 1500, (g2, s) => E.spinTop(g2, 0, 0, 1.3, { lw: 5 / s, tilt: .9 })));
  Wd.drawItems(g, V, items);
  E.fog(g, 1150, 500, t, { col: '#d8c8d8', a: .35, speed: 12 });
}

// ---------------------------------------------------------------- 47-48: the opening street, deserted; the horse rolls toward the fog; the loop
function emptyStreet(g, t, cam, o = {}) {
  const { V, items } = HOOK.nightTown(g, t, { cam });
  items.push(Wd.propItem(-1150, 1150, (g2, s) => E.torch(g2, 0, -700, { t, s: 2.4, lw: 4 / s })));
  if (o.toyZ) items.push(Wd.propItem(o.toyX ?? 120, o.toyZ, (g2, s) => E.toyHorse(g2, 0, 0, 1.3, { lw: 5 / s, rock: o.rock || 0 })));
  if (o.piperA > 0) items.push({ z: 2100, draw: (g2, V2) => {
    const [sx, sy, s] = V2.p(-120, 0, 2100);
    g2.save(); g2.globalAlpha = o.piperA;
    PS.drawPerson(g2, CAST.piper, R.merge(PP.playPose(t), { yaw: .1 }), { x: sx, y: sy, s, sil: '#151a2c', lw: 2.5, t, wind: .4, shadow: false });
    g2.restore();
    E.addLight(g2, sx, sy - 420 * s, 320, '#9fb4e6', .5 * o.piperA);
  } });
  DP.flush(g, V, items);
  E.fog(g, 1020, 480, t, { col: '#aab9de', a: .45, speed: 22 });
  E.fog(g, 1330, 420, t, { col: '#9fb0d8', a: .25, speed: -14, off: 400 });
}
function shot47(g, t, lt) {
  const u = ease.io(lt / 1.77);
  emptyStreet(g, t, { ...HOOK.OPEN_CAM, cz: lerp(-260, -160, u), cx: lerp(40, 20, u) }, { toyZ: 760, toyX: 140 });
}
function shot48(g, t, lt) {
  const t0 = b(36);
  const gig = C.FL.filter(n => n.t >= t0 - .01).map(n => n.t);
  // the horse rolls a little on each giggle note, pulled toward the fog; he appears, then dissolves
  const roll = gig.slice(0, 3).reduce((a, nt) => a + 60 * ease.io(clamp((t - nt) / .2)), 0);
  const pa = ease.io(clamp((t - t0) / .25)) * (1 - ease.io(clamp((t - t0 - 1.0) / .5)));
  const u = ease.io(clamp(lt / 1.5));
  const toyGone = ease.io(clamp((lt - 1.15) / .45));
  emptyStreet(g, t, { ...HOOK.OPEN_CAM, cz: lerp(-160, 0, u), cx: lerp(20, 0, u) }, { toyZ: toyGone < 1 ? 760 + roll * 3 : 0, toyX: 140 - roll * .3, piperA: pa * .9 });
  if (toyGone > 0 && toyGone < 1) { /* the horse fades into the fog with him */ }
}

module.exports = [
  { id: '43_passage_swallows', t0: b(31), mood: 'night', draw: shot43, flashIn: true, finish: (t) => ({ fade: t > SEAL ? .35 * ease.io(clamp((t - SEAL) / .3)) : 0 }) },
  { id: '44_sealed_mountain', t0: b(32), mood: 'night', draw: shot44 },
  { id: '45_empty_bed', t0: b(33), mood: 'night', draw: shot45 },
  { id: '46_parents_doorways', t0: b(34), mood: 'dusk', grade: () => ({ mood: 'cold', amt: .8 }), draw: shot46 },
  { id: '47_deserted_street', t0: b(35), mood: 'night', draw: shot47, finish: () => ({ vig: .72 }) },
  { id: '48_loop', t0: b(36), mood: 'night', draw: shot48, finish: () => ({ vig: .72 }) },
];
