// ===================================================================== shots.js  (opening + profession 1)
'use strict';
const SHOTS = [];
const shot = (a, b, name, tr, draw) => SHOTS.push({ a, b, name, tr, draw });
const blink = (t, s = 0) => { const p = (t + s * 1.37) % 3.1; return p < .12 ? Math.abs(p - .06) / .06 : 1; };
const bars = b => b * BAR;

// ---------- shared: stage trio (opening + loop target)
function stageBG(c, t, zoom = 1, cx = 540, cy = 960) {
  c.save(); cam(c, cx, cy, zoom);
  c.drawImage(SETS.stage.bg, 0, 0);
  // moving spotlights
  for (const [x0, ph, col] of [[150, 0, 'rgba(255,230,170,0.22)'], [930, 2, 'rgba(200,220,255,0.18)'], [540, 4, 'rgba(255,200,140,0.18)']]) {
    const ang = Math.sin(t * 1.3 + ph) * .25;
    c.save(); c.globalCompositeOperation = 'lighter'; c.translate(x0, 0); c.rotate(ang);
    c.fillStyle = lg(c, 0, 0, 0, 1600, [[0, col], [1, 'rgba(0,0,0,0)']]); c.beginPath(); c.moveTo(-30, 0); c.lineTo(30, 0); c.lineTo(260, 1600); c.lineTo(-260, 1600); c.fill(); c.restore();
  }
  c.restore();
}
function stageFG(c, t, zoom = 1, cx = 540, cy = 960, open = 0) {
  c.save(); cam(c, cx, cy, zoom);
  // footlights
  for (let i = 0; i < 9; i++) { const x = 80 + i * 115; ell(c, x, 1880, 34, 16, '#3a2a1a', 3); glow(c, x, 1860, 160, 'rgba(255,200,120,0.25)'); }
  c.restore();
  c.save(); cam(c, cx, cy, zoom * (1 + open * .1));
  if (open > 0) { c.translate(0, 0); }
  c.save(); c.translate(-open * 260, 0); c.drawImage(SETS.prosc, 0, 0, 540, H, 0, 0, 540, H); c.restore();
  c.save(); c.translate(open * 260, 0); c.drawImage(SETS.prosc, 540, 0, 540, H, 540, 0, 540, H); c.restore();
  c.restore();
}
// knocker pole held in the near hand, pointing up-forward at angle a (rad from vertical)
const holdPole = (a, len = 880, back = 190, behind = false) => ({ R: Object.assign((c, J) => { const h = J.handNear, dx = Math.sin(a), dy = -Math.cos(a); pole(c, h[0] - dx * back, h[1] - dy * back, h[0] + dx * len, h[1] + dy * len); }, { back: behind }) });
const holdBread = (s = .45) => ({ R: (c, J) => bread(c, J.handNear[0] + 10, J.handNear[1] - 20, s) });
const holdLinen = { R: (c, J) => { rrect(c, J.handNear[0] - 60, J.handNear[1] - 110, 120, 90, 10, '#f4efe2', 4); line(c, [[J.handNear[0] - 56, J.handNear[1] - 80], [J.handNear[0] + 56, J.handNear[1] - 80]], 3, '#c8a040'); } };
const holdPot = (s = .32) => ({ R: (c, J) => closeStool(c, J.handNear[0] + 20, J.handNear[1] + 70, s, 0, 0) });

function trio(c, t, o = {}) {
  // o.k: 0..1 dance intensity ; o.pose: 'open' | 'dance'
  const g = 1560;
  const jumpAir = key(t, [[0, 170], [.2, 0, 'in']]);
  const land = wob(t, .2, .16, 3);
  const hits = [0.4, 0.8, 1.2];
  const pk = n => hit(t, [hits[n]], .25);
  // knocker
  const kpose = merge({ x: 250, y: g, s: 1.0, f: 1, air: jumpAir, sq: 1 - land * .12, turn: .25, lean: -.05 + .1 * pk(0),
    hipR: .2, kneeR: .3, hipL: -.25, kneeL: .5, shR: 2.4 - .4 * pk(1), elR: .3, shL: -.5, elL: .6, handR: 'hold', head: -.1 + .15 * pk(0),
    expr: { mouth: 'grin', open: .3 + .4 * pk(2), eye: blink(t, 1) * (1 + .2 * pk(0)), lookX: .6, brow: .5 + pk(0) }, hold: holdPole(.35, 760, 150) }, o.k1);
  drawChar(c, CAST.knocker, kpose, t);
  // groom with close stool (pot) presented
  const gpose = merge({ x: 545, y: g + 30, s: 1.0, f: 1, air: jumpAir * .8, sq: 1 - land * .1, turn: .1, lean: .05 - .1 * pk(1),
    hipR: .1, kneeR: .1, hipL: -.15, kneeL: .2, shR: .9 + .25 * pk(1), elR: 1.1, shL: .7, elL: 1.2, handR: 'open', handL: 'open',
    expr: { mouth: 'smirk', lids: .35, eye: blink(t, 2), lookX: .1, brow: .6 * pk(1) }, hold: { R: (cc, J) => closeStool(cc, J.handNear[0] - 30, J.handNear[1] + 80, .38, .25 * pk(1), .8) } }, o.k2);
  drawChar(c, CAST.groom, gpose, t);
  // sin-eater with bread
  const spose = merge({ x: 885, y: g, s: 1.0, f: -1, air: jumpAir * .6, sq: 1 - land * .08, turn: .3, lean: .08,
    hipR: .15, kneeR: .25, hipL: -.1, kneeL: .3, shR: .05 + .2 * pk(2), elR: 2.25, shL: -.2, elL: .3, handR: 'hold',
    expr: { mouth: 'flat', eye: .75 * blink(t, 3), lookX: .8, lookY: -.2, brow: -.3 }, hold: holdBread(.42) }, o.k3);
  drawChar(c, CAST.sineater, spose, t);
}

