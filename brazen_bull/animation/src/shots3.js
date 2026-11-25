// V3 SHOTS: correct human scale (semi-reclined along the bull's torso), one-bar editorial cadence,
// character-first storytelling with anatomy entering through his body.
'use strict';

// ------------------------------------------------------------------ lying poses (figure space; mapped with the lying transform)
// Lying transform: screen = origin + (y, x) * sc   -> head to screen-left, his front faces UP (toward the bull's back)
Object.assign(POSES, {
  lie: { spine: 0.04, head: 0.12, nT: { c: [-140, 560] }, nB: -1, fT: { c: [-280, 430] }, fB: -1, nF: [-380, 900], fF: [-250, 980], nKB: 1, fKB: 1, nFa: -1.2, fFa: -1.2, nHand: 'relax', fHand: 'relax' },
  liePress: { spine: 0.0, head: -0.12, nT: [-640, -520], nB: 1, fT: [-700, -300], fB: 1, nF: [-400, 880], fF: [-260, 970], nKB: 1, fKB: 1, nFa: -1.2, fFa: -1.2, nHand: 'press', fHand: 'press', nWa: 0.5, fWa: 0.4 },
  lieCurl: { spine: -0.32, head: 0.42, nT: { c: [-380, 300] }, nB: 1, fT: { h: [-170, 40] }, fB: 1, nF: [-540, 520], fF: [-430, 640], nKB: 1, fKB: 1, nFa: -0.6, fFa: -0.5, nHand: 'fist', fHand: 'claw' },
  lieLimp: { spine: 0.08, head: -0.28, nT: { c: [60, 600] }, nB: -1, fT: { c: [-60, 640] }, fB: -1, nF: [-200, 1000], fF: [-60, 1040], nKB: 1, fKB: 1, nFa: -1.3, fFa: -1.3, nHand: 'relax', fHand: 'relax' },
  lieWipe: { spine: 0.02, head: 0.05, nT: { h: [-90, -150] }, nB: 1, fT: { c: [-280, 430] }, fB: -1, nF: [-380, 900], fF: [-250, 980], nKB: 1, fKB: 1, nFa: -1.2, fFa: -1.2, nHand: 'flat', fHand: 'relax', frontArm: true, nWa: 1.4 },
});
const FLOOR_X = 250, CEIL_X = -900;           // interior surfaces in figure space (his back rests on the floor)
function LIE(ox, oy, sc) { const L = [ox, oy, sc]; L.map = (p) => [ox + p[1] * sc, oy + p[0] * sc]; L.rot = Math.PI / 2; L.lying = true; return L; }
// XP override: support the lying mapping for overlays (bones / nerves)
XP = (X, p) => X.map ? X.map(p) : [X[0] + p[0] * X[2], X[1] + p[1] * X[2]];
function lieDraw(g, L, fn) { g.save(); g.translate(L[0], L[1]); g.scale(L[2], L[2]); g.transform(0, 1, 1, 0, 0, 0); fn(g); g.restore(); }
function drawLying(ctx, pose, t, L, opt = {}) {
  const pal = warmPal(opt.heat ?? 0.6);
  litRender(ctx, (g, C) => lieDraw(g, L, (gg) => figure(gg, C, pose, t, { lag: opt.lag || 0 })),
    (m) => { opt.mask ? opt.mask(m) : radialMask(m, L[0] - 200 * L[2], L[1] - 600 * L[2], 30, 1400 * L[2], opt.key ?? 0.9); },
    Object.assign({ rim: { dx: 0, dy: -5 * Math.max(0.5, L[2] / 0.6), col: opt.rimCol || '#ffa050', a: opt.rimA ?? 0.85 } }, pal));
}
function silL(name, pose, t, L) {
  const S = cvs(name), g = S.getContext('2d');
  let J; lieDraw(g, L, (gg) => { J = figure(gg, SKIN_SHD, pose, t); });
  g.globalCompositeOperation = 'source-in'; g.fillStyle = '#fff'; g.fillRect(0, 0, W, H); g.globalCompositeOperation = 'source-over';
  return { S, J };
}
const lieP = (name, t, o = {}) => { const p = secondary(typeof name === 'string' ? blendPose(name, name, 0) : name, t, Object.assign({ breath: 1.4, rate: 3.4, tremble: 0.3 }, o)); return p; };

// ------------------------------------------------------------------ tight interior: bronze shell pressing above and below him
function shellTight(ctx, t, L, opt = {}) {
  const heat = opt.heat ?? 0.6, ceilY = L[1] + CEIL_X * L[2], floorY = L[1] + FLOOR_X * L[2] + 20 * L[2];
  ctx.fillStyle = '#0a0503'; ctx.fillRect(0, 0, W, H);
  // ceiling (inner side of the bull's back), curving down at both ends
  ctx.save(); ctx.beginPath(); ctx.moveTo(-50, -50); ctx.lineTo(W + 50, -50); ctx.lineTo(W + 50, ceilY + 160); ctx.quadraticCurveTo(W / 2, ceilY - 60, -50, ceilY + 160); ctx.closePath();
  ctx.fillStyle = linGrad(ctx, 0, ceilY - 400, 0, ceilY + 120, [[0, '#120804'], [1, mix('#5a3214', '#a8582a', heat)]]); ctx.fill(); ctx.clip();
  const r = mulberry(3); for (let i = 0; i < 120; i++) { ctx.fillStyle = rgba('#d8964a', 0.03 + r() * 0.06); ctx.beginPath(); ctx.ellipse(r() * W, ceilY - r() * 500 + 100, 20 + r() * 40, 12 + r() * 20, 0, 0, 6.283); ctx.fill(); }
  ctx.restore();
  ctx.save(); ctx.strokeStyle = rgba('#ffc078', 0.55); ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(-50, ceilY + 160); ctx.quadraticCurveTo(W / 2, ceilY - 60, W + 50, ceilY + 160); ctx.stroke(); ctx.restore();
  // the light seam in the shell, and its moving reflection
  if (opt.seam !== false) { const sx = opt.seamX ?? 620; ctx.save(); ctx.fillStyle = rgba('#ffe2a8', 0.95); ctx.fillRect(sx - 3, ceilY - 300, 6, 300); ctx.restore();
    shaft(ctx, sx, ceilY, 16, sx - 120, floorY, 220, '#ffc070', 0.22); }
  // floor (inner belly), hot from below
  ctx.save(); ctx.beginPath(); ctx.moveTo(-50, H + 50); ctx.lineTo(-50, floorY - 120); ctx.quadraticCurveTo(W / 2, floorY + 60, W + 50, floorY - 120); ctx.lineTo(W + 50, H + 50); ctx.closePath();
  ctx.fillStyle = linGrad(ctx, 0, floorY - 60, 0, floorY + 500, [[0, mix('#7a3a16', '#e0702a', heat)], [1, '#2a1006']]); ctx.fill(); ctx.restore();
  glow(ctx, W / 2, floorY + 120, 800, '#ff6a1a', 0.25 + 0.4 * heat);
  motes(ctx, t, 30, 61, { y0: ceilY, y1: floorY, vy: -30, vx: 14, size: [0.8, 2.2], col: '#ffe2b0', a: 0.5, life: 5 });
}

