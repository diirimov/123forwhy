// topdown: overhead views -- people seen from above, cobbled ground, roof edges
'use strict';
const C = require('./core');
const K = require('./ink');
const { clamp, lerp, TAU, hash } = C;
const { PAL, INK } = K;

// person from above, heading ang (radians, 0 = +x). o: {ch, s, phase (stride phase), lw, sil, wind}
function personTop(g, x, y, ang, o = {}) {
  const ch = o.ch, s = o.s || 1, ph = (o.phase || 0) * TAU;
  const piper = ch.outfit === 'piper', child = ch.body === 'child';
  const k = child ? .72 : piper ? 1.05 : 1;
  const lw = (o.lw ?? 3.2) / s;
  const F = c => o.sil || c;
  g.save(); g.translate(x, y); g.rotate(ang); g.scale(s * k, s * k);
  // shadow
  if (!o.sil) { g.save(); g.globalAlpha *= .25; g.fillStyle = '#100808'; g.beginPath(); g.ellipse(-8, 10, 42, 30, 0, 0, TAU); g.fill(); g.restore(); }
  // feet stepping (front/back alternation)
  for (const sd of [-1, 1]) { const f = Math.sin(ph + (sd > 0 ? 0 : Math.PI)) * 18; K.ellipse(g, f + 6, sd * 12, 12, 6.5, { fill: F(ch.shoe), lw: lw * .8 }); }
  // cloak trailing behind (Piper)
  if (piper) {
    const wv = Math.sin((o.t || 0) * 4) * 6;
    K.shape(g, [[10, -30], [-20, -34], [-70, -30 + wv], [-96, -8 + wv], [-98, 10 - wv], [-70, 32 - wv], [-20, 34], [10, 30]], { fill: F(PAL.purple), lw, tension: .45 });
  }
  // skirt / body
  K.ellipse(g, -2, 0, 26, 34, { fill: F(ch.skirt || ch.top), lw });
  // arms
  for (const sd of [-1, 1]) { const a = Math.sin(ph + (sd > 0 ? Math.PI : 0)) * .5 * (o.armAmt ?? 1); const sh = [0, sd * 30]; const hand = [sh[0] + Math.cos(a) * 30 * (o.armFwd ? 1.3 : 1), sh[1] + sd * 6 + Math.sin(a) * 4]; K.capsule(g, sh, hand, 9, 8, { fill: F(piper ? (sd < 0 ? PAL.burg : PAL.pgreen) : ch.sleeve), lw: lw * .9 }); K.ellipse(g, hand[0] + 4, hand[1], 7, 7, { fill: F(ch.skin), lw: lw * .8 }); }
  // shoulders
  K.ellipse(g, 0, 0, 22, 36, { fill: F(piper ? PAL.burg : (ch.bodice || ch.top)), lw });
  if (o.flute) K.capsule(g, [22, 2], [70, 2], 4, 5, { fill: '#a9764a', lw: lw * .8 });
  // head (hat / hair / coif)
  if (piper) {
    K.ellipse(g, 2, 0, 44, 44, { fill: F(PAL.burgD), lw });
    K.ellipse(g, 0, 0, 24, 24, { fill: F(PAL.burg), lw });
    const sw = Math.sin((o.t || 0) * 3) * 4;
    K.shape(g, [[0, -10], [-30, -30 + sw], [-70, -44 + sw], [-74, -36 + sw], [-34, -20], [-4, -2]], { fill: F('#efe3c6'), lw: lw * .8, tension: .5 });
  } else {
    const hc = (ch.hat === 'coif' || ch.hat === 'hood') ? ch.hatCol : ch.hat === 'beret' ? ch.hatCol : ch.hat === 'straw' ? '#cfae63' : ch.hat === 'helmet' ? '#8e8f93' : ch.hat === 'tophat' ? '#1e1b22' : ch.hairCol;
    const r = ch.hat === 'straw' ? 34 : 19;
    K.ellipse(g, 4, 0, r, r * .95, { fill: F(hc), lw });
    if (ch.hair === 'braids' && !o.sil) for (const sd of [-1, 1]) K.capsule(g, [-6, sd * 10], [-34, sd * 14], 5, 4, { fill: ch.hairCol, lw: lw * .7 });
  }
  g.restore();
}

// top-down cobbles: rounded stones in running bond, scrolled by camera
function cobblesTop(g, x0, y0, x1, y1, o = {}) {
  const sw = o.sw || 70, sh = o.sh || 44;
  const base = o.base || PAL.cobble, gap = o.gap || '#8a7151';
  g.fillStyle = gap; g.fillRect(x0, y0, x1 - x0, y1 - y0);
  const r0 = Math.floor(y0 / sh), r1 = Math.ceil(y1 / sh);
  for (let r = r0; r <= r1; r++) {
    const off = (r % 2) * sw / 2;
    const c0 = Math.floor((x0 - off) / sw) - 1, c1 = Math.ceil((x1 - off) / sw) + 1;
    for (let c = c0; c <= c1; c++) {
      const k = hash(c * 13.1 + r * 7.7);
      g.fillStyle = K.cmix(base, k > .5 ? '#fff4de' : '#2a1a10', Math.abs(k - .5) * .22);
      g.beginPath(); g.roundRect(c * sw + off + 3, r * sh + 3, sw - 6, sh - 6, 14); g.fill();
      g.lineWidth = 2.4; g.strokeStyle = K.rgba(INK, .55); g.stroke();
    }
  }
}
// roofs seen from above along a street edge (side = -1 left, 1 right)
function roofsTop(g, x, y0, y1, side, o = {}) {
  const w = o.w || 380; let y = y0; let i = 0;
  while (y < y1) {
    const h = 260 + hash(i * 3 + (o.seed || 0)) * 180;
    const col = [PAL.roof, '#7c4030', '#93513a', '#6e3a2b'][Math.floor(hash(i * 7 + (o.seed || 0)) * 4)];
    const xa = side < 0 ? x - w : x, xb = side < 0 ? x : x + w;
    K.shape(g, [[xa, y], [xb, y], [xb, y + h], [xa, y + h]], { fill: col, lw: 5, smooth: false, inner: (g2) => {
      g2.strokeStyle = 'rgba(40,20,10,.35)'; g2.lineWidth = 3; for (let yy = y + 18; yy < y + h; yy += 18) { g2.beginPath(); g2.moveTo(xa, yy); g2.lineTo(xb, yy); g2.stroke(); }
      g2.fillStyle = 'rgba(25,10,5,.25)'; g2.fillRect(side < 0 ? xa : (xa + xb) / 2, y, w / 2, h);
    } });
    K.line(g, [[(xa + xb) / 2, y], [(xa + xb) / 2, y + h]], 5, INK, 1, false);
    if (hash(i * 11) < .6) K.shape(g, [[(xa + xb) / 2 + 30, y + 40], [(xa + xb) / 2 + 70, y + 40], [(xa + xb) / 2 + 70, y + 80], [(xa + xb) / 2 + 30, y + 80]], { fill: '#8b5a45', lw: 4, smooth: false });
    y += h + 8; i++;
  }
}
module.exports = { personTop, cobblesTop, roofsTop };
