// ===================================================================== shots_c.js  (profession 3: Sin-Eater 38.4-56.0, finale 56.0-65.0)
'use strict';
const VILLAGERS = Array.from({ length: 6 }, (_, i) => townsfolk(1200 + i, 'vil'));
const MOURN = [CAST.mother, CAST.boy, CAST.elder];
function villageScene(c, t, camX, o = {}) {
  const S = SETS.village;
  c.drawImage(S.sky, 0, 0);
  c.drawImage(S.far, -camX * .4 - 50, 0);
  fogBand(c, 1250, 220, t, '#8a7aa8', .2, 15, 11);
  c.drawImage(S.mid, -camX, 0);
  // the church bell swings in the belfry on each toll
  const bx = 1180 + 195 * .95 - camX, by = 1440 - 655 * .95;
  const sw = Math.sin((t - 38.4) * PI / BAR) * .5;
  c.save(); c.translate(bx, by - 30); c.rotate(sw); blob(c, [[-26, 10], [-20, 50], [-34, 70], [34, 70], [20, 50], [26, 10], [0, -6]], '#b8862a', 3); c.restore();
  c.drawImage(S.ground, -camX, S.gy);
  // candle glows in windows
  for (const [x, y] of [[80 + 200, 1300], [1500 + 160, 1250]]) glow(c, x - camX, y, 160, 'rgba(255,180,90,0.25)');
}
function crows(c, t, t0, n = 7, seed = 3) {
  if (t < t0) return;
  const r = rng(seed);
  for (let i = 0; i < n; i++) { const u = t - t0, x = 1000 + (r() - .3) * 300 - u * (260 + r() * 200), y = 560 - u * (120 + r() * 160) + Math.sin(u * 3 + i) * 30; crow(c, x, y, .9 + r() * .5, t * 14 + i * 2); }
}
function procession(c, t, x0, y, s) {
  const lt = t - 38.4;
  const x = x0 - lt * 38;
  // bearers carrying a covered coffin, slow steps on every other beat
  const wpA = walkPose(t, { stepDur: SPB * 2, amp: .45 }), wpB = walkPose(t, { stepDur: SPB * 2, amp: .45, ph: PI });
  const bearers = [VILLAGERS[0], VILLAGERS[1], VILLAGERS[2], VILLAGERS[3]];
  const yb = y - 400 * s + Math.abs(Math.sin(t * PI / (SPB * 2))) * 6;
  rrect(c, x - 60 * s, yb - 110 * s, 460 * s, 100 * s, 14 * s, '#3a2418', 4);
  blob(c, [[x - 80 * s, yb - 70 * s], [x - 40 * s, yb - 150 * s], [x + 400 * s, yb - 150 * s], [x + 440 * s, yb - 70 * s], [x + 420 * s, yb - 20 * s], [x - 70 * s, yb - 20 * s]], '#d8d0c4', 4);
  line(c, [[x + 120 * s, yb - 150 * s], [x + 120 * s, yb - 40 * s]], 6, '#8a2a2a'); line(c, [[x + 60 * s, yb - 110 * s], [x + 180 * s, yb - 110 * s]], 6, '#8a2a2a');
  bearers.forEach((ch, i) => drawChar(c, ch, merge({ x: x + i * 120 * s, y, s: s * .95, f: -1, turn: .3, lean: .05 }, i % 2 ? wpA : wpB, { shR: 2.75, elR: .5, shL: 2.75, elL: .5, expr: { mouth: 'flat', eye: .7, lookX: -.4, brow: -.3 } }), t));
  // mourners with candles behind
  MOURN.forEach((ch, i) => { const xx = x + 520 * s + i * 120 * s; drawChar(c, ch, merge({ x: xx, y: y + 10, s: s * (ch === CAST.boy ? .9 : .95), f: -1, turn: .3, lean: .12 }, walkPose(t + i * .3, { stepDur: SPB * 2, amp: .4 }), { shR: 1.2, elR: 1.2, handR: 'hold', expr: { mouth: 'frown', eye: .55, lookY: .5, brow: -.2 }, hold: { R: (cc, J) => candle(cc, J.handNear[0], J.handNear[1] + 6, 70, t, i, .8) } }), t); });
}
shot(38.4, 41.6, 'S1 village at dusk + procession', 'flash', (c, t) => {
  const lt = t - 38.4, camX = 100 + lt * 70;
  villageScene(c, t, camX);
  crows(c, t, 38.6, 8, 3);
  procession(c, t, 820, 1690, .9);
  fogBand(c, 1750, 200, t, '#b0a0c8', .25, 30, 14);
  const ans = vocIn(39.9, 41.6), fl = hit(t, ans, .2);
  if (fl > .05) { c.save(); c.globalAlpha = fl * .25; c.fillStyle = '#ffc060'; c.fillRect(0, 0, W, H); c.restore(); }
  chapterCard(c, t, '3', 'THE SIN-EATER', 38.55, 41.3, '#4a3a6a');
});
shot(41.6, 43.2, 'S2 he walks through the fog', 'cut', (c, t) => {
  const lt = t - 41.6;
  villageScene(c, t, 520 + lt * 30);
  const bells = patT(26, 'X..x..X.X..x..X.');
  // villagers in doorways shrink back / slam shutters
  [[180, 1500, 0], [430, 1480, 1], [900, 1470, 2]].forEach(([x, y, i]) => { const back = clamp((t - 41.8 - i * .35) / .3); drawChar(c, VILLAGERS[i + 3], { x: x - back * 30, y, s: .7, f: 1, turn: .4, lean: -back * .2, shR: 1.6 * back, elR: 1.4, handR: 'open', expr: { mouth: back > .3 ? 'o' : 'flat', open: .5, eye: 1 + back * .2, brow: back * 1.4, lookX: 1 } }, t); });
  fogBand(c, 1600, 260, t, '#b0a0c8', .3, 25, 15);
  const wp = walkPose(t, { stepDur: SPB * 2, amp: .55 });
  drawChar(c, CAST.sineater, merge({ x: 640 - lt * 20, y: 1880, s: 1.45, f: -1, turn: .3, lean: .1 }, wp, { swing: wp.swing * 2, shR: .2, elR: .3, expr: { mouth: 'flat', eye: .65, lookX: -.6, brow: -.4 } }), t);
  fogBand(c, 1880, 160, t, '#c8b8e0', .3, 40, 16);
  subtitle(c, t, 'According to old *folklore*,\npeople paid him to absorb\nthe *sins of the dead.*', 41.6, 44.4, { size: 56, y: 300 });
});
shot(43.2, 44.0, 'S3 ECU eyes under the hood', 'cut', (c, t) => {
  c.fillStyle = '#0a0810'; c.fillRect(0, 0, W, H);
  c.save(); cam(c, 540, 1040, 3.0 + (t - 43.2) * .3);
  drawHeadOnly(c, CAST.sineater, 560, 1220, 0, 1.0, { turn: .1, expr: { eye: E.out(clamp((t - 43.25) / .2)) * .75 + .05, mouth: 'flat', lookX: .1, brow: -.5 } });
  c.restore();
  const gl = hit(t, [43.2, 43.5], .2);
  glow(c, 470, 830, 140, `rgba(230,210,140,${.25 + gl * .3})`); glow(c, 650, 830, 140, `rgba(230,210,140,${.25 + gl * .3})`);
  subtitle(c, t, 'According to old *folklore*,\npeople paid him to absorb\nthe *sins of the dead.*', 41.6, 44.4, { size: 56, y: 300 });
});
function wakeRoom(c, t, z = 1, cx = 540, cy = 960, o = {}) {
  c.save(); cam(c, cx, cy, z);
  c.drawImage(SETS.cottageIn.bg, 0, 0);
  // covered coffin on trestles
  rrect(c, 200, 1340, 30, 260, 4, '#2a1c14', 3); rrect(c, 850, 1340, 30, 260, 4, '#2a1c14', 3);
  poly(c, [[140, 1340], [180, 1210], [900, 1210], [940, 1340]], '#3a2418', 5);
  blob(c, [[120, 1300], [160, 1180], [920, 1180], [960, 1300], [940, 1420], [140, 1420]], '#e8e2d6', 5);
  line(c, [[540, 1185], [540, 1410]], 8, '#6a2a3a');
  for (const [x, h, s] of [[110, 260, 1], [980, 230, 2], [300, 140, 3], [780, 150, 4]]) candle(c, x, x < 200 || x > 900 ? 1600 : 1185, h, t, s, .9);
  c.restore();
}
shot(44.0, 44.6, 'S4 the offering', 'cut', (c, t) => {
  wakeRoom(c, t, 1.1, 540, 1150);
  c.save(); cam(c, 540, 1150, 1.1);
  drawChar(c, CAST.mother, { x: 760, y: 1760, s: 1.1, f: -1, turn: .3, lean: .1, shR: 1.5, elR: .3, handR: 'open', expr: { mouth: 'frown', eye: .8, lookX: -.6, brow: -.3 }, hold: { R: (cc, J) => { ell(cc, J.handNear[0] - 10, J.handNear[1] - 20, 90, 22, '#a8a8b0', 4); bread(cc, J.handNear[0] - 10, J.handNear[1] - 50, .5); coin(cc, J.handNear[0] + 50, J.handNear[1] - 30, 16, .3, '#c8c8d0', 'cross'); } } }, t);
  drawChar(c, CAST.sineater, { x: 300, y: 1760, s: 1.15, f: 1, turn: .35, shR: 1.2 * clamp((t - 44.1) / .3), elR: .5, handR: 'open', expr: { mouth: 'flat', eye: .65, lookX: .7, brow: -.3 } }, t);
  c.restore();
});
shot(44.6, 46.4, 'S5 the bite', 'punch', (c, t) => {
  const lt = t - 44.6;
  wakeRoom(c, t, 1.9, 420, 1000);
  c.save(); cam(c, 420, 1000, 1.9);
  const chew = lt > .2;
  drawChar(c, CAST.sineater, { x: 380, y: 1700, s: 1.2, f: 1, turn: .45, lean: .05, shR: 1.55, elR: 1.75, handR: 'hold', head: -.05,
    expr: { mouth: lt < .2 ? 'grin' : 'chew', open: .5, chewT: lt, eye: lt < .25 ? .35 : .65, lookX: .5, lookY: .3, brow: -.4 }, hold: { R: (cc, J) => bread(cc, J.handNear[0] + 10, J.handNear[1] - 30, .55, clamp(lt / .05)) } }, t);
  c.restore();
  // crumbs burst on the crunch
  if (lt < .8) particles(c, t, 77, 26, (cc, tt, i, a, b, d, e) => { const u = lt / .8; const x = 640 + (a - .3) * 500 * u, y = 860 + (b - .7) * 300 * u + u * u * 500; ell(cc, x, y, 6 + d * 8, 5 + d * 6, '#d8a060', 2); });
  if (lt < .3) { c.save(); c.translate(780, 640); c.rotate(.15); c.font = '120px Luckiest'; c.textAlign = 'center'; c.lineWidth = 18; c.strokeStyle = '#1a0c08'; c.lineJoin = 'round'; c.globalAlpha = 1 - lt / .3; c.strokeText('CRUNCH!', 0, 0); c.fillStyle = '#f0c070'; c.fillText('CRUNCH!', 0, 0); c.restore(); }
  subtitle(c, t, 'He ate *bread* offered\nduring the funeral.', 44.6, 47.4);
});
shot(46.4, 48.0, 'S6 symbolic smoke rises', 'cut', (c, t) => {
  const lt = t - 46.4;
  wakeRoom(c, t, 1.0, 540, 1000);
  const k = clamp(lt / .5);
  c.save(); c.globalCompositeOperation = 'source-over';
  smokeWisps(c, 540, 1200, t, k, 31);
  c.restore();
  // ghost-choir accents bend the candle flames
  drawChar(c, CAST.sineater, { x: 920, y: 1760, s: 1.0, f: -1, turn: .3, shR: 1.0 + k * .8, elR: .2, shL: .9 + k * .8, elL: .2, handR: 'open', handL: 'open', head: -.15,
    expr: { mouth: 'o', open: .3, eye: .5 + k * .3, lookX: -.6, lookY: -.6, brow: .3 } }, t);
  drawChar(c, CAST.boy, { x: 170, y: 1780, s: .95, f: 1, turn: .3, shR: 1.6, elR: 1.6, handR: 'open', expr: { mouth: 'o', open: .7, eye: 1.2, brow: 1.4, lookX: .6, lookY: -.6 } }, t);
  subtitle(c, t, 'He ate *bread* offered\nduring the funeral.', 44.6, 47.4);
});
shot(48.0, 49.6, 'S7 the shadow grows (belief)', 'cut', (c, t) => {
  const lt = t - 48.0;
  wakeRoom(c, t, 1.0, 540, 1000);
  // huge stylised shadow on the stone wall
  glow(c, 560, 900, 700, `rgba(120,90,200,${.25 * clamp(lt / .4)})`); c.save(); c.globalAlpha = .82 * clamp(lt / .4); c.translate(560, 1500); c.scale(2.3 + lt * .2, 2.3 + lt * .2);
  drawChar(c, Object.assign({}, CAST.sineater, { skin: '#0a0610', col: { coat: '#0a0610', sleeve: '#0a0610', legs: '#0a0610', boots: '#0a0610' }, lw: 0.01, face: { nose: 'hook', eyeR: .01, iris: '#0a0610' }, faceShadow: 0, hat: hood('#0a0610'), backHair: hoodBack('#0a0610'), shadowOnGround: false }), { x: 0, y: 0, s: 1, f: -1, turn: .3, shR: 2.4, elR: .4, shL: 2.3, elL: .4 }, t);
  c.restore();
  smokeWisps(c, 560, 1100 - lt * 120, t, 1 - clamp((lt - 1.0) / .6) * .6, 33, '#3a1a5a');
  drawChar(c, CAST.sineater, { x: 560, y: 1780, s: 1.15, f: -1, turn: .1, shR: 2.6, elR: .2, shL: 2.6, elL: .2, handR: 'open', handL: 'open', head: -.2, air: Math.sin(lt * 3) * 10,
    expr: { mouth: 'o', open: .4, eye: .9, lookY: -.8, brow: .2 } }, t);
  glow(c, 560, 1000, 500, `rgba(150,110,255,${.15 + .1 * Math.sin(t * 6)})`);
  subtitle(c, t, 'This was *believed* to transfer\nthe deceased’s sins to him.', 48.0, 51.0, { size: 56 });
});
shot(49.6, 51.2, 'S8 relief + payment', 'cut', (c, t) => {
  const lt = t - 49.6;
  wakeRoom(c, t, 1.15, 540, 1150);
  c.save(); cam(c, 540, 1150, 1.15);
  const relief = clamp(lt / .6);
  drawChar(c, CAST.mother, { x: 700, y: 1770, s: 1.05, f: -1, turn: .3, shR: 1.2, elR: .4, handR: 'open', head: .1 * relief, expr: { mouth: relief > .5 ? 'smile' : 'frown', eye: .6 + relief * .3, lookX: -.6, brow: relief * .6, blush: .3 * relief } }, t);
  drawChar(c, CAST.boy, { x: 900, y: 1790, s: .85, f: -1, turn: .3, shR: 2.0, elR: 1.5, expr: { mouth: 'smile', eye: 1, lookX: -.6 } }, t);
  drawChar(c, CAST.sineater, { x: 330, y: 1770, s: 1.1, f: 1, turn: .35, shR: 1.3, elR: .2, handR: 'open', expr: { mouth: 'flat', eye: .65, lookX: .8, brow: -.2 } }, t);
  // the coin drops into his palm on the choir accent
  const u = clamp((t - 49.8) / .35);
  coin(c, lerp(620, 470, u), lerp(1220, 1290, u) - Math.sin(u * PI) * 120, 22, t * 12, '#c8c8d0', 'cross');
  c.restore();
});
shot(51.2, 52.8, 'S9 he leaves alone', 'cut', (c, t) => {
  const lt = t - 51.2;
  villageScene(c, t, 300 + lt * 20);
  [[220, 1520, 0], [420, 1500, 1], [880, 1490, 2], [1000, 1530, 4]].forEach(([x, y, i]) => drawChar(c, VILLAGERS[i], { x, y, s: .72, f: x < 540 ? 1 : -1, turn: .4, lean: -.15, shR: .6, elR: 1.4, handR: 'open', expr: { mouth: 'frown', eye: .9, lookX: x < 540 ? 1 : -1, brow: .8 } }, t));
  fogBand(c, 1650, 220, t, '#b0a0c8', .3, 25, 17);
  const wp = walkPose(t, { stepDur: SPB * 2, amp: .5 });
  drawChar(c, CAST.sineater, merge({ x: 560 + lt * 40, y: 1700 - lt * 30, s: 1.0 - lt * .08, f: 1, turn: .7, lean: .12 }, wp, { swing: wp.swing * 2, expr: { mouth: 'flat', eye: .6, lookX: .8 } }), t);
  subtitle(c, t, 'He carried the burden,\naccording to the *legend.*', 51.4, 54.4);
});
shot(52.8, 54.4, 'S10 silhouette against the moon', 'cut', (c, t) => {
  const lt = t - 52.8;
  c.save(); cam(c, 540, 1000, 1.0 + lt * .05); c.drawImage(SETS.moon.bg, 0, 0); c.restore();
  const sil = Object.assign({}, CAST.sineater, { skin: '#0c0a14', col: { coat: '#0c0a14', sleeve: '#0c0a14', legs: '#0c0a14', boots: '#0c0a14' }, lw: 3, faceShadow: 0, face: { nose: 'hook', eyeR: .01, iris: '#0c0a14', jaw: .82 }, hat: hood('#0c0a14'), backHair: hoodBack('#0c0a14') });
  const wp = walkPose(t, { stepDur: SPB * 2, amp: .5 });
  drawChar(c, sil, merge({ x: 380 + lt * 90, y: 1250, s: .95, f: 1, turn: .9, lean: .1 }, wp, { swing: wp.swing * 2.5 }), t);
  crows(c, t, 52.9, 5, 9);
  motes(c, t, 44, 30, '#d8d0ff', .4, 10);
  subtitle(c, t, 'He carried the burden,\naccording to the *legend.*', 51.4, 54.4);
});
shot(54.4, 56.0, 'S11 build: the worlds collide', 'cut', (c, t) => {
  const heys = [55.2, 55.4, 55.6, 55.8];
  const idx = heys.filter(h => t >= h).length;
  if (idx === 0) {
    c.save(); cam(c, 540, 960, 1 + (t - 54.4) * .15); c.drawImage(SETS.cottageIn.bg, 0, 0); c.restore();
    // the door creaks open, light pouring in
    const o = clamp((t - 54.4) / .8);
    rrect(c, 380, 900, 320, 700, 10, '#ffd890'); glow(c, 540, 1250, 600 * o, 'rgba(255,210,140,0.4)');
    if (o > .15) { const sil = Object.assign({}, CAST.sineater, { skin: '#120c14', col: { coat: '#120c14', sleeve: '#120c14', legs: '#120c14', boots: '#120c14' }, faceShadow: 0, face: { nose: 'hook', eyeR: .01, iris: '#120c14', jaw: .82 }, hat: hood('#120c14'), backHair: hoodBack('#120c14') }); c.save(); c.globalAlpha = clamp((o - .15) * 3); drawChar(c, sil, { x: 560, y: 1600, s: .9, f: -1, turn: .2, shR: .2, shL: -.2 }, t); c.restore(); }
    c.save(); c.translate(380, 900); c.scale(1 - o * .85, 1); rrect(c, 0, 0, 320, 700, 10, '#3a2418', 6); for (let i = 0; i < 4; i++) line(c, [[20 + i * 80, 10], [20 + i * 80, 690]], 4, '#2a1810'); c.restore();
    for (let i = 0; i < 8; i++) { const bt = 54.4 + i * .1; if (t > bt) sparkles(c, 540 + Math.sin(i * 2) * 200, 800 + i * 60, 50, hit(t, [bt], .2), i, t); }
  } else {
    // whip montage: one hero per shout
    const bg = ['#3a6a9a', '#a8203a', '#4a3a6a', '#c8862a'][idx - 1];
    c.fillStyle = rg(c, 540, 1000, 50, 1300, [[0, tint(bg, .3)], [1, shade(bg, .5)]]); c.fillRect(0, 0, W, H);
    speedLines(c, 540, 1000, .5, idx * 7);
    const who = [CAST.knocker, CAST.groomRich, CAST.sineater, CAST.king][idx - 1];
    const k = E.back(clamp((t - heys[idx - 1]) / .12));
    drawChar(c, who, { x: 540, y: 2000, s: 1.7 * (.85 + .15 * k), f: idx % 2 ? 1 : -1, turn: .1, shR: 2.8, elR: .2, shL: 2.8, elL: .2, handR: 'open', handL: 'open', expr: { mouth: 'shout', open: 1, eye: 1.2, brow: 1.6 },
      hold: who === CAST.knocker ? holdPole(.2, 600, 100) : null }, t);
    c.save(); c.translate(540, 520); c.scale(k, k); c.rotate((idx % 2 ? -1 : 1) * .08); c.font = '170px Luckiest'; c.textAlign = 'center'; c.lineWidth = 26; c.strokeStyle = '#1a0c08'; c.lineJoin = 'round'; c.strokeText('HEY!', 0, 0); c.fillStyle = '#ffd34d'; c.fillText('HEY!', 0, 0); c.restore();
  }
});

