// PROTAGONIST - "Nikias": adult Greek man, ~30s. Short dark curls, trimmed beard, straight nose,
// deep-set eyes, undyed wool chiton with a madder-red border. Drawn in local units: head height ~420
// (crown y=-228, chin y=+182), origin between the eyes horizontally / at the brow line vertically.
'use strict';

// Palettes for the two-pass chiaroscuro renderer
const SKIN_LIT = { skin: '#c9906a', skin2: '#b27552', skinLt: '#f0c39b', skinDk: '#8a5236', lip: '#9a5548', hair: '#2a1d17', hairLt: '#5a4030', beard: '#2b1e17', beardLt: '#5c4231', eyeW: '#e8dccb', iris: '#4a3222', cloth: '#ddd0b8', clothDk: '#a89880', border: '#8a2e1a', line: '#3a1e12' };
const SKIN_SHD = { skin: '#3a2218', skin2: '#2d1912', skinLt: '#4e2e20', skinDk: '#1d0f0a', lip: '#3a1c16', hair: '#0d0907', hairLt: '#1d140f', beard: '#0e0a08', beardLt: '#1f1610', eyeW: '#5a4a3e', iris: '#1c120c', cloth: '#4a4036', clothDk: '#2c241d', border: '#3a140c', line: '#120805' };

