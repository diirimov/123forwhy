// node tools/envtest.js mood t out.png
const fs = require('fs'); const { createCanvas } = require('@napi-rs/canvas');
const C = require('../src/core'), E = require('../src/env'), Wd = require('../src/world'), PO = require('../src/post'), R = require('../src/rig'), PS = require('../src/person'), CAST = require('../src/cast'), RT = require('../src/rats'), CP = require('../src/captions');
const mood = process.argv[2] || 'night', t = +(process.argv[3] || 0), out = process.argv[4] || 'env.png';
const cv = createCanvas(C.W, C.H), g = cv.getContext('2d');
E.LIGHTS.length = 0;
const V = new Wd.View({ cx: 0, cy: 300, cz: 0, f: 1150, hy: 700 });
g.save(); E.sky(g, mood, C.W, 900, t); if (mood === 'night') E.moon(g, 760, 260, 95); else E.sun(g, 800, 250, 70, t); E.skyline(g, -100, V.p(0, 0, 9000)[1] + 2, 1300, mood, 4); g.restore();
Wd.ground(g, V, { mood });
const items = Wd.streetItems({ mood, lit: .7, seed: 3 });
// procession: piper + children walking toward camera
const ph = (t / (2 * C.BEAT)) % 1;
const kids = [];
for (let i = 0; i < 12; i++) { const row = Math.floor(i / 2), side = i % 2 ? 1 : -1; kids.push({ ch: CAST.child(i + 1), x: side * 150, z: 2300 + row * 330 }); }
items.push({ z: 1900, draw: (g, V) => { const [sx, sy, s] = V.p(0, 0, 1900); PS.drawPerson(g, CAST.piper, R.merge(R.walk(ph, { B: CAST.piper.B, stride: 110, bob: 3, arm: .1 }), { yaw: 0, face: { mouth: 'flute', eyes: 'narrow' } }), { x: sx, y: sy, s, lw: V.lw(s), t }); } });
for (const k of kids) items.push({ z: k.z, draw: (g, V) => { const [sx, sy, s] = V.p(k.x, 0, k.z); PS.drawPerson(g, k.ch, R.merge(R.walk(ph, { B: k.ch.B, stride: 60, bob: 4, arm: .08 }), { yaw: 0, head: { yaw: .9 }, face: { eyes: 'half', mouth: 'peace' } }), { x: sx, y: sy, s, lw: V.lw(s), t }); } });
for (let i = 0; i < 4; i++) items.push({ z: 1200 + i * 90, draw: (g, V) => { const [sx, sy, s] = V.p(-620 + i * 70, 0, 1200 + i * 90); RT.ratSide(g, sx, sy, { s: s * .9, dir: 1, phase: t * 3 + i * .3, t }); } });
Wd.drawItems(g, V, items);
E.fog(g, 520, 420, t, { col: mood === 'night' ? '#aab8dc' : '#efe2c4', a: .35 });
PO.grade(g, mood); PO.lights(g); PO.finish(g, t);
CP.storyCaption(g, '130 CHILDREN VANISHED.', 1, { t0: 0, t1: 2, y: 420, size: 96, hl: new Set(['130']) });
fs.writeFileSync(out, cv.toBuffer('image/png'));
