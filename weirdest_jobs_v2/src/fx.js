// ===================================================================== fx.js
// Typography, props, particles, camera helpers.
'use strict';
const VOC = BEATMAP.vocal;                            // [[time,'HEY!'],...]
const vocIn = (a, b) => VOC.filter(v => v[0] >= a - 1e-3 && v[0] < b).map(v => v[0]);
const sw16 = (b) => { const bb = Math.floor(b), u = b - bb, e = Math.floor(u * 2) / 2, w = (u - e) * 2; const ww = w < .5 ? w / .5 * .53 : .53 + (w - .5) / .5 * .47; return (bb + e + ww / 2) * SPB; };
const stepT = (bar, step) => sw16(bar * 4 + step / 4);     // time of 16th step in a bar
const patT = (bar, pat) => [...pat.replace(/ /g, '')].map((ch, i) => ch !== '.' ? stepT(bar, i) : null).filter(v => v !== null);

// ------------------------------------------------------------------ camera
function cam(c, x, y, z = 1, r = 0) { c.translate(W / 2, H / 2); c.rotate(r); c.scale(z, z); c.translate(-x, -y); }
function shake(t, times, amp = 14, dec = .12) { const k = hit(t, times, dec); return [Math.sin(t * 91) * amp * k, Math.cos(t * 77) * amp * k]; }

// ------------------------------------------------------------------ text
function fitFont(c, txt, font, size, maxW) { let s = size; c.font = font.replace('$', s); while (c.measureText(txt).width > maxW && s > 20) { s -= 2; c.font = font.replace('$', s); } return s; }
// rich line: words wrapped in *...* are emphasised (gold)
function richLine(c, str, x, y, size, k, opts) {
  const parts = str.split(/(\*[^*]+\*)/).filter(Boolean);
  const font = opts.font || "$px Luckiest";
  c.font = font.replace('$', size);
  const widths = parts.map(p => c.measureText(p.replace(/\*/g, '')).width);
  let cx = x - widths.reduce((a, b) => a + b, 0) / 2;
  parts.forEach((p, i) => {
    const em = p.startsWith('*'), s = p.replace(/\*/g, '');
    c.save(); c.translate(cx + widths[i] / 2, y);
    if (em) { const pop = 1 + .12 * Math.exp(-Math.max(0, k - .15) * 6) * Math.sin(Math.min(k, 1) * PI); c.scale(pop, pop); }
    c.textAlign = 'center'; c.textBaseline = 'middle'; c.lineJoin = 'round';
    c.lineWidth = size * .26; c.strokeStyle = opts.stroke || '#1a0c08'; c.strokeText(s, 0, 0);
    c.fillStyle = em ? lg(c, 0, -size / 2, 0, size / 2, [[0, '#fff3a0'], [1, '#f0a020']]) : (opts.fill || '#fffaf0');
    c.fillText(s, 0, 0);
    c.restore();
    cx += widths[i];
  });
}
// subtitle block with pop-in / fade-out; lines separated by '\n'
function subtitle(c, t, txt, t0, t1, opts = {}) {
  if (t < t0 - .01 || t > t1 + .25) return;
  const k = (t - t0) / .35, out = clamp((t - t1) / .25);
  const s = (opts.size || 66) * (k < 1 ? E.back(clamp(k)) : 1) * (1 - out * .1);
  const lines = txt.split('\n');
  const y0 = opts.y || 360;
  c.save(); c.globalAlpha = (1 - out) * clamp(k * 3);
  // soft dark plate for contrast
  c.font = `${opts.size || 66}px Luckiest`;
  const wmax = Math.max(...lines.map(l => c.measureText(l.replace(/\*/g, '')).width));
  c.fillStyle = 'rgba(14,6,12,0.42)'; c.beginPath(); c.roundRect(540 - wmax / 2 - 40, y0 - (opts.size || 66) * .85, wmax + 80, lines.length * (opts.size || 66) * 1.12 + (opts.size || 66) * .5, 34); c.fill();
  lines.forEach((l, i) => richLine(c, l, 540 + (opts.dx || 0), y0 + i * (opts.size || 66) * 1.12, s, t - t0, opts));
  c.restore();
}
// chapter title card: big number medallion + title on ribbon
function chapterCard(c, t, num, title, t0, t1, accent) {
  if (t < t0 || t > t1 + .3) return;
  const k = t - t0, out = clamp((t - t1) / .3);
  c.save(); c.globalAlpha = 1 - out;
  const y = 330;
  // ribbon
  const rw = 940 * E.out(clamp(k / .35));
  c.save(); c.translate(540, y + 70);
  poly(c, [[-rw / 2, -54], [rw / 2, -54], [rw / 2 + 40, 0], [rw / 2, 54], [-rw / 2, 54], [-rw / 2 - 40, 0]], accent, 6);
  poly(c, [[-rw / 2 + 12, -40], [rw / 2 - 12, -40], [rw / 2 - 12, 40], [-rw / 2 + 12, 40]], null, 3, rgba('#fff2c0', .6));
  c.restore();
  // medallion
  const ms = E.back(clamp((k - .05) / .4));
  c.save(); c.translate(540, y - 70); c.scale(ms, ms); c.rotate((1 - ms) * 1.5);
  ell(c, 0, 0, 82, 82, lg(c, 0, -82, 0, 82, [[0, '#ffe58a'], [1, '#c8862a']]), 7);
  ell(c, 0, 0, 64, 64, null, 3, 0, '#7a4a10');
  c.font = '900 92px CinzelD'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillStyle = '#4a2408'; c.fillText(num, 0, 6);
  c.restore();
  // title letters drop in one by one
  const letters = [...title]; c.font = `${fitFont(c, title, '$px Luckiest', 74, 860)}px Luckiest`;
  const tw = c.measureText(title).width; let x = 540 - tw / 2;
  letters.forEach((ch, i) => {
    const lw = c.measureText(ch).width, kk = clamp((k - .12 - i * .025) / .3);
    c.save(); c.translate(x + lw / 2, y + 76 - (1 - E.back(kk)) * 90); c.globalAlpha *= clamp(kk * 3);
    c.textAlign = 'center'; c.textBaseline = 'middle'; c.lineJoin = 'round'; c.lineWidth = 16; c.strokeStyle = '#1a0c08'; c.strokeText(ch, 0, 0);
    c.fillStyle = '#fffaf0'; c.fillText(ch, 0, 0); c.restore(); x += lw;
  });
  c.restore();
}

