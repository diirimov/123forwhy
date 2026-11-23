// head: slice-based 2.5D head (turns from front to profile), features, hair; designs for the three musicians at two ages
const C = require('./core');
const I = require('./ink');
const { clamp, lerp, PI, dot, noise, hash } = C;

// ---------- design tables (cm, head-local; y up, z forward) ----------
const FACE = {
  narrow: { y: [-12.6, -11.4, -9.6, -7.5, -5.2, -3, -1, 1, 3, 5, 7, 9, 10.8, 12.2], a: [2.0, 3.4, 4.7, 5.6, 6.25, 6.8, 7.15, 7.35, 7.4, 7.3, 6.9, 5.9, 4.3, 1.8], b: [3.4, 5.2, 6.6, 7.6, 8.3, 8.7, 8.9, 9.1, 9.2, 9.1, 8.7, 7.7, 5.9, 3.0] },
  round: { y: [-12.2, -11.0, -9.4, -7.4, -5.2, -3, -1, 1, 3, 5, 7, 9, 10.8, 12.2], a: [2.6, 4.2, 5.4, 6.3, 6.9, 7.3, 7.5, 7.6, 7.6, 7.5, 7.1, 6.1, 4.5, 1.8], b: [3.6, 5.4, 6.8, 7.8, 8.4, 8.8, 9.0, 9.1, 9.2, 9.1, 8.7, 7.7, 5.9, 3.0] },
  oval: { y: [-12.8, -11.5, -9.6, -7.5, -5.2, -3, -1, 1, 3, 5, 7, 9, 10.8, 12.3], a: [2.3, 3.7, 5.0, 5.9, 6.5, 6.9, 7.2, 7.3, 7.35, 7.25, 6.85, 5.9, 4.3, 1.8], b: [3.4, 5.2, 6.6, 7.6, 8.3, 8.7, 8.9, 9.1, 9.2, 9.1, 8.7, 7.7, 5.9, 3.0] },
};
// front protrusion along the centre line
const PROF = {
  narrow: { y: [-12.6, -11.2, -9.6, -8.2, -7.1, -6.2, -5.2, -4.4, -3.2, -1.2, 0.6, 2.6, 4.5, 8], e: [0.1, 0.7, 0.2, 0.8, 0.55, 0.85, 0.5, 2.35, 2.0, 1.1, 0.25, 0.75, 0.35, 0] },
  round: { y: [-12.2, -11, -9.4, -8.1, -7.1, -6.2, -5.2, -4.4, -3.2, -1.2, 0.6, 2.6, 4.5, 8], e: [0.1, 0.6, 0.2, 0.75, 0.5, 0.8, 0.5, 2.0, 1.7, 0.9, 0.2, 0.55, 0.3, 0] },
  oval: { y: [-12.8, -11.4, -9.6, -8.2, -7.1, -6.2, -5.2, -4.4, -3.2, -1.2, 0.6, 2.6, 4.5, 8], e: [0.1, 0.6, 0.2, 0.75, 0.5, 0.8, 0.5, 2.15, 1.85, 1.0, 0.2, 0.6, 0.3, 0] },
};
function tab(T, key, y) { const Y = T.y, A = T[key]; if (y <= Y[0]) return A[0]; for (let i = 1; i < Y.length; i++) if (y <= Y[i]) { const t = (y - Y[i - 1]) / (Y[i] - Y[i - 1]); const u = t * t * (3 - 2 * t); return lerp(A[i - 1], A[i], u * .5 + t * .5); } return A[A.length - 1]; }

