// V2 SHOTS: character acting inside the bull, cutaway match cuts, anatomy mapped onto the protagonist.
'use strict';
POSES.stand.nT = { c: [240, 640] };

// ------------------------------------------------------------------ environment: inside the bronze bull
function insideBull(ctx, t, cam = {}, opt = {}) {
  const cx = cam.x || 0, heat = opt.heat ?? 0.5, slits = opt.slits ?? 1;
  ctx.fillStyle = radGrad(ctx, W / 2 - cx * 0.3, H * 0.95, 60, H * 1.1, [[0, mix('#5a2a10', '#c2501a', heat)], [0.45, mix('#24120a', '#4a1a0a', heat)], [1, '#080403']]);
  ctx.fillRect(0, 0, W, H);
  // hammered back wall
  const r = mulberry(5); ctx.save(); ctx.globalCompositeOperation = 'screen';
  for (let i = 0; i < 220; i++) { const x = r() * (W + 400) - 200 - cx * 0.3, y = r() * H, rr = 14 + r() * 34; ctx.fillStyle = rgba('#b0703a', 0.025 + r() * 0.04); ctx.beginPath(); ctx.ellipse(x, y, rr, rr * 0.7, r() * 3, 0, 6.283); ctx.fill(); }
  ctx.restore();
  // ribs of the hollow body: big arcs, mid-ground parallax
  for (let k = -3; k <= 3; k++) {
    const x = W / 2 + k * 420 - cx * 0.55;
    ctx.save(); ctx.strokeStyle = rgba('#3a2210', 0.95); ctx.lineWidth = 46; ctx.beginPath(); ctx.ellipse(x, 1150, 330, 1250, k * 0.05, Math.PI * 1.02, Math.PI * 1.98); ctx.stroke();
    ctx.strokeStyle = rgba('#e0a050', 0.16 + heat * 0.12); ctx.lineWidth = 5; ctx.beginPath(); ctx.ellipse(x - 14, 1150, 312, 1232, k * 0.05, Math.PI * 1.05, Math.PI * 1.6); ctx.stroke();
    ctx.restore();
  }
  // seams of light (the slit) with volumetric beams + dust in the beams
  for (let i = 0; i < slits; i++) {
    const sx = 220 + i * 520 - cx * 0.4, a = 0.55 + 0.1 * Math.sin(t * 1.7 + i);
    ctx.save(); ctx.fillStyle = rgba('#ffe0a0', 0.9); ctx.fillRect(sx - 3, 0, 6, 160); ctx.restore();
    shaft(ctx, sx, 60, 30, sx + 360, 1700, 300, '#ffc070', 0.22 * a);
    motes(ctx, t, 40, 17 + i, { x0: sx - 40, x1: sx + 300, y0: 100, y1: 1600, vy: -18, vx: 10, size: [0.8, 2.4], col: '#ffe2b0', a: 0.75, life: 6 });
  }
  // belly floor: curved, glowing from the fire below, with heat shimmer
  ctx.save(); ctx.beginPath(); ctx.moveTo(-50, H); ctx.quadraticCurveTo(W / 2 - cx * 0.8, 1520, W + 50, H); ctx.closePath();
  ctx.fillStyle = linGrad(ctx, 0, 1560, 0, H, [[0, mix('#6a3214', '#d8682a', heat)], [1, mix('#2a1206', '#5a1e0a', heat)]]); ctx.fill(); ctx.restore();
  glow(ctx, W / 2 - cx * 0.8, 1700, 700, '#ff6a1a', 0.25 + 0.35 * heat);
  motes(ctx, t, 40, 23, { y0: 1500, y1: 1920, vy: -140, vx: 6, size: [1, 2.6], col: '#ffb060', a: 0.6 * heat + 0.2, life: 2.6 });
}
// foreground occluding rib (depth): a dark curved bronze rib hugging the frame edge (x<540: left edge, else right edge)
function foreRib(ctx, x, t, a = 1) {
  const left = x < 540, ex = left ? lerp(-90, 60, clamp((x + 60) / 180)) : lerp(W + 90, W - 60, clamp((W + 120 - x) / 180));
  const bend = left ? 1 : -1;
  ctx.save(); ctx.globalAlpha = a; ctx.filter = 'blur(9px)';
  const pts = [[ex - bend * 40, H + 40], [ex + bend * 30, H * 0.6], [ex + bend * 120, H * 0.22], [ex + bend * 320, -60]];
  brush(ctx, curvePts(pts, 30), 170, 120, '#120804', false);
  ctx.filter = 'blur(3px)'; brush(ctx, curvePts(pts.map(([px, py]) => [px + bend * 68, py]), 30), 8, 5, 'rgba(255,170,90,0.35)', false);
  ctx.restore();
}
// ------------------------------------------------------------------ character render wrappers
function heatPalette(k) { return warmPal(k); }
function drawNikias(ctx, pose, t, X, opt = {}) {
  // X: [x, y, scale]; light: slit key from upper-left + fire from below
  const pal = heatPalette(opt.heat ?? 0.5);
  litRender(ctx, (g, C) => { g.save(); g.translate(X[0], X[1]); g.scale(X[2], X[2]); figure(g, C, pose, t, { lag: opt.lag || 0 }); g.restore(); },
    (m) => { radialMask(m, X[0] - 260 * X[2], X[1] - 700 * X[2], 30, 1300 * X[2], opt.key ?? 0.9); m.globalCompositeOperation = 'lighter'; lightBand(m, X[1] + 900 * X[2], 500 * X[2], 0.35 * (opt.heat ?? 0.5)); },
    Object.assign({ rim: { dx: 5 * X[2] / 0.6, dy: 2, col: opt.rimCol || '#ffa050', a: opt.rimA ?? 0.85 } }, pal));
}
// silhouette canvas of the figure (for overlays)
function silhouette(name, pose, t, X) {
  const S = cvs(name), g = S.getContext('2d');
  g.save(); g.translate(X[0], X[1]); g.scale(X[2], X[2]); const J = figure(g, SKIN_SHD, pose, t); g.restore();
  g.globalCompositeOperation = 'source-in'; g.fillStyle = '#fff'; g.fillRect(0, 0, W, H); g.globalCompositeOperation = 'source-over';
  return { S, J };
}
function clipTo(ctx, S, drawFn) { const L = cvs('clipL'), g = L.getContext('2d'); drawFn(g); g.globalCompositeOperation = 'destination-in'; g.drawImage(S, 0, 0); ctx.drawImage(L, 0, 0); }
function silRim(ctx, S, col, a = 1, dx = 6, dy = 2) {
  const e = cvs('silRim2'), eg = e.getContext('2d'); eg.drawImage(S, 0, 0); eg.globalCompositeOperation = 'source-in'; eg.fillStyle = col; eg.fillRect(0, 0, W, H);
  eg.globalCompositeOperation = 'destination-out'; eg.drawImage(S, dx, dy); eg.globalCompositeOperation = 'source-over';
  ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.globalAlpha = a; ctx.filter = 'blur(1.5px)'; ctx.drawImage(e, 0, 0); ctx.filter = 'blur(12px)'; ctx.globalAlpha = a * 0.7; ctx.drawImage(e, 0, 0); ctx.restore();
}
// joints -> screen
const XP = (X, p) => [X[0] + p[0] * X[2], X[1] + p[1] * X[2]];
// X-ray skeleton mapped onto the posed rig
function xrayBones(g, J, X, a = 1, col = '#cfe8ff') {
  g.save(); g.globalAlpha = a; g.strokeStyle = col; g.lineCap = 'round';
  const L = (A, B, w) => { const p = XP(X, A), q = XP(X, B); g.lineWidth = w * X[2]; g.beginPath(); g.moveTo(p[0], p[1]); g.lineTo(q[0], q[1]); g.stroke();
    g.fillStyle = col; for (const z of [p, q]) { g.beginPath(); g.arc(z[0], z[1], w * X[2] * 0.75, 0, 6.283); g.fill(); } };
  L(J.root, J.chest, 22); L(J.chest, J.neck, 18);
  L(J.nSh, J.nElb, 20); L(J.nElb, J.nWr, 15); L(J.fSh, J.fElb, 18); L(J.fElb, J.fWr, 14);
  L(J.nHip, J.nKn, 26); L(J.nKn, J.nAn, 20); L(J.fHip, J.fKn, 24); L(J.fKn, J.fAn, 18);
  // ribcage arcs around the chest
  for (let i = 0; i < 7; i++) { const u = i / 7; const c = XP(X, [lerp(J.chest[0], J.root[0], 0.15 + u * 0.45), lerp(J.chest[1], J.root[1], 0.15 + u * 0.45)]);
    g.lineWidth = 8 * X[2]; g.beginPath(); g.ellipse(c[0], c[1], 170 * X[2], 50 * X[2], -0.1, Math.PI * 0.95, Math.PI * 2.05); g.stroke(); }
  const pel = XP(X, J.root); g.lineWidth = 14 * X[2]; g.beginPath(); g.ellipse(pel[0], pel[1], 150 * X[2], 70 * X[2], 0, 0, 6.283); g.stroke();
  const sk = XP(X, [J.neck[0] - 30, J.neck[1] - 220]); g.lineWidth = 12 * X[2]; g.beginPath(); g.ellipse(sk[0], sk[1], 150 * X[2], 170 * X[2], 0, 0, 6.283); g.stroke();
  g.restore();
}
// nervous system mapped onto the posed rig (brain, cord, limb nerves + branches), impulses on kicks
function rigNerves(g, J, X, t, opt = {}) {
  const rev = opt.reveal ?? 1, col = opt.col || '#f6d58e', dist = opt.disturb || 0;
  const paths = [
    [[J.neck[0] - 40, J.neck[1] - 200], J.neck, J.chest, J.root],
    [J.chest, J.nSh, J.nElb, J.nWr], [J.chest, J.fSh, J.fElb, J.fWr],
    [J.root, J.nHip, J.nKn, J.nAn], [J.root, J.fHip, J.fKn, J.fAn],
  ];
  const r = mulberry(7);
  g.save(); g.lineCap = 'round'; g.lineJoin = 'round';
  paths.forEach((P, i) => {
    const pts = curvePts(P.map(p => XP(X, p)), 40); const m = Math.max(2, Math.floor(pts.length * clamp(rev * 1.25 - i * 0.05)));
    const pp = pts.slice(0, m);
    const zw = Math.min(1.4, Math.sqrt(X[2] / 0.72)); g.strokeStyle = rgba(col, 0.9); g.lineWidth = (i ? 6 : 9) * zw; g.beginPath(); pp.forEach(([x, y], k) => k ? g.lineTo(x, y) : g.moveTo(x, y)); g.stroke();
    g.save(); g.globalCompositeOperation = 'screen'; g.filter = 'blur(8px)'; g.strokeStyle = rgba(col, 0.5); g.lineWidth = 20 * zw; g.stroke(); g.restore();
    // branches
    for (let k = 4; k < pp.length - 2; k += 3) { const [x, y] = pp[k]; const a2 = r() * 6.28, L = (30 + r() * 70) * X[2] / 0.6;
      g.strokeStyle = rgba(col, 0.55); g.lineWidth = 2; g.beginPath(); g.moveTo(x, y); g.quadraticCurveTo(x + Math.cos(a2) * L * 0.5 + 8, y + Math.sin(a2) * L * 0.5, x + Math.cos(a2) * L, y + Math.sin(a2) * L); g.stroke(); }
    // impulses
    if (rev >= 1) for (let q = 0; q < 2; q++) { let u = ((t * 0.9 + i * 0.21 + q * 0.5) % 1); if (dist) u = clamp(u + Math.sin(t * 11 + i) * dist * 0.06);
      const [x, y] = pts[Math.floor(u * (pts.length - 1))]; const fl = dist ? (hash(Math.floor(t * 12) + i * 3 + q) > dist * 0.6 ? 1 : 0.15) : 1;
      glow(g, x, y, 36 * zw, dist > 0.35 && (i + q) % 3 === 0 ? '#ff8a5a' : '#fff4cc', 0.95 * fl); }
  });
  g.restore();
}

