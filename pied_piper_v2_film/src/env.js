// env: medieval Hamelin kit -- sky, skyline, timber-framed houses, cobbles, props, gate, river, mountain, interiors
'use strict';
const C = require('./core');
const K = require('./ink');
const { clamp, lerp, TAU, noise, hash, rng } = C;
const { PAL, INK } = K;

// emissive lights collected while drawing (drawn after the colour grade)
// LIGHTS also holds occluders in draw order: an occluder erases the lights recorded before it (farther away)
const LIGHTS = [];
function addLight(g, x, y, r, col, a = 1, kind = 'glow') {
  const m = g.getTransform(); const sx = Math.hypot(m.a, m.b);
  LIGHTS.push({ x: m.a * x + m.c * y + m.e, y: m.b * x + m.d * y + m.f, r: r * sx, col, a, kind });
}
function addLightRect(g, x, y, w, h, col, a = 1) {
  const m = g.getTransform(); const sx = Math.hypot(m.a, m.b);
  LIGHTS.push({ kind: 'rect', x: m.a * x + m.c * y + m.e, y: m.b * x + m.d * y + m.f, w: w * sx, h: h * sx, col, a });
}
function occlude(g, fn) { LIGHTS.push({ kind: 'occ', m: g.getTransform(), fn }); }
function occludePoly(g, P) { occlude(g, (g2) => { g2.beginPath(); K.poly(g2, P); g2.fill(); }); }

// ---------------------------------------------------------------- sky
function sky(g, mood, w, h, t = 0, o = {}) {
  const gr = g.createLinearGradient(0, 0, 0, h);
  if (mood === 'night') { gr.addColorStop(0, '#1d2540'); gr.addColorStop(.6, '#33416a'); gr.addColorStop(1, '#4b5a84'); }
  else if (mood === 'dusk') { gr.addColorStop(0, '#3d2c4d'); gr.addColorStop(.55, '#8a5a6b'); gr.addColorStop(1, '#d9925e'); }
  else { gr.addColorStop(0, '#cfd3c8'); gr.addColorStop(1, '#efe3c4'); }
  g.fillStyle = gr; g.fillRect(-w, -h * .2, w * 3, h * 1.4);
  if (mood === 'night') {
    const r = rng(77);
    for (let i = 0; i < 90; i++) { const x = r() * w, y = r() * h * .7, s = r() * 2.2 + .6; const tw = .6 + .4 * Math.sin(t * (1 + r() * 3) + i); g.fillStyle = `rgba(255,248,225,${.55 * tw})`; g.beginPath(); g.arc(x, y, s, 0, TAU); g.fill(); }
  }
}
function moon(g, x, y, r, o = {}) {
  K.glow(g, x, y, r * 3.2, '#9fb3e0', .35, 'source-over');
  K.ellipse(g, x, y, r, r, { fill: '#f3ead2', lw: o.lw ?? 4 });
  g.save(); g.globalAlpha = .18; g.fillStyle = '#a99f86';
  [[-.3, -.2, .22], [.25, .15, .16], [.05, .38, .1], [-.1, .1, .08]].forEach(([a, b, c]) => { g.beginPath(); g.arc(x + a * r, y + b * r, c * r, 0, TAU); g.fill(); });
  g.restore();
  addLight(g, x, y, r * 4, '#8fa6d8', .45);
}
function sun(g, x, y, r, t = 0) { // the studio's ink sun
  g.save(); g.translate(x, y); g.rotate(t * .1);
  for (let i = 0; i < 16; i++) { const a = i / 16 * TAU; const L = i % 2 ? r * .55 : r * .85; K.line(g, [[Math.cos(a) * r * 1.15, Math.sin(a) * r * 1.15], [Math.cos(a) * (r * 1.15 + L), Math.sin(a) * (r * 1.15 + L)]], 4, INK, .85, false); }
  K.ellipse(g, 0, 0, r, r, { fill: '#e7c46a', lw: 4 });
  g.restore();
}
function cloud(g, x, y, s, a = 1) {
  const P = [[-90, 10], [-80, -12], [-50, -28], [-15, -38], [25, -30], [55, -40], [85, -22], [100, 8]].map(p => [x + p[0] * s, y + p[1] * s]);
  K.shape(g, P, { fill: '#f1e9d6', lw: 3.5, alpha: a, closed: true, tension: .7 });
}
// far skyline: Marktkirche spire + roofs (pale, low contrast like the studio's cathedral)
function skyline(g, x0, y, w, mood, seed = 3) {
  const col = mood === 'night' ? '#3a4566' : mood === 'dusk' ? '#6b4a62' : '#d8cdb8';
  const ink = mood === 'night' ? '#202a44' : mood === 'dusk' ? '#3f2a3f' : '#a3957c';
  const r = rng(seed);
  const P = [[x0, y]];
  let x = x0;
  while (x < x0 + w) {
    const bw = 50 + r() * 90, bh = 60 + r() * 120;
    P.push([x, y - bh * .55]); P.push([x + bw / 2, y - bh]); P.push([x + bw, y - bh * .55]); x += bw;
  }
  P.push([x0 + w, y]);
  K.shape(g, P, { fill: col, lw: 3, ink, smooth: false });
  // church with twin spires (Hamelin Marktkirche-like)
  const cx = x0 + w * .45;
  K.shape(g, [[cx - 120, y], [cx - 120, y - 200], [cx + 120, y - 200], [cx + 120, y]], { fill: col, lw: 3, ink, smooth: false });
  K.shape(g, [[cx - 140, y - 195], [cx, y - 290], [cx + 140, y - 195]], { fill: col, lw: 3, ink, smooth: false });
  for (const sd of [-1, 1]) {
    const sx = cx + sd * 70;
    K.shape(g, [[sx - 34, y - 190], [sx - 34, y - 380], [sx + 34, y - 380], [sx + 34, y - 190]], { fill: col, lw: 3, ink, smooth: false });
    K.shape(g, [[sx - 40, y - 375], [sx, y - 560], [sx + 40, y - 375]], { fill: col, lw: 3, ink, smooth: false });
    K.ellipse(g, sx, y - 300, 9, 18, { fill: mood === 'night' ? '#2b3554' : ink, lw: 0, alpha: .6 });
  }
}

