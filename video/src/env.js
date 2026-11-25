// Environments: painted medieval street, three treatment rooms. Drawn in world units.
const C = require('./core');
const { rand, hash, lerp, mixh, clamp } = C;
const D = require('./draw');
const { INK, PAL, shape, tube, line, curve, ell, poly, glow, rays } = D;

// ------------------------------------------------------------------ street pieces
function sun(ctx, x, y, r, t) {
  const g = ctx.createRadialGradient(x, y, 0, x, y, r * 4);
  g.addColorStop(0, 'rgba(255,240,200,0.9)'); g.addColorStop(1, 'rgba(255,240,200,0)');
  ctx.fillStyle = g; ctx.fillRect(x - r * 4, y - r * 4, r * 8, r * 8);
  ctx.save(); ctx.translate(x, y); ctx.rotate(t * 0.15);
  for (let i = 0; i < 12; i++) { ctx.rotate(Math.PI / 6); shape(ctx, c => { c.moveTo(r * 1.15, -9); c.lineTo(r * 1.65, 0); c.lineTo(r * 1.15, 9); c.closePath(); }, '#f4c25a', { lw: 3.5, tex: false }); }
  ctx.restore();
  shape(ctx, ell(x, y, r, r), '#f7cf6a', { lw: 4, hi: { x: x - r * 0.3, y: y - r * 0.3, r: r, a: 0.5 } });
  ctx.save(); ctx.globalAlpha = 0.6; curve(ctx, [x - r * 0.4, y + r * 0.15], [x, y + r * 0.45], [x + r * 0.4, y + r * 0.15], 3.5); ctx.restore();
}
function cloud(ctx, x, y, s) {
  shape(ctx, c => { c.moveTo(x - 120 * s, y + 30 * s); c.bezierCurveTo(x - 150 * s, y - 20 * s, x - 80 * s, y - 50 * s, x - 50 * s, y - 25 * s); c.bezierCurveTo(x - 40 * s, y - 80 * s, x + 50 * s, y - 80 * s, x + 50 * s, y - 30 * s); c.bezierCurveTo(x + 100 * s, y - 50 * s, x + 150 * s, y, x + 120 * s, y + 30 * s); c.closePath(); }, '#fbf0d8', { lw: 3.5, tex: false, shade: { x0: x, y0: y - 60 * s, x1: x, y1: y + 30 * s, a: 0.18 } });
}
function tower(ctx, x, base, w, h, col, seed) {
  const r = rand(seed);
  shape(ctx, c => c.rect(x - w / 2, base - h, w, h), col, { lw: 2.5, texA: 0.12 });
  shape(ctx, poly([[x - w / 2 - 8, base - h], [x, base - h - w * 1.6], [x + w / 2 + 8, base - h]]), mixh(col, '#8a5a40', 0.3), { lw: 2.5, texA: 0.12 });
  for (let i = 0; i < 3; i++) shape(ctx, c => { const wy = base - h + 40 + i * 70; c.moveTo(x - 8, wy + 30); c.lineTo(x - 8, wy + 8); c.arc(x, wy + 8, 8, Math.PI, 0); c.lineTo(x + 8, wy + 30); c.closePath(); }, mixh(col, '#5a4030', 0.45), { lw: 2, tex: false });
  ctx.save(); ctx.globalAlpha = 0.3; for (let i = 0; i < 8; i++) line(ctx, [[x - w / 2, base - h * r()], [x - w / 2 + 14, base - h * r()]], 2); ctx.restore();
}
function skyline(ctx, x0, x1, base, seed) {
  const r = rand(seed);
  const col = '#d6bf94';
  // rolling hills + city wall
  shape(ctx, c => { c.moveTo(x0, base); for (let x = x0; x <= x1; x += 40) c.lineTo(x, base - 120 - 40 * Math.sin(x * 0.004 + seed)); c.lineTo(x1, base + 400); c.lineTo(x0, base + 400); c.closePath(); }, '#cdb58a', { lw: 2.5, texA: 0.12 });
  for (let x = x0 + 100; x < x1; x += 260 + r() * 200) {
    const k = r();
    if (k < 0.18) { // cathedral
      tower(ctx, x, base - 40, 70, 420, col, seed + x); tower(ctx, x + 150, base - 40, 70, 420, col, seed + x + 1);
      shape(ctx, c => c.rect(x + 20, base - 340, 120, 300), col, { lw: 2.5, texA: 0.12 });
      shape(ctx, ell(x + 75, base - 280, 28, 28), mixh(col, '#a88060', 0.35), { lw: 2.5, tex: false });
    } else if (k < 0.5) tower(ctx, x, base - 40, 50 + r() * 30, 180 + r() * 200, col, seed + x);
    else { // roofs
      const w = 120 + r() * 80, h = 120 + r() * 80;
      shape(ctx, c => c.rect(x - w / 2, base - 40 - h, w, h + 40), mixh(col, '#efe0c0', 0.3), { lw: 2.5, texA: 0.1 });
      shape(ctx, poly([[x - w / 2 - 10, base - 40 - h], [x, base - 40 - h - w * 0.7], [x + w / 2 + 10, base - 40 - h]]), '#c08a64', { lw: 2.5, texA: 0.1 });
    }
  }
}