// ------------------------------------------------------------------ exterior: bull with an artistic cutaway into its flank
function bullCutaway(ctx, bx, by, sc, t, opt = {}) {
  const open = opt.open ?? 1, heat = opt.heat ?? 0.6;
  bullLayer(ctx, bx, by, sc, { glow: opt.fire ?? 1, t, eyeGlow: opt.eyeGlow || 0 });
  if (open <= 0) return;
  const wx = bx + (-70) * sc, wy = by + (-410) * sc, rx = 250 * sc * open, ry = 140 * sc * open;
  const win = []; for (let i = 0; i < 36; i++) { const a = i / 36 * 6.283; const n = 1 + 0.07 * Math.sin(a * 5 + 1.3) + 0.04 * Math.sin(a * 11); win.push([wx + Math.cos(a) * rx * n, wy + Math.sin(a) * ry * n]); }
  // interior seen through the opening
  ctx.save(); ctx.beginPath(); crPath(ctx, win, true); ctx.clip();
  ctx.fillStyle = radGrad(ctx, wx, wy + ry, 10, rx * 1.4, [[0, mix('#8a3a12', '#ff6a1a', heat)], [0.5, mix('#3a1a0a', '#7a2a0c', heat)], [1, '#0e0604']]); ctx.fillRect(wx - rx * 1.5, wy - ry * 1.5, rx * 3, ry * 3);
  for (let k = -2; k <= 2; k++) { ctx.strokeStyle = 'rgba(30,14,6,0.9)'; ctx.lineWidth = 10 * sc; ctx.beginPath(); ctx.ellipse(wx + k * 120 * sc, wy + ry * 0.6, 70 * sc, ry * 1.6, 0, Math.PI, Math.PI * 2); ctx.stroke(); }
  if (opt.pose) {
    const X = [wx + 40 * sc, wy + ry * 0.92 - 1060 * 0.16 * sc / 0.98, 0.16 * sc];
    const { S } = silhouette('cutSil', opt.pose, t, X);
    const D = cvs('cutSilD'), dg = D.getContext('2d'); dg.drawImage(S, 0, 0); dg.globalCompositeOperation = 'source-in'; dg.fillStyle = '#120604'; dg.fillRect(0, 0, W, H);
    ctx.drawImage(D, 0, 0); silRim(ctx, S, '#ffb060', 0.9, 2, 1);
  }
  shaft(ctx, wx - rx * 0.5, wy - ry, 6 * sc, wx + rx * 0.2, wy + ry, 60 * sc, '#ffd08a', 0.35);
  ctx.restore();
  // the cut edge: bronze thickness with a hot inner bevel
  ctx.save(); ctx.lineJoin = 'round';
  ctx.strokeStyle = '#1a0c05'; ctx.lineWidth = 22 * sc; ctx.beginPath(); crPath(ctx, win, true); ctx.stroke();
  ctx.strokeStyle = rgba('#ffb868', 0.85); ctx.lineWidth = 4 * sc; ctx.beginPath(); crPath(ctx, win.map(([x, y]) => [x + (x - wx) * 0.04, y + (y - wy) * 0.04]), true); ctx.stroke();
  ctx.globalCompositeOperation = 'screen'; ctx.filter = 'blur(10px)'; ctx.strokeStyle = rgba('#ff7a2a', 0.6 * heat + 0.2); ctx.lineWidth = 24 * sc; ctx.beginPath(); crPath(ctx, win, true); ctx.stroke();
  ctx.restore();
}

