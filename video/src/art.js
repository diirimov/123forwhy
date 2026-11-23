// ---------- art: characters, creatures, props, environments ----------
const PAL = {
  skin: ['#f1c9a2', '#e0ab7e', '#c48a5c', '#f6d4b4', '#a8714a'],
  tunic: ['#8f2f2a', '#2f5d72', '#5e6d2c', '#7d5a2f', '#6c3f70', '#b8902f', '#3f4a6b', '#a4552b'],
  legs: ['#3c2f2a', '#4b3c36', '#2c3440', '#5a4632'],
  hair: ['#3a2418', '#1e1410', '#8a5a2b', '#b5642c', '#d6b16a', '#6b6b6b'],
  hood: ['#6b4a3a', '#4a5560', '#7a2f2f', '#55603a', '#3b3550'],
};

// ----- pose library (angles: 0 = straight down, + = forward) -----
function poseWalk(ph, amt = 1, lean = 0.05) {
  const s = Math.sin(ph * TAU), c = Math.cos(ph * TAU);
  return {
    lean, bob: -Math.abs(s) * 6 * amt,
    lt: [s * .45 * amt, Math.max(0, c) * .7 * amt + .05], rt: [-s * .45 * amt, Math.max(0, -c) * .7 * amt + .05],
    la: [-s * .45 * amt, .35], ra: [s * .45 * amt, .35],
  };
}
function poseRun(ph, amt = 1) {
  const s = Math.sin(ph * TAU), c = Math.cos(ph * TAU);
  return {
    lean: .28 * amt, bob: -Math.abs(s) * 14 * amt,
    lt: [s * .85 * amt + .15, Math.max(0, c) * 1.5 * amt + .2], rt: [-s * .85 * amt + .15, Math.max(0, -c) * 1.5 * amt + .2],
    la: [-s * .95 * amt, 1.5], ra: [s * .95 * amt, 1.5],
  };
}
function posePanic(ph, t, amt = 1) {
  const p = poseRun(ph, amt);
  p.lean = .12; p.la = [2.6 + Math.sin(t * 19) * .4, .6 + Math.sin(t * 23) * .3]; p.ra = [2.9 + Math.sin(t * 17 + 1) * .4, .5 + Math.sin(t * 21) * .3];
  return p;
}
function poseIdle(t, amt = 1) {
  const b = bounce(t, 5 * amt);
  return { lean: 0, bob: b, lt: [.05, .05], rt: [-.05, .05], la: [.15 + Math.sin(t * 2) * .05, .25], ra: [-.1, .3] };
}
function poseRecoil(k = 1) {
  return { lean: -.32 * k, bob: 0, lt: [.35 * k, .1], rt: [-.25 * k, .3 * k], la: [1.5 * k, 1.2 * k], ra: [1.9 * k, 1.0 * k] };
}
function posePoint(t) {
  return { lean: .08, bob: bounce(t, 3), lt: [.15, .05], rt: [-.12, .1], la: [1.55, .05], ra: [.2, .6] };
}
function posePray(t) {
  return { lean: .1, bob: bounce(t, 4), lt: [.05, .05], rt: [-.05, .05], la: [1.0, 1.6], ra: [1.1, 1.55] };
}
function poseDance(t, k = 1) { // dancing-plague jig on the beat
  const ph = t / BEAT;
  const s = Math.sin(ph * Math.PI);
  return {
    lean: Math.sin(ph * Math.PI) * .12 * k, bob: -Math.abs(s) * 16 * k,
    lt: [Math.max(0, s) * 1.0 * k, Math.max(0, s) * 1.4 * k + .05], rt: [-Math.max(0, -s) * .5 * k, Math.max(0, -s) * 1.4 * k + .05],
    la: [2.4 + s * .5, .4], ra: [-.6 + s * .5 * k, .6],
  };
}

// ----- person -----
function legPts(hip, a, bend, L1 = 40, L2 = 42) {
  const k = [hip[0] + Math.sin(a) * L1, hip[1] + Math.cos(a) * L1];
  const b = a - bend;
  const f = [k[0] + Math.sin(b) * L2, k[1] + Math.cos(b) * L2];
  return [hip, k, f];
}
function armPts(sh, a, bend, L1 = 34, L2 = 31) {
  const e = [sh[0] + Math.sin(a) * L1, sh[1] + Math.cos(a) * L1];
  const b = a + bend;
  const h = [e[0] + Math.sin(b) * L2, e[1] + Math.cos(b) * L2];
  return [sh, e, h];
}
function face(ctx, hx, hy, ex, view, skinShade) {
  const eyes = ex.eyes || 'normal', mouth = ex.mouth || 'flat', brow = ex.brow || 0;
  const lookX = (ex.look || [0, 0])[0], lookY = (ex.look || [0, 0])[1];
  const E2 = view === 'front' ? [[-12, -2], [12, -2]] : [[-2, -3], [16, -3]];
  const big = eyes === 'wide' ? 1.35 : 1;
  for (let i = 0; i < 2; i++) {
    const [dx, dy] = E2[i]; const sc = view === 'front' ? 1 : (i === 0 ? .82 : 1);
    if (eyes === 'closed') {
      ctx.beginPath(); ctx.arc(hx + dx, hy + dy + 2, 6 * sc, .15 * Math.PI, .85 * Math.PI); ctx.lineWidth = 3.5; ctx.strokeStyle = INK; ctx.stroke();
    } else {
      ell(ctx, hx + dx, hy + dy, 7.5 * sc * big, 9.5 * sc * big); fillStroke(ctx, '#fbf6ea', 3);
      ell(ctx, hx + dx + 2 * sc + lookX * 3, hy + dy + 1 + lookY * 3, (eyes === 'wide' ? 3 : 4.2) * sc, (eyes === 'wide' ? 3 : 4.8) * sc); ctx.fillStyle = INK; ctx.fill();
      if (eyes === 'sick' || eyes === 'tired') { // heavy lids
        ctx.save(); ell(ctx, hx + dx, hy + dy, 8 * sc, 10 * sc); ctx.clip(); ctx.fillStyle = skinShade; ctx.fillRect(hx + dx - 10, hy + dy - 12, 20, eyes === 'sick' ? 11 : 9); ctx.restore();
        ctx.beginPath(); ctx.moveTo(hx + dx - 7 * sc, hy + dy - 1); ctx.lineTo(hx + dx + 7 * sc, hy + dy - 1); ctx.lineWidth = 3; ctx.strokeStyle = INK; ctx.stroke();
      }
    }
    // brows: brow>0 worried (inner up), brow<0 angry
    const bx = hx + dx, by = hy + dy - 15 * big;
    ctx.beginPath(); const inner = (view === 'front' ? (i === 0 ? 1 : -1) : (i === 0 ? 1 : -1));
    ctx.moveTo(bx - 7 * sc, by + (inner > 0 ? brow * 4 : -brow * 4) * .5); ctx.lineTo(bx + 7 * sc, by - (inner > 0 ? brow * 4 : -brow * 4) * .5);
    ctx.lineWidth = 4; ctx.strokeStyle = INK; ctx.stroke();
  }
  // nose
  if (view !== 'front') { ctx.beginPath(); ctx.arc(hx + 30, hy + 5, 5, -1.2, 1.6); ctx.lineWidth = 3.5; ctx.strokeStyle = INK; ctx.stroke(); }
  else { ctx.beginPath(); ctx.arc(hx, hy + 7, 4, 0, Math.PI); ctx.lineWidth = 3; ctx.strokeStyle = INK; ctx.stroke(); }
  // mouth
  const mx = view === 'front' ? hx : hx + 14, my = hy + 17;
  ctx.strokeStyle = INK; ctx.lineWidth = 3.5;
  if (mouth === 'o') { ell(ctx, mx, my + 2, 6, 8); fillStroke(ctx, '#4a1a1e', 3); }
  else if (mouth === 'scream') { ell(ctx, mx, my + 4, 9, 12); fillStroke(ctx, '#4a1a1e', 3); ell(ctx, mx, my + 10, 5, 3); ctx.fillStyle = '#c0565a'; ctx.fill(); }
  else if (mouth === 'frown') { ctx.beginPath(); ctx.arc(mx, my + 8, 8, 1.15 * Math.PI, 1.85 * Math.PI); ctx.stroke(); }
  else if (mouth === 'smile') { ctx.beginPath(); ctx.arc(mx, my - 2, 8, .15 * Math.PI, .85 * Math.PI); ctx.stroke(); }
  else if (mouth === 'grit') { rr(ctx, mx - 9, my - 3, 18, 9, 3); fillStroke(ctx, '#f6f1e2', 3); ctx.beginPath(); ctx.moveTo(mx - 9, my + 1.5); ctx.lineTo(mx + 9, my + 1.5); ctx.lineWidth = 2; ctx.stroke(); }
  else if (mouth === 'wavy') { ctx.beginPath(); ctx.moveTo(mx - 8, my); ctx.quadraticCurveTo(mx - 4, my - 4, mx, my); ctx.quadraticCurveTo(mx + 4, my + 4, mx + 8, my); ctx.stroke(); }
  else { ctx.beginPath(); ctx.moveTo(mx - 6, my); ctx.lineTo(mx + 6, my); ctx.stroke(); }
}

