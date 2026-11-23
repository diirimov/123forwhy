// Environment pieces, props, crowds, lights.
const L = require('./lib');
const { W, H, S, shape, line, limb, ellipse, mix, shade, alpha, clamp, lerp, ss, eo, hash, noise1, rng, glow, vgrad, text } = L;

const BEATS = require('./beats.json'); // video-time beats
function lastBeat(T) { let b = -10; for (const x of BEATS) { if (x <= T) b = x; else break; } return b; }
function beatIdx(T) { let i = -1; for (let k = 0; k < BEATS.length; k++) { if (BEATS[k] <= T) i = k; else break; } return i; }
function pulse(T, k = .14) { return Math.exp(-(T - lastBeat(T)) / k); }

function blink(T, seed) { const per = 2.2 + hash(seed) * 1.6; const ph = (T + hash(seed + 3) * per) % per; return ph < .12 ? Math.sin(ph / .12 * Math.PI) : 0; }
// front-view walk
function walk(t, f = 1.6, amp = 1) {
  const ph = t * f * Math.PI * 2; const s = Math.sin(ph);
  return {
    fl: [-34, -Math.max(0, s) * 34 * amp], fr: [34, -Math.max(0, -s) * 34 * amp], bob: -Math.abs(Math.cos(ph)) * 10 * amp,
    hl: [-86 + s * 12, -330 - s * 30 * amp], hr: [86 - s * 12, -330 + s * 30 * amp],
  };
}
function cam(g, c) { g.translate(W / 2, H / 2); g.rotate(c.r || 0); g.scale(c.z || 1, c.z || 1); g.translate(-(c.x ?? W / 2), -(c.y ?? H / 2)); }

// ---------- crowd ----------
function crowd(g, T, o) {
  // o: {y, rows, spread, scale, col, rim, seed, arms, wave}
  const r = rng(o.seed || 7);
  for (let row = 0; row < (o.rows || 3); row++) {
    const sc = (o.scale || 1) * (1 + row * .45); const y = o.y + row * 70 * sc; const n = Math.ceil((o.width || W * 1.4) / (70 * sc)) + 2;
    const col = mix(o.col || '#0b0b14', '#000000', row * .2);
    for (let i = 0; i < n; i++) {
      const x = (o.x0 ?? -W * .2) + i * 70 * sc + (r() - .5) * 30 * sc; const ph = r() * 6.28; const armsUp = r() < (o.arms ?? .5);
      const jump = (o.jump ?? 0) * Math.max(0, Math.sin(T * 9 + ph)) * 14 * sc;
      const yy = y - jump + (r() - .5) * 20 * sc;
      g.fillStyle = col; g.strokeStyle = col; g.lineCap = 'round';
      if (armsUp) {
        const w = Math.sin(T * (o.wave || 6) + ph) * .35;
        g.lineWidth = 11 * sc;
        g.beginPath(); g.moveTo(x - 18 * sc, yy - 50 * sc); g.lineTo(x - 30 * sc + w * 40 * sc, yy - 150 * sc); g.moveTo(x + 18 * sc, yy - 50 * sc); g.lineTo(x + 32 * sc - w * 30 * sc, yy - 150 * sc); g.stroke();
      }
      g.beginPath(); ellipse(g, x, yy - 78 * sc, 20 * sc, 24 * sc); g.fill();
      g.beginPath(); g.roundRect(x - 32 * sc, yy - 56 * sc, 64 * sc, 140 * sc, 22 * sc); g.fill();
      if (o.rim) { g.save(); g.globalAlpha = (o.rimA ?? .5) * (1 - row * .25); g.strokeStyle = o.rim; g.lineWidth = 3 * sc; g.beginPath(); g.arc(x, yy - 78 * sc, 21 * sc, Math.PI * 1.05, Math.PI * 1.95); g.stroke(); g.restore(); }
    }
  }
}
// phone-light / lighter dots in a far crowd sea
function crowdSea(g, T, y0, y1, col, seed = 3, density = 1) {
  const r = rng(seed);
  for (let i = 0; i < 900 * density; i++) {
    const yy = lerp(y0, y1, Math.pow(r(), .8)); const k = (yy - y0) / (y1 - y0 + 1e-3);
    const x = r() * W * 1.6 - W * .3; const s = lerp(3, 16, k);
    g.fillStyle = mix('#05050a', col, .18 + .3 * (1 - k)); g.beginPath(); ellipse(g, x, yy + Math.sin(T * 7 + i) * s * .3, s, s * 1.1); g.fill();
  }
}
// stage light beams (additive)
function beams(g, T, list) {
  g.save(); g.globalCompositeOperation = 'lighter';
  for (const b of list) {
    const ang = b.a + Math.sin(T * (b.sp || 1) + (b.ph || 0)) * (b.sw || .25);
    const len = b.len || 2200, wid = b.w || .12;
    const gr = g.createLinearGradient(b.x, b.y, b.x + Math.sin(ang) * len, b.y + Math.cos(ang) * len);
    gr.addColorStop(0, alpha(b.col, b.i ?? .55)); gr.addColorStop(1, alpha(b.col, 0));
    g.fillStyle = gr; g.beginPath(); g.moveTo(b.x, b.y);
    g.lineTo(b.x + Math.sin(ang - wid) * len, b.y + Math.cos(ang - wid) * len); g.lineTo(b.x + Math.sin(ang + wid) * len, b.y + Math.cos(ang + wid) * len); g.closePath(); g.fill();
    glow(g, b.x, b.y, 60, b.col, .9);
  }
  g.restore();
}
function haze(g, col, a, y0 = 0, y1 = H) { vgrad(g, 0, y0, W, y1 - y0, [[0, alpha(col, 0)], [.5, alpha(col, a)], [1, alpha(col, 0)]]); }

