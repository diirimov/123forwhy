// ===================================================================== shots2.js
'use strict';
const SHOTS = [];
const shot = (a, b, name, tr, draw, theme) => SHOTS.push({ a, b, name, tr, draw, theme });
const blink2 = (t, s = 0) => { const p = (t + s * 1.37) % 3.3; return p < .11 ? .05 : 1; };
const E2 = (name, t, s, o) => { const e = X(name, o); e.eye = (e.eye ?? 1) * (blink2(t, s) < .5 ? .05 : 1); return e; };
// ---- props held in hands (character-local coordinates, already scaled)
const POLE_L = 1150;
function poleAt(c, h, a, back = 260, len = POLE_L) { const dx = Math.sin(a), dy = -Math.cos(a); pole(c, h[0] - dx * back, h[1] - dy * back, h[0] + dx * (len - back), h[1] + dy * (len - back)); }
const carryPole = (a = -.55) => ({ back: (c, J) => poleAt(c, J.handN, a, 120, POLE_L) });
const raisePole = (a, back = 200) => ({ Rb: (c, J) => poleAt(c, J.handN, a, back, POLE_L) });
const twirlPole = (t, speed = 2.5) => ({ Rb: (c, J) => { const a = t * PI * speed; const h = J.handN; pole(c, h[0] - Math.sin(a) * 520, h[1] + Math.cos(a) * 520, h[0] + Math.sin(a) * 520, h[1] - Math.cos(a) * 520); } });
const holdBread2 = (s = .55, bite = 0, dx = 30, dy = -10) => ({ R: (c, J) => bread(c, J.handN[0] + dx, J.handN[1] + dy, s, bite) });

// ---- backgrounds
function townBG(c, t, camX, o = {}) {
  const S = SETS.town, g = S.ground;
  camX = Math.min(camX, S.w - W - 20);
  c.drawImage(S.sky, 0, 0);
  c.save(); c.globalAlpha = clamp((t - 3.2) / 16) * .3; c.fillStyle = lg(c, 0, 0, 0, H, [[0, '#ffb070'], [1, '#ffe0b0']]); c.fillRect(0, 0, W, H); c.restore();
  c.drawImage(S.far, -camX * .35 - 100, 0);
  for (const [x, h] of [[300, 520], [900, 640], [1500, 560], [2100, 600]]) smokePlume(c, x - camX * .35 - 100, 1180 - h, t, '#5a62a0', x, 1.2);
  fogBand(c, 1150, 200, t, '#c0b8e8', .18, 25, 5);
  c.drawImage(S.mid, -camX, 0);
  for (let i = 0; i < 9; i++) smokePlume(c, i * 300 + 220 - camX, 1460 - 740, t + i, '#b0a8c8', i + 20, .5);
  c.drawImage(S.street, -camX, g);
  for (const lx of [500, 1450, 2350]) lamp(c, lx - camX * 1.15, g + 160, 520, 1);
}
function privyBG(c, t, z = 1, cx = 540, cy = 960) {
  c.save(); cam(c, cx, cy, z); c.drawImage(SETS.privy.bg, 0, 0);
  lightShafts(c, 700, 0, .25, 260, 1700, '#ffe8b0', .16);
  candle(c, 140, 1520, 160, t, 1); candle(c, 940, 1520, 160, t, 2);
  c.restore();
}
function wakeBG(c, t, z = 1, cx = 540, cy = 960) {
  c.save(); cam(c, cx, cy, z); c.drawImage(SETS.cottageIn.bg, 0, 0);
  for (const [x, h, s] of [[110, 260, 1], [980, 230, 2]]) candle(c, x, 1600, h, t, s, .9);
  c.restore();
}
function stageBG2(c, t, z = 1, cx = 540, cy = 960) {
  c.save(); cam(c, cx, cy, z); c.drawImage(SETS.stage.bg, 0, 0);
  for (const [x0, ph, col] of [[150, 0, 'rgba(255,230,170,0.25)'], [930, 2, 'rgba(200,220,255,0.2)'], [540, 4, 'rgba(255,200,140,0.2)']]) {
    const ang = Math.sin(t * 1.3 + ph) * .25; c.save(); c.globalCompositeOperation = 'lighter'; c.translate(x0, 0); c.rotate(ang);
    c.fillStyle = lg(c, 0, 0, 0, 1600, [[0, col], [1, 'rgba(0,0,0,0)']]); c.beginPath(); c.moveTo(-30, 0); c.lineTo(30, 0); c.lineTo(260, 1600); c.lineTo(-260, 1600); c.fill(); c.restore(); }
  c.restore();
}




