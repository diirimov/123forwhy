// WORLD: the bronze bull sculpture, ancient courtyard, bronze interior.
'use strict';

// ------------------------------------------------------------------ BRONZE BULL (side profile, facing left)
// local units: ground y=0, hump ~ -600, nose x ~ -490, tail x ~ +390
const BULL = {
  body: [[-528, -290], [-512, -336], [-488, -392], [-462, -428], [-430, -448], [-372, -512], [-300, -578], [-220, -612], [-150, -612], [-60, -574],
  [60, -540], [190, -528], [292, -532], [350, -510], [384, -452], [384, -370], [360, -300], [300, -262], [220, -268], [110, -252],
  [-20, -232], [-150, -212], [-262, -184], [-318, -196], [-352, -236], [-392, -268], [-438, -262], [-478, -232], [-512, -226], [-532, -250]],
  legFN: [[-336, -262], [-250, -256], [-236, -160], [-246, -122], [-240, -48], [-232, -12], [-226, 0], [-296, 0], [-290, -14], [-288, -48], [-292, -122], [-306, -160], [-334, -214]],
  legFF: [[-264, -236], [-188, -230], [-182, -152], [-190, -118], [-186, -44], [-176, 0], [-238, 0], [-234, -44], [-238, -118], [-248, -152]],
  legHN: [[186, -434], [362, -424], [378, -330], [360, -252], [350, -186], [364, -150], [348, -128], [322, -70], [318, -22], [328, 0], [266, 0], [270, -24], [272, -74], [290, -142], [282, -194], [248, -262], [196, -330]],
  legHF: [[130, -330], [262, -306], [262, -226], [270, -164], [258, -132], [240, -72], [238, 0], [186, 0], [190, -72], [206, -140], [190, -222]],
  hornN: [[-446, -432], [-474, -470], [-522, -508], [-562, -556], [-576, -608], [-556, -618], [-540, -574], [-500, -526], [-450, -486], [-416, -456]],
  hornF: [[-402, -458], [-412, -502], [-392, -562], [-360, -602], [-346, -598], [-370, -552], [-380, -498], [-384, -460]],
  ear: [[-420, -424], [-370, -436], [-338, -422], [-370, -408], [-412, -404]],
  tail: [[350, -502], [394, -440], [406, -320], [400, -200], [396, -132]],
  dewlap: [[-330, -236], [-372, -232], [-412, -246], [-448, -246], [-420, -268], [-380, -270], [-346, -258]],
};