// ---------------------------------------------------------------- timber-framed house
// x: left, y: ground, w, h (wall height to eaves). o: {mood, lit (0..1 windows lit), shutter(i)->0..1 open, door 0..1 open, seed}
function house(g, x, y, w, h, o = {}) {
  const r = rng(o.seed ?? 1);
  const night = o.mood === 'night', dusk = o.mood === 'dusk';
  const plaster = o.plaster || [PAL.plaster, '#e6d7b8', '#ddc9a5', '#e9dcc2', '#d7c4a2'][Math.floor(r() * 5)];
  const beam = o.beam || [PAL.beam, '#4e3322', '#654229', '#5b3a24'][Math.floor(r() * 4)];
  const roofC = o.roof || [PAL.roof, '#7c4030', '#93513a', '#6e3a2b', '#8a5a3c'][Math.floor(r() * 5)];
  const lw = o.lw ?? 4;
  const floors = o.floors || (h > 330 ? 3 : 2);
  const fh = h / floors;
  const jet = o.jetty ?? 10;
  { const rx0 = x - jet * (floors - 1) - 14, rx1 = x + w + jet * (floors - 1) + 14; occludePoly(g, [[x, y], [x - jet * (floors - 1), y - h], [rx0, y - h], [(rx0 + rx1) / 2, y - h - (rx1 - rx0) * (o.roofPitch ?? .75)], [rx1, y - h], [x + w + jet * (floors - 1), y - h], [x + w, y]]); }
  // walls (each upper floor overhangs a little)
  for (let f = 0; f < floors; f++) {
    const fx = x - jet * f, fw = w + jet * 2 * f, fy = y - fh * (f + 1);
    K.shape(g, [[fx, fy], [fx + fw, fy], [fx + fw, fy + fh], [fx, fy + fh]], { fill: plaster, lw, smooth: false,
      inner: (g2) => { g2.fillStyle = 'rgba(70,40,20,.08)'; for (let i = 0; i < 6; i++) { g2.beginPath(); g2.ellipse(fx + r() * fw, fy + r() * fh, 20 + r() * 40, 10 + r() * 20, 0, 0, TAU); g2.fill(); } } });
    // beams: frame, posts, braces
    const bw = 9;
    const bm = (a, b, c, d) => K.shape(g, [[a, b], [c, b], [c, d], [a, d]], { fill: beam, lw: lw * .7, smooth: false });
    bm(fx, fy, fx + fw, fy + bw); bm(fx, fy + fh - bw, fx + fw, fy + fh);
    const posts = Math.max(2, Math.round(fw / 70));
    for (let i = 0; i <= posts; i++) { const px = fx + (fw - bw) * i / posts; bm(px, fy, px + bw, fy + fh); }
    // braces in alternate bays
    for (let i = 0; i < posts; i++) {
      const a = fx + (fw - bw) * i / posts + bw, b = fx + (fw - bw) * (i + 1) / posts;
      const kind = Math.floor(hash(i * 7 + (o.seed || 1) * 13 + f) * 4);
      g.save(); g.strokeStyle = INK; g.lineWidth = bw + lw * .7; g.lineCap = 'butt';
      const segs = kind === 0 ? [[a, fy + fh, b, fy]] : kind === 1 ? [[a, fy, b, fy + fh]] : kind === 2 ? [[a, fy + fh, (a + b) / 2, fy + fh * .4], [(a + b) / 2, fy + fh * .4, b, fy + fh]] : [];
      for (const [x1, y1, x2, y2] of segs) { g.strokeStyle = INK; g.lineWidth = bw + lw * 1.4; g.beginPath(); g.moveTo(x1, y1); g.lineTo(x2, y2); g.stroke(); g.strokeStyle = beam; g.lineWidth = bw; g.beginPath(); g.moveTo(x1, y1); g.lineTo(x2, y2); g.stroke(); }
      g.restore();
      // window in some bays
      const winH = fh * .38, winW = Math.min(46, (b - a) * .6);
      const hasWin = (f > 0 || i % 2 === 1 || o.allWindows) && kind !== 2;
      if (hasWin && b - a > 40) {
        const wx = (a + b) / 2 - winW / 2, wy = fy + fh * .28;
        const idx = f * 10 + i;
        const op = o.shutter ? clamp(o.shutter(idx, f, i)) : 0;
        const lit = o.litByShutter ? (op > .35 ? 1 : 0) : (night || dusk) && (o.litAlways || Math.hypot(g.getTransform().a, g.getTransform().b) > .5) ? (hash(idx * 3.1 + (o.seed || 1)) < (o.lit ?? .7) ? 1 : 0) : 0;
        window_(g, wx, wy, winW, winH, { lit, open: op, lw, beam, night });
      }
    }
  }
  // roof (gable facing viewer)
  const topY = y - h, rx0 = x - jet * (floors - 1) - 14, rx1 = x + w + jet * (floors - 1) + 14;
  const peak = topY - (rx1 - rx0) * (o.roofPitch ?? .75);
  K.shape(g, [[rx0, topY + 4], [(rx0 + rx1) / 2, peak], [rx1, topY + 4]], { fill: roofC, lw, smooth: false, inner: (g2) => {
    g2.strokeStyle = 'rgba(40,20,10,.35)'; g2.lineWidth = 2.5;
    for (let yy = peak + 22; yy < topY; yy += 20) { g2.beginPath(); g2.moveTo(rx0 - 10, yy); g2.lineTo(rx1 + 10, yy); g2.stroke(); }
    g2.fillStyle = 'rgba(30,10,5,.18)'; g2.beginPath(); g2.moveTo((rx0 + rx1) / 2, peak); g2.lineTo(rx1, topY + 4); g2.lineTo((rx0 + rx1) / 2, topY + 4); g2.fill();
  } });
  // gable plaster triangle with beams + attic window
  const gx0 = rx0 + 26, gx1 = rx1 - 26, gTop = peak + (rx1 - rx0) * .75 * .3;
  K.shape(g, [[gx0, topY + 2], [(gx0 + gx1) / 2, gTop + 18], [gx1, topY + 2]], { fill: plaster, lw: lw * .8, smooth: false });
  K.line(g, [[(gx0 + gx1) / 2, gTop + 20], [(gx0 + gx1) / 2, topY]], 9, beam, 1, false);
  const aw = 26, ah = 30;
  window_(g, (gx0 + gx1) / 2 - aw / 2 - 26, topY - ah - 14, aw, ah, { lit: night && hash((o.seed || 1) * 9) < .4 ? 1 : 0, lw, beam, night, open: o.shutter ? clamp(o.shutter(99, floors, 0)) : 0 });
  // chimney
  if (r() < .7) { const cx = lerp(rx0, rx1, .7 + r() * .1), cy = lerp(peak, topY, .35); K.shape(g, [[cx, cy], [cx + 26, cy], [cx + 26, cy - 60], [cx, cy - 60]], { fill: '#8b5a45', lw, smooth: false }); }
  // door on the ground floor
  if (o.door !== false) door_(g, x + w * (o.doorX ?? (.25 + r() * .5)) - 26, y, 52, Math.min(fh * .85, 96), { open: o.doorOpen || 0, lw, night, beam });
  return { peak, topY, rx0, rx1 };
}
function window_(g, x, y, w, h, o) {
  const lw = o.lw;
  const pane = o.lit ? '#f5c46a' : o.night ? '#1e2338' : '#3a3530';
  K.shape(g, [[x, y], [x + w, y], [x + w, y + h], [x, y + h]], { fill: pane, lw, smooth: false, inner: (g2) => {
    if (o.lit) { const gr = g2.createRadialGradient(x + w / 2, y + h * .6, 2, x + w / 2, y + h / 2, w); gr.addColorStop(0, '#ffe7a8'); gr.addColorStop(1, '#d88a3a'); g2.fillStyle = gr; g2.fillRect(x, y, w, h); }
    g2.strokeStyle = o.lit ? 'rgba(90,50,20,.7)' : 'rgba(150,140,120,.35)'; g2.lineWidth = 2;
    for (let i = -h; i < w + h; i += 12) { g2.beginPath(); g2.moveTo(x + i, y); g2.lineTo(x + i + h, y + h); g2.stroke(); g2.beginPath(); g2.moveTo(x + i + h, y); g2.lineTo(x + i, y + h); g2.stroke(); }
  } });
  if (o.lit) { const m = g.getTransform(); const sc = Math.hypot(m.a, m.b); const fl = o.open > 0 && o.open < .999 ? 1 : 0; addLightRect(g, x, y, w, h, '#ffcf7a', .5 + .3 * fl); if (sc > .35) addLight(g, x + w / 2, y + h / 2, w * (1.9 + 1.5 * fl), '#f0a24a', (.32 + .35 * fl) * clamp((sc - .35) * 2)); }
  // shutters (open = swing outward, foreshortened)
  const op = o.open || 0;
  const sw = w / 2 * (1 - op * .82);
  const shc = o.beam ? K.shade(o.beam, .15) : '#6a4a30';
  K.shape(g, [[x - (w / 2 - sw) * 0 - (op > 0 ? (w / 2) * op * .9 : 0), y], [x + sw - (op > 0 ? (w / 2) * op * .9 : 0), y], [x + sw - (op > 0 ? (w / 2) * op * .9 : 0), y + h], [x - (op > 0 ? (w / 2) * op * .9 : 0), y + h]].map((p, i) => op > 0 ? [x - (i === 0 || i === 3 ? (w * .45) * op : (w * .45) * op - sw), p[1]] : p), { fill: shc, lw: lw * .8, smooth: false });
  K.shape(g, [[x + w - sw, y], [x + w, y], [x + w, y + h], [x + w - sw, y + h]].map((p, i) => op > 0 ? [x + w + (i === 1 || i === 2 ? (w * .45) * op : (w * .45) * op - sw), p[1]] : p), { fill: shc, lw: lw * .8, smooth: false });
  K.shape(g, [[x - 5, y + h], [x + w + 5, y + h], [x + w + 5, y + h + 7], [x - 5, y + h + 7]], { fill: o.beam || PAL.beam, lw: lw * .7, smooth: false });
}
function door_(g, x, y, w, h, o) {
  const lw = o.lw;
  const arch = (dx, dy) => { const P = [[x + dx, y], [x + dx, y - h + w / 2 + dy]]; for (let i = 0; i <= 8; i++) { const a = Math.PI + Math.PI * i / 8; P.push([x + w / 2 + Math.cos(a) * (w / 2 - dx), y - h + w / 2 + Math.sin(a) * (w / 2 - dx) + dy]); } P.push([x + w - dx, y]); return P; };
  const inside = o.open > 0 ? (o.night ? '#f0a75a' : '#2a1d16') : '#5e3d27';
  K.shape(g, arch(0, 0), { fill: inside, lw, smooth: false });
  if (o.open > 0 && o.night) addLight(g, x + w / 2, y - h / 2, h * 1.2, '#f0a24a', .5 * o.open);
  if (o.open < 1) {
    const dw = w * (1 - o.open * .85);
    g.save(); g.beginPath(); K.poly(g, arch(0, 0)); g.clip();
    K.shape(g, [[x, y], [x + dw, y], [x + dw, y - h - 10], [x, y - h - 10]], { fill: '#6b4428', lw, smooth: false, inner: (g2) => { g2.strokeStyle = 'rgba(40,20,10,.45)'; g2.lineWidth = 2; for (let i = 1; i < 4; i++) { g2.beginPath(); g2.moveTo(x + dw * i / 4, y); g2.lineTo(x + dw * i / 4, y - h); g2.stroke(); } } });
    g.restore();
    K.shape(g, arch(0, 0), { lw, smooth: false });
    K.ellipse(g, x + dw - 9, y - h * .45, 3.5, 3.5, { fill: '#2a1d16', lw: 0 });
  }
}

