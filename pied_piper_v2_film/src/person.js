// person: draws an articulated character (townsfolk, children, the Piper) in the studio's ink style
'use strict';
const C = require('./core');
const R = require('./rig');
const K = require('./ink');
const { clamp, lerp, TAU, noise } = C;
const { PAL, INK } = K;
const { v, add, mul, rotY } = R;

const wrap = a => Math.atan2(Math.sin(a), Math.cos(a));
const tzz = J => R.proj(J, J.chest)[2];

// ---------------------------------------------------------------- character presets
function makeChar(o) {
  const body = o.body || 'adult';
  const B = { ...R.BODY[body], ...(o.dims || {}) };
  return {
    body, B, k: o.k ?? 1, name: o.name || body,
    skin: o.skin || PAL.skin, skinSh: o.skinSh || PAL.skinSh,
    outfit: o.outfit || 'tunic', // tunic | dress | robe | piper
    top: o.top || PAL.red, topD: o.topD || K.shade(o.top || PAL.red, -.35),
    bodice: o.bodice || null, sleeve: o.sleeve || PAL.mustard, sleeveD: K.shade(o.sleeve || PAL.mustard, -.3),
    skirt: o.skirt || o.top || PAL.red, legs: o.legs || PAL.blue, legs2: o.legs2 || null, shoe: o.shoe || PAL.brown,
    apron: o.apron || null, belt: o.belt ?? PAL.brownD, pouch: o.pouch ?? true, chain: o.chain || false, lacing: o.lacing ?? true,
    hat: o.hat || 'coif', hatCol: o.hatCol || PAL.coif, hatCol2: o.hatCol2 || PAL.red, hair: o.hair || 'none', hairCol: o.hairCol || '#6b3f22',
    brow: o.brow || o.hairCol || '#5a3420', eyeR: o.eyeR ?? 1, faceW: o.faceW ?? 1, chin: o.chin ?? 1, nose: o.nose || 'button',
    blush: o.blush ?? .55, beard: o.beard || null, hem: o.hem, cape: o.cape || null, seed: o.seed || 1,
  };
}

// ---------------------------------------------------------------- main draw
// o: {x, y (ground screen), s (scale), lw, sil (silhouette colour), lagA, lagB (poses at t-lag), wind, alpha, light}
function drawPerson(g, ch, P, o = {}) {
  const B = ch.B, s = (o.s ?? 1) * ch.k;
  const J = R.solve(B, P);
  const JA = o.lagA ? R.solve(B, o.lagA) : J, JB = o.lagB ? R.solve(B, o.lagB) : JA;
  const pr = p => R.proj(J, p, 1);
  const lw = (o.lw ?? 4.6) / s;
  const sil = o.sil || null;
  const F = c => sil || c;
  g.save();
  g.translate(o.x || 0, o.y || 0); g.scale(s, s);
  if (o.alpha != null) g.globalAlpha *= o.alpha;
  const yaw = J.yaw; const cy = Math.cos(yaw), sy = Math.sin(yaw);
  const items = [];
  const Z = p => pr(p)[2];
  // ground shadow
  if (o.shadow !== false && !sil) {
    g.save(); g.globalAlpha *= o.shadowA ?? .22; g.fillStyle = '#1b0f08';
    g.beginPath(); g.ellipse(pr(J.pel)[0], 0, 62 * B.slim * (B.hipW / 21 * .8 + .2) + 10, 13, 0, 0, TAU); g.fill(); g.restore();
  }
  // ---- cloak (behind everything) for the Piper or caped characters
  if (ch.outfit === 'piper' || ch.cape) items.push({ z: Math.cos(J.yaw) < -.05 ? tzz(J) + 20 : -999, d: () => drawCloak(g, ch, J, JA, JB, o, lw, pr, F) });
  // ---- legs
  for (const sd of ['l', 'r']) {
    const z = (Z(J['knee' + sd]) + Z(J['ankle' + sd])) / 2;
    items.push({ z: z - 30, d: () => drawLeg(g, ch, J, sd, lw, pr, F) });
  }
  // ---- torso + skirt
  const tz = Z(J.chest);
  items.push({ z: tz, d: () => drawTorso(g, ch, J, JA, JB, lw, pr, F, o) });
  // ---- arms
  if (!o.noArms) for (const sd of ['l', 'r']) {
    const zz = (Z(J['el' + sd]) + Z(J['wr' + sd])) / 2;
    const front = zz > tz - 2;
    items.push({ z: front ? zz + 40 : zz - 40, d: () => drawArm(g, ch, J, sd, lw, pr, F, P) });
  }
  // ---- head
  items.push({ z: tz + 30 + (Math.cos(yaw + J.head.yaw) < -.2 ? -200 : 0) * 0, d: () => drawHead(g, ch, J, JA, P.face || {}, lw, pr, F, o) });
  if (P.prop) items.push({ z: P.prop.z ?? (Math.cos(yaw + J.head.yaw * .5) < -.15 ? tz - 60 : tz + 60), d: () => P.prop.draw(g, J, pr, lw) });
  items.sort((a, b) => a.z - b.z);
  for (const it of items) it.d();
  g.restore();
  return J;
}

