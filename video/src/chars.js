// Character rig: one drawing routine, four consistent characters + extras.
const C = require('./core');
const { lerp, clamp, D2R, hash, mixh } = C;
const { INK, PAL, shape, tube, tubeCurve, line, curve, ell } = require('./draw');

const SPECS = {
  villager: {
    skin: '#f1c49b', tunic: '#7d8a3d', tunicDark: '#58622a', patch: '#b07a3e', belt: '#5a3a22', hose: '#6e4c36', shoe: '#4a2f1e',
    hood: '#c98a2e', hoodDark: '#9a6420', nose: 'potato', stubble: true, headW: 152, headH: 170, legL: 165, torso: 'tunic',
    bodyW: 1, brows: '#5a3a22', ear: true,
  },
  doc1: { // bloodletter: confident, overly serious
    skin: '#eec09a', robe: '#3b2c41', robeDark: '#261b2b', trim: '#b2392d', hat: 'tall', hatColor: '#b2392d', hatDark: '#7f2620',
    beard: 'pointy', beardColor: '#efe7da', brows: '#efe7da', nose: 'long', glasses: 'spectacles', headW: 140, headH: 166, legL: 185,
    torso: 'robe', bodyW: 1.05, shoe: '#2a1d16', sleeve: '#3b2c41', ear: true, hairSide: '#efe7da',
  },
  doc2: { // leech doctor: eccentric, cheerful
    skin: '#f3c9a2', robe: '#d39a35', robeDark: '#a8741f', apron: '#2f6a60', apronDark: '#1f4943', hair: 'wild', hairColor: '#d4602b',
    brows: '#b4481c', nose: 'round', glasses: 'goggles', freckles: true, headW: 162, headH: 160, legL: 135, torso: 'robe', bodyW: 1.32,
    shoe: '#3a2618', sleeve: '#d39a35', ear: true,
  },
  doc3: { // surgeon: intimidating, calm
    skin: '#e6bb95', robe: '#3e4a52', robeDark: '#28323a', apron: '#7b4b2b', apronDark: '#5a3520', hair: 'bald', hairColor: '#3a3a3a',
    brows: '#2f2a28', nose: 'hook', mustache: true, headW: 128, headH: 188, legL: 200, torso: 'robe', bodyW: 0.95,
    shoe: '#1f1a17', sleeve: '#3e4a52', ear: true, darkCircles: true,
  },
  extraA: { skin: '#e9b98e', tunic: '#8a3b2e', tunicDark: '#652a21', patch: '#8a3b2e', belt: '#4a2f1e', hose: '#5a4a3a', shoe: '#3a2618', hair: 'cap', hairColor: '#4a6a7a', nose: 'round', headW: 140, headH: 156, legL: 150, torso: 'tunic', bodyW: 1.1, brows: '#3a2618', ear: true },
  extraB: { skin: '#f0c8a4', robe: '#5b6f8c', robeDark: '#40516a', trim: '#e3d3b0', hair: 'coif', hairColor: '#f2ead9', nose: 'round', headW: 136, headH: 156, legL: 150, torso: 'robe', bodyW: 1.0, brows: '#6a4a30', shoe: '#3a2618', sleeve: '#5b6f8c', ear: false },
};

// default pose
function P0(o = {}) {
  return Object.assign({
    x: 0, y: 0, s: 1, face: 1, lean: 0, bob: 0, squash: 0, rot: 0, turn: 0.15, tilt: 0,
    armL: [8, 10], armR: [-8, 10], legL: [3, 0], legR: [-3, 0], sway: 0, tail: 0, shiver: 0,
    eyes: 'open', lid: 0, pupil: 1, look: [0.15, 0], brows: 'neutral', mouth: 'flat', open: 0.5,
    sweat: 0, pale: 0, blush: 0, sick: 0, tears: 0, bandage: 0, bump: 0,
    propL: null, propR: null, t: 0, alpha: 1,
  }, o);
}
function blend(a, b, k) {
  const out = {};
  for (const key in a) {
    const va = a[key], vb = b[key] === undefined ? va : b[key];
    if (typeof va === 'number' && typeof vb === 'number') out[key] = lerp(va, vb, k);
    else if (Array.isArray(va) && Array.isArray(vb) && typeof va[0] === 'number') out[key] = va.map((v, i) => lerp(v, vb[i], k));
    else out[key] = k < 0.5 ? va : vb;
  }
  for (const key in b) if (out[key] === undefined) out[key] = b[key];
  return out;
}

// walk / run cycles -> partial pose
function walk(ph, amp = 1) {
  const s = Math.sin(ph), c = Math.cos(ph);
  return {
    legL: [24 * s * amp, Math.max(0, 40 * Math.sin(ph - 1.3)) * amp], legR: [-24 * s * amp, Math.max(0, 40 * Math.sin(ph + Math.PI - 1.3)) * amp],
    armL: [-22 * s * amp, 14 + 6 * amp], armR: [22 * s * amp, 14 + 6 * amp], bob: 7 * Math.abs(c) * amp, sway: s * 0.6,
  };
}
function run(ph, amp = 1) {
  const s = Math.sin(ph), c = Math.cos(ph);
  return {
    legL: [45 * s * amp, 20 + Math.max(0, 75 * Math.sin(ph - 1.1)) * amp], legR: [-45 * s * amp, 20 + Math.max(0, 75 * Math.sin(ph + Math.PI - 1.1)) * amp],
    armL: [-55 * s * amp, 70], armR: [55 * s * amp, 70], bob: 14 * Math.abs(c) * amp, lean: 12 * amp, sway: s,
  };
}
// arms flailing in panic
function flail(t, amp = 1) {
  return { armL: [150 + 30 * Math.sin(t * 22), 40 + 30 * Math.sin(t * 17)], armR: [-150 + 30 * Math.sin(t * 19 + 1), 40 + 30 * Math.sin(t * 23)] };
}

