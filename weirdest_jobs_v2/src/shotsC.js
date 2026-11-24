// ===================================================================== shotsC.js  (Sin-Eater 38.4-56.0, finale 56.0-65.0)
'use strict';
const SIN = CAST2.sineater, WID = CAST2.widow, BOY = CAST2.boy;
const VIL2 = Array.from({ length: 7 }, (_, i) => villager(1200 + i, 'vil'));
const ELDER = Object.assign(villager(1250, 'vil'), { name: 'Elder' });
function villageBG2(c, t, camX) {
  const S = SETS.village;
  c.drawImage(S.sky, 0, 0); c.drawImage(S.far, -camX * .4 - 50, 0);
  fogBand(c, 1250, 220, t, '#a898d0', .18, 15, 11);
  c.drawImage(S.mid, -camX, 0);
  const bx = 1180 + 195 * .95 - camX, by = 1440 - 655 * .95, sw = Math.sin((t - 38.4) * PI / BAR) * .5;
  c.save(); c.translate(bx, by - 30); c.rotate(sw); blob(c, [[-26, 10], [-20, 50], [-34, 70], [34, 70], [20, 50], [26, 10], [0, -6]], '#d8a83a', 3); c.restore();
  c.drawImage(S.ground, -camX, S.gy);
  for (const [x, y] of [[280, 1300], [1660, 1250]]) glow(c, x - camX, y, 180, 'rgba(255,180,90,0.3)');
}
function crows2(c, t, t0, n = 7, seed = 3) { if (t < t0) return; const r = rng(seed); for (let i = 0; i < n; i++) { const u = t - t0, x = 1000 + (r() - .3) * 300 - u * (260 + r() * 200), y = 560 - u * (120 + r() * 160) + Math.sin(u * 3 + i) * 30; crow(c, x, y, .9 + r() * .5, t * 14 + i * 2); } }
function coffinCarried(c, x, y, s) {
  rrect(c, x - 70 * s, y - 120 * s, 520 * s, 110 * s, 14 * s, '#4a2c1c', 4);
  blob(c, [[x - 90 * s, y - 80 * s], [x - 50 * s, y - 160 * s], [x + 450 * s, y - 160 * s], [x + 490 * s, y - 80 * s], [x + 470 * s, y - 20 * s], [x - 80 * s, y - 20 * s]], '#e6dfd2', 4);
  line(c, [[x + 140 * s, y - 160 * s], [x + 140 * s, y - 40 * s]], 6, '#8a2a3a'); line(c, [[x + 80 * s, y - 120 * s], [x + 200 * s, y - 120 * s]], 6, '#8a2a3a');
}
shot(38.4, 41.6, 'S1 the village at dusk, a funeral procession', 'flash', (c, t) => {
  const lt = t - 38.4, camX = 100 + lt * 70;
  villageBG2(c, t, camX);
  crows2(c, t, 38.6, 8, 3);
  const s = .95, x = 840 - lt * 40, y = 1730;
  const wA = walk2(t, { step: SPB * 2, amp: .5 }), wB = walk2(t, { step: SPB * 2, amp: .5, ph: 1 });
  // the coffin rests on the bearers' shoulders; heads are in front of it, near hands steady its side
  const sh = 1730 - (BODY2.slim.thigh + BODY2.slim.shin + BODY2.slim.torso * .9) * s * .92;
  coffinCarried(c, x - 40 * s, sh + 30 * s, s * 1.05);
  [0, 1, 2, 3].forEach(i => drawChar2(c, VIL2[i], mergeP({ x: x + i * 125 * s, y, s: s * .92, f: -1, view: 'p' }, i % 2 ? wA : wB, { shR: .1, elR: .3, shL: -2.05, elL: -.35, handR: 'relaxed', handL: 'open', lean: .04, expr: X('sad', { lookX: .6 }) }), t));
  [WID, BOY, ELDER].forEach((ch, i) => drawChar2(c, ch, mergeP({ x: x + 560 * s + i * 135 * s, y: y + 10, s: s * (ch === BOY ? 1.05 : .95), f: -1, view: 'p' }, walk2(t + i * .3, { step: SPB * 2, amp: .4 }),
    { shR: 1.4, elR: 1.4, handR: 'grip', expr: X('sad', { lookY: .5 }), hold: { R: (cc, J) => candle(cc, J.handN[0], J.handN[1] + 6, 70, t, i, .8) } }), t));
  fogBand(c, 1750, 200, t, '#c8b8e8', .22, 30, 14);
  const ans = vocIn(39.9, 41.6), fl = hit(t, ans, .2);
  if (fl > .05) { c.save(); c.globalAlpha = fl * .22; c.fillStyle = '#ffc060'; c.fillRect(0, 0, W, H); c.restore(); }
  chapter2(c, t, '3', 'THE SIN-EATER', 38.55, 41.3, 'sin');
}, 'sin');
shot(41.6, 43.2, 'S2 he walks through the fog', 'cut', (c, t) => {
  const lt = t - 41.6;
  villageBG2(c, t, 520 + lt * 30);
  [[160, 1520, 3], [420, 1500, 4], [920, 1490, 5]].forEach(([x, y, i], j) => { const back = clamp((t - 41.8 - j * .35) / .3);
    drawChar2(c, VIL2[i], { x: x - back * 30, y, s: .78, f: 1, view: 'q', lean: -back * .2, shR: 1.6 * back, elR: 1.4, handR: 'open', expr: X(back > .3 ? 'fear' : 'neutral', { lookX: 1 }) }, t); });
  fogBand(c, 1600, 260, t, '#c8b8e8', .26, 25, 15);
  const w = walk2(t, { step: SPB * 2, amp: .6, bob: 1.2, lean: .1 });
  drawChar2(c, SIN, mergeP({ x: 640 - lt * 30, y: 1950, s: 1.9, f: -1, view: 'p' }, w, { swing: w.swing * 2.5, shR: .25, elR: .6, handR: 'relaxed', expr: X('mystic', { lookX: .6 }) }), t);
  fogBand(c, 1880, 160, t, '#d8c8f0', .26, 40, 16);
  caption(c, t, 'According to old *folklore*,\npeople paid him to absorb\nthe *sins of the dead.*', 41.6, 44.4, { size: 54, y: 320 });
}, 'sin');
shot(43.2, 44.0, 'S3 his eyes under the hood', 'cut', (c, t) => {
  c.fillStyle = rg(c, 540, 1000, 50, 1100, [[0, '#3a2a4a'], [1, '#0e0a16']]); c.fillRect(0, 0, W, H);
  c.save(); c.translate(560, 1500); drawHead2(c, SIN, 'q', X('mystic', { eye: E.out(clamp((t - 43.25) / .2)) * .75 + .05, lookX: .1 }), 760 + (t - 43.2) * 60, 9); c.restore();
  const gl = hit(t, [43.2, 43.5], .2);
  glow(c, 560 + 760 * .25, 1500 - 760 * .545, 160, `rgba(240,220,150,${.18 + gl * .3})`);
  caption(c, t, 'According to old *folklore*,\npeople paid him to absorb\nthe *sins of the dead.*', 41.6, 44.4, { size: 54, y: 320 });
}, 'sin');
function wakeRoom2(c, t, z = 1, cx = 540, cy = 960) {
  c.save(); cam(c, cx, cy, z); c.drawImage(SETS.cottageIn.bg, 0, 0);
  rrect(c, 200, 1340, 30, 260, 4, '#3a2618', 3); rrect(c, 850, 1340, 30, 260, 4, '#3a2618', 3);
  poly(c, [[140, 1340], [180, 1210], [900, 1210], [940, 1340]], '#5a3a26', 5);
  blob(c, [[120, 1300], [160, 1180], [920, 1180], [960, 1300], [940, 1420], [140, 1420]], '#ece6da', 5);
  line(c, [[540, 1185], [540, 1410]], 8, '#7a2a3a'); line(c, [[470, 1260], [610, 1260]], 8, '#7a2a3a');
  for (const [x, h, s] of [[110, 260, 1], [980, 230, 2], [300, 140, 3], [780, 150, 4]]) candle(c, x, x < 200 || x > 900 ? 1600 : 1185, h, t, s, .9);
  c.restore();
}
shot(44.0, 44.6, 'S4 the offering', 'cut', (c, t) => {
  wakeRoom2(c, t, 1.15, 540, 1150);
  c.save(); cam(c, 540, 1150, 1.15);
  drawChar2(c, WID, { x: 780, y: 1820, s: 1.25, f: -1, view: 'p', lean: .12, shR: 1.5, elR: .3, handR: 'open', wrR: -.6, expr: X('sad', { lookX: .8 }),
    hold: { R: (cc, J) => { ell(cc, J.handN[0] - 10, J.handN[1] - 24, 95, 22, '#b8b8c0', 4); bread(cc, J.handN[0] - 10, J.handN[1] - 55, .5); coin(cc, J.handN[0] + 55, J.handN[1] - 34, 16, .3, '#c8c8d0', 'cross'); } } }, t);
  drawChar2(c, SIN, { x: 310, y: 1810, s: 1.25, f: 1, view: 'p', shR: 1.3 * clamp((t - 44.1) / .3), elR: .5, handR: 'open', expr: X('mystic', { lookX: .7 }) }, t);
  c.restore();
}, 'sin');
shot(44.6, 46.4, 'S5 the bite', 'punch', (c, t) => {
  const lt = t - 44.6;
  wakeRoom2(c, t, 1.6, 420, 1000);
  c.save(); c.globalCompositeOperation = 'lighter'; c.fillStyle = rg(c, 900, 900, 50, 900, [[0, 'rgba(255,170,80,0.38)'], [1, 'rgba(0,0,0,0)']]); c.fillRect(0, 0, W, H); c.restore();
  const chewing = lt > .12, open = key(t, [[44.3, 0], [44.52, .95, 'out'], [44.6, 0, 'in']]);
  const by = key(t, [[44.3, 60], [44.55, -10, 'out'], [44.75, 20, 'out'], [46.4, 40]]);
  drawChar2(c, SIN, { x: 470, y: 2380, s: 2.55, f: 1, view: 'p', lean: .08, head: chewing ? Math.sin(lt * 22) * .015 : 0,
    shR: 1.1, elR: 2.0, handR: 'grip', wrR: -.4, shL: .95, elL: 2.1, handL: 'grip',
    expr: chewing ? X('chew', { lookX: .8, lookY: .2 }) : X('mystic', { open, mouth: 'open', lookX: .9 }), chewT: lt,
    hold: { R: (cc, J) => bread(cc, J.handN[0] + 45, J.handN[1] + by * .5 - 20, .5, clamp(lt / .05)) } }, t);
  if (lt >= 0 && lt < .8) particles(c, t, 77, 30, (cc, tt, i, a, b, d, e) => { const u = lt / .8; const x = 720 + (a - .2) * 520 * u, y = 860 + (b - .7) * 300 * u + u * u * 700; ell(cc, x, y, 6 + d * 9, 5 + d * 7, '#e0a860', 2); });
  popWord(c, t, 'CRUNCH!', 44.6, 800, 1180, 115, '#ffd23c', .12);
  caption(c, t, 'He ate *bread* offered\nduring the funeral.', 44.6, 47.4);
}, 'sin');
shot(46.4, 48.0, 'S6 symbolic smoke rises from the coffin', 'cut', (c, t) => {
  const lt = t - 46.4, k = clamp(lt / .5);
  wakeRoom2(c, t, 1.0, 540, 1000);
  smokeWisps(c, 540, 1200, t, k, 31, '#4a2a7a');
  drawChar2(c, SIN, { x: 900, y: 1830, s: 1.25, f: -1, view: 'q', shR: 1.0 + k * .8, elR: .2, shL: .9 + k * .8, elL: .2, handR: 'spread', handL: 'spread', head: -.15, expr: X('ooh', { lookX: -.6, lookY: -.6, eye: .8 }) }, t);
  drawChar2(c, BOY, { x: 190, y: 1840, s: 1.3, f: 1, view: 'q', shR: 1.6, elR: 1.7, handR: 'open', expr: X('fear', { lookX: .6, lookY: -.6 }) }, t);
  caption(c, t, 'He ate *bread* offered\nduring the funeral.', 44.6, 47.4);
}, 'sin');
shot(48.0, 49.6, 'S7 the shadow grows (a folk belief)', 'cut', (c, t) => {
  const lt = t - 48.0;
  wakeRoom2(c, t, 1.0, 540, 1000);
  glow(c, 560, 900, 700, `rgba(140,100,220,${.3 * clamp(lt / .4)})`);
  c.save(); c.globalAlpha = .8 * clamp(lt / .4); c.translate(560, 1560); c.scale(2.2 + lt * .2, 2.2 + lt * .2);
  const shadowCh = Object.assign({}, SIN, { skin: '#120a1c', col: { body: '#120a1c', sleeve: '#120a1c', legs: '#120a1c', shoes: '#120a1c' }, lw: .01, faceShadow: 0, face: { nose: 'hook', noseLen: .14, eyeS: .01, iris: '#120a1c' }, hat: hoodHat('#120a1c'), hairBack: null, hair: null, noShadow: true,
    costume: Object.assign({}, SIN.costume, { detail: null, cuff: null }) });
  drawChar2(c, shadowCh, { x: 0, y: 0, s: 1, f: -1, view: 'p', shR: 2.5, elR: .4, shL: 2.4, elL: .4, handR: 'spread', handL: 'spread' }, t);
  c.restore();
  smokeWisps(c, 560, 1100 - lt * 120, t, 1 - clamp((lt - 1.0) / .6) * .6, 33, '#5a2a8a');
  drawChar2(c, SIN, { x: 560, y: 1850, s: 1.35, f: -1, view: 'f', shR: 2.6, elR: .2, shL: 2.6, elL: .2, handR: 'spread', handL: 'spread', head: -.15, air: Math.sin(lt * 3) * 10, expr: X('ooh', { lookY: -.8 }) }, t);
  caption(c, t, 'This was *believed* to transfer\nthe deceased’s sins to him.', 48.0, 51.0, { size: 54 });
}, 'sin');
shot(49.6, 51.2, 'S8 relief, and a coin', 'cut', (c, t) => {
  const lt = t - 49.6, relief = clamp(lt / .6);
  wakeRoom2(c, t, 1.15, 540, 1150);
  c.save(); cam(c, 540, 1150, 1.15);
  drawChar2(c, WID, { x: 720, y: 1830, s: 1.2, f: -1, view: 'q', shR: 1.2, elR: .4, handR: 'open', head: .1 * relief, expr: X(relief > .5 ? 'relief' : 'sad', { lookX: .6 }) }, t);
  drawChar2(c, BOY, { x: 930, y: 1850, s: 1.05, f: -1, view: 'q', shR: 2.0, elR: 1.5, handR: 'open', expr: X('happy', { lookX: .6 }) }, t);
  drawChar2(c, SIN, { x: 330, y: 1830, s: 1.2, f: 1, view: 'p', shR: 1.3, elR: .2, handR: 'open', wrR: -.6, expr: X('mystic', { lookX: .8 }) }, t);
  const u = clamp((t - 49.8) / .35);
  coin(c, lerp(620, 520, u), lerp(1250, 1320, u) - Math.sin(u * PI) * 120, 22, t * 12, '#c8c8d0', 'cross');
  c.restore();
}, 'sin');
shot(51.2, 52.8, 'S9 he leaves alone', 'cut', (c, t) => {
  const lt = t - 51.2;
  villageBG2(c, t, 300 + lt * 20);
  [[200, 1540, 0], [420, 1510, 1], [880, 1500, 2], [1010, 1540, 4]].forEach(([x, y, i]) => drawChar2(c, VIL2[i], { x, y, s: .82, f: x < 540 ? 1 : -1, view: 'q', lean: -.15, shR: .6, elR: 1.4, handR: 'open', expr: X('fear', { lookX: x < 540 ? 1 : -1 }) }, t));
  fogBand(c, 1650, 220, t, '#c8b8e8', .26, 25, 17);
  const w = walk2(t, { step: SPB * 2, amp: .55 });
  drawChar2(c, SIN, mergeP({ x: 560 + lt * 40, y: 1760 - lt * 30, s: 1.25 - lt * .1, f: 1, view: 'b' }, w, { swing: w.swing * 2 }), t);
  caption(c, t, 'He carried the burden,\naccording to the *legend.*', 51.4, 54.4);
}, 'sin');
shot(52.8, 54.4, 'S10 a silhouette against the moon', 'cut', (c, t) => {
  const lt = t - 52.8;
  c.save(); cam(c, 540, 1000, 1.0 + lt * .05); c.drawImage(SETS.moon.bg, 0, 0); c.restore();
  const sil = Object.assign({}, SIN, { skin: '#0c0a14', col: { body: '#0c0a14', sleeve: '#0c0a14', legs: '#0c0a14', shoes: '#0c0a14' }, lw: 3, faceShadow: 0, face: { nose: 'hook', noseLen: .14, eyeS: .01, iris: '#0c0a14' }, hat: hoodHat('#0c0a14'), hairBack: null, hair: null, costume: Object.assign({}, SIN.costume, { detail: null, cuff: null }) });
  const w = walk2(t, { step: SPB * 2, amp: .55 });
  drawChar2(c, sil, mergeP({ x: 380 + lt * 90, y: 1250, s: 1.05, f: 1, view: 'p' }, w, { swing: w.swing * 2.5 }), t);
  crows2(c, t, 52.9, 5, 9);
  motes(c, t, 44, 30, '#d8d0ff', .4, 10);
  caption(c, t, 'He carried the burden,\naccording to the *legend.*', 51.4, 54.4);
}, 'sin');
shot(54.4, 56.0, 'S11 build: the worlds collide', 'cut', (c, t) => {
  const heys = [55.2, 55.4, 55.6, 55.8], idx = heys.filter(h => t >= h).length;
  if (idx === 0) {
    c.save(); cam(c, 540, 960, 1 + (t - 54.4) * .15); c.drawImage(SETS.cottageIn.bg, 0, 0); c.restore();
    const o = clamp((t - 54.4) / .8);
    rrect(c, 380, 900, 320, 700, 10, '#ffd890'); glow(c, 540, 1250, 600 * o, 'rgba(255,210,140,0.45)');
    if (o > .15) { c.save(); c.globalAlpha = clamp((o - .15) * 3); const sil = Object.assign({}, SIN, { skin: '#140c18', col: { body: '#140c18', sleeve: '#140c18', legs: '#140c18', shoes: '#140c18' }, faceShadow: 0, face: { nose: 'hook', noseLen: .14, eyeS: .01, iris: '#140c18' }, hat: hoodHat('#140c18'), hair: null, hairBack: null, costume: Object.assign({}, SIN.costume, { detail: null, cuff: null }) }); drawChar2(c, sil, { x: 560, y: 1600, s: .95, f: -1, view: 'f' }, t); c.restore(); }
    c.save(); c.translate(380, 900); c.scale(1 - o * .85, 1); rrect(c, 0, 0, 320, 700, 10, '#5a3a26', 6); for (let i = 0; i < 4; i++) line(c, [[20 + i * 80, 10], [20 + i * 80, 690]], 4, '#3a2618'); c.restore();
  } else {
    const bg = ['#3a6ad0', '#c8283a', '#6a4ab0', '#e0a030'][idx - 1];
    c.fillStyle = rg(c, 540, 1000, 50, 1300, [[0, tint(bg, .35)], [1, shade(bg, .45)]]); c.fillRect(0, 0, W, H);
    speedLines(c, 540, 1000, .5, idx * 7);
    const who = [NED, TOMR, SIN, KING][idx - 1], k = E.back(clamp((t - heys[idx - 1]) / .12));
    drawChar2(c, who, { x: 540, y: 2250, s: 2.1 * (.88 + .12 * k), f: idx % 2 ? 1 : -1, view: 'q', shR: 2.8, elR: .2, shL: 2.8, elL: .2, handR: 'spread', handL: 'spread', expr: X('shout'), hold: who === NED ? raisePole(.25, 200) : null }, t);
    popWord(c, t, 'HEY!', heys[idx - 1], 540, 640, 200);
  }
}, 'stage');