// ---------------------------------------------------------------- legs
function drawLeg(g, ch, J, sd, lw, pr, F) {
  const B = ch.B; const sl = B.slim;
  const H = pr(J['hip' + sd]), Kp = pr(J['knee' + sd]), A = pr(J['ankle' + sd]), T = pr(J['toe' + sd]);
  const col = (ch.legs2 && sd === 'r') ? ch.legs2 : ch.legs;
  const r = [15 * sl * B.hipW / 21 + 2, 11.5 * sl * B.hipW / 21 + 1.5, 8.5 * sl * B.hipW / 21 + 1];
  K.shape(g, K.tubePts([[H[0], H[1]], [Kp[0], Kp[1]], [A[0], A[1]]], r), { fill: F(col), lw, smooth: true, tension: .35 });
  // knee crease
  if (!ch.sil) K.line(g, [[Kp[0] - r[1] * .5, Kp[1]], [Kp[0] + r[1] * .3, Kp[1] + 2]], lw * .5, INK, .35);
  // shoe: heel at ankle, toe forward
  const pointy = ch.outfit === 'piper' ? 1.6 : 1;
  const tx = A[0] + (T[0] - A[0]) * pointy, ty = A[1] + (T[1] - A[1]) * pointy;
  const P = [[A[0] - 9, A[1] - 6], [A[0] + 8, A[1] - 7], [tx + (tx > A[0] ? 3 : -3), ty - 2], [tx, ty + 6], [A[0] - 10, A[1] + 7]];
  const flat = Math.abs(tx - A[0]) < 8; // front view: rounded shoe
  if (flat) K.ellipse(g, A[0], A[1] + 2, 11 * (B.hipW / 21 * .5 + .5), 9, { fill: F(ch.shoe), lw });
  else K.shape(g, P, { fill: F(ch.shoe), lw, tension: .4 });
}

