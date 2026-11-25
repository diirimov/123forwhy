// SHOTS: every shot is a pure function of time (local lt, global t) -> deterministic, parallel-renderable.
'use strict';

// ------------------------------------------------------------------ audio-locked events (from BRAZEN_BULL_BEATMAP_V3.json)
const EV = {
  vo: 0.45, w_the: 0.55, w_brazen: 0.78, w_bull: 1.38, w_sim: 1.84, vo_end: 2.53,
  whoosh0: 2.647, slam1: 3.5294, wail1: 6.838, scan1: 10.588, wail2: 13.897, fire1: 14.1176, slam2: 17.2059, brk2: 17.647,
  shriek1: 20.956, scan2: 21.176, riser: 22.941, roarRise: 24.305, predrop: 24.7059, power1: 26.029, sil1: 26.278, drop1: 26.4706,
  wail3: 29.779, slam3: 33.088, scan3: 33.529, wail4: 36.838, clank: 37.059, slam4: 40.588, wailDark: 40.809, wail5: 43.676,
  roarRev: 45.221, sil2: 47.426, drop2: 47.6471, wail6: 50.956, stutter: 51.838, scan4: 54.706, bar32: 56.4706, roarClimax: 57.794,
  sil3: 58.097, final: 58.2353,
};
const HEARTBEATS = [40.588, 41.471, 42.353, 43.235, 44.118, 44.559, 45.0, 45.441, 45.882, 46.324, 46.765, 46.985, 47.206];
let KICKS = []; // filled from beat map JSON at boot
function lastKick(t) { let k = -1e9; for (const x of KICKS) { if (x <= t) k = x; else break; } return k; }
function kickPulse(t, decay = 9) { return Math.exp(-(t - lastKick(t)) * decay); }

// ------------------------------------------------------------------ helpers
function camApply(ctx, cx, cy, s, rot = 0, px = W / 2, py = H / 2) { ctx.translate(px, py); ctx.rotate(rot); ctx.scale(s, s); ctx.translate(-cx, -cy); }
function heatShimmer(ctx, src, t, amp, y0 = 0, y1 = H, freq = 0.025, speed = 5) {
  const step = 6;
  for (let y = y0; y < y1; y += step) { const dx = Math.sin(y * freq + t * speed) * amp + Math.sin(y * freq * 2.3 - t * speed * 1.7) * amp * 0.4; ctx.drawImage(src, 0, y, W, step, dx, y, W, step); }
}
function charLayerLit(ctx, drawFn, maskFn, rim, palettes) { litRender(ctx, drawFn, maskFn, Object.assign({ rim }, palettes || {})); }
function bustProfile(g, C, s) {
  g.save(); g.translate(0, (s.breath || 0) * 6 + (s.slump || 0) * 30);
  const sh = [[-40, 230], [150, 220], [250, 300], [300, 420], [320, 700], [-200, 700], [-170, 430], [-110, 300]];
  g.fillStyle = C.cloth; g.beginPath(); crPath(g, sh, true); g.fill();
  softIn(g, sh, 20, () => { g.fillStyle = rgba(C.clothDk, 0.8); g.beginPath(); g.ellipse(200, 520, 120, 200, 0, 0, 6.283); g.fill(); });
  brush(g, curvePts([[-110, 300], [-20, 280], [90, 270]], 20), 12, 12, C.border, false);
  g.restore();
}
function nikiasMedium(g, C, s) { bust34(g, C, s); g.save(); g.translate(s.hx || 0, (s.breath || 0) * 5 + (s.slump || 0) * 40); g.rotate(s.tilt || 0); head34(g, C, s); g.restore(); }
function nikiasProfile(g, C, s) { bustProfile(g, C, s); g.save(); g.translate(0, (s.slump || 0) * 46); g.rotate(s.tilt || 0); headProfile(g, C, s); g.restore(); }
// natural blink schedule (pure function of t)
function blinkAt(t, seed = 1, extra = []) {
  const times = [0.9, 2.2, 4.1, 5.3, 7.8, 9.6, 12.1, 15.0, 18.7, 23.3, 24.1, 31.0, 35.2, 41.2, 49.5, 51.0, 52.4].concat(extra);
  let b = 0; for (const x of times) { const d = t - x; if (d > 0 && d < 0.16) b = Math.max(b, Math.sin(d / 0.16 * Math.PI)); }
  return b;
}
function lightBand(m, y, h, a = 1, feather = 0.5) {
  m.fillStyle = linGrad(m, 0, y - h, 0, y + h, [[0, 'rgba(255,255,255,0)'], [feather * 0.5, rgba('#ffffff', a * 0.6)], [0.5, rgba('#ffffff', a)], [1 - feather * 0.5, rgba('#ffffff', a * 0.6)], [1, 'rgba(255,255,255,0)']]);
  m.fillRect(0, y - h, W, 2 * h);
}
function radialMask(m, x, y, r0, r1, a = 1) { m.fillStyle = radGrad(m, x, y, r0, r1, [[0, rgba('#ffffff', a)], [1, 'rgba(255,255,255,0)']]); m.fillRect(0, 0, W, H); }
// warm-shifted palettes for the heat progression
function warmPal(k) {
  const L = Object.assign({}, SKIN_LIT);
  L.skin = mix(SKIN_LIT.skin, '#d8805a', k * 0.6); L.skinLt = mix(SKIN_LIT.skinLt, '#ffb48a', k * 0.6); L.skin2 = mix(SKIN_LIT.skin2, '#b4583a', k * 0.5);
  L.cloth = mix(SKIN_LIT.cloth, '#e8b890', k * 0.5);
  const S = Object.assign({}, SKIN_SHD); S.skin = mix(SKIN_SHD.skin, '#4a1a10', k * 0.6); S.skin2 = mix(SKIN_SHD.skin2, '#3a120a', k * 0.5);
  return { lit: L, shadow: S };
}
function label(ctx, x, y, x2, y2, text, col = '#cfe8ff', a = 1) {
  if (a <= 0) return;
  ctx.save(); ctx.globalAlpha = a; ctx.strokeStyle = rgba(col, 0.8); ctx.lineWidth = 2;
  ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x2, y2); ctx.lineTo(x2 + (x2 > x ? 40 : -40), y2); ctx.stroke();
  ctx.fillStyle = col; ctx.beginPath(); ctx.arc(x, y, 5, 0, 6.283); ctx.fill();
  ctx.font = '700 26px Inter'; ctx.textAlign = x2 > x ? 'left' : 'right'; ctx.textBaseline = 'middle';
  ctx.fillText(text, x2 + (x2 > x ? 50 : -50), y2); ctx.restore();
}

