// ===================================================================== style2.js
// Reference-matched presentation: ornamental bands, navy caption plates, slab lettering, job counter.
'use strict';
const BAND_TOP = 150, BAND_BOT = 1590, BAND_H = 64;
const THEMES = {
  knocker: { band: '#1d2b5c', trim: '#f0b83a', icon: '#f6d27a' },
  groom: { band: '#6a0f1e', trim: '#f0c040', icon: '#ffe08a' },
  sin: { band: '#1c1838', trim: '#b8a0e0', icon: '#d8c8ff' },
  stage: { band: '#3a1030', trim: '#f0c040', icon: '#ffe08a' },
};
function motif(c, kind, x, y, s, col) {
  c.save(); c.translate(x, y); c.strokeStyle = col; c.fillStyle = col; c.lineWidth = 3.2; sk(c);
  if (kind === 0) { c.beginPath(); c.arc(0, 0, s * .42, 0, TAU); c.stroke(); for (let i = 0; i < 8; i++) { const a = i / 8 * TAU; line(c, [[Math.cos(a) * s * .42, Math.sin(a) * s * .42], [Math.cos(a) * s * .58, Math.sin(a) * s * .58]], 4, col); } ell(c, 0, 0, s * .12, s * .12, col); }   // cog
  else if (kind === 1) { c.beginPath(); c.arc(0, 0, s * .38, 0, TAU); c.stroke(); line(c, [[0, 0], [0, -s * .26]], 3, col); line(c, [[0, 0], [s * .18, 0]], 3, col); }     // clock
  else if (kind === 2) { line(c, [[-s * .4, s * .4], [s * .4, -s * .4]], 4, col); c.beginPath(); c.arc(s * .4, -s * .4, s * .08, 0, TAU); c.fill(); }                           // pole
  else if (kind === 3) { for (let i = 0; i < 5; i++) { const a = i / 5 * TAU; ell(c, Math.cos(a) * s * .2, Math.sin(a) * s * .2, s * .16, s * .16, col); } ell(c, 0, 0, s * .1, s * .1, '#c8203a'); }   // rose
  else if (kind === 4) { poly(c, [[-s * .4, s * .25], [-s * .4, -s * .2], [-s * .2, 0], [0, -s * .35], [s * .2, 0], [s * .4, -s * .2], [s * .4, s * .25]], col); }         // crown
  else if (kind === 5) { c.beginPath(); c.ellipse(0, 0, s * .4, s * .16, .8, 0, TAU); c.stroke(); c.beginPath(); c.ellipse(0, 0, s * .4, s * .16, -.8, 0, TAU); c.stroke(); }   // knot
  else if (kind === 6) { rrect(c, -s * .08, -s * .1, s * .16, s * .4, 3, col); c.beginPath(); c.moveTo(0, -s * .4); c.quadraticCurveTo(s * .12, -s * .2, 0, -s * .12); c.quadraticCurveTo(-s * .12, -s * .2, 0, -s * .4); c.fill(); }   // candle
  else { poly(c, [[0, -s * .35], [s * .3, s * .25], [-s * .3, s * .25]], null, 3, col); }
  c.restore();
}
function band(c, y, theme, t, flip = false) {
  const T = THEMES[theme];
  c.save();
  c.fillStyle = T.band; c.fillRect(0, y, W, BAND_H);
  c.fillStyle = T.trim; c.fillRect(0, y + 6, W, 4); c.fillRect(0, y + BAND_H - 10, W, 4);
  c.fillStyle = 'rgba(0,0,0,0.35)'; c.fillRect(0, y + BAND_H, W, 8);
  const kinds = theme === 'knocker' ? [0, 1, 2] : theme === 'groom' ? [3, 4, 3] : theme === 'sin' ? [5, 6, 7] : [0, 3, 6, 2, 4, 5];
  const off = (t * 22) % 72 * (flip ? -1 : 1);
  for (let i = -2; i < 17; i++) motif(c, kinds[(i + 40) % kinds.length], i * 72 + off, y + BAND_H / 2, 40, T.icon);
  c.restore();
}
function counter(c, active, theme, t) {
  const T = THEMES[theme];
  for (let i = 0; i < 3; i++) {
    const x = 450 + i * 90, y = 262, on = i + 1 === active, done = i + 1 < active;
    const pop = on ? 1 + .12 * Math.sin(t * 6) : 1;
    ell(c, x, y, 30 * pop, 30 * pop, on ? '#c8283a' : done ? '#e8b440' : '#1d2240', 4, 0, '#f0c040');
    c.font = '30px Slab'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillStyle = '#fff3d6'; c.fillText(String(i + 1), x, y + 2);
  }
}
// caption: each line on its own navy pill (like the reference)
function caption(c, t, txt, t0, t1, o = {}) {
  if (t < t0 - .01 || t > t1 + .22) return;
  const k = clamp((t - t0) / .3), out = clamp((t - t1) / .22);
  const lines = txt.split('\n'), size = o.size || 64, y0 = o.y || 350;
  c.save(); c.globalAlpha = 1 - out;
  lines.forEach((ln, i) => {
    const kk = clamp((t - t0 - i * .06) / .3), s = E.back(kk);
    const plain = ln.replace(/\*/g, '');
    c.font = `${size}px Slab`; const w = c.measureText(plain).width;
    const y = y0 + i * size * 1.22;
    c.save(); c.translate(540, y); c.scale(s, s);
    const pw = w + size * .9, ph = size * 1.14;
    c.fillStyle = 'rgba(0,0,0,0.35)'; c.beginPath(); c.roundRect(-pw / 2 + 6, -ph / 2 + 8, pw, ph, ph / 2); c.fill();
    c.fillStyle = '#16204a'; c.beginPath(); c.roundRect(-pw / 2, -ph / 2, pw, ph, ph / 2); c.fill();
    c.lineWidth = 5; c.strokeStyle = '#e8b440'; c.stroke();
    c.fillStyle = '#e8b440'; c.fillRect(pw / 2 - 10, -ph / 2 + 8, 6, ph - 16);
    // words
    const parts = ln.split(/(\*[^*]+\*)/).filter(Boolean);
    let x = -w / 2; c.textBaseline = 'middle'; c.textAlign = 'left';
    for (const p of parts) { const em = p.startsWith('*'), s2 = p.replace(/\*/g, ''); c.fillStyle = em ? '#ffd23c' : '#fff3d6'; c.fillText(s2, x, size * .06); x += c.measureText(s2).width; }
    c.restore();
  });
  c.restore();
}
function chapter2(c, t, num, title, t0, t1, theme) {
  if (t < t0 || t > t1 + .25) return;
  const k = t - t0, out = clamp((t - t1) / .25);
  c.save(); c.globalAlpha = 1 - out;
  const s = E.back(clamp(k / .35));
  c.save(); c.translate(540, 360); c.scale(s, s);
  const fs = fitFont(c, title, '$px Slab', 84, 780); c.font = `${fs}px Slab`; const w = c.measureText(title).width + 150;
  c.fillStyle = '#16204a'; c.beginPath(); c.roundRect(-w / 2, -64, w, 128, 64); c.fill(); c.lineWidth = 6; c.strokeStyle = '#e8b440'; c.stroke();
  ell(c, -w / 2 + 64, 0, 50, 50, '#c8283a', 5, 0, '#f0c040');
  c.fillStyle = '#fff3d6'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.font = '62px Slab'; c.fillText(num, -w / 2 + 64, 4);
  c.font = `${fs}px Slab`; c.fillStyle = '#ffd23c'; c.fillText(title, 40, 6);
  c.restore(); c.restore();
}
function popWord(c, t, word, t0, x, y, size = 130, col = '#ffd23c', rot = -.08) {
  if (t < t0 || t > t0 + .55) return;
  const k = E.back(clamp((t - t0) / .14)), a = 1 - clamp((t - t0 - .4) / .15);
  c.save(); c.translate(x, y); c.rotate(rot); c.scale(k, k); c.globalAlpha = a;
  c.font = `${size}px Slab`; c.textAlign = 'center'; c.textBaseline = 'middle'; c.lineJoin = 'round';
  c.lineWidth = size * .22; c.strokeStyle = '#16204a'; c.strokeText(word, 0, 0); c.fillStyle = col; c.fillText(word, 0, 0);
  c.restore();
}