// ---------------------------------------------------------------- torso + skirt
function torsoSil(J, B, sections) {
  const yaw = J.yaw;
  const L = [], Rt = [];
  for (const [h, a, b] of sections) {
    const c = R.proj(J, R.add(J.pel, J.chestFrame.bend(v(0, h, 0))));
    const tw = yaw + 0; const e = Math.sqrt((a * Math.cos(tw)) ** 2 + (b * Math.sin(tw)) ** 2);
    L.push([c[0] - e, c[1]]); Rt.push([c[0] + e, c[1]]);
  }
  return { L, R: Rt };
}
function drawTorso(g, ch, J, JA, JB, lw, pr, F, o) {
  const B = ch.B, w = B.shW, sl = B.slim;
  const piper = ch.outfit === 'piper';
  // skirt / hem first (under bodice)
  const hemH = ch.hem ?? (ch.outfit === 'dress' ? 18 : ch.outfit === 'robe' ? 10 : piper ? B.hip * .62 : B.hip * .48);
  const waist = pr(R.add(J.pel, J.chestFrame.bend(v(0, B.waist * .6, 0))));
  const cy = Math.cos(J.yaw), sy = Math.sin(J.yaw);
  const hipA = B.hipW * 1.55 + 6, hipB = B.hipW * 1.1;
  const flare = ch.outfit === 'dress' ? 1.75 : ch.outfit === 'robe' ? 1.45 : piper ? 1.35 : 1.4;
  // hem follows legs + lags behind body motion (follow-through)
  const legC = (J.kneel[0] + J.kneer[0] + J.anklel[0] + J.ankler[0]) / 4;
  const legZ = (J.kneel[2] + J.kneer[2] + J.anklel[2] + J.ankler[2]) / 4;
  const lagX = (J.pel[0] - JB.pel[0]) * 1.6, lagZ = (J.pel[2] - JB.pel[2]) * 1.6, lagY = (J.pel[1] - JA.pel[1]);
  const hemC = R.proj(J, v(lerp(J.pel[0], legC, .5) - lagX, hemH - lagY * .4, lerp(J.pel[2], legZ, .4) - lagZ));
  const spreadK = Math.abs(J.anklel[0] - J.ankler[0]) / (B.hipW * 2 + 10);
  const ha = hipA * flare * (0.9 + .25 * clamp(spreadK - 1, 0, 1.5)), hb = hipB * flare;
  const he = Math.sqrt((ha * cy) ** 2 + (hb * sy) ** 2);
  const we = Math.sqrt((hipA * cy) ** 2 + (hipB * sy) ** 2);
  const n = 7; const hem = [];
  for (let i = 0; i <= n; i++) {
    const u = i / n; const x = lerp(hemC[0] + he, hemC[0] - he, u);
    const wav = Math.sin(u * Math.PI * n) * 3 + noise(u * 5 + ch.seed) * 2;
    hem.push([x, hemC[1] + wav + Math.sin(u * Math.PI) * 5]);
  }
  const skirtPts = [[waist[0] - we, waist[1]], [waist[0] + we, waist[1]], ...hem];
  const skirtCol = ch.skirt;
  const pied = piper;
  const drawSkirt = () => K.shape(g, skirtPts, {
    fill: F(skirtCol), lw, tension: .35,
    inner: ch.sil ? null : (g2) => {
      if (pied) { g2.fillStyle = PAL.pgreen; g2.beginPath(); g2.rect(waist[0] - (cy >= 0 ? 0 : 400), waist[1] - 10, 400, 400); g2.fill(); }
      // pleats
      g2.strokeStyle = K.rgba(INK, .35); g2.lineWidth = lw * .55;
      for (let i = 1; i < n; i++) { const hx = hem[i][0], hy = hem[i][1]; const wx = lerp(waist[0] + we, waist[0] - we, i / n); g2.beginPath(); g2.moveTo(wx, waist[1] + 6); g2.lineTo(lerp(wx, hx, .9), hy - 4); g2.stroke(); }
      // shading on the far side
      g2.fillStyle = K.rgba('#2a1505', .14); g2.beginPath(); g2.rect(waist[0] + (sy > 0 ? -400 : we * .35), waist[1] - 10, 400 - we * .35, 400); g2.fill();
    },
  });
  if (ch.apron && !piper) { /* drawn after bodice */ }
  drawSkirt();
  if (ch.apron) {
    const ax = waist[0] + sy * we * .2, aw = we * .75 * Math.abs(cy) + 4;
    if (cy > -.1) K.shape(g, [[ax - aw, waist[1] + 2], [ax + aw, waist[1] + 2], [ax + aw * 1.15, hemC[1] - 14], [ax - aw * 1.15, hemC[1] - 14]], { fill: F(ch.apron), lw, tension: .2 });
  }
  // bodice / doublet
  const secs = [[-8, B.hipW * 1.45 + 5, B.hipW * 1.1], [B.waist, B.hipW * 1.25 + 3, B.hipW], [B.chest * .8, w * .78, w * .55],
    [B.shY - 16, w * .98, w * .6], [B.shY + 2, w * .82, w * .5]];
  const T = torsoSil(J, B, secs);
  const top = pr(J.neck);
  const TL = T.L.slice(), TR = T.R.slice();
  const torsoPts = [...TL, [top[0] - w * .35 * Math.abs(cy) - 6, top[1] + 8], [top[0] + w * .35 * Math.abs(cy) + 6, top[1] + 8], ...TR.reverse()];
  const bodCol = ch.bodice || ch.top;
  K.shape(g, torsoPts, {
    fill: F(bodCol), lw, tension: .4,
    inner: ch.sil ? null : (g2) => {
      const ch0 = pr(J.chest), wst = pr(J.waist);
      if (pied) { // split doublet
        const mx = ch0[0] + sy * w * .55;
        g2.fillStyle = PAL.pgreen; g2.beginPath(); g2.rect(cy >= 0 ? mx : mx - 400, ch0[1] - 300, 400, 600); g2.fill();
        g2.strokeStyle = K.rgba(PAL.gold, .9); g2.lineWidth = lw * .7; g2.beginPath(); g2.moveTo(mx, top[1] + 8); g2.lineTo(mx + (wst[0] - ch0[0]), wst[1] + 30); g2.stroke();
        for (let i = 0; i < 4; i++) { const yy = lerp(top[1] + 30, wst[1], i / 3.5); K.ellipse(g2, mx + (wst[0] - ch0[0]) * (i / 4) , yy, 3.2, 3.2, { fill: PAL.gold, lw: lw * .4 }); }
      } else if (ch.lacing && cy > 0.15) { // DP bodice with lacing
        const bw = w * .36 * cy;
        const cx0 = top[0] + sy * w * .45;
        g2.fillStyle = K.shade(bodCol === ch.top ? PAL.black : bodCol, -.1);
        const dxw = (wst[0] - top[0]);
        g2.beginPath(); g2.moveTo(cx0 - bw, top[1] + 14); g2.lineTo(cx0 + bw, top[1] + 14); g2.lineTo(cx0 + bw * .8 + dxw, wst[1] + 8); g2.lineTo(cx0 - bw * .8 + dxw, wst[1] + 8); g2.closePath(); g2.fill();
        g2.strokeStyle = K.rgba('#e9dcc0', .75); g2.lineWidth = lw * .45; g2.beginPath();
        for (let i = 0; i < 4; i++) { const y0 = lerp(top[1] + 24, wst[1] - 4, i / 4), y1 = y0 + (wst[1] - top[1]) / 9; g2.moveTo(cx0 - bw * .45, y0); g2.lineTo(cx0 + bw * .45, y0 + 4); g2.lineTo(cx0 - bw * .4, y1); }
        g2.stroke();
      }
      // soft side shading
      g2.fillStyle = K.rgba('#2a1505', .16); g2.beginPath(); const sx = ch0[0] + (sy > 0 ? -1 : 1) * w * .5 * Math.abs(cy); g2.rect(sy > 0 ? sx - 400 : sx, ch0[1] - 300, 400, 600); g2.fill();
    },
  });
  // belt + pouch
  if (ch.belt && !ch.sil) {
    const wl = T.L[1] || T.L[0];
    const bl = pr(R.add(J.pel, J.chestFrame.bend(v(0, B.waist * .55, 0))));
    const be = Math.sqrt(((B.hipW * 1.28 + 3) * cy) ** 2 + ((B.hipW) * sy) ** 2);
    K.line(g, [[bl[0] - be, bl[1]], [bl[0] + be, bl[1] + 2]], lw * 1.5, F(ch.belt), 1, false);
    if (ch.pouch && cy > -.2) {
      const px = bl[0] + sy * be * .5 - cy * be * .45 * (ch.seed % 2 ? 1 : -1) , py = bl[1] + 4;
      const sw = (J.pel[0] - JA.pel[0]) * .8;
      K.shape(g, [[px - 6, py], [px + 6, py], [px + 9 - sw, py + 16], [px - sw, py + 26], [px - 9 - sw, py + 16]], { fill: F('#7a5233'), lw: lw * .8, tension: .6 });
    }
  }
  if (ch.chain && !ch.sil && cy > 0) {
    const c0 = pr(J.neck), c1 = pr(J.chest);
    g.save(); g.strokeStyle = PAL.gold; g.lineWidth = lw * 1.1; g.beginPath(); g.moveTo(c0[0] - w * .5 * cy, c0[1] + 10); g.quadraticCurveTo(c1[0], c1[1] + 8, c0[0] + w * .5 * cy, c0[1] + 10); g.stroke();
    K.ellipse(g, c1[0], c1[1] + 10, 8, 9, { fill: PAL.gold, lw: lw * .6 }); g.restore();
  }
  // neck
  const nk = pr(J.neck), sc = pr(J.shc);
  K.capsule(g, [sc[0], sc[1] + 4], [nk[0], nk[1] - 6], 9 * sl + 3, 9 * sl + 3, { fill: F(ch.skin), lw });
}