// row of houses along a street edge (screen-space, layer handles parallax)
function houseRow(g, x0, x1, y, o = {}) {
  const r = rng(o.seed || 5);
  let x = x0; let i = 0;
  const out = [];
  while (x < x1) {
    const w = (o.wMin || 150) + r() * ((o.wMax || 230) - (o.wMin || 150));
    const h = (o.hMin || 240) + r() * ((o.hMax || 380) - (o.hMin || 240));
    out.push(house(g, x, y, w, h, { ...o, seed: (o.seed || 5) * 31 + i, idx: i }));
    x += w + (o.gap ?? 26); i++;
  }
  return out;
}

// ---------------------------------------------------------------- cobblestones (studio rounded-rect cobbles, perspective)
// draws a ground plane from horizonY to bottom; camX shifts world laterally; vx: vanishing x
function cobbles(g, o) {
  const { x0 = -200, x1 = 1280, yTop, yBot = 2000, vx = 540, camX = 0, camZ = 0, mood } = o;
  const base = mood === 'night' ? '#6d7186' : mood === 'dusk' ? '#9a7c74' : PAL.cobble;
  const gap = mood === 'night' ? '#3b3f52' : mood === 'dusk' ? '#5a4248' : '#8f7756';
  g.fillStyle = gap; g.fillRect(x0, yTop, x1 - x0, yBot - yTop);
  const H0 = yTop;
  // depth rows: screen y = H0 + F / z
  const F = o.F || 420;
  let z = 18;
  const zStep = .55;
  const rows = [];
  for (let zz = 40; zz > .7; zz /= 1.12) rows.push(zz);
  for (const zz of rows) {
    const y = H0 + F / zz; const y2 = H0 + F / (zz / 1.12);
    if (y > yBot + 40) break;
    const rowH = y2 - y; if (rowH < 2) continue;
    const sw = 120 / zz * 9; // stone width in screen px
    const off = ((camX / zz) % sw + sw) % sw + (hash(Math.round(zz * 100)) * sw);
    const zz2 = zz + camZ;
    for (let x = x0 - sw - off; x < x1 + sw; x += sw) {
      const jx = (hash(Math.round(x / sw) * 13.1 + zz * 7) - .5) * sw * .12;
      const shadeK = hash(Math.round(x / sw) * 3.7 + zz * 11);
      const col = K.cmix(base, shadeK > .5 ? '#ffffff' : '#000000', Math.abs(shadeK - .5) * .16);
      g.fillStyle = col; g.strokeStyle = gap;
      const rr = Math.min(rowH * .4, sw * .25);
      g.beginPath(); g.roundRect(x + jx + sw * .06, y + rowH * .1, sw * .88, rowH * .8, rr); g.fill();
      g.lineWidth = Math.max(1, Math.min(3.5, rowH * .09)); g.strokeStyle = K.rgba(INK, .55); g.stroke();
    }
  }
}