// ---------- Norway ----------
function mountains(g, y, h, col, seed, snow = true, amp = 1) {
  const r = rng(seed); const pts = []; let x = -200;
  while (x < W + 400) { pts.push([x, y - r() * h * amp]); x += 120 + r() * 220; }
  shape(g, g => { g.moveTo(-200, H + 400); pts.forEach(p => g.lineTo(p[0], p[1])); g.lineTo(W + 400, H + 400); g.closePath(); }, col, {
    lw: 4, inkColor: shade(col, -.4), shadeFn: snow ? g2 => {
      g2.fillStyle = 'rgba(235,242,255,.85)';
      pts.forEach((p, i) => { if (p[1] < y - h * .45) { g2.beginPath(); g2.moveTo(p[0], p[1]); g2.lineTo(p[0] - 70, p[1] + 90); g2.lineTo(p[0] - 20, p[1] + 70); g2.lineTo(p[0] + 10, p[1] + 100); g2.lineTo(p[0] + 60, p[1] + 80); g2.closePath(); g2.fill(); } });
    } : null
  });
}
function aurora(g, T, y, a = 1) {
  g.save(); g.globalCompositeOperation = 'lighter';
  for (let k = 0; k < 3; k++) {
    g.beginPath();
    for (let x = -50; x <= W + 50; x += 20) { const yy = y + k * 60 + Math.sin(x * .006 + T * .6 + k) * 70 + noise1(x * .01 + T * .3 + k * 5) * 40; x === -50 ? g.moveTo(x, yy) : g.lineTo(x, yy); }
    g.lineTo(W + 50, y + 500); g.lineTo(-50, y + 500); g.closePath();
    const gr = g.createLinearGradient(0, y - 100, 0, y + 400); gr.addColorStop(0, `rgba(80,255,170,${.0})`); gr.addColorStop(.25, `rgba(80,255,170,${.22 * a})`); gr.addColorStop(.6, `rgba(90,120,255,${.10 * a})`); gr.addColorStop(1, 'rgba(0,0,0,0)');
    g.fillStyle = gr; g.fill();
  }
  g.restore();
}
function snow(g, T, n = 160, seed = 2, wind = 30, size = 1) {
  const r = rng(seed); g.fillStyle = 'rgba(255,255,255,.85)';
  for (let i = 0; i < n; i++) { const z = .4 + r(); const sp = 90 * z; const x = ((r() * W + T * wind * z + Math.sin(T + i) * 20) % W + W) % W; const y = ((r() * H + T * sp) % H); g.beginPath(); ellipse(g, x, y, 3 * z * size, 3 * z * size); g.fill(); }
}
function woodHouse(g, x, y, w, h, col, winOn = 1, T = 0) {
  shape(g, g => { g.rect(x - w / 2, y - h, w, h); }, col, { shadeFn: g2 => { g2.strokeStyle = 'rgba(0,0,0,.2)'; g2.lineWidth = 3; for (let xx = x - w / 2; xx < x + w / 2; xx += 22) { g2.beginPath(); g2.moveTo(xx, y - h); g2.lineTo(xx, y); g2.stroke(); } } });
  shape(g, g => { g.moveTo(x - w / 2 - 30, y - h + 4); g.lineTo(x, y - h - w * .42); g.lineTo(x + w / 2 + 30, y - h + 4); g.closePath(); }, '#2b2f3e', { shadeFn: g2 => { g2.fillStyle = '#e9f0fb'; g2.fillRect(x - w, y - h - w * .5, w * 2, 26); } });
  // snow on roof
  shape(g, g => { g.moveTo(x - w / 2 - 34, y - h + 2); g.lineTo(x, y - h - w * .45); g.lineTo(x + w / 2 + 34, y - h + 2); g.lineTo(x + w / 2 + 20, y - h - 14); g.lineTo(x, y - h - w * .45 + 22); g.lineTo(x - w / 2 - 20, y - h - 14); g.closePath(); }, '#eef3fb', { lw: 4 });
  for (const wx of [x - w * .22, x + w * .22]) {
    const ww = w * .2, wh = h * .34; const wy = y - h * .62;
    shape(g, g => { g.rect(wx - ww / 2, wy, ww, wh); }, winOn ? '#ffc76a' : '#30364a', { lw: 5 });
    if (winOn) glow(g, wx, wy + wh / 2, ww * 1.8, '#ffb347', .35 + .05 * Math.sin(T * 7));
    line(g, g => { g.moveTo(wx, wy); g.lineTo(wx, wy + wh); g.moveTo(wx - ww / 2, wy + wh / 2); g.lineTo(wx + ww / 2, wy + wh / 2); }, 4, '#3a2a1e');
  }
}
function pine(g, x, y, h, col = '#1f3a3a', snowy = true) {
  shape(g, g => { g.moveTo(x, y - h); for (let i = 0; i < 4; i++) { const yy = y - h + h * (i + 1) * .24; const ww = h * (.12 + i * .08); g.lineTo(x + ww, yy); g.lineTo(x + ww * .45, yy - h * .02); } g.lineTo(x + h * .06, y); g.lineTo(x - h * .06, y); for (let i = 3; i >= 0; i--) { const yy = y - h + h * (i + 1) * .24; const ww = h * (.12 + i * .08); g.lineTo(x - ww * .45, yy - h * .02); g.lineTo(x - ww, yy); } g.closePath(); }, col, {
    lw: 4, shadeFn: snowy ? g2 => { g2.fillStyle = 'rgba(235,242,255,.8)'; for (let i = 0; i < 4; i++) { const yy = y - h + h * i * .24 + h * .14; g2.fillRect(x - h * .4, yy, h * .8, h * .035); } } : null
  });
}