// ---------------------------------------------------------------- arms
function drawArm(g, ch, J, sd, lw, pr, F, P) {
  const B = ch.B, sl = B.slim;
  const S = pr(J['sh' + sd]), E = pr(J['el' + sd]), Wr = pr(J['wr' + sd]);
  const r0 = 13 * sl * (B.ua / 72) + 2, r1 = 10.5 * sl * (B.ua / 72) + 2;
  let col = ch.sleeve;
  if (ch.outfit === 'piper') col = sd === 'l' ? PAL.burg : PAL.pgreen;
  K.capsule(g, [S[0], S[1]], [E[0], E[1]], r0, r1, { fill: F(col), lw });
  K.capsule(g, [E[0], E[1]], [Wr[0], Wr[1]], r1, r1 * .85, { fill: F(K.shade(col, ch.outfit === 'piper' ? 0 : -.08)), lw });
  if (!ch.sil && ch.outfit !== 'piper') { // cuff
    const dx = Wr[0] - E[0], dy = Wr[1] - E[1], L = Math.hypot(dx, dy) || 1;
    const cx = Wr[0] - dx / L * 6, cyy = Wr[1] - dy / L * 6;
    K.line(g, [[cx - dy / L * r1 * .9, cyy + dx / L * r1 * .9], [cx + dy / L * r1 * .9, cyy - dx / L * r1 * .9]], lw * .6, INK, .5, false);
  }
  const hand = (P.hands && P.hands[sd]) || 'mitten';
  drawHand(g, ch, Wr, Math.atan2(Wr[1] - E[1], Wr[0] - E[0]), hand, lw, F, sd, r1);
}
function drawHand(g, ch, W, ang, type, lw, F, sd, r) {
  if (type === 'none') return;
  const s = (ch.B.ua / 72) * (ch.body === 'child' ? 1.1 : 1);
  g.save(); g.translate(W[0], W[1]); g.rotate(ang - Math.PI / 2); g.scale(s, s);
  const fill = F(ch.skin);
  if (type === 'open') { // palm with spread fingers
    K.shape(g, [[-9, -2], [9, -2], [12, 10], [14, 22], [8, 24], [6, 14], [3, 27], [-2, 27], [-3, 15], [-7, 25], [-12, 22], [-10, 10], [-15, 4]], { fill, lw, tension: .25 });
  } else if (type === 'point') {
    K.shape(g, [[-9, -2], [9, -2], [10, 12], [3, 30], [-2, 30], [-2, 18], [-10, 14]], { fill, lw, tension: .3 });
  } else if (type === 'fist') {
    K.ellipse(g, 0, 8, 11, 11, { fill, lw });
  } else { // DP mitten: round with a little thumb
    K.ellipse(g, 0, 9, 10.5, 12, { fill, lw });
    K.ellipse(g, (sd === 'l' ? 1 : -1) * 8, 4, 4.5, 6, { fill, lw: lw * .8 }, .3);
  }
  g.restore();
}

