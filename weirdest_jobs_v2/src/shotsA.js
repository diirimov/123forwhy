// ===================================================================== shotsA.js  (opening 0-3.2, Knocker-Up 3.2-20.8)
'use strict';
const ALF = CAST2.sleeper, NED = CAST2.knocker;
function stageFG2(c, t, z = 1, cx = 540, cy = 960, open = 0) {
  c.save(); cam(c, cx, cy, z);
  for (let i = 0; i < 9; i++) { const x = 80 + i * 115; ell(c, x, 1880, 34, 16, '#3a2a1a', 3); glow(c, x, 1860, 160, 'rgba(255,200,120,0.25)'); }
  c.restore();
  c.save(); cam(c, cx, cy, z * (1 + open * .1));
  c.save(); c.translate(-open * 300, 0); c.drawImage(SETS.prosc, 0, 0, 540, H, 0, 0, 540, H); c.restore();
  c.save(); c.translate(open * 300, 0); c.drawImage(SETS.prosc, 540, 0, 540, H, 540, 0, 540, H); c.restore();
  c.restore();
}
// --------------------------------------------------------------- the trio (opening + loop target)
function trio2(c, t, o = {}) {
  const g = 1720, air = o.air ?? key(t, [[0, 220], [.22, 0, 'in']]), land = o.land ?? wob(t, .22, .16, 3);
  const pk = n => hit(t, [[.4, .8, 1.2][n]], .28);
  drawChar2(c, NED, mergeP({ x: 225, y: g, s: 1.22, f: 1, view: 'q', air, sq: 1 - land * .12, lean: -.05 + .1 * pk(0),
    hipR: .25, kneeR: .35, hipL: -.25, kneeL: .5, shR: 2.6 - .3 * pk(1), elR: .25, handR: 'grip', shL: -.6, elL: .7, handL: 'fist',
    head: -.05 + .1 * pk(0), expr: E2(pk(2) > .3 ? 'shout' : 'grin', t, 1, { lookX: .6 }), hold: raisePole(.32, 160) }, o.k1), t);
  drawChar2(c, CAST2.groom, mergeP({ x: 545, y: g + 40, s: 1.22, f: 1, view: 'q', air: air * .8, sq: 1 - land * .1, lean: .04 - .08 * pk(1),
    hipR: .15, kneeR: .12, hipL: -.15, kneeL: .2, shR: .75 + .2 * pk(1), elR: 1.45, handR: 'open', shL: .55, elL: 1.6, handL: 'open',
    expr: E2('smug', t, 2, { lookX: .2 }), hold: { R: (cc, J) => closeStool(cc, J.handN[0] - 20, J.handN[1] + 90, .34, .25 * pk(1), .7) } }, o.k2), t);
  drawChar2(c, CAST2.sineater, mergeP({ x: 900, y: g, s: 1.18, f: -1, view: 'q', air: air * .6, sq: 1 - land * .08, lean: .06,
    hipR: .15, kneeR: .25, hipL: -.1, kneeL: .3, shR: .1 + .15 * pk(2), elR: 2.35, handR: 'grip', shL: -.2, elL: .4, handL: 'relaxed',
    expr: E2('mystic', t, 3, { lookX: .7 }), hold: holdBread2(.38, 0, 20, -20) }, o.k3), t);
}
// =============================================================== OPENING 0.0 - 3.2
shot(0, 1.6, 'O1 the trio leaps on stage', 'cut', (c, t) => {
  const z = key(t, [[0, 1.12], [1.6, 1.0, 'out']]);
  stageBG2(c, t, z, 540, 1050);
  c.save(); cam(c, 540, 1050, z);
  for (let i = 0; i < 7; i++) { const ch = villager(300 + i, ['ind', 'court', 'vil'][i % 3]); drawChar2(c, ch, mergeP({ x: 120 + i * 140, y: 1330, s: .5, f: i % 2 ? 1 : -1, view: 'q', expr: X('grin') }, phrase(t + i * .07, 0, [[0, { shR: 2.5, elR: .3, shL: .5, elL: .6, hipR: .4, kneeR: .4 }], [1, { shR: .5, elR: .6, shL: 2.5, elL: .3, hipL: .4, kneeL: .4, hipR: 0, kneeR: .1 }], [2, { shR: 2.5, elR: .3, shL: .5, elL: .6, hipR: .4, kneeR: .4 }]], 2)), t); }
  trio2(c, t);
  c.restore();
  stageFG2(c, t, z, 540, 1050);
  speedLines(c, 540, 1100, hit(t, [0], .3) * .5, 4);
}, 'stage');
function ecuGlass2(c, t, taps) {
  bricks(c, 0, 0, W, H, '#b0583a', 5, 150, 64);
  rrect(c, 140, 260, 800, 1440, 8, '#ece4d0', 14);
  c.fillStyle = lg(c, 160, 280, 920, 1680, [[0, '#3a5ab0'], [.5, '#22306a'], [1, '#4a62b0']]); c.fillRect(160, 280, 760, 1400);
  for (let i = 0; i < 50; i++) { const r = rng(i * 7); ell(c, 160 + r() * 760, 280 + r() * 1400, 4 + r() * 18, 2 + r() * 8, 'rgba(220,235,255,0.2)'); }
  c.fillStyle = 'rgba(255,255,255,0.12)'; c.beginPath(); c.moveTo(200, 1680); c.lineTo(600, 280); c.lineTo(720, 280); c.lineTo(320, 1680); c.fill();
  line(c, [[540, 280], [540, 1680]], 24, '#ece4d0'); line(c, [[160, 980], [920, 980]], 24, '#ece4d0');
  const k = hit(t, taps, .09);
  for (const tp of taps) if (t > tp && t < tp + .6) { const u = (t - tp) / .6; ell(c, 700, 720, 40 + u * 260, (40 + u * 260) * .8, null, 6 * (1 - u), 0, `rgba(230,240,255,${.8 * (1 - u)})`); }
  const pull = 1 - k;
  pole(c, 1300, 1800, 700 + pull * 70, 720 + pull * 60);
  hand2(c, [1180, 1620], -2.3, 'grip', 110, NED.skin, 6);
  sparkles(c, 700, 720, 120, k, 3, t);
}
shot(1.6, 2.0, 'O2 ECU pole on glass', 'cut', (c, t) => { c.save(); cam(c, 600, 900, 1 + (t - 1.6) * .3); ecuGlass2(c, t, [1.6, 1.8]); c.restore(); }, 'knocker');
shot(2.0, 2.4, 'O3 ECU royal close stool', 'cut', (c, t) => {
  c.fillStyle = rg(c, 540, 900, 50, 1100, [[0, '#d0303a'], [1, '#5a0a18']]); c.fillRect(0, 0, W, H);
  lightShafts(c, 540, -100, 0, 500, 1800, '#ffd890', .2);
  c.save(); cam(c, 540, 1050, .85 + (t - 2) * .4);
  closeStool(c, 540, 1350, 1.25, .3 + .08 * Math.sin(t * 8), 1);
  const hx = 650 + Math.sin(t * 20) * 50;
  hand2(c, [hx, 1030], .5, 'open', 140, '#f6f0e4', 6);
  rrect(c, hx - 40, 1110, 160, 70, 22, '#f4efe2', 5);
  c.restore();
  sparkles(c, 540, 1000, 380, 1, 9, t);
}, 'groom');
shot(2.4, 2.8, 'O4 ECU bread + candle', 'cut', (c, t) => {
  c.fillStyle = rg(c, 540, 1100, 50, 1100, [[0, '#5a4a7a'], [1, '#141028']]); c.fillRect(0, 0, W, H);
  c.save(); cam(c, 540, 1050, 1 + (t - 2.4) * .25);
  candle(c, 840, 1520, 260, t, 1, 1.4);
  hand2(c, [330, 1330], -1.2, 'open', 170, CAST2.sineater.skin, 6);
  hand2(c, [760, 1340], 1.25, 'open', 170, CAST2.sineater.skin, 6, -1);
  bread(c, 545, 1250, 1.5);
  blob(c, [[-100, -100], [1180, -100], [1180, 400], [900, 250], [540, 190], [180, 260], [-100, 420]], '#3a3236', 0);
  c.restore();
  motes(c, t, 4, 40, '#ffcf8a', .5, 20);
}, 'sin');
shot(2.8, 3.2, 'O5 the trio points: HA!', 'cut', (c, t) => {
  const z = key(t, [[2.8, 1.0], [3.0, 1.2, 'out'], [3.2, 1.32, 'in']]);
  stageBG2(c, t, z, 540, 1200);
  c.save(); cam(c, 540, 1200, z);
  const ha = E.back(clamp((t - 2.98) / .12));
  trio2(c, t, { air: 0, land: 0, k1: { shL: lerp(.4, 1.6, ha), elL: 0, handL: 'point', expr: X('shout') }, k2: { shL: lerp(.5, 1.55, ha), elL: .1, handL: 'point', expr: X('grin') }, k3: { shL: lerp(.2, 1.5, ha), elL: .1, handL: 'point', expr: X('grin', { eye: .7 }) } });
  c.restore();
  stageFG2(c, t, z, 540, 1200);
  speedLines(c, 540, 1100, hit(t, [3.0], .3) * .7, 6);
  popWord(c, t, 'HA!', 3.0, 540, 760, 200);
}, 'stage');

