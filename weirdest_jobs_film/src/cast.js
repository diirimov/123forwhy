// ===================================================================== cast.js
'use strict';
const SKIN = { pale: '#f2c7a5', warm: '#e8b48e', ruddy: '#eaa98a', olive: '#d39f78', deep: '#a8714f', grey: '#d8b8a0' };

// ---------- reusable hair / hat pieces (head-local coords: neck top = origin, head up to -hh)
const hairTuft = (col) => (c, hw, hh, p, lw, tx) => {
  blob(c, [[-hw * .5, -hh * .62], [-hw * .55, -hh * .95], [-hw * .2, -hh * 1.12], [hw * .2, -hh * 1.1], [hw * .5, -hh * .92], [hw * .42, -hh * .78], [hw * .05, -hh * .9], [-hw * .3, -hh * .78]], col, lw);
};
const flatCap = (col, band) => (c, hw, hh, p, lw, tx) => {
  blob(c, [[-hw * .56, -hh * .78], [-hw * .5, -hh * 1.02], [-hw * .05, -hh * 1.14], [hw * .45, -hh * 1.06], [hw * .6, -hh * .86], [hw * .3, -hh * .8]], col, lw);
  blob(c, [[hw * .15 + tx * .5, -hh * .84], [hw * .78 + tx, -hh * .78], [hw * .8 + tx, -hh * .72], [hw * .2 + tx * .5, -hh * .74]], shade(col, .25), lw);
  line(c, [[-hw * .5, -hh * .88], [hw * .55, -hh * .9]], lw * .5, rgba(INK, .5));
  ell(c, -hw * .05, -hh * 1.1, 5, 4, band || shade(col, .3));
};
const nightcap = (col, stripe) => (c, hw, hh, p, lw, tx) => {
  const droop = p.capDroop ?? 0;
  blob(c, [[-hw * .58, -hh * .62], [-hw * .55, -hh * .95], [-hw * .1, -hh * 1.12], [hw * .4, -hh * 1.02], [hw * .85, -hh * (.6 - droop)], [hw * 1.0, -hh * (.38 - droop)], [hw * .7, -hh * (.5 - droop)], [hw * .45, -hh * .76], [0, -hh * .82]], col, lw);
  if (stripe) line(c, [[-hw * .3, -hh * 1.02], [hw * .2, -hh * 1.02], [hw * .65, -hh * (.72 - droop)]], lw * 1.6, stripe);
  ell(c, hw * 1.0, -hh * (.36 - droop), 13, 13, '#f4efe4', lw);
  blob(c, [[-hw * .6, -hh * .6], [-hw * .58, -hh * .74], [hw * .5, -hh * .8], [hw * .52, -hh * .68]], tint(col, .5), lw);
};
const curls = (col) => (c, hw, hh, p, lw) => {
  for (let i = 0; i < 7; i++) { const a = PI * (1.05 + i * .13); ell(c, Math.cos(a) * hw * .5, -hh * .58 + Math.sin(a) * hh * .48, hw * .16, hw * .14, col, lw * .8); }
};
const tudorCap = (col, feather) => (c, hw, hh, p, lw, tx) => {
  const t = p.capT || 0;
  // soft beret tilted
  blob(c, [[-hw * .7, -hh * .86], [-hw * .55, -hh * 1.08], [0, -hh * 1.18], [hw * .62, -hh * 1.1], [hw * .78, -hh * .92], [hw * .3, -hh * .86]], col, lw);
  blob(c, [[-hw * .6, -hh * .9], [hw * .7, -hh * .95], [hw * .72, -hh * .88], [-hw * .6, -hh * .82]], shade(col, .3), lw * .7);
  if (feather) { const w = Math.sin(t * 6) * .12; c.save(); c.translate(hw * .45, -hh * 1.05); c.rotate(-.6 + w);
    blob(c, [[0, 0], [10, -60], [26, -120], [10, -110], [-8, -50]], feather, lw * .8);
    curve(c, [[2, -4], [14, -70], [20, -112]], lw * .5, shade(feather, .3)); c.restore(); }
  ell(c, hw * .35, -hh * .98, 7, 7, '#f3c74a', lw * .6);
};
const crown = (c, hw, hh, p, lw, tx) => {
  const y0 = -hh * .9, y1 = -hh * 1.32;
  blob(c, [[-hw * .55, -hh * .84], [-hw * .5, -hh * 1.0], [hw * .5, -hh * 1.0], [hw * .55, -hh * .84]], '#8c1d2a', lw);
  poly(c, [[-hw * .52, y0], [-hw * .5, y1], [-hw * .28, -hh * 1.12], [-hw * .1, -hh * 1.38], [hw * .1, -hh * 1.12], [hw * .3, -hh * 1.38], [hw * .5, y1], [hw * .52, y0]], '#f0c040', lw);
  c.save(); c.globalAlpha = .55; poly(c, [[-hw * .45, y0], [-hw * .45, y0 - 14], [hw * .45, y0 - 14], [hw * .45, y0]], '#fff1a8'); c.restore();
  for (const [x, col] of [[-hw * .3, '#d23a4a'], [0, '#3a74d2'], [hw * .3, '#2ca870']]) ell(c, x, -hh * .99, 8, 9, col, lw * .5);
  for (const x of [-hw * .5, -hw * .1, hw * .3, hw * .5]) ell(c, x, y1 - 4, 6, 6, '#fff3b0', lw * .5);
};
const hood = (col, depth = .75) => (c, hw, hh, p, lw, tx) => {
  // front rim of a deep hood (drawn after face); back of hood drawn in backHair
  blob(c, [[-hw * .78, -hh * .1], [-hw * .7, -hh * .9], [-hw * .25, -hh * 1.25], [hw * .4, -hh * 1.2], [hw * .82, -hh * .82], [hw * .8, -hh * .2],
    [hw * .62, -hh * .3], [hw * .6, -hh * .82], [hw * .2, -hh * 1.02], [-hw * .3, -hh * 1.0], [-hw * .58, -hh * .75], [-hw * .6, -hh * .15]], col, lw);
  line(c, [[-hw * .5, -hh * .3], [-hw * .45, -hh * .8]], lw * .6, shade(col, .4));
};
const hoodBack = (col) => (c, hw, hh, p, lw) => {
  blob(c, [[-hw * .85, hh * .15], [-hw * .9, -hh * .7], [-hw * .4, -hh * 1.28], [hw * .4, -hh * 1.25], [hw * .9, -hh * .8], [hw * .85, hh * .15]], shade(col, .35), lw);
};
const bonnet = (col) => (c, hw, hh, p, lw, tx) => {
  blob(c, [[-hw * .62, -hh * .3], [-hw * .64, -hh * .9], [-hw * .2, -hh * 1.12], [hw * .35, -hh * 1.08], [hw * .66, -hh * .8], [hw * .58, -hh * .62], [hw * .2, -hh * .92], [-hw * .3, -hh * .85], [-hw * .5, -hh * .3]], col, lw);
  line(c, [[-hw * .3, -hh * .2], [-hw * .1, hh * .02], [hw * .1, -hh * .1]], lw * .8, shade(col, .3));
};
const longHair = (col) => (c, hw, hh, p, lw) => blob(c, [[-hw * .6, hh * .1], [-hw * .65, -hh * .8], [-hw * .2, -hh * 1.1], [hw * .4, -hh * 1.05], [hw * .62, -hh * .7], [hw * .55, -hh * .2], [hw * .1, hh * .2]], col, lw);
const beardFull = (col) => (c, hw, hh, tx, p, lw) => blob(c, [[-hw * .48, -hh * .42], [-hw * .5, -hh * .05], [-hw * .2, hh * .2], [tx * .4 + hw * .05, hh * .26], [hw * .35 + tx * .4, hh * .12], [hw * .5 + tx * .2, -hh * .2], [hw * .48 + tx * .2, -hh * .42], [hw * .2 + tx, -hh * .26], [tx * .5, -hh * .3], [-hw * .25 + tx * .3, -hh * .28]], col, lw);
const tache = (col, big = 1) => (c, hw, hh, tx, p, lw) => {
  const x = tx + hw * .04, y = -hh * .24;
  blob(c, [[x - hw * .34 * big, y + 8], [x - hw * .15, y - 6], [x, y - 2], [x + hw * .15, y - 6], [x + hw * .36 * big, y + 8], [x + hw * .18, y + 4], [x, y + 3], [x - hw * .18, y + 4]], col, lw * .8);
};
const scarf = (col) => (c, J, p, lw, shC, up) => {
  const n = J.neck;
  blob(c, [[n[0] - 34, n[1] + 4], [n[0] - 30, n[1] - 14], [n[0] + 34, n[1] - 14], [n[0] + 38, n[1] + 6], [n[0], n[1] + 16]], col, lw);
  const sw = (p.swing || 0) * 60 + Math.sin((p.tt || 0) * 7) * 6;
  blob(c, [[n[0] + 10, n[1] + 6], [n[0] + 26, n[1] + 8], [n[0] + 34 - sw, n[1] + 78], [n[0] + 14 - sw, n[1] + 82]], shade(col, .12), lw);
  for (let i = 0; i < 3; i++) line(c, [[n[0] + 15 - sw + i * 7, n[1] + 82], [n[0] + 14 - sw + i * 7, n[1] + 94]], lw * .5);
};
const ruffCollar = (c, J, p, lw) => { const n = J.neck; for (let i = -3; i <= 3; i++) ell(c, n[0] + i * 11, n[1] + 4, 9, 11, '#f7f1e4', lw * .6); };

