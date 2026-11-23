// LONDON doorway + STUDIO second attempt (22.39 -> 30.91)
const C = require('../core'); const I = require('../ink'); const Pr = require('../props'); const B = require('../body'); const Hn = require('../hand'); const E = require('../env'); const S = require('../scene');
const TL = require('../timeline'); const RH = require('../rehearsal');
const { key, clamp, lerp, inv, ss, eOut, eIn, add, sub, mul, norm, dot, cross, fx, fdir, frame, frot, wob, basisFrom } = C;
const T_LON = TL.downNear(22.39), T_ST = 24.20, T_MAG = 25.90, T_STOP = 27.00, T_BACK = 28.80, T_LT = TL.downNear(30.91);
const SETTLE = TL.snareNear(29.84);
const blinkT = (t, seed) => { const per = 2.4 + C.hash(seed) * 1.6; const ph = (t + C.hash(seed + 3) * per) % per; return ph < .13 ? Math.sin(ph / .13 * Math.PI) : 0; };

// ---------------- London doorway ----------------
let STREET = null;
function streetView() {
  if (STREET) return STREET; const [c, g] = S.layer();
  const gr = g.createLinearGradient(0, 0, 0, C.H); gr.addColorStop(0, '#0c1226'); gr.addColorStop(.6, '#1e2a48'); gr.addColorStop(1, '#2a2f3c'); g.fillStyle = gr; g.fillRect(0, 0, C.W, C.H);
  // terrace silhouettes with lit windows
  g.fillStyle = '#121626'; g.fillRect(0, 420, C.W, 900); const r = C.rng(8);
  for (let i = 0; i < 7; i++) for (let j = 0; j < 3; j++) { g.fillStyle = r() < .4 ? '#f2c27a' : '#232a40'; g.fillRect(40 + i * 150, 520 + j * 230, 70, 120); }
  g.fillStyle = '#1a1c24'; g.fillRect(0, 1320, C.W, 600);
  for (let i = 0; i < 9; i++) { const x = r() * C.W; const q = g.createLinearGradient(0, 1330, 0, 1900); q.addColorStop(0, 'rgba(255,200,120,.35)'); q.addColorStop(1, 'rgba(255,200,120,0)'); g.fillStyle = q; g.fillRect(x, 1330, 30, 570); }
  const lq = g.createRadialGradient(820, 380, 0, 820, 380, 420); lq.addColorStop(0, 'rgba(255,214,150,.65)'); lq.addColorStop(1, 'rgba(255,214,150,0)'); g.fillStyle = lq; g.fillRect(0, 0, C.W, C.H);
  STREET = I.blurCanvas(c, 6); return STREET;
}
function carriedCase(handW, dirZ = -1) { // case hanging from the hand, long axis along walking direction
  const ctr = add(handW, [0, -21, 0]); const fr = { o: ctr, L: [1, 0, 0], U: [0, 1, 0], F: [0, 0, dirZ] };
  return [...Pr.box(fr, 4.8, 17, 50, '#3a3130', { lw: 1.3 }), ...Pr.box({ ...fr, o: add(handW, [0, -3, 0]) }, 1.2, 1.4, 7, '#151515')];
}
function london(g, t) {
  I.ST.toLight = [.5, -.86]; I.ST.shadowTint = '#1a2244'; I.ST.shadeMix = .5; I.ST.rim = { color: '#8fb0ff', dir: [0, -1], w: 3, a: .8 }; Pr.setLight([.3, .7, -.6]);
  const z0 = 70, z1 = -45;
  const pel = key(t, [[T_LON, [-12, 99, z0]], [T_ST, [-10, 99, z1], 'lin']]);
  const ph = (t - T_LON) * 1.9; const bob = -Math.abs(Math.sin(ph * Math.PI)) * 2; pel[1] += bob;
  const F = frame(pel, Math.PI);
  const st = Math.sin(ph * Math.PI) * 17;
  const handW = add(fx(F, 24, -45, 2 + st * .15), [0, Math.sin(ph * Math.PI * 2) * .8, 0]);
  const R = B.rig('magne', '80s', { pelvis: pel, yaw: Math.PI, lean: .06,
    fl: add(fx(F, 11, -91.5 - bob, 0), [0, Math.max(0, Math.sin(ph * Math.PI)) * 6, -st]), fr: add(fx(F, -11, -91.5 - bob, 0), [0, Math.max(0, -Math.sin(ph * Math.PI)) * 6, st]),
    head: { pitch: key(t, [[T_LON, -.25], [23.3, .05]]), yaw: key(t, [[T_LON, 0], [23.4, .25], [24.0, -.1]]), E: { blink: blinkT(t, 4), gaze: [0, 0], mouth: { smile: .1 }, brow: { raise: .2 } } },
    hl: { p: handW, dirs: { fwd: [.15, -.35, -1], nrm: norm([0, .9, -.4]) }, pose: { curl: [1.0, 1.05, 1.05, 1.1], thumb: { curl: .5, opp: .8 } } },
    hr: { p: fx(F, -22, -46 - st * .1, -st * .3) } });
  // camera: starts on the hand (same place as the Norway handle), backs away and cranes up to his face
  const cam = new C.Cam({
    pos: key(t, [[T_LON, add(handW, [-72, 14, -26])], [22.95, add(handW, [-80, 30, -60]), 'io2'], [T_ST, [8, 168, -150], 'io2']]),
    look: key(t, [[T_LON, add(handW, [4, -8, 0])], [22.95, add(handW, [10, 20, 0]), 'io2'], [T_ST, [-10, 170, -10], 'io2']]), fov: 44 });
  // interior walls + doorway onto the rainy street
  g.fillStyle = '#2a2018'; g.fillRect(0, 0, C.W, C.H);
  E.quad(g, cam, [[-400, 0, 0], [400, 0, 0], [400, 300, 0], [-400, 300, 0]], '#c9b79a');
  const dp = [[-55, 0, 0], [55, 0, 0], [55, 215, 0], [-55, 215, 0]].map(p => cam.p(p)); const poly = dp.map(q => [q.x, q.y]);
  g.save(); g.beginPath(); I.poly(g, poly); g.clip(); g.drawImage(streetView(), 0, 0);
  // the other two coming in from the rain
  const P2 = B.rig('pal', '80s', { pelvis: [30, 99, 230 - (t - T_LON) * 40], yaw: Math.PI, head: { pitch: -.2, E: { blink: 0 } } });
  const M2 = B.rig('morten', '80s', { pelvis: [-50, 102, 330 - (t - T_LON) * 40], yaw: Math.PI, head: { pitch: -.1, E: {} } });
  const save = { ...I.ST }; I.ST.shadeMix = .7; B.drawRig(g, cam, M2); B.drawRig(g, cam, P2); Object.assign(I.ST, save);
  E.lines3(g, cam, (() => { const r = C.rng(Math.floor(t * 30)); const a = []; for (let i = 0; i < 70; i++) { const x = -60 + r() * 120, z = 10 + r() * 260, y = r() * 230; a.push([[x, y, z], [x - 2, y - 26, z]]); } return a; })(), '#b9cdf5', .5, .55);
  g.restore();
  // door frame, open door, threshold
  Pr.drawFaces(g, cam, [...Pr.box(frame([-60, 110, 0], 0), 5, 110, 6, '#3d2a1c'), ...Pr.box(frame([60, 110, 0], 0), 5, 110, 6, '#3d2a1c'), ...Pr.box(frame([0, 220, 0], 0), 65, 5, 6, '#3d2a1c')]);
  Pr.drawFaces(g, cam, Pr.box({ o: [-55 - 1, 107, -50], L: [0, 0, -1], U: [0, 1, 0], F: [-1, 0, 0] }, 50, 107, 2.5, '#244a3a', { lw: 1.4 }));
  const num = cam.p([-36, 160, -97.2]);
  S.floorPlanks(g, cam, -400, 400, -400, 0, 0, '#4a3324', 14, true);
  // light pool from the corridor lamp
  const lq = cam.p([0, 250, -150]); I.glow(g, lq.x, lq.y, 900 * lq.s, '#ffcf8a', .3, 'lighter');
  B.drawRig(g, cam, R, { props: [{ z: cam.p(handW).z - 6, draw: () => Pr.drawFaces(g, cam, carriedCase(handW)) }] });
  I.vignette(g, .55, '10,10,25');
}

