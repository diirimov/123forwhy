// post: camera layers, colour grades, emissive lights, paper texture, vignette, grain, depth of field
'use strict';
const { createCanvas } = require('@napi-rs/canvas');
const C = require('./core');
const E = require('./env');
const { W, H, clamp, lerp, TAU, hash } = C;

// ---------------------------------------------------------------- camera / parallax layers
// cam: {x, y, zoom, rot}; d: depth factor (0 = sky at infinity, 1 = character plane, >1 = foreground)
function layer(g, cam, d, fn) {
  g.save();
  const z = 1 + (cam.zoom - 1) * d;
  g.translate(W / 2, H / 2); if (cam.rot) g.rotate(cam.rot * d); g.scale(z, z);
  g.translate(-W / 2 - (cam.x || 0) * d, -H / 2 - (cam.y || 0) * d);
  fn(g);
  g.restore();
}

// ---------------------------------------------------------------- textures (built once per process)
let PAPER = null, GRAIN = null, SCRATCH = null;
function paper() {
  if (PAPER) return PAPER;
  const cv = createCanvas(W, H), g = cv.getContext('2d');
  const img = g.createImageData(W, H);
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
    const n = C.fbm(x / 140, y / 140, 4) * .5 + C.fbm(x / 18, y / 18, 2) * .25 + (hash(x * 1.3 + y * 7.7) - .5) * .18;
    const fib = Math.sin((x * .7 + y * .2) * .09 + C.noise2(x / 60, y / 60) * 6) * .05;
    const v = clamp(.92 + (n + fib) * .22, 0, 1);
    const i = (y * W + x) * 4;
    img.data[i] = 255 * v; img.data[i + 1] = 247 * v; img.data[i + 2] = 230 * v; img.data[i + 3] = 255;
  }
  g.putImageData(img, 0, 0);
  PAPER = cv; return cv;
}
function grainTiles() {
  if (GRAIN) return GRAIN;
  GRAIN = [];
  for (let k = 0; k < 6; k++) {
    const cv = createCanvas(360, 640), g = cv.getContext('2d'); const img = g.createImageData(360, 640);
    for (let i = 0; i < 360 * 640; i++) { const v = hash(i * 1.37 + k * 911.3) * 255; img.data[i * 4] = v; img.data[i * 4 + 1] = v; img.data[i * 4 + 2] = v; img.data[i * 4 + 3] = 255; }
    g.putImageData(img, 0, 0); GRAIN.push(cv);
  }
  return GRAIN;
}