// hairline (front hairline / hair bottom) as function of theta, plus hair thickness etc.
const HAIR = {
  quiff: { // Morten 80s: tall swept-up volume, short sides, ears free
    hl: th => { const a = Math.abs(th); return a < .55 ? 6.4 + a * .6 : a < 1.0 ? lerp(6.7, 5.0, (a - .55) / .45) : a < 1.45 ? lerp(5.0, 2.2, (a - 1) / .45) : a < 1.9 ? lerp(2.2, 1.2, (a - 1.45) / .45) : lerp(1.2, -8.5, (a - 1.9) / (PI - 1.9)); },
    thick: (y, th) => 0.55 + clamp((y - 6) / 6) * 3.2 * (Math.cos(th) * .35 + .65) + (Math.abs(th) > 1.7 ? .6 : 0),
    top: 18.2, dzTop: 1.7, flow: 'sweepUp', bump: { amp: .35, n: 9, top: true },
  },
  short: { // Morten later: shorter, swept back
    hl: th => { const a = Math.abs(th); return a < .55 ? 7.2 + a * .3 : a < 1.0 ? lerp(7.4, 5.2, (a - .55) / .45) : a < 1.5 ? lerp(5.2, 2.0, (a - 1) / .5) : a < 1.9 ? lerp(2.0, 1.0, (a - 1.5) / .4) : lerp(1.0, -8.0, (a - 1.9) / (PI - 1.9)); },
    thick: (y, th) => 0.45 + clamp((y - 6) / 6) * 1.3, top: 13.8, dzTop: .6, flow: 'sweepBack', bump: { amp: .12, n: 12, top: true },
  },
  spiky: { // Magne 80s: feathered spiky top, fringe spikes, sides over upper ears
    hl: th => { const a = Math.abs(th); return a < .5 ? 5.4 - Math.abs(Math.sin(th * 9)) * .9 : a < 1.0 ? lerp(5.0, 3.6, (a - .5) / .5) : a < 1.5 ? lerp(3.6, 1.2, (a - 1) / .5) : a < 1.9 ? lerp(1.2, .2, (a - 1.5) / .4) : lerp(.2, -6, (a - 1.9) / (PI - 1.9)); },
    thick: (y, th) => 0.9 + clamp((y - 5) / 7) * 2.4, top: 16.6, dzTop: .8, flow: 'spikes', bump: { amp: 1.7, n: 14, top: true, spike: true },
  },
  spikyShort: {
    hl: th => { const a = Math.abs(th); return a < .5 ? 6.4 - Math.abs(Math.sin(th * 8)) * .5 : a < 1.0 ? lerp(6.2, 4.4, (a - .5) / .5) : a < 1.5 ? lerp(4.4, 1.6, (a - 1) / .5) : a < 1.9 ? lerp(1.6, .6, (a - 1.5) / .4) : lerp(.6, -5, (a - 1.9) / (PI - 1.9)); },
    thick: (y, th) => 0.6 + clamp((y - 6) / 6) * 1.4, top: 14.6, dzTop: .5, flow: 'spikes', bump: { amp: 1.0, n: 10, top: true, spike: true },
  },
  curly: { // Pål 80s: curly mop over the ears, fringe to the brows
    hl: th => { const a = Math.abs(th); return a < .45 ? 3.9 - Math.cos(th * 7) * .35 : a < 1.0 ? lerp(3.9, 1.2, (a - .45) / .55) : a < 1.4 ? lerp(1.2, -6.0, (a - 1.0) / .4) : lerp(-6.0, -8.2, (a - 1.4) / (PI - 1.4)); },
    thick: (y, th) => 1.9 + clamp((y - 2) / 9) * 1.6 + (y < 0 ? 1.0 : 0), top: 16.2, dzTop: .4, flow: 'curls', bump: { amp: .85, n: 15 },
  },
  curlyShort: {
    hl: th => { const a = Math.abs(th); return a < .45 ? 5.0 - Math.cos(th * 7) * .3 : a < 1.0 ? lerp(5.0, 3.0, (a - .45) / .55) : a < 1.5 ? lerp(3.0, 0.8, (a - 1) / .5) : a < 1.9 ? lerp(.8, .2, (a - 1.5) / .4) : lerp(.2, -5.2, (a - 1.9) / (PI - 1.9)); },
    thick: (y, th) => 1.1 + clamp((y - 4) / 8) * 1.2, top: 14.8, dzTop: .3, flow: 'curls', bump: { amp: .45, n: 16 },
  },
  pony: { // teenager: long hair tied back
    hl: th => { const a = Math.abs(th); return a < .5 ? 6.2 : a < 1.2 ? lerp(6.2, 2.0, (a - .5) / .7) : a < 1.7 ? lerp(2.0, -2.0, (a - 1.2) / .5) : lerp(-2, -7, (a - 1.7) / (PI - 1.7)); },
    thick: (y, th) => 0.6 + clamp((y - 6) / 6) * .9, top: 13.6, dzTop: 0, flow: 'sweepBack', bump: { amp: .1, n: 12 },
  },
  crop: { // generic short crop
    hl: th => { const a = Math.abs(th); return a < .6 ? 6.8 : a < 1.4 ? lerp(6.8, 2.2, (a - .6) / .8) : a < 1.9 ? lerp(2.2, 1.0, (a - 1.4) / .5) : lerp(1.0, -5.0, (a - 1.9) / (PI - 1.9)); },
    thick: (y, th) => 0.5 + clamp((y - 6) / 6) * .8, top: 13.4, dzTop: .3, flow: 'sweepBack', bump: { amp: .2, n: 14 },
  },
};

const SKIN = '#efc4a2';
const DES = {
  morten: {
    '80s': { face: 'narrow', hair: 'quiff', hairC: '#26170f', hairHi: '#6a4430', brow: '#22140d', iris: '#6c8ea8', lips: '#c88576', skin: SKIN, cheek: true, browW: 1.0 },
    late: { face: 'narrow', hair: 'short', hairC: '#3d3029', hairHi: '#9a8a80', brow: '#2e221c', iris: '#6c8ea8', lips: '#c4857a', skin: '#ecbf9f', cheek: true, age: 1, stubble: .25, browW: 1.0 },
  },
  magne: {
    '80s': { face: 'round', hair: 'spiky', hairC: '#dcb35c', hairHi: '#fbe5a4', brow: '#a57a37', iris: '#6f8f68', lips: '#cf8a7a', skin: '#f2c8a8', browW: .85 },
    late: { face: 'round', hair: 'spikyShort', hairC: '#b7a173', hairHi: '#e4d6b2', brow: '#8c7046', iris: '#6f8f68', lips: '#c98a7c', skin: '#eec2a2', glasses: '#1c1c22', age: 1, stubble: .15, browW: .85 },
  },
  pal: {
    '80s': { face: 'oval', hair: 'curly', hairC: '#5e3720', hairHi: '#9a6643', brow: '#2f1b10', iris: '#5a3c26', lips: '#c98377', skin: '#efc3a0', browW: 1.15 },
    late: { face: 'oval', hair: 'curlyShort', hairC: '#5c4a3e', hairHi: '#9c8b7c', brow: '#3a2a20', iris: '#5a3c26', lips: '#c4857a', skin: '#ebbe9c', age: 1, stubble: .35, browW: 1.1 },
  },
  teen: { '80s': { face: 'round', hair: 'pony', hairC: '#3a2418', hairHi: '#7a5236', brow: '#3a2418', iris: '#4f6a86', lips: '#d68c80', skin: '#f3cdb0', browW: .75, lashes: true } },
  fan: { '80s': { face: 'oval', hair: 'crop', hairC: '#1f1a18', hairHi: '#55463e', brow: '#1f1a18', iris: '#4a3626', lips: '#b9776a', skin: '#c99273', browW: .95 } },
  animator: { '80s': { face: 'oval', hair: 'pony', hairC: '#7a3c22', hairHi: '#b8704a', brow: '#5a2a16', iris: '#4b6a5a', lips: '#cf8476', skin: '#f2cbb0', browW: .8, lashes: true } },
};

