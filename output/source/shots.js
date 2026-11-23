// Shot list: each shot draws itself for local time u in [0,d).
const L = require('./lib');
const C = require('./chars');
const E = require('./env');
const { W, H, S, shape, line, ellipse, mix, shade, alpha, clamp, lerp, inv, ss, sss, eo, ei, eob, hash, noise1, rng, glow, vgrad, text, vignette, measure } = L;
const { drawMember: M, guitar, keyboard, micStand, handMic } = C;
const { cam, pulse, blink, walk, BEATS } = E;

// beat times relative to the chorus beat (index c)
const C0 = BEATS.reduce((bi, b, i) => Math.abs(b - 34.8) < Math.abs(BEATS[bi] - 34.8) ? i : bi, 0);
const B = r => BEATS[C0 + r];
const CHORUS = B(0);

// ---------- reusable posed members ----------
const idle = (T, seed) => ({ bob: Math.sin(T * 2.2 + seed) * 4 });
function headP(T, seed, extra = {}) { return { blink: blink(T, seed), ...extra }; }
function keysPose(T, beatK = 1) { const p = pulse(T, .12) * beatK; return { hl: [-70, -360 + p * 14], hr: [70, -362 + (1 - p) * 10] }; }
function strum(T) { const p = pulse(T, .1); return { hr: [10 + p * 26, -330 - p * 40], hl: [-150, -470] }; }
const guitarProp = col => (g) => guitar(g, -6, -360, -0.95, .95, col);
function labelName(g, str, x, y, col, a) {
  if (a <= 0) return; const sz = 96; const w = measure(g, str, sz, 'Bebas', 6);
  g.save(); g.globalAlpha = a; g.translate(0, (1 - eo(a)) * 30);
  g.fillStyle = col; g.fillRect(x - w / 2 - 8, y + 12, (w + 16) * eo(a), 12);
  text(g, str, x, y, sz, { font: 'Bebas', track: 6, shadowBlur: 18 });
  g.restore();
}
function kick(T, amt = .02, k = .09) { return 1 + pulse(T, k) * amt; }

// ---------- TEXT identities ----------
function hookText(g, T, part) {
  // bold white condensed w/ black stroke; "300" in signal red
  const a1 = eob(inv(.25, .55, T));
  g.save(); g.translate(W / 2, part >= 2 ? 420 : 330); g.scale(lerp(1.25, 1, a1), lerp(1.25, 1, a1)); g.globalAlpha = clamp(a1 * 1.5);
  text(g, 'THEIR FIRST RELEASE', 0, 0, 92, { stroke: 14, strokeColor: '#0a0a0a', shadowBlur: 30 });
  g.restore();
  if (part >= 2) {
    const u = T - B(-92); const a2 = eob(inv(0, .2, u)), a3 = eob(inv(.3, .55, u));
    g.save(); g.translate(W / 2, 560); g.globalAlpha = clamp(a2 * 1.5); g.scale(lerp(1.4, 1, a2), lerp(1.4, 1, a2));
    text(g, 'SOLD ONLY', 0, 0, 120, { stroke: 16, strokeColor: '#0a0a0a' }); g.restore();
    g.save(); g.translate(W / 2, 790); g.globalAlpha = clamp(a3 * 1.5); const k = lerp(1.6, 1, a3) * (1 + pulse(T, .1) * .03); g.scale(k, k); g.rotate(-.03);
    const w300 = measure(g, '300 ', 230), wC = measure(g, 'COPIES.', 150);
    const x0 = -(w300 + wC) / 2;
    text(g, '300', x0 + w300 / 2 - 20, 0, 230, { stroke: 18, strokeColor: '#0a0a0a', color: '#ff3b30' });
    text(g, 'COPIES.', x0 + w300 + wC / 2, 0, 150, { stroke: 16, strokeColor: '#0a0a0a' });
    g.restore();
  }
}

// =============== SHOTS ===============
const shots = [];
function shot(a, b, name, fn) { shots.push({ a, b, name, fn }); }

// S1 cold open – arena roar
shot(0, B(-92), 'arena', (g, u, d, T) => {
  g.save(); cam(g, { z: lerp(1.0, 1.12, ss(u / d)) * kick(T, .025), y: H / 2 + 40 });
  vgrad(g, -200, -200, W + 400, H + 400, [[0, '#14061f'], [.45, '#2a0b3a'], [1, '#07040c']]);
  // video wall
  shape(g, g => { g.rect(140, 500, 800, 330); }, '#111018', { lw: 6 });
  g.save(); g.globalCompositeOperation = 'lighter'; glow(g, 540, 665, 600, '#ff2f8a', .35 + .25 * pulse(T)); g.restore();
  text(g, 'a-ha', 540, 750, 230, { font: 'InterXB', color: '#ffe9f3', shadowBlur: 40, track: -6 });
  // stage
  shape(g, g => { g.rect(40, 960, 1000, 70); }, '#1b1426', { lw: 5 });
  const ps = .25;
  M(g, 'magne', { x: 330, y: 962, s: ps, ...keysPose(T), head: headP(T, 1, { mouth: 'smile' }), front: g => keyboard(g, 0, -330, 320, [], 1) });
  M(g, 'morten', { x: 540, y: 966, s: ps * 1.05, hr: [30, -700], br: 1, hl: [-200, -760], head: headP(T, 2, { mouth: 'sing', open: .9, tilt: -.15 }) });
  M(g, 'pal', { x: 750, y: 962, s: ps, ...strum(T), prop: guitarProp('#d23b2b') });
  E.beams(g, T, [
    { x: 160, y: 330, a: .25, col: '#ff2f8a', sp: 2.1, sw: .3, w: .08 }, { x: 920, y: 330, a: -.25, col: '#36d7ff', sp: 1.7, sw: .3, w: .08, ph: 1 },
    { x: 540, y: 300, a: 0, col: '#ffd36e', sp: 2.6, sw: .45, w: .06, ph: 2, i: .35 }, { x: 360, y: 320, a: .1, col: '#a05cff', sp: 1.4, sw: .35, w: .07, ph: 3, i: .4 },
  ]);
  E.crowdSea(g, T, 1040, 1500, '#ff4fa0', 5, 1.2);
  E.crowd(g, T, { y: 1500, rows: 3, scale: 1.3, col: '#06030a', rim: '#ff4fa0', arms: .7, jump: 1, wave: 9, seed: 3 });
  // strobe on beats
  g.restore();
  g.fillStyle = `rgba(255,240,255,${pulse(T, .06) * .22})`; g.fillRect(0, 0, W, H);
  vignette(g, .6);
  hookText(g, T, 1);
});

// S2 smash cut – lonely 1984 single in a record shop
shot(B(-92), B(-84), 'shop', (g, u, d, T) => {
  g.save(); cam(g, { z: lerp(1.04, 1.12, ss(u / d)), y: H / 2 + 80, r: -.01 });
  vgrad(g, 0, 0, W, H, [[0, '#2a3336'], [1, '#121718']]);
  // back wall shelves with mostly empty slots
  for (let r = 0; r < 2; r++) {
    const y = 1000 + r * 330;
    shape(g, g => { g.rect(-40, y, W + 80, 26); }, '#5a4636', { lw: 5 });
    if (r !== 1) for (let i = 0; i < 9; i++) { if (hash(r * 20 + i) < .55) continue; const x = 30 + i * 118; shape(g, g => { g.rect(x, y - 150 - hash(i) * 20, 22, 150 + hash(i) * 20); }, mix('#3e4a4e', '#6a5a4a', hash(i + r)), { lw: 4 }); }
  }
  // the lonely single
  L.S.lwMul = 1;
  E.sleeve(g, 540, 1166, 1.1, -.04, { year: '1984', bg: '#e2ddcd', accent: '#a8323a' });
  // price tag
  shape(g, g => { g.rect(650, 1262, 120, 60); }, '#f6e36b', { lw: 4 });
  text(g, '£0.99', 710, 1306, 36, { font: 'InterXB', color: '#222', shadow: false });
  // bin foreground
  shape(g, g => { g.moveTo(-40, 1700); g.lineTo(W + 40, 1700); g.lineTo(W + 40, H + 40); g.lineTo(-40, H + 40); g.closePath(); }, '#3a2c22', { shadeFn: g2 => { vgrad(g2, 0, 1700, W, 420, [[0, 'rgba(255,255,255,.06)'], [1, 'rgba(0,0,0,.4)']]); } });
  for (let i = 0; i < 7; i++) shape(g, g => { g.rect(40 + i * 150, 1620 + (i % 2) * 14, 130, 120); }, mix('#59605a', '#7a6650', hash(i * 3)), { lw: 4 });
  // fluorescent flicker light from top
  const fl = hash(Math.floor(T * 15)) > .2 ? 1 : .55;
  g.save(); g.globalCompositeOperation = 'lighter';
  const gr = g.createLinearGradient(540, 180, 540, 1400); gr.addColorStop(0, `rgba(190,255,240,${.25 * fl})`); gr.addColorStop(1, 'rgba(190,255,240,0)');
  g.fillStyle = gr; g.beginPath(); g.moveTo(380, 180); g.lineTo(700, 180); g.lineTo(980, 1400); g.lineTo(100, 1400); g.closePath(); g.fill();
  g.restore();
  // dust in the beam
  const r = rng(9); g.fillStyle = 'rgba(230,255,245,.5)'; for (let i = 0; i < 40; i++) { const x = 250 + r() * 580, y = (r() * 1100 + 250 + u * 30 * (r() - .3)); g.beginPath(); ellipse(g, x + Math.sin(u + i) * 10, y, 2.2, 2.2); g.fill(); }
  g.restore();
  // cold desaturate overlay
  g.fillStyle = 'rgba(30,60,70,.18)'; g.fillRect(0, 0, W, H);
  vignette(g, .75);
  hookText(g, T, 2);
  if (u < 2 / 30) { g.fillStyle = 'rgba(255,255,255,.85)'; g.fillRect(0, 0, W, H); }
});

