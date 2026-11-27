// model sheet: node tools/sheet.js out.png
'use strict';
const path = require('path');
const fs = require('fs');
const { createCanvas, GlobalFonts } = require('@napi-rs/canvas');
const C = require('../src/core');
const R = require('../src/rig');
const PS = require('../src/person');
const CAST = require('../src/cast');

const out = process.argv[2] || 'sheet.png';
const cv = createCanvas(2160, 1920), g = cv.getContext('2d');
g.fillStyle = '#d9c9a6'; g.fillRect(0, 0, 2160, 1920);
const B = R.BODY.adult;
const items = [
  ['piper', R.merge(R.idle(1, { B: R.BODY.piper }), { yaw: 0.35, face: { mouth: 'sly', eyes: 'open', brow: 'sly' } })],
  ['piper', R.merge(R.walk(.12, { B: R.BODY.piper, stride: 110, bob: 4, arm: .25 }), { yaw: 1.45, face: { mouth: 'closed' } })],
  ['mayor', R.merge(R.idle(2), { yaw: 0, face: { mouth: 'frown', brow: 'angry' } })],
  ['councillor', R.merge(R.idle(3), { yaw: -.5, face: { mouth: 'laugh', eyes: 'narrow' } })],
  ['baker', R.merge(R.squatDance(.35, 1), { yaw: .2, face: { mouth: 'grin' } })],
  ['merchant', R.merge(R.walk(.3, { stride: 80 }), { yaw: 1.2, face: { mouth: 'gasp', eyes: 'wide', brow: 'worry' } })],
  ['woman', R.merge(R.squatDance(.1, 2), { yaw: 0, face: { mouth: 'o', eyes: 'wide' } })],
  ['guard', R.merge(R.idle(4), { yaw: .6, face: {} })],
  ['girl1', R.merge(R.walk(.2, { B: R.BODY.child, stride: 50, arm: .1, bob: 3 }), { yaw: 1.3, face: { eyes: 'half', mouth: 'peace' } })],
  ['boy1', R.merge(R.idle(5, { B: R.BODY.child }), { yaw: 0, face: { eyes: 'half', mouth: 'peace' } })],
  ['girl2', R.merge(R.idle(6, { B: R.BODY.child }), { yaw: -.4, face: { eyes: 'open', mouth: 'o' } })],
  ['farmer', R.merge(R.jig(.4, 1), { yaw: -.3, face: { mouth: 'laugh', eyes: 'narrow' } })],
];
items.forEach(([who, P], i) => {
  const col = i % 6, row = Math.floor(i / 6);
  const x = 180 + col * 360, y = 880 + row * 900;
  const ch = CAST[who];
  PS.drawPerson(g, ch, P, { x, y, s: 1.35, t: 1 });
  g.fillStyle = '#28170c'; g.font = '28px sans-serif'; g.textAlign = 'center'; g.fillText(who, x, y + 60);
});
fs.writeFileSync(out, cv.toBuffer('image/png'));
console.log('wrote', out);