// ================================================================== SHOT 01 — hook: eyes in the light streak -> pull back to the bull
function s01(ctx, t) {
  const pull = ease.in3(inv(EV.whoosh0, EV.slam1 - 0.02, t));             // 0..1 camera pull-back
  const faceA = 1 - inv(2.95, 3.35, t);
  if (faceA > 0) {
    bronzeInterior(ctx, t, { oy: -t * 20 });
    const sc = lerp(3.6, 3.95, ease.out2(inv(0, 2.6, t))) * lerp(1, 0.3, pull);
    const eyesOpen = inv(0.04, 0.16, t);
    const st = { blink: Math.max(1 - eyesOpen, blinkAt(t, 1, [2.3])), look: [lerp(0.15, -0.45, ease.io3(inv(1.3, 1.6, t))), 0.05], brow: 0.35 + 0.35 * inv(1.3, 1.6, t), sweat: 0.55, t, mouth: 0.15 };
    const bandY = lerp(1135, 1115, inv(0, 2.6, t));
    const draw = (g, C) => { g.save(); g.translate(600, bandY + 20 * sc - pull * 300); g.scale(sc, sc); g.translate(-10, 20); nikiasMedium(g, C, Object.assign({ breath: Math.sin(t * 2.4) * 0.5 }, st)); g.restore(); };
    const DEEP = Object.assign({}, SKIN_SHD, { skin: '#1e100b', skin2: '#170c08', skinLt: '#2a160e', hair: '#070504', beard: '#080504', cloth: '#1a1510', eyeW: '#2a2018' });
    const mask = (m) => { lightBand(m, bandY, 95 + 40 * pull, 1, 0.75); radialMask(m, 260, bandY, 0, 420, 0.25); };
    ctx.save(); ctx.globalAlpha = faceA; litRender(ctx, draw, mask, { rim: { dx: 6, dy: 0, col: '#ff9a4a', a: 0.6 }, shadow: DEEP }); ctx.restore();
    // the streak itself (volumetric light leaking through a seam)
    ctx.save(); ctx.globalAlpha = faceA; shaft(ctx, -100, bandY, 40, W + 100, bandY, 160, '#ffb466', 0.35); ctx.restore();
    motes(ctx, t, 70, 4, { y0: bandY - 90, y1: bandY + 90, vy: -6, vx: 22, size: [0.8, 2.6], col: '#ffd6a0', a: 0.9 * faceA, life: 5 });
  }
  if (t > 2.9) {
    // match cut: the streak becomes the glowing seam on the bull's flank in the courtyard
    const k = ease.out3(inv(2.9, 3.4, t));
    ctx.save(); ctx.globalAlpha = k;
    const s = lerp(1.6, 0.92, ease.out2(inv(2.9, EV.slam1, t)));
    ctx.translate(W / 2, 1115); ctx.scale(s, s); ctx.translate(-W / 2, -1115);
    courtyard(ctx, { x: 0, y: 0, s: 1.1, hz: 1260, bullX: 600, bullY: 1420, bullS: 0.92 }, t, { fire: 1, eyeGlow: 0.25 });
    shaft(ctx, 150, 1115, 6, 1050, 1115, 10, '#ffd08a', 0.9);
    ctx.restore();
  }
}

// ================================================================== SHOT 02 — low-angle bull, ancient courtyard
function s02(ctx, t) {
  const lt = t - EV.slam1;
  const crane = ease.io3(inv(0, 3.4, lt));
  const torch = 0.8 + 0.2 * Math.sin(t * 11) * Math.sin(t * 7.3);
  const L = cvs('s02');
  const g = L.getContext('2d');
  courtyard(g, { x: lerp(-60, 60, crane), y: 0, s: 1.55, hz: lerp(1680, 1640, crane), bullX: lerp(790, 760, crane), bullY: lerp(1700, 1680, crane), bullS: lerp(1.24, 1.3, crane) }, t, { fire: torch * (1 + kickPulse(t) * 0.15), eyeGlow: 0.2 + 0.5 * inv(EV.wail1 - 0.2, EV.wail1 + 0.2, t) });
  ctx.drawImage(L, 0, 0);
  // moving torch shadows sweeping across the floor
  ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.globalAlpha = 0.45;
  ctx.fillStyle = linGrad(ctx, 0, 0, W, 0, [[0, '#000'], [0.5 + 0.12 * Math.sin(t * 1.7), '#fff'], [1, '#000']]); ctx.fillRect(0, 1500, W, 420); ctx.restore();
  // foreground occlusion: out-of-focus column + brazier flame at the left edge
  ctx.save(); ctx.filter = 'blur(12px)'; ctx.globalAlpha = 0.85; column(ctx, lerp(-20, -90, crane), 2100, 200, 2600, 0.55); ctx.restore();
  glow(ctx, lerp(150, 60, crane), 1700, 260 * torch, '#ff8a3a', 0.45);
  motes(ctx, t, 50, 21, { x0: 0, x1: 320, y0: 1500, y1: 1800, vy: -160, vx: 30, size: [1.2, 3.5], col: '#ffb060', a: 0.9, life: 2.4 });
}

// ================================================================== SHOT 03 — extreme heat: Nikias in an abstract furnace of light
function s03(ctx, t) {
  const lt = t - 7.06, k = inv(0, 3.5, lt);
  const B = cvs('s03bg'), g = B.getContext('2d');
  g.fillStyle = radGrad(g, 540, 1300, 50, 1400, [[0, mix('#5a2410', '#b8501a', k)], [0.5, mix('#2a120a', '#5a1e0c', k)], [1, '#0a0504']]); g.fillRect(0, 0, W, H);
  // bronze ribs curving around him (abstract interior)
  for (let i = 0; i < 7; i++) { g.save(); g.strokeStyle = rgba('#e8a050', 0.05 + 0.03 * k); g.lineWidth = 40 + i * 8; g.filter = 'blur(14px)';
    g.beginPath(); g.ellipse(540, 900, 520 + i * 120, 820 + i * 90, Math.sin(t * 0.2) * 0.05, 0, 6.283); g.stroke(); g.restore(); }
  glow(g, 540, 1750, 900, '#ff6a1a', 0.35 + 0.35 * k);
  ctx.drawImage(B, 0, 0); ctx.save(); ctx.globalAlpha = 0.9; heatShimmer(ctx, B, t, 3 + 6 * k); ctx.restore();
  // character
  const push = lerp(1.02, 1.12, ease.io2(k));
  const st = { blink: blinkAt(t), look: [-0.2 + 0.25 * Math.sin(lt * 0.9), 0.05 + 0.1 * k], brow: 0.3 + 0.5 * k, sweat: 0.5 + 0.5 * k, t, mouth: 0.2 + 0.35 * k * (0.5 + 0.5 * Math.sin(t * 2.6)), breath: Math.sin(t * 2.8) * (0.6 + 0.4 * k), hx: Math.sin(lt * 0.7) * 6, tilt: -0.03 + Math.sin(lt * 0.6) * 0.02 };
  const pal = warmPal(k);
  const outPush = ease.in3(inv(EV.scan1 - 0.45, EV.scan1, t));
  const draw = (g2, C) => { g2.save(); camApply(g2, 540, 1000, push * lerp(1, 2.6, outPush), 0, 560 - outPush * 120, 1050); g2.translate(540, 900); g2.scale(1.15, 1.15); nikiasMedium(g2, C, st); g2.restore(); };
  litRender(ctx, draw, (m) => { radialMask(m, 260, 900, 50, 900, 0.95); lightBand(m, 1500, 500, 0.5 * k); }, Object.assign({ rim: { dx: -8, dy: 0, col: '#ffb070', a: 0.9 } }, pal));
  // heat haze over everything near the bottom
  motes(ctx, t, 80, 31, { y0: 1100, y1: 1920, vy: -220, vx: 20, size: [1, 3], col: '#ffb060', a: 0.7 * k + 0.2, life: 2.2 });
  ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.globalAlpha = 0.18 * k; ctx.fillStyle = '#ff7a2a'; ctx.fillRect(0, 0, W, H); ctx.restore();
}

