// props: toon-shaded mesh renderer + textured quads + the film's props
const C = require('./core');
const I = require('./ink');
const { add, sub, mul, dot, cross, norm, len, fx, fdir, frame, frot, rotAxis, clamp, lerp } = C;

let LIGHT = norm([-.45, .8, .45]); // world direction toward key light
function setLight(v) { LIGHT = norm(v); }
// ---------- faces ----------
function faceNormal(P) { return norm(cross(sub(P[1], P[0]), sub(P[2], P[0]))); }
function shadeCol(col, n, o = {}) {
  if (o.emit) return col;
  const k = dot(n, LIGHT);
  if (I.ST.mode !== 'color') return col;
  if (k > .35) return o.hi && k > .8 ? I.mix(col, '#ffffff', .12) : col;
  if (k > -.05) return I.mix(col, I.shadowOf(col, 1), .55);
  return I.shadowOf(col, 1.05);
}
// draw a list of faces (each {P:[world], col, emit, noInk, tex, twoSided}); returns nothing
function drawFaces(g, cam, faces, o = {}) {
  const vis = [];
  for (const f of faces) {
    const n = faceNormal(f.P); const c = mul(f.P.reduce((a, b) => add(a, b), [0, 0, 0]), 1 / f.P.length);
    const facing = dot(n, sub(cam.pos, c));
    if (facing <= 0 && !f.twoSided) continue;
    const Q = f.P.map(p => cam.p(p)); const z = Q.reduce((a, q) => a + q.z, 0) / Q.length;
    vis.push({ f, n: facing > 0 ? n : mul(n, -1), Q, z });
  }
  vis.sort((a, b) => b.z - a.z);
  const lw = (o.lw ?? I.ST.inkW) * .8;
  for (const v of vis) {
    const pts = v.Q.map(q => [q.x, q.y]);
    if (v.f.tex) { texPoly(g, v.f.tex, pts, v.f.uv); }
    else if (I.ST.mode === 'color') {
      g.fillStyle = shadeCol(v.f.col, v.n, v.f); g.beginPath(); I.poly(g, pts); g.fill();
    } else { g.fillStyle = I.mix(I.ST.paper, '#c8c2b6', clamp((.55 - I.lum(v.f.col)) * .5, 0, .35)); g.beginPath(); I.poly(g, pts); g.fill(); if (dot(v.n, LIGHT) < 0) { g.save(); g.beginPath(); I.poly(g, pts); g.clip(); I.hatchRect(g, I.bbox(pts), 7, -.85, 3, .45); g.restore(); } }
    if (!v.f.noInk && lw > 0) {
      if (I.ST.mode === 'color') { g.strokeStyle = v.f.inkCol || I.ST.ink; g.lineWidth = v.f.lw ?? lw; g.lineJoin = 'round'; g.beginPath(); I.poly(g, pts); g.stroke(); }
      else I.pencilLine(g, pts, false, 7, true, 1.2);
    }
  }
}
// map an image onto a projected quad/poly (two-triangle affine, fan)
function texPoly(g, img, pts, uv) {
  uv = uv || [[0, 0], [img.width, 0], [img.width, img.height], [0, img.height]];
  for (let i = 1; i < pts.length - 1; i++) tri(g, img, [pts[0], pts[i], pts[i + 1]], [uv[0], uv[i], uv[i + 1]]);
}
function tri(g, img, d, s) {
  const [x0, y0] = d[0], [x1, y1] = d[1], [x2, y2] = d[2]; const [u0, v0] = s[0], [u1, v1] = s[1], [u2, v2] = s[2];
  const den = (u1 - u0) * (v2 - v0) - (u2 - u0) * (v1 - v0); if (Math.abs(den) < 1e-9) return;
  const a = ((x1 - x0) * (v2 - v0) - (x2 - x0) * (v1 - v0)) / den, b = ((y1 - y0) * (v2 - v0) - (y2 - y0) * (v1 - v0)) / den;
  const c = ((x2 - x0) * (u1 - u0) - (x1 - x0) * (u2 - u0)) / den, d2 = ((y2 - y0) * (u1 - u0) - (y1 - y0) * (u2 - u0)) / den;
  const e = x0 - a * u0 - c * v0, f = y0 - b * u0 - d2 * v0;
  // expand triangle slightly to hide seams
  const cx = (x0 + x1 + x2) / 3, cy = (y0 + y1 + y2) / 3; const ex = p => [p[0] + (p[0] - cx) * .02 + Math.sign(p[0] - cx) * .6, p[1] + (p[1] - cy) * .02 + Math.sign(p[1] - cy) * .6];
  const D = d.map(ex);
  g.save(); g.beginPath(); g.moveTo(D[0][0], D[0][1]); g.lineTo(D[1][0], D[1][1]); g.lineTo(D[2][0], D[2][1]); g.closePath(); g.clip();
  g.transform(a, b, c, d2, e, f); g.drawImage(img, 0, 0); g.restore();
}
// ---------- primitives ----------
function box(fr, hl, hu, hf, col, o = {}) {
  const p = (a, b, c) => fx(fr, a * hl, b * hu, c * hf);
  const F = (P, k) => { const tx = o.tex && o.tex[k]; return { P, col: (o.cols && o.cols[k]) || col, emit: o.emit, noInk: o.noInk, tex: tx, uv: (o.uv && o.uv[k]) || (tx ? [[0, tx.height], [tx.width, tx.height], [tx.width, 0], [0, 0]] : null), lw: o.lw }; };
  return [
    F([p(-1, -1, 1), p(1, -1, 1), p(1, 1, 1), p(-1, 1, 1)], 'f'), F([p(1, -1, -1), p(-1, -1, -1), p(-1, 1, -1), p(1, 1, -1)], 'b'),
    F([p(-1, 1, 1), p(1, 1, 1), p(1, 1, -1), p(-1, 1, -1)], 'u'), F([p(-1, -1, -1), p(1, -1, -1), p(1, -1, 1), p(-1, -1, 1)], 'd'),
    F([p(1, -1, 1), p(1, -1, -1), p(1, 1, -1), p(1, 1, 1)], 'l'), F([p(-1, -1, -1), p(-1, -1, 1), p(-1, 1, 1), p(-1, 1, -1)], 'r'),
  ];
}
function cyl(fr, r, h, n, col, o = {}) { // axis along fr.U, base at fr.o
  const F = []; const ring = (y, rr) => Array.from({ length: n }, (_, i) => { const a = i / n * C.TAU; return fx(fr, Math.cos(a) * rr, y, Math.sin(a) * rr); });
  const A = ring(0, r), B = ring(h, o.r2 ?? r);
  for (let i = 0; i < n; i++) { const j = (i + 1) % n; F.push({ P: [A[i], A[j], B[j], B[i]], col, noInk: true, emit: o.emit }); }
  F.push({ P: B.slice().reverse(), col: o.cap || col, emit: o.emit }); F.push({ P: A.slice(), col: o.cap || col, emit: o.emit });
  return F;
}
// silhouette ink for an object (outline of its projected points' hull)
function outline(g, cam, pts3, lw) { const P = pts3.map(p => { const q = cam.p(p); return [q.x, q.y]; }); const H = require('./hand').hull(P); I.brush(g, H.concat([H[0]]), lw ?? I.ST.inkW * 1.2, { t0: .01, t1: .01, min: .8 }); }