// ---------------------------------------------------------------- head + face
function headShape(w, h, chin, narrow) {
  const P = [];
  for (let i = 0; i < 28; i++) {
    const a = i / 28 * TAU; const c = Math.cos(a), s = Math.sin(a);
    let x = c * w / 2, y = s * h / 2;
    if (s > 0) { x *= 1 - .22 * s * chin * (narrow ? 1.5 : 1); y *= 1 + .04 * chin; }   // chin taper
    else { x *= 1 - .06 * (-s); }
    P.push([x, y]);
  }
  return P;
}
function drawHead(g, ch, J, JA, face, lw, pr, F, o) {
  const B = ch.B; const hc = pr(J.headC);
  const hy = wrap(J.yaw + J.head.yaw); const fc = Math.cos(hy), sn = Math.sin(hy);
  const w = B.headW * ch.faceW, h = B.headH; const piper = ch.outfit === 'piper';
  const pitch = J.head.pitch;
  g.save(); g.translate(hc[0], hc[1]); g.rotate(J.head.roll);
  const hw = w * (.86 + .14 * Math.abs(fc));
  const lagRoll = (J.headC[0] - (JA.headC ? JA.headC[0] : J.headC[0])) * .004;
  // back layer of headwear / hair
  drawHeadwear(g, ch, 'back', hw, h, fc, sn, lw, F, lagRoll, o);
  // ears (profile-ish)
  if (Math.abs(sn) > .35 && ['none', 'bowl', 'short', 'long', 'bald'].includes(ch.hair) && !['coif', 'hood'].includes(ch.hat) && fc > -.3) {
    K.ellipse(g, -sn * hw * .12, 4, 9, 13, { fill: F(ch.skin), lw });
  }
  // face
  const HP = headShape(hw, h, ch.chin, piper);
  K.shape(g, HP, { fill: F(ch.skin), lw, inner: ch.sil || o.sil ? null : (g2) => {
    // soft shading on the far side + under the hat
    g2.fillStyle = K.rgba('#7a3a20', .14); g2.beginPath(); g2.ellipse(-hw * .1, -h * .06, hw * .5, h * .5, 0, 0, TAU); g2.rect(-400, -400, 800, 800); g2.fill('evenodd');
  } });
  drawSkullHair(g, ch, HP, hw, h, fc, sn, lw, F, o);
  if (ch.beard && fc > -.2) { const sx = sn * hw * .18; K.shape(g, [[-hw * .47 + sx, h * .02], [-hw * .3 + sx, h * .18], [hw * .3 + sx, h * .18], [hw * .47 + sx, h * .02], [hw * .3 + sx * 1.3, h * .48], [sx * 1.3, h * .6], [-hw * .3 + sx * 1.3, h * .48]], { fill: F(ch.beard), lw, tension: .5 }); }
  if (!(ch.sil || o.sil) && fc > -.25) drawFace(g, ch, face, hw, h, fc, sn, pitch, lw, o);
  if (piper && !(ch.sil || o.sil)) { // brim shadow over the eyes
    g.save(); g.beginPath(); K.smooth(g, HP, true); g.clip(); const gr = g.createLinearGradient(0, -h * .5, 0, h * .05); gr.addColorStop(0, 'rgba(25,12,20,.55)'); gr.addColorStop(.75, 'rgba(25,12,20,.18)'); gr.addColorStop(1, 'rgba(25,12,20,0)'); g.fillStyle = gr; g.fillRect(-hw, -h, hw * 2, h * 1.05); g.restore();
    if (face.glow) for (const sd of [-1, 1]) K.glow(g, sn * hw * .36 + sd * hw * .19 * Math.max(.25, Math.abs(fc)), -h * .06, 10 + 14 * face.glow, '#cfe8c0', .6 * face.glow); }
  drawHeadwear(g, ch, 'front', hw, h, fc, sn, lw, F, lagRoll, o);
  g.restore();
}
function drawFace(g, ch, f, w, h, fc, sn, pitch, lw, o) {
  const piper = ch.outfit === 'piper';
  const py = pitch * h * .35;
  const cx = sn * w * .36;
  const eyeY = -h * .02 + py + (piper ? -h * .04 : 0);
  const sep = w * (piper ? .19 : .21) * Math.max(.25, Math.abs(fc));
  const er = w * .105 * ch.eyeR * (piper ? .82 : 1);
  const eyes = f.eyes || 'open';
  const look = f.look || [0, 0];
  for (const sd of [-1, 1]) {
    const ex = cx + sd * sep * (fc >= 0 ? 1 : -1);
    const far = sd * sn < 0 ? 0 : 0;
    if (Math.abs(sn) > .72 && sd * sn < 0) continue;   // hidden far eye in profile
    const sq = Math.abs(sn) > .4 && sd * sn < 0 ? .7 : 1;
    const rx = er * sq * (.75 + .25 * Math.abs(fc)), ry = er * (piper ? .78 : 1.05);
    // sclera
    K.ellipse(g, ex, eyeY, rx, ry, { fill: piper ? '#f1e6d5' : PAL.white, lw: lw * .75 });
    // pupil
    const pr2 = er * (piper ? .48 : .36) * (f.pupil ?? 1);
    const pxx = ex + look[0] * rx * .45 + sn * rx * .25, pyy = eyeY + look[1] * ry * .4;
    g.save(); g.beginPath(); g.ellipse(ex, eyeY, rx, ry, 0, 0, TAU); g.clip();
    if (piper) { K.ellipse(g, pxx, pyy, pr2, pr2, { fill: '#3e5a3c', lw: 0 }); K.ellipse(g, pxx, pyy, pr2 * .55, pr2 * .55, { fill: '#0e0a0a', lw: 0 }); }
    else K.ellipse(g, pxx, pyy, pr2, pr2, { fill: '#1a1210', lw: 0 });
    if (f.glint !== false) K.ellipse(g, pxx - pr2 * .35, pyy - pr2 * .4, pr2 * .32 * (f.glint ?? 1), pr2 * .32 * (f.glint ?? 1), { fill: '#fff', lw: 0 });
    // eyelid
    let lid = eyes === 'half' ? .52 : eyes === 'closed' ? 1.05 : eyes === 'sleepy' ? .38 : eyes === 'narrow' ? .62 : eyes === 'wide' ? -.1 : (piper ? .3 : .06);
    lid = Math.max(lid, f.blink || 0);
    if (lid > 0) {
      g.fillStyle = ch.skin; g.beginPath(); g.rect(ex - rx - 2, eyeY - ry - 2, rx * 2 + 4, (ry * 2 + 2) * lid); g.fill();
      g.restore();
      K.line(g, [[ex - rx * 1.02, eyeY - ry + 2 * ry * lid], [ex, eyeY - ry + 2 * ry * lid - 2], [ex + rx * 1.02, eyeY - ry + 2 * ry * lid]], lw * .9, INK);
    } else g.restore();
    if (f.bags || eyes === 'sleepy') K.line(g, [[ex - rx * .8, eyeY + ry * 1.1], [ex, eyeY + ry * 1.3], [ex + rx * .8, eyeY + ry * 1.1]], lw * .45, INK, .45);
    // brow
    const bt = f.brow || 'neutral';
    const by = eyeY - ry - h * (piper ? .05 : .07) - (bt === 'raised' ? 7 : 0);
    let inner = 0; if (bt === 'worry') inner = -7; if (bt === 'angry') inner = 7; if (bt === 'sly') inner = sd > 0 ? -5 : 4;
    const b0 = [ex - rx * 1.05 * (fc >= 0 ? 1 : -1) * -sd * -1, by], b1 = [ex + sd * rx * 1.05, by];
    const innerX = ex - sd * rx * 1.0, outerX = ex + sd * rx * 1.1;
    K.line(g, [[innerX, by + inner], [ex, by - 3], [outerX, by + 2]], lw * (piper ? 1.4 : 1.7), ch.brow);
  }
  // nose
  const nx = cx + sn * w * .1, ny = eyeY + h * .13;
  if (Math.abs(sn) > .55) K.shape(g, [[nx, ny - 14], [nx + sn * (piper ? 18 : 12), ny + 4], [nx, ny + 6]], { fill: ch.skin, lw: lw * .8, tension: .3, closed: false });
  else if (piper) K.line(g, [[nx - 1, ny - 18], [nx + 4, ny + 2], [nx - 4, ny + 5]], lw * .75, INK);
  else K.line(g, [[nx + 2, ny - 7], [nx + 5, ny + 2], [nx - 2, ny + 4]], lw * .75, INK);
  // blush
  if (ch.blush && !piper) for (const sd of [-1, 1]) { if (Math.abs(sn) > .6 && sd * sn < 0) continue; K.ellipse(g, cx + sd * sep * 1.25, eyeY + h * .17, w * .085, w * .05, { fill: K.rgba(PAL.blush, ch.blush * (f.flush ?? 1)), lw: 0 }); }
  // mouth
  const mx = cx + sn * w * .06, my = eyeY + h * (piper ? .3 : .27);
  const m = f.mouth || 'closed';
  const mw = w * (piper ? .13 : .12) * (.6 + .4 * Math.abs(fc));
  if (m === 'closed') K.line(g, [[mx - mw, my], [mx, my + 1], [mx + mw, my]], lw * .75, INK);
  else if (m === 'smile' || m === 'peace') K.line(g, [[mx - mw * 1.1, my - 2], [mx, my + (m === 'peace' ? 4 : 7)], [mx + mw * 1.1, my - 2]], lw * .8, INK);
  else if (m === 'sly') K.line(g, [[mx - mw * 1.1, my + 1], [mx + mw * .3, my + 3], [mx + mw * 1.2, my - 5]], lw * .8, INK);
  else if (m === 'frown') K.line(g, [[mx - mw, my + 4], [mx, my - 2], [mx + mw, my + 4]], lw * .8, INK);
  else if (m === 'flat') K.line(g, [[mx - mw * .9, my + 1], [mx + mw * .9, my + 1]], lw * .8, INK, 1, false);
  else if (m === 'o' || m === 'gasp') K.ellipse(g, mx, my + 3, mw * (m === 'gasp' ? .75 : .5), mw * (m === 'gasp' ? 1.0 : .62), { fill: '#5a2320', lw: lw * .75 });
  else if (m === 'laugh' || m === 'grin') {
    const oh = m === 'laugh' ? mw * 1.1 : mw * .55;
    K.shape(g, [[mx - mw * 1.25, my - 3], [mx + mw * 1.25, my - 3], [mx + mw * .7, my + oh], [mx - mw * .7, my + oh]], { fill: '#5a2320', lw: lw * .8, tension: .5 });
    K.shape(g, [[mx - mw * 1.0, my - 2], [mx + mw * 1.0, my - 2], [mx + mw * .8, my + 3], [mx - mw * .8, my + 3]], { fill: '#f4ecdc', lw: 0, tension: .5 });
  } else if (m === 'flute') { K.ellipse(g, mx, my, mw * .45, mw * .35, { fill: '#6a2f2b', lw: lw * .6 }); }
  if (f.tear) K.shape(g, [[cx + sep * 1.1, eyeY + 14 + f.tear * 30], [cx + sep * 1.1 + 4, eyeY + 24 + f.tear * 30], [cx + sep * 1.1, eyeY + 28 + f.tear * 30], [cx + sep * 1.1 - 4, eyeY + 24 + f.tear * 30]], { fill: '#bfe3f2', lw: lw * .5 });
  if (f.sweat) K.shape(g, [[cx - w * .42, -h * .2], [cx - w * .38, -h * .1], [cx - w * .42, -h * .06], [cx - w * .46, -h * .1]], { fill: '#bfe3f2', lw: lw * .5 });
}

