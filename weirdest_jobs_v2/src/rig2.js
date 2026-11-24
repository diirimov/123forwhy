// ===================================================================== rig2.js
// V2 character system: ~7-heads-tall stylised humans, parametric profile / 3-4 / front / back heads,
// anatomical limb segments with cuffs, 5-finger hands, costume silhouettes that adapt to the view.
'use strict';
const OL = '#2a150c';

// ---------------------------------------------------------------- expressions
const EXPR = {
  neutral: { eye: 1, brow: 0, tilt: 0, mouth: 'closed', smile: 0, open: 0 },
  happy: { eye: .82, brow: .3, tilt: -.1, mouth: 'closed', smile: 1, open: 0, cheek: 1 },
  grin: { eye: .85, brow: .35, tilt: -.1, mouth: 'open', smile: 1, open: .35, cheek: 1 },
  laugh: { eye: .2, brow: .45, tilt: -.2, mouth: 'open', smile: 1, open: .85, cheek: 1 },
  surprise: { eye: 1.3, brow: 1.2, tilt: -.2, mouth: 'open', smile: 0, open: .8, pupil: .7 },
  shout: { eye: 1.05, brow: .7, tilt: .25, mouth: 'open', smile: .4, open: 1 },
  anger: { eye: .75, brow: -.45, tilt: 1, mouth: 'teeth', smile: -.7, open: .2 },
  fear: { eye: 1.3, brow: 1, tilt: -.8, mouth: 'open', smile: -.6, open: .45, pupil: .55 },
  confused: { eye: 1, brow: .6, tilt: -.3, asym: 1, mouth: 'closed', smile: -.35 },
  smug: { eye: .5, brow: .3, tilt: .3, mouth: 'closed', smile: .75, smirk: 1 },
  sleep: { eye: 0, brow: -.15, tilt: 0, mouth: 'open', smile: 0, open: .3 },
  sad: { eye: .7, brow: .25, tilt: -.85, mouth: 'closed', smile: -.8 },
  chew: { eye: .55, brow: -.25, tilt: .2, mouth: 'chew' },
  stern: { eye: .72, brow: -.2, tilt: .55, mouth: 'closed', smile: -.25 },
  mystic: { eye: .62, brow: -.25, tilt: .45, mouth: 'closed', smile: .05 },
  relief: { eye: .55, brow: .5, tilt: -.5, mouth: 'closed', smile: .55 },
  ooh: { eye: 1.15, brow: 1.0, tilt: -.3, mouth: 'o', open: .6 },
};
const X = (name, o) => Object.assign({}, EXPR[name] || EXPR.neutral, o || {});

// ---------------------------------------------------------------- helpers
function sk(c) { c.lineJoin = 'round'; c.lineCap = 'round'; }
function rot(p, piv, a) { const s = Math.sin(a), co = Math.cos(a), x = p[0] - piv[0], y = p[1] - piv[1]; return [piv[0] + x * co - y * s, piv[1] + x * s + y * co]; }
function shapePath(c, pts, closed = true, ten = .45) { c.beginPath(); spline(c, pts, closed, ten); }
function fillOL(c, pts, fill, lw, ten = .45, closed = true) { shapePath(c, pts, closed, ten); if (fill) { c.fillStyle = fill; c.fill(); } if (lw) { c.lineWidth = lw; c.strokeStyle = OL; sk(c); c.stroke(); } }
function shadeIn(c, pts, fn, ten = .45) { c.save(); shapePath(c, pts, true, ten); c.clip(); fn(c); c.restore(); }

