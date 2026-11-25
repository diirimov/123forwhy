// ANATOMY: custom medical illustrations with their own visual identity
// (deep navy field, crimson arteries, blue veins, gold nerves, restrained cyan accents).
'use strict';

// ------------------------------------------------------------------ background field
function anatomyField(ctx, t, opt = {}) {
  const warm = opt.warm || 0;
  ctx.fillStyle = radGrad(ctx, W / 2, H * 0.45, 50, H * 0.8, [[0, mix('#13233a', '#3a1a14', warm)], [0.6, mix('#0a1322', '#1c0c0a', warm)], [1, '#04070d']]);
  ctx.fillRect(0, 0, W, H);
  // faint technical grid
  ctx.save(); ctx.globalAlpha = 0.06 + 0.02 * Math.sin(t); ctx.strokeStyle = warm > 0.5 ? '#ff9a5a' : '#7fd6ff'; ctx.lineWidth = 1;
  for (let x = 60; x < W; x += 80) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }
  for (let y = 40; y < H; y += 80) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }
  ctx.restore();
  motes(ctx, t, 40, 3, { vy: -10, vx: 4, size: [0.8, 2], col: warm > 0.5 ? '#ffb07a' : '#9fdcff', a: 0.35, life: 10 });
}

// ------------------------------------------------------------------ BODY FIGURE (front view), height 1500 units, origin at pelvis
const BODY_R = [[0, -750], [50, -742], [78, -704], [86, -652], [80, -602], [64, -566], [48, -540], [52, -506], [110, -484], [170, -462],
[202, -420], [214, -330], [224, -236], [232, -164], [246, -64], [258, 26], [276, 62], [288, 112], [272, 150], [250, 132], [240, 84],
[226, 44], [206, -60], [190, -172], [172, -300], [152, -376], [142, -330], [122, -172], [140, -62], [150, 6], [146, 120], [118, 320],
[124, 426], [88, 640], [104, 700], [112, 742], [34, 750], [40, 700], [46, 480], [52, 322], [36, 120], [0, 44]];
const BODY = BODY_R.concat(BODY_R.slice(1, -1).reverse().map(([x, y]) => [-x, y]));

function bodySil(g, opt = {}) {
  const fill = opt.fill || 'rgba(127,214,255,0.08)', edge = opt.edge || '#7fd6ff', ea = opt.edgeA ?? 0.8, t = opt.t || 0;
  g.save(); g.lineJoin = 'round';
  g.fillStyle = fill; g.beginPath(); crPath(g, BODY, true, 0.45); g.fill();
  // inner volume shading
  softIn(g, BODY, 30, () => { g.fillStyle = rgba(opt.inner || '#7fd6ff', 0.10); g.fillRect(-60, -760, 120, 1520);
    g.fillStyle = rgba('#000000', 0.25); for (const sx of [-1, 1]) { g.beginPath(); g.ellipse(sx * 140, -200, 50, 300, 0, 0, 6.283); g.fill(); } });
  // edge line + glow
  g.strokeStyle = rgba(edge, ea); g.lineWidth = opt.lw || 3; g.beginPath(); crPath(g, BODY, true, 0.45); g.stroke();
  g.save(); g.filter = 'blur(10px)'; g.globalAlpha = ea * 0.6; g.lineWidth = 10; g.stroke(); g.restore();
  g.restore();
}

// ------------------------------------------------------------------ SKELETAL HINT (ribcage + spine + pelvis), subtle
function skeletonHint(g, a = 0.25, col = '#cfe6ff') {
  g.save(); g.strokeStyle = rgba(col, a); g.lineCap = 'round';
  g.lineWidth = 6; g.beginPath(); g.moveTo(0, -540); g.lineTo(0, -40); g.stroke();
  for (let i = 0; i < 9; i++) { const y = -470 + i * 34, w = 70 + Math.sin((i + 1) / 10 * Math.PI) * 40;
    g.lineWidth = 4; for (const sx of [-1, 1]) { g.beginPath(); g.moveTo(sx * 8, y); g.bezierCurveTo(sx * w, y - 10, sx * (w + 14), y + 30, sx * (w - 20), y + 60); g.stroke(); } }
  g.lineWidth = 5; g.beginPath(); g.moveTo(-110, -60); g.quadraticCurveTo(0, 40, 110, -60); g.stroke();
  g.beginPath(); g.ellipse(0, -650, 70, 92, 0, 0, 6.283); g.stroke();
  g.restore();
}

