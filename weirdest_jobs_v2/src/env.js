// ===================================================================== env.js
// Painted environment kit. Each set is pre-rendered once into layer canvases (for parallax).
'use strict';
const SETS = {};

// ------------------------------------------------------------------ building blocks
function sky(c, w, h, stops, stars = 0, seed = 1) {
  c.fillStyle = lg(c, 0, 0, 0, h, stops); c.fillRect(0, 0, w, h);
  if (stars) { const r = rng(seed); for (let i = 0; i < stars; i++) { const y = r() * h * .55; ell(c, r() * w, y, 1 + r() * 2.2, 1 + r() * 2.2, `rgba(255,250,235,${(.25 + r() * .7) * (1 - y / (h * .55))})`); } }
}
function bricks(c, x, y, w, h, base, seed, bw = 46, bh = 20) {
  const r = rng(seed);
  c.save(); c.beginPath(); c.rect(x, y, w, h); c.clip();
  c.fillStyle = shade(base, .35); c.fillRect(x, y, w, h);
  for (let j = 0, yy = y; yy < y + h; j++, yy += bh) {
    for (let xx = x - (j % 2) * bw / 2; xx < x + w; xx += bw) {
      c.fillStyle = mix(base, r() < .5 ? '#3a2018' : '#c98a60', r() * .3);
      c.fillRect(xx + 1.5, yy + 1.5, bw - 3, bh - 3);
      if (r() < .25) { c.fillStyle = 'rgba(255,230,200,0.08)'; c.fillRect(xx + 2, yy + 2, bw - 6, 4); }
    }
  }
  c.fillStyle = lg(c, x, y, x, y + h, [[0, 'rgba(10,6,20,0.15)'], [1, 'rgba(10,6,20,0.45)']]); c.fillRect(x, y, w, h);
  c.restore();
}
function stones(c, x, y, w, h, base, seed, s = 46) {
  const r = rng(seed);
  c.save(); c.beginPath(); c.rect(x, y, w, h); c.clip();
  c.fillStyle = shade(base, .45); c.fillRect(x, y, w, h);
  for (let yy = y; yy < y + h; yy += s * .7) for (let xx = x - r() * s; xx < x + w; xx += s * (.8 + r() * .5)) {
    const ww = s * (.7 + r() * .5), hh = s * .6 * (.8 + r() * .3);
    blob(c, [[xx, yy + hh * .1], [xx + ww * .1, yy], [xx + ww * .9, yy + 2], [xx + ww, yy + hh * .5], [xx + ww * .85, yy + hh], [xx + ww * .1, yy + hh * .95]], mix(base, r() < .5 ? '#20202a' : '#e8e0cc', r() * .25));
  }
  c.restore();
}
function windowLit(c, x, y, w, h, lit, seed, opts = {}) {
  const r = rng(seed);
  const frame = opts.frame || '#e9e1cf';
  rrect(c, x - 8, y - 8, w + 16, h + 16, 4, shade(opts.wall || '#6a3a2a', .5));
  if (lit > 0) {
    c.fillStyle = lg(c, x, y, x, y + h, [[0, mix('#ffd27a', '#ff9a3c', .3)], [1, '#ffb05a']]); c.fillRect(x, y, w, h);
    c.save(); c.globalAlpha = lit; glow(c, x + w / 2, y + h / 2, Math.max(w, h) * 1.3, 'rgba(255,190,90,0.35)'); c.restore();
  } else {
    c.fillStyle = lg(c, x, y, x + w, y + h, [[0, '#2a3a5a'], [.5, '#1a2236'], [1, '#2d3d5d']]); c.fillRect(x, y, w, h);
    c.fillStyle = 'rgba(170,200,255,0.14)'; c.beginPath(); c.moveTo(x + w * .1, y + h); c.lineTo(x + w * .55, y); c.lineTo(x + w * .75, y); c.lineTo(x + w * .3, y + h); c.fill();
  }
  if (opts.curtain) { c.fillStyle = opts.curtain; c.fillRect(x, y, w * .22, h); c.fillRect(x + w * .78, y, w * .22, h); }
  c.lineWidth = Math.max(3, w * .05); c.strokeStyle = frame;
  c.strokeRect(x, y, w, h); line(c, [[x + w / 2, y], [x + w / 2, y + h]], c.lineWidth * .7, frame); line(c, [[x, y + h / 2], [x + w, y + h / 2]], c.lineWidth * .7, frame);
  rrect(c, x - 14, y + h + 4, w + 28, 12, 3, mix(frame, '#8a8070', .3), 3);
  rrect(c, x - 10, y - 18, w + 20, 14, 3, mix(frame, '#8a8070', .2), 3);
}
function slateRoof(c, pts, col, seed) {
  poly(c, pts, col, 4);
  c.save(); c.beginPath(); pts.forEach((p, i) => i ? c.lineTo(p[0], p[1]) : c.moveTo(p[0], p[1])); c.closePath(); c.clip();
  const r = rng(seed), ys = Math.min(...pts.map(p => p[1])), ye = Math.max(...pts.map(p => p[1])), xs = Math.min(...pts.map(p => p[0])), xe = Math.max(...pts.map(p => p[0]));
  for (let y = ys; y < ye; y += 14) { line(c, [[xs, y], [xe, y]], 2, rgba('#000000', .25)); for (let x = xs + (y % 28 ? 0 : 14); x < xe; x += 28) { line(c, [[x, y], [x, y + 14]], 1.5, rgba('#000', .2)); if (r() < .15) { c.fillStyle = 'rgba(255,255,255,0.05)'; c.fillRect(x, y, 28, 14); } } }
  c.fillStyle = lg(c, 0, ys, 0, ye, [[0, 'rgba(180,200,255,0.15)'], [1, 'rgba(0,0,0,0.25)']]); c.fillRect(xs, ys, xe - xs, ye - ys);
  c.restore();
}
function chimney(c, x, y, w, h, col, seed) {
  bricks(c, x, y, w, h, col, seed, 22, 12); c.lineWidth = 4; c.strokeStyle = INK; c.strokeRect(x, y, w, h);
  rrect(c, x - 6, y - 10, w + 12, 14, 3, shade(col, .2), 4);
  for (let i = 0; i < Math.max(1, Math.floor(w / 30)); i++) rrect(c, x + 6 + i * 30, y - 34, 18, 26, 3, '#a85a3a', 3);
}
function terrace(c, x0, ground, n, seed, opts = {}) {
  // a row of industrial terraced houses, front view
  const r = rng(seed), hw = opts.hw || 300, hh = opts.hh || 520;
  for (let i = 0; i < n; i++) {
    const x = x0 + i * hw, top = ground - hh - r() * 30;
    const wall = mix(opts.brick || '#b0583a', ['#a04a34', '#c86a44', '#9a4a3a'][i % 3], .35);
    bricks(c, x, top, hw, ground - top, wall, seed * 10 + i);
    c.lineWidth = 4; c.strokeStyle = INK; c.strokeRect(x, top, hw, ground - top);
    slateRoof(c, [[x - 10, top], [x + hw * .2, top - 120], [x + hw * .8, top - 120], [x + hw + 10, top]], '#3a4258', seed + i);
    chimney(c, x + hw * .62, top - 200, 62, 100, '#7a3a2a', seed + i * 3);
    const lit = r(); const lit2 = r();
    windowLit(c, x + hw * .14, top + 70, hw * .26, 150, lit < (opts.litP ?? .45) ? .9 : 0, seed + i, { wall, curtain: lit < .45 ? rgba('#7a2a2a', .6) : null });
    windowLit(c, x + hw * .6, top + 70, hw * .26, 150, lit2 < (opts.litP ?? .45) ? .9 : 0, seed + i + 50, { wall });
    // door + step + lower window
    rrect(c, x + hw * .14, ground - 210, hw * .26, 210, 6, ['#2e4a3a', '#4a2a2a', '#2a3a5a'][i % 3], 4);
    ell(c, x + hw * .35, ground - 105, 5, 5, '#d8b060');
    rrect(c, x + hw * .1, ground - 20, hw * .34, 20, 2, '#8a8478', 3);
    windowLit(c, x + hw * .58, ground - 200, hw * .3, 140, r() < .3 ? .7 : 0, seed + i + 90, { wall });
    line(c, [[x + hw - 8, top], [x + hw - 8, ground]], 6, '#2a2a30');
  }
}
function cobbles(c, x, y, w, h, base, seed, horizonY) {
  const r = rng(seed);
  c.fillStyle = lg(c, 0, y, 0, y + h, [[0, shade(base, .5)], [1, shade(base, .15)]]); c.fillRect(x, y, w, h);
  for (let yy = y; yy < y + h;) {
    const k = (yy - y) / h, sz = 14 + k * 40;
    for (let xx = x - r() * sz; xx < x + w; xx += sz * 1.05) ell(c, xx, yy, sz * .5, sz * .26, mix(base, r() < .5 ? '#101018' : '#c8c0b0', r() * .25), 1.5, 0, rgba(INK, .5));
    yy += sz * .55;
  }
  c.fillStyle = lg(c, 0, y, 0, y + h, [[0, 'rgba(120,150,200,0.25)'], [.4, 'rgba(0,0,0,0)']]); c.fillRect(x, y, w, h);
}
function factory(c, x, ground, w, h, col, seed) {
  const r = rng(seed);
  poly(c, [[x, ground], [x, ground - h], [x + w * .2, ground - h - 60], [x + w * .4, ground - h], [x + w * .6, ground - h - 60], [x + w * .8, ground - h], [x + w, ground - h - 60], [x + w, ground]], col);
  for (let j = 0; j < 3; j++) for (let i = 0; i < Math.floor(w / 50); i++) if (r() < .5) { c.fillStyle = r() < .6 ? 'rgba(255,190,90,0.8)' : 'rgba(255,190,90,0.25)'; c.fillRect(x + 20 + i * 50, ground - h + 40 + j * 70, 22, 34); }
}
function millChimney(c, x, ground, h, col) {
  poly(c, [[x - 34, ground], [x - 22, ground - h], [x + 22, ground - h], [x + 34, ground]], col);
  c.fillStyle = shade(col, .2); c.fillRect(x - 28, ground - h - 16, 56, 18);
}
function smokePlume(c, x, y, t, col, seed, scale = 1) {
  const r = rng(seed);
  for (let i = 0; i < 14; i++) {
    const age = ((t * .12 + i / 14 + r() * .05) % 1), rr = (20 + age * 120) * scale;
    const px = x + (age * 260 + Math.sin(i + t * .5) * 20) * scale, py = y - age * 380 * scale;
    c.fillStyle = rgba(col, .38 * (1 - age)); c.beginPath(); c.arc(px, py, rr, 0, TAU); c.fill();
  }
}
function fogBand(c, y, h, t, col, a, speed = 20, seed = 3, w = W) {
  const r = rng(seed);
  for (let i = 0; i < 16; i++) {
    const x = ((r() * w * 1.6 + t * speed * (.6 + r() * .8)) % (w * 1.6)) - w * .3, yy = y + (r() - .5) * h, rr = 160 + r() * 240;
    c.fillStyle = rg(c, x, yy, 0, rr, [[0, rgba(col, a)], [1, rgba(col, 0)]]); c.fillRect(x - rr, yy - rr, rr * 2, rr * 2);
  }
}
function lamp(c, x, ground, h, lit = 1) {
  line(c, [[x, ground], [x, ground - h]], 12, '#1e2026'); line(c, [[x, ground], [x, ground - h]], 4, '#3a3e48');
  poly(c, [[x - 26, ground - h - 70], [x + 26, ground - h - 70], [x + 18, ground - h], [x - 18, ground - h]], lit ? '#ffd27a' : '#3a4a5a', 4);
  poly(c, [[x - 34, ground - h - 70], [x, ground - h - 100], [x + 34, ground - h - 70]], '#1e2026', 4);
  if (lit) glow(c, x, ground - h - 35, 220, 'rgba(255,200,110,0.45)');
}
function tree(c, x, ground, h, col, seed, bare = true) {
  const r = rng(seed);
  const br = (x0, y0, a, l, w, d) => { if (d > 6 || l < 8) return; const x1 = x0 + Math.sin(a) * l, y1 = y0 - Math.cos(a) * l; line(c, [[x0, y0], [x1, y1]], w, col); br(x1, y1, a - .35 - r() * .3, l * (.68 + r() * .12), w * .66, d + 1); if (r() < .85) br(x1, y1, a + .3 + r() * .3, l * (.62 + r() * .14), w * .62, d + 1); };
  br(x, ground, (r() - .5) * .15, h * .32, h * .06, 0);
}
function church(c, x, ground, s, wall, roof, lit) {
  stones(c, x - 160 * s, ground - 380 * s, 320 * s, 380 * s, wall, 21, 40 * s);
  c.lineWidth = 4; c.strokeStyle = INK; c.strokeRect(x - 160 * s, ground - 380 * s, 320 * s, 380 * s);
  poly(c, [[x - 190 * s, ground - 380 * s], [x, ground - 560 * s], [x + 190 * s, ground - 380 * s]], roof, 4);
  // tower
  stones(c, x + 120 * s, ground - 760 * s, 150 * s, 760 * s, mix(wall, '#000', .1), 22, 38 * s);
  c.strokeRect(x + 120 * s, ground - 760 * s, 150 * s, 760 * s);
  poly(c, [[x + 105 * s, ground - 760 * s], [x + 195 * s, ground - 1020 * s], [x + 285 * s, ground - 760 * s]], roof, 4);
  rrect(c, x + 165 * s, ground - 700 * s, 60 * s, 90 * s, 28 * s, '#141018', 3);   // belfry
  poly(c, [[x - 30 * s, ground], [x - 30 * s, ground - 140 * s], [x, ground - 180 * s], [x + 30 * s, ground - 140 * s], [x + 30 * s, ground]], '#2a1a14', 4);
  for (const wx of [-110, 70]) { rrect(c, x + wx * s, ground - 300 * s, 40 * s, 110 * s, 20 * s, lit ? '#ffcc66' : '#2a2a3a', 3); if (lit) glow(c, x + (wx + 20) * s, ground - 250 * s, 120 * s, 'rgba(255,190,90,0.35)'); }
  line(c, [[x + 195 * s, ground - 1020 * s], [x + 195 * s, ground - 1080 * s]], 5, '#2a2a30'); line(c, [[x + 175 * s, ground - 1055 * s], [x + 215 * s, ground - 1055 * s]], 5, '#2a2a30');
}
function cottage(c, x, ground, w, h, wall, roof, seed, lit) {
  stones(c, x, ground - h, w, h, wall, seed, 34);
  c.lineWidth = 4; c.strokeStyle = INK; c.strokeRect(x, ground - h, w, h);
  blob(c, [[x - 30, ground - h + 10], [x + w * .15, ground - h - 150], [x + w * .85, ground - h - 160], [x + w + 30, ground - h + 10], [x + w * .5, ground - h + 24]], roof, 4, INK, .2);   // thatch
  for (let i = 0; i < 18; i++) line(c, [[x + i * w / 18, ground - h - 130], [x + i * w / 18 - 10, ground - h + 10]], 1.5, rgba('#000', .2));
  rrect(c, x + w * .12, ground - 170, 70, 170, 4, '#2a1c14', 4);
  windowLit(c, x + w * .56, ground - h + 60, 80, 80, lit ? .9 : 0, seed, { frame: '#5a4a3a', wall });
}
function crow(c, x, y, s, flap, col = '#0c0a10') {
  c.save(); c.translate(x, y); c.scale(s, s);
  const f = Math.sin(flap);
  blob(c, [[-30, 0], [-10, -8], [20, -6], [34, -2], [20, 6], [-6, 6]], col);
  blob(c, [[-6, -4], [-30, -30 * f - 10], [-50, -36 * f - 4], [-22, 4]], col);
  blob(c, [[2, -4], [24, -34 * f - 10], [8, 4]], col);
  poly(c, [[34, -4], [46, 0], [34, 2]], '#3a3020');
  c.restore();
}
function curtainDrape(c, x, y, w, h, col, side, t = 0) {
  const folds = 6;
  c.fillStyle = col; c.beginPath(); c.moveTo(x, y);
  for (let i = 0; i <= folds; i++) c.lineTo(x + w * i / folds + Math.sin(i * 2 + t) * 6, y + h - (side * 40) * Math.sin(i / folds * PI));
  c.lineTo(x + w, y); c.closePath(); c.fill();
  for (let i = 0; i < folds; i++) { const xx = x + w * (i + .5) / folds; c.fillStyle = lg(c, xx - w / folds / 2, 0, xx + w / folds / 2, 0, [[0, 'rgba(0,0,0,0.35)'], [.5, 'rgba(255,220,200,0.12)'], [1, 'rgba(0,0,0,0.35)']]); c.fillRect(xx - w / folds / 2, y, w / folds, h); }
}