// ------------------------------------------------------------------ 3/4 HEAD (facing screen-left)
// s: {blink 0..1, look [x,y] -1..1, brow 0..1 (tension), mouth 0..1, jaw 0..1, sweat 0..1, strain 0..1}
function softIn(g, clipPts, blur, fn) {
  g.save(); g.beginPath(); crPath(g, clipPts, true); g.clip(); g.filter = `blur(${blur}px)`; fn(); g.filter = 'none'; g.restore();
}
const FACE34 = [[-62, -200], [-104, -150], [-122, -88], [-128, -46], [-118, -18], [-126, 14], [-114, 56], [-98, 108],
[-62, 158], [-22, 182], [40, 170], [96, 130], [126, 72], [134, 0], [150, -80], [132, -170], [70, -222], [0, -230]];
function head34(g, C, s) {
  const blink = s.blink || 0, lx = (s.look || [0, 0])[0], ly = (s.look || [0, 0])[1];
  const brow = s.brow || 0, mouth = s.mouth || 0;
  g.save();
  g.lineJoin = 'round'; g.lineCap = 'round';
  // --- neck (behind head): short and strong ---
  const neck = [[-46, 110], [118, 86], [138, 170], [158, 262], [-24, 286], [-52, 210]];
  g.fillStyle = linGrad(g, -40, 120, 150, 250, [[0, C.skin], [1, C.skin2]]); g.beginPath(); crPath(g, neck, true); g.fill();
  softIn(g, neck, 14, () => { g.fillStyle = rgba(C.skinDk, 0.75); g.beginPath(); g.ellipse(50, 150, 110, 46, -0.12, 0, 6.283); g.fill();
    g.fillStyle = rgba(C.skinLt, 0.35); g.beginPath(); g.ellipse(-20, 240, 30, 60, 0.2, 0, 6.283); g.fill(); });
  // sternocleidomastoid hint
  g.save(); g.globalAlpha = 0.35; brush(g, [[112, 120], [80, 190], [34, 262]], 10, 4, C.skinDk); g.restore();
  // --- ear (near side) ---
  const ear = [[112, -8], [140, -32], [162, -2], [158, 52], [140, 92], [120, 84], [116, 40]];
  g.fillStyle = C.skin2; g.beginPath(); crPath(g, ear, true); g.fill();
  softIn(g, ear, 5, () => { g.fillStyle = rgba(C.skinDk, 0.9); g.beginPath(); crPath(g, [[126, 4], [144, -12], [152, 22], [142, 60], [128, 52]], true); g.fill(); });
  g.strokeStyle = rgba(C.line, 0.5); g.lineWidth = 2.5; g.beginPath(); crPath(g, [[146, -20], [158, 10], [150, 56], [138, 80]], false); g.stroke();
  // --- face mass ---
  const face = FACE34;
  g.fillStyle = C.skin; g.beginPath(); crPath(g, face, true); g.fill();
  softIn(g, face, 26, () => {
    // turning planes: near cheek -> ear darkens, far temple darkens
    g.fillStyle = rgba(C.skinDk, 0.7); g.beginPath(); g.ellipse(150, -20, 70, 200, 0, 0, 6.283); g.fill();
    g.fillStyle = rgba(C.skinDk, 0.45); g.beginPath(); g.ellipse(-140, -40, 40, 140, 0, 0, 6.283); g.fill();
    // forehead + cheek light planes
    g.fillStyle = rgba(C.skinLt, 0.8); g.beginPath(); g.ellipse(-20, -150, 90, 50, -0.1, 0, 6.283); g.fill();
    g.fillStyle = rgba(C.skinLt, 0.55); g.beginPath(); g.ellipse(24, 40, 46, 30, -0.4, 0, 6.283); g.fill();
    g.fillStyle = rgba(C.skinLt, 0.45); g.beginPath(); g.ellipse(-92, 34, 22, 26, 0, 0, 6.283); g.fill();
  });
  softIn(g, face, 12, () => {
    // eye sockets
    g.fillStyle = rgba(C.skinDk, 0.6); g.beginPath(); g.ellipse(24, -18, 46, 22, -0.08, 0, 6.283); g.fill();
    g.beginPath(); g.ellipse(-84, -18, 26, 18, 0.1, 0, 6.283); g.fill();
    // under-brow shadow (deep-set eyes)
    g.fillStyle = rgba(C.skinDk, 0.5); g.beginPath(); g.ellipse(0, -44, 100, 12, -0.04, 0, 6.283); g.fill();
    // brow ridge light
    g.fillStyle = rgba(C.skinLt, 0.6); g.beginPath(); g.ellipse(-10, -76 - brow * 4, 84, 10, -0.05, 0, 6.283); g.fill();
    // nasolabial + cheek hollow
    g.fillStyle = rgba(C.skinDk, 0.45); g.beginPath(); g.ellipse(-4, 82, 18, 40, 0.5, 0, 6.283); g.fill();
    // nose side shadow cast on near cheek
    g.fillStyle = rgba(C.skinDk, 0.75); g.beginPath(); crPath(g, [[-38, -30], [-36, 20], [-46, 66], [-70, 92], [-58, 58], [-50, 6]], true); g.fill();
  });
  // face outline (illustrative line, light weight)
  g.strokeStyle = rgba(C.line, 0.35); g.lineWidth = 2.2; g.beginPath(); crPath(g, face.slice(0, 10), false); g.stroke();
  // --- eyes ---
  eye34(g, C, 22, -20, 58, 22, blink, lx, ly, 1.0, brow);
  eye34(g, C, -86, -19, 34, 18, blink, lx, ly, 0.62, brow);
  // --- brows (hair strokes) ---
  const bt = brow * 8;
  brush(g, [[-6, -60 + bt * 0.2], [24, -68 - bt * 0.4], [56, -66 + bt * 0.2], [80, -54]], 14, 6, C.hair, true);
  brush(g, [[-114, -56], [-92, -64 - bt * 0.3], [-62, -64 + bt * 0.6], [-40, -56 + bt]], 9, 12, C.hair, true);
  if (brow > 0.15) { g.save(); g.globalAlpha = (brow - 0.15) * 0.7; g.filter = 'blur(1px)'; brush(g, [[-28, -62], [-31, -42], [-27, -26]], 5, 3, C.skinDk); g.restore(); }
  // --- nose ---
  const nose = [[-42, -42], [-60, -2], [-84, 34], [-108, 62], [-112, 76], [-100, 88], [-80, 90], [-64, 80], [-54, 56], [-44, 14], [-36, -30]];
  softIn(g, nose, 7, () => {
    g.fillStyle = rgba(C.skinDk, 0.55); g.beginPath(); crPath(g, [[-48, 0], [-56, 50], [-66, 86], [-40, 86], [-36, 0]], true); g.fill();
    g.fillStyle = rgba(C.skinLt, 0.9); g.beginPath(); crPath(g, [[-48, -30], [-70, 8], [-96, 52], [-102, 66], [-90, 64], [-66, 20], [-46, -20]], true); g.fill();
    g.fillStyle = rgba(C.skinDk, 0.5); g.beginPath(); g.ellipse(-92, 92, 22, 7, -0.2, 0, 6.283); g.fill();
  });
  // nostril + wing line
  g.fillStyle = rgba(C.skinDk, 0.95); g.beginPath(); g.ellipse(-86, 85, 9, 4, -0.3, 0, 6.283); g.fill();
  g.strokeStyle = rgba(C.line, 0.55); g.lineWidth = 2.5; g.beginPath(); crPath(g, [[-58, 58], [-50, 72], [-58, 86], [-72, 90]], false); g.stroke();
  // --- mouth ---
  const mo = mouth * 12;
  g.fillStyle = '#1a0c08'; g.beginPath(); crPath(g, [[-84, 122], [-50, 119 - mo * 0.2], [-8, 124], [-48, 131 + mo], [-80, 128]], true); g.fill();
  g.fillStyle = C.lip; g.beginPath(); crPath(g, [[-82, 130], [-46, 133 + mo], [-12, 128], [-46, 148 + mo * 0.6]], true); g.fill();
  g.fillStyle = rgba(C.skinLt, 0.35); g.beginPath(); g.ellipse(-46, 138 + mo * 0.6, 14, 3, 0, 0, 6.283); g.fill();
  // --- beard ---
  const beard = [[126, 8], [128, 70], [104, 128], [56, 170], [0, 190], [-40, 186], [-78, 168], [-104, 122], [-118, 70], [-112, 52], [-96, 92],
  [-84, 140], [-56, 152], [-20, 152], [6, 138], [22, 104], [52, 84], [86, 72], [108, 40], [112, 8]];
  hairMass(g, C, beard, 7, 260, [-120, 20, 130, 195], 9);
  // moustache
  hairMass(g, C, [[-100, 106], [-76, 96], [-46, 100], [-12, 104], [20, 118], [-4, 124], [-46, 118], [-86, 122], [-106, 118]], 11, 50, [-104, 96, 20, 124], 7);
  // --- hair ---
  hair34(g, C);
  if (s.sweat > 0) sweat34(g, C, s.sweat, s.t || 0);
  g.restore();
}
// textured hair/beard mass: soft-edged fill + many short directional strokes
function hairMass(g, C, pts, seed, n, box, len) {
  g.fillStyle = C.beard; g.beginPath(); crPath(g, pts, true); g.fill();
  const r = mulberry(seed); g.save(); g.beginPath(); crPath(g, pts, true); g.clip();
  for (let i = 0; i < n; i++) {
    const x = lerp(box[0], box[2], r()), y = lerp(box[1], box[3], r()); const L = len * (0.6 + r() * 0.8), a = 1.35 + (r() - 0.5) * 0.9;
    g.strokeStyle = rgba(r() > 0.5 ? C.beardLt : '#000000', 0.32 + r() * 0.2); g.lineWidth = 1.6 + r() * 1.2;
    g.beginPath(); g.moveTo(x, y); g.quadraticCurveTo(x + Math.cos(a - 0.4) * L * 0.6, y + Math.sin(a - 0.4) * L * 0.6, x + Math.cos(a) * L, y + Math.sin(a) * L); g.stroke();
  }
  g.restore();
}
function eye34(g, C, cx, cy, w, h, blink, lx, ly, persp, brow) {
  const open = (1 - blink) * (1 - brow * 0.18);
  g.save();
  // eye opening shape (almond, slightly hooded)
  const top = [[cx - w / 2, cy + 2], [cx - w * 0.15, cy - h * 0.55 * open], [cx + w * 0.25, cy - h * 0.5 * open], [cx + w / 2, cy + 1]];
  const bot = [[cx + w / 2, cy + 1], [cx + w * 0.2, cy + h * 0.38 * Math.max(open, 0.25)], [cx - w * 0.2, cy + h * 0.36 * Math.max(open, 0.25)], [cx - w / 2, cy + 2]];
  const pts = top.concat(bot.slice(1, 3));
  g.beginPath(); crPath(g, pts, true); g.save(); g.clip();
  g.fillStyle = C.eyeW; g.fillRect(cx - w, cy - h, w * 2, h * 2);
  // iris + pupil
  const ix = cx + lx * w * 0.22 - w * 0.08 * (1 - persp), iy = cy + ly * h * 0.15;
  g.fillStyle = C.iris; g.beginPath(); g.ellipse(ix, iy, h * 0.62 * persp + 2, h * 0.62, 0, 0, 6.283); g.fill();
  g.fillStyle = '#0a0605'; g.beginPath(); g.ellipse(ix, iy, h * 0.28 * persp + 1, h * 0.28, 0, 0, 6.283); g.fill();
  // upper lid shadow on eyeball
  g.fillStyle = 'rgba(0,0,0,0.35)'; g.fillRect(cx - w, cy - h, w * 2, h * 0.55);
  // catchlight
  g.fillStyle = 'rgba(255,240,220,0.9)'; g.beginPath(); g.arc(ix - h * 0.18, iy - h * 0.2, Math.max(1.5, h * 0.12), 0, 6.283); g.fill();
  g.restore();
  // lid line + crease
  g.strokeStyle = C.line; g.lineWidth = 4 * persp + 1;
  g.beginPath(); crPath(g, top, false); g.stroke();
  g.lineWidth = 2; g.strokeStyle = rgba(C.line, 0.55); g.beginPath();
  crPath(g, [[cx - w * 0.42, cy - h * 0.62], [cx, cy - h * 1.0], [cx + w * 0.45, cy - h * 0.6]], false); g.stroke();
  // lower lid
  g.strokeStyle = rgba(C.line, 0.4); g.lineWidth = 2; g.beginPath(); crPath(g, bot.slice(0, 4), false); g.stroke();
  g.restore();
}