// ---------------- studio ----------------
const ST = { mach: [55, 150, -95], desk: 85, box: [-12, 86.2, -62], pal: [34, 99, -12], magSynth: [-118, 92, -118], couch: [-170, 0, 60] };
function machine() { const fr = frame(ST.mach, 0); return { fr, ...Pr.tapeMachine(fr, { rec: false }) }; }
function studioRoom(g, cam, t, mood = 0) {
  g.fillStyle = '#15131a'; g.fillRect(0, 0, C.W, C.H);
  const wall = I.mix('#4a4552', '#5a4a40', mood);
  E.quad(g, cam, [[-400, 0, -200], [400, 0, -200], [400, 300, -200], [-400, 300, -200]], wall);
  // acoustic panels
  const panels = []; for (let i = -3; i <= 3; i++) for (let j = 0; j < 2; j++) panels.push(...Pr.box(frame([i * 95, 150 + j * 85, -198], 0), 40, 36, 2, I.mix('#5a4f62', '#6a5544', mood), { lw: 1 }));
  Pr.drawFaces(g, cam, panels);
  S.floorPlanks(g, cam, -400, 400, -200, 300, 0, '#2c2620', 10, true);
  // desk / console
  Pr.drawFaces(g, cam, [...Pr.box(frame([-20, ST.desk / 2, -80], 0), 170, ST.desk / 2, 32, '#2e2b30', { cols: { u: '#3b373e' } })]);
  // console faders on the desk top
  const segs = []; for (let i = 0; i < 26; i++) { const x = -170 + i * 9; segs.push([[x, ST.desk + .3, -100], [x, ST.desk + .3, -70]]); }
  E.lines3(g, cam, segs, '#8a8590', .25, .7);
  // desk lamp warm pool
  const lq = cam.p([-60, 140, -120]); I.glow(g, lq.x, lq.y, 700 * lq.s, '#ffbe73', .35 + mood * .15, 'lighter');
  const cq = cam.p([80, 260, -60]); I.glow(g, cq.x, cq.y, 900 * cq.s, '#8aa8ff', .12, 'lighter');
}
// reel state over time: position, orientation basis (F = reel axis), rotation
function reelState(t, M) {
  const sp = M.sp[0]; const onSp = add(sp, [0, 0, 3.2]);
  const boxIn = add(ST.box, [0, 2.2, 0]), half = add(ST.box, [0, 15, 5]);
  const vert = { L: [1, 0, 0], U: [0, 1, 0], F: [0, 0, 1] }, flat = { L: [1, 0, 0], U: [0, 0, -1], F: [0, 1, 0] };
  const p = key(t, [[T_ST, onSp], [24.45, onSp], [24.85, add(onSp, [0, 1, 12]), 'io2'], [25.9, add(half, [0, 9, 0]), 'io2'], [26.9, add(half, [0, -2, 0]), 'out2'], [T_BACK, add(half, [0, -2, 0])], [29.25, add(onSp, [0, 4, 14]), 'io2'], [29.62, add(onSp, [0, .6, 3.5]), 'io2'], [SETTLE, onSp, 'in2']]);
  const o = C.keyOrient(t, [[24.6, vert], [25.7, flat, 'io2'], [T_BACK + .05, flat], [29.3, vert, 'io2']]);
  let rot = 0; if (t > SETTLE) { rot = C.wob(t - SETTLE, 3.2, 4.5) * .35; p[1] -= Math.abs(C.wob(t - SETTLE, 7, 14)) * .5; }
  return { p, o, rot };
}
function palStudio(t, M, rs, o = {}) {
  const grip = s => add(rs.p, add(mul(rs.o.L, s * 16.5), mul(rs.o.U, -3)));
  const onReel = t < (o.release ?? 30.0);
  const hands = s => onReel ? { p: grip(s), dirs: { fwd: norm(add(mul(rs.o.U, .55), mul(rs.o.L, -s * .5))), nrm: norm(add(mul(rs.o.L, s), mul(rs.o.F, .3))) } } : { p: fx(frame(ST.pal, Math.PI), s * 21, -48, 3) };
  return B.rig('pal', '80s', { pelvis: [ST.pal[0], ST.pal[1] - (o.crouch || 0), ST.pal[2]], yaw: Math.PI + (o.yawOff || 0), lean: o.lean ?? .12, twist: o.twist || 0,
    head: { yaw: o.headYaw || 0, pitch: o.headPitch ?? -.35, E: { blink: blinkT(t, 7), gaze: o.gaze || [0, -.5], mouth: { smile: o.smile || 0 }, brow: o.brow || { worry: .4 } } },
    hl: { ...hands(1), pose: { curl: onReel ? [.62, .66, .7, .74] : .3, spread: .1, thumb: { curl: .2, opp: .8, out: .2 } } }, hr: { ...hands(-1), pose: { curl: onReel ? [.62, .66, .7, .74] : .3, spread: .1, thumb: { curl: .2, opp: .8, out: .2 } } } });
}
function magneStudio(t, o = {}) {
  return B.rig('magne', '80s', { pelvis: [ST.magSynth[0], 99, ST.magSynth[2] - 32], yaw: .55, lean: .2, head: { yaw: o.headYaw || 0, pitch: o.headPitch ?? -.4, E: { blink: blinkT(t, 4), gaze: o.gaze || [0, -.5], mouth: { smile: o.smile || 0 } } }, hl: { p: fx(frame(ST.magSynth, .55), 12, 4, -14) }, hr: { p: fx(frame(ST.magSynth, .55), -12, 4, -14) } });
}
function mortenCouch(t, o = {}) { // slumped on the couch
  const P = [ST.couch[0], 58, ST.couch[2]]; const yaw = 1.1; const F = frame(P, yaw);
  return B.rig('morten', '80s', { pelvis: P, yaw, lean: o.lean ?? -.25, fl: fx(F, 14, -52, 44), fr: fx(F, -14, -52, 40), head: { yaw: o.headYaw || 0, pitch: o.headPitch ?? -.3, E: { blink: blinkT(t, 2), mouth: {}, brow: { worry: .3 } } }, hl: { p: fx(F, 20, -6, 22) }, hr: { p: fx(F, -22, -4, 20) } });
}
function couch(g, cam) { const F = frame(ST.couch, 1.1); Pr.drawFaces(g, cam, [...Pr.box({ ...F, o: fx(F, 0, 22, 0) }, 70, 22, 34, '#5a3a3a'), ...Pr.box({ ...F, o: fx(F, 0, 55, -28) }, 70, 32, 8, '#4e3232')]); }
function lightStudio(mood = 0) { I.ST.toLight = [-.5, -.86]; I.ST.shadowTint = mood > .5 ? '#3a2a40' : '#24284a'; I.ST.shadeMix = .45; I.ST.rim = { color: '#9fb4ff', dir: [.5, -.86], w: 2.2, a: .5 }; Pr.setLight([-.4, .8, .5]); }
function reelBox(g, cam, open = 1) {
  const fr = frame(ST.box, 0); Pr.drawFaces(g, cam, Pr.box(fr, 15.5, 1.8, 15.5, '#d8cdb2', { cols: { u: '#3a3436' }, lw: 1.2 }));
  const lf = frot({ ...fr, o: fx(fr, 0, 1.8, -15.5) }, fr.L, -1.7 * open); Pr.drawFaces(g, cam, Pr.box({ ...lf, o: fx(lf, 0, .4, 15.5) }, 15.5, .4, 15.5, '#e6dcc2', { lw: 1.2 }));
  E.lines3(g, cam, [[fx(lf, -10, .9, 22), fx(lf, 6, .9, 22)]], '#3a3030', .4, .9);
}
function drawReelOn(g, cam, rs) { Pr.reelDraw(g, cam, { o: rs.p, L: rs.o.L, U: rs.o.U, F: rs.o.F }, 13.3, rs.rot + .4, .62); }