// ================================================================== V2 SHOT 01 — opening: eyes -> inside -> cutaway -> hero
function v01(ctx, t) {
  if (t < EV.w_brazen) { s01(ctx, Math.min(t, 0.75)); return; }       // eyes in the streak (V1 close-up, faster)
  if (t < EV.w_bull) {
    // inside: he is pressed against the bronze, camera rushing back
    const lt = t - EV.w_brazen, k = ease.out3(clamp(lt / 0.6));
    insideBull(ctx, t, { x: lerp(-60, 0, k) }, { heat: 0.45 });
    const pose = secondary(poseAt(t, [[EV.w_brazen, 'push'], [EV.w_bull, 'push']]), t, { breath: 1.2, tremble: 0.6, rate: 3.4 });
    pose.face = { brow: 0.8, mouth: 0.4, sweat: 0.6, look: [-0.5, -0.1], blink: blinkAt(t) };
    const s = lerp(1.05, 0.62, k);
    drawNikias(ctx, pose, t, [lerp(600, 620, k), lerp(820, 760, k), s], { heat: 0.45 });
    foreRib(ctx, lerp(-60, 120, k), t);
    return;
  }
  // exterior hero: the bull with the cutaway, he is visible inside; fast pull then slow orbit
  const lt = t - EV.w_bull, k = ease.out5(clamp(lt / 0.75));
  const sc = lerp(2.4, 0.98, k) + 0.04 * ease.io2(clamp((lt - 0.75) / 1.4));
  const bx = lerp(700, 620, k), by = lerp(2050, 1520, k);
  const L = cvs('v01'), g = L.getContext('2d');
  courtyard(g, { x: lerp(40, 0, k) - lt * 18, y: 0, s: 1.15, hz: 1300, bullX: -9999, bullY: by, bullS: sc }, t, { fire: 1 });
  g.save(); g.translate(bx, by); g.scale(sc, sc); plinth(g); g.restore();
  glow(g, bx, by, 520 * sc, '#ff6a1a', 0.35);
  bullCutaway(g, bx, by, sc, t, { open: 1, heat: 0.6, pose: secondary(blendPose('push', 'push', 0), t, { breath: 1, tremble: 0.5 }), eyeGlow: 0.25 });
  motes(g, t, 60, 7, { x0: bx - 380 * sc, x1: bx + 380 * sc, y0: by - 40, y1: by + 80, vy: -120, vx: 10, size: [1, 3], col: '#ffb060', a: 0.85, life: 3.5 });
  ctx.drawImage(L, 0, 0);
}
// courtyard() draws a bull; allow skipping it via bullX:-9999
const _court = courtyard;
courtyard = function (ctx, cam, t, opt = {}) {
  if (cam.bullX > -9000) return _court(ctx, cam, t, opt);
  const c2 = Object.assign({}, cam, { bullX: -5000 }); _court(ctx, c2, t, Object.assign({}, opt, { fire: 0 }));
};

// ================================================================== V2 SHOT 03 — EXTREME HEAT: acting inside the bull
function v03(ctx, t) {
  const lt = t - 7.06;
  const keys = [[7.06, 'brace'], [7.32, 'gasp', ease.out3], [7.75, 'gasp'], [8.15, 'wipe', ease.io3], [8.9, 'wipe'], [9.25, 'gasp', ease.io2], [9.85, 'gasp'], [10.3, 'brace', ease.io3]];
  let pose = poseAt(t, keys);
  // wiping motion: hand sweeps across the brow while in 'wipe'
  const wipeK = env(t, 8.15, 8.9, 0.15, 0.15);
  if (wipeK > 0) pose.nT = [pose.nT[0] + Math.sin((t - 8.15) * 7) * 70 * wipeK, pose.nT[1] + Math.cos((t - 8.15) * 7) * 12 * wipeK];
  pose = secondary(pose, t, { breath: lerp(1.2, 2.4, inv(8.8, 9.8, t)), tremble: 0.3, rate: lerp(2.8, 4.6, inv(8.8, 9.8, t)) });
  const heat = lerp(0.5, 0.85, inv(0, 3.5, lt));
  pose.face = { brow: lerp(0.4, 0.85, inv(0, 3, lt)), mouth: 0.25 + 0.5 * env(t, 7.2, 10.5, 0.3, 0.3) * (0.6 + 0.4 * Math.sin(t * 4)), sweat: lerp(0.5, 1, inv(0, 3, lt)), look: [-0.2, wipeK > 0 ? -0.3 : 0.1], blink: Math.max(blinkAt(t), wipeK * 0.7) };
  const cam = ease.io2(inv(0, 3.5, lt));
  const L = cvs('v03bg'), g = L.getContext('2d');
  insideBull(g, t, { x: lerp(-80, 60, cam) }, { heat, slits: 2 });
  ctx.drawImage(L, 0, 0); heatShimmer(ctx, L, t, 2 + 4 * heat, 1100, H);
  const recoil = kick(t, 7.32, 7, 2.2) * 30;
  drawNikias(ctx, pose, t, [lerp(560, 600, cam) + recoil, lerp(800, 760, cam), lerp(0.66, 0.74, cam)], { heat, lag: Math.sin((t - 7.3) * 4) * kick(t, 7.32, 2) });
  // hot bronze contact flare where his hand left the wall
  glow(ctx, 160, 640, 140, '#ffb060', 0.9 * kick(t, 7.32, 4));
  foreRib(ctx, lerp(980, 1080, cam), t, 0.95);
  motes(ctx, t, 50, 33, { y0: 1100, y1: 1920, vy: -220, vx: 20, size: [1, 3], col: '#ffb060', a: 0.6 * heat, life: 2.2 });
}