// ------------------------------------------------------------------ HEART (anterior view), ~ 420 x 520 units, origin at center
const HEART = {
  ventricles: [[-150, -40], [-120, -110], [-40, -130], [60, -120], [150, -70], [180, 20], [160, 130], [100, 230], [40, 290], [10, 300], [-30, 250], [-110, 150], [-160, 50]],
  ra: [[-190, -150], [-150, -190], [-110, -170], [-100, -90], [-130, -20], [-180, -10], [-210, -70]],
  la: [[100, -140], [150, -160], [176, -126], [162, -92], [120, -96]],
  aorta: [[-40, -120], [-50, -250], [-30, -330], [40, -370], [120, -360], [180, -300], [190, -220], [150, -210], [140, -280], [80, -310], [30, -300], [10, -250], [20, -130]],
  pulm: [[10, -120], [20, -220], [70, -260], [130, -250], [140, -210], [90, -210], [60, -160], [60, -110]],
  svc: [[-150, -180], [-150, -340], [-96, -340], [-100, -180]],
};
function heartAnt(g, opt = {}) {
  const beat = opt.beat || 0, stress = opt.stress || 0, t = opt.t || 0;
  g.save(); g.lineJoin = 'round';
  const sq = 1 - beat * 0.06;
  g.scale(1 + beat * 0.02, sq);
  // great vessels behind
  const vfill = (pts, c1, c2) => { g.fillStyle = linGrad(g, -200, -380, 200, -100, [[0, c1], [1, c2]]); g.beginPath(); crPath(g, pts, true); g.fill(); };
  vfill(HEART.svc, '#5a8fd8', '#2a4f94');
  vfill(HEART.aorta, '#ff6a5e', '#9a1c22');
  // aortic arch branches
  [[60, -350, 46, -440, 30], [112, -356, 114, -446, 26], [160, -322, 182, -416, 24]].forEach(([x0, y0, x1, y1, w]) => {
    g.strokeStyle = '#b52c34'; g.lineWidth = w; g.lineCap = 'butt'; g.beginPath(); g.moveTo(x0, y0); g.quadraticCurveTo(lerp(x0, x1, 0.5), y0 - 30, x1, y1); g.stroke();
    g.fillStyle = '#5a0a10'; g.beginPath(); g.ellipse(x1, y1, w / 2, w / 5, 0.15, 0, 6.283); g.fill();
    g.strokeStyle = '#ff7a72'; g.lineWidth = 2; g.stroke(); });
  g.fillStyle = '#2a4f94'; g.beginPath(); g.ellipse(-123, -340, 27, 8, 0, 0, 6.283); g.fill();
  vfill(HEART.pulm, '#6a9ae0', '#3157a6');
  vfill(HEART.ra, '#4a7ccf', '#284b8f');
  vfill(HEART.la, '#c0404a', '#7a1a20');
  // ventricles (myocardium)
  g.fillStyle = radGrad(g, -40, -40, 20, 340, [[0, mix('#e0565a', '#ff7a3a', stress)], [0.55, mix('#a32630', '#c8382a', stress)], [1, '#4e0c12']], -60, -60);
  g.beginPath(); crPath(g, HEART.ventricles, true); g.fill();
  softIn(g, HEART.ventricles, 26, () => {
    g.fillStyle = rgba('#ffd0c0', 0.35); g.beginPath(); g.ellipse(-50, -40, 80, 50, -0.4, 0, 6.283); g.fill();
    g.fillStyle = rgba('#200406', 0.6); g.beginPath(); g.ellipse(120, 120, 70, 140, 0.3, 0, 6.283); g.fill();
  });
  // coronary arteries + fat in grooves
  brush(g, curvePts([[0, -120], [30, -10], [40, 110], [20, 270]], 30), 18, 8, rgba('#f2d6a0', 0.55));
  brush(g, curvePts([[0, -120], [28, -10], [38, 110], [18, 270]], 30), 7, 3, '#ff4a4a');
  brush(g, curvePts([[-120, -100], [-150, 0], [-120, 150], [-40, 260]], 30), 6, 3, '#ff4a4a');
  [[30, 20, 110, 70], [36, 120, 110, 180], [-130, 40, -60, 90]].forEach(([x0, y0, x1, y1]) => brush(g, curvePts([[x0, y0], [lerp(x0, x1, 0.5), y0 + 10], [x1, y1]], 12), 4, 1.5, '#ff5a5a'));
  brush(g, curvePts([[-100, -80], [-70, 40], [-20, 200]], 20), 4, 2, '#5a8fd8');
  // specular
  g.save(); g.globalCompositeOperation = 'screen'; g.filter = 'blur(4px)';
  brush(g, curvePts([[-110, -80], [-70, -110], [0, -112]], 16), 10, 3, rgba('#ffe0d8', 0.6));
  brush(g, curvePts([[40, -350], [100, -362], [150, -330]], 16), 8, 3, rgba('#ffe0d8', 0.6));
  g.restore();
  if (stress > 0) glow(g, 0, 60, 320, '#ff5a2a', stress * 0.35);
  g.restore();
}

