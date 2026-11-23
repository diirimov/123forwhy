// ---------- core: timing, math, camera, text, post ----------
const W = 1080, H = 1920, FPS = 60, DUR = 90;
const BPM = 128, BEAT = 60 / BPM, BAR = BEAT * 4, S16 = BEAT / 4;
const TB = (bar, step = 0) => (bar - 1) * BAR + step * S16;

const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a, b, t) => a + (b - a) * t;
const prog = (t, a, b) => clamp((t - a) / (b - a));
const TAU = Math.PI * 2;
const E = {
  lin: t => t,
  in: t => t * t * t,
  out: t => 1 - Math.pow(1 - t, 3),
  out5: t => 1 - Math.pow(1 - t, 5),
  inOut: t => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2,
  sine: t => -(Math.cos(Math.PI * t) - 1) / 2,
  outBack: t => { const c1 = 1.9, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); },
  outElastic: t => t === 0 ? 0 : t === 1 ? 1 : Math.pow(2, -10 * t) * Math.sin((t * 10 - .75) * TAU / 3) + 1,
  expo: t => t === 1 ? 1 : 1 - Math.pow(2, -10 * t),
};
function hash(n) { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453123; return x - Math.floor(x); }
function hash2(a, b) { return hash(a * 57.3 + b * 113.9); }
function vnoise(x) { const i = Math.floor(x), f = x - i, u = f * f * (3 - 2 * f); return lerp(hash(i), hash(i + 1), u) * 2 - 1; }
function fbm(x) { return vnoise(x) * .6 + vnoise(x * 2.1 + 5) * .3 + vnoise(x * 4.3 + 9) * .1; }
function rngFrom(seed) { let s = seed >>> 0 || 1; return () => { s ^= s << 13; s ^= s >>> 17; s ^= s << 5; return ((s >>> 0) % 100000) / 100000; }; }

// ---------- music map ----------
function kickSteps(bar) {
  if (bar < 1 || bar > 48) return [];
  if ([8, 24, 32, 40].includes(bar)) return [0, 4, 8];
  if (bar === 16) return [0, 4, 8, 12, 14];
  if (bar === 36) return [0];
  if (bar === 48) return [0, 3, 6, 12];
  return [0, 4, 8, 12];
}
const KICKS = []; for (let b = 1; b <= 48; b++) for (const s of kickSteps(b)) KICKS.push(TB(b, s));
function sinceLast(t, list) { let best = 1e9; for (const k of list) { if (k <= t && t - k < best) best = t - k; } return best; }
function kickEnv(t, dec = 0.14) { const d = sinceLast(t, KICKS); return d > 2 ? 0 : Math.exp(-d / dec); }
function beatPhase(t) { return (t / BEAT) % 1; }
function bounce(t, amt = 1) { const p = beatPhase(t); return -Math.abs(Math.sin(p * Math.PI)) * amt; }
const SECTION_HITS = [TB(5), TB(9), TB(17), TB(25), TB(29), TB(33), TB(36), TB(41), TB(48, 12)];

// ---------- canvas helpers ----------
function mkCanvas(w, h) { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; }
const INK = '#160e12';
function rr(ctx, x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }
function ell(ctx, x, y, rx, ry, rot = 0) { ctx.beginPath(); ctx.ellipse(x, y, Math.abs(rx), Math.abs(ry), rot, 0, TAU); }
function fillStroke(ctx, fill, lw = 5, stroke = INK) {
  if (fill) { ctx.fillStyle = fill; ctx.fill(); }
  if (lw > 0) { ctx.lineWidth = lw; ctx.strokeStyle = stroke; ctx.lineJoin = 'round'; ctx.lineCap = 'round'; ctx.stroke(); }
}
function limb(ctx, pts, w, color, lw = 5) {
  ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  ctx.beginPath(); ctx.moveTo(pts[0][0], pts[0][1]); for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1]);
  ctx.strokeStyle = INK; ctx.lineWidth = w + lw * 2; ctx.stroke();
  ctx.strokeStyle = color; ctx.lineWidth = w; ctx.stroke();
}
function shade(hex, f) { // f<0 darker, f>0 lighter
  const n = parseInt(hex.slice(1), 16); let r = n >> 16, g = (n >> 8) & 255, b = n & 255;
  if (f < 0) { r *= 1 + f; g *= 1 + f; b *= 1 + f; } else { r += (255 - r) * f; g += (255 - g) * f; b += (255 - b) * f; }
  return `rgb(${r | 0},${g | 0},${b | 0})`;
}
function mix(h1, h2, t) {
  const a = parseInt(h1.slice(1), 16), b = parseInt(h2.slice(1), 16);
  const r = lerp(a >> 16, b >> 16, t), g = lerp((a >> 8) & 255, (b >> 8) & 255, t), bl = lerp(a & 255, b & 255, t);
  return '#' + ((1 << 24) + ((r | 0) << 16) + ((g | 0) << 8) + (bl | 0)).toString(16).slice(1);
}
function vgrad(ctx, y0, y1, stops) { const g = ctx.createLinearGradient(0, y0, 0, y1); stops.forEach(([o, c]) => g.addColorStop(o, c)); return g; }
function glow(ctx, x, y, r, color, a = 1) {
  const g = ctx.createRadialGradient(x, y, 0, x, y, r);
  g.addColorStop(0, color); g.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.save(); ctx.globalAlpha *= a; ctx.globalCompositeOperation = 'lighter'; ctx.fillStyle = g; ctx.fillRect(x - r, y - r, r * 2, r * 2); ctx.restore();
}