// ---------------------------------------------------------------- props
function barrel(g, x, y, s = 1, o = {}) {
  g.save(); g.translate(x, y); g.scale(s, s);
  const lw = (o.lw ?? 4) / s;
  K.shape(g, [[-48, 0], [-55, -60], [-48, -120], [48, -120], [55, -60], [48, 0]], { fill: '#8a5a36', lw, tension: .5, inner: (g2) => {
    g2.strokeStyle = 'rgba(40,20,10,.35)'; g2.lineWidth = 2.5; for (let i = -40; i <= 40; i += 16) { g2.beginPath(); g2.moveTo(i, 0); g2.quadraticCurveTo(i * 1.15, -60, i, -120); g2.stroke(); } } });
  for (const yy of [-22, -98]) K.shape(g, [[-52, yy - 6], [52, yy - 6], [53, yy + 6], [-53, yy + 6]], { fill: '#5d5a5a', lw: lw * .8, smooth: false });
  const lid = o.lid || 0; // 0 closed, 1 off
  K.ellipse(g, 0, -120, 48, 12, { fill: lid > 0 ? '#1b120c' : '#9b6a42', lw });
  if (lid > 0) { g.save(); g.translate(-48 - lid * 40, -120 - lid * 70); g.rotate(-lid * 1.2); K.ellipse(g, 48, 0, 48, 12, { fill: '#9b6a42', lw }); g.restore(); }
  g.restore();
}
function sack(g, x, y, s = 1, o = {}) {
  g.save(); g.translate(x, y); g.scale(s, s); const lw = (o.lw ?? 4) / s;
  const torn = o.torn || 0;
  K.shape(g, [[-40, 0], [-46, -50], [-30, -86], [-12, -96], [-4, -110], [8, -112], [10, -96], [32, -84], [46, -48], [40, 0]], { fill: '#c9ae7c', lw, tension: .5 });
  K.line(g, [[-10, -98], [12, -98]], lw * 1.2, '#7a5a35', 1, false);
  if (torn) { K.shape(g, [[-18, -40], [6, -52], [22, -30], [2, -18], [-14, -26]], { fill: '#2a1d14', lw: lw * .8 }); for (let i = 0; i < 14 * torn; i++) K.ellipse(g, -30 + hash(i) * 70, 4 + hash(i + 9) * 6, 5, 3, { fill: '#e6c98a', lw: 1 }); }
  g.restore();
}
function crate(g, x, y, w, h, o = {}) { K.shape(g, [[x, y], [x + w, y], [x + w, y - h], [x, y - h]], { fill: '#9a6b40', lw: o.lw ?? 4, smooth: false, inner: g2 => { g2.strokeStyle = 'rgba(40,20,10,.4)'; g2.lineWidth = 3; g2.beginPath(); g2.moveTo(x, y); g2.lineTo(x + w, y - h); g2.moveTo(x, y - h / 2); g2.lineTo(x + w, y - h / 2); g2.stroke(); } }); }
function stall(g, x, y, w, o = {}) { // market stall with striped awning
  const lw = o.lw ?? 4, h = o.h || 210;
  const stripe = o.stripe || ['#b0402b', '#e8dcbf'];
  K.shape(g, [[x + 8, y], [x + 18, y], [x + 18, y - h], [x + 8, y - h]], { fill: '#5a3b26', lw, smooth: false });
  K.shape(g, [[x + w - 18, y], [x + w - 8, y], [x + w - 8, y - h], [x + w - 18, y - h]], { fill: '#5a3b26', lw, smooth: false });
  // table
  K.shape(g, [[x - 6, y - 82], [x + w + 6, y - 82], [x + w + 6, y - 64], [x - 6, y - 64]], { fill: '#8a5a36', lw, smooth: false });
  K.shape(g, [[x, y - 64], [x + w, y - 64], [x + w, y - 30], [x, y - 30]], { fill: '#6b4428', lw, smooth: false });
  // goods
  const r = rng(o.seed || 3);
  if (o.goods !== false) for (let i = 0; i < 6; i++) { const gx = x + 20 + (w - 40) * (i + .5) / 6; const kind = Math.floor(r() * 3); if (kind === 0) K.ellipse(g, gx, y - 92, 16, 10, { fill: '#d2a256', lw: lw * .8 }); else if (kind === 1) { K.ellipse(g, gx - 6, y - 90, 9, 9, { fill: '#b84a2c', lw: lw * .7 }); K.ellipse(g, gx + 7, y - 92, 9, 9, { fill: '#c06030', lw: lw * .7 }); } else K.shape(g, [[gx - 14, y - 82], [gx + 14, y - 82], [gx + 10, y - 106], [gx - 10, y - 106]], { fill: '#c9ae7c', lw: lw * .8, tension: .4 }); }
  // awning (scalloped stripes)
  const aw = w + 40, ax = x - 20, ay = y - h;
  const n = 7;
  for (let i = 0; i < n; i++) {
    const sx = ax + aw * i / n, ex = ax + aw * (i + 1) / n;
    K.shape(g, [[sx + (i === 0 ? 0 : 0), ay - 50], [ex, ay - 50], [ex, ay + 8], [(sx + ex) / 2, ay + 24], [sx, ay + 8]], { fill: stripe[i % 2], lw: lw * .8, smooth: false });
  }
  K.shape(g, [[ax - 6, ay - 64], [ax + aw + 6, ay - 64], [ax + aw, ay - 50], [ax, ay - 50]], { fill: '#5a3b26', lw, smooth: false });
}
function bread(g, x, y, s = 1, o = {}) { g.save(); g.translate(x, y); g.scale(s, s); K.ellipse(g, 0, 0, 34, 18, { fill: '#c98a44', lw: (o.lw ?? 4) / s }); for (let i = -1; i <= 1; i++) K.line(g, [[i * 14 - 6, -10], [i * 14 + 6, 6]], 2.5 / s, '#7a4a22', .7, false); g.restore(); }
function lamp(g, x, y, h, o = {}) { // lantern post / torch with flame
  const lw = o.lw ?? 4, t = o.t || 0;
  K.shape(g, [[x - 6, y], [x + 6, y], [x + 6, y - h], [x - 6, y - h]], { fill: '#2d221c', lw, smooth: false });
  K.shape(g, [[x - 22, y - h], [x + 22, y - h], [x + 18, y - h - 40], [x - 18, y - h - 40]], { fill: o.lit ? '#f3c66a' : '#3a3530', lw, smooth: false });
  K.shape(g, [[x - 26, y - h - 40], [x, y - h - 62], [x + 26, y - h - 40]], { fill: '#2d221c', lw, smooth: false });
  if (o.lit) { const fl = 1 + .08 * Math.sin(t * 17) + .05 * Math.sin(t * 29); addLight(g, x, y - h - 20, 260 * fl, '#f0a24a', .55); addLight(g, x, y - h - 20, 60, '#ffe3a0', .7); }
}
function torch(g, x, y, o = {}) {
  const t = o.t || 0, s = o.s || 1, lw = o.lw ?? 4;
  K.shape(g, [[x - 5 * s, y], [x + 5 * s, y], [x + 7 * s, y - 50 * s], [x - 7 * s, y - 50 * s]], { fill: '#4a3121', lw, smooth: false });
  const fl = (a) => [[x - 12 * s, y - 50 * s], [x - 8 * s + Math.sin(t * 13 + a) * 4, y - 78 * s], [x + Math.sin(t * 9 + a) * 6, y - 100 * s - Math.sin(t * 21) * 6], [x + 8 * s, y - 76 * s], [x + 12 * s, y - 50 * s]];
  K.shape(g, fl(0), { fill: '#f29b3a', lw: lw * .7, tension: .5 });
  K.shape(g, fl(1).map(p => [x + (p[0] - x) * .55, y - 50 * s + (p[1] - y + 50 * s) * .6]), { fill: '#ffe08a', lw: 0, tension: .5 });
  addLight(g, x, y - 70 * s, 300 * s * (1 + .06 * Math.sin(t * 15)), '#f08a3a', .6);
}
function bunting(g, x0, y0, x1, y1, sag, t = 0, o = {}) {
  const n = Math.max(4, Math.round(Math.abs(x1 - x0) / 46)); const cols = o.cols || ['#b0402b', '#e8dcbf', '#53719a', '#cf9f45'];
  const pts = [];
  for (let i = 0; i <= n; i++) { const u = i / n; pts.push([lerp(x0, x1, u), lerp(y0, y1, u) + sag * Math.sin(Math.PI * u) + Math.sin(t * 3 + u * 6) * 3]); }
  K.line(g, pts, 2.5, INK, 1);
  for (let i = 0; i < n; i++) { const a = pts[i], b = pts[i + 1]; const m = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 30 + Math.sin(t * 5 + i) * 4]; K.shape(g, [a, b, m], { fill: cols[i % cols.length], lw: 2.5, smooth: false }); }
}
function chest(g, x, y, s = 1, o = {}) { // chest of gold; o.lid: 0 closed .. 1 open
  g.save(); g.translate(x, y); g.scale(s, s); const lw = (o.lw ?? 4) / s;
  K.shape(g, [[-90, 0], [90, 0], [90, -80], [-90, -80]], { fill: '#7a4a28', lw, smooth: false });
  K.shape(g, [[-90, -40], [90, -40], [90, -30], [-90, -30]], { fill: '#c9a03c', lw: lw * .7, smooth: false });
  const lid = o.lid ?? 0;
  if (lid > .05) { // gold heap visible
    K.shape(g, [[-84, -80], [-60, -104], [-20, -112], [24, -110], [64, -100], [84, -80]], { fill: '#e2b34a', lw, tension: .5 });
    for (let i = 0; i < 12; i++) K.ellipse(g, -70 + hash(i) * 140, -86 - hash(i + 3) * 22, 10, 6, { fill: '#f0c95a', lw: lw * .6 });
    addLight(g, 0, -100, 160, '#f0c040', .3 * lid);
  }
  g.save(); g.translate(0, -80); g.scale(1, Math.cos(lid * 1.9)); // lid hinge at back
  K.shape(g, [[-94, 0], [94, 0], [94, -50], [60, -70], [-60, -70], [-94, -50]], { fill: '#8d5730', lw: lw / Math.max(.2, Math.abs(Math.cos(lid * 1.9))), tension: .3 });
  g.restore();
  K.shape(g, [[-10, -60], [10, -60], [10, -36], [-10, -36]], { fill: '#d6b04a', lw: lw * .7, smooth: false });
  g.restore();
}
function toyHorse(g, x, y, s = 1, o = {}) { // wooden horse on wheels
  g.save(); g.translate(x, y); g.rotate(o.rock || 0); g.scale(s, s); const lw = (o.lw ?? 4) / s;
  K.shape(g, [[-60, -40], [40, -40], [46, -70], [68, -96], [84, -90], [74, -60], [50, -30], [-60, -30]], { fill: '#b88550', lw, tension: .3 });
  K.shape(g, [[52, -86], [66, -112], [74, -100]], { fill: '#6b4428', lw: lw * .8, smooth: false });
  K.line(g, [[-60, -38], [-82, -60]], lw * 2.2, '#6b4428', 1, false);
  for (const lx of [-46, 30]) K.shape(g, [[lx - 8, -32], [lx + 8, -32], [lx + 8, -8], [lx - 8, -8]], { fill: '#a97848', lw, smooth: false });
  K.shape(g, [[-70, -10], [60, -10], [60, -2], [-70, -2]], { fill: '#6b4428', lw, smooth: false });
  for (const wx of [-52, 44]) K.ellipse(g, wx, 4, 14, 14, { fill: '#8a5a36', lw });
  K.ellipse(g, 70, -88, 3, 3, { fill: INK, lw: 0 });
  g.restore();
}
function spinTop(g, x, y, s = 1, o = {}) { g.save(); g.translate(x, y); g.rotate(o.tilt || 0); g.scale(s, s); const lw = (o.lw ?? 4) / s; K.shape(g, [[0, 0], [-30, -30], [-22, -46], [22, -46], [30, -30]], { fill: '#b0402b', lw, tension: .3 }); K.line(g, [[-26, -36], [26, -36]], lw * 1.2, '#e8dcbf', 1, false); K.line(g, [[0, -46], [0, -62]], lw * 1.5, '#6b4428', 1, false); g.restore(); }
function doll(g, x, y, s = 1, o = {}) { g.save(); g.translate(x, y); g.rotate(o.rot || 0); g.scale(s, s); const lw = (o.lw ?? 4) / s; for (const sd of [-1, 1]) { K.capsule(g, [sd * 10, -44], [sd * 30, -24], 5, 4, { fill: '#e8c8a0', lw: lw * .8 }); K.capsule(g, [sd * 7, -4], [sd * 9, 14], 5, 4.5, { fill: '#e8c8a0', lw: lw * .8 }); } K.shape(g, [[-26, 0], [26, 0], [14, -48], [-14, -48]], { fill: '#b0402b', lw, tension: .3 }); K.shape(g, [[-14, -48], [14, -48], [12, -30], [-12, -30]], { fill: '#e8dcbf', lw: lw * .8, smooth: false }); K.ellipse(g, 0, -64, 15, 16, { fill: '#e8c8a0', lw }); K.ellipse(g, -5, -66, 2.5, 2.5, { fill: INK, lw: 0 }); K.ellipse(g, 5, -66, 2.5, 2.5, { fill: INK, lw: 0 }); K.shape(g, [[-16, -70], [0, -84], [16, -70], [12, -62], [-12, -62]], { fill: '#8a5a2a', lw: lw * .8, tension: .5 }); g.restore(); }