// ------------------------------------------------------------------ BRAIN (lateral, facing left), ~ 560 x 420, origin center
const BRAIN = [[-270, 10], [-262, -80], [-220, -160], [-140, -214], [-40, -236], [70, -226], [170, -186], [244, -110], [272, -20], [262, 60], [220, 110],
[150, 130], [100, 120], [40, 140], [-40, 150], [-120, 140], [-200, 110], [-250, 70]];
const CEREB = [[90, 130], [150, 126], [220, 116], [250, 150], [230, 200], [160, 222], [100, 200], [80, 160]];
const STEM = [[40, 140], [80, 150], [90, 210], [80, 320], [40, 320], [44, 220]];
function brainLat(g, opt = {}) {
  const t = opt.t || 0, misfire = opt.misfire || 0, glowC = opt.glow || '#7fd6ff', hot = opt.hot || 0;
  g.save(); g.lineJoin = 'round'; g.lineCap = 'round';
  const tone = (c1, c2) => mix(c1, c2, hot);
  g.fillStyle = linGrad(g, 0, 130, 0, 320, [[0, tone('#b07a86', '#c46a54')], [1, '#4a2a30']]); g.beginPath(); crPath(g, STEM, true); g.fill();
  g.fillStyle = tone('#a86a7a', '#b8604c'); g.beginPath(); crPath(g, CEREB, true); g.fill();
  g.save(); g.beginPath(); crPath(g, CEREB, true); g.clip(); g.strokeStyle = rgba('#3a1820', 0.6); g.lineWidth = 3;
  for (let k = 0; k < 9; k++) { g.beginPath(); g.ellipse(170, 230, 170 - k * 8, 110 - k * 11, -0.15, Math.PI * 1.05, Math.PI * 1.95); g.stroke(); } g.restore();
  g.fillStyle = radGrad(g, -60, -80, 20, 360, [[0, tone('#f2c2c8', '#ffb08a')], [0.6, tone('#cf8c98', '#d8765a')], [1, tone('#7a3e4c', '#7a2a22')]]);
  g.beginPath(); crPath(g, BRAIN, true); g.fill();
  // gyri: plump rounded ridges packed over a dark sulcal base (brain-coral method)
  g.save(); g.beginPath(); crPath(g, BRAIN, true); g.clip();
  g.fillStyle = tone('#5e2232', '#6a2418'); g.fillRect(-300, -260, 600, 420);
  if (!brainLat._g) {
    const r = mulberry(61), G = [];
    for (let gx = -280; gx < 290; gx += 42) for (let gy = -250; gy < 170; gy += 38) {
      let x = gx + (r() - 0.5) * 24, y = gy + (r() - 0.5) * 20, dir = r() * 6.28, turn = (r() - 0.5) * 0.5;
      const pts = [[x, y]]; const L = 5 + Math.floor(r() * 6);
      for (let k = 0; k < L; k++) { turn += (r() - 0.5) * 0.5; turn = clamp(turn, -0.6, 0.6); dir += turn; x += Math.cos(dir) * 11; y += Math.sin(dir) * 11; pts.push([x, y]); }
      G.push(pts);
    }
    brainLat._g = G;
  }
  g.lineCap = 'round'; g.lineJoin = 'round';
  const gy0 = tone('#d89aa6', '#e08a6a'), gy1 = tone('#f4c8d0', '#ffc09a');
  for (const f of brainLat._g) { g.strokeStyle = gy0; g.lineWidth = 27; g.beginPath(); crPath(g, f, false); g.stroke(); }
  g.save(); g.globalAlpha = 0.6; for (const f of brainLat._g) { g.strokeStyle = gy1; g.lineWidth = 10; g.save(); g.translate(-3, -4); g.beginPath(); crPath(g, f, false); g.stroke(); g.restore(); } g.restore();
  // lateral (Sylvian) fissure + central sulcus
  brush(g, curvePts([[-170, 40], [-90, 10], [0, -20], [80, -60]], 30), 9, 4, '#4a1a26');
  brush(g, curvePts([[30, -230], [10, -150], [-10, -70], [0, -20]], 30), 8, 4, '#4a1a26');
  softIn(g, BRAIN, 30, () => { g.fillStyle = rgba('#ffffff', 0.18); g.beginPath(); g.ellipse(-60, -150, 160, 50, -0.2, 0, 6.283); g.fill();
    g.fillStyle = rgba('#2a0c14', 0.45); g.beginPath(); g.ellipse(120, 100, 200, 60, 0, 0, 6.283); g.fill(); });
  g.restore();
  g.strokeStyle = rgba('#3a1420', 0.7); g.lineWidth = 3; g.beginPath(); crPath(g, BRAIN, true); g.stroke();
  // neural signals: arcs of light between regions
  const r = mulberry(13);
  for (let i = 0; i < 26; i++) {
    const x0 = lerp(-220, 220, r()), y0 = lerp(-180, 90, r()), x1 = lerp(-220, 220, r()), y1 = lerp(-180, 90, r());
    const ph = r(), speed = 0.6 + r();
    let u = ((t * speed + ph) % 1);
    let a = Math.sin(Math.PI * u);
    if (misfire > 0) { const flick = hash(Math.floor(t * 14) + i * 7.3); a *= flick < misfire * 0.7 ? 0 : 1 + misfire * flick; u = clamp(u + (hash(i + Math.floor(t * 6)) - 0.5) * misfire * 0.5); }
    const cx = (x0 + x1) / 2, cy = Math.min(y0, y1) - 60;
    const px = (1 - u) * (1 - u) * x0 + 2 * (1 - u) * u * cx + u * u * x1, py = (1 - u) * (1 - u) * y0 + 2 * (1 - u) * u * cy + u * u * y1;
    g.save(); g.globalCompositeOperation = 'screen';
    g.strokeStyle = rgba(misfire > 0.4 && i % 3 === 0 ? '#ff7a4a' : glowC, 0.12 * a); g.lineWidth = 2; g.beginPath(); g.moveTo(x0, y0); g.quadraticCurveTo(cx, cy, x1, y1); g.stroke();
    glow(g, px, py, 26, misfire > 0.4 && i % 3 === 0 ? '#ff7a4a' : glowC, 0.8 * a);
    g.restore();
  }
  g.restore();
}