function drawPerson(ctx, P) {
  const s = P.s || 1, view = P.view || 'side';
  const pose = P.pose || poseIdle(0);
  const C = P.c || {};
  const skin = P.pale ? mix(C.skin || '#f1c9a2', '#c9d6cc', P.pale) : (C.skin || '#f1c9a2');
  const tunic = C.tunic || '#8f2f2a', legs = C.legs || '#3c2f2a', shoes = C.shoes || '#2a1c16';
  ctx.save();
  ctx.translate(P.x, P.y); ctx.scale(s * (P.face || 1), s);
  if (P.shadow !== false) { ctx.save(); ctx.scale(1 / (P.face || 1), 1); ell(ctx, 0, 2, 46, 9); ctx.fillStyle = 'rgba(0,0,0,.35)'; ctx.fill(); ctx.restore(); }
  ctx.rotate(P.rot || 0);
  const bob = pose.bob || 0;
  const hip = [0, -80 + bob];
  ctx.save(); ctx.translate(hip[0], hip[1]); ctx.rotate(pose.lean || 0); ctx.translate(-hip[0], -hip[1]);
  const sh = [0, -140 + bob], head = [view === 'front' ? 0 : 4, -176 + bob + (P.headDy || 0)];
  if (view === 'side') {
    // back limbs
    limb(ctx, armPts([sh[0] - 4, sh[1] + 4], pose.ra[0], pose.ra[1]), 15, shade(tunic, -.35), 4.5);
    const ra = armPts([sh[0] - 4, sh[1] + 4], pose.ra[0], pose.ra[1]); ell(ctx, ra[2][0], ra[2][1], 8, 8); fillStroke(ctx, shade(skin, -.2), 4);
  }
  // legs (counter-rotate lean so legs stay grounded)
  ctx.save(); ctx.translate(hip[0], hip[1]); ctx.rotate(-(pose.lean || 0) * .85); ctx.translate(-hip[0], -hip[1]);
  if (view === 'side') {
    const L1 = legPts([hip[0] - 3, hip[1]], pose.rt[0], pose.rt[1]);
    limb(ctx, L1, 17, shade(legs, -.3), 4.5); ell(ctx, L1[2][0] + 7, L1[2][1] + 1, 13, 7, Math.sin(pose.rt[0] - pose.rt[1]) * .5); fillStroke(ctx, shade(shoes, -.2), 4);
    const L2 = legPts([hip[0] + 3, hip[1]], pose.lt[0], pose.lt[1]);
    limb(ctx, L2, 17, legs, 4.5); ell(ctx, L2[2][0] + 7, L2[2][1] + 1, 13, 7, Math.sin(pose.lt[0] - pose.lt[1]) * .5); fillStroke(ctx, shoes, 4);
  } else {
    for (const [side, lg] of [[-1, pose.lt], [1, pose.rt]]) {
      const lift = Math.max(0, lg[1] - .1) * 18;
      const pts = [[side * 12, hip[1]], [side * 15, hip[1] + 40 - lift * .4], [side * 14, hip[1] + 80 - lift]];
      limb(ctx, pts, 18, legs, 4.5); ell(ctx, side * 15, hip[1] + 82 - lift, 12, 8); fillStroke(ctx, shoes, 4);
    }
  }
  ctx.restore();
  // torso / tunic
  const robe = P.robe, hem = robe ? -6 : -58, flare = robe ? 40 : 30;
  ctx.beginPath();
  ctx.moveTo(-24, sh[1] - 2); ctx.quadraticCurveTo(-30, sh[1] + 30, -flare, hem + bob * (robe ? 0 : 1));
  ctx.quadraticCurveTo(0, hem + 8 + bob * (robe ? 0 : 1), flare, hem + bob * (robe ? 0 : 1));
  ctx.quadraticCurveTo(30, sh[1] + 30, 24, sh[1] - 2); ctx.quadraticCurveTo(0, sh[1] - 12, -24, sh[1] - 2); ctx.closePath();
  const tg = ctx.createLinearGradient(-30, 0, 30, 0); tg.addColorStop(0, shade(tunic, -.25)); tg.addColorStop(.5, tunic); tg.addColorStop(1, shade(tunic, .08));
  fillStroke(ctx, tg, 5);
  // belt
  ctx.beginPath(); ctx.moveTo(-27, -92 + bob); ctx.quadraticCurveTo(0, -86 + bob, 27, -92 + bob); ctx.lineWidth = 7; ctx.strokeStyle = C.belt || '#3a2a1c'; ctx.stroke();
  if (C.apron) { ctx.beginPath(); ctx.moveTo(-14, -92 + bob); ctx.lineTo(14, -92 + bob); ctx.lineTo(18, hem + 4); ctx.lineTo(-18, hem + 4); ctx.closePath(); fillStroke(ctx, C.apron, 4); }
  if (view === 'front' && pose.ra) {
    const A = armPts([-22, sh[1] + 6], -pose.ra[0] * .6 - .15, -pose.ra[1] * .5);
    limb(ctx, A, 15, shade(tunic, -.1), 4.5); ell(ctx, A[2][0], A[2][1], 8, 8); fillStroke(ctx, skin, 4);
  }
  // head
  ctx.save(); ctx.translate(head[0], head[1]); ctx.rotate(P.headRot || 0); ctx.translate(-head[0], -head[1]);
  const hx = head[0], hy = head[1];
  // hood/cape behind head
  if (P.head === 'hood') {
    ctx.beginPath(); ctx.moveTo(hx - 40, hy + 34); ctx.quadraticCurveTo(hx - 52, hy - 30, hx - 6, hy - 40);
    ctx.quadraticCurveTo(hx + 38, hy - 40, hx + 40, hy + 10); ctx.lineTo(hx + 34, hy + 38); ctx.closePath(); fillStroke(ctx, C.hood || '#6b4a3a', 5);
    ctx.beginPath(); ctx.moveTo(hx - 38, hy - 10); ctx.quadraticCurveTo(hx - 70, hy + 0, hx - 72, hy + 40 + Math.sin((P.t || 0) * 5) * 4); ctx.lineWidth = 12; ctx.strokeStyle = INK; ctx.stroke(); ctx.lineWidth = 6; ctx.strokeStyle = C.hood || '#6b4a3a'; ctx.stroke();
  }
  ell(ctx, hx - 8, hy + 26, 10, 9); fillStroke(ctx, shade(skin, -.15), 4); // neck
  ell(ctx, hx, hy, 30, 31); const hg = ctx.createRadialGradient(hx + 10, hy - 10, 4, hx, hy, 34); hg.addColorStop(0, shade(skin, .12)); hg.addColorStop(1, shade(skin, -.12)); fillStroke(ctx, hg, 5);
  if (view !== 'front') { ell(ctx, hx - 14, hy + 3, 6, 8); fillStroke(ctx, shade(skin, -.1), 3.5); }
  if (P.flush) { ctx.save(); ell(ctx, hx, hy, 29, 30); ctx.clip(); ctx.globalAlpha = P.flush * .45; ctx.fillStyle = '#ff3a2a'; ctx.fillRect(hx - 40, hy - 40, 80, 80); ctx.restore(); }
  if (P.patches) { ctx.save(); ell(ctx, hx, hy, 29, 30); ctx.clip(); ctx.fillStyle = 'rgba(235,225,205,.7)'; ell(ctx, hx - 8, hy + 12, 8, 6); ctx.fill(); ell(ctx, hx + 18, hy - 14, 5, 4); ctx.fill(); ctx.restore(); }
  // cheeks
  ctx.save(); ctx.globalAlpha = P.pale ? .1 : .35; ell(ctx, view === 'front' ? hx - 17 : hx + 5, hy + 11, 7, 4.5); ctx.fillStyle = '#e06a5a'; ctx.fill(); if (view === 'front') { ell(ctx, hx + 17, hy + 11, 7, 4.5); ctx.fill(); } ctx.restore();
  if (!P.back) face(ctx, view === 'front' ? hx : hx + 3, hy, P.ex || {}, view, shade(skin, -.08));
  else { ell(ctx, hx, hy - 2, 30, 30); fillStroke(ctx, P.head === 'hood' ? (C.hood || '#6b4a3a') : (P.head === 'coif' ? '#eee6d4' : (C.hair || '#3a2418')), 5); }
  // headwear
  if (P.head === 'coif') {
    ctx.beginPath(); ctx.moveTo(hx - 30, hy + 12); ctx.quadraticCurveTo(hx - 36, hy - 40, hx + 4, hy - 36); ctx.quadraticCurveTo(hx + 30, hy - 34, hx + 28, hy - 14);
    ctx.quadraticCurveTo(hx + 4, hy - 22, hx - 10, hy - 6); ctx.quadraticCurveTo(hx - 18, hy + 6, hx - 14, hy + 26); ctx.closePath(); fillStroke(ctx, C.coif || '#eee6d4', 4.5);
  } else if (P.head === 'hair') {
    ctx.beginPath(); ctx.moveTo(hx - 31, hy + 8); ctx.quadraticCurveTo(hx - 34, hy - 36, hx + 4, hy - 34); ctx.quadraticCurveTo(hx + 30, hy - 32, hx + 30, hy - 10);
    ctx.quadraticCurveTo(hx + 12, hy - 20, hx - 4, hy - 16); ctx.quadraticCurveTo(hx - 16, hy - 8, hx - 20, hy + 12); ctx.closePath(); fillStroke(ctx, C.hair || '#3a2418', 4.5);
  } else if (P.head === 'hat') {
    ctx.beginPath(); ctx.moveTo(hx - 26, hy - 18); ctx.quadraticCurveTo(hx - 20, hy - 54, hx + 6, hy - 50); ctx.quadraticCurveTo(hx + 26, hy - 46, hx + 24, hy - 18); ctx.closePath(); fillStroke(ctx, C.hat || '#5a3d2a', 4.5);
    ell(ctx, hx, hy - 18, 44, 9, -.05); fillStroke(ctx, shade(C.hat || '#5a3d2a', -.1), 4.5);
  } else if (P.head === 'cap') {
    ctx.beginPath(); ctx.moveTo(hx - 30, hy - 6); ctx.quadraticCurveTo(hx - 28, hy - 44, hx + 6, hy - 40); ctx.quadraticCurveTo(hx + 34, hy - 36, hx + 30, hy - 10); ctx.quadraticCurveTo(hx, hy - 22, hx - 30, hy - 6); fillStroke(ctx, C.hat || '#7a2f2f', 4.5);
  } else if (P.head === 'hood') {
    ctx.beginPath(); ctx.moveTo(hx - 36, hy + 20); ctx.quadraticCurveTo(hx - 40, hy - 44, hx + 2, hy - 42); ctx.quadraticCurveTo(hx + 40, hy - 40, hx + 36, hy - 4);
    ctx.quadraticCurveTo(hx + 18, hy - 30, hx - 6, hy - 26); ctx.quadraticCurveTo(hx - 26, hy - 18, hx - 22, hy + 22); ctx.closePath(); fillStroke(ctx, C.hood || '#6b4a3a', 5);
  } else if (P.head === 'tudor') {
    ctx.beginPath(); ctx.moveTo(hx - 32, hy - 16); ctx.quadraticCurveTo(hx - 30, hy - 48, hx + 4, hy - 46); ctx.quadraticCurveTo(hx + 36, hy - 44, hx + 34, hy - 16); ctx.closePath(); fillStroke(ctx, C.hat || '#1d1a22', 4.5);
    ctx.beginPath(); ctx.moveTo(hx + 18, hy - 40); ctx.quadraticCurveTo(hx + 40, hy - 70, hx + 46, hy - 50); ctx.lineWidth = 5; ctx.strokeStyle = '#f2efe6'; ctx.stroke();
  }
  if (P.headFn) P.headFn(ctx, hx, hy);
  // sweat
  if (P.sweat > 0) {
    const n = Math.floor(3 + P.sweat * 7);
    for (let i = 0; i < n; i++) {
      const ph = ((P.t || 0) * (1.2 + hash(i) * 1.5) + hash(i + 9)) % 1;
      const sx = hx - 24 + hash(i + 3) * 54, sy = hy - 22 + hash(i + 5) * 20 + ph * 34 * P.sweat;
      ctx.save(); ctx.globalAlpha = (1 - ph) * clamp(P.sweat * 2);
      ctx.beginPath(); ctx.moveTo(sx, sy - 9); ctx.quadraticCurveTo(sx + 6, sy, sx, sy + 5); ctx.quadraticCurveTo(sx - 6, sy, sx, sy - 9);
      ctx.fillStyle = '#bfe8ff'; ctx.fill(); ctx.lineWidth = 2.5; ctx.strokeStyle = '#1d3a52'; ctx.stroke(); ctx.restore();
    }
  }
  ctx.restore(); // head
  // front arm
  if (view === 'side') {
    const A = armPts([sh[0] + 4, sh[1] + 6], pose.la[0], pose.la[1]);
    limb(ctx, A, 16, shade(tunic, .05), 4.5);
    ell(ctx, A[2][0], A[2][1], 8.5, 8.5); fillStroke(ctx, skin, 4);
    if (P.patchHand) { ell(ctx, A[2][0] + 2, A[2][1] - 1, 4, 3); ctx.fillStyle = '#e8dfcc'; ctx.fill(); }
    if (P.hold) P.hold(ctx, A[2][0], A[2][1]);
  } else if (pose.la) {
    const A = armPts([22, sh[1] + 6], pose.la[0] * .6 + .15, pose.la[1] * .5);
    limb(ctx, A, 15, shade(tunic, .05), 4.5); ell(ctx, A[2][0], A[2][1], 8, 8); fillStroke(ctx, skin, 4);
    if (P.hold) P.hold(ctx, A[2][0], A[2][1]);
  }
  ctx.restore(); // lean
  ctx.restore();
}

