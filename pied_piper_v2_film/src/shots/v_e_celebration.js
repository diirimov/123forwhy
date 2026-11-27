// 25-30 CELEBRATION + BETRAYAL (bars 18-22). The whole town in the DP dance (squats, jigs, spins, stomps,
// claps on every beat in bar 19); the Piper walks through them to the officials; the chest SLAMS on the
// betrayal downbeat; the town keeps dancing (now half-time) around his total stillness; his smile dies.
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
const DP = require('../dp');
const CH = require('../chor');
const SETS = require('../sets');
const { barT: b, clamp, lerp, ease, BEAT, BAR, S16, HIT, W, H, TAU, hash } = C;
const { PAL } = K;
const PB = CAST.piper.B;
const SLAM = b(19) + HIT;
const MOVES = ['squat', 'jig', 'squat', 'spin', 'stomp', 'squat', 'clap', 'jig'];
const joy = { eyes: 'narrow', mouth: 'laugh', brow: 'raised' };

function bunting(g, t) { for (let i = 0; i < 3; i++) { const y = 260 + i * 170; E.bunting(g, -40, y, W + 40, y + 50, 100, t); } }

// the dancing crowd: rows x cols, each with its own move; `half` = the betrayal's half-time
function crowd(items, t, o = {}) {
  const rows = o.rows || [[760, 4, 380], [1100, 5, 330], [1500, 6, 300], [1950, 7, 290]];
  rows.forEach(([z, n, sp], r) => {
    for (let i = 0; i < n; i++) {
      const id = r * 10 + i;
      if (o.skip && o.skip(r, i)) continue;
      const ch = r === 0 && i === 1 ? CAST.woman : r === 0 && i === 2 ? CAST.baker : CAST.townsfolk(120 + id);
      const x = (i - (n - 1) / 2) * sp + (r % 2) * sp * .5 + (hash(id) - .5) * 60 + (o.dx || 0);
      const kind = o.half ? (id % 3 ? 'half' : 'sway') : o.clap && r < 2 ? 'clap' : MOVES[(id * 3 + r) % MOVES.length];
      const burst = o.burst != null ? o.burst + r * S16 : null;
      DP.actorAt(items, ch, x, z, tt => {
        let P = CH.dance(kind, tt, { B: ch.B, amt: .95, delay: r * S16 * .5, yaw: (x > 0 ? -.2 : .2) + Math.sin(tt * .8 + id) * .05, dir: id % 2 ? 1 : -1,
          face: o.half ? { eyes: 'narrow', mouth: 'grin', brow: 'raised', look: [0, 0], glint: .3 } : joy, handsUp: id % 2 === 0 });
        if (burst != null && tt < burst + .35) {          // spring up from a crouch on the downbeat
          const u = clamp((tt - burst) / .35);
          P = R.merge(P, { bob: tt < burst ? -60 : -60 + 110 * Math.sin(Math.PI * u) + 60 * u, knees: { l: 1, r: 1 },
            arms: { l: { swing: 2.7, out: .9, elbow: .2 }, r: { swing: 2.7, out: .9, elbow: .2 } }, hands: { l: 'open', r: 'open' } });
        }
        return P;
      }, t);
    }
  });
}

// ---------------------------------------------------------------- 25: the town bursts into the DP dance
function shot25(g, t, lt) {
  const t0 = b(17);
  const u = ease.io(lt / 1.77);
  const { V, items } = DP.town(g, t, { mood: 'day', cam: { cx: lerp(-60, 60, u), cz: lerp(-40, 60, u) }, sunX: 840, clouds: [[220, 300, 1.1]], seed: 91 });
  crowd(items, t, { burst: t0 + HIT });
  bunting(g, t);
  DP.flush(g, V, items);
  // confetti of grain / petals thrown on the beats
  for (let i = 0; i < 40; i++) { const tb = t0 + (i % 4) * BEAT; const dt = t - tb; if (dt < 0) continue; const x = hash(i) * W + Math.sin(dt * 3 + i) * 40, y = 300 + dt * 420 + hash(i * 3) * 400; if (y < 1700) K.ellipse(g, x, y, 9, 5, { fill: ['#c94a3a', '#e8c25a', '#f0e6d0', '#5a7aa8'][i % 4], lw: 2 }, dt * 5 + i); }
}

