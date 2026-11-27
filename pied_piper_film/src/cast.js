// cast: character designs (the studio's townsfolk look + the Piper + children)
'use strict';
const C = require('./core');
const { makeChar } = require('./person');
const { PAL } = require('./ink');

const CAST = {
  piper: makeChar({ name: 'piper', body: 'piper', outfit: 'piper', skin: PAL.pale, skinSh: PAL.paleSh, top: PAL.burg, skirt: PAL.burg,
    sleeve: PAL.burg, legs: PAL.pgreen, legs2: PAL.burg, shoe: '#2b1d17', hat: 'piper', hair: 'piper', hairCol: PAL.hair, brow: '#2a1d1f',
    belt: '#3b2416', pouch: false, lacing: false, blush: 0, chin: 1.25, faceW: .95, seed: 7 }),
  mayor: makeChar({ name: 'mayor', outfit: 'robe', top: '#8e2b25', skirt: '#8e2b25', bodice: PAL.gold, sleeve: '#1f1d26', legs: '#2b2730', shoe: '#2a1d14',
    hat: 'tophat', hatCol2: '#a32d2d', hair: 'bald', hairCol: '#b8b3a8', beard: '#cfc8bb', chain: true, lacing: true, k: 1.05, dims: { hipW: 25 }, seed: 2 }),
  councillor: makeChar({ name: 'councillor', outfit: 'robe', top: '#2c3346', skirt: '#2c3346', bodice: '#c8a050', sleeve: '#2c3346', legs: '#2b2730',
    hat: 'beret', hatCol: '#3f6a43', hair: 'short', hairCol: '#3b2a20', lacing: true, seed: 3 }),
  clerk: makeChar({ name: 'clerk', outfit: 'robe', top: '#1f1d26', skirt: '#1f1d26', bodice: '#a33a2a', sleeve: '#a33a2a', legs: '#2b2730',
    hat: 'tophat', hatCol2: '#2e2a36', hair: 'short', hairCol: '#5b4a3a', seed: 4 }),
  baker: makeChar({ name: 'baker', outfit: 'tunic', top: '#d8cdb5', sleeve: '#e9e1cf', legs: '#6e5a45', apron: '#f2ece0', hat: 'toque',
    hair: 'short', hairCol: '#7a4a2a', k: 1.03, dims: { hipW: 27 }, beard: null, seed: 5 }),
  merchant: makeChar({ name: 'merchant', outfit: 'tunic', top: PAL.green, sleeve: PAL.mustard, legs: PAL.blue, hat: 'beret', hatCol: '#6e3a2a', hair: 'short', hairCol: '#4a2c1c', seed: 6 }),
  woman: makeChar({ name: 'woman', outfit: 'dress', top: PAL.red, skirt: PAL.red, sleeve: PAL.mustard, legs: PAL.blue, hat: 'coif', hatCol2: PAL.red, seed: 8 }),
  mother: makeChar({ name: 'mother', outfit: 'dress', top: PAL.blue, skirt: PAL.blue, sleeve: '#8b7a5c', legs: PAL.blue, hat: 'coif', hatCol2: PAL.blueD, seed: 9 }),
  guard: makeChar({ name: 'guard', outfit: 'tunic', top: '#8e2b25', sleeve: '#7c7d82', legs: '#3c3a40', hat: 'helmet', hair: 'short', hairCol: '#3b2a20', beard: '#4a3426', lacing: false, seed: 10 }),
  farmer: makeChar({ name: 'farmer', outfit: 'tunic', top: PAL.olive, sleeve: '#9a7a50', legs: '#6e5a45', hat: 'straw', hair: 'short', hairCol: '#a0703a', seed: 11 }),
  father: makeChar({ name: 'father', outfit: 'tunic', top: PAL.brown, sleeve: '#8a6a4a', legs: '#4d4f63', hat: 'none', hair: 'short', hairCol: '#4a2c1c', beard: '#4a2c1c', seed: 12 }),
};