function bullBronze(g, o = {}) {
  const glowA = o.glow ?? 0.6, t = o.t || 0;
  g.save(); g.lineJoin = 'round';
  const base = '#120804', mid = '#33200f', hi = '#8a5a2a';
  const metal = (pts, dark) => {
    g.fillStyle = linGrad(g, 0, -640, 0, 0, [[0, mix(mid, hi, 0.35)], [0.35, mid], [1, base]]);
    g.beginPath(); crPath(g, pts, true); g.fill();
    if (dark) { g.fillStyle = rgba('#000000', dark); g.fill(); }
  };
  metal(BULL.legFF, 0.5); metal(BULL.legHF, 0.5); metal(BULL.hornF, 0.4);
  brush(g, curvePts(BULL.tail, 20), 24, 12, '#2e1a0c', false);
  g.fillStyle = '#24140a'; g.beginPath(); crPath(g, [[378, -150], [412, -140], [426, -80], [400, -46], [374, -70], [368, -120]], true); g.fill();
  metal(BULL.legFN); metal(BULL.legHN);
  if (glowA > 0) for (const L of [BULL.legFN, BULL.legHN, BULL.legFF, BULL.legHF]) { g.save(); g.beginPath(); crPath(g, L, true); g.clip(); g.globalCompositeOperation = 'screen';
    g.fillStyle = linGrad(g, 0, 0, 0, -200, [[0, rgba('#ff6a1a', 0.42 * glowA)], [1, rgba('#ff6a1a', 0)]]); g.fillRect(-600, -320, 1060, 330); g.restore(); }
  metal(BULL.dewlap, 0.15); metal(BULL.body);
  // sculpted volumes
  const vol = (pts, blur, fn) => softIn(g, pts, blur, fn);
  vol(BULL.body, 34, () => {
    g.fillStyle = rgba('#000000', 0.7); g.beginPath(); g.ellipse(40, -240, 430, 60, 0, 0, 6.283); g.fill();
    g.fillStyle = rgba('#000000', 0.55); g.beginPath(); g.ellipse(170, -360, 80, 140, 0.25, 0, 6.283); g.fill();
    g.fillStyle = rgba('#000000', 0.55); g.beginPath(); g.ellipse(-330, -330, 60, 120, -0.4, 0, 6.283); g.fill();
    g.fillStyle = rgba('#ffcf8a', 0.32); g.beginPath(); g.ellipse(-220, -545, 130, 55, -0.25, 0, 6.283); g.fill();
    g.fillStyle = rgba('#ffcf8a', 0.20); g.beginPath(); g.ellipse(-210, -400, 90, 110, 0.25, 0, 6.283); g.fill();
    g.fillStyle = rgba('#ffcf8a', 0.20); g.beginPath(); g.ellipse(280, -460, 90, 70, 0, 0, 6.283); g.fill();
    g.fillStyle = rgba('#000000', 0.5); g.beginPath(); g.ellipse(-470, -330, 50, 60, 0, 0, 6.283); g.fill();
    // cool sky reflection on the top planes (polished metal)
    g.fillStyle = rgba('#8aa0c0', 0.16); g.beginPath(); g.ellipse(-120, -610, 300, 40, -0.05, 0, 6.283); g.fill();
  });
  vol(BULL.legHN, 16, () => { g.fillStyle = rgba('#ffcf8a', 0.22); g.beginPath(); g.ellipse(300, -360, 50, 70, 0, 0, 6.283); g.fill(); g.fillStyle = rgba('#000', 0.5); g.fillRect(250, -150, 140, 160); });
  vol(BULL.legFN, 14, () => { g.fillStyle = rgba('#ffcf8a', 0.18); g.beginPath(); g.ellipse(-280, -210, 30, 50, 0, 0, 6.283); g.fill(); g.fillStyle = rgba('#000', 0.45); g.fillRect(-310, -110, 100, 120); });
  // verdigris patina settling in the recesses (aged bronze)
  softIn(g, BULL.body, 22, () => { g.fillStyle = rgba('#3f6a5a', 0.16); [[-330, -300, 50, 70], [150, -300, 90, 50], [-60, -250, 120, 30], [330, -330, 30, 60]].forEach(([x, y, a, b]) => { g.beginPath(); g.ellipse(x, y, a, b, 0, 0, 6.283); g.fill(); }); });
  // specular streaks
  const spec = (pts, w, a) => { g.save(); g.globalCompositeOperation = 'screen'; g.filter = 'blur(2.5px)'; brush(g, curvePts(pts, 32), w, w * 0.25, rgba('#ffe6b4', a)); g.restore(); };
  const sh = 0.8 + 0.2 * Math.sin(t * 0.9);
  spec([[-470, -420], [-400, -480], [-320, -556], [-230, -604], [-150, -604]], 11, 0.85 * sh);
  spec([[-40, -566], [90, -538], [220, -528], [320, -520]], 8, 0.6 * sh);
  spec([[-270, -490], [-250, -400], [-266, -300]], 6, 0.45);
  spec([[330, -480], [360, -400], [346, -320]], 7, 0.45);
  spec([[-512, -330], [-520, -270]], 5, 0.55);
  spec([[-262, -230], [-252, -140], [-250, -40]], 5, 0.4);
  spec([[340, -300], [334, -200], [330, -100]], 5, 0.3);
  spec([[-160, -212], [-20, -228], [120, -248]], 4, 0.25);
  // horns: pale bronze with gradient tips
  g.fillStyle = linGrad(g, -570, -610, -440, -450, [[0, '#f6d7a0'], [0.4, '#b98448'], [1, '#3a2212']]); g.beginPath(); crPath(g, BULL.hornN, true); g.fill();
  spec([[-560, -600], [-530, -556], [-480, -508]], 4, 0.7);
  metal(BULL.ear, 0.25);
  // eye
  const ex = -470, ey = -372;
  g.fillStyle = '#0a0503'; g.beginPath(); g.ellipse(ex, ey, 17, 11, -0.25, 0, 6.283); g.fill();
  softIn(g, BULL.body, 8, () => { g.fillStyle = rgba('#000000', 0.8); g.beginPath(); g.ellipse(ex + 4, ey - 4, 32, 20, -0.25, 0, 6.283); g.fill(); });
  g.fillStyle = '#050201'; g.beginPath(); g.ellipse(ex, ey, 13, 8, -0.25, 0, 6.283); g.fill();
  g.fillStyle = rgba('#ffdca0', 0.85); g.beginPath(); g.ellipse(ex - 4, ey - 2, 3, 2, -0.25, 0, 6.283); g.fill();
  if (o.eyeGlow) { glow(g, ex, ey, 70, '#ff7a1a', o.eyeGlow); g.fillStyle = rgba('#ffb04a', o.eyeGlow); g.beginPath(); g.ellipse(ex, ey, 9, 5, -0.25, 0, 6.283); g.fill(); }
  // heavy brow ridge over the eye
  g.save(); g.globalCompositeOperation = 'screen'; g.filter = 'blur(2px)'; brush(g, [[ex - 34, ey - 20], [ex - 4, ey - 30], [ex + 30, ey - 26]], 7, 3, rgba('#ffd090', 0.55)); g.restore();
  g.fillStyle = '#0a0503'; g.beginPath(); g.ellipse(-520, -288, 10, 7, 0.4, 0, 6.283); g.fill();
  g.strokeStyle = rgba('#0a0503', 0.85); g.lineWidth = 3; g.beginPath(); g.moveTo(-530, -254); g.quadraticCurveTo(-500, -246, -470, -252); g.stroke();
  // casting seams
  g.strokeStyle = rgba('#0a0503', 0.4); g.lineWidth = 2;
  g.beginPath(); crPath(g, [[-110, -596], [-96, -420], [-120, -222]], false); g.stroke();
  g.beginPath(); crPath(g, [[160, -534], [172, -400], [150, -256]], false); g.stroke();
  // fire bounce from below: one smooth gradient, clipped per part
  if (glowA > 0) {
    for (const pts of [BULL.body]) {
      g.save(); g.beginPath(); crPath(g, pts, true); g.clip(); g.globalCompositeOperation = 'screen';
      g.fillStyle = linGrad(g, 0, 0, 0, -430, [[0, rgba('#ff6a1a', 0.75 * glowA)], [0.35, rgba('#ff6a1a', 0.35 * glowA)], [1, rgba('#ff6a1a', 0)]]);
      g.fillRect(-600, -470, 1060, 480); g.restore();
    }
  }
  g.restore();
}