// ---------------------------------------------------------------- 26: closer -- spins, stomps, and claps on every beat
function shot26(g, t, lt) {
  const { V, items } = DP.town(g, t, { mood: 'day', cam: { cz: 180 + lt * 60, cy: 210 }, sunX: 200, seed: 93 });
  crowd(items, t, { clap: true, rows: [[640, 3, 420], [980, 4, 360], [1400, 6, 300]] });
  bunting(g, t);
  DP.flush(g, V, items);
}

// ---------------------------------------------------------------- 27: he walks through the dancers to the officials, hand held out
function shot27(g, t, lt) {
  const t0 = b(18, 8);
  const { V, items } = DP.town(g, t, { mood: 'day', cam: { cx: 80, cz: lerp(0, 80, ease.io(lt / .88)), cy: 230 }, sunX: 860, seed: 95, zNear: 3100 });
  // town-hall steps with the table, the mayor and the chest (open)
  items.push(Wd.propItem(0, 2300, (g2, s) => { const lw = 4.5 / s; K.shape(g2, [[-800, 0], [800, 0], [760, -70], [-760, -70]], { fill: '#b9a684', lw, smooth: false }); K.shape(g2, [[-720, -70], [720, -70], [680, -140], [-680, -140]], { fill: '#c7b493', lw, smooth: false }); }));
  DP.actorAt(items, CAST.mayor, 140, 2250, tt => R.merge(R.idle(tt, { seed: 42 }), { yaw: -.1, face: { eyes: 'narrow', mouth: 'grin', brow: 'raised', look: [-.2, .2] } }), t);
  items.push(Wd.propItem(160, 2150, (g2, s) => { const lw = 4.5 / s; K.shape(g2, [[-260, 0], [260, 0], [260, -180], [-260, -180]], { fill: '#2f5a3c', lw, smooth: false }); E.chest(g2, 0, -180, 1.3, { lid: .9, lw: lw }); }));
  crowd(items, t, { rows: [[900, 3, 520], [1350, 4, 420], [1800, 5, 360]], skip: (r, i) => r === 0 && i === 1, dx: -40 });
  // the Piper (foreground right, back three-quarter), walking in, the open palm rising
  DP.actorAt(items, CAST.piper, 330, lerp(640, 820, ease.io(clamp(lt / .88))), tt => {
    const reach = ease.io(clamp((tt - t0 - .25) / .4));
    const Wk = R.walk(ST.stridePh(tt, t0), { B: PB, stride: 90, bob: 2.4, arm: .12 });
    return R.merge(Wk, { yaw: Math.PI - .25, arms: { r: { swing: lerp(.1, 1.3, reach), out: .1, elbow: .2 } }, hands: { r: reach > .4 ? 'open' : 'mitten' }, head: { yaw: .1 } });
  }, t, { wind: .2 });
  bunting(g, t);
  DP.flush(g, V, items);
}