// ---------- London ----------
function terrace(g, x0, y, n, T, o = {}) {
  const r = rng(o.seed || 11);
  for (let i = 0; i < n; i++) {
    const w = 300, h = 640 + (i % 2) * 20; const x = x0 + i * w;
    const brick = mix('#5a3a34', '#3e2c33', r() * .6);
    shape(g, g => { g.rect(x, y - h, w, h); }, brick, {
      lw: 5, shadeFn: g2 => {
        g2.strokeStyle = 'rgba(0,0,0,.18)'; g2.lineWidth = 2;
        for (let yy = y - h; yy < y; yy += 18) { g2.beginPath(); g2.moveTo(x, yy); g2.lineTo(x + w, yy); g2.stroke(); }
        g2.fillStyle = 'rgba(20,20,40,.35)'; g2.fillRect(x, y - h, w, h);
      }
    });
    // chimney
    shape(g, g => { g.rect(x + w * .7, y - h - 70, 50, 70); }, shade(brick, -.15), { lw: 4 });
    // windows: 2 floors x 2
    for (let fl = 0; fl < 2; fl++) for (let c = 0; c < 2; c++) {
      const wx = x + 50 + c * 130, wy = y - h + 80 + fl * 230; const lit = o.lit && o.lit(i, fl, c);
      shape(g, g => { g.rect(wx, wy, 80, 130); }, lit ? '#ffcf7a' : '#1b2033', { lw: 5, shadeFn: g2 => { if (!lit) { g2.fillStyle = 'rgba(120,140,200,.12)'; g2.fillRect(wx, wy, 40, 130); } } });
      line(g, g => { g.moveTo(wx + 40, wy); g.lineTo(wx + 40, wy + 130); g.moveTo(wx, wy + 65); g.lineTo(wx + 80, wy + 65); }, 4, '#2a1e1a');
      shape(g, g => { g.rect(wx - 8, wy + 128, 96, 12); }, '#d9d2c4', { lw: 3 });
      if (lit) glow(g, wx + 40, wy + 65, 150, '#ffb347', .35);
    }
    // door
    shape(g, g => { g.rect(x + 110, y - 170, 80, 170); }, ['#1f3a5a', '#6a1e24', '#1e3d2e'][i % 3], { lw: 5 });
  }
}
function rain(g, T, n = 220, seed = 4, col = 'rgba(190,210,255,.35)') {
  const r = rng(seed); g.strokeStyle = col; g.lineWidth = 2.5; g.beginPath();
  for (let i = 0; i < n; i++) { const z = .5 + r(); const x = (r() * W * 1.2 + T * 80) % (W * 1.2) - 50; const y = (r() * H + T * 1900 * z) % H; g.moveTo(x, y); g.lineTo(x - 8, y + 46 * z); }
  g.stroke();
}
function bus(g, x, y, sc = 1) {
  g.save(); g.translate(x, y); g.scale(sc, sc);
  shape(g, g => { g.roundRect(-330, -380, 660, 380, 26); }, '#c3242c', { shadeFn: g2 => { g2.fillStyle = 'rgba(0,0,0,.18)'; g2.fillRect(-330, -60, 660, 60); g2.fillStyle = 'rgba(255,255,255,.12)'; g2.fillRect(-330, -380, 660, 40); } });
  for (let row = 0; row < 2; row++) for (let i = 0; i < 5; i++) { shape(g, g => { g.rect(-300 + i * 122, -350 + row * 160, 104, 100); }, '#ffd88a', { lw: 4 }); }
  shape(g, g => { ellipse(g, -200, 0, 44, 44); }, '#151515', { lw: 4 }); shape(g, g => { ellipse(g, 210, 0, 44, 44); }, '#151515', { lw: 4 });
  g.restore();
}
function lamp(g, x, y, h, T) {
  line(g, g => { g.moveTo(x, y); g.lineTo(x, y - h); g.quadraticCurveTo(x, y - h - 40, x + 40, y - h - 40); }, 10, '#15151c');
  shape(g, g => { g.moveTo(x + 20, y - h - 50); g.lineTo(x + 70, y - h - 50); g.lineTo(x + 60, y - h - 20); g.lineTo(x + 30, y - h - 20); g.closePath(); }, '#ffe3a1', { lw: 4 });
  glow(g, x + 45, y - h - 20, 320, '#ffcf80', .45);
}