// quick randomized townsperson
function townsfolk(seed) {
  const r = rngFrom(seed * 7919 + 13);
  const pick = a => a[Math.floor(r() * a.length)];
  const female = r() < .45;
  const heads = female ? ['coif', 'coif', 'hood'] : ['hair', 'hat', 'cap', 'hood', 'hair'];
  return {
    c: { skin: pick(PAL.skin), tunic: pick(PAL.tunic), legs: pick(PAL.legs), hair: pick(PAL.hair), hood: pick(PAL.hood), hat: pick(['#5a3d2a', '#3c4a5a', '#7a2f2f', '#4d5b2e']), apron: female && r() < .5 ? '#e7dcc4' : null, coif: '#efe8d8' },
    head: pick(heads), robe: female || r() < .12, s: .9 + r() * .2,
  };
}

// ----- plague doctor (front 3/4 view) -----
function drawDoctor(ctx, D) {
  const s = D.s || 1, t = D.t || 0, ph = D.ph || 0, turn = D.turn || 0; // turn -1..1 beak direction
  ctx.save(); ctx.translate(D.x, D.y); ctx.scale(s, s);
  ell(ctx, 0, 4, 80, 14); ctx.fillStyle = 'rgba(0,0,0,.45)'; ctx.fill();
  const step = Math.sin(ph * TAU);
  const bob = -Math.abs(step) * 8;
  // boots
  for (const side of [-1, 1]) {
    const lift = Math.max(0, side * step) * 22;
    rr(ctx, side * 24 - 16, -38 - lift, 30, 40, 8); fillStroke(ctx, '#1b1416', 5);
  }
  // cloak
  const flap = Math.sin(t * 3.2) * 10 + step * 8;
  ctx.beginPath();
  ctx.moveTo(-34, -250 + bob); ctx.quadraticCurveTo(-70, -140 + bob, -92 - flap, -24);
  ctx.quadraticCurveTo(-60, -14 + step * 6, -30, -30); ctx.quadraticCurveTo(0, -18, 30, -30); ctx.quadraticCurveTo(60, -14 - step * 6, 94 + flap, -22);
  ctx.quadraticCurveTo(70, -140 + bob, 34, -250 + bob); ctx.closePath();
  const cg = ctx.createLinearGradient(-90, 0, 90, 0); cg.addColorStop(0, '#0e0b10'); cg.addColorStop(.55, '#2a2330'); cg.addColorStop(1, '#141017');
  fillStroke(ctx, cg, 6);
  // cloak folds
  ctx.strokeStyle = 'rgba(255,255,255,.07)'; ctx.lineWidth = 4;
  for (const fx of [-40, -10, 22, 50]) { ctx.beginPath(); ctx.moveTo(fx * .4, -220 + bob); ctx.quadraticCurveTo(fx, -120, fx * 1.4 + flap * .3, -36); ctx.stroke(); }
  // arms (cane + lantern)
  const sw = Math.sin(t * 2.6) * .25;
  ctx.save(); ctx.translate(-48, -200 + bob);
  limb(ctx, [[0, 0], [-12, 50], [-22, 92]], 22, '#1c171f', 5);
  ctx.beginPath(); ctx.moveTo(-22, 60); ctx.lineTo(-30, 205 - bob); ctx.lineWidth = 9; ctx.strokeStyle = INK; ctx.stroke(); ctx.lineWidth = 5; ctx.strokeStyle = '#6b4a2a'; ctx.stroke();
  ell(ctx, -22, 92, 11, 11); fillStroke(ctx, '#2b2226', 4);
  ctx.restore();
  ctx.save(); ctx.translate(50, -200 + bob);
  limb(ctx, [[0, 0], [16, 50], [24, 88]], 22, '#1c171f', 5);
  ell(ctx, 24, 88, 11, 11); fillStroke(ctx, '#2b2226', 4);
  ctx.translate(24, 92); ctx.rotate(sw);
  ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(0, 24); ctx.lineWidth = 4; ctx.strokeStyle = INK; ctx.stroke();
  rr(ctx, -15, 24, 30, 40, 6); fillStroke(ctx, 'rgba(255,190,90,.95)', 5);
  ctx.beginPath(); ctx.moveTo(-18, 24); ctx.lineTo(0, 12); ctx.lineTo(18, 24); ctx.closePath(); fillStroke(ctx, '#2a2024', 4);
  glow(ctx, 0, 44, 220, 'rgba(255,170,70,.55)', D.lamp == null ? 1 : D.lamp);
  ctx.restore();
  // head
  ctx.save(); ctx.translate(0, -282 + bob);
  ell(ctx, 0, 0, 46, 48); fillStroke(ctx, '#241c22', 6); // hood
  // mask face
  ell(ctx, turn * 10, 6, 34, 36); fillStroke(ctx, '#3b2f2a', 5);
  // beak
  const bx = turn * 70, by = 70 - Math.abs(turn) * 34;
  ctx.beginPath(); ctx.moveTo(turn * 10 - 20, 12); ctx.quadraticCurveTo(bx * .6 - 10, 40, bx, by); ctx.quadraticCurveTo(bx * .55 + 14, 30, turn * 10 + 20, 10); ctx.closePath();
  const bg = ctx.createLinearGradient(-20, 0, 40, 60); bg.addColorStop(0, '#efe4c8'); bg.addColorStop(1, '#a8956e'); fillStroke(ctx, bg, 5);
  ctx.strokeStyle = 'rgba(40,30,20,.6)'; ctx.lineWidth = 2.5; for (let k = 1; k < 4; k++) { const u = k / 4; ctx.beginPath(); ctx.moveTo(lerp(turn * 10 - 16, bx, u) - 6, lerp(14, by, u) - 4); ctx.lineTo(lerp(turn * 10 + 16, bx, u) + 4, lerp(12, by, u) - 6); ctx.stroke(); }
  // lenses
  for (const ex of [-14, 14]) {
    const lx = ex + turn * 14;
    ell(ctx, lx, -6, 11, 11); fillStroke(ctx, '#7a1a1a', 5);
    ell(ctx, lx, -6, 6, 6); ctx.fillStyle = '#ff4a3a'; ctx.fill();
    glow(ctx, lx, -6, 34, 'rgba(255,60,40,.8)', D.eyeGlow == null ? .7 : D.eyeGlow);
    ell(ctx, lx - 3, -9, 2.5, 2.5); ctx.fillStyle = '#fff'; ctx.fill();
  }
  // hat
  ell(ctx, 0, -40, 92, 20); fillStroke(ctx, '#18131a', 6);
  ctx.beginPath(); ctx.moveTo(-40, -44); ctx.lineTo(-34, -112); ctx.quadraticCurveTo(0, -122, 34, -112); ctx.lineTo(40, -44); ctx.closePath(); fillStroke(ctx, '#1f1922', 6);
  rr(ctx, -40, -62, 80, 13, 3); fillStroke(ctx, '#6b2a2a', 4);
  ctx.restore();
  ctx.restore();
}