// procedurally varied townsfolk + children in the studio palette
const TOPS = [PAL.red, PAL.blue, PAL.green, PAL.olive, '#8a5a3c', '#7b3f5a', '#a8763c'];
const SLEEVES = [PAL.mustard, '#a98f63', PAL.green, '#9b5a3c', '#7d6e55', PAL.red];
const LEGS = [PAL.blue, '#5d4a3a', '#3f4a5f', '#6e5a45'];
const HAIR = ['#6b3f22', '#3b2a20', '#a0703a', '#c99a55', '#2a1d1f', '#7a4a2a'];
function townsfolk(i) {
  const r = C.rng(1000 + i * 17);
  const woman = r() < .5;
  return makeChar({
    name: 'tf' + i, outfit: woman ? 'dress' : 'tunic', top: TOPS[Math.floor(r() * TOPS.length)], sleeve: SLEEVES[Math.floor(r() * SLEEVES.length)],
    legs: LEGS[Math.floor(r() * LEGS.length)], hat: woman ? (r() < .75 ? 'coif' : 'hood') : ['none', 'beret', 'straw', 'hood', 'coif'][Math.floor(r() * 5)],
    hatCol: woman ? PAL.coif : ['#6e3a2a', '#3f6a43', '#cfae63', '#5d4a3a', PAL.coif][Math.floor(r() * 5)], hatCol2: [PAL.red, PAL.blueD, PAL.greenD][Math.floor(r() * 3)],
    hair: woman ? 'none' : ['short', 'bald', 'short', 'bowl'][Math.floor(r() * 4)], hairCol: HAIR[Math.floor(r() * HAIR.length)],
    beard: !woman && r() < .35 ? HAIR[Math.floor(r() * HAIR.length)] : null, k: .94 + r() * .12, apron: r() < .25 ? '#e8dcbf' : null, seed: i,
    dims: { hipW: 19 + r() * 7 },
  });
}
function child(i) {
  const r = C.rng(5000 + i * 31);
  const girl = r() < .5;
  return makeChar({
    name: 'child' + i, body: 'child', outfit: girl ? 'dress' : 'tunic', top: TOPS[Math.floor(r() * TOPS.length)], sleeve: SLEEVES[Math.floor(r() * SLEEVES.length)],
    legs: LEGS[Math.floor(r() * LEGS.length)], hat: girl ? (r() < .4 ? 'coif' : 'none') : (r() < .3 ? 'hood' : 'none'),
    hatCol: girl ? PAL.coif : ['#6e3a2a', '#3f6a43', '#5d4a3a'][Math.floor(r() * 3)],
    hair: girl ? (r() < .6 ? 'braids' : 'long') : (r() < .6 ? 'bowl' : 'short'), hairCol: HAIR[Math.floor(r() * HAIR.length)],
    k: .9 + r() * .2, blush: .7, pouch: r() < .3, apron: girl && r() < .2 ? '#e8dcbf' : null, seed: 100 + i, eyeR: 1.08,
  });
}
CAST.girl1 = child(1); CAST.boy1 = child(2); CAST.girl2 = child(3);
CAST.townsfolk = townsfolk; CAST.child = child;
// guarantee variety for named kids
CAST.girl1 = makeChar({ ...CAST.girl1, name: 'girl1', body: 'child', outfit: 'dress', top: PAL.red, skirt: PAL.red, sleeve: PAL.mustard, hat: 'none', hair: 'braids', hairCol: '#a0703a', blush: .7, eyeR: 1.1, seed: 101 });
CAST.boy1 = makeChar({ name: 'boy1', body: 'child', outfit: 'tunic', top: PAL.blue, sleeve: '#a98f63', legs: '#5d4a3a', hat: 'none', hair: 'bowl', hairCol: '#6b3f22', blush: .7, eyeR: 1.1, seed: 102 });
CAST.girl2 = makeChar({ name: 'girl2', body: 'child', outfit: 'dress', top: PAL.green, skirt: PAL.green, sleeve: '#d8cdb5', hat: 'coif', hatCol2: PAL.greenD, hair: 'none', blush: .7, eyeR: 1.1, seed: 103 });
module.exports = CAST;
