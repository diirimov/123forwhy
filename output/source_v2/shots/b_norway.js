// NORWAY rehearsal (2.26 -> 22.39)
const C = require('../core'); const I = require('../ink'); const Pr = require('../props'); const B = require('../body'); const Hn = require('../hand'); const E = require('../env'); const S = require('../scene');
const TL = require('../timeline'); const RH = require('../rehearsal');
const { key, clamp, lerp, inv, ss, eOut, eIn, add, sub, mul, norm, dot, cross, fx, fdir, frame, frot, wob, spring } = C;
const HIT = TL.snareNear(2.16), BLK = HIT + 0.1;
const NOTES = TL.RIFF;
const D = TL.D;
const MAGNE_SKIN = '#f2c8a8', PAL_SKIN = '#efc3a0';

function lightNorway() { I.ST.toLight = [-.55, -.83]; I.ST.shadowTint = '#3a2a40'; I.ST.shadeMix = .4; I.ST.rim = { color: '#a9c6ff', dir: [.35, -.94], w: 2.2, a: .55 }; Pr.setLight([-.5, .75, .45]); }
const blinkT = (t, seed) => { const per = 2.4 + C.hash(seed) * 1.6; const ph = (t + C.hash(seed + 3) * per) % per; return ph < .13 ? Math.sin(ph / .13 * Math.PI) : 0; };
const strumPhase = t => { const B8 = 0.1771; return Math.sin((t - TL.lastBeat(t)) / B8 * Math.PI); };

// ---------- poses ----------
function magnePose(t, o = {}) {
  const P = RH.POS.magne; const ks = o.ks;
  const fing = RH.fingering(t, NOTES.filter(n => n.t > (o.from ?? -1)), ks.sf, ks.S0, { scale: .95 });
  const bob = Math.sin((t - TL.lastBeat(t)) / .354 * Math.PI) * .8;
  const R = B.rig('magne', '80s', {
    pelvis: [P[0], P[1] - bob * .5, P[2]], yaw: 0, lean: .16 + (o.lean || 0),
    head: { yaw: o.headYaw ?? 0, pitch: o.headPitch ?? -.42, roll: o.headRoll ?? .04, E: { blink: blinkT(t, 4), gaze: o.gaze || [0, -.6], mouth: { smile: o.smile ?? .15, open: o.open || 0 }, brow: o.brow || { raise: .1 } } },
    hr: { p: fing.Hs.w, dirs: { fwd: fing.Hs.fwd, nrm: fing.Hs.nrm }, pose: fing.pose },
    hl: { p: fx(ks.sf, -15, 5.5 - (TL.pulse(t, .1) > .6 && Math.abs(t - TL.downNear(t)) < .1 ? 1 : 0), 13), dirs: { fwd: norm(add(mul(ks.sf.F, -.93), mul(ks.sf.U, -.36))), nrm: ks.sf.U }, pose: { f: [[.5, .55, .35], [.5, .58, .35], [.5, .6, .38], [.55, .62, .4]], spread: .25 } },
  });
  return { R, fing };
}
function palPose(t, o = {}) {
  const P = RH.POS.pal; const yaw = o.yaw ?? -1.49;
  const R0 = B.rig('pal', '80s', { pelvis: P, yaw, twist: o.twist || 0, lean: o.lean ?? .05 });
  const sp = o.strum ?? strumPhase(t);
  const G = RH.guitarOn(R0, sp, 0);
  const R = B.rig('pal', '80s', {
    pelvis: [P[0], P[1] + (o.bob ?? 0), P[2]], yaw, twist: o.twist || 0, lean: o.lean ?? .05,
    head: { yaw: o.headYaw ?? 0, pitch: o.headPitch ?? -.25, roll: o.headRoll ?? 0, E: { blink: blinkT(t, 7), gaze: o.gaze || [0, -.3], mouth: { smile: o.smile ?? 0, open: o.open || 0 }, brow: o.brow || {} } },
    hr: { p: G.strumP, roll: .6, flex: -.3, pose: { curl: [.55, .7, .75, .8], thumb: { curl: .1, opp: .9, out: .1 } } },
    hl: { p: G.fretP, dirs: { fwd: norm(add(mul(G.gf.F, -1), mul(G.gf.U, -.2))), nrm: norm(G.gf.U) }, pose: { curl: [.55, .7, .6, .5], spread: .3, thumb: { curl: .2, opp: .3 } } },
  });
  return { R, G };
}
function guitarItem(cam, G, t, vib = .6) { const gq = cam.p(G.gf.o); return { z: gq.z - 4, draw: g => { Pr.drawFaces(g, cam, Pr.guitarFaces(G.gf, '#c23a2c')); Pr.guitarStrings(g, cam, G.gf, vib, t); } }; }
function mortenPose(t, o = {}) {
  return B.rig('morten', '80s', {
    pelvis: o.pelvis, yaw: o.yaw ?? 0, lean: o.lean ?? 0, twist: o.twist || 0,
    fl: o.fl, fr: o.fr,
    head: { yaw: o.headYaw ?? 0, pitch: o.headPitch ?? 0, roll: o.headRoll ?? 0, E: { blink: o.eyesClosed ? 1 : blinkT(t, 2), gaze: o.gaze || [0, 0], mouth: o.mouth || {}, brow: o.brow || {} } },
    hl: o.hl, hr: o.hr,
  });
}
function walkTo(t, t0, t1, a, b, yaw, k = 1.03) { // simple walk: pelvis path + alternating feet
  const u = ss(inv(t0, t1, t)); const pel = C.lerp3(a, b, u); const steps = 3; const ph = inv(t0, t1, t) * steps;
  const bob = (t > t0 && t < t1) ? -Math.abs(Math.sin(ph * Math.PI)) * 2 : 0; pel[1] += bob;
  const F = frame(pel, yaw); const fw = C.norm(sub(b, a)); const st = (t > t0 && t < t1) ? Math.sin(ph * Math.PI) * 18 : 0;
  const lift = s => (t > t0 && t < t1) ? Math.max(0, Math.sin(ph * Math.PI) * s) * 7 : 0;
  return { pelvis: pel, fl: add(fx(F, 11, -91.5 * k - bob, 0), add(mul(fw, st), [0, lift(1), 0])), fr: add(fx(F, -11, -91.5 * k - bob, 0), add(mul(fw, -st), [0, lift(-1), 0])) };
}
function micSetup() { const m = Pr.micFaces(frame(RH.POS.mic, Math.PI), 158, { tilt: .55 }); return m; }