// ---------------------------------------------------------------- city gate
function gate(g, cx, y, o = {}) {
  const lw = o.lw ?? 5, open = o.open || 0, night = o.mood === 'night';
  const stone = night ? '#7d8094' : o.mood === 'dusk' ? '#9c8584' : '#b9a684';
  const stoneD = K.shade(stone, -.25);
  // walls
  K.shape(g, [[cx - 1200, y], [cx - 230, y], [cx - 230, y - 420], [cx - 1200, y - 420]], { fill: stoneD, lw, smooth: false });
  K.shape(g, [[cx + 230, y], [cx + 1200, y], [cx + 1200, y - 420], [cx + 230, y - 420]], { fill: stoneD, lw, smooth: false });
  for (let x = cx - 1200; x < cx + 1200; x += 60) if (Math.abs(x - cx) > 250) K.shape(g, [[x, y - 420], [x + 34, y - 420], [x + 34, y - 460], [x, y - 460]], { fill: stoneD, lw, smooth: false });
  // tower
  K.shape(g, [[cx - 260, y], [cx + 260, y], [cx + 250, y - 760], [cx - 250, y - 760]], { fill: stone, lw, smooth: false, inner: (g2) => {
    g2.strokeStyle = 'rgba(40,30,20,.3)'; g2.lineWidth = 3;
    for (let yy = y; yy > y - 760; yy -= 42) { g2.beginPath(); g2.moveTo(cx - 270, yy); g2.lineTo(cx + 270, yy); g2.stroke(); const off = ((y - yy) / 42) % 2 ? 0 : 45; for (let xx = cx - 260 + off; xx < cx + 260; xx += 90) { g2.beginPath(); g2.moveTo(xx, yy); g2.lineTo(xx, yy - 42); g2.stroke(); } }
  } });
  K.shape(g, [[cx - 300, y - 750], [cx, y - 1010], [cx + 300, y - 750]], { fill: PAL.roof, lw, smooth: false });
  window_(g, cx - 22, y - 640, 44, 60, { lw, lit: night ? 1 : 0, night, beam: PAL.beam });
  // arch opening
  const aw = 300, ah = 480;
  const archP = () => { const P = [[cx - aw / 2, y], [cx - aw / 2, y - ah + aw / 2]]; for (let i = 0; i <= 12; i++) { const a = Math.PI + Math.PI * i / 12; P.push([cx + Math.cos(a) * aw / 2, y - ah + aw / 2 + Math.sin(a) * aw / 2]); } P.push([cx + aw / 2, y]); return P; };
  const beyond = o.beyond || (night ? '#35406a' : o.mood === 'dusk' ? '#e0a070' : '#efe0be');
  K.shape(g, archP(), { fill: beyond, lw, smooth: false, inner: o.inner });
  // doors swing inward (shrink toward the hinges)
  g.save(); g.beginPath(); K.poly(g, archP()); g.clip();
  const dw = aw / 2 * (1 - open * .88);
  for (const sd of [-1, 1]) {
    const x0 = sd < 0 ? cx - aw / 2 : cx + aw / 2 - dw;
    K.shape(g, [[x0, y], [x0 + dw, y], [x0 + dw, y - ah - 20], [x0, y - ah - 20]], { fill: '#6b4428', lw, smooth: false, inner: g2 => {
      g2.strokeStyle = 'rgba(30,15,5,.5)'; g2.lineWidth = 3; for (let i = 1; i < 5; i++) { g2.beginPath(); g2.moveTo(x0 + dw * i / 5, y); g2.lineTo(x0 + dw * i / 5, y - ah); g2.stroke(); }
      g2.fillStyle = '#2f2f33'; for (const yy of [y - 90, y - 300]) g2.fillRect(x0, yy, dw, 14);
    } });
  }
  g.restore();
  K.shape(g, archP(), { lw: lw * 1.3, smooth: false });
  // portcullis teeth above
  return { archTop: y - ah, aw };
}

