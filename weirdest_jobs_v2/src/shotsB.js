// ===================================================================== shotsB.js  (Groom of the Stool 20.8 - 38.4)
'use strict';
const KING = CAST2.king, TOM = CAST2.groom, TOMR = CAST2.groomRich, GDS = CAST2.guards;
const sceptreHold = (a = .3, len = 380) => ({ R: (c, J) => { const h = J.handN; sceptre(c, h[0] - Math.sin(a) * 90, h[1] + Math.cos(a) * 90, h[0] + Math.sin(a) * len, h[1] - Math.cos(a) * len); } });
const halberd2 = (raise, side = 'R') => ({ [side === 'R' ? 'Rb' : 'L']: (c, J) => { const h = side === 'R' ? J.handN : J.handF, a = lerp(.35, 0, raise); const x0 = h[0] - Math.sin(a) * 260, y0 = h[1] + Math.cos(a) * 260, x1 = h[0] + Math.sin(a) * 620, y1 = h[1] - Math.cos(a) * 620;
  line(c, [[x0, y0], [x1, y1]], 18, OL); line(c, [[x0, y0], [x1, y1]], 12, '#7a4a28'); c.save(); c.translate(x1, y1); c.rotate(a); poly(c, [[0, -70], [14, 0], [-14, 0]], '#d8dce8', 4); blob(c, [[6, -14], [70, -40], [74, 26], [6, 12]], '#d8dce8', 4); poly(c, [[-6, -24], [-42, -6], [-6, 6]], '#d8dce8', 4); c.restore(); } });