const WALLS = ['#eedfbd', '#e9cf9e', '#efd8c2', '#dfe0cc', '#ecd4a6'];
const ROOFS = ['#9a4a2e', '#8a5236', '#a2583a', '#7e4a35'];
// half-timbered house. x = left, base = ground y.
function house(ctx, x, base, w, floors, seed, o = {}) {
  const r = rand(seed);
  const fh = 230, wall = o.wall || WALLS[seed % WALLS.length], roof = o.roof || ROOFS[seed % ROOFS.length];
  const plinth = 70;
  // stone ground floor plinth
  shape(ctx, c => c.rect(x, base - plinth, w, plinth), '#b3a385', { lw: 4, texA: 0.25 });
  ctx.save(); ctx.globalAlpha = 0.45; for (let i = 0; i < w / 50; i++) { line(ctx, [[x + i * 50 + (i % 2) * 20, base - plinth], [x + i * 50 + (i % 2) * 20, base - plinth / 2]], 2.5); } line(ctx, [[x, base - plinth / 2], [x + w, base - plinth / 2]], 2.5); ctx.restore();
  let top = base - plinth;
  for (let f = 0; f < floors; f++) {
    const jut = f * 14, fx = x - jut, fw = w + 2 * jut, y0 = top - fh;
    shape(ctx, c => c.rect(fx, y0, fw, fh), wall, { lw: 5, shade: { x0: fx + fw, y0, x1: fx, y1: top, a: 0.18 }, texA: 0.25 });
    // timber frame
    const beamC = PAL.beam, bw = 16;
    const posts = Math.max(2, Math.round(fw / 110));
    for (let i = 0; i <= posts; i++) { const px = fx + i * (fw - bw) / posts; shape(ctx, c => c.rect(px, y0, bw, fh), beamC, { lw: 3, tex: false }); }
    shape(ctx, c => c.rect(fx - 6, top - 16, fw + 12, 16), beamC, { lw: 3, tex: false });
    shape(ctx, c => c.rect(fx - 6, y0, fw + 12, 14), beamC, { lw: 3, tex: false });
    for (let i = 0; i < posts; i++) {
      const px0 = fx + i * (fw - bw) / posts + bw, px1 = fx + (i + 1) * (fw - bw) / posts;
      const kind = (seed + i + f) % 3;
      if (kind === 0) { line(ctx, [[px0, top - 16], [px1, y0 + 14]], 11, beamC); }
      else if (kind === 1) { line(ctx, [[px0, y0 + 14], [px1, top - 16]], 11, beamC); }
      if (f === 0 && i === Math.floor(posts / 2) && o.door !== false) continue;
      // window
      const ww = Math.min(70, (px1 - px0) * 0.55), wh = 90, wx = (px0 + px1) / 2 - ww / 2, wy = y0 + 55;
      if (kind === 2 || r() < 0.7) {
        shape(ctx, c => c.rect(wx - 8, wy - 8, ww + 16, wh + 16), beamC, { lw: 3, tex: false });
        const lit = r() < (o.lit || 0.35);
        shape(ctx, c => { c.moveTo(wx, wy + wh); c.lineTo(wx, wy + 14); c.quadraticCurveTo(wx + ww / 2, wy - 12, wx + ww, wy + 14); c.lineTo(wx + ww, wy + wh); c.closePath(); }, lit ? '#f6c66a' : '#4a3a3a', { lw: 3.5, tex: false });
        line(ctx, [[wx + ww / 2, wy], [wx + ww / 2, wy + wh]], 3); line(ctx, [[wx, wy + wh / 2], [wx + ww, wy + wh / 2]], 3);
        if (r() < 0.45) { shape(ctx, c => c.rect(wx - 12, wy + wh + 6, ww + 24, 20), PAL.woodDark, { lw: 3, tex: false }); for (let k = 0; k < 4; k++) shape(ctx, ell(wx + k * ww / 3, wy + wh + 2, 11, 9), ['#c44a3a', '#e0a33a', '#d86c8a'][k % 3], { lw: 2.5, tex: false }); }
      }
    }
    top = y0;
  }
  // roof (steep gable facing street) with tiles
  const jut = (floors) * 14, rx = x - jut - 30, rw = w + 2 * jut + 60, rh = Math.min(380, rw * 0.75);
  shape(ctx, poly([[rx, top + 8], [rx + rw / 2, top - rh], [rx + rw, top + 8]]), roof, { lw: 5, shade: { x0: rx + rw, y0: top - rh, x1: rx, y1: top, a: 0.28 }, texA: 0.25 });
  ctx.save(); ctx.beginPath(); poly([[rx, top + 8], [rx + rw / 2, top - rh], [rx + rw, top + 8]])(ctx); ctx.clip(); ctx.globalAlpha = 0.35;
  for (let yy = top; yy > top - rh; yy -= 26) line(ctx, [[rx, yy], [rx + rw, yy]], 2.5);
  for (let yy = top; yy > top - rh; yy -= 26) for (let xx = rx + ((yy / 26) % 2) * 20; xx < rx + rw; xx += 40) line(ctx, [[xx, yy], [xx, yy - 26]], 2);
  ctx.restore();
  // gable window
  if (rw > 220) { const gx = rx + rw / 2, gy = top - rh * 0.4; shape(ctx, ell(gx, gy, 26, 30), '#4a3a3a', { lw: 3.5, tex: false }); line(ctx, [[gx - 26, gy], [gx + 26, gy]], 3); }
  if (r() < 0.6) { const cx = rx + rw * (0.25 + r() * 0.5); shape(ctx, c => c.rect(cx, top - rh * 0.9, 34, 120), '#a06a4a', { lw: 4 }); }
  // door
  if (o.door !== false) {
    const dw = o.doorW || 88, dh = 170, dx = x + w / 2 - dw / 2 + (o.doorOff || 0);
    shape(ctx, c => { c.moveTo(dx - 12, base); c.lineTo(dx - 12, base - dh); c.arc(dx + dw / 2, base - dh, dw / 2 + 12, Math.PI, 0); c.lineTo(dx + dw + 12, base); c.closePath(); }, '#9a8a70', { lw: 4 });
    if (!o.openDoor) {
      shape(ctx, c => { c.moveTo(dx, base); c.lineTo(dx, base - dh); c.arc(dx + dw / 2, base - dh, dw / 2, Math.PI, 0); c.lineTo(dx + dw, base); c.closePath(); }, PAL.wood, { lw: 4, shade: { x0: dx, y0: base - dh, x1: dx + dw, y1: base, a: 0.3 } });
      for (let k = 1; k < 4; k++) line(ctx, [[dx + k * dw / 4, base - dh - 20], [dx + k * dw / 4, base]], 2.5, PAL.woodDark);
      shape(ctx, ell(dx + dw * 0.78, base - dh * 0.45, 6, 6), '#d8b060', { lw: 2.5, tex: false });
    }
  }
}

