// ===================================================================== cast2.js
'use strict';
// better expression blending for pose keys
poseLerp = function (a, b, k) {
  const r = Object.assign({}, a);
  for (const kk in b) {
    if (kk === 'expr') {
      const ea = a.expr || EXPR.neutral, eb = b.expr || EXPR.neutral, e = {};
      for (const f of new Set([...Object.keys(ea), ...Object.keys(eb)])) { const va = ea[f], vb = eb[f]; e[f] = (typeof va === 'number' && typeof vb === 'number') ? lerp(va, vb, k) : (k > .5 ? (vb ?? va) : (va ?? vb)); }
      r.expr = e;
    } else if (typeof b[kk] === 'number' && typeof a[kk] === 'number') r[kk] = lerp(a[kk], b[kk], k);
    else if (k > .5 || a[kk] === undefined) r[kk] = b[kk];
  }
  return r;
};
const SK = { fair: '#f3c9a8', peach: '#eeb58e', tan: '#d99a6c', ruddy: '#e8a582', olive: '#c98e62', brown: '#9c6640', pale: '#e9d2bd', grey: '#cfb4a0' };

// ---------------------------------------------------------------- hair (generic, per view)
function skullPts(view, u, k = 1.07) {
  const ch = { face: {} }, e = EXPR.neutral;
  const pts = (view === 'p' ? headProfile(ch, e) : view === 'q' ? head34(ch, e) : headFront(ch, e)).pts;
  return pts.map(p => [p[0] * u * k, (p[1] + .5) * u * k - .5 * u]);
}
const HAIRLINE = {
  p: [[.36, -.86], [.22, -.87], [.12, -.82], [.05, -.72], [.02, -.6], [.0, -.5], [.03, -.42], [-.03, -.4], [-.07, -.55], [-.18, -.62], [-.27, -.42], [-.33, -.14], [-.8, -.1], [-.8, -1.3], [.6, -1.3]],
  q: [[.44, -.78], [.3, -.85], [.1, -.86], [-.1, -.8], [-.2, -.7], [-.25, -.56], [-.27, -.44], [-.31, -.42], [-.33, -.56], [-.42, -.6], [-.44, -.3], [-.38, -.12], [-.9, -.1], [-.9, -1.3], [.6, -1.3]],
  f: [[-.46, -.4], [-.42, -.62], [-.3, -.8], [-.1, -.84], [.1, -.84], [.3, -.8], [.42, -.62], [.46, -.4], [.6, -.4], [.6, -1.3], [-.6, -1.3], [-.6, -.4]],
  b: [[-.6, -.12], [.6, -.12], [.6, -1.3], [-.6, -1.3]],
};
function hairShort(col, o = {}) {
  return (c, view, u, lw, e) => {
    const vol = o.vol || 1.07, sk2 = skullPts(view, u, vol);
    const hl = (HAIRLINE[view] || HAIRLINE.f).map(p => [p[0] * u, (p[1] + (o.recede || 0) * (p[1] < -.75 ? .06 : 0)) * u]);
    c.save(); shapePath(c, sk2); c.clip();
    c.beginPath(); hl.forEach((p, i) => i ? c.lineTo(p[0], p[1]) : c.moveTo(p[0], p[1])); c.closePath(); c.fillStyle = col; c.fill();
    c.strokeStyle = rgba(tint(col, .35), .5); c.lineWidth = lw * .6;
    for (let i = 0; i < 9; i++) { c.beginPath(); c.moveTo((-.4 + i * .09) * u, -1.05 * u); c.quadraticCurveTo((-.3 + i * .1) * u, -.85 * u, (-.38 + i * .08) * u, -.62 * u); c.stroke(); }
    c.restore();
    c.save(); c.beginPath(); hl.forEach((p, i) => i ? c.lineTo(p[0], p[1]) : c.moveTo(p[0], p[1])); c.closePath(); c.clip(); shapePath(c, sk2); c.lineWidth = lw; c.strokeStyle = OL; c.stroke(); c.restore();
    if (o.curls) for (let i = 0; i < 9; i++) { const a = PI * (1.05 + i * .11); ell(c, Math.cos(a) * .5 * u - (view === 'p' ? .05 * u : 0), -.52 * u + Math.sin(a) * .5 * u, .09 * u, .085 * u, col, lw * .7); }
  };
}
function hairLong(col) {    // falls behind the shoulders (drawn before the head)
  return (c, view, u, lw) => {
    if (view === 'p') fillOL(c, [[.1 * u, -.95 * u], [-.42 * u, -.85 * u], [-.55 * u, -.4 * u], [-.5 * u, .35 * u], [-.2 * u, .4 * u], [-.12 * u, -.1 * u]], col, lw);
    else fillOL(c, [[-.5 * u, -.8 * u], [-.6 * u, -.2 * u], [-.55 * u, .38 * u], [.55 * u, .38 * u], [.6 * u, -.2 * u], [.5 * u, -.8 * u], [0, -1.05 * u]], col, lw);
  };
}
// ---------------------------------------------------------------- hats
function flatCap(col) {
  return (c, view, u, lw) => {
    if (view === 'p') { fillOL(c, [[-.48 * u, -.62 * u], [-.42 * u, -.95 * u], [-.05 * u, -1.1 * u], [.32 * u, -1.0 * u], [.42 * u, -.86 * u], [.62 * u, -.84 * u], [.62 * u, -.78 * u], [.2 * u, -.76 * u], [-.3 * u, -.7 * u]], col, lw); line(c, [[.2 * u, -.78 * u], [.6 * u, -.8 * u]], lw * .6, shade(col, .4)); }
    else if (view === 'b') fillOL(c, [[-.52 * u, -.7 * u], [-.48 * u, -.98 * u], [0, -1.12 * u], [.48 * u, -.98 * u], [.52 * u, -.7 * u]], col, lw);
    else { const o = view === 'q' ? .08 : 0; fillOL(c, [[-.5 * u, -.7 * u], [-.48 * u, -.98 * u], [(-.05 + o) * u, -1.12 * u], [.46 * u, -.98 * u], [.52 * u, -.74 * u], [(.25 + o) * u, -.7 * u]], col, lw); fillOL(c, [[(-.36 + o) * u, -.74 * u], [(.4 + o) * u, -.76 * u], [(.46 + o) * u, -.66 * u], [(-.3 + o) * u, -.64 * u]], shade(col, .25), lw); }
    c.save(); c.globalAlpha = .25; for (let i = 0; i < 5; i++) line(c, [[(-.4 + i * .18) * u, -1.05 * u], [(-.3 + i * .18) * u, -.75 * u]], lw * .5, tint(col, .5)); c.restore();
  };
}
function nightcap(col, stripe) {
  return (c, view, u, lw, e) => {
    const d = view === 'p' ? -1 : 1;
    fillOL(c, [[-.5 * u, -.6 * u], [-.48 * u, -.95 * u], [0, -1.12 * u], [.42 * u, -1.0 * u], [.5 * u, -.62 * u], [.2 * u, -.7 * u], [-.2 * u, -.7 * u]], col, lw);
    fillOL(c, [[-.3 * u, -1.0 * u], [-.7 * d * u, -.9 * u], [-1.0 * d * u, -.55 * u], [-.88 * d * u, -.5 * u], [-.6 * d * u, -.7 * u], [-.2 * u, -.85 * u]], col, lw);
    if (stripe) for (let i = 0; i < 3; i++) line(c, [[(-.35 + i * .3) * u, -1.02 * u], [(-.3 + i * .32) * u, -.66 * u]], lw * 1.6, stripe);
    ell(c, -.98 * d * u, -.5 * u, .07 * u, .07 * u, '#f5efe2', lw);
    fillOL(c, [[-.52 * u, -.6 * u], [-.5 * u, -.72 * u], [.5 * u, -.72 * u], [.52 * u, -.6 * u]], tint(col, .55), lw);
  };
}
function tudorBonnet(col, feather, jewel = '#f0c040') {
  return (c, view, u, lw, e) => {
    const o = view === 'p' ? .12 : view === 'q' ? .06 : 0;
    fillOL(c, [[(-.62 + o) * u, -.86 * u], [(-.5 + o) * u, -1.06 * u], [o * u, -1.14 * u], [(.58 + o) * u, -1.05 * u], [(.68 + o) * u, -.9 * u], [(.1 + o) * u, -.84 * u]], col, lw);
    fillOL(c, [[(-.56 + o) * u, -.9 * u], [(.64 + o) * u, -.92 * u], [(.62 + o) * u, -.82 * u], [(-.56 + o) * u, -.8 * u]], shade(col, .3), lw * .8);
    for (let i = 0; i < 5; i++) ell(c, (-.4 + o + i * .22) * u, -.86 * u, .025 * u, .025 * u, jewel);
    if (feather) { const w = Math.sin((e.t || 0) * 5) * .08; c.save(); c.translate((.45 + o) * u, -1.02 * u); c.rotate(-.9 + w); fillOL(c, [[0, 0], [.1 * u, -.5 * u], [.28 * u, -.95 * u], [.06 * u, -.85 * u], [-.08 * u, -.45 * u]], feather, lw * .8); line(c, [[0, 0], [.2 * u, -.85 * u]], lw * .5, shade(feather, .3)); c.restore(); }
  };
}
function crownHat(c, view, u, lw) {
  const o = view === 'p' ? .1 : view === 'q' ? .05 : 0, w = view === 'p' ? .42 : .5;
  fillOL(c, [[(o - w) * u, -.82 * u], [(o - w) * u, -.98 * u], [(o + w) * u, -.98 * u], [(o + w) * u, -.82 * u]], '#7a1424', lw);
  const pts = [[(o - w) * u, -.86 * u], [(o - w - .03) * u, -1.28 * u], [(o - w * .5) * u, -1.1 * u], [o * u, -1.38 * u], [(o + w * .5) * u, -1.1 * u], [(o + w + .03) * u, -1.28 * u], [(o + w) * u, -.86 * u]];
  c.beginPath(); pts.forEach((p, i) => i ? c.lineTo(...p) : c.moveTo(...p)); c.closePath(); c.fillStyle = lg(c, 0, -1.4 * u, 0, -.8 * u, [[0, '#fff2a0'], [1, '#d0901c']]); c.fill(); c.lineWidth = lw; c.strokeStyle = OL; sk(c); c.stroke();
  for (const [x, cc] of [[-.5, '#c8203a'], [0, '#2a5ad0'], [.5, '#1a9a60']]) ell(c, (o + x * w) * u, -.94 * u, .05 * u, .055 * u, cc, lw * .5);
  for (const x of [-1.07, 0, 1.07]) ell(c, (o + x * w) * u, (x === 0 ? -1.4 : -1.3) * u, .04 * u, .04 * u, '#fff8d0', lw * .5);
  ell(c, (o - w * .5) * u, -1.12 * u, .03 * u, .03 * u, '#fff8d0'); ell(c, (o + w * .5) * u, -1.12 * u, .03 * u, .03 * u, '#fff8d0');
}
function hoodHat(col) {   // hood framing a visible face
  return (c, view, u, lw) => {
    if (view === 'b') { fillOL(c, [[-.62 * u, .2 * u], [-.66 * u, -.7 * u], [-.3 * u, -1.18 * u], [.3 * u, -1.18 * u], [.66 * u, -.7 * u], [.62 * u, .2 * u]], col, lw); return; }
    if (view === 'p') {
      fillOL(c, [[-.62 * u, .25 * u], [-.66 * u, -.5 * u], [-.48 * u, -1.0 * u], [-.05 * u, -1.22 * u], [.38 * u, -1.1 * u], [.56 * u, -.85 * u], [.5 * u, -.78 * u], [.3 * u, -.95 * u], [-.05 * u, -1.0 * u], [-.3 * u, -.8 * u], [-.36 * u, -.4 * u], [-.2 * u, -.05 * u], [-.1 * u, .25 * u]], col, lw);
      line(c, [[.3 * u, -.95 * u], [.5 * u, -.8 * u]], lw * .6, shade(col, .4)); return;
    }
    const o = view === 'q' ? .07 : 0;
    fillOL(c, [[-.72 * u, .25 * u], [-.74 * u, -.55 * u], [(-.5 + o) * u, -1.05 * u], [o * u, -1.24 * u], [(.52 + o) * u, -1.05 * u], [(.7 + o) * u, -.55 * u], [(.66 + o) * u, .25 * u], [(.46 + o) * u, .1 * u], [(.52 + o) * u, -.6 * u], [(.38 + o) * u, -.92 * u], [o * u, -1.02 * u], [(-.38 + o) * u, -.92 * u], [(-.52 + o) * u, -.6 * u], [(-.48 + o) * u, .1 * u]], col, lw);
    line(c, [[(-.4 + o) * u, -.85 * u], [(-.48 + o) * u, -.3 * u]], lw * .5, shade(col, .4));
  };
}
function gableHood(col, trim) {
  return (c, view, u, lw) => {
    const o = view === 'p' ? .05 : view === 'q' ? .03 : 0;
    fillOL(c, [[(-.6 + o) * u, .15 * u], [(-.58 + o) * u, -.7 * u], [o * u, -1.25 * u], [(.58 + o) * u, -.7 * u], [(.6 + o) * u, .15 * u], [(.46 + o) * u, .1 * u], [(.46 + o) * u, -.65 * u], [o * u, -1.05 * u], [(-.46 + o) * u, -.65 * u], [(-.46 + o) * u, .1 * u]], col, lw);
    line(c, [[(-.46 + o) * u, -.62 * u], [o * u, -1.03 * u], [(.46 + o) * u, -.62 * u]], lw * 2.2, trim);
  };
}
function coif(col) {
  return (c, view, u, lw) => { const o = view === 'p' ? .05 : 0; fillOL(c, [[(-.56 + o) * u, -.2 * u], [(-.55 + o) * u, -.85 * u], [o * u, -1.1 * u], [(.5 + o) * u, -.88 * u], [(.52 + o) * u, -.62 * u], [(.38 + o) * u, -.75 * u], [o * u, -.9 * u], [(-.4 + o) * u, -.7 * u], [(-.44 + o) * u, -.2 * u]], col, lw); };
}
// ---------------------------------------------------------------- beards / moustaches
function beardFull2(col) {
  return (c, view, u, lw, e, H) => {
    const d = (e.open || 0);
    if (view === 'p') { const J = H.J; fillOL(c, [[-.06 * u, -.46 * u], [.02 * u, -.3 * u], [.2 * u, -.36 * u], ...[[.3, -.33], [.36, -.22], [.44, -.15], [.4, -.02], [.2, .06], [-.02, -.02], [-.14, -.16]].map(p => { const q = J(p); return [q[0] * u, q[1] * u]; })], col, lw); fillOL(c, [[.25 * u, -.355 * u], [.42 * u, -.34 * u], [.46 * u, -.27 * u], [.33 * u, -.3 * u]], col, lw * .8); return; }
    const o = view === 'q' ? .1 : 0;
    fillOL(c, [[(-.42 + o * .5) * u, -.46 * u], [(-.4 + o * .5) * u, -.2 * u], [(-.2 + o) * u, (.02 + d * .11) * u], [o * u, (.1 + d * .11) * u], [(.24 + o) * u, (.02 + d * .11) * u], [(.42 + o * .3) * u, -.2 * u], [(.44 + o * .2) * u, -.46 * u], [(.3 + o) * u, -.3 * u], [(o) * u, (-.18 + d * .1) * u], [(-.28 + o) * u, -.3 * u]], col, lw);
    fillOL(c, [[(-.16 + o) * u, -.32 * u], [o * u, -.35 * u], [(.18 + o) * u, -.32 * u], [(.22 + o) * u, -.27 * u], [o * u, -.3 * u], [(-.2 + o) * u, -.27 * u]], col, lw * .8);
  };
}
function tache2(col, big = 1) {
  return (c, view, u, lw) => {
    if (view === 'p') { fillOL(c, [[.3 * u, -.35 * u], [.42 * u, -.345 * u], [.45 * u, -.3 * u], [.28 * u, -.3 * u]], col, lw * .8); return; }
    const o = view === 'q' ? .15 : 0;
    fillOL(c, [[(o - .2 * big) * u, -.27 * u], [(o - .1) * u, -.33 * u], [o * u, -.32 * u], [(o + .1) * u, -.33 * u], [(o + .2 * big) * u, -.27 * u], [(o + .1) * u, -.29 * u], [o * u, -.295 * u], [(o - .1) * u, -.29 * u]], col, lw * .8);
  };
}
function goatee(col) {
  return (c, view, u, lw, e, H) => {
    if (view === 'p') { const J = H.J; const q = [[.32, -.2], [.42, -.17], [.38, -.06], [.3, -.1]].map(p => { const r = J(p); return [r[0] * u, r[1] * u]; }); fillOL(c, q, col, lw * .8); return; }
    const o = view === 'q' ? .15 : 0, d = (e.open || 0) * .11;
    fillOL(c, [[(o - .08) * u, (-.12 + d) * u], [(o + .08) * u, (-.12 + d) * u], [(o + .04) * u, (.0 + d) * u], [(o - .04) * u, (.0 + d) * u]], col, lw * .8);
  };
}

