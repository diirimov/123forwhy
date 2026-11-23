// stage world shared by the late shots (audience toward -z, stage floor y=0, crowd floor y=-150)
const C = require('./core'); const I = require('./ink'); const Pr = require('./props'); const E = require('./env'); const S = require('./scene');
const { clamp, lerp, ss, inv, fx, frame, add } = C;
function stage(g, cam, t, o = {}) {
  const L = o.light ?? 1; const warm = o.warm ?? 0; const era = o.era || '80s';
  const sky = g.createLinearGradient(0, 0, 0, C.H);
  const top = I.mix('#03030a', era === 'late' ? I.mix('#0c1838', '#3a1c0e', warm) : '#1a0f38', L), mid = I.mix('#05050c', era === 'late' ? I.mix('#24407a', '#a8582a', warm) : '#5a2c6e', L);
  sky.addColorStop(0, top); sky.addColorStop(.5, mid); sky.addColorStop(1, '#040308'); g.fillStyle = sky; g.fillRect(0, 0, C.W, C.H);
  if (L > .05 && o.tiers !== false) { const r = C.rng(5); for (let i = 0; i < 600; i++) { const x = (r() - .5) * 9000, z = -5200 - r() * 800, y = -150 + r() * 1100; const q = cam.p([x, y, z]); if (q.x < 0 || q.x > C.W || q.z < 1) continue; g.fillStyle = `rgba(255,${210 + r() * 45 | 0},${170 + r() * 80 | 0},${(.25 + .5 * Math.abs(Math.sin(t * 3 + i))) * L})`; g.fillRect(q.x, q.y, 2.4, 2.4); } }
  const wash = (x, z) => { const a = Math.sin(x * .0011 + t * .9) * .5 + .5; return era === 'late' ? I.mix(I.mix('#7fb4ff', '#ffc27a', warm), '#ffffff', a * .3) : I.mix(I.mix('#ffb070', '#7fb4ff', a), '#ff6fa0', .2); };
  if (o.crowd !== false) E.crowd2(g, cam, { x0: -3600, x1: 3600, z0: -260, z1: -5400, y: -150, n: o.n || 4200, seed: o.seed || 31, zPow: 1.9, fogCol: I.mix('#03040a', era === 'late' ? I.mix('#2a4a8a', '#a8582a', warm) : '#7a4a90', L), fogNear: 400, fogFar: 5000, lit: Math.max(.03, L), wash: L > .2 ? wash : null, arms: .3 + .35 * L, energy: L, t, rim: era === 'late' ? I.mix('#cfe0ff', '#ffe2b8', warm) : '#ffe2b8', rimA: .45 * L, faces: L > .5, phones: era === 'late' && o.phones });
  E.quad(g, cam, [[-700, 0, -60], [700, 0, -60], [700, 0, 600], [-700, 0, 600]], I.mix('#08070c', '#1c1620', L));
  E.quad(g, cam, [[-700, 0, -60], [700, 0, -60], [700, -150, -60], [-700, -150, -60]], '#040306');
  E.lines3(g, cam, [[[-700, .3, -60], [700, .3, -60]]], I.mix('#202030', '#ffcf9a', L), 1.3, .8);
  if (o.beams !== false && L > .1) {
    E.haze(g, era === 'late' ? I.mix('#5a7ac8', '#d08a50', warm) : '#b07ac8', .18 * L, C.H * .2, C.H * .75);
    const lamps = [[-420, 330, -40], [-160, 350, -50], [160, 350, -50], [420, 330, -40]];
    lamps.forEach((Lm, i) => { const sw = Math.sin(t * (1.0 + i * .21) + i * 1.9) * 800; const col = era === 'late' ? [I.mix('#9fd0ff', '#ffd59a', warm), '#ffffff', I.mix('#7fb4ff', '#ffb36b', warm), I.mix('#cfe0ff', '#ffe7c4', warm)][i] : ['#ffd7a0', '#9fd0ff', '#ff7aa8', '#b49bff'][i]; E.beam3(g, cam, Lm, [Lm[0] * 3 + sw, -150, -2000 - i * 400], .06, col, .28 * L); });
  }
}
module.exports = { stage };