// ----- rat -----
function drawRat(ctx, x, y, s, face, ph, t, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s * face, s);
  const run = Math.sin(ph * TAU);
  const body = o.color || '#4a3e3c';
  ell(ctx, 0, 6, 46, 7); ctx.fillStyle = 'rgba(0,0,0,.35)'; ctx.fill();
  // tail
  ctx.beginPath(); ctx.moveTo(-36, -10);
  ctx.bezierCurveTo(-70, -6 + run * 10, -90, -30 - run * 12, -120, -18 + Math.sin(t * 9) * 10);
  ctx.lineWidth = 9; ctx.strokeStyle = INK; ctx.stroke(); ctx.lineWidth = 4.5; ctx.strokeStyle = '#c88a86'; ctx.stroke();
  // legs
  for (const [lx, p] of [[-20, 0], [-10, .5], [18, .25], [28, .75]]) {
    const a = Math.sin((ph + p) * TAU) * .7;
    limb(ctx, [[lx, -8], [lx + Math.sin(a) * 14, 4 - Math.abs(Math.cos(a)) * 2]], 6, shade(body, -.2), 3);
  }
  // body
  const hump = Math.abs(run) * 5;
  ctx.beginPath(); ctx.moveTo(-42, -6); ctx.quadraticCurveTo(-40, -40 - hump, 0, -38 - hump); ctx.quadraticCurveTo(30, -36, 46, -20);
  ctx.quadraticCurveTo(70, -12, 76, -6); ctx.quadraticCurveTo(50, 4, 20, 2); ctx.quadraticCurveTo(-20, 6, -42, -6); ctx.closePath();
  const g = ctx.createLinearGradient(0, -40, 0, 4); g.addColorStop(0, shade(body, .1)); g.addColorStop(1, shade(body, -.35)); fillStroke(ctx, g, 4.5);
  // fur ticks
  ctx.strokeStyle = 'rgba(0,0,0,.35)'; ctx.lineWidth = 2; for (let i = 0; i < 6; i++) { ctx.beginPath(); ctx.moveTo(-28 + i * 10, -30 - hump * .5); ctx.lineTo(-32 + i * 10, -24); ctx.stroke(); }
  // ear + eye + nose
  ell(ctx, 38, -32, 9, 11, -.3); fillStroke(ctx, '#c88a86', 4);
  ell(ctx, 54, -20, 4.5, 4.5); ctx.fillStyle = '#ff3b30'; ctx.fill(); glow(ctx, 54, -20, 22, 'rgba(255,40,30,.9)', o.eyeGlow == null ? .8 : o.eyeGlow);
  ell(ctx, 77, -7, 4, 4); ctx.fillStyle = '#f19a9a'; ctx.fill();
  ctx.strokeStyle = 'rgba(240,230,220,.6)'; ctx.lineWidth = 1.5; for (const d of [-6, 0, 6]) { ctx.beginPath(); ctx.moveTo(70, -8); ctx.lineTo(92, -10 + d); ctx.stroke(); }
  ctx.restore();
}
function drawFlea(ctx, x, y, s, rot, glowA = 1) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
  glow(ctx, 0, 0, 34, 'rgba(255,40,40,.85)', glowA);
  ell(ctx, 0, 0, 9, 7, .3); fillStroke(ctx, '#3a1210', 2.5);
  ell(ctx, 7, -4, 4, 3.5); fillStroke(ctx, '#2a0c0c', 2);
  ctx.strokeStyle = INK; ctx.lineWidth = 2; for (const lx of [-4, 0, 4]) { ctx.beginPath(); ctx.moveTo(lx, 4); ctx.lineTo(lx - 6, 12); ctx.lineTo(lx - 2, 15); ctx.stroke(); }
  ctx.restore();
}

