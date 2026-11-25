// Character rig v2: curved limbs, articulated hands, weight shift, breathing, squash & stretch,
// animatable brows/lids, sitting & lying, velocity-driven secondary motion. Same character designs.
const C = require('./core');
const { lerp, clamp, D2R, hash, mixh } = C;
const { INK, shape, tube, tubeCurve, line, curve, ell } = require('./draw');
const K1 = require('./chars');          // reuse the approved character specs (designs unchanged)
const SPECS = K1.SPECS;

const BROWS = {
  neutral: [0, 0, 0, 0], worried: [-14, 6, -14, 6], angry: [12, -7, 12, -7], raised: [-16, -14, -16, -14],
  sad: [-11, 8, -11, 8], skeptic: [8, -2, -16, -15], calm: [4, 4, 4, 4], shock: [-22, -18, -22, -18],
};
function P0(o = {}) {
  const p = Object.assign({
    x: 0, y: 0, s: 1, face: 1, rot: 0, piv: 'feet', lean: 0, hip: 0, bob: 0, squash: 0, sit: 0,
    armL: [10, 12], armR: [-10, 12], handL: 'relaxed', handR: 'relaxed', legL: [3, 2], legR: [-3, 2],
    tilt: 0, turn: 0.15, headSq: 0, vx: 0, tail: 0, shiver: 0, breath: 1,
    eyes: 'open', lid: 0.05, lidLow: 0, pupil: 1, look: [0.15, 0], brows: 'neutral', mouth: 'flat', open: 0.5,
    sweat: 0, pale: 0, blush: 0, sick: 0, tears: 0, bandage: 0, bump: 0, chalk: 0,
    propL: null, propR: null, t: 0, alpha: 1,
  }, o);
  if (typeof p.brows === 'string') p.brows = BROWS[p.brows] || BROWS.neutral;
  return p;
}
function blend(a, b, k) {
  const out = {};
  for (const key of new Set([...Object.keys(a), ...Object.keys(b)])) {
    let va = a[key], vb = b[key];
    if (key === 'brows') { va = typeof va === 'string' ? BROWS[va] : va; vb = typeof vb === 'string' ? BROWS[vb] : vb; }
    if (va === undefined) { out[key] = vb; continue; }
    if (vb === undefined) { out[key] = va; continue; }
    if (typeof va === 'number' && typeof vb === 'number') out[key] = lerp(va, vb, k);
    else if (Array.isArray(va) && Array.isArray(vb) && typeof va[0] === 'number') out[key] = va.map((v, i) => lerp(v, vb[i], k));
    else out[key] = k < 0.5 ? va : vb;
  }
  return out;
}
// keyframed acting: keys [{t, e:'spring'|'back'|'smooth'|'snap'|'lin', ...pose}] -> pose at t
function act(keys, t) {
  let i = 0; while (i + 1 < keys.length && t >= keys[i + 1].t) i++;
  if (i === 0 && t < keys[0].t) return keys[0];
  const a = keys[i], b = keys[i + 1];
  if (!b) return a;
  const u = (t - a.t) / (b.t - a.t), e = b.e || 'smooth';
  let k;
  if (e === 'snap') k = u < 0.5 ? 0 : 1;
  else if (e === 'lin') k = clamp(u);
  else if (e === 'back') k = C.outBack(u, 1.8);
  else if (e === 'spring') k = clamp(C.spring(u * (b.t - a.t), 20, 10), 0, 1.15);
  else if (e === 'in') k = C.inQ(u);
  else if (e === 'out') k = C.outC(u);
  else k = C.smoother(u);
  return blend(a, b, k);
}
// walk / run / idle partial poses
function walk(ph, amp = 1) {
  const s = Math.sin(ph), c = Math.cos(ph);
  return { legL: [26 * s * amp, Math.max(4, 46 * Math.sin(ph - 1.2) * amp)], legR: [-26 * s * amp, Math.max(4, 46 * Math.sin(ph + Math.PI - 1.2) * amp)],
    armL: [-24 * s * amp, 18 + 10 * amp], armR: [24 * s * amp, 18 + 10 * amp], bob: 8 * Math.abs(c) * amp, hip: 5 * s * amp, lean: 4 * amp };
}
function run(ph, amp = 1) {
  const s = Math.sin(ph), c = Math.cos(ph);
  return { legL: [50 * s * amp, 22 + Math.max(0, 85 * Math.sin(ph - 1.0)) * amp], legR: [-50 * s * amp, 22 + Math.max(0, 85 * Math.sin(ph + Math.PI - 1.0)) * amp],
    armL: [-60 * s * amp, 85], armR: [60 * s * amp, 85], bob: 16 * Math.abs(c) * amp, lean: 14 * amp, hip: 4 * s, handL: 'fist', handR: 'fist' };
}
function flail(t, amp = 1) {
  return { armL: [150 + 28 * Math.sin(t * 21), 35 + 30 * Math.sin(t * 17)], armR: [-150 + 28 * Math.sin(t * 19 + 1), 35 + 30 * Math.sin(t * 23)], handL: 'spread', handR: 'spread' };
}
function idle(t, seed = 1, amp = 1) {    // subtle weight shift + breathing, never a dead hold
  return { hip: 6 * amp * Math.sin(t * 0.9 + seed), bob: 2.5 * amp * Math.sin(t * 2.2 + seed), tilt: 2 * amp * Math.sin(t * 0.7 + seed * 2) };
}
function blink(t, seed, base = 0.05) {
  const per = 1.7 + (hash(seed) * 0.5 + 0.5) * 1.6, ph = (t + hash(seed * 3) * 3) % per;
  return ph < 0.06 ? 1 : ph < 0.1 ? lerp(1, base, (ph - 0.06) / 0.04) : base;
}

const pt = (x, y, a, L) => [x + Math.sin(a * D2R) * L, y + Math.cos(a * D2R) * L];