function hair34(g, C) {
  // scalloped outer contour (curl bumps) generated around a base mass
  const base = [[-66, -152], [-104, -170], [-108, -212], [-50, -254], [40, -262], [116, -238], [164, -186], [180, -110], [166, -36],
  [142, 4], [128, -54], [118, -116], [80, -150], [20, -164], [-28, -160]];
  const dense = curvePts(base.concat([base[0]]), 90);
  const sc = dense.map(([x, y], i) => { const k = Math.sin(i * 1.9) * 0.5 + Math.sin(i * 0.77) * 0.5; const cx = 30, cy = -150; const dx = x - cx, dy = y - cy, d = Math.hypot(dx, dy); return [x + dx / d * k * 7, y + dy / d * k * 7]; });
  g.fillStyle = C.hair; g.beginPath(); crPath(g, sc, true); g.fill();
  // sideburn
  g.beginPath(); crPath(g, [[116, -80], [142, -66], [136, 18], [118, 18]], true); g.fill();
  // curl texture: small C-strokes, lighter on top (light from above-left)
  const r = mulberry(31);
  g.save(); g.beginPath(); crPath(g, sc, true); g.clip();
  for (let i = 0; i < 420; i++) {
    const x = lerp(-110, 182, r()), y = lerp(-266, -40, r()); const rad = 5 + r() * 7, ph = r() * 6.28;
    const top = clamp(1 - (y + 266) / 200);
    g.strokeStyle = rgba(r() < 0.55 + top * 0.3 ? C.hairLt : '#000000', 0.25 + 0.45 * r());
    g.lineWidth = 1.6 + r() * 1.6;
    g.beginPath(); g.arc(x, y, rad, ph, ph + 2.2 + r() * 1.5); g.stroke();
  }
  // soft sheen band
  g.filter = 'blur(10px)'; g.fillStyle = rgba(C.hairLt, 0.35); g.beginPath(); g.ellipse(10, -220, 110, 22, -0.15, 0, 6.283); g.fill(); g.filter = 'none';
  g.restore();
}

function sweat34(g, C, amt, t) {
  const drops = [[-40, -128, 0.0], [12, -150, 0.4], [74, -118, 0.8], [-100, -112, 0.2], [98, -44, 0.6], [-116, 22, 0.9], [48, 54, 0.3]];
  for (const [x, y0, ph] of drops) {
    const k = clamp(amt * 1.6 - ph * 0.6); if (k <= 0) continue;
    const slide = ((t * 0.12 + ph) % 1) * 46 * amt;
    const y = y0 + slide, r = 2.4 + 2.2 * k;
    // wet trail
    g.strokeStyle = rgba('#fff0dc', 0.12 * k); g.lineWidth = r * 1.1; g.beginPath(); g.moveTo(x, y0 - 4); g.lineTo(x + 1, y); g.stroke();
    g.fillStyle = rgba(C.skinDk, 0.28 * k); g.beginPath(); g.ellipse(x + 0.8, y + 1.2, r, r * 1.4, 0, 0, 6.283); g.fill();
    g.fillStyle = rgba('#fff3e0', 0.7 * k); g.beginPath(); g.ellipse(x - r * 0.3, y - r * 0.5, r * 0.32, r * 0.5, -0.3, 0, 6.283); g.fill();
  }
}