// ----- buildings -----
const PLASTER = ['#dcc7a0', '#cfb68c', '#e3d2b0', '#c2a47c', '#d4c3a3', '#b89a74'];
function drawHouse(g, x, by, w, h, seed, o = {}) {
  const r = rngFrom(seed * 1013 + 7);
  const wall = PLASTER[Math.floor(r() * PLASTER.length)];
  const beam = '#3a2a21', roofC = r() < .6 ? ['#7c3b2b', '#8a4a32', '#6b3226'][Math.floor(r() * 3)] : ['#3e4452', '#4a4f5c'][Math.floor(r() * 2)];
  const floors = h > 330 ? 3 : 2;
  const baseH = h * .34, fh = (h - baseH) / (floors - 1 + .001);
  const wins = [];
  // ground floor stone
  g.save();
  g.beginPath(); g.rect(x, by - baseH, w, baseH); fillStroke(g, '#8d8174', 5);
  g.strokeStyle = 'rgba(40,30,25,.45)'; g.lineWidth = 2.5;
  for (let yy = by - baseH + 18; yy < by; yy += 22) { g.beginPath(); g.moveTo(x, yy); g.lineTo(x + w, yy); g.stroke(); for (let xx = x + (yy % 44 ? 0 : 20); xx < x + w; xx += 40) { g.beginPath(); g.moveTo(xx, yy); g.lineTo(xx, yy - 22); g.stroke(); } }
  // door
  const dw = Math.min(70, w * .32), dx = x + (r() < .5 ? w * .18 : w * .55), dh = baseH * .82;
  g.beginPath(); g.moveTo(dx, by); g.lineTo(dx, by - dh + dw / 2); g.arc(dx + dw / 2, by - dh + dw / 2, dw / 2, Math.PI, 0); g.lineTo(dx + dw, by); g.closePath();
  fillStroke(g, '#4e3524', 5);
  g.strokeStyle = 'rgba(0,0,0,.35)'; g.lineWidth = 3; for (let k = 1; k < 4; k++) { g.beginPath(); g.moveTo(dx + dw * k / 4, by); g.lineTo(dx + dw * k / 4, by - dh + 12); g.stroke(); }
  wins.push({ type: 'door', x: dx, y: by - dh, w: dw, h: dh });
  // ground window
  const gwx = dx < x + w * .4 ? x + w * .62 : x + w * .14, gww = w * .22;
  if (gwx + gww < x + w - 6) { g.beginPath(); g.rect(gwx, by - baseH * .78, gww, baseH * .42); fillStroke(g, '#1b1418', 4); wins.push({ type: 'win', x: gwx, y: by - baseH * .78, w: gww, h: baseH * .42 }); }
  // upper floors (jetty)
  let top = by - baseH;
  for (let f = 0; f < floors - 1; f++) {
    const ov = 10 * (f + 1);
    const fx = x - ov, fw = w + ov * 2, fy = top - fh;
    g.beginPath(); g.rect(fx, fy, fw, fh); const wg = g.createLinearGradient(fx, 0, fx + fw, 0); wg.addColorStop(0, shade(wall, -.12)); wg.addColorStop(.6, wall); wg.addColorStop(1, shade(wall, -.2)); fillStroke(g, wg, 5);
    // jetty shadow
    g.fillStyle = 'rgba(0,0,0,.28)'; g.fillRect(fx + 4, top, fw - 8, 14);
    // timber
    g.strokeStyle = beam; g.lineWidth = 9; g.lineCap = 'butt';
    g.beginPath(); g.moveTo(fx, top - 4); g.lineTo(fx + fw, top - 4); g.moveTo(fx, fy + 4); g.lineTo(fx + fw, fy + 4); g.stroke();
    const bays = Math.max(2, Math.round(fw / 75));
    for (let b = 0; b <= bays; b++) { const bx = fx + fw * b / bays; g.beginPath(); g.moveTo(bx, fy); g.lineTo(bx, top); g.stroke(); }
    const winBays = [];
    for (let b = 0; b < bays; b++) {
      const bx0 = fx + fw * b / bays, bx1 = fx + fw * (b + 1) / bays;
      const k = r();
      if (k < .45) { winBays.push(b); }
      else if (k < .75) { g.lineWidth = 7; g.beginPath(); g.moveTo(bx0, top); g.lineTo(bx1, fy); g.moveTo(bx1, top); g.lineTo(bx0, fy); g.stroke(); }
      else { g.lineWidth = 7; g.beginPath(); g.moveTo(bx0, top - fh * .5); g.lineTo((bx0 + bx1) / 2, fy); g.lineTo(bx1, top - fh * .5); g.stroke(); }
    }
    if (!winBays.length) winBays.push(Math.floor(bays / 2));
    for (const b of winBays) {
      const bx0 = fx + fw * b / bays, bw = fw / bays;
      const ww = bw * .62, wh = fh * .52, wx = bx0 + (bw - ww) / 2, wy = fy + fh * .22;
      g.beginPath(); g.rect(wx, wy, ww, wh); fillStroke(g, '#1b1418', 5);
      wins.push({ type: 'win', x: wx, y: wy, w: ww, h: wh });
      g.strokeStyle = beam; g.lineWidth = 6; g.beginPath(); g.moveTo(wx - 6, wy + wh + 4); g.lineTo(wx + ww + 6, wy + wh + 4); g.stroke();
    }
    g.lineCap = 'round';
    top = fy;
  }
  // roof
  const ov = 10 * floors + 16, rh = w * (.55 + r() * .35);
  const gable = r() < .7;
  g.beginPath();
  if (gable) { g.moveTo(x - ov, top + 4); g.lineTo(x + w / 2, top - rh); g.lineTo(x + w + ov, top + 4); }
  else { g.moveTo(x - ov, top + 4); g.lineTo(x - ov + 30, top - rh * .6); g.lineTo(x + w + ov - 30, top - rh * .6); g.lineTo(x + w + ov, top + 4); }
  g.closePath();
  const rg = g.createLinearGradient(0, top - rh, 0, top); rg.addColorStop(0, shade(roofC, .1)); rg.addColorStop(1, shade(roofC, -.25));
  fillStroke(g, rg, 5);
  g.save(); g.clip(); g.strokeStyle = 'rgba(0,0,0,.3)'; g.lineWidth = 2.5;
  for (let yy = top; yy > top - rh; yy -= 16) { g.beginPath(); g.moveTo(x - ov, yy); g.lineTo(x + w + ov, yy); g.stroke(); for (let xx = x - ov + ((yy / 16) % 2 ? 0 : 10); xx < x + w + ov; xx += 20) { g.beginPath(); g.moveTo(xx, yy); g.lineTo(xx, yy - 16); g.stroke(); } }
  g.restore();
  if (gable) { // gable window
    const gw = w * .16; g.beginPath(); g.rect(x + w / 2 - gw / 2, top - rh * .45, gw, rh * .22); fillStroke(g, '#1b1418', 4);
    wins.push({ type: 'win', x: x + w / 2 - gw / 2, y: top - rh * .45, w: gw, h: rh * .22 });
  }
  // chimney
  if (r() < .6) { const cx = x + w * (.2 + r() * .55), ch = 40 + r() * 30; g.beginPath(); g.rect(cx, top - rh * (gable ? .55 : .6) - ch, 26, ch + 20); fillStroke(g, '#6e5446', 4); }
  g.restore();
  return { x, w, top: top - rh, wins, wall };
}