// S3 Norway exterior
shot(B(-84), B(-76), 'norway', (g, u, d, T) => {
  const p = sss(u / d);
  g.save(); cam(g, { z: lerp(1.0, 1.3, p), y: lerp(900, 1180, p), x: lerp(540, 560, p) });
  vgrad(g, -300, -300, W + 600, H + 600, [[0, '#06102a'], [.35, '#12305a'], [.6, '#3f6f99'], [.75, '#a9c3d6']]);
  const r = rng(5); g.fillStyle = '#fff'; for (let i = 0; i < 90; i++) { g.globalAlpha = .4 + .6 * Math.abs(Math.sin(T * 2 + i)); g.fillRect(r() * W, r() * 900, 3, 3); } g.globalAlpha = 1;
  E.aurora(g, T, 280, 1);
  E.mountains(g, 1150, 420, '#5d7da3', 3, true);
  E.mountains(g, 1250, 260, '#3c5a80', 8, true);
  // fjord water
  shape(g, g => { g.rect(-300, 1250, W + 600, 160); }, '#1e3c5e', { lw: 4, shadeFn: g2 => { g2.strokeStyle = 'rgba(180,220,255,.35)'; g2.lineWidth = 3; for (let i = 0; i < 12; i++) { const y = 1265 + i * 12; g2.beginPath(); g2.moveTo(100 + Math.sin(T + i) * 40, y); g2.lineTo(300 + Math.sin(T + i) * 40, y); g2.moveTo(600 + Math.cos(T * .8 + i) * 50, y + 5); g2.lineTo(760 + Math.cos(T * .8 + i) * 50, y + 5); g2.stroke(); } } });
  // snow ground
  shape(g, g => { g.moveTo(-300, 1400); g.quadraticCurveTo(540, 1340, W + 300, 1420); g.lineTo(W + 300, H + 300); g.lineTo(-300, H + 300); g.closePath(); }, '#dfe8f4', { lw: 5, shadeFn: g2 => { vgrad(g2, 0, 1380, W, 600, [[0, 'rgba(120,150,200,0)'], [1, 'rgba(90,110,170,.35)']]); } });
  E.pine(g, 180, 1450, 330); E.pine(g, 300, 1430, 240); E.pine(g, 900, 1470, 360); E.pine(g, 1010, 1440, 250);
  E.woodHouse(g, 580, 1460, 300, 210, '#9a2f2a', 1, T);
  // window light spill on snow
  g.save(); g.globalCompositeOperation = 'lighter'; glow(g, 580, 1520, 260, '#ffb347', .18); g.restore();
  g.restore();
  E.snow(g, T, 140, 2, 40);
  vignette(g, .55, '5,10,30');
  const a = inv(.4, .9, u) * (1 - inv(d - .3, d, u));
  text(g, 'NORWAY', W / 2, 400, 120, { font: 'Bebas', track: 30, alpha: a, shadowBlur: 30 });
});

// S4 warm interior – Magne's melody, Pål's songwriting
function homeRoom(g, T) {
  vgrad(g, -200, -200, W + 400, H + 400, [[0, '#3b2418'], [.5, '#6a4128'], [1, '#2a1a12']]);
  g.save(); g.globalAlpha = .25; g.strokeStyle = '#2a170e'; g.lineWidth = 4; for (let x = -200; x < W + 200; x += 46) { g.beginPath(); g.moveTo(x, -200); g.lineTo(x, H * .74); g.stroke(); } g.restore();
  // window w/ snow night
  shape(g, g => { g.rect(380, 360, 330, 400); }, '#1d3557', { lw: 9, shadeFn: g2 => { vgrad(g2, 380, 360, 330, 400, [[0, '#14254a'], [1, '#4f79a8']]); E.snow(g2, T, 30, 7, 20, .8); } });
  line(g, g => { g.moveTo(545, 360); g.lineTo(545, 760); g.moveTo(380, 560); g.lineTo(710, 560); }, 9, '#3a2416');
  shape(g, g => { g.rect(-200, H * .74, W + 400, 800); }, '#4a2c1c', { shadeFn: g2 => { vgrad(g2, 0, H * .74, W, 600, [[0, 'rgba(255,200,120,.12)'], [1, 'rgba(0,0,0,.35)']]); } });
  // lamp
  line(g, g => { g.moveTo(140, 1420); g.lineTo(140, 900); }, 8, '#2a1a10');
  shape(g, g => { g.moveTo(70, 900); g.lineTo(210, 900); g.lineTo(180, 800); g.lineTo(100, 800); g.closePath(); }, '#f2d39a', { lw: 5 });
  g.save(); g.globalCompositeOperation = 'lighter'; glow(g, 140, 880, 700, '#ffb35c', .32); g.restore();
}
shot(B(-76), B(-70), 'home', (g, u, d, T) => {
  const p = sss(u / d);
  g.save(); cam(g, { z: 1.32, x: lerp(380, 700, p), y: 1020 });
  homeRoom(g, T);
  // Magne at keys
  const kb = pulse(T, .12); const bi = E.beatIdx(T);
  M(g, 'magne', { x: 330, y: 1560, s: .95, ...keysPose(T), head: headP(T, 4, { look: [.25, .5], mouth: 'smile', tilt: Math.sin(T * 3) * .05 }), front: g => keyboard(g, 0, -340, 400, [(bi * 3) % 16, (bi * 5 + 4) % 16], 1) });
  // melody ribbon rising from keys
  g.save(); g.globalCompositeOperation = 'lighter'; g.strokeStyle = 'rgba(255,215,120,.75)'; g.lineWidth = 7; g.lineCap = 'round'; g.beginPath();
  for (let i = 0; i <= 40; i++) { const k = i / 40; const x = 330 + k * 300 + Math.sin(k * 9 - T * 6) * 30; const y = 1200 - k * 520 - (1 - k) * 0; if (k > clamp(u / d * 2)) break; i ? g.lineTo(x, y) : g.moveTo(x, y); }
  g.stroke(); g.restore();
  // Pål with notebook & guitar
  M(g, 'pal', { x: 830, y: 1570, s: .95, hl: [-110, -440], hr: [20, -460], br: -1, head: headP(T, 7, { look: [-.3, .8], mouth: 'closed', brows: 'focus', tilt: .08 }), prop: guitarProp('#c0392b'),
    front: g => { // notebook + pencil
      shape(g, g => { g.save(); g.translate(-60, -470); g.rotate(-.15); g.rect(-70, -50, 150, 100); g.restore(); }, '#efe6cf', { lw: 5, shadeFn: g2 => { g2.save(); g2.translate(-60, -470); g2.rotate(-.15); g2.strokeStyle = '#7a8bb0'; g2.lineWidth = 2; for (let y = -30; y < 40; y += 14) { g2.beginPath(); g2.moveTo(-60, y); g2.lineTo(70, y); g2.stroke(); } g2.strokeStyle = '#333'; g2.lineWidth = 3; g2.beginPath(); for (let x = -55; x < -55 + clamp(u / d) * 120; x += 6) g2.lineTo(x, -24 + Math.sin(x * .4) * 4); g2.stroke(); g2.restore(); } });
      E.pencil(g, 20 + Math.sin(T * 18) * 4, -460, -1.9, .35);
    } });
  g.restore();
  vignette(g, .5, '20,8,0');
  labelName(g, 'MAGNE', 300, 560, '#5d94c9', inv(.15, .5, u) * (1 - inv(d * .55, d * .7, u)));
  labelName(g, 'PÅL', 780, 560, '#b94a58', inv(d * .5, d * .7, u));
});

// S5 Morten's voice
shot(B(-70), B(-64), 'morten', (g, u, d, T) => {
  const p = ss(u / d);
  g.save(); cam(g, { z: lerp(1, 1.08, p), y: H / 2 });
  homeRoom(g, T);
  // background listeners, soft
  { const q = .2; const oc = L.createCanvas(W * q | 0, H * q | 0); const og = oc.getContext('2d'); og.scale(q, q);
  M(og, 'magne', { x: 170, y: 1500, s: .75, ...keysPose(T, .3), head: headP(T, 4, { look: [.6, -.2], mouth: 'o', open: .3, brows: 'up' }), front: g => keyboard(g, 0, -340, 380, [], 1) });
  M(og, 'pal', { x: 930, y: 1500, s: .75, hl: [-120, -430], hr: [30, -330], head: headP(T, 7, { look: [-.6, -.2], mouth: 'smile', brows: 'up' }), prop: guitarProp('#c0392b') });
  g.save(); g.imageSmoothingQuality = 'high'; g.drawImage(oc, 0, 0, W, H); g.restore(); }
  g.fillStyle = 'rgba(30,15,5,.25)'; g.fillRect(0, 0, W, H);
  // Morten big
  const sing = .5 + .5 * Math.abs(Math.sin(T * 4.4));
  const eyes = u < d * .55;
  M(g, 'morten', { x: 540, y: 2350, s: 2.05, bob: Math.sin(T * 2) * 4, hl: [-170 - Math.sin(T * 2.2) * 20, -620 - Math.sin(T * 2.2) * 30], bl: -1, hr: [110, -380], head: { tilt: lerp(-.1, .08, p), eyesClosed: eyes, mouth: 'sing', open: .5 + sing * .6, brows: eyes ? 'up' : 'focus', look: [0, -.2], blink: eyes ? 0 : blink(T, 3) } });
  // voice rings
  g.save(); g.globalCompositeOperation = 'lighter';
  for (let k = 0; k < 3; k++) { const ph = ((T * 1.2 + k / 3) % 1); g.strokeStyle = `rgba(255,220,160,${(1 - ph) * .45})`; g.lineWidth = 6; g.beginPath(); g.arc(540, 1240, 80 + ph * 420, Math.PI * .15, Math.PI * .85); g.stroke(); }
  g.restore();
  g.restore();
  vignette(g, .55, '20,8,0');
  labelName(g, 'MORTEN', 540, 420, '#9aa0b5', inv(.2, .55, u));
});