// ------------------------------------------------------------------ BUST (shoulders + chiton) 3/4
function bust34(g, C, s) {
  const br = s.breath || 0, slump = s.slump || 0;
  g.save();
  g.translate(0, br * 7 + slump * 34 - 120);
  // torso skin (only the area above the neckline is visible)
  const torso = [[-300, 1400], [-280, 800], [-250, 520], [-190, 410], [-90, 372], [40, 356], [170, 372], [290, 420], [360, 520], [392, 800], [410, 1400]];
  g.fillStyle = C.skin2; g.beginPath(); crPath(g, torso, true); g.fill();
  softIn(g, torso, 16, () => {
    g.fillStyle = rgba(C.skinDk, 0.7); g.beginPath(); g.ellipse(60, 380, 120, 36, 0, 0, 6.283); g.fill();
    g.fillStyle = rgba(C.skinLt, 0.35); g.beginPath(); g.ellipse(-40, 410, 50, 22, 0, 0, 6.283); g.fill(); });
  g.save(); g.globalAlpha = 0.5; brush(g, [[-60, 404], [30, 414], [140, 404]], 7, 4, C.skinDk); g.restore();
  // chiton (pinned at both shoulders, swags across the chest)
  const cloth = [[-330, 1500], [-300, 820], [-262, 560], [-214, 440], [-140, 396], [-84, 400], [-20, 440], [50, 452], [130, 430], [190, 404], [262, 408],
  [330, 450], [372, 540], [398, 680], [410, 820], [440, 1500]];
  g.fillStyle = C.cloth; g.beginPath(); crPath(g, cloth, true); g.fill();
  softIn(g, cloth, 22, () => {
    g.fillStyle = rgba(C.clothDk, 0.9); g.beginPath(); g.ellipse(340, 640, 110, 260, 0, 0, 6.283); g.fill();
    g.fillStyle = rgba(C.clothDk, 0.8); g.beginPath(); g.ellipse(40, 800, 360, 90, 0, 0, 6.283); g.fill();
    g.fillStyle = rgba('#ffffff', 0.18); g.beginPath(); g.ellipse(-150, 470, 90, 50, -0.4, 0, 6.283); g.fill();
  });
  // swag folds between the shoulder pins
  const pinL = [-142, 404], pinR = [214, 404];
  g.save(); g.beginPath(); crPath(g, cloth, true); g.clip();
  for (let k = 0; k < 4; k++) {
    const sag = 70 + k * 62, pts = curvePts([pinL, [lerp(pinL[0], pinR[0], 0.5) - 10, 420 + sag], pinR], 30);
    g.filter = 'blur(5px)'; brush(g, pts.map(([x, y]) => [x, y + 10]), 26 - k * 3, 8, rgba(C.clothDk, 0.75), true);
    g.filter = 'blur(2px)'; brush(g, pts.map(([x, y]) => [x, y - 6]), 8, 2, rgba('#fff7e6', 0.16), true); g.filter = 'none';
  }
  // vertical hanging folds
  [[-210, 520], [-120, 600], [300, 520], [360, 600]].forEach(([x, y], i) => {
    const pts = curvePts([[x, y], [x + 8 * (i % 2 ? 1 : -1), y + 120], [x - 6, 840]], 16);
    g.filter = 'blur(6px)'; brush(g, pts, 22, 14, rgba(C.clothDk, 0.7), false); g.filter = 'none';
    g.filter = 'blur(3px)'; brush(g, pts.map(([a, b]) => [a + 14, b]), 8, 4, rgba('#fff7e6', 0.12), false); g.filter = 'none';
  });
  g.restore();
  // madder-red border along the neckline
  brush(g, curvePts([[-140, 398], [-84, 402], [-20, 442], [50, 454], [130, 432], [190, 406], [214, 404]], 40), 12, 12, C.border, false);
  // bronze fibula pins
  for (const [x, y] of [pinL, pinR]) {
    g.fillStyle = '#9a6a2e'; g.beginPath(); g.arc(x, y, 12, 0, 6.283); g.fill();
    g.fillStyle = '#e8b86a'; g.beginPath(); g.arc(x - 3, y - 3, 5, 0, 6.283); g.fill();
  }
  g.restore();
}

// ------------------------------------------------------------------ two-pass lit render
// draw(g, C) renders the subject in a palette. mask(g) paints the light (white = lit).
// rim: {angle, col, a} draws a thin rim light along the silhouette.
const _cv = {};
function cvs(name, w = W, h = H) { if (!_cv[name] || _cv[name].width !== w) _cv[name] = mk(w, h); const c = _cv[name]; const g = c.getContext('2d'); g.reset(); return c; }
function litRender(ctx, draw, mask, opt = {}) {
  const shd = cvs('shd'), lit = cvs('lit'), m = cvs('mask');
  draw(shd.getContext('2d'), opt.shadow || SKIN_SHD);
  draw(lit.getContext('2d'), opt.lit || SKIN_LIT);
  const mg = m.getContext('2d'); mask(mg);
  const lg = lit.getContext('2d'); lg.globalCompositeOperation = 'destination-in'; lg.drawImage(m, 0, 0); lg.globalCompositeOperation = 'source-over';
  ctx.drawImage(shd, 0, 0);
  ctx.drawImage(lit, 0, 0);
  if (opt.rim) {
    // rim: silhouette alpha, offset-subtract -> edge band
    const e = cvs('rim'), eg = e.getContext('2d');
    eg.drawImage(shd, 0, 0); eg.globalCompositeOperation = 'source-in'; eg.fillStyle = opt.rim.col; eg.fillRect(0, 0, W, H);
    eg.globalCompositeOperation = 'destination-out';
    eg.drawImage(shd, opt.rim.dx, opt.rim.dy);
    eg.globalCompositeOperation = 'source-over';
    ctx.save(); ctx.globalAlpha = opt.rim.a; ctx.globalCompositeOperation = 'screen'; ctx.filter = 'blur(1.5px)'; ctx.drawImage(e, 0, 0);
    ctx.filter = 'blur(10px)'; ctx.globalAlpha = opt.rim.a * 0.6; ctx.drawImage(e, 0, 0); ctx.restore();
  }
}