// ---------------------------------------------------------------- costumes
// levels: [lev, W, Df, Db]  (W = front half width; Df/Db = profile depths)
function costume(o) { return Object.assign({ levels: [], flare: 1 }, o); }
function frame(H, uu, lev) {   // map costume coords (uu: -1 back .. +1 front, lev) to local xy
  const { hip, up, rt, T } = H;
  const base = [hip[0] + up[0] * T * lev, hip[1] + up[1] * T * lev];
  return [base[0] + rt[0] * uu * 60, base[1] + rt[1] * uu * 60];
}
function buttons(H, x, levs, col, r = 6) { for (const l of levs) { const p = frame(H, x, l); ell(H.c, p[0], p[1], r, r, col, H.lw * .5); } }
function vline(H, x, l0, l1, col, w) { const a = frame(H, x, l0), b = frame(H, x, l1); line(H.c, [a, b], w, col); }

const BODY2 = {
  // hh head height; 7-ish heads tall
  lanky: { hh: 95, torso: 205, thigh: 158, shin: 156, foot: 70, upperArm: 128, foreArm: 116, hand: 58, shW: 150, hipW: 92, armW: 36, legW: 44, neckW: 34 },
  stocky: { hh: 101, torso: 200, thigh: 140, shin: 138, foot: 74, upperArm: 118, foreArm: 108, hand: 62, shW: 176, hipW: 120, armW: 44, legW: 52, neckW: 44 },
  slim: { hh: 92, torso: 196, thigh: 150, shin: 150, foot: 66, upperArm: 120, foreArm: 110, hand: 56, shW: 144, hipW: 90, armW: 34, legW: 40, neckW: 32 },
  king: { hh: 101, torso: 210, thigh: 138, shin: 134, foot: 74, upperArm: 122, foreArm: 110, hand: 62, shW: 230, hipW: 150, armW: 52, legW: 52, neckW: 48 },
  tall: { hh: 95, torso: 210, thigh: 162, shin: 162, foot: 70, upperArm: 130, foreArm: 120, hand: 60, shW: 140, hipW: 88, armW: 34, legW: 40, neckW: 32 },
  woman: { hh: 90, torso: 182, thigh: 140, shin: 140, foot: 60, upperArm: 110, foreArm: 100, hand: 50, shW: 122, hipW: 104, armW: 30, legW: 40, neckW: 28 },
  boy: { hh: 88, torso: 128, thigh: 96, shin: 94, foot: 52, upperArm: 82, foreArm: 74, hand: 42, shW: 104, hipW: 76, armW: 28, legW: 34, neckW: 26 },
};