// ---------------------------------------------------------------- HEADS  (u = head height; origin = neck top; facing +x)
function headProfile(ch, e) {
  const F = ch.face, nl = F.noseLen ?? .1, nd = F.noseDrop ?? .02, lip = F.lip ?? .015, chin = F.chin ?? 0, jaw = F.jaw ?? 1, fs = F.forehead ?? 0, br = F.browRidge ?? 0;
  const ja = (e.open || 0) * .62 + (e.mouth === 'chew' ? .12 * (.5 + .5 * Math.sin((e.chewT || 0) * 22)) : 0);
  const piv = [-.02, -.40];
  const J = p => rot(p, piv, ja);
  let nose;
  if (F.nose === 'hook') nose = [[.39 + br, -.57], [.43 + nl * .6, -.52], [.40 + nl, -.42 + nd], [.37 + nl * .4, -.38 + nd * .5]];
  else if (F.nose === 'button') nose = [[.38, -.56], [.40, -.48], [.43 + nl * .5, -.43], [.40, -.385]];
  else if (F.nose === 'long') nose = [[.385 + br, -.57], [.43 + nl * .5, -.5], [.44 + nl, -.43 + nd], [.40 + nl * .3, -.38]];
  else if (F.nose === 'bulb') nose = [[.385, -.57], [.41 + nl * .4, -.5], [.46 + nl * .7, -.43 + nd], [.42 + nl * .5, -.385], [.39, -.375]];
  else nose = [[.385 + br, -.57], [.42 + nl * .5, -.5], [.43 + nl * .8, -.43 + nd], [.395 + nl * .2, -.385]];   // roman/straight
  const pts = [[-.27, -.10], [-.43, -.34], [-.47, -.62], [-.33, -.90], [-.06, -1.0], [.22, -.95], [.34 + fs * .5, -.82], [.39 + fs + br, -.66],
    ...nose, [.405, -.355], [.415 + lip, -.325], [.40 - Math.min(.12, (e.open || 0) * .14), -.297],
    J([.405 + lip * .8, -.272]), J([.385, -.235]), J([.405 + chin, -.185]), J([.37 + chin * .8, -.105]), J([.25 + chin * .3, -.055]), J([.06, -.06]), [-.14, -.13]];
  return { pts, eye: [.255, -.545], ear: [-.12, -.47], mouthTop: [.415 + lip, -.325], mouthCorner: [.27, -.30], mouthLow: J([.405 + lip * .8, -.272]), J, ja };
}
function head34(ch, e) {
  const F = ch.face, nl = F.noseLen ?? .1, chin = F.chin ?? 0, jaw = F.jaw ?? 1;
  const drop = (e.open || 0) * .11 + (e.mouth === 'chew' ? .03 * (.5 + .5 * Math.sin((e.chewT || 0) * 22)) : 0);
  const D = p => [p[0], p[1] + drop * clamp((p[1] + .35) / .3, 0, 1)];
  const pts = [[-.36, -.14], [-.48, -.5], [-.40, -.85], [-.12, -1.0], [.2, -.96], [.39, -.8], [.44, -.63], [.43 * jaw + .02, -.46], [.41 * jaw, -.34],
    D([.34 * jaw, -.19]), D([.2 + chin, -.07]), D([.07 + chin * .5, -.04]), D([-.12, -.09]), [-.3, -.2]];
  return { pts, eyeN: [.25, -.545], eyeF: [-.01, -.545], ear: [-.37, -.48], nose: [.15, -.58], noseTip: [.22 + nl * .6, -.42 + (F.noseDrop || 0)], mouth: D([.15, -.255]), drop, D };
}
function headFront(ch, e) {
  const F = ch.face, jaw = F.jaw ?? 1, drop = (e.open || 0) * .11;
  const D = p => [p[0], p[1] + drop * clamp((p[1] + .35) / .3, 0, 1)];
  const pts = [[0, -1.0], [.3, -.95], [.44, -.75], [.45, -.55], [.43 * jaw, -.38], D([.33 * jaw, -.18]), D([.12, -.05]), D([0, -.03]), D([-.12, -.05]), D([-.33 * jaw, -.18]), [-.43 * jaw, -.38], [-.45, -.55], [-.44, -.75], [-.3, -.95]];
  return { pts, eyeR: [.17, -.545], eyeL: [-.17, -.545], mouth: D([0, -.255]), drop, D };
}
function almondEye(c, x, y, w, h, e, look, iris, lw, side = 1, lash = false) {
  // w,h in px; side=1 front corner towards +x
  const open = clamp(e.eye ?? 1, 0, 1.4);
  if (open < .08) { c.beginPath(); c.moveTo(x - w * .5, y); c.quadraticCurveTo(x, y + h * .45, x + w * .5, y); c.lineWidth = lw * 1.1; c.strokeStyle = OL; c.stroke(); return; }
  const top = y - h * .5 * open, bot = y + h * .42 * Math.min(open, 1.1);
  const fx = x + w * .5 * side, bx = x - w * .5 * side;
  const path = () => { c.beginPath(); c.moveTo(bx, y); c.quadraticCurveTo(x, top - h * .15, fx, y - h * .05); c.quadraticCurveTo(x, bot + h * .1, bx, y); c.closePath(); };
  path(); c.fillStyle = '#fbf5ea'; c.fill();
  c.save(); path(); c.clip();
  const ir = h * .46 * (e.pupil ? 1 : 1), px = x + (look[0] * .32 + .14 * side) * w, py = y + look[1] * h * .25;
  ell(c, px, py, ir, ir, iris); ell(c, px, py, ir * .52 * (e.pupil || 1), ir * .52 * (e.pupil || 1), '#140a06');
  ell(c, px - ir * .32, py - ir * .35, ir * .26, ir * .26, '#fff');
  c.fillStyle = 'rgba(80,40,30,0.18)'; c.fillRect(x - w, top - h, w * 2, h * .55);
  c.restore();
  c.beginPath(); c.moveTo(bx, y); c.quadraticCurveTo(x, top - h * .15, fx, y - h * .05); c.lineWidth = lw * 1.5; c.strokeStyle = OL; sk(c); c.stroke();
  if (lash) { c.beginPath(); c.moveTo(fx, y - h * .05); c.lineTo(fx + side * w * .18, y - h * .35); c.lineWidth = lw; c.stroke(); }
  c.beginPath(); c.moveTo(bx + side * w * .1, y + h * .08); c.quadraticCurveTo(x, bot + h * .1, fx - side * w * .08, y + h * .02); c.lineWidth = lw * .55; c.stroke();
  // crease
  c.beginPath(); c.moveTo(bx + side * w * .1, top - h * .12); c.quadraticCurveTo(x, top - h * .5, fx - side * w * .15, top - h * .05); c.lineWidth = lw * .5; c.strokeStyle = rgba(OL, .55); c.stroke();
}
function brow(c, x, y, w, e, lw, side, col, thick = 1, asymK = 0) {
  const raise = (e.brow || 0) * w * .35 + asymK * (e.asym || 0) * w * .25, tilt = (e.tilt || 0) * w * .3;
  const inner = [x - side * w * .5, y - raise + tilt], mid = [x, y - raise - w * .12], outer = [x + side * w * .55, y - raise - tilt * .4 + w * .05];
  c.beginPath(); c.moveTo(inner[0], inner[1]); c.quadraticCurveTo(mid[0], mid[1] - w * .05, outer[0], outer[1]);
  c.lineWidth = lw * 2.4 * thick; c.strokeStyle = col; c.lineCap = 'round'; c.stroke();
}
function mouthFront(c, x, y, w, e, lw, skin) {
  const sm = e.smile || 0, o = e.open || 0;
  if (e.mouth === 'closed' || (e.mouth !== 'chew' && o < .06 && e.mouth !== 'o')) {
    const sk_ = e.smirk ? 1 : 0;
    c.beginPath(); c.moveTo(x - w * .5, y - sm * w * .18 + sk_ * w * .1); c.quadraticCurveTo(x, y + sm * w * .22, x + w * .5, y - sm * w * .18 - sk_ * w * .12);
    c.lineWidth = lw * 1.1; c.strokeStyle = OL; c.stroke();
    if (sm > .5) { line(c, [[x + w * .5, y - sm * w * .18 - sk_ * w * .12], [x + w * .6, y - sm * w * .1]], lw * .7, OL); }
    return;
  }
  if (e.mouth === 'chew') { const k = .5 + .5 * Math.sin((e.chewT || 0) * 22); ell(c, x, y, w * .28, w * (.06 + .12 * k), '#5a1a18', lw); return; }
  let pts;
  if (e.mouth === 'o') pts = [[x - w * .22, y], [x, y - w * .16], [x + w * .22, y], [x, y + w * .3 * (.5 + o)]];
  else if (e.mouth === 'teeth') pts = [[x - w * .5, y - w * .08], [x + w * .5, y - w * .08], [x + w * .45, y + w * .14], [x - w * .45, y + w * .14]];
  else pts = [[x - w * .52, y - w * .06 - sm * w * .1], [x, y + w * .02], [x + w * .52, y - w * .06 - sm * w * .1], [x + w * .32, y + w * (.18 + .38 * o)], [x, y + w * (.26 + .45 * o)], [x - w * .32, y + w * (.18 + .38 * o)]];
  c.save(); c.beginPath(); spline(c, pts, true, .5); c.fillStyle = '#5a1a18'; c.fill(); c.clip();
  c.fillStyle = '#fbf5ea'; c.fillRect(x - w, y - w * .4, w * 2, e.mouth === 'teeth' ? w * .6 : w * .2);
  if (e.mouth !== 'teeth') ell(c, x, y + w * (.42 + .4 * o), w * .32, w * .2, '#d6606a');
  c.restore();
  c.beginPath(); spline(c, pts, true, .5); c.lineWidth = lw; c.strokeStyle = OL; c.stroke();
}
function ear(c, x, y, u, skin, lw, flip = 1) {
  fillOL(c, [[x, y - u * .09], [x - flip * u * .07, y - u * .1], [x - flip * u * .1, y - u * .02], [x - flip * u * .08, y + u * .07], [x - flip * u * .02, y + u * .1], [x + flip * u * .02, y + u * .04]], skin, lw);
  c.beginPath(); c.moveTo(x - flip * u * .03, y - u * .05); c.quadraticCurveTo(x - flip * u * .08, y, x - flip * u * .03, y + u * .05); c.lineWidth = lw * .6; c.strokeStyle = rgba(OL, .7); c.stroke();
}
function noseFront(c, x, y, u, F, lw, skin, side = 0) {
  const w = (F.noseW || .09) * u, l = (F.noseLen || .1) * u;
  c.beginPath(); c.moveTo(x + side * w * .2 - w * .15, y - u * .14); c.quadraticCurveTo(x + side * w * .8, y - u * .02, x + side * w + w * .35, y + u * .04);
  c.lineWidth = lw * .8; c.strokeStyle = rgba(OL, .8); c.stroke();
  c.beginPath(); c.moveTo(x - w * .5, y + u * .06); c.quadraticCurveTo(x + side * w * .3, y + u * .1 + l * .2, x + w * .55, y + u * .06); c.lineWidth = lw * .9; c.strokeStyle = OL; c.stroke();
  ell(c, x - w * .25, y + u * .065, w * .12, w * .07, rgba(OL, .7)); ell(c, x + w * .3, y + u * .065, w * .12, w * .07, rgba(OL, .7));
}