// S6 leaving Norway – backs to us, heading for the ship
shot(B(-64), B(-56), 'leave', (g, u, d, T) => {
  const p = ss(u / d);
  g.save(); cam(g, { z: lerp(1.0, 1.12, p), y: lerp(980, 1020, p) });
  vgrad(g, -200, -200, W + 400, H + 400, [[0, '#2b3d6b'], [.38, '#c98a9c'], [.52, '#f2c6a0'], [.6, '#d9e2ee']]);
  glow(g, 700, 900, 400, '#ffd9a0', .5);
  E.mountains(g, 1000, 300, '#6c7fa6', 12, true, .9);
  shape(g, g => { g.rect(-300, 990, W + 600, 140); }, '#4d6688', { lw: 4, shadeFn: g2 => { g2.strokeStyle = 'rgba(255,220,200,.4)'; g2.lineWidth = 3; for (let i = 0; i < 8; i++) { g2.beginPath(); g2.moveTo(500 + Math.sin(T + i) * 30, 1000 + i * 15); g2.lineTo(760 + Math.sin(T + i) * 30, 1000 + i * 15); g2.stroke(); } } });
  // ship
  const sx = 760 + u * 10;
  shape(g, g => { g.moveTo(sx - 220, 1010); g.lineTo(sx + 220, 1010); g.lineTo(sx + 180, 1070); g.lineTo(sx - 190, 1070); g.closePath(); }, '#2a2f45', { lw: 5 });
  shape(g, g => { g.rect(sx - 120, 940, 220, 70); }, '#e9e4dc', { lw: 5, shadeFn: g2 => { for (let i = 0; i < 6; i++) { g2.fillStyle = '#ffcf7a'; g2.fillRect(sx - 105 + i * 34, 960, 18, 18); } } });
  shape(g, g => { g.rect(sx - 10, 880, 46, 62); }, '#b2323a', { lw: 5 });
  g.save(); g.globalAlpha = .5; for (let i = 0; i < 5; i++) { const t = (T * .4 + i * .2) % 1; g.fillStyle = 'rgba(230,230,240,.6)'; g.beginPath(); ellipse(g, sx + 14 - t * 120, 860 - t * 160, 22 + t * 40, 18 + t * 30); g.fill(); } g.restore();
  // pier / snowy road
  shape(g, g => { g.moveTo(-300, 1130); g.lineTo(W + 300, 1130); g.lineTo(W + 300, H + 300); g.lineTo(-300, H + 300); g.closePath(); }, '#e3e9f2', { lw: 5 });
  shape(g, g => { g.moveTo(450, 1130); g.lineTo(630, 1130); g.lineTo(1000, H + 300); g.lineTo(80, H + 300); g.closePath(); }, '#7d6a5c', { lw: 5, shadeFn: g2 => { g2.strokeStyle = 'rgba(0,0,0,.25)'; g2.lineWidth = 3; for (let i = 0; i < 14; i++) { const y = 1140 + Math.pow(i / 14, 2) * 900; g2.beginPath(); g2.moveTo(0, y); g2.lineTo(W, y); g2.stroke(); } } });
  // three walking away (back view), carrying cases
  const walkers = [['magne', 380, .1], ['morten', 545, 0], ['pal', 720, .25]];
  const dep = lerp(0, 1, p);
  walkers.forEach(([who, x0, ph], i) => {
    const s = lerp(.62, .42, dep) * (who === 'morten' ? 1.03 : 1);
    const y = lerp(1720, 1420, dep) + (i === 1 ? 10 : 0);
    const x = lerp(x0, 540 + (x0 - 540) * .55, dep);
    const w = walk(T + ph, 1.5, .8);
    let front = null, hl = w.hl, hr = w.hr;
    if (who === 'magne') { hr = [96, -360]; front = g => { shape(g, g => { g.roundRect(60, -440, 70, 260, 14); }, '#2b2b33', { lw: 6 }); }; }
    if (who === 'pal') { hl = [-90, -300]; front = g => { shape(g, g => { g.save(); g.translate(-96, -290); g.rotate(.12); g.moveTo(-26, -20); g.bezierCurveTo(-40, 100, -50, 200, -30, 280); g.lineTo(30, 280); g.bezierCurveTo(50, 200, 40, 100, 26, -20); g.closePath(); g.restore(); }, '#3a2a20', { lw: 6 }); }; }
    if (who === 'morten') { hr = [96, -300]; front = g => { shape(g, g => { g.roundRect(60, -300, 150, 120, 12); }, '#7a4a2a', { lw: 6, shadeFn: g2 => { g2.fillStyle = 'rgba(0,0,0,.25)'; g2.fillRect(60, -250, 150, 14); } }); }; }
    M(g, who, { x, y, s, back: true, ...w, hl, hr, front });
  });
  g.restore();
  E.snow(g, T, 90, 3, 60, .9);
  vignette(g, .45, '20,20,50');
});

// S7 London night
shot(B(-56), B(-48), 'london', (g, u, d, T) => {
  const p = sss(u / d);
  g.save(); cam(g, { z: lerp(1.0, 1.5, p), x: lerp(540, 690, p), y: lerp(1050, 760, p) });
  vgrad(g, -400, -400, W + 800, H + 800, [[0, '#0b0f24'], [.5, '#1d2346'], [1, '#2a2438']]);
  glow(g, 540, 300, 600, '#4a3f7a', .35);
  // far rooftops
  g.fillStyle = '#141833'; g.beginPath(); g.moveTo(-400, 700); for (let x = -400; x < W + 400; x += 90) { g.lineTo(x, 640 - hash(x) * 120); g.lineTo(x + 60, 640 - hash(x) * 120); } g.lineTo(W + 400, 900); g.lineTo(-400, 900); g.fill();
  E.terrace(g, -220, 1380, 6, T, { lit: (i, fl, c) => (i === 3 && fl === 0 && c === 0) || (i === 1 && fl === 1 && c === 1 && hash(Math.floor(T * 2)) > .1) });
  // street
  shape(g, g => { g.rect(-400, 1380, W + 800, 900); }, '#1b1d2a', { lw: 5, shadeFn: g2 => { g2.save(); g2.globalCompositeOperation = 'lighter'; for (const [x, c] of [[700, '#ffb347'], [330, '#ffcf80'], [880, '#ffb347']]) { const gr = g2.createLinearGradient(0, 1380, 0, 1900); gr.addColorStop(0, alpha(c, .35)); gr.addColorStop(1, alpha(c, 0)); g2.fillStyle = gr; g2.fillRect(x - 30 + Math.sin(T * 3) * 4, 1390, 60, 500); } g2.restore(); } });
  shape(g, g => { g.rect(-400, 1380, W + 800, 40); }, '#6a6670', { lw: 4 });
  E.lamp(g, 90, 1390, 560, T);
  // passing bus
  const bx = lerp(-700, 1800, inv(.2, d - .2, u));
  E.bus(g, bx, 1760, 1.0);
  g.restore();
  E.rain(g, T, 260, 4);
  vignette(g, .6, '5,5,20');
  text(g, 'LONDON', W / 2, 400, 120, { font: 'Bebas', track: 30, alpha: inv(.3, .8, u) * (1 - inv(d - .3, d, u)), shadowBlur: 30 });
});

// S8 cramped flat – again and again (time-lapse jumps on beats)
shot(B(-48), B(-42), 'flat', (g, u, d, T) => {
  const st = Math.min(2, Math.floor(u / (d / 3)));
  g.save(); cam(g, { z: 1.08 + st * .04, x: 540 + (st - 1) * 30, y: 1000 });
  E.flatRoom(g, T, 0);
  E.windowRain(g, 640, 420, 300, 380, T, 1);
  E.clock(g, 300, 470, 70, 1 + (u / d) * 5.5);
  E.mattress(g, 760, 1640, 460);
  for (let i = 0; i < 2 + st * 3; i++) E.mug(g, 120 + i * 50 + (i % 2) * 10, 1720 - (i % 3) * 8, ['#e8e2d6', '#b3d1e0', '#e6b9a6'][i % 3]);
  // crate + keyboard
  shape(g, g => { g.rect(140, 1440, 240, 200); }, '#8a6a43', { shadeFn: g2 => { g2.strokeStyle = 'rgba(0,0,0,.3)'; g2.lineWidth = 4; for (let y = 1480; y < 1640; y += 40) { g2.beginPath(); g2.moveTo(140, y); g2.lineTo(380, y); g2.stroke(); } } });
  const poses = [
    { mag: [260, 1720, { mouth: 'closed', brows: 'focus', look: [0, .8] }], pal: [720, 1700, { mouth: 'closed', brows: 'focus', look: [-.3, .6] }], mor: [520, 1660, { mouth: 'sing', open: .6, look: [.3, 0] }] },
    { mag: [260, 1720, { mouth: 'o', open: .3, brows: 'up', look: [.6, 0] }], pal: [760, 1700, { mouth: 'closed', brows: 'sad', look: [-.6, 0] }], mor: [480, 1680, { mouth: 'closed', brows: 'focus', look: [-.4, .4] }] },
    { mag: [260, 1720, { mouth: 'closed', brows: 'focus', look: [0, .8] }], pal: [740, 1700, { mouth: 'smile', brows: 'up', look: [-.6, 0] }], mor: [540, 1660, { mouth: 'sing', open: 1, look: [0, -.4], tilt: -.1 }] },
  ][st];
  M(g, 'morten', { x: poses.mor[0], y: poses.mor[1], s: .82, hl: [-90, -330], hr: st === 2 ? [90, -660] : [96, -330], br: st === 2 ? 1 : -1, head: headP(T, 2, poses.mor[2]) });
  M(g, 'magne', { x: poses.mag[0], y: poses.mag[1], s: .82, ...keysPose(T), head: headP(T, 4, poses.mag[2]), front: g => keyboard(g, 0, -330, 360, [E.beatIdx(T) % 15], 1) });
  M(g, 'pal', { x: poses.pal[0], y: poses.pal[1], s: .82, ...strum(T), head: headP(T, 7, poses.pal[2]), prop: guitarProp('#c0392b') });
  g.restore();
  g.save(); g.globalCompositeOperation = 'lighter'; glow(g, 300, 300, 700, '#ffae5a', .2); g.restore();
  vignette(g, .6, '15,5,5');
  // time-lapse flash on jumps
  const j = (u % (d / 3)); if (st > 0 && j < .06) { g.fillStyle = 'rgba(255,240,220,.35)'; g.fillRect(0, 0, W, H); }
});