const CAST2 = {};
// ---- Ned the knocker-up: lanky, confident, long nose, tweed frock coat
CAST2.knocker = { name: 'Ned', skin: SK.ruddy, body: BODY2.lanky, hairCol: '#6a3a1c',
  face: { nose: 'long', noseLen: .14, noseDrop: .03, chin: .03, jaw: .92, stubble: '#6a4430', iris: '#3f6f4a', browT: 1.25, cheeks: .35, forehead: .02 },
  col: { body: '#8a5a32', sleeve: '#7e512c', legs: '#4a4c58', shoes: '#2e1e14' },
  hair: hairShort('#6a3a1c'), hat: flatCap('#5d6b58'),
  costume: costume({
    levels: [[-.62, 82, 60, 92], [-.3, 64, 50, 62], [0, 52, 44, 46], [.42, 50, 46, 42], [.75, 66, 52, 46], [.93, 76, 34, 40], [1.03, 55, 27, 34], [1.08, 22, 18, 22]],
    detail: (H, back) => { const { c, lw } = H; c.globalAlpha = .18; for (let i = -10; i <= 10; i++) vline(H, i * .12, -.7, 1.1, '#3a2010', 2); c.globalAlpha = 1;
      if (!back) { // waistcoat + buttons + lapel + patch
        const a = frame(H, .25, 1.0), b = frame(H, .6, .45), d = frame(H, -.05, .45), e = frame(H, .1, 1.0);
        fillOL(c, [e, a, b, d], '#6a3a3a', lw * .7); buttons(H, .3, [.55, .7, .85], '#e0c070', 5);
        const p = frame(H, -.45, .1); rrect(c, p[0] - 18, p[1] - 18, 36, 36, 6, '#a88a5a', lw * .5); }
    },
    collar: (H, back) => { const u = H.u; fillOL(H.c, [[-.42 * u, .18 * u], [-.36 * u, -.06 * u], [.4 * u, -.06 * u], [.46 * u, .2 * u], [0, .3 * u]], '#c8423a', H.lw * .9); const sw = H.p.swing * 40 + Math.sin(H.t * 7) * 5; fillOL(H.c, [[.12 * u, .2 * u], [.3 * u, .22 * u], [.3 * u - sw, .82 * u], [.1 * u - sw, .85 * u]], '#b03a32', H.lw * .9); },
    cuff: (H, A, near) => { const d = [A[2][0] - A[1][0], A[2][1] - A[1][1]], L = Math.hypot(...d); const p = [A[2][0] - d[0] / L * 14, A[2][1] - d[1] / L * 14]; ell(H.c, p[0], p[1], 20, 20, near ? '#6a4224' : '#4a2e1a', H.lw * .7); },
  }) };