// ----- church / bell tower -----
function drawTower(g, x, by, w, h, o = {}) {
  g.beginPath(); g.rect(x, by - h, w, h); const tg = g.createLinearGradient(x, 0, x + w, 0); tg.addColorStop(0, '#9a8d7d'); tg.addColorStop(.6, '#b3a796'); tg.addColorStop(1, '#7a6e60'); fillStroke(g, tg, 6);
  g.strokeStyle = 'rgba(40,30,25,.35)'; g.lineWidth = 2.5;
  for (let yy = by - h + 30; yy < by; yy += 30) { g.beginPath(); g.moveTo(x, yy); g.lineTo(x + w, yy); g.stroke(); }
  // belfry opening
  const bw = w * .6, bh = h * .2, bx = x + (w - bw) / 2, byy = by - h + h * .08;
  g.beginPath(); g.moveTo(bx, byy + bh); g.lineTo(bx, byy + bw / 2); g.arc(bx + bw / 2, byy + bw / 2, bw / 2, Math.PI, 0); g.lineTo(bx + bw, byy + bh); g.closePath(); fillStroke(g, '#141018', 5);
  // slit windows
  for (let k = 0; k < 3; k++) { g.beginPath(); g.rect(x + w / 2 - 7, by - h * (.55 - k * .15), 14, 40); fillStroke(g, '#141018', 3); }
  // spire
  g.beginPath(); g.moveTo(x - 14, by - h + 4); g.lineTo(x + w / 2, by - h - w * 1.6); g.lineTo(x + w + 14, by - h + 4); g.closePath();
  const sg = g.createLinearGradient(x, 0, x + w, 0); sg.addColorStop(0, '#2e3442'); sg.addColorStop(.6, '#4a5164'); sg.addColorStop(1, '#262b37'); fillStroke(g, sg, 6);
  g.beginPath(); g.moveTo(x + w / 2, by - h - w * 1.6); g.lineTo(x + w / 2, by - h - w * 1.6 - 50); g.moveTo(x + w / 2 - 16, by - h - w * 1.6 - 32); g.lineTo(x + w / 2 + 16, by - h - w * 1.6 - 32); g.lineWidth = 8; g.strokeStyle = INK; g.stroke();
  return { bell: [bx + bw / 2, byy + bw * .25], bw };
}
function drawBell(ctx, x, y, s, ang, col = '#c9a043') {
  ctx.save(); ctx.translate(x, y); ctx.rotate(ang); ctx.scale(s, s);
  ctx.beginPath(); ctx.moveTo(-12, 0); ctx.lineTo(12, 0); ctx.lineTo(10, -14); ctx.lineTo(-10, -14); ctx.closePath(); fillStroke(ctx, '#3a2a20', 4);
  ctx.beginPath(); ctx.moveTo(-22, 4); ctx.quadraticCurveTo(-26, 50, -46, 74); ctx.lineTo(46, 74); ctx.quadraticCurveTo(26, 50, 22, 4); ctx.quadraticCurveTo(0, -6, -22, 4); ctx.closePath();
  const g = ctx.createLinearGradient(-46, 0, 46, 0); g.addColorStop(0, shade(col, -.35)); g.addColorStop(.35, shade(col, .35)); g.addColorStop(.6, col); g.addColorStop(1, shade(col, -.45)); fillStroke(ctx, g, 5);
  ell(ctx, 0, 74, 46, 8); fillStroke(ctx, shade(col, -.3), 4);
  ell(ctx, Math.sin(ang * -2) * 10, 82, 9, 9); fillStroke(ctx, '#3a2a20', 4);
  ctx.restore();
}