// ================================================================== V2 SHOT 04 — scan lens on his forearm -> skin
function v04(ctx, t) {
  const lt = t - EV.scan1;
  const lens = ease.io3(inv(0.0, 0.75, lt));
  if (lens < 1) {
    // close-up of his forearm braced on the hot wall
    insideBull(ctx, t, { x: 100 }, { heat: 0.85 });
    const pose = secondary(blendPose('brace', 'brace', 0), t, { breath: 2, tremble: 0.5, rate: 4.4 });
    pose.face = { brow: 0.9, mouth: 0.6, sweat: 1, look: [-0.3, 0.1] };
    drawNikias(ctx, pose, t, [1100, 900, 1.55], { heat: 0.85 });
  }
  if (lens > 0) {
    const R = lerp(0, 1500, lens), cx = 420, cy = 760;
    const L = cvs('v04'), g = L.getContext('2d');
    s04(g, t);
    ctx.save(); ctx.beginPath(); ctx.arc(cx, cy, R, 0, 6.283); ctx.clip(); ctx.drawImage(L, 0, 0); ctx.restore();
    if (lens < 1) { ctx.save(); ctx.strokeStyle = rgba('#bfe8ff', 0.9); ctx.lineWidth = 6; ctx.beginPath(); ctx.arc(cx, cy, R, 0, 6.283); ctx.stroke();
      ctx.globalCompositeOperation = 'screen'; ctx.filter = 'blur(12px)'; ctx.lineWidth = 30; ctx.stroke(); ctx.restore(); }
  }
}

// ================================================================== V2 SHOT 05/06 — vessel -> flow -> heart (bigger, layered)
function v05(ctx, t) {
  const rush = ease.in3(inv(EV.slam2 - 0.55, EV.slam2, t));
  ctx.save(); if (rush > 0) { ctx.translate(-rush * 900, 0); }
  s05(ctx, t);
  ctx.restore();
  // foreground drifting cells (depth)
  const r = mulberry(19); ctx.save(); ctx.filter = 'blur(9px)';
  for (let i = 0; i < 6; i++) { const x = ((r() * W + t * (200 + rush * 1800) * (0.5 + r())) % (W + 400)) - 200, y = r() * H, s = 60 + r() * 50;
    ctx.fillStyle = 'rgba(200,40,50,0.55)'; ctx.beginPath(); ctx.ellipse(W - x, y, s, s * 0.55, r() * 3, 0, 6.283); ctx.fill(); }
  ctx.restore();
}
function v06(ctx, t) {
  const lt = t - EV.slam2;
  ctx.save(); ctx.translate(W / 2, H / 2); const s = lerp(1.25, 1.12, ease.out3(inv(0, 1, lt))); ctx.scale(s, s); ctx.translate(-W / 2, -H / 2 - 40); s06(ctx, t); ctx.restore();
  // flowing cells crossing the foreground
  const r = mulberry(29); ctx.save(); ctx.filter = 'blur(7px)';
  for (let i = 0; i < 7; i++) { const u = ((lt * (0.25 + r() * 0.2) + r()) % 1); const x = lerp(-150, W + 150, u), y = lerp(200, 1800, r()); ctx.fillStyle = 'rgba(210,50,60,0.5)'; ctx.beginPath(); ctx.ellipse(x, y, 56, 30, r() * 3, 0, 6.283); ctx.fill(); }
  ctx.restore();
}

// ================================================================== V2 SHOT 07 — water & salts leave HIS body
function v07(ctx, t) {
  const lt = t - EV.shriek1;
  insideBull(ctx, t, { x: 0 }, { heat: 0.9, slits: 1 });
  ctx.save(); ctx.globalAlpha = 0.72; ctx.fillStyle = '#05070c'; ctx.fillRect(0, 0, W, H); ctx.restore();
  const pose = secondary(poseAt(t, [[EV.shriek1, 'gasp'], [22.5, 'wipe'], [23.1, 'wipe']]), t, { breath: 2.2, tremble: 0.4, rate: 4 });
  const X = [560, 820, 0.68];
  const { S, J } = silhouette('v07s', pose, t, X);
  const drain = ease.io2(inv(0.15, 1.9, lt));
  const lvl = lerp(XP(X, J.neck)[1] - 40, XP(X, J.root)[1] + 200, drain);
  clipTo(ctx, S, (g) => {
    g.fillStyle = 'rgba(14,30,52,0.92)'; g.fillRect(0, 0, W, H);
    g.fillStyle = linGrad(g, 0, lvl, 0, H, [[0, rgba('#5ac8ff', 0.75)], [1, rgba('#1a6aa0', 0.6)]]); g.fillRect(0, lvl, W, H);
    g.strokeStyle = '#d8f4ff'; g.lineWidth = 5; g.beginPath(); for (let x = 0; x <= W; x += 12) g.lineTo(x, lvl + Math.sin(x * 0.03 + t * 6) * 7); g.stroke();
  });
  silRim(ctx, S, '#7fd6ff', 0.9, 4, 1);
  // droplets + ions leaving the skin
  const r = mulberry(55);
  for (let i = 0; i < 50; i++) {
    const side = r() < 0.5 ? -1 : 1, y0 = lerp(300, 1500, r()), ph = r(), sp = 0.6 + r() * 0.6;
    const u = ((lt * sp + ph) % 1.2); if (u > 1) continue;
    const x = 560 + side * (170 + ease.out2(u) * 380), y = y0 - u * 120, a = Math.sin(Math.PI * u) * inv(0, 0.3, lt);
    ctx.save(); ctx.globalAlpha = a;
    if (i % 3 === 0) { ctx.fillStyle = '#ffd27a'; ctx.font = '800 32px Inter'; ctx.textAlign = 'center'; ctx.fillText(['Na⁺', 'K⁺', 'Cl⁻'][i % 2 ? 1 : (i % 9 === 0 ? 0 : 2)], x, y); }
    else { ctx.fillStyle = '#9fdcff'; ctx.beginPath(); ctx.ellipse(x, y, 9, 12, 0, 0, 6.283); ctx.fill(); ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(x - 3, y - 4, 2.5, 0, 6.283); ctx.fill(); }
    ctx.restore();
  }
  label(ctx, 760, 760, 680, 640, 'ELECTROLYTES', '#ffd27a', env(lt, 0.4, 1.9, 0.25, 0.2));
}

// ================================================================== V2 SHOT 08 — WEAKNESS: he sinks to his knees
function v08(ctx, t) {
  const lt = t - EV.riser;
  const keys = [[EV.riser, 'wipe'], [23.25, 'stand', ease.io2], [23.55, 'sink', ease.in2], [23.82, 'kneel', ease.out3], [24.7, 'kneel']];
  let pose = poseAt(t, keys);
  const land = kick(t, 23.82, 9, 3);            // impact overshoot when the knee hits
  pose.y += land * 40; pose.spine -= land * 0.08; pose.head += land * 0.15;
  pose = secondary(pose, t, { breath: 2.4, tremble: 0.5, rate: 4.8 });
  pose.face = { brow: 0.7, mouth: 0.55 + 0.2 * Math.sin(t * 5), sweat: 1, look: [0, 0.6], blink: Math.max(blinkAt(t), 0.45) };
  const L = cvs('v08bg'), g = L.getContext('2d'); insideBull(g, t, { x: 40 }, { heat: 0.9, slits: 1 });
  ctx.save(); ctx.translate(W / 2, H / 2); ctx.rotate(lerp(0, -0.05, inv(0, 1.7, lt))); ctx.translate(-W / 2, -H / 2);
  ctx.drawImage(L, 0, 0); heatShimmer(ctx, L, t, 5, 1200, H);
  drawNikias(ctx, pose, t, [600, 720, 0.78], { heat: 0.9, lag: -land * 1.2 });
  // dust kicked up where the knee and hand hit the hot floor
  for (const [x, y] of [[480, 1610], [240, 1560]]) { glow(ctx, x, y, 160, '#ffb070', 0.6 * kick(t, 23.82, 5)); motes(ctx, t, 20, 3 + x, { x0: x - 60, x1: x + 60, y0: y - 20, y1: y + 10, vy: -90, size: [1, 3], col: '#ffc890', a: kick(t, 23.82, 2), life: 1 }); }
  ctx.restore();
  foreRib(ctx, -40, t, 0.9);
}