// ---------- interiors ----------
function flatRoom(g, T, mood = 0) { // mood 0 warm night, 1 cold dawn
  const wall = mix('#6b4f45', '#4a5266', mood), wall2 = mix('#7d5d4e', '#58627a', mood);
  vgrad(g, 0, 0, W, H, [[0, shade(wall, -.25)], [.6, wall], [1, shade(wall, -.3)]]);
  // wallpaper stripes
  g.save(); g.globalAlpha = .18; g.fillStyle = wall2; for (let x = 0; x < W; x += 60) g.fillRect(x, 0, 26, H * .72); g.restore();
  // sloped ceiling
  shape(g, g => { g.moveTo(-20, -20); g.lineTo(W + 20, -20); g.lineTo(W + 20, 160); g.lineTo(-20, 420); g.closePath(); }, shade(wall, -.35), { lw: 5 });
  // floor
  shape(g, g => { g.rect(-20, H * .72, W + 40, H); }, mix('#5a3e2c', '#3d3f4a', mood), { shadeFn: g2 => { g2.strokeStyle = 'rgba(0,0,0,.25)'; g2.lineWidth = 3; for (let x = -200; x < W + 200; x += 110) { g2.beginPath(); g2.moveTo(x, H * .72); g2.lineTo(x * 1.6 - W * .3, H); g2.stroke(); } } });
  // posters
  shape(g, g => { g.rect(90, 560, 170, 230); }, '#d9cba8', { lw: 4, shadeFn: g2 => { g2.fillStyle = '#b03a2e'; g2.beginPath(); ellipse(g2, 175, 650, 50, 50); g2.fill(); g2.fillStyle = '#222'; g2.fillRect(110, 730, 130, 16); } });
  shape(g, g => { g.rect(800, 600, 150, 200); }, '#9fb6c9', { lw: 4, shadeFn: g2 => { g2.fillStyle = '#2b3550'; g2.fillRect(815, 620, 120, 110); g2.fillStyle = '#f2e6c8'; g2.fillRect(815, 745, 90, 14); } });
}
function windowRain(g, x, y, w, h, T, night = 1) {
  shape(g, g => { g.rect(x, y, w, h); }, mix('#8fa6c6', '#1a2238', night), { lw: 8, shadeFn: g2 => { for (let i = 0; i < 6; i++) { g2.fillStyle = `rgba(255,210,120,${.25 * night})`; g2.fillRect(x + 20 + i * 45, y + h * .6 + (i % 3) * 20, 18, 26); } rain(g2, T, 60, 9, 'rgba(220,230,255,.35)'); } });
  line(g, g => { g.moveTo(x + w / 2, y); g.lineTo(x + w / 2, y + h); g.moveTo(x, y + h / 2); g.lineTo(x + w, y + h / 2); }, 8, '#3a2c24');
}
function clock(g, x, y, r, t) {
  shape(g, g => { ellipse(g, x, y, r, r); }, '#f3ede0', { lw: 6 });
  for (let i = 0; i < 12; i++) { const a = i / 12 * Math.PI * 2; line(g, g => { g.moveTo(x + Math.cos(a) * r * .8, y + Math.sin(a) * r * .8); g.lineTo(x + Math.cos(a) * r * .92, y + Math.sin(a) * r * .92); }, 3); }
  const hA = t / 12 * Math.PI * 2 - Math.PI / 2, mA = t * Math.PI * 2 - Math.PI / 2;
  line(g, g => { g.moveTo(x, y); g.lineTo(x + Math.cos(hA) * r * .5, y + Math.sin(hA) * r * .5); }, 7);
  line(g, g => { g.moveTo(x, y); g.lineTo(x + Math.cos(mA) * r * .78, y + Math.sin(mA) * r * .78); }, 4.5);
}
function mattress(g, x, y, w) { shape(g, g => { g.roundRect(x - w / 2, y - 60, w, 70, 20); }, '#cfc6b4', { shadeFn: g2 => { g2.fillStyle = '#8b6a8a'; g2.fillRect(x - w / 2, y - 60, w * .55, 70); } }); }
function mug(g, x, y, col = '#e8e2d6') { shape(g, g => { g.roundRect(x - 18, y - 40, 36, 40, 6); }, col, { lw: 4 }); line(g, g => { g.arc(x + 20, y - 22, 10, -1.4, 1.4); }, 4); }

