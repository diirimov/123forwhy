// film: shot timeline, captions schedule, frame compositor (V2 -- rebuilt around the new soundtrack)
'use strict';
const C = require('./core');
const E = require('./env');
const PO = require('./post');
const CP = require('./captions');
const { barT: b, clamp, W, H } = C;

const SEQ = ['v_a_hook', 'v_b_rats', 'v_c_arrival', 'v_d_rat_dance', 'v_e_celebration', 'v_f_return', 'v_g_children', 'v_h_end'];
const SHOTS = [];
for (const s of SEQ) { try { SHOTS.push(...require('./shots/' + s)); } catch (e) { if (e.code !== 'MODULE_NOT_FOUND' || !String(e.message).includes(s)) throw e; } }
SHOTS.sort((a, c) => a.t0 - c.t0);

// captions: short, the legend told in the studio's DP style (uppercase story captions, one word per 8th note)
const CAPS = [
  { kind: 'title', text: 'IN 1284, 130 CHILDREN VANISHED.', t0: 0.12, t1: b(1, 15), y: 380, size: 96, times: [0.12, 0.62, 1.40, 2.22, 2.78], hl: ['1284,', '130'] },   // word times = the narration (data/voiceover.json)
  { kind: 'engraved', text: 'HAMELIN, 1284', t0: b(2) + .05, t1: b(3) - .05, y: 330, size: 96 },
  { kind: 'story', text: 'THE TOWN WAS OVERRUN BY RATS.', t0: b(3, 2), t1: b(5) - .12, y: 380, beats: true, hl: ['RATS.'] },
  { kind: 'story', text: 'A STRANGER OFFERED TO SAVE THEM.', t0: b(7) + .05, t1: b(9, 8), y: 380, beats: true, hl: ['STRANGER'] },
  { kind: 'story', text: 'THE RATS FOLLOWED HIS MELODY.', t0: b(11) + .05, t1: b(13) - .12, y: 380, beats: true, hl: ['MELODY.'] },
  { kind: 'story', text: 'BUT THEY REFUSED TO PAY HIM.', t0: b(19) + .08, t1: b(20, 12), y: 380, beats: true, hl: ['REFUSED'] },
  { kind: 'story', text: 'SO HE PLAYED AGAIN.', t0: b(22) + .05, t1: C.BM.gaps[2] - .02, y: 400, beats: true, hl: ['AGAIN.'] },
  { kind: 'story', text: 'THIS TIME, THE CHILDREN FOLLOWED.', t0: b(23) + .1, t1: b(25) - .12, y: 380, beats: true, hl: ['CHILDREN'] },
  { kind: 'legend', label: 'THE LEGEND', text: 'According to legend,\n130 children vanished.', t0: b(33) + .1, t1: b(35) - .1, y: 330 },
  { kind: 'story', text: 'THEY NEVER RETURNED.', t0: b(35) + .1, t1: C.DUR + 1, y: 400, beats: true, hl: ['NEVER'] },
];
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
  if (S.flashIn && lt < 2 / 60) { g.fillStyle = 'rgba(255,240,215,.3)'; g.fillRect(0, 0, W, H); }
  g.restore();
  return S;
}

module.exports = { SHOTS, CAPS, renderFrame, shotAt };