// ---- Alf, the sleeping worker
CAST2.sleeper = { name: 'Alf', skin: SK.peach, body: BODY2.stocky, hairCol: '#4a3020',
  face: { nose: 'bulb', noseLen: .1, chin: -.01, jaw: 1.08, stubble: '#5a4030', iris: '#6a4b30', cheeks: .55, browT: 1.3 },
  col: { body: '#ece4d4', sleeve: '#e4dccc', legs: '#e4dccc', shoes: '#d99a7a' }, hair: hairShort('#4a3020', { recede: 1 }), hat: nightcap('#5b86c4', '#f3efe4'),
  costume: costume({ levels: [[-.9, 92, 80, 84], [0, 70, 60, 62], [.45, 74, 66, 58], [.8, 84, 64, 54], [.93, 88, 42, 44], [1.03, 63, 34, 37], [1.08, 26, 20, 24]],
    detail: (H) => { for (let i = -8; i <= 8; i++) vline(H, i * .15, -1, 1.1, rgba('#5b86c4', .35), 6); buttons(H, .35, [.75, .9], '#fff', 5); } }) };
// ---- the King: enormous padded Tudor silhouette
CAST2.king = { name: 'The King', skin: SK.ruddy, body: BODY2.king, hairCol: '#a5552a', lw: 4.6,
  face: { nose: 'roman', noseLen: .1, chin: .02, jaw: 1.15, iris: '#4a3020', browCol: '#8a4420', browT: 1.5, cheeks: .7, beard: beardFull2('#b05a2a'), browRidge: .02 },
  col: { body: '#9a1c2c', sleeve: '#d8a83a', legs: '#f2ead8', shoes: '#3a1a18' }, hair: hairShort('#a5552a'), hat: crownHat,
  costume: costume({ flare: 1.15, levels: [[-.62, 150, 130, 150], [-.3, 128, 112, 120], [0, 118, 108, 96], [.45, 122, 110, 90], [.8, 140, 96, 92], [.93, 150, 66, 70], [1.03, 108, 53, 60], [1.08, 40, 30, 36]],
    detail: (H, back) => { const { c, lw } = H;
      const L = frame(H, -.95, 1.05), L2 = frame(H, -1.8, -.7), R = frame(H, .95, 1.05), R2 = frame(H, 1.8, -.7);
      fillOL(c, [[L[0] - 70, L[1]], L, [L2[0] + 40, L2[1]], [L2[0] - 60, L2[1]]], '#f2ead8', lw * .7);   // fur-lined gown edges
      fillOL(c, [R, [R[0] + 70, R[1]], [R2[0] + 60, R2[1]], [R2[0] - 40, R2[1]]], '#f2ead8', lw * .7);
      for (let i = 0; i < 26; i++) { const p = frame(H, (i % 2 ? -1.15 : 1.15), 1 - i * .07); ell(c, p[0], p[1], 3, 3, '#2a2018'); }
      if (!back) { for (let i = -2; i <= 2; i++) vline(H, i * .25, .05, .95, '#f0c040', 3); for (let i = 0; i < 4; i++) { const a = frame(H, -.6, .15 + i * .22), b = frame(H, .6, .15 + i * .22); line(c, [a, b], 2, rgba('#f0c040', .7)); }
        for (let i = 0; i < 11; i++) { const a = PI * (.12 + i * .076); const p = frame(H, Math.cos(a) * 1.0, .98 - Math.sin(a) * .42); ell(c, p[0], p[1], 9, 7, '#f0c040', lw * .4); }
        const m = frame(H, 0, .52); ell(c, m[0], m[1], 18, 18, '#f0c040', lw * .6); ell(c, m[0], m[1], 8, 8, '#c8203a'); } },
    puff: (H, A, near, sleeve) => { const { c, lw } = H; const m = [(A[0][0] + A[1][0]) / 2, (A[0][1] + A[1][1]) / 2]; const a = Math.atan2(A[1][1] - A[0][1], A[1][0] - A[0][0]);
      c.save(); c.translate(m[0], m[1]); c.rotate(a); ell(c, 8, 0, 64, 44, near ? '#d8a83a' : '#b08a2a', lw); for (let i = -2; i <= 2; i++) { ell(c, 8 + i * 22, 0, 5, 32, '#9a1c2c'); } c.restore(); },
    cuff: (H, A) => { ell(H.c, A[2][0], A[2][1], 20, 16, '#f2ead8', H.lw * .6); },
    collar: (H) => { const u = H.u; fillOL(H.c, [[-.9 * u, .32 * u], [-.6 * u, -.02 * u], [.6 * u, -.02 * u], [.9 * u, .32 * u], [0, .2 * u]], '#f2ead8', H.lw * .9); },
  }) };
