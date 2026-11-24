// ===================================================================== rig.js
// Articulated, auto-grounded 2D character rig with expressive face + secondary motion.
'use strict';
// Pose fields (all optional):
//  x,y ground point; f facing (+1 right / -1 left); s scale; turn 0(front)..1(profile)
//  lean (rad, + = forward), air (lift off ground, px), sq (squash 1 = none)
//  hipL,kneeL,hipR,kneeR  (rad; hip + = leg forward, knee + = shin back)
//  shL,elL,shR,elR       (rad; shoulder 0 = arm down, + = forward/up; elbow + = forearm bends forward)
//  head (tilt rad), nod, expr {eye,lookX,lookY,brow,browAng,mouth,open,blush}
//  handL/handR: 'open'|'fist'|'point'|'hold'|'wave'
//  swing (coat swing rad), hold: {L:fn, R:fn}
const DEF_POSE = { x: 0, y: 0, f: 1, s: 1, turn: .35, lean: 0, air: 0, sq: 1, hipL: 0, kneeL: 0, hipR: 0, kneeR: 0,
  shL: -.14, elL: .3, shR: .12, elR: .25, head: 0, nod: 0, swing: 0, handL: 'open', handR: 'open', expr: {} };
const DEF_EXPR = { eye: 1, lookX: .2, lookY: 0, brow: 0, browAng: 0, mouth: 'smile', open: 0, blush: 0, lids: 0 };

function P(o) { const p = Object.assign({}, DEF_POSE, o); p.expr = Object.assign({}, DEF_EXPR, o && o.expr); return p; }

// ----------------------------------------------------------------- body geometry
function legPts(hip, a, k, L1, L2) {
  const kn = [hip[0] + Math.sin(a) * L1, hip[1] + Math.cos(a) * L1];
  const an = [kn[0] + Math.sin(a - k) * L2, kn[1] + Math.cos(a - k) * L2];
  return [hip, kn, an];
}
function armPts(sh, a, e, L1, L2) {
  const el = [sh[0] + Math.sin(a) * L1, sh[1] + Math.cos(a) * L1];
  const wr = [el[0] + Math.sin(a + e) * L2, el[1] + Math.cos(a + e) * L2];
  return [sh, el, wr];
}
// tapered organic limb through 3 joints with widths
function limbPath(c, p, w) {
  const side = (a, b, s) => { const dx = b[0] - a[0], dy = b[1] - a[1], l = Math.hypot(dx, dy) || 1; return [-dy / l * s, dx / l * s]; };
  const n0 = side(p[0], p[1], 1), n2 = side(p[1], p[2], 1);
  const n1 = [(n0[0] + n2[0]) / 2, (n0[1] + n2[1]) / 2];
  const L = [[p[0][0] + n0[0] * w[0], p[0][1] + n0[1] * w[0]], [p[1][0] + n1[0] * w[1], p[1][1] + n1[1] * w[1]], [p[2][0] + n2[0] * w[2], p[2][1] + n2[1] * w[2]]];
  const R = [[p[2][0] - n2[0] * w[2], p[2][1] - n2[1] * w[2]], [p[1][0] - n1[0] * w[1], p[1][1] - n1[1] * w[1]], [p[0][0] - n0[0] * w[0], p[0][1] - n0[1] * w[0]]];
  c.beginPath(); spline(c, [...L, ...R], true, .45);
}
function drawLimb(c, p, w, col, lw, shadeCol) {
  limbPath(c, p, w); c.fillStyle = col; c.fill();
  if (shadeCol) { c.save(); limbPath(c, p, w); c.clip(); c.globalAlpha = .5; limbPath(c, p.map(q => [q[0] - w[1] * .55, q[1]]), w); c.fillStyle = shadeCol; c.fill(); c.restore(); }
  limbPath(c, p, w); c.lineWidth = lw; c.strokeStyle = INK; c.lineJoin = 'round'; c.stroke();
}
function drawHand(c, wr, ang, kind, col, sc, lw) {
  c.save(); c.translate(wr[0], wr[1]); c.rotate(-ang);
  const r = 17 * sc;
  if (kind === 'fist' || kind === 'hold') {
    blob(c, [[-r, -r * .2], [-r * .9, r * .9], [0, r * 1.25], [r * .95, r * .8], [r, -r * .3], [0, -r * .6]], col, lw);
    line(c, [[-r * .5, r * .55], [r * .5, r * .55]], lw * .5, rgba(INK, .5));
  } else if (kind === 'point') {
    blob(c, [[-r, -r * .2], [-r * .9, r * .8], [0, r * 1.1], [r * .8, r * .7], [r, -r * .3], [0, -r * .6]], col, lw);
    blob(c, [[-r * .25, r * .8], [-r * .25, r * 2.6], [r * .25, r * 2.6], [r * .25, r * .8]], col, lw);
  } else {
    // open hand with spread fingers + thumb
    blob(c, [[-r, -r * .3], [-r * 1.15, r * .9], [-r * .5, r * 1.9], [0, r * 2.05], [r * .5, r * 1.9], [r * 1.0, r * 1.2], [r * 1.5, r * .6], [r * 1.1, r * .2], [r * .9, -r * .4], [0, -r * .7]], col, lw);
    line(c, [[-r * .25, r * 1.3], [-r * .3, r * 1.85]], lw * .5); line(c, [[r * .25, r * 1.3], [r * .25, r * 1.85]], lw * .5);
  }
  c.restore();
}
function drawBoot(c, an, f, col, sc, lw, k = 0) {
  const r = sc;
  c.save(); c.translate(an[0], an[1]); c.rotate(clamp(k * .3, -.5, .5));
  blob(c, [[-14 * r, -10 * r], [-16 * r, 12 * r], [-8 * r, 20 * r], [26 * r, 20 * r], [34 * r, 12 * r], [24 * r, 0], [10 * r, -12 * r]], col, lw);
  line(c, [[-15 * r, 17 * r], [33 * r, 17 * r]], lw * .7, shade(col, .4));
  c.restore();
}

