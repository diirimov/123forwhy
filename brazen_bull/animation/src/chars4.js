// V4 CAST: distinct characters (palettes + head specs + costumes + props + acting poses)
'use strict';
const PAL = {
  // Perillus: weathered, sun-darkened artisan; grey hair and beard; undyed work tunic
  perillus: { lit: Object.assign({}, SKIN_LIT, { skin: '#b07a55', skin2: '#94603f', skinLt: '#d8a07a', skinDk: '#6a3e26', hair: '#9a948c', hairLt: '#d8d2c8', beard: '#8e8880', beardLt: '#d0cac0', cloth: '#b8a888', clothDk: '#7a6a52', border: '#5a4a2a' }),
    shadow: Object.assign({}, SKIN_SHD, { skin: '#33200f', skin2: '#29180c', hair: '#2a2826', hairLt: '#3a3836', beard: '#2a2826', beardLt: '#3a3836', cloth: '#3a3226', clothDk: '#231d15' }) },
  // Phalaris: pale olive aristocrat; jet-black hair; Tyrian purple and gold
  phalaris: { lit: Object.assign({}, SKIN_LIT, { skin: '#d4a882', skin2: '#b88a66', skinLt: '#f0caa6', skinDk: '#8a5a40', lip: '#8a4a48', hair: '#120c0c', hairLt: '#3a2a2a', beard: '#120c0c', cloth: '#ece2cc', clothDk: '#b8a88a', border: '#c8962e', robe: '#5a1a4a', robeLt: '#8a3a72' }),
    shadow: Object.assign({}, SKIN_SHD, { skin: '#3a2618', skin2: '#2e1c12', hair: '#050303', cloth: '#4a4236', clothDk: '#2a241c', robe: '#1a0614', robeLt: '#2a0c22' }) },
  guard: { lit: Object.assign({}, SKIN_LIT, { skin: '#a8704c', skin2: '#8a5838', cloth: '#9a2a1e', clothDk: '#5a140c', border: '#d8a050' }),
    shadow: Object.assign({}, SKIN_SHD, { cloth: '#2a0a06', clothDk: '#1a0604' }) },
  citizen: (k) => ({ lit: Object.assign({}, SKIN_LIT, { cloth: ['#d8c8a0', '#a8582a', '#4a6a7a', '#7a8a4a', '#c8a050'][k % 5], clothDk: ['#8a7a5a', '#6a3014', '#24404a', '#4a5a2a', '#8a6a20'][k % 5] }), shadow: SKIN_SHD }),
};
const SPEC = {
  perillus: { hair: 'bald', beard: 'full', faceW: 1.08, jaw: 1.05, age: 1.0 },
  phalaris: { hair: 'long', beard: 'none', faceW: 0.98, jaw: 1.16, hook: true, lids: 0.25 },
  guard: { hair: 'helmet', beard: 'short', faceW: 1.0 },
  subject: {},
};