// hair covering the skull everywhere except a face window that follows head yaw (works front/profile/back)
function drawSkullHair(g, ch, HP, w, h, fc, sn, lw, F, o) {
  const hair = ch.hair;
  if (!['short', 'bowl', 'long', 'piper', 'braids'].includes(hair)) return;
  if ((ch.hat === 'coif' || ch.hat === 'hood')) return;
  const col = F(ch.hairCol);
  const fcl = Math.max(0, fc);
  const wx = sn * w * .3, wy = h * (hair === 'bowl' ? .16 : .12);
  const rx = w * (.3 + .2 * fcl), ry = h * (hair === 'bowl' ? .36 : .42);
  g.save();
  g.beginPath(); K.smooth(g, HP.map(p => [p[0] * 1.04, p[1] * 1.03 - 2]), true); g.clip();
  g.beginPath(); g.rect(-w, -h, w * 2, h * 2);
  if (fc > -.15) { g.ellipse(wx, wy, rx * Math.min(1, (fc + .15) * 2.5), ry, 0, 0, TAU); }
  g.fillStyle = col; g.fill('evenodd'); g.clip('evenodd');
  // hair strands (clipped to the hair region)
  if (!(ch.sil || o.sil)) { g.strokeStyle = K.rgba(INK, .3); g.lineWidth = lw * .5; for (let i = -3; i <= 3; i++) { g.beginPath(); g.moveTo(i * w * .12 - sn * w * .2, -h * .48); g.quadraticCurveTo(i * w * .14 - sn * w * .4, -h * .1, i * w * .1 - sn * w * .45, h * .3); g.stroke(); } }
  g.restore();
  if (fc > -.15) { // hairline ink
    g.save(); g.beginPath(); K.smooth(g, HP, true); g.clip();
    g.beginPath(); g.ellipse(wx, wy, rx * Math.min(1, (fc + .15) * 2.5), ry, 0, Math.PI, TAU); g.lineWidth = lw * .8; g.strokeStyle = INK; g.stroke(); g.restore();
  }
  // a fringe tuft for bowl cuts
  if (hair === 'bowl' && fc > .2) K.shape(g, [[wx - rx, wy - ry * .55], [wx + rx, wy - ry * .55], [wx + rx * .9, wy - ry * .25], [wx, wy - ry * .35], [wx - rx * .9, wy - ry * .25]], { fill: col, lw: lw * .8, tension: .4 });
  K.shape(g, HP, { lw, fill: null });
}