// ---------- textures ----------
const TEX = {};
function texCanvas(name, w, h, fn) { if (!TEX[name]) { const c = C.createCanvas(w, h); fn(c.getContext('2d'), w, h); TEX[name] = c; } return TEX[name]; }
// the single's sleeve (original typographic design)
function sleeveTex(variant = 0) {
  return texCanvas('sleeve' + variant, 600, 600, (g, w, h) => {
    g.fillStyle = '#efe7d6'; g.fillRect(0, 0, w, h);
    // pencil-portrait motif: three loose sketched heads
    g.strokeStyle = '#3a3640'; g.lineCap = 'round'; const r = C.rng(11 + variant);
    for (let k = 0; k < 3; k++) { const cx = 150 + k * 150, cy = 300; for (let j = 0; j < 3; j++) { g.lineWidth = 2.2 - j * .5; g.globalAlpha = .75; g.beginPath(); g.ellipse(cx + (r() - .5) * 6, cy + (r() - .5) * 6, 46, 58, 0, 0, 7); g.stroke(); } g.beginPath(); g.moveTo(cx - 70, 430); g.quadraticCurveTo(cx, 360, cx + 70, 430); g.stroke(); }
    g.globalAlpha = 1;
    g.fillStyle = '#b33c3c'; g.fillRect(0, 0, w, 120);
    g.fillStyle = '#fff4e2'; g.font = '92px CapXB'; g.textBaseline = 'alphabetic'; g.fillText('a-ha', 34, 96);
    g.font = '46px CapBold'; g.textAlign = 'right'; g.fillText('Take On Me', w - 30, 92);
    g.fillStyle = '#2b2730'; g.font = '30px CapSemi'; g.textAlign = 'left'; g.fillText('7" single', 34, h - 34);
    g.strokeStyle = 'rgba(80,60,40,.25)'; g.lineWidth = 3; g.strokeRect(6, 6, w - 12, h - 12);
  });
}
function paperTex(name, w, h, fn) { return texCanvas(name, w, h, (g) => { g.fillStyle = '#f5f0e4'; g.fillRect(0, 0, w, h); const r = C.rng(3); g.fillStyle = 'rgba(120,100,70,.05)'; for (let i = 0; i < w * h / 300; i++) g.fillRect(r() * w, r() * h, 1 + r() * 2, 1 + r() * 2); if (fn) fn(g, w, h); }); }