// ---------- camera ----------
// cam: {x,y,z,r} world point at screen center, zoom z, rotation r (rad)
function applyCam(ctx, cam, par = 1) {
  ctx.translate(W / 2, H / 2);
  ctx.rotate(cam.r || 0);
  const z = 1 + ((cam.z || 1) - 1) * par;
  ctx.scale(z, z);
  ctx.translate(-(cam.x || 0) * par, -(cam.y || 0) * par);
}
function shakeAt(t, hits, amp = 18, dec = .25) {
  let x = 0, y = 0, r = 0;
  for (const h of hits) {
    const d = t - h; if (d < 0 || d > 1) continue;
    const a = amp * Math.exp(-d / dec);
    x += vnoise(d * 40 + h * 3) * a; y += vnoise(d * 37 + h * 7 + 50) * a; r += vnoise(d * 30 + h) * a * .0012;
  }
  return { x, y, r };
}

// ---------- typography ----------
const FONTS = {
  goth: "'Pirata One'", cin: "'Cinzel'", fell: "'IM Fell English'", fellsc: "'IM Fell English SC'", inter: "'Inter'",
};
// draw text with layered ink outline, colored glow, drop shadow
function fancyText(ctx, str, x, y, o) {
  const size = o.size || 100;
  ctx.save();
  ctx.font = `${o.weight || ''} ${size}px ${o.font || FONTS.cin}`;
  ctx.textAlign = o.align || 'center'; ctx.textBaseline = 'middle';
  ctx.letterSpacing = (o.track || 0) + 'px';
  ctx.lineJoin = 'round';
  if (o.shadow !== false) {
    ctx.fillStyle = 'rgba(0,0,0,.55)'; ctx.fillText(str, x + size * .05, y + size * .07);
  }
  if (o.glow) { ctx.shadowColor = o.glow; ctx.shadowBlur = o.glowR || size * .4; }
  ctx.strokeStyle = o.stroke || INK; ctx.lineWidth = o.strokeW == null ? size * .14 : o.strokeW;
  if (ctx.lineWidth > 0) ctx.strokeText(str, x, y);
  ctx.shadowBlur = 0;
  if (o.grad) {
    const m = ctx.measureText(str);
    const g = ctx.createLinearGradient(0, y - size * .5, 0, y + size * .5);
    o.grad.forEach(([p, c]) => g.addColorStop(p, c)); ctx.fillStyle = g;
  } else ctx.fillStyle = o.color || '#f3e6c8';
  ctx.fillText(str, x, y);
  if (o.inner) { // subtle top highlight
    ctx.globalCompositeOperation = 'source-atop';
  }
  ctx.restore();
}
function measure(ctx, str, o) {
  ctx.save(); ctx.font = `${o.weight || ''} ${o.size || 100}px ${o.font || FONTS.cin}`; ctx.letterSpacing = (o.track || 0) + 'px';
  const w = ctx.measureText(str).width; ctx.restore(); return w;
}
// slam-in animation: returns {s, a, dy, rot}
function slam(lt, dur = .28) {
  if (lt < 0) return null;
  const p = clamp(lt / dur);
  return { s: lerp(1.9, 1, E.out5(p)) + (p >= 1 ? 0 : 0), a: clamp(p * 3), rot: (1 - E.out(p)) * -0.08 };
}
let NOTEXT = false;
// caption plate: words pop on, holds, exits. times relative.
function caption(ctx, lines, t, tIn, tOut, o = {}) {
  if (NOTEXT) return;
  if (t < tIn || t > tOut + .4) return;
  const lt = t - tIn, out = clamp((t - tOut) / .3);
  const size = o.size || 92, lh = size * 1.12;
  const y0 = o.y || 980;
  ctx.save();
  ctx.globalAlpha = 1 - E.in(out);
  const tot = lines.length * lh;
  // backing plate
  if (o.plate !== false) {
    const pw = Math.max(...lines.map(l => measure(ctx, l, { size, weight: 900, font: FONTS.cin, track: o.track || 2 }))) + 120;
    const pp = E.out5(clamp(lt / .25));
    ctx.save(); ctx.translate(W / 2, y0); ctx.rotate(o.plateRot || -0.02);
    ctx.globalAlpha *= .78 * pp;
    ctx.fillStyle = o.plateColor || 'rgba(12,6,8,.85)';
    ctx.beginPath(); const hw = pw / 2 * pp, hh = tot / 2 + 34;
    ctx.moveTo(-hw - 10, -hh + 6); ctx.lineTo(hw + 14, -hh); ctx.lineTo(hw, hh + 4); ctx.lineTo(-hw, hh); ctx.closePath(); ctx.fill();
    ctx.restore();
  }
  lines.forEach((ln, i) => {
    const words = ln.split(' ');
    const full = measure(ctx, ln, { size, weight: 900, font: FONTS.cin, track: o.track || 2 });
    let cx = W / 2 - full / 2;
    const y = y0 - tot / 2 + lh * (i + .5);
    words.forEach((wd, j) => {
      const ww = measure(ctx, wd, { size, weight: 900, font: FONTS.cin, track: o.track || 2 });
      const sp = measure(ctx, ' ', { size, weight: 900, font: FONTS.cin, track: o.track || 2 });
      const wdel = (o.wordStep == null ? .07 : o.wordStep) * (i * words.length + j);
      const s = slam(lt - wdel, .22);
      if (s) {
        ctx.save(); ctx.translate(cx + ww / 2, y); ctx.scale(s.s, s.s); ctx.rotate(s.rot * .5); ctx.globalAlpha *= s.a;
        fancyText(ctx, wd, 0, 0, { size, weight: 900, font: FONTS.cin, color: o.color || '#f6ead0', stroke: INK, strokeW: size * .12, track: o.track || 2, glow: o.glow, glowR: o.glowR });
        ctx.restore();
      }
      cx += ww + sp;
    });
  });
  ctx.restore();
}