// =============================================================== FINALE
function crowdDance(c, t, list, y, s, spacing, x0, ph = 0) {
  list.forEach((ch, i) => { const P = phrase(t + i * .04, 56 + ph, [[0, { shR: 2.6, elR: .3, shL: .5, elL: .7, hipR: .5, kneeR: .4, hipL: 0, kneeL: .1, handR: 'spread' }, 'back'], [1, { shR: .5, elR: .7, shL: 2.6, elL: .3, hipL: .5, kneeL: .4, hipR: 0, kneeR: .1, handL: 'spread' }, 'back'], [2, { shR: 2.6, elR: .3, shL: 2.6, elL: .3, hipR: .2, kneeR: .5, hipL: .2, kneeL: .5, air: 30 }, 'back'], [3, { shR: 1.2, elR: 1.5, shL: 1.2, elL: 1.5, hipR: -.1, kneeR: .3, hipL: .3, kneeL: .3 }, 'back'], [4, { shR: 2.6, elR: .3, shL: .5, elL: .7, hipR: .5, kneeR: .4, hipL: 0, kneeL: .1, handR: 'spread' }, 'back']], 4);
    drawChar2(c, ch, mergeP({ x: x0 + i * spacing, y: y + (i % 2) * 18, s, f: i % 2 ? 1 : -1, view: 'q', expr: X(hit(t, vocIn(56, 65), .2) > .3 ? 'shout' : 'grin') }, P), t); });
}
const CHORUS2 = [GDS[1], VIL2[0], WINF[0], CAST2.servant, CAST2.lady, VIL2[2], WINF[2], WID, GDS[3], CAST2.noble];
function confetti(c, t) { particles(c, t, 91, 44, (cc, tt, i, a, b, d, e) => { const u = ((tt - 56) * (.3 + d * .3) + a) % 1; const x = b * W + Math.sin(u * 8 + i) * 40, y = u * 1900 - 100; if (i % 3 === 0) coin(cc, x, y, 14, tt * 8 + i); else { cc.save(); cc.translate(x, y); cc.rotate(tt * 5 + i); cc.fillStyle = ['#ffd34d', '#e8505a', '#5ab0e8', '#7ad07a'][i % 4]; cc.fillRect(-8, -4, 16, 8); cc.restore(); } }); }
shot(56.0, 57.6, 'F1 the curtains fly open - everybody dances', 'flash', (c, t) => {
  const lt = t - 56, open = E.out(clamp(lt / .5)), z = key(lt, [[0, 1.15], [1.6, 1.0, 'out']]);
  stageBG2(c, t, z, 540, 1080);
  c.save(); cam(c, 540, 1080, z);
  crowdDance(c, t, CHORUS2, 1350, .55, 102, 80);
  confetti(c, t);
  drawChar2(c, KING, mergeP({ x: 540, y: 1560, s: .95, f: 1, view: 'f' }, phrase(t, 56, [[0, { shR: 2.7, elR: .2, shL: 2.7, elL: .2, hipR: .3, kneeR: .4, hipL: -.3, kneeL: .4, handR: 'spread', handL: 'spread', expr: X('laugh') }, 'back'], [1, { shR: 1.0, elR: 1.6, shL: 1.0, elL: 1.6, air: 40, expr: X('shout') }, 'back'], [2, { shR: 2.7, elR: .2, shL: 2.7, elL: .2, hipR: .3, kneeR: .4, hipL: -.3, kneeL: .4, handR: 'spread', handL: 'spread', expr: X('laugh') }, 'back']], 2)), t);
  drawChar2(c, NED, mergeP({ x: 210, y: 1770, s: 1.1, f: 1, handR: 'grip' }, phrase(t, 56, DANCE.ned, 4), { hold: twirlPole(t) }), t);
  drawChar2(c, TOMR, mergeP({ x: 560, y: 1830, s: 1.1, f: 1 }, phrase(t, 56, DANCE.thomas, 4)), t);
  drawChar2(c, SIN, mergeP({ x: 890, y: 1780, s: 1.08, f: -1 }, phrase(t, 56, DANCE.sin, 4)), t);
  c.restore();
  stageFG2(c, t, z, 540, 1080, open);
  speedLines(c, 540, 1100, hit(t, [56], .35) * .7, 5);
}, 'stage');
shot(57.6, 59.2, 'F2 the village answers', 'cut', (c, t) => {
  stageBG2(c, t, 1.3, 540, 1240);
  c.save(); cam(c, 540, 1240, 1.3);
  crowdDance(c, t, CHORUS2.slice(0, 6), 1420, .62, 170, 110, .5);
  crowdDance(c, t, [VIL2[1], WINF[4], CAST2.servant, GDS[0]], 1760, .95, 240, 180);
  confetti(c, t);
  c.restore();
  vocIn(57.5, 59.3).forEach((h, i) => popWord(c, t, VOC.find(v => Math.abs(v[0] - h) < 1e-3)[1], h, 200 + (i * 263) % 700, 520 + (i * 137) % 300, 110, ['#ffd23c', '#ff8a5a', '#8ad0ff'][i % 3], (i % 2 ? .08 : -.08)));
  stageFG2(c, t, 1.3, 540, 1240, 1);
}, 'stage');
shot(59.2, 60.8, 'F3 the trio dances', 'cut', (c, t) => {
  const lt = t - 59.2, z = 1.0 + Math.sin(lt * 2) * .03, cx = 540 + Math.sin(lt * 1.5) * 30;
  stageBG2(c, t, z, cx, 1100);
  c.save(); cam(c, cx, 1100, z);
  crowdDance(c, t, CHORUS2.slice(2, 9), 1350, .56, 145, 110);
  drawChar2(c, NED, mergeP({ x: 200, y: 1880, s: 1.3, f: 1, handR: 'grip' }, phrase(t, 59.2, DANCE.ned, 4), { hold: twirlPole(t) }), t);
  drawChar2(c, TOMR, mergeP({ x: 545, y: 1930, s: 1.3, f: 1 }, phrase(t, 59.2, DANCE.thomas, 4)), t);
  drawChar2(c, SIN, mergeP({ x: 885, y: 1880, s: 1.26, f: -1 }, phrase(t, 59.2, DANCE.sin, 4)), t);
  c.restore();
  motes(c, t, 51, 40, '#ffe0a0', .6, 60);
}, 'stage');
shot(60.8, 62.4, 'F4 the king leads a kick line', 'cut', (c, t) => {
  stageBG2(c, t, 1.0, 540, 1080);
  c.save(); cam(c, 540, 1080, 1.0);
  crowdDance(c, t, CHORUS2, 1350, .55, 102, 80, 1);
  confetti(c, t);
  const line_ = [[110, NED], [325, TOMR], [540, KING], [755, SIN], [970, GDS[2]]];
  line_.forEach(([x, ch], i) => { const kb = (t - 60.8) / SPB + i * .5, kick = Math.max(0, Math.sin(kb * PI)), side = Math.floor(kb) % 2;
    drawChar2(c, ch, { x, y: 1700, s: .95, f: i < 2 ? 1 : i > 2 ? -1 : 1, view: 'q', shR: 2.0, elR: 1.9, shL: 2.0, elL: 1.9, handR: 'fist', handL: 'fist', hipR: side ? kick * 1.5 : -.1, kneeR: side ? .1 : .3, hipL: side ? -.1 : kick * 1.5, kneeL: side ? .3 : .1, lean: -.05, air: 8, expr: X(kick > .6 ? 'shout' : 'grin') }, t); });
  c.restore();
  sparkles(c, 540, 900, 500, hit(t, vocIn(60.8, 62.4), .25), 12, t);
  stageFG2(c, t, 1.0, 540, 1080, 1);
}, 'stage');
shot(62.4, 64.0, 'F5 which job would you choose?', 'cut', (c, t) => {
  const z = key(t, [[62.4, 1.1], [64.0, 1.0]]);
  stageBG2(c, t, z, 540, 1150);
  c.save(); cam(c, 540, 1150, z);
  crowdDance(c, t, CHORUS2, 1350, .55, 102, 80, 2);
  confetti(c, t);
  const fr = t >= 63.2;
  [[210, NED, 'ned', 1, '1'], [545, TOMR, 'thomas', 1, '2'], [880, SIN, 'sin', -1, '3']].forEach(([x, ch, who, f, n], i) => {
    const step = E.back(clamp((t - 63.2 - i * .13) / .2));
    const pose = fr ? { view: 'q', shR: 2.8, elR: .1, shL: -.6, elL: .3, handR: who === 'ned' ? 'grip' : 'spread', handL: 'open', expr: X('grin'), hold: who === 'ned' ? raisePole(.15, 150) : null } : mergeP(phrase(t, 62.4, DANCE[who], 4), who === 'ned' ? { handR: 'grip', hold: twirlPole(t) } : {});
    drawChar2(c, ch, mergeP({ x, y: 1880 + step * 50, s: 1.15 + step * .08, f }, pose), t);
    if (fr) { c.save(); c.translate(x, 1010 + (1 - step) * 80); c.scale(step, step); ell(c, 0, 0, 62, 62, '#c8283a', 6, 0, '#f0c040'); c.font = '70px Slab'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillStyle = '#fff3d6'; c.fillText(n, 0, 6); c.restore(); }
  });
  c.restore();
  stageFG2(c, t, z, 540, 1150, 1);
  flash(c, t, [63.2, 63.6], '#fff6e0', .07, .3);
}, 'stage');
shot(64.0, 65.01, 'F6 tail: tap tap tap -> loop', 'cut', (c, t) => {
  const lt = t - 64.0, k = E.io(clamp(lt / .9)), z = lerp(1.0, 1.12, k);
  stageBG2(c, t, z, 540, 1050);
  c.save(); cam(c, 540, 1050, z);
  for (let i = 0; i < 7; i++) { const ch = villager(300 + i, ['ind', 'court', 'vil'][i % 3]); drawChar2(c, ch, { x: 120 + i * 140, y: 1330, s: .5, f: i % 2 ? 1 : -1, view: 'q', shR: 2.5, elR: .3, shL: .5, elL: .6, expr: X('grin') }, t); }
  const crouch = E.io(clamp((lt - .45) / .5)), taps = [64.4, 64.6, 64.8], tk = hit(t, taps, .1);
  const cr = { air: 0, land: 0, k1: { sq: 1 - crouch * .12, kneeR: .35 + crouch * .9, kneeL: .5 + crouch * .9, hipR: .25 + crouch * .5, hipL: -.25 + crouch * .5, hold: raisePole(.32 - tk * .1, 160) },
    k2: { sq: 1 - crouch * .1, kneeR: .12 + crouch * .9, kneeL: .2 + crouch * .9, hipR: .15 + crouch * .5, hipL: -.15 + crouch * .5 }, k3: { sq: 1 - crouch * .08, kneeR: .25 + crouch * .8, kneeL: .3 + crouch * .8, hipR: .15 + crouch * .5 } };
  trio2(c, 0.0, cr);
  c.restore();
  stageFG2(c, t, z, 540, 1050);
  taps.forEach(tt => popWord(c, t, 'tap!', tt, 250, 640, 80, '#fff3d6'));
}, 'stage');