// ------------------------------------------------------------------ LIVER + KIDNEYS (positioned in body coords)
function liver(g, opt = {}) {
  const hot = opt.hot || 0;
  const pts = [[-170, -300], [-100, -330], [0, -320], [80, -296], [110, -270], [60, -250], [0, -230], [-80, -200], [-140, -196], [-176, -240]];
  g.fillStyle = radGrad(g, -100, -300, 10, 220, [[0, mix('#a8503a', '#e0642a', hot)], [1, mix('#4a1a10', '#7a2a10', hot)]]);
  g.beginPath(); crPath(g, pts, true); g.fill();
  softIn(g, pts, 14, () => { g.fillStyle = rgba('#ffd0b0', 0.25); g.beginPath(); g.ellipse(-90, -300, 70, 20, -0.1, 0, 6.283); g.fill(); });
  brush(g, curvePts([[-10, -320], [-20, -270], [-40, -226]], 10), 5, 2, rgba('#2a0a06', 0.7));
}
function kidney(g, x, y, sx, opt = {}) {
  const hot = opt.hot || 0;
  g.save(); g.translate(x, y); g.scale(sx, 1);
  const pts = [[0, -60], [30, -54], [44, -20], [40, 30], [22, 62], [-4, 64], [-14, 40], [-4, 14], [-6, -12], [-18, -38]];
  g.fillStyle = radGrad(g, 10, -20, 5, 80, [[0, mix('#c0505a', '#ff7040', hot)], [1, mix('#5a1420', '#7a2410', hot)]]);
  g.beginPath(); crPath(g, pts, true); g.fill();
  brush(g, [[-8, 2], [-40, 10], [-60, 40]], 7, 5, '#c63a3a', false);
  brush(g, [[-6, 8], [-24, 60], [-30, 140]], 5, 4, '#e8d0a0', false);
  g.restore();
}

