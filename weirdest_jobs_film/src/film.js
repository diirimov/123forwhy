// ===================================================================== film.js  (assembler)
'use strict';
let BUF = null, BUF2 = null;
function mainTitle(c, t) {
  if (t > 3.25) return;
  const appear = clamp((t - .3) / .35);
  if (appear <= 0) return;
  const small = t >= 1.6 && t < 2.8;              // shrink during the object close-ups
  const sc = small ? .62 : 1, y0 = small ? 190 : 300;
  c.save(); c.translate(540, y0); c.scale(sc, sc);
  const notes = [0, .2, .3, .5, .6, .8, 1.0, 1.1, 1.3, 1.4];
  const bump = hit(t, notes.map(n => n + .0), .12) * .06;
  // gold "3" medallion
  const ms = E.back(clamp((t - .3) / .4)) * (1 + bump);
  c.save(); c.translate(0, -10); c.scale(ms, ms);
  ell(c, 0, 0, 105, 105, lg(c, 0, -105, 0, 105, [[0, '#fff0a0'], [.5, '#f0b030'], [1, '#a8601a']]), 9);
  ell(c, 0, 0, 84, 84, null, 4, 0, '#7a4010');
  c.font = '900 150px CinzelD'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.lineWidth = 8; c.strokeStyle = '#4a2008'; c.strokeText('3', 0, 10); c.fillStyle = '#fff8e0'; c.fillText('3', 0, 10);
  c.restore();
  const words = [['WEIRDEST JOBS', 118, 170], ['IN HISTORY', 74, 270]];
  words.forEach(([w, size, y], wi) => {
    c.font = `${size}px Luckiest`; const tw = c.measureText(w).width; let x = -tw / 2;
    [...w].forEach((ch, i) => {
      const lw = c.measureText(ch).width, kk = clamp((t - .4 - wi * .2 - i * .03) / .3);
      const b = hit(t, [notes[(i + wi * 3) % notes.length] + .4], .15) * 14;
      c.save(); c.translate(x + lw / 2, y - (1 - E.back(kk)) * 120 - b); c.rotate((1 - kk) * (i % 2 ? .3 : -.3)); c.globalAlpha = clamp(kk * 3);
      c.textAlign = 'center'; c.textBaseline = 'middle'; c.lineJoin = 'round'; c.lineWidth = size * .28; c.strokeStyle = '#1a0c08'; c.strokeText(ch, 0, 0);
      c.fillStyle = wi === 0 ? lg(c, 0, -size / 2, 0, size / 2, [[0, '#fffaf0'], [1, '#ffd890']]) : '#ffd34d'; c.fillText(ch, 0, 0);
      c.restore(); x += lw;
    });
  });
  c.restore();
}
function findShot(t) { for (let i = 0; i < SHOTS.length; i++) if (t >= SHOTS[i].a && t < SHOTS[i].b) return i; return SHOTS.length - 1; }
function drawFilm(t) {
  if (!BUF) { BUF = mk(W, H); BUF2 = mk(W, H); }
  const i = findShot(t), S = SHOTS[i];
  const lt = t - S.a;
  const b = BUF.x; b.save(); b.setTransform(1, 0, 0, 1, 0, 0); b.globalAlpha = 1; b.globalCompositeOperation = 'source-over'; b.filter = 'none';
  try { S.draw(b, t); } catch (e) { console.log('shot error', S.name, e.message, e.stack.split('\n')[1]); }
  b.restore();
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.filter = 'none'; ctx.globalAlpha = 1;
  const tr = S.tr, d = .2;
  if (tr === 'whip' && lt < d) {
    const k = E.out(lt / d), off = (1 - k) * 700;
    ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
    ctx.filter = `blur(${(1 - k) * 28}px)`; ctx.drawImage(BUF.c, off, 0); ctx.filter = 'none';
    ctx.globalAlpha = .5 * (1 - k); ctx.drawImage(BUF.c, off + 120, 0); ctx.globalAlpha = 1;
  } else if (tr === 'punch' && lt < .25) {
    const k = E.out(lt / .25), z = 1.18 - .18 * k; ctx.translate(W / 2, H / 2); ctx.scale(z, z); ctx.translate(-W / 2, -H / 2); ctx.drawImage(BUF.c, 0, 0);
  } else if (tr === 'fade' && lt < .3) {
    ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); ctx.globalAlpha = lt / .3; ctx.drawImage(BUF.c, 0, 0);
  } else ctx.drawImage(BUF.c, 0, 0);
  ctx.restore();
  if (tr === 'flash' && lt < .25) { ctx.save(); ctx.globalAlpha = (1 - lt / .25) * .8; ctx.fillStyle = '#fff6e0'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
  mainTitle(ctx, t);
  if (window.overlay) overlay(ctx, t);
  finishFrame(ctx, t, S.vign ?? .5, .05);
}