// ---------- specific props ----------
// synth keyboard: origin fr at front-centre of keybed top; returns {faces, keyPos(i)->world top centre, white count}
const BLACK = [1, 3, 6, 8, 10];
function synth(fr, nOct = 3, o = {}) {
  const WW = 2.35, WL = 14, nW = nOct * 7 + 1; const width = nW * WW; const faces = [];
  const body = o.body || '#2a2a31';
  faces.push(...box(frot({ ...fr, o: fx(fr, 0, -4, -9) }, fr.U, 0), width / 2 + 4, 4, 13, body));
  faces.push(...box({ ...fr, o: fx(fr, 0, 1.8, -21) }, width / 2 + 4, 2.6, 6, I.mix(body, '#000000', .2), { cols: { u: '#34343c' } }));
  const press = o.press || {}; // midi -> depth 0..1
  const lo = o.lowMidi ?? 60; const keyWorld = {};
  let wi = 0;
  for (let m = lo; wi < nW; m++) {
    const pc = ((m % 12) + 12) % 12;
    if (BLACK.includes(pc)) continue;
    const x = -width / 2 + (wi + .5) * WW; const d = (press[m] || 0) * .55;
    const kf = frot({ ...fr, o: fx(fr, x, -.8 - d, -WL / 2 + .2) }, fr.L, d * .06);
    faces.push(...box(kf, WW / 2 - .06, .8, WL / 2, press[m] ? (o.pressCol || '#f3efe6') : '#f7f4ec', { lw: .9, cols: { u: '#fbf9f3' } }));
    keyWorld[m] = fx(fr, x, -d, -4.0); wi++;
  }
  // black keys
  wi = 0;
  for (let m = lo; wi < nW; m++) {
    const pc = ((m % 12) + 12) % 12;
    if (BLACK.includes(pc)) { const x = -width / 2 + wi * WW; const d = (press[m] || 0) * .5; faces.push(...box({ ...fr, o: fx(fr, x, .45 - d, -WL + 4.6) }, .62, .75, 4.4, '#18181c', { lw: .8, cols: { u: '#2a2a30' } })); keyWorld[m] = fx(fr, x, 1.2 - d, -WL + 3.2); }
    else wi++;
  }
  // panel: knobs & leds
  for (let i = 0; i < 9; i++) faces.push(...cyl({ ...fr, o: fx(fr, -width / 2 + 6 + i * 4.2, 4.4, -21) }, .9, .9, 8, '#d8d8de', { cap: '#c9c9d0' }));
  for (let i = 0; i < 6; i++) faces.push(...box({ ...fr, o: fx(fr, width / 2 - 20 + i * 3, 4.45, -19.5) }, .55, .2, .4, i % 2 ? '#ff5a4e' : '#61f0c2', { emit: true, noInk: true }));
  return { faces, keyWorld, width };
}
// hard keyboard case (lid hinged at back), open 0..1; fr at case front-bottom centre
function keyCase(fr, w, open, col = '#3b3330', o = {}) {
  const faces = []; const D = 34, Hh = 7;
  // base tray (open top)
  faces.push(...box({ ...fr, o: fx(fr, 0, Hh / 2, -D / 2) }, w / 2, Hh / 2, D / 2, col, { cols: { u: '#191719' }, lw: 1.2 }));
  // lid
  const hinge = fx(fr, 0, Hh, -D); const ang = -open * 1.9;
  let lf = { o: hinge, L: fr.L, U: fr.U, F: fr.F }; lf = frot(lf, fr.L, ang);
  faces.push(...box({ ...lf, o: fx(lf, 0, 2.4, D / 2) }, w / 2, 2.4, D / 2, I.mix(col, '#ffffff', .06), { cols: { d: '#5a2a2e' }, lw: 1.2 }));
  // handle on lid front edge
  const hp = fx(lf, 0, 2.4, D + .2);
  faces.push(...box({ ...lf, o: add(hp, mul(lf.F, 1.2)) }, 8, 1.1, 1.2, '#161616', { lw: 1 }));
  return { faces, hinge, lid: lf };
}
function guitarFaces(fr, col = '#c23a2c') { // fr: body centre, U along neck, F out of top
  const faces = []; const outline = [];
  for (let i = 0; i < 36; i++) { const a = i / 36 * C.TAU; const r = 1 + .18 * Math.cos(2 * a) - .1 * Math.cos(a); const x = Math.cos(a) * 17 * r, y = Math.sin(a) * 21 * (1 + .1 * Math.sin(a)); outline.push([x, y - 4]); }
  const top = outline.map(([x, y]) => fx(fr, x, y, 2.5)), bot = outline.map(([x, y]) => fx(fr, x, y, -2.5));
  faces.push({ P: top, col }); faces.push({ P: bot.slice().reverse(), col: I.mix(col, '#000000', .3) });
  for (let i = 0; i < outline.length; i++) { const j = (i + 1) % outline.length; faces.push({ P: [bot[i], bot[j], top[j], top[i]], col: I.mix(col, '#000000', .2), noInk: true }); }
  faces.push(...box({ ...fr, o: fx(fr, 0, 36, 2.4) }, 2.2, 22, 1.2, '#4a2e1c'));
  faces.push(...box({ ...fr, o: fx(fr, 0, 61, 2.4) }, 3.2, 4.5, 1.2, '#24170f'));
  faces.push(...box({ ...fr, o: fx(fr, 0, -6, 2.8) }, 6, 1.2, .5, '#1b1b1b', { noInk: false }));
  faces.push(...box({ ...fr, o: fx(fr, 0, 6, 2.7) }, 4.5, 1.6, .4, '#ededed'));
  return faces;
}
function guitarStrings(g, cam, fr, vib = 0, t = 0) {
  for (let s = 0; s < 6; s++) {
    const x = -1.5 + s * .6; const a = cam.p(fx(fr, x, -6, 3.2)), b = cam.p(fx(fr, x, 57, 3.6)); const m = cam.p(fx(fr, x, 20, 3.4));
    const v = vib * Math.sin(t * 90 + s) * 1.2;
    g.save(); g.strokeStyle = I.ST.mode === 'color' ? 'rgba(235,235,225,.85)' : I.ST.graphite; g.lineWidth = Math.max(.7, a.s * .12); g.beginPath(); g.moveTo(a.x, a.y); g.quadraticCurveTo(m.x + v, m.y, b.x, b.y); g.stroke(); g.restore();
  }
}
function micFaces(fr, h = 150, o = {}) { // stand base at fr.o; mic head at top angled
  const faces = [];
  faces.push(...cyl(fr, 12, 1.6, 18, '#1c1c20'));
  faces.push(...cyl({ ...fr, o: fx(fr, 0, 1.6, 0) }, .9, h - 14, 8, '#2b2b31'));
  const top = fx(fr, 0, h - 12, 0);
  let mf = frot({ ...fr, o: top }, fr.L, o.tilt ?? .5);
  faces.push(...cyl(mf, 1.3, 9, 10, '#1f1f24', { r2: 1.7 }));
  faces.push(...cyl({ ...mf, o: fx(mf, 0, 9, 0) }, 2.4, 6, 12, '#a7adb7', { cap: '#c2c7cf' }));
  return { faces, head: fx(mf, 0, 12, 0), clip: fx(mf, 0, 4, 0) };
}
function handMicFaces(fr) { const f = []; f.push(...cyl(fr, 1.35, 16, 10, '#1d1d22', { r2: 1.8 })); f.push(...cyl({ ...fr, o: fx(fr, 0, 16, 0) }, 2.5, 6, 12, '#a7adb7', { cap: '#c2c7cf' })); return f; }