// ------------------------------------------------------------------ PROFILE HEAD (facing screen-left)
const FACEP = [[-40, -222], [-84, -178], [-106, -120], [-112, -66], [-104, -38], [-118, -4], [-140, 44], [-152, 64], [-140, 80], [-122, 84],
[-110, 92], [-114, 110], [-106, 122], [-112, 136], [-100, 150], [-96, 170], [-60, 196], [10, 200], [70, 160], [110, 112],
[150, 110], [176, 40], [190, -60], [160, -170], [90, -226], [20, -236]];
function headProfile(g, C, s) {
  const blink = s.blink || 0, brow = s.brow || 0, mouth = s.mouth || 0, ly = (s.look || [0, 0])[1];
  g.save(); g.lineJoin = 'round'; g.lineCap = 'round';
  const neck = [[0, 150], [120, 110], [170, 150], [160, 300], [10, 300], [-30, 220]];
  g.fillStyle = C.skin2; g.beginPath(); crPath(g, neck, true); g.fill();
  softIn(g, neck, 14, () => { g.fillStyle = rgba(C.skinDk, 0.7); g.beginPath(); g.ellipse(60, 170, 100, 40, 0, 0, 6.283); g.fill(); });
  g.save(); g.globalAlpha = 0.4; brush(g, [[70, 140], [40, 220], [0, 290]], 12, 5, C.skinDk); g.restore();
  // throat / larynx contour
  g.strokeStyle = rgba(C.line, 0.3); g.lineWidth = 2; g.beginPath(); crPath(g, [[-28, 210], [-34, 250], [-22, 296]], false); g.stroke();
  const face = FACEP;
  g.fillStyle = C.skin; g.beginPath(); crPath(g, face, true); g.fill();
  softIn(g, face, 24, () => {
    g.fillStyle = rgba(C.skinLt, 0.7); g.beginPath(); g.ellipse(-60, -150, 70, 50, 0, 0, 6.283); g.fill();
    g.fillStyle = rgba(C.skinLt, 0.5); g.beginPath(); g.ellipse(-50, 30, 46, 30, 0, 0, 6.283); g.fill();
    g.fillStyle = rgba(C.skinDk, 0.6); g.beginPath(); g.ellipse(80, -40, 90, 120, 0, 0, 6.283); g.fill();
  });
  softIn(g, face, 10, () => {
    g.fillStyle = rgba(C.skinDk, 0.6); g.beginPath(); g.ellipse(-70, -20, 30, 20, 0, 0, 6.283); g.fill();
    g.fillStyle = rgba(C.skinLt, 0.7); g.beginPath(); crPath(g, [[-112, -30], [-130, 20], [-146, 58], [-136, 60], [-118, 18], [-104, -26]], true); g.fill();
    g.fillStyle = rgba(C.skinDk, 0.5); g.beginPath(); g.ellipse(-96, 74, 18, 12, 0, 0, 6.283); g.fill();
  });
  g.strokeStyle = rgba(C.line, 0.35); g.lineWidth = 2.2; g.beginPath(); crPath(g, face.slice(0, 17), false); g.stroke();
  // eye (profile: wedge shape)
  const open = (1 - blink) * (1 - brow * 0.2);
  g.save(); const ex = -82, ey = -18;
  g.beginPath(); crPath(g, [[ex - 20, ey + 2], [ex - 6, ey - 11 * open], [ex + 14, ey - 6 * open], [ex + 18, ey + 2], [ex + 6, ey + 8 * Math.max(open, 0.3)], [ex - 12, ey + 7 * Math.max(open, 0.3)]], true);
  g.clip(); g.fillStyle = C.eyeW; g.fillRect(ex - 30, ey - 20, 60, 40);
  g.fillStyle = C.iris; g.beginPath(); g.ellipse(ex - 10, ey + ly * 3, 6, 9, 0, 0, 6.283); g.fill();
  g.fillStyle = 'rgba(0,0,0,0.35)'; g.fillRect(ex - 30, ey - 20, 60, 12);
  g.restore();
  g.strokeStyle = C.line; g.lineWidth = 3.5; g.beginPath(); crPath(g, [[ex - 20, ey + 2], [ex - 6, ey - 11 * open], [ex + 14, ey - 6 * open], [ex + 18, ey + 2]], false); g.stroke();
  brush(g, [[-108, -52 + brow * 4], [-84, -62 - brow * 4], [-56, -60], [-36, -50]], 12, 6, C.hair);
  // ear
  const ear = [[40, -20], [70, -40], [92, -10], [88, 50], [66, 84], [44, 70], [40, 30]];
  g.fillStyle = C.skin2; g.beginPath(); crPath(g, ear, true); g.fill();
  softIn(g, ear, 4, () => { g.fillStyle = rgba(C.skinDk, 0.9); g.beginPath(); crPath(g, [[52, -4], [74, -18], [82, 14], [74, 50], [56, 44]], true); g.fill(); });
  // mouth line
  g.strokeStyle = '#1a0c08'; g.lineWidth = 3 + mouth * 4; g.beginPath(); g.moveTo(-108, 124 + mouth * 3); g.lineTo(-84, 126 + mouth * 4); g.stroke();
  // beard + moustache
  const beard = [[40, 40], [60, 100], [40, 160], [0, 196], [-60, 198], [-98, 176], [-108, 140], [-100, 128], [-80, 140], [-60, 136], [-40, 110], [-10, 90], [20, 60]];
  hairMass(g, C, beard, 17, 200, [-110, 40, 70, 200], 9);
  hairMass(g, C, [[-112, 100], [-92, 96], [-64, 104], [-50, 118], [-80, 120], [-108, 118]], 19, 30, [-112, 94, -48, 122], 6);
  // hair
  const base = [[-70, -150], [-100, -196], [-50, -250], [50, -262], [150, -220], [196, -120], [192, -30], [168, 50], [120, 60], [120, -30], [80, -60], [40, -90], [0, -150], [-40, -164]];
  const dense = curvePts(base.concat([base[0]]), 80).map(([x, y], i) => { const k = Math.sin(i * 1.9) * 0.5 + Math.sin(i * 0.77) * 0.5; const d = Math.hypot(x - 60, y + 110) || 1; return [x + (x - 60) / d * k * 7, y + (y + 110) / d * k * 7]; });
  g.fillStyle = C.hair; g.beginPath(); crPath(g, dense, true); g.fill();
  const r = mulberry(41); g.save(); g.beginPath(); crPath(g, dense, true); g.clip();
  for (let i = 0; i < 380; i++) { const x = lerp(-104, 200, r()), y = lerp(-266, 60, r()), rad = 5 + r() * 7, ph = r() * 6.28;
    g.strokeStyle = rgba(r() < 0.6 - (y + 266) / 700 ? C.hairLt : '#000000', 0.25 + 0.45 * r()); g.lineWidth = 1.6 + r() * 1.6; g.beginPath(); g.arc(x, y, rad, ph, ph + 2.6); g.stroke(); }
  g.restore();
  if (s.sweat > 0) sweat34(g, C, s.sweat * 0.8, s.t || 0);
  g.restore();
}