// draw bull into its own layer, then add a crisp rim light along the silhouette
function bullLayer(ctx, x, y, sc, opt = {}) {
  const L = cvs('bull'), g = L.getContext('2d');
  g.save(); g.translate(x, y); g.scale(sc * (opt.flip ? -1 : 1), sc); bullBronze(g, opt); g.restore();
  ctx.drawImage(L, 0, 0);
  const rims = opt.rims || [[-7 * sc, 5 * sc, '#ffb46a', 0.85], [9 * sc, 0, '#ff7a30', 0.45]];
  for (const [dx, dy, col, a] of rims) {
    const e = cvs('bullrim'), eg = e.getContext('2d');
    eg.drawImage(L, 0, 0); eg.globalCompositeOperation = 'source-in'; eg.fillStyle = col; eg.fillRect(0, 0, W, H);
    eg.globalCompositeOperation = 'destination-out'; eg.drawImage(L, dx, dy); eg.globalCompositeOperation = 'source-over';
    ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.globalAlpha = a; ctx.filter = 'blur(1px)'; ctx.drawImage(e, 0, 0);
    ctx.globalAlpha = a * 0.5; ctx.filter = 'blur(8px)'; ctx.drawImage(e, 0, 0); ctx.restore();
  }
}

// plinth (stone base the bull stands on)
function plinth(g, w = 1000, h = 120) {
  g.fillStyle = linGrad(g, 0, 0, 0, h, [[0, '#5c5047'], [1, '#2a231e']]); g.fillRect(-w / 2, 0, w, h);
  g.fillStyle = '#6f6258'; g.fillRect(-w / 2 - 20, 0, w + 40, 18);
  g.fillStyle = linGrad(g, 0, h, 0, h + 60, [[0, '#3a312a'], [1, '#1d1814']]); g.fillRect(-w / 2 - 60, h, w + 120, 60);
  // stone joints
  g.strokeStyle = 'rgba(0,0,0,0.35)'; g.lineWidth = 2;
  for (let x = -w / 2 + 160; x < w / 2; x += 200) { g.beginPath(); g.moveTo(x, 18); g.lineTo(x, h); g.stroke(); }
}