const pt = (x, y, a, L) => [x + Math.sin(a * D2R) * L, y + Math.cos(a * D2R) * L];

// ------------------------------------------------------------------ head & face
function headPath(w, h) {
  return c => {
    c.moveTo(0, -h / 2);
    c.bezierCurveTo(w * 0.6, -h / 2, w * 0.6, h * 0.16, w * 0.3, h * 0.42);
    c.bezierCurveTo(w * 0.16, h * 0.53, -w * 0.16, h * 0.53, -w * 0.3, h * 0.42);
    c.bezierCurveTo(-w * 0.6, h * 0.16, -w * 0.6, -h / 2, 0, -h / 2);
    c.closePath();
  };
}

function drawEye(ctx, ex, ey, rx, ry, P, side, skin, sp) {
  const kind = P.eyes;
  if (kind === 'closed' || kind === 'happy') {
    const dy = kind === 'happy' ? -ry * 0.1 : ry * 0.1;
    if (kind === 'happy') curve(ctx, [ex - rx, ey + dy + 4], [ex, ey - ry * 0.9 + dy], [ex + rx, ey + dy + 4], 5);
    else curve(ctx, [ex - rx, ey], [ex, ey + ry * 0.5], [ex + rx, ey], 5);
    return;
  }
  if (kind === 'dead') { line(ctx, [[ex - rx * 0.7, ey - ry * 0.6], [ex + rx * 0.7, ey + ry * 0.6]], 5); line(ctx, [[ex + rx * 0.7, ey - ry * 0.6], [ex - rx * 0.7, ey + ry * 0.6]], 5); return; }
  const big = kind === 'wide' ? 1.32 : 1;
  const RX = rx * big, RY = ry * big;
  if (sp.darkCircles || P.sick > 0.3) {
    ctx.fillStyle = `rgba(120,70,90,${sp.darkCircles ? 0.25 : 0.25 * P.sick})`;
    ctx.beginPath(); ctx.ellipse(ex, ey + RY * 0.55, RX * 1.05, RY * 0.6, 0, 0, Math.PI * 2); ctx.fill();
  }
  shape(ctx, ell(ex, ey, RX, RY), '#fffaf0', { lw: 4.5, tex: false });
  if (kind === 'spiral') {
    ctx.beginPath();
    for (let a = 0; a < 14; a += 0.2) { const r = a * RX * 0.06; const an = a + P.t * 9 * side; ctx.lineTo(ex + Math.cos(an) * r, ey + Math.sin(an) * r); }
    ctx.lineWidth = 3.5; ctx.strokeStyle = INK; ctx.stroke();
  } else {
    const pr = RX * 0.42 * P.pupil * (kind === 'wide' ? 0.55 : 1);
    const px = ex + P.look[0] * RX * 0.45, py = ey + P.look[1] * RY * 0.4;
    ctx.fillStyle = INK; ctx.beginPath(); ctx.ellipse(px, py, pr, pr * 1.12, 0, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = 'rgba(255,255,255,0.9)'; ctx.beginPath(); ctx.arc(px - pr * 0.35, py - pr * 0.4, pr * 0.28, 0, Math.PI * 2); ctx.fill();
  }
  const lid = clamp(P.lid);
  if (lid > 0.01) {
    ctx.save(); ctx.beginPath(); ctx.ellipse(ex, ey, RX + 1, RY + 1, 0, 0, Math.PI * 2); ctx.clip();
    const yl = ey - RY + 2 * RY * lid;
    ctx.fillStyle = skin; ctx.fillRect(ex - RX - 3, ey - RY - 3, 2 * RX + 6, yl - (ey - RY) + 3);
    ctx.restore();
    const ww = RX * Math.sqrt(Math.max(0, 1 - Math.pow((yl - ey) / RY, 2)));
    line(ctx, [[ex - ww - 1, yl], [ex + ww + 1, yl]], 4.5);
  }
}

function drawBrow(ctx, bx, by, w, side, kind, color) {
  // side: -1 left (screen), +1 right. inner end is toward 0.
  let inner = 0, outer = 0, lift = 0;
  if (kind === 'worried') { inner = -12; outer = 4; }
  else if (kind === 'angry') { inner = 10; outer = -6; }
  else if (kind === 'raised') { lift = -16; inner = -4; outer = -4; }
  else if (kind === 'skeptic') { if (side > 0) { lift = -16; inner = -6; } else { inner = 6; } }
  else if (kind === 'sad') { inner = -10; outer = 6; }
  else if (kind === 'calm') { inner = 3; outer = 3; }
  const xi = bx - side * w * 0.5, xo = bx + side * w * 0.5;
  ctx.lineCap = 'round'; ctx.lineWidth = 9; ctx.strokeStyle = color;
  ctx.beginPath(); ctx.moveTo(xi, by + inner + lift); ctx.quadraticCurveTo(bx, by - 5 + lift + (inner + outer) / 2, xo, by + outer + lift); ctx.stroke();
}

function drawMouth(ctx, mx, my, w, P, sp) {
  const m = P.mouth, o = clamp(P.open);
  ctx.lineCap = 'round';
  const darkFill = '#5a1f1c', tongue = '#d4635a';
  if (m === 'flat') line(ctx, [[mx - w * 0.3, my], [mx + w * 0.3, my]], 5);
  else if (m === 'smile') curve(ctx, [mx - w * 0.42, my - 6], [mx, my + 18], [mx + w * 0.42, my - 6], 5);
  else if (m === 'frown') curve(ctx, [mx - w * 0.36, my + 8], [mx, my - 12], [mx + w * 0.36, my + 8], 5);
  else if (m === 'smirk') curve(ctx, [mx - w * 0.32, my + 4], [mx + w * 0.05, my + 8], [mx + w * 0.38, my - 10], 5);
  else if (m === 'wavy') { ctx.beginPath(); for (let i = 0; i <= 16; i++) { const u = i / 16; ctx.lineTo(mx - w * 0.38 + u * w * 0.76, my + Math.sin(u * Math.PI * 3 + P.t * 8) * 5); } ctx.lineWidth = 5; ctx.strokeStyle = INK; ctx.stroke(); }
  else if (m === 'grin' || m === 'chuckle') {
    const hh = (m === 'chuckle' ? 20 + 18 * o : 26);
    shape(ctx, c => { c.moveTo(mx - w * 0.45, my - 6); c.quadraticCurveTo(mx, my - 2, mx + w * 0.45, my - 6); c.quadraticCurveTo(mx + w * 0.3, my + hh, mx, my + hh); c.quadraticCurveTo(mx - w * 0.3, my + hh, mx - w * 0.45, my - 6); c.closePath(); }, darkFill, { lw: 5, tex: false });
    ctx.save(); ctx.beginPath(); ctx.moveTo(mx - w * 0.45, my - 6); ctx.quadraticCurveTo(mx, my - 2, mx + w * 0.45, my - 6); ctx.quadraticCurveTo(mx + w * 0.3, my + hh, mx, my + hh); ctx.quadraticCurveTo(mx - w * 0.3, my + hh, mx - w * 0.45, my - 6); ctx.clip();
    ctx.fillStyle = '#fffaf0'; ctx.fillRect(mx - w * 0.5, my - 10, w, 12);
    ctx.fillStyle = tongue; ctx.beginPath(); ctx.ellipse(mx, my + hh, w * 0.2, 10, 0, 0, Math.PI * 2); ctx.fill();
    ctx.restore();
  } else if (m === 'o' || m === 'scream' || m === 'sneeze' || m === 'gasp') {
    const rx = m === 'scream' ? w * (0.28 + 0.12 * o) : m === 'gasp' ? w * 0.18 : w * 0.16;
    const ry = m === 'scream' ? w * (0.3 + 0.25 * o) : m === 'gasp' ? w * (0.22 + 0.12 * o) : m === 'sneeze' ? w * 0.1 * (0.4 + o) : w * 0.18;
    shape(ctx, ell(mx, my + ry * 0.5, rx, ry), darkFill, { lw: 5, tex: false });
    ctx.save(); ctx.beginPath(); ctx.ellipse(mx, my + ry * 0.5, rx, ry, 0, 0, Math.PI * 2); ctx.clip();
    if (m === 'scream') { ctx.fillStyle = '#fffaf0'; ctx.fillRect(mx - rx, my + ry * 0.5 - ry - 2, rx * 2, ry * 0.28); }
    ctx.fillStyle = tongue; ctx.beginPath(); ctx.ellipse(mx, my + ry * 1.35, rx * 0.7, ry * 0.5, 0, 0, Math.PI * 2); ctx.fill();
    ctx.restore();
  } else if (m === 'teeth') {
    shape(ctx, c => c.roundRect(mx - w * 0.4, my - 10, w * 0.8, 26, 10), '#fffaf0', { lw: 5, tex: false });
    line(ctx, [[mx - w * 0.38, my + 3], [mx + w * 0.38, my + 3]], 3);
    for (let i = -2; i <= 2; i++) line(ctx, [[mx + i * w * 0.14, my - 9], [mx + i * w * 0.14, my + 15]], 3);
  } else if (m === 'cough') {
    shape(ctx, ell(mx, my + 4, w * 0.2, w * 0.13), darkFill, { lw: 5, tex: false });
  }
}

function drawHead(ctx, sp, P) {
  const w = sp.headW, h = sp.headH, t = P.t;
  const skin = P.pale > 0 ? mixh(sp.skin, '#c3d3a0', P.pale * 0.85) : sp.skin;
  const fx = clamp(P.turn, -1, 1) * w * 0.16;     // face shift with head turn
  // wild hair behind
  if (sp.hair === 'wild') {
    for (let i = 0; i < 9; i++) {
      const a = -Math.PI * 0.95 + i * Math.PI * 0.9 / 8 + Math.sin(t * 3 + i) * 0.05;
      const r0 = w * 0.42, r1 = w * (0.72 + 0.12 * Math.sin(i * 2.3));
      shape(ctx, c => { c.moveTo(Math.cos(a - 0.22) * r0, -h * 0.12 + Math.sin(a - 0.22) * r0); c.quadraticCurveTo(Math.cos(a) * r1 * 1.1, -h * 0.12 + Math.sin(a) * r1 * 1.1, Math.cos(a + 0.18) * r1, -h * 0.12 + Math.sin(a + 0.18) * r1); c.lineTo(Math.cos(a + 0.25) * r0, -h * 0.12 + Math.sin(a + 0.25) * r0); c.closePath(); }, sp.hairColor, { lw: 4.5 });
    }
  }
  if (sp.hood) {   // hood back + liripipe tail (secondary motion)
    const ta = (P.tail || 0) + Math.sin(t * 2.4) * 6 + P.sway * 8;
    const pts = [];
    for (let i = 0; i < 7; i++) {
      const u = i / 6, wav = Math.sin(t * 3.2 - i * 0.9) * 6 * u + ta * u * 1.6;
      pts.push([-w * 0.5 - u * w * 0.32 - wav * 0.6, -h * 0.12 + u * h * 0.95 + Math.abs(wav) * 0.2]);
    }
    tubeCurve(ctx, pts, 22, sp.hoodDark, 4.5);
    shape(ctx, c => { c.ellipse(-w * 0.02, -h * 0.02, w * 0.66, h * 0.62, 0, 0, Math.PI * 2); }, sp.hood, { lw: 5, shade: { x0: w * 0.4, y0: -h * 0.4, x1: -w * 0.6, y1: h * 0.5, a: 0.3 } });
  }
  if (sp.ear) shape(ctx, ell(-fx * 0.2 + (P.turn >= 0 ? -w * 0.47 : w * 0.47), h * 0.02, w * 0.09, h * 0.11), skin, { lw: 4.5, tex: false });
  shape(ctx, headPath(w, h), skin, { lw: 5, shade: { x0: w * 0.3, y0: -h * 0.3, x1: -w * 0.55, y1: h * 0.5, a: 0.22 }, hi: { x: w * 0.12 + fx, y: -h * 0.2, r: w * 0.4, a: 0.18 } });
  if (P.pale > 0.2) { ctx.save(); ctx.globalAlpha = P.pale * 0.25; ctx.beginPath(); headPath(w, h)(ctx); ctx.fillStyle = '#9fbf7a'; ctx.fill(); ctx.restore(); }
  // hair / hats on top of skull
  if (sp.hair === 'bald') {
    ctx.save(); ctx.globalAlpha = 0.5; curve(ctx, [-w * 0.2, -h * 0.47], [-w * 0.05, -h * 0.6], [w * 0.05, -h * 0.46], 2.5); curve(ctx, [w * 0.02, -h * 0.48], [w * 0.15, -h * 0.62], [w * 0.22, -h * 0.45], 2.5); ctx.restore();
    for (const sd of [-1, 1]) shape(ctx, c => { c.moveTo(sd * w * 0.5, -h * 0.02); c.quadraticCurveTo(sd * w * 0.56, -h * 0.18, sd * w * 0.47, -h * 0.26); c.lineTo(sd * w * 0.43, -h * 0.04); c.closePath(); }, '#5a5552', { lw: 3 });
  }
  if (sp.hair === 'cap') shape(ctx, c => { c.moveTo(-w * 0.55, -h * 0.12); c.quadraticCurveTo(-w * 0.5, -h * 0.72, w * 0.1, -h * 0.68); c.quadraticCurveTo(w * 0.6, -h * 0.6, w * 0.56, -h * 0.12); c.quadraticCurveTo(0, -h * 0.26, -w * 0.55, -h * 0.12); }, sp.hairColor, { lw: 5 });
  if (sp.hair === 'coif') shape(ctx, c => { c.moveTo(-w * 0.58, h * 0.25); c.quadraticCurveTo(-w * 0.7, -h * 0.75, 0, -h * 0.66); c.quadraticCurveTo(w * 0.7, -h * 0.75, w * 0.58, h * 0.25); c.quadraticCurveTo(w * 0.5, -h * 0.35, 0, -h * 0.4); c.quadraticCurveTo(-w * 0.5, -h * 0.35, -w * 0.58, h * 0.25); }, sp.hairColor, { lw: 5 });
  if (sp.hairSide) {
    for (const s of [-1, 1]) shape(ctx, c => { c.moveTo(s * w * 0.42, -h * 0.25); c.quadraticCurveTo(s * w * 0.6, -h * 0.05, s * w * 0.46, h * 0.16); c.lineTo(s * w * 0.38, -h * 0.05); c.closePath(); }, sp.hairSide, { lw: 4 });
  }
  if (sp.hood) {   // hood front rim framing the face
    ctx.save(); ctx.beginPath(); ctx.ellipse(-w * 0.02, -h * 0.02, w * 0.66, h * 0.62, 0, 0, Math.PI * 2); ctx.clip();
    shape(ctx, c => { c.moveTo(-w * 0.7, -h * 0.75); c.lineTo(w * 0.75, -h * 0.75); c.lineTo(w * 0.75, -h * 0.25); c.quadraticCurveTo(w * 0.25 + fx, -h * 0.48, -w * 0.4 + fx, -h * 0.25); c.quadraticCurveTo(-w * 0.62, -h * 0.05, -w * 0.62, h * 0.4); c.lineTo(-w * 0.7, h * 0.4); c.closePath(); }, sp.hood, { lw: 5, shade: { x0: w * 0.3, y0: -h * 0.6, x1: -w * 0.5, y1: h * 0.3, a: 0.25 } });
    ctx.restore();
    shape(ctx, c => { c.ellipse(-w * 0.02, -h * 0.02, w * 0.66, h * 0.62, 0, Math.PI * 0.94, Math.PI * 2.06); }, null, { lw: 5 });
  }
  // bump (head injury) & bandage
  if (P.bump > 0) shape(ctx, ell(w * 0.05, -h * 0.52, w * 0.13 * P.bump, h * 0.1 * P.bump), mixh(skin, '#e07a6a', 0.45), { lw: 4.5, tex: false });

  // ---- face ----
  const ex = w * 0.2, ey = -h * 0.02, erx = w * 0.12, ery = h * 0.135;
  if (sp.stubble) { ctx.fillStyle = 'rgba(70,45,30,0.35)'; for (let i = 0; i < 26; i++) { const a = Math.PI * (0.15 + 0.7 * ((hash(i * 3) + 1) / 2)), r = w * (0.33 + 0.08 * hash(i * 5)); ctx.beginPath(); ctx.arc(fx + Math.cos(a) * r, h * 0.12 + Math.sin(a) * r * 0.62, 2.2, 0, Math.PI * 2); ctx.fill(); } }
  if (sp.freckles) { ctx.fillStyle = 'rgba(170,90,50,0.5)'; for (let i = 0; i < 10; i++) { ctx.beginPath(); ctx.arc(fx + (i < 5 ? -1 : 1) * (w * 0.2 + hash(i) * 14), h * 0.14 + hash(i * 7) * 8, 2.5, 0, Math.PI * 2); ctx.fill(); } }
  if (P.blush > 0 || P.sick > 0) {
    const a = Math.max(P.blush, P.sick * 0.8) * 0.45;
    for (const s of [-1, 1]) { const g = ctx.createRadialGradient(fx + s * w * 0.27, h * 0.13, 0, fx + s * w * 0.27, h * 0.13, w * 0.14); g.addColorStop(0, `rgba(230,90,80,${a})`); g.addColorStop(1, 'rgba(230,90,80,0)'); ctx.fillStyle = g; ctx.fillRect(-w, -h, 2 * w, 2 * h); }
  }
  for (const s of [-1, 1]) drawEye(ctx, fx + s * ex * (1 - 0.18 * s * P.turn), ey, erx, ery, P, s, skin, sp);
  if (sp.glasses === 'spectacles') {
    ctx.lineWidth = 4; ctx.strokeStyle = '#3a2a1a';
    for (const s of [-1, 1]) { ctx.beginPath(); ctx.arc(fx + s * ex, ey, erx * 1.45, 0, Math.PI * 2); ctx.stroke(); ctx.fillStyle = 'rgba(220,240,255,0.18)'; ctx.fill(); }
    line(ctx, [[fx - ex + erx * 1.45, ey], [fx + ex - erx * 1.45, ey]], 4, '#3a2a1a');
    ctx.save(); ctx.globalAlpha = 0.7; line(ctx, [[fx - ex - 6, ey - 12], [fx - ex + 4, ey - 20]], 3, '#ffffff'); line(ctx, [[fx + ex - 6, ey - 12], [fx + ex + 4, ey - 20]], 3, '#ffffff'); ctx.restore();
  }
  if (sp.glasses === 'goggles') {
    ctx.lineWidth = 6; line(ctx, [[-w * 0.5, ey - 4], [w * 0.5, ey - 4]], 8, '#5a3a22');
    for (const s of [-1, 1]) { shape(ctx, c => { c.arc(fx + s * ex, ey, erx * 1.55, 0, Math.PI * 2); c.arc(fx + s * ex, ey, erx * 1.2, 0, Math.PI * 2, true); }, '#c8913a', { lw: 4, tex: false }); }
    ctx.save(); ctx.globalAlpha = 0.25; ctx.fillStyle = '#bfe8ff'; for (const s of [-1, 1]) { ctx.beginPath(); ctx.arc(fx + s * ex, ey, erx * 1.2, 0, Math.PI * 2); ctx.fill(); } ctx.restore();
  }
  const by = ey - ery * (P.eyes === 'wide' ? 1.75 : 1.45);
  for (const s of [-1, 1]) drawBrow(ctx, fx + s * ex, by, erx * 2.1, s, P.brows, sp.brows || INK);
  // nose
  const nx = fx * 1.25 + w * 0.02, ny = h * 0.12;
  const noseC = P.sick > 0 ? mixh(skin, '#e2675c', P.sick * 0.55) : mixh(skin, '#d98a6a', 0.25);
  if (sp.nose === 'potato') shape(ctx, c => { c.ellipse(nx + 4, ny, w * 0.13, h * 0.1, 0, 0, Math.PI * 2); }, noseC, { lw: 4.5, tex: false, hi: { x: nx + 10, y: ny - 8, r: 18, a: 0.5 } });
  else if (sp.nose === 'long') shape(ctx, c => { c.moveTo(nx - 6, ny - h * 0.12); c.quadraticCurveTo(nx + w * 0.3, ny + h * 0.02, nx + w * 0.16, ny + h * 0.09); c.quadraticCurveTo(nx, ny + h * 0.1, nx - 8, ny + h * 0.04); }, noseC, { lw: 4.5, tex: false });
  else if (sp.nose === 'hook') shape(ctx, c => { c.moveTo(nx - 4, ny - h * 0.14); c.quadraticCurveTo(nx + w * 0.28, ny - h * 0.08, nx + w * 0.14, ny + h * 0.1); c.quadraticCurveTo(nx + w * 0.04, ny + h * 0.05, nx - 6, ny + h * 0.07); }, noseC, { lw: 4.5, tex: false });
  else shape(ctx, ell(nx + 2, ny, w * 0.08, h * 0.065), noseC, { lw: 4.5, tex: false });
  if (P.sick > 0.4 && sp.nose === 'potato') { ctx.fillStyle = `rgba(200,230,255,${0.7 * P.sick})`; ctx.beginPath(); ctx.ellipse(nx - 6, ny + h * 0.13 + Math.sin(P.t * 2) * 2, 4, 7, 0, 0, Math.PI * 2); ctx.fill(); }
  // mouth
  const my = h * 0.3;
  drawMouth(ctx, fx * 1.2, my, w * 0.55, P, sp);
  if (sp.mustache) shape(ctx, c => { c.moveTo(fx * 1.2 - 2, my - 12); c.quadraticCurveTo(fx * 1.2 - w * 0.25, my - 18, fx * 1.2 - w * 0.36, my + 10); c.quadraticCurveTo(fx * 1.2 - w * 0.2, my - 4, fx * 1.2, my - 6); c.quadraticCurveTo(fx * 1.2 + w * 0.2, my - 4, fx * 1.2 + w * 0.36, my + 10); c.quadraticCurveTo(fx * 1.2 + w * 0.25, my - 18, fx * 1.2 + 2, my - 12); c.closePath(); }, '#2f2a28', { lw: 3, tex: false });
  if (sp.beard === 'pointy') {
    shape(ctx, c => { c.moveTo(-w * 0.36, h * 0.2); c.quadraticCurveTo(-w * 0.3, h * 0.55, fx * 0.8 + w * 0.02, h * 0.86 + Math.sin(P.t * 2) * 3); c.quadraticCurveTo(w * 0.3, h * 0.55, w * 0.36, h * 0.2); c.quadraticCurveTo(w * 0.2, h * 0.42, fx * 1.2, h * 0.42); c.quadraticCurveTo(-w * 0.2, h * 0.42, -w * 0.36, h * 0.2); c.closePath(); }, sp.beardColor, { lw: 4.5, shade: { x0: w * 0.3, y0: h * 0.2, x1: -w * 0.3, y1: h * 0.8, a: 0.2 } });
    shape(ctx, c => { c.moveTo(fx * 1.2 - 4, my - 10); c.quadraticCurveTo(fx * 1.2 - w * 0.3, my - 20, fx * 1.2 - w * 0.4, my - 2); c.quadraticCurveTo(fx * 1.2 - w * 0.2, my - 4, fx * 1.2, my - 4); c.quadraticCurveTo(fx * 1.2 + w * 0.2, my - 4, fx * 1.2 + w * 0.4, my - 2); c.quadraticCurveTo(fx * 1.2 + w * 0.3, my - 20, fx * 1.2 + 4, my - 10); c.closePath(); }, sp.beardColor, { lw: 4 });
  }
  // hats
  if (sp.hat === 'tall') {   // physician's bonnet: soft, puffed crown with a folded band
    const sq = Math.sin(P.t * 2.1) * 2;
    shape(ctx, c => { c.moveTo(-w * 0.5, -h * 0.34); c.bezierCurveTo(-w * 0.72, -h * 0.9, -w * 0.2, -h * 1.12 + sq, w * 0.12, -h * 1.05 + sq); c.bezierCurveTo(w * 0.62, -h * 0.98, w * 0.72, -h * 0.62, w * 0.5, -h * 0.34); c.quadraticCurveTo(0, -h * 0.44, -w * 0.5, -h * 0.34); c.closePath(); }, sp.hatColor, { lw: 5, shade: { x0: w * 0.3, y0: -h, x1: -w * 0.5, y1: -h * 0.3, a: 0.32 }, hi: { x: w * 0.1, y: -h * 0.85, r: w * 0.4, a: 0.25 } });
    ctx.save(); ctx.globalAlpha = 0.5; curve(ctx, [-w * 0.25, -h * 0.45], [-w * 0.1, -h * 0.8], [w * 0.1, -h * 1.0 + sq], 3.5, sp.hatDark); curve(ctx, [w * 0.2, -h * 0.45], [w * 0.3, -h * 0.75], [w * 0.15, -h * 0.98 + sq], 3.5, sp.hatDark); ctx.restore();
    shape(ctx, c => { c.moveTo(-w * 0.54, -h * 0.28); c.quadraticCurveTo(0, -h * 0.44, w * 0.54, -h * 0.28); c.lineTo(w * 0.52, -h * 0.42); c.quadraticCurveTo(0, -h * 0.58, -w * 0.52, -h * 0.42); c.closePath(); }, sp.hatDark, { lw: 4.5 });
  }
  // sweat, tears
  if (P.sweat > 0) {
    for (let i = 0; i < 3; i++) {
      const k = ((P.t * 1.4 + i * 0.33) % 1), a = P.sweat * (1 - k);
      const sx = (i === 1 ? -1 : 1) * w * (0.48 + 0.04 * i), sy = -h * 0.25 + k * h * 0.35;
      ctx.save(); ctx.globalAlpha = a;
      shape(ctx, c => { c.moveTo(sx, sy - 16); c.quadraticCurveTo(sx + 10, sy + 2, sx, sy + 8); c.quadraticCurveTo(sx - 10, sy + 2, sx, sy - 16); }, '#bfe6ff', { lw: 3.5, tex: false });
      ctx.restore();
    }
  }
  if (P.tears > 0) for (const s of [-1, 1]) { ctx.save(); ctx.globalAlpha = P.tears; const k = (P.t * 2 + (s > 0 ? 0.5 : 0)) % 1; shape(ctx, ell(fx + s * ex, ey + ery + 10 + k * 60, 7, 11), '#bfe6ff', { lw: 3, tex: false }); ctx.restore(); }
  if (P.bandage > 0) {
    ctx.save(); ctx.globalAlpha = P.bandage;
    shape(ctx, c => { c.moveTo(-w * 0.56, -h * 0.28); c.quadraticCurveTo(0, -h * 0.5, w * 0.56, -h * 0.28); c.lineTo(w * 0.52, -h * 0.12); c.quadraticCurveTo(0, -h * 0.32, -w * 0.52, -h * 0.12); c.closePath(); }, '#f4ecdc', { lw: 4.5 });
    shape(ctx, c => { c.moveTo(-w * 0.3, -h * 0.42); c.quadraticCurveTo(0, -h * 0.66, w * 0.34, -h * 0.4); c.lineTo(w * 0.24, -h * 0.3); c.quadraticCurveTo(0, -h * 0.5, -w * 0.22, -h * 0.32); c.closePath(); }, '#efe4d0', { lw: 4.5 });
    shape(ctx, c => { c.moveTo(-w * 0.58, -h * 0.22); c.lineTo(-w * 0.75, -h * 0.16 + Math.sin(P.t * 4) * 6); c.lineTo(-w * 0.7, -h * 0.06 + Math.sin(P.t * 4 + 1) * 6); c.lineTo(-w * 0.55, -h * 0.14); c.closePath(); }, '#f4ecdc', { lw: 4 });
    ctx.restore();
  }
}

// ------------------------------------------------------------------ body
function drawPerson(ctx, who, P) {
  const sp = typeof who === 'string' ? SPECS[who] : who;
  const L = sp.legL, thigh = L * 0.52, shin = L * 0.48, bw = sp.bodyW || 1;
  const hipY = -L, torsoH = 150 + (sp.torso === 'robe' ? 10 : 0), neckY = hipY - torsoH;
  const shX = 50 * bw, shY = neckY + 16;
  const t = P.t;
  ctx.save();
  ctx.globalAlpha = P.alpha;
  const shv = P.shiver ? [Math.sin(t * 90) * P.shiver * 3, Math.cos(t * 77) * P.shiver * 2] : [0, 0];
  ctx.translate(P.x + shv[0], P.y + shv[1]);
  ctx.rotate(P.rot * D2R);
  ctx.scale(P.s * P.face * (1 + P.squash * 0.35), P.s * (1 - P.squash * 0.35));
  ctx.translate(0, -P.bob);

  const hip = [0, hipY];
  const lean = P.lean;
  // transform for upper body: rotate around hip
  const up = (fn) => { ctx.save(); ctx.translate(hip[0], hip[1]); ctx.rotate(lean * D2R); ctx.translate(-hip[0], -hip[1]); fn(); ctx.restore(); };
  const legPts = (side, ang) => { const h = [side * 22 * bw, hipY]; const k = pt(h[0], h[1], ang[0], thigh); const a = pt(k[0], k[1], ang[0] - ang[1], shin); return [h, k, a]; };
  const drawLeg = (side, ang) => {
    const [h, k, a] = legPts(side, ang);
    if (sp.torso !== 'robe') tube(ctx, [h, k, a], 24, sp.hose, 4.5);
    const fa = (ang[0] - ang[1]) * 0.4;
    shape(ctx, c => { c.save(); c.translate(a[0], a[1]); c.rotate(-fa * D2R); c.moveTo(-14, -8); c.quadraticCurveTo(18, -16, 44, 4); c.quadraticCurveTo(20, 10, -14, 9); c.closePath(); c.restore(); }, sp.shoe, { lw: 4.5, tex: false });
  };
  const armPts = (side, ang) => { const s = [side * shX, shY]; const e = pt(s[0], s[1], ang[0], 72); const hnd = pt(e[0], e[1], ang[0] + ang[1], 66); return [s, e, hnd]; };
  const drawArm = (side, ang, prop) => {
    const [s, e, hnd] = armPts(side, ang);
    const sleeve = sp.sleeve || sp.tunic;
    tube(ctx, [s, e], 34, sleeve, 4.5);
    tube(ctx, [e, hnd], 26, sp.torso === 'robe' ? sleeve : sp.skin, 4.5);
    if (sp.torso === 'robe' && sp.trim) { ctx.save(); ctx.translate(hnd[0], hnd[1]); ctx.rotate(-(ang[0] + ang[1]) * D2R); shape(ctx, c => c.roundRect(-19, -22, 38, 12, 5), sp.trim, { lw: 3.5, tex: false }); ctx.restore(); }
    shape(ctx, ell(hnd[0], hnd[1], 17, 17), P.pale > 0 ? mixh(sp.skin, '#c3d3a0', P.pale * 0.8) : sp.skin, { lw: 4.5, tex: false });
    if (prop) { ctx.save(); ctx.translate(hnd[0], hnd[1]); ctx.rotate(-(ang[0] + ang[1]) * D2R + (prop.rot || 0) * D2R); ctx.scale(prop.s || 1, prop.s || 1); prop.fn(ctx, t); ctx.restore(); }
  };

  // back leg / back arm (far side = left in local coords)
  drawLeg(-1, P.legL);
  up(() => drawArm(-1, P.armL, P.propL));
  drawLeg(1, P.legR);

  up(() => {
    const sw = P.sway * 10 + Math.sin(t * 2.2) * 2;
    if (sp.torso === 'tunic') {
      const hemY = hipY + 28;
      shape(ctx, c => {
        c.moveTo(-shX, shY - 4); c.quadraticCurveTo(0, neckY - 6, shX, shY - 4);
        c.quadraticCurveTo(shX + 10, hipY - 60, 44 * bw + 6, hipY - 40);
        c.quadraticCurveTo(66 * bw + sw, hemY - 10, 64 * bw + sw, hemY + 6);
        for (let i = 0; i <= 6; i++) { const u = i / 6; c.lineTo(lerp(64 * bw + sw, -64 * bw + sw, u), hemY + 6 + (i % 2 ? 10 : 0)); }
        c.quadraticCurveTo(-66 * bw + sw, hemY - 10, -44 * bw - 6, hipY - 40);
        c.quadraticCurveTo(-shX - 10, hipY - 60, -shX, shY - 4); c.closePath();
      }, sp.tunic, { lw: 5, shade: { x0: 40, y0: neckY, x1: -60, y1: hipY + 30, a: 0.3 }, hi: { x: 20, y: neckY + 40, r: 90, a: 0.15 } });
      // patch + belt
      if (sp.patch && sp.patch !== sp.tunic) shape(ctx, c => c.rect(14 * bw, hipY - 92, 30, 28), sp.patch, { lw: 3.5 });
      if (sp.patch && sp.patch !== sp.tunic) { ctx.save(); ctx.setLineDash([5, 5]); line(ctx, [[16 * bw, hipY - 90], [42 * bw, hipY - 90]], 2); ctx.restore(); }
      shape(ctx, c => { c.moveTo(-50 * bw, hipY - 44); c.quadraticCurveTo(0, hipY - 34, 50 * bw, hipY - 44); c.lineTo(50 * bw, hipY - 30); c.quadraticCurveTo(0, hipY - 20, -50 * bw, hipY - 30); c.closePath(); }, sp.belt, { lw: 4, tex: false });
      tube(ctx, [[10, hipY - 30], [6 + Math.sin(t * 3) * 3, hipY + 6]], 6, sp.belt, 3);
    } else {
      const hemY = -14, hw = 78 * bw;
      shape(ctx, c => {
        c.moveTo(-shX, shY - 4); c.quadraticCurveTo(0, neckY - 8, shX, shY - 4);
        c.quadraticCurveTo(shX + 12 * bw, hipY - 20, hw + sw, hemY);
        for (let i = 0; i <= 8; i++) { const u = i / 8; c.lineTo(lerp(hw + sw, -hw + sw, u), hemY + (i % 2 ? 8 : 0) + Math.sin(t * 4 + i) * 2); }
        c.quadraticCurveTo(-shX - 12 * bw, hipY - 20, -shX, shY - 4); c.closePath();
      }, sp.robe, { lw: 5, shade: { x0: 50, y0: neckY, x1: -80, y1: 0, a: 0.32 }, hi: { x: 25, y: neckY + 50, r: 110, a: 0.12 } });
      // robe folds
      ctx.save(); ctx.globalAlpha = 0.55; for (const fxp of [-0.45, 0.1, 0.5]) curve(ctx, [fxp * hw * 0.6, hipY + 10], [fxp * hw * 0.8 + sw * 0.5, (hipY + hemY) / 2], [fxp * hw + sw, hemY - 4], 3.5, sp.robeDark); ctx.restore();
      if (sp.trim) { line(ctx, [[0, neckY + 4], [0 + sw * 0.4, hemY]], 10, sp.trim); line(ctx, [[0, neckY + 4], [0 + sw * 0.4, hemY]], 3, sp.robeDark); }
      if (sp.apron) shape(ctx, c => { c.moveTo(-40 * bw, shY + 22); c.lineTo(40 * bw, shY + 22); c.quadraticCurveTo(50 * bw, hipY, 56 * bw + sw * 0.6, hemY - 18); c.lineTo(-56 * bw + sw * 0.6, hemY - 18); c.quadraticCurveTo(-50 * bw, hipY, -40 * bw, shY + 22); c.closePath(); }, sp.apron, { lw: 4.5, shade: { x0: 40, y0: shY, x1: -50, y1: 0, a: 0.3 } });
      if (sp.apron) { tube(ctx, [[-40 * bw, shY + 22], [-24 * bw, neckY + 4]], 6, sp.apronDark, 3); tube(ctx, [[40 * bw, shY + 22], [24 * bw, neckY + 4]], 6, sp.apronDark, 3); }
      if (sp === SPECS.doc2) shape(ctx, c => c.roundRect(-22, hipY - 40, 44, 34, 6), sp.apronDark, { lw: 3.5, tex: false }); // pocket
    }
    // head with tilt
    ctx.save();
    ctx.translate(0, neckY - sp.headH * 0.38);
    ctx.rotate(P.tilt * D2R);
    drawHead(ctx, sp, P);
    ctx.restore();
    drawArm(1, P.armR, P.propR);
  });
  ctx.restore();
}

module.exports = { SPECS, P0, blend, walk, run, flail, drawPerson, drawHead };