// ---- overlays: main title (0-3.2) and the final question (62.3-65)
window.overlay = (c, t) => {
  if (t < 3.2) {
    const appear = clamp((t - .3) / .35); if (appear <= 0) return;
    const small = t >= 1.6 && t < 2.8, sc = small ? .62 : 1, y0 = small ? 330 : 470;
    c.save(); c.translate(540, y0); c.scale(sc * E.back(appear), sc * E.back(appear));
    const notes = [0, .2, .3, .5, .6, .8, 1.0, 1.1, 1.3, 1.4], b = hit(t, notes, .12) * .05; c.scale(1 + b, 1 + b);
    c.fillStyle = 'rgba(0,0,0,0.35)'; c.beginPath(); c.roundRect(-452, -132, 920, 300, 60); c.fill();
    c.fillStyle = '#16204a'; c.beginPath(); c.roundRect(-460, -140, 920, 300, 60); c.fill(); c.lineWidth = 8; c.strokeStyle = '#e8b440'; c.stroke();
    ell(c, -350, 10, 92, 92, '#c8283a', 8, 0, '#f0c040'); c.font = '130px Slab'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillStyle = '#fff3d6'; c.fillText('3', -350, 18);
    c.font = '92px Slab'; c.fillStyle = '#ffd23c'; c.fillText('WEIRDEST', 80, -44); c.fillStyle = '#fff3d6'; c.font = '60px Slab'; c.fillText('JOBS IN HISTORY', 80, 58);
    c.restore();
  }
  if (t >= 62.3) caption(c, t, 'WHICH JOB WOULD\nYOU *CHOOSE?*', 62.3, 66, { size: 84, y: 400 });
};