// ---------------------------------------------------------------- costumes on the rig
function costumeOverlay(g, C, J, p, t, lag) {
  const r = J.rot, belt = [lerp(J.root[0], J.chest[0], 0.2), lerp(J.root[1], J.chest[1], 0.2)];
  const rB = (dx, dy) => [belt[0] + dx * Math.cos(p.spine) + dy * Math.sin(p.spine), belt[1] - dx * Math.sin(p.spine) + dy * Math.cos(p.spine)];
  if (p.costume === 'apron') {
    // leather work apron (bronze-smith), scorch marks, neck strap
    const ap = [r(J.chest, -90, 150), r(J.chest, 120, 140), rB(150, 40), [lerp(J.nKn[0], J.fKn[0], 0.5) + 80, lerp(J.nKn[1], J.fKn[1], 0.5) - 40], [lerp(J.nKn[0], J.fKn[0], 0.5) - 120, lerp(J.nKn[1], J.fKn[1], 0.5) - 30], rB(-150, 40)];
    g.fillStyle = linGrad(g, J.chest[0], J.chest[1], J.root[0], J.root[1] + 300, [[0, '#6a4426'], [1, '#3a2412']]); g.beginPath(); crPath(g, ap, true, 0.4); g.fill();
    softIn(g, ap, 16, () => { g.fillStyle = 'rgba(0,0,0,0.45)'; g.beginPath(); g.ellipse(J.root[0] + 40, J.root[1] + 120, 90, 50, 0, 0, 6.283); g.fill();
      g.fillStyle = 'rgba(255,220,170,0.18)'; g.beginPath(); g.ellipse(J.chest[0] - 30, J.chest[1] + 220, 70, 120, 0.2, 0, 6.283); g.fill(); });
    brush(g, [r(J.chest, -90, 150), r(J.chest, 10, 20), r(J.chest, 120, 140)], 8, 8, '#3a2412', false);
  }
  if (p.costume === 'royal') {
    // long robe to the ankles + purple himation over the shoulder, gold border
    const robe = [rB(-170, 20), rB(170, 20), [J.nAn[0] + 120, J.nAn[1] - 20], [lerp(J.nAn[0], J.fAn[0], 0.5) + (lag || 0) * 30, Math.max(J.nAn[1], J.fAn[1]) + 10], [J.fAn[0] - 120, J.fAn[1] - 20]];
    g.fillStyle = linGrad(g, 0, belt[1], 0, J.nAn[1], [[0, C.cloth], [1, C.clothDk]]); g.beginPath(); crPath(g, robe, true, 0.4); g.fill();
    g.save(); g.beginPath(); crPath(g, robe, true, 0.4); g.clip(); for (let i = 0; i < 7; i++) { const u = (i + 0.5) / 7; const a = rB(lerp(-150, 150, u), 40), b = [lerp(J.fAn[0] - 100, J.nAn[0] + 100, u), J.nAn[1]];
      g.filter = 'blur(5px)'; brush(g, [a, [lerp(a[0], b[0], 0.5) + Math.sin(t + i) * 6, lerp(a[1], b[1], 0.5)], b], 20, 14, rgba(C.clothDk, 0.7), false); g.filter = 'none'; } g.restore();
    const him = [r(J.chest, 230, 0), r(J.chest, 140, -30), r(J.chest, -60, 60), r(J.chest, -170, 200), rB(-190, 60), rB(-120, 260), rB(60, 300), rB(200, 120), r(J.chest, 240, 160)];
    g.fillStyle = linGrad(g, J.chest[0] - 200, J.chest[1], J.root[0] + 200, J.root[1] + 300, [[0, C.robeLt || '#8a3a72'], [1, C.robe || '#5a1a4a']]); g.beginPath(); crPath(g, him, true, 0.45); g.fill();
    g.save(); g.beginPath(); crPath(g, him, true, 0.45); g.clip();
    for (let k = 0; k < 5; k++) { const a = r(J.chest, 220 - k * 30, 10 + k * 40), b = rB(-160 + k * 70, 200 + k * 20); g.filter = 'blur(6px)'; brush(g, [a, [lerp(a[0], b[0], 0.5) - 20, lerp(a[1], b[1], 0.5)], b], 26, 16, 'rgba(0,0,0,0.35)', false); g.filter = 'none'; }
    g.restore();
    brush(g, curvePts([r(J.chest, 140, -30), r(J.chest, -60, 60), r(J.chest, -170, 200), rB(-190, 60)], 30), 12, 12, C.border, false);
    g.fillStyle = '#e8b85a'; g.beginPath(); g.arc(...r(J.chest, 200, 10), 16, 0, 6.283); g.fill();
  }
  if (p.costume === 'guard') {
    // bronze muscle cuirass over the red tunic, leather pteruges
    const cu = [r(J.chest, -170, 30), r(J.chest, 230, 30), r(J.chest, 200, 220), rB(170, 10), rB(-160, 10), r(J.chest, -160, 220)];
    g.fillStyle = linGrad(g, J.chest[0] - 180, J.chest[1], J.chest[0] + 230, J.root[1], [[0, '#e0b060'], [0.5, '#9a6a30'], [1, '#4a2c12']]); g.beginPath(); crPath(g, cu, true, 0.35); g.fill();
    softIn(g, cu, 14, () => { g.fillStyle = 'rgba(255,235,180,0.5)'; for (const dx of [-60, 60]) { g.beginPath(); g.ellipse(...r(J.chest, dx, 110), 60, 40, 0, 0, 6.283); g.fill(); }
      g.fillStyle = 'rgba(0,0,0,0.4)'; g.beginPath(); g.ellipse(...r(J.chest, 0, 180), 20, 70, 0, 0, 6.283); g.fill(); });
    for (let i = 0; i < 9; i++) { const u = i / 8, a = rB(lerp(-160, 170, u), 10); brush(g, [a, [a[0], a[1] + 120]], 30, 26, i % 2 ? '#5a3a1e' : '#4a2e16', false); }
  }
}
function guardCloak(g, C, J, p, t) {
  const r = J.rot, sw = Math.sin(t * 1.4) * 20;
  const cl = [r(J.chest, -170, 20), r(J.chest, 240, 20), [J.root[0] + 330 + sw, J.root[1] + 700], [J.root[0] + 40 + sw, J.root[1] + 760], [J.root[0] - 230, J.root[1] + 680]];
  g.fillStyle = linGrad(g, 0, J.chest[1], 0, J.root[1] + 760, [[0, '#a8241a'], [1, '#4a0a06']]); g.beginPath(); crPath(g, cl, true, 0.4); g.fill();
}
// ---------------------------------------------------------------- props held in the hand (wrist, angle)
function drawProp(g, C, name, wr, a, t) {
  g.save(); g.translate(wr[0], wr[1]); g.rotate(-a);
  if (name === 'hammer') {
    g.fillStyle = '#5a3a1e'; g.fillRect(-12, 60, 24, 300);
    g.fillStyle = linGrad(g, -70, 330, 70, 400, [[0, '#d0d0c8'], [1, '#4a4a46']]); g.fillRect(-80, 330, 160, 76);
    g.fillStyle = 'rgba(255,255,255,0.5)'; g.fillRect(-80, 332, 160, 8);
  } else if (name === 'spear') {
    g.rotate(a);   // held vertical regardless of the hand
    g.fillStyle = '#6a4a2a'; g.fillRect(-10, -1500, 20, 2300);
    g.fillStyle = linGrad(g, -30, -1720, 30, -1500, [[0, '#f0d8a0'], [1, '#8a6a30']]); g.beginPath(); g.moveTo(0, -1760); g.lineTo(32, -1560); g.lineTo(0, -1500); g.lineTo(-32, -1560); g.closePath(); g.fill();
  } else if (name === 'chisel') {
    g.fillStyle = '#5a3a1e'; g.fillRect(-10, 40, 20, 120); g.fillStyle = '#b8b8b0'; g.fillRect(-7, 160, 14, 110);
  }
  g.restore();
}
// ---------------------------------------------------------------- acting poses
Object.assign(POSES, {
  hammerUp: { spine: -0.05, head: 0.3, nT: { c: [170, -170] }, nB: 1, fT: [-470, 330], fB: 1, nF: [40, G], fF: [-200, G], nFa: -1.5, fFa: -1.4, nHand: 'grip', fHand: 'press', nWa: 2.6, prop: 'hammer' },
  hammerDown: { spine: -0.4, head: 0.5, nT: [-540, 470], nB: 1, fT: [-470, 330], fB: 1, nF: [40, G], fF: [-200, G], nFa: -1.5, fFa: -1.4, nHand: 'grip', fHand: 'press', nWa: 1.4, prop: 'hammer' },
  present: { spine: 0.05, head: -0.1, nT: { c: [-560, 260] }, nB: 1, fT: { c: [-150, 560] }, fB: -1, nF: [60, G], fF: [-160, G], nFa: -1.5, fFa: -1.5, nHand: 'splay', fHand: 'relax', nWa: 0.3 },
  proud: { spine: 0.1, head: -0.12, nT: { c: [170, 470] }, nB: -1, fT: { c: [-120, 470] }, fB: -1, nF: [70, G], fF: [-150, G], nFa: -1.5, fFa: -1.5, nHand: 'fist', fHand: 'fist' },
  pull: { spine: 0.22, head: -0.2, nT: { c: [320, 60] }, nB: -1, fT: { c: [260, 200] }, fB: -1, nF: [-60, G], fF: [180, G], nFa: -1.5, fFa: -1.3, nHand: 'fist', fHand: 'fist' },
  seated: { y: 470, spine: 0.06, head: 0.02, nT: { c: [-120, 440] }, nB: -1, fT: { c: [-220, 430] }, fB: -1, nF: [-480, G], fF: [-400, G], nKB: 1, fKB: 1, nFa: -1.5, fFa: -1.5, nHand: 'relax', fHand: 'relax' },
  seatedPoint: { y: 470, spine: 0.02, head: 0.08, nT: { c: [-660, 140] }, nB: 1, fT: { c: [-220, 430] }, fB: -1, nF: [-480, G], fF: [-400, G], nKB: 1, fKB: 1, nFa: -1.5, fFa: -1.5, nHand: 'point', fHand: 'relax', nWa: 0.1 },
  standPoint: { spine: 0.0, head: 0.05, nT: { c: [-680, 160] }, nB: 1, fT: { c: [-150, 560] }, fB: -1, nF: [60, G], fF: [-150, G], nFa: -1.5, fFa: -1.5, nHand: 'point', fHand: 'relax' },
  guardStand: { spine: 0.0, head: 0.0, nT: { c: [140, 300] }, nB: -1, fT: { c: [-150, 560] }, fB: -1, nF: [60, G], fF: [-120, G], nFa: -1.5, fFa: -1.5, nHand: 'grip', fHand: 'relax', prop: 'spear', propBehind: false, nWa: Math.PI },
  guardStep: { spine: -0.12, head: 0.1, nT: { c: [100, 280] }, nB: -1, fT: { c: [-260, 460] }, fB: -1, nF: [-240, G], fF: [180, G], nFa: -1.5, fFa: -1.2, nHand: 'grip', fHand: 'fist', prop: 'spear', nWa: Math.PI },
  fear: { spine: 0.14, head: -0.08, nT: { c: [-240, 200] }, nB: 1, fT: { c: [-300, 260] }, fB: 1, nF: [120, G], fF: [-60, G], nFa: -1.5, fFa: -1.5, nHand: 'splay', fHand: 'splay' },
});
function cast(name, pose, extra = {}) { return Object.assign({}, typeof pose === 'string' ? blendPose(pose, pose, 0) : pose, { costume: { perillus: 'apron', phalaris: 'royal', guard: 'guard' }[name] || null, spec: SPEC[name] || {} }, extra); }
function drawChar(ctx, name, pose, t, X, opt = {}) {
  const pal = name === 'citizen' ? PAL.citizen(opt.k || 0) : (PAL[name] || { lit: SKIN_LIT, shadow: SKIN_SHD });
  litRender(ctx, (g, C) => { g.save(); g.translate(X[0], X[1]); g.scale(X[2] * (opt.flip ? -1 : 1), X[2]); figure(g, C, pose, t, { lag: opt.lag || 0 }); g.restore(); },
    opt.mask || ((m) => radialMask(m, X[0] - 260 * X[2], X[1] - 700 * X[2], 30, 1400 * X[2], opt.key ?? 0.95)),
    { lit: pal.lit, shadow: pal.shadow, rim: { dx: (opt.flip ? -1 : 1) * 4 * Math.max(0.5, X[2] / 0.6), dy: 1, col: opt.rimCol || '#ffb060', a: opt.rimA ?? 0.8 } });
}
function headChar(ctx, name, st, t, x, y, sc, opt = {}) {
  const pal = PAL[name] || { lit: SKIN_LIT, shadow: SKIN_SHD };
  litRender(ctx, (g, C) => { g.save(); g.translate(x, y); g.scale(sc * (opt.flip ? -1 : 1), sc); g.rotate(opt.rot || 0); bust34(g, C, st); head34(g, C, Object.assign({ t, spec: SPEC[name] }, st)); g.restore(); },
    opt.mask || ((m) => radialMask(m, x - 200 * sc, y - 260 * sc, 30, 900 * sc, opt.key ?? 0.95)),
    { lit: pal.lit, shadow: pal.shadow, rim: { dx: (opt.flip ? -1 : 1) * 6, dy: 0, col: opt.rimCol || '#ffb060', a: opt.rimA ?? 0.85 } });
}
TESTS.cast = (ctx, t) => {
  ctx.fillStyle = linGrad(ctx, 0, 0, 0, H, [[0, '#2a211a'], [1, '#100c09']]); ctx.fillRect(0, 0, W, H);
  ctx.font = '800 30px Inter'; ctx.fillStyle = '#e8d6b8'; ctx.textAlign = 'center'; ctx.fillText('V4 CAST — MODEL SHEET', W / 2, 60);
  headChar(ctx, 'perillus', { look: [-0.3, 0], brow: 0.2 }, t, 200, 330, 0.62); headChar(ctx, 'phalaris', { look: [-0.4, 0] }, t, 540, 330, 0.62); headChar(ctx, 'subject', { look: [-0.3, 0] }, t, 880, 330, 0.62);
  ctx.font = '600 22px Inter'; ctx.fillStyle = '#c8b090'; ctx.fillText('PERILLUS — bronze sculptor', 200, 600); ctx.fillText('PHALARIS — tyrant of Akragas', 540, 600); ctx.fillText('THE SUBJECT', 880, 600);
  const row = [['perillus', 'hammerUp'], ['perillus', 'present'], ['phalaris', 'seatedPoint'], ['guard', 'guardStand'], ['phalaris', 'standPoint']];
  row.forEach(([n, ps], i) => { const x = 110 + i * 215, y = 1000; drawChar(ctx, n, secondary(cast(n, ps), t, { breath: 0.4 }), t, [x, y, 0.17]); ctx.fillText(ps.toUpperCase(), x, 1250); });
  headChar(ctx, 'perillus', { look: [-0.5, 0.1], brow: 0.9, mouth: 0.5 }, t, 270, 1560, 0.55); ctx.fillText('PERILLUS — FEAR', 270, 1860);
  headChar(ctx, 'phalaris', { look: [-0.6, 0.1], brow: 0.5, mouth: 0.05 }, t, 780, 1560, 0.55); ctx.fillText('PHALARIS — COLD VERDICT', 780, 1860);
};