// ------------------------------------------------------------------ NERVOUS SYSTEM (body coords)
const NERVES = (() => {
  const out = [];
  const r = mulberry(91);
  const add = (pts, w) => out.push({ pts: curvePts(pts, 40), w });
  // spinal cord
  add([[0, -560], [0, -400], [0, -200], [0, -40]], 9);
  for (const s of [-1, 1]) {
    add([[0, -500], [s * 90, -480], [s * 180, -430], [s * 214, -300], [s * 228, -160], [s * 244, -40], [s * 262, 60], [s * 276, 110]], 5); // arm
    add([[s * 200, -380], [s * 196, -250], [s * 214, -150], [s * 222, -40], [s * 240, 70]], 3);
    add([[0, -60], [s * 50, 0], [s * 80, 120], [s * 84, 320], [s * 90, 440], [s * 80, 640], [s * 96, 730]], 6);   // sciatic
    add([[s * 60, 40], [s * 110, 140], [s * 100, 330], [s * 110, 480], [s * 76, 700]], 3);
    for (let i = 0; i < 8; i++) { const y = -440 + i * 46; add([[s * 6, y], [s * 60, y + 6], [s * 110, y + 20], [s * 128, y + 44]], 2); }
  }
  // fine branches
  const base = out.slice();
  for (const n of base) for (let k = 0; k < n.pts.length; k += 6) {
    if (r() < 0.55) continue;
    const [x, y] = n.pts[k]; const s = x >= 0 ? 1 : -1; const L = 30 + r() * 60, a = (r() - 0.5) * 1.6 + (s > 0 ? 0.3 : Math.PI - 0.3);
    add([[x, y], [x + Math.cos(a) * L * 0.5, y + Math.sin(a) * L * 0.5 + 6], [x + Math.cos(a) * L, y + Math.sin(a) * L + 14]], 1.2);
  }
  return out;
})();
function nerves(g, t, opt = {}) {
  const col = opt.col || '#f1d08a', reveal = opt.reveal ?? 1, disturb = opt.disturb || 0;
  g.save(); g.lineCap = 'round'; g.lineJoin = 'round';
  NERVES.forEach((n, i) => {
    const m = Math.max(2, Math.floor(n.pts.length * clamp(reveal * 1.3 - (n.w < 2 ? 0.3 : 0))));
    const p = n.pts.slice(0, m);
    g.strokeStyle = rgba(col, 0.75); g.lineWidth = n.w; g.beginPath(); p.forEach(([x, y], k) => k ? g.lineTo(x, y) : g.moveTo(x, y)); g.stroke();
    if (n.w >= 3) { g.save(); g.globalCompositeOperation = 'screen'; g.filter = 'blur(6px)'; g.strokeStyle = rgba(col, 0.35); g.lineWidth = n.w * 3; g.stroke(); g.restore(); }
    // travelling impulse
    if (n.w >= 2 && reveal >= 1) {
      let u = ((t * (0.5 + (i % 5) * 0.12) + i * 0.137) % 1);
      if (disturb) u = clamp(u + Math.sin(t * 9 + i) * disturb * 0.08);
      const k = Math.floor(u * (n.pts.length - 1)); const [x, y] = n.pts[k];
      const a = disturb ? (hash(Math.floor(t * 10) + i) > disturb * 0.6 ? 1 : 0.1) : 1;
      glow(g, x, y, 22 + n.w * 3, disturb > 0.3 && i % 4 === 0 ? '#ff8a5a' : '#fff2c8', 0.9 * a);
    }
  });
  g.restore();
}

