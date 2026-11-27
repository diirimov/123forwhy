// turnaround + walk strip: node tools/turn.js who out.png
const fs = require('fs'); const { createCanvas } = require('@napi-rs/canvas');
const R = require('../src/rig'), PS = require('../src/person'), CAST = require('../src/cast');
const who = process.argv[2] || 'piper', out = process.argv[3] || 'turn.png';
const ch = CAST[who]; const B = ch.B;
const cv = createCanvas(2160, 1500), g = cv.getContext('2d');
g.fillStyle = '#d9c9a6'; g.fillRect(0, 0, 2160, 1500);
const yaws = [0, .5, 1.0, 1.57, 2.3, 3.14];
yaws.forEach((y, i) => PS.drawPerson(g, ch, R.merge(R.idle(1, { B }), { yaw: y, face: { mouth: 'sly', brow: 'sly' } }), { x: 180 + i * 360, y: 700, s: 1.1, t: 1 }));
// walk strip: 8 frames across one stride, body advancing at stride speed (feet must stay planted)
const stride = who === 'piper' ? 120 : 76;
for (let i = 0; i < 9; i++) {
  const ph = i / 8; const x = 120 + i * 230 + ph * 0;
  const P = R.merge(R.walk(ph, { B, stride, bob: who === 'piper' ? 3 : 6, arm: who === 'piper' ? .2 : .45 }), { yaw: Math.PI / 2 });
  PS.drawPerson(g, ch, P, { x, y: 1420, s: .85, t: ph });
}
g.strokeStyle = '#28170c'; g.beginPath(); g.moveTo(0, 1420); g.lineTo(2160, 1420); g.stroke();
fs.writeFileSync(out, cv.toBuffer('image/png'));