// choreography phrases (beats relative to the shot start, 4 beats = 1 bar, loops every 8 beats)
const DANCE = {
  ned: [[0, { view: 'q', shR: 2.6, elR: .3, shL: .3, elL: .6, hipR: .9, kneeR: .2, hipL: -.15, kneeL: .25, lean: -.12, expr: X('grin'), handL: 'open' }, 'back'],
    [1, { view: 'q', shR: 2.2, elR: .6, shL: 1.2, elL: 1.4, hipR: -.1, kneeR: .5, hipL: .2, kneeL: .5, air: 0, lean: .1, expr: X('shout'), handL: 'fist' }, 'back'],
    [2, { view: 'p', shR: 2.8, elR: .1, shL: -.6, elL: .3, hipR: .2, kneeR: 1.4, hipL: -.1, kneeL: .1, air: 40, lean: -.05, expr: X('grin'), handL: 'spread' }, 'back'],
    [3, { view: 'q', shR: 2.4, elR: .4, shL: .9, elL: .9, hipR: .1, kneeR: .6, hipL: .1, kneeL: .6, air: 0, lean: .15, expr: X('laugh'), handL: 'open' }, 'out'],
    [4, { view: 'q', shR: 2.6, elR: .3, shL: .3, elL: .6, hipR: .9, kneeR: .2, hipL: -.15, kneeL: .25, lean: -.12, expr: X('grin'), handL: 'open' }, 'back']],
  thomas: [[0, { view: 'q', shR: 1.6, elR: 1.2, shL: 2.7, elL: .3, hipR: .5, kneeR: .1, hipL: -.1, kneeL: .2, lean: -.08, expr: X('smug'), handR: 'open', handL: 'spread' }, 'back'],
    [1, { view: 'p', shR: .4, elR: 1.6, shL: 2.2, elL: .8, hipR: -.2, kneeR: .1, hipL: .5, kneeL: .1, lean: .45, head: .2, expr: X('smug'), handR: 'open', handL: 'open' }, 'io'],     // courtly bow
    [2, { view: 'q', shR: 2.8, elR: .1, shL: 2.8, elL: .1, hipR: .1, kneeR: .3, hipL: .1, kneeL: .3, air: 50, lean: -.1, expr: X('grin'), handR: 'spread', handL: 'spread' }, 'back'],
    [3, { view: 'f', shR: 1.2, elR: 1.6, shL: 1.2, elL: 1.6, hipR: .25, kneeR: .5, hipL: -.25, kneeL: .5, lean: 0, expr: X('happy'), handR: 'open', handL: 'open' }, 'io'],
    [4, { view: 'q', shR: 1.6, elR: 1.2, shL: 2.7, elL: .3, hipR: .5, kneeR: .1, hipL: -.1, kneeL: .2, lean: -.08, expr: X('smug'), handR: 'open', handL: 'spread' }, 'back']],
  sin: [[0, { view: 'q', shR: .6, elR: 1.6, shL: 1.8, elL: .6, hipR: .2, kneeR: .4, hipL: -.2, kneeL: .4, lean: .1, swing: .5, expr: X('mystic'), handR: 'open', handL: 'spread' }, 'io'],
    [2, { view: 'q', shR: 1.8, elR: .6, shL: .6, elL: 1.6, hipR: -.2, kneeR: .4, hipL: .2, kneeL: .4, lean: -.1, swing: -.5, expr: X('smug', { eye: .5 }), handR: 'spread', handL: 'open' }, 'io'],
    [3, { view: 'f', shR: 2.7, elR: .2, shL: 2.7, elL: .2, hipR: .3, kneeR: .8, hipL: -.3, kneeL: .8, lean: 0, swing: 0, air: 20, expr: X('grin'), handR: 'spread', handL: 'spread' }, 'back'],
    [4, { view: 'q', shR: .6, elR: 1.6, shL: 1.8, elL: .6, hipR: .2, kneeR: .4, hipL: -.2, kneeL: .4, lean: .1, swing: .5, expr: X('mystic'), handR: 'open', handL: 'spread' }, 'io']],
};