// ================================================================== SHOT 04 — skin cross-section: the cooling response
function s04(ctx, t) {
  const lt = t - EV.scan1;
  anatomyField(ctx, t, { warm: 0.25 });
  const pull = ease.out3(inv(0, 1.4, lt));
  const dive = ease.in3(inv(EV.wail2 + 0.05, EV.fire1, t));
  const s = lerp(2.3, 0.98, pull) * lerp(1, 3.6, dive);
  ctx.save(); camApply(ctx, lerp(-60, 0, pull) + dive * (-440 + 80 + 145 * 2), lerp(-250, 40, pull) + dive * -110, s, lerp(-0.04, 0, pull), W / 2, 980);
  skinBlock(ctx, t, { sweat: 0.3 + 0.7 * inv(0.3, 1.6, lt), dilate: 0.25, flush: 0.2 });
  ctx.restore();
  // heat leaving the surface as soft rising waves
  ctx.save(); ctx.globalCompositeOperation = 'screen';
  for (let i = 0; i < 6; i++) { const x = 140 + i * 160; const pts = []; for (let y = 0; y < 300; y += 10) pts.push([x + Math.sin(y * 0.04 + t * 3 + i) * 14, 700 - y - ((t * 60) % 40)]);
    ctx.strokeStyle = rgba('#ffb07a', 0.25 * pull * (1 - dive)); ctx.lineWidth = 3; ctx.beginPath(); crPath(ctx, pts, false); ctx.stroke(); }
  ctx.restore();
  const la = env(lt, 0.9, 3.2, 0.3, 0.3) * (1 - dive);
  label(ctx, 470, 1060, 300, 880, 'SWEAT', '#bfe8ff', la);
  label(ctx, 640, 1290, 560, 1180, 'SWEAT GLAND', '#bfe8ff', la);
}

// ================================================================== SHOT 05 — blood vessels widen (vasodilation)
function s05(ctx, t) {
  const lt = t - EV.fire1;
  anatomyField(ctx, t, { warm: 0.45 });
  const open = ease.outBack(clamp(inv(0.15, 1.3, lt)), 1.2);
  const d = lerp(90, 190, open) * (1 + kickPulse(t, 7) * 0.05);
  // skin surface above with heat radiating out
  ctx.save(); ctx.fillStyle = linGrad(ctx, 0, 560, 0, 760, [[0, '#f0c0a0'], [1, mix('#c86a5a', '#e0503a', open)]]); ctx.fillRect(0, 560, W, 200);
  ctx.globalCompositeOperation = 'screen';
  for (let i = 0; i < 9; i++) { const x = 60 + i * 120; const pts = []; for (let y = 0; y < 380; y += 12) pts.push([x + Math.sin(y * 0.035 + t * 3.2 + i) * 16, 560 - y - ((t * 90) % 60)]);
    ctx.strokeStyle = rgba('#ff9a5a', 0.15 + 0.35 * open); ctx.lineWidth = 4; ctx.beginPath(); crPath(ctx, pts, false); ctx.stroke(); }
  ctx.restore();
  // the vessel (slight perspective drift)
  ctx.save(); ctx.translate(W / 2 + Math.sin(lt * 0.6) * 20, 1150); ctx.rotate(-0.12 + lt * 0.01); ctx.scale(1.05 + lt * 0.03, 1.05 + lt * 0.03);
  // ghost outline of the narrow vessel for comparison
  ctx.save(); ctx.setLineDash([16, 14]); ctx.strokeStyle = rgba('#cfe8ff', 0.55 * open); ctx.lineWidth = 3;
  ctx.strokeRect(-800, -45 - 24, 1600, 138); ctx.restore();
  vessel(ctx, t, { diam: d, len: 1700, speed: 1 + open * 0.8 });
  ctx.restore();
  // arrows showing widening
  const a = env(lt, 0.6, 3.0, 0.2, 0.3);
  ctx.save(); ctx.globalAlpha = a; ctx.strokeStyle = '#ffd6a0'; ctx.fillStyle = '#ffd6a0'; ctx.lineWidth = 5;
  for (const sy of [-1, 1]) { const y0 = 1150 + sy * (d / 2 + 70), y1 = y0 + sy * 60; ctx.beginPath(); ctx.moveTo(540, y0); ctx.lineTo(540, y1); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(540 - 16, y1 - sy * 18); ctx.lineTo(540, y1 + sy * 6); ctx.lineTo(540 + 16, y1 - sy * 18); ctx.fill(); }
  ctx.restore();
  label(ctx, 700, 700, 620, 560, 'HEAT RELEASED', '#ffc89a', env(lt, 1.0, 3.0, 0.3, 0.3));
}