// ------------------------------------------------------------------ COURTYARD
function column(g, x, y, w, h, lit = 0.5) {
  // Doric column with fluting, entasis, capital
  g.save(); g.translate(x, y);
  const sh = [[-w * 0.5, 0], [-w * 0.46, -h * 0.5], [-w * 0.4, -h], [w * 0.4, -h], [w * 0.46, -h * 0.5], [w * 0.5, 0]];
  g.fillStyle = linGrad(g, -w / 2, 0, w / 2, 0, [[0, '#1d1815'], [0.3, mix('#4a4038', '#c9a57a', lit * 0.6)], [0.55, '#3a322c'], [1, '#141110']]);
  g.beginPath(); g.moveTo(sh[0][0], 0); g.lineTo(sh[2][0], -h); g.lineTo(sh[3][0], -h); g.lineTo(sh[5][0], 0); g.closePath(); g.fill();
  g.strokeStyle = 'rgba(0,0,0,0.28)'; g.lineWidth = Math.max(1, w * 0.018);
  for (let k = 1; k < 9; k++) { const u = k / 9 - 0.5; g.beginPath(); g.moveTo(u * w * 0.98, 0); g.lineTo(u * w * 0.8, -h); g.stroke(); }
  // capital
  g.fillStyle = '#3e352e'; g.fillRect(-w * 0.62, -h - w * 0.16, w * 1.24, w * 0.16);
  g.fillStyle = '#2b2420'; g.beginPath(); g.moveTo(-w * 0.42, -h); g.quadraticCurveTo(-w * 0.62, -h - 4, -w * 0.56, -h - w * 0.12); g.lineTo(w * 0.56, -h - w * 0.12); g.quadraticCurveTo(w * 0.62, -h - 4, w * 0.42, -h); g.fill();
  g.restore();
}

function courtyard(ctx, cam, t, opt = {}) {
  // cam: {x, y, s (scale), hz (horizon y in screen), bullX, bullY, bullS}
  const hz = cam.hz;
  // sky: deep dusk with smoke haze
  ctx.fillStyle = linGrad(ctx, 0, 0, 0, hz, [[0, '#08070b'], [0.6, '#17121a'], [1, '#3a2418']]); ctx.fillRect(0, 0, W, hz + 2);
  // haze + smoke bands
  for (let i = 0; i < 4; i++) { const y = hz - 120 - i * 160 + Math.sin(t * 0.2 + i) * 10; ctx.save(); ctx.globalAlpha = 0.18; ctx.filter = 'blur(40px)';
    ctx.fillStyle = i % 2 ? '#4a3020' : '#2a2026'; ctx.beginPath(); ctx.ellipse(W / 2 + Math.sin(t * 0.1 + i * 2) * 200 + cam.x * 0.1, y, 700, 60, 0, 0, 6.283); ctx.fill(); ctx.restore(); }
  // distant temple silhouette (parallax 0.2)
  ctx.save(); ctx.translate(W / 2 - cam.x * 0.2, hz);
  const ts = 0.9 * cam.s;
  ctx.fillStyle = '#1a1416';
  ctx.beginPath(); ctx.moveTo(-360 * ts, -300 * ts); ctx.lineTo(0, -420 * ts); ctx.lineTo(360 * ts, -300 * ts); ctx.closePath(); ctx.fill();
  ctx.fillRect(-380 * ts, -300 * ts, 760 * ts, 40 * ts);
  for (let k = 0; k < 8; k++) ctx.fillRect((-330 + k * 92) * ts, -262 * ts, 34 * ts, 262 * ts);
  ctx.restore();
  // colonnade (parallax 0.5)
  ctx.save(); ctx.translate(W / 2 - cam.x * 0.5, hz + 30 * cam.s);
  const cs = cam.s * 1.15;
  ctx.fillStyle = '#181312'; ctx.fillRect(-900 * cs, -760 * cs, 1800 * cs, 90 * cs);
  for (let k = -5; k <= 5; k++) column(ctx, k * 170 * cs, 0, 70 * cs, 670 * cs, 0.3 + 0.4 * Math.exp(-Math.abs(k) * 0.4));
  ctx.restore();
  // floor: stone slabs in perspective, warm light pool under the bull
  ctx.fillStyle = linGrad(ctx, 0, hz, 0, H, [[0, '#2a221d'], [1, '#100c0a']]); ctx.fillRect(0, hz, W, H - hz);
  floorSlabs(ctx, hz, cam.x);
  const bx = cam.bullX, by = cam.bullY;
  glow(ctx, bx, by + 40, 520 * cam.bullS, '#ff7a2a', 0.35 * (opt.fire ?? 1));
  // the bull
  ctx.save(); ctx.translate(bx, by); ctx.scale(cam.bullS, cam.bullS); plinth(ctx); ctx.restore();
  bullLayer(ctx, bx, by, cam.bullS, { glow: opt.fire ?? 1, t, eyeGlow: opt.eyeGlow || 0, flip: opt.flip });
  // embers rising from under the plinth
  motes(ctx, t, 60, 7, { x0: bx - 380 * cam.bullS, x1: bx + 380 * cam.bullS, y0: by - 40, y1: by + 80, vy: -120, vx: 10, size: [1, 3], col: '#ffb060', a: 0.85 * (opt.fire ?? 1), life: 3.5 });
  // floating dust in the air
  motes(ctx, t, 50, 11, { vy: -12, vx: 6, size: [0.8, 2.2], col: '#e8c9a0', a: 0.35, life: 9 });
}