// =============================================================== KNOCKER-UP
shot(3.2, 6.4, 'K1 Ned struts through the dawn town', 'whip', (c, t) => {
  const lt = t - 3.2, camX = 300 + lt * 150;
  townBG(c, t, camX);
  drawChar2(c, villager(611, 'ind'), mergeP({ x: 1700 - camX - lt * 60, y: 1500, s: .55, f: -1, view: 'p', expr: E2('happy', t, 3) }, walk2(t + .2, { amp: .8 })), t);
  const w = walk2(t, { amp: 1.05, bob: 1.3, lean: .02, armAmp: .6 });
  let o = { view: 'p', expr: E2('happy', t, 1, { lookX: .4 }), hold: carryPole(-.62 + Math.sin(t * PI / SPB) * .03), shR: .9 + w.shR * .2, elR: -1.9, handR: 'grip', wrR: .3 };
  const tip = t >= 4.75 && t < 5.35, spin = t >= 5.35 && t < 6.05, point = t >= 6.05;
  if (tip) { const k = E.back(clamp((t - 4.8) / .15)); o = mergeP(o, { shL: lerp(.3, 2.95, k), elL: lerp(.3, 1.5, k), handL: 'grip', expr: E2('grin', t, 1, { lookX: 1 }), head: -.05 }); }
  if (spin) { const u = (t - 5.35) / .7, views = ['p', 'q', 'f', 'b', 'p']; const vi = Math.min(4, Math.floor(u * 5)); o = mergeP(o, { view: views[vi], f: vi === 3 ? -1 : 1, air: Math.sin(u * PI) * 60, expr: E2('laugh', t, 1) }); }
  if (point) { const k = E.back(clamp((t - 6.1) / .14)); o = mergeP(o, { shL: lerp(.3, 2.75, k), elL: .05, handL: 'point', lean: -.12, head: -.25, headView: 'q', expr: X('shout', { lookX: .6, lookY: -.8 }) }); }
  drawChar2(c, NED, mergeP({ x: 470 + Math.sin(lt * .7) * 15, y: 1830, s: 1.95, f: 1 }, w, o), t);
  fogBand(c, 1760, 140, t, '#e0d8f8', .12, 40, 8);
  chapter2(c, t, '1', 'THE HUMAN ALARM CLOCK', 3.3, 6.1, 'knocker');
}, 'knocker');