// ----- sky -----
function drawSky(ctx, o) {
  const g = ctx.createLinearGradient(0, o.y0 || 0, 0, o.y1 || H);
  o.stops.forEach(([p, c]) => g.addColorStop(p, c)); ctx.fillStyle = g; ctx.fillRect(o.x || -2000, o.y0 || -2000, o.w || 6000, (o.y1 || H) - (o.y0 || -2000) + 3000);
}
function drawMoon(ctx, x, y, r, col = '#f3e3b8', glowCol = 'rgba(255,220,170,.35)') {
  glow(ctx, x, y, r * 5, glowCol, 1);
  ell(ctx, x, y, r, r); ctx.fillStyle = col; ctx.fill();
  ctx.save(); ell(ctx, x, y, r, r); ctx.clip(); ctx.fillStyle = 'rgba(0,0,0,.08)';
  for (const [dx, dy, rr2] of [[-.3, -.2, .22], [.25, .1, .15], [-.05, .35, .12], [.35, -.35, .1]]) { ell(ctx, x + dx * r, y + dy * r, rr2 * r, rr2 * r); ctx.fill(); }
  ctx.restore();
}
function drawClouds(ctx, t, o) {
  const r = rngFrom(o.seed || 5);
  for (let i = 0; i < (o.n || 8); i++) {
    const y = o.y0 + r() * (o.y1 - o.y0), sp = 10 + r() * 30, w = 300 + r() * 500;
    const x = ((r() * 3000 + t * sp * (o.speed || 1)) % 3400) - 1200;
    ctx.save(); ctx.globalAlpha = (o.a || .5) * (.5 + r() * .5); ctx.fillStyle = o.col || '#2a1f38';
    for (let k = 0; k < 5; k++) { ell(ctx, x + k * w / 5, y + Math.sin(k * 2.1 + i) * 14, w / 4, 40 + r() * 30); ctx.fill(); }
    ctx.restore();
  }
}
function drawStars(ctx, n, seed, a = 1) {
  const r = rngFrom(seed); ctx.save(); ctx.fillStyle = '#fff6dd';
  for (let i = 0; i < n; i++) { ctx.globalAlpha = a * (.3 + r() * .7); const x = r() * 3000 - 1000, y = r() * 1200 - 600; ell(ctx, x, y, 1 + r() * 2, 1 + r() * 2); ctx.fill(); }
  ctx.restore();
}
// cobblestones band
function cobbles(g, x0, y0, w, h, seed, col = '#6a5f57') {
  const r = rngFrom(seed);
  g.save(); g.beginPath(); g.rect(x0, y0, w, h); g.clip();
  g.fillStyle = shade(col, -.45); g.fillRect(x0, y0, w, h);
  let y = y0, row = 0;
  while (y < y0 + h) {
    const sh = 14 + (y - y0) / h * 38; let x = x0 - (row % 2) * sh * .7;
    while (x < x0 + w) {
      const sw = sh * (1.3 + r() * .6);
      rr(g, x + 2, y + 2, sw - 4, sh - 4, sh * .4);
      const c = shade(col, (r() - .5) * .3); g.fillStyle = c; g.fill();
      g.fillStyle = 'rgba(255,255,255,.08)'; rr(g, x + 4, y + 3, sw - 10, (sh - 6) * .4, sh * .3); g.fill();
      x += sw;
    }
    y += sh; row++;
  }
  g.restore();
}