// ---- the Groom of the Stool: slim, elegant, clever
const groomCostume = (main, trim, slash, rich) => costume({ flare: 1.25, levels: [[-.42, 92, 78, 84], [-.2, 78, 64, 70], [0, 58, 48, 46], [.42, 56, 48, 40], [.78, 68, 52, 42], [.93, 76, 36, 38], [1.03, 55, 29, 32], [1.08, 22, 18, 20]],
  detail: (H, back) => { const { c, lw } = H;
    for (let i = -5; i <= 5; i++) vline(H, i * .22, .15, .95, slash, 7);
    vline(H, 0, -.4, 1.0, trim, 5); buttons(H, 0, [.3, .45, .6, .75, .9], trim, 5);
    const w = frame(H, -1.2, .02), w2 = frame(H, 1.2, .02); line(c, [w, w2], 12, trim);
    if (rich) { for (let i = 0; i < 9; i++) { const a = PI * (.15 + i * .09); const p = frame(H, Math.cos(a) * .85, .98 - Math.sin(a) * .35); ell(c, p[0], p[1], 8, 6, '#f6d050', lw * .4); } const m = frame(H, 0, .6); ell(c, m[0], m[1], 14, 14, '#f6d050', lw * .5); ell(c, m[0], m[1], 6, 6, '#3a7ad0'); } },
  puff: (H, A, near, sleeve) => { const { c, lw } = H; const m = [(A[0][0] * .35 + A[1][0] * .65), (A[0][1] * .35 + A[1][1] * .65)]; const a = Math.atan2(A[1][1] - A[0][1], A[1][0] - A[0][0]);
    segment(c, A[0], A[1], 22, 24, 17, near ? sleeve : shade(sleeve, .2), lw, .2, .3);
    c.save(); c.translate(m[0], m[1]); c.rotate(a); ell(c, 0, 0, 36, 27, near ? main : shade(main, .2), lw); for (let i = -1; i <= 1; i++) ell(c, i * 16, 0, 4, 20, slash); c.restore(); },
  cuff: (H, A) => { ell(H.c, A[2][0], A[2][1] - 4, 15, 10, '#f7f1e4', H.lw * .6); },
  collar: (H) => { const u = H.u; for (let i = -3; i <= 3; i++) ell(H.c, i * .1 * u, .08 * u, .07 * u, .09 * u, '#f7f1e4', H.lw * .5); },
  over: (H) => { const { c, lw, J } = H; // short skirt pleats (peplum) over trunk hose
    const a = frame(H, -1.35, -.02), b = frame(H, 1.35, -.02), d = frame(H, 1.55, -.42), e = frame(H, -1.55, -.42);
    fillOL(c, [a, b, d, e], shade(main, .1), lw * .8, .2); for (let i = 1; i < 6; i++) { const p = frame(H, -1.35 + i * .45, -.02), q = frame(H, -1.55 + i * .52, -.42); line(c, [p, q], 2, rgba(OL, .5)); } },
});
CAST2.groom = { name: 'Thomas, Groom of the Stool', skin: SK.fair, body: BODY2.slim, hairCol: '#3a2214',
  face: { nose: 'roman', noseLen: .08, chin: .02, jaw: .9, iris: '#3a6aa0', eyeS: 1.08, browT: 1.1, browCol: '#3a2214', cheeks: .3, beard: goatee('#3a2214'), tache: tache2('#3a2214', .8) },
  col: { body: '#1f6e6a', sleeve: '#f2ead8', legs: '#f4eee2', shoes: '#1e1614' }, hair: hairShort('#3a2214', { curls: true }), hat: tudorBonnet('#18202e', '#f6f1e6'),
  costume: groomCostume('#1f6e6a', '#d8a83a', '#f0d890', false) };
