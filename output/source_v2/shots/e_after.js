// AFTER THE BREAKTHROUGH (44.10 -> 50.77): teen at the TV, concertgoer, Pål -> Magne on stage
const C = require('../core'); const I = require('../ink'); const Pr = require('../props'); const B = require('../body'); const Hn = require('../hand'); const E = require('../env'); const S = require('../scene');
const TL = require('../timeline'); const ST = require('../stage'); const RH = require('../rehearsal');
const { key, clamp, lerp, inv, ss, eOut, add, sub, mul, norm, dot, cross, fx, frame } = C;
const T_TEEN = 44.10, T_FAN = 45.65, T_TRACK = 47.08, T_END = TL.downNear(50.77);
const blinkT = (t, seed) => { const per = 2.4 + C.hash(seed) * 1.6; const ph = (t + C.hash(seed + 3) * per) % per; return ph < .13 ? Math.sin(ph / .13 * Math.PI) : 0; };
const flick = t => .82 + .18 * (C.noise(t * 14) * .6 + Math.sin(t * 47) * .4);

// face framing shared by teen & fan (match cut): camera relative to head
function faceCam(head, t, t0) { return new C.Cam({ pos: add(head, [-66 - (t - t0) * 2, 8, 64]), look: add(head, [-48, -10, 0]), fov: 50 }); }
let TVTEX = null;
function tvContent() { if (TVTEX) return TVTEX; const c = C.createCanvas(480, 360); const g = c.getContext('2d'); g.fillStyle = '#dfe6f0'; g.fillRect(0, 0, 480, 360); const save = { ...I.ST }; I.ST.mode = 'pencil'; I.ST.inkW = 2; const cam = new C.Cam({ pos: [0, 168, 70], look: [0, 160, 0], vw: 480, vh: 360, fov: 40 }); B.drawRig(g, cam, B.rig('morten', '80s', { pelvis: [0, 103, 0], yaw: 0, head: { pitch: .05, E: { mouth: { open: .5 } } }, hl: { p: [24, 150, 30] } }), { lw: 2 }); Object.assign(I.ST, save); TVTEX = c; return c; }
function teen(g, t) {
  const scoot = key(t, [[T_TEEN, 0], [44.39, 0], [44.55, 5, 'out2'], [45.08, 5], [45.24, 10, 'out2']]);
  const pel = [26 - scoot, 32, 0]; const F = frame(pel, -Math.PI / 2 + .35);
  const R = B.rig('teen', '80s', { pelvis: pel, yaw: -Math.PI / 2 + .35, lean: .32 + scoot * .01, fl: fx(F, 12, -30, 42), fr: fx(F, -12, -30, 40),
    hl: { p: fx(F, 14, -18, 34) }, hr: { p: fx(F, -14, -18, 32) },
    head: { pitch: .06, yaw: .35, E: { blink: blinkT(t, 9) * .7, gaze: [0, .1], mouth: { open: .18 + scoot * .015 }, brow: { raise: .5 } } } });
  const head = R.headC; const cam = faceCam([head[0] + 26, head[1], head[2]], t, T_TEEN);
  const fl = flick(t);
  I.ST.toLight = [-1, -.15]; I.ST.shadowTint = '#0e1430'; I.ST.shadeMix = .62; I.ST.rim = { color: '#cfe4ff', dir: [-1, -.1], w: 3.5 * fl, a: .9 }; Pr.setLight([-1, .3, 0]);
  g.fillStyle = '#05060c'; g.fillRect(0, 0, C.W, C.H);
  // living room hints: sofa edge, wallpaper in deep shadow
  E.quad(g, cam, [[-300, 0, -200], [300, 0, -200], [300, 260, -200], [-300, 260, -200]], '#121522');
  E.quad(g, cam, [[-300, 0, -200], [300, 0, -200], [300, 0, 300], [-300, 0, 300]], '#0d0f18');
  // TV (screen faces +x)
  const tvF = { o: [-62, 68, 0], L: [0, 0, -1], U: [0, 1, 0], F: [1, 0, 0] };
  Pr.drawFaces(g, cam, Pr.box(tvF, 34, 26, 24, '#3a2c22', { cols: { f: '#2a201a' } }));
  const sc = [[-37.2, 50, 26], [-37.2, 50, -26], [-37.2, 88, -26], [-37.2, 88, 26]].map(p => { const q = cam.p([p[0] + 0, p[1], p[2]]); return [q.x, q.y]; });
  g.save(); g.globalAlpha = fl; Pr.texPoly(g, tvContent(), sc, [[0, 360], [480, 360], [480, 0], [0, 0]]); g.restore();
  const tq = cam.p([-36, 69, 0]); I.glow(g, tq.x, tq.y, 900, '#9ec4ff', .5 * fl, 'lighter');
  B.drawRig(g, cam, R);
  // TV light spill on the face side
  const hq = cam.p(head); I.glow(g, hq.x - 60, hq.y, 260, '#bcd6ff', .18 * fl, 'lighter');
  I.vignette(g, .65, '0,0,10');
}
function fan(g, t) {
  const pel = [16, 99, 0]; const R = B.rig('fan', '80s', { pelvis: pel, yaw: -Math.PI / 2 + .15, lean: -.05,
    head: { pitch: .38, yaw: -.1, E: { blink: blinkT(t, 13) * .5, gaze: [0, .5], mouth: { open: .25 + .2 * TL.pulse(t, .2), smile: .3 }, brow: { raise: .6 } } },
    hl: { p: [24, 178 + Math.sin(t * 6) * 3, -26] }, hr: { p: fx(frame(pel, -Math.PI / 2), -20, -46, 4) } });
  const head = R.headC; const cam = faceCam([head[0] + 26, head[1], head[2]], t, T_FAN);
  const k = ss(inv(T_FAN, T_FAN + .35, t)); const pul = TL.pulse(t, .15);
  const col = I.mix('#cfe4ff', I.mix('#ffb36b', '#ff6fa8', Math.sin(t * 2) * .5 + .5), k);
  I.ST.toLight = [-1, -.35]; I.ST.shadowTint = I.mix('#0e1430', '#2a1238', k); I.ST.shadeMix = .58; I.ST.rim = { color: col, dir: [-1, -.3], w: 3.5 + pul * 1.5, a: .95 }; Pr.setLight([-1, .5, 0]);
  // blurred concert behind
  S.drawBlurred(g, x => {
    x.fillStyle = '#080510'; x.fillRect(0, 0, C.W, C.H);
    const r = C.rng(3); for (let i = 0; i < 40; i++) { const px = r() * C.W, py = 200 + r() * 900; I.glow(x, px, py, 40 + r() * 80, ['#ffb36b', '#ff6fa8', '#8fb8ff', '#ffe0a0'][i % 4], .35 * (.6 + .4 * Math.sin(t * 5 + i)), 'lighter'); }
    E.crowd2(x, cam, { x0: -500, x1: 200, z0: -90, z1: -900, y: 0, n: 260, seed: 5, lit: .25, fogCol: '#1a0f28', arms: .5, t, energy: 1 });
  }, 14);
  B.drawRig(g, cam, R);
  const hq = cam.p(head); I.glow(g, hq.x - 80, hq.y - 40, 300, col, .2 + pul * .12, 'lighter');
  I.vignette(g, .6, '5,0,10');
}
// one continuous move across the stage: Pål, then Magne
function track(g, t) {
  const u = ss(inv(T_TRACK, T_END, t));
  I.ST.toLight = [-.2, -.98]; I.ST.shadowTint = '#2a1840'; I.ST.shadeMix = .45; I.ST.rim = { color: '#ffd6a8', dir: [0, -1], w: 3, a: .8 }; Pr.setLight([0, .9, .4]);
  const cam = new C.Cam({ pos: [lerp(150, -140, u), lerp(150, 146, u), lerp(150, 140, u)], look: [lerp(90, -100, u), lerp(140, 128, u), -10], fov: 42 });
  ST.stage(g, cam, t, { light: 1, era: '80s', crowd: false, beams: true });
  // stage backdrop: a sun on the screen wall
  const wall = [[-420, 40, -260], [420, 40, -260], [420, 330, -260], [-420, 330, -260]].map(p => cam.p(p)).map(q => [q.x, q.y]);
  g.save(); g.beginPath(); I.poly(g, wall); g.fillStyle = '#1a0c20'; g.fill(); g.clip();
  const sc = cam.p([0, 190, -259]); const rr = 110 * sc.s;
  const gr = g.createRadialGradient(sc.x, sc.y, rr * .2, sc.x, sc.y, rr * 3); gr.addColorStop(0, 'rgba(255,210,120,.9)'); gr.addColorStop(1, 'rgba(255,120,60,0)'); g.fillStyle = gr; g.fillRect(sc.x - rr * 3, sc.y - rr * 3, rr * 6, rr * 6);
  g.fillStyle = '#ffd58a'; g.beginPath(); g.arc(sc.x, sc.y, rr, 0, 7); g.fill();
  g.strokeStyle = 'rgba(255,200,120,.6)'; g.lineWidth = 6 * sc.s; for (let i = 0; i < 16; i++) { const a = i / 16 * Math.PI * 2 + t * .2; g.beginPath(); g.moveTo(sc.x + Math.cos(a) * rr * 1.25, sc.y + Math.sin(a) * rr * 1.25); g.lineTo(sc.x + Math.cos(a) * rr * 1.9, sc.y + Math.sin(a) * rr * 1.9); g.stroke(); }
  g.fillStyle = 'rgba(0,0,0,.25)'; for (let y = 0; y < C.H; y += 8) g.fillRect(0, y, C.W, 3);
  g.restore();
  // Pål performing
  const sp = Math.sin((t - TL.lastBeat(t)) / .177 * Math.PI);
  const P = [100, 99, 0]; const R0 = B.rig('pal', '80s', { pelvis: P, yaw: -.25, lean: -.08 }); const G = RH.guitarOn(R0, sp, 1);
  const RP = B.rig('pal', '80s', { pelvis: [P[0], P[1] + TL.pulse(t, .12) * 1.5, P[2]], yaw: -.25, lean: -.08, head: { pitch: .25, roll: Math.sin(t * 3) * .08, E: { blink: blinkT(t, 7), mouth: { open: .15, smile: .3 }, brow: { raise: .4 } } },
    hr: { p: G.strumP, roll: .6, flex: -.3, pose: { curl: [.55, .7, .75, .8], thumb: { curl: .1, opp: .9 } } }, hl: { p: G.fretP, dirs: { fwd: norm(add(mul(G.gf.F, -1), mul(G.gf.U, -.2))), nrm: norm(G.gf.U) }, pose: { curl: [.55, .7, .6, .5], spread: .3 } } });
  B.drawRig(g, cam, RP, { props: [{ z: cam.p(G.gf.o).z - 4, draw: () => { Pr.drawFaces(g, cam, Pr.guitarFaces(G.gf, '#c23a2c')); Pr.guitarStrings(g, cam, G.gf, 1, t); } }] });
  // Morten singing at the centre microphone
  const mSing = .35 + .4 * Math.abs(Math.sin(t * 6.5));
  const RMo = B.rig('morten', '80s', { pelvis: [0, 101, -60], yaw: -.1, lean: -.05, head: { pitch: .12, E: { blink: blinkT(t, 2), mouth: { open: mSing, o: .3 }, brow: { raise: .5 } } }, hr: { p: [-6, 160, -36], dirs: { fwd: [0, .8, .6], nrm: [-1, 0, 0] }, pose: { curl: .9, thumb: { curl: .6, opp: 1 } } }, hl: { p: [40, 150, -40], roll: -1 } });
  B.drawRig(g, cam, RMo, { props: [{ z: cam.p([-6, 166, -34]).z - 1, draw: () => Pr.drawFaces(g, cam, Pr.handMicFaces({ o: [-6, 162, -33], L: [1, 0, 0], U: norm([0, .8, .6]), F: norm([0, -.6, .8]) })) }] });
  // Magne at keys on a stand
  const sf = frame([-110, 98, 12], Math.PI + .3); const notes = TL.RIFF.map(n => ({ ...n, t: n.t + (TL.downNear(47.93) - TL.downNear(1.09)) }));
  const fA = RH.fingering(t, notes, sf, Pr.synth(sf, 2, { lowMidi: 72 })); const Ssy = Pr.synth(sf, 2, { lowMidi: 72, press: fA.press });
  const RM = B.rig('magne', '80s', { pelvis: [-110 - 22 * Math.sin(.3), 99, 12 - 36], yaw: .3, lean: .18, head: { pitch: -.15 + TL.pulse(t, .15) * .08, yaw: .2, E: { blink: blinkT(t, 4), mouth: { smile: .6 }, brow: { raise: .3 } } },
    hr: { p: fA.Hs.w, dirs: { fwd: fA.Hs.fwd, nrm: fA.Hs.nrm }, pose: fA.pose }, hl: { p: fx(sf, -14, 6, 12), dirs: { fwd: fA.Hs.fwd, nrm: fA.Hs.nrm }, pose: { curl: .45 } } });
  const stand = [...Pr.box(frame([-110, 48, 12 - 6], .3), 3, 48, 3, '#1a1a20')];
  B.drawRig(g, cam, RM, { props: [{ z: cam.p(fx(sf, 0, 0, -8)).z, draw: () => { Pr.drawFaces(g, cam, stand); Pr.drawFaces(g, cam, Ssy.faces); } }] });
  E.beam3(g, cam, [100, 400, 60], [100, 0, 0], .1, '#ffd6a8', .25); E.beam3(g, cam, [-110, 400, 60], [-110, 0, 0], .1, '#9fd0ff', .25);
  I.vignette(g, .55);
}
module.exports = [
  { t0: T_TEEN, t1: T_FAN, name: 'teen', draw: teen },
  { t0: T_FAN, t1: T_TRACK, name: 'fan', draw: fan },
  { t0: T_TRACK, t1: T_END, name: 'track', draw: track },
];