// ---------- costume detail painters (clipped to torso)
function patches(cols) { return (c, J, p, lw, g) => {
  rrect(c, g.hipF[0] + 14, g.hipF[1] - 70, 30, 34, 6, cols[0], lw * .6);
  line(c, [[g.hipF[0] + 18, g.hipF[1] - 66], [g.hipF[0] + 40, g.hipF[1] - 40]], lw * .35, rgba(INK, .5));
  for (let i = 0; i < 4; i++) ell(c, g.shC[0] + 30 + i * 2, g.shC[1] + 40 + i * 38, 5, 5, cols[1], lw * .5);
  line(c, [[g.shC[0] + 24, g.shC[1] + 10], [g.hipN[0] - 6, g.hemN[1] + 4]], lw * .5, rgba(INK, .6));
}; }
function doublet(slash, trim) { return (c, J, p, lw, g) => {
  for (let i = -3; i <= 3; i++) { const x = g.shC[0] + i * 22; c.fillStyle = slash; c.fillRect(x - 4, g.shC[1] + 20, 8, 120); }
  line(c, [[g.hipF[0] - 20, g.hipF[1] - 2], [g.hipN[0] + 20, g.hipN[1] - 2]], 12, trim);
  for (let i = 0; i < 5; i++) ell(c, g.shC[0] + 6, g.shC[1] + 30 + i * 26, 5, 5, trim, lw * .4);
}; }
function robeFur(fur, chain) { return (c, J, p, lw, g) => {
  c.fillStyle = fur; c.fillRect(g.shC[0] - 120, g.shC[1] - 10, 60, 400); c.fillRect(g.shC[0] + 50, g.shC[1] - 10, 60, 400);
  for (let i = 0; i < 40; i++) ell(c, g.shC[0] - 90 + (i % 2) * 140 + Math.sin(i) * 14, g.shC[1] + i * 9, 3, 3, '#2a2018');
  if (chain) for (let i = 0; i < 9; i++) { const a = PI * (.15 + i * .085); ell(c, g.shC[0] + Math.cos(a) * 70, g.shC[1] + 20 + Math.sin(a) * 70, 9, 7, '#f0c040', lw * .4); }
  if (chain) ell(c, g.shC[0], g.shC[1] + 100, 16, 16, '#f0c040', lw * .6);
}; }
function cloakRags(col) { return (c, J, p, lw, g) => {
  for (let i = 0; i < 6; i++) line(c, [[g.hipF[0] + i * 24, g.shC[1] + 60], [g.hipF[0] + i * 26 + 6, g.hemN[1] + 20]], lw * .5, rgba(INK, .35));
  rrect(c, g.shC[0] - 10, g.shC[1] + 120, 40, 30, 6, shade(col, .25), lw * .5);
}; }
function apron(col) { return (c, J, p, lw, g) => {
  blob(c, [[g.hipF[0] + 10, g.hipF[1] - 60], [g.hipN[0] - 4, g.hipN[1] - 60], [g.hemN[0] - 10, g.hemN[1] + 10], [g.hemF[0] + 14, g.hemF[1] + 10]], col, lw * .6);
}; }
function tabard(col, emblem) { return (c, J, p, lw, g) => {
  blob(c, [[g.shC[0] - 50, g.shC[1] + 10], [g.shC[0] + 50, g.shC[1] + 10], [g.hipN[0] - 6, g.hemN[1] + 10], [g.hipF[0] + 6, g.hemF[1] + 10]], col, lw * .6);
  ell(c, g.shC[0], g.shC[1] + 90, 22, 26, emblem, lw * .5);
  poly(c, [[g.shC[0] - 12, g.shC[1] + 80], [g.shC[0], g.shC[1] + 66], [g.shC[0] + 12, g.shC[1] + 80], [g.shC[0], g.shC[1] + 108]], '#f0c040');
}; }

