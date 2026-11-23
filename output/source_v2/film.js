// film: shot table + caption track + frame renderer
const C = require('./core'); const I = require('./ink');
const fs = require('fs'); const path = require('path');
const SHOTS = [];
for (const f of fs.readdirSync(path.join(__dirname, 'shots')).sort()) { if (!f.endsWith('.js')) continue; const m = require('./shots/' + f); (Array.isArray(m) ? m : [m]).forEach(s => SHOTS.push(s)); }
SHOTS.sort((a, b) => a.t0 - b.t0);
let CAP = null; try { CAP = require('./captions'); } catch (e) { }
function renderFrame(g, t, frame) {
  I.ST.frame = frame; I.ST.mode = 'color'; I.ST.rim = null; I.ST.toLight = [-.55, -.83]; I.ST.shadowTint = '#2a2350'; I.ST.shadeMix = .38; I.ST.inkW = 3;
  const s = SHOTS.find(s => t >= s.t0 && t < s.t1) || SHOTS[SHOTS.length - 1];
  g.save(); g.fillStyle = '#000'; g.fillRect(0, 0, C.W, C.H); s.draw(g, t, t - s.t0); g.restore();
  I.grain(g, .05);
  if (CAP && !s.noCaption) CAP.draw(g, t);
  return s.name;
}
module.exports = { SHOTS, renderFrame };
