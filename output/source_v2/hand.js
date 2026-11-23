// hand: jointed 3D hand (palm, four fingers, thumb) projected and drawn with ink/pencil
const C = require('./core');
const I = require('./ink');
const { add, sub, mul, dot, cross, norm, rotAxis, clamp, lerp } = C;

const FING = [ // [knuckle side offset, fwd offset, segment lengths, radius]
  { o: 2.75, f: 8.3, L: [4.3, 2.6, 2.15], r: .9 },
  { o: .92, f: 8.7, L: [4.7, 2.9, 2.25], r: .93 },
  { o: -.92, f: 8.4, L: [4.4, 2.75, 2.15], r: .87 },
  { o: -2.6, f: 7.6, L: [3.5, 2.15, 1.95], r: .78 },
];
// build hand geometry. H: {w (wrist pos), fwd, nrm (back of hand), th (thumb side), scale}
// pose: {curl:[4] 0..1 or per-finger {m,p,d}, spread 0..1, thumb:{curl, out, opp}, f:[...] explicit [mcp,pip,dip] radians}
function buildHand(H, pose = {}) {
  const sc = H.scale || 1; const fwd = norm(H.fwd), nrm0 = norm(H.nrm); const th = norm(H.th);
  const nrm = norm(sub(nrm0, mul(fwd, dot(nrm0, fwd))));
  const P = (f, s, n) => add(H.w, add(mul(fwd, f * sc), add(mul(th, s * sc), mul(nrm, n * sc))));
  const fingers = FING.map((F, i) => {
    let ang;
    if (pose.f && pose.f[i]) ang = pose.f[i];
    else { const c = Array.isArray(pose.curl) ? pose.curl[i] : (pose.curl ?? .25); ang = [c * 1.35, c * 1.6, c * 1.05]; }
    const spread = (pose.spread ?? .25) * (i - 1.4) * -.16;
    const base = P(F.f, F.o, 0);
    let dir = rotAxis(fwd, nrm, spread); let flexAx = norm(cross(dir, nrm)); // bending toward palm (-nrm)
    const pts = [base]; let p = base; let d = dir;
    for (let k = 0; k < 3; k++) {
      d = rotAxis(d, flexAx, -ang[k]); // negative: curl toward palm side
      p = add(p, mul(d, F.L[k] * sc)); pts.push(p);
    }
    return { pts, r: F.r * sc, dirTip: d };
  });
  // thumb
  const tp = pose.thumb || {}; const tc = tp.curl ?? .2, tout = tp.out ?? .4, topp = tp.opp ?? .3;
  const tb = P(1.9, 2.9, -.9);
  let td = norm(add(add(mul(fwd, .55), mul(th, .75 * (.4 + tout))), mul(nrm, -.35 - topp * .55)));
  td = rotAxis(td, fwd, -topp * .4 * (H.side || 1));
  const tAx = norm(cross(td, nrm)); const tpts = [tb]; let tpp = tb, tdd = td;
  [4.2, 3.1, 2.6].forEach((l, k) => { if (k) tdd = rotAxis(tdd, add(tAx, mul(nrm, .4)), -(tc * (k === 1 ? .7 : 1.0))); tpp = add(tpp, mul(tdd, l * sc)); tpts.push(tpp); });
  const thumb = { pts: tpts, r: 1.08 * sc };
  // palm hull points (back and palm surfaces)
  const palm = [];
  for (const n of [-1.15, 1.0]) {
    palm.push(P(0, 2.4, n * .8), P(0, -2.3, n * .8), P(1.2, -3.2, n), P(5, -3.25, n), P(7.6, -2.6 - .2, n * .9), P(8.4, -.9, n * .9), P(8.7, .9, n * .9), P(8.3, 2.75, n * .9), P(5.5, 3.3, n), P(2.4, 3.4, n));
  }
  return { fingers, thumb, palm, H: { ...H, fwd, nrm, th }, sc };
}

function hull(pts) { // monotone chain
  const P = pts.slice().sort((a, b) => a[0] - b[0] || a[1] - b[1]); if (P.length < 3) return P;
  const crs = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
  const lo = [], up = [];
  for (const p of P) { while (lo.length >= 2 && crs(lo[lo.length - 2], lo[lo.length - 1], p) <= 0) lo.pop(); lo.push(p); }
  for (let i = P.length - 1; i >= 0; i--) { const p = P[i]; while (up.length >= 2 && crs(up[up.length - 2], up[up.length - 1], p) <= 0) up.pop(); up.push(p); }
  up.pop(); lo.pop(); return lo.concat(up);
}
function roundHull(H) { // Chaikin corner cutting x2
  let P = H; for (let k = 0; k < 2; k++) { const o = []; for (let i = 0; i < P.length; i++) { const a = P[i], b = P[(i + 1) % P.length]; o.push([a[0] * .75 + b[0] * .25, a[1] * .75 + b[1] * .25], [a[0] * .25 + b[0] * .75, a[1] * .25 + b[1] * .75]); } P = o; } return P;
}

