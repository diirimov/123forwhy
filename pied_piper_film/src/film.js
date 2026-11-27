// film: shot timeline, captions schedule, frame compositor
'use strict';
const C = require('./core');
const E = require('./env');
const PO = require('./post');
const CP = require('./captions');
const { barT, clamp, W, H } = C;

const SHOTS = [
  ...require('./shots/a_open'),
  ...require('./shots/b_rats'),
  ...require('./shots/c_stranger'),
  ...require('./shots/d_play'),
  ...require('./shots/e_river'),
  ...require('./shots/f_betrayal'),
  ...require('./shots/g_night'),
  ...require('./shots/h_procession'),
  ...require('./shots/i_end'),
].sort((a, b) => a.t0 - b.t0);

// captions (story told as a legend; studio uppercase style)
const b = barT;
const CAPS = [
  { kind: 'title', text: '130 CHILDREN VANISHED.', t0: 0.05, t1: 1.70, y: 400, size: 104, times: [0.05, 0.36, 0.69], hl: ['130'] },
  { kind: 'engraved', text: 'HAMELIN, 1284', t0: 1.86, t1: 3.36, y: 300, size: 92 },
  { kind: 'story', text: 'THE TOWN WAS OVERRUN BY RATS.', t0: b(2, 1), t1: b(4) - .15, y: 400, beats: true, hl: ['RATS'] },
  { kind: 'story', text: 'A MYSTERIOUS STRANGER OFFERED A SOLUTION.', t0: b(8), t1: b(10) - .1, y: 380, beats: true, hl: ['STRANGER'] },
  { kind: 'story', text: 'THEN HE BEGAN TO PLAY.', t0: b(10, 1), t1: b(11) - .12, y: 400, beats: true, hl: ['PLAY'] },
  { kind: 'story', text: 'THE RATS DISAPPEARED.', t0: b(16), t1: b(17) - .1, y: 410, beats: true, hl: ['DISAPPEARED'] },
  { kind: 'story', text: 'BUT THE TOWN REFUSED TO PAY.', t0: b(20), t1: b(21) + .85, y: 380, beats: true, hl: ['REFUSED'] },
  { kind: 'story', text: 'SO HE RETURNED.', t0: b(22, 4), t1: C.BM.gaps[1] - .02, y: 420, beats: true, hl: ['RETURNED'] },
  { kind: 'story', text: 'THIS TIME, THE RATS STAYED STILL.', t0: b(24), t1: b(25) - .1, y: 380, beats: true, hl: ['STILL'] },
  { kind: 'story', text: 'THE CHILDREN FOLLOWED INSTEAD.', t0: b(26), t1: b(27) - .14, y: 390, beats: true, hl: ['CHILDREN'] },
  { kind: 'story', text: 'THEY NEVER RETURNED.', t0: b(33), t1: b(34) - .1, y: 420, beats: true, hl: ['NEVER'] },
  { kind: 'legend', label: 'THE LEGEND', text: 'According to legend,\n130 children vanished.', t0: b(34) + .15, t1: b(35, 14), y: 330 },
  { kind: 'engraved', text: 'THE PIED PIPER\nOF HAMELIN', t0: b(36) + .05, t1: C.DUR + 1, y: 520, size: 96 },
];
// word times on the beat grid (one word per 8th note starting at t0)
for (const c of CAPS) if (c.beats) { const n = c.text.split(' ').length; c.times = Array.from({ length: n }, (_, i) => c.t0 + i * C.BEAT / 2); }

function drawCaptions(g, t) {
  for (const c of CAPS) {
    if (t < c.t0 - .05 || t > c.t1 + .5) continue;
    if (c.kind === 'engraved') CP.engraved(g, c.text, t, { t0: c.t0, t1: c.t1, y: c.y, size: c.size });
    else if (c.kind === 'legend') CP.paperCard(g, c.label, c.text, t, { t0: c.t0, t1: c.t1, y: c.y, h: 250, size: 66, labelSize: 38 });
    else CP.storyCaption(g, c.text, t, { t0: c.t0, t1: c.t1, y: c.y, size: c.size || 76, times: c.times, hl: new Set(c.hl || []) });
  }
}

function shotAt(t) { let s = SHOTS[0]; for (const x of SHOTS) if (x.t0 <= t + 1e-6) s = x; return s; }

function renderFrame(g, t) {
  const S = shotAt(t);
  E.LIGHTS.length = 0;
  g.save(); g.setTransform(1, 0, 0, 1, 0, 0);
  g.fillStyle = '#120a06'; g.fillRect(0, 0, W, H);
  const lt = t - S.t0;
  S.draw(g, t, lt, S);
  g.restore();
  g.save(); g.setTransform(1, 0, 0, 1, 0, 0);
  const gr = typeof S.grade === 'function' ? S.grade(t, lt) : { mood: S.mood || 'day' };
  PO.grade(g, gr.mood, gr.amt ?? 1, gr.mood2, gr.mix || 0);
  PO.lights(g, gr.lights ?? 1);
  if (S.over) S.over(g, t, lt);
  drawCaptions(g, t);
  const fin = S.finish ? S.finish(t, lt) : {};
  PO.finish(g, t, fin);
  // cut punctuation: a 2-frame ink flash at hard cuts marked 'flash'
  if (S.flashIn && lt < 2 / 60) { g.fillStyle = 'rgba(255,240,215,.35)'; g.fillRect(0, 0, W, H); }
  g.restore();
  return S;
}

module.exports = { SHOTS, CAPS, renderFrame, shotAt };