// ================================================================== V2 SHOT 09 — pre-drop: his kneeling silhouette -> X-ray
function v09(ctx, t) {
  const lt = t - EV.predrop, heat = inv(0, 1.32, lt);
  ctx.fillStyle = '#070304'; ctx.fillRect(0, 0, W, H);
  glow(ctx, 560, 1000, lerp(600, 1200, heat), '#ff4a14', lerp(0.4, 0.95, heat));
  const pose = secondary(blendPose('kneel', 'kneel', 0), t, { breath: 2.6, tremble: 0.6, rate: 5 });
  const X = [600, 640, lerp(0.82, 0.9, ease.io2(heat))];
  const { S, J } = silhouette('v09s', pose, t, X);
  const scanY = lerp(-100, H + 100, ease.io3(inv(25.33, EV.power1, t)));
  const burst = inv(EV.power1 - 0.05, EV.power1 + 0.08, t);
  // dark silhouette with fire rim
  const D = cvs('v09d'), dg = D.getContext('2d'); dg.drawImage(S, 0, 0); dg.globalCompositeOperation = 'source-in'; dg.fillStyle = '#060203'; dg.fillRect(0, 0, W, H);
  ctx.drawImage(D, 0, 0); silRim(ctx, S, '#ffb060', 1, 9, 3);
  if (t > 25.33) {
    ctx.save(); ctx.beginPath(); ctx.rect(0, 0, W, scanY); ctx.clip();
    clipTo(ctx, S, (g) => { g.fillStyle = burst > 0 ? mix('#0a1626', '#3a1a0a', burst) : '#0a1626'; g.fillRect(0, 0, W, H); });
    xrayBones(ctx, J, X, 0.85, burst > 0 ? '#ffe0a8' : '#cfe8ff');
    silRim(ctx, S, burst > 0 ? '#ffd08a' : '#7fd6ff', 1, 4, 1);
    ctx.restore();
    ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.fillStyle = linGrad(ctx, 0, scanY - 60, 0, scanY + 4, [[0, 'rgba(127,214,255,0)'], [1, 'rgba(200,240,255,0.95)']]); ctx.fillRect(0, scanY - 60, W, 64); ctx.restore();
  }
  motes(ctx, t, 90, 51, { vy: -260, vx: 30, size: [1, 3.5], col: '#ffb060', a: 0.8, life: 2 });
}

// ================================================================== V2 SHOT 10 — DROP: nervous system ignites inside him
function v10(ctx, t) {
  const lt = t - EV.drop1;
  const keys = [[EV.drop1, 'kneel'], [26.8, 'gasp', ease.out3], [28.6, 'gasp'], [29.6, 'temples', ease.io3]];
  const pose = secondary(poseAt(t, keys), t, { breath: 2, tremble: 0.5, rate: 4.2 });
  pose.y += lerp(0, 0, 0);
  anatomyField(ctx, t, { warm: 0.15 });
  const cam = ease.io3(inv(0, 2.6, lt));
  const X = [lerp(760, 560, cam), lerp(1500, 760, cam), lerp(1.9, 0.72, cam)];
  const { S, J } = silhouette('v10s', pose, t, X);
  clipTo(ctx, S, (g) => { g.fillStyle = 'rgba(16,30,50,0.9)'; g.fillRect(0, 0, W, H); });
  silRim(ctx, S, '#7fd6ff', 0.9, 4, 1);
  rigNerves(ctx, J, X, t, { reveal: ease.out3(inv(0, 0.8, lt)), disturb: 0.2 * inv(1.5, 3.5, lt) });
  const head = XP(X, [J.neck[0] - 50, J.neck[1] - 210]);
  ctx.save(); ctx.translate(head[0], head[1]); ctx.rotate(-(pose.spine + pose.head) * 0.6); ctx.scale(0.27 * X[2] / 0.72, 0.27 * X[2] / 0.72); brainLat(ctx, { t, glow: '#ffe6a8' }); ctx.restore();
  glow(ctx, head[0], head[1], 900 * (1 - inv(0, 0.5, lt)), '#ffd890', 0.6 * (1 - inv(0, 0.5, lt)));
}

