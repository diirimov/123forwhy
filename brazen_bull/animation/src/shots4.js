// V4 SHOTS — three acts: THE LEGEND / THE SIMULATION / THE INVENTOR'S FATE.
'use strict';
const SH = (fn, src, dst) => (ctx, t) => fn(ctx, t - dst + src);     // reuse a shot at a new time (bar-aligned shifts keep beats aligned)

// ================================================================== ACT I — THE LEGEND
// 0.00-3.53: the bull's face emerging from darkness (the title words follow the narration)
function bullFace(ctx, t, reveal, opt = {}) {
  ctx.fillStyle = '#050302'; ctx.fillRect(0, 0, W, H);
  const s = opt.s ?? lerp(3.4, 3.0, ease.out2(clamp(reveal))), eyeX = -470, eyeY = -372;
  const L = cvs('bface'), g = L.getContext('2d');
  g.save(); g.translate(opt.x ?? 600, opt.y ?? 1130); g.scale(s, s); g.translate(-eyeX + 40, -eyeY + 20);
  bullBronze(g, { glow: 0.5 + 0.5 * reveal, t, eyeGlow: opt.eye ?? (0.35 + 0.5 * reveal) }); g.restore();
  // light sweep reveal: only the swept band + rim is visible early on
  const M = cvs('bfaceM'), m = M.getContext('2d');
  const sx = lerp(-500, 1500, ease.io2(clamp(reveal)));
  m.fillStyle = linGrad(m, sx - 700, 0, sx + 200, 0, [[0, rgba('#ffffff', 0.25 + 0.75 * clamp(reveal))], [0.75, '#ffffff'], [1, rgba('#ffffff', 0.12)]]); m.fillRect(0, 0, W, H);
  g.globalCompositeOperation = 'destination-in'; g.drawImage(M, 0, 0); g.globalCompositeOperation = 'source-over';
  ctx.drawImage(L, 0, 0);
  ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.globalAlpha = 0.35 * (1 - clamp(reveal)); ctx.fillStyle = linGrad(ctx, sx - 160, 0, sx + 160, 0, [[0, 'rgba(255,190,110,0)'], [0.5, 'rgba(255,200,120,1)'], [1, 'rgba(255,190,110,0)']]); ctx.fillRect(0, 0, W, H); ctx.restore();
  motes(ctx, t, 50, 77, { y0: 1100, y1: 1900, vy: -110, vx: 12, size: [1, 3], col: '#ffb060', a: 0.7, life: 3 });
}
function a01(ctx, t) { bullFace(ctx, t, inv(0.0, 3.2, t) * 0.85 + 0.15); }
// 3.53-5.29: engraved bronze map, route Athens -> Akragas, zoom into Sicily
function a02(ctx, t) { const lt = t - EV.slam1; mapScene(ctx, t, ease.io3(inv(0.2, 1.76, lt)) * 0.75, { route: ease.out3(inv(0, 1.2, lt)), pulse: kickPulse(t, 5) }); }
// 5.29-7.06: Akragas — city, temples, citizens
function a03(ctx, t) { const lt = t - BAR * 3; const k = ease.io2(inv(0, 1.77, lt)); ctx.save(); ctx.translate(W / 2, H / 2); const s = lerp(1.12, 1.0, k); ctx.scale(s, s); ctx.translate(-W / 2, -H / 2 + lerp(-60, 0, k)); akragas(ctx, t, { x: lerp(-40, 40, k), up: lerp(40, 0, k) }); ctx.restore(); }
// 7.06-8.82: Perillus at the anvil — hammer strikes land on the beat (sparks)
function a04(ctx, t) {
  const lt = t - 7.06, cam = ease.io2(inv(0, 1.77, lt));
  workshop(ctx, t, { x: lerp(-30, 30, cam) });
  // strike on every other kick: down-stroke 0.12 s before the kick, rebound after
  let lastK = -9, nextK = 99; for (const k of KICKS) { if (k <= t && k >= 7.0) lastK = k; if (k > t) { nextK = Math.min(nextK, k); } }
  const toNext = nextK - t, sinceK = t - lastK;
  let ph = 0; if (toNext < 0.14) ph = ease.in3(1 - toNext / 0.14); else if (sinceK < 0.3) ph = 1 - ease.out3(sinceK / 0.3);
  const pose = secondary(cast('perillus', blendPose('hammerUp', 'hammerDown', ph)), t, { breath: 0.8 });
  pose.face = { brow: 0.55, look: [-0.6, 0.4], mouth: 0.2 + 0.25 * ph }; pose.propA = lerp(Math.PI * 0.3, Math.PI * 0.7, ph);
  anvil(ctx, 640, 1090, 1.0);
  ctx.fillStyle = linGrad(ctx, 520, 958, 800, 970, [[0, '#ffb060'], [1, '#d87a30']]); ctx.fillRect(520, 958, 280, 14);   // hot bronze sheet
  drawChar(ctx, 'perillus', pose, t, [lerp(830, 810, cam), 820, 0.6], { lag: -ph * 0.5 });
  if (sinceK < 0.25) { const a = 1 - sinceK / 0.25; glow(ctx, 790, 960, 220, '#ffd090', 0.9 * a);
    const r = mulberry(Math.floor(lastK * 100)); for (let i = 0; i < 26; i++) { const ang = -Math.PI * r(), sp = 300 + r() * 500, d = sinceK;
      const x = 790 + Math.cos(ang) * sp * d, y = 960 + Math.sin(ang) * sp * d + 900 * d * d; ctx.fillStyle = rgba('#ffd890', a); ctx.fillRect(x, y, 4, 4); } }
}
// 8.82-10.59: the reveal — he pulls the cloth from the finished bull and steps back
function a05(ctx, t) {
  const lt = t - BAR * 5, pull = ease.io3(inv(0.15, 0.75, lt));
  workshop(ctx, t, { x: 40 });
  const bx = 640, by = 1540, sc = 0.78;
  ctx.save(); ctx.translate(bx, by); ctx.scale(sc, sc); plinth(ctx, 900, 60); ctx.restore();
  bullLayer(ctx, bx, by, sc, { glow: 0.3, t, eyeGlow: 0.25 * pull, rims: [[-6, 4, '#ffe0a8', 0.9 * pull], [8, 0, '#ff9a4a', 0.4 * pull]] });
  // the cloth: covers the bull, slides off to the right with folds
  if (pull < 1) { const dx = pull * 900, sag = Math.sin(pull * Math.PI) * 120;
    const cl = [[bx - 560 * sc + dx, by - 660 * sc - sag * 0.2], [bx + 450 * sc + dx, by - 640 * sc], [bx + 470 * sc + dx * 1.2, by + 20], [bx - 540 * sc + dx * 0.9, by + 20 + sag * 0.3]];
    ctx.fillStyle = linGrad(ctx, bx - 400, by - 500, bx + 400, by, [[0, '#9a4a2a'], [1, '#3a140a']]); ctx.beginPath(); crPath(ctx, cl, true, 0.3); ctx.fill();
    ctx.save(); ctx.beginPath(); crPath(ctx, cl, true, 0.3); ctx.clip(); for (let i = 0; i < 8; i++) { ctx.filter = 'blur(5px)'; brush(ctx, [[bx - 500 * sc + dx + i * 110 * sc, by - 600 * sc], [bx - 480 * sc + dx * 1.05 + i * 116 * sc + sag * 0.2, by - 200 * sc], [bx - 470 * sc + dx * 1.1 + i * 120 * sc, by]], 24, 14, 'rgba(0,0,0,0.12)', false); } ctx.restore(); }
  const pose = secondary(cast('perillus', poseAt(t, [[BAR * 5, 'pull'], [BAR * 5 + 0.75, 'pull'], [BAR * 5 + 1.15, 'proud', ease.out3]])), t, { breath: 0.9 });
  pose.face = { brow: 0.1, look: [-0.5, -0.1], mouth: 0.35 * env(t, 9.9, 10.6, 0.2, 0.2) };
  drawChar(ctx, 'perillus', pose, t, [lerp(960, 880, pull), 900, 0.52], { lag: Math.sin(lt * 5) * kick(t, BAR * 5 + 0.75, 3) });
  glow(ctx, bx, by - 300, 600 * pull, '#ffd8a0', 0.25 * pull);
}
// 10.59-12.35: Phalaris enthroned, guards at his sides (low angle push-in)
function a06(ctx, t) {
  const lt = t - EV.scan1, k = ease.io2(inv(0, 1.77, lt));
  ctx.save(); ctx.translate(W / 2, H); const s = lerp(1.0, 1.08, k); ctx.scale(s, s); ctx.translate(-W / 2, -H);
  throneRoom(ctx, t, { x: lerp(-20, 20, k) });
  for (const [x, flip] of [[150, false], [930, true]]) drawChar(ctx, 'guard', secondary(cast('guard', 'guardStand'), t + x, { breath: 0.4 }), t, [x, 900, 0.5], { flip });
  const pose = secondary(cast('phalaris', 'seated'), t, { breath: 0.5 }); pose.face = { look: [-0.2, 0.15], brow: 0.3 };
  drawChar(ctx, 'phalaris', pose, t, [560, 700, 0.62], { key: 0.85, rimCol: '#ffc070' });
  ctx.restore();
}
// 12.35-13.24: Perillus presents his work (gesture), shot from Phalaris' side
function a07(ctx, t) {
  const lt = t - BAR * 7;
  throneRoom(ctx, t, { x: 200 });
  ctx.save(); ctx.globalAlpha = 0.55; ctx.fillStyle = '#0a0506'; ctx.fillRect(0, 0, W, H); ctx.restore();
  const pose = secondary(cast('perillus', poseAt(t, [[BAR * 7, 'proud'], [BAR * 7 + 0.4, 'present', ease.outBack]])), t, { breath: 0.8 });
  pose.face = { brow: 0.1, look: [-0.6, -0.1], mouth: 0.4 * env(t, 12.6, 13.2, 0.1, 0.1) };
  drawChar(ctx, 'perillus', pose, t, [600, 800, 0.72], { key: 0.9 });
  // over-the-shoulder: the tyrant's dark silhouette in the foreground
  ctx.save(); ctx.filter = 'blur(6px)'; ctx.fillStyle = '#080406'; ctx.beginPath(); ctx.ellipse(1040, 1500, 300, 520, 0.1, 0, 6.283); ctx.fill(); ctx.beginPath(); ctx.ellipse(980, 960, 150, 180, 0, 0, 6.283); ctx.fill(); ctx.restore();
}
// 13.24-14.12: reverse shot — Phalaris' slow, cold smile; he raises a hand
function a08(ctx, t) {
  const lt = t - (BAR * 7 + 0.882);
  throneRoom(ctx, t, { x: -120 });
  ctx.save(); ctx.globalAlpha = 0.45; ctx.fillStyle = '#0a0506'; ctx.fillRect(0, 0, W, H); ctx.restore();
  headChar(ctx, 'phalaris', { look: [0.2, 0.05], brow: lerp(0.2, 0.45, lt), mouth: 0.08 }, t, 520 + lt * 20, 900, 1.5, { flip: true, key: 0.9, rimCol: '#ff9a4a' });
}
// 14.12-15.88: the bull's head, close, fire beneath; symbolic sound waves pulse from its mouth on the beat
function a09(ctx, t) {
  const lt = t - EV.fire1;
  bullFace(ctx, t, 1, { s: lerp(1.9, 2.1, lt / 1.76), x: 560, y: 1080, eye: 0.7 + 0.3 * kickPulse(t, 6) });
  glow(ctx, 540, 1900, 900, '#ff6a1a', 0.35 + 0.25 * kick(t, EV.fire1, 2));
  const mx = 560 + (-520 + 470 - 40) * lerp(1.9, 2.1, lt / 1.76) * 0, my = 1080;
  const ox = 560 + (-525 + 470 - 40) * lerp(1.9, 2.1, lt / 1.76), oy = 1080 + (-270 + 372 - 20) * lerp(1.9, 2.1, lt / 1.76);
  for (const k of KICKS) { const d = t - k; if (d < 0 || d > 1.2 || k < EV.fire1) continue;
    const u = d / 1.2; ctx.save(); ctx.strokeStyle = rgba('#ffd08a', 0.75 * (1 - u)); ctx.lineWidth = 6 * (1 - u) + 1;
    ctx.beginPath(); ctx.arc(ox, oy, 60 + u * 700, Math.PI * 0.7, Math.PI * 1.3); ctx.stroke(); ctx.restore(); }
}
// 15.88-17.21: reactions — the court watches the bronze; a guard turns his head away
function a10(ctx, t) {
  const lt = t - BAR * 9;
  throneRoom(ctx, t, { x: 60 });
  ctx.save(); ctx.globalAlpha = 0.4; ctx.fillStyle = '#0a0506'; ctx.fillRect(0, 0, W, H); ctx.restore();
  // bull silhouette behind, glowing waves
  bullLayer(ctx, 540, 1280, 0.62, { glow: 1, t, eyeGlow: 0.6 });
  for (const k of KICKS) { const d = t - k; if (d < 0 || d > 1.2 || k < BAR * 9) continue; const u = d / 1.2;
    ctx.save(); ctx.strokeStyle = rgba('#ffd08a', 0.6 * (1 - u)); ctx.lineWidth = 4; ctx.beginPath(); ctx.arc(540 - 470 * 0.62, 1280 - 300 * 0.62, 40 + u * 600, 0, 6.283); ctx.stroke(); ctx.restore(); }
  const gp = secondary(cast('guard', poseAt(t, [[BAR * 9, 'guardStand'], [BAR * 9 + 0.6, 'guardStep']])), t, { breath: 0.6 }); gp.head += lerp(0, 0.35, inv(BAR * 9 + 0.3, BAR * 9 + 0.8, t));
  drawChar(ctx, 'guard', gp, t, [200, 980, 0.62], { key: 0.8 });
  const pp = secondary(cast('phalaris', 'standPoint'), t, { breath: 0.4 }); pp.nT = { c: [-150, 560] }; pp.nHand = 'relax'; pp.face = { look: [-0.4, 0], brow: 0.2, mouth: 0.05 };
  drawChar(ctx, 'phalaris', pp, t, [860, 900, 0.7], { flip: true, key: 0.85, rimCol: '#ff9a4a' });
}