// ---------- shots ----------
// S2: the keyboard case opens (match to the closing lid)
function caseOpen(g, t) {
  lightNorway();
  const open = key(t, [[BLK, 0], [2.36, .02], [2.80, 1.0, 'out2'], [3.02, 1.62, 'in2']]) - (t > 3.02 ? Math.abs(wob(t - 3.02, 5, 11)) * .1 : 0);
  const ks = RH.keySetup(t, open);
  const lf = ks.kc.lid; const edge = s => fx(lf, s * 30, 4.6, 34.5);
  const grab = t < 2.84; const u = ss(inv(2.84, 3.7, t));
  const handAt = (s) => { if (grab) return { p: add(edge(s), mul(lf.U, 2.5)), dirs: { fwd: norm(add(lf.F, mul(lf.U, -.6))), nrm: lf.U } }; const e = add(edge(s), [0, 12, -8]); const rest = s < 0 ? fx(ks.sf, 12, 7, 13) : fx(ks.sf, -15, 7, 13); return { p: C.lerp3(e, rest, u), dirs: { fwd: norm(add(mul(ks.sf.F, -.93), mul(ks.sf.U, -.36))), nrm: ks.sf.U } }; };
  const L = handAt(1), Rr = handAt(-1);
  const lean = grab ? .38 : lerp(.38, .2, u);
  const R = B.rig('magne', '80s', { pelvis: RH.POS.magne, yaw: 0, lean, head: { pitch: -.5, E: { blink: blinkT(t, 4), gaze: [0, -.7], mouth: { smile: lerp(0, .35, u) } } },
    hl: { ...L, pose: { curl: grab ? [.6, .65, .68, .7] : .4, spread: .2, thumb: { curl: .25, opp: .5 } } }, hr: { ...Rr, pose: { curl: grab ? [.6, .65, .68, .7] : .4, spread: .2, thumb: { curl: .25, opp: .5 } } } });
  const cam = new C.Cam({ pos: key(t, [[BLK, [30, 150, -6]], [3.94, [22, 146, -14], 'io2']]), look: key(t, [[BLK, [-82, 92, -84]], [3.94, [-82, 92, -86]]]), fov: 44 });
  RH.room(g, cam, t);
  Pr.drawFaces(g, cam, ks.faces);
  B.drawRig(g, cam, R, { props: [{ z: cam.p(fx(ks.sf, 0, 0, -8)).z, draw: () => { Pr.drawFaces(g, cam, ks.S0.faces); Pr.drawFaces(g, cam, ks.caseFaces); } }] });
  I.vignette(g, .5, '20,10,5');
}
// S3: fingers find the riff
function fingersCU(g, t) {
  lightNorway(); I.ST.inkW = 3.4;
  const ks0 = RH.keySetup(t, 1.62); const f0 = RH.fingering(t, NOTES, ks0.sf, ks0.S0);
  const ks = RH.keySetup(t, 1.62, { press: f0.press });
  const look = key(t, [[3.94, [-80, 86, -80]], [6.78, [-84, 86, -79]]]);
  const cam = new C.Cam({ pos: key(t, [[3.94, [-104, 124, -44]], [6.78, [-99, 120, -50], 'io2']]), look, fov: 34 });
  RH.room(g, cam, t);
  Pr.drawFaces(g, cam, ks.faces); Pr.drawFaces(g, cam, ks.caseFaces); Pr.drawFaces(g, cam, ks.S0.faces);
  const h = Hn.buildHand(f0.Hs, f0.pose);
  Hn.drawHand(g, cam, h, { skin: MAGNE_SKIN, sleeve: { col: '#6c9dcf', r: 4.4, len: 34, cuff: '#f5f2ea' } });
  I.vignette(g, .45, '20,10,5');
}
// S4: Magne mid shot, glances toward Pål
function magneMS(g, t) {
  lightNorway();
  const ks0 = RH.keySetup(t, 1.62); const tmp = RH.fingering(t, NOTES, ks0.sf, ks0.S0); const ks = RH.keySetup(t, 1.62, { press: tmp.press });
  const look = TL.D.find(d => d > 8.1) ; // 8.20 downbeat
  const lk = ss(inv(look - .12, look + .32, t));
  const { R } = magnePose(t, { ks, headYaw: lk * .85, headPitch: lerp(-.42, -.05, lk), gaze: [lk * .6, lerp(-.6, .1, lk)], smile: lerp(.15, .7, ss(inv(look + .2, look + .7, t))), brow: { raise: lk * .4 } });
  const cam = new C.Cam({ pos: key(t, [[6.78, [-30, 152, 52]], [9.63, [-38, 150, 38], 'io2']]), look: [-80, 126, -105], fov: 40 });
  RH.room(g, cam, t);
  Pr.drawFaces(g, cam, ks.faces);
  B.drawRig(g, cam, R, { props: [{ z: cam.p(fx(ks.sf, 0, 0, -6)).z, draw: () => { Pr.drawFaces(g, cam, ks.caseFaces); Pr.drawFaces(g, cam, ks.S0.faces); } }] });
  I.vignette(g, .5, '20,10,5');
}
// S5: Pål hears it and turns toward Magne, picking hand already moving
function palTurns(g, t) {
  lightNorway();
  const hy = ss(inv(9.92, 10.42, t)), tw = ss(inv(10.15, 10.85, t)), by = ss(inv(10.4, 11.25, t));
  const yaw = lerp(2.45, -1.49, by);
  const twist = (1 - by) * tw * -1.1; const headYaw = hy * (1 - by) * -1.25 + (1 - hy) * 0;
  const sm = ss(inv(10.95, 11.4, t));
  const { R, G } = palPose(t, { yaw, twist, headYaw, headPitch: lerp(-.35, -.02, hy), gaze: [hy * -.4 * (1 - by), lerp(-.4, 0, hy)], smile: sm * .8, brow: { raise: sm * .5 } });
  const cam = new C.Cam({ pos: key(t, [[9.63, [-10, 150, 14]], [12.46, [4, 146, -2], 'io2']]), look: [86, 128, -130], fov: 38 });
  RH.room(g, cam, t);
  B.drawRig(g, cam, R, { props: [guitarItem(cam, G, t, .7)] });
  I.vignette(g, .5, '20,10,5');
}
// S6: picking hand close-up
function pickCU(g, t) {
  lightNorway(); I.ST.inkW = 3.4;
  const { R, G } = palPose(t, { headPitch: -.1, smile: .6 });
  const cam = new C.Cam({ pos: key(t, [[12.46, fx(G.gf, -34, -14, 86)], [13.89, fx(G.gf, -28, -8, 74)]]), look: fx(G.gf, -4, 16, 0), fov: 40 });
  RH.room(g, cam, t);
  B.drawRig(g, cam, R, { props: [guitarItem(cam, G, t, 1)] });
  I.vignette(g, .5, '20,10,5');
}
// S7: wide room - Morten turns from the window and walks to the mic
function wideRoom(g, t) {
  lightNorway();
  const ks0 = RH.keySetup(t, 1.62); const tmp = RH.fingering(t, NOTES, ks0.sf, ks0.S0); const ks = RH.keySetup(t, 1.62, { press: tmp.press });
  const { R: RM } = magnePose(t, { ks, headYaw: .3, headPitch: -.3, smile: .5 });
  const { R: RP, G } = palPose(t, { smile: .6, headYaw: -.1 });
  const turn = ss(inv(14.35, 15.1, t)); const myaw = lerp(Math.PI, 0.05, turn);
  const w = walkTo(t, 15.75, 16.72, RH.POS.morten0, [8, 103, -211], 0.05);
  const RMo = mortenPose(t, { pelvis: w.pelvis, yaw: myaw, fl: t > 15.7 ? w.fl : undefined, fr: t > 15.7 ? w.fr : undefined, headYaw: turn < 1 ? (1 - turn) * .5 * turn : 0, headPitch: key(t, [[14.9, 0], [15.25, .12], [15.45, -.05], [15.6, .06]]), mouth: { smile: .2 } });
  const cam = new C.Cam({ pos: key(t, [[13.89, [-6, 172, 320]], [16.72, [0, 166, 285], 'io2']]), look: [4, 116, -170], fov: 52 });
  RH.room(g, cam, t);
  const mic = micSetup();
  Pr.drawFaces(g, cam, ks.faces);
  Pr.drawFaces(g, cam, mic.faces);
  B.drawRig(g, cam, RMo);
  B.drawRig(g, cam, RM, { props: [{ z: cam.p(fx(ks.sf, 0, 0, -6)).z, draw: () => { Pr.drawFaces(g, cam, ks.caseFaces); Pr.drawFaces(g, cam, ks.S0.faces); } }] });
  B.drawRig(g, cam, RP, { props: [guitarItem(cam, G, t, .6)] });
  I.vignette(g, .5, '20,10,5');
}
// S8: Morten leans into the microphone -> vocal entrance 19.30
function mortenMic(g, t) {
  lightNorway(); I.ST.rim = { color: '#a9c6ff', dir: [.1, -1], w: 3, a: .7 };
  const V = TL.CUE.vocal;
  const breath = ss(inv(18.55, 18.95, t)) * (1 - ss(inv(19.0, 19.3, t)));
  const leanIn = ss(inv(18.95, 19.28, t));
  const sway = Math.sin(t * 2.2) * .03 * (1 - leanIn);
  const sing = t >= V ? .45 + .35 * Math.abs(Math.sin((t - V) * 7)) : 0;
  const pel = [8, 103 + breath * 1.5, -211 + leanIn * 3];
  const mic = micSetup();
  const R = mortenPose(t, { pelvis: pel, yaw: .05, lean: -.04 * breath + .12 * leanIn, headPitch: -.06 + breath * .1 - leanIn * .05, headRoll: sway, eyesClosed: t > 17.3, mouth: { open: sing + breath * .15, o: t >= V ? .3 : 0 }, brow: { raise: t >= V ? .5 : .15 },
    hr: { p: [0, 140 + breath, -193], dirs: { fwd: [0, 0, 1], nrm: [-1, 0, 0] }, pose: { curl: [.85, .9, .9, .95], thumb: { curl: .6, opp: 1 } } }, hl: { p: [30, 98, -206], roll: .3 } });
  const cam = new C.Cam({ pos: key(t, [[16.72, [32, 172, -106]], [19.55, [24, 168, -122], 'io2']]), look: [8, 163, -211], fov: 34 });
  RH.room(g, cam, t);
  B.drawRig(g, cam, R, { props: [{ z: cam.p(mic.head).z - 2, draw: () => Pr.drawFaces(g, cam, mic.faces) }] });
  I.vignette(g, .55, '20,10,5');
}
// S9: the look
function theLook(g, t) {
  lightNorway();
  const ks0 = RH.keySetup(t, 1.62); const tmp = RH.fingering(t, NOTES, ks0.sf, ks0.S0); const ks = RH.keySetup(t, 1.62, { press: tmp.press });
  const mY = key(t, [[19.55, 0], [19.85, -.75, 'io2'], [20.4, -.75], [20.7, .75, 'io2'], [21.1, .75], [21.35, 0, 'io2']]);
  const magLook = ss(inv(20.0, 20.3, t)); const palLook = ss(inv(20.75, 21.0, t));
  const { R: RM } = magnePose(t, { ks, headYaw: magLook * 1.25, headPitch: lerp(-.35, .02, magLook), gaze: [magLook * .7, 0], smile: lerp(.2, .95, magLook), brow: { raise: magLook * .5 } });
  const { R: RP, G } = palPose(t, { headYaw: lerp(0, -.75, palLook), headPitch: lerp(-.2, 0, palLook), smile: lerp(.3, .9, palLook), gaze: [-palLook * .5, 0], brow: { raise: palLook * .4 } });
  const mic = micSetup(); const V = TL.CUE.vocal; const sing = .4 + .35 * Math.abs(Math.sin((t - V) * 7));
  const RMo = mortenPose(t, { pelvis: [8, 103, -208], yaw: .05, lean: .08, headYaw: mY, headPitch: .04, mouth: { open: sing, smile: .35 }, brow: { raise: .3 }, gaze: [mY * .5, 0],
    hr: { p: [0, 140, -193], dirs: { fwd: [0, 0, 1], nrm: [-1, 0, 0] }, pose: { curl: [.85, .9, .9, .95], thumb: { curl: .6, opp: 1 } } } });
  const cam = new C.Cam({ pos: key(t, [[19.55, [-4, 236, 230]], [21.62, [0, 228, 205], 'io2']]), look: [4, 118, -160], fov: 54 });
  RH.room(g, cam, t);
  Pr.drawFaces(g, cam, ks.faces);
  B.drawRig(g, cam, RMo, { props: [{ z: cam.p(mic.head).z - 2, draw: () => Pr.drawFaces(g, cam, mic.faces) }] });
  B.drawRig(g, cam, RM, { props: [{ z: cam.p(fx(ks.sf, 0, 0, -6)).z, draw: () => { Pr.drawFaces(g, cam, ks.caseFaces); Pr.drawFaces(g, cam, ks.S0.faces); } }] });
  B.drawRig(g, cam, RP, { props: [guitarItem(cam, G, t, .6)] });
  I.vignette(g, .5, '20,10,5');
}
// S10: hand takes the case handle (match cut to London)
const CUT_LON = TL.downNear(22.39);
function handle(g, t) {
  lightNorway();
  const lift = key(t, [[21.62, 0], [22.0, 0], [CUT_LON, 14, 'in2']]);
  const ks = RH.keySetup(t, 0, { lift });
  const hp = fx(ks.kc.lid, 0, 2.4, 34 + 1.2 + 1.0);
  const grip = add(hp, [0, 4.2, -1.5]);
  const w = key(t, [[21.62, add(grip, [-18, 34, -16])], [21.92, grip, 'out2'], [CUT_LON, grip]]);
  const R = B.rig('magne', '80s', { pelvis: [RH.POS.magne[0] - 30, RH.POS.magne[1] - 4 + lift * .3, RH.POS.magne[2] + 4], yaw: .55, lean: lerp(.32, .2, inv(22, CUT_LON, t)), head: { pitch: -.5, E: { blink: blinkT(t, 4), gaze: [0, -.6], mouth: { smile: .3 } } },
    hl: { p: w, dirs: { fwd: [.15, -.45, 1], nrm: norm([0, .95, .4]) }, pose: { curl: t > 21.92 ? [1.0, 1.05, 1.05, 1.1] : .35, spread: .15, thumb: { curl: .5, opp: .8 } } }, hr: { p: fx(frame([RH.POS.magne[0] - 34, 99, -108], -.35), -20, -48, 4) } });
  const cam = new C.Cam({ pos: key(t, [[21.62, [22, 122, -205]], [CUT_LON, [20, 128, -205]]]), look: key(t, [[21.62, [-80, 90, -92]], [CUT_LON, [-80, 98, -92]]]), fov: 38 });
  RH.room(g, cam, t);
  Pr.drawFaces(g, cam, ks.faces);
  B.drawRig(g, cam, R, { props: [{ z: cam.p(ks.cf.o).z, draw: () => Pr.drawFaces(g, cam, ks.caseFaces) }] });
  I.vignette(g, .5, '20,10,5');
}

const d = D; const at = t => TL.downNear(t);
module.exports = [
  { t0: BLK, t1: at(3.94), name: 'case', draw: caseOpen },
  { t0: at(3.94), t1: at(6.78), name: 'fingers', draw: fingersCU },
  { t0: at(6.78), t1: at(9.63), name: 'magne', draw: magneMS },
  { t0: at(9.63), t1: at(12.46), name: 'palturn', draw: palTurns },
  { t0: at(12.46), t1: at(13.89), name: 'pick', draw: pickCU },
  { t0: at(13.89), t1: at(16.72), name: 'room', draw: wideRoom },
  { t0: at(16.72), t1: at(19.55), name: 'mic', draw: mortenMic },
  { t0: at(19.55), t1: 21.62, name: 'look', draw: theLook },
  { t0: 21.62, t1: CUT_LON, name: 'handle', draw: handle },
];
