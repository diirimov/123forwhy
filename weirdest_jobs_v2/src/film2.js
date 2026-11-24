'use strict';
let BUF = null;
function findShot(t) { for (let i = 0; i < SHOTS.length; i++) if (t >= SHOTS[i].a && t < SHOTS[i].b) return i; return SHOTS.length - 1; }
function drawFilm(t) {
  if (!BUF) BUF = mk(W, H);
  const S = SHOTS[findShot(t)], lt = t - S.a, b = BUF.x;
  b.save(); b.setTransform(1, 0, 0, 1, 0, 0); b.globalAlpha = 1; b.globalCompositeOperation = 'source-over'; b.filter = 'none';
  try { S.draw(b, t); } catch (e) { console.log('shot error', S.name, e.message, (e.stack || '').split('\n').slice(0, 3).join(' | ')); }
  b.restore();
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.filter = 'none'; ctx.globalAlpha = 1;
  if (S.tr === 'whip' && lt < .2) { const k = E.out(lt / .2), off = (1 - k) * 700; ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); ctx.filter = `blur(${(1 - k) * 28}px)`; ctx.drawImage(BUF.c, off, 0); ctx.filter = 'none'; }
  else if (S.tr === 'punch' && lt < .25) { const z = 1.18 - .18 * E.out(lt / .25); ctx.translate(W / 2, H / 2); ctx.scale(z, z); ctx.translate(-W / 2, -H / 2); ctx.drawImage(BUF.c, 0, 0); }
  else ctx.drawImage(BUF.c, 0, 0);
  ctx.restore();
  if (S.tr === 'flash' && lt < .25) { ctx.save(); ctx.globalAlpha = (1 - lt / .25) * .75; ctx.fillStyle = '#fff6e0'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
  if (window.overlay) overlay(ctx, t, S);
  finishFrame(ctx, t, .38, .045);
  if (S.theme && !S.noBands) { band(ctx, BAND_TOP, S.theme, t); band(ctx, BAND_BOT, S.theme, t, true); }
  if (window.overlayTop) overlayTop(ctx, t, S);
}
