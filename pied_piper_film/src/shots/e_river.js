// 15-18: the river Weser (dusk) -- the rats follow him into the water; the town celebrates
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
const { barT: b, clamp, lerp, ease, BEAT, BAR, S16, HIT, W, H, TAU, hash, EV } = C;
const { PAL } = K;

function duskSky(g, t, o = {}) {
  const gr = g.createLinearGradient(0, 0, 0, o.horizon || 1150);
  gr.addColorStop(0, '#2e2440'); gr.addColorStop(.45, '#6b4560'); gr.addColorStop(.8, '#c57a5a'); gr.addColorStop(1, '#eaa76a');
  g.fillStyle = gr; g.fillRect(0, 0, W, (o.horizon || 1150) + 10);
  // low sun
  const sx = o.sunX ?? 720, sy = o.sunY ?? (o.horizon || 1150) - 120;
  K.glow(g, sx, sy, 420, '#f6b26b', .5, 'source-over');
  K.ellipse(g, sx, sy, 110, 110, { fill: '#f3c27a', lw: 4 });
  E.addLight(g, sx, sy, 520, '#ffb070', .45);
}
function hills(g, y, col, amp, seed, lw = 4) {
  const P = [[-50, y + 400]]; for (let x = -50; x <= W + 50; x += 60) P.push([x, y - amp * (.5 + .5 * C.noise(x * .004 + seed))]); P.push([W + 50, y + 400]);
  K.shape(g, P, { fill: col, lw, tension: .5 });
}
function hamelinSilhouette(g, x, y, s, col) { // the town on the far bank, spires against the sky
  g.save(); g.translate(x, y); g.scale(s, s);
  const P = [[0, 0]]; let xx = 0; let i = 0;
  while (xx < 700) { const w = 50 + hash(i * 3) * 50, h = 60 + hash(i * 5) * 70; P.push([xx, -h * .6], [xx + w / 2, -h], [xx + w, -h * .6]); xx += w; i++; }
  P.push([700, 0]);
  K.shape(g, P, { fill: col, lw: 3 / s, smooth: false });
  for (const sx of [260, 330]) K.shape(g, [[sx - 18, -100], [sx - 18, -200], [sx, -310], [sx + 18, -200], [sx + 18, -100]], { fill: col, lw: 3 / s, smooth: false });
  g.restore();
}
function water(g, y0, y1, t, o = {}) {
  const gr = g.createLinearGradient(0, y0, 0, y1); gr.addColorStop(0, o.top || '#b57a6a'); gr.addColorStop(.3, '#6a4a62'); gr.addColorStop(1, '#2c2640');
  g.fillStyle = gr; g.fillRect(0, y0, W, y1 - y0);
  // sun reflection streaks
  g.save(); g.lineCap = 'round';
  for (let i = 0; i < 46; i++) {
    const yy = y0 + 8 + Math.pow(hash(i * 1.7), 1.4) * (y1 - y0);
    const k = (yy - y0) / (y1 - y0);
    const xc = (o.sunX ?? 720) + (hash(i * 3) - .5) * (80 + 500 * k) + Math.sin(t * 1.5 + i) * 10;
    g.strokeStyle = `rgba(255,${200 - k * 60},${140 - k * 40},${.55 * (1 - k * .6)})`; g.lineWidth = 2 + 4 * k;
    g.beginPath(); g.moveTo(xc - 20 - 60 * k, yy); g.lineTo(xc + 20 + 60 * k, yy); g.stroke();
  }
  g.restore();
}