// ================================================================== SHOT 06 — the heart works harder
function s06(ctx, t) {
  const lt = t - EV.slam2;
  anatomyField(ctx, t, { warm: 0.15 });
  // beats: quick double-pulse; cadence speeds up over the shot (visual, not tied to BPM)
  const per = lerp(0.95, 0.6, inv(0, 3.5, lt));
  const ph = (lt % per) / per;
  const beat = Math.max(0, Math.exp(-ph * 14) * 1.0 + Math.exp(-Math.max(0, ph - 0.16) * 14) * (ph > 0.16 ? 0.6 : 0));
  const enter = ease.out3(inv(0, 0.45, lt));
  ctx.save(); ctx.translate(W / 2, 1010); ctx.rotate(Math.sin(lt * 0.5) * 0.03); const s = lerp(0.6, 1.55, enter) + lt * 0.02; ctx.scale(s, s);
  // flow streams in the great vessels
  ctx.save(); ctx.globalCompositeOperation = 'screen';
  for (let i = 0; i < 18; i++) { const u = ((lt * 0.9 + i / 18) % 1); const P = curvePts([[-10, -130], [-20, -260], [40, -360], [150, -330], [186, -230]], 30); const [x, y] = P[Math.floor(u * (P.length - 1))]; glow(ctx, x, y, 22, '#ff8a7a', 0.7); }
  for (let i = 0; i < 12; i++) { const u = ((lt * 0.8 + i / 12) % 1); const y = lerp(-340, -180, u); glow(ctx, -123, y, 18, '#8ab8ff', 0.7); }
  ctx.restore();
  heartAnt(ctx, { beat, stress: 0.25 * inv(0, 3.6, lt), t });
  ctx.restore();
  glow(ctx, W / 2, 1060, 600, '#ff3a2a', 0.18 * beat);
  // pressure rings
  for (let r = 0; r < 3; r++) { const u = ((lt / per) + r / 3) % 1; ctx.save(); ctx.strokeStyle = rgba('#ff8a7a', 0.25 * (1 - u)); ctx.lineWidth = 3; ctx.beginPath(); ctx.ellipse(W / 2, 1060, 300 + u * 380, 360 + u * 420, 0, 0, 6.283); ctx.stroke(); ctx.restore(); }
}

// ================================================================== SHOT 07 — water and salts are lost
function s07(ctx, t) {
  const lt = t - EV.shriek1;
  anatomyField(ctx, t, { warm: 0.1 });
  const drain = ease.io2(inv(0.2, 1.9, lt));
  ctx.save(); ctx.translate(W / 2, 1040); const s = 0.98 + lt * 0.04; ctx.scale(s, s);
  // torso-scale body with water level inside
  ctx.save(); ctx.beginPath(); crPath(ctx, BODY, true, 0.45); ctx.clip();
  const lvl = lerp(-620, -40, drain);
  ctx.fillStyle = linGrad(ctx, 0, lvl, 0, 760, [[0, rgba('#5ac8ff', 0.55)], [1, rgba('#1a6aa0', 0.5)]]); ctx.fillRect(-400, lvl, 800, 1400);
  ctx.strokeStyle = rgba('#cfefff', 0.9); ctx.lineWidth = 4; ctx.beginPath();
  for (let x = -300; x <= 300; x += 10) ctx.lineTo(x, lvl + Math.sin(x * 0.04 + t * 5) * 6); ctx.stroke();
  ctx.restore();
  bodySil(ctx, { t, edge: '#7fd6ff' });
  ctx.restore();
  // droplets + ions escaping through the skin
  const r = mulberry(55);
  ctx.save();
  for (let i = 0; i < 46; i++) {
    const side = r() < 0.5 ? -1 : 1, y0 = lerp(400, 1500, r()), ph = r(), sp = 0.6 + r() * 0.6;
    const u = ((lt * sp + ph) % 1.2); if (u > 1) continue;
    const x = W / 2 + side * (200 + ease.out2(u) * 420), y = y0 - u * 120;
    const a = Math.sin(Math.PI * u) * inv(0, 0.4, lt);
    if (i % 3 === 0) {
      ctx.globalAlpha = a; ctx.fillStyle = '#ffd27a'; ctx.font = '800 30px Inter'; ctx.textAlign = 'center';
      ctx.fillText(['Na⁺', 'K⁺', 'Cl⁻'][i % 9 === 0 ? 0 : i % 2 ? 1 : 2], x, y); glow(ctx, x, y - 10, 30, '#ffd27a', 0.5 * a);
    } else { ctx.globalAlpha = a; ctx.fillStyle = '#9fdcff'; ctx.beginPath(); ctx.ellipse(x, y, 8, 11, 0, 0, 6.283); ctx.fill(); ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(x - 3, y - 4, 2.5, 0, 6.283); ctx.fill(); }
  }
  ctx.restore();
  label(ctx, 720, 900, 640, 760, 'ELECTROLYTES', '#ffd27a', env(lt, 0.5, 2.0, 0.25, 0.2));
}

// ================================================================== SHOT 08 — weakness: Nikias slumps against the bronze
function s08(ctx, t) {
  const lt = t - EV.riser;
  const k = inv(0, 1.7, lt);
  // background: bronze wall, very warm
  bronzeInterior(ctx, t, { oy: 40 });
  glow(ctx, 540, 1900, 1100, '#ff5a1a', 0.45);
  // the curved bronze wall he leans on (right side), the hand pressed flat against it
  ctx.save(); ctx.beginPath(); ctx.moveTo(760, 0); ctx.quadraticCurveTo(700, 960, 780, H); ctx.lineTo(W, H); ctx.lineTo(W, 0); ctx.closePath();
  ctx.fillStyle = linGrad(ctx, 720, 0, W, 0, [[0, '#2a1608'], [0.35, '#5a3416'], [1, '#1a0c05']]); ctx.fill(); ctx.clip();
  const rr = mulberry(9); for (let i = 0; i < 60; i++) { ctx.fillStyle = rgba('#d89a52', 0.04 + rr() * 0.05); ctx.beginPath(); ctx.ellipse(740 + rr() * 360, rr() * H, 20 + rr() * 30, 14 + rr() * 20, rr() * 3, 0, 6.283); ctx.fill(); }
  glow(ctx, 900, 1480, 420, '#ff7a2a', 0.5); ctx.restore();
  ctx.save(); ctx.strokeStyle = 'rgba(255,190,120,0.5)'; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(760, 0); ctx.quadraticCurveTo(700, 960, 780, H); ctx.stroke(); ctx.restore();
  const slump = ease.io3(k) * 0.8;
  const st = { blink: Math.max(blinkAt(t), 0.35 + 0.25 * k), look: [0.1, 0.5], brow: 0.55, sweat: 1, t, mouth: 0.45 + 0.25 * Math.sin(t * 3.2), breath: Math.sin(t * 3.4) * 1.2, slump, tilt: 0.05 + 0.16 * slump, hx: 26 * slump };
  const pal = warmPal(0.85);
  const tilt = lerp(0, 0.06, k);
  const draw = (g, C) => { g.save(); camApply(g, 540, 1000, lerp(1.05, 1.18, k), tilt, W / 2 - 60, 1000); g.translate(500 + 60 * slump, 880); g.scale(1.12, 1.12); nikiasMedium(g, C, st); g.restore(); };
  litRender(ctx, draw, (m) => { radialMask(m, 760, 1200, 60, 900, 0.9); }, Object.assign({ rim: { dx: 8, dy: -4, col: '#ff8a3a', a: 0.9 } }, pal));
  ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.globalAlpha = 0.25; ctx.fillStyle = '#ff5a1a'; ctx.fillRect(0, 0, W, H); ctx.restore();
  motes(ctx, t, 50, 41, { y0: 900, y1: 1920, vy: -120, vx: -10, size: [1, 2.6], col: '#ffb060', a: 0.7, life: 3 });
}