// ----------------------------------------------------------------- face
function drawEye(c, x, y, rx, ry, e, side, sc, lw, iris) {
  const open = clamp(e.eye, 0, 1.25);
  if (open < .08) { curve(c, [[x - rx, y], [x, y + ry * .35], [x + rx, y]], lw * 1.1); return; }
  const oy = ry * open;
  c.save();
  c.beginPath(); c.ellipse(x, y, rx, oy, 0, 0, TAU); c.fillStyle = '#fbf6ec'; c.fill();
  c.clip();
  const px = x + e.lookX * rx * .45, py = y + e.lookY * oy * .45;
  ell(c, px, py, rx * .58, rx * .62, iris);
  ell(c, px, py, rx * .3, rx * .33, '#120a08');
  ell(c, px - rx * .17, py - rx * .2, rx * .13, rx * .13, '#fff');
  // upper lid (sleepy / smug)
  const lid = clamp(e.lids, 0, 1);
  if (lid > 0) { c.fillStyle = e.lidCol || '#d9a07c'; c.fillRect(x - rx * 1.2, y - oy * 1.2, rx * 2.4, oy * 2.2 * lid * .62 + .1); }
  c.restore();
  c.beginPath(); c.ellipse(x, y, rx, oy, 0, PI * 1.05, PI * 1.95); c.lineWidth = lw * 1.25; c.strokeStyle = INK; c.stroke();
  c.beginPath(); c.ellipse(x, y, rx, oy, 0, .25, PI - .25); c.lineWidth = lw * .55; c.stroke();
  if (lid > 0) line(c, [[x - rx, y - oy + oy * 2 * lid * .62], [x + rx, y - oy + oy * 2 * lid * .62]], lw * 1.1);
}
function drawMouth(c, x, y, w, e, sc, lw, skin) {
  const m = e.mouth, o = clamp(e.open, 0, 1.4);
  const dark = '#4a1414', tongue = '#d4626a', teeth = '#fbf6ec';
  if (m === 'flat') { curve(c, [[x - w * .45, y], [x, y + 1], [x + w * .45, y - 1]], lw); return; }
  if (m === 'smile') { curve(c, [[x - w * .55, y - w * .1], [x, y + w * .22], [x + w * .55, y - w * .12]], lw); return; }
  if (m === 'smirk') { curve(c, [[x - w * .45, y + w * .05], [x + w * .1, y + w * .08], [x + w * .6, y - w * .22]], lw); line(c, [[x + w * .6, y - w * .22], [x + w * .68, y - w * .14]], lw * .8); return; }
  if (m === 'frown') { curve(c, [[x - w * .5, y + w * .15], [x, y - w * .08], [x + w * .5, y + w * .15]], lw); return; }
  if (m === 'chew') { const k = .5 + .5 * Math.sin(e.chewT * 22); ell(c, x, y, w * .3, w * (.06 + .14 * k), dark, lw); return; }
  // open shapes
  let pts;
  if (m === 'grin') pts = [[x - w * .62, y - w * .12], [x, y - w * .02], [x + w * .62, y - w * .14], [x + w * .35, y + w * (.25 + .3 * o)], [x, y + w * (.35 + .35 * o)], [x - w * .35, y + w * (.25 + .3 * o)]];
  else if (m === 'o') pts = [[x - w * .25, y], [x, y - w * .18 * (.6 + o)], [x + w * .25, y], [x, y + w * .28 * (.6 + o)]];
  else if (m === 'shout') pts = [[x - w * .5, y - w * .15], [x, y - w * .22], [x + w * .5, y - w * .15], [x + w * .38, y + w * (.35 + .45 * o)], [x, y + w * (.5 + .5 * o)], [x - w * .38, y + w * (.35 + .45 * o)]];
  else if (m === 'teeth') pts = [[x - w * .55, y - w * .1], [x + w * .55, y - w * .1], [x + w * .5, y + w * .14], [x - w * .5, y + w * .14]];
  else pts = [[x - w * .3, y], [x, y - w * .1], [x + w * .3, y], [x, y + w * .3 * (.5 + o)]];   // 'snore' etc
  c.save(); c.beginPath(); spline(c, pts, true, .55); c.fillStyle = dark; c.fill(); c.clip();
  if (m === 'grin' || m === 'teeth') { c.fillStyle = teeth; c.fillRect(x - w, y - w * .4, w * 2, m === 'teeth' ? w * .7 : w * .28); if (m === 'teeth') line(c, [[x - w, y + w * .02], [x + w, y + w * .02]], lw * .5); }
  if (m !== 'teeth') ell(c, x, y + w * (.45 + .4 * o), w * .35, w * .22, tongue);
  c.restore();
  c.beginPath(); spline(c, pts, true, .55); c.lineWidth = lw; c.strokeStyle = INK; c.lineJoin = 'round'; c.stroke();
}