// ---------- projection helpers ----------
function headOrient(cam, c, fr) {
  const P = cam.p(c);
  const F = fr.F, U = fr.U;
  const fx = dot(F, cam.r), fy = dot(F, cam.u), fz = dot(F, cam.f);
  // also account for view direction (perspective): direction from camera to head
  const vd = C.norm(C.sub(c, cam.pos)); const vx = dot(vd, cam.r), vy = dot(vd, cam.u);
  const yaw = Math.atan2(fx - vx * -fz * 0, -fz) - Math.atan2(vx, 1) * 0.9;
  const pitch = Math.asin(clamp(fy, -1, 1)) - Math.asin(clamp(vy, -1, 1)) * .9;
  const ux = dot(U, cam.r), uy = dot(U, cam.u);
  const roll = Math.atan2(ux, uy);
  return { P, yaw, pitch, roll, s: P.s };
}
function mkXf(o) { const cr = Math.cos(o.roll), sr = Math.sin(o.roll); return (X, Y) => [o.P.x + o.s * (X * cr + Y * sr), o.P.y + o.s * (X * sr - Y * cr)]; }

function surf(F, Pf, th, y, off, yaw, pitch, eK = 1) {
  const a = tab(F, 'a', y) + off, b = tab(F, 'b', y) + off;
  const e = tab(Pf, 'e', y) * Math.exp(-Math.pow(th / (y < -3.5 && y > -5.6 ? .16 : .24), 2)) * eK;
  const x = a * Math.sin(th), z = b * Math.cos(th) + e;
  const X = x * Math.cos(yaw) + z * Math.sin(yaw), Z0 = -x * Math.sin(yaw) + z * Math.cos(yaw);
  const Y = y * Math.cos(pitch) + Z0 * Math.sin(pitch), Z = Z0 * Math.cos(pitch) - y * Math.sin(pitch);
  return [X, Y, Z];
}

// silhouette of a surface family between y0..y1, optional theta filter
function silhouette(F, Pf, yaw, pitch, y0, y1, off, filter, dzFn, eK = 1) {
  const R = [], Lf = []; const N = 128;
  for (let y = y1; y >= y0; y -= .4) {
    let mn = 1e9, mx = -1e9, ymn = 0, ymx = 0, ok = false;
    for (let i = 0; i < N; i++) {
      const th = -PI + i / N * 2 * PI; if (filter && !filter(th, y)) continue;
      const o = typeof off === 'function' ? off(y, th) : off;
      let p = surf(F, Pf, th, y, o, yaw, pitch, eK);
      if (dzFn) { const dz = dzFn(y); p = [p[0] + dz * Math.sin(yaw), p[1] + dz * Math.sin(pitch), p[2]]; }
      ok = true; if (p[0] < mn) { mn = p[0]; ymn = p[1]; } if (p[0] > mx) { mx = p[0]; ymx = p[1]; }
    }
    if (ok) { R.push([mx, ymx]); Lf.push([mn, ymn]); }
  }
  const out = R.concat(Lf.reverse());
  return smoothPoly(smoothPoly(out));
}
function smoothPoly(P) { const n = P.length; return P.map((p, i) => { const a = P[(i - 1 + n) % n], b = P[(i + 1) % n]; return [(a[0] + 2 * p[0] + b[0]) / 4, (a[1] + 2 * p[1] + b[1]) / 4]; }); }
// hair outer surface point
function hairSurf(F, Hs, th, y, yaw, pitch, k = 1) {
  const yc = 10.5; const top = Hs.top;
  let a, b;
  if (y <= yc) { a = tab(F, 'a', y) + Hs.thick(y, th) * k; b = tab(F, 'b', y) + Hs.thick(y, th) * k; }
  else { const a0 = tab(F, 'a', yc) + Hs.thick(yc, th) * k, b0 = tab(F, 'b', yc) + Hs.thick(yc, th) * k; const u = clamp((y - yc) / (top - yc)); const r = Math.sqrt(Math.max(0, 1 - u * u)); a = a0 * r; b = b0 * r; }
  const dz = Hs.dzTop * clamp((y - 7) / (top - 7));
  const x = a * Math.sin(th), z = b * Math.cos(th) + dz;
  const X = x * Math.cos(yaw) + z * Math.sin(yaw), Z0 = -x * Math.sin(yaw) + z * Math.cos(yaw);
  return [X, y * Math.cos(pitch) + Z0 * Math.sin(pitch), Z0 * Math.cos(pitch) - y * Math.sin(pitch)];
}
function hairSilhouette(F, Hs, yaw, pitch) {
  const R = [], Lf = []; const N = 128;
  for (let y = Hs.top - .02; y >= -9; y -= .4) {
    let mn = 1e9, mx = -1e9, ymn = 0, ymx = 0, ok = false;
    for (let i = 0; i < N; i++) { const th = -PI + i / N * 2 * PI; if (y < Hs.hl(th) - .2) continue; const p = hairSurf(F, Hs, th, y, yaw, pitch); ok = true; if (p[0] < mn) { mn = p[0]; ymn = p[1]; } if (p[0] > mx) { mx = p[0]; ymx = p[1]; } }
    if (ok) { R.push([mx, ymx]); Lf.push([mn, ymn]); }
  }
  return smoothPoly(smoothPoly(R.concat(Lf.reverse())));
}
function modulate(P, amp, n, topOnly, spike, seed) { // push polygon outward with bumps
  const m = P.length; let cx = 0, cy = 0; P.forEach(p => { cx += p[0]; cy += p[1]; }); cx /= m; cy /= m;
  let per = 0; const acc = [0]; for (let i = 1; i < m; i++) { per += Math.hypot(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1]); acc.push(per); }
  return P.map((p, i) => {
    const dx = p[0] - cx, dy = p[1] - cy, l = Math.hypot(dx, dy) || 1; const u = acc[i] / per;
    let k = spike ? Math.pow(Math.max(0, Math.sin(u * n * PI * 2 + seed)), 6) : Math.abs(Math.sin(u * n * PI + seed));
    if (topOnly) k *= clamp((p[1] - 3) / 6);
    return [p[0] + dx / l * amp * k, p[1] + dy / l * amp * k];
  });
}