// ---------------------------------------------------------------- river
function river(g, x0, x1, y0, y1, t, o = {}) {
  const mood = o.mood;
  const top = mood === 'night' ? '#2b3a5e' : mood === 'dusk' ? '#6a5a7a' : '#7d9aa2';
  const bot = mood === 'night' ? '#1b2440' : mood === 'dusk' ? '#4a3a58' : '#5a7880';
  const gr = g.createLinearGradient(0, y0, 0, y1); gr.addColorStop(0, top); gr.addColorStop(1, bot);
  g.fillStyle = gr; g.fillRect(x0, y0, x1 - x0, y1 - y0);
  // flowing highlight lines
  g.save(); g.lineCap = 'round';
  for (let i = 0; i < 40; i++) {
    const yy = y0 + (y1 - y0) * Math.pow(hash(i * 3.3), 1.3);
    const sp = 40 + hash(i) * 60; const L = 40 + hash(i * 7) * 120 * (yy - y0) / (y1 - y0) + 20;
    const xx = x0 + (((hash(i * 9) * (x1 - x0) + t * sp) % (x1 - x0)) + (x1 - x0)) % (x1 - x0);
    g.strokeStyle = mood === 'night' ? 'rgba(170,190,240,.35)' : 'rgba(235,240,225,.45)'; g.lineWidth = 2 + 3 * (yy - y0) / (y1 - y0);
    g.beginPath(); g.moveTo(xx, yy); g.lineTo(xx + L, yy); g.stroke();
  }
  g.restore();
  // bank line
  K.line(g, [[x0, y0], [x1, y0]], o.lw ?? 4, INK, .8, false);
}
function ripple(g, x, y, age, s = 1, o = {}) { // expanding ring
  if (age < 0 || age > (o.life || 1.6)) return;
  const u = age / (o.life || 1.6);
  const r = (20 + 180 * Math.sqrt(u)) * s;
  g.save(); g.globalAlpha = (1 - u) * (o.a ?? .8); g.strokeStyle = o.col || '#e9eee4'; g.lineWidth = (5 * (1 - u) + 1.5) * s;
  g.beginPath(); g.ellipse(x, y, r, r * .22, 0, 0, TAU); g.stroke();
  if (u < .5) { g.beginPath(); g.ellipse(x, y, r * .55, r * .55 * .22, 0, 0, TAU); g.stroke(); }
  g.restore();
}