// ------------------------------------------------------------------ FRONT HEAD
function headFront(g, C, s) {
  const blink = s.blink || 0, brow = s.brow || 0, mouth = s.mouth || 0, lx = (s.look || [0, 0])[0];
  g.save(); g.lineJoin = 'round'; g.lineCap = 'round';
  const neck = [[-78, 100], [78, 100], [92, 300], [-92, 300]];
  g.fillStyle = C.skin2; g.beginPath(); crPath(g, neck, true); g.fill();
  softIn(g, neck, 14, () => { g.fillStyle = rgba(C.skinDk, 0.75); g.beginPath(); g.ellipse(0, 150, 110, 46, 0, 0, 6.283); g.fill(); });
  for (const sx of [-1, 1]) { const ear = [[sx * 112, -20], [sx * 140, -36], [sx * 150, 10], [sx * 140, 70], [sx * 118, 74]]; g.fillStyle = C.skin2; g.beginPath(); crPath(g, ear, true); g.fill();
    softIn(g, ear, 4, () => { g.fillStyle = rgba(C.skinDk, 0.8); g.beginPath(); g.ellipse(sx * 130, 16, 8, 30, 0, 0, 6.283); g.fill(); }); }
  const face = [[0, -232], [80, -214], [118, -150], [126, -60], [122, 20], [110, 90], [80, 150], [36, 184], [0, 190], [-36, 184], [-80, 150], [-110, 90], [-122, 20], [-126, -60], [-118, -150], [-80, -214]];
  g.fillStyle = C.skin; g.beginPath(); crPath(g, face, true); g.fill();
  softIn(g, face, 24, () => {
    g.fillStyle = rgba(C.skinDk, 0.55); g.beginPath(); g.ellipse(-140, 0, 50, 200, 0, 0, 6.283); g.fill(); g.beginPath(); g.ellipse(140, 0, 50, 200, 0, 0, 6.283); g.fill();
    g.fillStyle = rgba(C.skinLt, 0.7); g.beginPath(); g.ellipse(0, -150, 90, 50, 0, 0, 6.283); g.fill();
    g.fillStyle = rgba(C.skinLt, 0.4); g.beginPath(); g.ellipse(-62, 36, 34, 22, 0, 0, 6.283); g.fill(); g.beginPath(); g.ellipse(62, 36, 34, 22, 0, 0, 6.283); g.fill();
  });
  softIn(g, face, 10, () => {
    g.fillStyle = rgba(C.skinDk, 0.6); for (const sx of [-1, 1]) { g.beginPath(); g.ellipse(sx * 56, -18, 40, 20, 0, 0, 6.283); g.fill(); }
    g.fillStyle = rgba(C.skinDk, 0.5); g.beginPath(); crPath(g, [[-14, -30], [-20, 40], [-30, 76], [0, 92], [30, 76], [20, 40], [14, -30]], true); g.fill();
    g.fillStyle = rgba(C.skinLt, 0.8); g.beginPath(); g.ellipse(0, 20, 9, 50, 0, 0, 6.283); g.fill();
    g.fillStyle = rgba(C.skinDk, 0.6); g.beginPath(); g.ellipse(0, 92, 30, 9, 0, 0, 6.283); g.fill();
  });
  for (const sx of [-1, 1]) eye34(g, C, sx * 56, -18, 54, 21, blink, lx, 0, 1.0, brow);
  const bt = brow * 8;
  brush(g, [[-104, -50], [-80, -64 + bt * 0.3], [-46, -66 - bt * 0.5], [-18, -56 + bt]], 9, 13, C.hair);
  brush(g, [[18, -56 + bt], [46, -66 - bt * 0.5], [80, -64 + bt * 0.3], [104, -50]], 13, 9, C.hair);
  g.fillStyle = rgba(C.skinDk, 0.9); for (const sx of [-1, 1]) { g.beginPath(); g.ellipse(sx * 13, 86, 8, 4, sx * 0.3, 0, 6.283); g.fill(); }
  const mo = mouth * 12;
  g.fillStyle = '#1a0c08'; g.beginPath(); crPath(g, [[-38, 124], [0, 120 - mo * 0.2], [38, 124], [0, 132 + mo]], true); g.fill();
  g.fillStyle = C.lip; g.beginPath(); crPath(g, [[-34, 130], [0, 134 + mo], [34, 130], [0, 148 + mo * 0.6]], true); g.fill();
  const beard = [[118, 0], [120, 80], [96, 140], [50, 186], [0, 200], [-50, 186], [-96, 140], [-120, 80], [-118, 0], [-100, 50], [-80, 96], [-50, 118], [-36, 150], [0, 158], [36, 150], [50, 118], [80, 96], [100, 50]];
  hairMass(g, C, beard, 23, 260, [-124, 0, 124, 200], 9);
  hairMass(g, C, [[-60, 112], [-30, 100], [0, 104], [30, 100], [60, 112], [40, 122], [0, 116], [-40, 122]], 29, 50, [-60, 98, 60, 124], 7);
  const base = [[-120, -120], [-136, -190], [-80, -252], [0, -268], [80, -252], [136, -190], [120, -120], [110, -80], [80, -160], [0, -176], [-80, -160], [-110, -80]];
  const dense = curvePts(base.concat([base[0]]), 80).map(([x, y], i) => { const k = Math.sin(i * 1.9) * 0.5 + Math.sin(i * 0.77) * 0.5; const d = Math.hypot(x, y + 150) || 1; return [x + x / d * k * 7, y + (y + 150) / d * k * 7]; });
  g.fillStyle = C.hair; g.beginPath(); crPath(g, dense, true); g.fill();
  const r = mulberry(53); g.save(); g.beginPath(); crPath(g, dense, true); g.clip();
  for (let i = 0; i < 380; i++) { const x = lerp(-140, 140, r()), y = lerp(-270, -70, r()), rad = 5 + r() * 7, ph = r() * 6.28;
    g.strokeStyle = rgba(r() < 0.6 - (y + 270) / 600 ? C.hairLt : '#000000', 0.25 + 0.45 * r()); g.lineWidth = 1.6 + r() * 1.6; g.beginPath(); g.arc(x, y, rad, ph, ph + 2.6); g.stroke(); }
  g.restore();
  if (s.sweat > 0) sweat34(g, C, s.sweat * 0.7, s.t || 0);
  g.restore();
}

