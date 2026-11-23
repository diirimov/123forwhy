// body: 3D-posed puppet rendered with hand-drawn ink (torso slices, IK limbs, clothing, head, hands)
const C = require('./core');
const I = require('./ink');
const Hd = require('./head');
const Hn = require('./hand');
const { add, sub, mul, dot, cross, norm, len, rotAxis, frame, fx, fdir, frot, clamp, lerp } = C;

const CLOTH = {
  morten: { '80s': { jacket: '#1d1c23', jhi: '#565569', shirt: '#f1ede4', pants: '#24232b', shoe: '#141416', neck: 'crew', leather: true, cuff: null, build: .95, h: 1.03 },
    late: { jacket: '#202128', jhi: '#45465a', shirt: '#2e2f38', pants: '#1c1c22', shoe: '#121214', neck: 'open', build: .98, h: 1.03 } },
  magne: { '80s': { jacket: '#6c9dcf', jhi: '#a6c8ea', shirt: '#f5f2ea', pants: '#373c52', shoe: '#e7e3da', neck: 'collar', tie: '#b5313a', cuff: '#f5f2ea', build: 1.0, h: 1.0 },
    late: { jacket: '#2c4565', jhi: '#4f6e96', shirt: '#e5dfd3', pants: '#24283a', shoe: '#2a2a2e', neck: 'collar', cuff: '#e5dfd3', build: 1.02, h: 1.0 } },
  pal: { '80s': { jacket: '#87283a', jhi: '#b9505f', shirt: '#2a2c38', stripes: '#d6d0c2', pants: '#2a2932', shoe: '#4b3222', neck: 'crew', build: .94, h: .99 },
    late: { jacket: '#5a2a31', jhi: '#86454f', shirt: '#383942', pants: '#24232a', shoe: '#2f241c', neck: 'crew', build: .96, h: .99 } },
  teen: { '80s': { jacket: '#d4675a', jhi: '#ee9a86', shirt: '#d4675a', stripes: '#f1d9b8', pants: '#3f5f86', shoe: '#e9e6df', neck: 'crew', build: .86, h: .92, sweater: true } },
  fan: { '80s': { jacket: '#4a6c95', jhi: '#7d9cc2', shirt: '#e9e3d4', pants: '#2c3445', shoe: '#e5e1d8', neck: 'crew', build: .95, h: .98 } },
  animator: { '80s': { jacket: '#c4a385', jhi: '#e3c7a8', shirt: '#f2ece0', pants: '#4a4a52', shoe: '#3a2a20', neck: 'collar', cuff: '#f2ece0', build: .9, h: .95, rolled: true } },
};
const DIM = { upper: 29, fore: 26.5, thigh: 46, shin: 44, shoulderW: 18, hipW: 9.5 };