// ================================================================== SHOT 09 — pre-drop: character -> anatomical silhouette
function s09(ctx, t) {
  const lt = t - EV.predrop;
  const burst = inv(EV.power1 - 0.05, EV.power1 + 0.08, t);
  ctx.fillStyle = '#080406'; ctx.fillRect(0, 0, W, H);
  const heat = inv(0, 1.32, lt);
  glow(ctx, 600, 980, lerp(500, 1100, heat), '#ff4a14', lerp(0.35, 0.9, heat));
  glow(ctx, 600, 980, 300, '#ffd08a', 0.4 * heat);
  // silhouette of Nikias in profile against the glow
  const S = cvs('sil'), sg = S.getContext('2d');
  sg.save(); sg.translate(540, 820); const sc = lerp(1.25, 1.45, ease.io2(heat)); sg.scale(sc, sc); nikiasProfile(sg, SKIN_SHD, { breath: Math.sin(t * 4) * 0.8, slump: 0.3, brow: 0.6 }); sg.restore();
  sg.globalCompositeOperation = 'source-in'; sg.fillStyle = '#050203'; sg.fillRect(0, 0, W, H); sg.globalCompositeOperation = 'source-over';
  ctx.save(); ctx.globalAlpha = 1 - burst; ctx.drawImage(S, 0, 0);
  // rim of fire around the silhouette
  const e = cvs('silrim'), eg = e.getContext('2d'); eg.drawImage(S, 0, 0); eg.globalCompositeOperation = 'source-in'; eg.fillStyle = '#ffb060'; eg.fillRect(0, 0, W, H); eg.globalCompositeOperation = 'destination-out'; eg.drawImage(S, 10, 4); eg.globalCompositeOperation = 'source-over';
  ctx.globalCompositeOperation = 'screen'; ctx.filter = 'blur(2px)'; ctx.drawImage(e, 0, 0); ctx.filter = 'blur(14px)'; ctx.drawImage(e, 0, 0); ctx.restore();
  // scan line converts him into the anatomical figure
  const scanY = lerp(-100, H + 100, ease.io3(inv(25.33, EV.power1, t)));
  if (t > 25.33) {
    ctx.save(); ctx.beginPath(); ctx.rect(0, 0, W, scanY); ctx.clip();
    ctx.fillStyle = 'rgba(4,8,16,0.9)'; ctx.fillRect(0, 0, W, H);
    ctx.translate(560, 1000); ctx.scale(0.86, 0.86); bodySil(ctx, { t, edge: '#7fd6ff', ea: 0.9 }); skeletonHint(ctx, 0.25);
    ctx.restore();
    ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.fillStyle = linGrad(ctx, 0, scanY - 40, 0, scanY + 4, [[0, 'rgba(127,214,255,0)'], [1, 'rgba(180,235,255,0.9)']]); ctx.fillRect(0, scanY - 40, W, 44); ctx.restore();
  }
  if (burst > 0) { ctx.save(); ctx.globalAlpha = burst; ctx.translate(560, 1000); ctx.scale(0.86 + burst * 0.06, 0.86 + burst * 0.06); bodySil(ctx, { t, edge: '#ffd08a', ea: 1, fill: 'rgba(255,170,90,0.14)' }); ctx.restore(); }
  motes(ctx, t, 90, 51, { vy: -260, vx: 30, size: [1, 3.5], col: '#ffb060', a: 0.8, life: 2 });
}

// ================================================================== SHOT 10 — DROP: the nervous system ignites
function s10(ctx, t) {
  const lt = t - EV.drop1;
  anatomyField(ctx, t);
  const rev = ease.out3(inv(0, 0.9, lt));
  const cam = ease.io3(inv(0.0, 3.4, lt));
  ctx.save(); camApply(ctx, 0, lerp(-560, -160, cam), lerp(2.4, 1.02, cam), lerp(0.05, 0, cam), W / 2, 980);
  bodySil(ctx, { t, fill: 'rgba(30,60,90,0.35)', ea: 0.7 });
  skeletonHint(ctx, 0.12);
  nerves(ctx, t, { reveal: rev, disturb: 0.15 * inv(1.5, 3.5, lt) });
  ctx.save(); ctx.translate(0, -655); ctx.scale(0.25, 0.25); brainLat(ctx, { t, glow: '#ffe6a8' }); ctx.restore();
  ctx.restore();
  // drop burst
  glow(ctx, W / 2, 700, 900 * (1 - rev * 0.5), '#ffd890', 0.6 * (1 - inv(0, 0.5, lt)));
  motes(ctx, t, 60, 61, { vy: -40, vx: 0, size: [1, 3], col: '#ffe6a8', a: 0.6, life: 3 });
}