// ------------------------------------------------------------------ HAND (palm pressed flat, back of hand view)
function handFlat(g, C, s) {
  // back of a right hand pressed flat on a surface, fingers slightly spread. ~ real proportions:
  // palm length ~= middle finger length, knuckle arc, tapering fingers that touch at the base.
  const curl = s.curl || 0, press = s.press || 0;
  g.save(); g.lineJoin = 'round';
  const F = [[-46, -52, -0.10, 92, 28], [-16, -60, -0.03, 104, 30], [15, -58, 0.04, 98, 29], [43, -48, 0.12, 78, 25]];
  F.forEach(([x, y, a, L, w]) => {
    const L2 = L * (1 - curl * 0.3);
    g.save(); g.translate(x, y); g.rotate(a);
    const f = [[-w / 2, 14], [-w / 2 + 1, -L2 * 0.45], [-w * 0.42, -L2 * 0.82], [-w * 0.28, -L2 + 3], [0, -L2 - 2], [w * 0.28, -L2 + 3], [w * 0.42, -L2 * 0.82], [w / 2 - 1, -L2 * 0.45], [w / 2, 14]];
    g.fillStyle = C.skin; g.beginPath(); crPath(g, f, true); g.fill();
    softIn(g, f, 4, () => { g.fillStyle = rgba(C.skinDk, 0.6); g.fillRect(w / 2 - 7, -L2 - 4, 10, L2 + 20);
      g.fillStyle = rgba(C.skinLt, 0.45); g.fillRect(-w / 2 + 3, -L2, 7, L2);
      g.fillStyle = rgba(C.skinDk, 0.35); for (const k of [0.42, 0.72]) { g.beginPath(); g.ellipse(0, -L2 * k, w * 0.4, 3.5, 0, 0, 6.283); g.fill(); } });
    g.fillStyle = rgba('#f6d6bc', 0.75); g.beginPath(); crPath(g, [[-w * 0.26, -L2 + 22], [-w * 0.2, -L2 + 4], [0, -L2 + 1], [w * 0.2, -L2 + 4], [w * 0.26, -L2 + 22], [0, -L2 + 26]], true); g.fill();
    g.restore();
  });
  // thumb: lies along the surface, angled out from the side of the palm
  const th = [[-58, 46], [-92, 22], [-122, -6], [-138, -26], [-128, -40], [-104, -26], [-70, -6], [-54, 10]];
  g.fillStyle = C.skin; g.beginPath(); crPath(g, th, true); g.fill();
  softIn(g, th, 5, () => { g.fillStyle = rgba(C.skinDk, 0.45); g.beginPath(); g.ellipse(-90, 20, 50, 10, -0.6, 0, 6.283); g.fill(); });
  g.fillStyle = rgba('#f6d6bc', 0.7); g.beginPath(); g.ellipse(-126, -30, 9, 12, -0.9, 0, 6.283); g.fill();
  // back of hand (knuckle arc on top)
  const back = [[-64, -44], [-32, -62], [0, -66], [30, -62], [60, -46], [66, 10], [58, 70], [36, 96], [-30, 98], [-56, 70], [-66, 10]];
  g.fillStyle = C.skin; g.beginPath(); crPath(g, back, true); g.fill();
  softIn(g, back, 12, () => { g.fillStyle = rgba(C.skinLt, 0.55); g.beginPath(); g.ellipse(-14, -6, 40, 40, 0, 0, 6.283); g.fill();
    g.fillStyle = rgba(C.skinDk, 0.6); g.beginPath(); g.ellipse(66, 40, 22, 70, 0, 0, 6.283); g.fill(); });
  // knuckle bumps + tendons (stronger when pressing)
  g.save(); g.globalAlpha = 0.3 + press * 0.3;
  [[-44, -50], [-16, -58], [14, -56], [41, -46]].forEach(([x, y]) => { g.fillStyle = C.skinLt; g.beginPath(); g.ellipse(x, y + 4, 11, 7, 0, 0, 6.283); g.fill(); });
  [[-44, -40, -20, 96], [-16, -48, -4, 96], [14, -46, 10, 96], [40, -38, 26, 94]].forEach(([x0, y0, x1, y1]) => brush(g, [[x0, y0], [lerp(x0, x1, 0.5), lerp(y0, y1, 0.5)], [x1, y1]], 5, 3, C.skinLt));
  g.restore();
  // wrist
  const wr = [[-50, 84], [44, 84], [48, 260], [-56, 260]];
  g.fillStyle = C.skin2; g.beginPath(); crPath(g, wr, true); g.fill();
  softIn(g, wr, 10, () => { g.fillStyle = rgba(C.skinDk, 0.5); g.fillRect(20, 80, 40, 200); });
  g.restore();
}

