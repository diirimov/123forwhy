const { createCanvas } = require('@napi-rs/canvas'); const F = require('../src/film'); const C = require('../src/core');
const cv = createCanvas(C.W, C.H), g = cv.getContext('2d');
for (const t of process.argv.slice(2).map(Number)) { const t0 = Date.now(); let S; for (let i = 0; i < 4; i++) S = F.renderFrame(g, t + i / 60); console.log(t, S.id, ((Date.now() - t0) / 4).toFixed(0) + ' ms'); }