CAST2.groomRich = Object.assign({}, CAST2.groom, { name: 'Thomas (prestige)', col: { body: '#5a1f7a', sleeve: '#f6e8c0', legs: '#f4eee2', shoes: '#140e10' }, hat: tudorBonnet('#100a14', '#ffd34d', '#ffe680'),
  costume: groomCostume('#5a1f7a', '#f6d050', '#f6dc8a', true) });
// ---- guards (Yeomen-style)
function guard(seed) {
  const r = rng(seed), skins = [SK.peach, SK.tan, SK.olive, SK.brown, SK.ruddy];
  const hc = ['#2a1a10', '#5a3a20', '#1a1410', '#7a5030'][Math.floor(r() * 4)];
  return { name: 'Guard', skin: skins[Math.floor(r() * skins.length)], body: Object.assign({}, BODY2.stocky, { hh: 95 + r() * 6 }), hairCol: hc,
    face: { nose: ['roman', 'bulb', 'hook', 'long'][Math.floor(r() * 4)], noseLen: .08 + r() * .06, jaw: 1 + r() * .15, iris: '#4a3020', browT: 1.5, tache: tache2(hc, 1.2), stubble: r() < .5 ? '#3a2a20' : null },
    col: { body: '#b8222e', sleeve: '#b8222e', legs: '#b8222e', shoes: '#1a100c' }, hair: hairShort(hc), hat: tudorBonnet('#14101a', null, '#f0c040'),
    costume: costume({ flare: 1.2, levels: [[-.45, 96, 80, 84], [0, 70, 58, 56], [.45, 74, 62, 52], [.8, 86, 60, 52], [.93, 90, 40, 42], [1.03, 65, 32, 36], [1.08, 26, 20, 24]],
      detail: (H, back) => { for (const l of [-.38, -.1, .2, .5, .8]) { const a = frame(H, -1.6, l), b = frame(H, 1.6, l); line(H.c, [a, b], 4, '#1a1418'); line(H.c, [a, b], 2, '#f0c040'); }
        if (!back) { const m = frame(H, 0, .5); ell(H.c, m[0], m[1], 26, 26, '#f6e6c0', H.lw * .6); for (let i = 0; i < 5; i++) { const a = i / 5 * TAU; ell(H.c, m[0] + Math.cos(a) * 12, m[1] + Math.sin(a) * 12, 9, 9, '#c8203a'); } ell(H.c, m[0], m[1], 6, 6, '#f0c040'); } },
      collar: (H) => { const u = H.u; for (let i = -2; i <= 2; i++) ell(H.c, i * .1 * u, .08 * u, .07 * u, .08 * u, '#f7f1e4', H.lw * .5); } }) };
}
CAST2.guards = [guard(3), guard(7), guard(11), guard(19)];
// ---- nobles
CAST2.noble = { name: 'Noble', skin: SK.pale, body: BODY2.slim, hairCol: '#2a2a2a', face: { nose: 'hook', noseLen: .13, jaw: .9, iris: '#4a4a4a', tache: tache2('#2a2a2a', .9), beard: goatee('#2a2a2a'), browT: 1.2 },
  col: { body: '#2f4a8a', sleeve: '#d9c08a', legs: '#2a2a3a', shoes: '#151018' }, hair: hairShort('#2a2a2a'), hat: tudorBonnet('#2a1d2a', '#d23a4a'),
  costume: costume({ flare: 1.3, levels: [[-.62, 100, 86, 96], [0, 66, 54, 54], [.45, 66, 56, 48], [.8, 84, 58, 50], [.93, 92, 40, 42], [1.03, 66, 32, 36], [1.08, 24, 20, 22]],
    detail: (H) => { vline(H, -1.1, -.7, 1.05, '#e8dcc0', 26); vline(H, 1.1, -.7, 1.05, '#e8dcc0', 26); for (let i = 0; i < 3; i++) { const a = frame(H, -.8, .3 + i * .2), b = frame(H, .8, .3 + i * .2); line(H.c, [a, b], 3, rgba('#d8b060', .8)); } } }) };
