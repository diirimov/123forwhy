// ===================================================================== shots_b.js  (profession 2: Groom of the Stool, 20.8 - 38.4)
'use strict';
const holdSceptre = (a, len = 360) => ({ R: (c, J) => { const h = J.handNear; sceptre(c, h[0] - Math.sin(a) * 90, h[1] + Math.cos(a) * 90, h[0] + Math.sin(a) * len, h[1] - Math.cos(a) * len); } });
const GUARDS = [CAST.guard, Object.assign({}, CAST.guard, { skin: SKIN.olive, face: Object.assign({}, CAST.guard.face, { tache: tache('#2a1a10', .9) }) }), Object.assign({}, CAST.guard, { skin: SKIN.pale }), Object.assign({}, CAST.guard, { skin: SKIN.deep })];
const halberd = (raise) => ({ R: (c, J) => { const h = J.handNear, a = lerp(.35, 0, raise); line(c, [[h[0] - Math.sin(a) * 200, h[1] + Math.cos(a) * 200], [h[0] + Math.sin(a) * 520, h[1] - Math.cos(a) * 520]], 14, '#5a3a20'); const tx = h[0] + Math.sin(a) * 520, ty = h[1] - Math.cos(a) * 520; c.save(); c.translate(tx, ty); c.rotate(a); poly(c, [[0, -60], [12, 0], [-12, 0]], '#c8ccd8', 4); blob(c, [[6, -10], [60, -30], [64, 20], [6, 10]], '#c8ccd8', 4); poly(c, [[-6, -20], [-36, -4], [-6, 4]], '#c8ccd8', 4); c.restore(); } });
const COURT = [CAST.noble1, CAST.noble2, CAST.servant, townsfolk(901, 'vil'), Object.assign({}, CAST.noble1, { col: Object.assign({}, CAST.noble1.col, { coat: '#6a2a5a' }), skin: SKIN.warm })];

