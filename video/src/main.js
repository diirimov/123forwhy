// ---------- frame renderer ----------
const CV = document.getElementById('cv'), CTX = CV.getContext('2d');
let READY = false;
async function init() {
  await Promise.all(["900 40px 'Cinzel'", "700 40px 'Cinzel'", "40px 'Pirata One'", "40px 'IM Fell English'", "italic 40px 'IM Fell English'", "40px 'IM Fell English SC'"].map(f => document.fonts.load(f)));
  if (typeof loadData === 'function') await loadData();
  makeGrain(); makePaper(); buildEnvs();
  READY = true;
}
const BUF = mkCanvas(W, H), BCTX = BUF.getContext('2d');
function sceneAt(t) { for (const s of SCENES) if (t >= s.t0 && t < s.t1) return s; return SCENES[SCENES.length - 1]; }
function drawScene(ctx, s, t) {
  ctx.save(); ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
  s.fn(ctx, t, t - s.t0); ctx.restore();
}
function renderAt(t) {
  const s = sceneAt(t);
  const mb = s.mb ? s.mb(t - s.t0, t) : 0; // motion blur samples
  const ctx = CTX; ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over';
  if (mb > 1) {
    for (let i = 0; i < mb; i++) {
      const ts = t + (i / mb - .5) * (1 / FPS) * .9;
      drawScene(BCTX, s, ts);
      ctx.globalAlpha = 1 / (i + 1); ctx.drawImage(BUF, 0, 0);
    }
    ctx.globalAlpha = 1;
  } else drawScene(ctx, s, t);
  if (s.overlay) { ctx.save(); s.overlay(ctx, t, t - s.t0); ctx.restore(); }
  post(ctx, t, s.post || {});
  if (window.GLOBAL_OVERLAY) GLOBAL_OVERLAY(ctx, t);
}
window.renderAt = renderAt;
window.initDone = init();
