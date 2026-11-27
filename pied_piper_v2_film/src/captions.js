// captions: the studio's typography. Safe zone for TikTok/Reels UI: x 80..960, y 230..1450 (we use 300..720 mostly)
'use strict';
const path = require('path');
const { GlobalFonts } = require('@napi-rs/canvas');
const C = require('./core');
const K = require('./ink');
const { clamp, lerp, ease, W, H } = C;

const FD = path.join(C.ROOT, 'assets/fonts');
for (const f of require('fs').readdirSync(FD)) GlobalFonts.registerFromPath(path.join(FD, f));
const FELL = GlobalFonts.families.map(f => f.family).find(f => /FELL English$/i.test(f) || /IM FELL English(?! SC)/i.test(f)) || 'IM FELL English';
const FELLSC = GlobalFonts.families.map(f => f.family).find(f => /SC/i.test(f) && /FELL/i.test(f)) || 'IM FELL English SC';

const YEL = '#f3b847';

function wrapWords(g, words, maxW) {
  const lines = [[]]; let cur = 0;
  for (const w of words) {
    const ww = g.measureText(w.text + ' ').width;
    if (cur + ww > maxW && lines[lines.length - 1].length) { lines.push([]); cur = 0; }
    lines[lines.length - 1].push(w); cur += ww;
  }
  return lines;
}

// story caption: words pop in (scale overshoot) at given times; o: {t0, t1, y, size, times[], hl:Set(words)}
function storyCaption(g, text, t, o) {
  const { t0, t1 } = o;
  if (t < t0 - .01 || t > t1 + .25) return;
  const size = o.size || 74;
  g.save();
  g.font = `${size}px "Luckiest Guy"`; g.textBaseline = 'alphabetic';
  const words = text.split(' ').map((w, i) => ({ text: w, i, at: o.times ? (o.times[i] ?? o.times[o.times.length - 1]) : t0 + i * (o.step || .11) }));
  const lines = wrapWords(g, words, o.maxW || 880);
  const lh = size * 1.12;
  const out = clamp((t - t1) / .25); // exit
  let y = (o.y || 420) - (lines.length - 1) * lh / 2;
  for (const L of lines) {
    const widths = L.map(w => g.measureText(w.text).width); const sp = size * .28;
    const total = widths.reduce((a, b) => a + b, 0) + sp * (L.length - 1);
    let x = W / 2 - total / 2;
    L.forEach((w, j) => {
      const u = clamp((t - w.at) / .22);
      if (u <= 0) { x += widths[j] + sp; return; }
      const sc = (0.4 + .6 * ease.back(u)) * (1 - out * .3);
      const cx = x + widths[j] / 2;
      g.save(); g.translate(cx, y - size * .35); g.scale(sc, sc); g.rotate((1 - u) * (j % 2 ? .08 : -.08));
      g.globalAlpha = clamp(u * 3) * (1 - out);
      const hl = o.hl && o.hl.has(w.text.replace(/[.,]/g, ''));
      K.outlinedText(g, w.text, 0, size * .35, { font: `${size}px "Luckiest Guy"`, fill: hl ? YEL : '#fbf4e6', lw: size * .2, ink: '#1b0f08', shadow: size * .06 });
      g.restore();
      x += widths[j] + sp;
    });
    y += lh;
  }
  g.restore();
}

// engraved title (Cinzel Decorative), letters fade/rise in. o: {t0,t1,y,size,col}
function engraved(g, text, t, o) {
  const { t0, t1 } = o; if (t < t0 || t > t1 + .4) return;
  const size = o.size || 84;
  g.save(); g.font = `${size}px "Cinzel Decorative Black"`; g.textAlign = 'center';
  const out = clamp((t - t1) / .4);
  const lines = text.split('\n');
  lines.forEach((line, li) => {
    const yy = (o.y || 600) + li * size * 1.15;
    const chars = [...line]; const widths = chars.map(c => g.measureText(c).width); const sp = (o.track || .04) * size;
    const total = widths.reduce((a, b) => a + b, 0) + sp * (chars.length - 1);
    let x = W / 2 - total / 2;
    chars.forEach((ch, i) => {
      const at = t0 + (li * chars.length + i) * (o.stagger ?? .025);
      const u = clamp((t - at) / .3);
      if (u > 0 && ch !== ' ') {
        g.save(); g.globalAlpha = ease.o(u) * (1 - out);
        g.translate(x + widths[i] / 2, yy + (1 - ease.o3(u)) * 26);
        g.textAlign = 'center';
        K.outlinedText(g, ch, 0, 0, { font: `${size}px "Cinzel Decorative Black"`, fill: o.col || '#f1e4c4', lw: size * .16, ink: '#1f120a', shadow: size * .05 });
        g.restore();
      }
      x += widths[i] + sp;
    });
  });
  g.restore();
}

// torn-paper legend card (the studio's "RECORDED" note style)
function paperCard(g, label, text, t, o) {
  const { t0, t1 } = o; if (t < t0 || t > t1 + .35) return;
  const u = ease.back(clamp((t - t0) / .35)), out = clamp((t - t1) / .35);
  const w = o.w || 860, h = o.h || 170, x = W / 2 - w / 2, y = o.y || 360;
  g.save(); g.globalAlpha = clamp((t - t0) / .15) * (1 - out);
  g.translate(W / 2, y + h / 2); g.rotate(-.012 + (1 - u) * .05); g.scale(.9 + .1 * u, .9 + .1 * u); g.translate(-W / 2, -(y + h / 2));
  const P = []; const r = C.rng(31);
  for (let i = 0; i <= 24; i++) P.push([x + w * i / 24, y + (r() - .5) * 8]);
  for (let i = 0; i <= 8; i++) P.push([x + w + (r() - .5) * 6, y + h * i / 8]);
  for (let i = 24; i >= 0; i--) P.push([x + w * i / 24, y + h + (r() - .5) * 8]);
  for (let i = 8; i >= 0; i--) P.push([x + (r() - .5) * 6, y + h * i / 8]);
  g.save(); g.fillStyle = 'rgba(0,0,0,.35)'; g.translate(6, 9); g.beginPath(); K.poly(g, P); g.fill(); g.restore();
  K.shape(g, P, { fill: '#efe5cc', lw: 2.5, smooth: false, inner: (g2) => { g2.globalAlpha = .25; g2.drawImage(require('./post').paper(), 0, 0); } });
  g.fillStyle = '#2a1a10'; g.textAlign = 'left';
  g.font = `${o.labelSize || 34}px "${FELLSC}"`; g.fillText(label, x + 34, y + 52);
  g.font = `italic ${o.size || 46}px "${FELL}"`;
  const lines = text.split('\n'); lines.forEach((L, i) => g.fillText(L, x + 34, y + 104 + i * (o.size || 46) * 1.1));
  g.restore();
}

module.exports = { storyCaption, engraved, paperCard, YEL, FELL, FELLSC };