// hanging guild sign on bracket
function sign(ctx, x, y, t, kind, swing = 0) {
  line(ctx, [[x - 10, y], [x + 140, y]], 9, PAL.beam);
  line(ctx, [[x, y + 40], [x + 60, y]], 6, PAL.beam);
  const a = Math.sin(t * 1.7) * 4 + swing;
  ctx.save(); ctx.translate(x + 100, y); ctx.rotate(a * C.D2R);
  line(ctx, [[-30, 0], [-30, 30]], 3); line(ctx, [[30, 0], [30, 30]], 3);
  shape(ctx, c => c.roundRect(-55, 30, 110, 90, 12), '#e6cf9f', { lw: 4.5, shade: { x0: 0, y0: 30, x1: 0, y1: 120, a: 0.2 } });
  if (kind === 'bowl') { shape(ctx, c => { c.moveTo(-32, 62); c.quadraticCurveTo(0, 112, 32, 62); c.closePath(); }, '#c0c4c8', { lw: 4, tex: false }); line(ctx, [[-20, 48], [16, 74]], 5, '#7a3a2a'); }
  if (kind === 'leech') { shape(ctx, c => c.roundRect(-24, 44, 48, 64, 10), '#9fc8b8', { lw: 4, tex: false }); tube(ctx, [[-10, 90], [0, 78], [10, 86], [6, 70]], 8, '#3a2a2a', 2.5); }
  if (kind === 'skull') { shape(ctx, ell(0, 70, 26, 24), '#f1e7d2', { lw: 4, tex: false }); shape(ctx, c => c.rect(-14, 86, 28, 16), '#f1e7d2', { lw: 3.5, tex: false }); ctx.fillStyle = INK; ctx.beginPath(); ctx.arc(-9, 70, 6, 0, 7); ctx.arc(9, 70, 6, 0, 7); ctx.fill(); }
  if (kind === 'ale') { shape(ctx, c => c.roundRect(-22, 50, 44, 56, 8), '#c98a3a', { lw: 4, tex: false }); shape(ctx, ell(0, 50, 24, 10), '#fff6e0', { lw: 3, tex: false }); }
  ctx.restore();
}