// S9 studio session
function studioLive(g, T, u, energy = 0) {
  // live room seen through glass
  vgrad(g, 0, 0, W, H, [[0, '#2b2230'], [1, '#191520']]);
  g.save(); g.globalAlpha = .3; for (let x = 0; x < W; x += 80) { g.fillStyle = x % 160 ? '#3a2c3c' : '#30253a'; g.fillRect(x, 0, 80, H); } g.restore();
  g.save(); g.globalCompositeOperation = 'lighter'; glow(g, 540, 700, 800, energy > .5 ? '#ff9e4a' : '#ffcf8a', .25 + energy * .25 + pulse(T) * energy * .15); g.restore();
}
shot(B(-42), B(-36), 'studio', (g, u, d, T) => {
  const p = ss(u / d);
  g.save(); cam(g, { z: lerp(1.0, 1.1, p), y: H / 2 + lerp(0, -60, p) });
  studioLive(g, T, u, 0);
  // Morten at mic with headphones, behind glass
  M(g, 'morten', { x: 540, y: 1450, s: .95, hl: [-100, -690], bl: -1, hr: [100, -690], br: 1, head: headP(T, 2, { mouth: 'sing', open: .4 + .5 * Math.abs(Math.sin(T * 4.4)), eyesClosed: true, brows: 'up' }), front: g => {
    line(g, g => { g.arc(0, -680, 96, Math.PI * 1.05, Math.PI * 1.95); }, 14, '#222');
    shape(g, g => { g.roundRect(-104, -700, 34, 70, 10); }, '#2b2b2b', { lw: 4 }); shape(g, g => { g.roundRect(70, -700, 34, 70, 10); }, '#2b2b2b', { lw: 4 });
  } });
  micStand(g, 540, 1460, 560, .95);
  // glass frame + reflection
  g.save(); g.globalAlpha = .12; g.fillStyle = '#bcd6ff'; g.beginPath(); g.moveTo(100, 300); g.lineTo(300, 300); g.lineTo(80, 1250); g.lineTo(-120, 1250); g.fill(); g.restore();
  shape(g, g => { g.rect(-100, 1150, W + 200, 1000); g.rect(-100, -100, W + 200, 300); }, '#2e2a33', { lw: 6 });
  line(g, g => { g.rect(60, 200, W - 120, 950); }, 12, '#111');
  // desk + meters
  E.mixDesk(g, 540, 1260, 980, T, .1 + pulse(T) * .2);
  E.vu(g, 300, 1210, 160, .35 + .5 * Math.abs(Math.sin(T * 4.4)) + pulse(T) * .2);
  E.vu(g, 780, 1210, 160, .3 + .5 * Math.abs(Math.sin(T * 4.4 + .5)) + pulse(T) * .2);
  // Pål & Magne foreground backs
  M(g, 'pal', { x: 220, y: 2280, s: 1.05, back: true, hl: [-90, -560], hr: [90, -520] });
  M(g, 'magne', { x: 880, y: 2300, s: 1.05, back: true, hl: [-90, -520], hr: [90, -560] });
  g.restore();
  vignette(g, .55);
});

// S10 FAILURE – cold, monochrome stockroom, counter stops at 300, stamp
shot(B(-36), B(-28), 'flop', (g, u, d, T) => {
  const stampT = B(-31) - B(-36);
  const p = ss(u / d);
  g.save(); cam(g, { z: lerp(1.02, 1.1, p) * (u > stampT ? 1 + Math.exp(-(u - stampT) / .08) * .03 : 1), y: H / 2 + 60 });
  vgrad(g, 0, 0, W, H, [[0, '#1d2226'], [1, '#0c0f11']]);
  // bulb
  line(g, g => { g.moveTo(540, -100); g.lineTo(540, 300); }, 4, '#555');
  shape(g, g => { ellipse(g, 540, 330, 34, 44); }, '#fff6d8', { lw: 4 });
  g.save(); g.globalCompositeOperation = 'lighter'; const sw = Math.sin(T * 1.7) * 30;
  const gr = g.createRadialGradient(540, 330, 10, 540 + sw, 1100, 900); gr.addColorStop(0, 'rgba(235,240,245,.35)'); gr.addColorStop(1, 'rgba(235,240,245,0)'); g.fillStyle = gr; g.fillRect(0, 0, W, H); g.restore();
  // shelves of unsold boxes
  for (let r = 0; r < 3; r++) for (let i = 0; i < 4; i++) {
    const x = 60 + i * 250 + (r % 2) * 40, y = 1820 - r * 230;
    shape(g, g => { g.rect(x, y - 210, 230, 210); }, mix('#7c7468', '#5d5a55', hash(r * 9 + i)), { lw: 5, shadeFn: g2 => { g2.fillStyle = 'rgba(0,0,0,.18)'; g2.fillRect(x, y - 140, 230, 10); } });
    text(g, 'RETURNS', x + 115, y - 80, 30, { font: 'InterXB', color: 'rgba(40,40,40,.6)', shadow: false });
  }
  // stack of sleeves on table
  shape(g, g => { g.rect(140, 1180, 800, 40); }, '#3c3934', { lw: 5 });
  for (let k = 0; k < 9; k++) E.sleeve(g, 540 + (hash(k) - .5) * 20, 1170 - k * 12 - 150 * .9, .9, (hash(k + 3) - .5) * .06, { bg: '#cfccc4', accent: '#6b6b6b' });
  // tally counter
  const cnt = Math.floor(300 * eo(inv(.25, stampT - .1, u)));
  shape(g, g => { g.roundRect(330, 560, 420, 200, 30); }, '#9aa0a8', { lw: 6 });
  shape(g, g => { g.roundRect(370, 600, 340, 120, 12); }, '#121417', { lw: 5 });
  text(g, String(cnt).padStart(4, '0'), 540, 702, 110, { font: 'InterXB', color: '#e8ecef', shadow: false, track: 14 });
  shape(g, g => { g.roundRect(500, 500 - (u < stampT ? pulse(T, .08) * 12 : 0), 80, 60, 10); }, '#6d737a', { lw: 5 });
  g.restore();
  // stamp
  if (u > stampT) {
    const k = eo(inv(stampT, stampT + .12, u));
    g.save(); g.translate(540, 1000); g.rotate(-.12); g.scale(lerp(2.2, 1, k), lerp(2.2, 1, k)); g.globalAlpha = k * .95;
    g.strokeStyle = '#d7261e'; g.lineWidth = 14; g.strokeRect(-380, -150, 760, 300);
    text(g, '300 COPIES', 0, 40, 150, { color: '#d7261e', shadow: false });
    text(g, 'FIRST RELEASE · 1984', 0, 118, 52, { font: 'InterXB', color: '#d7261e', shadow: false });
    g.restore();
  }
  g.fillStyle = 'rgba(40,60,70,.12)'; g.fillRect(0, 0, W, H);
  vignette(g, .75);
});

// S11 disappointment – behaviour, no words
function seated(who, x, floorY, s, extra) {
  const hipY = floorY - 170 * s; const py = hipY + 300 * s;
  return { x, y: py, s, fl: [-70, (floorY - py) / s + 0], fr: [70, (floorY - py) / s], ...extra, _who: who };
}
shot(B(-28), B(-24), 'down', (g, u, d, T) => {
  const p = ss(u / d);
  g.save(); cam(g, { z: lerp(1.05, 1.13, p), y: 1060 });
  E.flatRoom(g, T, 1);
  E.windowRain(g, 640, 420, 300, 380, T, .3);
  // rain shadows on wall
  g.save(); g.globalAlpha = .12; E.rain(g, T * .3, 60, 12, 'rgba(10,20,40,1)'); g.restore();
  E.mattress(g, 420, 1640, 520);
  M(g, 'morten', { x: 790, y: 1700, s: .86, back: true, hl: [-70, -560], hr: [80, -330] });
  const ms = seated('magne', 420, 1700, .82, {}); M(g, 'magne', { ...ms, hl: [-30, -330], hr: [30, -330], head: { tilt: .15, look: [0, 1], mouth: 'sad', brows: 'sad', blink: blink(T, 4) } });
  M(g, 'pal', { x: 160, y: 1720, s: .82, hl: [-40, -420], hr: [40, -420], head: { tilt: .1, look: [.1, 1], mouth: 'closed', brows: 'sad', blink: blink(T, 7) }, front: g => { shape(g, g => { g.rect(-70, -470, 140, 100); }, '#efe6cf', { lw: 5 }); } });
  g.restore();
  g.fillStyle = 'rgba(40,60,110,.22)'; g.fillRect(0, 0, W, H);
  vignette(g, .7, '5,10,25');
});

