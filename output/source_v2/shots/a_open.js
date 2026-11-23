// OPENING (0 -> 2.26): a thumb slides the sleeve back into a crate of identical sleeves; the lid lands on the snare -> black
const C = require('../core'); const I = require('../ink'); const Pr = require('../props'); const Hn = require('../hand'); const E = require('../env'); const S = require('../scene');
const TL = require('../timeline');
const { key, clamp, lerp, inv, ss, eIn, eOut, add, mul, norm } = C;
const HIT = TL.snareNear(2.16); // 2.162
const SW = 31.5;

let BG = null;
function shopBackdrop() { // painted record-shop wall, pre-blurred
  if (BG) return BG; const [c, g] = S.layer();
  const gr = g.createLinearGradient(0, 0, 0, C.H); gr.addColorStop(0, '#3a2a22'); gr.addColorStop(.6, '#5a3d2a'); gr.addColorStop(1, '#2a1d16'); g.fillStyle = gr; g.fillRect(0, 0, C.W, C.H);
  const r = C.rng(4); const cols = ['#b33c3c', '#2f5d8a', '#e0c070', '#3a3a3a', '#7a4a8a', '#d8d0c0', '#2f7a5a', '#c87a3a'];
  for (let row = 0; row < 6; row++) { const y = 80 + row * 300; g.fillStyle = '#2a1a12'; g.fillRect(0, y + 250, C.W, 26); for (let x = -20; x < C.W; ) { const w = 14 + r() * 26; g.fillStyle = cols[(r() * cols.length) | 0]; g.fillRect(x, y + 40 + r() * 30, w - 3, 210); x += w; } }
  // warm practical lights
  for (const [x, y] of [[200, 300], [880, 520], [520, 1100]]) { const q = g.createRadialGradient(x, y, 0, x, y, 420); q.addColorStop(0, 'rgba(255,200,130,.55)'); q.addColorStop(1, 'rgba(255,200,130,0)'); g.fillStyle = q; g.fillRect(0, 0, C.W, C.H); }
  BG = I.blurCanvas(c, 24); return BG;
}

function draw(g, t) {
  const tex = Pr.sleeveTex(0);
  const hero = key(t, [[0, 23], [.28, 23], [1.22, 0, 'io2']]) + (t > 1.22 ? -C.wob(t - 1.22, 6, 14) * .6 : 0);
  const lid = key(t, [[0, 1], [1.5, 1], [HIT, 0, 'in2']]);
  const camPos = key(t, [[0, [0, 44, 80]], [.25, [0, 44, 80]], [1.3, [2, 40, 70], 'io2'], [HIT, [2, 37, 60], 'io2']]);
  const camLook = key(t, [[0, [0, 41.5, -4]], [.25, [0, 41.5, -4]], [1.3, [0, 24, -12], 'io2'], [HIT, [0, 20, -14], 'io2']]);
  const sh = S.shake(t, HIT, 14, 12);
  const cam = new C.Cam({ pos: camPos, look: camLook, fov: 45, shift: sh });
  Pr.setLight([-.4, .8, .5]);
  I.ST.toLight = [-.45, -.9]; I.ST.shadowTint = '#3a2418'; I.ST.shadeMix = .36; I.ST.inkW = 3;
  g.drawImage(shopBackdrop(), 0, 0);
  // crate & sleeves
  const fr = C.frame([0, 0, 0], 0);
  const cr = Pr.crate(fr, 35, 40, 26, lid, '#7a5532');
  // draw crate back/sides first, sleeves, then front & lid via depth sort: split faces
  const faces = [];
  const sleeves = [];
  for (let i = 0; i < 13; i++) {
    const z = -4.5 - i * 2.3; const y = i === 0 ? hero + 1.2 : 1.2 + Math.sin(i * 7) * .3;
    const sf = C.frame([0, y + SW / 2, z], (i % 3 - 1) * .012);
    sleeves.push(...Pr.box(sf, SW / 2, SW / 2, .18, '#efe7d6', { tex: { f: tex }, cols: { u: '#d9d0bf', l: '#d9d0bf', r: '#d9d0bf' }, lw: 1.1 }));
  }
  const lidFaces = cr.faces.filter((f, k) => k >= 30);
  if (lid > .45) Pr.drawFaces(g, cam, lidFaces);
  Pr.drawFaces(g, cam, cr.faces.filter((f, k) => k >= 6 && k < 30)); // back/sides/bottom
  Pr.drawFaces(g, cam, sleeves);
  Pr.drawFaces(g, cam, cr.faces.filter((f, k) => k < 6)); // front wall
  E.lines3(g, cam, [3, 9, 15, 21].map(y => [[-17.5, y, .05], [17.5, y + .4, .05]]), '#4a321c', .5, .6);
  // the thumb/hand pushing the hero sleeve down, then leaving
  const hx = key(t, [[0, [9, 23 + SW + 1.5, -3.2]], [.28, [9, 23 + SW + 1.5, -3.2]], [1.22, [9, SW + 2.5, -3.2], 'io2'], [1.5, [26, SW + 16, 4], 'in2'], [1.8, [60, SW + 40, 12], 'in2']]);
  if (t < 1.8) {
    const hand = Hn.buildHand({ w: hx, fwd: norm([-.55, -.25, -.8]), nrm: norm([.2, 1, -.2]), th: norm([-.3, .1, 1]), scale: 1.0, side: -1 }, { curl: [.55, .62, .7, .75], spread: .15, thumb: { curl: .15, out: .2, opp: .55 } });
    // thumb lands on the sleeve front
    Hn.drawHand(g, cam, hand, { skin: '#eebf9c', sleeve: { col: '#3d4a5e', r: 4.4, len: 26, cuff: '#d9d4c8' } });
  }
  // lid (with its faces) on top
  if (lid <= .45) Pr.drawFaces(g, cam, lidFaces);
  if (t > 1.5) { const q = cam.p([0, 26, -40]); I.glow(g, q.x, q.y, 500, '#000000', .25 * ss(inv(1.5, HIT, t)), 'source-over'); }
  I.vignette(g, .55, '20,10,5');
}
function black(g, t) { g.fillStyle = '#000'; g.fillRect(0, 0, C.W, C.H); }
module.exports = [{ t0: 0, t1: HIT, name: 'open', draw }, { t0: HIT, t1: HIT + 0.1, name: 'black', draw: black }];