function barrel(ctx, x, base, s = 1) {
  shape(ctx, c => { c.moveTo(x - 50 * s, base); c.quadraticCurveTo(x - 64 * s, base - 70 * s, x - 50 * s, base - 140 * s); c.lineTo(x + 50 * s, base - 140 * s); c.quadraticCurveTo(x + 64 * s, base - 70 * s, x + 50 * s, base); c.closePath(); }, PAL.wood, { lw: 4.5, shade: { x0: x + 50 * s, y0: 0, x1: x - 50 * s, y1: 0, a: 0.35 } });
  for (const k of [0.2, 0.8]) line(ctx, [[x - 58 * s, base - 140 * s * k], [x + 58 * s, base - 140 * s * k]], 7 * s, '#5a5550');
  shape(ctx, ell(x, base - 140 * s, 50 * s, 12 * s), PAL.woodLight, { lw: 4, tex: false });
}
function crate(ctx, x, base, s = 1) {
  shape(ctx, c => c.rect(x - 60 * s, base - 110 * s, 120 * s, 110 * s), PAL.woodLight, { lw: 4.5, shade: { x0: x + 60 * s, y0: 0, x1: x - 60 * s, y1: 0, a: 0.3 } });
  line(ctx, [[x - 60 * s, base - 110 * s], [x + 60 * s, base]], 7 * s, PAL.wood); line(ctx, [[x - 60 * s, base - 55 * s], [x + 60 * s, base - 55 * s]], 4 * s, PAL.woodDark);
}
function cartWheel(ctx, x, y, r) {
  shape(ctx, c => { c.arc(x, y, r, 0, Math.PI * 2); c.arc(x, y, r * 0.82, 0, Math.PI * 2, true); }, PAL.wood, { lw: 4, rule: 'evenodd' });
  for (let i = 0; i < 8; i++) line(ctx, [[x, y], [x + Math.cos(i * Math.PI / 4) * r * 0.82, y + Math.sin(i * Math.PI / 4) * r * 0.82]], 9, PAL.woodDark);
  shape(ctx, ell(x, y, r * 0.16, r * 0.16), PAL.woodDark, { lw: 4, tex: false });
}