function hallScene(c, t, camZ = 1, camY = 960, doorOpen = 1) {
  c.save(); cam(c, 540, camY, camZ);
  c.drawImage(SETS.hall.bg, 0, 0);
  lightShafts(c, 540, 330, 0, 300, 1500, '#ffe0a0', .12);
  motes(c, t, 21, 50, '#ffe6a8', .55, 15);
  c.restore();
}
function doors(c, open, cx = 540, cy = 960, z = 1) {
  if (open >= 1) return;
  c.save(); cam(c, cx, cy, z);
  const w = 540 * (1 - E.out(open));
  c.drawImage(SETS.door, 0, 0, 540, 1300, 0, 300, w, 1620);
  c.save(); c.translate(1080, 0); c.scale(-1, 1); c.drawImage(SETS.door, 0, 0, 540, 1300, 0, 300, w, 1620); c.restore();
  c.restore();
}
// G1: match cut sceptre -> doors burst -> king strides in
shot(20.8, 22.4, 'G1 doors burst + king strides', 'cut', (c, t) => {
  const lt = t - 20.8;
  const z = key(lt, [[0, 1.0], [.6, 1.0]]);
  hallScene(c, t, 1.0);
  const prog = clamp((lt - .25) / 1.35);
  const kx = 540, ky = lerp(1380, 1850, E.io(prog)), ks = lerp(.75, 1.15, E.io(prog));
  // guards line the carpet
  [[230, 1450, .62, 1], [850, 1450, .62, -1], [120, 1700, .85, 1], [960, 1700, .85, -1]].forEach(([x, y, s, f], i) => drawChar(c, GUARDS[i], { x, y, s, f, turn: .45, shR: .25, elR: -.2, handR: 'hold', expr: { mouth: 'flat', eye: blink(t, i + 5), lookX: f > 0 ? .6 : -.6 }, hold: halberd(1) }, t));
  const wp = walkPose(t, { amp: .55, strut: .8 });
  drawChar(c, CAST.king, merge({ x: kx, y: ky, s: ks, f: 1, turn: .05 }, wp, { shR: 2.5, elR: .1, handR: 'hold', shL: -.3 + Math.sin(t * 7.85) * .2, expr: { mouth: 'grin', open: .3, eye: blink(t, 9), brow: .6, lookX: 0, lookY: .2 }, hold: holdSceptre(.35) }), t);
  // the doors swing open on the slam (we are inside looking out through them)
  doors(c, clamp(lt / .3));
  // match-cut ECU: first frames are a sceptre in the same line as the pole
  if (lt < .35) { const k = 1 - E.in(lt / .35); c.save(); c.globalAlpha = k; c.save(); cam(c, 540, 700, 2.4); c.drawImage(SETS.hall.bg, 0, 0); c.restore(); c.fillStyle = 'rgba(60,10,20,0.35)'; c.fillRect(0, 0, W, H); sceptre(c, 1400, 2200, 540 - 100, 600); sparkles(c, 440, 600, 200, 1, 5, t); c.restore(); }
  flash(c, t, [20.8], '#fff0c0', .1, .45);
  chapterCard(c, t, '2', 'GROOM OF THE STOOL', 20.95, 23.8, '#a8203a');
});
shot(22.4, 24.0, 'G2 fanfare + court bows', 'cut', (c, t) => {
  hallScene(c, t, 1.08, 1000);
  const notes = [22.4, 22.5, 22.6, 22.7], shouts = vocIn(23.1, 24.0);
  c.save(); cam(c, 540, 1000, 1.08);
  // trumpeters on the balcony
  for (const [x, f] of [[250, 1], [830, -1]]) { const tp = hit(t, notes, .14); c.save(); c.translate(x, 700); c.scale(f, 1); rrect(c, -110, 40, 220, 50, 8, '#c8a040', 4); drawChar(c, CAST.servant, { x: 0, y: 80, s: .5, f: 1, turn: .6, shR: 1.6, elR: .1, shL: 1.5, elL: .2, expr: { mouth: 'o', open: .5, eye: .6 + tp * .5, brow: tp } }, t); line(c, [[40, -130], [200, -160 - tp * 10]], 10, '#f0c040'); ell(c, 210, -162, 26, 34, '#f0c040', 4); poly(c, [[60, -120], [160, -150], [170, -100], [70, -100]], '#b0202c', 3); c.restore(); }
  // guards snap halberds one per fanfare note
  [[150, 1500, 1], [930, 1500, -1], [300, 1450, 1], [780, 1450, -1]].forEach(([x, y, f], i) => { const up = E.back(clamp((t - notes[i]) / .12)); drawChar(c, GUARDS[i], { x, y, s: .72, f, turn: .45, shR: .25 + up * .4, elR: -.2, handR: 'hold', lean: -up * .06, expr: { mouth: up > .5 ? 'flat' : 'o', eye: 1 + up * .2, brow: up, lookX: f > 0 ? .6 : -.6 }, hold: halberd(up) }, t); });
  // courtiers bow in a wave on the shouts
  COURT.forEach((ch, i) => { const s0 = shouts[i % shouts.length] ?? 23.2; const bow = clamp((t - s0) / .2) * (1 - clamp((t - s0 - .5) / .3)); drawChar(c, ch, { x: 120 + i * 210, y: 1780, s: .9, f: i < 2 ? 1 : -1, turn: .4, lean: bow * .7, shR: bow * .9 + .2, elR: 1.2 * bow + .2, head: bow * .3, expr: { mouth: bow > .3 ? 'o' : 'smile', open: .4, eye: blink(t, i), lookX: i < 2 ? .5 : -.5 } }, t); });
  // the king tosses coins over the court
  const ct = 23.4; if (t > ct) for (let i = 0; i < 14; i++) { const r = rng(i * 13), u = (t - ct) / 1.0; const x = 540 + (r() - .5) * 900 * u, y = 1050 - Math.sin(clamp(u) * PI) * 400 * (0.6 + r() * .6) + E.in(clamp(u)) * 500; if (u < 1.2) coin(c, x, y, 22, t * 15 + i); }
  drawChar(c, CAST.king, { x: 540, y: 1650, s: 1.05, f: 1, turn: .05, shR: 2.4, elR: .2, handR: 'hold', shL: t > ct - .1 ? 2.5 : .3, elL: .2, handL: 'open', expr: { mouth: 'grin', open: .6, eye: 1, brow: 1 }, hold: holdSceptre(.3) }, t);
  c.restore();
});
function privyScene(c, t, z = 1, cx = 540, cy = 960) {
  c.save(); cam(c, cx, cy, z); c.drawImage(SETS.privy.bg, 0, 0);
  lightShafts(c, 700, 0, .25, 260, 1700, '#ffe8b0', .13);
  candle(c, 140, 1520, 160, t, 1); candle(c, 940, 1520, 160, t, 2);
  c.restore();
}
shot(24.0, 25.6, 'G3 the ceremony', 'cut', (c, t) => {
  privyScene(c, t, 1.0);
  const bow = clamp((t - 24.8) / .25) * (1 - clamp((t - 25.25) / .25));
  c.save();
  // spotlight
  c.save(); c.globalCompositeOperation = 'lighter'; c.fillStyle = rg(c, 540, 1350, 50, 650, [[0, 'rgba(255,230,160,0.3)'], [1, 'rgba(0,0,0,0)']]); c.fillRect(0, 0, W, H); c.restore();
  closeStool(c, 700, 1540, .95, 0, .7 + .3 * Math.sin(t * 6));
  sparkles(c, 700, 1300, 300, 1, 2, t);
  drawChar(c, CAST.groom, { x: 330, y: 1700, s: 1.15, f: 1, turn: .2, lean: bow * .55 - .05, shR: .6 + bow * 1.4, elR: 1.0 - bow * .8, handR: 'open', shL: -.4 - bow * .6, elL: .4, hipR: .35 * bow, kneeR: .2, head: -.12 + bow * .2,
    expr: { mouth: 'smirk', lids: .35, eye: blink(t, 3), lookX: .9, brow: .5, blush: .3 } }, t);
  c.restore();
  subtitle(c, t, 'His job was to assist the king\nwith his *toilet.*', 24.0, 27.0, { size: 58 });
});
shot(25.6, 27.2, 'G4 comedic reveal', 'cut', (c, t) => {
  const lt = t - 25.6;
  const cy = key(lt, [[0, 820], [.5, 1250, 'io']]), z = key(lt, [[0, 1.6], [.5, 1.25, 'io'], [1.6, 1.15]]);
  privyScene(c, t, z, 540, cy);
  c.save(); cam(c, 540, cy, z);
  const fan = [25.6, 25.7, 25.8, 25.9, 26.0, 26.1];
  const lid = E.back(clamp((t - 25.9) / .25));
  closeStool(c, 700, 1540, .95, lid, 1);
  if (lid > .5) { lightShafts(c, 700, 1300, PI, 240, 600, '#fff4c0', .2 * lid); }
  drawChar(c, CAST.groom, { x: 330, y: 1700, s: 1.15, f: 1, turn: .2, shR: 1.5 + hit(t, fan, .1) * .3, elR: .3, handR: 'open', shL: -.3, elL: .3, lean: -.08,
    expr: { mouth: 'grin', open: .4, lids: .3, eye: 1, lookX: .9, brow: .8 } }, t);
  // maids peek from the curtains on "OOOH"
  const ooh = E.back(clamp((t - 26.35) / .2));
  if (ooh > 0) { drawChar(c, CAST.noble2, { x: 60 + ooh * 70, y: 1450, s: .8, f: 1, turn: .5, expr: { mouth: 'o', open: .9, eye: 1.3, brow: 1.6, lookX: 1 } }, t); drawChar(c, CAST.servant, { x: 1030 - ooh * 70, y: 1450, s: .8, f: -1, turn: .5, shR: 1.4, elR: 1.6, expr: { mouth: 'o', open: .9, eye: 1.3, brow: 1.6, lookX: 1 } }, t); }
  c.restore();
  subtitle(c, t, 'His job was to assist the king\nwith his *toilet.*', 24.0, 27.0, { size: 58 });
});
shot(27.2, 28.8, 'G5 elegant duties', 'cut', (c, t) => {
  privyScene(c, t, 1.05, 540, 1000);
  const lt = t - 27.2, x = lerp(180, 900, lt / 1.6);
  const jete = hit(t, [27.6, 28.4], .25);
  const wp = walkPose(t, { amp: 1.1, strut: 1.4 });
  c.save(); cam(c, 540, 1000, 1.05);
  // two surprised servants in the back
  drawChar(c, CAST.servant, { x: 860, y: 1550, s: .75, f: -1, turn: .4, shR: 2.5, elR: .4, shL: 2.4, elL: .5, expr: { mouth: 'o', open: .7, eye: 1.2, brow: 1.5, lookX: -1 } }, t);
  drawChar(c, townsfolk(931, 'vil'), { x: 980, y: 1560, s: .72, f: -1, turn: .3, shR: 1.4, elR: 1.8, expr: { mouth: 'teeth', eye: 1.1, brow: 1.2, lookX: -1 } }, t);
  drawChar(c, CAST.groom, merge({ x, y: 1720, s: 1.1, f: 1, turn: .35 }, wp, { air: jete * 90 + wp.air, hipR: wp.hipR + jete * .7, hipL: wp.hipL - jete * .6, kneeL: jete * .2 + wp.kneeL,
    shR: 2.0, elR: 1.6, handR: 'open', shL: 1.5 + jete, elL: .2, handL: 'open', expr: { mouth: 'smile', lids: .4, eye: 1, lookX: .7, brow: .6 }, hold: holdLinen }), t);
  c.restore();
});
shot(28.8, 30.4, 'G6 doors flung open + reactions', 'cut', (c, t) => {
  const notes = [28.8, 28.9, 29.0, 29.1], shouts = vocIn(29.5, 30.4);
  const open = clamp((t - 28.85) / .35);
  hallScene(c, t, 1.0);
  c.save();
  drawChar(c, CAST.king, { x: 540, y: 1500, s: .85, f: 1, turn: .05, shR: 2.2, elR: .3, handR: 'hold', shL: 2.0 * open, elL: .4, expr: { mouth: 'grin', open: .6, eye: 1, brow: 1 }, hold: holdSceptre(.3) }, t);
  // servants pop up on the shouts
  shouts.forEach((s0, i) => { const k = E.back(clamp((t - s0) / .18)); if (k > 0) { const x = [150, 930, 320, 760][i % 4]; drawChar(c, COURT[(i + 2) % COURT.length], { x, y: 1980 - k * 160, s: .95, f: x < 540 ? 1 : -1, turn: .4, shR: 2.7, elR: .3, shL: 2.6, elL: .3, expr: { mouth: 'shout', open: 1, eye: 1.3, brow: 1.8, lookX: x < 540 ? .6 : -.6 } }, t); } });
  c.restore();
  doors(c, open);
  // the groom in the foreground throws the doors open with a flourish
  drawChar(c, CAST.groom, { x: 540, y: 2080, s: 1.4, f: 1, turn: .9, shR: 2.6 * open + .4, elR: .2, handR: 'open', shL: 2.4 * open + .3, elL: .2, handL: 'open', lean: -.1, expr: { mouth: 'grin', open: .6, eye: 1, lookX: .3 } }, t);
  if (t > 29.75) for (let i = 0; i < 18; i++) { const r = rng(i * 7 + 3), u = (t - 29.8) / .8; if (u > 0 && u < 1.3) coin(c, 540 + (r() - .5) * 1000 * u, 600 + E.in(clamp(u)) * 1300 - Math.sin(clamp(u) * PI) * 300 * r(), 20, t * 12 + i); }
});
shot(30.4, 32.0, 'G7 transformation: prestige', 'punch', (c, t) => {
  privyScene(c, t, 1.12, 540, 1050);
  const lt = t - 30.4, spin = clamp(lt / .45), rich = lt > .22;
  c.save(); cam(c, 540, 1050, 1.12);
  c.save(); c.globalCompositeOperation = 'lighter'; c.fillStyle = rg(c, 540, 1300, 30, 700, [[0, `rgba(255,220,140,${.45 * (1 - clamp((lt - .5) / .6))})`], [1, 'rgba(0,0,0,0)']]); c.fillRect(0, 0, W, H); c.restore();
  const f = Math.cos(spin * TAU * 2) >= 0 ? 1 : -1;
  drawChar(c, rich ? CAST.groomRich : CAST.groom, { x: 540, y: 1760, s: 1.25, f, turn: spin < 1 ? Math.abs(Math.sin(spin * TAU * 2)) : .15, air: Math.sin(spin * PI) * 120,
    shR: spin < 1 ? 2.8 : .9, elR: spin < 1 ? .2 : 1.3, shL: spin < 1 ? 2.8 : -.5, elL: .3, handR: 'open', lean: spin >= 1 ? -.08 : 0,
    expr: { mouth: spin < 1 ? 'grin' : 'smirk', open: .5, lids: spin < 1 ? 0 : .45, eye: 1, lookX: .1, brow: .6, blush: .4 } }, t);
  sparkles(c, 540, 1300, 400, 1 - clamp((lt - .8) / .6), 8, t);
  // the king's hand places the gold chain
  if (lt > .45) { const k = E.out(clamp((lt - .45) / .45)); drawChar(c, CAST.king, { x: lerp(1350, 1000, k), y: 1800, s: 1.05, f: -1, turn: .3, lean: .15, shR: 1.5, elR: .2, handR: 'open', expr: { mouth: 'grin', open: .4, eye: 1, lookX: -.8, brow: .8 } }, t); }
  c.restore();
  subtitle(c, t, 'Surprisingly, it was a\n*prestigious* position.', 30.4, 33.4);
});
shot(32.0, 33.6, 'G8 whispering secrets', 'cut', (c, t) => {
  privyScene(c, t, 1.25, 540, 1000);
  c.save(); cam(c, 540, 1000, 1.25);
  const oho = t >= 32.8 && t < 33.35, ha = hit(t, [33.4], .3);
  const shakeB = oho ? Math.sin(t * 40) * .05 : 0;
  drawChar(c, CAST.king, { x: 680, y: 1700, s: 1.0, f: -1, turn: .3, lean: shakeB + (oho ? -.12 : .05), shR: oho ? 1.0 : .3, elR: oho ? 1.5 : .2, shL: .2, head: oho ? -.15 : .12,
    expr: { mouth: oho ? 'grin' : 'o', open: oho ? .9 : .3, eye: oho ? .1 : 1, brow: oho ? 1 : .4, lookX: -.4, lookY: .3 } }, t);
  drawChar(c, CAST.groomRich, { x: 400, y: 1700, s: 1.0, f: 1, turn: .45, lean: .16, shR: 1.9, elR: 1.6, handR: 'open', head: .1, shL: -.3,
    expr: { mouth: oho ? 'grin' : 'smirk', open: .4, lids: .4, eye: 1, lookX: 1, brow: .5 } }, t);
  if (t < 32.8) { c.save(); c.globalAlpha = .9; c.font = '54px Luckiest'; c.textAlign = 'center'; c.lineWidth = 10; c.strokeStyle = '#1a0c08'; c.lineJoin = 'round'; const y = 900 - (t - 32) * 40; c.strokeText('psst...', 560, y); c.fillStyle = '#fff'; c.fillText('psst...', 560, y); c.restore(); }
  c.restore();
  if (ha > .05) speedLines(c, 540, 1000, ha * .5, 21);
  subtitle(c, t, 'Surprisingly, it was a\n*prestigious* position.', 30.4, 33.4);
});
function antechamber(c, t, z = 1) {
  c.save(); cam(c, 540, 960, z);
  c.drawImage(SETS.privy.bg, 0, 0, W, H);
  c.fillStyle = 'rgba(30,8,10,0.35)'; c.fillRect(0, 0, W, H);
  c.drawImage(SETS.door, 0, 0, 540, 1300, 310, 520, 230, 560); c.save(); c.translate(1080, 0); c.scale(-1, 1); c.drawImage(SETS.door, 0, 0, 540, 1300, 310, 520, 230, 560); c.restore();
  c.restore();
}
shot(33.6, 35.2, 'G9 nobles blocked', 'cut', (c, t) => {
  antechamber(c, t);
  const heys = [33.6, 34.4], cross = E.back(clamp((t - 33.6) / .15));
  const k2 = hit(t, heys, .2);
  drawChar(c, GUARDS[0], { x: 380, y: 1520, s: .9, f: 1, turn: .2, shR: .3 + cross * .5, elR: .1, handR: 'hold', expr: { mouth: 'flat', browAng: .9, eye: 1, lookX: .8 }, hold: { R: (cc, J) => { const h = J.handNear; line(cc, [[h[0] - 200, h[1] + 200], [h[0] + 420 * cross, h[1] - 520 + cross * 200]], 14, '#5a3a20'); } } }, t);
  drawChar(c, GUARDS[2], { x: 700, y: 1520, s: .9, f: -1, turn: .2, shR: .3 + cross * .5, elR: .1, handR: 'hold', expr: { mouth: 'flat', browAng: .9, eye: 1, lookX: .8 }, hold: { R: (cc, J) => { const h = J.handNear; line(cc, [[h[0] - 200, h[1] + 200], [h[0] + 420 * cross, h[1] - 520 + cross * 200]], 14, '#5a3a20'); } } }, t);
  const back = hit(t, heys, .3);
  drawChar(c, CAST.noble1, { x: 250 - back * 40, y: 1840, s: 1.15, f: 1, turn: .4, lean: -back * .3, shR: 1.4 + back, elR: .3, handR: 'open', expr: { mouth: back > .3 ? 'o' : 'smile', open: .7, eye: 1 + back * .3, brow: 1.5 * back, lookX: .8 } }, t);
  drawChar(c, CAST.noble2, { x: 850 + back * 40, y: 1850, s: 1.1, f: -1, turn: .4, lean: -back * .25, shR: 1.2 + back, elR: .6, expr: { mouth: back > .3 ? 'o' : 'smile', open: .7, eye: 1 + back * .3, brow: 1.5 * back, lookX: .8 } }, t);
  if (k2 > .2) { c.save(); c.translate(540, 720); c.font = '96px Luckiest'; c.textAlign = 'center'; c.lineWidth = 16; c.strokeStyle = '#1a0c08'; c.lineJoin = 'round'; c.rotate(-.06); c.strokeText('HALT!', 0, 0); c.fillStyle = '#ff5a4a'; c.fillText('HALT!', 0, 0); c.restore(); }
  subtitle(c, t, 'He had *rare private access*\nto the king.', 33.6, 36.6, { size: 60 });
});
shot(35.2, 36.8, 'G10 groom struts through + wink', 'cut', (c, t) => {
  antechamber(c, t);
  const lt = t - 35.2, open = E.back(clamp((t - 35.2) / .2));
  const strut = walkPose(t, { amp: .9, strut: 1.5 });
  drawChar(c, CAST.king, { x: 540, y: 1250, s: .6, f: 1, turn: .05, shR: 2.2 * clamp((t - 35.9) / .2), elR: .3, shL: 2.2 * clamp((t - 35.9) / .2), elL: .3, expr: { mouth: 'grin', open: .6, eye: 1, brow: 1 } }, t);
  for (const [x, f, g] of [[300, 1, GUARDS[0]], [780, -1, GUARDS[2]]]) drawChar(c, g, { x, y: 1520, s: .9, f, turn: .2, shR: .3 + (1 - open) * .5, elR: .1, lean: -.05 * open, expr: { mouth: 'flat', eye: 1, lookX: -f * .5 }, hold: halberd(open) }, t);
  const toCam = t > 36.45;
  const gx = lerp(150, 540, clamp(lt / 1.1));
  drawChar(c, CAST.groomRich, merge({ x: gx, y: 1880, s: 1.35, f: 1 }, toCam ? { turn: 0, shR: .3, elR: .4, shL: -.3, expr: { mouth: 'smirk', lids: .55, eye: 1, lookX: 0, brow: .8, blush: .4 } } : merge(strut, { turn: .45, shR: 1.0, elR: 1.6, handR: 'open', expr: { mouth: 'smirk', lids: .5, eye: 1, lookX: .6, brow: .4 } })), t);
  drawChar(c, CAST.noble1, { x: 1000, y: 1950, s: 1.15, f: -1, turn: .4, expr: { mouth: 'o', open: .8, eye: 1.2, brow: 1.4, lookX: -1 } }, t);
  if (toCam) sparkles(c, 600, 640, 60, hit(t, [36.6], .3), 3, t);
  subtitle(c, t, 'He had *rare private access*\nto the king.', 33.6, 36.6, { size: 60 });
});
// G11: TA-DA, then a coin flips to camera and darkens into the funeral coin
shot(36.8, 38.4, 'G11 ta-da + coin match-cut', 'cut', (c, t) => {
  const lt = t - 36.8;
  const dark = clamp((t - 37.55) / .65);
  if (dark < 1) {
    privyScene(c, t, 1.1, 540, 1050);
    c.save(); cam(c, 540, 1050, 1.1);
    const tada = E.back(clamp(lt / .15));
    drawChar(c, CAST.king, { x: 700, y: 1750, s: 1.0, f: -1, turn: .1, shR: 2.6 * tada, elR: .2, shL: 2.6 * tada, elL: .2, handR: 'open', handL: 'open', expr: { mouth: 'grin', open: .8, eye: 1, brow: 1.2 } }, t);
    drawChar(c, CAST.groomRich, { x: 380, y: 1760, s: 1.05, f: 1, turn: .1, shR: 2.4 * tada, elR: .2, shL: t > 37.15 ? 2.2 : 2.4 * tada, elL: .2, handR: 'open', handL: 'open', air: tada * 30 * (1 - clamp(lt / .4)), expr: { mouth: 'smirk', lids: .45, eye: 1, lookX: 0, brow: .8, blush: .5 } }, t);
    c.restore();
    c.save(); c.globalAlpha = dark; c.fillStyle = '#0a0812'; c.fillRect(0, 0, W, H); c.restore();
  } else { c.fillStyle = '#0a0812'; c.fillRect(0, 0, W, H); }
  // the coin flies at the camera
  if (t > 37.15) {
    const u = clamp((t - 37.15) / .6), r = lerp(20, 520, E.in(u));
    const x = lerp(330, 540, u), y = lerp(870, 960, u);
    const col = mix('#f0c040', '#a8a8b0', dark);
    coin(c, x, y, r, (t - 37.15) * 16, col, dark > .5 ? 'cross' : 'crown');
    if (dark > .3) { c.save(); c.globalAlpha = dark * .8; glow(c, x, y, r * 1.6, 'rgba(160,170,255,0.25)'); c.restore(); }
  }
  if (dark > .5) { const k = (dark - .5) * 2; c.save(); c.globalAlpha = k; candle(c, 840, 1600, 220, t, 4, 1.2); bread(c, 300, 1500, 1.4); c.restore(); }
});