// ================================================================== SHOT 11 — dizziness & confusion (subjective POV)
function s11(ctx, t) {
  const lt = t - 30.0;
  const frozen = t >= EV.slam3;
  const tt = frozen ? EV.slam3 : t;
  const sway = Math.sin(tt * 1.9) * 0.07 + Math.sin(tt * 3.1) * 0.03;
  const L = cvs('s11'), g = L.getContext('2d');
  g.save(); camApply(g, W / 2, H / 2, 1.18 + Math.sin(tt * 1.3) * 0.05, sway, W / 2 + Math.sin(tt * 0.9) * 40, H / 2);
  courtyard(g, { x: Math.sin(tt * 0.8) * 120, y: 0, s: 1.0, hz: 1100, bullX: 560, bullY: 1300, bullS: 0.85 }, tt, { fire: 1, eyeGlow: 0.4 });
  g.restore();
  // double vision: offset ghost swinging with the beat
  const dv = 18 + 26 * Math.abs(Math.sin(tt * 1.7)) + 20 * kickPulse(tt, 6);
  ctx.save(); ctx.filter = `blur(${2 + 3 * Math.abs(Math.sin(tt * 1.1))}px)`; ctx.drawImage(L, 0, 0); ctx.restore();
  ctx.save(); ctx.globalAlpha = 0.42; ctx.globalCompositeOperation = 'screen'; ctx.drawImage(L, dv, -dv * 0.3); ctx.restore();
  heatShimmer(ctx, L, tt, 0, 0, 0);
  // tunnel vignette breathing
  ctx.save(); ctx.fillStyle = radGrad(ctx, W / 2, H / 2, 200 + 60 * Math.sin(tt * 2), 1000, [[0, 'rgba(0,0,0,0)'], [1, 'rgba(20,4,2,0.95)']]); ctx.fillRect(0, 0, W, H); ctx.restore();
  if (frozen) { const k = inv(EV.slam3, EV.slam3 + 0.25, t); ctx.save(); ctx.globalAlpha = 0.6 * k; ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
}

// ================================================================== SHOT 12 — thermoregulation: the body struggles
function s12(ctx, t) {
  const lt = t - EV.scan3;
  anatomyField(ctx, t, { warm: 0.3 * inv(0, 3.5, lt) });
  const k = inv(0, 3.5, lt);
  ctx.save(); camApply(ctx, 0, lerp(-80, 0, ease.io2(k)), lerp(1.12, 1.0, ease.io2(k)), 0, W / 2, 1000);
  // core heat filling outward
  ctx.save(); ctx.beginPath(); crPath(ctx, BODY, true, 0.45); ctx.clip();
  ctx.fillStyle = radGrad(ctx, 0, -280, 20, lerp(260, 900, k), [[0, rgba('#ff6a2a', 0.75)], [0.5, rgba('#ff4a1a', 0.35)], [1, rgba('#ff4a1a', 0)]]); ctx.fillRect(-400, -800, 800, 1600);
  ctx.restore();
  bodySil(ctx, { t, edge: mix('#7fd6ff', '#ffb07a', k), ea: 0.85 });
  // heat flow lines core -> skin (turbulent as it struggles)
  ctx.save(); ctx.globalCompositeOperation = 'screen';
  for (let i = 0; i < 22; i++) {
    const ang = -Math.PI / 2 + (i / 22 - 0.5) * 5.6, len = 260 + (i % 3) * 60;
    const u = ((lt * 0.7 + i * 0.13) % 1);
    const pts = []; for (let s2 = 0; s2 <= 1; s2 += 0.1) { const rr = s2 * len * (0.4 + 0.6 * u); pts.push([Math.cos(ang) * rr * 0.8 + Math.sin(s2 * 8 + t * 4 + i) * 12 * k, -280 + Math.sin(ang) * rr * 1.6]); }
    ctx.strokeStyle = rgba('#ffb07a', 0.5 * (1 - u)); ctx.lineWidth = 4; ctx.beginPath(); crPath(ctx, pts, false); ctx.stroke();
  }
  ctx.restore();
  // hypothalamus thermostat signal
  ctx.save(); ctx.translate(0, -655); ctx.scale(0.25, 0.25); brainLat(ctx, { t, glow: '#9fdcff' }); ctx.restore();
  const hp = 0.5 + 0.5 * Math.sin(t * 6);
  glow(ctx, -10, -650, 60, '#9fdcff', 0.9 * hp);
  // sweat at the skin edges
  for (let i = 0; i < 24; i++) { const p = BODY[(i * 7) % BODY.length]; const u = ((t * 0.6 + i * 0.37) % 1); ctx.fillStyle = rgba('#bfe8ff', 0.8 * Math.sin(Math.PI * u)); ctx.beginPath(); ctx.ellipse(p[0] * 1.04, p[1] + u * 30, 7, 9, 0, 0, 6.283); ctx.fill(); }
  ctx.restore();
  label(ctx, 540, 350, 640, 230, 'HYPOTHALAMUS', '#9fdcff', env(lt, 0.5, 3.4, 0.3, 0.3));
}

// ================================================================== SHOT 13 — HEATSTROKE: central silhouette, eclipse of heat
function s13(ctx, t) {
  const lt = t - EV.clank;
  ctx.fillStyle = '#050304'; ctx.fillRect(0, 0, W, H);
  const k = ease.out3(inv(0, 0.8, lt));
  const pulse = kickPulse(t, 5);
  // corona behind the figure
  glow(ctx, W / 2, 1040, lerp(300, 820, k) + pulse * 60, '#ff3a10', 0.75);
  glow(ctx, W / 2, 1040, 280, '#ffc070', 0.55 * k);
  ctx.save(); ctx.strokeStyle = rgba('#ffb070', 0.5 * k); ctx.lineWidth = 2;
  for (let i = 0; i < 3; i++) { ctx.beginPath(); ctx.arc(W / 2, 1040, 420 + i * 70 + Math.sin(t * 2 + i) * 8, 0, 6.283); ctx.stroke(); } ctx.restore();
  ctx.save(); ctx.translate(W / 2, 1130); ctx.scale(0.78 + lt * 0.01, 0.78 + lt * 0.01);
  ctx.fillStyle = '#030102'; ctx.beginPath(); crPath(ctx, BODY, true, 0.45); ctx.fill();
  ctx.strokeStyle = rgba('#ffc890', 0.9); ctx.lineWidth = 3; ctx.stroke();
  ctx.restore();
  motes(ctx, t, 80, 71, { vy: -90, vx: 0, size: [1, 3], col: '#ffb070', a: 0.8, life: 4 });
}

// ================================================================== SHOT 14 — the brain: function impaired
function s14(ctx, t) {
  const lt = t - EV.slam4;
  anatomyField(ctx, t, { warm: 0.35 });
  const hb = HEARTBEATS.reduce((a, x) => (t >= x ? Math.max(a, Math.exp(-(t - x) * 6)) : a), 0);
  const push = ease.io2(inv(0, 3.2, lt));
  const out = ease.in3(inv(EV.wail5 - 0.25, EV.wail5 + 0.2, t));
  ctx.save(); ctx.translate(W / 2 + Math.sin(lt * 0.5) * 20, lerp(980, 380, out)); const s = lerp(1.45, 1.75, push) * (1 + hb * 0.02) * lerp(1, 0.35, out); ctx.scale(s, s);
  ctx.rotate(Math.sin(lt * 0.8) * 0.02);
  brainLat(ctx, { t, misfire: 0.25 + 0.6 * inv(0.5, 3.0, lt), hot: 0.35 * inv(0, 3, lt), glow: '#9fdcff' });
  ctx.restore();
  glow(ctx, W / 2, 980, 700, '#ff3a2a', 0.15 * hb);
  // misfire distortion slices
  if (lt > 1) { const r = mulberry(Math.floor(t * 12)); if (r() < 0.25) { const y = 600 + r() * 800, h2 = 20 + r() * 60; const src = cvs('glitch'); src.getContext('2d').drawImage(ctx.canvas, 0, 0);
    ctx.drawImage(src, 0, y, W, h2, (r() - 0.5) * 40, y, W, h2); } }
}

// ================================================================== SHOT 15 — vital organs at risk (heart, liver, kidneys)
function s15(ctx, t) {
  const lt = t - EV.wail5;
  const hot = inv(0.3, 3.6, lt);
  anatomyField(ctx, t, { warm: 0.4 + 0.4 * hot });
  const hb = HEARTBEATS.reduce((a, x) => (t >= x ? Math.max(a, Math.exp(-(t - x) * 7)) : a), 0);
  const ent = ease.out3(inv(0, 0.6, lt));
  ctx.save(); camApply(ctx, 0, -250, lerp(1.4, 2.05, ease.io2(inv(0, 3.6, lt))), 0, W / 2, lerp(1300, 960, ent));
  bodySil(ctx, { t, fill: 'rgba(40,60,90,0.35)', edge: mix('#7fd6ff', '#ffb07a', hot), ea: 0.7 });
  skeletonHint(ctx, 0.12);
  // kidneys (posterior, drawn first + dimmed)
  ctx.save(); ctx.globalAlpha = 0.85; kidney(ctx, -70, -150, -1, { hot }); kidney(ctx, 70, -150, 1, { hot }); ctx.restore();
  ctx.save(); ctx.translate(-30, 0); liver(ctx, { hot }); ctx.restore();
  ctx.save(); ctx.translate(30, -380); ctx.scale(0.3, 0.3); heartAnt(ctx, { beat: hb, stress: hot, t }); ctx.restore();
  // warning pulses on each heartbeat
  for (const [x, y] of [[30, -380], [-70, -270], [-70, -150], [70, -150]]) { ctx.save(); ctx.strokeStyle = rgba('#ff5a3a', 0.6 * hb * hot + 0.1); ctx.lineWidth = 3; ctx.beginPath(); ctx.arc(x, y, 50 + (1 - hb) * 40, 0, 6.283); ctx.stroke(); ctx.restore(); }
  ctx.restore();
  const la = env(lt, 0.5, 3.4, 0.3, 0.3);
  label(ctx, 600, 520, 840, 400, 'HEART', '#ffc0a8', la);
  label(ctx, 330, 900, 150, 760, 'LIVER', '#ffc0a8', la);
  label(ctx, 720, 1170, 820, 1060, 'KIDNEYS', '#ffc0a8', la);
  // building reverse-roar heat toward the silence
  ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.globalAlpha = 0.35 * inv(EV.roarRev, EV.sil2, t); ctx.fillStyle = '#ff4a1a'; ctx.fillRect(0, 0, W, H); ctx.restore();
}

// ================================================================== SHOT 16 — FINAL DROP: medical emergency (character x anatomy fusion)
function s16(ctx, t) {
  const lt = t - EV.drop2;
  ctx.fillStyle = '#070305'; ctx.fillRect(0, 0, W, H);
  const pulse = kickPulse(t, 6);
  glow(ctx, 620, 900, 1000, '#c8201a', 0.45 + 0.2 * pulse);
  const S = cvs('fusion'), g = S.getContext('2d');
  const sc = lerp(1.6, 1.45, ease.out3(inv(0, 1.2, lt)));
  g.save(); g.translate(560, 760); g.scale(sc, sc); nikiasProfile(g, SKIN_SHD, { breath: Math.sin(t * 4) * 0.8, slump: 0.2, brow: 0.7 }); g.restore();
  // fill silhouette with anatomical interior (nerves / vessels glow)
  const I2 = cvs('fusionIn'), ig = I2.getContext('2d');
  ig.fillStyle = '#12060a'; ig.fillRect(0, 0, W, H);
  ig.save(); ig.translate(470, 1660); ig.scale(1.5, 1.5); nerves(ig, t, { col: '#ff9a6a', disturb: 0.5 }); ig.restore();
  ig.save(); ig.translate(560 + 30 * sc, 760 - 118 * sc); ig.scale(0.5 * sc, 0.5 * sc); brainLat(ig, { t, misfire: 0.8, hot: 0.8, glow: '#ff9a6a' }); ig.restore();
  ig.globalCompositeOperation = 'destination-in'; ig.drawImage(S, 0, 0); ig.globalCompositeOperation = 'source-over';
  ctx.drawImage(I2, 0, 0);
  const e = cvs('fusRim'), eg = e.getContext('2d'); eg.drawImage(S, 0, 0); eg.globalCompositeOperation = 'source-in'; eg.fillStyle = '#ff6a4a'; eg.fillRect(0, 0, W, H); eg.globalCompositeOperation = 'destination-out'; eg.drawImage(S, -8, 3); eg.globalCompositeOperation = 'source-over';
  ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.filter = 'blur(2px)'; ctx.drawImage(e, 0, 0); ctx.filter = 'blur(16px)'; ctx.globalAlpha = 0.8 + 0.2 * pulse; ctx.drawImage(e, 0, 0); ctx.restore();
  // emergency pulse rings + roar shockwave at the drop
  const sw = inv(0, 0.7, lt); if (sw < 1) { ctx.save(); ctx.strokeStyle = rgba('#ffb08a', 0.8 * (1 - sw)); ctx.lineWidth = 8 * (1 - sw) + 1; ctx.beginPath(); ctx.arc(560, 900, 100 + sw * 900, 0, 6.283); ctx.stroke(); ctx.restore(); }
  for (let r = 0; r < 2; r++) { const u = ((lt * 0.9 + r * 0.5) % 1); ctx.save(); ctx.strokeStyle = rgba('#ff4a3a', 0.35 * (1 - u)); ctx.lineWidth = 3; ctx.beginPath(); ctx.arc(560, 900, 300 + u * 500, 0, 6.283); ctx.stroke(); ctx.restore(); }
  motes(ctx, t, 70, 81, { vy: -150, vx: 20, size: [1, 3.2], col: '#ff9a6a', a: 0.8, life: 2.5 });
}

// ================================================================== SHOT 17 — consciousness can be lost
function s17(ctx, t) {
  const lt = t - EV.wail6, k = inv(0, 3.6, lt);
  const stutter = (t > EV.stutter && t < EV.stutter + 0.36) ? Math.floor((t - EV.stutter) / 0.11) % 2 : 0;
  bronzeInterior(ctx, t, { oy: 40 });
  const st = { blink: lerp(0.15, 1, ease.in2(k)) * 0 + clamp(ease.io3(inv(0.6, 3.2, lt))), look: [0, 0.4], brow: lerp(0.5, 0.1, k), sweat: 1, t, mouth: lerp(0.4, 0.1, k), breath: Math.sin(t * 2) * lerp(1, 0.2, k), tilt: 0.08 + 0.1 * k, slump: 0.5 + 0.3 * k };
  const pal = warmPal(lerp(0.8, 0.3, k));
  const L = cvs('s17'), g = L.getContext('2d');
  litRender(g, (g2, C) => { g2.save(); camApply(g2, 540, 1000, lerp(1.3, 1.6, ease.io2(k)), lerp(0.05, 0.12, k), W / 2, 1000); g2.translate(480, 900); g2.scale(1.15, 1.15); nikiasMedium(g2, C, st); g2.restore(); },
    (m) => radialMask(m, 500, 950, 50, lerp(800, 380, k), lerp(0.9, 0.4, k)), Object.assign({ rim: { dx: 7, dy: -3, col: '#ff9a4a', a: lerp(0.8, 0.2, k) } }, pal));
  ctx.save(); ctx.filter = `blur(${lerp(0, 9, ease.in2(k))}px) saturate(${lerp(1, 0.35, k)})`; ctx.drawImage(L, stutter * 24, 0); ctx.restore();
  if (stutter) { ctx.save(); ctx.globalAlpha = 0.4; ctx.globalCompositeOperation = 'screen'; ctx.drawImage(L, -30, 6); ctx.restore(); }
  // the world fading: closing darkness
  ctx.save(); ctx.fillStyle = radGrad(ctx, W / 2, 960, lerp(600, 120, k), lerp(1200, 600, k), [[0, 'rgba(0,0,0,0)'], [1, 'rgba(0,0,0,0.97)']]); ctx.fillRect(0, 0, W, H); ctx.restore();
}

// ================================================================== SHOT 18 — extreme heat can be fatal: restrained outline
function s18(ctx, t) {
  const lt = t - EV.scan4;
  ctx.fillStyle = '#040304'; ctx.fillRect(0, 0, W, H);
  const draw = ease.io3(inv(0, 1.2, lt));
  const pts = curvePts(BODY.concat([BODY[0]]), 400);
  const n = Math.floor(pts.length * draw);
  ctx.save(); ctx.translate(W / 2, 1060); ctx.scale(0.74, 0.74);
  ctx.strokeStyle = rgba('#e8dccb', 0.85); ctx.lineWidth = 3; ctx.beginPath(); pts.slice(0, n).forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)); ctx.stroke();
  if (n > 1) { const [hx, hy] = pts[n - 1]; glow(ctx, hx, hy, 50, '#ff8a5a', 0.9 * (1 - inv(1.1, 1.4, lt))); }
  ctx.globalAlpha = 0.5 * inv(1.0, 1.7, lt); ctx.filter = 'blur(12px)'; ctx.strokeStyle = '#8a1a14'; ctx.lineWidth = 10; ctx.beginPath(); crPath(ctx, BODY, true, 0.45); ctx.stroke();
  ctx.restore();
  motes(ctx, t, 30, 91, { vy: -30, vx: 0, size: [0.8, 2], col: '#e8c9a0', a: 0.35, life: 8 });
}