// muddy cobbled street band
function ground(ctx, x0, x1, top, bottom, seed) {
  shape(ctx, c => c.rect(x0, top, x1 - x0, bottom - top), '#a98c66', { lw: 0, shade: { x0: 0, y0: top, x1: 0, y1: bottom, a: 0.25 }, texA: 0.3 });
  const r = rand(seed);
  // cobbles get bigger toward the viewer
  for (let y = top + 10, row = 0; y < bottom; row++) {
    const k = (y - top) / (bottom - top), ch = 14 + 46 * k, cw = 40 + 70 * k;
    for (let x = x0 - (row % 2) * cw / 2; x < x1; x += cw * (0.9 + r() * 0.25)) {
      if (r() < 0.22) continue;
      const col = mixh('#bba684', '#8f7a5c', r());
      shape(ctx, c => c.roundRect(x + 3, y + 2, cw * 0.86, ch * 0.8, ch * 0.35), col, { lw: 2 + 2 * k, tex: false, shade: { x0: 0, y0: y, x1: 0, y1: y + ch, a: 0.25 } });
    }
    y += ch;
  }
  // mud patches + puddles
  for (let i = 0; i < (x1 - x0) / 400; i++) {
    const px = x0 + r() * (x1 - x0), py = top + 60 + r() * (bottom - top - 120), k = (py - top) / (bottom - top);
    ctx.save(); ctx.globalAlpha = 0.55; shape(ctx, ell(px, py, 110 + 120 * k, 26 + 30 * k), '#7a5a3a', { lw: 0, texA: 0.4 }); ctx.restore();
    if (r() < 0.5) { shape(ctx, ell(px + 20, py, 70 + 80 * k, 14 + 18 * k), '#cfd8c8', { lw: 3, tex: false, shade: { x0: px, y0: py - 20, x1: px, y1: py + 20, a: 0.3, c: '60,80,90' } }); line(ctx, [[px - 10, py - 4], [px + 40, py - 4]], 3, 'rgba(255,255,255,0.7)'); }
  }
  // straw bits
  ctx.save(); ctx.globalAlpha = 0.7; for (let i = 0; i < (x1 - x0) / 25; i++) { const px = x0 + r() * (x1 - x0), py = top + r() * (bottom - top), a = r() * 3; line(ctx, [[px, py], [px + Math.cos(a) * 18, py + Math.sin(a) * 6]], 2.5, '#d8b860'); } ctx.restore();
}

// complete street layer set; x range wide for the chase
const HOUSES = [];
function streetBack(ctx, x0, x1, groundY, seed = 11, o = {}) {
  let x = x0, i = 0; const r = rand(seed); HOUSES.length = 0;
  while (x < x1) {
    const w = 330 + Math.floor(r() * 4) * 40, floors = 2 + (r() < 0.55 ? 1 : 0);
    const spec = (o.special || []).find(s => s.i === i) || {};
    house(ctx, x, groundY, w, floors, seed * 10 + i, spec); HOUSES.push({ i, x, w, floors });
    if (spec.sign) sign(ctx, x + w - 40, groundY - 330, 0, spec.sign);
    x += w + 10 + r() * 30; i++;
  }
}

