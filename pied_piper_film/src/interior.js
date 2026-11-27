// interior: a child's bedroom at night (moonlit window, bed, toys) -- used for the reactions and the empty beds
'use strict';
const C = require('./core');
const K = require('./ink');
const E = require('./env');
const { clamp, lerp, TAU, hash, W, H } = C;
const { PAL, INK } = K;

function bedroom(g, t, o = {}) {
  // walls: plaster above, timber beams, plank floor
  g.fillStyle = '#d9c7a4'; g.fillRect(0, 0, W, 1250);
  for (const x of [120, 560, 1000]) K.shape(g, [[x - 14, 0], [x + 14, 0], [x + 14, 1250], [x - 14, 1250]], { fill: PAL.beam, lw: 5, smooth: false });
  K.shape(g, [[0, 300], [W, 300], [W, 330], [0, 330]], { fill: PAL.beam, lw: 5, smooth: false });
  K.shape(g, [[-20, 1250], [W + 20, 1250], [W + 20, H + 20], [-20, H + 20]], { fill: '#8a6342', lw: 5, smooth: false, inner: g2 => { g2.strokeStyle = 'rgba(40,20,10,.4)'; g2.lineWidth = 3; for (let y = 1250; y < H; y += 70) { g2.beginPath(); g2.moveTo(0, y); g2.lineTo(W, y); g2.stroke(); } for (let i = 0; i < 30; i++) { const y = 1250 + Math.floor(i / 5) * 70, x = (i % 5) * 230 + (Math.floor(i / 5) % 2) * 110; g2.beginPath(); g2.moveTo(x, y); g2.lineTo(x, y + 70); g2.stroke(); } } });
  // window (left), moonlit, with a light shaft across the floor
  const wx = o.winX ?? 200, wy = 480, ww = 260, wh = 380;
  K.shape(g, [[wx, wy], [wx + ww, wy], [wx + ww, wy + wh], [wx, wy + wh]], { fill: '#33416e', lw: 6, smooth: false, inner: g2 => { g2.fillStyle = '#f3ead2'; g2.beginPath(); g2.arc(wx + ww * .7, wy + 110, 46, 0, TAU); g2.fill(); g2.strokeStyle = 'rgba(30,30,40,.7)'; g2.lineWidth = 4; for (let i = -400; i < 400; i += 44) { g2.beginPath(); g2.moveTo(wx + i, wy); g2.lineTo(wx + i + 500, wy + 500); g2.stroke(); g2.beginPath(); g2.moveTo(wx + i + 500, wy); g2.lineTo(wx + i, wy + 500); g2.stroke(); } } });
  K.shape(g, [[wx - 18, wy + wh], [wx + ww + 18, wy + wh], [wx + ww + 18, wy + wh + 24], [wx - 18, wy + wh + 24]], { fill: '#b9a98a', lw: 5, smooth: false });
  // open shutters
  const op = o.shutterOpen ?? 1;
  if (op > 0) for (const sd of [-1, 1]) { const x0 = sd < 0 ? wx - ww * .45 * op : wx + ww; K.shape(g, [[x0, wy], [x0 + ww * .45 * op, wy], [x0 + ww * .45 * op, wy + wh], [x0, wy + wh]], { fill: '#6b4a30', lw: 5, smooth: false }); }
  // light shaft (screen-blended after the grade)
  g.save(); g.globalAlpha = .22; g.fillStyle = '#eef3ff';
  g.beginPath(); g.moveTo(wx, wy); g.lineTo(wx + ww, wy); g.lineTo(wx + ww + 520, 1700); g.lineTo(wx + 260, 1750); g.closePath(); g.fill(); g.restore();
  E.addLight(g, wx + ww / 2, wy + wh / 2, 420, '#9fb4e6', .5);
  // bed (right)
  const bx = o.bedX ?? 560, by = 1380;
  K.shape(g, [[bx, by], [bx + 470, by], [bx + 470, by - 120], [bx, by - 120]], { fill: '#7a5233', lw: 6, smooth: false });
  K.shape(g, [[bx + 430, by - 300], [bx + 490, by - 300], [bx + 490, by + 40], [bx + 430, by + 40]], { fill: '#6b4428', lw: 6, smooth: false });
  K.shape(g, [[bx - 20, by - 240], [bx + 40, by - 240], [bx + 40, by + 40], [bx - 20, by + 40]], { fill: '#6b4428', lw: 6, smooth: false });
  K.ellipse(g, bx + 380, by - 150, 60, 30, { fill: '#efe6d2', lw: 5 });             // pillow
  const empty = o.empty ?? 0;
  // blanket: lumpy (child asleep) or pulled back, flat
  if (empty < .5) K.shape(g, [[bx + 20, by - 120], [bx + 120, by - 190], [bx + 260, by - 200], [bx + 380, by - 180], [bx + 440, by - 130], [bx + 440, by - 100], [bx + 20, by - 100]], { fill: '#53719a', lw: 6, tension: .4, inner: g2 => { g2.strokeStyle = 'rgba(20,30,60,.35)'; g2.lineWidth = 4; for (let i = 0; i < 5; i++) { g2.beginPath(); g2.moveTo(bx + 60 + i * 80, by - 190); g2.lineTo(bx + 80 + i * 80, by - 100); g2.stroke(); } } });
  else {
    K.shape(g, [[bx + 20, by - 120], [bx + 300, by - 130], [bx + 440, by - 122], [bx + 440, by - 100], [bx + 20, by - 100]], { fill: '#efe6d2', lw: 5, tension: .3 });
    K.shape(g, [[bx + 20, by - 120], [bx + 180, by - 150], [bx + 230, by - 120], [bx + 210, by - 40], [bx + 20, by - 60]], { fill: '#53719a', lw: 6, tension: .4 });
  }
}
module.exports = { bedroom };