// draws a whole head in a view; returns nothing. view: 'p' profile, 'q' three-quarter, 'f' front, 'b' back
function drawHead2(c, ch, view, e, u, lw) {
  const F = ch.face, skin = ch.skin, sh = shade(skin, .28), hl = tint(skin, .25);
  const iris = F.iris || '#5a3a22', bc = F.browCol || ch.hairCol || '#3a2416';
  const look = [e.lookX ?? .3, e.lookY ?? 0];
  const S = p => [p[0] * u, p[1] * u];
  if (ch.hairBack) ch.hairBack(c, view, u, lw, e);
  if (view === 'b') {
    const pts = headFront(ch, e).pts.map(S);
    fillOL(c, pts, skin, lw);
    ear(c, -.45 * u, -.5 * u, u, skin, lw, 1); ear(c, .45 * u, -.5 * u, u, skin, lw, -1);
    if (ch.hair) ch.hair(c, view, u, lw, e);
    if (ch.hat) ch.hat(c, view, u, lw, e);
    return;
  }
  if (view === 'p') {
    const H = headProfile(ch, e);
    const pts = H.pts.map(S);
    fillOL(c, pts, skin, 0);
    shadeIn(c, pts, cc => {
      cc.fillStyle = lg(cc, -.5 * u, 0, .45 * u, 0, [[0, rgba(sh, .45)], [.4, rgba(skin, 0)], [.85, rgba(hl, 0)], [1, rgba(hl, .4)]]); cc.fillRect(-u, -1.2 * u, 2 * u, 1.4 * u);
      if (F.stubble) { cc.fillStyle = rgba(F.stubble, .22); cc.beginPath(); cc.ellipse(.24 * u, -.11 * u, .2 * u, .085 * u, -.35, 0, TAU); cc.fill(); }
      if (e.cheek || F.cheeks) ell(cc, .26 * u, -.37 * u, .08 * u, .05 * u, rgba('#e0605a', .35 * Math.max(e.cheek || 0, F.cheeks || 0)));
      if (ch.faceShadow) { cc.fillStyle = lg(cc, 0, -u, 0, -.1 * u, [[0, `rgba(10,5,15,${ch.faceShadow})`], [1, `rgba(10,5,15,${ch.faceShadow * .25})`]]); cc.fillRect(-u, -1.2 * u, 2 * u, 1.2 * u); }
    });
    shapePath(c, pts); c.lineWidth = lw; c.strokeStyle = OL; sk(c); c.stroke();
    if ((e.open || 0) > .05 || e.mouth === 'chew') {
      const a = S(H.mouthTop), m = S([.4 - Math.min(.12, (e.open || 0) * .14), -.297]), b = S(H.mouthLow);
      const cav = [a, [m[0] - u * .02, m[1]], b, [lerp(a[0], b[0], .5) + u * .015, lerp(a[1], b[1], .5)]];
      fillOL(c, cav, '#5a1a18', 0, .3);
      c.save(); shapePath(c, cav, true, .3); c.clip();
      c.fillStyle = '#fbf5ea'; c.fillRect(m[0] - u * .05, a[1] - 2, u * .25, u * .05);
      ell(c, b[0] - u * .05, b[1] - u * .02, u * .08, u * .04, '#d6606a');
      c.restore();
      shapePath(c, cav, true, .3); c.lineWidth = lw * .9; c.strokeStyle = OL; c.stroke();
    }
    // nostril + lip line + chin crease
    const nt = S([.37 + (F.noseLen ?? .1) * .5, -.405]);
    c.beginPath(); c.moveTo(nt[0] - u * .04, nt[1]); c.quadraticCurveTo(nt[0], nt[1] + u * .02, nt[0] + u * .02, nt[1] - u * .005); c.lineWidth = lw * .7; c.strokeStyle = OL; c.stroke();
    if ((e.open || 0) <= .05 && e.mouth !== 'chew') {
      const a = S([.405, -.3]), sm = e.smile || 0;
      c.beginPath(); c.moveTo(a[0], a[1]); c.quadraticCurveTo(a[0] - u * .05, a[1] + u * (.01 - sm * .03), a[0] - u * .09, a[1] - u * sm * .04); c.lineWidth = lw * .9; c.stroke();
      if (sm > .4) { c.beginPath(); c.arc(a[0] - u * .1, a[1] - u * .06 * sm, u * .03, .8, 2.4); c.lineWidth = lw * .6; c.stroke(); }
    }
    ear(c, H.ear[0] * u, H.ear[1] * u, u, skin, lw, 1);
    almondEye(c, H.eye[0] * u, H.eye[1] * u, u * .17 * (F.eyeS || 1), u * .13 * (F.eyeS || 1), e, look, iris, lw * .8, 1, F.lash);
    brow(c, H.eye[0] * u, H.eye[1] * u - u * .11, u * .19, e, lw, 1, bc, F.browT || 1, 1);
    if (F.beard) F.beard(c, 'p', u, lw, e, H);
    if (F.tache) F.tache(c, 'p', u, lw, e, H);
    if (F.wrinkles) { c.beginPath(); c.moveTo(.34 * u, -.4 * u); c.quadraticCurveTo(.3 * u, -.33 * u, .33 * u, -.27 * u); c.lineWidth = lw * .5; c.strokeStyle = rgba(OL, .55); c.stroke(); }
    if (ch.hair) ch.hair(c, view, u, lw, e);
    if (ch.hat) ch.hat(c, view, u, lw, e);
    return;
  }
  if (view === 'q') {
    const H = head34(ch, e), pts = H.pts.map(S);
    fillOL(c, pts, skin, 0);
    shadeIn(c, pts, cc => {
      cc.fillStyle = lg(cc, -.5 * u, 0, .45 * u, 0, [[0, rgba(sh, .5)], [.35, rgba(skin, 0)], [.9, rgba(hl, .22)]]); cc.fillRect(-u, -1.2 * u, 2 * u, 1.4 * u);
      if (F.stubble) { cc.fillStyle = rgba(F.stubble, .22); cc.beginPath(); cc.ellipse(.14 * u, -.1 * u, .28 * u, .09 * u, 0, 0, TAU); cc.fill(); }
      if (e.cheek || F.cheeks) { ell(cc, .33 * u, -.38 * u, .07 * u, .045 * u, rgba('#e0605a', .35 * Math.max(e.cheek || 0, F.cheeks || 0))); ell(cc, -.04 * u, -.38 * u, .06 * u, .04 * u, rgba('#e0605a', .3 * Math.max(e.cheek || 0, F.cheeks || 0))); }
      if (ch.faceShadow) { cc.fillStyle = lg(cc, 0, -u, 0, -.1 * u, [[0, `rgba(10,5,15,${ch.faceShadow})`], [1, `rgba(10,5,15,${ch.faceShadow * .25})`]]); cc.fillRect(-u, -1.2 * u, 2 * u, 1.2 * u); }
    });
    shapePath(c, pts); c.lineWidth = lw; c.strokeStyle = OL; sk(c); c.stroke();
    ear(c, H.ear[0] * u, H.ear[1] * u, u, skin, lw, 1);
    const es = F.eyeS || 1;
    almondEye(c, H.eyeF[0] * u, H.eyeF[1] * u, u * .14 * es, u * .12 * es, e, look, iris, lw * .75, 1, F.lash);
    almondEye(c, H.eyeN[0] * u, H.eyeN[1] * u, u * .17 * es, u * .13 * es, e, look, iris, lw * .8, 1, F.lash);
    brow(c, H.eyeF[0] * u, H.eyeF[1] * u - u * .11, u * .15, e, lw, -1, bc, F.browT || 1, -1);
    brow(c, H.eyeN[0] * u, H.eyeN[1] * u - u * .11, u * .19, e, lw, 1, bc, F.browT || 1, 1);
    // nose: designed 3/4 nose protruding toward the near cheek
    const nl = F.noseLen ?? .1, nd = F.noseDrop || 0, tipx = .27 + nl * .55, tipy = -.42 + nd;
    const nosePts = [[.1, -.6], [.15, -.53], [tipx, tipy - .01], [tipx + .005, tipy + .035], [tipx - .06, tipy + .05], [.09, tipy + .045], [.07, -.47]].map(S);
    fillOL(c, nosePts, tint(skin, .1), 0, .35);
    c.beginPath(); c.moveTo(...S([.11, -.6])); c.quadraticCurveTo(...S([.17, -.5]), ...S([tipx, tipy - .01])); c.quadraticCurveTo(...S([tipx + .03, tipy + .04]), ...S([tipx - .05, tipy + .05])); c.lineWidth = lw * .9; c.strokeStyle = OL; c.stroke();
    c.beginPath(); c.moveTo(...S([.13, tipy + .04])); c.quadraticCurveTo(...S([.07, tipy + .02]), ...S([.1, tipy - .02])); c.lineWidth = lw * .7; c.stroke();
    ell(c, ...S([tipx - .07, tipy + .035]), u * .02, u * .012, rgba(OL, .8));
    const m = S(H.mouth);
    mouthFront(c, m[0], m[1], u * .24, e, lw * .9, skin);
    if (F.beard) F.beard(c, 'q', u, lw, e, H);
    if (F.tache) F.tache(c, 'q', u, lw, e, H);
    if (ch.hair) ch.hair(c, view, u, lw, e);
    if (ch.hat) ch.hat(c, view, u, lw, e);
    return;
  }
  // front
  const H = headFront(ch, e), pts = H.pts.map(S);
  fillOL(c, pts, skin, 0);
  shadeIn(c, pts, cc => {
    cc.fillStyle = rg(cc, .1 * u, -.55 * u, .1 * u, .7 * u, [[0, rgba(hl, .25)], [1, rgba(sh, .55)]]); cc.fillRect(-u, -1.2 * u, 2 * u, 1.4 * u);
    if (F.stubble) { cc.fillStyle = rgba(F.stubble, .22); cc.beginPath(); cc.ellipse(0, -.15 * u, .38 * u, .16 * u, 0, 0, TAU); cc.fill(); }
    if (e.cheek || F.cheeks) for (const s of [-1, 1]) ell(cc, s * .25 * u, -.38 * u, .07 * u, .045 * u, rgba('#e0605a', .35 * Math.max(e.cheek || 0, F.cheeks || 0)));
    if (ch.faceShadow) { cc.fillStyle = lg(cc, 0, -u, 0, -.1 * u, [[0, `rgba(10,5,15,${ch.faceShadow})`], [1, `rgba(10,5,15,${ch.faceShadow * .25})`]]); cc.fillRect(-u, -1.2 * u, 2 * u, 1.2 * u); }
  });
  shapePath(c, pts); c.lineWidth = lw; c.strokeStyle = OL; sk(c); c.stroke();
  ear(c, -.45 * u, -.5 * u, u, skin, lw, 1); ear(c, .45 * u, -.5 * u, u, skin, lw, -1);
  const es = F.eyeS || 1;
  for (const s of [-1, 1]) { almondEye(c, s * .17 * u, -.545 * u, u * .16 * es, u * .125 * es, e, look, iris, lw * .8, s, F.lash); brow(c, s * .17 * u, -.66 * u, u * .18, e, lw, s, bc, F.browT || 1, s); }
  noseFront(c, 0, -.47 * u, u, F, lw, skin);
  const m = S(H.mouth); mouthFront(c, m[0], m[1], u * .25, e, lw * .9, skin);
  if (F.beard) F.beard(c, 'f', u, lw, e, H);
  if (F.tache) F.tache(c, 'f', u, lw, e, H);
  if (ch.hair) ch.hair(c, view, u, lw, e);
  if (ch.hat) ch.hat(c, view, u, lw, e);
}