// ------------------------------------------------------------------ SETS
function buildEnv() {
  // ---------- 1. pre-dawn industrial town (side view street), wide for tracking
  {
    const w = 2600;
    const skyL = mk(W, H); sky(skyL.x, W, H, [[0, '#1a2a6a'], [.3, '#3a5ab0'], [.55, '#8a8ad0'], [.7, '#f09a70'], [.8, '#ffc884']], 220, 3);
    glow(skyL.x, W * .7, H * .78, 900, 'rgba(255,180,110,0.55)');
    ell(skyL.x, 240, 380, 46, 46, '#f6eedc'); glow(skyL.x, 240, 380, 200, 'rgba(240,240,255,0.25)');
    const far = mk(w, H); const fx = far.x;
    for (let i = 0; i < 9; i++) factory(fx, i * 300 + 40, 1180, 200 + (i % 3) * 60, 380, '#34407a', 30 + i);
    for (const [x, h] of [[300, 520], [900, 640], [1500, 560], [2100, 600]]) millChimney(fx, x, 1180, h, '#2e3870');
    fx.fillStyle = lg(fx, 0, 900, 0, 1200, [[0, 'rgba(120,130,180,0)'], [1, 'rgba(120,130,180,0.45)']]); fx.fillRect(0, 900, w, 300);
    const mid = mk(w, H); terrace(mid.x, 0, 1460, 9, 7, { litP: .4 });
    const street = mk(w, H - 1460); cobbles(street.x, 0, 0, w, H - 1460, '#6a72a0', 9);
    rrect(street.x, 0, w, 18, 0, '#8a8a90', 3);
    SETS.town = { sky: skyL.c, far: far.c, mid: mid.c, street: street.c, w, ground: 1460 };
  }
  // ---------- 2. bedroom interior
  {
    const b = mk(W, H), c = b.x;
    c.fillStyle = '#5a6a7a'; c.fillRect(0, 0, W, H);
    for (let x = 0; x < W; x += 90) { c.fillStyle = 'rgba(30,40,60,0.25)'; c.fillRect(x, 0, 45, 1500); for (let y = 30; y < 1500; y += 120) { ell(c, x + 67, y, 12, 16, 'rgba(240,220,180,0.18)'); ell(c, x + 67, y + 18, 5, 8, 'rgba(120,160,110,0.25)'); } }
    c.fillStyle = lg(c, 0, 1400, 0, H, [[0, '#5a3a24'], [1, '#2a1a10']]); c.fillRect(0, 1450, W, 470);
    for (let i = 0; i < 9; i++) line(c, [[i * 140 - 20, 1450], [i * 180 - 200, H]], 3, 'rgba(0,0,0,0.3)');
    rrect(c, 0, 1435, W, 22, 0, '#3a2414', 3);
    // window with pre-dawn
    rrect(c, 560, 260, 380, 520, 10, '#e8dcc0', 6);
    c.fillStyle = lg(c, 0, 280, 0, 760, [[0, '#1a2448'], [.7, '#4a5a8a'], [1, '#d98a6a']]); c.fillRect(584, 284, 332, 472);
    for (const [x, y] of [[640, 330], [720, 300], [860, 360], [600, 420]]) ell(c, x, y, 2, 2, '#fff');
    line(c, [[750, 284], [750, 756]], 10, '#e8dcc0'); line(c, [[584, 520], [916, 520]], 10, '#e8dcc0');
    curtainDrape(c, 520, 230, 110, 600, '#7a2f3a', 0); curtainDrape(c, 870, 230, 110, 600, '#7a2f3a', 0);
    rrect(c, 500, 210, 500, 26, 8, '#3a2414', 4);
    // picture frame + shelf + candle
    rrect(c, 120, 360, 220, 170, 6, '#b08a4a', 6); c.fillStyle = '#4a6a5a'; c.fillRect(140, 380, 180, 130); poly(c, [[140, 510], [210, 430], [260, 470], [320, 410], [320, 510]], '#2a4a3a');
    rrect(c, 80, 900, 230, 24, 4, '#5a3a24', 4); rrect(c, 120, 924, 20, 520, 4, '#4a2e1c', 3); rrect(c, 250, 924, 20, 520, 4, '#4a2e1c', 3);
    rrect(c, 140, 820, 70, 80, 14, '#e8e0d0', 4); ell(c, 240, 880, 50, 20, '#d8d0c0', 4);
    SETS.bedroom = { bg: b.c };
  }
  // ---------- 3. close-up brick wall + sash window (exterior)
  {
    const b = mk(W, H), c = b.x;
    bricks(c, 0, 0, W, H, '#8a4a32', 77, 120, 50);
    c.fillStyle = lg(c, 0, 0, W, H, [[0, 'rgba(20,30,70,0.35)'], [1, 'rgba(255,150,90,0.12)']]); c.fillRect(0, 0, W, H);
    rrect(c, 170, 420, 740, 980, 10, '#1e1a1a');
    SETS.wallwin = { bg: b.c };
  }
  // ---------- 4. terrace facade (front, 2 storeys, windows animate per shot)
  {
    const b = mk(W, H), c = b.x;
    sky(c, W, 520, [[0, '#2a3a6a'], [1, '#e09a70']]);
    bricks(c, 0, 300, W, H - 300, '#8a4a32', 41, 64, 28);
    slateRoof(c, [[-20, 300], [120, 140], [960, 140], [1100, 300]], '#3a4258', 4);
    chimney(c, 200, 30, 80, 120, '#7a3a2a', 5); chimney(c, 760, 40, 80, 110, '#7a3a2a', 6);
    rrect(c, 0, 1100, W, 24, 0, '#a8a090', 4);
    cobbles(c, 0, 1700, W, 220, '#5a5e6a', 2);
    rrect(c, 430, 1350, 220, 350, 8, '#2e4a3a', 5); ell(c, 610, 1520, 7, 7, '#d8b060');
    SETS.facade = { bg: b.c };
  }
  // ---------- 5. factory gate street
  {
    const b = mk(W, H), c = b.x;
    sky(c, W, H, [[0, '#3a4a7a'], [.45, '#e08a5a'], [.6, '#f6c27a']]);
    glow(c, 540, 1000, 600, 'rgba(255,200,120,0.4)');
    millChimney(c, 820, 1250, 1050, '#4a2a24'); bricks(c, 120, 600, 840, 650, '#7a3a2a', 88, 50, 22);
    c.lineWidth = 5; c.strokeStyle = INK; c.strokeRect(120, 600, 840, 650);
    poly(c, [[100, 600], [540, 420], [980, 600]], '#3a3a4a', 5);
    for (let i = 0; i < 6; i++) { rrect(c, 170 + i * 130, 680, 80, 120, 40, '#ffc870', 4); glow(c, 210 + i * 130, 740, 120, 'rgba(255,190,90,0.3)'); }
    rrect(c, 380, 900, 320, 350, 160, '#1e1410', 6);
    c.fillStyle = '#e8dcc0'; c.font = '700 54px Cinzel'; c.textAlign = 'center'; c.fillText('MILL', 540, 880);
    cobbles(c, 0, 1250, W, 670, '#5a5e6a', 17);
    SETS.factory = { bg: b.c };
  }
  // ---------- 6. palace great hall (one-point perspective)
  {
    const b = mk(W, H), c = b.x, vx = 540, vy = 820;
    c.fillStyle = lg(c, 0, 0, 0, H, [[0, '#7a1a2a'], [.5, '#b02a34'], [1, '#5a1018']]); c.fillRect(0, 0, W, H);
    // back wall + throne window
    rrect(c, 300, 300, 480, 700, 0, '#8a2028', 5);
    rrect(c, 420, 340, 240, 360, 120, '#f6d690', 6); glow(c, 540, 520, 420, 'rgba(255,220,140,0.55)');
    for (let i = 1; i < 4; i++) line(c, [[420 + i * 60, 360], [420 + i * 60, 700]], 4, '#a8803a');
    // floor checker in perspective
    for (let j = 0; j < 14; j++) for (let i = -10; i < 10; i++) {
      const y0 = 1000 + Math.pow(j / 14, 1.6) * 920, y1 = 1000 + Math.pow((j + 1) / 14, 1.6) * 920;
      const k0 = (y0 - vy) / (H - vy), k1 = (y1 - vy) / (H - vy);
      const x00 = vx + i * 140 * k0 * 1.6, x01 = vx + (i + 1) * 140 * k0 * 1.6, x10 = vx + i * 140 * k1 * 1.6, x11 = vx + (i + 1) * 140 * k1 * 1.6;
      poly(c, [[x00, y0], [x01, y0], [x11, y1], [x10, y1]], (i + j) % 2 ? '#e8dcc4' : '#3a2a28');
    }
    // red carpet
    poly(c, [[470, 1000], [610, 1000], [900, H], [180, H]], '#b0202c'); poly(c, [[470, 1000], [490, 1000], [230, H], [180, H]], '#f0c040'); poly(c, [[590, 1000], [610, 1000], [900, H], [850, H]], '#f0c040');
    // columns + banners
    for (const s of [-1, 1]) for (let k = 0; k < 3; k++) {
      const d = [.45, .7, 1.0][k], x = vx + s * (300 + k * 120) * d * 1.1, top = 1000 - 900 * d * .9, bot = 1000 + 460 * (d - .45) * 1.9;
      rrect(c, x - 40 * d, top, 80 * d, bot - top, 6, '#d8c8a8', 4);
      c.fillStyle = lg(c, x - 40 * d, 0, x + 40 * d, 0, [[0, 'rgba(0,0,0,0.35)'], [.5, 'rgba(255,255,255,0.15)'], [1, 'rgba(0,0,0,0.35)']]); c.fillRect(x - 40 * d, top, 80 * d, bot - top);
      rrect(c, x - 55 * d, top - 20 * d, 110 * d, 30 * d, 4, '#c8b088', 3);
      const bx = x + s * -70 * d;
      poly(c, [[bx - 50 * d, top + 60 * d], [bx + 50 * d, top + 60 * d], [bx + 50 * d, top + 460 * d], [bx, top + 400 * d], [bx - 50 * d, top + 460 * d]], '#b0202c', 3);
      ell(c, bx, top + 220 * d, 32 * d, 32 * d, '#f0c040', 3); ell(c, bx, top + 220 * d, 18 * d, 18 * d, '#b0202c'); ell(c, bx, top + 220 * d, 8 * d, 8 * d, '#f0c040');
    }
    // chandeliers
    for (const [x, y, s] of [[300, 220, 1], [780, 220, 1], [540, 120, 1.3]]) { line(c, [[x, 0], [x, y]], 3, '#a8803a'); ell(c, x, y, 70 * s, 18 * s, '#c8a040', 3); for (let i = -2; i <= 2; i++) { ell(c, x + i * 28 * s, y - 20 * s, 5, 12, '#fff4d0'); glow(c, x + i * 28 * s, y - 30 * s, 50, 'rgba(255,200,110,0.5)'); } }
    SETS.hall = { bg: b.c };
    // big doors (separate layer, two leaves)
    const d = mk(540, 1300), dc = d.x;
    rrect(dc, 10, 10, 520, 1280, 20, '#5a3018', 8);
    for (let i = 0; i < 3; i++) for (let j = 0; j < 2; j++) rrect(dc, 50 + j * 230, 60 + i * 400, 210, 360, 12, '#6e3c20', 5);
    for (let i = 0; i < 8; i++) { ell(dc, 40, 100 + i * 150, 10, 10, '#f0c040', 3); ell(dc, 500, 100 + i * 150, 10, 10, '#f0c040', 3); }
    ell(dc, 470, 650, 30, 30, '#f0c040', 5); ell(dc, 470, 650, 16, 16, '#5a3018', 4);
    SETS.door = d.c;
  }
  // ---------- 7. privy chamber
  {
    const b = mk(W, H), c = b.x;
    c.fillStyle = '#3a1a14'; c.fillRect(0, 0, W, H);
    // linenfold panelling
    for (let i = 0; i < 6; i++) for (let j = 0; j < 4; j++) { rrect(c, 20 + i * 178, 760 + j * 240, 160, 220, 6, '#6a3a20', 4); for (let k = 0; k < 4; k++) curve(c, [[50 + i * 178 + k * 30, 790 + j * 240], [44 + i * 178 + k * 30, 870 + j * 240], [56 + i * 178 + k * 30, 950 + j * 240]], 4, 'rgba(0,0,0,0.3)'); }
    // tapestry
    rrect(c, 90, 120, 900, 600, 8, '#2a4a3a', 6);
    for (let i = 0; i < 40; i++) { const r = rng(i); ell(c, 120 + r() * 840, 150 + r() * 540, 10 + r() * 30, 10 + r() * 30, rgba(['#c8a040', '#a8303a', '#6a8a4a'][i % 3], .5)); }
    blob(c, [[300, 640], [380, 400], [460, 380], [540, 300], [620, 380], [700, 400], [780, 640]], '#3a5a40'); ell(c, 540, 300, 60, 60, '#c8a040');
    c.fillStyle = '#c8a040'; c.font = '900 64px CinzelD'; c.textAlign = 'center'; c.fillText('H', 540, 560);
    rrect(c, 70, 100, 940, 30, 6, '#c8a040', 4);
    curtainDrape(c, -20, 60, 260, 1300, '#6a1020', 0); curtainDrape(c, 840, 60, 260, 1300, '#6a1020', 0);
    // dais
    rrect(c, 200, 1520, 680, 60, 10, '#8a1a24', 5); rrect(c, 160, 1580, 760, 340, 0, '#4a2010', 5);
    for (let i = 0; i < 12; i++) ell(c, 210 + i * 60, 1550, 8, 8, '#f0c040', 3);
    SETS.privy = { bg: b.c };
  }
  // ---------- 8. dusk village (wide for panning)
  {
    const w = 1800;
    const s = mk(W, H); sky(s.x, W, H, [[0, '#1a1a4a'], [.35, '#3a3a8a'], [.58, '#8a5aa0'], [.7, '#f0906a'], [.76, '#ffb87a']], 180, 8);
    ell(s.x, 760, 560, 140, 140, '#f6ecd2'); glow(s.x, 760, 560, 520, 'rgba(240,230,255,0.3)');
    ell(s.x, 730, 530, 30, 22, 'rgba(200,190,170,0.4)'); ell(s.x, 800, 610, 20, 16, 'rgba(200,190,170,0.35)');
    const far = mk(w, H); blob(far.x, [[0, 1250], [300, 1080], [700, 1150], [1100, 1040], [1500, 1120], [1800, 1060], [1800, 1400], [0, 1400]], '#3a3a6a');
    for (let i = 0; i < 14; i++) tree(far.x, 60 + i * 130, 1180 + Math.sin(i) * 30, 260 + (i % 3) * 60, '#1c1630', 40 + i);
    const mid = mk(w, H);
    church(mid.x, 1180, 1440, .95, '#6a6478', '#2a2438', true);
    cottage(mid.x, 80, 1440, 360, 300, '#7a7060', '#5a4a2a', 31, true);
    cottage(mid.x, 520, 1440, 300, 260, '#6a6458', '#4a3e26', 32, false);
    cottage(mid.x, 1500, 1440, 280, 250, '#6a6458', '#4a3e26', 33, true);
    tree(mid.x, 900, 1440, 520, '#1a1426', 51); tree(mid.x, 1700, 1440, 460, '#1a1426', 52);
    for (let i = 0; i < 10; i++) { rrect(mid.x, 1350 + i * 30, 1380 - (i % 2) * 10, 14, 60, 6, '#4a4458', 2); }
    const ground = mk(w, H - 1440); ground.x.fillStyle = lg(ground.x, 0, 0, 0, H - 1440, [[0, '#4a4a6a'], [1, '#2a2840']]); ground.x.fillRect(0, 0, w, H - 1440);
    curve(ground.x, [[0, 120], [600, 80], [1200, 140], [1800, 90]], 160, 'rgba(120,110,120,0.35)');
    SETS.village = { sky: s.c, far: far.c, mid: mid.c, ground: ground.c, w, gy: 1440 };
  }
  // ---------- 9. cottage interior (wake room)
  {
    const b = mk(W, H), c = b.x;
    stones(c, 0, 0, W, H, '#6a5a60', 61, 70);
    c.fillStyle = 'rgba(40,20,40,0.25)'; c.fillRect(0, 0, W, H);
    rrect(c, 700, 300, 220, 260, 110, '#1a2040', 6); ell(c, 810, 400, 50, 50, '#f6ecd2'); glow(c, 810, 400, 300, 'rgba(200,210,255,0.25)');
    line(c, [[810, 300], [810, 560]], 8, '#3a2a20'); line(c, [[700, 430], [920, 430]], 8, '#3a2a20');
    for (let i = 0; i < 4; i++) rrect(c, -10, 120 + i * 18, W + 20, 0, 0);
    rrect(c, 0, 80, W, 50, 0, '#2a1c14', 5); rrect(c, 0, 1500, W, 420, 0, '#2a1e18');
    for (let i = 0; i < 8; i++) line(c, [[0, 1520 + i * 60], [W, 1520 + i * 60]], 3, 'rgba(0,0,0,0.35)');
    SETS.cottageIn = { bg: b.c };
  }
  // ---------- 10. moon hill
  {
    const b = mk(W, H), c = b.x;
    sky(c, W, H, [[0, '#0a0a1e'], [.5, '#1e1e40'], [1, '#2a2440']], 260, 12);
    ell(c, 540, 900, 380, 380, '#f2ead6'); glow(c, 540, 900, 900, 'rgba(230,230,255,0.25)');
    for (const [x, y, r] of [[460, 820, 60], [640, 980, 40], [580, 760, 26], [420, 1000, 30]]) ell(c, x, y, r, r * .8, 'rgba(190,180,160,0.35)');
    blob(c, [[0, 1350], [300, 1260], [540, 1230], [800, 1270], [1080, 1330], [1080, H], [0, H]], '#0c0a14');
    tree(c, 900, 1290, 420, '#0c0a14', 5); tree(c, 140, 1330, 330, '#0c0a14', 6);
    for (let i = 0; i < 8; i++) line(c, [[650 + i * 50, 1270 + i * 6], [650 + i * 50, 1210 + i * 6]], 6, '#0c0a14');
    line(c, [[640, 1240], [1040, 1290]], 5, '#0c0a14');
    SETS.moon = { bg: b.c };
  }
  // ---------- 11. theatre stage (opening + finale)
  {
    const b = mk(W, H), c = b.x;
    c.fillStyle = '#1a0a12'; c.fillRect(0, 0, W, H);
    // painted backdrop: three worlds blending
    const bd = (x, w, stops) => { c.fillStyle = lg(c, 0, 220, 0, 1300, stops); c.fillRect(x, 220, w, 1080); };
    bd(60, 320, [[0, '#2a3a6a'], [1, '#e09a70']]); bd(380, 320, [[0, '#6a1a24'], [1, '#e8b860']]); bd(700, 320, [[0, '#1e1838'], [1, '#6a4a7a']]);
    terrace(c, 60, 1300, 1, 5, { hw: 320, hh: 560, litP: 1 });
    for (const x of [430, 640]) { rrect(c, x, 520, 60, 780, 6, '#d8c8a8', 4); }
    rrect(c, 470, 420, 160, 300, 80, '#f6d690', 5); glow(c, 550, 560, 260, 'rgba(255,220,140,0.5)');
    poly(c, [[380, 1300], [700, 1300], [600, 1100], [480, 1100]], '#b0202c');
    church(c, 880, 1300, .55, '#6a6478', '#2a2438', true);
    ell(c, 960, 380, 60, 60, '#f6ecd2');
    // blending fog between panels
    for (const x of [380, 700]) { c.fillStyle = lg(c, x - 80, 0, x + 80, 0, [[0, 'rgba(26,10,18,0)'], [.5, 'rgba(26,10,18,0.55)'], [1, 'rgba(26,10,18,0)']]); c.fillRect(x - 80, 220, 160, 1080); }
    // stage floor
    c.fillStyle = lg(c, 0, 1300, 0, H, [[0, '#6a3a1e'], [1, '#2a160c']]); c.fillRect(0, 1300, W, 620);
    for (let i = 0; i < 16; i++) line(c, [[540 + (i - 8) * 40, 1300], [540 + (i - 8) * 150, H]], 3, 'rgba(0,0,0,0.35)');
    for (let j = 0; j < 6; j++) line(c, [[0, 1300 + Math.pow(j / 6, 1.5) * 620], [W, 1300 + Math.pow(j / 6, 1.5) * 620]], 2, 'rgba(0,0,0,0.25)');
    rrect(c, 0, 1290, W, 20, 0, '#c8a040', 3);
    SETS.stage = { bg: b.c };
    // proscenium curtains (foreground layer)
    const f = mk(W, H), fc = f.x;
    curtainDrape(fc, -20, 0, 200, 1500, '#9a1424', 1); curtainDrape(fc, 900, 0, 200, 1500, '#9a1424', 1);
    curtainDrape(fc, -20, 0, W + 40, 240, '#8a1020', 1);
    for (let i = 0; i < 12; i++) poly(fc, [[i * 95, 230], [i * 95 + 47, 300], [i * 95 + 95, 230]], '#c8a040', 3);
    SETS.prosc = f.c;
  }
}