// ---------------------------------------------------------------- 15: wide -- the river of rats follows his silhouette (gong)
function shot15(g, t, lt) {
  const t0 = b(14);
  const push = 1 + .05 * ease.io(lt / 1.77) + .02 * C.decay(t - t0 - HIT, 3);
  g.save(); g.translate(W / 2, H * .55); g.scale(push, push); g.translate(-W / 2, -H * .55);
  const hz = 1080;
  duskSky(g, t, { horizon: hz, sunX: 760, sunY: 930 });
  hills(g, hz - 40, '#4a3550', 140, 3); hills(g, hz, '#3a2a44', 80, 9);
  hamelinSilhouette(g, 40, hz - 4, .9, '#2c2034');
  water(g, hz, 1460, t, { sunX: 760 });
  // near bank (foreground earth + reeds)
  K.shape(g, [[-40, 1520], [300, 1470], [700, 1500], [W + 40, 1440], [W + 40, H + 40], [-40, H + 40]], { fill: '#3b2c2c', lw: 5, tension: .4 });
  K.shape(g, [[-40, 1455], [200, 1450], [520, 1460], [800, 1448], [W + 40, 1430], [W + 40, 1500], [-40, 1520]], { fill: '#4d3a35', lw: 5, tension: .4 });
  // a pale shoreline strip; the river of rats walks it, silhouetted against the bright water
  K.shape(g, [[-40, 1352], [300, 1346], [600, 1352], [820, 1344], [820, 1376], [600, 1384], [300, 1378], [-40, 1386]], { fill: '#9a7480', lw: 3.5, tension: .4 });
  // the river of rats along the bank: silhouettes, flowing in lockstep toward the Piper
  for (let i = 0; i < 70; i++) {
    const u = ((i / 70) + (t - t0) * .11) % 1;
    const x = lerp(-80, 790, u), y = 1360 - u * 6 + (i % 3) * 7 + Math.sin(u * 30) * 2;
    const s = .5 + .14 * (i % 3) / 2;
    RT.ratSide(g, x, y, { s, dir: 1, phase: (t - t0) * 4 + (i % 2) * .5, t, speed: 1, sil: '#1e1520', shadow: false });
  }
  // the Piper on the rock at the river's edge, silhouette, playing
  K.shape(g, [[770, 1390], [800, 1330], [880, 1312], [960, 1336], [990, 1390]], { fill: '#2a1f28', lw: 5, tension: .3 });
  PS.drawPerson(g, CAST.piper, R.merge(PP.playPose(t), { yaw: -.9 }), { x: 880, y: 1322, s: .78, sil: '#1a1220', lw: 3.5, t, wind: .5, shadow: false });
  // reeds in the foreground, swaying
  for (let i = 0; i < 18; i++) { const x = 40 + i * 62 + hash(i) * 30, h = 120 + hash(i * 3) * 120; const sw = Math.sin(t * 1.6 + i) * 10; K.line(g, [[x, 1560], [x + sw * .5, 1560 - h * .6], [x + sw, 1560 - h]], 5, '#2a2024', 1); }
  g.restore();
}

// ---------------------------------------------------------------- 16: they pour into the water; ripples ring out on the half-time hits
function shot16(g, t, lt) {
  const t0 = b(15);
  const hz = 820;
  duskSky(g, t, { horizon: hz, sunX: 300, sunY: 640 });
  hills(g, hz, '#3a2a44', 70, 5);
  water(g, hz, H, t, { sunX: 300, top: '#a87068' });
  // the bank edge on the left: rats leap off in arcs (two per 16th), each makes a ring, then sinks
  K.shape(g, [[-40, 1180], [180, 1150], [330, 1210], [360, 1320], [-40, 1380]], { fill: '#4d3a35', lw: 5, tension: .4 });
  const hits = [t0, b(15, 8)];
  const jumpers = [];
  for (let i = 0; i < 40; i++) {
    const tj = t0 - .3 + i * S16 * .5 + (hits.some(h => Math.abs(t0 - .3 + i * S16 * .5 - h) < .05) ? 0 : 0);
    jumpers.push({ tj, x0: 200 + hash(i) * 120, land: 420 + hash(i * 3) * 520, ly: 1250 + hash(i * 7) * 380, i });
  }
  // ripples first (on the water), then flying rats above
  for (const J of jumpers) {
    const tl = J.tj + .38;
    E.ripple(g, J.land, J.ly, t - tl, 1 + (J.ly - 1200) / 900, { col: '#f2d7c0', life: 1.4, a: .7 });
  }
  for (const h of hits) for (let k = 0; k < 3; k++) E.ripple(g, 650 + (k - 1) * 220, 1500 + k * 40, t - h - HIT - k * .05, 2.2, { col: '#ffe6cc', life: 1.6, a: .9 });
  for (const J of jumpers) {
    const dt = t - J.tj; if (dt < 0) continue;
    if (dt < .38) {
      const u = dt / .38; const x = lerp(J.x0, J.land, u), y = lerp(1170, J.ly, u) - Math.sin(Math.PI * u) * 160;
      RT.ratSide(g, x, y, { s: .8 + (J.ly - 1200) / 900, dir: 1, phase: dt * 4, t, speed: .2, tilt: lerp(-.6, .9, u), shadow: false });
    } else if (dt < .9) { // head bobbing then sinking
      const u = (dt - .38) / .52;
      g.save(); g.beginPath(); g.rect(0, 0, W, J.ly - 4 + 0); g.clip();
      RT.ratSide(g, J.land + u * 30, J.ly + 10 + u * u * 60, { s: .8 + (J.ly - 1200) / 900, dir: 1, phase: 0, t, speed: 0, look: 0, shadow: false });
      g.restore();
    }
  }
  // the Piper on his rock (right), playing the low notes, cloak in the river wind
  K.shape(g, [[700, 1180], [740, 1090], [860, 1070], [960, 1100], [1000, 1180]], { fill: '#3a2c30', lw: 5, tension: .3 });
  PS.drawPerson(g, CAST.piper, R.merge(PP.playPose(t, { eyes: 'narrow' }), { yaw: -.65 }), { x: 860, y: 1085, s: 1.15, lw: 5, t, wind: .8 });
}