// =============================================================== OPENING 0.0 - 3.2
shot(0, 1.6, 'O1 trio stage', 'cut', (c, t) => {
  const z = key(t, [[0, 1.12], [1.6, 1.0, 'out']]);
  stageBG(c, t, z, 540, 1000);
  c.save(); cam(c, 540, 1000, z);
  // dancers silhouettes behind (life)
  for (let i = 0; i < 7; i++) { const f = townsfolk(300 + i); drawChar(c, f, merge({ x: 120 + i * 140, y: 1330, s: .42, f: i % 2 ? 1 : -1, turn: .3 }, walkPose(t + i * .2, { amp: .4 }), { expr: { mouth: 'grin', open: .3 } }), t); }
  trio(c, t);
  c.restore();
  stageFG(c, t, z, 540, 1000);
  speedLines(c, 540, 1100, hit(t, [0], .3) * .5, 4);
  flash(c, t, [0.0], '#fff6e0', .08, .22);
});
function ecuGlass(c, t, taps) {
  // extreme close-up: pole tip tapping a frosty window pane
  c.fillStyle = lg(c, 0, 0, 0, H, [[0, '#1a2448'], [1, '#3a4a7a']]); c.fillRect(0, 0, W, H);
  bricks(c, 0, 0, W, H, '#8a4a32', 5, 150, 64);
  rrect(c, 140, 200, 800, 1500, 8, '#e8e0cc', 14);
  c.fillStyle = lg(c, 160, 220, 920, 1680, [[0, '#2a3a6a'], [.5, '#1a2244'], [1, '#3a4a7a']]); c.fillRect(160, 220, 760, 1460);
  for (let i = 0; i < 60; i++) { const r = rng(i * 7); ell(c, 160 + r() * 760, 220 + r() * 1460, 4 + r() * 18, 2 + r() * 8, 'rgba(220,235,255,0.18)'); }
  line(c, [[540, 220], [540, 1680]], 24, '#e8e0cc'); line(c, [[160, 950], [920, 950]], 24, '#e8e0cc');
  const k = hit(t, taps, .09);
  for (const tp of taps) if (t > tp && t < tp + .6) { const u = (t - tp) / .6; ell(c, 700, 700, 40 + u * 260, (40 + u * 260) * .8, null, 6 * (1 - u), 0, `rgba(230,240,255,${.8 * (1 - u)})`); }
  const pull = 1 - k;
  pole(c, 1300, 1700, 700 + pull * 60, 700 + pull * 50);
  sparkles(c, 700, 700, 120, k, 3, t);
}
shot(1.6, 2.0, 'O2 ECU pole on glass', 'cut', (c, t) => { c.save(); const z = 1 + (t - 1.6) * .3; cam(c, 600, 800, z); ecuGlass(c, t, [1.6, 1.8]); c.restore(); });
shot(2.0, 2.4, 'O3 ECU royal close stool', 'cut', (c, t) => {
  c.fillStyle = rg(c, 540, 900, 50, 1100, [[0, '#8a1a2a'], [1, '#2a0610']]); c.fillRect(0, 0, W, H);
  lightShafts(c, 540, -100, 0, 500, 1800, '#ffd890', .14);
  const z = 1.55 + (t - 2) * .5;
  c.save(); cam(c, 540, 1050, z * .7);
  closeStool(c, 540, 1300, 1.2, .35 + .1 * Math.sin(t * 8), 1);
  // white-gloved hand polishing with a cloth
  const hx = 640 + Math.sin(t * 20) * 50;
  blob(c, [[hx - 60, 1060], [hx + 60, 1040], [hx + 80, 1110], [hx - 50, 1130]], '#fbf7ee', 5);
  rrect(c, hx - 30, 1100, 140, 70, 20, '#f4efe2', 5);
  c.restore();
  sparkles(c, 540, 1000, 380, 1, 9, t);
});
shot(2.4, 2.8, 'O4 ECU bread + candle', 'cut', (c, t) => {
  c.fillStyle = rg(c, 540, 1100, 50, 1100, [[0, '#3a2a40'], [1, '#08060e']]); c.fillRect(0, 0, W, H);
  const z = 1 + (t - 2.4) * .25;
  c.save(); cam(c, 540, 1050, z);
  candle(c, 820, 1500, 260, t, 1, 1.4);
  // pale hands cupping the bread
  for (const s of [-1, 1]) blob(c, [[540 + s * 260, 1300], [540 + s * 120, 1240], [540 + s * 10, 1330], [540 + s * 120, 1420], [540 + s * 300, 1400]], '#d8b8a0', 5);
  bread(c, 540, 1240, 1.6);
  // hood edge foreground
  blob(c, [[-100, -100], [1180, -100], [1180, 380], [900, 220], [540, 160], [180, 230], [-100, 400]], '#1c191c', 0);
  c.restore();
  motes(c, t, 4, 40, '#ffcf8a', .5, 20);
});
shot(2.8, 3.2, 'O5 trio push + HA', 'cut', (c, t) => {
  const z = key(t, [[2.8, 1.0], [3.0, 1.18, 'out'], [3.2, 1.3, 'in']]);
  stageBG(c, t, z, 540, 1150);
  c.save(); cam(c, 540, 1150, z);
  const ha = hit(t, [3.0], .3);
  trio(c, t, { k1: { shL: .9 + ha * 1.2, elL: 0, handL: 'point', expr: { mouth: 'shout', open: .8, brow: 1.4 } }, k2: { shL: 1.2 * ha + .7, elL: .3, handL: 'point', expr: { mouth: 'grin', open: .6 } },
    k3: { shL: 1.0 * ha, elL: .1, handL: 'point', expr: { mouth: 'flat', eye: 1 } } });
  c.restore();
  stageFG(c, t, z, 540, 1150);
  speedLines(c, 540, 1100, ha * .7, 6);
});