const COURT2 = [CAST2.noble, CAST2.lady, CAST2.servant, villager(901, 'court'), villager(905, 'court'), villager(907, 'court')];
function hallBG(c, t, z = 1, cy = 960) {
  c.save(); cam(c, 540, cy, z); c.drawImage(SETS.hall.bg, 0, 0); lightShafts(c, 540, 330, 0, 300, 1500, '#ffe8b0', .16); motes(c, t, 21, 50, '#ffe6a8', .55, 15); c.restore();
}
function doors2(c, open) {
  if (open >= 1) return;
  const w = 540 * (1 - E.out(open));
  c.drawImage(SETS.door, 0, 0, 540, 1300, 0, 300, w, 1620);
  c.save(); c.translate(1080, 0); c.scale(-1, 1); c.drawImage(SETS.door, 0, 0, 540, 1300, 0, 300, w, 1620); c.restore();
}
shot(20.8, 22.4, 'G1 the doors burst open, the king strides in', 'cut', (c, t) => {
  const lt = t - 20.8;
  hallBG(c, t);
  const prog = clamp((lt - .2) / 1.4);
  [[200, 1480, .78, 1], [880, 1480, .78, -1], [80, 1760, 1.05, 1], [1000, 1760, 1.05, -1]].forEach(([x, y, s, f], i) =>
    drawChar2(c, GDS[i], { x, y, s, f, view: 'q', shR: .35, elR: -.1, handR: 'grip', expr: E2('stern', t, i + 5, { lookX: .6 }), hold: halberd2(1) }, t));
  const w = walk2(t, { amp: .55, bob: 1.6 });
  drawChar2(c, KING, mergeP({ x: 540, y: lerp(1400, 1880, E.io(prog)), s: lerp(.85, 1.45, E.io(prog)), f: 1, view: 'f' }, w, { hipR: w.hipR * .3, hipL: w.hipL * .3, shR: 2.55, elR: .1, handR: 'grip', shL: -.35 + Math.sin(t * 7.85) * .2, elL: .4, handL: 'open', lean: 0, expr: E2('grin', t, 9, { lookX: 0, lookY: .2 }), hold: sceptreHold(.3) }), t);
  doors2(c, clamp(lt / .3));
  if (lt < .35) { const k = 1 - E.in(lt / .35); c.save(); c.globalAlpha = k; c.save(); cam(c, 540, 700, 2.4); c.drawImage(SETS.hall.bg, 0, 0); c.restore(); sceptre(c, 1400, 2200, 440, 600); sparkles(c, 440, 600, 200, 1, 5, t); c.restore(); }
  flash(c, t, [20.8], '#fff0c0', .1, .4);
  chapter2(c, t, '2', 'GROOM OF THE STOOL', 20.95, 23.8, 'groom');
}, 'groom');
shot(22.4, 24.0, 'G2 fanfare: guards snap, the court bows', 'cut', (c, t) => {
  hallBG(c, t, 1.08, 1000);
  const notes = [22.4, 22.5, 22.6, 22.7], shouts = vocIn(23.1, 24.0);
  c.save(); cam(c, 540, 1000, 1.08);
  for (const [x, f] of [[230, 1], [850, -1]]) { const tp = hit(t, notes, .14); c.save(); c.translate(x, 700); c.scale(f, 1); rrect(c, -120, 40, 240, 50, 8, '#e0b040', 4);
    drawChar2(c, CAST2.servant, { x: 0, y: 70, s: .48, f: 1, view: 'p', shR: 1.55, elR: .2, shL: 1.45, elL: .3, handR: 'grip', handL: 'grip', expr: X('ooh', { eye: .7 + tp * .4 }) }, t);
    line(c, [[60, -195], [220, -230 - tp * 10]], 10, '#f0c040'); ell(c, 232, -232, 26, 34, '#f0c040', 4); poly(c, [[80, -186], [180, -214], [190, -164], [90, -164]], '#c8203a', 3); c.restore(); }
  [[130, 1520, 1], [950, 1520, -1], [300, 1460, 1], [780, 1460, -1]].forEach(([x, y, f], i) => { const up = E.back(clamp((t - notes[i]) / .12));
    drawChar2(c, GDS[i], { x, y, s: .85, f, view: 'q', shR: .35 + up * .4, elR: -.1, handR: 'grip', lean: -up * .05, expr: X(up > .5 ? 'stern' : 'ooh', { lookX: .6 }), hold: halberd2(up) }, t); });
  COURT2.forEach((ch, i) => { const s0 = shouts[i % Math.max(1, shouts.length)] ?? 23.2; const bow = clamp((t - s0) / .2) * (1 - clamp((t - s0 - .5) / .3));
    drawChar2(c, ch, { x: 110 + i * 172, y: 1830, s: .98, f: i < 3 ? 1 : -1, view: bow > .3 ? 'p' : 'q', lean: bow * .75, shR: bow * 1.1 + .2, elR: 1.3 * bow + .3, handR: 'open', head: bow * .25, expr: X(bow > .3 ? 'ooh' : 'happy', { lookX: .5 }) }, t); });
  const ct = 23.4; if (t > ct) for (let i = 0; i < 14; i++) { const r = rng(i * 13), u = (t - ct) / 1.0; const x = 540 + (r() - .5) * 900 * u, y = 1050 - Math.sin(clamp(u) * PI) * 400 * (.6 + r() * .6) + E.in(clamp(u)) * 500; if (u < 1.2) coin(c, x, y, 22, t * 15 + i); }
  drawChar2(c, KING, { x: 540, y: 1700, s: 1.15, f: 1, view: 'f', shR: 2.5, elR: .2, handR: 'grip', shL: t > ct - .1 ? 2.6 : .3, elL: .2, handL: 'spread', expr: X('laugh'), hold: sceptreHold(.3) }, t);
  c.restore();
  shouts.forEach((s, i) => popWord(c, t, VOC.find(v => Math.abs(v[0] - s) < 1e-3)[1], s, 220 + (i * 211) % 640, 520 + (i % 2) * 90, 96, ['#ffd23c', '#fff3d6'][i % 2]));
}, 'groom');
function privy2(c, t, z = 1, cx = 540, cy = 960) { privyBG(c, t, z, cx, cy); }
shot(24.0, 25.6, 'G3 the solemn ceremony', 'cut', (c, t) => {
  privy2(c, t, 1.0);
  const bow = clamp((t - 24.8) / .25) * (1 - clamp((t - 25.25) / .25));
  c.save(); c.globalCompositeOperation = 'lighter'; c.fillStyle = rg(c, 640, 1350, 50, 650, [[0, 'rgba(255,230,160,0.35)'], [1, 'rgba(0,0,0,0)']]); c.fillRect(0, 0, W, H); c.restore();
  closeStool(c, 720, 1560, 1.0, 0, .7 + .3 * Math.sin(t * 6));
  sparkles(c, 720, 1300, 300, 1, 2, t);
  drawChar2(c, TOM, { x: 320, y: 1820, s: 1.5, f: 1, view: bow > .2 ? 'p' : 'q', lean: bow * .55 - .05, shR: .7 + bow * 1.3, elR: 1.1 - bow * .8, handR: 'open', shL: -.4 - bow * .6, elL: .4, handL: 'spread', hipR: .35 * bow, kneeR: .2, head: -.1 + bow * .2,
    expr: E2('smug', t, 3, { lookX: .9 }) }, t);
  caption(c, t, 'His job was to assist the king\nwith his *toilet.*', 24.0, 27.0, { size: 56, y: 330 });
}, 'groom');
shot(25.6, 27.2, 'G4 the reveal', 'cut', (c, t) => {
  const lt = t - 25.6, cy = key(lt, [[0, 800], [.5, 1250, 'io']]), z = key(lt, [[0, 1.65], [.5, 1.25, 'io'], [1.6, 1.15]]);
  privy2(c, t, z, 540, cy);
  c.save(); cam(c, 540, cy, z);
  const fan = [25.6, 25.7, 25.8, 25.9, 26.0, 26.1], lid = E.back(clamp((t - 25.9) / .25));
  closeStool(c, 720, 1560, 1.0, lid, 1);
  if (lid > .5) lightShafts(c, 720, 1300, PI, 240, 600, '#fff4c0', .22 * lid);
  drawChar2(c, TOM, { x: 320, y: 1820, s: 1.5, f: 1, view: 'q', shR: 1.55 + hit(t, fan, .1) * .3, elR: .3, handR: 'spread', shL: -.3, elL: .3, lean: -.08, expr: X('grin', { lookX: .9 }) }, t);
  const ooh = E.back(clamp((t - 26.35) / .2));
  if (ooh > 0) { drawChar2(c, CAST2.lady, { x: 40 + ooh * 90, y: 1500, s: .95, f: 1, view: 'q', shR: 1.6, elR: 1.7, handR: 'open', expr: X('ooh', { lookX: 1 }) }, t);
    drawChar2(c, CAST2.servant, { x: 1040 - ooh * 90, y: 1500, s: .95, f: -1, view: 'q', shR: 1.6, elR: 1.7, handR: 'open', expr: X('ooh', { lookX: 1 }) }, t); }
  c.restore();
  popWord(c, t, 'OOOH!', 26.4, 540, 620, 130);
  caption(c, t, 'His job was to assist the king\nwith his *toilet.*', 24.0, 27.0, { size: 56, y: 330 });
}, 'groom');
shot(27.2, 28.8, 'G5 elegant duties', 'cut', (c, t) => {
  privy2(c, t, 1.05, 540, 1000);
  const lt = t - 27.2, x = lerp(170, 880, lt / 1.6), jete = hit(t, [27.6, 28.4], .25);
  const w = walk2(t, { amp: 1.1, bob: 1.5 });
  c.save(); cam(c, 540, 1000, 1.05);
  drawChar2(c, CAST2.servant, { x: 880, y: 1600, s: .9, f: -1, view: 'q', shR: 2.5, elR: .4, shL: 2.4, elL: .5, handR: 'spread', handL: 'spread', expr: X('surprise', { lookX: 1 }) }, t);
  drawChar2(c, villager(931, 'court'), { x: 1010, y: 1610, s: .88, f: -1, view: 'q', shR: 1.5, elR: 1.8, handR: 'open', expr: X('fear', { lookX: 1 }) }, t);
  drawChar2(c, TOM, mergeP({ x, y: 1860, s: 1.4, f: 1, view: 'p' }, w, { air: jete * 100 + w.air, hipR: w.hipR + jete * .8, hipL: w.hipL - jete * .7, shR: 2.05, elR: 1.7, handR: 'open', wrR: -.8, shL: 1.5 + jete, elL: .2, handL: 'spread',
    expr: X('smug', { lookX: .7 }), hold: { R: (cc, J) => { rrect(cc, J.handN[0] - 70, J.handN[1] - 140, 140, 110, 12, '#f6f1e4', 4); line(cc, [[J.handN[0] - 64, J.handN[1] - 100], [J.handN[0] + 64, J.handN[1] - 100]], 3, '#d8a83a'); line(cc, [[J.handN[0] - 64, J.handN[1] - 70], [J.handN[0] + 64, J.handN[1] - 70]], 3, '#d8a83a'); } } }), t);
  c.restore();
}, 'groom');
shot(28.8, 30.4, 'G6 Thomas throws open the doors', 'cut', (c, t) => {
  const shouts = vocIn(29.5, 30.4), open = clamp((t - 28.85) / .35);
  hallBG(c, t, 1.0);
  drawChar2(c, KING, { x: 540, y: 1520, s: .95, f: 1, view: 'f', shR: 2.3, elR: .3, handR: 'grip', shL: 2.0 * open, elL: .4, handL: 'spread', expr: X('laugh'), hold: sceptreHold(.3) }, t);
  shouts.forEach((s0, i) => { const k = E.back(clamp((t - s0) / .18)); if (k > 0) { const x = [150, 930, 320, 760][i % 4];
    drawChar2(c, COURT2[(i + 2) % COURT2.length], { x, y: 2050 - k * 170, s: 1.05, f: x < 540 ? 1 : -1, view: 'q', shR: 2.7, elR: .3, shL: 2.6, elL: .3, handR: 'spread', handL: 'spread', expr: X('surprise', { lookX: .6 }) }, t); } });
  doors2(c, open);
  drawChar2(c, TOM, { x: 540, y: 2150, s: 1.65, f: 1, view: 'b', shR: 2.6 * open + .4, elR: .2, handR: 'spread', shL: 2.4 * open + .3, elL: .2, handL: 'spread', lean: -.1 }, t);
  if (t > 29.75) for (let i = 0; i < 18; i++) { const r = rng(i * 7 + 3), u = (t - 29.8) / .8; if (u > 0 && u < 1.3) coin(c, 540 + (r() - .5) * 1000 * u, 600 + E.in(clamp(u)) * 1300 - Math.sin(clamp(u) * PI) * 300 * r(), 20, t * 12 + i); }
}, 'groom');
shot(30.4, 32.0, 'G7 transformation: prestige', 'punch', (c, t) => {
  privy2(c, t, 1.12, 540, 1050);
  const lt = t - 30.4, spin = clamp(lt / .5), rich = lt > .25;
  c.save(); cam(c, 540, 1050, 1.12);
  c.save(); c.globalCompositeOperation = 'lighter'; c.fillStyle = rg(c, 540, 1300, 30, 700, [[0, `rgba(255,220,140,${.45 * (1 - clamp((lt - .5) / .6))})`], [1, 'rgba(0,0,0,0)']]); c.fillRect(0, 0, W, H); c.restore();
  const views = ['q', 'p', 'b', 'p', 'q', 'f'], vi = Math.min(5, Math.floor(spin * 6));
  drawChar2(c, rich ? TOMR : TOM, { x: 540, y: 1840, s: 1.5, f: vi === 3 ? -1 : 1, view: spin < 1 ? views[vi] : 'q', air: Math.sin(spin * PI) * 120,
    shR: spin < 1 ? 2.8 : .9, elR: spin < 1 ? .2 : 1.4, shL: spin < 1 ? 2.8 : -.5, elL: .3, handR: spin < 1 ? 'spread' : 'open', handL: 'spread', lean: spin >= 1 ? -.08 : 0,
    expr: X(spin < 1 ? 'laugh' : 'smug', { lookX: .1 }) }, t);
  sparkles(c, 540, 1300, 420, 1 - clamp((lt - .8) / .6), 8, t);
  if (lt > .45) { const k = E.out(clamp((lt - .45) / .45)); drawChar2(c, KING, { x: lerp(1400, 1020, k), y: 1880, s: 1.2, f: -1, view: 'p', lean: .15, shR: 1.5, elR: .2, handR: 'open', expr: X('grin', { lookX: 1 }) }, t); }
  c.restore();
  caption(c, t, 'Surprisingly, it was a\n*prestigious* position.', 30.4, 33.4);
}, 'groom');
shot(32.0, 33.6, 'G8 the whisper and the royal laugh', 'cut', (c, t) => {
  privy2(c, t, 1.3, 540, 1080);
  const oho = t >= 32.8 && t < 33.35, ha = t >= 33.35;
  const lean = key(t, [[32, 0], [32.25, .22, 'out'], [32.75, .22], [32.85, -.05, 'back']]);
  const shakeB = oho ? Math.sin(t * 42) * .05 : 0;
  drawChar2(c, KING, { x: 735, y: 2120, s: 1.65, f: -1, view: ha ? 'q' : 'p', lean: oho ? -.14 + shakeB : .03, head: oho ? -.2 : .05,
    shR: oho ? .9 : ha ? 2.3 : .35, elR: oho ? 1.6 : ha ? .5 : .3, handR: oho || ha ? 'spread' : 'relaxed', shL: oho ? .7 : ha ? 2.4 : -.1, elL: oho ? 1.7 : .4, handL: 'spread', air: oho ? Math.abs(Math.sin(t * 21)) * 12 : 0,
    expr: oho ? X('laugh') : ha ? X('shout') : t < 32.4 ? X('neutral', { lookX: -.2 }) : X('surprise', { lookX: .6 }) }, t);
  drawChar2(c, TOMR, { x: 330, y: 2130, s: 1.6, f: 1, view: ha ? 'q' : 'p', lean: ha ? -.05 : lean, head: ha ? 0 : .08,
    shR: ha ? 2.5 : 2.0, elR: ha ? .3 : 2.35, handR: ha ? 'spread' : 'open', wrR: ha ? 0 : -.6, shL: ha ? 2.4 : -.3, elL: .5, handL: 'spread',
    expr: oho ? X('laugh') : ha ? X('grin') : X('smug', { lookX: 1 }) }, t);
  if (t < 32.8) { const a = clamp((t - 32.15) / .2) * (1 - clamp((t - 32.7) / .1)); c.save(); c.globalAlpha = a; c.font = '62px Slab'; c.textAlign = 'center'; c.lineWidth = 12; c.strokeStyle = '#16204a'; c.lineJoin = 'round'; c.strokeText('psst...', 540, 640); c.fillStyle = '#fff3d6'; c.fillText('psst...', 540, 640); c.restore(); }
  popWord(c, t, 'HO HO HO!', 32.8, 640, 640, 100, '#ffd23c', .06);
  caption(c, t, 'Surprisingly, it was a\n*prestigious* position.', 30.4, 33.4);
}, 'groom');
function antechamber2(c, t) {
  c.drawImage(SETS.privy.bg, 0, 0, W, H); c.fillStyle = 'rgba(60,10,20,0.2)'; c.fillRect(0, 0, W, H);
  c.drawImage(SETS.door, 0, 0, 540, 1300, 310, 520, 230, 560); c.save(); c.translate(1080, 0); c.scale(-1, 1); c.drawImage(SETS.door, 0, 0, 540, 1300, 310, 520, 230, 560); c.restore();
}
shot(33.6, 35.2, 'G9 HALT! the nobles are blocked', 'cut', (c, t) => {
  antechamber2(c, t);
  const heys = [33.6, 34.4], cross = E.back(clamp((t - 33.6) / .15)), back = hit(t, heys, .3);
  const xh = (cc, J) => { const h = J.handN; line(cc, [[h[0] - 220, h[1] + 220], [h[0] + 440 * cross, h[1] - 560 + cross * 220]], 16, '#7a4a28'); };
  drawChar2(c, GDS[0], { x: 380, y: 1560, s: .98, f: 1, view: 'q', shR: .35 + cross * .5, elR: .1, handR: 'grip', expr: X('stern', { lookX: .8 }), hold: { Rb: xh } }, t);
  drawChar2(c, GDS[2], { x: 700, y: 1560, s: .98, f: -1, view: 'q', shR: .35 + cross * .5, elR: .1, handR: 'grip', expr: X('stern', { lookX: .8 }), hold: { Rb: xh } }, t);
  drawChar2(c, CAST2.noble, { x: 230 - back * 40, y: 1950, s: 1.4, f: 1, view: 'p', lean: -back * .3, shR: 1.4 + back, elR: .3, handR: 'spread', expr: X(back > .3 ? 'fear' : 'happy', { lookX: .8 }) }, t);
  drawChar2(c, CAST2.lady, { x: 870 + back * 40, y: 1960, s: 1.35, f: -1, view: 'p', lean: -back * .25, shR: 1.2 + back, elR: .6, handR: 'spread', expr: X(back > .3 ? 'surprise' : 'happy', { lookX: .8 }) }, t);
  popWord(c, t, 'HALT!', 33.62, 540, 680, 130, '#ff5a4a'); popWord(c, t, 'HALT!', 34.42, 540, 680, 130, '#ff5a4a');
  caption(c, t, 'He had *rare private access*\nto the king.', 33.6, 36.6, { size: 58, y: 330 });
}, 'groom');
shot(35.2, 36.8, 'G10 Thomas struts past - and winks', 'cut', (c, t) => {
  antechamber2(c, t);
  const lt = t - 35.2, open = E.back(clamp((t - 35.2) / .2)), toCam = t > 36.45;
  drawChar2(c, KING, { x: 540, y: 1300, s: .62, f: 1, view: 'f', shR: 2.3 * clamp((t - 35.9) / .2), elR: .3, shL: 2.3 * clamp((t - 35.9) / .2), elL: .3, handR: 'spread', handL: 'spread', expr: X('grin') }, t);
  for (const [x, f, g] of [[300, 1, GDS[0]], [780, -1, GDS[2]]]) drawChar2(c, g, { x, y: 1560, s: .98, f, view: 'q', shR: .35 + (1 - open) * .5, elR: .1, handR: 'grip', lean: -.05 * open, expr: X('stern', { lookX: -f * .5 }), hold: halberd2(open) }, t);
  const gx = lerp(120, 540, clamp(lt / 1.1)), w = walk2(t, { amp: .9, bob: 1.6 });
  drawChar2(c, TOMR, mergeP({ x: gx, y: 2000, s: 1.6, f: 1 }, toCam ? { view: 'f', shR: .3, elR: .5, shL: -.3, handR: 'relaxed', expr: X('smug', { eye: hit(t, [36.6], .25) > .3 ? .2 : .55, lookX: 0 }) } : mergeP(w, { view: 'p', shR: 1.0, elR: 1.7, handR: 'open', wrR: -.6, expr: X('smug', { lookX: .6 }) })), t);
  drawChar2(c, CAST2.noble, { x: 1010, y: 2050, s: 1.35, f: -1, view: 'p', expr: X('surprise', { lookX: 1 }) }, t);
  if (toCam) sparkles(c, 600, 760, 60, hit(t, [36.6], .3), 3, t);
  popWord(c, t, '*wink*', 36.6, 760, 700, 80, '#fff3d6');
  caption(c, t, 'He had *rare private access*\nto the king.', 33.6, 36.6, { size: 58, y: 330 });
}, 'groom');
shot(36.8, 38.4, 'G11 TA-DA, and a coin flips into darkness', 'cut', (c, t) => {
  const lt = t - 36.8, dark = clamp((t - 37.55) / .65);
  if (dark < 1) {
    privy2(c, t, 1.1, 540, 1050);
    c.save(); cam(c, 540, 1050, 1.1);
    const tada = E.back(clamp(lt / .15));
    drawChar2(c, KING, { x: 720, y: 1880, s: 1.25, f: -1, view: 'q', shR: 2.7 * tada, elR: .2, shL: 2.7 * tada, elL: .2, handR: 'spread', handL: 'spread', expr: X('laugh') }, t);
    drawChar2(c, TOMR, { x: 360, y: 1890, s: 1.25, f: 1, view: 'q', shR: 2.5 * tada, elR: .2, shL: t > 37.15 ? 2.3 : 2.5 * tada, elL: .2, handR: 'spread', handL: t > 37.15 ? 'open' : 'spread', air: tada * 30 * (1 - clamp(lt / .4)), expr: X('smug') }, t);
    c.restore();
    c.save(); c.globalAlpha = dark; c.fillStyle = '#0e0a1a'; c.fillRect(0, 0, W, H); c.restore();
  } else { c.fillStyle = '#0e0a1a'; c.fillRect(0, 0, W, H); }
  if (t > 37.15) { const u = clamp((t - 37.15) / .6), r = lerp(20, 520, E.in(u)); coin(c, lerp(330, 540, u), lerp(870, 960, u), r, (t - 37.15) * 16, mix('#f0c040', '#b8b8c0', dark), dark > .5 ? 'cross' : 'crown'); }
  if (dark > .5) { const k = (dark - .5) * 2; c.save(); c.globalAlpha = k; candle(c, 840, 1560, 220, t, 4, 1.2); bread(c, 300, 1460, 1.2); c.restore(); }
  popWord(c, t, 'TA-DA!', 36.8, 540, 640, 140);
}, 'groom');