function rig(who, era, P) {
  const Cl = CLOTH[who][era]; const k = Cl.h; const b = Cl.build;
  const pel = P.pelvis;
  const Fp = P.orient ? { o: pel, L: P.orient.L, U: P.orient.U, F: P.orient.F } : frame(pel, P.yaw || 0, 0, (P.tilt || 0) * .4);
  let Fc = frot(Fp, Fp.U, P.twist || 0);
  Fc = frot(Fc, Fc.L, P.lean || 0); Fc = frot(Fc, Fc.F, P.tilt || 0);
  const lumbar = fx(Fp, 0, 11 * k, 0);
  Fc = { ...Fc, o: add(lumbar, mul(Fc.U, 27 * k)) }; // chest centre
  let Fh = frot(Fc, Fc.U, (P.head?.yaw) || 0); Fh = frot(Fh, Fh.L, -(P.head?.pitch || 0)); Fh = frot(Fh, Fh.F, P.head?.roll || 0);
  const neckBase = fx(Fc, 0, 14 * k, -.5);
  const neckTop = add(neckBase, add(mul(Fh.U, 7.5 * k), mul(Fh.F, .8)));
  const HS = 1.2; const headC = add(neckTop, add(mul(Fh.U, 11.5 * k * HS), mul(Fh.F, 1.6 * HS)));
  const sh = s => fx(Fc, s * DIM.shoulderW * b, 9.5 * k, -1);
  const arm = (s, A) => {
    const S = sh(s); const tgt = A?.p || fx(Fc, s * 21 * b, -50 * k, 3);
    const pole = A?.pole || add(add(mul(Fc.L, s * .7), mul(Fc.F, -.7)), mul(Fc.U, -.2));
    const [E, Wr] = ik3(S, tgt, DIM.upper * k, DIM.fore * k, pole);
    // hand frame
    let fwd = norm(sub(Wr, E));
    let nrm, th;
    if (A?.dirs) { fwd = norm(A.dirs.fwd); nrm = norm(A.dirs.nrm); }
    else {
      let n0 = mul(Fc.L, s); n0 = norm(sub(n0, mul(fwd, dot(n0, fwd)))); if (len(n0) < .1) n0 = norm(cross(fwd, Fc.U));
      nrm = rotAxis(n0, fwd, (A?.roll || 0) * -s);
      if (A?.flex) { const ax = norm(cross(fwd, nrm)); fwd = rotAxis(fwd, ax, A.flex); nrm = rotAxis(nrm, ax, A.flex); }
    }
    nrm = norm(sub(nrm, mul(fwd, dot(nrm, fwd))));
    th = mul(norm(cross(nrm, fwd)), s < 0 ? 1 : -1);
    return { S, E, W: Wr, fwd, nrm, th, side: s, pose: A?.pose || { curl: .3, spread: .15, thumb: { curl: .3, out: .2, opp: .2 } } };
  };
  const leg = (s, Fv) => {
    const Hp = fx(Fp, s * DIM.hipW * b, -3, 0); const tgt = Fv || fx(Fp, s * 11 * b, -(DIM.thigh + DIM.shin) * k + 2, 0);
    const pole = add(Fp.F, mul(Fp.L, s * .25));
    const [K, A] = ik3(Hp, tgt, DIM.thigh * k, DIM.shin * k, pole); return { H: Hp, K, A, s };
  };
  return { HS, who, era, Cl, k, b, Fp, Fc, Fh, neckBase, neckTop, headC, arms: { l: arm(1, P.hl), r: arm(-1, P.hr) }, legs: { l: leg(1, P.fl), r: leg(-1, P.fr) }, P };
}
// 3D two-bone IK with pole vector
function ik3(S, T, a, b, pole) {
  let d = sub(T, S); let L = len(d); const Lc = clamp(L, Math.abs(a - b) + .1, a + b - .05); const dir = norm(d);
  const Tc = add(S, mul(dir, Lc));
  const cosA = clamp((a * a + Lc * Lc - b * b) / (2 * a * Lc), -1, 1); const sinA = Math.sqrt(1 - cosA * cosA);
  let pv = sub(pole, mul(dir, dot(pole, dir))); if (len(pv) < 1e-4) pv = norm(cross(dir, [0, 0, 1])); pv = norm(pv);
  const E = add(S, add(mul(dir, a * cosA), mul(pv, a * sinA)));
  return [E, Tc];
}