function reel(g, x, y, r, ang, tape = .6) {
  shape(g, g => { ellipse(g, x, y, r, r); }, '#b9bcc4', { lw: 5 });
  shape(g, g => { ellipse(g, x, y, r * (.35 + tape * .55), r * (.35 + tape * .55)); }, '#3b2a22', { lw: 3 });
  for (let i = 0; i < 3; i++) { const a = ang + i * Math.PI * 2 / 3; shape(g, g => { g.moveTo(x, y); g.arc(x, y, r * .3, a - .4, a + .4); g.closePath(); }, '#e9eaee', { lw: 3 }); }
  shape(g, g => { ellipse(g, x, y, r * .1, r * .1); }, '#222', { lw: 3 });
}
function tapeMachine(g, x, y, sc, T, spin, counter, rec = false) {
  g.save(); g.translate(x, y); g.scale(sc, sc);
  shape(g, g => { g.roundRect(-380, -420, 760, 840, 30); }, '#4d4f58', { shadeFn: g2 => { vgrad(g2, -380, -420, 760, 840, [[0, 'rgba(255,255,255,.12)'], [1, 'rgba(0,0,0,.25)']]); } });
  reel(g, -190, -200, 160, spin, .7); reel(g, 190, -200, 160, spin * 1.08, .4);
  line(g, g => { g.moveTo(-190 - 115, -200 + 60); g.lineTo(-60, 60); g.lineTo(60, 60); g.lineTo(190 + 70, -200 + 120); }, 6, '#3b2a22');
  shape(g, g => { g.roundRect(-120, 30, 240, 80, 10); }, '#2a2b30', { lw: 4 });
  // counter
  shape(g, g => { g.roundRect(-140, 160, 280, 90, 10); }, '#111', { lw: 4 });
  text(g, String(Math.max(0, Math.floor(counter))).padStart(4, '0'), 0, 232, 76, { font: 'InterXB', color: '#f2f2f2', shadow: false, track: 8 });
  // buttons
  for (let i = 0; i < 5; i++) shape(g, g => { g.roundRect(-250 + i * 105, 300, 80, 60, 8); }, i === 4 ? (rec ? '#ff2d2d' : '#7a1b1b') : '#c9cbd2', { lw: 4 });
  if (rec) glow(g, 210 + 40 - 40, 330, 160, '#ff3030', .6);
  g.restore();
}
function mixDesk(g, x, y, w, T, lift = 0) {
  shape(g, g => { g.moveTo(x - w / 2, y); g.lineTo(x + w / 2, y); g.lineTo(x + w / 2 + 80, y + 420); g.lineTo(x - w / 2 - 80, y + 420); g.closePath(); }, '#33343c', { shadeFn: g2 => { vgrad(g2, x - w, y, w * 2, 420, [[0, 'rgba(255,255,255,.08)'], [1, 'rgba(0,0,0,.3)']]); } });
  const n = 14;
  for (let i = 0; i < n; i++) {
    const fx = x - w / 2 + 40 + i * (w - 80) / (n - 1);
    line(g, g => { g.moveTo(fx, y + 60); g.lineTo(fx, y + 260); }, 5, '#111');
    const pos = clamp(.3 + .2 * Math.sin(i * 1.7 + T * 2) * .5 + lift * (.4 + .2 * Math.sin(i)), 0, 1);
    shape(g, g => { g.roundRect(fx - 14, y + 240 - pos * 180, 28, 30, 5); }, '#e8e8ec', { lw: 3 });
    for (let k = 0; k < 3; k++) shape(g, g => { ellipse(g, fx, y + 290 + k * 34, 9, 9); }, ['#d94c4c', '#e0b84a', '#4ca3d9'][k], { lw: 2.5 });
  }
}
function vu(g, x, y, w, v) {
  shape(g, g => { g.roundRect(x - w / 2, y - w * .35, w, w * .6, 10); }, '#f1e2b0', { lw: 4, shadeFn: g2 => { g2.fillStyle = 'rgba(255,190,80,.35)'; g2.fillRect(x - w / 2, y - w * .35, w, w * .6); } });
  line(g, g => { g.arc(x, y + w * .2, w * .38, Math.PI * 1.2, Math.PI * 1.8); }, 3);
  g.save(); g.strokeStyle = '#d02b2b'; g.lineWidth = 5; g.beginPath(); g.arc(x, y + w * .2, w * .38, Math.PI * 1.65, Math.PI * 1.8); g.stroke(); g.restore();
  const a = Math.PI * (1.25 + .55 * clamp(v));
  line(g, g => { g.moveTo(x, y + w * .2); g.lineTo(x + Math.cos(a) * w * .42, y + w * .2 + Math.sin(a) * w * .42); }, 3.5, '#111');
}