// S12 "They didn't." – warmth returns, they move
shot(B(-24), B(-18), 'again', (g, u, d, T) => {
  const tD = 26.75 - B(-24); // "They didn't."
  const warm = ss(inv(tD - .3, tD + .9, u));
  g.save(); cam(g, { z: lerp(1.1, 1.22, ss(u / d)) * (1 + Math.exp(-Math.max(0, u - tD) / .1) * (u > tD ? .03 : 0)), y: 1060, x: 520 });
  E.flatRoom(g, T, 1 - warm);
  E.windowRain(g, 640, 420, 300, 380, T, .3 + warm * .7);
  E.mattress(g, 420, 1640, 520);
  const up = warm;
  M(g, 'morten', { x: 790, y: 1700, s: .86, back: up < .5, hl: [-90, -330], hr: up > .5 ? [100, -600] : [80, -330], br: 1, head: { mouth: up > .5 ? 'sing' : 'closed', open: .5, brows: 'focus', look: [-.4, 0], blink: blink(T, 2) } });
  if (up < .4) { const ms = seated('magne', 420, 1700, .82, {}); M(g, 'magne', { ...ms, hl: [-30, -330], hr: [30, -330], head: { tilt: lerp(.15, 0, up * 2), look: [0, lerp(1, 0, up * 2.5)], mouth: 'closed', brows: 'sad' } }); }
  else M(g, 'magne', { x: 420, y: 1720, s: .82, ...keysPose(T), head: { look: [.3, .6], mouth: 'smile', brows: 'focus', blink: blink(T, 4) }, front: g => keyboard(g, 0, -330, 360, [E.beatIdx(T) % 15, (E.beatIdx(T) + 4) % 15], 1) });
  M(g, 'pal', { x: 160, y: 1720, s: .82, hl: [-60, -480 - up * 120], hr: [40, -420], head: { look: [.6, 0], mouth: up > .3 ? 'smile' : 'closed', brows: up > .3 ? 'focus' : 'sad', blink: blink(T, 7) }, front: g => { shape(g, g => { g.save(); g.translate(-30, -500 - up * 120); g.rotate(-.2 * up); g.rect(-75, -55, 150, 105); g.restore(); }, '#efe6cf', { lw: 5 }); } });
  g.restore();
  g.fillStyle = `rgba(40,60,110,${.22 * (1 - warm)})`; g.fillRect(0, 0, W, H);
  g.save(); g.globalCompositeOperation = 'lighter'; glow(g, 400, 900, 900, '#ffad55', .25 * warm); g.restore();
  vignette(g, .6, '10,8,15');
});

// S13 tape rewinds – the arrangement changes
shot(B(-18), B(-12), 'rewind', (g, u, d, T) => {
  const tRec = B(-15) - B(-18);
  const rew = u < tRec; const sp = rew ? -lerp(25, 8, u / tRec) : 3;
  const ang = rew ? -u * 22 : -tRec * 22 + (u - tRec) * 3;
  g.save(); cam(g, { z: lerp(1.0, 1.08, ss(u / d)) * kick(T, .02), y: 980, r: lerp(-.03, .02, u / d) });
  vgrad(g, 0, 0, W, H, [[0, '#2a1d18'], [1, '#120c0a']]);
  g.save(); g.globalCompositeOperation = 'lighter'; glow(g, 540, 900, 900, rew ? '#7fa8ff' : '#ff9a4a', .25); g.restore();
  const counter = rew ? 300 * (1 - eo(u / tRec)) : (u - tRec) * 40;
  E.tapeMachine(g, 540, 900, 1.15, T, ang, counter, !rew);
  // masking-tape label
  g.save(); g.translate(540, 1500); g.rotate(-.04);
  shape(g, g => { g.rect(-260, -50, 520, 100); }, '#efe2b8', { lw: 4 });
  text(g, 'TAKE ON ME — NEW VERSION', 0, 16, 44, { font: 'InterXB', color: '#3a2a20', shadow: false }); g.restore();
  // motion streaks while rewinding
  if (rew) { g.save(); g.globalAlpha = .25; g.strokeStyle = '#cfe0ff'; g.lineWidth = 5; for (let i = 0; i < 6; i++) { g.beginPath(); g.arc(320 + 0, 670, 120 + i * 8, ang * 2 + i, ang * 2 + i + .8); g.stroke(); g.beginPath(); g.arc(760, 670, 120 + i * 8, ang * 2 + i + 2, ang * 2 + i + 2.8); g.stroke(); } g.restore(); }
  g.restore();
  vignette(g, .6);
});

// S14 recording comes alive
shot(B(-12), B(-8), 'alive', (g, u, d, T) => {
  g.save(); cam(g, { z: lerp(1.05, 1.18, ss(u / d)) * kick(T, .03), y: 1080 });
  studioLive(g, T, u, 1);
  E.beams(g, T, [{ x: 200, y: 150, a: .35, col: '#ff9e4a', sp: 3, sw: .2, w: .1, i: .3 }, { x: 880, y: 150, a: -.35, col: '#ffd36e', sp: 2.5, sw: .2, w: .1, i: .3 }]);
  M(g, 'magne', { x: 230, y: 1560, s: .78, ...keysPose(T), head: headP(T, 4, { mouth: 'grin', brows: 'up', look: [.4, .2] }), front: g => keyboard(g, 0, -330, 380, [E.beatIdx(T) % 15, (E.beatIdx(T) * 2) % 15], 1) });
  M(g, 'pal', { x: 860, y: 1560, s: .78, ...strum(T), lean: -.05, head: headP(T, 7, { mouth: 'grin', brows: 'up', look: [-.4, 0] }), prop: guitarProp('#d23b2b') });
  M(g, 'morten', { x: 540, y: 1640, s: .95, hr: [70, -680], br: 1, hl: [-200, -640], head: { tilt: -.12, mouth: 'sing', open: 1.1, eyesClosed: true, brows: 'up' }, front: g => C.handMic(g, 60, -720, -.35, 1) });
  // VU overlay in corners pinned
  E.vu(g, 170, 520, 170, .85 + pulse(T) * .15); E.vu(g, 910, 520, 170, .8 + pulse(T) * .2);
  g.restore();
  vignette(g, .5);
});

// S15 pencil line leads to the chorus
shot(B(-8), B(0), 'pencil', (g, u, d, T) => {
  const p = u / d;
  const zoom = lerp(1, 1.05, ss(p)) + ei(inv(.8, 1, p)) * .6;
  g.save(); cam(g, { z: zoom, y: H / 2 + ei(inv(.8, 1, p)) * 60 });
  E.paper(g, T);
  // drawn line: wave across
  const lp = eo(inv(0, .42, p));
  const wave = x => 760 + Math.sin(x * .012) * 80 * Math.sin(x * .003 + 1) + Math.sin(x * .05) * 14;
  g.save(); g.strokeStyle = '#2b2a2e'; g.lineWidth = 7; g.lineCap = 'round'; g.beginPath();
  for (let x = -20; x <= -20 + lp * (W + 40); x += 6) { const y = wave(x); x === -20 ? g.moveTo(x, y) : g.lineTo(x, y); } g.stroke(); g.restore();
  // members sketched in, revealed by a sweeping circle following the pencil
  const rp = eo(inv(.38, .88, p));
  const pathPt = t => [lerp(1060, 120, t) + Math.sin(t * 12) * 60, 1000 - Math.sin(t * Math.PI) * 600 + t * 100];
  let px, py;
  if (p < .42) { px = -20 + lp * (W + 40); py = wave(px); } else { [px, py] = pathPt(rp); }
  S.mode = 'sketch';
  g.save(); g.beginPath();
  // reveal region: union of circles along path so far
  for (let k = 0; k <= 30; k++) { const t = rp * k / 30; const [cx, cy] = pathPt(t); g.moveTo(cx + 420, cy); g.arc(cx, cy, 420, 0, Math.PI * 2); }
  g.clip();
  M(g, 'magne', { x: 250, y: 1560, s: .78, hl: [-80, -360], hr: [80, -360], head: { mouth: 'smile', look: [.3, 0] } });
  M(g, 'pal', { x: 830, y: 1560, s: .78, ...strum(0), head: { mouth: 'smile', look: [-.3, 0] }, prop: guitarProp('#c0392b') });
  M(g, 'morten', { x: 540, y: 1600, s: .9, hl: [-100, -380], hr: [100, -380], head: { mouth: 'closed', look: [0, 0], brows: 'focus' } });
  g.restore();
  S.mode = 'color';
  E.pencil(g, px, py, -2.3 + Math.sin(T * 20) * .05, 1.0);
  g.restore();
  // whiteout into chorus
  const wf = ei(inv(.9, 1, p)); g.fillStyle = `rgba(255,255,255,${wf})`; g.fillRect(0, 0, W, H);
});

// ====== CHORUS ======
function burst(g, T, cx, cy, cols, rot = 0, n = 18) {
  for (let i = 0; i < n; i++) {
    const a0 = rot + i / n * Math.PI * 2, a1 = a0 + Math.PI / n;
    g.fillStyle = cols[i % cols.length]; g.beginPath(); g.moveTo(cx, cy); g.lineTo(cx + Math.cos(a0) * 2600, cy + Math.sin(a0) * 2600); g.lineTo(cx + Math.cos(a1) * 2600, cy + Math.sin(a1) * 2600); g.closePath(); g.fill();
  }
}
function halftone(g, col, a = .25, step = 26) { g.save(); g.fillStyle = col; g.globalAlpha = a; for (let y = 0; y < H; y += step) for (let x = (y / step) % 2 * step / 2; x < W; x += step) { g.beginPath(); ellipse(g, x, y, 5, 5); g.fill(); } g.restore(); }