// ------------------------------------------------------------------ hands
// local frame: origin at wrist, +y points away from the forearm. side flips thumb.
function hand(ctx, kind, col, side = 1) {
  const sk = col, lw = 4;
  const finger = (x0, y0, a, L, w = 11) => tubeCurve(ctx, [[x0, y0], [x0 + Math.sin(a * D2R) * L * 0.55, y0 + Math.cos(a * D2R) * L * 0.55], [x0 + Math.sin((a + 12 * side) * D2R) * L, y0 + Math.cos((a + 12 * side) * D2R) * L]], w, sk, lw);
  if (kind === 'fist' || kind === 'point' || kind === 'thumb' || kind === 'grip') {
    if (kind === 'point') finger(4 * side, 18, 0, 40, 11);
    if (kind === 'thumb') finger(-14 * side, 4, -160 * side, 30, 12);
    shape(ctx, c => c.roundRect(-17, 2, 34, 32, 12), sk, { lw, tex: false });
    if (kind !== 'grip') { for (let i = 0; i < 3; i++) line(ctx, [[-13 + i * 9, 30], [-13 + i * 9, 22]], 2.5); }
    if (kind === 'grip') for (let i = 0; i < 4; i++) shape(ctx, ell(-12 + i * 8, 30, 6, 7), sk, { lw: 3, tex: false });
    if (kind !== 'thumb') shape(ctx, ell(16 * side, 14, 7, 11, -0.4 * side), sk, { lw: 3.5, tex: false });
    return;
  }
  const spread = kind === 'spread' ? 1.6 : kind === 'open' ? 0.8 : 0.35;
  const curl = kind === 'relaxed' ? 30 : 0;
  for (let i = 0; i < 4; i++) { const a = (i - 1.5) * 14 * spread; finger(-11 + i * 7.5, 22, a - curl * side * 0.3, kind === 'relaxed' ? 26 : 32, 10); }
  shape(ctx, c => c.roundRect(-16, 0, 32, 30, 12), sk, { lw, tex: false });
  finger(15 * side, 10, (55 + 25 * spread) * side, 24, 11);
}