// ------------------------------------------------------------------ exterior: torso-shaped cutaway with him lying inside at true scale
const TORSO_WIN = [[-300, -470], [-230, -525], [-120, -560], [0, -546], [130, -526], [250, -518], [322, -480], [340, -400], [322, -320], [262, -282], [120, -266], [-20, -256], [-160, -245], [-262, -262], [-318, -330], [-326, -410]];
function bullCutaway3(ctx, bx, by, sc, t, opt = {}) {
  const open = opt.open ?? 1, heat = opt.heat ?? 0.6;
  bullLayer(ctx, bx, by, sc, { glow: opt.fire ?? 1, t, eyeGlow: opt.eyeGlow || 0 });
  if (open <= 0) return;
  const c = [bx + 10 * sc, by - 400 * sc];
  const win = TORSO_WIN.map(([x, y]) => [c[0] + (bx + x * sc - c[0]) * open, c[1] + (by + y * sc - c[1]) * open]);
  ctx.save(); ctx.beginPath(); crPath(ctx, win, true); ctx.clip();
  ctx.fillStyle = linGrad(ctx, 0, by - 560 * sc, 0, by - 250 * sc, [[0, '#1a0a05'], [0.6, mix('#4a1e0a', '#8a3410', heat)], [1, mix('#a04a18', '#ff7a2a', heat)]]); ctx.fillRect(bx - 400 * sc, by - 600 * sc, 800 * sc, 400 * sc);
  const L = LIE(bx - 20 * sc, by - 335 * sc, 0.285 * sc);
  if (opt.silhouette) {
    const { S } = silL('cut3', opt.pose || lieP('lie', t), t, L);
    const D = cvs('cut3d'), dg = D.getContext('2d'); dg.drawImage(S, 0, 0); dg.globalCompositeOperation = 'source-in'; dg.fillStyle = opt.silCol || '#130705'; dg.fillRect(0, 0, W, H);
    ctx.drawImage(D, 0, 0); silRim(ctx, S, '#ffb060', 0.95, 0, -2);
  } else drawLying(ctx, opt.pose || lieP('lie', t), t, L, { heat, mask: (m) => { m.fillStyle = linGrad(m, 0, by - 560 * sc, 0, by - 250 * sc, [[0, 'rgba(255,255,255,0.25)'], [1, 'rgba(255,255,255,0.95)']]); m.fillRect(0, 0, W, H); } });
  glow(ctx, bx, by - 250 * sc, 380 * sc, '#ff6a1a', 0.35 * heat);
  ctx.restore();
  ctx.save(); ctx.lineJoin = 'round';
  ctx.strokeStyle = '#140904'; ctx.lineWidth = 16 * sc; ctx.beginPath(); crPath(ctx, win, true); ctx.stroke();
  ctx.strokeStyle = rgba('#ffc070', 0.9); ctx.lineWidth = 3.5 * sc; ctx.beginPath(); crPath(ctx, win, true); ctx.stroke();
  ctx.globalCompositeOperation = 'screen'; ctx.filter = 'blur(10px)'; ctx.strokeStyle = rgba('#ff7a2a', 0.5 * heat + 0.2); ctx.lineWidth = 22 * sc; ctx.beginPath(); crPath(ctx, win, true); ctx.stroke();
  ctx.restore();
}
function exteriorBase(ctx, t, cam) {
  courtyard(ctx, { x: cam.x || 0, y: 0, s: cam.s || 1.2, hz: cam.hz || 1400, bullX: -9999, bullY: cam.by, bullS: cam.sc }, t, { fire: 1 });
  ctx.save(); ctx.translate(cam.bx, cam.by); ctx.scale(cam.sc, cam.sc); plinth(ctx); ctx.restore();
  glow(ctx, cam.bx, cam.by, 600 * cam.sc, '#ff6a1a', 0.35 * (cam.fire ?? 1));
}

// ------------------------------------------------------------------ close-up helpers
// his head as he lies: the camera rolls with him (slight tilt), drawn huge with moving bronze reflections
const FACE_ROLL = -0.22;
function headAt(px, py, sc, roll = 0) { const a = FACE_ROLL + roll, c = Math.cos(a), s2 = Math.sin(a); return [px * c * sc - py * s2 * sc, px * s2 * sc + py * c * sc]; }
function faceLying(ctx, t, cx, cy, sc, st, opt = {}) {
  const pal = warmPal(opt.heat ?? 0.6);
  const draw = (g, C) => { g.save(); g.translate(cx, cy); g.rotate(FACE_ROLL + (opt.roll || 0)); g.scale(sc, sc); head34(g, C, Object.assign({ t }, st)); g.restore(); };
  const mask = (m) => {
    // reflections of the bronze shell sliding across the skin
    for (let i = 0; i < 3; i++) { const p = ((t * (0.18 + i * 0.07) + i * 0.33) % 1.4) - 0.2; const x = lerp(-200, W + 200, p);
      m.fillStyle = linGrad(m, x - 160, 0, x + 160, 0, [[0, 'rgba(255,255,255,0)'], [0.5, rgba('#ffffff', 0.85 - i * 0.2)], [1, 'rgba(255,255,255,0)']]); m.fillRect(0, 0, W, H); }
    radialMask(m, cx - 300, cy - 300, 30, 900, opt.key ?? 0.35);
  };
  const DEEP = Object.assign({}, SKIN_SHD, { skin: '#24130c', skin2: '#1a0e08', hair: '#070504', beard: '#080504', eyeW: '#3a2a20' });
  litRender(ctx, draw, mask, Object.assign({ rim: { dx: 0, dy: -6, col: '#ffa050', a: 0.8 }, shadow: DEEP }, pal));
}
// a close crop of his posed body (e.g. chest, forearm) using the lying transform
function bodyClose(ctx, t, pose, L, opt) { drawLying(ctx, pose, t, L, opt); }

// ================================================================== V3 SHOTS (one-bar cadence)
const B = (n) => n * BAR;