// ---------------------------------------------------------------- mountain with passage
function mountain(g, cx, y, o = {}) {
  const lw = o.lw ?? 5, mood = o.mood || 'night';
  const col = mood === 'night' ? '#2e3654' : '#5a4a5a', colD = mood === 'night' ? '#222842' : '#3f3242';
  K.shape(g, [[cx - 1100, y], [cx - 700, y - 380], [cx - 420, y - 560], [cx - 150, y - 760], [cx + 80, y - 820], [cx + 360, y - 640], [cx + 640, y - 520], [cx + 1100, y - 260], [cx + 1300, y]], { fill: col, lw, tension: .35 });
  K.shape(g, [[cx + 80, y - 820], [cx + 360, y - 640], [cx + 640, y - 520], [cx + 1100, y - 260], [cx + 1300, y], [cx + 200, y], [cx + 120, y - 400]], { fill: colD, lw: 0, tension: .35, alpha: .7 });
  // the passage (a dark cleft); o.open 0..1
  const op = o.open ?? 1;
  const pw = 130 * op, ph = 260;
  if (op > .01) {
    K.shape(g, [[cx - pw, y], [cx - pw * .9, y - ph * .6], [cx - pw * .4, y - ph], [cx + pw * .35, y - ph * .95], [cx + pw * .9, y - ph * .55], [cx + pw, y]], { fill: '#06070d', lw, tension: .4 });
    if (o.glow) addLight(g, cx, y - ph * .4, 260, '#a8b8f0', .35 * o.glow);
  }
  // rocks
  for (let i = 0; i < 9; i++) { const rx = cx - 600 + hash(i * 5) * 1200, ry = y - hash(i * 2) * 30; if (Math.abs(rx - cx) < 180) continue; K.shape(g, [[rx - 50, ry], [rx - 30, ry - 40], [rx + 10, ry - 55], [rx + 50, ry - 20], [rx + 55, ry]], { fill: colD, lw: lw * .8, tension: .3 }); }
}

