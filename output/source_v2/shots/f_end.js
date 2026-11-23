// ENDING (50.77 -> 60): 2010 the mic goes back on the stand as the lights fall; 2015 the hand takes it back; widest crowd; the look
const C = require('../core'); const I = require('../ink'); const Pr = require('../props'); const B = require('../body'); const Hn = require('../hand'); const E = require('../env'); const S = require('../scene');
const TL = require('../timeline'); const ST = require('../stage'); const RH = require('../rehearsal');
const { key, clamp, lerp, inv, ss, eOut, add, sub, mul, norm, fx, frame, frot } = C;
const T_2010 = TL.downNear(50.77), T_2015 = TL.CUE.high, T_LOOK = TL.CUE.highEnd, T_END = 60.0;
const blinkT = (t, seed) => { const per = 2.4 + C.hash(seed) * 1.6; const ph = (t + C.hash(seed + 3) * per) % per; return ph < .13 ? Math.sin(ph / .13 * Math.PI) : 0; };
const MIC = [0, 0, -42]; const STAND_H = 150;
function standFaces() { const fr = frame(MIC, Math.PI); const f = []; f.push(...Pr.cyl(fr, 12, 1.6, 18, '#1c1c20')); f.push(...Pr.cyl({ ...fr, o: fx(fr, 0, 1.6, 0) }, .9, STAND_H - 6, 8, '#2b2b31')); return f; }
const CLIP = add(MIC, [0, STAND_H, 0]);
const clipFrame = () => frot({ ...frame(CLIP, Math.PI) }, frame(CLIP, Math.PI).L, .55); // mic angled toward the singer
function micAt(pos, fwd) { const U = norm(fwd); const F = norm(C.cross(U, [1, 0, 0])); return Pr.handMicFaces({ o: pos, L: C.cross(U, F), U, F }); }
const MPEL = [6, 101, 6];
// shared framing for 2010 and 2015 (upstage, over Morten's right side, toward the mic and the audience)
const camMic = (t, t0) => new C.Cam({ pos: [150 - (t - t0) * 2, 170, 78], look: [-8, 150, -36], fov: 42 });