// record sleeve (original design)
function sleeve(g, x, y, s, rot = 0, o = {}) {
  g.save(); g.translate(x, y); g.rotate(rot); g.scale(s, s);
  shape(g, g => { g.rect(-150, -150, 300, 300); }, o.bg || '#e9e4d6', {
    lw: 5, shadeFn: g2 => {
      // pencil-like portrait lines motif
      g2.strokeStyle = '#2a2a2e'; g2.lineWidth = 3; g2.globalAlpha = .75;
      for (let i = 0; i < 3; i++) { g2.beginPath(); ellipse(g2, -70 + i * 70, 10, 26, 34); g2.stroke(); g2.beginPath(); g2.moveTo(-100 + i * 70, 90); g2.quadraticCurveTo(-70 + i * 70, 40, -40 + i * 70, 90); g2.stroke(); }
      g2.globalAlpha = 1;
      g2.fillStyle = o.accent || '#c8323c'; g2.fillRect(-150, -150, 300, 56);
    }
  });
  text(g, 'a-ha', -132, -108, 40, { font: 'InterXB', align: 'left', color: '#fff', shadow: false });
  text(g, 'TAKE ON ME', 132, -108, 26, { font: 'InterB', align: 'right', color: '#fff', shadow: false });
  if (o.year) text(g, o.year, 132, 136, 26, { font: 'InterB', align: 'right', color: '#2a2a2e', shadow: false });
  g.restore();
}
function vinyl(g, x, y, r, ang) {
  shape(g, g => { ellipse(g, x, y, r, r); }, '#121214', { lw: 4, shadeFn: g2 => { g2.strokeStyle = 'rgba(255,255,255,.08)'; g2.lineWidth = 2; for (let k = r * .4; k < r; k += 8) { g2.beginPath(); g2.arc(x, y, k, 0, 7); g2.stroke(); } g2.strokeStyle = 'rgba(255,255,255,.25)'; g2.lineWidth = 6; g2.beginPath(); g2.arc(x, y, r * .8, ang, ang + .5); g2.stroke(); } });
  shape(g, g => { ellipse(g, x, y, r * .32, r * .32); }, '#c8323c', { lw: 3 });
}