// ---------------------------------------------------------------- 17: still water -- the last rings fade
function shot17(g, t, lt) {
  const t0 = b(16);
  const hz = 1000;
  const pull = 1 - .06 * ease.io(lt / 1.77);
  g.save(); g.translate(W / 2, H * .5); g.scale(pull, pull); g.translate(-W / 2, -H * .5);
  duskSky(g, t, { horizon: hz, sunX: 540, sunY: 900 });
  hills(g, hz - 30, '#4a3550', 120, 7); hills(g, hz, '#3a2a44', 60, 2);
  water(g, hz, H + 100, t, { sunX: 540 });
  // reflection of the Piper (inverted silhouette) + the man himself on the far rock
  K.shape(g, [[620, 1004], [650, 960], [760, 950], [830, 975], [850, 1004]], { fill: '#2a1f28', lw: 4, tension: .3 });
  const P = R.merge(R.idle(t * .3, { B: CAST.piper.B, shift: .05 }), { yaw: -.3, arms: { l: { swing: .5, out: .1, elbow: 1.2 }, r: { swing: .1, out: .1, elbow: .3 } }, head: { pitch: .12 } });
  g.save(); g.globalAlpha = .35; g.translate(0, 2 * 960); g.scale(1, -1);
  PS.drawPerson(g, CAST.piper, P, { x: 735, y: 960, s: .5, sil: '#1a1220', lw: 3, t, shadow: false });
  g.restore();
  PS.drawPerson(g, CAST.piper, P, { x: 735, y: 960, s: .5, sil: '#1a1220', lw: 3, t, wind: .3, shadow: false });
  // the last rings, fading -- one small pulse on each stomp in the silence
  const st = C.eventsIn(EV.stomp, t0, b(17));
  for (const [i, x, y] of [[0, 360, 1350], [1, 560, 1500], [2, 760, 1420]]) E.ripple(g, x, y, t - t0 + .7 + i * .25, 2.4, { col: '#f2d7c0', life: 2.6, a: .55 });
  st.forEach((s, i) => E.ripple(g, 420 + i * 140, 1250 + i * 70, t - s - HIT, 1.2, { col: '#f2d7c0', life: 1.2, a: .45 }));
  // a few bubbles rising
  for (let i = 0; i < 6; i++) { const u = ((t - t0) * .7 + hash(i)) % 1; K.ellipse(g, 400 + hash(i * 3) * 400, 1600 - u * 200, 6, 6, { fill: null, lw: 2.5, ink: '#f2d7c0', alpha: 1 - u }); }
  g.restore();
}

// ---------------------------------------------------------------- 18: the town bursts out -- bunting rises, people jump up on the rising notes
function shot18(g, t, lt) {
  const t0 = b(17);
  const V = new Wd.View({ cx: 0, cy: 300, cz: 0, f: 1150, hy: 1060 });
  ST.streetBackdrop(g, V, t, 'day', { sunX: 830, clouds: [[260, 300, 1.2]] });
  const items = Wd.streetItems({ mood: 'day', seed: 88, half: 900, z0: 1300 });
  Wd.drawItems(g, V, items);
  // bunting strings rising on the beats
  const bt = [t0, t0 + BEAT, t0 + 2 * BEAT, t0 + 3 * BEAT];
  bt.forEach((tb, i) => {
    const u = ease.back(clamp((t - tb - HIT) / .3)); if (u <= 0) return;
    const y = lerp(1300, 380 + i * 150, u);
    E.bunting(g, -40, y, W + 40, y + 40, 90, t);
  });
  // townsfolk jump into frame, one on each rising note of the chromatic creep
  const creep = C.FL.concat(C.BM.flute_lo || []).filter(n => n.t >= b(17, 8) - .01 && n.t < b(18)).map(n => n.t).sort((a, c) => a - c);
  const jumpers = [[200, 13], [880, 17], [430, 21], [700, 25], [560, 29]];
  creep.slice(0, 5).forEach((tj, i) => {
    const [x, sd] = jumpers[i]; const ch = CAST.townsfolk(sd);
    const dt = t - tj - HIT; if (dt < 0) return;
    const u = clamp(dt / .3);
    const y = 2150 - 520 * ease.o3(u) + (dt > .3 ? Math.sin((dt - .3) * TAU * 1.13) * 12 : 0);
    const P = R.merge(R.jig(C.beatPhase(t), C.beatIndex(t), { handsUp: true, amt: .8 }), { yaw: (i % 2 ? -.3 : .3), face: { eyes: 'narrow', mouth: 'laugh', brow: 'raised' } });
    PS.drawPerson(g, ch, P, { x, y, s: 1.6, lw: 5.5, t });
  });
}

module.exports = [
  { id: '15_river_wide', t0: b(14), mood: 'dusk', grade: () => ({ mood: 'dusk', amt: .55 }), draw: shot15, flashIn: true },
  { id: '16_into_water', t0: b(15), mood: 'dusk', grade: () => ({ mood: 'dusk', amt: .55 }), draw: shot16 },
  { id: '17_still_water', t0: b(16), mood: 'dusk', grade: () => ({ mood: 'dusk', amt: .6 }), draw: shot17 },
  { id: '18_celebration_burst', t0: b(17), mood: 'day', draw: shot18 },
];