// bedroom with Alf. wake: 0 asleep .. 1 sitting up
function bedroom2(c, t, o = {}) {
  c.drawImage(SETS.bedroom.bg, 0, 0);
  glow(c, 750, 520, 520, `rgba(170,190,255,${.18 + (o.tapK || 0) * .35})`);
  candle(c, 230, 830, 90, t, 3, .9);
  rrect(c, 90, 1200, 900, 60, 14, '#5a3a2a', 5);
  line(c, [[120, 1260], [120, 1600]], 24, '#2a2a34'); line(c, [[960, 1260], [960, 1600]], 24, '#2a2a34');
  line(c, [[100, 980], [100, 1600]], 20, '#2a2a34'); for (let i = 0; i < 5; i++) line(c, [[100, 1000 + i * 40], [150, 1000 + i * 40]], 9, '#2a2a34'); ell(c, 100, 970, 22, 22, '#e0b040', 4);
  blob(c, [[150, 1100], [180, 1010], [440, 995], [480, 1090], [430, 1150], [180, 1150]], '#f4f0e6', 5);
}
function quilt(c, y0, breath, lift) {
  const qy = y0 - breath * 28 - lift;
  const pts = [[160, qy + 50], [330, qy - 10], [620, qy - 30], [950, qy + 10], [1000, 1320], [960, 1400], [150, 1410], [120, 1270]];
  blob(c, pts, '#d8503a', 5);
  c.save(); c.beginPath(); spline(c, pts); c.clip();
  const pr = rng(4); for (let i = 0; i < 11; i++) for (let j = 0; j < 4; j++) { c.fillStyle = ['#f0b040', '#3a7ab0', '#d8503a', '#5aa050', '#f2e6c8'][Math.floor(pr() * 5)]; c.fillRect(120 + i * 90, qy - 40 + j * 95, 88, 93); }
  for (let i = 0; i < 11; i++) line(c, [[120 + i * 90, qy - 60], [120 + i * 90, 1420]], 3, 'rgba(60,30,20,0.5)');
  c.fillStyle = lg(c, 0, qy - 40, 0, 1410, [[0, 'rgba(255,240,220,0.15)'], [1, 'rgba(20,10,20,0.4)']]); c.fillRect(0, qy - 60, W, 600);
  c.restore();
}
function dream2(c, t, x, y, a) {
  if (a <= 0) return;
  c.save(); c.globalAlpha = a;
  ell(c, x - 150, y + 200, 16, 16, '#f4f2ff', 4); ell(c, x - 100, y + 150, 26, 26, '#f4f2ff', 4);
  blob(c, [[x - 190, y], [x - 130, y - 120], [x, y - 160], [x + 150, y - 130], [x + 200, y - 10], [x + 130, y + 100], [x - 20, y + 120], [x - 170, y + 90]], '#f4f2ff', 5);
  const ph = bphase(t), jx = x - 90 + ph * 180, jy = y + 30 - Math.sin(ph * PI) * 80;
  line(c, [[x - 10, y + 70], [x - 10, y + 15]], 6, '#7a5a3a'); line(c, [[x + 30, y + 70], [x + 30, y + 15]], 6, '#7a5a3a'); line(c, [[x - 20, y + 30], [x + 40, y + 30]], 6, '#7a5a3a');
  for (let i = 0; i < 6; i++) ell(c, jx + Math.cos(i) * 24, jy + Math.sin(i) * 15, 19, 17, '#fff', 3);
  ell(c, jx + 36, jy - 4, 14, 16, '#3a3a3a', 3); line(c, [[jx - 10, jy + 14], [jx - 14, jy + 36]], 5, '#3a3a3a'); line(c, [[jx + 14, jy + 14], [jx + 18, jy + 36]], 5, '#3a3a3a');
  c.restore();
}
function alfHead(c, t, x, y, ang, s, e) { c.save(); c.translate(x, y); c.rotate(ang); drawHead2(c, ALF, 'p', e, ALF.body.hh * s, 4.5 * Math.min(s, 1.6)); c.restore(); }
shot(6.4, 8.0, 'K2 Alf snores', 'cut', (c, t) => {
  const lt = t - 6.4, z = 1.75 + lt * .05;
  const breath = .5 - .5 * Math.cos(lt / 1.6 * TAU);
  c.save(); cam(c, 400, 1060, z);
  bedroom2(c, t);
  alfHead(c, t, 300, 1105, -1.45 + Math.sin(t * 1.2) * .03, 1.45, X('sleep', { open: .15 + breath * .75, mouth: 'open' }));
  quilt(c, 1130, breath, 0);
  c.restore();
  zzz(c, 300, 820, t, 1);
  dream2(c, t, 760, 700, clamp((t - 6.6) * 3));
  caption(c, t, 'Workers *paid* people\nto wake them up.', 6.5, 9.4);
}, 'knocker');
shot(8.0, 8.8, 'K3a ECU tap tap tap', 'cut', (c, t) => { c.save(); cam(c, 640, 860, 1.1 + (t - 8) * .2); ecuGlass2(c, t, patT(5, 'x.x...x..x.x.x..')); c.restore(); caption(c, t, 'Workers *paid* people\nto wake them up.', 6.5, 9.4); }, 'knocker');
shot(8.8, 9.6, 'K3b Ned taps the upstairs window', 'cut', (c, t) => {
  const S = SETS.town;
  c.save(); cam(c, 560, 900, 1.05); c.drawImage(S.sky, 0, 0); c.drawImage(S.mid, -1450, -180); c.restore();
  const taps = patT(5, 'x.x...x..x.x.x..').filter(v => v > 8.7), k = hit(t, taps, .1);
  drawChar2(c, NED, { x: 380, y: 2150, s: 2.4, f: 1, view: 'p', lean: -.18, hipR: .2, kneeR: .1, hipL: -.15, kneeL: .1, shR: 2.65 + k * .08, elR: -.1, handR: 'grip', shL: 2.35, elL: .25, handL: 'grip', head: -.42, headView: 'p',
    expr: X('grin', { lookX: .5, lookY: -.9, open: .2 + k * .3 }), hold: raisePole(-.02 + (1 - k) * .08, 300) }, t);
  fogBand(c, 1800, 160, t, '#e0d8f8', .16, 30, 9);
  caption(c, t, 'Workers *paid* people\nto wake them up.', 6.5, 9.4);
}, 'knocker');
shot(9.6, 11.2, 'K4 Alf wakes up', 'cut', (c, t) => {
  const lt = t - 9.6, sit = E.back(clamp(lt / .22));
  const [sx, sy] = shake(t, [9.6], 18, .15);
  c.save(); c.translate(sx, sy); cam(c, 400, 1000, 1.55 + hit(t, [9.6], .4) * .1);
  bedroom2(c, t, { tapK: hit(t, [9.6], .3) });
  const angry = t > 10.3 && t < 10.8, wave = t >= 10.8;
  const air = hit(t, [9.72], .22) * 70;
  if (lt < .02) alfHead(c, t, 300, 1105, -1.45, 1.25, X('sleep', { open: .4, mouth: 'open' }));
  else drawChar2(c, ALF, { x: 330, y: 1270, s: 1.2, f: 1, view: angry || wave ? 'q' : 'p', lean: lerp(-1.3, angry ? .2 : -.05, sit), air,
    hipR: 1.5, kneeR: .05, hipL: 1.55, kneeL: .05,
    shR: angry ? 2.5 : wave ? 2.9 + Math.sin(t * 18) * .25 : 2.7, elR: angry ? 1.5 : .3, handR: angry ? 'fist' : 'spread', shL: angry ? .8 : 2.6, elL: angry ? 1.2 : .4, handL: 'spread',
    head: angry ? .15 : 0, expr: angry ? X('anger', { lookX: 1 }) : wave ? X('grin', { lookX: 1 }) : X('surprise', { lookY: -.3 }) }, t);
  quilt(c, 1130, 0, sit * 30);
  c.restore();
  if (lt < .5) speedLines(c, 400, 900, (1 - lt * 2) * .6, 12);
  if (t > 9.6 && t < 10.6) { const u = (t - 9.6) / 1.0; c.save(); c.translate(380 + u * 500, 700 - Math.sin(u * PI) * 380); c.rotate(u * 8); nightcap('#5b86c4', '#f3efe4')(c, 'q', 120, 5, {}); c.restore(); }
  popWord(c, t, 'WHAT?!', 9.7, 700, 640, 110);
  if (wave) popWord(c, t, "I'M UP!", 10.85, 720, 640, 100, '#8ad0ff');
}, 'knocker');
// --- terrace facade with five windows opening in turn
function windowFrame2(c, x, y, o) {
  c.lineWidth = 16; c.strokeStyle = '#ece4d0'; c.strokeRect(x - 8, y - 8, 256, 316); c.lineWidth = 4; c.strokeStyle = OL; c.strokeRect(x - 16, y - 16, 272, 332);
  const sy = y - o * 150;
  c.save(); c.beginPath(); c.rect(x - 20, y - 170, 280, 480); c.clip();
  rrect(c, x, sy, 240, 150, 3, o < .5 ? 'rgba(50,70,140,0.85)' : 'rgba(170,190,240,0.15)', 8, '#ece4d0'); line(c, [[x + 120, sy], [x + 120, sy + 150]], 6, '#ece4d0');
  c.restore();
  rrect(c, x, y + 150, 240, 150, 3, o < .5 ? 'rgba(50,70,140,0.85)' : 'rgba(170,190,240,0.1)', 8, '#ece4d0'); line(c, [[x + 120, y + 150], [x + 120, y + 300]], 6, '#ece4d0');
  rrect(c, x - 26, y + 300, 292, 22, 4, '#cfc6b0', 5);
}
const WINF = [villager(41, 'ind'), Object.assign(villager(46, 'ind'), {}), villager(43, 'ind'), ALF, villager(45, 'ind')];
shot(11.2, 12.8, 'K5 five windows, five reactions', 'cut', (c, t) => {
  c.save(); cam(c, 540, 960, 1.0 + (t - 11.2) * .04);
  c.drawImage(SETS.facade.bg, 0, 0);
  const vs = vocIn(11.15, 12.8).slice(0, 5), times = [vs[0] ?? 11.2, vs[1] ?? 11.5, vs[2] ?? 11.8, vs[3] ?? 12.0, vs[4] ?? 12.3];
  const op = times.map(tt => E.back(clamp((t - tt) / .18)));
  const wins = [[80, 420], [420, 420], [760, 420], [80, 820], [760, 820]];
  wins.forEach(([x, y], i) => {
    c.fillStyle = '#20182a'; c.fillRect(x, y, 240, 300);
    if (op[i] > 0) { c.fillStyle = lg(c, x, y, x, y + 300, [[0, '#ffd27a'], [1, '#f09040']]); c.globalAlpha = Math.min(1, op[i] * 1.5); c.fillRect(x, y, 240, 300); c.globalAlpha = 1; }
    if (op[i] > .05) {
      c.save(); c.beginPath(); c.rect(x, y, 240, 300); c.clip();
      const pop = E.back(clamp((t - times[i]) / .25));
      const R = [
        { y: y + 560 - pop * 70, view: 'f', shR: 2.8, elR: .2, shL: 2.8, elL: .2, handR: 'spread', handL: 'spread', expr: X('surprise') },
        { y: y + 520, view: 'q', shR: 2.3 + Math.sin(t * 22) * .2, elR: 1.6, handR: 'fist', expr: X('anger', { lookX: .6, lookY: .5 }) },
        { y: y + 520, view: 'p', f: -1, expr: X('confused', { lookX: 1 }), head: .2 },
        { y: y + 520, view: 'q', shR: 1.5, elR: .7, handR: 'spread', expr: X('fear', { lookY: .9 }), head: .2 },
        { y: y + 520 + Math.sin(t * 25) * 8, view: 'q', shR: .5 + Math.sin(t * 30) * .6, elR: 1.0, shL: .8 + Math.cos(t * 30) * .6, elL: 1, handR: 'spread', expr: X('fear'), lean: Math.sin(t * 25) * .1 },
      ][i];
      drawChar2(c, WINF[i], mergeP({ x: x + 120, s: .85, f: 1, noShadow: true }, R), t);
      c.restore();
    }
    windowFrame2(c, x, y, op[i]);
  });
  if (t > times[3]) { const u = clamp((t - times[3]) / .7); c.save(); c.translate(200 + u * 120, 860 + E.in(u) * 900); c.rotate(u * 5); nightcap('#d8506a', '#fff')(c, 'q', 110, 5, {}); c.restore(); }
  const sweep = key(t, times.map((tt, i) => [tt, [-.5, 0, .45, -.45, .45][i]]).concat([[12.8, .2]]));
  drawChar2(c, NED, { x: 300, y: 2250, s: 1.7, f: 1, view: 'p', shR: 2.6, elR: 0, handR: 'grip', shL: 2.3, elL: .3, handL: 'grip', head: -.35, lean: -.1, expr: X('grin', { lookX: .5, lookY: -.9 }), hold: raisePole(sweep, 300) }, t);
  c.restore();
  caption(c, t, 'They tapped on *bedroom windows*\nevery morning.', 11.2, 14.2, { size: 56, y: 330 });
}, 'knocker');
shot(12.8, 13.6, 'K6a the furious neighbour', 'cut', (c, t) => {
  c.drawImage(SETS.wallwin.bg, 0, 0);
  rrect(c, 170, 420, 740, 1000, 10, '#ffcf7a'); glow(c, 540, 900, 600, 'rgba(255,190,90,0.4)');
  c.save(); c.beginPath(); c.rect(170, 420, 740, 1000); c.clip();
  drawChar2(c, WINF[1], { x: 540, y: 2300, s: 2.3, f: -1, view: 'q', shR: 2.4 + Math.sin(t * 28) * .25, elR: 1.5, handR: 'fist', shL: .5, elL: 1.6, handL: 'fist', head: Math.sin(t * 14) * .06, lean: .1,
    expr: X('anger', { lookX: -.3, lookY: .4, open: .3 + .2 * Math.sin(t * 20), mouth: 'teeth' }) }, t);
  c.restore();
  windowFrame2(c, 170, 420, 1);
  popWord(c, t, 'GRRR!', 12.9, 760, 1300, 110, '#ff7a5a');
  caption(c, t, 'They tapped on *bedroom windows*\nevery morning.', 11.2, 14.2, { size: 56, y: 330 });
}, 'knocker');
shot(13.6, 14.4, 'K6b Alf hops into his trousers', 'cut', (c, t) => {
  c.drawImage(SETS.bedroom.bg, 0, 0);
  const knocks = [13.9, 14.2], k = hit(t, knocks, .12);
  c.save(); cam(c, 540, 1150, 1.25);
  const hop = Math.abs(Math.sin((t - 13.6) * PI / SPB)) * 70;
  drawChar2(c, ALF, { x: 540, y: 1700, s: 1.25, f: 1, view: 'q', air: hop, hipR: 1.2, kneeR: 1.4, hipL: -.1, kneeL: .1, shR: .3, elR: 1.7, shL: .2, elL: 1.7, handR: 'grip', handL: 'grip', lean: .22 + Math.sin(t * 15) * .1,
    expr: X('fear', { open: .5 + k * .4, mouth: 'open', lookX: .8 }) }, t);
  blob(c, [[430, 1330 - hop], [570, 1320 - hop], [620, 1600 - hop * .4], [530, 1620 - hop * .5], [470, 1460 - hop]], '#4a4a7a', 5);
  c.restore();
  popWord(c, t, 'KNOCK!', 13.9, 780, 640, 100); popWord(c, t, 'KNOCK!', 14.2, 760, 760, 100);
  caption(c, t, 'They tapped on *bedroom windows*\nevery morning.', 11.2, 14.2, { size: 56, y: 330 });
}, 'knocker');
shot(14.4, 16.0, 'K7 a coin for every shout', 'cut', (c, t) => {
  townBG(c, t, 1200);
  const hey = vocIn(14.35, 16.0), hk = hit(t, hey, .15);
  c.save(); cam(c, 540, 1150, 1.2);
  drawChar2(c, WINF[0], { x: 250, y: 1830, s: 1.25, f: 1, view: 'q', shR: 1.5, elR: .5, handR: 'open', expr: E2('happy', t, 4, { lookX: 1 }) }, t);
  drawChar2(c, NED, { x: 760, y: 1840, s: 1.35, f: -1, view: 'q', shR: 1.35, elR: 1.0, handR: 'open', wrR: -.5, shL: -.3, elL: .3, lean: .05 + hk * .06, air: hk * 22,
    expr: X(hk > .3 ? 'laugh' : 'grin', { lookX: .8, lookY: .4 }), hold: { back: (cc, J) => poleAt(cc, J.sF, .2, 500) } }, t);
  hey.forEach((h, i) => { const u = (t - h + .3) / .45; if (u > 0 && u < 1.2) { const uu = clamp(u); const x = lerp(420, 650, uu), y = lerp(1300, 1290, uu) - Math.sin(uu * PI) * 260; coin(c, x, y, 26, t * 14 + i); if (u >= 1) sparkles(c, 650, 1290, 60, 1 - (u - 1) * 5, i, t); } });
  c.restore();
  const n = hey.filter(h => t > h + .15).length;
  if (n) { const p = 1 + hit(t, hey.map(h => h + .15), .15) * .3; c.save(); c.translate(900, 1000); c.scale(p, p); c.font = '80px Slab'; c.textAlign = 'center'; c.lineWidth = 16; c.strokeStyle = '#16204a'; c.lineJoin = 'round'; c.strokeText('+' + n, 0, 0); c.fillStyle = '#ffd23c'; c.fillText('+' + n, 0, 0); c.restore(); }
  caption(c, t, 'He was literally a\n*human alarm clock.*', 14.4, 17.4);
}, 'knocker');
shot(16.0, 17.6, 'K8 Ned dances with his pole', 'cut', (c, t) => {
  townBG(c, t, 1700 + (t - 16) * 60);
  const ph = phrase(t, 16.0, [
    [0, { view: 'q', f: 1, shR: 2.4, elR: .4, shL: 1.0, elL: 1.6, hipR: .9, kneeR: .2, hipL: -.15, kneeL: .3, lean: -.12, expr: X('grin'), handL: 'fist' }, 'back'],
    [1, { view: 'p', f: 1, shR: 2.0, elR: .6, shL: -.5, elL: .4, hipR: -.2, kneeR: .6, hipL: .3, kneeL: .5, air: 0, lean: .15, expr: X('shout') }, 'back'],
    [2, { view: 'q', f: -1, shR: 2.8, elR: .1, shL: 2.2, elL: .4, hipR: .3, kneeR: 1.3, hipL: -.1, kneeL: .1, air: 70, lean: -.05, expr: X('laugh'), handL: 'spread' }, 'back'],
    [3, { view: 'p', f: -1, shR: 2.2, elR: .5, shL: .8, elL: 1.2, hipR: .5, kneeR: .2, hipL: -.4, kneeL: .3, air: 0, lean: .2, expr: X('grin'), handL: 'open' }, 'out'],
    [4, { view: 'q', f: 1, shR: 2.4, elR: .4, shL: 1.0, elL: 1.6, hipR: .9, kneeR: .2, hipL: -.15, kneeL: .3, lean: -.12, expr: X('grin'), handL: 'fist' }, 'back']], 4);
  drawChar2(c, NED, mergeP({ x: 540, y: 1920, s: 1.65, handR: 'grip' }, ph, { hold: twirlPole(t, 2.5) }), t);
  motes(c, t, 6, 30, '#ffe0b0', .5, 40);
  caption(c, t, 'He was literally a\n*human alarm clock.*', 14.4, 17.4);
}, 'knocker');
const WORKERS2 = Array.from({ length: 8 }, (_, i) => villager(700 + i, 'ind'));
shot(17.6, 19.2, 'K9 the town marches to the mill', 'cut', (c, t) => {
  c.drawImage(SETS.factory.bg, 0, 0);
  smokePlume(c, 820, 200, t, '#7a6a8a', 3, 1.4);
  const lt = t - 17.6;
  WORKERS2.forEach((ch, i) => { const row = i % 2, x = 1250 - ((lt * 240 + i * 170) % 1600), y = 1640 + row * 130, s = .95 + row * .15;
    drawChar2(c, ch, mergeP({ x, y, s, f: -1, view: 'p' }, walk2(t + i * .05, { amp: 1, bob: 1.2 }), { expr: E2(['happy', 'neutral', 'grin'][i % 3], t, i, { lookX: .3 }) }), t); });
  drawChar2(c, NED, { x: 880, y: 1960, s: 1.45, f: -1, view: 'q', shR: 2.6 + Math.sin(t * 12) * .3, elR: .3, handR: 'spread', shL: -.3, elL: .3, expr: X('grin', { lookX: -.5 }), hold: { back: (cc, J) => poleAt(cc, J.sF, -.2, 500) } }, t);
  fogBand(c, 1500, 150, t, '#f0d0b0', .14, 30, 3);
}, 'knocker');
shot(19.2, 20.8, 'K10 stop-time, then KNOCK on the lens', 'cut', (c, t) => {
  townBG(c, t, 900);
  const fr1 = t >= 19.2 && t < 19.5, knocks = [20.0, 20.2, 20.4], kk = hit(t, knocks, .1), swing = clamp((t - 20.45) / .35);
  const pose = fr1 ? { view: 'f', shR: 3.0, elR: 0, shL: -.9, elL: .4, hipR: .5, kneeR: .2, hipL: -.4, kneeL: .3, lean: -.15, handR: 'grip', handL: 'spread', expr: X('shout') }
    : { view: 'q', shR: 2.0 - swing * .6, elR: .2, shL: 1.2, elL: .6, lean: .1 + swing * .2, handR: 'grip', handL: 'open', expr: X(t > 20.38 && t < 20.6 ? 'ooh' : 'grin', { lookX: .1 }) };
  c.save(); cam(c, 540, 1150, 1.1 + kk * .04 + swing * .3);
  drawChar2(c, NED, mergeP({ x: 540, y: 1840, s: 1.75, f: 1 }, pose, { hold: raisePole(fr1 ? .08 : (.9 - kk * .15 + swing * .4), 200) }), t);
  c.restore();
  flash(c, t, [19.2, 19.5], '#fff6e0', .08, .45);
  knocks.forEach((kt, i) => { if (t > kt) { c.save(); c.globalAlpha = .85; const cx = 640 + i * 40, cy = 700 - i * 30; for (let j = 0; j < 7; j++) { const a = j * .9 + i; line(c, [[cx, cy], [cx + Math.cos(a) * 70, cy + Math.sin(a) * 70], [cx + Math.cos(a + .3) * 130, cy + Math.sin(a + .3) * 130]], 3, '#eef4ff'); } c.restore(); } });
  popWord(c, t, 'HEY!', 19.2, 540, 560, 160); popWord(c, t, 'HA!', 19.5, 560, 600, 160, '#ff9a5a');
  knocks.forEach(kt => popWord(c, t, 'KNOCK!', kt, 600, 520, 110));
  if (swing > 0) { c.save(); c.globalAlpha = swing; pole(c, 1400, 2200, 540 - swing * 100, 900 - swing * 300); c.restore(); speedLines(c, 540, 900, swing * .8, 33); }
}, 'knocker');