// ================================================================== SHOT 19 — the bronze bull returns (exterior, roar)
function s19(ctx, t) {
  const lt = t - EV.bar32;
  const roar = inv(EV.roarClimax - 0.05, EV.roarClimax + 0.1, t) * (1 - inv(EV.roarClimax + 0.15, EV.sil3, t) * 0.5);
  const L = cvs('s19'), g = L.getContext('2d');
  const mv = ease.io2(inv(0, 1.7, lt));
  courtyard(g, { x: lerp(80, -40, mv), y: 0, s: 1.25, hz: 1420, bullX: lerp(720, 690, mv), bullY: 1560, bullS: lerp(0.98, 1.04, mv) }, t, { fire: 1 + roar * 0.8, eyeGlow: 0.3 + roar * 1.0 });
  ctx.drawImage(L, 0, 0);
  // roar: shockwave from the bull's head + ember burst
  if (roar > 0) { const hx = lerp(720, 690, mv) - 470 * lerp(0.98, 1.04, mv), hy = 1560 - 372 * lerp(0.98, 1.04, mv); glow(ctx, hx, hy, 500 * roar, '#ff7a2a', 0.5 * roar);
    const u = inv(EV.roarClimax, EV.roarClimax + 0.4, t); ctx.save(); ctx.strokeStyle = rgba('#ffc890', 0.7 * (1 - u)); ctx.lineWidth = 6; ctx.beginPath(); ctx.arc(hx, hy, 60 + u * 700, 0, 6.283); ctx.stroke(); ctx.restore(); }
  motes(ctx, t, 90, 101, { y0: 1300, y1: 1900, vy: -300 - 400 * roar, vx: 30, size: [1, 3.6], col: '#ffb060', a: 0.9, life: 2 });
  ctx.save(); ctx.filter = 'blur(16px)'; column(ctx, lerp(1100, 1040, mv), 2200, 280, 2600, 0.1); ctx.restore();
}