CAST2.lady = { name: 'Lady', skin: SK.fair, body: BODY2.woman, hairCol: '#3a2416', face: { nose: 'button', noseLen: .06, jaw: .85, iris: '#3f7a4a', eyeS: 1.12, lash: true, cheeks: .5, browT: .8 },
  col: { body: '#2d6b4a', sleeve: '#2d6b4a', legs: '#2d6b4a', shoes: '#1a1010' }, hat: gableHood('#1a1620', '#f0c040'),
  costume: costume({ flare: 1.6, levels: [[-1.75, 150, 140, 150], [-.9, 112, 96, 108], [0, 54, 46, 46], [.45, 50, 46, 38], [.8, 62, 52, 40], [.93, 66, 32, 34], [1.03, 48, 26, 29], [1.08, 20, 16, 18]],
    detail: (H) => { const a = frame(H, -.5, .95), b = frame(H, .5, .95), d = frame(H, .9, -1.7), e = frame(H, -.9, -1.7); fillOL(H.c, [a, b, d, e], '#d8b860', H.lw * .6); for (let i = 0; i < 6; i++) { const p = frame(H, -.6 + i * .24, -1.6); ell(H.c, p[0], p[1], 6, 6, '#c8203a'); } } }) };
CAST2.servant = { name: 'Servant', skin: SK.tan, body: BODY2.slim, hairCol: '#5a3a22', face: { nose: 'button', noseLen: .08, iris: '#5a3a22', cheeks: .4, jaw: .95 },
  col: { body: '#7a4a2a', sleeve: '#e8dcc6', legs: '#4a3a2a', shoes: '#1e1410' }, hair: hairShort('#5a3a22', { curls: true }),
  costume: costume({ levels: [[-.5, 80, 66, 70], [0, 62, 52, 50], [.45, 62, 54, 46], [.8, 74, 56, 46], [.93, 80, 38, 40], [1.03, 58, 30, 34], [1.08, 22, 18, 20]],
    detail: (H) => { const a = frame(H, -.8, .7), b = frame(H, .8, .7), d = frame(H, .9, -.5), e = frame(H, -.9, -.5); fillOL(H.c, [a, b, d, e], '#f2ead8', H.lw * .6); } }) };
// ---- the Sin-Eater: tall, gaunt, human, readable
CAST2.sineater = { name: 'The Sin-Eater', skin: '#dcb79a', body: BODY2.tall, hairCol: '#8a8580', faceShadow: .16,
  face: { nose: 'hook', noseLen: .14, noseDrop: .04, chin: .0, jaw: .82, stubble: '#4a4440', iris: '#b8a060', browT: 1.5, browCol: '#5a5450', wrinkles: true, eyeS: .95 },
  col: { body: '#5a4e48', sleeve: '#4e4440', legs: '#3a3432', shoes: '#2a2220' }, hair: (c, view, u, lw) => { if (view === 'b') return; const xs = view === 'f' ? [-.42, -.37, .37, .42] : view === 'q' ? [-.44, -.39, -.34] : [-.36, -.3, -.24]; for (const x of xs) { c.beginPath(); c.moveTo(x * u, -.7 * u); c.quadraticCurveTo((x - .03) * u, -.45 * u, x * u, -.12 * u); c.lineWidth = lw * 1.4; c.strokeStyle = '#8a8580'; c.stroke(); } }, hat: hoodHat('#4a3e3a'), hairBack: (c, view, u, lw) => { if (view !== 'b') ell(c, (view === 'p' ? -.05 : .03) * u, -.5 * u, .62 * u, .66 * u, '#16101a'); },
  costume: costume({ flare: 1.35, levels: [[-1.55, 118, 96, 120], [-.8, 92, 76, 92], [0, 62, 50, 54], [.45, 60, 50, 50], [.8, 72, 56, 50], [.93, 78, 36, 44], [1.03, 56, 29, 37], [1.08, 26, 20, 24]],
    detail: (H) => { const { c } = H; c.globalAlpha = .25; for (let i = -6; i <= 6; i++) vline(H, i * .2, -1.6, 1.05, '#2a2020', 3); c.globalAlpha = 1;
      const a = frame(H, -1.3, .02), b = frame(H, 1.3, .02); line(c, [a, b], 9, '#a88a5a'); const k = frame(H, .4, -.02); line(c, [k, [k[0] + 8, k[1] + 70]], 6, '#a88a5a');
      const p = frame(H, -.5, -.9); rrect(c, p[0] - 22, p[1] - 22, 44, 40, 6, '#6a5e52', H.lw * .5); },
    cape: (H, layer) => { const { c, lw, J, p } = H; if (layer !== 'back') return; const sw = clamp(p.swing, -.8, .8) * 80;
      fillOL(c, [[J.shC[0] - 70, J.shC[1] + 10], [J.shC[0] + 60, J.shC[1] + 10], [70 - sw, 40], [90 - sw * 1.4, 260], [-120 - sw * 1.6, 280], [-110 - sw, 40]], '#2e282c', lw, .3);
      for (let i = 0; i < 5; i++) poly(c, [[-110 - sw * 1.6 + i * 44, 270], [-90 - sw * 1.6 + i * 44, 300], [-70 - sw * 1.6 + i * 44, 270]], '#2e282c'); },
    cuff: (H, A, near) => { const d = [A[2][0] - A[1][0], A[2][1] - A[1][1]], L = Math.hypot(...d); const q = [A[2][0] - d[0] / L * 16, A[2][1] - d[1] / L * 16]; fillOL(H.c, [[q[0] - 22, q[1] - 10], [q[0] + 22, q[1] - 10], [q[0] + 26, q[1] + 14], [q[0] - 26, q[1] + 14]], near ? '#4e4440' : '#3a3230', H.lw * .7); },
  }) };