function drawHeadwear(g, ch, layer, w, h, fc, sn, lw, F, lagRoll, o) {
  const hat = ch.hat, hair = ch.hair;
  const back = layer === 'back', front = !back;
  const sx = sn * w * .18;
  const fcol = F;
  // ---------------- hair
  if (hair === 'braids' && back) {
    for (const sd of [-1, 1]) { const bx = sd * w * .42 * Math.abs(fc) + sx * .2; const P = []; for (let i = 0; i < 6; i++) P.push([bx + Math.sin(i * 1.3 + lagRoll * 40) * 3 + lagRoll * 200 * i, -h * .05 + i * 18]); K.shape(g, K.tubePts(P, P.map((_, i) => 9 - i * .7)), { fill: fcol(ch.hairCol), lw }); for (let i = 1; i < 6; i++) K.line(g, [[P[i][0] - 6, P[i][1] - 4], [P[i][0] + 6, P[i][1] + 2]], lw * .5, INK, .5); }
  }
  if ((hair === 'long' || hair === 'piper') && back) {
    const lenH = hair === 'piper' ? h * .62 : h * .7;
    K.shape(g, [[-w * .52, -h * .25], [w * .52, -h * .25], [w * .58 - lagRoll * 120, lenH], [w * .2, lenH + 10], [-w * .2, lenH + 8], [-w * .58 - lagRoll * 120, lenH]], { fill: fcol(ch.hairCol), lw, tension: .4 });
  }
  if (back && (hat === 'coif' || hat === 'hood')) {
    const col = hat === 'hood' ? ch.hatCol : ch.hatCol;
    K.shape(g, headShape(w * 1.26, h * 1.16, .6).map(p => [p[0] + sx * .1, p[1] - 4]), { fill: fcol(col), lw });
  }
  if (front) {
    if (hair === 'bald') for (const sd of [-1, 1]) K.shape(g, [[sd * w * .5 + sx * .4, h * .02], [sd * w * .52 + sx * .4, -h * .2], [sd * w * .43 + sx * .4, -h * .14], [sd * w * .44 + sx * .4, h * .04]], { fill: fcol(ch.hairCol), lw: lw * .8, tension: .4 });
  }
  // ---------------- hats
  if ((hat === 'coif' || hat === 'hood') && front && fc < -.05) { K.shape(g, headShape(w * 1.2, h * 1.1, .6).map(p => [p[0], p[1] - 4]), { fill: fcol(ch.hatCol), lw }); if (!(ch.sil || o.sil)) { K.line(g, [[-sn * w * .1, -h * .55], [-sn * w * .15, -h * .1], [-sn * w * .05, h * .45]], lw * .6, INK, .45); K.line(g, [[-w * .55, h * .18], [0, h * .26], [w * .55, h * .18]], lw * .9, hat === 'coif' ? ch.hatCol2 : K.shade(ch.hatCol, -.3), .8); } return; }
  if (hat === 'coif' && front) {
    // band framing the face + DP stripe
    const P = [[-w * .62 + sx * .3, h * .1], [-w * .6 + sx * .5, -h * .32], [sx * .6, -h * .56], [w * .6 + sx * .5, -h * .32], [w * .62 + sx * .3, h * .1], [w * .47 + sx * .4, h * .06], [w * .44 + sx * .5, -h * .2], [sx * .6, -h * .36], [-w * .44 + sx * .5, -h * .2], [-w * .47 + sx * .4, h * .06]];
    K.shape(g, P, { fill: fcol(ch.hatCol), lw, tension: .45 });
    if (!(ch.sil || o.sil)) K.line(g, [[-w * .53 + sx * .4, -h * .05], [-w * .5 + sx * .5, -h * .28], [sx * .6, -h * .47], [w * .5 + sx * .5, -h * .28], [w * .53 + sx * .4, -h * .05]], lw * 1.2, ch.hatCol2, .9);
  }
  if (hat === 'hood' && front) {
    K.shape(g, [[-w * .6 + sx * .3, h * .2], [-w * .62, -h * .3], [sx * .5, -h * .62], [w * .62, -h * .3], [w * .6 + sx * .3, h * .2], [w * .45, h * .05], [w * .42, -h * .25], [sx * .5, -h * .4], [-w * .42, -h * .25], [-w * .45, h * .05]], { fill: fcol(ch.hatCol), lw, tension: .45 });
  }
  if (hat === 'tophat' && front) {
    K.shape(g, [[-w * .7, -h * .32], [w * .7, -h * .32], [w * .72, -h * .26], [-w * .72, -h * .26]], { fill: fcol('#1e1b22'), lw, tension: .2 });
    K.shape(g, [[-w * .4, -h * .3], [w * .4, -h * .3], [w * .44, -h * 1.05], [-w * .44, -h * 1.05]], { fill: fcol('#1e1b22'), lw, smooth: false });
    if (!(ch.sil || o.sil)) K.shape(g, [[-w * .41, -h * .36], [w * .41, -h * .36], [w * .415, -h * .45], [-w * .415, -h * .45]], { fill: ch.hatCol2, lw: lw * .7, smooth: false });
  }
  if (hat === 'beret' && front) {
    K.shape(g, [[-w * .62, -h * .24], [-w * .5, -h * .55], [w * .1, -h * .68], [w * .62, -h * .5], [w * .64, -h * .26], [0, -h * .32]], { fill: fcol(ch.hatCol), lw, tension: .5 });
    K.shape(g, [[w * .3, -h * .55], [w * .55 - lagRoll * 100, -h * 1.05], [w * .62 - lagRoll * 120, -h * 1.15], [w * .42, -h * .58]], { fill: fcol('#f2ead8'), lw: lw * .8, tension: .5 });
  }
  if (hat === 'toque' && front) {
    K.shape(g, [[-w * .5, -h * .26], [-w * .62, -h * .6], [-w * .2, -h * .9], [w * .25, -h * .88], [w * .62, -h * .6], [w * .5, -h * .26]], { fill: fcol('#f3eee3'), lw, tension: .55 });
    K.shape(g, [[-w * .52, -h * .22], [w * .52, -h * .22], [w * .52, -h * .34], [-w * .52, -h * .34]], { fill: fcol('#e6dcc8'), lw, smooth: false });
  }
  if (hat === 'helmet' && front) {
    K.shape(g, [[-w * .8, -h * .18], [w * .8, -h * .18], [w * .55, -h * .32], [w * .4, -h * .62], [0, -h * .72], [-w * .4, -h * .62], [-w * .55, -h * .32]], { fill: fcol('#8e8f93'), lw, tension: .35 });
    if (!(ch.sil || o.sil)) K.line(g, [[-w * .3, -h * .55], [0, -h * .64], [w * .3, -h * .55]], lw * .6, '#dfe1e6', .7);
  }
  if (hat === 'straw' && front) {
    K.shape(g, [[-w * .95, -h * .2], [w * .95, -h * .2], [w * .5, -h * .32], [w * .35, -h * .6], [-w * .35, -h * .6], [-w * .5, -h * .32]], { fill: fcol('#cfae63'), lw, tension: .4 });
    if (!(ch.sil || o.sil)) K.line(g, [[-w * .48, -h * .34], [w * .48, -h * .34]], lw * 1.4, '#8a5a2b', 1, false);
  }
  if (hat === 'piper') {
    const tilt = -.18 + lagRoll * .5;
    if (front) {
      g.save(); g.rotate(tilt);
      // feather (long, sweeping back, sways with lag)
      const sw = lagRoll * 260 + (o.wind || 0) * 18;
      const fx = -sn * w * .2;
      const FP = [[w * .25 + fx, -h * .55], [w * .85 + fx + sw * .3, -h * .95], [w * 1.45 + fx + sw, -h * 1.12], [w * 1.62 + fx + sw * 1.2, -h * 1.05], [w * 1.1 + fx + sw * .7, -h * .86], [w * .45 + fx, -h * .46]];
      K.shape(g, FP, { fill: fcol('#efe3c6'), lw: lw * .8, tension: .6 });
      if (!(ch.sil || o.sil)) K.line(g, [[w * .35 + fx, -h * .52], [w * 1.0 + fx + sw * .5, -h * .95], [w * 1.5 + fx + sw, -h * 1.08]], lw * .45, '#9b3a2c', .8);
      // crown
      K.shape(g, [[-w * .45, -h * .38], [-w * .4, -h * .72], [-w * .05, -h * .88], [w * .38, -h * .78], [w * .5, -h * .38]], { fill: fcol(PAL.burg), lw, tension: .45 });
      if (!(ch.sil || o.sil)) K.shape(g, [[-w * .46, -h * .4], [w * .5, -h * .4], [w * .48, -h * .5], [-w * .44, -h * .5]], { fill: PAL.pgreen, lw: lw * .7, smooth: false });
      // brim
      K.shape(g, [[-w * .98, -h * .3], [-w * .5, -h * .46], [w * .6, -h * .46], [w * 1.05, -h * .34], [w * .9, -h * .26], [-w * .9, -h * .22]], { fill: fcol(PAL.burgD), lw, tension: .5 });
      g.restore();
    }
  }
}