// ================================================================== SHOT 20 — the bull's eye -> light streak (loops to frame 1)
function s20(ctx, t) {
  const lt = t - EV.final;
  ctx.fillStyle = '#060403'; ctx.fillRect(0, 0, W, H);
  const push = ease.in3(inv(0.6, 1.765, lt));
  const s = lerp(3.0, 3.4, ease.out2(inv(0, 0.8, lt))) * lerp(1, 6, push);
  const eyeX = -470, eyeY = -372;
  const L = cvs('s20'), g = L.getContext('2d');
  g.save(); g.translate(W * 0.5, 980); g.scale(s, s); g.translate(-eyeX, -eyeY);
  bullBronze(g, { glow: 0.6, t, eyeGlow: 0.6 + 0.4 * kick(t, EV.final, 3) });
  g.restore();
  ctx.save(); ctx.globalAlpha = 1 - push; ctx.drawImage(L, 0, 0); ctx.restore();
  // rim light sweep across the bronze head
  ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.globalAlpha = 0.35 * (1 - push);
  { const sx = lerp(-600, 1700, inv(0, 1.2, lt)); ctx.globalAlpha = 0.22 * (1 - push); ctx.fillStyle = linGrad(ctx, sx - 420, -200, sx + 420, 600, [[0, 'rgba(255,190,110,0)'], [0.5, 'rgba(255,190,110,1)'], [1, 'rgba(255,190,110,0)']]); ctx.fillRect(0, 0, W, H); } ctx.restore();
  // final frames: the eye's glint stretches into the opening light streak (loop match)
  const streak = inv(0.9, 1.75, lt);
  if (streak > 0) {
    const bandY = 1135;
    shaft(ctx, -100, bandY, 40 * streak, W + 100, bandY, 160 * streak, '#ffb466', 0.5 * streak);
    ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.fillStyle = linGrad(ctx, 0, bandY - 60 * streak, 0, bandY + 60 * streak, [[0, 'rgba(255,180,100,0)'], [0.5, rgba('#ffc890', 0.5 * streak)], [1, 'rgba(255,180,100,0)']]);
    ctx.fillRect(0, bandY - 80, W, 160); ctx.restore();
  }
}