// ------------------------------------------------------------------ SKIN CROSS-SECTION (perspective block), centered, ~ 900 wide
function skinBlock(g, t, opt = {}) {
  const sweat = opt.sweat ?? 1, dil = opt.dilate || 0, flush = opt.flush || 0;
  g.save(); g.lineJoin = 'round';
  const X0 = -440, X1 = 440, top = -260, ep = -200, de = 80, sub = 300;
  // front face layers
  const wave = (y, amp, ph) => { const pts = []; for (let x = X0; x <= X1; x += 20) pts.push([x, y + Math.sin(x * 0.03 + ph) * amp]); return pts; };
  const band = (y0, y1, c1, c2, a0 = 0, a1 = 0) => {
    const up = wave(y0, a0, 0.6), dn = wave(y1, a1, 1.7).reverse();
    g.fillStyle = linGrad(g, 0, y0, 0, y1, [[0, c1], [1, c2]]); g.beginPath(); crPath(g, up, false); crPath(g, dn, false, 0.5, false); g.closePath(); g.fill();
  };
  band(de, sub, '#e8c67a', '#a8803a', 10, 0);                                            // subcutaneous fat
  band(ep, de, mix('#e89a9a', '#ff7a6a', flush), mix('#b05a62', '#c8463e', flush), 6, 10);  // dermis
  band(top, ep, '#f0c8a8', '#d89a80', 4, 6);                                            // epidermis
  // fat lobules
  const r = mulberry(17);
  g.save(); g.globalAlpha = 0.55; for (let i = 0; i < 40; i++) { const x = lerp(X0 + 20, X1 - 20, r()), y = lerp(de + 30, sub - 20, r()); g.strokeStyle = '#8a6020'; g.lineWidth = 2;
    g.fillStyle = rgba('#ffe6a0', 0.5); g.beginPath(); g.ellipse(x, y, 22 + r() * 14, 16 + r() * 8, r() * 3, 0, 6.283); g.fill(); g.stroke(); } g.restore();
  // capillary loops (dilate with heat)
  for (let i = 0; i < 6; i++) {
    const x = X0 + 80 + i * 145, w = 7 + dil * 9;
    brush(g, curvePts([[x - 40, de + 40], [x - 30, ep + 40], [x, ep + 6], [x + 30, ep + 40], [x + 40, de + 40]], 30), w, w, '#d8323a', false);
    brush(g, curvePts([[x - 40, de + 40], [x - 30, ep + 40], [x, ep + 6]], 20), w * 0.4, w * 0.3, rgba('#ff9a9a', 0.6), false);
    // flowing cells
    for (let k = 0; k < 5; k++) { const u = ((t * (0.4 + dil * 0.5) + k / 5 + i * 0.1) % 1); const P = curvePts([[x - 40, de + 40], [x - 30, ep + 40], [x, ep + 6], [x + 30, ep + 40], [x + 40, de + 40]], 30); const [px, py] = P[Math.floor(u * (P.length - 1))];
      g.fillStyle = '#ffb0a8'; g.beginPath(); g.ellipse(px, py, 4, 3, 0, 0, 6.283); g.fill(); }
  }
  // sweat glands: coiled tube in dermis -> duct -> pore
  for (let i = 0; i < 5; i++) {
    const x = X0 + 150 + i * 160, cy = de - 10;
    g.strokeStyle = '#9fd8f0'; g.lineWidth = 6; g.beginPath();
    for (let k = 0; k <= 70; k++) { const a = k * 0.5; g.lineTo(x + Math.cos(a) * 30 + Math.sin(k * 0.13) * 8, cy + Math.sin(a) * 18 + Math.cos(k * 0.21) * 6); } g.stroke();
    brush(g, curvePts([[x, cy - 14], [x + 6, ep + 40], [x - 4, ep], [x, top + 2]], 20), 6, 5, '#9fd8f0', false);
    // sweat droplet emerging (animated)
    const u = ((t * 0.55 + i * 0.23) % 1);
    const yy = top - 4 - ease.out2(u) * 26 * sweat, rr = (4 + u * 12) * sweat;
    if (sweat > 0.02) { g.fillStyle = rgba('#bfe8ff', 0.85); g.beginPath(); g.ellipse(x, yy, rr * 0.85, rr, 0, 0, 6.283); g.fill();
      g.fillStyle = 'rgba(255,255,255,0.9)'; g.beginPath(); g.arc(x - rr * 0.3, yy - rr * 0.35, rr * 0.22, 0, 6.283); g.fill(); }
  }
  // hair follicles
  for (const x of [X0 + 90, X0 + 400, X0 + 720]) { g.strokeStyle = '#3a2418'; g.lineWidth = 5; g.beginPath(); g.moveTo(x, de + 10); g.quadraticCurveTo(x + 10, ep, x + 34, top - 110); g.stroke();
    g.fillStyle = '#e8b890'; g.beginPath(); g.ellipse(x, de + 14, 12, 18, 0, 0, 6.283); g.fill(); }
  // top surface (perspective plane)
  g.fillStyle = linGrad(g, 0, top - 160, 0, top, [[0, '#c48a70'], [1, '#f2c8aa']]);
  g.beginPath(); g.moveTo(X0, top); g.lineTo(X0 + 160, top - 160); g.lineTo(X1 + 160, top - 160); g.lineTo(X1, top); g.closePath(); g.fill();
  // surface droplets on the plane
  for (let i = 0; i < 16; i++) { const u = hash(i * 3.1), v = hash(i * 7.7), x = lerp(X0, X1, u) + v * 160, y = top - v * 160, s2 = (3 + hash(i) * 6) * sweat * (0.7 + 0.3 * Math.sin(t * 2 + i));
    if (s2 > 0.5) { g.fillStyle = rgba('#d8f2ff', 0.7); g.beginPath(); g.ellipse(x, y, s2 * 1.2, s2 * 0.7, 0, 0, 6.283); g.fill(); } }
  // side face
  g.fillStyle = linGrad(g, X1, 0, X1 + 160, 0, [[0, '#6a3a3a'], [1, '#2a1416']]);
  g.beginPath(); g.moveTo(X1, top); g.lineTo(X1 + 160, top - 160); g.lineTo(X1 + 160, sub - 160); g.lineTo(X1, sub); g.closePath(); g.fill();
  // labels lines
  g.restore();
}