// ---------------------------------------------------------------- TEST: model sheet head
TESTS.head = (ctx, t) => {
  ctx.fillStyle = '#16110e'; ctx.fillRect(0, 0, W, H);
  const draw = (g, C) => { g.save(); g.translate(560, 820); g.scale(1.6, 1.6); bust34(g, C, { breath: 0 }); head34(g, C, { blink: 0, look: [-0.3, 0], brow: 0.3, sweat: 0.6, t }); g.restore(); };
  litRender(ctx, draw, (m) => { m.fillStyle = radGrad(m, 300, 600, 50, 1100, [[0, '#fff'], [0.6, 'rgba(255,255,255,0.6)'], [1, 'rgba(255,255,255,0)']]); m.fillRect(0, 0, W, H); },
    { rim: { dx: 10, dy: 0, col: '#ffb060', a: 0.8 } });
};

// ---------------------------------------------------------------- MODEL SHEET
TESTS.sheet = (ctx, t) => {
  ctx.fillStyle = linGrad(ctx, 0, 0, 0, H, [[0, '#2a211a'], [1, '#120e0b']]); ctx.fillRect(0, 0, W, H);
  const lightMask = (x, y, r) => (m) => { m.fillStyle = radGrad(m, x, y, 30, r, [[0, '#fff'], [0.55, 'rgba(255,255,255,0.75)'], [1, 'rgba(255,255,255,0.05)']]); m.fillRect(0, 0, W, H); };
  const put = (fn, x, y, sc, st, mask, rim) => litRender(ctx, (g, C) => { g.save(); g.translate(x, y); g.scale(sc, sc); fn(g, C, st); g.restore(); }, mask, { rim });
  ctx.font = '800 30px Inter'; ctx.fillStyle = '#e8d6b8'; ctx.textAlign = 'center';
  ctx.fillText('NIKIAS — PROTAGONIST MODEL SHEET', W / 2, 70);
  ctx.font = '600 20px Inter'; ctx.fillStyle = '#a89070';
  put(headFront, 190, 330, 0.62, { look: [0, 0] }, lightMask(150, 260, 380)); ctx.fillText('FRONT', 190, 520);
  put(head34, 540, 330, 0.62, { look: [-0.3, 0] }, lightMask(500, 260, 380)); ctx.fillText('THREE-QUARTER', 540, 520);
  put(headProfile, 880, 330, 0.62, {}, lightMask(820, 260, 380)); ctx.fillText('SIDE', 880, 520);
  // expressions
  const ex = [['NEUTRAL', {}], ['TENSION', { brow: 0.9, look: [-0.6, 0.1] }], ['HEAT / BREATH', { brow: 0.5, mouth: 0.8, sweat: 0.8 }], ['EXHAUSTION', { brow: 0.4, blink: 0.62, mouth: 0.35, sweat: 1, look: [0, 0.6] }]];
  ex.forEach(([n, st], i) => { const x = 140 + i * 267; put(head34, x, 760, 0.42, st, lightMask(x - 30, 700, 260)); ctx.fillText(n, x, 900); });
  // lighting conditions
  const L = [['WARM KEY', lightMask(200, 1120, 300), { dx: 6, dy: 0, col: '#ffb060', a: 0.7 }], ['LIGHT STREAK', (m) => { m.fillStyle = linGrad(m, 0, 1100, 0, 1180, [[0, 'rgba(255,255,255,0)'], [0.5, '#fff'], [1, 'rgba(255,255,255,0)']]); m.fillRect(0, 0, W, H); }, null],
  ['RIM ONLY', (m) => { }, { dx: -8, dy: 0, col: '#ff9a4a', a: 1 }]];
  L.forEach(([n, mk_, rim], i) => { const x = 190 + i * 350; put(head34, x, 1180, 0.5, { look: [-0.2, 0] }, mk_, rim); ctx.fillText(n, x, 1340); });
  // hands + bust
  put(handFlat, 200, 1600, 0.85, {}, lightMask(200, 1550, 300)); ctx.fillText('HAND — PRESSED FLAT', 200, 1860);
  put(handFlat, 470, 1600, 0.85, { curl: 0.6, press: 1 }, lightMask(470, 1550, 300)); ctx.fillText('HAND — STRAINING', 470, 1860);
  put((g, C, st) => { bust34(g, C, st); head34(g, C, st); }, 820, 1560, 0.48, { look: [-0.3, 0] }, lightMask(760, 1480, 420)); ctx.fillText('BUST / CHITON', 820, 1860);
};