// ------------------------------------------------------------------ head
function headPath(w, h) {
  return c => {
    c.moveTo(0, -h / 2);
    c.bezierCurveTo(w * 0.6, -h / 2, w * 0.6, h * 0.16, w * 0.3, h * 0.42);
    c.bezierCurveTo(w * 0.16, h * 0.53, -w * 0.16, h * 0.53, -w * 0.3, h * 0.42);
    c.bezierCurveTo(-w * 0.6, h * 0.16, -w * 0.6, -h / 2, 0, -h / 2); c.closePath();
  };
}
function drawEye(ctx, ex, ey, rx, ry, P, side, skin, sp) {
  const kind = P.eyes;
  if (kind === 'closed') { curve(ctx, [ex - rx, ey], [ex, ey + ry * 0.55], [ex + rx, ey], 5); return; }
  if (kind === 'happy') { curve(ctx, [ex - rx, ey + 4], [ex, ey - ry * 0.95], [ex + rx, ey + 4], 5.5); return; }
  if (kind === 'squeeze') { line(ctx, [[ex - rx, ey - ry * 0.4 * side], [ex + rx * 0.2, ey], [ex - rx, ey + ry * 0.4 * side]].map(p => [ex + (p[0] - ex) * side, p[1]]), 5); return; }
  if (kind === 'dead') { line(ctx, [[ex - rx * 0.7, ey - ry * 0.6], [ex + rx * 0.7, ey + ry * 0.6]], 5); line(ctx, [[ex + rx * 0.7, ey - ry * 0.6], [ex - rx * 0.7, ey + ry * 0.6]], 5); return; }
  const big = kind === 'wide' ? 1.32 : 1, RX = rx * big, RY = ry * big;
  if (sp.darkCircles || P.sick > 0.3) { ctx.fillStyle = `rgba(120,70,90,${sp.darkCircles ? 0.25 : 0.25 * P.sick})`; ctx.beginPath(); ctx.ellipse(ex, ey + RY * 0.55, RX * 1.05, RY * 0.6, 0, 0, Math.PI * 2); ctx.fill(); }
  shape(ctx, ell(ex, ey, RX, RY), '#fffaf0', { lw: 4.5, tex: false });
  if (kind === 'spiral') {
    ctx.beginPath(); for (let a = 0; a < 14; a += 0.2) { const r = a * RX * 0.06, an = a + P.t * 9 * side; ctx.lineTo(ex + Math.cos(an) * r, ey + Math.sin(an) * r); }
    ctx.lineWidth = 3.5; ctx.strokeStyle = INK; ctx.stroke();
  } else {
    const pr = RX * 0.42 * P.pupil * (kind === 'wide' ? 0.55 : 1);
    const px = ex + P.look[0] * RX * 0.45, py = ey + P.look[1] * RY * 0.42;
    ctx.fillStyle = '#3d2a20'; ctx.beginPath(); ctx.ellipse(px, py, pr * 1.25, pr * 1.35, 0, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = INK; ctx.beginPath(); ctx.ellipse(px, py, pr * 0.8, pr * 0.9, 0, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = 'rgba(255,255,255,0.92)'; ctx.beginPath(); ctx.arc(px - pr * 0.45, py - pr * 0.5, pr * 0.32, 0, Math.PI * 2); ctx.fill();
  }
  const lid = clamp(P.lid), low = clamp(P.lidLow);
  if (lid > 0.01 || low > 0.01) {
    ctx.save(); ctx.beginPath(); ctx.ellipse(ex, ey, RX + 1, RY + 1, 0, 0, Math.PI * 2); ctx.clip(); ctx.fillStyle = skin;
    const yl = ey - RY + 2 * RY * lid, yb = ey + RY - 2 * RY * low * 0.6;
    if (lid > 0.01) ctx.fillRect(ex - RX - 3, ey - RY - 3, 2 * RX + 6, yl - (ey - RY) + 3);
    if (low > 0.01) ctx.fillRect(ex - RX - 3, yb, 2 * RX + 6, ey + RY - yb + 3);
    ctx.restore();
    if (lid > 0.01) { const ww = RX * Math.sqrt(Math.max(0, 1 - Math.pow((yl - ey) / RY, 2))); line(ctx, [[ex - ww - 1, yl], [ex + ww + 1, yl]], 5); }
    if (low > 0.05) { const ww = RX * Math.sqrt(Math.max(0, 1 - Math.pow((yb - ey) / RY, 2))); curve(ctx, [ex - ww, yb], [ex, yb - 4], [ex + ww, yb], 3); }
  }
}
function drawBrow(ctx, bx, by, w, side, inner, outer, color) {
  const xi = bx - side * w * 0.5, xo = bx + side * w * 0.5;
  shape(ctx, c => { c.moveTo(xi, by + inner + 4); c.quadraticCurveTo(bx, by - 8 + (inner + outer) / 2, xo, by + outer + 2); c.quadraticCurveTo(bx, by - 2 + (inner + outer) / 2, xi, by + inner + 10); c.closePath(); }, color, { lw: 2.5, tex: false });
}
function drawMouth(ctx, mx, my, w, P) {
  const m = P.mouth, o = clamp(P.open), dark = '#5a1f1c', tongue = '#d4635a', tooth = '#fffaf0';
  const ovalMouth = (rx, ry, teethTop = false, teethBot = false) => {
    shape(ctx, ell(mx, my + ry * 0.5, rx, ry), dark, { lw: 5, tex: false });
    ctx.save(); ctx.beginPath(); ctx.ellipse(mx, my + ry * 0.5, rx, ry, 0, 0, Math.PI * 2); ctx.clip();
    if (teethTop) { ctx.fillStyle = tooth; ctx.fillRect(mx - rx, my + ry * 0.5 - ry - 2, rx * 2, ry * 0.32); }
    if (teethBot) { ctx.fillStyle = tooth; ctx.fillRect(mx - rx, my + ry * 1.25, rx * 2, ry * 0.3); }
    ctx.fillStyle = tongue; ctx.beginPath(); ctx.ellipse(mx, my + ry * 1.35, rx * 0.7, ry * 0.5, 0, 0, Math.PI * 2); ctx.fill(); ctx.restore();
  };
  ctx.lineCap = 'round';
  if (m === 'flat') line(ctx, [[mx - w * 0.3, my], [mx + w * 0.3, my + 2]], 5);
  else if (m === 'smile') curve(ctx, [mx - w * 0.42, my - 6], [mx, my + 18], [mx + w * 0.42, my - 6], 5);
  else if (m === 'frown') curve(ctx, [mx - w * 0.36, my + 8], [mx, my - 12], [mx + w * 0.36, my + 8], 5);
  else if (m === 'smirk') curve(ctx, [mx - w * 0.32, my + 4], [mx + w * 0.05, my + 8], [mx + w * 0.38, my - 10], 5);
  else if (m === 'wavy') { ctx.beginPath(); for (let i = 0; i <= 16; i++) { const u = i / 16; ctx.lineTo(mx - w * 0.38 + u * w * 0.76, my + Math.sin(u * Math.PI * 3 + P.t * 8) * 5); } ctx.lineWidth = 5; ctx.strokeStyle = INK; ctx.stroke(); }
  else if (m === 'grin' || m === 'chuckle' || m === 'yell') {
    const hh = m === 'chuckle' ? 18 + 22 * o : m === 'yell' ? 30 + 20 * o : 26;
    const path = c => { c.moveTo(mx - w * 0.45, my - 6); c.quadraticCurveTo(mx, my - 2, mx + w * 0.45, my - 6); c.quadraticCurveTo(mx + w * 0.3, my + hh, mx, my + hh); c.quadraticCurveTo(mx - w * 0.3, my + hh, mx - w * 0.45, my - 6); c.closePath(); };
    shape(ctx, path, dark, { lw: 5, tex: false });
    ctx.save(); ctx.beginPath(); path(ctx); ctx.clip(); ctx.fillStyle = tooth; ctx.fillRect(mx - w * 0.5, my - 10, w, 12);
    ctx.fillStyle = tongue; ctx.beginPath(); ctx.ellipse(mx, my + hh, w * 0.2, 10, 0, 0, Math.PI * 2); ctx.fill(); ctx.restore();
  }
  else if (m === 'o') ovalMouth(w * 0.15, w * 0.17);
  else if (m === 'ooh') ovalMouth(w * 0.11, w * 0.13);
  else if (m === 'gasp') ovalMouth(w * 0.18, w * (0.22 + 0.12 * o));
  else if (m === 'scream') ovalMouth(w * (0.28 + 0.12 * o), w * (0.3 + 0.25 * o), true);
  else if (m === 'sneeze') ovalMouth(w * 0.16, w * 0.1 * (0.4 + o));
  else if (m === 'eek' || m === 'teeth') {
    const hw = m === 'eek' ? w * 0.48 : w * 0.4, hh = m === 'eek' ? 34 : 26;
    shape(ctx, c => { c.moveTo(mx - hw, my - 4); c.quadraticCurveTo(mx, my - 14, mx + hw, my - 4); c.quadraticCurveTo(mx + hw * 0.9, my + hh, mx, my + hh - 4); c.quadraticCurveTo(mx - hw * 0.9, my + hh, mx - hw, my - 4); c.closePath(); }, tooth, { lw: 5, tex: false });
    line(ctx, [[mx - hw * 0.95, my + hh * 0.4], [mx + hw * 0.95, my + hh * 0.4]], 3);
    for (let i = -2; i <= 2; i++) line(ctx, [[mx + i * hw * 0.34, my - 8], [mx + i * hw * 0.34, my + hh - 6]], 2.5);
  }
  else if (m === 'cough') shape(ctx, ell(mx, my + 4, w * 0.2, w * 0.13), dark, { lw: 5, tex: false });
}

function drawHead(ctx, sp, P) {
  const w = sp.headW, h = sp.headH, t = P.t;
  const skin = P.pale > 0 ? mixh(sp.skin, '#c3d3a0', P.pale * 0.85) : sp.skin;
  const fx = clamp(P.turn, -1, 1) * w * 0.17;
  ctx.save(); ctx.scale(1 + P.headSq * 0.3, 1 - P.headSq * 0.3);
  if (sp.hair === 'wild') {
    for (let i = 0; i < 9; i++) {
      const a = -Math.PI * 0.95 + i * Math.PI * 0.9 / 8 + Math.sin(t * 3 + i) * 0.05 - P.vx * 0.0002;
      const r0 = w * 0.42, r1 = w * (0.72 + 0.12 * Math.sin(i * 2.3));
      shape(ctx, c => { c.moveTo(Math.cos(a - 0.22) * r0, -h * 0.12 + Math.sin(a - 0.22) * r0); c.quadraticCurveTo(Math.cos(a) * r1 * 1.1, -h * 0.12 + Math.sin(a) * r1 * 1.1, Math.cos(a + 0.18) * r1, -h * 0.12 + Math.sin(a + 0.18) * r1); c.lineTo(Math.cos(a + 0.25) * r0, -h * 0.12 + Math.sin(a + 0.25) * r0); c.closePath(); }, sp.hairColor, { lw: 4.5 });
    }
  }
  if (sp.hood) {
    const ta = (P.tail || 0) + Math.sin(t * 2.4) * 6 - clamp(P.vx * 0.04, -40, 40);
    const pts = [];
    for (let i = 0; i < 7; i++) { const u = i / 6, wav = Math.sin(t * 3.2 - i * 0.9) * 6 * u + ta * u * 1.6; pts.push([-w * 0.5 - u * w * 0.32 - wav * 0.6, -h * 0.12 + u * h * 0.95 + Math.abs(wav) * 0.2]); }
    tubeCurve(ctx, pts, 22, sp.hoodDark, 4.5);
    shape(ctx, c => { c.ellipse(-w * 0.02, -h * 0.02, w * 0.66, h * 0.62, 0, 0, Math.PI * 2); }, sp.hood, { lw: 5, shade: { x0: w * 0.4, y0: -h * 0.4, x1: -w * 0.6, y1: h * 0.5, a: 0.3 } });
  }
  if (sp.ear) shape(ctx, ell(P.turn >= 0 ? -w * 0.47 : w * 0.47, h * 0.02, w * 0.09, h * 0.11), skin, { lw: 4.5, tex: false });
  shape(ctx, headPath(w, h), skin, { lw: 5, shade: { x0: w * 0.3, y0: -h * 0.3, x1: -w * 0.55, y1: h * 0.5, a: 0.22 }, hi: { x: w * 0.12 + fx, y: -h * 0.2, r: w * 0.4, a: 0.18 } });
  if (P.pale > 0.2) { ctx.save(); ctx.globalAlpha = P.pale * 0.25; ctx.beginPath(); headPath(w, h)(ctx); ctx.fillStyle = '#9fbf7a'; ctx.fill(); ctx.restore(); }
  if (sp.hair === 'bald') {
    ctx.save(); ctx.globalAlpha = 0.5; curve(ctx, [-w * 0.2, -h * 0.47], [-w * 0.05, -h * 0.6], [w * 0.05, -h * 0.46], 2.5); curve(ctx, [w * 0.02, -h * 0.48], [w * 0.15, -h * 0.62], [w * 0.22, -h * 0.45], 2.5); ctx.restore();
    for (const sd of [-1, 1]) shape(ctx, c => { c.moveTo(sd * w * 0.5, -h * 0.02); c.quadraticCurveTo(sd * w * 0.56, -h * 0.18, sd * w * 0.47, -h * 0.26); c.lineTo(sd * w * 0.43, -h * 0.04); c.closePath(); }, '#5a5552', { lw: 3 });
  }
  if (sp.hair === 'cap') shape(ctx, c => { c.moveTo(-w * 0.55, -h * 0.12); c.quadraticCurveTo(-w * 0.5, -h * 0.72, w * 0.1, -h * 0.68); c.quadraticCurveTo(w * 0.6, -h * 0.6, w * 0.56, -h * 0.12); c.quadraticCurveTo(0, -h * 0.26, -w * 0.55, -h * 0.12); }, sp.hairColor, { lw: 5 });
  if (sp.hair === 'coif') shape(ctx, c => { c.moveTo(-w * 0.58, h * 0.25); c.quadraticCurveTo(-w * 0.7, -h * 0.75, 0, -h * 0.66); c.quadraticCurveTo(w * 0.7, -h * 0.75, w * 0.58, h * 0.25); c.quadraticCurveTo(w * 0.5, -h * 0.35, 0, -h * 0.4); c.quadraticCurveTo(-w * 0.5, -h * 0.35, -w * 0.58, h * 0.25); }, sp.hairColor, { lw: 5 });
  if (sp.hairSide) for (const s of [-1, 1]) shape(ctx, c => { c.moveTo(s * w * 0.42, -h * 0.25); c.quadraticCurveTo(s * w * 0.6, -h * 0.05, s * w * 0.46, h * 0.16); c.lineTo(s * w * 0.38, -h * 0.05); c.closePath(); }, sp.hairSide, { lw: 4 });
  if (sp.hood) {
    ctx.save(); ctx.beginPath(); ctx.ellipse(-w * 0.02, -h * 0.02, w * 0.66, h * 0.62, 0, 0, Math.PI * 2); ctx.clip();
    shape(ctx, c => { c.moveTo(-w * 0.7, -h * 0.75); c.lineTo(w * 0.75, -h * 0.75); c.lineTo(w * 0.75, -h * 0.25); c.quadraticCurveTo(w * 0.25 + fx, -h * 0.48, -w * 0.4 + fx, -h * 0.25); c.quadraticCurveTo(-w * 0.62, -h * 0.05, -w * 0.62, h * 0.4); c.lineTo(-w * 0.7, h * 0.4); c.closePath(); }, sp.hood, { lw: 5, shade: { x0: w * 0.3, y0: -h * 0.6, x1: -w * 0.5, y1: h * 0.3, a: 0.25 } });
    ctx.restore();
    shape(ctx, c => { c.ellipse(-w * 0.02, -h * 0.02, w * 0.66, h * 0.62, 0, Math.PI * 0.94, Math.PI * 2.06); }, null, { lw: 5 });
  }
  if (P.bump > 0) shape(ctx, ell(w * 0.05, -h * 0.52, w * 0.13 * P.bump, h * 0.1 * P.bump), mixh(skin, '#e07a6a', 0.45), { lw: 4.5, tex: false });
  // face
  const ex = w * 0.2, ey = -h * 0.02, erx = w * 0.12, ery = h * 0.135;
  if (sp.stubble) { ctx.fillStyle = 'rgba(70,45,30,0.35)'; for (let i = 0; i < 26; i++) { const a = Math.PI * (0.15 + 0.7 * ((hash(i * 3) + 1) / 2)), r = w * (0.33 + 0.08 * hash(i * 5)); ctx.beginPath(); ctx.arc(fx + Math.cos(a) * r, h * 0.12 + Math.sin(a) * r * 0.62, 2.2, 0, Math.PI * 2); ctx.fill(); } }
  if (sp.freckles) { ctx.fillStyle = 'rgba(170,90,50,0.5)'; for (let i = 0; i < 10; i++) { ctx.beginPath(); ctx.arc(fx + (i < 5 ? -1 : 1) * (w * 0.2 + hash(i) * 14), h * 0.14 + hash(i * 7) * 8, 2.5, 0, Math.PI * 2); ctx.fill(); } }
  if (P.blush > 0 || P.sick > 0) { const a = Math.max(P.blush, P.sick * 0.8) * 0.45; for (const s of [-1, 1]) { const g = ctx.createRadialGradient(fx + s * w * 0.27, h * 0.13, 0, fx + s * w * 0.27, h * 0.13, w * 0.14); g.addColorStop(0, `rgba(230,90,80,${a})`); g.addColorStop(1, 'rgba(230,90,80,0)'); ctx.fillStyle = g; ctx.fillRect(-w, -h, 2 * w, 2 * h); } }
  for (const s of [-1, 1]) drawEye(ctx, fx + s * ex * (1 - 0.18 * s * P.turn), ey, erx, ery, P, s, skin, sp);
  if (sp.glasses === 'spectacles') {
    ctx.lineWidth = 4; ctx.strokeStyle = '#3a2a1a';
    for (const s of [-1, 1]) { ctx.beginPath(); ctx.arc(fx + s * ex, ey, erx * 1.45, 0, Math.PI * 2); ctx.stroke(); ctx.fillStyle = 'rgba(220,240,255,0.18)'; ctx.fill(); }
    line(ctx, [[fx - ex + erx * 1.45, ey], [fx + ex - erx * 1.45, ey]], 4, '#3a2a1a');
    ctx.save(); ctx.globalAlpha = 0.7; line(ctx, [[fx - ex - 6, ey - 12], [fx - ex + 4, ey - 20]], 3, '#ffffff'); line(ctx, [[fx + ex - 6, ey - 12], [fx + ex + 4, ey - 20]], 3, '#ffffff'); ctx.restore();
  }
  if (sp.glasses === 'goggles') {
    line(ctx, [[-w * 0.5, ey - 4], [w * 0.5, ey - 4]], 8, '#5a3a22');
    for (const s of [-1, 1]) shape(ctx, c => { c.arc(fx + s * ex, ey, erx * 1.55, 0, Math.PI * 2); c.arc(fx + s * ex, ey, erx * 1.2, 0, Math.PI * 2, true); }, '#c8913a', { lw: 4, tex: false });
    ctx.save(); ctx.globalAlpha = 0.25; ctx.fillStyle = '#bfe8ff'; for (const s of [-1, 1]) { ctx.beginPath(); ctx.arc(fx + s * ex, ey, erx * 1.2, 0, Math.PI * 2); ctx.fill(); } ctx.restore();
  }
  const by = ey - ery * (P.eyes === 'wide' ? 1.75 : 1.45), B = P.brows;
  drawBrow(ctx, fx - ex, by, erx * 2.2, -1, B[0], B[1], sp.brows || INK);
  drawBrow(ctx, fx + ex, by, erx * 2.2, 1, B[2], B[3], sp.brows || INK);
  const nx = fx * 1.25 + w * 0.02, ny = h * 0.12;
  const noseC = P.sick > 0 ? mixh(skin, '#e2675c', P.sick * 0.55) : mixh(skin, '#d98a6a', 0.25);
  if (sp.nose === 'potato') shape(ctx, c => { c.ellipse(nx + 4, ny, w * 0.13, h * 0.1, 0, 0, Math.PI * 2); }, noseC, { lw: 4.5, tex: false, hi: { x: nx + 10, y: ny - 8, r: 18, a: 0.5 } });
  else if (sp.nose === 'long') shape(ctx, c => { c.moveTo(nx - 6, ny - h * 0.12); c.quadraticCurveTo(nx + w * 0.3, ny + h * 0.02, nx + w * 0.16, ny + h * 0.09); c.quadraticCurveTo(nx, ny + h * 0.1, nx - 8, ny + h * 0.04); }, noseC, { lw: 4.5, tex: false });
  else if (sp.nose === 'hook') shape(ctx, c => { c.moveTo(nx - 4, ny - h * 0.14); c.quadraticCurveTo(nx + w * 0.28, ny - h * 0.08, nx + w * 0.14, ny + h * 0.1); c.quadraticCurveTo(nx + w * 0.04, ny + h * 0.05, nx - 6, ny + h * 0.07); }, noseC, { lw: 4.5, tex: false });
  else shape(ctx, ell(nx + 2, ny, w * 0.08, h * 0.065), noseC, { lw: 4.5, tex: false });
  const my = h * 0.3;
  drawMouth(ctx, fx * 1.2, my, w * 0.55, P);
  if (sp.mustache) shape(ctx, c => { const mx = fx * 1.2; c.moveTo(mx - 2, my - 12); c.quadraticCurveTo(mx - w * 0.25, my - 18, mx - w * 0.36, my + 10); c.quadraticCurveTo(mx - w * 0.2, my - 4, mx, my - 6); c.quadraticCurveTo(mx + w * 0.2, my - 4, mx + w * 0.36, my + 10); c.quadraticCurveTo(mx + w * 0.25, my - 18, mx + 2, my - 12); c.closePath(); }, '#2f2a28', { lw: 3, tex: false });
  if (sp.beard === 'pointy') {
    const sw = clamp(-P.vx * 0.03, -20, 20) + Math.sin(P.t * 2) * 3;
    shape(ctx, c => { c.moveTo(-w * 0.36, h * 0.2); c.quadraticCurveTo(-w * 0.3, h * 0.55, fx * 0.8 + w * 0.02 + sw, h * 0.86); c.quadraticCurveTo(w * 0.3, h * 0.55, w * 0.36, h * 0.2); c.quadraticCurveTo(w * 0.2, h * 0.42, fx * 1.2, h * 0.42); c.quadraticCurveTo(-w * 0.2, h * 0.42, -w * 0.36, h * 0.2); c.closePath(); }, sp.beardColor, { lw: 4.5, shade: { x0: w * 0.3, y0: h * 0.2, x1: -w * 0.3, y1: h * 0.8, a: 0.2 } });
    const mx = fx * 1.2;
    shape(ctx, c => { c.moveTo(mx - 4, my - 10); c.quadraticCurveTo(mx - w * 0.3, my - 20, mx - w * 0.4, my - 2); c.quadraticCurveTo(mx - w * 0.2, my - 4, mx, my - 4); c.quadraticCurveTo(mx + w * 0.2, my - 4, mx + w * 0.4, my - 2); c.quadraticCurveTo(mx + w * 0.3, my - 20, mx + 4, my - 10); c.closePath(); }, sp.beardColor, { lw: 4 });
  }
  if (sp.hat === 'tall') {
    const sq = Math.sin(P.t * 2.1) * 2 - clamp(P.vx * 0.01, -8, 8);
    shape(ctx, c => { c.moveTo(-w * 0.5, -h * 0.34); c.bezierCurveTo(-w * 0.72, -h * 0.9, -w * 0.2, -h * 1.12 + sq, w * 0.12, -h * 1.05 + sq); c.bezierCurveTo(w * 0.62, -h * 0.98, w * 0.72, -h * 0.62, w * 0.5, -h * 0.34); c.quadraticCurveTo(0, -h * 0.44, -w * 0.5, -h * 0.34); c.closePath(); }, sp.hatColor, { lw: 5, shade: { x0: w * 0.3, y0: -h, x1: -w * 0.5, y1: -h * 0.3, a: 0.32 }, hi: { x: w * 0.1, y: -h * 0.85, r: w * 0.4, a: 0.25 } });
    ctx.save(); ctx.globalAlpha = 0.5; curve(ctx, [-w * 0.25, -h * 0.45], [-w * 0.1, -h * 0.8], [w * 0.1, -h * 1.0 + sq], 3.5, sp.hatDark); curve(ctx, [w * 0.2, -h * 0.45], [w * 0.3, -h * 0.75], [w * 0.15, -h * 0.98 + sq], 3.5, sp.hatDark); ctx.restore();
    shape(ctx, c => { c.moveTo(-w * 0.54, -h * 0.28); c.quadraticCurveTo(0, -h * 0.44, w * 0.54, -h * 0.28); c.lineTo(w * 0.52, -h * 0.42); c.quadraticCurveTo(0, -h * 0.58, -w * 0.52, -h * 0.42); c.closePath(); }, sp.hatDark, { lw: 4.5 });
  }
  if (P.chalk > 0) { ctx.save(); ctx.globalAlpha = P.chalk; line(ctx, [[w * 0.02, -h * 0.62], [w * 0.16, -h * 0.5]], 7, '#ffffff'); line(ctx, [[w * 0.16, -h * 0.62], [w * 0.02, -h * 0.5]], 7, '#ffffff'); ctx.restore(); }
  if (P.sweat > 0) for (let i = 0; i < 3; i++) {
    const k = ((P.t * 1.4 + i * 0.33) % 1), a = P.sweat * (1 - k), sx = (i === 1 ? -1 : 1) * w * (0.48 + 0.04 * i), sy = -h * 0.25 + k * h * 0.35;
    ctx.save(); ctx.globalAlpha = a; shape(ctx, c => { c.moveTo(sx, sy - 16); c.quadraticCurveTo(sx + 10, sy + 2, sx, sy + 8); c.quadraticCurveTo(sx - 10, sy + 2, sx, sy - 16); }, '#bfe6ff', { lw: 3.5, tex: false }); ctx.restore();
  }
  if (P.tears > 0) for (const s of [-1, 1]) { ctx.save(); ctx.globalAlpha = P.tears; const k = (P.t * 2 + (s > 0 ? 0.5 : 0)) % 1; shape(ctx, ell(fx + s * ex, ey + ery + 10 + k * 60, 7, 11), '#bfe6ff', { lw: 3, tex: false }); ctx.restore(); }
  if (P.bandage > 0) {
    ctx.save(); ctx.globalAlpha = P.bandage;
    shape(ctx, c => { c.moveTo(-w * 0.56, -h * 0.28); c.quadraticCurveTo(0, -h * 0.5, w * 0.56, -h * 0.28); c.lineTo(w * 0.52, -h * 0.12); c.quadraticCurveTo(0, -h * 0.32, -w * 0.52, -h * 0.12); c.closePath(); }, '#f4ecdc', { lw: 4.5 });
    shape(ctx, c => { c.moveTo(-w * 0.3, -h * 0.42); c.quadraticCurveTo(0, -h * 0.66, w * 0.34, -h * 0.4); c.lineTo(w * 0.24, -h * 0.3); c.quadraticCurveTo(0, -h * 0.5, -w * 0.22, -h * 0.32); c.closePath(); }, '#efe4d0', { lw: 4.5 });
    shape(ctx, c => { c.moveTo(-w * 0.58, -h * 0.22); c.lineTo(-w * 0.75, -h * 0.16 + Math.sin(P.t * 4) * 6); c.lineTo(-w * 0.7, -h * 0.06 + Math.sin(P.t * 4 + 1) * 6); c.lineTo(-w * 0.55, -h * 0.14); c.closePath(); }, '#f4ecdc', { lw: 4 });
    ctx.restore();
  }
  ctx.restore();
}

// ------------------------------------------------------------------ body
function drawPerson(ctx, who, Pin) {
  const P = P0(Pin), sp = typeof who === 'string' ? SPECS[who] : who;
  const L = sp.legL, thigh = L * 0.52, shin = L * 0.48, bw = sp.bodyW || 1, t = P.t;
  const robe = sp.torso === 'robe';
  const sitting = P.sit > 0.5;
  const hipY = sitting ? -shin : -L;
  const breath = 1 + 0.018 * P.breath * Math.sin(t * 2.3);
  const torsoH = (150 + (robe ? 10 : 0)) * breath, neckY = hipY - torsoH;
  const shX = 50 * bw, shY = neckY + 16;
  ctx.save(); ctx.globalAlpha = P.alpha;
  const shv = P.shiver ? [Math.sin(t * 90) * P.shiver * 3, Math.cos(t * 77) * P.shiver * 2] : [0, 0];
  ctx.translate(P.x + shv[0], P.y + shv[1]);
  // squash & stretch preserve volume, anchored at the feet
  const sq = P.squash; ctx.scale(P.s * P.face * (1 + sq * 0.35), P.s * (1 - sq * 0.35));
  if (P.rot) { if (P.piv === 'hip') { ctx.translate(0, hipY); ctx.rotate(P.rot * D2R * P.face); ctx.translate(0, -hipY); } else ctx.rotate(P.rot * D2R * P.face); }
  ctx.translate(0, -P.bob);
  const hx = P.hip;                                   // weight shift: hips slide, shoulders counter-tilt
  const lean = P.lean - P.hip * 0.25;
  const up = fn => { ctx.save(); ctx.translate(hx, hipY); ctx.rotate(lean * D2R); ctx.translate(0, -hipY); fn(); ctx.restore(); };
  const legAng = (side, a) => sitting ? [88 + a[0] * 0.15, 88 + a[1] * 0.2] : a;
  const drawLeg = (side, ang0) => {
    const ang = legAng(side, ang0);
    const h = [hx + side * 22 * bw, hipY], k = pt(h[0], h[1], ang[0], thigh), a = pt(k[0], k[1], ang[0] - ang[1], shin);
    const ctrl = [2 * k[0] - (h[0] + a[0]) / 2, 2 * k[1] - (h[1] + a[1]) / 2];
    if (!robe || sitting) {
      ctx.lineJoin = ctx.lineCap = 'round';
      const go = () => { ctx.beginPath(); ctx.moveTo(h[0], h[1]); ctx.quadraticCurveTo(ctrl[0], ctrl[1], a[0], a[1]); };
      go(); ctx.lineWidth = 34; ctx.strokeStyle = INK; ctx.stroke(); go(); ctx.lineWidth = 25; ctx.strokeStyle = robe ? sp.robeDark : sp.hose; ctx.stroke();
    }
    const fa = (ang[0] - ang[1]) * 0.45;
    shape(ctx, c => { c.save(); c.translate(a[0], a[1]); c.rotate(-fa * D2R); c.moveTo(-16, -10); c.quadraticCurveTo(14, -18, 46, 4); c.quadraticCurveTo(44, 12, 20, 12); c.lineTo(-16, 11); c.quadraticCurveTo(-22, 0, -16, -10); c.closePath(); c.restore(); }, sp.shoe, { lw: 4.5, tex: false, hi: { x: a[0] + 10, y: a[1] - 8, r: 20, a: 0.25 } });
  };
  const armGeo = (side, ang) => { const s = [side * shX, shY + 4]; const e = pt(s[0], s[1], ang[0], 74); const w = pt(e[0], e[1], ang[0] + ang[1], 66); return [s, e, w, ang[0] + ang[1]]; };
  const drawArm = (side, ang, kind, prop) => {
    const [s, e, w, fa] = armGeo(side, ang);
    const sleeve = sp.sleeve || sp.tunic, skin = P.pale > 0 ? mixh(sp.skin, '#c3d3a0', P.pale * 0.8) : sp.skin;
    const ctrl = [2 * e[0] - (s[0] + w[0]) / 2, 2 * e[1] - (s[1] + w[1]) / 2];
    const mid = [(s[0] + 2 * ctrl[0] + w[0]) / 4, (s[1] + 2 * ctrl[1] + w[1]) / 4];
    ctx.lineJoin = ctx.lineCap = 'round';
    // upper arm (sleeve) then forearm with cuff
    const seg = (p0, c, p1, wd, col) => { const go = () => { ctx.beginPath(); ctx.moveTo(p0[0], p0[1]); ctx.quadraticCurveTo(c[0], c[1], p1[0], p1[1]); }; go(); ctx.lineWidth = wd + 9; ctx.strokeStyle = INK; ctx.stroke(); go(); ctx.lineWidth = wd; ctx.strokeStyle = col; ctx.stroke(); };
    const c1 = [(s[0] + ctrl[0]) / 2, (s[1] + ctrl[1]) / 2], c2 = [(ctrl[0] + w[0]) / 2, (ctrl[1] + w[1]) / 2];
    seg(s, c1, mid, 34, sleeve);
    seg(mid, c2, w, robe ? 30 : 24, robe ? sleeve : skin);
    if (robe && sp.trim) { ctx.save(); ctx.translate(w[0], w[1]); ctx.rotate(-fa * D2R); shape(ctx, c => c.roundRect(-20, -20, 40, 12, 5), sp.trim, { lw: 3.5, tex: false }); ctx.restore(); }
    ctx.save(); ctx.translate(w[0], w[1]); ctx.rotate(-fa * D2R);
    if (prop) { ctx.save(); ctx.translate(0, 18); ctx.rotate((prop.rot || 0) * D2R); ctx.scale(prop.s || 1, prop.s || 1); prop.fn(ctx, t); ctx.restore(); }
    hand(ctx, prop && kind === 'relaxed' ? 'grip' : kind, skin, side * P.face);
    ctx.restore();
  };

  drawLeg(-1, P.legL);
  up(() => drawArm(-1, P.armL, P.handL, P.propL));
  drawLeg(1, P.legR);
  up(() => {
    const sw = P.sway !== undefined ? P.sway * 10 : 0;
    const drag = clamp(-P.vx * 0.025, -26, 26) + Math.sin(t * 2.2) * 2 + sw;
    if (!robe) {
      const hemY = hipY + 28;
      shape(ctx, c => {
        c.moveTo(-shX, shY - 4); c.quadraticCurveTo(0, neckY - 6, shX, shY - 4);
        c.quadraticCurveTo(shX + 10, hipY - 60, 44 * bw + 6, hipY - 40);
        c.quadraticCurveTo(66 * bw + drag, hemY - 10, 64 * bw + drag, hemY + 6);
        for (let i = 0; i <= 6; i++) { const u = i / 6; c.lineTo(lerp(64 * bw + drag, -64 * bw + drag * 1.2, u), hemY + 6 + (i % 2 ? 10 : 0)); }
        c.quadraticCurveTo(-66 * bw + drag, hemY - 10, -44 * bw - 6, hipY - 40);
        c.quadraticCurveTo(-shX - 10, hipY - 60, -shX, shY - 4); c.closePath();
      }, sp.tunic, { lw: 5, shade: { x0: 40, y0: neckY, x1: -60, y1: hipY + 30, a: 0.3 }, hi: { x: 20, y: neckY + 40, r: 90, a: 0.15 } });
      if (sp.patch && sp.patch !== sp.tunic) { shape(ctx, c => c.rect(14 * bw, hipY - 92, 30, 28), sp.patch, { lw: 3.5 }); ctx.save(); ctx.setLineDash([5, 5]); line(ctx, [[16 * bw, hipY - 90], [42 * bw, hipY - 90]], 2); ctx.restore(); }
      shape(ctx, c => { c.moveTo(-50 * bw, hipY - 44); c.quadraticCurveTo(0, hipY - 34, 50 * bw, hipY - 44); c.lineTo(50 * bw, hipY - 30); c.quadraticCurveTo(0, hipY - 20, -50 * bw, hipY - 30); c.closePath(); }, sp.belt, { lw: 4, tex: false });
      tube(ctx, [[10, hipY - 30], [6 + Math.sin(t * 3) * 3 + drag * 0.3, hipY + 6]], 6, sp.belt, 3);
    } else {
      const hemY = sitting ? hipY + 40 : -14, hw = (sitting ? 70 : 78) * bw;
      shape(ctx, c => {
        c.moveTo(-shX, shY - 4); c.quadraticCurveTo(0, neckY - 8, shX, shY - 4);
        c.quadraticCurveTo(shX + 12 * bw, hipY - 20, hw + drag, hemY);
        for (let i = 0; i <= 8; i++) { const u = i / 8; c.lineTo(lerp(hw + drag, -hw + drag * 1.3, u), hemY + (i % 2 ? 8 : 0) + Math.sin(t * 4 + i) * 2); }
        c.quadraticCurveTo(-shX - 12 * bw, hipY - 20, -shX, shY - 4); c.closePath();
      }, sp.robe, { lw: 5, shade: { x0: 50, y0: neckY, x1: -80, y1: 0, a: 0.32 }, hi: { x: 25, y: neckY + 50, r: 110, a: 0.12 } });
      ctx.save(); ctx.globalAlpha = 0.55; for (const fxp of [-0.45, 0.1, 0.5]) curve(ctx, [fxp * hw * 0.6, hipY + 10], [fxp * hw * 0.8 + drag * 0.5, (hipY + hemY) / 2], [fxp * hw + drag, hemY - 4], 3.5, sp.robeDark); ctx.restore();
      if (sp.trim) { line(ctx, [[0, neckY + 4], [drag * 0.4, hemY]], 10, sp.trim); line(ctx, [[0, neckY + 4], [drag * 0.4, hemY]], 3, sp.robeDark); }
      if (sp.apron) { shape(ctx, c => { c.moveTo(-40 * bw, shY + 22); c.lineTo(40 * bw, shY + 22); c.quadraticCurveTo(50 * bw, hipY, 56 * bw + drag * 0.6, hemY - 18); c.lineTo(-56 * bw + drag * 0.6, hemY - 18); c.quadraticCurveTo(-50 * bw, hipY, -40 * bw, shY + 22); c.closePath(); }, sp.apron, { lw: 4.5, shade: { x0: 40, y0: shY, x1: -50, y1: 0, a: 0.3 } }); tube(ctx, [[-40 * bw, shY + 22], [-24 * bw, neckY + 4]], 6, sp.apronDark, 3); tube(ctx, [[40 * bw, shY + 22], [24 * bw, neckY + 4]], 6, sp.apronDark, 3); }
      if (sp === SPECS.doc2) shape(ctx, c => c.roundRect(-22, hipY - 40, 44, 34, 6), sp.apronDark, { lw: 3.5, tex: false });
    }
    ctx.save(); ctx.translate(0, neckY - sp.headH * 0.38); ctx.rotate(P.tilt * D2R); drawHead(ctx, sp, P); ctx.restore();
    drawArm(1, P.armR, P.handR, P.propR);
  });
  ctx.restore();
}
// head position (world) of a character pose, for camera framing
function headY(who, P) { const sp = SPECS[who]; const L = sp.legL; return (P.y || 0) - (P.s || 1) * ((P.sit ? L * 0.48 : L) + 150 + (sp.torso === 'robe' ? 10 : 0) + sp.headH * 0.38); }


// ---- shoulder position + 2-bone IK so hands can genuinely reach objects
function shoulderWorld(who, P, side) {
  const sp = SPECS[who], L = sp.legL, bw = sp.bodyW || 1, robe = sp.torso === 'robe', s = P.s || 1, face = P.face || 1;
  const hipY = P.sit ? -L * 0.48 : -L, neckY = hipY - (150 + (robe ? 10 : 0)), shY = neckY + 16 + 4;
  const hx = P.hip || 0, lean = ((P.lean || 0) - hx * 0.25) * D2R;
  let lx = side * 50 * bw, ly = shY - hipY; const rx = lx * Math.cos(lean) - ly * Math.sin(lean), ry = lx * Math.sin(lean) + ly * Math.cos(lean);
  lx = hx + rx; ly = hipY + ry - (P.bob || 0);
  return [P.x + s * face * lx, (P.y || 0) + s * ly];
}
function ik(who, P, side, target, bendOut = 1) {
  const s = P.s || 1, face = P.face || 1, sh = shoulderWorld(who, P, side);
  const lean = ((P.lean || 0) - (P.hip || 0) * 0.25) * D2R;
  let dx = (target[0] - sh[0]) / (s * face), dy = (target[1] - sh[1]) / s;
  const ux = dx * Math.cos(-lean) - dy * Math.sin(-lean), uy = dx * Math.sin(-lean) + dy * Math.cos(-lean); dx = ux; dy = uy;
  const L1 = 74, L2 = 66; let d = Math.hypot(dx, dy); d = Math.min(d, L1 + L2 - 0.5);
  const phi = Math.atan2(dx, dy), inner = Math.acos(clamp((L1 * L1 + d * d - L2 * L2) / (2 * L1 * d), -1, 1));
  const a1 = phi + bendOut * inner;
  const ex = Math.sin(a1) * L1, ey = Math.cos(a1) * L1;
  const a2 = Math.atan2(dx - ex, dy - ey);
  return [a1 / D2R, (a2 - a1) / D2R];
}
module.exports = { shoulderWorld, ik, SPECS, BROWS, P0, blend, act, walk, run, flail, idle, blink, drawPerson, drawHead, hand, headY };