// ----------------------------------------------------------------- full head
// head local: origin at neck top; head drawn upward. spec.face describes the character.
function drawHead(c, ch, p, sc, lw) {
  const hw = ch.headW * (ch.hs || 1.13), hh = ch.headH * (ch.hs || 1.13), e = p.expr, f = ch.face;
  const tx = p.turn * hw * .22;                     // feature shift for 3/4 view
  c.save();
  if (ch.backHair) ch.backHair(c, hw, hh, p, lw);
  // ears
  const earX = -hw * .44 + tx * .3;
  if (!ch.noEars) { ell(c, earX - 4, -hh * .44, hw * .1, hh * .13, ch.skin, lw); ell(c, earX - 2, -hh * .44, hw * .05, hh * .07, shade(ch.skin, .25)); }
  if (p.turn < .55 && !ch.noEars) { ell(c, hw * .47 + tx * .2, -hh * .44, hw * .08, hh * .12, ch.skin, lw); }
  // skull / jaw shape
  const jaw = f.jaw || 1, chin = f.chin || 0;
  const head = [[-hw * .5, -hh * .55], [-hw * .44, -hh * .9], [-hw * .1, -hh * 1.02], [hw * .32, -hh * .95], [hw * .52 + tx * .2, -hh * .62],
    [hw * .5 * jaw + tx * .25, -hh * .28], [hw * .28 + tx * .4 + chin, -hh * .03], [tx * .4 + chin * .5, hh * .03], [-hw * .3 * jaw + tx * .2, -hh * .06], [-hw * .5 * jaw, -hh * .3]];
  blob(c, head, ch.skin);
  // skin shading + blush + stubble
  c.save(); c.beginPath(); spline(c, head, true); c.clip();
  c.fillStyle = lg(c, -hw * .5, 0, hw * .5, 0, [[0, rgba(shade(ch.skin, .35), .65)], [.45, rgba(ch.skin, 0)], [1, rgba(tint(ch.skin, .3), .35)]]);
  c.fillRect(-hw, -hh * 1.2, hw * 2, hh * 1.4);
  if (f.stubble) { c.fillStyle = rgba(f.stubble, .35); c.beginPath(); c.ellipse(tx * .4, -hh * .1, hw * .48, hh * .26, 0, 0, TAU); c.fill(); }
  if (e.blush || f.cheeks) { const b = Math.max(e.blush || 0, f.cheeks || 0); ell(c, tx + hw * .25, -hh * .33, hw * .13, hh * .06, rgba('#e8636a', .45 * b)); ell(c, tx - hw * .22, -hh * .33, hw * .12, hh * .06, rgba('#e8636a', .4 * b)); }
  if (ch.faceShadow) { c.fillStyle = lg(c, 0, -hh * 1.05, 0, -hh * .1, [[0, `rgba(8,4,12,${ch.faceShadow})`], [.75, `rgba(8,4,12,${ch.faceShadow * .7})`], [1, 'rgba(8,4,12,0)']]); c.fillRect(-hw, -hh * 1.2, hw * 2, hh * 1.3); }
  c.restore();
  c.beginPath(); spline(c, head, true); c.lineWidth = lw; c.strokeStyle = INK; c.stroke();
  // eyes
  const ey = -hh * (f.eyeY || .5), er = hw * (f.eyeR || .13), sp = hw * (f.eyeSp || .2);
  const lidCol = shade(ch.skin, .12);
  const ee = Object.assign({ lidCol }, e);
  drawEye(c, tx + sp * (1 - p.turn * .25), ey, er * (1 - p.turn * .15), er * 1.12, ee, 1, sc, lw * .8, f.iris || '#4a6b8a');
  drawEye(c, tx - sp * (1 - p.turn * .4), ey, er * (1 - p.turn * .35), er * 1.12, ee, -1, sc, lw * .8, f.iris || '#4a6b8a');
  // brows
  const bw = er * 1.25, by = ey - er * 1.35 - e.brow * hh * .06, ba = e.browAng;
  const bt = f.browT || 1;
  for (const sgn of [1, -1]) {
    const bx = tx + sgn * sp * (1 - p.turn * (sgn > 0 ? .25 : .4));
    const inner = by + sgn * 0 + ba * 10 * sc, outer = by - ba * 4 * sc;
    const pts = sgn > 0 ? [[bx - bw * .7, inner], [bx, by - 5 * sc], [bx + bw * .8, outer]] : [[bx + bw * .7, inner], [bx, by - 5 * sc], [bx - bw * .8, outer]];
    curve(c, pts, lw * 1.6 * bt, f.browCol || INK);
  }
  // nose
  const nx = tx + hw * .06 + p.turn * hw * .14, ny = -hh * (f.noseY || .36);
  const nose = f.nose || 'round';
  if (nose === 'long') blob(c, [[nx - 6 * sc, ny - 36 * sc], [nx + 26 * sc + p.turn * 18 * sc, ny + 2 * sc], [nx + 16 * sc + p.turn * 10 * sc, ny + 12 * sc], [nx - 10 * sc, ny + 9 * sc]], tint(ch.skin, .05), lw);
  else if (nose === 'hook') blob(c, [[nx - 4 * sc, ny - 30 * sc], [nx + 14 * sc + p.turn * 10 * sc, ny - 6 * sc], [nx + 10 * sc + p.turn * 8 * sc, ny + 12 * sc], [nx - 9 * sc, ny + 10 * sc]], shade(ch.skin, .05), lw);
  else if (nose === 'button') ell(c, nx, ny, hw * .07, hw * .06, tint(ch.skin, .12), lw);
  else blob(c, [[nx - 12 * sc, ny - 8 * sc], [nx - 2 * sc, ny - 22 * sc], [nx + 14 * sc + p.turn * 6 * sc, ny], [nx + 4 * sc, ny + 12 * sc], [nx - 12 * sc, ny + 8 * sc]], tint(ch.skin, .08), lw);
  // moustache / beard (under mouth for beard)
  const my = -hh * (f.mouthY || .17), mw = hw * (f.mouthW || .3);
  if (f.beard) f.beard(c, hw, hh, tx, p, lw);
  drawMouth(c, tx + hw * .04, my, mw, e, sc, lw * .9, ch.skin);
  if (f.tache) f.tache(c, hw, hh, tx, p, lw);
  if (ch.frontHair) ch.frontHair(c, hw, hh, p, lw, tx);
  if (ch.hat) ch.hat(c, hw, hh, p, lw, tx);
  c.restore();
}

