// sets: reusable sets carried over from V1 (council chamber, the dusk river, water, hills, Hamelin's skyline)
'use strict';
const C = require('./core');
const E = require('./env');
const K = require('./ink');
const { clamp, lerp, TAU, hash, W, H } = C;
const { PAL } = K;

function councilRoom(g, t, o = {}) {
  // panelled walls, leaded arched window, red banner with Hamelin's millwheel, candles
  g.fillStyle = '#e3d2ae'; g.fillRect(0, 0, W, H);
  g.fillStyle = 'rgba(80,50,25,.12)'; for (let i = 0; i < 8; i++) g.fillRect(0, i * 240 + 120, W, 4);
  K.shape(g, [[0, 1080], [W, 1080], [W, 1200], [0, 1200]], { fill: '#6b4428', lw: 5, smooth: false });
  for (let i = 0; i < 6; i++) K.shape(g, [[20 + i * 180, 1110], [180 + i * 180, 1110], [180 + i * 180, 1180], [20 + i * 180, 1180]], { fill: '#7b5233', lw: 3.5, smooth: false });
  // window
  const wx = 110, wy = 230, ww = 300, wh = 560;
  const P = [[wx, wy + wh], [wx, wy + ww / 2]]; for (let i = 0; i <= 10; i++) { const a = Math.PI + Math.PI * i / 10; P.push([wx + ww / 2 + Math.cos(a) * ww / 2, wy + ww / 2 + Math.sin(a) * ww / 2]); } P.push([wx + ww, wy + wh]);
  K.shape(g, P, { fill: o.night ? '#33406a' : '#fbf1d6', lw: 6, smooth: false, inner: g2 => { g2.strokeStyle = 'rgba(70,60,50,.55)'; g2.lineWidth = 3; for (let i = -600; i < 600; i += 46) { g2.beginPath(); g2.moveTo(wx + i, wy); g2.lineTo(wx + i + 700, wy + 700); g2.stroke(); g2.beginPath(); g2.moveTo(wx + i + 700, wy); g2.lineTo(wx + i, wy + 700); g2.stroke(); } } });
  K.line(g, [[wx + ww / 2, wy], [wx + ww / 2, wy + wh]], 8, PAL.ink, 1, false);
  K.shape(g, [[wx - 20, wy + wh], [wx + ww + 20, wy + wh], [wx + ww + 20, wy + wh + 22], [wx - 20, wy + wh + 22]], { fill: '#b9a98a', lw: 5, smooth: false });
  if (!o.night) E.addLight(g, wx + ww / 2, wy + wh / 2, 520, '#fff0c8', .35);
  // banner
  const bx = 560, by = 150;
  K.line(g, [[bx - 30, by], [bx + 330, by]], 10, '#3a2418', 1, false);
  K.shape(g, [[bx, by], [bx + 300, by], [bx + 300, by + 520], [bx + 150, by + 600], [bx, by + 520]], { fill: '#9a2a25', lw: 6, smooth: false, inner: g2 => { g2.strokeStyle = '#d6a845'; g2.lineWidth = 5; g2.strokeRect(bx + 14, by + 14, 272, 480); } });
  K.shape(g, [[bx + 60, by + 120], [bx + 240, by + 120], [bx + 240, by + 300], [bx + 150, by + 400], [bx + 60, by + 300]], { fill: '#efe6d2', lw: 5, tension: .3 });
  g.save(); g.translate(bx + 150, by + 245); for (let i = 0; i < 8; i++) { g.rotate(Math.PI / 4); K.line(g, [[0, 0], [0, 60]], 8, '#9a2a25', 1, false); } K.ellipse(g, 0, 0, 62, 62, { fill: null, lw: 0 }); g.strokeStyle = '#9a2a25'; g.lineWidth = 10; g.beginPath(); g.arc(0, 0, 58, 0, TAU); g.stroke(); g.restore();
  // candle sconce
  K.shape(g, [[960, 620], [990, 620], [990, 760], [960, 760]], { fill: '#2a2420', lw: 4, smooth: false });
  K.shape(g, [[965, 520], [985, 520], [985, 620], [965, 620]], { fill: '#efe6d2', lw: 3.5, smooth: false });
  K.shape(g, [[975, 470 + Math.sin(t * 11) * 4], [985, 505], [975, 520], [965, 505]], { fill: '#f6c24a', lw: 2.5 });
  E.addLight(g, 975, 500, 260, '#f3a64a', .45);
}

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

module.exports = { councilRoom, duskSky, hills, hamelinSilhouette, water };