// ----- props -----
function drawShutterPair(ctx, x, y, w, h, open) { // open 1 = fully open (folded out), 0 = closed
  for (const side of [-1, 1]) {
    const hinge = side < 0 ? x : x + w;
    const ang = open * Math.PI * .5;
    const sw = (w / 2) * Math.cos(ang);
    const sx = side < 0 ? hinge - (w / 2) * Math.sin(0) : hinge;
    ctx.save();
    ctx.beginPath();
    if (side < 0) { ctx.moveTo(hinge, y); ctx.lineTo(hinge + sw, y - (w * .08) * Math.sin(ang)); ctx.lineTo(hinge + sw, y + h + (w * .08) * Math.sin(ang)); ctx.lineTo(hinge, y + h); }
    else { ctx.moveTo(hinge, y); ctx.lineTo(hinge - sw, y - (w * .08) * Math.sin(ang)); ctx.lineTo(hinge - sw, y + h + (w * .08) * Math.sin(ang)); ctx.lineTo(hinge, y + h); }
    ctx.closePath(); fillStroke(ctx, shade('#5b3b28', -open * .3), 4);
    ctx.strokeStyle = 'rgba(0,0,0,.4)'; ctx.lineWidth = 2.5;
    for (let k = 1; k < 3; k++) { const u = k / 3; ctx.beginPath(); ctx.moveTo(hinge + (side < 0 ? sw : -sw) * u, y + 2); ctx.lineTo(hinge + (side < 0 ? sw : -sw) * u, y + h - 2); ctx.stroke(); }
    ctx.restore();
  }
}
function drawCart(ctx, x, y, s, wheelA, load = true) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  if (load) { // covered bundles
    for (const [bx, by2, bw] of [[-70, -118, 70], [0, -122, 80], [60, -112, 60], [-20, -150, 90]]) { ell(ctx, bx, by2, bw * .55, 26); fillStroke(ctx, '#cfc2a6', 4); ctx.strokeStyle = 'rgba(60,40,30,.5)'; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(bx - bw * .3, by2); ctx.lineTo(bx + bw * .3, by2); ctx.stroke(); }
  }
  ctx.beginPath(); ctx.moveTo(-130, -100); ctx.lineTo(120, -100); ctx.lineTo(110, -60); ctx.lineTo(-120, -60); ctx.closePath(); fillStroke(ctx, '#6b4a2e', 5);
  ctx.strokeStyle = 'rgba(0,0,0,.35)'; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(-125, -80); ctx.lineTo(115, -80); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(115, -80); ctx.lineTo(220, -70); ctx.lineWidth = 12; ctx.strokeStyle = INK; ctx.stroke(); ctx.lineWidth = 6; ctx.strokeStyle = '#6b4a2e'; ctx.stroke();
  for (const wx of [-70, 60]) {
    ctx.save(); ctx.translate(wx, -44); ctx.rotate(wheelA);
    ell(ctx, 0, 0, 44, 44); fillStroke(ctx, null, 9); ell(ctx, 0, 0, 44, 44); ctx.lineWidth = 5; ctx.strokeStyle = '#7a5634'; ctx.stroke();
    for (let k = 0; k < 6; k++) { ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(Math.cos(k * Math.PI / 3) * 42, Math.sin(k * Math.PI / 3) * 42); ctx.lineWidth = 5; ctx.strokeStyle = INK; ctx.stroke(); }
    ell(ctx, 0, 0, 9, 9); fillStroke(ctx, '#3a2a1c', 4);
    ctx.restore();
  }
  ctx.restore();
}
function drawCandle(ctx, x, y, s, t, h = 90) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  rr(ctx, -14, -h, 28, h, 4); const g = ctx.createLinearGradient(-14, 0, 14, 0); g.addColorStop(0, '#d9c9a2'); g.addColorStop(.5, '#f6ecd2'); g.addColorStop(1, '#bfae88'); fillStroke(ctx, g, 4);
  ell(ctx, 0, 4, 34, 9); fillStroke(ctx, '#8a7a55', 4);
  const fl = 1 + Math.sin(t * 17) * .08 + Math.sin(t * 29) * .05;
  glow(ctx, 0, -h - 18, 260, 'rgba(255,180,80,.6)', 1);
  ctx.beginPath(); ctx.moveTo(0, -h - 42 * fl); ctx.quadraticCurveTo(12, -h - 14, 0, -h - 2); ctx.quadraticCurveTo(-12, -h - 14, 0, -h - 42 * fl);
  ctx.fillStyle = '#ffd27a'; ctx.fill(); ell(ctx, 0, -h - 12, 4, 8); ctx.fillStyle = '#fff6d8'; ctx.fill();
  ctx.restore();
}
function drawClock(ctx, x, y, r, hA, mA, t) {
  ctx.save(); ctx.translate(x, y);
  ell(ctx, 0, 0, r * 1.12, r * 1.12); fillStroke(ctx, '#5a3a22', 8);
  ell(ctx, 0, 0, r, r); const g = ctx.createRadialGradient(-r * .3, -r * .3, r * .1, 0, 0, r); g.addColorStop(0, '#f6e8c4'); g.addColorStop(1, '#c9b07a'); fillStroke(ctx, g, 6);
  ctx.fillStyle = INK; ctx.font = `${r * .2}px ${FONTS.fellsc}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  const RN = ['XII', 'I', 'II', 'III', 'IIII', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI'];
  for (let k = 0; k < 12; k++) { const a = k * TAU / 12 - Math.PI / 2; ctx.fillText(RN[k], Math.cos(a) * r * .78, Math.sin(a) * r * .78); ctx.beginPath(); ctx.moveTo(Math.cos(a) * r * .92, Math.sin(a) * r * .92); ctx.lineTo(Math.cos(a) * r, Math.sin(a) * r); ctx.lineWidth = 4; ctx.strokeStyle = INK; ctx.stroke(); }
  const hand = (a, L, w) => { ctx.save(); ctx.rotate(a); ctx.beginPath(); ctx.moveTo(-w, 0); ctx.lineTo(0, -L); ctx.lineTo(w, 0); ctx.lineTo(0, L * .15); ctx.closePath(); fillStroke(ctx, '#2a1a14', 3); ctx.restore(); };
  hand(hA, r * .5, r * .06); hand(mA, r * .78, r * .04);
  ell(ctx, 0, 0, r * .06, r * .06); fillStroke(ctx, '#b8902f', 3);
  ctx.restore();
}
function drawGoblet(ctx, x, y, s, rot = 0) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
  ctx.beginPath(); ctx.moveTo(-22, -60); ctx.quadraticCurveTo(-20, -24, 0, -20); ctx.quadraticCurveTo(20, -24, 22, -60); ctx.closePath(); fillStroke(ctx, '#c9a043', 4);
  ctx.beginPath(); ctx.moveTo(-3, -20); ctx.lineTo(-3, -4); ctx.lineTo(3, -4); ctx.lineTo(3, -20); fillStroke(ctx, '#a8822c', 3); ell(ctx, 0, -2, 16, 5); fillStroke(ctx, '#a8822c', 3);
  ell(ctx, 0, -58, 20, 5); ctx.fillStyle = '#6a0f1e'; ctx.fill();
  ctx.restore();
}
function drawBook(ctx, x, y, w, h, open, o = {}) { // open: 0 closed .. 1 flat
  ctx.save(); ctx.translate(x, y);
  // cover
  rr(ctx, -w * .53, -h * .52, w * 1.06, h * 1.04, 18); fillStroke(ctx, '#4a1a16', 7);
  ctx.restore();
}