// ----------------------------------------------------------------- full character
function drawChar(c, ch, pose, t) {
  const p = P(pose);
  const sc = p.s * (ch.scale || 1);
  const lw = (ch.lw || 5) * Math.max(sc, .35);
  const B = ch.body;
  c.save();
  c.translate(p.x, p.y);
  c.scale(p.f * sc, sc);
  // auto-ground: compute feet with hip at origin, place the lowest foot on y=0
  const L1 = B.thigh, L2 = B.shin;
  const hipW = B.hipW;
  const hipNear = [hipW * .25, 0], hipFar = [-hipW * .2, 0];
  const lf = legPts(hipFar, p.hipL, p.kneeL, L1, L2), lr = legPts(hipNear, p.hipR, p.kneeR, L1, L2);
  const low = Math.max(lf[2][1], lr[2][1]) + 18;
  c.translate(0, -low - p.air);
  if (p.sq !== 1) { c.translate(0, low); c.scale(1 / Math.sqrt(p.sq), p.sq); c.translate(0, -low); }
  if (ch.shadowOnGround !== false && p.air < 400) {
    c.save(); c.translate(0, low + p.air); c.scale(1, .22);
    ell(c, 10, 0, (B.hipW * .9 + 40) * (1 - clamp(p.air / 400, 0, .6)), 60, 'rgba(10,5,15,0.28)'); c.restore();
  }
  // torso frame
  const T = B.torso, lean = p.lean;
  const up = [Math.sin(lean), -Math.cos(lean)], rt = [Math.cos(lean), Math.sin(lean)];
  const shC = [up[0] * T, up[1] * T];
  const sw = B.shW;
  const shNear = [shC[0] + rt[0] * sw * (.5 - p.turn * .12), shC[1] + rt[1] * sw * (.5 - p.turn * .12) + 6];
  const shFar = [shC[0] - rt[0] * sw * (.5 - p.turn * .22), shC[1] - rt[1] * sw * (.5 - p.turn * .22) + 6];
  const A1 = B.upperArm, A2 = B.foreArm;
  const af = armPts(shFar, -p.shL * 1, -p.elL, A1, A2), an = armPts(shNear, p.shR, p.elR, A1, A2);
  // convention: + shoulder = arm swings forward (toward +x)
  af[1] = [shFar[0] + Math.sin(p.shL) * A1, shFar[1] + Math.cos(p.shL) * A1];
  af[2] = [af[1][0] + Math.sin(p.shL + p.elL) * A2, af[1][1] + Math.cos(p.shL + p.elL) * A2];
  an[1] = [shNear[0] + Math.sin(p.shR) * A1, shNear[1] + Math.cos(p.shR) * A1];
  an[2] = [an[1][0] + Math.sin(p.shR + p.elR) * A2, an[1][1] + Math.cos(p.shR + p.elR) * A2];
  const J = { hip: [0, 0], shNear, shFar, handFar: af[2], handNear: an[2], footFar: lf[2], footNear: lr[2], elFar: af[1], elNear: an[1],
    neck: [shC[0] + up[0] * 10, shC[1] + up[1] * 10], angFar: p.shL + p.elL, angNear: p.shR + p.elR };
  const col = ch.col;
  if (p.hold && p.hold.R && p.hold.R.back) p.hold.R(c, J, 'near', sc);
  if (p.hold && p.hold.L && p.hold.L.back) p.hold.L(c, J, 'far', sc);
  const sleeve = col.sleeve || col.coat, sleeveF = shade(sleeve, .18);
  // far limbs (darker, behind)
  if (ch.cape) ch.cape(c, J, p, lw, 'back');
  if (p.hold && p.hold.L && p.hold.L.behind && !p.hold.L.back) p.hold.L(c, J, 'far', sc);
  drawLimb(c, lf, [B.legW, B.legW * .85, B.legW * .62], shade(col.legs, .22), lw);
  drawBoot(c, lf[2], 1, shade(col.boots, .2), 1, lw, p.hipL - p.kneeL);
  drawLimb(c, af, [B.armW, B.armW * .82, B.armW * .62], sleeveF, lw);
  drawHand(c, af[2], p.shL + p.elL, p.handL, shade(ch.handCol || ch.skin, .15), 1, lw);
  if (p.hold && p.hold.L && !p.hold.L.behind && !p.hold.L.back) p.hold.L(c, J, 'far', sc);
  // near leg
  drawLimb(c, lr, [B.legW, B.legW * .85, B.legW * .62], col.legs, lw, shade(col.legs, .25));
  drawBoot(c, lr[2], 1, col.boots, 1, lw, p.hipR - p.kneeR);
  // torso / coat
  const hemY = B.coatLen || 40, flare = B.flare || 1;
  const sway = clamp(p.swing, -.6, .6);
  const hipN = [hipW * .55, -6], hipF = [-hipW * .5, -6];
  const wN = [shNear[0] * .4 + hipN[0] * .6 + (B.belly || 0), shNear[1] * .4 + hipN[1] * .6], wF = [shFar[0] * .45 + hipF[0] * .55, shFar[1] * .45 + hipF[1] * .55];
  const hemN = [hipW * .62 * flare + sway * hemY * 1.2, hemY], hemF = [-hipW * .58 * flare + sway * hemY * 1.2, hemY * .95];
  const torso = [[shFar[0] - 6, shFar[1] - 4], [shC[0] - 10 * up[0], shC[1] + up[1] * 4], [shNear[0] + 6, shNear[1] - 4],
    [shNear[0] + 14, shNear[1] + 30], wN, hipN, hemN, [sway * hemY + hipW * .1, hemY + 8], hemF, hipF, wF, [shFar[0] - 12, shFar[1] + 30]];
  if (ch.cape) ch.cape(c, J, p, lw, 'mid');
  blob(c, torso, col.coat);
  c.save(); c.beginPath(); spline(c, torso, true); c.clip();
  if (ch.coatDetail) ch.coatDetail(c, J, p, lw, { shC, hipN, hipF, hemN, hemF, up, rt, T, hemY });
  c.fillStyle = lg(c, hipF[0] - 20, 0, hipN[0] + 30, 0, [[0, rgba('#120818', .45)], [.5, rgba('#120818', 0)], [.88, rgba('#fff0d0', 0)], [1, rgba('#fff0d0', .22)]]);
  c.fillRect(-400, -T - 200, 800, T + 400);
  c.restore();
  c.beginPath(); spline(c, torso, true); c.lineWidth = lw; c.strokeStyle = INK; c.lineJoin = 'round'; c.stroke();
  if (ch.collar) ch.collar(c, J, p, lw, shC, up);
  // head
  c.save();
  c.translate(J.neck[0], J.neck[1] + 6);
  c.rotate(lean * .6 + p.head);
  if (ch.neck !== false) blob(c, [[-12, 10], [-12, -16], [14, -16], [14, 10]], shade(ch.skin, .25), lw * .8);
  c.translate(0, -8 + p.nod);
  drawHead(c, ch, p, sc, lw);
  c.restore();
  if (ch.cape) ch.cape(c, J, p, lw, 'front');
  // near arm
  if (p.hold && p.hold.R && p.hold.R.behind && !p.hold.R.back) p.hold.R(c, J, 'near', sc);
  drawLimb(c, an, [B.armW, B.armW * .82, B.armW * .62], sleeve, lw, shade(sleeve, .25));
  if (ch.cuff) ch.cuff(c, an, lw);
  drawHand(c, an[2], p.shR + p.elR, p.handR, ch.handCol || ch.skin, 1, lw);
  if (p.hold && p.hold.R && !p.hold.R.behind && !p.hold.R.back) p.hold.R(c, J, 'near', sc);
  c.restore();
  return J;
}