// ---------- draw head ----------
// E: {blink, gaze:[x,y], brow:{raise, frown}, mouth:{open, smile, wide, o}, squint}
function drawHead(g, cam, c, fr, who, era, E = {}, opts = {}) {
  const D = DES[who][era]; const F = FACE[D.face], Pf = PROF[D.face], Hs = HAIR[D.hair];
  const o = headOrient(cam, c, fr); o.s *= (opts.scale || 1); const yaw = clamp(o.yaw, -3.1, 3.1), pitch = clamp(o.pitch, -.5, .5);
  const X = mkXf(o); const sc = o.s; const lwF = Math.max(1.6, Math.min(7, sc * .32));
  const T = (p) => X(p[0], p[1]);
  const seed = { morten: 10, magne: 40, pal: 70, teen: 100, fan: 130, animator: 160 }[who] || 1;
  const back = Math.abs(yaw) > PI / 2;
  // hair volume (behind face)
  const hairFilter = (th, y) => y >= Hs.hl(th) - .2;
  const dzFn = y => Hs.dzTop * clamp((y - 8) / (Hs.top - 8));
  let hairSil = hairSilhouette(F, Hs, yaw, pitch);
  if (Hs.bump) hairSil = modulate(hairSil, Hs.bump.amp, Hs.bump.n, Hs.bump.top, Hs.bump.spike, seed);
  const hairScr = hairSil.map(T);
  const hairCol = D.hairC;
  if (back) { // full skull + jaw in skin under the hair, so the head joins the neck
    const skull = silhouette(F, Pf, yaw, pitch, -12.6, 12.2, 0, null, null).map(T);
    I.shape(g, skull, { fill: D.skin, lw: lwF, seed: seed + 3, shade: sc * 1.8 });
  }
  I.shape(g, hairScr, { fill: hairCol, lw: lwF * (back ? .55 : 1.25), seed: seed + 1, shade: back ? 2 : sc * 1.6, shadowK: back ? .4 : 1, hi: [D.hairHi, sc * .5] });
  if (back) {
    for (const s of [-1, 1]) { const th = s * PI / 2; const p = surf(F, Pf, th, -0.6, 0, yaw, pitch); if (Math.cos(th + yaw) > -0.75 && Hs.hl(th) > -1) { const pts = I.ellipsePts(0, 0, 1.3, 2.7, 0, 16).map(([x, y]) => X(p[0] + x * .6 + Math.sign(p[0]) * .5, p[1] + y)); I.shape(g, pts, { fill: D.skin, lw: lwF * .8, seed: seed + 5 + s }); } }
    const r = C.rng(seed + 3); const col = I.ST.mode === 'color' ? I.mix(D.hairC, '#000000', .45) : null;
    for (let i = 0; i < 9; i++) { const th = PI + (-0.9 + i * .22) * (yaw > 0 ? 1 : 1); const pts = []; for (let k = 0; k < 5; k++) { const y = Hs.top - 2 - k * (Hs.top + 3) / 5; if (y < Hs.hl(th)) break; pts.push(hairSurf(F, Hs, th + (r() - .5) * .05, y, yaw, pitch, .95)); } const vis = pts.filter(p => p[2] > 0); if (vis.length > 1) I.brush(g, vis.map(p => X(p[0], p[1])), Math.max(1, sc * .22), { color: i % 3 ? col : D.hairHi, seed: seed + i }); }
    return o;
  }
  // ears
  const earSide = s => { const p = surf(F, Pf, s * PI / 2, -0.8, 0, yaw, pitch); return { p, vis: Math.sin(s * PI / 2 + yaw) * 0 + (Math.cos(yaw) * 0 + (-Math.sin(yaw) * s)) > -0.75 }; };
  const ears = [-1, 1].map(s => { const th = s * PI / 2; const p = surf(F, Pf, th, -0.6, 0, yaw, pitch); const facing = Math.sin(th + yaw); return { s, p, facing: Math.cos(th + yaw) }; });
  // face
  const faceSil = silhouette(F, Pf, yaw, pitch, -12.6, 12.2, 0, null, null);
  const faceScr = faceSil.map(T);
  const light = opts.lightK ?? 1;
  // ears behind face edge (draw before face when mostly side-on on far side)
  const drawEar = (e) => {
    const vis = e.facing > -0.35; if (!vis) return;
    const w = 1.1 + 1.7 * clamp(Math.abs(Math.sin(e.s * PI / 2 + yaw)) * 0 + clamp(1 - Math.abs(e.facing) * 0.9 + 0.1)), h = 5.4;
    const ex = e.p[0] + Math.sign(e.p[0] || e.s) * (0.7 * clamp(Math.abs(Math.cos(yaw)))), ey = e.p[1] - .2;
    const pts = I.ellipsePts(0, 0, w * .55 + .5, h / 2, 0, 18).map(([x, y]) => X(ex + x + (x > 0 ? .25 : 0) * Math.sign(e.s), ey + y * (y < 0 ? .85 : 1)));
    I.shape(g, pts, { fill: D.skin, lw: lwF * .85, seed: seed + 5 + e.s, shade: sc * .7 });
    I.brush(g, [X(ex + .2 * e.s, ey + 1.6), X(ex + .55 * e.s, ey + .2), X(ex + .2 * e.s, ey - 1.4)], lwF * .7, { seed: seed + 9 });
  };
  ears.forEach(e => { if (e.facing < 0.15) drawEar(e); });
  I.shape(g, faceScr, {
    fill: D.skin, lw: lwF, seed: seed + 3, shade: sc * (1.4 + light * .6), after: (g2) => {
      // soft cheek warmth + under-hair shadow
      if (I.ST.mode === 'color') {
        const ch = surf(F, Pf, .62, -3.2, 0, yaw, pitch), ch2 = surf(F, Pf, -.62, -3.2, 0, yaw, pitch);
        for (const p of [ch, ch2]) if (p[2] > 0) { const q = X(p[0], p[1]); I.glow(g2, q[0], q[1], sc * 3.2, '#e08a7a', .18, 'source-over'); }
        const hp = []; for (let th = -1.6; th <= 1.6; th += .2) { const y = Hs.hl(th); const p = surf(F, Pf, th, y - .8, .05, yaw, pitch); if (p[2] > -1) hp.push(X(p[0], p[1])); }
        if (hp.length > 2) { g2.save(); g2.strokeStyle = I.rgba('#6b3a3a', .22); g2.lineWidth = sc * 1.6; g2.lineCap = 'round'; g2.beginPath(); I.smoothPath(g2, hp, false); g2.stroke(); g2.restore(); }
      }
    }
  });
  ears.forEach(e => { if (e.facing >= 0.15) drawEar(e); });
  features(g, D, F, Pf, yaw, pitch, X, sc, lwF, E, seed, who);
  // front hair: region above the visible hairline, clipped to hair silhouette
  const vis = []; for (let th = -PI; th <= PI; th += .05) { const p = surf(F, Pf, th, Hs.hl(th), .1, yaw, pitch); if (p[2] > 0.25) vis.push([th, p]); }
  // keep the longest contiguous run
  if (vis.length > 1) { let best = [], cur = [vis[0]]; for (let i = 1; i < vis.length; i++) { if (vis[i][0] - vis[i - 1][0] < .08) cur.push(vis[i]); else { if (cur.length > best.length) best = cur; cur = [vis[i]]; } } if (cur.length > best.length) best = cur; vis.length = 0; vis.push(...best); }
  if (vis.length > 1) {
    const hl = vis.map(v => X(v[1][0], v[1][1]));
    const top = X(0, -60);
    const dn = (p) => [p[0] + (top[0] - X(0, 0)[0]) * 1.5, p[1] + (top[1] - X(0, 0)[1]) * 1.5];
    const faceArea = [dn(hl[0]), ...hl, dn(hl[hl.length - 1])];
    g.save(); I.clipOutside(g, faceArea, false); g.beginPath(); I.smoothPath(g, hairScr, true); g.clip();
    I.shape(g, hairScr, { fill: hairCol, noInk: true, seed: seed + 1, shade: sc * 1.6, hi: [D.hairHi, sc * .5] });
    hairStrands(g, D, Hs, yaw, pitch, X, sc, seed, false, F, Pf);
    g.restore();
    I.brush(g, hl, lwF * 1.0, { seed: seed + 12, t0: .12, t1: .12, min: .5 });
  }
  if (D.glasses) glasses(g, D, F, Pf, yaw, pitch, X, sc, lwF);
  return o;
}