// draw hand; o: {skin, sleeve:{col, r, len} drawn from wrist backwards, nails:bool, cuff}
function drawHand(g, cam, hand, o = {}) {
  const skin = o.skin || '#efc4a2'; const toCam = cam.toCam(hand.H.w);
  const backVis = dot(hand.H.nrm, toCam);
  const proj = p => { const q = cam.p(p); return q; };
  const items = [];
  const palm2 = roundHull(hull(hand.palm.map(p => { const q = proj(p); return [q.x, q.y]; })));
  const pc = proj(add(hand.H.w, mul(hand.H.fwd, 4.5 * hand.sc)));
  items.push({ z: pc.z + (backVis > 0 ? .0 : 0), draw: () => I.shape(g, palm2, { fill: skin, lw: o.lw, seed: 501, shade: pc.s * 1.6 }) });
  const fingerItem = (f, i, isThumb) => {
    const Q = f.pts.map(proj); const C2 = Q.map(q => [q.x, q.y]);
    const R = Q.map((q, k) => f.r * (1 - k * .06) * q.s / (f.r ? 1 : 1));
    const mid = proj(f.pts[2]);
    // relative depth vs palm: fingers that bend toward palm and palm faces camera -> in front
    items.push({
      z: mid.z - (isThumb ? .3 : 0), draw: () => {
        const pts = I.tubePts(C2, R.map((r, k) => k === 0 ? r * 1.05 : r), false, true, 4);
        I.shape(g, pts, { fill: skin, lw: o.lw, seed: 510 + i, shade: mid.s * .9 });
        // nail
        if (o.nails !== false && backVis > .05) {
          const a = f.pts[2], b = f.pts[3]; const nb = add(lerp3(a, b, .55), mul(hand.H.nrm, f.r * .7));
          const q = proj(nb), qa = proj(add(lerp3(a, b, .25), mul(hand.H.nrm, f.r * .7))), qb = proj(add(lerp3(a, b, .92), mul(hand.H.nrm, f.r * .6)));
          const ang = Math.atan2(qb.y - qa.y, qb.x - qa.x); const lx = Math.hypot(qb.x - qa.x, qb.y - qa.y) / 2;
          if (lx > 1.2) I.shape(g, I.ellipsePts(q.x, q.y, lx, f.r * q.s * .62 * clamp(backVis * 1.3 + .2, .3, 1), ang, 14), { fill: I.mix(skin, '#ffffff', .35), lw: Math.max(.8, (o.lw ?? I.ST.inkW) * .45), seed: 520 + i, shade: 1 });
        }
        // knuckle creases
        if (backVis > .2 && !isThumb) for (const k of [1, 2]) { const q = proj(add(f.pts[k], mul(hand.H.nrm, f.r * .85))); const r = f.r * q.s * .45; if (r > 1.5) I.brush(g, [[q.x - r, q.y], [q.x, q.y - r * .25], [q.x + r, q.y]], Math.max(.8, r * .22), { alpha: .5 }); }
      }
    });
  };
  hand.fingers.forEach((f, i) => fingerItem(f, i, false));
  fingerItem(hand.thumb, 4, true);
  // sleeve / forearm behind the wrist
  if (o.sleeve) {
    const S = o.sleeve; const a = proj(hand.H.w), b = proj(add(hand.H.w, mul(hand.H.fwd, -(S.len || 30) * hand.sc)));
    items.push({ z: Math.max(a.z, b.z) + 1, draw: () => { const pts = I.tubePts([[b.x, b.y], [a.x, a.y]], [S.r * b.s, S.r * .9 * a.s], false, false, 3); if (S.cuff) { const c0 = proj(add(hand.H.w, mul(hand.H.fwd, -3.2 * hand.sc))), c1 = proj(add(hand.H.w, mul(hand.H.fwd, -.6 * hand.sc))); I.shape(g, pts, { fill: S.col, lw: o.lw, seed: 530, shade: a.s * 2 }); const cp = I.tubePts([[c0.x, c0.y], [c1.x, c1.y]], [S.r * .98 * c0.s, S.r * .95 * c1.s], false, false, 2); I.shape(g, cp, { fill: S.cuff, lw: o.lw, seed: 531, shade: c1.s }); } else I.shape(g, pts, { fill: S.col, lw: o.lw, seed: 530, shade: a.s * 2 }); } });
  }
  items.sort((p, q) => q.z - p.z); items.forEach(it => it.draw());
}
const lerp3 = C.lerp3;
function tip(hand, i) { return i === 4 ? hand.thumb.pts[3] : hand.fingers[i].pts[3]; }
// solve finger i flex so that its tip reaches plane y = yTarget (world y), returns per-joint angles
function solveDown(Hspec, pose, i, yTarget, iters = 18) {
  let lo = -.4, hi = 1.6;
  for (let k = 0; k < iters; k++) {
    const m = (lo + hi) / 2; const f = (pose.f || []).slice(); f[i] = [m * .9, m * 1.05, m * .7];
    const h = buildHand(Hspec, { ...pose, f }); const y = tip(h, i)[1];
    if (y > yTarget) lo = m; else hi = m;
  }
  const m = (lo + hi) / 2; return [m * .9, m * 1.05, m * .7];
}

module.exports = { buildHand, drawHand, tip, solveDown, FING, hull };