// reel-to-reel: fr at machine face centre (F out of face). returns faces + spindle positions
function tapeMachine(fr, o = {}) {
  const faces = [];
  faces.push(...box({ ...fr, o: fx(fr, 0, 0, -14) }, 34, 40, 14, '#4b4d55', { cols: { f: '#5a5c66' }, lw: 1.4 }));
  const sp = [fx(fr, -17, 18, 0), fx(fr, 17, 18, 0)];
  sp.forEach(p => faces.push(...cyl(frot({ ...fr, o: p }, fr.L, Math.PI / 2), 1.0, 3.2, 8, '#d5d6db')));
  // head block & buttons
  faces.push(...box({ ...fr, o: fx(fr, 0, -6, 1.2) }, 9, 3.5, 1.2, '#2a2b30'));
  for (let i = 0; i < 5; i++) faces.push(...box({ ...fr, o: fx(fr, -14 + i * 7, -26, .9) }, 2.6, 1.8, .9, i === 4 ? (o.rec ? '#ff3a30' : '#7a1f1f') : '#c8cad1', { emit: i === 4 && o.rec }));
  for (let i = 0; i < 2; i++) faces.push(...box({ ...fr, o: fx(fr, -10 + i * 20, -16, .4) }, 6, 3.2, .4, '#efe3b8', { emit: true }));
  return { faces, sp };
}
// a reel (disc) with three windows; fr: centre, F axis (face normal), rot angle around F
function reelDraw(g, cam, fr, r, rot, tape = .6, o = {}) {
  const n = 40; const ring = (rr, off) => Array.from({ length: n }, (_, i) => { const a = i / n * C.TAU; return add(fx(fr, Math.cos(a) * rr, Math.sin(a) * rr, off), [0, 0, 0]); });
  const toCam = cam.toCam(fr.o); const facing = dot(fr.F, toCam);
  const front = facing >= 0 ? 1 : -1;
  const rim = ring(r, .6 * front), rim2 = ring(r, -.6 * front);
  const P = a => a.map(p => { const q = cam.p(p); return [q.x, q.y]; });
  // edge band
  const band = P(rim2).concat(P(rim)); const H = require('./hand').hull(band);
  I.shape(g, H, { fill: '#9da1aa', lw: o.lw, seed: 701, smooth: false });
  const face = P(rim); const col = o.col || '#c9ccd3';
  I.shape(g, face, {
    fill: col, lw: o.lw, seed: 702, smooth: false, after: (g2) => {
      // tape pack
      const tp = P(ring(r * (.3 + tape * .62), .62 * front)); g2.fillStyle = I.ST.mode === 'color' ? '#3a2a22' : '#7a7670'; g2.beginPath(); I.poly(g2, tp); g2.fill();
      // windows
      for (let k = 0; k < 3; k++) {
        const a0 = rot + k * C.TAU / 3; const win = [];
        for (let i = 0; i <= 10; i++) { const a = a0 - .55 + i / 10 * 1.1; win.push(fx(fr, Math.cos(a) * r * .9, Math.sin(a) * r * .9, .64 * front)); }
        for (let i = 10; i >= 0; i--) { const a = a0 - .42 + i / 10 * .84; win.push(fx(fr, Math.cos(a) * r * .42, Math.sin(a) * r * .42, .64 * front)); }
        const wp = P(win); g2.fillStyle = o.bg || '#2a2328'; g2.beginPath(); I.poly(g2, wp); g2.fill(); g2.strokeStyle = I.ST.ink; g2.lineWidth = Math.max(1, cam.p(fr.o).s * .15); g2.stroke();
      }
      const hub = P(ring(r * .16, .7 * front)); g2.fillStyle = '#e6e7ea'; g2.beginPath(); I.poly(g2, hub); g2.fill(); g2.stroke();
      const hole = P(ring(r * .06, .72 * front)); g2.fillStyle = '#222'; g2.beginPath(); I.poly(g2, hole); g2.fill();
    }
  });
}
// record crate with lid: fr at front-bottom centre; returns faces; lid open 0..1 (hinged at back)
function crate(fr, w, d, h, open, col = '#7a5532') {
  const faces = []; const t = 1.2;
  const wall = (o2, a, b, c, k) => faces.push(...box({ ...fr, o: o2 }, a, b, c, col, { cols: { u: I.mix(col, '#ffffff', .1) }, lw: 1.3 }));
  wall(fx(fr, 0, h / 2, -t / 2), w / 2, h / 2, t / 2); wall(fx(fr, 0, h / 2, -d + t / 2), w / 2, h / 2, t / 2);
  wall(fx(fr, -w / 2 + t / 2, h / 2, -d / 2), t / 2, h / 2, d / 2); wall(fx(fr, w / 2 - t / 2, h / 2, -d / 2), t / 2, h / 2, d / 2);
  faces.push(...box({ ...fr, o: fx(fr, 0, .5, -d / 2) }, w / 2, .5, d / 2, I.mix(col, '#000000', .3)));
  // slats
  const hinge = fx(fr, 0, h, -d); let lf = { o: hinge, L: fr.L, U: fr.U, F: fr.F }; lf = frot(lf, fr.L, -open * 1.75);
  faces.push(...box({ ...lf, o: fx(lf, 0, 1, d / 2) }, w / 2 + .6, 1, d / 2 + .3, I.mix(col, '#ffffff', .05), { cols: { d: I.mix(col, '#000000', .35) }, lw: 1.3 }));
  return { faces, lid: lf, hinge };
}
module.exports = { setLight, get LIGHT() { return LIGHT; }, drawFaces, texPoly, tri, box, cyl, outline, texCanvas, sleeveTex, paperTex, synth, keyCase, guitarFaces, guitarStrings, micFaces, handMicFaces, tapeMachine, reelDraw, crate, faceNormal, TEX };