// ---------------------------------------------------------------- 28: SLAM -- the chest shuts on the downbeat; the mayor wags "no" on each half-time beat
function shot28(g, t, lt) {
  const t0 = b(19);
  PO.blurred(g, 9, (g2) => { const tw = DP.town(g2, t, { mood: 'day', sunX: 860, seed: 91, cam: { cy: 260 } }); crowd(tw.items, t, { half: true, rows: [[1200, 5, 330], [1700, 6, 300]] }); DP.flush(g2, tw.V, tw.items); });
  E.LIGHTS.length = 0;
  const shake = C.springHit(t - SLAM, 9, 10) * 14;
  g.save(); g.translate(0, shake);
  const mp = tt => {
    const s = ease.o3(clamp((tt - SLAM + .22) / .22));
    const wag = tt > SLAM + .3 ? Math.sin(TAU * (tt - SLAM - .3) / (2 * BEAT)) : 0;
    return R.merge(R.idle(tt, { seed: 42 }), { yaw: -.3, lean: .3 * s - .05 * Math.abs(wag),
      arms: { l: { swing: lerp(.5, 1.25, s), out: .1, elbow: lerp(.5, .1, s) }, r: tt > SLAM + .3 ? { swing: 2.0, out: .3 + .3 * wag, elbow: 1.6 } : { swing: lerp(.5, 1.2, s), out: .1, elbow: lerp(.5, .1, s) } },
      hands: { r: tt > SLAM + .3 ? 'point' : 'mitten' }, head: { pitch: .08 * s, yaw: .15 + .12 * wag },
      face: tt < SLAM ? { eyes: 'narrow', mouth: 'sly', brow: 'raised', look: [-.6, .2] } : { eyes: 'narrow', mouth: 'frown', brow: 'angry', look: [-.7, 0] } });
  };
  PS.drawPerson(g, CAST.mayor, mp(t), { x: 720, y: 1620, s: 1.9, lw: 6.5, lagA: mp(t - .07), lagB: mp(t - .16), t });
  K.shape(g, [[60, 1400], [W, 1400], [W + 40, 1700], [20, 1700]], { fill: '#2f5a3c', lw: 7, smooth: false });
  K.shape(g, [[20, 1700], [W + 40, 1700], [W + 40, H + 40], [20, H + 40]], { fill: '#244731', lw: 7, smooth: false });
  const lidAng = t < SLAM - .09 ? .95 : t < SLAM ? lerp(.95, 0, ease.i((t - SLAM + .09) / .09)) : 0;
  E.chest(g, 560, 1420, 2.1, { lid: lidAng, lw: 7 });
  if (t > SLAM) for (let i = 0; i < 9; i++) { const dt = t - SLAM; const x = 560 + (i - 4) * 70 + dt * (i - 4) * 300, y = 1240 - 420 * dt + 2000 * dt * dt; if (y < 1420) K.ellipse(g, x, y, 15, 9, { fill: PAL.gold, lw: 3 }, dt * 9 + i); }
  // dust puff on the slam
  if (t > SLAM && t < SLAM + .5) { const u = (t - SLAM) / .5; for (let i = 0; i < 8; i++) K.ellipse(g, 560 + (i - 3.5) * 60 * (1 + u * 2), 1420 - 20 * u, 30 * (1 + u), 14 * (1 + u), { fill: '#e8dcc0', lw: 0, alpha: .5 * (1 - u) }); }
  // the Piper's hand in the foreground, still out -- it does not move
  const pp = tt => R.merge(R.idle(tt * .1, { B: PB, shift: 0 }), { yaw: 1.2, arms: { r: { swing: 1.3, out: .05, elbow: .15 }, l: { swing: .1, out: .05, elbow: .3 } }, hands: { r: 'open' }, head: { yaw: -.1 },
    face: tt < SLAM ? { eyes: 'open', mouth: 'sly', brow: 'sly', look: [.8, 0] } : { eyes: 'open', mouth: 'flat', brow: 'neutral', look: [.9, 0], glint: .4 } });
  PS.drawPerson(g, CAST.piper, pp(t), { x: 60, y: 2300, s: 2.6, lw: 7, t, wind: .1 });
  g.restore();
}

// ---------------------------------------------------------------- 29: stillness -- the town dances on (half-time) around the motionless Piper
function shot29(g, t, lt) {
  const u = ease.io(lt / 1.77);
  const { V, items } = DP.town(g, t, { mood: 'day', cam: { cz: lerp(0, 220, u), cy: 210 }, sunX: 860, seed: 91 });
  crowd(items, t, { half: true, skip: (r, i) => r === 0 && (i === 1 || i === 2) });
  // officials laughing silently on the steps at the back
  for (const [x, ch, sd] of [[-300, CAST.mayor, 1], [0, CAST.councillor, 2], [280, CAST.clerk, 3]]) DP.actorAt(items, ch, x, 2350, tt => {
    const e8 = Math.abs(Math.sin(TAU * tt / (BEAT / 2)));
    return R.merge(R.idle(tt, { seed: sd }), { bob: -e8 * 5, lean: -.15, head: { pitch: -.25 - .06 * e8 }, arms: { l: { swing: .6, out: .3, elbow: 1.5 }, r: { swing: .7, out: .3, elbow: 1.4 } }, face: { eyes: 'closed', mouth: 'laugh', brow: 'raised' } });
  }, t);
  // the Piper: dead centre, perfectly still, staring at us
  DP.actorAt(items, CAST.piper, 0, 700, tt => R.merge(R.idle(0, { B: PB, shift: 0 }), { yaw: 0, bob: -2, arms: { l: { swing: .05, out: .06, elbow: .2 }, r: { swing: .05, out: .06, elbow: .2 } },
    head: { pitch: .08, yaw: 0, roll: 0 }, face: { eyes: 'narrow', mouth: 'flat', brow: 'angry', look: [0, 0], glint: 1.6, glow: .25 * u } }), t, { wind: 0 });
  bunting(g, t);
  DP.flush(g, V, items);
}