// ---------- drawing ----------
function torsoSil(cam, R) {
  const { Fp, Fc, k, b } = R; const Cl = R.Cl; const th = Cl.leather ? 1.2 : .8;
  const H = [-9, -2, 8, 16, 26, 36, 43, 47.5, 50.5];
  const A = [17.6, 16.8, 15.2, 15.0, 16.2, 17.6, 19.4, 18.4, 11.5].map(x => x * b + th);
  const Bd = [11.2, 10.6, 10.0, 10.2, 11.0, 11.6, 10.8, 9.2, 7.5].map(x => x * b + th * .7);
  const slices = H.map((h, i) => {
    const hk = h * k; let c, L, F;
    if (hk <= 11 * k) { c = fx(Fp, 0, hk, 0); L = Fp.L; F = Fp.F; }
    else { c = add(Fc.o, mul(Fc.U, hk - 38 * k)); L = Fc.L; F = Fc.F; }
    const pts = []; for (let j = 0; j < 28; j++) { const a = j / 28 * C.TAU; pts.push(add(c, add(mul(L, Math.sin(a) * A[i]), mul(F, Math.cos(a) * Bd[i])))); }
    return { c, L, F, pts: pts.map(p => cam.p(p)), a: A[i], b: Bd[i], h };
  });
  const top = cam.p(R.neckBase), bot = cam.p(fx(Fp, 0, -9 * k, 0));
  let sx = top.x - bot.x, sy = top.y - bot.y; const sl = Math.hypot(sx, sy) || 1; const px = -sy / sl, py = sx / sl;
  const Lf = [], Rt = [];
  slices.forEach(sl => { let mn = 1e9, mx = -1e9, pm, pM; sl.pts.forEach(q => { const d = q.x * px + q.y * py; if (d < mn) { mn = d; pm = q; } if (d > mx) { mx = d; pM = q; } }); Lf.push([pm.x, pm.y]); Rt.push([pM.x, pM.y]); });
  // shoulder rounding: add a top cap point
  const capT = cam.p(add(slices[slices.length - 1].c, mul(Fc.U, 2)));
  return { poly: Lf.concat([[capT.x, capT.y]], Rt.reverse()), slices };
}
function frontLine(cam, R, s, slices) { // jacket opening edge
  const out = [];
  slices.forEach((sl, i) => { if (sl.h < -8 || sl.h > 48) return; const t = clamp((sl.h + 8) / 56); const ang = s * lerp(.12, .55, t * t); const p = add(sl.c, add(mul(sl.L, Math.sin(ang) * sl.a), mul(sl.F, Math.cos(ang) * sl.b + .3))); const q = cam.p(p); out.push([q.x, q.y]); });
  return out;
}