function floorSlabs(ctx, hz, camx) {
  const r = mulberry(77);
  ctx.save();
  let y = hz, row = 0;
  while (y < H + 40) {
    const depth = (y - hz) / (H - hz), hgt = 10 + Math.pow(depth, 1.6) * 260, sc = 0.15 + depth * 1.6;
    let x = -((camx * (0.6 + depth)) % (220 * sc)) - r() * 120 * sc - 60;
    while (x < W + 60) {
      const w = (150 + r() * 140) * sc;
      const tone = 0.08 + r() * 0.07;
      ctx.fillStyle = rgba('#8a7563', tone * (0.6 + depth));
      ctx.fillRect(x + 2, y + 1, w - 3, hgt - 2);
      ctx.fillStyle = rgba('#000000', 0.35); ctx.fillRect(x, y, 2.5 * sc + 0.5, hgt); ctx.fillRect(x, y, w, 1.5 + sc);
      x += w;
    }
    y += hgt; row++;
  }
  ctx.restore();
}

// ------------------------------------------------------------------ BRONZE INTERIOR (curved hammered wall)
function bronzeInterior(ctx, t, opt = {}) {
  const ox = opt.ox || 0, oy = opt.oy || 0;
  ctx.fillStyle = '#0b0705'; ctx.fillRect(0, 0, W, H);
  // curved ribs of the hollow body (concentric arcs)
  for (let k = 0; k < 9; k++) {
    const y = -400 + k * 330 + oy;
    ctx.save(); ctx.strokeStyle = rgba('#5a3519', 0.5 - k * 0.03); ctx.lineWidth = 40;
    ctx.beginPath(); ctx.ellipse(W / 2 + ox, y, 1100, 260, 0, Math.PI * 0.05, Math.PI * 0.95); ctx.stroke();
    ctx.strokeStyle = rgba('#d89a52', 0.10); ctx.lineWidth = 4; ctx.beginPath(); ctx.ellipse(W / 2 + ox, y - 18, 1100, 260, 0, Math.PI * 0.1, Math.PI * 0.9); ctx.stroke();
    ctx.restore();
  }
  // hammered texture
  const r = mulberry(5);
  ctx.save(); ctx.globalCompositeOperation = 'screen';
  for (let i = 0; i < 260; i++) { const x = r() * W, y = r() * H, rr = 10 + r() * 30; ctx.fillStyle = rgba('#b0703a', 0.03 + r() * 0.04); ctx.beginPath(); ctx.ellipse(x + ox * 0.5, y + oy * 0.5, rr, rr * 0.7, r() * 3, 0, 6.283); ctx.fill(); }
  ctx.restore();
}

TESTS.court = (ctx, t) => {
  courtyard(ctx, { x: 0, y: 0, s: 1.25, hz: 1330, bullX: 640, bullY: 1500, bullS: 0.98 }, t, { fire: 1, eyeGlow: 0.3 });
  vignette(ctx, 0.85); grain(ctx, 0, 0.06);
};
