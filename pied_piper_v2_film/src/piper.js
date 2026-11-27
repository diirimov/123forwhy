// piper: playing pose, recorder prop with fingering driven by the real flute notes, close-up hands
'use strict';
const C = require('./core');
const R = require('./rig');
const K = require('./ink');
const { clamp, lerp, TAU } = C;
const { PAL, INK } = K;
const { v } = R;

// recorder fingering (alto): holes 0 = thumb (back), 1..7 front top->bottom. returns closed flags
function fingering(midi) {
  if (midi == null) return [1, 1, 1, 1, 0, 0, 0, 0];
  const m = Math.round(midi);
  const table = {
    65: '11111111', 66: '11111110', 67: '11111110', 68: '11111101', 69: '11111100', 70: '11111011', 71: '11110110',
    72: '11110000', 73: '11101100', 74: '11100000', 75: '11011110', 76: '11000000', 77: '10100000', 78: '01100000', 79: '00100000',
    80: '01111110', 81: '21111100', 82: '21111010', 83: '21110000', 84: '21100000', 85: '21110110', 86: '21011100', 87: '21011010', 88: '21001100',
  };
  const s = table[clamp(m, 65, 88)] || '11110000';
  return [...s].map(ch => ch === '2' ? .5 : +ch);
}
// smoothly animated finger lift amounts (0 = on hole, 1 = lifted) at time t, from the beat map's flute notes
function fingersAt(t) {
  const n = C.fluteAt(t);
  const cur = fingering(n ? n.m : null);
  // fingers move ~35 ms before the note (anticipation) -> look ahead
  const nx = C.fluteAt(t + .035);
  const tgt = fingering(nx ? nx.m : (n ? n.m : null));
  return tgt.map(x => 1 - x);
}

// playing pose for the Piper (in place). o: {sway, t, yaw}
function playPose(t, o = {}) {
  const B = R.BODY.piper;
  const phr = Math.sin(t * TAU / (C.BAR * 2));          // slow phrase sway
  const env = C.envAt('flute', t);
  const P = R.idle(t * .5, { B, shift: .25 });
  P.lean = .04 + .03 * phr;
  P.side = .05 * phr;
  P.bob = -2 + 1.5 * env;
  P.head = { yaw: 0, pitch: .18 + .03 * Math.sin(t * 2.1), roll: .06 * phr };
  // hands on the recorder: chest-local targets (left hand above right), held in front of the mouth, angled down
  const mouthY = B.shY + B.neck + B.headH * .3;
  P.arms = {
    l: { hand: v(6, mouthY - 66, 40), pole: v(.45, -1, .15) },
    r: { hand: v(-4, mouthY - 112, 50), pole: v(-.45, -1, .15) },
  };
  P.hands = { l: 'none', r: 'none' };
  P.face = { mouth: 'flute', eyes: o.eyes || 'narrow', brow: o.brow || 'sly', look: o.look || [0, .2], glow: o.glow || 0 };
  P.prop = { draw: (g, J, pr, lw) => drawRecorder(g, J, pr, lw, t, o) };
  return P;
}

// recorder + fingers drawn between mouth and lower hand
function drawRecorder(g, J, pr, lw, t, o = {}) {
  const B = J.B;
  const hc = pr(J.headC);
  const yawH = J.yaw + J.head.yaw;
  const mouth = [hc[0] + Math.sin(yawH) * B.headW * .25, hc[1] + B.headH * .28 + Math.sin(J.head.pitch) * 10];
  const lo = pr(J.wrr), up = pr(J.wrl);
  // flute axis: from mouth through the hands, extending past the lower hand
  const dx = lo[0] - mouth[0], dy = lo[1] - mouth[1], L = Math.hypot(dx, dy) || 1, ux = dx / L, uy = dy / L;
  const end = [lo[0] + ux * 34, lo[1] + uy * 34];
  const nx = -uy, ny = ux;
  const r0 = 6.2, r1 = 8.8;
  const body = [[mouth[0] + nx * r0, mouth[1] + ny * r0], [end[0] + nx * r1, end[1] + ny * r1], [end[0] - nx * r1, end[1] - ny * r1], [mouth[0] - nx * r0, mouth[1] - ny * r0]];
  K.shape(g, body, { fill: '#a9764a', lw, smooth: false, inner: (g2) => { g2.strokeStyle = 'rgba(255,235,200,.5)'; g2.lineWidth = 2; g2.beginPath(); g2.moveTo(mouth[0] + nx * 2, mouth[1] + ny * 2); g2.lineTo(end[0] + nx * 3, end[1] + ny * 3); g2.stroke(); } });
  // bell + rings
  K.ellipse(g, end[0], end[1], r1 * 1.25, r1 * .7, { fill: '#8a5a36', lw: lw * .8 }, Math.atan2(uy, ux) + Math.PI / 2);
  for (const u of [.18, .62]) { const p = [lerp(mouth[0], end[0], u), lerp(mouth[1], end[1], u)]; K.line(g, [[p[0] + nx * (r0 + 1.5), p[1] + ny * (r0 + 1.5)], [p[0] - nx * (r0 + 1.5), p[1] - ny * (r0 + 1.5)]], lw * .7, '#5d3a22', 1, false); }
  // fingers: left hand covers holes 1..3, right hand 4..7
  const lift = fingersAt(t);
  const holeU = i => .3 + (i - 1) * .085;
  const side = Math.cos(yawH) >= 0 ? 1 : -1;
  for (let i = 1; i <= 7; i++) {
    const u = holeU(i); const p = [lerp(mouth[0], end[0], u), lerp(mouth[1], end[1], u)];
    if (lift[i] > .5) K.ellipse(g, p[0], p[1], 2.6, 2.6, { fill: '#2a1a10', lw: 0 });
    const up2 = lift[i] * 13;
    const fx = p[0] + nx * side * (r1 + 3 + up2), fy = p[1] + ny * side * (r1 + 3 + up2);
    K.capsule(g, [p[0] + nx * side * (r1 + 18 + up2 * .4), p[1] + ny * side * (r1 + 18 + up2 * .4)], [fx, fy], 5.2, 4.6, { fill: PAL.pale, lw: lw * .7 });
  }
  // hand bodies (palms around the tube)
  for (const [w, u] of [[up, .37], [lo, .72]]) {
    const p = [lerp(mouth[0], end[0], u), lerp(mouth[1], end[1], u)];
    K.ellipse(g, p[0] + nx * side * 26, p[1] + ny * side * 26, 15, 19, { fill: PAL.pale, lw: lw * .85 }, Math.atan2(uy, ux));
  }
  // a few notes of light when playing loud (the melody's spell, subtle)
}