// ---------- body presets
const BODY = {
  lanky: { thigh: 118, shin: 122, legW: 22, hipW: 70, torso: 175, shW: 108, upperArm: 98, foreArm: 92, armW: 15, coatLen: 95, flare: 1.15 },
  avg: { thigh: 100, shin: 102, legW: 24, hipW: 82, torso: 160, shW: 118, upperArm: 86, foreArm: 80, armW: 16, coatLen: 50, flare: 1.05 },
  broad: { thigh: 98, shin: 98, legW: 30, hipW: 125, torso: 175, shW: 170, upperArm: 92, foreArm: 84, armW: 25, coatLen: 110, flare: 1.35, belly: 30 },
  slim: { thigh: 108, shin: 110, legW: 20, hipW: 70, torso: 158, shW: 112, upperArm: 88, foreArm: 82, armW: 14, coatLen: 30, flare: 1.0 },
  small: { thigh: 72, shin: 72, legW: 15, hipW: 64, torso: 118, shW: 92, upperArm: 64, foreArm: 60, armW: 13, coatLen: 30, flare: 1.0 },
  tallgaunt: { thigh: 120, shin: 124, legW: 20, hipW: 72, torso: 180, shW: 112, upperArm: 100, foreArm: 96, armW: 15, coatLen: 210, flare: 1.4 },
  dress: { thigh: 95, shin: 96, legW: 18, hipW: 92, torso: 150, shW: 108, upperArm: 82, foreArm: 78, armW: 15, coatLen: 195, flare: 1.55 },
};

