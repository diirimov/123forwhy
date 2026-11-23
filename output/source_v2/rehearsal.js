// shared: Norway rehearsal room, fingering engine, band poses
const C = require('./core'); const I = require('./ink'); const Pr = require('./props'); const B = require('./body'); const Hn = require('./hand'); const E = require('./env'); const S = require('./scene');
const TL = require('./timeline');
const { key, clamp, lerp, inv, ss, eOut, eIn, add, sub, mul, norm, dot, cross, fx, fdir, frame, frot } = C;

// ---------- fingering: right hand over a synth, playing given note events ----------
// notes: [{t, m, v}] ; synthFr: frame of keyboard (keys top y=0 local, front edge z=0, keys toward -F)
function fingering(t, notes, synthFr, S0, o = {}) {
  const U = synthFr.U, Fp = synthFr.F; // F points toward player
  const th = mul(synthFr.L, -1); // thumb toward player's left
  const fwd = norm(add(mul(Fp, -.93), mul(U, -.36)));
  const nrm = norm(sub(U, mul(fwd, dot(U, fwd))));
  const sc = o.scale || .95;
  // find current and next note
  let i = -1; for (let k = 0; k < notes.length; k++) if (notes[k].t <= t) i = k;
  const cur = i >= 0 ? notes[i] : null, nxt = notes[i + 1] || null;
  const press = {}; let pf = -1; let depth = 0;
  // choose finger per note: keep a stable assignment by pitch relative to running centre
  const fingerFor = (m, centre) => clamp(Math.round((m - centre) / 2.2 + 1.5), 0, 3);
  const centreAt = k => { let a = 0, n = 0; for (let j = Math.max(0, k - 2); j <= Math.min(notes.length - 1, k + 2); j++) { a += notes[j].m; n++; } return n ? a / n : 82; };
  const wristFor = (k) => {
    const nt = notes[k]; const kp = S0.keyWorld[nt.m] || S0.keyWorld[nt.m + 1]; const f = fingerFor(nt.m, centreAt(k));
    const F = Hn.FING[f];
    const knuckle = add(add(kp, mul(U, 4.2)), mul(Fp, 6.2));
    return { w: sub(sub(knuckle, mul(fwd, F.f * sc)), mul(th, F.o * sc)), f };
  };
  let W;
  if (!cur) W = notes.length ? wristFor(0).w : fx(synthFr, 0, 7, 12);
  else {
    const a = wristFor(i); W = a.w; pf = a.f;
    const dt = t - cur.t; const dur = nxt ? Math.min(nxt.t - cur.t, .26) : .26;
    depth = dt < .025 ? dt / .025 : dt < dur - .05 ? 1 : clamp(1 - (dt - (dur - .05)) / .05);
    if (nxt && nxt.t - t < .09) { const b = wristFor(i + 1); W = C.lerp3(a.w, b.w, ss(1 - (nxt.t - t) / .09)); }
    press[cur.m] = depth;
  }
  // wrist lift before accents, drop on the accent
  let lift = 0; for (const n of notes) { if (n.v < 30) continue; const d = n.t - t; if (d > 0 && d < .16) lift = Math.max(lift, Math.sin((1 - d / .16) * Math.PI) * 1.8); const a = t - n.t; if (a >= 0 && a < .12) lift = Math.max(lift, -0.6 * Math.sin(a / .12 * Math.PI)); }
  W = add(W, mul(U, lift + (o.hover || 0)));
  // finger poses: hover curl, pressing finger reaches key
  const base = { f: [[.5, .55, .35], [.48, .58, .35], [.5, .6, .38], [.55, .62, .4]], spread: .25, thumb: { curl: .25, out: .35, opp: .25 } };
  const Hs = { w: W, fwd, nrm, th, scale: sc, side: -1 };
  if (pf >= 0 && depth > 0) {
    const kp = S0.keyWorld[cur.m] || S0.keyWorld[cur.m + 1];
    const y = kp[1] - depth * .5 + (1 - depth) * 1.2;
    base.f[pf] = Hn.solveDown(Hs, base, pf, y);
  }
  return { Hs, pose: base, press };
}