// =============================================================== FINALE 56.0 - 65.0
function dancePose(who, t, o = {}) {
  const b = t / SPB, ph = b * PI, on = Math.abs(Math.sin(ph));
  const hey = hit(t, vocIn(56, 65), .18);
  if (who === 'knocker') {
    const kick = Math.max(0, Math.sin(ph)), kick2 = Math.max(0, -Math.sin(ph));
    return { hipR: kick * 1.1 - .1, kneeR: .2, hipL: kick2 * 1.1 - .1, kneeL: .2, air: on * 30 + hey * 50, shR: 2.4, elR: .2, shL: 1.2 + Math.sin(ph) * .8, elL: .6, handR: 'hold', lean: -.05, swing: Math.sin(ph) * .3,
      expr: { mouth: 'grin', open: .4 + hey * .5, eye: 1, brow: .8 + hey }, hold: { R: (c, J) => { const a = t * PI * 1.25; const h = J.handNear; pole(c, h[0] - Math.sin(a) * 380, h[1] + Math.cos(a) * 380, h[0] + Math.sin(a) * 380, h[1] - Math.cos(a) * 380); } } };
  }
  if (who === 'groom') {
    const tw = (b % 4) / 4;
    return { f: Math.cos(tw * TAU) >= 0 ? 1 : -1, turn: Math.abs(Math.sin(tw * TAU)) * .7 + .1, shR: 2.0 + Math.sin(ph) * .6, elR: .5, shL: 1.0 - Math.sin(ph) * .6, elL: 1.2, handR: 'open', handL: 'open', hipR: .4 + Math.sin(ph) * .3, kneeR: .1, hipL: -.2, kneeL: .3, air: on * 20 + hey * 40,
      expr: { mouth: 'smirk', lids: .4, eye: 1, brow: .6, blush: .4 } };
  }
  if (who === 'sineater') {
    return { shR: 1.4 + Math.sin(ph * .5) * .9, elR: .8 + Math.sin(ph) * .4, shL: 1.4 - Math.sin(ph * .5) * .9, elL: .8, handR: 'open', handL: 'open', lean: Math.sin(ph * .5) * .15, hipR: .1, kneeR: .3 + on * .3, hipL: -.1, kneeL: .3, swing: Math.sin(ph * .5) * .5, air: hey * 25,
      expr: { mouth: hey > .3 ? 'grin' : 'flat', open: .3, eye: .7, lookX: Math.sin(ph * .5) * .8, brow: -.2 } };
  }
  if (who === 'king') return { shR: 2.6 + hey * .3, elR: .2 + on * .3, shL: 2.6 + hey * .3, elL: .2 + on * .3, handR: 'open', handL: 'open', air: on * 25 + hey * 40, sq: 1 - on * .06, lean: Math.sin(ph) * .08, expr: { mouth: 'grin', open: .6 + hey * .3, eye: 1, brow: 1 } };
  return { shR: 2.2 + on * .5, elR: .4, shL: 2.2 + on * .5, elL: .4, handR: 'open', handL: 'open', air: on * 20 + hey * 45, expr: { mouth: hey > .3 ? 'shout' : 'grin', open: .5 + hey * .4, eye: 1, brow: .5 + hey } };
}
const CHORUS = [CAST.guard, VILLAGERS[0], WIN_FOLK[0], CAST.servant, CAST.noble2, VILLAGERS[2], WIN_FOLK[1], CAST.mother, GUARDS[1], CAST.noble1];
function finaleStage(c, t, z, cy, o = {}) {
  stageBG(c, t, z, 540, cy);
  c.save(); cam(c, 540, cy, z);
  // chorus rows bobbing; set-flat windows pop open on the shouts
  const heys = vocIn(56, 65);
  CHORUS.forEach((ch, i) => { const row = i % 2; drawChar(c, ch, merge({ x: 80 + i * 102, y: 1330 + row * 25, s: .48, f: i % 2 ? 1 : -1, turn: .3 }, dancePose('crowd', t + i * .05)), t); });
  // coins + confetti rain
  particles(c, t, 91, 40, (cc, tt, i, a, b, d, e) => { const u = ((tt - 56) * (.3 + d * .3) + a) % 1; const x = b * W + Math.sin(u * 8 + i) * 40, y = u * 1900 - 100; if (i % 3 === 0) coin(cc, x, y, 14, tt * 8 + i); else { cc.save(); cc.translate(x, y); cc.rotate(tt * 5 + i); cc.fillStyle = ['#ffd34d', '#e8505a', '#5ab0e8', '#7ad07a'][i % 4]; cc.fillRect(-8, -4, 16, 8); cc.restore(); } });
  c.restore();
}
shot(56.0, 57.6, 'F1 curtains fly open - all dance', 'flash', (c, t) => {
  const lt = t - 56, open = E.out(clamp(lt / .5));
  const z = key(lt, [[0, 1.15], [1.6, 1.0, 'out']]);
  finaleStage(c, t, z, 1050);
  c.save(); cam(c, 540, 1050, z);
  drawChar(c, CAST.king, merge({ x: 540, y: 1520, s: .85, f: 1, turn: .05 }, dancePose('king', t)), t);
  drawChar(c, CAST.knocker, merge({ x: 230, y: 1640, s: .95, f: 1, turn: .3 }, dancePose('knocker', t)), t);
  drawChar(c, CAST.groomRich, merge({ x: 540, y: 1700, s: .95 }, dancePose('groom', t)), t);
  drawChar(c, CAST.sineater, merge({ x: 860, y: 1650, s: .95, f: -1, turn: .3 }, dancePose('sineater', t)), t);
  c.restore();
  stageFG(c, t, z, 540, 1050, open);
  speedLines(c, 540, 1100, hit(t, [56], .35) * .7, 5);
});
shot(57.6, 59.2, 'F2 the village answers', 'cut', (c, t) => {
  finaleStage(c, t, 1.35, 1250);
  c.save(); cam(c, 540, 1250, 1.35);
  const heys = vocIn(57.5, 59.3);
  [[200, 1650, VILLAGERS[1]], [400, 1680, WIN_FOLK[2]], [680, 1680, CAST.servant], [880, 1650, GUARDS[3]]].forEach(([x, y, ch], i) => drawChar(c, ch, merge({ x, y, s: .9, f: x < 540 ? 1 : -1, turn: .3 }, dancePose('crowd', t + i * .03)), t));
  c.restore();
  // windows on the painted flats burst open on every shout
  heys.forEach((h, i) => { const k = E.back(clamp((t - h) / .15)); if (k > 0 && t - h < .5) { c.save(); c.globalAlpha = 1 - clamp((t - h - .3) / .2); c.translate(160 + (i * 263) % 760, 300 + (i * 137) % 300); c.scale(k, k); c.font = '110px Luckiest'; c.textAlign = 'center'; c.lineWidth = 18; c.strokeStyle = '#1a0c08'; c.lineJoin = 'round'; const w = VOC.find(v => Math.abs(v[0] - h) < 1e-3)[1]; c.strokeText(w, 0, 0); c.fillStyle = ['#ffd34d', '#ff7a5a', '#8ad0ff'][i % 3]; c.fillText(w, 0, 0); c.restore(); } });
  stageFG(c, t, 1.35, 540, 1250, 1);
});
shot(59.2, 60.8, 'F3 the trio dances', 'cut', (c, t) => {
  const lt = t - 59.2, z = 1.25 + Math.sin(lt * 2) * .05, cx = 540 + Math.sin(lt * 1.5) * 60;
  stageBG(c, t, z, cx, 1250);
  c.save(); cam(c, cx, 1250, z);
  drawChar(c, CAST.knocker, merge({ x: 250, y: 1720, s: 1.0, f: 1, turn: .3 }, dancePose('knocker', t)), t);
  drawChar(c, CAST.groomRich, merge({ x: 540, y: 1760, s: 1.0 }, dancePose('groom', t)), t);
  drawChar(c, CAST.sineater, merge({ x: 840, y: 1720, s: 1.0, f: -1, turn: .3 }, dancePose('sineater', t)), t);
  c.restore();
  motes(c, t, 51, 40, '#ffe0a0', .6, 60);
  stageFG(c, t, z, cx, 1250, 1);
});
shot(60.8, 62.4, 'F4 the king joins: chorus line', 'cut', (c, t) => {
  finaleStage(c, t, 1.0, 1050);
  c.save(); cam(c, 540, 1050, 1.0);
  const line_ = [[120, CAST.knocker, 'knocker', 1], [330, CAST.groomRich, 'groom', 1], [540, CAST.king, 'king', 1], [750, CAST.sineater, 'sineater', -1], [960, GUARDS[0], 'crowd', -1]];
  line_.forEach(([x, ch, who, f], i) => { const kick = Math.max(0, Math.sin((t / SPB + i * .5) * PI)); drawChar(c, ch, merge({ x, y: 1640, s: .82, f, turn: .2 }, dancePose(who, t), who === 'king' || who === 'crowd' ? { hipR: kick * 1.2, kneeR: .1 } : {}), t); });
  c.restore();
  stageFG(c, t, 1.0, 540, 1050, 1);
  sparkles(c, 540, 900, 500, hit(t, vocIn(60.8, 62.4), .25), 12, t);
});
shot(62.4, 64.0, 'F5 which job would you choose?', 'cut', (c, t) => {
  const z = key(t, [[62.4, 1.1], [64.0, 1.0]]);
  finaleStage(c, t, z, 1100);
  c.save(); cam(c, 540, 1100, z);
  const hits2 = [63.2, 63.6];
  const fr = t >= 63.2;
  const heroes = [[230, CAST.knocker, 'knocker', 1, '1'], [540, CAST.groomRich, 'groom', 1, '2'], [850, CAST.sineater, 'sineater', -1, '3']];
  heroes.forEach(([x, ch, who, f, n], i) => {
    const step = E.back(clamp((t - 63.2 - i * .13) / .2));
    const pose = fr ? { shR: 2.8, elR: .1, shL: -.6, elL: .3, handR: who === 'knocker' ? 'hold' : 'open', expr: { mouth: 'grin', open: .7, eye: 1.1, brow: 1.2 }, hold: who === 'knocker' ? holdPole(.15, 700, 120) : null } : dancePose(who, t);
    drawChar(c, ch, merge({ x, y: 1700 + step * 60, s: .98 + step * .08, f, turn: .2 }, pose), t);
    if (fr) { c.save(); c.translate(x, 1000 + (1 - step) * 80); c.scale(step, step); ell(c, 0, 0, 64, 64, lg(c, 0, -64, 0, 64, [[0, '#fff0a0'], [1, '#c8862a']]), 7); c.font = '900 84px CinzelD'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillStyle = '#4a2408'; c.fillText(n, 0, 6); c.restore(); }
  });
  c.restore();
  stageFG(c, t, z, 540, 1100, 1);
  flash(c, t, hits2, '#fff6e0', .07, .35);
});
shot(64.0, 65.01, 'F6 tail: knock-knock -> loop', 'cut', (c, t) => {
  // ease back into the exact opening composition (t=0 frame) for a seamless loop
  const lt = t - 64.0, k = E.io(clamp(lt / .9));
  const z = lerp(1.0, 1.12, k);
  stageBG(c, t, z, 540, 1000);
  c.save(); cam(c, 540, 1000, z);
  for (let i = 0; i < 7; i++) { const f = townsfolk(300 + i); drawChar(c, f, merge({ x: 120 + i * 140, y: 1330, s: .42, f: i % 2 ? 1 : -1, turn: .3 }, walkPose(t + i * .2, { amp: .4 }), { expr: { mouth: 'grin', open: .3 } }), t); }
  // crouch (anticipation) for the jump that the loop's first frame continues
  const crouch = E.io(clamp((lt - .45) / .5));
  const taps = [64.4, 64.6, 64.8], tk = hit(t, taps, .1);
  trio(c, 0.0 + lt * 0, { k1: { air: 0, sq: 1 - crouch * .15, kneeR: .3 + crouch * .9, kneeL: .5 + crouch * .9, hipR: .2 + crouch * .5, hipL: -.25 + crouch * .5, shR: 2.6 - tk * .15, expr: { mouth: 'grin', open: .4, eye: 1, brow: .8 }, hold: holdPole(.35 - tk * .1, 760, 150) },
    k2: { air: 0, sq: 1 - crouch * .12, kneeR: .1 + crouch * .9, kneeL: .2 + crouch * .9, hipR: .1 + crouch * .5, hipL: -.15 + crouch * .5 }, k3: { air: 0, sq: 1 - crouch * .1, kneeR: .25 + crouch * .8, kneeL: .3 + crouch * .8, hipR: .15 + crouch * .5 } });
  c.restore();
  stageFG(c, t, z, 540, 1000);
  if (tk > .2) { c.save(); c.translate(250, 520); c.font = '80px Luckiest'; c.textAlign = 'center'; c.lineWidth = 14; c.strokeStyle = '#1a0c08'; c.lineJoin = 'round'; c.strokeText('tap!', 0, 0); c.fillStyle = '#fff'; c.fillText('tap!', 0, 0); c.restore(); }
});

// final question text (spans F5 + tail)
window.overlay = (c, t) => {
  if (t >= 62.3) {
    const k = E.back(clamp((t - 62.3) / .4));
    c.save(); c.translate(540, 360); c.scale(k, k);
    const b = 1 + hit(t, [63.2, 63.6, 64.0], .15) * .08; c.scale(b, b);
    c.fillStyle = 'rgba(14,6,12,0.5)'; c.beginPath(); c.roundRect(-470, -150, 940, 260, 40); c.fill();
    richLine(c, 'WHICH JOB', 0, -60, 104, t - 62.3, {});
    richLine(c, 'WOULD YOU *CHOOSE?*', 0, 50, 84, t - 62.3, {});
    c.restore();
  }
};