const CAST = {};
CAST.knocker = { name: 'Ned the Knocker-Up', skin: SKIN.ruddy, headW: 118, headH: 150, body: BODY.lanky, lw: 5,
  face: { nose: 'long', stubble: '#5a4636', eyeR: .12, iris: '#3f6f4a', browT: 1.3, browCol: '#3b2a1e', jaw: .9, chin: 6 },
  col: { coat: '#7a4b2e', sleeve: '#6c4129', legs: '#4c4a52', boots: '#3a2618' },
  backHair: (c, hw, hh, p, lw) => blob(c, [[-hw * .56, -hh * .4], [-hw * .6, -hh * .75], [-hw * .35, -hh * .7], [-hw * .4, -hh * .38]], '#4b3020', lw),
  hat: flatCap('#5d6a5c'), collar: scarf('#c8423a'), coatDetail: patches(['#9a7a4e', '#d8b060']) };
CAST.sleeper = { name: 'Sleepy Worker', skin: SKIN.warm, headW: 128, headH: 140, body: BODY.avg, face: { nose: 'round', stubble: '#6a4e3a', eyeR: .13, iris: '#6a4b30', cheeks: .5 },
  col: { coat: '#ece2cf', legs: '#ece2cf', boots: '#d9a07c' }, hat: nightcap('#6d8fbf', '#f2eee0') };