shot(B(0), B(6), 'burst', (g, u, d, T) => {
  const z = 1 + pulse(T, .1) * .06 + u * .03;
  g.save(); cam(g, { z, y: H / 2 + 60, r: Math.sin(T * 3) * .015 });
  E.paper(g, T);
  burst(g, T, 540, 900, ['#ff3b30', '#ffd23f', '#18b7d9', '#f3efe4'], T * .5);
  g.fillStyle = 'rgba(243,239,228,.35)'; g.fillRect(-200, -200, W + 400, H + 400);
  halftone(g, '#1a1a1a', .12);
  S.mode = 'sketch';
  const j = pulse(T, .12);
  M(g, 'magne', { x: 230, y: 1620 - j * 20, s: .8, ...keysPose(T), head: { mouth: 'grin', brows: 'up', look: [.3, 0] }, front: g => keyboard(g, 0, -330, 380, [E.beatIdx(T) % 15], 1) });
  M(g, 'pal', { x: 860, y: 1620 - j * 40, s: .8, ...strum(T), lean: -.08, head: { mouth: 'grin', brows: 'up', look: [-.3, 0] }, prop: guitarProp('#c0392b') });
  M(g, 'morten', { x: 540, y: 1700 - j * 30, s: 1.0, hr: [60, -690], br: 1, hl: [-260, -820], head: { tilt: -.15, mouth: 'sing', open: 1.15, eyesClosed: true, brows: 'up' }, front: g => C.handMic(g, 50, -730, -.35, 1) });
  S.mode = 'color';
  // speed lines
  g.save(); g.strokeStyle = '#1b1b1b'; g.lineWidth = 5; g.globalAlpha = .5; const r = rng(Math.floor(T * 12));
  for (let i = 0; i < 26; i++) { const a = r() * Math.PI * 2; const r0 = 620 + r() * 200; g.beginPath(); g.moveTo(540 + Math.cos(a) * r0, 900 + Math.sin(a) * r0); g.lineTo(540 + Math.cos(a) * (r0 + 220), 900 + Math.sin(a) * (r0 + 220)); g.stroke(); }
  g.restore();
  g.restore();
  // 1985 badge
  const a = eob(inv(.1, .35, u)); g.save(); g.translate(W / 2, 430); g.scale(a, a); g.rotate(-.05);
  text(g, '1985', 0, 0, 210, { color: '#ffd23f', stroke: 16, strokeColor: '#1a1a1a', shadow: false }); g.restore();
  if (u < .1) { g.fillStyle = `rgba(255,255,255,${1 - u / .1})`; g.fillRect(0, 0, W, H); }
});

// S17 a drawn hand reaches out of the TV into the real room
function roomTV(g, T) {
  vgrad(g, -300, -300, W + 600, H + 600, [[0, '#24324a'], [.6, '#3a4560'], [1, '#1c2030']]);
  g.save(); g.globalAlpha = .2; for (let x = -300; x < W + 300; x += 70) { g.fillStyle = '#5a6a90'; g.fillRect(x, -300, 22, H * .8 + 300); } g.restore();
  shape(g, g => { g.rect(-300, 1420, W + 600, 800); }, '#5a3a2e', { shadeFn: g2 => vgrad(g2, 0, 1420, W, 500, [[0, 'rgba(0,0,0,0)'], [1, 'rgba(0,0,0,.4)']]) });
  shape(g, g => { g.rect(170, 1250, 740, 190); }, '#6b4a33', { lw: 6 });
  // sofa silhouette foreground
}
function sketchScreen(g, sx, sy, sw, sh, T) {
  g.fillStyle = '#f3efe4'; g.fillRect(sx, sy, sw, sh);
  const sm = S.mode; S.mode = 'sketch';
  M(g, 'morten', { x: sx + sw / 2, y: sy + sh * 1.6, s: sh / 600, head: { mouth: 'closed', brows: 'focus', look: [0, 0] } });
  S.mode = sm;
}
shot(B(6), B(12), 'hand', (g, u, d, T) => {
  const p = u / d;
  g.save(); cam(g, { z: lerp(1.0, 1.25, ss(p)), y: lerp(1000, 960, p) });
  roomTV(g, T);
  const tx = 540, ty = 1000, tw = 640; const th = tw * .78;
  E.tv(g, tx, ty, tw, 1, (g, sx, sy, sw, sh) => sketchScreen(g, sx, sy, sw, sh, T), { glow: '#fff6e0', body: '#5a4434' });
  const sx = tx - tw * .42, sy = ty - th * .4, sw = tw * .7, sh = th * .78;
  // hand: grows out of the screen
  const k = eo(inv(.1, .95, p)); const hs = lerp(.35, 1.9, k); const hx = sx + sw / 2 + k * 40, hy = sy + sh * .85 + k * 520;
  const reach = g => E.hand(g, hx, hy, hs, -.1 + Math.sin(T * 4) * .03, lerp(.6, 1.1, k));
  // inside-screen part in sketch, outside part in colour
  g.save(); g.beginPath(); g.roundRect(sx, sy, sw, sh, tw * .06); g.clip(); S.mode = 'sketch'; reach(g); S.mode = 'color'; g.restore();
  g.save(); g.beginPath(); g.rect(-400, -400, W + 800, H + 800); g.roundRect(sx, sy, sw, sh, tw * .06); g.clip('evenodd');
  reach(g); g.restore();
  g.restore();
  // living-room viewer silhouettes in the foreground
  g.fillStyle = '#0d0f18'; g.beginPath(); ellipse(g, 160, 1900, 200, 260); ellipse(g, 160, 1600, 80, 95); g.fill();
  vignette(g, .55);
});

// S18 crossing between drawing and reality
shot(B(12), B(18), 'cross', (g, u, d, T) => {
  const p = u / d;
  const edge = 540 + Math.sin(T * 2) * 10;
  const drawWorld = (mode) => {
    g.save(); cam(g, { z: 1.0 + p * .06, x: 540 + p * 40, y: 1000 });
    if (mode === 'sketch') { E.paper(g, T); halftone(g, '#1a1a1a', .07); }
    else {
      vgrad(g, -300, -300, W + 600, H + 600, [[0, '#2a0b3a'], [.6, '#5a1a4a'], [1, '#14061f']]);
      E.beams(g, T, [{ x: 700, y: 100, a: .1, col: '#ff2f8a', sp: 2, sw: .3, w: .08 }, { x: 1000, y: 100, a: -.2, col: '#36d7ff', sp: 1.6, sw: .3, w: .08, ph: 2 }]);
      shape(g, g => { g.rect(-300, 1560, W + 600, 600); }, '#1b1426', { lw: 5 });
    }
    S.mode = mode;
    const walkers = [['pal', -0.05, 1530, .7], ['magne', .12, 1570, .74], ['morten', .3, 1620, .85]];
    walkers.forEach(([who, off, y, s]) => {
      const x = lerp(-180, 1200, clamp(p)) + off * 900 - 120;
      const w = walk(T + off * 3, 1.7, 1);
      const extra = who === 'pal' ? { prop: guitarProp('#c0392b'), hl: [-150, -470], hr: w.hr } : {};
      M(g, who, { x, y, s, ...w, ...extra, head: { mouth: 'smile', brows: 'up', look: [.5, 0], blink: blink(T, off * 10) } });
    });
    S.mode = 'color';
    g.restore();
  };
  g.save(); g.beginPath(); g.rect(edge, 0, W, H); g.clip(); drawWorld('color'); g.restore();
  g.save(); g.beginPath(); g.rect(0, 0, edge, H); g.clip(); drawWorld('sketch'); g.restore();
  // torn edge
  g.save(); g.fillStyle = '#f3efe4'; g.beginPath(); g.moveTo(edge, 0); for (let y = 0; y <= H; y += 24) g.lineTo(edge + 6 + hash(y + Math.floor(T * 8)) * 16, y); g.lineTo(edge, H); g.closePath(); g.fill(); g.restore();
  g.save(); g.globalCompositeOperation = 'lighter'; glow(g, edge, 1000, 500, '#ffffff', .25 + pulse(T) * .2); g.restore();
  vignette(g, .4);
});

// S19 TVs light up across cities
shot(B(18), B(24), 'tvs', (g, u, d, T) => {
  const p = u / d;
  g.save(); cam(g, { z: lerp(1.7, 1.0, eo(p)), y: lerp(980, 960, p) });
  vgrad(g, -900, -900, W + 1800, H + 1800, [[0, '#120a2a'], [.6, '#2a1650'], [1, '#0c0a18']]);
  const lit = Math.floor(u / d * 24);
  const blocks = [[-700, 1700, 4, '#1c1836', .55], [-80, 1900, 6, '#221c40', .8], [600, 1650, 4, '#1a1530', .5], [1300, 1800, 5, '#1d1838', .6]];
  blocks.forEach(([bx, by, fl, col, sc], bi) => {
    const bw = 520 * sc * 1.4, fh = 200 * sc * 1.3;
    shape(g, g => { g.rect(bx, by - fl * fh - 60, bw, fl * fh + 60 + 600); }, col, { lw: 5 });
    for (let f = 0; f < fl; f++) for (let c = 0; c < 3; c++) {
      const wx = bx + 30 * sc + c * (bw - 60 * sc) / 3, wy = by - (f + 1) * fh + 20, ww = (bw - 60 * sc) / 3 - 24 * sc, wh = fh - 50;
      const order = Math.abs(f - fl + 2) + Math.abs(c - 1) + Math.abs(bi - 1) * 2; const on = lit >= order ? 1 : 0;
      shape(g, g => { g.rect(wx, wy, ww, wh); }, on ? '#2c3b66' : '#0e0d1c', { lw: 4 });
      if (on) {
        const tw = ww * .55, tx = wx + ww / 2, ty = wy + wh * .6;
        g.save(); g.globalCompositeOperation = 'lighter'; glow(g, tx, ty, ww * .9, '#bfe4ff', .3 + .1 * Math.sin(T * 9 + order)); g.restore();
        shape(g, g => { g.roundRect(tx - tw / 2, ty - tw * .38, tw, tw * .76, 6); }, '#f3efe4', { lw: 3 });
        g.fillStyle = '#2b2a2e'; for (let m = 0; m < 3; m++) { g.beginPath(); ellipse(g, tx - tw * .25 + m * tw * .25, ty - tw * .05, tw * .07, tw * .09); g.fill(); g.fillRect(tx - tw * .3 + m * tw * .25, ty + tw * .07, tw * .1, tw * .2); }
      }
    }
  });
  g.restore();
  vignette(g, .55);
});