// ---------------------------------------------------------------- HANDS (size = hand length px)
function hand2(c, wr, ang, kind, sz, skin, lw, flip = 1) {
  c.save(); c.translate(wr[0], wr[1]); c.rotate(-ang); c.scale(flip, 1);
  const s = sz, sh = shade(skin, .2);
  const finger = (x, y, a, len, w) => { c.save(); c.translate(x, y); c.rotate(a); rrect(c, -w / 2, 0, w, len, w / 2, skin, lw * .8, OL); c.restore(); };
  if (kind === 'fist' || kind === 'grip') {
    fillOL(c, [[-.3 * s, 0], [-.36 * s, .3 * s], [-.25 * s, .62 * s], [.12 * s, .66 * s], [.32 * s, .5 * s], [.3 * s, .1 * s], [.1 * s, -.04 * s]], skin, lw);
    for (let i = 0; i < 4; i++) { c.beginPath(); c.arc(-.18 * s + i * .14 * s, .58 * s, .07 * s, 0, PI); c.lineWidth = lw * .6; c.strokeStyle = OL; c.stroke(); }
    fillOL(c, [[.18 * s, .12 * s], [.36 * s, .22 * s], [.34 * s, .4 * s], [.16 * s, .34 * s]], tint(skin, .05), lw * .8);
  } else if (kind === 'point') {
    fillOL(c, [[-.3 * s, 0], [-.34 * s, .32 * s], [-.22 * s, .55 * s], [.1 * s, .58 * s], [.3 * s, .42 * s], [.3 * s, .08 * s], [.08 * s, -.04 * s]], skin, lw);
    finger(-.12 * s, .5 * s, 0, .55 * s, .13 * s);
    for (let i = 1; i < 4; i++) { c.beginPath(); c.arc(-.12 * s + i * .12 * s, .54 * s, .06 * s, 0, PI); c.lineWidth = lw * .6; c.stroke(); }
    fillOL(c, [[.2 * s, .14 * s], [.38 * s, .26 * s], [.34 * s, .42 * s], [.18 * s, .36 * s]], skin, lw * .8);
  } else {
    // open / spread / palm / wave / relaxed
    const spread = kind === 'spread' ? .22 : kind === 'relaxed' ? .02 : .08, curl = kind === 'relaxed' ? .55 : 1;
    fillOL(c, [[-.3 * s, 0], [-.34 * s, .3 * s], [-.3 * s, .52 * s], [.28 * s, .52 * s], [.32 * s, .25 * s], [.26 * s, 0]], skin, lw);
    const fl = [.42, .5, .47, .36];
    for (let i = 0; i < 4; i++) finger(-.22 * s + i * .15 * s, .48 * s, (i - 1.5) * -spread, fl[i] * s * curl, .13 * s);
    c.save(); c.translate(.28 * s, .12 * s); c.rotate(-.9 - spread * 2); rrect(c, -.07 * s, 0, .14 * s, .4 * s, .07 * s, skin, lw * .8, OL); c.restore();
    c.fillStyle = rgba(sh, .5); c.fillRect(-.28 * s, .05 * s, .54 * s, .12 * s);
  }
  c.restore();
}
// ---------------------------------------------------------------- LIMB SEGMENTS
// shaped segment from a to b; widths [start, bulge, end]; bias shifts the bulge to one side (+ = toward 'front')
function segment(c, a, b, w0, w1, w2, fill, lw, bias = 0, bulgeAt = .35, shadeSide = -1) {
  const dx = b[0] - a[0], dy = b[1] - a[1], L = Math.hypot(dx, dy) || 1, nx = -dy / L, ny = dx / L;
  const P = (k, w) => [a[0] + dx * k + nx * w, a[1] + dy * k + ny * w];
  const pts = [P(0, w0), P(bulgeAt, w1 * (1 + bias)), P(.85, (w1 + w2) / 2), P(1, w2), [b[0] + dx / L * w2 * .6, b[1] + dy / L * w2 * .6], P(1, -w2), P(.85, -(w1 + w2) / 2), P(bulgeAt, -w1 * (1 - bias)), P(0, -w0), [a[0] - dx / L * w0 * .5, a[1] - dy / L * w0 * .5]];
  fillOL(c, pts, fill, 0, .5);
  shadeIn(c, pts, cc => { cc.fillStyle = rgba('#1a0c18', .22); cc.beginPath(); const Q = (k, w) => [a[0] + dx * k + nx * w, a[1] + dy * k + ny * w]; const s = shadeSide; cc.moveTo(...Q(-.1, s * w0 * 1.2)); cc.lineTo(...Q(1.1, s * w2 * 1.2)); cc.lineTo(...Q(1.1, s * w2 * .2)); cc.lineTo(...Q(-.1, s * w0 * .2)); cc.fill(); }, .5);
  shapePath(c, pts, true, .5); c.lineWidth = lw; c.strokeStyle = OL; sk(c); c.stroke();
  return pts;
}
function shoe(c, ank, f, len, col, lw, view, lift = 0) {
  c.save(); c.translate(ank[0], ank[1]); c.rotate(lift);
  if (view < .35) { fillOL(c, [[-len * .32, -len * .1], [-len * .36, len * .2], [0, len * .28], [len * .36, len * .2], [len * .32, -len * .1], [0, -len * .2]], col, lw); }
  else fillOL(c, [[-len * .28, -len * .22], [-len * .32, len * .16], [-len * .2, len * .26], [len * .8, len * .26], [len * .92, len * .12], [len * .62, -len * .04], [len * .25, -len * .14], [len * .1, -len * .28]], col, lw);
  line(c, [[-len * .3, len * .22], [view < .35 ? len * .3 : len * .88, len * .22]], lw * .8, shade(col, .4));
  c.restore();
}