// ---- mourners / villagers
CAST2.widow = { name: 'Widow', skin: SK.fair, body: BODY2.woman, hairCol: '#4a3022', face: { nose: 'roman', noseLen: .07, jaw: .88, iris: '#4a5a6a', lash: true, browT: .9 },
  col: { body: '#2a2630', sleeve: '#2a2630', legs: '#2a2630', shoes: '#151218' }, hat: coif('#f2eee4'),
  costume: costume({ flare: 1.5, levels: [[-1.75, 140, 130, 140], [-.9, 108, 92, 104], [0, 56, 46, 48], [.45, 52, 46, 40], [.8, 62, 52, 40], [.93, 66, 32, 34], [1.03, 48, 26, 29], [1.08, 20, 16, 18]],
    detail: (H) => { const a = frame(H, -.9, .95), b = frame(H, .9, .95), d = frame(H, .4, .6), e = frame(H, -.4, .6); fillOL(H.c, [a, b, d, e], '#e8e2d6', H.lw * .5); } }) };
CAST2.boy = { name: 'Boy', skin: SK.peach, body: BODY2.boy, hairCol: '#5a3a1a', face: { nose: 'button', noseLen: .06, jaw: .95, iris: '#5a3a22', eyeS: 1.2, cheeks: .5 },
  col: { body: '#3a4a5a', sleeve: '#3a4a5a', legs: '#2a2a32', shoes: '#1a1418' }, hair: hairShort('#5a3a1a', { curls: true }),
  costume: costume({ levels: [[-.3, 64, 52, 56], [0, 50, 42, 42], [.45, 50, 44, 38], [.8, 58, 44, 36], [.93, 62, 30, 32], [1.03, 45, 24, 27], [1.08, 18, 14, 16]] }) };
function villager(seed, era = 'vil') {
  const r = rng(seed), pick = a => a[Math.floor(r() * a.length)];
  const fem = r() < .45;
  const hc = pick(['#3a2416', '#6a4a2a', '#b07a3a', '#2a2a2a', '#a8a8a8', '#8a3a1a']);
  const coats = era === 'ind' ? ['#4a6a8a', '#7a4a3a', '#4a6a4a', '#7a3a5a', '#8a7a4a', '#3a4a6a', '#a05a3a'] : era === 'court' ? ['#2a4a8a', '#7a2a5a', '#2a6a4a', '#8a6a2a', '#5a2a7a'] : ['#5a4a3a', '#4a4a3e', '#6a5040', '#4a3e4a', '#5a4436'];
  const body = fem ? BODY2.woman : pick([BODY2.slim, BODY2.stocky, BODY2.lanky]);
  const coat = pick(coats);
  return { name: 'folk' + seed, skin: pick(Object.values(SK)), body: Object.assign({}, body, { hh: body.hh * (.95 + r() * .1) }), hairCol: hc,
    face: { nose: pick(['roman', 'button', 'hook', 'long', 'bulb']), noseLen: .06 + r() * .08, jaw: .85 + r() * .3, chin: (r() - .5) * .05, iris: pick(['#4a6b8a', '#5a3a22', '#3f6f4a']), cheeks: r() * .5, eyeS: .95 + r() * .2, lash: fem,
      tache: !fem && r() < .4 ? tache2(hc, .9 + r() * .4) : null, stubble: !fem && r() < .35 ? '#5a4636' : null, beard: !fem && r() < .15 ? beardFull2(hc) : null, wrinkles: r() < .3 },
    col: { body: coat, sleeve: shade(coat, .08), legs: fem ? coat : shade(coat, .35), shoes: '#2a1e18' },
    hair: fem ? null : hairShort(hc, { curls: r() < .3, recede: r() < .3 ? 1 : 0 }), hairBack: fem ? hairLong(hc) : null,
    hat: fem ? (era === 'court' ? gableHood(pick(['#1a1620', '#5a1a2a']), '#f0c040') : coif(era === 'vil' ? pick(['#9a8a78', '#6a5a50', '#b8a890']) : pick(['#f2eee4', '#d8cfc0', '#e8d8c0']))) : (r() < .6 ? (era === 'court' ? tudorBonnet(pick(['#1a1620', '#2a1a10']), r() < .5 ? '#f4f0e4' : null) : flatCap(pick(['#4a4a44', '#5a4a3a', '#3a3a3a', '#6a5a4a']))) : null),
    costume: costume({ flare: fem ? 1.55 : 1.1, levels: fem ? [[-1.75, 132, 124, 132], [-.9, 100, 88, 100], [0, 54, 46, 46], [.45, 50, 46, 38], [.8, 60, 50, 40], [.93, 64, 32, 34], [1.03, 46, 26, 29], [1.08, 20, 16, 18]]
      : [[-.45, 82, 66, 72], [0, 62, 52, 52], [.45, 64, 54, 46], [.8, 76, 56, 46], [1.0, 82, 38, 40], [1.08, 22, 18, 20]],
      detail: (H) => { if (fem) { const a = frame(H, -.8, .05), b = frame(H, .8, .05), d = frame(H, .9, -1.4), e = frame(H, -.9, -1.4); fillOL(H.c, [a, b, d, e], era === 'vil' ? rgba('#8a7a68', .9) : rgba('#f2ead8', .85), H.lw * .5); } else buttons(H, .3, [.3, .5, .7, .9], '#d8c080', 4); } }) };
}