// ---------------------------------------------------------------- fog
let FOGTEX = null;
function fogTex() {
  if (FOGTEX) return FOGTEX;
  const { createCanvas } = require('@napi-rs/canvas');
  const w = 512, h = 256, cv = createCanvas(w, h), g = cv.getContext('2d');
  const img = g.createImageData(w, h);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    // tileable horizontally via circular sampling
    const a = x / w * TAU; const v = C.fbm(Math.cos(a) * 2.2 + 10, y / h * 3 + Math.sin(a) * 2.2, 5);
    const e = Math.sin(Math.PI * y / h);
    const al = clamp((v * .9 + .35)) * e;
    const i = (y * w + x) * 4; img.data[i] = 255; img.data[i + 1] = 255; img.data[i + 2] = 255; img.data[i + 3] = Math.round(al * 255);
  }
  g.putImageData(img, 0, 0);
  FOGTEX = cv; return cv;
}
function fog(g, y, h, t, o = {}) {
  const tex = fogTex();
  const col = o.col || '#c9d3ea', a = o.a ?? .35, speed = o.speed ?? 18, W2 = 1080 * 1.6;
  g.save(); g.globalAlpha *= a;
  // tint by drawing onto a temp layer
  const { createCanvas } = require('@napi-rs/canvas');
  fog._cache = fog._cache || new Map();          // one tinted texture per colour, built once (no per-frame canvases)
  let tint = fog._cache.get(col);
  if (!tint) { tint = createCanvas(tex.width, tex.height); const c2 = tint.getContext('2d'); c2.drawImage(tex, 0, 0); c2.globalCompositeOperation = 'source-in'; c2.fillStyle = col; c2.fillRect(0, 0, tex.width, tex.height); fog._cache.set(col, tint); }
  const off = ((t * speed + (o.off || 0)) % W2 + W2) % W2;
  for (let k = -1; k < 2; k++) g.drawImage(tint, -off + k * W2 - 200, y, W2, h);
  g.restore();
}

module.exports = { LIGHTS, addLight, addLightRect, occlude, occludePoly, sky, moon, sun, cloud, skyline, house, houseRow, window_, door_, cobbles, barrel, sack, crate, stall, bread, lamp, torch, bunting, chest, toyHorse, spinTop, doll, gate, river, ripple, mountain, fog, fogTex };