// ------------------------------------------------------------------ props
function pole(c, x0, y0, x1, y1, lw = 5) {     // the knocker-up's long pole with wire tip
  line(c, [[x0, y0], [x1, y1]], 18 + lw, INK); line(c, [[x0, y0], [x1, y1]], 14, '#c8a46a');
  line(c, [[x0, y0], [x1, y1]], 4, rgba('#fff4d0', .45));
  const n = 7; for (let i = 1; i < n; i++) { const k = i / n; const x = lerp(x0, x1, k), y = lerp(y0, y1, k); const a = Math.atan2(y1 - y0, x1 - x0) + PI / 2; line(c, [[x - Math.cos(a) * 9, y - Math.sin(a) * 9], [x + Math.cos(a) * 9, y + Math.sin(a) * 9]], 4, '#6a4a2a'); }
  const a = Math.atan2(y1 - y0, x1 - x0);
  for (let i = -1; i <= 1; i++) curve(c, [[x1, y1], [x1 + Math.cos(a + i * .4) * 30, y1 + Math.sin(a + i * .4) * 30], [x1 + Math.cos(a + i * .6) * 46, y1 + Math.sin(a + i * .6) * 46 + 8]], 4, '#4a4a52');
}
function sceptre(c, x0, y0, x1, y1) {
  line(c, [[x0, y0], [x1, y1]], 26, INK); line(c, [[x0, y0], [x1, y1]], 18, '#e8b840'); line(c, [[x0, y0], [x1, y1]], 5, '#fff2a8');
  ell(c, x1, y1, 34, 34, rg(c, x1 - 8, y1 - 8, 2, 34, [[0, '#fff2a8'], [1, '#d8a030']]), 6);
  ell(c, x1, y1, 14, 14, '#c8203a', 3); glow(c, x1, y1, 120, 'rgba(255,220,120,0.4)');
}
function closeStool(c, x, y, s, lid = 0, shine = 0) {   // ornate Tudor close stool (box seat + pot)
  c.save(); c.translate(x, y); c.scale(s, s);
  ell(c, 0, 12, 230, 34, 'rgba(0,0,0,0.35)');
  rrect(c, -190, -230, 380, 240, 18, '#6a1424', 6);
  c.fillStyle = lg(c, -190, 0, 190, 0, [[0, 'rgba(0,0,0,0.35)'], [.5, 'rgba(255,200,200,0.12)'], [1, 'rgba(0,0,0,0.35)']]); c.fillRect(-186, -226, 372, 232);
  for (let i = 0; i < 9; i++) { ell(c, -170 + i * 42.5, -218, 7, 7, '#f0c040', 2); ell(c, -170 + i * 42.5, -6, 7, 7, '#f0c040', 2); }
  rrect(c, -150, -190, 300, 150, 12, null, 4, '#f0c040');
  // crest
  ell(c, 0, -115, 40, 44, '#f0c040', 4); poly(c, [[-14, -132], [0, -150], [14, -132], [0, -96]], '#8a1424');
  // lid: hinged at the back. Closed = padded cushion on top; open = upright padded panel behind the seat
  const lk = clamp(lid);
  const seatTop = -236;
  if (lk > .05) {
    const ph = 250 * Math.sin(lk * PI / 2);          // panel rises behind the seat
    rrect(c, -185, seatTop - ph, 370, ph + 20, 40, '#7a1628', 6);
    c.save(); c.beginPath(); c.roundRect(-185, seatTop - ph, 370, ph + 20, 40); c.clip();
    c.fillStyle = lg(c, -185, 0, 185, 0, [[0, 'rgba(0,0,0,0.3)'], [.5, 'rgba(255,210,210,0.18)'], [1, 'rgba(0,0,0,0.3)']]); c.fillRect(-185, seatTop - ph, 370, ph + 20);
    for (let i = 0; i < 3; i++) for (let j = 0; j < 4; j++) ell(c, -110 + j * 73, seatTop - ph + 50 + i * 70, 5, 5, '#f0c040', 1.5);
    c.restore();
    rrect(c, -185, seatTop - ph, 370, ph + 20, 40, null, 6);
  }
  // seat board with the opening (porcelain pot inside) when the lid is up
  rrect(c, -205, seatTop - 18, 410, 40, 18, '#8a1a2c', 6);
  if (lk > .05) { ell(c, 0, seatTop + 2, 120, 22, '#3a1012', 4); ell(c, 0, seatTop - 1, 96, 14, '#f2ece2', 3); ell(c, 0, seatTop - 3, 70, 8, '#d8d0c6'); }
  else { ell(c, 0, seatTop - 2, 150, 20, '#a8243a', 4); ell(c, 0, seatTop - 6, 110, 10, 'rgba(255,220,220,0.25)'); }
  for (let i = 0; i < 9; i++) ell(c, -180 + i * 45, seatTop + 12, 5, 5, '#f0c040', 1.5);
  // tassels
  for (const sx of [-1, 1]) { line(c, [[sx * 190, -200], [sx * 205, -150]], 4, '#f0c040'); ell(c, sx * 205, -140, 10, 16, '#f0c040', 3); }
  c.restore();
  if (shine > 0) sparkles(c, x, y - 150 * s, 260 * s, shine, 7);
}
function sparkles(c, x, y, r, a, seed, t = 0) {
  const rr = rng(seed);
  c.save(); c.globalCompositeOperation = 'lighter';
  for (let i = 0; i < 14; i++) {
    const ang = rr() * TAU, d = rr() * r, ph = rr() * TAU, s = (8 + rr() * 22) * (0.5 + 0.5 * Math.sin(t * 9 + ph)) * a;
    const px = x + Math.cos(ang) * d, py = y + Math.sin(ang) * d * .7;
    c.fillStyle = `rgba(255,240,180,${.9 * a})`;
    c.beginPath(); c.moveTo(px, py - s); c.quadraticCurveTo(px, py, px + s, py); c.quadraticCurveTo(px, py, px, py + s); c.quadraticCurveTo(px, py, px - s, py); c.quadraticCurveTo(px, py, px, py - s); c.fill();
  }
  c.restore();
}
function coin(c, x, y, r, spin = 0, col = '#f0c040', mark = true) {
  const sx = Math.max(.08, Math.abs(Math.cos(spin)));
  c.save(); c.translate(x, y); c.scale(sx, 1);
  ell(c, 0, 0, r, r, lg(c, 0, -r, 0, r, [[0, tint(col, .5)], [1, shade(col, .25)]]), Math.max(2, r * .12));
  ell(c, 0, 0, r * .72, r * .72, null, Math.max(1.5, r * .06), 0, shade(col, .45));
  if (mark && sx > .4) { const m = shade(col, .5);
    if (mark === 'cross') { line(c, [[0, -r * .45], [0, r * .45]], r * .12, m); line(c, [[-r * .3, -r * .12], [r * .3, -r * .12]], r * .12, m); }
    else { poly(c, [[-r * .4, r * .25], [-r * .45, -r * .25], [-r * .2, 0], [0, -r * .35], [r * .2, 0], [r * .45, -r * .25], [r * .4, r * .25]], m); }
    for (let i = 0; i < 16; i++) ell(c, Math.cos(i / 16 * TAU) * r * .86, Math.sin(i / 16 * TAU) * r * .86, r * .035, r * .035, m); }
  c.restore();
}
function bread(c, x, y, s, bite = 0) {
  c.save(); c.translate(x, y); c.scale(s, s);
  blob(c, [[-120, 10], [-110, -40], [-60, -70], [20, -78], [90, -58], [125, -15], [110, 20], [0, 34]], '#c8843a', 6);
  c.save(); c.beginPath(); spline(c, [[-120, 10], [-110, -40], [-60, -70], [20, -78], [90, -58], [125, -15], [110, 20], [0, 34]]); c.clip();
  c.fillStyle = lg(c, 0, -80, 0, 34, [[0, '#f0b868'], [1, '#8a4a1a']]); c.fillRect(-130, -80, 260, 120);
  for (let i = 0; i < 4; i++) curve(c, [[-70 + i * 45, -55], [-58 + i * 45, -28], [-50 + i * 45, -10]], 5, '#7a3e14');
  if (bite > 0) { ell(c, 110, -28, 46 * bite, 40 * bite, '#f4e2bc', 4); for (let i = 0; i < 5; i++) ell(c, 92 + i * 6, -50 + i * 16, 8 * bite, 8 * bite, '#f4e2bc'); }
  c.restore();
  c.restore();
}
function candle(c, x, y, h, t, seed = 0, s = 1) {
  rrect(c, x - 14 * s, y - h, 28 * s, h, 6, '#f0e6cc', 3);
  ell(c, x, y - h, 14 * s, 4 * s, '#d8ccb0');
  const fl = 1 + .15 * Math.sin(t * 17 + seed) + .08 * Math.sin(t * 31 + seed * 2);
  glow(c, x, y - h - 26 * s, 180 * s * fl, 'rgba(255,170,70,0.55)');
  blob(c, [[x, y - h - 52 * s * fl], [x + 12 * s, y - h - 18 * s], [x, y - h - 6 * s], [x - 12 * s, y - h - 18 * s]], '#ffd27a');
  blob(c, [[x, y - h - 34 * s * fl], [x + 6 * s, y - h - 16 * s], [x, y - h - 9 * s], [x - 6 * s, y - h - 16 * s]], '#fff8e0');
}
function zzz(c, x, y, t, a = 1) {
  for (let i = 0; i < 3; i++) {
    const k = ((t * .9 + i / 3) % 1);
    c.save(); c.globalAlpha = a * Math.sin(k * PI); c.translate(x + k * 90 + Math.sin(k * 6) * 16, y - k * 200); c.rotate(-.2);
    c.font = `${40 + k * 50}px Luckiest`; c.lineWidth = 10; c.strokeStyle = '#1a0c08'; c.lineJoin = 'round'; c.strokeText('Z', 0, 0); c.fillStyle = '#e8f0ff'; c.fillText('Z', 0, 0);
    c.restore();
  }
}
function smokeWisps(c, x, y, t, k, seed, col = '#2a1438') {   // symbolic dark smoke/sin wisps
  const r = rng(seed);
  for (let i = 0; i < 26; i++) {
    const ph = r() * TAU, sp = .5 + r(), a = (t * sp + r()) % 1;
    const px = x + Math.sin(ph + t * 2) * 60 * (1 + a * 2) + (r() - .5) * 120, py = y - a * 420 * k;
    const rr = (30 + a * 90) * k;
    c.fillStyle = rg(c, px, py, 0, rr, [[0, rgba(col, .55 * (1 - a) * k)], [1, rgba(col, 0)]]); c.fillRect(px - rr, py - rr, rr * 2, rr * 2);
  }
  // glowing motes
  particles(c, t, seed + 5, 30, (c, t, i, a, b, d, e) => { const u = (t * (.3 + d * .4) + a) % 1; const px = x + (b - .5) * 300 + Math.sin(u * 9 + e * 6) * 30, py = y - u * 500 * k; ell(c, px, py, 3 + e * 4, 3 + e * 4, `rgba(190,150,255,${.8 * Math.sin(u * PI) * k})`); });
}
function motes(c, t, seed, n, col, a = .6, spd = 30) {
  particles(c, t, seed, n, (c, t, i, r1, r2, r3, r4) => { const x = (r1 * W + t * spd * (r3 - .5) * 2 + W * 2) % W, y = (r2 * H - t * spd * r4 + H * 3) % H; ell(c, x, y, 1.5 + r3 * 3, 1.5 + r3 * 3, rgba(col, a * (.4 + .6 * Math.sin(t * 2 + i)))); });
}
function lightShafts(c, x, y, ang, w, len, col, a) {
  c.save(); c.globalCompositeOperation = 'lighter'; c.translate(x, y); c.rotate(ang);
  for (let i = 0; i < 4; i++) { c.fillStyle = lg(c, 0, 0, 0, len, [[0, rgba(col, a)], [1, rgba(col, 0)]]); c.beginPath(); c.moveTo(-w / 2 + i * w / 4, 0); c.lineTo(-w / 2 + i * w / 4 + w / 8, 0); c.lineTo(-w + i * w / 2 + w / 4, len); c.lineTo(-w + i * w / 2, len); c.fill(); }
  c.restore();
}
function flash(c, t, times, col = '#fff6e0', dec = .08, a = .7) { const k = hit(t, times, dec); if (k > .01) { c.save(); c.globalAlpha = k * a; c.fillStyle = col; c.fillRect(0, 0, W, H); c.restore(); } }
function speedLines(c, cx, cy, a, seed) { if (a <= .01) return; const r = rng(seed); c.save(); c.globalAlpha = a; for (let i = 0; i < 40; i++) { const ang = r() * TAU, r0 = 420 + r() * 200; line(c, [[cx + Math.cos(ang) * r0, cy + Math.sin(ang) * r0], [cx + Math.cos(ang) * 1600, cy + Math.sin(ang) * 1600]], 3 + r() * 8, '#fff8ea'); } c.restore(); }