function drawRig(g, cam, R, opt = {}) {
  const Cl = R.Cl; const items = []; const P = R.P;
  const toCam = cam.toCam(R.Fc.o); const frontVis = dot(R.Fc.F, toCam);
  const pz = p => cam.p(p).z;
  const torsoZ = pz(R.Fc.o);
  const lw = opt.lw;
  // legs
  if (!opt.noLegs) for (const s of ['l', 'r']) {
    const Lg = R.legs[s]; const q = [Lg.H, Lg.K, Lg.A].map(p => cam.p(p));
    items.push({
      z: q[1].z + 4, draw: () => {
        const R2 = [8.0 * R.b, 6.2 * R.b, 4.9 * R.b];
        I.shape(g, I.tubePts(q.map(p => [p.x, p.y]), q.map((p, i) => R2[i] * p.s), true, false, 4), { fill: Cl.pants, lw, seed: 300 + (s === 'l' ? 1 : 2), shade: q[1].s * 4 });
        const fwdF = norm(sub(fdir(R.Fp, 0, 0, 1), mul([0, 1, 0], 0)));
        const heel = add(Lg.A, add(mul(fwdF, -4), [0, -6.5, 0])), toe = add(Lg.A, add(mul(fwdF, 15), [0, -7.5, 0]));
        const hq = cam.p(heel), tq = cam.p(toe);
        I.shape(g, I.tubePts([[hq.x, hq.y], [tq.x, tq.y]], [4.6 * hq.s, 4.1 * tq.s], true, true, 3), { fill: Cl.shoe, lw, seed: 310 + (s === 'l' ? 1 : 2), shade: hq.s * 2 });
      }
    });
  }
  // torso
  const TS = torsoSil(cam, R);
  items.push({
    z: torsoZ, draw: () => {
      I.shape(g, TS.poly, {
        fill: Cl.jacket, lw, seed: 320, shade: cam.p(R.Fc.o).s * 7, hi: Cl.leather ? [Cl.jhi, cam.p(R.Fc.o).s * 1.4] : null, after: (g2) => {
          if (frontVis > -.15) {
            const Lx = frontLine(cam, R, 1, TS.slices), Rx = frontLine(cam, R, -1, TS.slices);
            const shirt = Lx.concat(Rx.slice().reverse());
            if (Cl.sweater) { // sweater: stripes across chest
              g2.save(); g2.strokeStyle = I.ST.mode === 'color' ? Cl.stripes : I.ST.graphite; g2.globalAlpha = I.ST.mode === 'color' ? 1 : .4; g2.lineWidth = cam.p(R.Fc.o).s * 2.2;
              for (const h of [30, 36]) { const sl = TS.slices.find(s => s.h >= h) || TS.slices[5]; const pts = []; for (let j = -6; j <= 6; j++) { const a = j / 6 * 1.4; const q = cam.p(add(add(R.Fc.o, mul(R.Fc.U, (h - 38) * R.k)), add(mul(R.Fc.L, Math.sin(a) * sl.a), mul(R.Fc.F, Math.cos(a) * sl.b)))); pts.push([q.x, q.y]); } g2.beginPath(); I.smoothPath(g2, pts, false); g2.stroke(); }
              g2.restore();
            } else {
              I.shape(g2, shirt, {
                fill: Cl.shirt, lw: (lw ?? I.ST.inkW) * .8, seed: 330, shade: cam.p(R.Fc.o).s * 3, after: Cl.stripes ? (g3, pp, bb) => { g3.strokeStyle = I.ST.mode === 'color' ? Cl.stripes : I.ST.graphite; g3.lineWidth = Math.max(1, (bb[3] - bb[1]) / 34); g3.globalAlpha = .9; for (let y = bb[1]; y < bb[3]; y += (bb[3] - bb[1]) / 14) { g3.beginPath(); g3.moveTo(bb[0] - 4, y); g3.lineTo(bb[2] + 4, y + 2); g3.stroke(); } } : null
              });
              if (Cl.tie) { const a = cam.p(fx(R.Fc, 0, 11 * R.k, 11 * R.b)), b2 = cam.p(fx(R.Fc, 0, -14 * R.k, 11.6 * R.b)); I.shape(g2, I.tubePts([[a.x, a.y], [b2.x, b2.y]], [1.2 * a.s, 2.4 * b2.s], false, true, 3), { fill: Cl.tie, lw: (lw ?? I.ST.inkW) * .7, seed: 340 }); }
              I.brush(g2, Lx, (lw ?? I.ST.inkW) * 1.1, { seed: 341 }); I.brush(g2, Rx, (lw ?? I.ST.inkW) * 1.1, { seed: 342 });
              // lapel fold lines
              const lap = s => { const L0 = frontLine(cam, R, s, TS.slices); const n = L0.length; const p0 = L0[n - 1], p1 = L0[Math.max(0, n - 4)]; const o = cam.p(fx(R.Fc, s * 9 * R.b, 4 * R.k, 9 * R.b)); return [p0, [o.x, o.y], p1]; };
              if (!Cl.leather) { I.brush(g2, lap(1), (lw ?? I.ST.inkW) * .8, { seed: 343, alpha: .8 }); I.brush(g2, lap(-1), (lw ?? I.ST.inkW) * .8, { seed: 344, alpha: .8 }); }
              else { const z1 = cam.p(fx(R.Fc, 3 * R.b, 2 * R.k, 11.2 * R.b)), z2 = cam.p(fx(R.Fc, 2.4 * R.b, -26 * R.k, 11.6 * R.b)); I.brush(g2, [[z1.x, z1.y], [z2.x, z2.y]], (lw ?? I.ST.inkW) * .7, { color: '#8d8d9c', alpha: .8, seed: 345 }); }
            }
          } else {
            const a = cam.p(fx(R.Fc, 0, 8 * R.k, -11 * R.b)), b2 = cam.p(fx(R.Fp, 0, -6 * R.k, -11 * R.b)); I.brush(g2, [[a.x, a.y], [b2.x, b2.y]], (lw ?? I.ST.inkW) * .6, { alpha: .45, seed: 346 });
          }
          // waist crease / hem
          const hem = []; for (let j = -5; j <= 5; j++) { const a = j / 5 * 1.3; const q = cam.p(add(fx(R.Fp, 0, -8.5 * R.k, 0), add(mul(R.Fp.L, Math.sin(a) * 17.4 * R.b), mul(R.Fp.F, Math.cos(a) * 11 * R.b)))); hem.push([q.x, q.y]); }
          I.brush(g2, hem, (lw ?? I.ST.inkW) * .7, { alpha: .5, seed: 347 });
        }
      });
    }
  });
  // neck & head
  const hz = pz(R.headC);
  items.push({
    z: Math.min(hz, torsoZ) - 1, draw: () => {
      const a = cam.p(R.neckBase), b2 = cam.p(R.neckTop);
      I.shape(g, I.tubePts([[a.x, a.y], [b2.x, b2.y]], [5.4 * a.s, 5.0 * b2.s], false, false, 2), { fill: Hd.DES[R.who][R.era].skin, lw, seed: 350, shade: a.s * 2 });
      if (frontVis > -.2) {
        if (Cl.neck === 'collar') for (const s of [-1, 1]) { const p0 = cam.p(fx(R.Fc, s * 6 * R.b, 14.5 * R.k, 4)), p1 = cam.p(fx(R.Fc, s * 1.2, 9.5 * R.k, 8.5 * R.b)), p2 = cam.p(fx(R.Fc, s * 7.5 * R.b, 11 * R.k, 5)); I.shape(g, [[p0.x, p0.y], [p1.x, p1.y], [p2.x, p2.y]], { fill: Cl.shirt, lw: (lw ?? I.ST.inkW) * .8, smooth: false, seed: 351 + s }); }
        else { const pts = []; for (let j = -5; j <= 5; j++) { const an = j / 5 * 1.25; const q = cam.p(add(fx(R.Fc, 0, 13.2 * R.k, 0), add(mul(R.Fc.L, Math.sin(an) * 6.4), mul(R.Fc.F, Math.cos(an) * 5.6)))); pts.push([q.x, q.y]); } I.brush(g, pts, (lw ?? I.ST.inkW) * (Cl.neck === 'open' ? .6 : 1.0), { seed: 352 }); }
      }
      if (!opt.noHead) Hd.drawHead(g, cam, R.headC, R.Fh, R.who, R.era, P.head?.E || {}, { lightK: opt.lightK, scale: R.HS });
    }
  });
  // arms & hands
  for (const s of ['l', 'r']) {
    const A = R.arms[s]; if (opt.hide && opt.hide[s]) continue;
    const q = [A.S, A.E, A.W].map(p => cam.p(p));
    const behind = (q[1].z > torsoZ + 5 && q[2].z > torsoZ + 2);
    const az = behind ? torsoZ + 8 : Math.min(q[1].z, q[2].z, torsoZ) - 2;
    items.push({
      z: az, draw: () => {
        const R2 = [6.4 * R.b, 5.1 * R.b, 4.3 * R.b];
        I.shape(g, I.tubePts(q.map(p => [p.x, p.y]), q.map((p, i) => R2[i] * p.s), true, false, 5), { fill: Cl.jacket, lw, seed: 360 + (s === 'l' ? 1 : 2), shade: q[1].s * 3.5, hi: Cl.leather ? [Cl.jhi, q[1].s * 1.0] : null });
        if (Cl.cuff && !Cl.rolled) { const c0 = cam.p(add(A.W, mul(norm(sub(A.W, A.E)), -1.4))), c1 = cam.p(add(A.W, mul(norm(sub(A.W, A.E)), .1))); I.shape(g, I.tubePts([[c0.x, c0.y], [c1.x, c1.y]], [3.9 * c0.s, 3.7 * c1.s], false, false, 2), { fill: Cl.cuff, lw, seed: 365 }); }
        const hand = Hn.buildHand({ w: A.W, fwd: A.fwd, nrm: A.nrm, th: A.th, scale: .95 * R.k, side: A.side }, A.pose);
        A.hand = hand;
        if (!opt.noHands) Hn.drawHand(g, cam, hand, { skin: Hd.DES[R.who][R.era].skin, lw });
      }
    });
  }
  if (opt.props) opt.props.forEach(p => items.push(p));
  items.sort((a, b) => b.z - a.z);
  items.forEach(it => it.draw(g));
  return R;
}
// convenient: build+draw
function person(g, cam, who, era, P, opt) { const R = rig(who, era, P); drawRig(g, cam, R, opt); return R; }
// default standing pose helper: place feet under pelvis
function stand(pelvis, yaw, k = 1) { const F = frame(pelvis, yaw); return { pelvis, yaw, fl: fx(F, 11, -91.5 * k, 1), fr: fx(F, -11, -91.5 * k, -1) }; }

module.exports = { rig, drawRig, person, stand, ik3, CLOTH, DIM };
