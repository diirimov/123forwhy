'use strict';
const fs = require('fs');
const { createCanvas } = require('@napi-rs/canvas');
const C = require('../src/core'), R = require('../src/rig'), PS = require('../src/person'), CAST = require('../src/cast');
const E = require('../src/env'), Wd = require('../src/world'), ST = require('../src/stage'), PO = require('../src/post'), PP = require('../src/piper');
const cv = createCanvas(C.W, C.H), g = cv.getContext('2d');
const t = +(process.argv[2] || 31);
E.LIGHTS.length = 0;
const V = new Wd.View({ cx: 0, cy: 170, cz: 0, f: 1150, hy: 880 });
ST.streetBackdrop(g, V, t, 'day', { sunX: 820, sunY: 240, clouds: [[200, 300, 1.1]] });
const items = [];
// back wall rows of frontal houses (DP)
for (const [z, n, seed] of [[3800, 9, 1], [2700, 7, 2]]) for (let i = 0; i < n; i++) { const w = 230 + C.hash(i * 3 + seed) * 70; items.push(Wd.houseItem((i - (n - 1) / 2) * 640 + (seed - 1) * 300, z, w, 360 + C.hash(i + seed * 9) * 140, { seed: seed * 50 + i, mood: 'day' })); }
const dancers = [];
for (let r = 0; r < 3; r++) for (let c = 0; c < 4 + r; c++) dancers.push({ x: (c - (3 + r) / 2) * (330 + r * 60) + (r % 2) * 90, z: 820 + r * 380, ch: CAST.townsfolk(10 + r * 7 + c), i: r * 7 + c });
for (const d of dancers) items.push({ z: d.z, draw: (g2, V2) => ST.actor(g2, V2, d.ch, d.x, d.z, tt => R.merge(R.squatDance(C.beatPhase(tt), C.beatIndex(tt), { amt: 1 }), { yaw: (d.x > 0 ? -.2 : .2), face: { eyes: 'open', mouth: 'flat', look: [0, 0] } }), t) });
Wd.drawItems(g, V, items);
PO.grade(g, 'day'); PO.lights(g); PO.finish(g, t, {});
fs.writeFileSync(process.argv[3] || 'review/dptest.jpg', cv.toBuffer('image/jpeg', 85));