// ---------------------------------------------------------------- BODY / COSTUME
// Costume levels: list of [lev, W (front half-width), Df (front depth), Db (back depth)] from hem up to neck.
// lev: 0 = hip, 1 = shoulder line, negative = below hip.
function torsoPts(levels, hip, up, rt, T, v, swing, flare = 1) {
  const fr = [], bk = [];
  for (const [lev, W, Df, Db] of levels) {
    const below = lev < 0 ? -lev : 0;
    const base = [hip[0] + up[0] * T * lev, hip[1] + up[1] * T * lev];
    const sw = swing * below * T * .6;
    const ef = lerp(W, Df, v) * (lev < 0 ? flare : 1), eb = lerp(W, Db, v) * (lev < 0 ? flare : 1);
    const cs = lerp(0, (Df - Db) * .15, v);
    fr.push([base[0] + rt[0] * (ef + cs) - sw, base[1] + rt[1] * (ef + cs)]);
    bk.push([base[0] - rt[0] * (eb - cs) - sw, base[1] - rt[1] * (eb - cs)]);
  }
  return [...fr, ...bk.reverse()];
}
const VIEWV = { f: 0, q: .5, p: 1, b: 0 };

function drawChar2(c, ch, pose, t) {
  const p = Object.assign({ x: 0, y: 0, s: 1, f: 1, view: 'q', head: 0, lean: 0, air: 0, sq: 1, swing: 0, shL: -.12, elL: .25, shR: .1, elR: .3, wrL: 0, wrR: 0,
    hipL: 0, kneeL: 0, hipR: 0, kneeR: 0, handL: 'relaxed', handR: 'relaxed', expr: EXPR.neutral }, pose);
  const B = ch.body, u = B.hh, sc = p.s;
  const lw = (ch.lw || 4.2) / Math.max(.6, Math.min(sc, 2.4)) * Math.max(.75, Math.min(sc, 1.6));
  const v = VIEWV[p.view] ?? .5, back = p.view === 'b';
  const hv = p.headView || (p.view === 'f' ? 'f' : p.view === 'b' ? 'b' : p.view === 'p' ? 'p' : 'q');
  c.save(); c.translate(p.x, p.y); c.scale(p.f * sc, sc);
  // ---- legs (hip at origin, solve ground)
  const hipW = B.hipW;
  const hxN = lerp(hipW * .22, 6, v), hxF = lerp(-hipW * .22, -6, v);
  const legPt = (hx, a, k) => { const hip = [hx, 0], kn = [hx + Math.sin(a) * B.thigh, Math.cos(a) * B.thigh], an = [kn[0] + Math.sin(a - k) * B.shin, kn[1] + Math.cos(a - k) * B.shin]; return [hip, kn, an]; };
  const lN = legPt(hxN, p.hipR, p.kneeR), lF = legPt(hxF, p.hipL, p.kneeL);
  const low = Math.max(lN[2][1], lF[2][1]) + B.foot * .25;
  c.translate(0, -low - p.air);
  if (p.sq !== 1) { c.translate(0, low); c.scale(1 / Math.sqrt(p.sq), p.sq); c.translate(0, -low); }
  // ground shadow
  if (ch.noShadow !== true) { c.save(); c.translate(0, low + p.air); c.scale(1, .18); ell(c, 8, 0, (hipW + 60) * (1 - clamp(p.air / 500, 0, .6)), 70, 'rgba(20,10,20,0.3)'); c.restore(); }
  // ---- torso frame
  const T = B.torso, up = [Math.sin(p.lean), -Math.cos(p.lean)], rt = [Math.cos(p.lean), Math.sin(p.lean)];
  const hip = [0, 0], shC = [up[0] * T, up[1] * T];
  const shW = B.shW;
  const sN = [shC[0] + rt[0] * lerp(shW * .5, shW * .12, v) + (back ? 0 : 0), shC[1] + rt[1] * lerp(shW * .5, shW * .12, v) + u * .12];
  const sF = [shC[0] - rt[0] * lerp(shW * .5, shW * .05, v), shC[1] - rt[1] * lerp(shW * .5, shW * .05, v) + u * .12];
  const armPts = (sh, a, e) => { const el = [sh[0] + Math.sin(a) * B.upperArm, sh[1] + Math.cos(a) * B.upperArm]; const wr = [el[0] + Math.sin(a + e) * B.foreArm, el[1] + Math.cos(a + e) * B.foreArm]; return [sh, el, wr]; };
  const aN = armPts(sN, p.shR, p.elR), aF = armPts(sF, p.shL, p.elL);
  const J = { hip, shC, sN, sF, handN: aN[2], handF: aF[2], elN: aN[1], elF: aF[1], footN: lN[2], footF: lF[2], kneeN: lN[1], kneeF: lF[1], neck: [shC[0] + up[0] * u * .1, shC[1] + up[1] * u * .1], angN: p.shR + p.elR, angF: p.shL + p.elL, u };
  const col = ch.col;
  const H = { c, J, p, lw, u, v, back, hip, up, rt, T, t };
  // ---- far side
  if (ch.costume.cape) ch.costume.cape(H, 'back');
  if (p.hold && p.hold.back) p.hold.back(c, J, sc);
  const farArmBehind = v > .25 && !back;
  const drawArm = (A, near, a0, e0, wr, hk) => {
    const sleeve = near ? col.sleeve : shade(col.sleeve, .2), skin = near ? ch.skin : shade(ch.skin, .15);
    const aw = B.armW;
    const fore = segment(c, A[1], A[2], aw * .42, aw * .46, aw * .3, ch.costume.bareFore ? skin : shade(sleeve, .06), lw, .25, .3, near ? -1 : 1);
    if (ch.costume.cuff) ch.costume.cuff(H, A, near);
    const handAng = a0 + e0 + wr;
    hand2(c, A[2], handAng, hk, B.hand, skin, lw, 1);
    if (ch.costume.puff) ch.costume.puff(H, A, near, sleeve);
    else segment(c, A[0], A[1], aw * .55, aw * .58, aw * .42, sleeve, lw, .2, .25, near ? -1 : 1);
    ell(c, A[1][0], A[1][1], aw * .4, aw * .4, sleeve);   // elbow cap (hides pivot)
  };
  if (farArmBehind) { drawArm(aF, false, p.shL, p.elL, p.wrL, p.handL); if (p.hold && p.hold.L) p.hold.L(c, J, sc); }
  // legs
  const drawLeg = (Lg, near, a, k) => {
    const legc = near ? col.legs : shade(col.legs, .2);
    segment(c, Lg[1], Lg[2], B.legW * .44, B.legW * .5, B.legW * .3, legc, lw, -.35, .3, near ? -1 : 1);
    shoe(c, Lg[2], 1, B.foot, near ? col.shoes : shade(col.shoes, .2), lw, v, clamp((a - k) * .35, -.6, .6));
    segment(c, Lg[0], Lg[1], B.legW * .62, B.legW * .62, B.legW * .44, legc, lw, .15, .3, near ? -1 : 1);
    ell(c, Lg[1][0], Lg[1][1], B.legW * .42, B.legW * .42, legc);
    if (ch.costume.boot) ch.costume.boot(H, Lg, near);
  };
  drawLeg(lF, false, p.hipL, p.kneeL);
  drawLeg(lN, true, p.hipR, p.kneeR);
  // ---- torso costume
  const sway = clamp(p.swing, -.8, .8);
  const tp = torsoPts(ch.costume.levels, hip, up, rt, T, v, sway, ch.costume.flare || 1);
  if (ch.costume.cape) ch.costume.cape(H, 'mid');
  fillOL(c, tp, col.body, 0, .42);
  shadeIn(c, tp, cc => {
    if (ch.costume.detail) ch.costume.detail(H, back);
    cc.fillStyle = lg(cc, -B.shW * .6, 0, B.shW * .6, 0, [[0, rgba('#1a0c18', .35)], [.45, rgba('#1a0c18', 0)], [.85, rgba('#fff0d0', 0)], [1, rgba('#fff0d0', .2)]]);
    cc.fillRect(-500, -T - 300, 1000, T + 700);
  }, .42);
  shapePath(c, tp, true, .42); c.lineWidth = lw; c.strokeStyle = OL; sk(c); c.stroke();
  if (ch.costume.over) ch.costume.over(H, back);
  // ---- neck + head
  c.save(); c.translate(J.neck[0], J.neck[1]);
  const nw = B.neckW;
  fillOL(c, [[-nw * .5, u * .14], [-nw * .45, -u * .22], [nw * .5, -u * .22], [nw * .55, u * .14]], shade(ch.skin, .2), lw * .9);
  if (ch.costume.collar) ch.costume.collar(H, back);
  c.translate(lerp(0, u * .08, v), -u * .1 + (p.nod || 0)); c.rotate(p.lean * .5 + p.head);
  drawHead2(c, ch, hv, Object.assign({}, p.expr, { chewT: p.chewT }), u, lw);
  c.restore();
  if (ch.costume.cape) ch.costume.cape(H, 'front');
  // ---- near arm (and far arm when facing front)
  if (!farArmBehind) { drawArm(aF, back ? true : false, p.shL, p.elL, p.wrL, p.handL); if (p.hold && p.hold.L) p.hold.L(c, J, sc); }
  if (p.hold && p.hold.Rb) p.hold.Rb(c, J, sc);
  drawArm(aN, true, p.shR, p.elR, p.wrR, p.handR);
  if (p.hold && p.hold.R) p.hold.R(c, J, sc);
  c.restore();
  return J;
}