// ---------------------------------------------------------------- grades
// mood presets: day = the studio's sepia, dusk = violet/amber, night = navy moonlight, cold = drained blue-grey
const GRADES = {
  day: { desat: .3, mul: '#f4e0b8', mulA: 1, lift: 'rgba(60,35,15,.05)' },
  warm: { desat: .25, mul: '#f5d6a2', mulA: 1, lift: 'rgba(80,40,10,.06)' },
  dusk: { desat: .25, mul: '#e8b89a', mulA: 1, top: '#8a6aa0', bot: '#f0b080', lift: 'rgba(40,20,50,.08)' },
  night: { desat: .28, mul: '#9aaad3', mulA: 1, lift: 'rgba(10,15,40,.08)' },
  cold: { desat: .55, mul: '#b9bfcc', mulA: 1, lift: 'rgba(20,25,40,.1)' },
};
function grade(g, mood, amt = 1, mood2 = null, mix = 0) {
  const A = GRADES[mood] || GRADES.day;
  const apply = (Gd, a) => {
    if (a <= 0) return;
    g.save();
    g.globalCompositeOperation = 'saturation'; g.globalAlpha = Gd.desat * a; g.fillStyle = '#808080'; g.fillRect(0, 0, W, H);
    g.globalCompositeOperation = 'multiply'; g.globalAlpha = Gd.mulA * a;
    if (Gd.top) { const gr = g.createLinearGradient(0, 0, 0, H); gr.addColorStop(0, Gd.top); gr.addColorStop(1, Gd.bot); g.fillStyle = gr; }
    else g.fillStyle = Gd.mul;
    g.fillRect(0, 0, W, H);
    g.globalCompositeOperation = 'source-over'; g.globalAlpha = a; g.fillStyle = Gd.lift; g.fillRect(0, 0, W, H);
    g.restore();
  };
  if (mood2 && mix > 0) { apply(A, amt * (1 - mix)); apply(GRADES[mood2], amt * mix); }
  else apply(A, amt);
}
function lights(g, scale = 1) {
  // NB: the canvas library leaks ~8.6 MB per drawImage() under destination-out/-in, so occlusion is done by MULTIPLY:
  // the light layer is opaque black + additive lights; each batch of occluders is a white mask with black silhouettes.
  if (!E.LIGHTS.some(L => L.kind !== 'occ')) return;
  const cv = off(), L2 = cv.getContext('2d'); L2.setTransform(1, 0, 0, 1, 0, 0); L2.globalCompositeOperation = 'source-over'; L2.fillStyle = '#000'; L2.fillRect(0, 0, W, H);
  const MK = off(), M = MK.getContext('2d');
  const K = require('./ink');
  let pending = false, drawnLight = false;
  const flush = () => {
    if (!pending) return;
    if (drawnLight) { L2.save(); L2.setTransform(1, 0, 0, 1, 0, 0); L2.globalCompositeOperation = 'multiply'; L2.drawImage(MK, 0, 0); L2.restore(); }
    pending = false;
  };
  for (const L of E.LIGHTS) {
    if (L.kind === 'occ') {
      if (!drawnLight) continue;              // nothing behind it to occlude yet
      if (!pending) { M.setTransform(1, 0, 0, 1, 0, 0); M.globalCompositeOperation = 'source-over'; M.fillStyle = '#fff'; M.fillRect(0, 0, W, H); pending = true; }
      M.save(); M.setTransform(L.m); M.fillStyle = '#000'; M.strokeStyle = '#000'; L.fn(M); M.restore();
      continue;
    }
    flush();
    drawnLight = true;
    L2.save(); L2.globalCompositeOperation = 'lighter';
    if (L.kind === 'rect') { L2.globalAlpha = L.a * scale; L2.fillStyle = L.col; L2.fillRect(L.x, L.y, L.w, L.h); L2.restore(); continue; }
    const gr = L2.createRadialGradient(L.x, L.y, 0, L.x, L.y, L.r);
    gr.addColorStop(0, K.rgba(L.col, .7)); gr.addColorStop(.3, K.rgba(L.col, .28)); gr.addColorStop(1, K.rgba(L.col, 0));
    L2.globalAlpha = L.a * scale; L2.fillStyle = gr; L2.beginPath(); L2.arc(L.x, L.y, L.r, 0, TAU); L2.fill(); L2.restore();
  }
  flush();
  g.save(); g.globalCompositeOperation = 'screen'; g.drawImage(cv, 0, 0); g.restore();
  release(cv); release(MK);
}

function finish(g, t, o = {}) {
  // paper texture (static, like the studio's printed-paper look)
  g.save(); g.globalCompositeOperation = 'multiply'; g.globalAlpha = o.paper ?? .55; g.drawImage(paper(), 0, 0); g.restore();
  // vignette
  const vg = g.createRadialGradient(W / 2, H * .46, H * .28, W / 2, H * .5, H * .78);
  vg.addColorStop(0, 'rgba(30,15,8,0)'); vg.addColorStop(1, `rgba(25,12,6,${o.vig ?? .62})`);
  g.save(); g.fillStyle = vg; g.fillRect(0, 0, W, H); g.restore();
  // grain (changes every frame, 4 px clumps)
  const tiles = grainTiles(); const k = Math.floor(t * 60) % tiles.length;
  g.save(); g.globalCompositeOperation = 'overlay'; g.globalAlpha = o.grain ?? .07;
  g.drawImage(tiles[k], -((t * 997) % 40), -((t * 613) % 40), W + 60, H + 100); g.restore();
  if (o.fade) { g.save(); g.fillStyle = `rgba(8,5,4,${o.fade})`; g.fillRect(0, 0, W, H); g.restore(); }
}

// ---------------------------------------------------------------- offscreen helpers (DOF, transitions)
const POOL = [];
function off() { return POOL.pop() || createCanvas(W, H); }
function release(cv) { POOL.push(cv); }
function blurred(g, px, fn, alpha = 1) {
  const cv = off(), c2 = cv.getContext('2d'); c2.setTransform(1, 0, 0, 1, 0, 0); c2.clearRect(0, 0, W, H);
  fn(c2);
  g.save(); g.globalAlpha = alpha; g.filter = `blur(${px}px)`; g.drawImage(cv, 0, 0); g.filter = 'none'; g.restore();
  release(cv);
}

module.exports = { layer, paper, grade, lights, finish, off, release, blurred, GRADES };