function y2010(g, t) {
  const lights = [51.48, 52.19, 52.90, 53.62].map(b => TL.near(b));
  let L = 1; lights.forEach((b, i) => { L -= .21 * ss(inv(b, b + .35, t)); });
  I.ST.toLight = [-.3, -.95]; I.ST.shadowTint = '#121a3a'; I.ST.shadeMix = .5 + (1 - L) * .2; I.ST.rim = { color: '#bcd2ff', dir: [-.4, -.9], w: 3.2, a: .85 * L + .15 }; Pr.setLight([-.2, .9, -.3]);
  const cam = camMic(t, T_2010);
  // the mic travels from his chest to the clip in one unbroken movement across the climb
  const u = C.eIO(inv(51.0, 53.0, t), 2);
  const chest = [20, 150, -8]; const clipP = add(CLIP, [0, 4, 3]);
  const mp = C.lerp3(chest, clipP, u); mp[1] += Math.sin(u * Math.PI) * 6;
  const mfwd = C.lerp3([-.2, .75, -.6], [0, .85, .52], u);
  const release = ss(inv(53.0, 53.35, t)); const away = ss(inv(53.25, 53.95, t));
  const hp = add(add(mp, mul(norm(mfwd), -6)), [away * 14, -away * 26, away * 22]);
  const R = B.rig('morten', 'late', { pelvis: MPEL, yaw: Math.PI, lean: .06 + u * .1, head: { pitch: lerp(-.05, -.3, u), yaw: -.2, E: { blink: blinkT(t, 2), gaze: [0, -.4], mouth: {}, brow: { worry: .3 } } },
    hr: { p: hp, dirs: { fwd: norm(mfwd), nrm: [1, 0, 0] }, pose: { curl: lerp(.9, .3, release), thumb: { curl: lerp(.6, .2, release), opp: 1 } } }, hl: { p: fx(frame(MPEL, Math.PI), 22, -48, 2) } });
  ST.stage(g, cam, t, { light: L, era: 'late', warm: 0, beams: true });
  Pr.drawFaces(g, cam, standFaces());
  B.drawRig(g, cam, R, { props: [{ z: cam.p(mp).z - 1, draw: () => Pr.drawFaces(g, cam, micAt(mp, mfwd)) }] });
  // a last spot on the microphone
  const q = cam.p(CLIP); I.glow(g, q.x, q.y, 300, '#cfe0ff', .25 * (1 - L) + .05, 'lighter');
  g.fillStyle = `rgba(0,0,6,${(1 - L) * .55})`; g.fillRect(0, 0, C.W, C.H);
  I.vignette(g, .6 + (1 - L) * .2);
}
function y2015(g, t) {
  const rise = ss(inv(T_2015, T_2015 + .5, t)); const warm = .85;
  I.ST.toLight = [-.3, -.95]; I.ST.shadowTint = '#3a1a20'; I.ST.shadeMix = .42; I.ST.rim = { color: '#ffd8a8', dir: [-.3, -.95], w: 3.4, a: .9 }; Pr.setLight([-.2, .9, -.3]);
  // hand reaches in and takes the mic, then the camera cranes up and back to the widest crowd
  const crane = C.eIO(inv(55.0, 57.35, t), 3);
  const c0 = camMic(Math.min(t, 55.0), T_2015); const cam = new C.Cam({ pos: C.lerp3(c0.pos, [70, 560, 520], crane), look: C.lerp3([-6, 150, -44], [0, -60, -1300], crane), fov: lerp(40, 62, crane) });
  const grab = ss(inv(54.0, 54.6, t)), lift = ss(inv(54.75, 55.3, t));
  const clipP = add(CLIP, [0, 4, 3]); const mfwd0 = [0, .85, .52];
  const mp = add(clipP, [lift * 18, lift * -10, lift * 30]); const mfwd = C.lerp3(mfwd0, [-.2, .75, -.6], lift);
  const hp = C.lerp3([70, 108, 40], add(clipP, mul(norm(mfwd0), -6)), grab); const hand = lift > 0 ? add(mp, mul(norm(mfwd), -6)) : hp;
  const R = B.rig('morten', 'late', { pelvis: MPEL, yaw: Math.PI, lean: .1 - lift * .06, head: { pitch: lerp(-.25, .05, lift), yaw: -.1, E: { blink: blinkT(t, 2), mouth: { smile: lift * .5 }, brow: { raise: lift * .3 } } },
    hr: { p: hand, dirs: { fwd: norm(lift > 0 ? mfwd : C.lerp3([.4, .2, -.9], mfwd0, grab)), nrm: [1, 0, 0] }, pose: { curl: lerp(.3, .9, ss(inv(54.5, 54.7, t))), thumb: { curl: .6, opp: 1 } } }, hl: { p: fx(frame(MPEL, Math.PI), 22, -48, 2) } });
  ST.stage(g, cam, t, { light: rise, era: 'late', warm, beams: true, n: 5200, phones: true });
  // the other two take their places
  const sf = frame([-150, 98, 18], Math.PI + .2); const Ssy = Pr.synth(sf, 2, { lowMidi: 72 });
  const RM = B.rig('magne', 'late', { pelvis: [-150 - 8, 99, 18 - 36], yaw: .2, lean: .15, head: { pitch: -.1, E: { mouth: { smile: .6 } } }, hr: { p: fx(sf, 10, 6, 12) }, hl: { p: fx(sf, -12, 6, 12) } });
  const P = [150, 99, 10]; const R0 = B.rig('pal', 'late', { pelvis: P, yaw: Math.PI - .15 }); const G = RH.guitarOn(R0, 0, 1);
  const RP = B.rig('pal', 'late', { pelvis: P, yaw: Math.PI - .15, head: { pitch: .1, E: { mouth: { smile: .5 } } }, hr: { p: G.strumP, roll: .6, flex: -.3, pose: { curl: [.55, .7, .75, .8] } }, hl: { p: G.fretP, dirs: { fwd: norm(add(mul(G.gf.F, -1), mul(G.gf.U, -.2))), nrm: norm(G.gf.U) }, pose: { curl: [.55, .7, .6, .5] } } });
  B.drawRig(g, cam, RM, { props: [{ z: cam.p(fx(sf, 0, 0, -8)).z, draw: () => Pr.drawFaces(g, cam, Ssy.faces) }] });
  B.drawRig(g, cam, RP, { props: [{ z: cam.p(G.gf.o).z - 4, draw: () => Pr.drawFaces(g, cam, Pr.guitarFaces(G.gf, '#2a2624')) }] });
  Pr.drawFaces(g, cam, standFaces());
  B.drawRig(g, cam, R, { props: [{ z: cam.p(mp).z - 1, draw: () => Pr.drawFaces(g, cam, micAt(mp, mfwd)) }] });
  g.fillStyle = `rgba(0,0,6,${(1 - rise) * .6})`; g.fillRect(0, 0, C.W, C.H);
  I.vignette(g, .55, '20,8,0');
}
// the look, again
function finalLook(g, t) {
  I.ST.toLight = [-.25, -.97]; I.ST.shadowTint = '#3a1a28'; I.ST.shadeMix = .42; I.ST.rim = { color: '#ffd8a8', dir: [0, -1], w: 3.6, a: .95 }; Pr.setLight([0, .9, .3]);
  const cam = new C.Cam({ pos: key(t, [[T_LOOK, [0, 168, -250]], [T_END, [0, 166, -226]]]), look: [0, 152, 0], fov: 40 });
  // backdrop: warm stage glow behind them (they face the audience = toward camera)
  g.fillStyle = '#120806'; g.fillRect(0, 0, C.W, C.H);
  const r = C.rng(4); for (let i = 0; i < 10; i++) { const q = cam.p([-300 + i * 66, 300 + (i % 3) * 30, 220]); I.glow(g, q.x, q.y, 260, ['#ffcf8a', '#ff9e5a', '#ffe2b0'][i % 3], .32 + .08 * Math.sin(t * 3 + i), 'lighter'); }
  E.haze(g, '#d08a50', .22, 0, C.H * .7);
  E.quad(g, cam, [[-400, 0, -60], [400, 0, -60], [400, 0, 400], [-400, 0, 400]], '#1c1210');
  const mY = key(t, [[T_LOOK, 0], [57.8, -.75, 'io2'], [58.5, -.75], [58.85, .75, 'io2'], [59.5, .75], [59.85, .1, 'io2']]);
  const magL = ss(inv(57.95, 58.3, t)), palL = ss(inv(58.95, 59.25, t));
  const RMo = B.rig('morten', 'late', { pelvis: [0, 101, 0], yaw: Math.PI, head: { yaw: mY, pitch: .02, E: { blink: blinkT(t, 2), gaze: [mY * .5, 0], mouth: { smile: .55 }, brow: { raise: .3 } } }, hr: { p: [14, 128, -18], dirs: { fwd: [0, .8, -.5], nrm: [1, 0, 0] }, pose: { curl: .9, thumb: { curl: .6, opp: 1 } } }, hl: { p: [-24, 52, -4] } });
  const RMa = B.rig('magne', 'late', { pelvis: [42, 99, 12], yaw: Math.PI + .3, head: { yaw: lerp(.1, .7, magL), pitch: .02, E: { blink: blinkT(t, 4), gaze: [-magL * .6, 0], mouth: { smile: lerp(.4, 1, magL), open: magL * .15 }, brow: { raise: magL * .5 } } } });
  const RP = B.rig('pal', 'late', { pelvis: [-44, 99, 12], yaw: Math.PI - .3, head: { yaw: lerp(-.1, -.7, palL), pitch: lerp(0, -.08, palL), E: { blink: blinkT(t, 7), gaze: [palL * .6, 0], mouth: { smile: lerp(.35, .9, palL) }, brow: { raise: palL * .4 } } } });
  const mic = Pr.handMicFaces({ o: [14, 126, -20], L: [1, 0, 0], U: norm([0, .8, -.5]), F: norm([0, .5, .8]) });
  B.drawRig(g, cam, RMa); B.drawRig(g, cam, RP);
  B.drawRig(g, cam, RMo, { props: [{ z: cam.p([14, 130, -20]).z - 1, draw: () => Pr.drawFaces(g, cam, mic) }] });
  I.vignette(g, .5, '20,8,0');
}
module.exports = [
  { t0: T_2010, t1: T_2015, name: '2010', draw: y2010 },
  { t0: T_2015, t1: T_LOOK, name: '2015', draw: y2015 },
  { t0: T_LOOK, t1: T_END + .1, name: 'look2', draw: finalLook },
];