// ------------------------------------------------------------------ BLOOD VESSEL (longitudinal cut), widening
function vessel(g, t, opt = {}) {
  const d = opt.diam || 120, len = opt.len || 1400, speed = opt.speed || 1;
  g.save();
  // outer wall
  g.fillStyle = linGrad(g, 0, -d / 2 - 24, 0, d / 2 + 24, [[0, '#ff8a8a'], [0.12, '#c8323e'], [0.88, '#7a141e'], [1, '#3a080c']]);
  g.beginPath(); g.roundRect(-len / 2, -d / 2 - 24, len, d + 48, d / 2 + 24); g.fill();
  // lumen
  g.fillStyle = linGrad(g, 0, -d / 2, 0, d / 2, [[0, '#5a0a12'], [0.5, '#8a1620'], [1, '#3a060a']]); g.fillRect(-len / 2, -d / 2, len, d);
  // red blood cells (biconcave discs) streaming
  const r = mulberry(23);
  for (let i = 0; i < 26; i++) {
    const lane = (r() - 0.5) * d * 0.7, ph = r(), sp = (0.8 + r() * 0.4) * speed, rot = r() * 6.28, sz = 30 + r() * 8;
    const x = -len / 2 + (((t * 180 * sp) / len + ph) % 1) * len;
    const flat = 0.45 + 0.4 * Math.abs(Math.sin(rot + t * 1.5));
    g.save(); g.translate(x, lane); g.rotate(Math.sin(rot + t) * 0.5);
    g.fillStyle = '#d8323a'; g.beginPath(); g.ellipse(0, 0, sz, sz * flat, 0, 0, 6.283); g.fill();
    g.fillStyle = '#9a141c'; g.beginPath(); g.ellipse(0, 0, sz * 0.5, sz * flat * 0.45, 0, 0, 6.283); g.fill();
    g.fillStyle = 'rgba(255,190,180,0.6)'; g.beginPath(); g.ellipse(-sz * 0.3, -sz * flat * 0.4, sz * 0.35, sz * flat * 0.18, 0, 0, 6.283); g.fill();
    g.restore();
  }
  // wall specular
  g.save(); g.globalCompositeOperation = 'screen'; g.filter = 'blur(6px)'; g.fillStyle = 'rgba(255,200,200,0.35)'; g.fillRect(-len / 2, -d / 2 - 18, len, 8); g.restore();
  g.restore();
}