// ---------- the room ----------
const ROOM = { back: -330, left: -320, right: 330 };
let OUT = null;
function windowView() { // painted dusk landscape (cached)
  if (OUT) return OUT; const [c, g] = S.layer();
  const gr = g.createLinearGradient(0, 0, 0, C.H); gr.addColorStop(0, '#16224a'); gr.addColorStop(.5, '#3c5c92'); gr.addColorStop(.75, '#9fb6d6'); gr.addColorStop(1, '#d8e2ef'); g.fillStyle = gr; g.fillRect(0, 0, C.W, C.H);
  g.fillStyle = '#7f95bb'; g.beginPath(); g.moveTo(0, 1250); for (let x = 0; x <= C.W; x += 60) g.lineTo(x, 1180 - Math.abs(Math.sin(x * .004)) * 260 - Math.sin(x * .013) * 40); g.lineTo(C.W, C.H); g.lineTo(0, C.H); g.fill();
  g.fillStyle = '#e9eef7'; g.fillRect(0, 1450, C.W, 500);
  const r = C.rng(9); for (let i = 0; i < 16; i++) { const x = r() * C.W, h = 200 + r() * 260, y = 1480; g.fillStyle = '#1f3040'; g.beginPath(); g.moveTo(x, y - h); g.lineTo(x + h * .28, y); g.lineTo(x - h * .28, y); g.fill(); }
  g.fillStyle = 'rgba(255,214,150,.9)'; g.fillRect(820, 1380, 26, 22); g.fillRect(860, 1380, 26, 22);
  OUT = c; return OUT;
}
function room(g, cam, t, o = {}) {
  const wall = '#7a4e31', wall2 = '#6a4329';
  g.fillStyle = '#1a100a'; g.fillRect(0, 0, C.W, C.H);
  S.floorPlanks(g, cam, ROOM.left, ROOM.right, ROOM.back, 400, 0, '#5a3a24', 16, true);
  S.boards(g, cam, [ROOM.left, 0, ROOM.back], [ROOM.right, 0, ROOM.back], 300, wall, 26);
  S.boards(g, cam, [ROOM.left, 0, 400], [ROOM.left, 0, ROOM.back], 300, wall2, 30);
  S.boards(g, cam, [ROOM.right, 0, ROOM.back], [ROOM.right, 0, 400], 300, wall2, 30);
  // window on back wall
  const wp = [[-65, 95, ROOM.back + .5], [85, 95, ROOM.back + .5], [85, 225, ROOM.back + .5], [-65, 225, ROOM.back + .5]].map(p => cam.p(p));
  const poly = wp.map(q => [q.x, q.y]); const bb = I.bbox(poly);
  g.save(); g.beginPath(); I.poly(g, poly); g.clip(); g.drawImage(windowView(), bb[0], bb[1], bb[2] - bb[0], bb[3] - bb[1]); S.snowfall(g, t, bb, 50, 4); g.restore();
  E.lines3(g, cam, [[[10, 95, ROOM.back + 1], [10, 225, ROOM.back + 1]], [[-65, 160, ROOM.back + 1], [85, 160, ROOM.back + 1]], [[-65, 95, ROOM.back + 1], [85, 95, ROOM.back + 1]], [[-65, 225, ROOM.back + 1], [85, 225, ROOM.back + 1]], [[-65, 95, ROOM.back + 1], [-65, 225, ROOM.back + 1]], [[85, 95, ROOM.back + 1], [85, 225, ROOM.back + 1]]], '#e8dccb', 3.2, 1);
  const wc = cam.p([10, 160, ROOM.back + 5]); I.glow(g, wc.x, wc.y, 700 * wc.s / 2, '#8fb4ff', .28, 'lighter');
  // rug
  const rug = [[-200, .3, -220], [200, .3, -220], [200, .3, 60], [-200, .3, 60]]; E.quad(g, cam, rug, '#7a2e2e');
  E.quad(g, cam, [[-185, .4, -205], [185, .4, -205], [185, .4, 45], [-185, .4, 45]], '#8e3a34');
  E.lines3(g, cam, [[[-170, .5, -190], [170, .5, -190]], [[-170, .5, 30], [170, .5, 30]], [[-170, .5, -190], [-170, .5, 30]], [[170, .5, -190], [170, .5, 30]]], '#e3c58a', .5, .8);
  // standing lamp (left) and a woodstove glow
  const lb = [-250, 0, -230]; Pr.drawFaces(g, cam, [...Pr.cyl(frame(lb, 0), 1.3, 160, 8, '#2a2018'), ...Pr.cyl(frame(add(lb, [0, 152, 0]), 0), 18, 24, 14, '#f0d6a0', { r2: 11, emit: true })]);
  const lq = cam.p(add(lb, [0, 165, 0])); I.glow(g, lq.x, lq.y, 900 * lq.s / 1.8, '#ffb35c', .42, 'lighter');
}
// positions
const POS = {
  table: [-80, 0, -70], magne: [-80, 99, -110], pal: [88, 99, -128], morten0: [14, 103, -268], mic: [8, 0, -182],
};
// keyboard case + synth on a table; returns {S0 synth geom, faces}
function keySetup(t, open, o = {}) {
  const T = POS.table; const faces = [];
  faces.push(...Pr.box(frame([T[0], 73, T[2]], 0), 62, 1.8, 26, '#6a4428', { cols: { u: '#7a5032' } }));
  for (const sx of [-1, 1]) for (const sz of [-1, 1]) faces.push(...Pr.box(frame([T[0] + sx * 56, 36, T[2] + sz * 21], 0), 2, 36, 2, '#4a2e1a'));
  const cf = frame([T[0], 74.8 + (o.lift || 0), T[2] - 18], Math.PI); // case front toward player (−z)
  const kc = Pr.keyCase(cf, 100, open, '#3a3130');
  const caseFaces = kc.faces;
  const sf = frame([T[0], 74.8 + 9.5 + (o.lift || 0), T[2] - 15], Math.PI); // keys front edge near case front
  const S0 = Pr.synth(sf, 2, { press: o.press || {}, lowMidi: 72, body: '#2b2b33' });
  return { faces, caseFaces, S0, sf, kc, cf };
}
// guitar mounted on a rig (returns frame + hand targets)
function guitarOn(R, strum = 0, fret = 0) {
  const Fc = R.Fc; let U = norm(fdir(Fc, .86, .42, .18)); let Fn = norm(fdir(Fc, -.1, .05, 1)); Fn = norm(sub(Fn, mul(U, dot(Fn, U)))); const L = cross(U, Fn);
  const o = fx(Fc, -4, -27, 13);
  const gf = { o, L, U, F: Fn };
  return { gf, strumP: add(fx(gf, -4 + strum * 5, 2 + strum * 3.5, 6), [0, 0, 0]), fretP: fx(gf, 0, 40 + fret * 4, 2) };
}
module.exports = { fingering, room, ROOM, POS, keySetup, guitarOn, windowView };