// ---------------------------------------------------------------- cloak (Piper)
function drawCloak(g, ch, J, JA, JB, o, lw, pr, F) {
  const B = ch.B; const cy = Math.cos(J.yaw), sy = Math.sin(J.yaw);
  const shL = pr(J.shl), shR = pr(J.shr);
  const nk = pr(J.neck);
  const vel = [J.pel[0] - JB.pel[0], J.pel[2] - JB.pel[2]];     // body velocity (local) over the lag window
  const velS = R.proj(J, v(vel[0], 0, vel[1]));
  const wind = o.wind || 0, t = o.t || 0;
  const flow = -velS[0] * 2.2 - wind * 60;       // hem streams opposite to motion
  const hemY = -(B.hip * .22) - Math.abs(velS[0]) * .4;
  const back = cy < 0;
  const wv = i => Math.sin(t * 3.1 + i * 1.7) * (8 + Math.abs(flow) * .15) + Math.sin(t * 5.3 + i * 2.9) * 4;
  const width = B.shW * 1.5 + 30 * Math.abs(cy);
  const N = 6, hem = [];
  for (let i = 0; i <= N; i++) {
    const u = i / N; const x = lerp(-width, width, u) + flow * (0.6 + .4 * Math.sin(u * Math.PI)) + wv(i);
    hem.push([x + (shL[0] + shR[0]) / 2, hemY + Math.sin(u * Math.PI) * 10 + wv(i + 3) * .5 + (flow ? Math.abs(flow) * .1 * Math.sin(u * 3 + t * 4) : 0)]);
  }
  const top = [[Math.min(shL[0], shR[0]) - 12, Math.min(shL[1], shR[1]) - 4], [nk[0], nk[1] + 4], [Math.max(shL[0], shR[0]) + 12, Math.min(shL[1], shR[1]) - 4]];
  const P = [top[2], ...hem.slice().reverse(), top[0], top[1]];
  K.shape(g, P, { fill: F(PAL.purple), lw, tension: .45, inner: o.sil ? null : (g2) => {
    // lining visible on the trailing side
    g2.fillStyle = PAL.pgreen; g2.beginPath();
    const side = flow >= 0 ? 1 : -1;
    g2.moveTo(hem[side > 0 ? N : 0][0], hem[side > 0 ? N : 0][1]);
    g2.quadraticCurveTo((top[side > 0 ? 2 : 0][0] + hem[side > 0 ? N : 0][0]) / 2 + side * 20, (top[0][1] + hemY) / 2, top[side > 0 ? 2 : 0][0], top[0][1] + 30);
    g2.lineTo(top[side > 0 ? 2 : 0][0] + side * 200, top[0][1]); g2.lineTo(hem[side > 0 ? N : 0][0] + side * 200, hem[side > 0 ? N : 0][1] + 50); g2.closePath();
    g2.globalAlpha = .9; g2.fill();
    // folds
    g2.globalAlpha = 1; g2.strokeStyle = K.rgba(INK, .4); g2.lineWidth = lw * .6;
    for (let i = 1; i < N; i++) { g2.beginPath(); g2.moveTo(lerp(top[0][0], top[2][0], i / N), top[0][1] + 20); g2.quadraticCurveTo(lerp(top[0][0], top[2][0], i / N) + flow * .3, (top[0][1] + hemY) / 2, hem[i][0], hem[i][1] - 8); g2.stroke(); }
  } });
}

module.exports = { makeChar, drawPerson, drawHand, wrap };
