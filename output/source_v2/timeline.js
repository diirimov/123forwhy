// timeline: musical cues (video seconds) measured from the locked audio
const Q = require('./cues.json');
const B = Q.beats, D = Q.down;
const near = t => B.reduce((a, b) => Math.abs(b - t) < Math.abs(a - t) ? b : a, B[0]);
const snareNear = t => { let best = 1e9, bt = t; B.forEach((b, i) => { if (Q.lab[i] === 'S' && Math.abs(b - t) < Math.abs(best - t)) best = b; }); return best; };
const downNear = t => D.reduce((a, b) => Math.abs(b - t) < Math.abs(a - t) ? b : a, D[0]);
function lastBeat(t) { let r = -10; for (const b of B) { if (b <= t) r = b; else break; } return r; }
function pulse(t, k = .12) { return Math.exp(-(t - lastBeat(t)) / k); }
const CUE = { vocal: 19.30, pre: 33.75, take: 42.263, climb: 47.75, high: 53.954, highEnd: 57.507 };
// riff notes in the intro (time, folded midi, strength)
const RIFF = Q.riff.map(([t, m, v]) => { let mm = m; while (mm > 88) mm -= 12; while (mm < 76) mm += 12; return { t, m: mm, v }; });
module.exports = { Q, B, D, near, snareNear, downNear, lastBeat, pulse, CUE, RIFF };