function hairStrands(g, D, Hs, yaw, pitch, X, sc, seed, back, F, Pf) {
  F = F || FACE.narrow; Pf = Pf || PROF.narrow;
  const col = I.ST.mode === 'color' ? I.mix(D.hairC, '#000000', .45) : null;
  const hi = D.hairHi; const w = Math.max(1, sc * .2);
  const ok = p => p[2] > 0;
  const curve = (pts, ww, c) => { const vis = pts.filter(ok); if (vis.length < 2) return; I.brush(g, vis.map(p => X(p[0], p[1])), ww, { color: c, seed: seed + vis.length, t0: .3, t1: .45 }); };
  const r = C.rng(seed);
  if (Hs.flow === 'sweepUp' || Hs.flow === 'sweepBack') {
    for (let i = 0; i < 11; i++) {
      const th0 = -1.2 + i * .24 + (r() - .5) * .1; const y0 = Hs.hl(th0) + .3; const pts = [];
      for (let k = 0; k < 6; k++) { const th = th0 * (1 - k * .06) + (Hs.flow === 'sweepUp' ? .05 * k : 0); const y = y0 + k * (Hs.top - y0) * .17; pts.push(hairSurf(F, Hs, th, Math.min(y, Hs.top - 1), yaw, pitch, .92)); }
      curve(pts, w * (i % 3 === 0 ? 1.4 : 1), i % 3 === 1 ? hi : col);
    }
  } else if (Hs.flow === 'spikes') {
    for (let i = 0; i < 9; i++) {
      const th0 = -1.2 + i * .3 + (r() - .5) * .1; const y0 = Hs.hl(th0) + 1.5 + r() * 2; const pts = [];
      for (let k = 0; k < 3; k++) { const y = y0 + k * 1.9; pts.push(hairSurf(F, Hs, th0 * (1 + k * .08), Math.min(y, Hs.top - .6), yaw, pitch, .95)); }
      curve(pts, w * 1.1, i % 2 ? hi : col);
    }
  } else if (Hs.flow === 'curls') {
    for (let i = 0; i < 26; i++) {
      const th = -1.5 + r() * 3.0, y = lerp(Hs.hl(th) + .8, Hs.top - 1.5, r());
      const p = hairSurf(F, Hs, th, y, yaw, pitch, .9); if (!ok(p)) continue;
      const q = X(p[0], p[1]); const rr = sc * (.75 + r() * .45); const a0 = r() * 6;
      const arc = []; for (let k = 0; k < 7; k++) { const a = a0 + k / 6 * 4.2; arc.push([q[0] + Math.cos(a) * rr, q[1] + Math.sin(a) * rr]); }
      I.brush(g, arc, w * 1.1, { color: i % 3 ? col : hi, seed: seed + i });
    }
  }
}