// ------------------------------------------------------------------ TEST SHEET
TESTS.anat = (ctx, t) => {
  anatomyField(ctx, t);
  ctx.save(); ctx.translate(250, 520); ctx.scale(0.48, 0.48); bodySil(ctx, { t }); skeletonHint(ctx, 0.18); nerves(ctx, t); brainLat(ctx, { t: t }); ctx.restore();
  ctx.save(); ctx.translate(760, 300); ctx.scale(0.62, 0.62); brainLat(ctx, { t }); ctx.restore();
  ctx.save(); ctx.translate(780, 760); ctx.scale(0.62, 0.62); heartAnt(ctx, { t }); ctx.restore();
  ctx.save(); ctx.translate(540, 1240); ctx.scale(0.75, 0.75); skinBlock(ctx, t, { sweat: 1, dilate: 0.5 }); ctx.restore();
  ctx.save(); ctx.translate(300, 1700); ctx.scale(0.5, 0.5); liver(ctx); kidney(ctx, -120, -120, -1); kidney(ctx, 120, -120, 1); ctx.restore();
  ctx.save(); ctx.translate(760, 1700); ctx.scale(0.4, 0.6); vessel(ctx, t, { diam: 140 }); ctx.restore();
};
TESTS.brain = (ctx, t) => { anatomyField(ctx, t); ctx.save(); ctx.translate(540, 900); ctx.scale(1.5, 1.5); brainLat(ctx, { t }); ctx.restore(); };