// ================================================================== ACT II — THE SIMULATION (V3 shots, re-timed to bar-aligned slots)
function b01(ctx, t) {
  // the simulation begins: a scan line converts the bronze into the cutaway; correct human scale
  const lt = t - EV.slam2, k = ease.out3(inv(0, 0.6, lt));
  const sc = lerp(1.3, 1.05, ease.io2(inv(0, 2.2, lt))), bx = 560, by = 1640;
  const L = cvs('b01'), g = L.getContext('2d');
  exteriorBase(g, t, { x: lt * 8, s: 1.2, hz: 1400, bx, by, sc });
  bullCutaway3(g, bx, by, sc, t, { open: k, heat: 0.6, pose: lieP(poseAt(t, [[EV.slam2, 'lie'], [19.0, 'liePress']]), t, { tremble: 0.4 }), eyeGlow: 0.3 });
  ctx.drawImage(L, 0, 0);
  // simulation grid overlay (cool, technical) reveals the shift from history to science
  ctx.save(); ctx.globalAlpha = 0.18 * k; ctx.strokeStyle = '#7fd6ff'; ctx.lineWidth = 1; for (let x = 40; x < W; x += 80) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); } for (let y = 40; y < H; y += 80) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); } ctx.restore();
  const sy = lerp(-50, H + 50, ease.io3(inv(0, 0.42, lt)));
  if (lt < 0.45) { ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.fillStyle = 'rgba(200,240,255,0.95)'; ctx.fillRect(0, sy - 2, W, 4); ctx.filter = 'blur(12px)'; ctx.fillRect(0, sy - 20, W, 40); ctx.restore(); }
}
// confusion & weakness: his hands slip from the bronze, then his eyes lose focus (subjective)
function b09(ctx, t) {
  const lt = t - BAR * 18;
  if (lt < 0.95) {
    const L = LIE(940, 1880, 1.0);
    const pose = lieP(poseAt(t, [[BAR * 18, 'liePress'], [BAR * 18 + 0.9, 'lie', ease.in2]]), t, { tremble: 1.0, breath: 2, rate: 4.4 });
    pose.face = { brow: 0.6, mouth: 0.5, sweat: 1, blink: 0.4 };
    const B2 = cvs('b09'), g = B2.getContext('2d'); shellTight(g, t, L, { heat: 0.85, seamX: 300 }); drawLying(g, pose, t, L, { heat: 0.85 });
    const dv = 14 + 12 * Math.sin(t * 3);
    ctx.save(); ctx.filter = `blur(${1 + 2 * Math.abs(Math.sin(t * 2))}px)`; ctx.drawImage(B2, 0, 0); ctx.globalAlpha = 0.35; ctx.globalCompositeOperation = 'screen'; ctx.drawImage(B2, dv, 0); ctx.restore();
  } else {
    const Lc = cvs('b09f'), g = Lc.getContext('2d'); g.fillStyle = '#080403'; g.fillRect(0, 0, W, H); glow(g, 540, 1600, 800, '#ff5a1a', 0.4);
    faceLying(g, t, 620, 980, 2.4, { blink: 0.35 + 0.2 * Math.sin(t * 3), look: [Math.sin(t * 5) * 0.5, 0.2], brow: 0.5, mouth: 0.3, sweat: 1, t }, { heat: 0.7, key: 0.5 });
    const f = Math.abs(Math.sin(t * 2.2));
    ctx.save(); ctx.filter = `blur(${2 + 6 * f}px)`; ctx.drawImage(Lc, 0, 0); ctx.globalAlpha = 0.4; ctx.drawImage(Lc, 30 * f, 0); ctx.restore();
  }
  // freeze on the musical break (33.09-33.53)
  if (t >= EV.slam3) { const k = inv(EV.slam3, EV.slam3 + 0.15, t); ctx.save(); ctx.globalCompositeOperation = 'saturation'; ctx.globalAlpha = 0.9 * k; ctx.fillStyle = '#808080'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
}
function b10(ctx, t) { // profile breathing with subjective focus pulls
  const L = cvs('b10'); SH(w19, BAR * 20, EV.scan3)(L.getContext('2d'), t);
  const f = Math.abs(Math.sin((t - EV.scan3) * 2.4)); ctx.save(); ctx.filter = `blur(${f * 5}px)`; ctx.drawImage(L, 0, 0); ctx.restore();
}

// ================================================================== ACT III — THE INVENTOR'S FATE
// 47.65-49.41: sudden return: the palace courtyard in golden light; Perillus by his bull, Phalaris arrives with guards
function c01(ctx, t) {
  const lt = t - EV.drop2, k = ease.io2(inv(0, 1.76, lt));
  const L = cvs('c01'), g = L.getContext('2d');
  courtyardGold(g, t, { x: lerp(-40, 30, k), y: 0, s: 1.15, hz: 1330, bullX: 520, bullY: 1500, bullS: 0.78 });
  ctx.drawImage(L, 0, 0);
  const pp = secondary(cast('perillus', 'proud'), t, { breath: 0.7 }); pp.face = { look: [0.4, 0], brow: 0, mouth: 0.3 };
  drawChar(ctx, 'perillus', pp, t, [lerp(300, 290, k), 1060, 0.4], { flip: true, key: 0.95, rimCol: '#ffd8a0' });
  const walkX = lerp(1080, 820, ease.out2(inv(0, 1.6, lt))), ph = Math.sin(lt * 7);
  const fp = secondary(cast('phalaris', 'stand'), t, { breath: 0.5 }); fp.nF = [60 + ph * 120, G]; fp.fF = [-150 - ph * 120, G]; fp.face = { look: [-0.5, 0], brow: 0.3 };
  for (const [dx, sc] of [[150, 0.38], [260, 0.38]]) drawChar(ctx, 'guard', secondary(cast('guard', 'guardStand'), t + dx, { breath: 0.4 }), t, [walkX + dx, 1040, sc], { key: 0.8 });
  drawChar(ctx, 'phalaris', fp, t, [walkX, 1060, 0.42], { key: 0.95, rimCol: '#ffd8a0', lag: ph * 0.4 });
}
// 49.41-50.96: two-shot — Phalaris turns his gaze to the proud inventor
function c02(ctx, t) {
  const lt = t - BAR * 28, turn = ease.io3(inv(0.3, 1.0, lt));
  const L = cvs('c02'), g = L.getContext('2d');
  courtyardGold(g, t, { x: 120, y: 0, s: 1.4, hz: 1500, bullX: 1500, bullY: 1700, bullS: 1.0 }); ctx.drawImage(L, 0, 0);
  headChar(ctx, 'perillus', { look: [0.3, 0], brow: 0, mouth: 0.25, t }, t, 300, 1180, 0.95, { flip: true, rimCol: '#ffd8a0' });
  headChar(ctx, 'phalaris', { look: [lerp(-0.3, 0.6, turn), 0], brow: 0.35, mouth: 0.05, t }, t, 820, 1080, 1.0, { flip: turn > 0.5, rimCol: '#ffb070' });
}
// 50.96-52.06: Phalaris close — cold, silent; his hand rises to point
function c03(ctx, t) {
  const lt = t - EV.wail6, k = ease.io3(inv(0.1, 0.9, lt));
  const L = cvs('c03'), g = L.getContext('2d'); courtyardGold(g, t, { x: -200, y: 0, s: 1.6, hz: 1600, bullX: -2000, bullY: 1700, bullS: 1 });
  ctx.save(); ctx.filter = 'blur(10px)'; ctx.drawImage(L, 0, 0); ctx.restore();
  const p = secondary(cast('phalaris', blendPose('stand', 'standPoint', k)), t, { breath: 0.4 }); p.face = { look: [-0.7, 0], brow: 0.55, mouth: 0.02 };
  drawChar(ctx, 'phalaris', p, t, [660, 980, 0.95], { key: 0.9, rimCol: '#ffb070' });
}
// 52.06-52.94: guards step in on either side of Perillus
function c04(ctx, t) {
  const lt = t - 52.06, k = ease.out3(inv(0, 0.5, lt));
  const L = cvs('c04'), g = L.getContext('2d'); courtyardGold(g, t, { x: 60, y: 0, s: 1.3, hz: 1450, bullX: -2000, bullY: 1700, bullS: 1 }); ctx.drawImage(L, 0, 0);
  const pp = secondary(cast('perillus', 'proud'), t, { breath: 1.2 }); pp.face = { look: [0.4, 0], brow: 0.6, mouth: 0.2 };
  drawChar(ctx, 'perillus', pp, t, [540, 840, 0.58], { key: 0.9 });
  drawChar(ctx, 'guard', secondary(cast('guard', 'guardStep'), t, { breath: 0.5 }), t, [lerp(-80, 200, k), 860, 0.62], { key: 0.8 });
  drawChar(ctx, 'guard', secondary(cast('guard', 'guardStep'), t + 3, { breath: 0.5 }), t, [lerp(1160, 880, k), 860, 0.62], { flip: true, key: 0.8 });
}
// 52.94-53.82: Perillus close — the smile collapses into fear
function c05(ctx, t) {
  const lt = t - 52.94, k = ease.io3(inv(0.05, 0.6, lt));
  ctx.fillStyle = '#140a06'; ctx.fillRect(0, 0, W, H); glow(ctx, 300, 600, 900, '#ffb070', 0.35);
  headChar(ctx, 'perillus', { look: [lerp(0.3, -0.2, k), lerp(0, -0.3, k)], brow: lerp(0.0, 1.0, k), mouth: lerp(0.25, 0.7, k), sweat: 0.4 * k, t }, t, 600 + k * 20, 1000, 1.7, { key: lerp(0.95, 0.7, k) });
}
// 53.82-54.71: the bull's silhouette towers in red light; their long shadows
function c06(ctx, t) {
  const lt = t - 53.82;
  ctx.fillStyle = linGrad(ctx, 0, 0, 0, H, [[0, '#3a0a06'], [1, '#0a0302']]); ctx.fillRect(0, 0, W, H);
  glow(ctx, 540, 1500, 900, '#ff3a10', 0.6);
  const L = cvs('c06'), g = L.getContext('2d'); g.save(); g.translate(560, 1520); g.scale(1.15 + lt * 0.05, 1.15 + lt * 0.05); bullBronze(g, { glow: 0, t, eyeGlow: 1 }); g.restore();
  g.globalCompositeOperation = 'source-in'; g.fillStyle = '#070202'; g.fillRect(0, 0, W, H);
  ctx.drawImage(L, 0, 0);
  glow(ctx, 560 - 470 * 1.15, 1520 - 372 * 1.15, 90, '#ff6a2a', 1);
  ctx.save(); ctx.globalAlpha = 0.85; ctx.fillStyle = '#050101';
  for (const [x, w] of [[300, 60], [560, 70], [820, 60]]) { ctx.beginPath(); ctx.moveTo(x - w / 2, H); ctx.lineTo(x + w / 2, H); ctx.lineTo(x + w * 0.3 + (x - 540) * 0.4, 1600); ctx.lineTo(x - w * 0.3 + (x - 540) * 0.4, 1600); ctx.closePath(); ctx.fill(); }
  ctx.restore();
}
// 54.71-56.47: THE INVENTOR HIMSELF — his face turns to bronze; within the bull's outline, his reclined silhouette (symbolic)
function c07(ctx, t) {
  const lt = t - EV.scan4, k = ease.io3(inv(0.0, 1.3, lt));
  ctx.fillStyle = '#080303'; ctx.fillRect(0, 0, W, H);
  // his face above, turning into bronze
  const pal = { lit: Object.assign({}, PAL.perillus.lit), shadow: PAL.perillus.shadow };
  for (const key of ['skin', 'skin2', 'skinLt', 'hair', 'beard', 'cloth']) pal.lit[key] = mix(pal.lit[key], key === 'skinLt' ? '#ffd890' : '#8a5a2a', k);
  litRender(ctx, (g, C) => { g.save(); g.translate(560, 380); g.scale(0.8, 0.8); bust34(g, C, {}); head34(g, C, { t, spec: SPEC.perillus, look: [0, -0.2], brow: 0.9, mouth: 0.5, blink: k * 0.6 }); g.restore(); },
    (m) => radialMask(m, 300, 200, 40, 700, 0.95), { lit: pal.lit, shadow: pal.shadow, rim: { dx: 6, dy: 0, col: '#ffb060', a: 0.9 } });
  ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.fillStyle = linGrad(ctx, 0, 300, 0, 900, [[0, '#ffffff'], [1, '#2a1006']]); ctx.globalAlpha = 0.5; ctx.fillRect(0, 300, W, 600); ctx.restore();
  ctx.fillStyle = linGrad(ctx, 0, 820, 0, 1000, [[0, 'rgba(8,3,3,0)'], [1, '#080303']]); ctx.fillRect(0, 820, W, 1100);
  // bull outline with his silhouette inside, at true scale
  const bx = 560, by = 1500, sc = 1.0;
  ctx.save(); ctx.globalAlpha = k; ctx.translate(bx, by); ctx.scale(sc, sc); ctx.strokeStyle = '#ffb060'; ctx.lineWidth = 4; ctx.beginPath(); crPath(ctx, BULL.body, true); ctx.stroke();
  ctx.filter = 'blur(10px)'; ctx.lineWidth = 16; ctx.strokeStyle = 'rgba(255,120,40,0.5)'; ctx.stroke(); ctx.restore();
  if (k > 0.2) { const Ls = LIE(bx - 20 * sc, by - 335 * sc, 0.285 * sc); const { S } = silL('c07s', lieP('lieCurl', t, { breath: 0.4 }), t, Ls);
    const D = cvs('c07d'), dg = D.getContext('2d'); dg.drawImage(S, 0, 0); dg.globalCompositeOperation = 'source-in'; dg.fillStyle = '#ff9a4a'; dg.fillRect(0, 0, W, H);
    ctx.save(); ctx.globalAlpha = inv(0.2, 0.6, k) * 0.5; ctx.filter = 'blur(4px)'; ctx.drawImage(D, 0, 0); ctx.restore(); }
}
// 56.47-58.10: final exterior: the most beautiful composition — moonlit, ember-lit bronze, roar on the climax
function c08(ctx, t) {
  const lt = t - EV.bar32, roar = inv(EV.roarClimax - 0.05, EV.roarClimax + 0.1, t), mv = ease.io2(inv(0, 1.63, lt));
  const sc = lerp(1.0, 1.06, mv), bx = lerp(600, 570, mv), by = 1640;
  const L = cvs('c08'), g = L.getContext('2d');
  courtyard(g, { x: lerp(100, -60, mv), y: 0, s: 1.3, hz: 1460, bullX: -9999, bullY: by, bullS: sc }, t, { fire: 1 });
  glow(g, 840, 520, 260, '#f0e0c0', 0.35); g.fillStyle = '#efe3c8'; g.beginPath(); g.arc(840, 520, 62, 0, 6.283); g.fill();
  g.save(); g.translate(bx, by); g.scale(sc, sc); plinth(g); g.restore();
  glow(g, bx, by, 720 * sc, '#ff6a1a', 0.45 + roar * 0.35);
  bullLayer(g, bx, by, sc, { glow: 1 + roar * 0.6, t, eyeGlow: 0.35 + roar * 1.2 });
  ctx.drawImage(L, 0, 0);
  const r = mulberry(19);
  for (let i = 0; i < 120; i++) { const ph = r(), sp = 0.4 + r() * 0.6, u = ((lt * sp + ph) % 1); const x = bx + lerp(-300, 250, r()) * sc + Math.sin(u * 5 + i) * 60 + u * 160, y = by - 600 * sc - u * 1300;
    ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.globalAlpha = Math.sin(Math.PI * u) * (0.55 + roar * 0.45); ctx.fillStyle = '#ffb060'; ctx.beginPath(); ctx.arc(x, y, 1.6 + r() * 2.6, 0, 6.283); ctx.fill(); ctx.restore(); }
  if (roar > 0) { const hx = bx - 470 * sc, hy = by - 372 * sc, u = inv(EV.roarClimax, EV.roarClimax + 0.45, t); glow(ctx, hx, hy, 600 * roar, '#ff7a2a', 0.55 * roar);
    ctx.save(); ctx.strokeStyle = rgba('#ffc890', 0.7 * (1 - u)); ctx.lineWidth = 8 * (1 - u) + 1; ctx.beginPath(); ctx.arc(hx, hy, 60 + u * 800, 0, 6.283); ctx.stroke(); ctx.restore(); }
  ctx.save(); ctx.filter = 'blur(16px)'; column(ctx, lerp(40, -40, mv), 2300, 260, 2800, 0.3); ctx.restore();
}
// 58.24-60.0: back to the bull's face in darkness — the very first frame (loop)
function c09(ctx, t) { const lt = t - EV.final; bullFace(ctx, t, lerp(1, 0.15, ease.io2(inv(0.2, 1.76, lt)))); }

const SHOTS4 = [
  [a01, 0, EV.slam1], [a02, EV.slam1, BAR * 3], [a03, BAR * 3, 7.06], [a04, 7.06, BAR * 5], [a05, BAR * 5, EV.scan1], [a06, EV.scan1, BAR * 7],
  [a07, BAR * 7, BAR * 7 + 0.882], [a08, BAR * 7 + 0.882, EV.fire1], [a09, EV.fire1, BAR * 9], [a10, BAR * 9, EV.slam2],
  [b01, EV.slam2, BAR * 11], [SH(w04, 7.06, BAR * 11), BAR * 11, BAR * 12], [SH(w06, EV.scan1, BAR * 12), BAR * 12, BAR * 13], [SH(w08, EV.fire1, BAR * 13), BAR * 13, EV.predrop],
  [SH(w10, EV.slam2, EV.predrop), EV.predrop, EV.drop1], [SH(w11, EV.slam2, EV.drop1), EV.drop1, BAR * 16], [SH(w12, EV.shriek1, BAR * 16), BAR * 16, 30.0],
  [SH(w07, BAR * 7, 30.0), 30.0, BAR * 18], [b09, BAR * 18, EV.scan3], [b10, EV.scan3, BAR * 20], [SH(w18, EV.scan3, BAR * 20), BAR * 20, EV.clank],
  [w20, EV.clank, EV.slam4], [w21, EV.slam4, BAR * 24], [SH(w15, EV.drop1, BAR * 24), BAR * 24, EV.wail5], [w23, EV.wail5, 45.0],
  [SH(w27, EV.wail6, 45.0), 45.0, 46.3], [SH(w31, EV.scan4, 46.3), 46.3, EV.drop2],
  [c01, EV.drop2, BAR * 28], [c02, BAR * 28, EV.wail6], [c03, EV.wail6, 52.06], [c04, 52.06, 52.94], [c05, 52.94, 53.82], [c06, 53.82, EV.scan4],
  [c07, EV.scan4, EV.bar32], [c08, EV.bar32, EV.final], [c09, EV.final, 60.01],
];