// ---------------------------------------------------------------- 30: his smile dies; the day drains into night across his face (C# hang)
function shot30(g, t, lt) {
  const t0 = b(21);
  const u = ease.io(clamp(lt / 1.6)), night = ease.io(clamp((t - b(21, 6)) / (b(22) - b(21, 6))));
  E.sky(g, 'day', W, H, t);
  g.save(); g.globalAlpha = night; E.sky(g, 'night', W, H, t); g.restore();
  E.sun(g, 860, lerp(260, 1400, u), 70, t);
  if (night > .2) { g.save(); g.globalAlpha = clamp((night - .2) / .6); E.moon(g, 230, lerp(900, 330, night), 110); g.restore(); }
  PO.blurred(g, 10, (g2) => { g2.save(); g2.translate(0, 1350); let x = -50; for (let i = 0; i < 7; i++) { E.house(g2, x, 0, 200, 430, { seed: 120 + i, mood: night > .5 ? 'night' : 'day', lit: .8 * night, litAlways: true }); x += 220; } g2.restore(); g2.fillStyle = night > .5 ? '#3a3e52' : '#9c8463'; g2.fillRect(0, 1350, W, 700); });
  E.LIGHTS.length = 0;
  const hang = b(21, 8);
  const turn = ease.io(clamp((t - hang) / .4));
  const push = 1 + .12 * ease.io(lt / 1.77);
  g.save(); g.translate(W / 2, H * .42); g.scale(push, push); g.translate(-W / 2, -H * .42);
  const P = R.merge(R.idle(t * .2, { B: PB, shift: .02 }), { yaw: lerp(.45, .05, turn), head: { yaw: lerp(-.3, 0, turn), pitch: .14 + .06 * u },
    arms: { r: { swing: lerp(1.1, .1, u), out: .05, elbow: lerp(.2, .4, u) }, l: { swing: .1, out: .05, elbow: .3 } }, hands: { r: u < .6 ? 'open' : 'fist' },
    face: { eyes: u > .45 ? 'narrow' : 'open', mouth: u < .3 ? 'sly' : u < .6 ? 'closed' : 'flat', brow: u > .45 ? 'angry' : 'sly', look: [0, .05], glint: lerp(1, .5, u), glow: .9 * turn, pupil: .55 } });
  PS.drawPerson(g, CAST.piper, P, { x: 560, y: 2950, s: 4.4, lw: 8, t, wind: .2 + .6 * night, shadow: false });
  g.restore();
}

module.exports = [
  { id: '25_celebration_burst', t0: b(17), mood: 'day', draw: shot25, flashIn: true },
  { id: '26_spins_and_claps', t0: b(18), mood: 'day', draw: shot26 },
  { id: '27_to_the_officials', t0: b(18, 8), mood: 'day', draw: shot27 },
  { id: '28_chest_slam', t0: b(19), mood: 'warm', draw: shot28 },
  { id: '29_stillness', t0: b(20), mood: 'day', draw: shot29, grade: (t, lt) => ({ mood: 'day', mood2: 'cold', mix: .35 * ease.io(clamp(lt / 1.77)) }) },
  { id: '30_smile_dies', t0: b(21), draw: shot30, grade: (t, lt) => ({ mood: 'warm', mood2: 'night', mix: ease.io(clamp(lt / 1.7)) }) },
];
module.exports.helpers = { crowd, bunting };