// ================================================================== V2 SHOT 11 — DIZZINESS: first-person, through his own hands
function v11(ctx, t) {
  const frozen = t >= EV.slam3, tt = frozen ? EV.slam3 : t, lt = tt - 30.0;
  const sway = Math.sin(tt * 1.6) * 0.09 + Math.sin(tt * 2.9) * 0.04;
  const L = cvs('v11'), g = L.getContext('2d');
  g.save(); camApply(g, W / 2, H / 2, 1.25 + Math.sin(tt * 1.1) * 0.08, sway, W / 2 + Math.sin(tt * 0.8) * 60, H / 2);
  insideBull(g, tt, { x: Math.sin(tt * 0.7) * 160 }, { heat: 0.8, slits: 2 });
  g.restore();
  // swirl smear of the light seams
  ctx.drawImage(L, 0, 0);
  ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.globalAlpha = 0.35;
  for (let k = 1; k <= 3; k++) { ctx.save(); ctx.translate(W / 2, H * 0.4); ctx.rotate(Math.sin(tt * 1.3) * 0.05 * k); ctx.scale(1 + 0.03 * k, 1 + 0.03 * k); ctx.translate(-W / 2, -H * 0.4); ctx.drawImage(L, 0, 0); ctx.restore(); }
  ctx.restore();
  // double vision offset ghost
  const dv = 24 + 30 * Math.abs(Math.sin(tt * 1.7)) + 26 * kickPulse(tt, 6);
  ctx.save(); ctx.globalAlpha = 0.35; ctx.globalCompositeOperation = 'screen'; ctx.drawImage(L, dv, -dv * 0.3); ctx.restore();
  // tunnel vignette
  ctx.save(); ctx.fillStyle = radGrad(ctx, W / 2, H * 0.5, 320 + 80 * Math.sin(tt * 2), 1150, [[0, 'rgba(0,0,0,0)'], [1, 'rgba(20,4,2,0.8)']]); ctx.fillRect(0, 0, W, H); ctx.restore();
  // his hands in the foreground (POV), trembling, slightly out of focus, swaying with the view
  const H1 = cvs('v11h'), hg = H1.getContext('2d');
  const handsDraw = (gg, C) => {
    const tr = 0.8; const hpL = handPose(['splay', 'relax', 0.15 + 0.15 * Math.sin(tt * 2)]), hpR = handPose(['splay', 'relax', 0.15 + 0.15 * Math.sin(tt * 2 + 1)]);
    gg.save(); gg.translate(250 + Math.sin(tt * 1.6) * 40 + vnoise(tt * 8) * 10, 1880 + Math.sin(tt * 2.1) * 30); gg.rotate(-0.22 + sway); gg.scale(2.3, 2.3);
    limb(gg, C, [0, 300], [0, 0], 96, 74, { bulge: 0.12 }); hand(gg, C, [0, 0], Math.PI, hpL, 1, 1, tr, tt); gg.restore();
    gg.save(); gg.translate(840 + Math.sin(tt * 1.6 + 1) * 40 + vnoise(tt * 8 + 4) * 10, 1910 + Math.sin(tt * 2.1 + 1) * 30); gg.rotate(0.22 + sway); gg.scale(-2.3, 2.3);
    limb(gg, C, [0, 300], [0, 0], 96, 74, { bulge: 0.12 }); hand(gg, C, [0, 0], Math.PI, hpR, 1, 1, tr, tt); gg.restore();
  };
  litRender(hg, handsDraw, (m) => { m.fillStyle = '#fff'; m.fillRect(0, 0, W, H); }, Object.assign({ rim: { dx: -6, dy: -5, col: '#ffc070', a: 1 } }, warmPal(0.7)));
  ctx.save(); ctx.filter = `blur(${0.5 + 1.5 * Math.abs(Math.sin(tt * 1.4))}px)`; ctx.drawImage(H1, 0, 0); ctx.globalAlpha = 0.3; ctx.drawImage(H1, dv * 0.6, 0); ctx.restore();
  if (frozen) { const k = inv(EV.slam3, EV.slam3 + 0.2, t); ctx.save(); ctx.globalCompositeOperation = 'saturation'; ctx.globalAlpha = 0.9 * k; ctx.fillStyle = '#808080'; ctx.fillRect(0, 0, W, H); ctx.restore();
    ctx.save(); ctx.globalAlpha = 0.45 * k; ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
}

// ================================================================== V2 SHOT 12 — thermoregulation mapped on his staggering body
function v12(ctx, t) {
  const lt = t - EV.scan3, k = inv(0, 3.5, lt);
  insideBull(ctx, t, { x: -40 + lt * 20 }, { heat: 0.9 });
  ctx.save(); ctx.globalAlpha = 0.6; ctx.fillStyle = '#04070d'; ctx.fillRect(0, 0, W, H); ctx.restore();
  const pose = secondary(poseAt(t, [[EV.scan3, 'temples'], [35.0, 'brace', ease.io3], [36.4, 'temples', ease.io3]]), t, { breath: 2, tremble: 0.6, rate: 4.2 });
  const X = [lerp(600, 560, k), 760, 0.72];
  const { S, J } = silhouette('v12s', pose, t, X);
  const core = XP(X, [lerp(J.root[0], J.chest[0], 0.5), lerp(J.root[1], J.chest[1], 0.5)]);
  clipTo(ctx, S, (g) => {
    g.fillStyle = 'rgba(14,26,44,0.95)'; g.fillRect(0, 0, W, H);
    g.fillStyle = radGrad(g, core[0], core[1], 20, lerp(250, 1000, k), [[0, rgba('#ff5a1a', 0.95)], [0.45, rgba('#ff8a2a', 0.55)], [1, rgba('#ffb04a', 0.0)]]); g.fillRect(0, 0, W, H);
  });
  silRim(ctx, S, mix('#7fd6ff', '#ffb07a', k), 0.95, 4, 1);
  // heat flowing from the core outward (struggling, turbulent)
  ctx.save(); ctx.globalCompositeOperation = 'screen';
  for (let i = 0; i < 20; i++) { const a = i / 20 * 6.283, u = ((lt * 0.8 + i * 0.137) % 1), len = 240 + (i % 3) * 70;
    const pts = []; for (let s2 = 0; s2 <= 1; s2 += 0.1) { const rr = s2 * len * (0.3 + 0.7 * u); pts.push([core[0] + Math.cos(a) * rr + Math.sin(s2 * 7 + t * 5 + i) * 14 * k, core[1] + Math.sin(a) * rr * 1.5]); }
    ctx.strokeStyle = rgba('#ffc07a', 0.55 * (1 - u)); ctx.lineWidth = 4; ctx.beginPath(); crPath(ctx, pts, false); ctx.stroke(); }
  ctx.restore();
  const hyp = XP(X, [J.neck[0] - 60, J.neck[1] - 170]);
  glow(ctx, hyp[0], hyp[1], 70, '#9fdcff', 0.6 + 0.4 * Math.sin(t * 7));
  label(ctx, hyp[0], hyp[1], hyp[0] + 160, hyp[1] - 150, 'HYPOTHALAMUS', '#9fdcff', env(lt, 0.4, 3.3, 0.3, 0.3));
  // sweat streaming off his outline
  const r = mulberry(77); for (let i = 0; i < 26; i++) { const x = lerp(300, 820, r()), y0 = lerp(300, 1500, r()), u = ((t * 0.7 + r()) % 1);
    ctx.fillStyle = rgba('#bfe8ff', 0.8 * Math.sin(Math.PI * u)); ctx.beginPath(); ctx.ellipse(x, y0 + u * 60, 6, 9, 0, 0, 6.283); ctx.fill(); }
}

// ================================================================== V2 SHOT 13 — HEATSTROKE: exterior cutaway, red-hot interior
function v13(ctx, t) {
  const lt = t - EV.clank;
  const L = cvs('v13'), g = L.getContext('2d');
  const mv = ease.io2(inv(0, 3.5, lt));
  courtyard(g, { x: lerp(-60, 60, mv), y: 0, s: 1.4, hz: 1560, bullX: -9999, bullY: 1640, bullS: 1.12 }, t, { fire: 1 });
  const bx = lerp(700, 660, mv), by = 1660, sc = lerp(1.12, 1.2, mv);
  g.save(); g.translate(bx, by); g.scale(sc, sc); plinth(g); g.restore();
  glow(g, bx, by, 700, '#ff3a10', 0.5 + 0.1 * kickPulse(t, 5));
  bullCutaway(g, bx, by, sc, t, { open: ease.out3(inv(0, 0.5, lt)), heat: 1, pose: secondary(blendPose('kneel', 'kneel', 0), t, { breath: 2, tremble: 0.6 }), eyeGlow: 0.5 });
  ctx.drawImage(L, 0, 0);
  ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.fillStyle = linGrad(ctx, 0, 0, 0, H, [[0, '#5a2a2a'], [0.6, '#ffffff'], [1, '#7a3a2a']]); ctx.fillRect(0, 0, W, H); ctx.restore();
  motes(ctx, t, 90, 71, { y0: 1300, y1: 1900, vy: -180, vx: 10, size: [1, 3.4], col: '#ffb060', a: 0.85, life: 3 });
}

// ================================================================== V2 SHOT 14 — the brain inside HIS head (profile lens)
function v14(ctx, t) {
  const lt = t - EV.slam4;
  const hb = HEARTBEATS.reduce((a, x) => (t >= x ? Math.max(a, Math.exp(-(t - x) * 6)) : a), 0);
  insideBull(ctx, t, { x: 80 }, { heat: 0.8, slits: 1 });
  ctx.save(); ctx.globalAlpha = 0.5; ctx.fillStyle = '#05030a'; ctx.fillRect(0, 0, W, H); ctx.restore();
  const push = ease.io2(inv(0, 3.0, lt)), out = ease.in3(inv(EV.wail5 - 0.3, EV.wail5 + 0.15, t));
  const sc = lerp(2.15, 2.4, push) * (1 + hb * 0.01), hx = 600, hy = lerp(1080, 1000, push) + out * 900;
  const st = { blink: lerp(0.3, 0.6, push), brow: 0.6, mouth: 0.4, sweat: 1, t, breath: Math.sin(t * 3) * 0.8, slump: 0.1 };
  litRender(ctx, (g2, C) => { g2.save(); g2.translate(hx, hy); g2.scale(sc, sc); nikiasProfile(g2, C, st); g2.restore(); },
    (m) => radialMask(m, 300, 700, 40, 900, 0.75), Object.assign({ rim: { dx: -8, dy: 0, col: '#ff9a4a', a: 0.9 } }, warmPal(0.8)));
  // lens: skull opens into the brain (clipped to the head)
  const lens = ease.out3(inv(0.25, 0.9, lt));
  const bx = hx + 40 * sc, by = hy - 110 * sc, R = 190 * sc * lens;
  ctx.save(); ctx.beginPath(); ctx.ellipse(bx, by, R * 1.05, R * 0.85, -0.1, 0, 6.283); ctx.clip();
  ctx.fillStyle = 'rgba(10,18,30,0.95)'; ctx.fillRect(0, 0, W, H);
  ctx.translate(bx, by + 10 * sc); ctx.scale(1.0 * sc / 2.2, 1.0 * sc / 2.2);
  brainLat(ctx, { t, misfire: 0.3 + 0.6 * inv(0.5, 3.0, lt), hot: 0.35 * inv(0, 3, lt), glow: '#9fdcff' });
  ctx.restore();
  ctx.save(); ctx.strokeStyle = rgba('#bfe8ff', 0.85 * lens); ctx.lineWidth = 5; ctx.beginPath(); ctx.ellipse(bx, by, R * 1.05, R * 0.85, -0.1, 0, 6.283); ctx.stroke();
  ctx.globalCompositeOperation = 'screen'; ctx.filter = 'blur(10px)'; ctx.lineWidth = 24; ctx.stroke(); ctx.restore();
  // heartbeat: the world contracts
  ctx.save(); ctx.fillStyle = radGrad(ctx, W / 2, H / 2, 300 - hb * 120, 1100, [[0, 'rgba(0,0,0,0)'], [1, rgba('#200404', 0.55 + hb * 0.35)]]); ctx.fillRect(0, 0, W, H); ctx.restore();
}

// ================================================================== V2 SHOT 15 — organs inside HIS torso (close, layered)
function v15(ctx, t) {
  const lt = t - EV.wail5, hot = inv(0.3, 3.6, lt);
  const hb = HEARTBEATS.reduce((a, x) => (t >= x ? Math.max(a, Math.exp(-(t - x) * 7)) : a), 0);
  insideBull(ctx, t, { x: -60 }, { heat: 0.9, slits: 1 });
  ctx.save(); ctx.globalAlpha = 0.55; ctx.fillStyle = '#05030a'; ctx.fillRect(0, 0, W, H); ctx.restore();
  const pose = secondary(blendPose('kneel', 'kneel', 0), t, { breath: 2.2, tremble: 0.4, rate: 4 });
  pose.spine = -0.25; pose.head = 0.3;
  const ent = ease.out3(inv(0, 0.7, lt));
  const X = [lerp(560, 620, ent), lerp(-300, 220, ent) + lt * 10, lerp(1.6, 1.55, ent) + lt * 0.02];
  const { S, J } = silhouette('v15s', pose, t, X);
  clipTo(ctx, S, (g) => { g.fillStyle = mix('#14233a', '#3a1a12', hot * 0.6); g.fillRect(0, 0, W, H); });
  silRim(ctx, S, mix('#7fd6ff', '#ffb07a', hot), 0.9, 4, 1);
  // organs placed along the posed torso (3/4 view, facing left)
  const at = (u, dx) => { const b = [lerp(J.root[0], J.chest[0], u), lerp(J.root[1], J.chest[1], u)]; return XP(X, J.rot(b, dx, 0)); };
  const sp = -pose.spine;
  const kid = at(0.42, 120), liv = at(0.55, -40), hrt = at(0.78, 40);
  ctx.save(); ctx.globalAlpha = 0.85; ctx.translate(kid[0], kid[1]); ctx.rotate(sp); ctx.scale(X[2] * 0.9, X[2] * 0.9); kidney(ctx, -40, 0, -1, { hot }); kidney(ctx, 50, -10, 1, { hot }); ctx.restore();
  ctx.save(); ctx.translate(liv[0], liv[1]); ctx.rotate(sp); ctx.scale(X[2] * 0.85, X[2] * 0.85); ctx.translate(0, 270); liver(ctx, { hot }); ctx.restore();
  ctx.save(); ctx.translate(hrt[0], hrt[1]); ctx.rotate(sp); ctx.scale(X[2] * 0.32, X[2] * 0.32); heartAnt(ctx, { beat: hb, stress: hot, t }); ctx.restore();
  for (const [x, y] of [hrt, liv, kid]) { ctx.save(); ctx.strokeStyle = rgba('#ff5a3a', 0.55 * hb * hot + 0.12); ctx.lineWidth = 3; ctx.beginPath(); ctx.arc(x, y, 70 + (1 - hb) * 60, 0, 6.283); ctx.stroke(); ctx.restore(); }
  const la = env(lt, 0.5, 3.4, 0.3, 0.3);
  label(ctx, hrt[0], hrt[1], hrt[0] + 170, hrt[1] - 140, 'HEART', '#ffc0a8', la);
  label(ctx, liv[0] - 60, liv[1] + 60, liv[0] - 200, liv[1] + 220, 'LIVER', '#ffc0a8', la);
  label(ctx, kid[0] + 40, kid[1], kid[0] + 180, kid[1] - 130, 'KIDNEYS', '#ffc0a8', la);
  ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.globalAlpha = 0.3 * inv(EV.roarRev, EV.sil2, t); ctx.fillStyle = '#ff4a1a'; ctx.fillRect(0, 0, W, H); ctx.restore();
}

// ================================================================== V2 SHOT 17 — consciousness: he slides down the wall
function v17(ctx, t) {
  const lt = t - EV.wail6, k = inv(0, 3.6, lt);
  const stutter = (t > EV.stutter && t < EV.stutter + 0.36) ? Math.floor((t - EV.stutter) / 0.11) % 2 : 0;
  const keys = [[EV.wail6, 'kneel'], [52.1, 'sink', ease.io2], [53.4, 'slump', ease.io3], [54.7, 'slump']];
  const pose = secondary(poseAt(t, keys), t, { breath: lerp(1.6, 0.3, k), tremble: lerp(0.4, 0, k), rate: lerp(3.6, 1.6, k) });
  pose.face = { blink: clamp(ease.io3(inv(1.0, 3.2, lt))), brow: lerp(0.5, 0.05, k), mouth: lerp(0.45, 0.15, k), sweat: 1, look: [0, 0.3] };
  const L = cvs('v17'), g = L.getContext('2d');
  insideBull(g, t, { x: 0 }, { heat: lerp(0.8, 0.5, k), slits: 1 });
  // the curved wall he slides down
  g.save(); g.fillStyle = linGrad(g, 700, 0, W, 0, [[0, '#2a1608'], [0.4, '#4a2a12'], [1, '#140a05']]); g.beginPath(); g.moveTo(820, 0); g.quadraticCurveTo(700, 1000, 860, H); g.lineTo(W, H); g.lineTo(W, 0); g.closePath(); g.fill(); g.restore();
  drawNikias(g, pose, t, [520, 640, 0.74], { heat: lerp(0.8, 0.4, k), key: lerp(0.9, 0.5, k) });
  ctx.save(); ctx.filter = `blur(${lerp(0, 8, ease.in2(k))}px) saturate(${lerp(1, 0.35, k)})`; ctx.drawImage(L, stutter * 24, 0); ctx.restore();
  if (stutter) { ctx.save(); ctx.globalAlpha = 0.4; ctx.globalCompositeOperation = 'screen'; ctx.drawImage(L, -30, 6); ctx.restore(); }
  ctx.save(); ctx.fillStyle = radGrad(ctx, 560, 1000, lerp(650, 160, k), lerp(1300, 650, k), [[0, 'rgba(0,0,0,0)'], [1, 'rgba(0,0,0,0.96)']]); ctx.fillRect(0, 0, W, H); ctx.restore();
}

// ================================================================== V2 SHOT 18 — symbolic: his silhouette dissolves into rising embers
function v18(ctx, t) {
  const lt = t - EV.scan4, k = inv(0, 1.76, lt);
  ctx.fillStyle = '#050304'; ctx.fillRect(0, 0, W, H);
  // the slit of light above, the only way out
  shaft(ctx, 540, 0, 20, 540, 900, 380, '#ffc070', 0.25 + 0.25 * k);
  ctx.save(); ctx.fillStyle = rgba('#ffe0a0', 0.9); ctx.fillRect(536, 0, 8, 120); ctx.restore();
  const pose = secondary(blendPose('slump', 'slump', 0), t, { breath: 0 });
  const X = [520, 640, 0.74];
  const { S } = silhouette('v18s', pose, t, X);
  // silhouette fading out from the top, outline glowing
  const D = cvs('v18d'), dg = D.getContext('2d'); dg.drawImage(S, 0, 0); dg.globalCompositeOperation = 'source-in'; dg.fillStyle = '#0c0504'; dg.fillRect(0, 0, W, H);
  dg.globalCompositeOperation = 'destination-out'; dg.fillStyle = linGrad(dg, 0, lerp(H, 300, k) - 300, 0, lerp(H, 300, k), [[0, 'rgba(0,0,0,1)'], [1, 'rgba(0,0,0,0)']]); dg.fillRect(0, 0, W, lerp(H, 300, k));
  ctx.drawImage(D, 0, 0); ctx.save(); ctx.globalAlpha = 1 - k * 0.7; silRim(ctx, S, '#ffb060', 0.9, 4, 1); ctx.restore();
  // embers lifting off him toward the light
  const r = mulberry(5);
  for (let i = 0; i < 160; i++) {
    const x0 = lerp(280, 820, r()), y0 = lerp(900, 1700, r()), ph = r() * 0.8, u = clamp((lt * 0.75 - ph * 0.5) / 1.0);
    if (u <= 0) continue;
    const x = lerp(x0, 540 + (x0 - 540) * 0.25, ease.io2(u)) + Math.sin(t * 3 + i) * 14, y = lerp(y0, 80, ease.in2(u));
    const a = Math.sin(Math.PI * clamp(u * 1.1)) * 0.9, s = 1.5 + r() * 3;
    ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.globalAlpha = a; ctx.fillStyle = '#ffc070'; ctx.beginPath(); ctx.arc(x, y, s, 0, 6.283); ctx.fill(); ctx.globalAlpha = a * 0.3; ctx.beginPath(); ctx.arc(x, y, s * 4, 0, 6.283); ctx.fill(); ctx.restore();
  }
}

// ================================================================== V2 SHOT 19 — spectacular bull: embers escape into the night, the roar
function v19(ctx, t) {
  const lt = t - EV.bar32;
  const roar = inv(EV.roarClimax - 0.05, EV.roarClimax + 0.1, t);
  const mv = ease.io2(inv(0, 1.77, lt));
  const L = cvs('v19'), g = L.getContext('2d');
  // dramatic sky: moon behind smoke
  courtyard(g, { x: lerp(120, -60, mv), y: 0, s: 1.5, hz: 1600, bullX: -9999, bullY: 1700, bullS: 1.15 }, t, { fire: 1 });
  glow(g, 830, 640, 260, '#f0e0c0', 0.35); g.fillStyle = '#efe3c8'; g.beginPath(); g.arc(830, 640, 64, 0, 6.283); g.fill();
  g.save(); g.globalAlpha = 0.55; g.filter = 'blur(30px)'; g.fillStyle = '#2a1a1a'; g.beginPath(); g.ellipse(760 + lt * 40, 680, 380, 60, -0.2, 0, 6.283); g.fill(); g.restore();
  const bx = lerp(800, 770, mv), by = 1720, sc = lerp(1.12, 1.2, mv);
  g.save(); g.translate(bx, by); g.scale(sc, sc); plinth(g); g.restore();
  glow(g, bx, by, 760 * sc, '#ff6a1a', 0.45 + roar * 0.3);
  bullLayer(g, bx, by, sc, { glow: 1 + roar * 0.6, t, eyeGlow: 0.35 + roar * 1.2 });
  ctx.drawImage(L, 0, 0);
  // smoke + embers streaming up out of the bull into the sky (the souls of the story, symbolically)
  const r = mulberry(19);
  for (let i = 0; i < 140; i++) { const ph = r(), sp = 0.4 + r() * 0.6, u = ((lt * sp + ph) % 1); const x0 = bx + lerp(-300, 200, r()) * sc, y0 = by - 600 * sc;
    const x = x0 + Math.sin(u * 5 + i) * 60 + u * 160, y = y0 - u * 1300, a = Math.sin(Math.PI * u) * (0.6 + roar * 0.4);
    ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.globalAlpha = a; ctx.fillStyle = '#ffb060'; ctx.beginPath(); ctx.arc(x, y, 1.6 + r() * 2.6, 0, 6.283); ctx.fill(); ctx.restore(); }
  if (roar > 0) { const hx = bx - 470 * sc, hy = by - 372 * sc, u = inv(EV.roarClimax, EV.roarClimax + 0.45, t);
    glow(ctx, hx, hy, 600 * roar, '#ff7a2a', 0.55 * roar);
    for (let k2 = 0; k2 < 2; k2++) { const uu = clamp(u - k2 * 0.15); ctx.save(); ctx.strokeStyle = rgba('#ffc890', 0.7 * (1 - uu)); ctx.lineWidth = 8 * (1 - uu) + 1; ctx.beginPath(); ctx.arc(hx, hy, 60 + uu * 800, 0, 6.283); ctx.stroke(); ctx.restore(); } }
  ctx.save(); ctx.filter = 'blur(16px)'; column(ctx, lerp(40, -40, mv), 2300, 260, 2800, 0.3); ctx.restore();
}

// ================================================================== V2 SHOT 16 — fusion, reframed lower and closer
function v16(ctx, t) {
  ctx.save(); ctx.translate(W / 2, H / 2); const lt = t - EV.drop2; const s = lerp(1.18, 1.06, ease.out3(inv(0, 1.2, lt))); ctx.scale(s, s); ctx.rotate(lerp(0.04, -0.02, inv(0, 3.3, lt)));
  ctx.translate(-W / 2, -H / 2 + 60); s16(ctx, t); ctx.restore();
}