// 0.00 - 2.65 : eye in darkness, bronze reflections, title words on the narration; pull back to his whole body
function w01(ctx, t) {
  const pull = ease.io3(inv(1.25, 2.65, t));
  const sc = lerp(5.2, 1.25, pull);
  // the eye: near eye of head34 at (22,-20); lying rotation -> place the eye at screen center
  const ex = 540, ey = 860;
  const [rx, ry] = headAt(22, -20, sc);
  if (pull < 0.55) {
    ctx.fillStyle = '#070403'; ctx.fillRect(0, 0, W, H);
    const open = inv(0.05, 0.22, t);
    faceLying(ctx, t, ex - rx, ey - ry, sc, { blink: Math.max(1 - open, blinkAt(t, 1, [1.9])), look: [lerp(0.2, -0.4, inv(1.2, 1.5, t)), -0.1], brow: 0.5, sweat: 0.6, mouth: 0.15 }, { heat: 0.4 });
    if (pull > 0.25) { ctx.save(); ctx.globalAlpha = inv(0.25, 0.55, pull); ctx.fillStyle = '#070403'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
  }
  if (pull > 0.3) {
    // full body revealed, tightly enclosed: the shell presses above and below
    const k = inv(0.3, 1, pull);
    const L = LIE(lerp(980, 640, ease.out3(k)), lerp(1250, 1080, ease.out3(k)), lerp(0.9, 0.46, ease.out3(k)));
    ctx.save(); ctx.globalAlpha = clamp(k * 2);
    shellTight(ctx, t, L, { heat: 0.5, seamX: 560 });
    drawLying(ctx, lieP(poseAt(t, [[1.3, 'lie'], [2.2, 'liePress']]), t, { tremble: 0.5 }), t, L, { heat: 0.5 });
    ctx.restore();
  }
}
// 2.65 - 5.29 : match cut into the exterior side profile; cutaway reveals him filling the torso; title locks on the door slam
function w02(ctx, t) {
  const lt = t - EV.whoosh0, k = ease.out5(inv(0, 0.85, lt));
  const sc = lerp(2.6, 1.02, k), bx = lerp(780, 560, k), by = lerp(2350, 1600, k);
  const L = cvs('w02'), g = L.getContext('2d');
  exteriorBase(g, t, { x: lerp(40, -20, k) - lt * 10, s: 1.2, hz: 1380, bx, by, sc });
  bullCutaway3(g, bx, by, sc, t, { open: 1, heat: 0.65, pose: lieP(poseAt(t, [[2.65, 'liePress'], [4.2, 'lie']]), t, { tremble: 0.4 }), eyeGlow: 0.3 + 0.4 * kick(t, EV.slam1, 3) });
  motes(g, t, 50, 7, { x0: bx - 400 * sc, x1: bx + 400 * sc, y0: by - 40, y1: by + 80, vy: -120, vx: 10, size: [1, 3], col: '#ffb060', a: 0.85, life: 3.5 });
  ctx.drawImage(L, 0, 0);
}
// 5.29 - 7.06 : low-angle exterior hero (no cutaway): the sculpture as the world sees it
function w03(ctx, t) { s02(ctx, t); }
// 7.06 - 8.82 : his face, lying, sweat beading, eyes searching (EXTREME HEAT)
function w04(ctx, t) {
  const lt = t - 7.06;
  const L = cvs('w04'), g = L.getContext('2d');
  g.fillStyle = '#0a0503'; g.fillRect(0, 0, W, H);
  glow(g, 540, 1500, 900, '#ff6a1a', 0.45);
  faceLying(g, t, lerp(600, 580, lt / 1.8), 980, lerp(2.1, 2.3, lt / 1.8), { blink: blinkAt(t), look: [Math.sin(lt * 2.2) * 0.4, -0.2], brow: 0.6 + 0.2 * Math.sin(lt * 3), sweat: 0.9, mouth: 0.3 + 0.25 * Math.sin(t * 4), t }, { heat: 0.7, key: 0.55, roll: Math.sin(lt * 1.3) * 0.04 });
  ctx.drawImage(L, 0, 0); heatShimmer(ctx, L, t, 4, 1300, H);
  shaft(ctx, 640, 0, 10, 520, 1100, 160, '#ffc070', 0.25);
}
// 8.82 - 10.59 : palms against the bronze above; recoil from the heat
function w05(ctx, t) {
  const lt = t - B(5);
  const L = LIE(lerp(940, 900, lt / 1.8), lerp(1900, 1860, lt / 1.8), 1.05);
  const pose = lieP(poseAt(t, [[B(5), 'liePress'], [9.75, 'liePress'], [9.95, 'lie', ease.out3], [10.59, 'lie']]), t, { tremble: 0.8, breath: 1.8, rate: 4 });
  pose.face = { brow: 0.8, mouth: 0.5, sweat: 1, look: [0.3, -0.6] };
  shellTight(ctx, t, L, { heat: 0.75, seamX: 300 });
  drawLying(ctx, pose, t, L, { heat: 0.75 });
  const touch = env(t, B(5), 9.8, 0.1, 0.1);
  glow(ctx, 360, L[1] + CEIL_X * L[2] + 40, 220, '#ffb060', 0.5 * touch + 0.8 * kick(t, 9.75, 6));
}
// 10.59 - 12.35 : scan: his forearm skin -> layers beneath (lens), skin block
function w06(ctx, t) { v04(ctx, t); }
// 12.35 - 14.12 : back to him: macro of sweat streaming on his temple
function w07(ctx, t) {
  const lt = t - B(7);
  ctx.fillStyle = '#0a0503'; ctx.fillRect(0, 0, W, H); glow(ctx, 540, 1600, 900, '#ff6a1a', 0.4);
  faceLying(ctx, t, 640, 900, 3.2, { blink: blinkAt(t, 1, [13.2]), look: [-0.4, -0.3], brow: 0.7, sweat: 1, mouth: 0.4, t }, { heat: 0.8, key: 0.45, roll: 0.1 });
  // large sweat droplets sliding (macro)
  const r = mulberry(12); for (let i = 0; i < 9; i++) { const x = lerp(120, 960, r()), y = ((lt * (60 + r() * 80)) + r() * 900) % 1400 + 200, s = 10 + r() * 16;
    ctx.save(); ctx.fillStyle = 'rgba(255,240,220,0.18)'; ctx.beginPath(); ctx.ellipse(x, y, s, s * 1.4, 0, 0, 6.283); ctx.fill();
    ctx.fillStyle = 'rgba(255,250,240,0.75)'; ctx.beginPath(); ctx.ellipse(x - s * 0.3, y - s * 0.4, s * 0.25, s * 0.4, -0.3, 0, 6.283); ctx.fill(); ctx.restore(); }
}
// 14.12 - 15.88 : vessels widen (macro)
function w08(ctx, t) { v05(ctx, t); }
// 15.88 - 17.21 : back on his arm: flushed skin with the widened vessels showing beneath
function w09(ctx, t) {
  const lt = t - B(9), k = inv(0, 0.9, lt);
  const L = LIE(lerp(1150, 1100, lt / 1.4), 2150, 1.3);
  const pose = secondary(blendPose('liePress', 'liePress', 0), t, { breath: 2, tremble: 0.6, rate: 4.4 });
  shellTight(ctx, t, L, { heat: 0.85, seamX: 220 });
  drawLying(ctx, pose, t, L, { heat: 0.9 });
  const { S, J } = silL('w09s', pose, t, L);
  clipTo(ctx, S, (g) => {
    g.fillStyle = rgba('#ff3a2a', 0.22 * k); g.fillRect(0, 0, W, H);
    for (const [A, Bq, Cq] of [[J.nSh, J.nElb, J.nWr], [J.fSh, J.fElb, J.fWr]]) {
      for (let i = -2; i <= 2; i++) { const pts = curvePts([A, Bq, Cq].map(p => XP(L, p)), 30).map(([x, y], j) => [x + i * 18 + Math.sin(j * 0.6 + i) * 6, y + i * 10]);
        g.strokeStyle = rgba(i % 2 ? '#4a7ad0' : '#e0343c', 0.65 * k); g.lineWidth = 7 + (2 - Math.abs(i)) * 3; g.beginPath(); crPath(g, pts, false); g.stroke();
        const u = ((lt * 0.9 + (i + 2) * 0.2) % 1), P = pts[Math.floor(u * (pts.length - 1))]; glow(g, P[0], P[1], 36, '#ffb0a0', 0.7 * k); }
    }
  });
  label(ctx, 520, 760, 360, 600, 'VESSELS WIDEN', '#ffc0a8', env(lt, 0.3, 1.3, 0.2, 0.2));
}
// 17.21 - 19.0 : push to his chest, ribs turn transparent, the heart appears in place
function w10(ctx, t) {
  const lt = t - EV.slam2, k = ease.io3(inv(0.1, 1.2, lt));
  const L = LIE(lerp(980, 1160, k), lerp(1500, 1300, k), lerp(0.75, 1.5, k));
  const pose = lieP('lie', t, { breath: 2.2, rate: 4.4 });
  shellTight(ctx, t, L, { heat: 0.7, seam: false });
  drawLying(ctx, pose, t, L, { heat: 0.7 });
  const { S, J } = silL('w10s', pose, t, L);
  const x = inv(0.35, 1.0, lt);
  if (x > 0) {
    clipTo(ctx, S, (g) => { g.globalAlpha = 0.7 * x; g.fillStyle = '#0c1626'; g.fillRect(0, 0, W, H); g.globalAlpha = 1; });
    xrayBones(ctx, J, L, 0.3 * x, '#cfe8ff');
    const c = XP(L, [lerp(J.chest[0], J.root[0], 0.25), lerp(J.chest[1], J.root[1], 0.25)]);
    const hb = kickPulse(t, 7);
    ctx.save(); ctx.globalAlpha = inv(0.6, 1.1, lt); ctx.translate(c[0], c[1]); ctx.scale(0.62 * L[2], 0.62 * L[2]); glow(ctx, 0, 0, 420, '#ff4a3a', 0.35 * hb + 0.15); heartAnt(ctx, { beat: hb, t }); ctx.restore();
  }
}
// 19.0 - 20.96 : heart macro; its pulse ring becomes the transition
function w11(ctx, t) { v06(ctx, t); }
// 20.96 - 22.94 : water & salts leaving his body (lying silhouette in the torso cutaway, close)
function w12(ctx, t) {
  const lt = t - EV.shriek1, drain = ease.io2(inv(0.15, 1.9, lt));
  const L = LIE(560, 1120, 0.52);
  shellTight(ctx, t, L, { heat: 0.85, seamX: 820 });
  ctx.save(); ctx.globalAlpha = 0.55; ctx.fillStyle = '#04070c'; ctx.fillRect(0, 0, W, H); ctx.restore();
  const pose = lieP('lieWipe', t, { breath: 2, rate: 4 });
  const { S, J } = silL('w12s', pose, t, L);
  const lvl = lerp(L[1] + CEIL_X * 0.45 * L[2], L[1] + FLOOR_X * L[2], drain);
  clipTo(ctx, S, (g) => { g.fillStyle = 'rgba(14,30,52,0.92)'; g.fillRect(0, 0, W, H);
    g.fillStyle = linGrad(g, 0, lvl, 0, H, [[0, rgba('#5ac8ff', 0.8)], [1, rgba('#1a6aa0', 0.65)]]); g.fillRect(0, lvl, W, H);
    g.strokeStyle = '#d8f4ff'; g.lineWidth = 5; g.beginPath(); for (let x = 0; x <= W; x += 12) g.lineTo(x, lvl + Math.sin(x * 0.03 + t * 6) * 6); g.stroke(); });
  silRim(ctx, S, '#7fd6ff', 0.9, 0, -3);
  const r = mulberry(55);
  for (let i = 0; i < 44; i++) { const u = ((lt * (0.6 + r() * 0.6) + r()) % 1.2); if (u > 1) continue; const x0 = lerp(80, 1000, r()), y = lerp(L[1] - 120, L[1] - 420, ease.out2(u)) - r() * 80;
    ctx.save(); ctx.globalAlpha = Math.sin(Math.PI * u);
    if (i % 3 === 0) { ctx.fillStyle = '#ffd27a'; ctx.font = '800 32px Inter'; ctx.textAlign = 'center'; ctx.fillText(['Na⁺', 'K⁺', 'Cl⁻'][i % 2 ? 1 : (i % 9 === 0 ? 0 : 2)], x0, y); }
    else { ctx.fillStyle = '#9fdcff'; ctx.beginPath(); ctx.ellipse(x0, y, 9, 12, 0, 0, 6.283); ctx.fill(); }
    ctx.restore(); }
  label(ctx, 760, L[1] - 300, 700, L[1] - 460, 'ELECTROLYTES', '#ffd27a', env(lt, 0.4, 1.9, 0.25, 0.2));
}
// 22.94 - 24.71 : character beat: he curls up, breath shortens (HEAT STRESS)
function w13(ctx, t) {
  const lt = t - EV.riser;
  const L = LIE(lerp(600, 640, lt / 1.8), 1150, lerp(0.62, 0.7, lt / 1.8));
  const pose = lieP(poseAt(t, [[EV.riser, 'lie'], [23.82, 'lieCurl', ease.io3], [24.71, 'lieCurl']]), t, { breath: 2.6, rate: 5, tremble: 0.7 });
  pose.face = { brow: 0.85, mouth: 0.5 + 0.2 * Math.sin(t * 6), sweat: 1, look: [0, 0.4], blink: Math.max(blinkAt(t), 0.35) };
  const Bg = cvs('w13'), g = Bg.getContext('2d'); shellTight(g, t, L, { heat: 0.9, seamX: 720 });
  ctx.save(); ctx.translate(W / 2, H / 2); ctx.rotate(lerp(0, -0.04, lt / 1.8)); ctx.translate(-W / 2, -H / 2);
  ctx.drawImage(Bg, 0, 0); heatShimmer(ctx, Bg, t, 5, L[1] + 100, H);
  drawLying(ctx, pose, t, L, { heat: 0.9 }); ctx.restore();
}
// 24.71 - 26.47 : pre-drop: his curled silhouette -> X-ray, burst on the power accent
function w14(ctx, t) {
  const lt = t - EV.predrop, heat = inv(0, 1.32, lt);
  ctx.fillStyle = '#070304'; ctx.fillRect(0, 0, W, H);
  glow(ctx, 540, 1000, lerp(600, 1200, heat), '#ff4a14', lerp(0.4, 0.95, heat));
  const pose = lieP('lieCurl', t, { breath: 2.6, rate: 5, tremble: 0.7 });
  const L = LIE(lerp(560, 600, heat), 1180, lerp(0.66, 0.74, ease.io2(heat)));
  const { S, J } = silL('w14s', pose, t, L);
  const D = cvs('w14d'), dg = D.getContext('2d'); dg.drawImage(S, 0, 0); dg.globalCompositeOperation = 'source-in'; dg.fillStyle = '#060203'; dg.fillRect(0, 0, W, H);
  ctx.drawImage(D, 0, 0); silRim(ctx, S, '#ffb060', 1, 0, -7);
  const burst = inv(EV.power1 - 0.05, EV.power1 + 0.08, t);
  const sx = lerp(-100, W + 100, ease.io3(inv(25.33, EV.power1, t)));
  if (t > 25.33) {
    ctx.save(); ctx.beginPath(); ctx.rect(0, 0, sx, H); ctx.clip();
    clipTo(ctx, S, (g) => { g.fillStyle = burst > 0 ? '#3a1a0a' : '#0a1626'; g.fillRect(0, 0, W, H); });
    xrayBones(ctx, J, L, 0.85, burst > 0 ? '#ffe0a8' : '#cfe8ff'); silRim(ctx, S, burst > 0 ? '#ffd08a' : '#7fd6ff', 1, 0, -3);
    ctx.restore();
    ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.fillStyle = linGrad(ctx, sx - 70, 0, sx + 4, 0, [[0, 'rgba(127,214,255,0)'], [1, 'rgba(200,240,255,0.95)']]); ctx.fillRect(sx - 70, 0, 74, H); ctx.restore();
  }
  motes(ctx, t, 80, 51, { vy: -260, vx: 30, size: [1, 3.5], col: '#ffb060', a: 0.8, life: 2 });
}
// 26.47 - 28.24 : DROP: his eye loses focus, the pupil swallows the frame -> neural light
function w15(ctx, t) {
  const lt = t - EV.drop1, pk = ease.in3(inv(0.15, 0.9, lt));
  ctx.fillStyle = '#060303'; ctx.fillRect(0, 0, W, H);
  const sc = lerp(5.0, 7.5, ease.io2(inv(0, 0.9, lt)));
  const eyeLocal = [22, -20], ex = 540, ey = 900;
  const [qx, qy] = headAt(22, -20, sc); if (pk < 1) faceLying(ctx, t, ex - qx, ey - qy, sc, { blink: 0, look: [0, 0], brow: 0.6, sweat: 0.8, t }, { heat: 0.6, key: 0.6 });
  // pupil dilation fills the frame
  const R = lerp(60, 1400, pk);
  ctx.save(); ctx.fillStyle = '#020102'; ctx.beginPath(); ctx.arc(ex, ey, R, 0, 6.283); ctx.fill(); ctx.restore();
  if (lt > 0.55) {
    // neural lightning radiating out of the pupil
    const k = inv(0.55, 1.75, lt), r = mulberry(31);
    ctx.save(); ctx.globalCompositeOperation = 'screen';
    for (let i = 0; i < 22; i++) { let x = ex, y = ey, a = r() * 6.283; const pts = [[x, y]];
      for (let s = 0; s < 14 * k; s++) { a += (r() - 0.5) * 0.9; x += Math.cos(a) * 48; y += Math.sin(a) * 48; pts.push([x, y]); }
      ctx.strokeStyle = rgba('#f6d58e', 0.85); ctx.lineWidth = 3.5; ctx.beginPath(); crPath(ctx, pts, false); ctx.stroke();
      ctx.filter = 'blur(6px)'; ctx.lineWidth = 12; ctx.strokeStyle = rgba('#f6d58e', 0.35); ctx.stroke(); ctx.filter = 'none';
      const P = pts[Math.floor(((t * 1.4 + i * 0.13) % 1) * (pts.length - 1))]; if (P) glow(ctx, P[0], P[1], 40, '#fff4cc', 0.9); }
    ctx.restore();
    glow(ctx, ex, ey, 500, '#ffd890', 0.4 * (1 - k));
  }
}
// 28.24 - 30.0 : the nervous system inside his body, lying, wide silhouette
function w16(ctx, t) {
  const lt = t - B(16);
  anatomyField(ctx, t, { warm: 0.15 });
  const pose = lieP(poseAt(t, [[B(16), 'lieCurl'], [29.6, 'liePress']]), t, { breath: 2, tremble: 0.5, rate: 4 });
  const L = LIE(lerp(620, 560, lt / 1.8), 1050, lerp(0.56, 0.6, lt / 1.8));
  const { S, J } = silL('w16s', pose, t, L);
  clipTo(ctx, S, (g) => { g.fillStyle = 'rgba(16,30,50,0.92)'; g.fillRect(0, 0, W, H); });
  silRim(ctx, S, '#7fd6ff', 0.9, 0, -3);
  rigNerves(ctx, J, L, t, { reveal: 1, disturb: 0.25 });
  const head = XP(L, [J.neck[0] - 50, J.neck[1] - 210]);
  ctx.save(); ctx.translate(head[0], head[1]); ctx.rotate(-Math.PI / 2); ctx.scale(0.25 * L[2] / 0.72, 0.25 * L[2] / 0.72); brainLat(ctx, { t, glow: '#ffe6a8' }); ctx.restore();
}
// 30.0 - 33.53 : DIZZINESS: subjective POV lying under the shell, hands before his eyes, unstable horizon
function w17(ctx, t) { v11(ctx, t); }
// 33.53 - 35.29 : thermoregulation heat map in his curled body
function w18(ctx, t) {
  const lt = t - EV.scan3, k = inv(0, 1.8, lt);
  const L = LIE(560, 1120, 0.6);
  shellTight(ctx, t, L, { heat: 0.9, seamX: 780 });
  ctx.save(); ctx.globalAlpha = 0.6; ctx.fillStyle = '#04070d'; ctx.fillRect(0, 0, W, H); ctx.restore();
  const pose = lieP(poseAt(t, [[EV.scan3, 'lieCurl'], [35.29, 'lieWipe']]), t, { breath: 2, tremble: 0.6, rate: 4.2 });
  const { S, J } = silL('w18s', pose, t, L);
  const core = XP(L, [lerp(J.root[0], J.chest[0], 0.5), lerp(J.root[1], J.chest[1], 0.5)]);
  clipTo(ctx, S, (g) => { g.fillStyle = 'rgba(14,26,44,0.95)'; g.fillRect(0, 0, W, H);
    g.fillStyle = radGrad(g, core[0], core[1], 20, lerp(250, 900, k), [[0, rgba('#ff5a1a', 0.95)], [0.45, rgba('#ff8a2a', 0.55)], [1, rgba('#ffb04a', 0)]]); g.fillRect(0, 0, W, H); });
  silRim(ctx, S, mix('#7fd6ff', '#ffb07a', k), 0.95, 0, -3);
  ctx.save(); ctx.globalCompositeOperation = 'screen';
  for (let i = 0; i < 18; i++) { const a = i / 18 * 6.283, u = ((lt * 0.8 + i * 0.137) % 1), len = 220 + (i % 3) * 60, pts = [];
    for (let s2 = 0; s2 <= 1; s2 += 0.1) { const rr = s2 * len * (0.3 + 0.7 * u); pts.push([core[0] + Math.cos(a) * rr * 1.5 + Math.sin(s2 * 7 + t * 5 + i) * 12, core[1] + Math.sin(a) * rr]); }
    ctx.strokeStyle = rgba('#ffc07a', 0.55 * (1 - u)); ctx.lineWidth = 4; ctx.beginPath(); crPath(ctx, pts, false); ctx.stroke(); }
  ctx.restore();
  const hyp = XP(L, [J.neck[0] - 60, J.neck[1] - 170]); glow(ctx, hyp[0], hyp[1], 60, '#9fdcff', 0.6 + 0.4 * Math.sin(t * 7));
  label(ctx, hyp[0], hyp[1], hyp[0] + 120, hyp[1] - 220, 'HYPOTHALAMUS', '#9fdcff', env(lt, 0.3, 1.7, 0.25, 0.25));
}
// 35.29 - 37.06 : character beat: profile close-up, laboured breath, heat haze (wail)
function w19(ctx, t) {
  const lt = t - B(20);
  const L = cvs('w19'), g = L.getContext('2d');
  g.fillStyle = '#0a0503'; g.fillRect(0, 0, W, H); glow(g, 300, 1700, 900, '#ff5a1a', 0.5);
  const st = { blink: blinkAt(t, 1, [36.4]), brow: 0.7, mouth: 0.4 + 0.3 * Math.sin(t * 5), sweat: 1, t, breath: Math.sin(t * 5) * 1.2, slump: 0 };
  litRender(g, (g2, C) => { g2.save(); g2.translate(lerp(560, 600, lt / 1.8), 1020); g2.rotate(-0.28); g2.scale(2.0, 2.0); headProfile(g2, C, st); g2.restore(); },
    (m) => radialMask(m, 400, 600, 40, 900, 0.75), Object.assign({ rim: { dx: 0, dy: -7, col: '#ff9a4a', a: 0.9 } }, warmPal(0.85)));
  ctx.drawImage(L, 0, 0); heatShimmer(ctx, L, t, 3 + 3 * Math.sin(t * 2), 0, H);
}
// 37.06 - 40.59 : HEATSTROKE: exterior side profile, interior red-hot, his silhouette fills the torso
function w20(ctx, t) {
  const lt = t - EV.clank, mv = ease.io2(inv(0, 3.5, lt));
  const sc = lerp(1.04, 1.5, ease.in2(inv(1.6, 3.5, lt))), bx = lerp(560, 600, mv), by = lerp(1640, 1760, ease.in2(inv(1.6, 3.5, lt)));
  const L = cvs('w20'), g = L.getContext('2d');
  exteriorBase(g, t, { x: lerp(-40, 40, mv), s: 1.3, hz: 1500, bx, by, sc });
  bullCutaway3(g, bx, by, sc, t, { open: ease.out3(inv(0, 0.4, lt)), heat: 1, silhouette: true, pose: lieP('lieCurl', t, { breath: 2, tremble: 0.6 }), eyeGlow: 0.5 });
  ctx.drawImage(L, 0, 0); heatShimmer(ctx, L, t, 2, by - 700 * sc, by);
  ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.fillStyle = linGrad(ctx, 0, 0, 0, H, [[0, '#5a2a2a'], [0.55, '#ffffff'], [1, '#7a3a2a']]); ctx.fillRect(0, 0, W, H); ctx.restore();
  motes(ctx, t, 80, 71, { y0: 1300, y1: 1900, vy: -180, vx: 10, size: [1, 3.4], col: '#ffb060', a: 0.85, life: 3 });
}
// 40.59 - 42.35 : brain through a lens in his head (profile)
function w21(ctx, t) { v14(ctx, t); }
// 42.35 - 43.68 : his eye, slow heavy blink, unfocused (heartbeat)
function w22(ctx, t) {
  const lt = t - B(24), hb = HEARTBEATS.reduce((a, x) => (t >= x ? Math.max(a, Math.exp(-(t - x) * 6)) : a), 0);
  ctx.fillStyle = '#060303'; ctx.fillRect(0, 0, W, H);
  const sc = 4.4 + hb * 0.06; const ex = 540, ey = 900;
  const Lc = cvs('w22'), g = Lc.getContext('2d');
  const [qx, qy] = headAt(22, -20, sc); faceLying(g, t, ex - qx, ey - qy, sc, { blink: clamp(0.35 + 0.65 * Math.sin(Math.PI * inv(0.3, 1.1, lt))), look: [0.1, 0.3], brow: 0.4, sweat: 1, t }, { heat: 0.6, key: 0.55 });
  ctx.save(); ctx.filter = `blur(${2 + 4 * hb}px)`; ctx.drawImage(Lc, 0, 0); ctx.globalAlpha = 0.35; ctx.drawImage(Lc, 18, 0); ctx.restore();
  ctx.save(); ctx.fillStyle = radGrad(ctx, W / 2, H / 2, 260 - hb * 100, 1000, [[0, 'rgba(0,0,0,0)'], [1, rgba('#200404', 0.6 + hb * 0.3)]]); ctx.fillRect(0, 0, W, H); ctx.restore();
}
// 43.68 - 45.44 : organs layered inside his lying torso
function w23(ctx, t) {
  const lt = t - EV.wail5, hot = inv(0.2, 3.5, lt);
  const hb = HEARTBEATS.reduce((a, x) => (t >= x ? Math.max(a, Math.exp(-(t - x) * 7)) : a), 0);
  const L = LIE(lerp(1180, 1240, lt / 1.8), lerp(900, 870, lt / 1.8), 1.35);
  const pose = lieP('lie', t, { breath: 2.2, rate: 4 });
  shellTight(ctx, t, L, { heat: 0.85, seam: false });
  ctx.save(); ctx.globalAlpha = 0.5; ctx.fillStyle = '#05030a'; ctx.fillRect(0, 0, W, H); ctx.restore();
  const { S, J } = silL('w23s', pose, t, L);
  clipTo(ctx, S, (g) => { g.fillStyle = mix('#14233a', '#3a1a12', hot * 0.6); g.fillRect(0, 0, W, H); });
  silRim(ctx, S, mix('#7fd6ff', '#ffb07a', hot), 0.9, 0, -4);
  const at = (u, dx) => XP(L, J.rot([lerp(J.root[0], J.chest[0], u), lerp(J.root[1], J.chest[1], u)], dx, 0));
  const kid = at(0.42, 90), liv = at(0.56, -60), hrt = at(0.8, 20);
  ctx.save(); ctx.globalAlpha = 0.85; ctx.translate(kid[0], kid[1]); ctx.rotate(-Math.PI / 2); ctx.scale(L[2] * 1.35, L[2] * 1.35); kidney(ctx, -40, 0, -1, { hot }); kidney(ctx, 50, -10, 1, { hot }); ctx.restore();
  ctx.save(); ctx.translate(liv[0], liv[1]); ctx.rotate(-Math.PI / 2); ctx.scale(L[2] * 1.25, L[2] * 1.25); ctx.translate(0, 260); liver(ctx, { hot }); ctx.restore();
  ctx.save(); ctx.translate(hrt[0], hrt[1]); ctx.rotate(-Math.PI / 2 * 0.2); ctx.scale(L[2] * 0.5, L[2] * 0.5); heartAnt(ctx, { beat: hb, stress: hot, t }); ctx.restore();
  const la = env(lt, 0.3, 1.7, 0.2, 0.2);
  label(ctx, hrt[0], hrt[1], hrt[0] - 140, hrt[1] - 380, 'HEART', '#ffc0a8', la);
  label(ctx, liv[0], liv[1], liv[0] + 120, liv[1] - 420, 'LIVER', '#ffc0a8', la);
  label(ctx, kid[0], kid[1], kid[0] - 120, kid[1] - 330, 'KIDNEYS', '#ffc0a8', la);
}
// 45.44 - 47.43 : the organs fade back into the real man; heat floods in (reverse roar)
function w24(ctx, t) {
  const lt = t - B(26), k = inv(0, 1.9, lt);
  const L = LIE(lerp(640, 600, k), 1120, lerp(0.62, 0.68, k));
  const pose = lieP(poseAt(t, [[B(26), 'lie'], [47.0, 'lieCurl']]), t, { breath: 2.4, rate: 5, tremble: 0.6 });
  pose.face = { brow: 0.8, mouth: 0.5, sweat: 1, blink: Math.max(blinkAt(t), 0.3) };
  shellTight(ctx, t, L, { heat: 0.95, seamX: 640 });
  drawLying(ctx, pose, t, L, { heat: 0.95 });
  ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.globalAlpha = 0.45 * inv(EV.roarRev, EV.sil2, t); ctx.fillStyle = '#ff4a1a'; ctx.fillRect(0, 0, W, H); ctx.restore();
}
// 47.65 - 49.41 : FINAL DROP: fusion (profile x anatomy)
function w25(ctx, t) { v16(ctx, t); }
// 49.41 - 50.96 : exterior, closer: the bull glows, his silhouette visible within
function w26(ctx, t) {
  const lt = t - B(28), mv = ease.io2(inv(0, 1.55, lt));
  const sc = lerp(1.55, 1.35, mv), bx = lerp(700, 640, mv), by = 1880;
  const L = cvs('w26'), g = L.getContext('2d');
  exteriorBase(g, t, { x: lerp(60, -60, mv), s: 1.5, hz: 1640, bx, by, sc });
  bullCutaway3(g, bx, by, sc, t, { open: 1, heat: 1, silhouette: true, pose: lieP('lieCurl', t, { breath: 2.2, tremble: 0.6 }), eyeGlow: 0.6 + 0.4 * kickPulse(t, 6) });
  ctx.drawImage(L, 0, 0);
  motes(ctx, t, 90, 81, { y0: 1100, y1: 1900, vy: -200, vx: 20, size: [1, 3.4], col: '#ffb060', a: 0.85, life: 2.5 });
}
// 50.96 - 52.06 : consciousness: his face, eyes closing, focus softening
function w27(ctx, t) {
  const lt = t - EV.wail6, k = inv(0, 1.1, lt);
  const stutter = (t > EV.stutter && t < EV.stutter + 0.36) ? Math.floor((t - EV.stutter) / 0.11) % 2 : 0;
  const Lc = cvs('w27'), g = Lc.getContext('2d');
  g.fillStyle = '#080403'; g.fillRect(0, 0, W, H); glow(g, 540, 1600, 800, '#ff5a1a', 0.35);
  faceLying(g, t, 600, 1000, 2.3, { blink: clamp(ease.io3(inv(0.1, 1.05, lt))), look: [0, 0.3], brow: lerp(0.5, 0.1, k), mouth: 0.2, sweat: 1, t }, { heat: 0.5, key: lerp(0.5, 0.25, k) });
  ctx.save(); ctx.filter = `blur(${lerp(0, 6, k)}px) saturate(${lerp(1, 0.4, k)})`; ctx.drawImage(Lc, stutter * 26, 0); ctx.restore();
  if (stutter) { ctx.save(); ctx.globalAlpha = 0.4; ctx.globalCompositeOperation = 'screen'; ctx.drawImage(Lc, -30, 6); ctx.restore(); }
}
// 52.06 - 52.94 : CLIMAX a) his silhouette, rim of fire
function w28(ctx, t) {
  ctx.fillStyle = '#060203'; ctx.fillRect(0, 0, W, H); glow(ctx, 540, 1000, 1000, '#ff3a10', 0.8);
  const L = LIE(lerp(560, 600, inv(52.06, 52.94, t)), 1100, 0.66);
  const { S } = silL('w28s', lieP('lieLimp', t, { breath: 0.6 }), t, L);
  const D = cvs('w28d'), dg = D.getContext('2d'); dg.drawImage(S, 0, 0); dg.globalCompositeOperation = 'source-in'; dg.fillStyle = '#050203'; dg.fillRect(0, 0, W, H);
  ctx.drawImage(D, 0, 0); silRim(ctx, S, '#ffb060', 1, 0, -8);
}
// 52.94 - 53.82 : b) the nervous system flickers through him
function w29(ctx, t) {
  anatomyField(ctx, t, { warm: 0.5 });
  const L = LIE(600, 1100, lerp(0.7, 0.76, inv(52.94, 53.82, t)));
  const pose = lieP('lieLimp', t, { breath: 0.4 });
  const { S, J } = silL('w29s', pose, t, L);
  clipTo(ctx, S, (g) => { g.fillStyle = 'rgba(20,10,12,0.95)'; g.fillRect(0, 0, W, H); });
  silRim(ctx, S, '#ff9a6a', 0.9, 0, -3);
  rigNerves(ctx, J, L, t, { reveal: 1, disturb: 0.85, col: '#ff9a6a' });
}
// 53.82 - 54.71 : c) eye close-up: the eye closes
function w30(ctx, t) {
  ctx.fillStyle = '#050202'; ctx.fillRect(0, 0, W, H);
  const sc = lerp(5.5, 6.2, inv(53.82, 54.71, t)), ex = 540, ey = 940;
  const [qx, qy] = headAt(22, -20, sc); faceLying(ctx, t, ex - qx, ey - qy, sc, { blink: clamp(ease.in2(inv(53.9, 54.6, t))), look: [0, 0.2], brow: 0.2, sweat: 1, t }, { heat: 0.4, key: 0.5 });
}
// 54.71 - 56.47 : d) his body fades into dark bronze; embers rise to the seam
function w31(ctx, t) {
  const lt = t - EV.scan4, k = inv(0, 1.76, lt);
  ctx.fillStyle = '#050304'; ctx.fillRect(0, 0, W, H);
  shaft(ctx, 540, 0, 20, 540, 900, 380, '#ffc070', 0.25 + 0.25 * k);
  const L = LIE(560, 1150, 0.68);
  const { S } = silL('w31s', lieP('lieLimp', t, { breath: 0 }), t, L);
  const D = cvs('w31d'), dg = D.getContext('2d'); dg.drawImage(S, 0, 0); dg.globalCompositeOperation = 'source-in';
  dg.fillStyle = linGrad(dg, 0, 900, 0, 1400, [[0, mix('#1a0c06', '#8a5a2a', k)], [1, mix('#0c0504', '#3a2210', k)]]); dg.fillRect(0, 0, W, H);   // turning to bronze
  ctx.drawImage(D, 0, 0); silRim(ctx, S, '#ffb060', 0.9 * (1 - k * 0.5), 0, -4);
  const r = mulberry(5);
  for (let i = 0; i < 150; i++) { const x0 = lerp(180, 900, r()), y0 = lerp(1000, 1300, r()), ph = r() * 0.8, u = clamp((lt * 0.8 - ph * 0.5) / 1.0); if (u <= 0) continue;
    const x = lerp(x0, 540 + (x0 - 540) * 0.25, ease.io2(u)) + Math.sin(t * 3 + i) * 14, y = lerp(y0, 60, ease.in2(u)), a = Math.sin(Math.PI * clamp(u * 1.1)) * 0.9, s = 1.5 + r() * 3;
    ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.globalAlpha = a; ctx.fillStyle = '#ffc070'; ctx.beginPath(); ctx.arc(x, y, s, 0, 6.283); ctx.fill(); ctx.globalAlpha = a * 0.3; ctx.beginPath(); ctx.arc(x, y, s * 4, 0, 6.283); ctx.fill(); ctx.restore(); }
}
// 56.47 - 58.10 : spectacular exterior side profile; the ROAR; a brief true-scale reveal inside the torso
function w32(ctx, t) {
  const lt = t - EV.bar32, roar = inv(EV.roarClimax - 0.05, EV.roarClimax + 0.1, t), mv = ease.io2(inv(0, 1.63, lt));
  const reveal = env(t, EV.roarClimax - 0.02, EV.roarClimax + 0.32, 0.05, 0.15);
  const sc = lerp(1.0, 1.08, mv), bx = lerp(600, 560, mv), by = 1620;
  const L = cvs('w32'), g = L.getContext('2d');
  courtyard(g, { x: lerp(100, -60, mv), y: 0, s: 1.3, hz: 1450, bullX: -9999, bullY: by, bullS: sc }, t, { fire: 1 });
  glow(g, 840, 520, 260, '#f0e0c0', 0.35); g.fillStyle = '#efe3c8'; g.beginPath(); g.arc(840, 520, 62, 0, 6.283); g.fill();
  g.save(); g.translate(bx, by); g.scale(sc, sc); plinth(g); g.restore();
  glow(g, bx, by, 720 * sc, '#ff6a1a', 0.45 + roar * 0.35);
  bullCutaway3(g, bx, by, sc, t, { open: reveal, heat: 1, silhouette: true, pose: lieP('lieLimp', t, { breath: 0 }), eyeGlow: 0.35 + roar * 1.2, fire: 1 + roar * 0.6 });
  ctx.drawImage(L, 0, 0);
  const r = mulberry(19);
  for (let i = 0; i < 140; i++) { const ph = r(), sp = 0.4 + r() * 0.6, u = ((lt * sp + ph) % 1); const x0 = bx + lerp(-300, 250, r()) * sc, y0 = by - 600 * sc;
    const x = x0 + Math.sin(u * 5 + i) * 60 + u * 160, y = y0 - u * 1300, a = Math.sin(Math.PI * u) * (0.55 + roar * 0.45);
    ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.globalAlpha = a; ctx.fillStyle = '#ffb060'; ctx.beginPath(); ctx.arc(x, y, 1.6 + r() * 2.6, 0, 6.283); ctx.fill(); ctx.restore(); }
  if (roar > 0) { const hx = bx - 470 * sc, hy = by - 372 * sc, u = inv(EV.roarClimax, EV.roarClimax + 0.45, t);
    glow(ctx, hx, hy, 600 * roar, '#ff7a2a', 0.55 * roar);
    for (let k2 = 0; k2 < 2; k2++) { const uu = clamp(u - k2 * 0.15); ctx.save(); ctx.strokeStyle = rgba('#ffc890', 0.7 * (1 - uu)); ctx.lineWidth = 8 * (1 - uu) + 1; ctx.beginPath(); ctx.arc(hx, hy, 60 + uu * 800, 0, 6.283); ctx.stroke(); ctx.restore(); } }
}
// 58.24 - 60.0 : bronze eye -> eye-shaped highlight that becomes the opening frame (loop)
function w33(ctx, t) {
  const lt = t - EV.final;
  ctx.fillStyle = '#060403'; ctx.fillRect(0, 0, W, H);
  const push = ease.in3(inv(0.5, 1.6, lt));
  const s = lerp(3.0, 3.4, ease.out2(inv(0, 0.8, lt))) * lerp(1, 4, push);
  const L = cvs('w33'), g = L.getContext('2d');
  g.save(); g.translate(540, 880); g.scale(s, s); g.translate(470, 372); bullBronze(g, { glow: 0.6, t, eyeGlow: 0.7 + 0.3 * kick(t, EV.final, 3) }); g.restore();
  ctx.save(); ctx.globalAlpha = 1 - inv(1.2, 1.7, lt); ctx.drawImage(L, 0, 0); ctx.restore();
  // last frames: his eye fades in under the same warm reflection - identical to frame 1
  const back = inv(1.35, 1.765, lt);
  if (back > 0) { ctx.save(); ctx.globalAlpha = back; w01(ctx, 0.0); ctx.restore(); }
}

const SHOTS3 = [
  [w01, 0, EV.whoosh0], [w02, EV.whoosh0, B(3)], [w03, B(3), 7.06], [w04, 7.06, B(5)], [w05, B(5), EV.scan1], [w06, EV.scan1, B(7)],
  [w07, B(7), EV.fire1], [w08, EV.fire1, B(9)], [w09, B(9), EV.slam2], [w10, EV.slam2, 19.0], [w11, 19.0, EV.shriek1], [w12, EV.shriek1, EV.riser],
  [w13, EV.riser, EV.predrop], [w14, EV.predrop, EV.drop1], [w15, EV.drop1, B(16)], [w16, B(16), 30.0], [w17, 30.0, EV.scan3], [w18, EV.scan3, B(20)],
  [w19, B(20), EV.clank], [w20, EV.clank, EV.slam4], [w21, EV.slam4, B(24)], [w22, B(24), EV.wail5], [w23, EV.wail5, B(26)], [w24, B(26), EV.drop2],
  [w25, EV.drop2, B(28)], [w26, B(28), EV.wail6], [w27, EV.wail6, 52.06], [w28, 52.06, 52.94], [w29, 52.94, 53.82], [w30, 53.82, EV.scan4], [w31, EV.scan4, EV.bar32],
  [w32, EV.bar32, EV.final], [w33, EV.final, 60.01],
];