// CRT TV
function tv(g, x, y, w, on, content, o = {}) {
  const h = w * .78;
  shape(g, g => { g.roundRect(x - w / 2, y - h / 2, w, h, w * .08); }, o.body || '#4a3a30', { lw: 6, shadeFn: g2 => { g2.fillStyle = 'rgba(255,255,255,.08)'; g2.fillRect(x - w / 2, y - h / 2, w, h * .2); } });
  const sx = x - w * .42, sy = y - h * .4, sw = w * .7, sh = h * .78;
  g.save(); g.beginPath(); g.roundRect(sx, sy, sw, sh, w * .06); g.clip();
  g.fillStyle = '#0c0f12'; g.fillRect(sx, sy, sw, sh);
  if (on > 0) { g.globalAlpha = on; if (content) content(g, sx, sy, sw, sh); g.globalAlpha = 1; g.fillStyle = 'rgba(0,0,0,.12)'; for (let yy = sy; yy < sy + sh; yy += 6) g.fillRect(sx, yy, sw, 2); }
  g.restore();
  line(g, g => { g.roundRect(sx, sy, sw, sh, w * .06); }, 6);
  for (let i = 0; i < 2; i++) shape(g, g => { ellipse(g, x + w * .4, y - h * .2 + i * h * .22, w * .04, w * .04); }, '#c9b9a0', { lw: 3 });
  if (on > 0 && S.mode === 'color') { g.save(); g.globalCompositeOperation = 'lighter'; glow(g, x - w * .07, y, w * 1.1, o.glow || '#7fb7ff', .22 * on); g.restore(); }
}