function studioReel(g, t) { // S12: Pål boxing the reel
  lightStudio(); const M = machine(); const rs = reelState(t, M);
  const cam = new C.Cam({ pos: key(t, [[T_ST, [-140, 178, 40]], [T_MAG, [-132, 174, 28], 'io2']]), look: [22, 150, -45], fov: 50 });
  studioRoom(g, cam, t); couch(g, cam); B.drawRig(g, cam, mortenCouch(t));
  B.drawRig(g, cam, magneStudio(t));
  Pr.drawFaces(g, cam, M.faces); reelBox(g, cam);
  // right spindle keeps its reel
  Pr.reelDraw(g, cam, { o: add(M.sp[1], [0, 0, 3.2]), L: [1, 0, 0], U: [0, 1, 0], F: [0, 0, 1] }, 13.3, .9, .3);
  const R = palStudio(t, M, rs, { headPitch: -.45, lean: .18 });
  B.drawRig(g, cam, R, { props: [{ z: cam.p(rs.p).z - 1, draw: () => drawReelOn(g, cam, rs) }] });
  I.vignette(g, .55);
}
function studioKeys(g, t) { // S13: Magne plays the opening notes again
  lightStudio(); I.ST.inkW = 3.4;
  const off = TL.downNear(26.66) - TL.downNear(2.52);
  const notes = TL.RIFF.map(n => ({ ...n, t: n.t + off })).filter(n => n.t > T_MAG - .3 && n.t < 27.2);
  const sf = frame([ST.magSynth[0], ST.magSynth[1], ST.magSynth[2]], .55 + Math.PI);
  const S0a = Pr.synth(sf, 2, { lowMidi: 72 }); const f0 = RH.fingering(t, notes, sf, S0a);
  const S0 = Pr.synth(sf, 2, { lowMidi: 72, press: f0.press });
  const kc = fx(sf, 0, 0, -6);
  const cam = new C.Cam({ pos: add(kc, key(t, [[T_MAG, [20, 30, 30]], [T_STOP, [16, 27, 26]]])), look: add(kc, [-2, 2, 0]), fov: 36 });
  studioRoom(g, cam, t); Pr.drawFaces(g, cam, S0.faces);
  Hn.drawHand(g, cam, Hn.buildHand(f0.Hs, f0.pose), { skin: '#f2c8a8', sleeve: { col: '#6c9dcf', r: 4.4, len: 34, cuff: '#f5f2ea' } });
  I.vignette(g, .5);
}
function studioStop(g, t) { // S14: the hand stops halfway; rack focus to Pål's face; he looks up
  lightStudio(); const M = machine(); const rs = reelState(t, M);
  const up = ss(inv(27.8, 28.25, t)); const tremor = Math.sin(t * 31) * .15 * (1 - up);
  rs.p = add(rs.p, [tremor, 0, 0]);
  const R = palStudio(t, M, rs, { headPitch: lerp(-.45, .05, up), headYaw: up * .55, gaze: [up * .7, lerp(-.5, 0, up)], brow: { worry: .5 - up * .3, raise: up * .3 }, lean: .2 });
  const focus = ss(inv(27.35, 27.85, t)); // 0 = foreground sharp, 1 = face sharp
  const cam = new C.Cam({ pos: key(t, [[T_STOP, [-44, 112, -118]], [T_BACK, [-40, 118, -112]]]), look: key(t, [[T_STOP, [-8, 104, -52]], [T_BACK, [16, 140, -20]]]), fov: 42 });
  // background layer: room + Pål without hands
  S.drawBlurred(g, x => { studioRoom(x, cam, t); Pr.drawFaces(x, cam, M.faces); B.drawRig(x, cam, R, { noHands: true }); }, lerp(10, 1, focus));
  // foreground layer: box, reel, hands
  S.drawBlurred(g, x => { reelBox(x, cam); drawReelOn(x, cam, rs); for (const s of ['l', 'r']) { const A = R.arms[s]; Hn.drawHand(x, cam, Hn.buildHand({ w: A.W, fwd: A.fwd, nrm: A.nrm, th: A.th, scale: .95 * R.k, side: A.side }, A.pose), { skin: '#efc3a0' }); } }, lerp(1, 7, focus));
  I.vignette(g, .55);
}
function studioBack(g, t) { // S15: the reel goes back on the machine and settles
  const mood = ss(inv(29.9, 30.8, t)); lightStudio(mood);
  const M = machine(); const rs = reelState(t, M);
  const gl = ss(inv(30.1, 30.45, t)), sm = ss(inv(30.4, 30.8, t));
  const R = palStudio(t, M, rs, { headPitch: lerp(-.2, .0, gl), headYaw: gl * .9, gaze: [gl * .7, 0], smile: sm * .6, brow: { raise: gl * .3 }, release: 30.0, lean: lerp(.12, .04, gl) });
  const cam = new C.Cam({ pos: key(t, [[T_BACK, [-125, 165, 70]], [T_LT, [-112, 160, 58], 'io2']]), look: [26, 142, -45], fov: 50 });
  studioRoom(g, cam, t, mood); couch(g, cam);
  B.drawRig(g, cam, mortenCouch(t, { lean: lerp(-.25, -.05, ss(inv(30.3, 30.8, t))), headPitch: lerp(-.3, 0, ss(inv(30.3, 30.8, t))), headYaw: ss(inv(30.3, 30.8, t)) * .4 }));
  B.drawRig(g, cam, magneStudio(t, { headYaw: ss(inv(30.2, 30.6, t)) * .6, headPitch: lerp(-.4, -.05, ss(inv(30.2, 30.6, t))), smile: sm * .5 }));
  Pr.drawFaces(g, cam, M.faces); reelBox(g, cam);
  Pr.reelDraw(g, cam, { o: add(M.sp[1], [0, 0, 3.2]), L: [1, 0, 0], U: [0, 1, 0], F: [0, 0, 1] }, 13.3, .9, .3);
  B.drawRig(g, cam, R, { props: [{ z: cam.p(rs.p).z - 1, draw: () => drawReelOn(g, cam, rs) }] });
  if (t > SETTLE) { const q = cam.p(rs.p); const k = Math.exp(-(t - SETTLE) * 6); if (k > .05) I.glow(g, q.x, q.y, 260 * k, '#ffffff', .12 * k, 'lighter'); }
  I.vignette(g, .55);
}
module.exports = [
  { t0: T_LON, t1: T_ST, name: 'london', draw: london },
  { t0: T_ST, t1: T_MAG, name: 'reel', draw: studioReel },
  { t0: T_MAG, t1: T_STOP, name: 'keys2', draw: studioKeys },
  { t0: T_STOP, t1: T_BACK, name: 'stop', draw: studioStop },
  { t0: T_BACK, t1: T_LT, name: 'back', draw: studioBack },
];