// ---------- post ----------
let GRAIN = null;
function makeGrain() {
  GRAIN = [];
  for (let k = 0; k < 6; k++) {
    const c = mkCanvas(540, 960), g = c.getContext('2d'), id = g.createImageData(540, 960);
    const r = rngFrom(99 + k * 7);
    for (let i = 0; i < id.data.length; i += 4) { const v = 128 + (r() - .5) * 90; id.data[i] = id.data[i + 1] = id.data[i + 2] = v; id.data[i + 3] = 255; }
    g.putImageData(id, 0, 0); GRAIN.push(c);
  }
}
let PAPER = null;
function makePaper() {
  PAPER = mkCanvas(1080, 1920); const g = PAPER.getContext('2d');
  g.fillStyle = '#808080'; g.fillRect(0, 0, W, H);
  const r = rngFrom(4242);
  for (let i = 0; i < 2600; i++) {
    const x = r() * W, y = r() * H, rad = 20 + r() * 160;
    const gr = g.createRadialGradient(x, y, 0, x, y, rad); const v = r() > .5 ? 255 : 0;
    gr.addColorStop(0, `rgba(${v},${v},${v},${.03 + r() * .03})`); gr.addColorStop(1, 'rgba(128,128,128,0)');
    g.fillStyle = gr; g.fillRect(x - rad, y - rad, rad * 2, rad * 2);
  }
  for (let i = 0; i < 400; i++) { // fibers
    g.strokeStyle = `rgba(${r() > .5 ? 255 : 0},${r() > .5 ? 255 : 0},${r() > .5 ? 255 : 0},.05)`; g.lineWidth = 1;
    const x = r() * W, y = r() * H; g.beginPath(); g.moveTo(x, y); g.quadraticCurveTo(x + r() * 40 - 20, y + r() * 40 - 20, x + r() * 80 - 40, y + r() * 80 - 40); g.stroke();
  }
}
function post(ctx, t, o = {}) {
  ctx.save();
  // paper texture
  ctx.globalCompositeOperation = 'overlay'; ctx.globalAlpha = o.paper == null ? .35 : o.paper; ctx.drawImage(PAPER, 0, 0);
  // vignette
  ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = 1;
  const v = ctx.createRadialGradient(W / 2, H * .46, H * .28, W / 2, H * .5, H * .78);
  v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, `rgba(0,0,0,${o.vig == null ? .62 : o.vig})`);
  ctx.fillStyle = v; ctx.fillRect(0, 0, W, H);
  // grain (12 fps flicker)
  const gi = Math.floor(t * 12) % GRAIN.length;
  ctx.globalCompositeOperation = 'overlay'; ctx.globalAlpha = o.grain == null ? .22 : o.grain;
  ctx.drawImage(GRAIN[gi], 0, 0, W, H);
  ctx.restore();
}