// ----------------------------------------------------------------- motion library
// Walk cycle synced to beats: one step per beat. ph in steps.
function walkPose(t, o = {}) {
  const spd = o.stepDur || SPB;                // a step every beat
  const ph = (t / spd) * PI + (o.ph || 0);    // half cycle per step
  const amp = o.amp ?? 1, strut = o.strut ?? 0;
  const s = Math.sin(ph), c2 = Math.cos(ph);
  const lift = Math.max(0, Math.sin(ph)), lift2 = Math.max(0, -Math.sin(ph));
  return {
    hipR: .42 * s * amp, kneeR: (.15 + .75 * lift2 * amp), hipL: -.42 * s * amp, kneeL: (.15 + .75 * lift * amp),
    shR: -.38 * s * amp + (o.armR ?? 0), elR: .25 + .2 * lift, shL: .38 * s * amp + (o.armL ?? 0), elL: .25 + .2 * lift2,
    air: Math.abs(Math.sin(ph)) * 10 * amp * (1 + strut), lean: .06 + strut * .08, head: Math.sin(ph * 2) * .03,
    swing: -Math.cos(ph) * .12 * amp, nod: Math.abs(Math.cos(ph)) * 4,
  };
}
function merge(...os) { const r = {}; for (const o of os) if (o) for (const k in o) { if (k === 'expr') r.expr = Object.assign({}, r.expr, o.expr); else r[k] = o[k]; } return r; }
// interpolate between pose objects (numeric fields only)
function poseLerp(a, b, k) { const r = Object.assign({}, a); for (const kk in b) { if (typeof b[kk] === 'number' && typeof a[kk] === 'number') r[kk] = lerp(a[kk], b[kk], k); else if (kk === 'expr') r.expr = Object.assign({}, a.expr || {}, k > .5 ? b.expr : {}); else if (k > .5 || a[kk] === undefined) r[kk] = b[kk]; } return r; }
// pose keyframes: [[t, poseObj, ease], ...]
function poseKeys(t, ks) {
  if (t <= ks[0][0]) return ks[0][1];
  for (let i = 1; i < ks.length; i++) if (t <= ks[i][0]) { const k = E[ks[i][2] || 'io']((t - ks[i - 1][0]) / (ks[i][0] - ks[i - 1][0])); return poseLerp(ks[i - 1][1], ks[i][1], k); }
  return ks[ks.length - 1][1];
}