// ------------------------------------------------------------------ interiors
function stoneWall(ctx, x0, y0, x1, y1, base, seed, bw = 140, bh = 70) {
  shape(ctx, c => c.rect(x0, y0, x1 - x0, y1 - y0), base, { lw: 0, texA: 0.3 });
  const r = rand(seed);
  for (let y = y0, row = 0; y < y1; y += bh, row++) {
    for (let x = x0 - (row % 2) * bw / 2; x < x1; x += bw) {
      const col = mixh(base, r() < 0.5 ? '#fff0d8' : '#3a2a22', r() * 0.18);
      shape(ctx, c => c.roundRect(x + 4, y + 4, bw - 8, bh - 8, 10), col, { lw: 3, tex: false, shade: { x0: 0, y0: y, x1: 0, y1: y + bh, a: 0.22 } });
    }
  }
}
function planks(ctx, x0, y0, x1, y1, seed, base = PAL.wood) {
  shape(ctx, c => c.rect(x0, y0, x1 - x0, y1 - y0), base, { lw: 0, shade: { x0: 0, y0, x1: 0, y1, a: 0.3 } });
  const r = rand(seed);
  for (let y = y0, row = 0; y < y1; row++) {
    const k = (y - y0) / (y1 - y0), h = 26 + 60 * k;
    line(ctx, [[x0, y], [x1, y]], 3);
    for (let x = x0 + r() * 300; x < x1; x += 300 + r() * 300) line(ctx, [[x, y], [x, y + h]], 2.5);
    y += h;
  }
}
function book(ctx, x, y, w, h, col) { shape(ctx, c => c.rect(x, y - h, w, h), col, { lw: 3.5, tex: false, shade: { x0: x, y0: 0, x1: x + w, y1: 0, a: 0.25 } }); line(ctx, [[x + 3, y - h * 0.8], [x + w - 3, y - h * 0.8]], 2.5, '#e8c870'); line(ctx, [[x + 3, y - h * 0.25], [x + w - 3, y - h * 0.25]], 2.5, '#e8c870'); }
function shelf(ctx, x, y, w, seed, kind = 'books') {
  const r = rand(seed);
  let bx = x + 10;
  while (bx < x + w - 30) {
    if (kind === 'books' || r() < 0.4) {
      const bw = 22 + r() * 18, bh = 70 + r() * 50; book(ctx, bx, y, bw, bh, ['#8a2f2a', '#2f5a6a', '#6a5a2a', '#4a3a5a', '#a0602a', '#2f5f3a'][Math.floor(r() * 6)]); bx += bw + 2;
    } else { jar(ctx, bx + 30, y, 26 + r() * 10, 50 + r() * 40, kind === 'leech' ? '#6fa894' : ['#9fbfb0', '#c8b070', '#b88060'][Math.floor(r() * 3)], kind === 'leech', seed + bx); bx += 70; }
  }
  shape(ctx, c => c.rect(x, y, w, 22), PAL.woodDark, { lw: 4, tex: false });
}
function jar(ctx, x, y, rw, h, col, leeches = false, seed = 1, t = 0) {
  shape(ctx, c => { c.moveTo(x - rw, y); c.lineTo(x - rw, y - h * 0.8); c.quadraticCurveTo(x - rw, y - h, x - rw * 0.6, y - h); c.lineTo(x + rw * 0.6, y - h); c.quadraticCurveTo(x + rw, y - h, x + rw, y - h * 0.8); c.lineTo(x + rw, y); c.closePath(); }, col, { lw: 3.5, tex: false, hi: { x: x - rw * 0.4, y: y - h * 0.6, r: rw, a: 0.5 } });
  if (leeches) { const r = rand(seed); for (let i = 0; i < 3; i++) { const lx = x - rw * 0.5 + r() * rw, ly = y - 10 - r() * h * 0.6; tube(ctx, [[lx - 8, ly], [lx, ly - 5 + Math.sin(t * 4 + i) * 3], [lx + 8, ly]], 5, '#2a2020', 1.5); } }
  shape(ctx, c => c.rect(x - rw * 0.7, y - h - 10, rw * 1.4, 12), '#a07050', { lw: 3, tex: false });
}
function candle(ctx, x, y, h, t, seed = 1) {
  shape(ctx, c => c.rect(x - 9, y - h, 18, h), '#f2e6c8', { lw: 3.5, tex: false });
  shape(ctx, c => { c.moveTo(x - 4, y - h); c.quadraticCurveTo(x - 16, y - h + 10, x - 14, y - h + 30); c.lineTo(x - 9, y - h + 8); c.closePath(); }, '#f2e6c8', { lw: 2.5, tex: false });
  const fl = 1 + 0.15 * Math.sin(t * 23 + seed) + 0.1 * Math.sin(t * 37 + seed * 2);
  shape(ctx, c => { c.moveTo(x, y - h - 34 * fl); c.quadraticCurveTo(x + 12, y - h - 10, x, y - h - 2); c.quadraticCurveTo(x - 12, y - h - 10, x, y - h - 34 * fl); }, '#ffcf5a', { lw: 3, tex: false });
  glow(ctx, x, y - h - 16, 150 * fl, '255,190,100', 0.35);
}

module.exports = { HOUSES, sun, cloud, skyline, house, sign, barrel, crate, cartWheel, ground, streetBack, stoneWall, planks, shelf, jar, candle, book, tower };