function features(g, D, F, Pf, yaw, pitch, X, sc, lw, E, seed, who) {
  const ink = I.ST.mode === 'color' ? I.ST.ink : I.ST.graphite;
  const blink = clamp(E.blink || 0), gaze = E.gaze || [0, 0], br = E.brow || {}, mo = E.mouth || {};
  const sq = E.squint || 0;
  // ---- eyes ----
  for (const s of [-1, 1]) {
    const th = s * .41; const ey = 1.0;
    const c = surf(F, Pf, th, ey, -.25, yaw, pitch); if (c[2] < 0.6) continue;
    const fs = clamp(Math.cos(th + yaw * .95) * 1.05, .12, 1);
    const pin = surf(F, Pf, th - s * .19 * 1, ey, -.2, yaw, pitch), pout = surf(F, Pf, th + s * .21, ey + .15, -.2, yaw, pitch);
    const inner = X(pin[0], pin[1]), outer = X(pout[0], pout[1]); const ctr = X(c[0], c[1]);
    const open = (1 - blink) * (1 - sq * .45) * (1 + (br.raise || 0) * .12);
    const hU = 1.05 * open, hL = .55 * (1 - blink) * (1 - sq * .2);
    const up = (k, h) => { const p = surf(F, Pf, lerp(th - s * .19, th + s * .21, k), ey + Math.sin(k * PI) * h + k * .15, -.15, yaw, pitch); return X(p[0], p[1]); };
    const top = [0, .2, .45, .7, .9, 1].map(k => up(k, hU)), bot = [1, .75, .45, .2, 0].map(k => up(k, -hL));
    if (open > .12) {
      if (I.ST.mode === 'color') {
        g.save(); g.beginPath(); I.smoothPath(g, top.concat(bot), true); g.fillStyle = '#f7f1e8'; g.fill(); g.clip();
        const ir = .62 * sc; const gx = ctr[0] + (gaze[0] * .55 + yaw * .25) * sc * fs, gy = ctr[1] - gaze[1] * .4 * sc - .05 * sc;
        g.fillStyle = D.iris; g.beginPath(); g.ellipse(gx, gy, ir * fs * 1.05, ir, 0, 0, 7); g.fill();
        g.strokeStyle = I.mix(D.iris, '#000000', .5); g.lineWidth = Math.max(1, sc * .09); g.stroke();
        g.fillStyle = '#120c0c'; g.beginPath(); g.ellipse(gx, gy, ir * .45 * fs, ir * .45, 0, 0, 7); g.fill();
        g.fillStyle = 'rgba(255,255,255,.9)'; g.beginPath(); g.ellipse(gx + ir * .35, gy - ir * .38, ir * .18, ir * .18, 0, 0, 7); g.fill();
        g.fillStyle = 'rgba(60,30,40,.18)'; g.fillRect(gx - 3 * ir, gy - 3 * ir, 6 * ir, ir * 1.4); // lid shadow
        g.restore();
      } else {
        const ir = .6 * sc; const gx = ctr[0] + (gaze[0] * .55 + yaw * .25) * sc * fs, gy = ctr[1] - gaze[1] * .4 * sc;
        g.save(); g.beginPath(); I.smoothPath(g, top.concat(bot), true); g.clip(); g.fillStyle = '#3b3940'; g.beginPath(); g.ellipse(gx, gy, ir * fs, ir, 0, 0, 7); g.fill(); g.restore();
      }
      I.brush(g, top, lw * (1.25 + .3 * fs), { color: ink, seed: seed + 20 + s, t0: .15, t1: .3, min: .35 });
      I.brush(g, bot.slice(0, 4), lw * .55, { color: ink, seed: seed + 22 + s, t0: .4, t1: .4 });
      // lid crease
      const crease = [.15, .5, .85].map(k => up(k, hU + .75)); I.brush(g, crease, lw * .5, { color: ink, seed: seed + 24 + s, alpha: .55 });
      if (D.lashes) I.brush(g, [top[5], [top[5][0] + s * sc * .5 * fs, top[5][1] - sc * .35]], lw * .8, { color: ink });
    } else {
      I.brush(g, [0, .25, .5, .75, 1].map(k => up(k, -.25)), lw * 1.2, { color: ink, seed: seed + 26 + s });
    }
    if (D.age) { const p = X(...surf(F, Pf, th + s * .33, ey - .3, 0, yaw, pitch).slice(0, 2)); I.brush(g, [[p[0], p[1] - sc * .3], [p[0] + s * sc * .5 * fs, p[1] + sc * .1]], lw * .5, { color: ink, alpha: .5 }); }
    // brow
    const raise = (br.raise || 0) + (s < 0 ? br.l || 0 : br.r || 0), frown = br.frown || 0, worry = br.worry || 0;
    const bp = [0, .33, .66, 1].map(k => { const t = lerp(th - s * .2, th + s * .28, k); const y = 3.15 + raise * .9 + (1 - k) * (-frown * .8 + worry * .9) + Math.sin(k * PI) * .35 - k * k * .3; const p = surf(F, Pf, t, y, .05, yaw, pitch); return p[2] > 0 ? X(p[0], p[1]) : null; }).filter(Boolean);
    if (bp.length > 1) I.brush(g, bp, lw * 1.6 * (D.browW || 1), { color: I.ST.mode === 'color' ? D.brow : ink, seed: seed + 30 + s, t0: .2, t1: .55, min: .3 });
  }
  // ---- nose ----
  const sd = Math.sign(yaw || 1e-3) * -1; // side away from viewer turn
  const tip = surf(F, Pf, 0, -4.35, 0, yaw, pitch), wL = surf(F, Pf, -.2, -4.75, -.1, yaw, pitch), wR = surf(F, Pf, .2, -4.75, -.1, yaw, pitch), und = surf(F, Pf, 0, -5.05, 0, yaw, pitch);
  const bridgeA = surf(F, Pf, .07 * (I.ST.toLight[0] > 0 ? -1 : 1), .2, 0, yaw, pitch), bridgeB = surf(F, Pf, .1 * (I.ST.toLight[0] > 0 ? -1 : 1), -3.6, 0, yaw, pitch);
  if (Math.abs(yaw) < 1.25) I.brush(g, [X(bridgeA[0], bridgeA[1]), X(bridgeB[0], bridgeB[1]), X(tip[0] + (yaw > 0 ? -.2 : .2), tip[1] + .2)], lw * .65, { color: ink, seed: seed + 40, alpha: .55, t0: .5, t1: .2 });
  const np = [wL, und, wR].filter(p => p[2] > 0).map(p => X(p[0], p[1]));
  if (np.length >= 2) I.brush(g, np, lw * .9, { color: ink, seed: seed + 41, t0: .35, t1: .35 });
  // ---- mouth ----
  const smile = mo.smile || 0, open = mo.open || 0, wide = mo.wide || 0, oo = mo.o || 0;
  const my = -6.65; const hw = .36 + wide * .08 - oo * .12;
  const lipPt = (k, dy, off = 0) => { const th = lerp(-hw, hw, k); const corner = Math.pow(Math.abs(k - .5) * 2, 2); const p = surf(F, Pf, th, my + dy + corner * smile * .75 - corner * (mo.sad || 0) * .6, off, yaw, pitch); return p; };
  const topLip = [0, .2, .4, .5, .6, .8, 1].map(k => lipPt(k, open * .35 + (k > .3 && k < .7 ? .1 : 0)));
  const botLip = [1, .8, .6, .4, .2, 0].map(k => lipPt(k, -open * (1.6 + oo * .9) * Math.sin(Math.max(.15, k) * PI * .999) * (1 - Math.abs(k - .5) * .6)));
  const vis = topLip.every(p => p[2] > -0.2);
  if (open > .06 && vis) {
    const poly = topLip.concat(botLip).map(p => X(p[0], p[1]));
    if (I.ST.mode === 'color') {
      g.save(); g.beginPath(); I.smoothPath(g, poly, true); g.fillStyle = '#5a1f22'; g.fill(); g.clip();
      const t0 = X(topLip[3][0], topLip[3][1]); g.fillStyle = '#f1ebe2'; g.fillRect(t0[0] - sc * 2.5, t0[1] - sc * .1, sc * 5, sc * .55 * clamp(open * 2));
      g.fillStyle = '#c45a5f'; g.beginPath(); g.ellipse(t0[0], t0[1] + sc * open * 1.9, sc * .9, sc * .5, 0, 0, 7); g.fill(); g.restore();
    } else { g.save(); g.beginPath(); I.smoothPath(g, poly, true); g.fillStyle = '#4a474c'; g.fill(); g.restore(); }
    I.brush(g, poly.concat([poly[0]]), lw * .9, { color: ink, seed: seed + 50, t0: .05, t1: .05, min: .6 });
  } else {
    const line = [0, .25, .5, .75, 1].map(k => lipPt(k, 0)).filter(p => p[2] > 0).map(p => X(p[0], p[1]));
    if (line.length > 1) I.brush(g, line, lw * 1.05, { color: ink, seed: seed + 51, t0: .25, t1: .25 });
  }
  const ll = [.35, .5, .65].map(k => lipPt(k, -.95 - open * 1.9, 0)).filter(p => p[2] > 0).map(p => X(p[0], p[1]));
  if (ll.length > 1 && I.ST.mode === 'color') I.brush(g, ll, lw * .55, { color: I.mix(D.lips, '#3a1a1a', .4), alpha: .7, seed: seed + 52 });
  // smile lines / age
  if (D.age || smile > .5) for (const s of [-1, 1]) {
    const a = surf(F, Pf, s * .25, -4.2, 0, yaw, pitch), b = surf(F, Pf, s * .42, -7.0, 0, yaw, pitch);
    if (a[2] > 0 && b[2] > 0) I.brush(g, [X(a[0], a[1]), X(lerp(a[0], b[0], .5) + s * .25, lerp(a[1], b[1], .5)), X(b[0], b[1])], lw * .55, { color: ink, alpha: .35 + (D.age ? .2 : 0) + smile * .15, seed: seed + 60 + s });
  }
  if (D.cheek) for (const s of [-1, 1]) {
    const a = surf(F, Pf, s * .78, -2.2, 0, yaw, pitch), b = surf(F, Pf, s * .62, -5.6, 0, yaw, pitch);
    if (a[2] > 0 && b[2] > 0 && s * (I.ST.toLight[0] > 0 ? -1 : 1) > 0) I.brush(g, [X(a[0], a[1]), X(b[0], b[1])], lw * .55, { color: ink, alpha: .28, seed: seed + 70 + s });
  }
  if (D.stubble && I.ST.mode === 'color') {
    const jaw = []; for (let th = -1.2; th <= 1.2; th += .2) { const p = surf(F, Pf, th, -9 + Math.abs(th) * 3, 0, yaw, pitch); if (p[2] > 0) jaw.push(X(p[0], p[1])); }
    if (jaw.length > 2) { g.save(); g.strokeStyle = I.rgba('#5a4036', D.stubble * .5); g.lineWidth = sc * 2.6; g.lineCap = 'round'; g.beginPath(); I.smoothPath(g, jaw, false); g.stroke(); g.restore(); }
  }
}
function glasses(g, D, F, Pf, yaw, pitch, X, sc, lw) {
  for (const s of [-1, 1]) {
    const th = s * .41; const c = surf(F, Pf, th, 1.0, .9, yaw, pitch); if (c[2] < .3) continue;
    const fs = clamp(Math.cos(th + yaw), .15, 1);
    const pts = []; for (let i = 0; i < 20; i++) { const a = i / 20 * PI * 2; const p = surf(F, Pf, th + Math.cos(a) * .22 * 1.0, 1.0 + Math.sin(a) * 1.45, 1.1, yaw, pitch); pts.push(X(p[0], p[1])); }
    I.brush(g, pts.concat([pts[0]]), lw * 1.05, { color: D.glasses, t0: .02, t1: .02, min: .8, forceInk: false });
    if (I.ST.mode === 'color') { g.save(); g.globalAlpha = .12; g.fillStyle = '#cfe6ff'; g.beginPath(); I.smoothPath(g, pts, true); g.fill(); g.restore(); }
  }
  const a = surf(F, Pf, -.17, 1.3, 1.1, yaw, pitch), b = surf(F, Pf, .17, 1.3, 1.1, yaw, pitch);
  if (a[2] > 0 && b[2] > 0) I.brush(g, [X(a[0], a[1]), X(0 * a[0] + (a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + .3), X(b[0], b[1])], lw * .9, { color: D.glasses });
}

module.exports = { drawHead, DES, FACE, PROF, HAIR, SKIN, headOrient, surf, tab };
