// Film framework: layer cache, camera, post-processing, subtitles, stamps, transitions.
const C = require('./core');
const { W, H, FPS, canvas, clamp, lerp, outBack, outC, inC, smooth, hash } = C;
const D = require('./draw');

// ---------------------------------------------------------------- cached layers
const CACHE = new Map();
// world-space bitmap layer, rendered once at `res` px per world unit
function layer(key, x0, y0, w, h, res, drawFn) {
  let L = CACHE.get(key);
  if (!L) {
    const cv = canvas(w * res, h * res), x = cv.getContext('2d');
    x.scale(res, res); x.translate(-x0, -y0); drawFn(x);
    L = { cv, x0, y0, w, h }; CACHE.set(key, L);
  }
  return L;
}
const drawLayer = (ctx, L) => ctx.drawImage(L.cv, L.x0, L.y0, L.w, L.h);
function clearCacheExcept(keys) { for (const k of [...CACHE.keys()]) if (!keys.some(p => k.startsWith(p))) CACHE.delete(k); }

// ---------------------------------------------------------------- camera
// cam = {x, y, z, r}: world point at screen centre, zoom, roll (deg). p = parallax depth (1 = subject plane).
function withCam(ctx, cam, p, fn, anchor = [0, 0]) {
  ctx.save();
  ctx.translate(W / 2 + (cam.sx || 0), H / 2 + (cam.sy || 0));
  ctx.rotate((cam.r || 0) * C.D2R * Math.min(1, p));
  const z = Math.pow(cam.z, p);
  ctx.scale(z, z);
  ctx.translate(-(cam.x * p + anchor[0] * (1 - p)), -(cam.y * p + anchor[1] * (1 - p)));
  fn(ctx);
  ctx.restore();
}
// keyframed camera: keys [{t, x, y, z, r, e}] with easing into each key
function camAt(keys, t) {
  if (t <= keys[0].t) return { ...keys[0] };
  for (let i = 1; i < keys.length; i++) {
    const a = keys[i - 1], b = keys[i];
    if (t <= b.t) {
      const u = (t - a.t) / (b.t - a.t), e = (b.e || C.smoother)(u);
      return { x: lerp(a.x, b.x, e), y: lerp(a.y, b.y, e), z: lerp(a.z, b.z, e), r: lerp(a.r || 0, b.r || 0, e) };
    }
  }
  return { ...keys[keys.length - 1] };
}

// ---------------------------------------------------------------- post
let PAPER = null, GRAINS = null, VIG = null;
function initPost() {
  if (PAPER) return;
  PAPER = D.makePaper(540, 960, 9);
  GRAINS = [0, 1, 2, 3].map(i => D.makeGrain(360, 640, 100 + i));
  VIG = canvas(W, H); const v = VIG.getContext('2d');
  const g = v.createRadialGradient(W / 2, H * 0.46, H * 0.22, W / 2, H * 0.5, H * 0.75);
  g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(40,18,8,0.62)');
  v.fillStyle = g; v.fillRect(0, 0, W, H);
}
function post(ctx, t, o = {}) {
  initPost();
  // warm parchment grade
  ctx.save();
  ctx.globalCompositeOperation = "multiply"; ctx.globalAlpha = o.paper === undefined ? 0.22 : o.paper;
  ctx.drawImage(PAPER, 0, 0, W, H);
  ctx.globalAlpha = 0.12; ctx.fillStyle = '#f2c58a'; ctx.fillRect(0, 0, W, H);
  ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = o.vig === undefined ? 0.85 : o.vig; ctx.drawImage(VIG, 0, 0);
  ctx.globalCompositeOperation = 'overlay'; ctx.globalAlpha = 0.09;
  ctx.drawImage(GRAINS[C.boilStep(t) % 4], 0, 0, W, H);
  ctx.restore();
}