// =============================================================== PROFESSION 1: KNOCKER-UP 3.2 - 20.8
function townScene(c, t, camX, opts = {}) {
  const S = SETS.town, g = S.ground;
  c.drawImage(S.sky, 0, 0);
  // dawn brightening over the section
  c.save(); c.globalAlpha = clamp((t - 3.2) / 16) * .35; c.fillStyle = lg(c, 0, 0, 0, H, [[0, '#ffb070'], [1, '#ffe0b0']]); c.fillRect(0, 0, W, H); c.restore();
  c.drawImage(S.far, -camX * .35 - 100, 0);
  for (const [x, h] of [[300, 520], [900, 640], [1500, 560], [2100, 600]]) smokePlume(c, x - camX * .35 - 100, 1180 - h, t, '#3a4266', x, 1.2);
  fogBand(c, 1150, 200, t, '#9aa8d0', .22, 25, 5);
  c.drawImage(S.mid, -camX, 0);
  for (let i = 0; i < 9; i++) smokePlume(c, i * 300 + 220 - camX, 1460 - 520 - 220, t + i, '#8a8aa0', i + 20, .5);
  c.drawImage(S.street, -camX, g);
  // cat on a wall-top (life)
  const catX = 1300 - camX + ((t * 60) % 1400);
  if (opts.cat !== false) { c.save(); c.translate(catX, 1200); blob(c, [[-40, 0], [-30, -30], [20, -34], [40, -10], [30, 10], [-30, 10]], '#141418'); ell(c, 44, -36, 20, 18, '#141418'); poly(c, [[34, -50], [40, -66], [48, -50]], '#141418'); poly(c, [[50, -50], [58, -66], [62, -48]], '#141418'); curve(c, [[-40, -4], [-70, -30 + Math.sin(t * 5) * 10], [-80, -60]], 7, '#141418'); ell(c, 52, -38, 3, 3, '#ffd040'); c.restore(); }
  for (const lx of [500, 1450, 2350]) lamp(c, lx - camX * 1.15, g + 160, 520, 1);
}
function knockerWalk(c, t, x, y, s, o = {}) {
  const wp = walkPose(t, { amp: 1, strut: .5 });
  return drawChar(c, CAST.knocker, merge({ x, y, s, f: 1, turn: .4 }, wp, { shR: .5, elR: -1.6, handR: 'hold', expr: { mouth: 'smile', eye: blink(t), lookX: .5 }, hold: holdPole(-.62 + Math.sin(t * PI / SPB) * .04, 760, 260, true) }, o), t);
}
shot(3.2, 6.4, 'K1 town tracking walk', 'whip', (c, t) => {
  const lt = t - 3.2, camX = 300 + lt * 140;
  townScene(c, t, camX);
  // early milk-woman walking the other way (background life)
  const mf = townsfolk(611);
  drawChar(c, mf, merge({ x: 1500 - camX - lt * 120 + 400, y: 1520, s: .55, f: -1 }, walkPose(t + .2, { amp: .8 }), { expr: { mouth: 'smile' } }), t);
  // the knocker: answer-bar gestures on the shouts
  const hey = vocIn(4.7, 6.4);
  const tip = hit(t, [4.8], .35), spin = clamp((t - 5.4) / .4), ha = hit(t, [6.2], .3);
  let o = {};
  if (t > 4.75 && t < 5.3) o = { shL: 2.6 * tip + .3, elL: 1.8, handL: 'open', expr: { mouth: 'grin', open: .5, brow: 1 } };
  if (t >= 5.4 && t < 5.8) o = { f: Math.cos(spin * TAU) >= 0 ? 1 : -1, turn: Math.abs(Math.sin(spin * TAU)) * .8 + .2, expr: { mouth: 'o', open: .6 } };
  if (t >= 6.1) o = { shL: 2.8, elL: .2, handL: 'point', expr: { mouth: 'shout', open: .8, brow: 1.5 }, lean: -.1 };
  const bump = hey.length ? hit(t, hey, .12) : 0;
  knockerWalk(c, t, 540 + Math.sin(lt * .7) * 20, 1700, 1.25, Object.assign({ air: bump * 18 }, o));
  fogBand(c, 1700, 120, t, '#c0c8e8', .15, 40, 8);
  chapterCard(c, t, '1', 'THE HUMAN ALARM CLOCK', 3.3, 6.1, '#3a6a9a');
});
// bedroom with snoring worker. wake: 0 asleep .. 1 awake
function bedroom(c, t, wake, o = {}) {
  c.drawImage(SETS.bedroom.bg, 0, 0);
  // window light flicker when tapped
  const tapK = o.tapK || 0;
  glow(c, 750, 520, 500, `rgba(150,180,255,${.15 + tapK * .3})`);
  candle(c, 230, 830, 90, t, 3, .9);
  // bed
  rrect(c, 120, 1180, 860, 60, 14, '#3a2a2a', 5);
  line(c, [[150, 1240], [150, 1560]], 22, '#2a2a30'); line(c, [[950, 1240], [950, 1560]], 22, '#2a2a30');
  line(c, [[130, 1000], [130, 1560]], 18, '#2a2a30'); for (let i = 0; i < 5; i++) line(c, [[130, 1020 + i * 40], [170, 1020 + i * 40]], 8, '#2a2a30'); ell(c, 130, 990, 20, 20, '#c8a040', 4);
  const breath = o.breath ?? 0;
  const sit = E.back(clamp(wake));
  // pillow
  blob(c, [[170, 1080], [200, 1010], [420, 1000], [450, 1080], [400, 1130], [200, 1130]], '#f2eee4', 5);
  // sleeper: when asleep we draw head on pillow; when awake the full rig sits up
  if (sit < .02) {
    drawHeadOnly(c, CAST.sleeper, 320, 1080, -1.25 + Math.sin(t * 1.2) * .03, 1.05, merge({ turn: .1, capDroop: .15 }, { expr: o.expr || { eye: 0, mouth: 'snore', open: .3 + breath * .6, blush: .4 } }));
  } else {
    drawChar(c, CAST.sleeper, merge({ x: 360, y: 1250, s: 1.05, f: 1, turn: .2, lean: lerp(-1.3, .1, sit) + (o.lean || 0), air: (o.air || 0), hipR: 1.45, kneeR: .1, hipL: 1.5, kneeL: .1, capDroop: .2 }, o.pose || {}), t);
  }
  // quilt (patchwork) covering legs, breathing
  const qy = 1110 - breath * 26 - sit * 40;
  const quilt = [[190, qy + 40], [330, qy - 10 + (sit > .1 ? 60 : 0)], [600, qy - 30], [930, qy + 10], [980, 1300], [940, 1380], [180, 1390], [150, 1250]];
  blob(c, quilt, '#c84a3a', 5);
  c.save(); c.beginPath(); spline(c, quilt); c.clip();
  const pr = rng(4); for (let i = 0; i < 10; i++) for (let j = 0; j < 4; j++) { c.fillStyle = ['#d8a040', '#3a6a8a', '#c84a3a', '#5a8a4a', '#e8dcc0'][Math.floor(pr() * 5)]; c.fillRect(150 + i * 90, qy - 40 + j * 90, 88, 88); }
  for (let i = 0; i < 10; i++) line(c, [[150 + i * 90, qy - 60], [150 + i * 90, 1400]], 3, 'rgba(60,30,20,0.5)');
  c.fillStyle = lg(c, 0, qy - 40, 0, 1390, [[0, 'rgba(255,240,220,0.15)'], [1, 'rgba(20,10,20,0.45)']]); c.fillRect(0, qy - 60, W, 600);
  c.restore();
}
function drawHeadOnly(c, ch, x, y, ang, s, p) {
  const pp = P(p); c.save(); c.translate(x, y); c.rotate(ang); c.scale(s, s); drawHead(c, ch, pp, s, 5); c.restore();
}
function dreamBubble(c, t, x, y, a) {
  if (a <= 0) return;
  c.save(); c.globalAlpha = a;
  ell(c, x - 140, y + 190, 16, 16, '#f4f2ff', 4); ell(c, x - 90, y + 140, 26, 26, '#f4f2ff', 4);
  blob(c, [[x - 170, y], [x - 120, y - 110], [x, y - 150], [x + 140, y - 120], [x + 190, y - 10], [x + 120, y + 90], [x - 20, y + 110], [x - 150, y + 80]], '#f4f2ff', 5);
  // sheep jumping a fence on every beat
  const ph = bphase(t), jx = x - 80 + ph * 160, jy = y + 30 - Math.sin(ph * PI) * 70;
  line(c, [[x - 10, y + 60], [x - 10, y + 10]], 6, '#7a5a3a'); line(c, [[x + 30, y + 60], [x + 30, y + 10]], 6, '#7a5a3a'); line(c, [[x - 20, y + 25], [x + 40, y + 25]], 6, '#7a5a3a');
  for (let i = 0; i < 6; i++) ell(c, jx + Math.cos(i) * 22, jy + Math.sin(i) * 14, 18, 16, '#fff', 3);
  ell(c, jx + 34, jy - 4, 13, 15, '#3a3a3a', 3);
  c.restore();
}
shot(6.4, 8.0, 'K2 bedroom snore', 'cut', (c, t) => {
  const lt = t - 6.4, z = 1.15 + lt * .06;
  c.save(); cam(c, 520, 1100, z);
  const breath = .5 - .5 * Math.cos((t - 6.4) / 1.6 * TAU);
  bedroom(c, t, 0, { breath });
  c.restore();
  zzz(c, 440, 820, t, 1);
  dreamBubble(c, t, 700, 640, clamp((t - 6.6) * 3));
  subtitle(c, t, 'Workers *paid* people\nto wake them up.', 6.5, 9.4);
});
shot(8.0, 8.8, 'K3a ECU tap glass', 'cut', (c, t) => { c.save(); cam(c, 640, 820, 1.15 + (t - 8) * .2); ecuGlass(c, t, patT(5, 'x.x...x..x.x.x..')); c.restore(); subtitle(c, t, 'Workers *paid* people\nto wake them up.', 6.5, 9.4); });
shot(8.8, 9.6, 'K3b low-angle knocker tapping', 'cut', (c, t) => {
  const S = SETS.town;
  c.save(); cam(c, 560, 900, 1.05);
  c.drawImage(S.sky, 0, 0); c.drawImage(S.mid, -1450, -180);
  c.restore();
  const taps = patT(5, 'x.x...x..x.x.x..').filter(v => v > 8.7);
  const k = hit(t, taps, .1);
  const a = -.08 + (1 - k) * .1;
  drawChar(c, CAST.knocker, { x: 380, y: 1960, s: 1.6, f: 1, turn: .55, lean: -.15, hipR: .2, kneeR: .1, hipL: -.15, kneeL: .1, shR: 2.7 + k * .1, elR: -.2, shL: 2.4, elL: .2, handR: 'hold', handL: 'hold', head: -.35,
    expr: { mouth: 'grin', open: .2 + k * .3, eye: blink(t), lookX: .8, lookY: -.8, brow: .6 }, hold: holdPole(a, 760, 120) }, t);
  fogBand(c, 1800, 160, t, '#c0c8e8', .2, 30, 9);
  subtitle(c, t, 'Workers *paid* people\nto wake them up.', 6.5, 9.4);
});
shot(9.6, 11.2, 'K4 worker wakes', 'cut', (c, t) => {
  const lt = t - 9.6;
  const wake = clamp(lt / .25);
  const shake_ = shake(t, [9.6], 18, .15);
  c.save(); c.translate(shake_[0], shake_[1]); cam(c, 520, 1060, 1.12 + hit(t, [9.6], .4) * .12);
  const angry = t > 10.35 && t < 10.8, wave = t >= 10.8;
  const pose = { shR: angry ? 2.6 : wave ? 2.9 + Math.sin(t * 18) * .25 : 1.8, elR: angry ? 1.6 : .2, handR: angry ? 'fist' : 'open', shL: 1.6, elL: .4,
    expr: angry ? { eye: 1, mouth: 'teeth', brow: -.4, browAng: .9, lookX: 1 } : wave ? { eye: 1, mouth: 'grin', open: .5, brow: .4, lookX: 1 } : { eye: 1.3, mouth: 'shout', open: 1.1, brow: 1.8, lookY: -.3 }, head: angry ? .2 : 0 };
  bedroom(c, t, wake, { tapK: hit(t, [9.6], .3), pose, air: hit(t, [9.75], .25) * 60, lean: angry ? .25 : 0 });
  c.restore();
  if (lt < .5) speedLines(c, 420, 900, (1 - lt * 2) * .6, 12);
  // shocked hair / nightcap flies on the snap
  if (t > 9.6 && t < 10.6) { const u = (t - 9.6) / 1.0; c.save(); c.translate(380 + u * 500, 760 - Math.sin(u * PI) * 380); c.rotate(u * 8); nightcap('#6d8fbf', '#f2eee0')(c, 128, 140, P({}), 5, 0); c.restore(); }
});
// terrace facade with animated windows
function facadeWindows(c, t, open) {
  const wins = [[80, 420], [420, 420], [760, 420], [80, 820], [760, 820]];
  wins.forEach(([x, y], i) => {
    const o = open[i] || 0;
    c.fillStyle = '#1a1420'; c.fillRect(x, y, 240, 300);
    if (o > 0) { c.fillStyle = lg(c, x, y, x, y + 300, [[0, '#ffcf7a'], [1, '#e08a40']]); c.globalAlpha = Math.min(1, o * 1.5); c.fillRect(x, y, 240, 300); c.globalAlpha = 1; }
  });
  return wins;
}
function windowFrame(c, x, y, o) {
  // sash slides up by o
  c.lineWidth = 16; c.strokeStyle = '#d8d0bc'; c.strokeRect(x - 8, y - 8, 256, 316); c.lineWidth = 4; c.strokeStyle = INK; c.strokeRect(x - 16, y - 16, 272, 332);
  const sy = y - o * 150;
  c.save(); c.beginPath(); c.rect(x - 20, y - 170, 280, 480); c.clip();
  rrect(c, x, sy, 240, 150, 3, o < .5 ? 'rgba(40,60,110,0.85)' : 'rgba(150,180,230,0.18)', 8, '#ece4d0'); line(c, [[x + 120, sy], [x + 120, sy + 150]], 6, '#ece4d0');
  c.restore();
  rrect(c, x, y + 150, 240, 150, 3, o < .5 ? 'rgba(40,60,110,0.85)' : 'rgba(150,180,230,0.12)', 8, '#ece4d0'); line(c, [[x + 120, y + 150], [x + 120, y + 300]], 6, '#ece4d0');
  rrect(c, x - 26, y + 300, 292, 22, 4, '#bfb6a0', 5);
}
const WIN_FOLK = [townsfolk(41), Object.assign(townsfolk(42), { hat: bonnet('#e8e0d0') }), townsfolk(43), Object.assign({}, CAST.sleeper, { name: 'capman' }), townsfolk(45)];
shot(11.2, 12.8, 'K5 windows open in sequence', 'cut', (c, t) => {
  const z = 1.0 + (t - 11.2) * .04;
  c.save(); cam(c, 540, 960, z);
  c.drawImage(SETS.facade.bg, 0, 0);
  const vs = vocIn(11.15, 12.8).slice(0, 5);   // HEY HEY HOO HEY HEY -> windows
  const times = [vs[0] ?? 11.2, vs[1] ?? 11.5, vs[2] ?? 11.8, vs[3] ?? 12.0, vs[4] ?? 12.3];
  const op = times.map(tt => E.back(clamp((t - tt) / .18)));
  const wins = facadeWindows(c, t, op);
  wins.forEach(([x, y], i) => {
    const o = op[i]; const ch = WIN_FOLK[i];
    if (o > .05) {
      c.save(); c.beginPath(); c.rect(x, y, 240, 300); c.clip();
      const pop = clamp((t - times[i]) / .25);
      const reacts = [
        { y: y + 470 - E.back(pop) * 110, air: 0, shR: 2.8, elR: .2, shL: 2.8, elL: .2, expr: { mouth: 'shout', open: 1, eye: 1.3, brow: 1.8 } },      // jumps up
        { y: y + 470, shR: 2.4 + Math.sin(t * 20) * .2, elR: 1.6, handR: 'fist', expr: { mouth: 'teeth', browAng: 1, eye: .9, lookX: .3, lookY: .4 } }, // annoyed
        { y: y + 470, turn: .9, f: -1, expr: { mouth: 'o', open: .6, eye: 1, lookX: -1, brow: 1 }, head: .3 },                                      // wrong window (looking the wrong way)
        { y: y + 470, shR: 1.5, elR: .6, expr: { mouth: 'o', open: .9, eye: 1.2, lookY: .8, brow: 1.5 }, head: .2 },                                  // drops nightcap
        { y: y + 470 + Math.sin(t * 25) * 10, shR: .5 + Math.sin(t * 30) * .6, elR: 1.0, shL: .8 + Math.cos(t * 30) * .6, elL: 1, expr: { mouth: 'grin', open: .8, eye: 1.2, brow: 1.5 }, lean: Math.sin(t * 25) * .1 },  // frantic dressing
      ][i];
      drawChar(c, ch, merge({ x: x + 120, s: .72, f: 1, turn: .2 }, reacts, { expr: Object.assign({ eye: 1 }, reacts.expr) }), t);
      c.restore();
    }
    windowFrame(c, x, y, op[i]);
  });
  // falling nightcap from window 4 (index 3) down to the street
  if (t > times[3]) { const u = clamp((t - times[3]) / .7); c.save(); c.translate(200 + u * 120, 860 + E.in(u) * 900); c.rotate(u * 5); nightcap('#d8506a', '#fff')(c, 120, 130, P({}), 5, 0); c.restore(); }
  // knocker in foreground with pole sweeping between windows
  const sweep = key(t, times.map((tt, i) => [tt, [-.5, 0, .45, -.45, .45][i]]).concat([[12.8, .2]]));
  drawChar(c, CAST.knocker, { x: 300, y: 2150, s: 1.45, f: 1, turn: .5, shR: 2.6, elR: 0, shL: 2.3, elL: .3, handR: 'hold', handL: 'hold', head: -.3, lean: -.1,
    expr: { mouth: 'grin', open: .3, eye: 1, lookY: -1, lookX: .5 }, hold: holdPole(sweep, 900, 100) }, t);
  c.restore();
  subtitle(c, t, 'They tapped on *bedroom windows*\nevery morning.', 11.2, 14.2, { y: 220, size: 58 });
});
shot(12.8, 13.6, 'K6a annoyed neighbour CU', 'cut', (c, t) => {
  c.drawImage(SETS.wallwin.bg, 0, 0);
  rrect(c, 170, 420, 740, 980, 10, '#ffcf7a'); glow(c, 540, 900, 600, 'rgba(255,190,90,0.4)');
  c.save(); c.beginPath(); c.rect(170, 420, 740, 980); c.clip();
  const shakeF = Math.sin(t * 28) * .25;
  drawChar(c, WIN_FOLK[1], { x: 540, y: 2050, s: 1.9, f: -1, turn: .1, shR: 2.5 + shakeF, elR: 1.5, handR: 'fist', shL: .4, elL: .8, head: Math.sin(t * 14) * .06,
    expr: { mouth: 'teeth', browAng: 1, brow: -.2, eye: .85, lookX: -.2, lookY: .3 } }, t);
  // hair curlers
  c.restore();
  windowFrame(c, 170, 420, 1);
  subtitle(c, t, 'They tapped on *bedroom windows*\nevery morning.', 11.2, 14.2, { y: 220, size: 58 });
});
shot(13.6, 14.4, 'K6b frantic dressing CU', 'cut', (c, t) => {
  c.drawImage(SETS.bedroom.bg, 0, 0);
  const knocks = [13.9, 14.2].filter(Boolean), k = hit(t, knocks, .12);
  c.save(); cam(c, 540, 1100, 1.3);
  const hop = Math.abs(Math.sin((t - 13.6) * PI / SPB)) * 60;
  drawChar(c, WIN_FOLK[4], { x: 540, y: 1600, s: 1.25, f: 1, air: hop, hipR: 1.1, kneeR: 1.3, hipL: -.1, kneeL: .1, shR: .3, elR: 1.6, shL: .2, elL: 1.6, lean: .2 + Math.sin(t * 15) * .1,
    expr: { mouth: 'shout', open: .7 + k * .4, eye: 1.2 + k * .2, brow: 1.6, lookX: .8 } }, t);
  // trousers half on
  blob(c, [[440, 1250 - hop], [560, 1240 - hop], [600, 1500], [520, 1520 - hop * .5], [470, 1380 - hop]], '#4a4a6a', 5);
  c.restore();
  if (k > .1) { c.save(); c.translate(760, 600); c.rotate(.2); c.font = '90px Luckiest'; c.lineWidth = 14; c.strokeStyle = '#1a0c08'; c.strokeText('KNOCK!', 0, 0); c.fillStyle = '#ffd34d'; c.fillText('KNOCK!', 0, 0); c.restore(); }
  subtitle(c, t, 'They tapped on *bedroom windows*\nevery morning.', 11.2, 14.2, { y: 220, size: 58 });
});
shot(14.4, 16.0, 'K7 coins into pocket', 'cut', (c, t) => {
  const camX = 1200;
  townScene(c, t, camX, { cat: false });
  const hey = vocIn(14.35, 16.0);
  // payer in doorway
  drawChar(c, WIN_FOLK[0], { x: 260, y: 1720, s: 1.2, f: 1, turn: .3, shR: 1.6, elR: .4, expr: { mouth: 'smile', eye: blink(t, 4), lookX: 1 } }, t);
  const J = drawChar(c, CAST.knocker, { x: 740, y: 1760, s: 1.3, f: -1, turn: .3, shR: 1.3, elR: .9, handR: 'open', shL: -.3, elL: .2, lean: .05 + hit(t, hey, .15) * .06, air: hit(t, hey, .12) * 20,
    expr: { mouth: 'grin', open: .3 + hit(t, hey, .2) * .5, eye: blink(t, 2), lookX: -.6, lookY: .3, brow: .8 }, hold: holdPole(.25, 800, 400) }, t);
  // coins arc from payer's hand to the knocker's palm, one per shout
  hey.forEach((h, i) => {
    const u = (t - h + .3) / .45;
    if (u > 0 && u < 1.2) { const uu = clamp(u); const x = lerp(400, 640, uu), y = lerp(1250, 1240, uu) - Math.sin(uu * PI) * 260; coin(c, x, y, 26, t * 14 + i, '#f0c040'); if (u >= 1) sparkles(c, 640, 1240, 60, 1 - (u - 1) * 5, i, t); }
  });
  const n = hey.filter(h => t > h + .15).length;
  c.font = '72px Luckiest'; c.textAlign = 'center'; c.lineWidth = 14; c.strokeStyle = '#1a0c08'; c.lineJoin = 'round';
  if (n) { const p = 1 + hit(t, hey.map(h => h + .15), .15) * .3; c.save(); c.translate(930, 880); c.scale(p, p); c.strokeText('+' + n, 0, 0); c.fillStyle = '#ffd34d'; c.fillText('+' + n, 0, 0); c.restore(); }
  subtitle(c, t, 'He was literally a\n*human alarm clock.*', 14.4, 17.4);
});
shot(16.0, 17.6, 'K8 pole dance', 'cut', (c, t) => {
  townScene(c, t, 1700 + (t - 16) * 60, { cat: false });
  const ph = (t - 16) / BAR;
  const spinA = (t - 16) * PI * 2.5;
  const ho = hit(t, [16.0, 16.8], .3);
  const pose = merge(walkPose(t, { amp: .6, strut: 1 }), { x: 540 + Math.sin(ph * TAU) * 70, y: 1760, s: 1.35, f: Math.sin(ph * TAU) > 0 ? 1 : -1, turn: .3,
    shR: 2.2 + Math.sin(t * 8) * .3, elR: .6, shL: 1.4, elL: .8, handR: 'hold', handL: 'open', air: ho * 70, sq: 1 - ho * .1,
    expr: { mouth: 'grin', open: .4 + ho * .4, eye: 1, brow: 1 + ho, lookX: .3 }, hold: { R: (cc, J) => { const h = J.handNear; pole(cc, h[0] - Math.sin(spinA) * 450, h[1] + Math.cos(spinA) * 450, h[0] + Math.sin(spinA) * 450, h[1] - Math.cos(spinA) * 450); } } });
  drawChar(c, CAST.knocker, pose, t);
  motes(c, t, 6, 30, '#ffe0b0', .5, 40);
  subtitle(c, t, 'He was literally a\n*human alarm clock.*', 14.4, 17.4);
});
const WORKERS = Array.from({ length: 8 }, (_, i) => townsfolk(700 + i));
shot(17.6, 19.2, 'K9 workers march to the mill', 'cut', (c, t) => {
  c.drawImage(SETS.factory.bg, 0, 0);
  smokePlume(c, 820, 200, t, '#5a4a5a', 3, 1.4);
  const lt = t - 17.6;
  WORKERS.forEach((ch, i) => {
    const row = i % 2, x = 1200 - ((lt * 220 + i * 160) % 1500), y = 1640 + row * 120, s = .9 + row * .12;
    drawChar(c, ch, merge({ x, y, s, f: -1, turn: .35 }, walkPose(t + i * .05, { amp: 1, strut: .3 }), { expr: { mouth: i % 3 ? 'flat' : 'o', open: .3, eye: .8 * blink(t, i), lookX: .2 } }), t);
  });
  drawChar(c, CAST.knocker, { x: 900, y: 1900, s: 1.3, f: -1, turn: .2, shR: 2.6 + Math.sin(t * 12) * .3, elR: .3, shL: -.2, expr: { mouth: 'grin', open: .4, eye: 1 }, hold: holdPole(-.2, 700, 300), handR: 'open' }, t);
  fogBand(c, 1500, 150, t, '#f0d0b0', .18, 30, 3);
});
shot(19.2, 20.8, 'K10 stop-time + pole at camera', 'cut', (c, t) => {
  townScene(c, t, 900, { cat: false });
  const fr1 = t >= 19.2 && t < 19.5, fr2 = t >= 19.5;
  const knocks = [20.0, 20.2, 20.4];
  const kk = hit(t, knocks, .1);
  const swing = clamp((t - 20.45) / .35);
  const pose = fr1 ? { shR: 3.0, elR: 0, shL: -.8, elL: .4, hipR: .5, kneeR: .2, hipL: -.4, kneeL: .3, lean: -.15, expr: { mouth: 'shout', open: 1, brow: 1.6 } }
    : { shR: 2.0 - swing * .6, elR: .2, shL: 1.2, elL: .6, lean: .1 + swing * .2, expr: { mouth: t > 20.38 && t < 20.6 ? 'o' : 'grin', open: .7, brow: 1.2, eye: 1.1, lookX: .1, lookY: -.1 } };
  const z = 1.1 + kk * .04 + swing * .3;
  c.save(); cam(c, 540, 1100, z);
  drawChar(c, CAST.knocker, merge({ x: 540, y: 1780, s: 1.45, f: 1, turn: .1, handR: 'hold' }, pose, { hold: holdPole(fr1 ? .1 : (.9 - kk * .15 + swing * .4), 820, 160) }), t);
  c.restore();
  flash(c, t, [19.2, 19.5], '#fff6e0', .08, .5);
  // the pole taps the "screen glass": cracks + KNOCK
  knocks.forEach((kt, i) => { if (t > kt) { c.save(); c.globalAlpha = .8; const cx = 640 + i * 40, cy = 640 - i * 30; for (let j = 0; j < 7; j++) { const a = j * .9 + i; line(c, [[cx, cy], [cx + Math.cos(a) * 70, cy + Math.sin(a) * 70], [cx + Math.cos(a + .3) * 130, cy + Math.sin(a + .3) * 130]], 3, '#eef4ff'); } c.restore(); } });
  if (kk > .2) { c.save(); c.translate(560, 400); c.rotate(-.12); c.font = '110px Luckiest'; c.textAlign = 'center'; c.lineWidth = 18; c.strokeStyle = '#1a0c08'; c.strokeText('KNOCK!', 0, 0); c.fillStyle = '#ffd34d'; c.fillText('KNOCK!', 0, 0); c.restore(); }
  if (swing > 0) { c.save(); c.globalAlpha = swing; pole(c, 1400, 2200, 540 - swing * 100, 900 - swing * 300); c.restore(); speedLines(c, 540, 900, swing * .8, 33); }
});