// ---------------------------------------------------------------- motion helpers
// Keyed walk: contact / down / passing / up, one step per beat. returns pose fields.
function walk2(t, o = {}) {
  const dur = o.step || SPB, ph = ((t / dur) + (o.ph || 0)) % 2;     // 0..2 for a full stride (2 steps)
  const side = ph < 1 ? 1 : -1, k = ph % 1;
  const A = o.amp ?? 1;
  // key poses for the leading (near when side=1) leg over one step
  const keys = [
    [0, { hipF: .42, kneeF: .05, hipB: -.38, kneeB: .25, bob: 0, arm: .45 }],
    [.25, { hipF: .25, kneeF: .3, hipB: -.32, kneeB: .55, bob: 10, arm: .35 }],    // down
    [.5, { hipF: 0, kneeF: .15, hipB: .05, kneeB: 1.15, bob: -2, arm: 0 }],         // passing
    [.75, { hipF: -.25, kneeF: .1, hipB: .32, kneeB: .55, bob: -8, arm: -.3 }],    // up
    [1, { hipF: -.38, kneeF: .25, hipB: .42, kneeB: .05, bob: 0, arm: -.45 }],
  ];
  let a = keys[0][1], b = keys[1][1], kk = 0;
  for (let i = 1; i < keys.length; i++) if (k <= keys[i][0]) { a = keys[i - 1][1]; b = keys[i][1]; kk = (k - keys[i - 1][0]) / (keys[i][0] - keys[i - 1][0]); break; }
  const L = (n) => lerp(a[n], b[n], sm(kk));
  const front = { hip: L('hipF') * A, knee: L('kneeF') * A }, backL = { hip: L('hipB') * A, knee: L('kneeB') * A };
  const near = side > 0 ? front : backL, far = side > 0 ? backL : front;
  const arm = L('arm') * side * A;
  return { hipR: near.hip, kneeR: near.knee, hipL: far.hip, kneeL: far.knee, shR: -arm * (o.armAmp ?? 1) + (o.armR || 0), elR: .35 + Math.max(0, -arm) * .3, shL: arm * (o.armAmp ?? 1) + (o.armL || 0), elL: .35 + Math.max(0, arm) * .3,
    air: -L('bob') * (o.bob ?? 1) + 8, lean: (o.lean ?? .06), swing: -arm * .25, nod: L('bob') * .2, head: Math.sin(ph * PI) * .02 };
}
// phrase of poses keyed in beats: [[beat, pose, ease], ...]  with anticipation/overshoot from easing
function phrase(t, t0, ks, loopBeats = 0) {
  let b = (t - t0) / SPB; if (loopBeats) b = ((b % loopBeats) + loopBeats) % loopBeats;
  return poseKeys(b, ks);
}
function mergeP(...os) { const r = {}; for (const o of os) if (o) for (const k in o) { if (k === 'expr') r.expr = Object.assign({}, r.expr, o.expr); else r[k] = o[k]; } return r; }

// interpolate between pose objects (numeric fields only)
function poseLerp(a, b, k) { const r = Object.assign({}, a); for (const kk in b) { if (typeof b[kk] === 'number' && typeof a[kk] === 'number') r[kk] = lerp(a[kk], b[kk], k); else if (kk === 'expr') r.expr = Object.assign({}, a.expr || {}, k > .5 ? b.expr : {}); else if (k > .5 || a[kk] === undefined) r[kk] = b[kk]; } return r; }
// pose keyframes: [[t, poseObj, ease], ...]
function poseKeys(t, ks) {
  if (t <= ks[0][0]) return ks[0][1];
  for (let i = 1; i < ks.length; i++) if (t <= ks[i][0]) { const k = E[ks[i][2] || 'io']((t - ks[i - 1][0]) / (ks[i][0] - ks[i - 1][0])); return poseLerp(ks[i - 1][1], ks[i][1], k); }
  return ks[ks.length - 1][1];
}