// ---------------------------------------------------------------- subtitles
const SUB_Y = 1490, SUB_MAXW = 920;
function wrapWords(ctx, words, size, maxW) {
  ctx.font = `${size}px "Archivo Black"`;
  const lines = [[]]; let w = 0; const sp = ctx.measureText(' ').width;
  for (const wd of words) {
    const ww = ctx.measureText(wd.text).width;
    if (w + ww > maxW && lines[lines.length - 1].length) { lines.push([]); w = 0; }
    lines[lines.length - 1].push({ ...wd, w: ww }); w += ww + sp;
  }
  return { lines, sp };
}
// sub = {t0, t1, text, em:[words], color, size, style}
function drawSub(ctx, sub, t) {
  if (t < sub.t0 - 0.01 || t > sub.t1) return;
  const lt = t - sub.t0, out = sub.t1 >= 59.99 ? 1 : clamp((sub.t1 - t) / 0.1);
  const size = sub.size || 76;
  const words = sub.text.split(' ').map(s => ({ text: s, em: (sub.em || []).some(e => s.replace(/[^A-Za-z']/g, '').toUpperCase() === e) }));
  const { lines, sp } = wrapWords(ctx, words, size, SUB_MAXW);
  const lh = size * 1.12, y0 = (sub.y || SUB_Y) - (lines.length - 1) * lh / 2;
  let k = 0;
  ctx.save(); ctx.globalAlpha = out;
  lines.forEach((ln, li) => {
    const tw = ln.reduce((a, b) => a + b.w, 0) + sp * (ln.length - 1);
    let x = W / 2 - tw / 2;
    for (const wd of ln) {
      const d = lt - k * 0.045; k++;
      if (d < 0) { x += wd.w + sp; continue; }
      const sc = outBack(clamp(d / 0.16), 2.4) * (wd.em ? 1 + 0.12 * Math.max(0, 1 - Math.abs(d - 0.2) / 0.2) : 1);
      const cx = x + wd.w / 2, cy = y0 + li * lh;
      ctx.save(); ctx.translate(cx, cy); ctx.scale(sc, sc); ctx.rotate(wd.em ? -0.025 : 0);
      ctx.font = `${size}px "Archivo Black"`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      ctx.lineJoin = 'round';
      ctx.lineWidth = size * 0.26; ctx.strokeStyle = 'rgba(30,14,8,0.55)'; ctx.strokeText(wd.text, 4, 7);
      ctx.lineWidth = size * 0.2; ctx.strokeStyle = '#2a140c'; ctx.strokeText(wd.text, 0, 0);
      ctx.fillStyle = wd.em ? (sub.color || '#ffc63d') : '#fff6e4'; ctx.fillText(wd.text, 0, 0);
      ctx.restore();
      x += wd.w + sp;
    }
  });
  ctx.restore();
}

// chapter stamp: "TREATMENT Nº1" + blackletter title on a parchment banner, slammed on a beat
function drawStamp(ctx, st, t) {
  const lt = t - st.t0; if (lt < 0 || t > st.t1) return;
  const inn = clamp(lt / 0.12), out = clamp((st.t1 - t) / 0.18);
  const sc = lerp(1.9, 1, outC(inn)) * (1 + 0.04 * Math.sin(lt * 4)) * lerp(0.6, 1, out);
  ctx.save();
  ctx.translate(W / 2, (st.y || 300) - (1 - out) * 120); ctx.rotate((-5 + 2 * Math.sin(lt * 2)) * C.D2R); ctx.scale(sc, sc);
  ctx.globalAlpha = inn * out;
  // banner with ribbon tails
  const bw = 640, bh = 210;
  D.shape(ctx, c => { c.moveTo(-bw / 2 - 70, -30); c.lineTo(-bw / 2 - 20, 10); c.lineTo(-bw / 2 - 70, 50); c.lineTo(-bw / 2 + 20, 50); c.lineTo(-bw / 2 + 20, -30); c.closePath(); }, '#8f2a22', { lw: 6 });
  D.shape(ctx, c => { c.moveTo(bw / 2 + 70, -30); c.lineTo(bw / 2 + 20, 10); c.lineTo(bw / 2 + 70, 50); c.lineTo(bw / 2 - 20, 50); c.lineTo(bw / 2 - 20, -30); c.closePath(); }, '#8f2a22', { lw: 6 });
  D.shape(ctx, c => { c.moveTo(-bw / 2, -bh / 2); c.quadraticCurveTo(0, -bh / 2 - 22, bw / 2, -bh / 2); c.lineTo(bw / 2, bh / 2); c.quadraticCurveTo(0, bh / 2 - 22, -bw / 2, bh / 2); c.closePath(); }, '#efdcaf', { lw: 7, shade: { x0: 0, y0: -bh / 2, x1: 0, y1: bh / 2, a: 0.25 } });
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillStyle = '#7a2018'; ctx.font = '40px "Cinzel Black"'; ctx.fillText(st.kicker, 0, -56);
  ctx.fillStyle = '#2a140c'; ctx.font = '104px "Unifraktur"'; ctx.fillText(st.title, 0, 30);
  ctx.restore();
}

// comic sound lettering (ACHOO!, BONK!)
function drawSfxText(ctx, s, t) {
  const lt = t - s.t0; if (lt < 0 || t > s.t1) return;
  const inn = outBack(clamp(lt / 0.14), 3), out = clamp((s.t1 - t) / 0.15);
  ctx.save(); ctx.translate(s.x, s.y + (1 - out) * -40); ctx.rotate((s.rot || -8) * C.D2R + Math.sin(lt * 30) * 0.02 * (1 - clamp(lt / 0.3)));
  ctx.scale(inn * (1 + 0.05 * Math.sin(lt * 9)), inn * (1 + 0.05 * Math.sin(lt * 9)));
  ctx.globalAlpha = out;
  ctx.font = `${s.size || 150}px "Luckiest Guy"`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.lineJoin = 'round';
  ctx.lineWidth = (s.size || 150) * 0.22; ctx.strokeStyle = '#2a140c'; ctx.strokeText(s.text, 0, 0);
  const g = ctx.createLinearGradient(0, -(s.size || 150) / 2, 0, (s.size || 150) / 2);
  g.addColorStop(0, s.c1 || '#fff1a8'); g.addColorStop(1, s.c2 || '#f2a33a');
  ctx.fillStyle = g; ctx.fillText(s.text, 0, 0);
  ctx.restore();
}

// ---------------------------------------------------------------- frame helpers
function blurInto(dst, src, dx, dy, n = 6) {    // directional motion blur (whip pans)
  const x = dst.getContext('2d');
  x.clearRect(0, 0, W, H);
  for (let i = 0; i < n; i++) { const k = (i / (n - 1) - 0.5); x.globalAlpha = 1 / (i + 1); x.drawImage(src, dx * k, dy * k); }
  x.globalAlpha = 1;
}

module.exports = { layer, drawLayer, clearCacheExcept, withCam, camAt, post, drawSub, drawStamp, drawSfxText, blurInto, CACHE };