CAST.king = { name: 'The King', skin: SKIN.ruddy, headW: 140, headH: 150, body: BODY.broad, lw: 5.5,
  face: { nose: 'round', eyeR: .11, iris: '#5a3e2a', beard: beardFull('#a5552a'), tache: tache('#a5552a', 1.1), cheeks: .6, browCol: '#8a4420', browT: 1.3 },
  col: { coat: '#8c1d2a', sleeve: '#c2903a', legs: '#f0e6d0', boots: '#3a1c18' }, hat: crown,
  coatDetail: robeFur('#efe4d0', true), collar: (c, J) => blob(c, [[J.neck[0] - 70, J.neck[1] + 20], [J.neck[0] - 40, J.neck[1] - 10], [J.neck[0] + 46, J.neck[1] - 10], [J.neck[0] + 76, J.neck[1] + 20], [J.neck[0], J.neck[1] + 34]], '#efe4d0', 4),
  cuff: (c, an, lw) => ell(c, an[2][0], an[2][1] - 6, 22, 14, '#efe4d0', lw * .7) };
CAST.groom = { name: 'Groom of the Stool', skin: SKIN.pale, headW: 120, headH: 145, body: BODY.slim,
  face: { nose: 'button', eyeR: .14, iris: '#3a6ea8', cheeks: .45, chin: 4 },
  col: { coat: '#1f6e6a', sleeve: '#e0c06a', legs: '#f2ece0', boots: '#2a1e18' },
  backHair: curls('#7a4a22'), hat: tudorCap('#1d2b44', '#f4f0e4'), coatDetail: doublet('#e9cf7a', '#c79a2c'), collar: ruffCollar,
  cuff: (c, an, lw) => ell(c, an[2][0], an[2][1] - 4, 14, 9, '#f7f1e4', lw * .6) };
CAST.groomRich = Object.assign({}, CAST.groom, { name: 'Groom (prestige)', col: { coat: '#5a1f7a', sleeve: '#f0c040', legs: '#f2ece0', boots: '#1e1414' },
  coatDetail: (c, J, p, lw, g) => { doublet('#f6dc8a', '#f0c040')(c, J, p, lw, g); robeFur('#3a2a1e', true)(c, J, p, lw, g); }, hat: tudorCap('#120c18', '#ffd34d') });
CAST.guard = { name: 'Guard', skin: SKIN.warm, headW: 122, headH: 140, body: BODY.avg, face: { nose: 'round', eyeR: .1, tache: tache('#4a2e1c', 1.2), browT: 1.5 },
  col: { coat: '#b32631', legs: '#2a1c18', boots: '#1e1410' }, coatDetail: tabard('#b32631', '#1d2b44'), hat: tudorCap('#1d1018', null) };
CAST.noble1 = { name: 'Noble', skin: SKIN.pale, headW: 120, headH: 146, body: BODY.avg, face: { nose: 'hook', eyeR: .11, iris: '#4a4a4a', tache: tache('#3a3a3a', .8) },
  col: { coat: '#2f4a7a', sleeve: '#c9b27a', legs: '#2a2a3a', boots: '#151018' }, coatDetail: robeFur('#d9c9a8', false), hat: tudorCap('#2a1d2a', '#d23a4a'), collar: ruffCollar };
CAST.noble2 = { name: 'Lady', skin: SKIN.pale, headW: 116, headH: 142, body: BODY.dress, face: { nose: 'button', eyeR: .14, iris: '#5a7a3a', cheeks: .4 },
  col: { coat: '#2d6b45', sleeve: '#d8b860', legs: '#2d6b45', boots: '#1a1010' }, backHair: longHair('#3a2416'),
  hat: (c, hw, hh, p, lw) => { blob(c, [[-hw * .6, -hh * .55], [-hw * .5, -hh * 1.05], [0, -hh * 1.25], [hw * .5, -hh * 1.05], [hw * .6, -hh * .55], [hw * .45, -hh * .9], [0, -hh * 1.05], [-hw * .45, -hh * .9]], '#1a1a22', lw); line(c, [[-hw * .46, -hh * .88], [0, -hh * 1.04], [hw * .46, -hh * .88]], lw * 1.2, '#f0c040'); },
  coatDetail: (c, J, p, lw, g) => { blob(c, [[g.shC[0] - 30, g.shC[1] + 10], [g.shC[0] + 30, g.shC[1] + 10], [g.shC[0] + 60, g.hemN[1] + 20], [g.shC[0] - 60, g.hemN[1] + 20]], '#d8b860', lw * .5); } };