// ------------------------------------------------------------------ close-up: big recorder and hands (screen space)
// cx,cy: point on the flute near the mouth; ang: flute angle; s: scale
function closeupFlute(g, x0, y0, ang, s, t, o = {}) {
  g.save(); g.translate(x0, y0); g.rotate(ang); g.scale(s, s);
  const lw = (o.lw ?? 5) / s;
  const L = 520;
  K.shape(g, [[0, -14], [L, -20], [L + 30, -28], [L + 30, 28], [L, 20], [0, 14]], { fill: '#a8744a', lw, smooth: false, inner: (g2) => {
    const gr = g2.createLinearGradient(0, -20, 0, 20); gr.addColorStop(0, 'rgba(255,230,190,.45)'); gr.addColorStop(.4, 'rgba(255,230,190,0)'); gr.addColorStop(1, 'rgba(40,20,5,.35)'); g2.fillStyle = gr; g2.fillRect(0, -30, L + 40, 60);
    g2.strokeStyle = 'rgba(80,45,20,.4)'; g2.lineWidth = 1.5; for (let i = 0; i < 9; i++) { g2.beginPath(); g2.moveTo(i * 60, -12); g2.bezierCurveTo(i * 60 + 30, -6, i * 60 + 40, 8, i * 60 + 70, 10); g2.stroke(); }
  } });
  for (const u of [70, 330]) K.line(g, [[u, -19], [u, 19]], lw * 1.2, '#5d3a22', 1, false);
  const lift = fingersAt(t);
  const holes = [0, 120, 160, 200, 268, 308, 348, 396];
  for (let i = 1; i <= 7; i++) K.ellipse(g, holes[i], -1, 7, 6, { fill: '#2a1608', lw: lw * .6 });
  // fingers: each finger = proximal + distal capsule bending over the hole, lifts with the note
  const fingerCol = o.skin || PAL.pale;
  for (let i = 1; i <= 7; i++) {
    const up = lift[i] * (1 + .15 * Math.sin(t * 40 + i));
    const knuck = [holes[i] - 10, -64 - up * 10];
    const mid = [holes[i] - 2, -36 - up * 22];
    const tip = [holes[i] + 2, -8 - up * 34];
    K.capsule(g, knuck, mid, 15, 13, { fill: fingerCol, lw });
    K.capsule(g, mid, tip, 13, 11.5, { fill: fingerCol, lw });
    K.shape(g, [[tip[0] - 7, tip[1] - 6], [tip[0] + 7, tip[1] - 6], [tip[0] + 6, tip[1] + 4], [tip[0] - 6, tip[1] + 4]], { fill: '#f0d9c6', lw: lw * .4, alpha: .7 });
  }
  // backs of the hands
  K.shape(g, [[70, -60], [240, -66], [250, -120], [190, -170], [60, -150], [30, -100]], { fill: fingerCol, lw, tension: .5 });
  K.shape(g, [[245, -62], [420, -68], [430, -125], [360, -175], [250, -150], [222, -100]], { fill: fingerCol, lw, tension: .5 });
  // sleeves
  K.shape(g, [[40, -140], [200, -165], [250, -260], [60, -300], [-20, -220]], { fill: PAL.burg, lw, tension: .4 });
  K.shape(g, [[260, -150], [420, -160], [470, -260], [300, -300], [230, -220]], { fill: PAL.pgreen, lw, tension: .4 });
  g.restore();
}

module.exports = { fingering, fingersAt, playPose, drawRecorder, closeupFlute };