// paper background
function paper(g, T, col = '#f3efe4') {
  g.fillStyle = col; g.fillRect(-600, -600, W + 1200, H + 1200);
  const r = rng(77); g.fillStyle = 'rgba(120,100,70,.05)';
  for (let i = 0; i < 400; i++) { g.fillRect(r() * W, r() * H, 2 + r() * 3, 2 + r() * 3); }
  // faint ruled grid
  g.strokeStyle = 'rgba(80,110,160,.08)'; g.lineWidth = 2; g.beginPath(); for (let y = 0; y < H; y += 64) { g.moveTo(0, y); g.lineTo(W, y); } g.stroke();
}
function pencil(g, x, y, ang = -.9, sc = 1) {
  g.save(); g.translate(x, y); g.rotate(ang); g.scale(sc, sc);
  const sm = S.mode; S.mode = 'color';
  shape(g, g => { g.moveTo(0, 0); g.lineTo(60, -18); g.lineTo(60, 18); g.closePath(); }, '#e9c79a', { lw: 4 });
  shape(g, g => { g.moveTo(0, 0); g.lineTo(18, -5.5); g.lineTo(18, 5.5); g.closePath(); }, '#2b2b2b', { lw: 3 });
  shape(g, g => { g.rect(60, -18, 380, 36); }, '#f2b92e', { lw: 4, shadeFn: g2 => { g2.fillStyle = 'rgba(255,255,255,.3)'; g2.fillRect(60, -18, 380, 10); } });
  shape(g, g => { g.rect(440, -19, 40, 38); }, '#b9b9c0', { lw: 4 });
  shape(g, g => { g.roundRect(480, -18, 50, 36, 10); }, '#e78a9a', { lw: 4 });
  S.mode = sm; g.restore();
}

// a big expressive hand (reaching), local origin at wrist, pointing up
function hand(g, x, y, s, rot = 0, spread = 1) {
  g.save(); g.translate(x, y); g.rotate(rot); g.scale(s, s);
  const skin = '#f1c7a6';
  limb(g, [[0, 260], [0, 40]], 120, '#1e1e26');
  shape(g, g => { g.moveTo(-70, 40); g.bezierCurveTo(-80, -40, -70, -90, -40, -110); g.lineTo(50, -110); g.bezierCurveTo(80, -80, 84, -20, 70, 40); g.closePath(); }, skin, { lw: 6 });
  const fingers = [[-58, -100, -.35 * spread, 110], [-22, -112, -.12 * spread, 140], [14, -112, .06 * spread, 145], [48, -100, .25 * spread, 120]];
  fingers.forEach(([fx, fy, a, len]) => limb(g, [[fx, fy], [fx + Math.sin(a) * len * .5, fy - Math.cos(a) * len * .5], [fx + Math.sin(a * 1.2) * len, fy - Math.cos(a * 1.2) * len]], 30, skin, { lw: 6 }));
  limb(g, [[-62, -10], [-110, -50], [-130 - 20 * spread, -100]], 32, skin, { lw: 6 });
  g.restore();
}

module.exports = { BEATS, lastBeat, beatIdx, pulse, blink, walk, cam, crowd, crowdSea, beams, haze, mountains, aurora, snow, woodHouse, pine, terrace, rain, bus, lamp, flatRoom, windowRain, clock, mattress, mug, reel, tapeMachine, mixDesk, vu, sleeve, vinyl, tv, paper, pencil, hand };