CAST.servant = { name: 'Servant', skin: SKIN.warm, headW: 118, headH: 140, body: BODY.slim, face: { nose: 'round', eyeR: .13, cheeks: .3 },
  col: { coat: '#6a3a24', legs: '#3a2a20', boots: '#1e1410' }, backHair: hairTuft('#5a3a22'), coatDetail: apron('#ece2cf'), hat: (c, hw, hh, p, lw) => hairTuft('#5a3a22')(c, hw, hh, p, lw) };
CAST.sineater = { name: 'The Sin-Eater', skin: SKIN.grey, headW: 112, headH: 150, body: BODY.tallgaunt, lw: 5, faceShadow: .62, noEars: true,
  face: { nose: 'hook', stubble: '#3a3434', eyeR: .1, iris: '#b9a774', browT: 1.4, jaw: .82, chin: 4 },
  col: { coat: '#3b3638', sleeve: '#333032', legs: '#2c2a2c', boots: '#1b1718' }, backHair: hoodBack('#3b3638'), hat: hood('#3b3638'), coatDetail: cloakRags('#3b3638') };
CAST.mother = { name: 'Mourning mother', skin: SKIN.pale, headW: 114, headH: 140, body: BODY.dress, face: { nose: 'button', eyeR: .13, iris: '#4a5a6a' },
  col: { coat: '#2a2630', sleeve: '#2a2630', legs: '#2a2630', boots: '#151218' }, backHair: longHair('#4a3022'), hat: bonnet('#1c1a20') };
CAST.boy = { name: 'Boy', skin: SKIN.warm, headW: 122, headH: 128, body: BODY.small, face: { nose: 'button', eyeR: .16, iris: '#5a3a22', cheeks: .4 },
  col: { coat: '#3a3a4a', legs: '#2a2a32', boots: '#1a1418' }, hat: hairTuft('#3a2416') };
CAST.elder = { name: 'Elder', skin: SKIN.grey, headW: 120, headH: 142, body: BODY.avg, face: { nose: 'hook', eyeR: .11, tache: tache('#e8e4dc', 1.1), browCol: '#d8d4cc', browT: 1.6 },
  col: { coat: '#33302e', legs: '#2a2826', boots: '#1a1614' }, hat: flatCap('#2a2624') };

// townsfolk / villagers generator for crowds (deterministic variety)
function townsfolk(seed, era = 'ind') {
  const r = rng(seed);
  const pick = a => a[Math.floor(r() * a.length)];
  const skins = Object.values(SKIN);
  const coatsInd = ['#4a5a6a', '#6a4a3a', '#3a4a3a', '#5a3a4a', '#7a6a4a', '#3a3a4a'];
  const coatsVil = ['#4a4038', '#3a3a34', '#5a4a3a', '#38343c', '#4a3a30'];
  const body = pick([BODY.avg, BODY.slim, BODY.broad, BODY.dress]);
  const fem = body === BODY.dress;
  const hc = pick(['#3a2416', '#6a4a2a', '#b07a3a', '#2a2a2a', '#a8a8a8']);
  const coat = pick(era === 'ind' ? coatsInd : coatsVil);
  return { name: 'folk' + seed, skin: pick(skins), headW: 112 + r() * 18, headH: 132 + r() * 18, body, face: { nose: pick(['round', 'button', 'hook', 'long']), eyeR: .11 + r() * .04, iris: pick(['#4a6b8a', '#5a3a22', '#3f6f4a']), cheeks: r() * .5,
      tache: !fem && r() < .35 ? tache(hc, .9) : null, stubble: !fem && r() < .3 ? '#5a4636' : null },
    col: { coat, legs: shade(coat, .3), boots: '#2a1e18' }, backHair: fem ? longHair(hc) : null,
    hat: fem ? bonnet(pick(['#d8cfc0', '#4a4a5a', '#7a3a3a'])) : (r() < .7 ? flatCap(pick(['#4a4a44', '#5a4a3a', '#3a3a3a'])) : hairTuft(hc)),
    coatDetail: !fem && r() < .4 ? apron('#d8cfc0') : null, collar: r() < .4 ? scarf(pick(['#7a3a3a', '#3a5a7a', '#c8a040'])) : null };
}