// S20 No. 1 in the US
shot(B(24), B(30), 'chart', (g, u, d, T) => {
  const p = u / d;
  g.save(); cam(g, { z: lerp(1.0, 1.06, p) * kick(T, .02), y: H / 2 });
  E.paper(g, T, '#f6f0dc');
  burst(g, T, 540, 1000, ['#ffd23f', '#f6f0dc'], -T * .3, 24);
  g.fillStyle = 'rgba(246,240,220,.45)'; g.fillRect(-100, -100, W + 200, H + 200);
  // chart board
  shape(g, g => { g.roundRect(110, 560, 860, 960, 24); }, '#1a1a1a', { lw: 8 });
  text(g, 'US SINGLES CHART', 540, 650, 64, { font: 'InterXB', color: '#ffd23f', shadow: false, track: 4 });
  const rank = Math.max(1, 5 - Math.floor(inv(.05, .45, p) * 4.999));
  const rows = 5;
  for (let r = 0; r < rows; r++) {
    const y = 720 + r * 150;
    text(g, String(r + 1), 190, y + 92, 84, { color: r === 0 ? '#ffd23f' : '#f3efe4', shadow: false });
    if (r + 1 === rank) {
      const flash = pulse(T, .12);
      shape(g, g => { g.roundRect(260, y + 18, 680, 110, 14); }, mix('#ff3b30', '#ffffff', flash * .3), { lw: 5, inkColor: '#000' });
      text(g, 'TAKE ON ME', 290, y + 82, 54, { font: 'InterXB', align: 'left', color: '#fff', shadow: false });
      text(g, 'a-ha', 910, y + 82, 46, { font: 'InterB', align: 'right', color: '#ffe1de', shadow: false });
    } else {
      g.fillStyle = '#3a3a3a'; g.beginPath(); g.roundRect(260, y + 30, 520 - r * 40, 34, 10); g.fill(); g.fillStyle = '#2b2b2b'; g.beginPath(); g.roundRect(260, y + 78, 300, 26, 10); g.fill();
    }
  }
  g.restore();
  const a = eob(inv(.5, .7, p));
  if (a > 0) {
    g.save(); g.translate(W / 2, 370); g.scale(a, a); g.rotate(-.04);
    text(g, 'No. 1 IN THE US', 0, 0, 150, { color: '#ff3b30', stroke: 16, strokeColor: '#1a1a1a', shadow: false });
    g.restore();
    text(g, 'OCTOBER 1985', W / 2, 490, 64, { font: 'Anton', color: '#1a1a1a', shadow: false, alpha: inv(.6, .8, p), track: 6 });
  }
});

// S21 the audience grows – pull out to a stadium
function stage(g, T, era, o = {}) {
  // o: {y, s, light}
  const y = o.y ?? 1250, s = o.s ?? .55;
  shape(g, g => { g.rect(-600, y, W + 1200, 120); }, '#18121f', { lw: 6 });
  const late = era === 'late';
  M(g, 'magne', { x: 540 - 330 * s / .55, y: y + 4, s: s * .95, era, ...keysPose(T), head: headP(T, 4, { mouth: 'smile', look: [.3, 0] }), front: g => keyboard(g, 0, -330, 360, [E.beatIdx(T) % 15], 1) });
  M(g, 'pal', { x: 540 + 330 * s / .55, y: y + 4, s: s * .95, era, ...strum(T), head: headP(T, 7, { mouth: 'smile', look: [-.3, 0] }), prop: guitarProp(late ? '#2a2a2a' : '#c0392b') });
  M(g, 'morten', { x: 540, y: y + 10, s, era, hr: [60, -690], br: 1, hl: o.armUp ? [-240, -800] : [-110, -360], head: { tilt: -.08, mouth: 'sing', open: .5 + .5 * Math.abs(Math.sin(T * 4.4)), eyesClosed: Math.sin(T) > .3, brows: 'up', blink: blink(T, 2) }, front: g => C.handMic(g, 50, -730, -.35, 1) });
}
shot(B(30), B(36), 'stadium', (g, u, d, T) => {
  const p = u / d; const z = lerp(2.4, 1.0, eo(p * 1.05)) * kick(T, .02);
  g.save(); cam(g, { z, y: lerp(1050, 1000, p) });
  vgrad(g, -1500, -1500, W + 3000, H + 3000, [[0, '#0a0718'], [.5, '#22104a'], [1, '#05040a']]);
  // stadium bowl rings of lights
  for (let r = 0; r < 4; r++) { const ry = 700 - r * 120; g.fillStyle = mix('#140c26', '#2a1a4a', r / 4); g.beginPath(); g.ellipse(540, ry + 400, 1400 + r * 300, 500 + r * 120, 0, Math.PI, 0); g.fill(); const rr = rng(r + 3); for (let i = 0; i < 160; i++) { const a = Math.PI + rr() * Math.PI; g.fillStyle = `rgba(255,${200 + rr() * 55},${150 + rr() * 100},${.5 + .5 * Math.sin(T * 5 + i)})`; g.fillRect(540 + Math.cos(a) * (1400 + r * 300) * (.85 + rr() * .1), ry + 400 + Math.sin(a) * (500 + r * 120) * (.9), 4, 4); } }
  shape(g, g => { g.rect(140, 560, 800, 380); }, '#0c0a14', { lw: 6 });
  g.save(); g.globalCompositeOperation = 'lighter'; glow(g, 540, 750, 500, '#36d7ff', .3 + pulse(T) * .2); g.restore();
  text(g, 'a-ha', 540, 820, 200, { font: 'InterXB', color: '#e8fbff', shadowBlur: 40, track: -6 });
  stage(g, T, '80s', { y: 1250, s: .5 });
  E.beams(g, T, [{ x: 100, y: 520, a: .2, col: '#ff2f8a', sp: 2.2, sw: .4 }, { x: 980, y: 520, a: -.2, col: '#36d7ff', sp: 1.8, sw: .4, ph: 1 }, { x: 540, y: 500, a: 0, col: '#ffd36e', sp: 3, sw: .5, ph: 2, i: .3, w: .05 }, { x: -600, y: 300, a: .5, col: '#a05cff', sp: 1.2, sw: .3, ph: 3 }, { x: 1700, y: 300, a: -.5, col: '#ff7b3a', sp: 1.3, sw: .3, ph: 4 }]);
  g.save(); g.translate(540, 0); g.scale(1.6, 1); g.translate(-540, 0); E.crowdSea(g, T, 1380, 2600, '#ff4fa0', 11, 1.4); g.restore();
  g.restore();
  vignette(g, .5);
});

// S22 massive crowds (narration resumes)
shot(B(36), B(44), 'concert', (g, u, d, T) => {
  const p = ss(u / d);
  g.save(); cam(g, { z: lerp(1.15, 1.25, p), y: lerp(1080, 1020, p), x: lerp(520, 560, p) });
  vgrad(g, -300, -300, W + 600, H + 600, [[0, '#06040f'], [.5, '#1a0d33'], [1, '#05040a']]);
  shape(g, g => { g.rect(60, 420, 960, 480); }, '#0c0a14', { lw: 6 });
  g.save(); g.globalCompositeOperation = 'lighter'; glow(g, 540, 660, 600, '#ff6a3a', .28 + pulse(T) * .2); g.restore();
  text(g, 'a-ha', 540, 740, 210, { font: 'InterXB', color: '#fff1e6', shadowBlur: 40, track: -6 });
  stage(g, T, '80s', { y: 1300, s: .62, armUp: true });
  E.beams(g, T, [{ x: 80, y: 380, a: .25, col: '#ff7b3a', sp: 2, sw: .35 }, { x: 1000, y: 380, a: -.25, col: '#ffd36e', sp: 1.6, sw: .35, ph: 1 }, { x: 300, y: 360, a: .05, col: '#ff2f8a', sp: 2.8, sw: .4, ph: 2, i: .35 }, { x: 780, y: 360, a: -.05, col: '#36d7ff', sp: 2.4, sw: .4, ph: 3, i: .35 }]);
  E.crowd(g, T, { y: 1560, rows: 4, scale: 1.0, col: '#07050c', rim: '#ffb36b', rimA: .7, arms: .75, jump: 1, wave: 8, seed: 21 });
  g.restore();
  g.fillStyle = `rgba(255,220,200,${pulse(T, .05) * .08})`; g.fillRect(0, 0, W, H);
  vignette(g, .55);
});

// S23 The Sun Always Shines on T.V.
shot(B(44), B(50), 'sun', (g, u, d, T) => {
  const p = ss(u / d);
  g.save(); cam(g, { z: lerp(1.0, 1.12, p), y: 1040 });
  vgrad(g, -300, -300, W + 600, H + 600, [[0, '#1a1024'], [1, '#0b0710']]);
  const tx = 540, ty = 1080, tw = 760;
  const sunOn = eo(inv(0, .5, u));
  E.tv(g, tx, ty, tw, 1, (g, sx, sy, sw, sh) => {
    vgrad(g, sx, sy, sw, sh, [[0, '#ff7a2f'], [.6, '#ffb347'], [1, '#ffd98a']]);
    const cy = sy + sh * lerp(.95, .58, sunOn);
    g.save(); g.translate(sx + sw / 2, cy); g.rotate(T * .3);
    for (let i = 0; i < 16; i++) { g.fillStyle = i % 2 ? 'rgba(255,240,180,.55)' : 'rgba(255,120,40,.25)'; g.beginPath(); g.moveTo(0, 0); g.arc(0, 0, sw, i / 16 * Math.PI * 2, (i + 1) / 16 * Math.PI * 2); g.fill(); }
    g.restore();
    g.fillStyle = '#fff3c4'; g.beginPath(); ellipse(g, sx + sw / 2, cy, sw * .2, sw * .2); g.fill();
    // band silhouettes against the sun
    g.fillStyle = '#2a1206';
    [[-.25, .9], [0, 1], [.25, .9]].forEach(([dx, k]) => { const bx = sx + sw / 2 + dx * sw, by = sy + sh; g.beginPath(); ellipse(g, bx, by - sh * .45 * k, sw * .06, sw * .075); g.fill(); g.beginPath(); g.roundRect(bx - sw * .09, by - sh * .36 * k, sw * .18, sh * .4, 20); g.fill(); });
  }, { glow: '#ffa040', body: '#3a2a22' });
  g.restore();
  g.save(); g.globalCompositeOperation = 'lighter'; glow(g, 500, 1080, 1000, '#ff8a2a', .3 * sunOn); g.restore();
  vignette(g, .6, '20,5,0');
  const a = inv(.2, .5, u);
  text(g, 'THE SUN ALWAYS', W / 2, 400, 104, { color: '#ffe1a6', alpha: a, stroke: 12, strokeColor: '#2a1206' });
  text(g, 'SHINES ON T.V.', W / 2, 520, 104, { color: '#ffe1a6', alpha: a, stroke: 12, strokeColor: '#2a1206' });
  text(g, 'ANOTHER HIT · UK No. 1', W / 2, 1520, 58, { font: 'InterXB', color: '#fff', alpha: inv(.6, .9, u), track: 3 });
});

// S24 Farewell 2010 – lights go out
shot(B(50), B(56), 'farewell', (g, u, d, T) => {
  const p = u / d; const tOut = [B(53), B(54), B(55)].map(b => b - B(50));
  const banks = tOut.map(t => u < t ? 1 : 0); const lights = (banks[0] + banks[1] + banks[2]) / 3;
  g.save(); cam(g, { z: lerp(1.05, 1.12, ss(p)), y: 1060 });
  vgrad(g, -300, -300, W + 600, H + 600, [[0, mix('#02030a', '#0a1430', lights)], [1, '#020205']]);
  if (banks[0]) E.beams(g, T * .4, [{ x: 140, y: 300, a: .2, col: '#6fa8ff', sp: .8, sw: .15, i: .4 }, { x: 940, y: 300, a: -.2, col: '#6fa8ff', sp: .7, sw: .15, i: .4, ph: 1 }]);
  if (banks[1]) E.beams(g, T * .4, [{ x: 540, y: 250, a: 0, col: '#bcd4ff', sp: .5, sw: .05, i: .45, w: .14 }]);
  shape(g, g => { g.rect(-300, 1380, W + 600, 140); }, '#0d0f1a', { lw: 6 });
  // band holds hands up together (late era)
  g.save(); g.globalAlpha = .35 + .65 * lights;
  const Y = 1390;
  M(g, 'magne', { x: 290, y: Y, s: .68, era: 'late', hl: [-120, -360], hr: [130, -760], br: 1, head: { mouth: 'smile', brows: 'sad', look: [.3, -.2], blink: blink(T, 4) } });
  M(g, 'pal', { x: 790, y: Y, s: .68, era: 'late', hl: [-130, -760], bl: -1, hr: [120, -360], head: { mouth: 'smile', brows: 'sad', look: [-.3, -.2], blink: blink(T, 7) } });
  M(g, 'morten', { x: 540, y: Y + 6, s: .72, era: 'late', hl: [-150, -780], bl: -1, hr: [150, -780], br: 1, head: { mouth: 'closed', brows: 'sad', look: [0, -.3], eyesClosed: u > tOut[0], blink: blink(T, 2) } });
  g.restore();
  E.crowd(g, T * .5, { y: 1640, rows: 3, scale: 1.0, col: '#03040a', rim: '#6fa8ff', rimA: .5 * lights, arms: .5, jump: 0, wave: 3, seed: 31 });
  g.restore();
  g.fillStyle = `rgba(0,0,0,${(1 - lights) * .75})`; g.fillRect(0, 0, W, H);
  vignette(g, .7);
  const a = inv(.15, .45, u) * (1 - inv(tOut[2] - .1, tOut[2] + .2, u) * .7);
  text(g, '2010', W / 2, 420, 170, { color: '#dbe6ff', alpha: a, track: 10 });
  text(g, 'FAREWELL CONCERT', W / 2, 520, 70, { font: 'Bebas', color: '#dbe6ff', alpha: a, track: 12 });
});

// S25 darkness – a single light on the empty mic
shot(B(56), B(60), 'dark', (g, u, d, T) => {
  const p = u / d;
  g.save(); cam(g, { z: lerp(1.0, 1.1, ss(p)), y: 1100 });
  g.fillStyle = '#020204'; g.fillRect(-300, -300, W + 600, H + 600);
  const on = eo(inv(.1, .7, u)) * (.85 + .15 * noise1(T * 6));
  g.save(); g.globalCompositeOperation = 'lighter';
  const gr = g.createLinearGradient(540, 0, 540, 1500); gr.addColorStop(0, `rgba(200,215,255,${.3 * on})`); gr.addColorStop(1, `rgba(200,215,255,${.05 * on})`);
  g.fillStyle = gr; g.beginPath(); g.moveTo(500, -100); g.lineTo(580, -100); g.lineTo(780, 1500); g.lineTo(300, 1500); g.closePath(); g.fill();
  g.fillStyle = `rgba(200,215,255,${.18 * on})`; g.beginPath(); g.ellipse(540, 1500, 260, 50, 0, 0, Math.PI * 2); g.fill();
  const r = rng(4); g.fillStyle = `rgba(220,230,255,${.5 * on})`; for (let i = 0; i < 30; i++) { const y = (r() * 1400 + u * 20) % 1400; const x = 540 + (r() - .5) * (100 + y * .3); g.fillRect(x, y, 3, 3); }
  g.restore();
  g.save(); g.globalAlpha = .4 + .6 * on; micStand(g, 540, 1500, 620, 1); g.restore();
  g.restore();
  vignette(g, .8);
});

// S26 2015 – the lights rise, together again
shot(B(60), 60.05, 'return', (g, u, d, T) => {
  const p = u / d; const rise = eo(inv(0, 1.2, u));
  g.save(); cam(g, { z: lerp(1.18, 1.05, ss(p)), y: lerp(1150, 1080, ss(p)) });
  vgrad(g, -300, -300, W + 600, H + 600, [[0, mix('#020204', '#3a1a0a', rise)], [.55, mix('#020204', '#c8692a', rise)], [1, mix('#020204', '#2a1208', rise)]]);
  g.save(); g.globalCompositeOperation = 'lighter'; glow(g, 540, 900, 1100 * rise + 10, '#ffcf7a', .55 * rise); g.restore();
  E.beams(g, T * .5, [{ x: 540, y: 200, a: 0, col: '#ffd59a', sp: .6, sw: .08, w: .2, i: .4 * rise }, { x: 100, y: 300, a: .3, col: '#ffb36b', sp: .8, sw: .2, i: .3 * rise }, { x: 980, y: 300, a: -.3, col: '#ffb36b', sp: .7, sw: .2, i: .3 * rise, ph: 1 }]);
  shape(g, g => { g.rect(-300, 1420, W + 600, 160); }, mix('#020204', '#3a2014', rise), { lw: 6 });
  // the three, arms around each other's shoulders
  const Y = 1430;
  g.save(); g.globalAlpha = .25 + .75 * rise;
  M(g, 'magne', { x: 330, y: Y, s: .78, era: 'late', hl: [-110, -350], hr: [150, -560], br: -1, head: { mouth: 'smile', brows: 'up', look: [.4, 0], blink: blink(T, 4) } });
  M(g, 'pal', { x: 750, y: Y, s: .78, era: 'late', hl: [-150, -560], hr: [110, -350], head: { mouth: 'smile', brows: 'up', look: [-.4, 0], blink: blink(T, 7) } });
  M(g, 'morten', { x: 540, y: Y + 8, s: .82, era: 'late', hl: [-190, -560], hr: [190, -560], head: { mouth: 'smile', brows: 'up', look: [0, -.1], blink: blink(T, 2) } });
  g.restore();
  E.crowd(g, T, { y: 1700, rows: 3, scale: 1.0, col: '#120804', rim: '#ffcf7a', rimA: .8 * rise, arms: .7, jump: rise, wave: 6, seed: 41 });
  g.restore();
  vignette(g, .55, '20,8,0');
  text(g, '2015', W / 2, 420, 170, { color: '#ffd27a', alpha: inv(.3, .8, u) * (1 - inv(1.35, 1.6, u)), track: 10 });
  text(g, 'TOGETHER AGAIN', W / 2, 520, 70, { font: 'Bebas', color: '#ffe8c0', alpha: inv(.5, .9, u) * (1 - inv(1.35, 1.6, u)), track: 12 });
  const f1 = inv(1.6, 2.0, u), f2 = inv(2.35, 2.75, u);
  g.save(); g.translate(0, (1 - eo(f1)) * 30);
  text(g, 'ONE SONG', W / 2, 350, 128, { color: '#fff4dc', alpha: f1, stroke: 10, strokeColor: '#2a1208' });
  text(g, 'OPENED THE DOOR.', W / 2, 475, 112, { color: '#fff4dc', alpha: f1, stroke: 10, strokeColor: '#2a1208' }); g.restore();
  g.save(); g.translate(0, (1 - eo(f2)) * 30);
  text(g, 'THEY KEPT GOING.', W / 2, 610, 112, { color: '#ffd27a', alpha: f2, stroke: 10, strokeColor: '#2a1208' }); g.restore();
  const fo = inv(d - .45, d, u); if (fo > 0) { g.fillStyle = `rgba(0,0,0,${fo})`; g.fillRect(0, 0, W, H); }
});

function renderFrame(g, T, frame) {
  S.frame = frame; S.T = T; S.mode = 'color';
  const sh = shots.find(s => T >= s.a && T < s.b) || shots[shots.length - 1];
  g.save(); g.fillStyle = '#000'; g.fillRect(0, 0, W, H);
  sh.fn(g, T - sh.a, sh.b - sh.a, T);
  g.restore();
  return sh.name;
}
module.exports = { shots, renderFrame, B, CHORUS };
