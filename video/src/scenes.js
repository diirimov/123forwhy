// Scene painters: street, study (Doctor 1), leech shop (Doctor 2), surgery (Doctor 3) + props.
const C = require('./core');
const { W, H, clamp, lerp, rand, hash, mixh } = C;
const D = require('./draw');
const { INK, PAL, shape, tube, line, curve, ell, poly, glow, rays, motes } = D;
const E = require('./env');
const F = require('./film');

// ================================================================ STREET
const ST = { x0: -2600, x1: 7600 };
function skyFill(ctx, cam, t, warm = 0) {
  const g = ctx.createLinearGradient(0, 0, 0, H);
  g.addColorStop(0, mixh('#e9c98e', '#e0a868', warm)); g.addColorStop(0.55, mixh('#f6e3b6', '#f3c88e', warm)); g.addColorStop(1, '#f7e6c0');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  const sx = 760 - cam.x * 0.03, sy = 330 - (cam.y + 400) * 0.03;
  E.sun(ctx, sx, sy, 70, t);
  for (let i = 0; i < 4; i++) E.cloud(ctx, ((i * 420 + t * 12 - cam.x * 0.06) % 1700 + 1700) % 1700 - 300, 180 + i * 90 + (i % 2) * 60, 0.8 + 0.2 * (i % 3));
  // birds
  ctx.save(); ctx.globalAlpha = 0.7;
  for (let i = 0; i < 3; i++) { const bx = ((i * 260 + t * 60 - cam.x * 0.08) % 1400 + 1400) % 1400 - 150, by = 520 + i * 40 + Math.sin(t * 2 + i) * 10, fl = Math.sin(t * 12 + i) * 8; curve(ctx, [bx - 18, by - fl], [bx - 8, by - 4], [bx, by], 3.5); curve(ctx, [bx, by], [bx + 8, by - 4], [bx + 18, by - fl], 3.5); }
  ctx.restore();
}
function streetLayers() {
  const sky = F.layer('street_skyline', ST.x0, -1500, ST.x1 - ST.x0, 1600, 0.6, x => E.skyline(x, ST.x0, ST.x1, -150, 4));
  const houses = F.layer('street_houses', ST.x0, -1500, ST.x1 - ST.x0, 1700, 1.0, x => {
    shape(x, c => c.rect(ST.x0, -10, ST.x1 - ST.x0, 210), '#6e5640', { lw: 0 });
    E.streetBack(x, ST.x0, ST.x1, 0, 11, { special: [
      { i: 6, sign: 'bowl', lit: 0.6 }, { i: 9, sign: 'leech', wall: '#dfe0cc', lit: 0.8 }, { i: 12, sign: 'ale' }, { i: 15, sign: 'skull', wall: '#d8d0c0' },
    ] });
  });
  const ground = F.layer('street_ground', ST.x0, -30, ST.x1 - ST.x0, 1500, 1.0, x => E.ground(x, ST.x0, ST.x1, -20, 1500, 21));
  return { sky, houses, ground };
}
// draw the street; fg(ctx) draws characters in world space (p = 1)
function street(ctx, cam, t, o = {}) {
  skyFill(ctx, cam, t, o.warm || 0);
  const L = streetLayers();
  F.withCam(ctx, cam, 0.3, x => F.drawLayer(x, L.sky), [540, -500]);
  F.withCam(ctx, cam, 0.82, x => {
    F.drawLayer(x, L.houses);
    if (o.houses) o.houses(x);
    // hanging laundry line between houses
    ctx.save(); line(x, [[1500, -760], [1600, -730], [1900, -740]], 3);
    for (let i = 0; i < 4; i++) { const lx = 1540 + i * 85, ly = -748 + Math.sin(i) * 6, sw = Math.sin(t * 2 + i) * 6; shape(x, c => { c.moveTo(lx, ly); c.lineTo(lx + 50, ly); c.lineTo(lx + 52 + sw, ly + 70); c.lineTo(lx - 2 + sw, ly + 70); c.closePath(); }, ['#e8e0d0', '#c96a4a', '#7a9ab0', '#e0c070'][i], { lw: 3.5 }); }
    ctx.restore();
  }, [540, -400]);
  F.withCam(ctx, cam, 1, x => {
    F.drawLayer(x, L.ground);
    if (o.props !== false) {
      E.barrel(x, -300, 60, 0.9); E.crate(x, -150, 70, 0.8); E.barrel(x, 1180, 40, 0.8); E.cartWheel(x, 2400, -40, 90); E.crate(x, 2300, 60, 1);
      E.barrel(x, 3600, 50, 0.9); E.crate(x, 5200, 60, 0.9); E.barrel(x, 5340, 50, 0.8);
    }
    if (o.fg) o.fg(x);
  });
  if (o.front) F.withCam(ctx, cam, 1.25, o.front, [cam.x, cam.y]);
}

// ================================================================ STUDY (Doctor 1)
function studyLayer() {
  return F.layer('study', -1400, -1700, 3200, 2700, 1.0, x => {
    E.stoneWall(x, -1400, -1700, 1800, 0, '#a8957a', 31, 150, 74);
    // timber posts + ceiling beam
    for (const px of [-1000, 520, 1500]) shape(x, c => c.rect(px, -1700, 60, 1700), PAL.beam, { lw: 5, shade: { x0: px, y0: 0, x1: px + 60, y1: 0, a: 0.35 } });
    shape(x, c => c.rect(-1400, -1480, 3200, 70), PAL.beam, { lw: 5 });
    // arched window with mullions
    const wx = -560, wy = -1150, ww = 420, wh = 620;
    shape(x, c => { c.moveTo(wx - 30, wy + wh + 30); c.lineTo(wx - 30, wy + 120); c.arc(wx + ww / 2, wy + 120, ww / 2 + 30, Math.PI, 0); c.lineTo(wx + ww + 30, wy + wh + 30); c.closePath(); }, '#8f8068', { lw: 5 });
    const wg = x.createLinearGradient(0, wy, 0, wy + wh); wg.addColorStop(0, '#fff2c8'); wg.addColorStop(1, '#f4cf88');
    shape(x, c => { c.moveTo(wx, wy + wh); c.lineTo(wx, wy + 120); c.arc(wx + ww / 2, wy + 120, ww / 2, Math.PI, 0); c.lineTo(wx + ww, wy + wh); c.closePath(); }, wg, { lw: 5, tex: false });
    for (let i = 1; i < 3; i++) line(x, [[wx + i * ww / 3, wy - 60], [wx + i * ww / 3, wy + wh]], 9, PAL.beam);
    for (let j = 1; j < 4; j++) line(x, [[wx, wy + 60 + j * (wh - 60) / 4], [wx + ww, wy + 60 + j * (wh - 60) / 4]], 6, PAL.beam);
    shape(x, c => c.rect(wx - 50, wy + wh + 20, ww + 100, 36), '#8f8068', { lw: 5 });
    // shelves with books & jars
    for (let i = 0; i < 3; i++) E.shelf(x, 640, -1250 + i * 230, 760, 40 + i, i === 1 ? 'jars' : 'books');
    // astrological "zodiac man" chart
    const zx = -90, zy = -1050;
    shape(x, c => c.rect(zx, zy, 360, 500), '#ead2a0', { lw: 5, shade: { x0: zx, y0: zy, x1: zx + 360, y1: zy + 500, a: 0.25 } });
    line(x, [[zx - 10, zy], [zx + 370, zy]], 12, PAL.woodDark); line(x, [[zx - 10, zy + 500], [zx + 370, zy + 500]], 12, PAL.woodDark);
    x.save(); x.translate(zx + 180, zy + 270); x.scale(0.55, 0.55);
    shape(x, ell(0, -280, 50, 60), '#f0d8b0', { lw: 4, tex: false }); tube(x, [[0, -220], [0, -20]], 70, '#f0d8b0', 4); tube(x, [[0, -180], [-120, -60]], 26, '#f0d8b0', 4); tube(x, [[0, -180], [120, -60]], 26, '#f0d8b0', 4); tube(x, [[-20, -20], [-50, 200]], 30, '#f0d8b0', 4); tube(x, [[20, -20], [50, 200]], 30, '#f0d8b0', 4);
    const sym = ['♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏'];
    x.font = '40px "IM Fell SC"'; x.fillStyle = '#8a2a20'; x.textAlign = 'center';
    sym.forEach((s, i) => { const a = -Math.PI / 2 + i * Math.PI * 2 / 8; x.fillText(s, Math.cos(a) * 220, -60 + Math.sin(a) * 260); line(x, [[Math.cos(a) * 180, -60 + Math.sin(a) * 210], [Math.cos(a) * 60, -60 + Math.sin(a) * 80]], 2, '#8a2a20'); });
    x.restore();
    x.font = '34px "Unifraktur"'; x.fillStyle = '#5a2a18'; x.textAlign = 'center'; x.fillText('Homo Signorum', zx + 180, zy + 50);
    // floor
    E.planks(x, -1400, 0, 1800, 1000, 7, '#7d5233');
    shape(x, c => c.rect(-1400, -40, 3200, 40), PAL.woodDark, { lw: 4, tex: false });
    // rug
    shape(x, ell(150, 330, 620, 150), '#8a2f2a', { lw: 5, shade: { x0: 0, y0: 200, x1: 0, y1: 480, a: 0.3 } });
    x.save(); x.setLineDash([16, 12]); shape(x, ell(150, 330, 540, 115), null, { lw: 4, ink: '#d8a050' }); x.restore();
  });
}
function desk(ctx, x, base, t) {
  shape(ctx, c => c.rect(x - 260, base - 300, 520, 40), PAL.wood, { lw: 5, shade: { x0: 0, y0: base - 300, x1: 0, y1: base - 260, a: 0.3 } });
  for (const lx of [-230, 200]) shape(ctx, c => c.rect(x + lx, base - 262, 34, 262), PAL.woodDark, { lw: 5 });
  shape(ctx, c => c.rect(x - 230, base - 262, 464, 90), PAL.wood, { lw: 5 });
  E.book(ctx, x - 200, base - 300, 140, 30, '#6a2a24'); E.book(ctx, x - 190, base - 330, 120, 30, '#2f4a5a');
  // hourglass + quill + inkwell
  shape(ctx, c => { c.moveTo(x + 60, base - 300); c.lineTo(x + 120, base - 300); c.lineTo(x + 92, base - 345); c.lineTo(x + 120, base - 390); c.lineTo(x + 60, base - 390); c.lineTo(x + 88, base - 345); c.closePath(); }, '#e8f0f0', { lw: 4, tex: false });
  shape(ctx, c => { c.moveTo(x + 92, base - 300); c.lineTo(x + 70, base - 300); c.lineTo(x + 90, base - 330); c.closePath(); }, '#e0b860', { lw: 0, tex: false });
  shape(ctx, ell(x + 180, base - 318, 22, 20), '#2a2a3a', { lw: 4, tex: false });
  tube(ctx, [[x + 175, base - 330], [x + 215, base - 430]], 6, '#f4efe0', 3);
  E.candle(ctx, x - 20, base - 300, 80, t, 1); E.candle(ctx, x + 10, base - 300, 50, t, 2);
}
function chair(ctx, x, base) {
  shape(ctx, c => c.rect(x - 90, base - 420, 26, 420), PAL.woodDark, { lw: 5 });
  shape(ctx, c => c.rect(x - 100, base - 200, 200, 36), PAL.wood, { lw: 5 });
  for (const lx of [-90, 70]) shape(ctx, c => c.rect(x + lx, base - 170, 22, 170), PAL.woodDark, { lw: 4 });
  shape(ctx, c => c.roundRect(x - 104, base - 430, 50, 250, 14), '#8a2f2a', { lw: 5 });
}
function study(ctx, cam, t, o = {}) {
  ctx.fillStyle = '#3a2a22'; ctx.fillRect(0, 0, W, H);
  const L = studyLayer();
  F.withCam(ctx, cam, 0.9, x => {
    F.drawLayer(x, L);
    rays(x, -380, -1000, Math.PI * 0.32, 0.5, 1700, 7, 0.09 + 0.02 * Math.sin(t * 0.7), 5);
    motes(x, t, -500, -900, 900, 1000, 40, 7, 0.5);
    E.candle(x, 820, -1020, 60, t, 4);
  }, [200, -500]);
  F.withCam(ctx, cam, 1, x => {
    if (o.desk !== false) desk(x, 760, 120, t);
    if (o.chair) chair(x, o.chair, 140);
    if (o.fg) o.fg(x);
  });
  if (o.front) F.withCam(ctx, cam, 1.3, o.front, [cam.x, cam.y]);
  // warm candle grade
  ctx.save(); ctx.globalCompositeOperation = 'soft-light'; ctx.fillStyle = 'rgba(255,170,80,0.25)'; ctx.fillRect(0, 0, W, H); ctx.restore();
}

// ================================================================ LEECH SHOP (Doctor 2)
function shopLayer() {
  return F.layer('shop', -1400, -1700, 3200, 2700, 1.0, x => {
    const wg = x.createLinearGradient(0, -1700, 0, 0); wg.addColorStop(0, '#5f7466'); wg.addColorStop(1, '#8a9a7c');
    shape(x, c => c.rect(-1400, -1700, 3200, 1700), wg, { lw: 0, texA: 0.35 });
    // wood panelling lower wall
    shape(x, c => c.rect(-1400, -520, 3200, 520), '#6a4a2e', { lw: 5, texA: 0.3 });
    for (let px = -1400; px < 1800; px += 160) line(x, [[px, -520], [px, 0]], 4, PAL.woodDark);
    // shelves of leech jars (green glow)
    for (let r = 0; r < 4; r++) for (let s = 0; s < 2; s++) {
      const sx = s ? 400 : -720, sy = -1180 + r * 180;
      shape(x, c => c.rect(sx, sy, 640, 20), PAL.woodDark, { lw: 4, tex: false });
      for (let j = 0; j < 6; j++) E.jar(x, sx + 55 + j * 105, sy, 34, 90 + (j * 37 % 40), ['#7fb5a0', '#8fc0a8', '#a6c99a', '#6fa894'][(j + r) % 4], true, r * 10 + j + s * 100);
    }
    // hanging herbs
    for (let i = 0; i < 9; i++) { const hx = -700 + i * 170; line(x, [[hx, -1700], [hx, -1520 - (i % 3) * 30]], 3); for (let k = 0; k < 5; k++) tube(x, [[hx, -1520 - (i % 3) * 30], [hx - 30 + k * 15, -1420 - (i % 3) * 30]], 7, ['#6d7438', '#8a8a3a', '#5a6a3a'][k % 3], 2.5); }
    // painted sign "LEECHES"
    shape(x, c => c.roundRect(-330, -1500, 660, 190, 20), '#2f5f5a', { lw: 6 });
    x.font = '110px "Unifraktur"'; x.fillStyle = '#f0d890'; x.textAlign = 'center'; x.textBaseline = 'middle'; x.fillText('Leeches', 0, -1400);
    tube(x, [[-280, -1380], [-260, -1405], [-235, -1385], [-215, -1405]], 12, '#2a2020', 3); tube(x, [[215, -1405], [235, -1385], [260, -1405], [280, -1380]], 12, '#2a2020', 3);
    E.planks(x, -1400, 0, 1800, 1000, 9, '#6f5a3a');
  });
}
function counter(ctx, x, base, w = 760) {
  shape(ctx, c => c.rect(x - w / 2, base - 330, w, 330), '#7a4e2c', { lw: 6, shade: { x0: 0, y0: base - 330, x1: 0, y1: base, a: 0.35 } });
  for (let i = 0; i < 4; i++) { shape(ctx, c => c.rect(x - w / 2 + 30 + i * (w - 60) / 4, base - 290, (w - 60) / 4 - 16, 120), '#8a5a34', { lw: 4 }); shape(ctx, ell(x - w / 2 + 30 + (i + 0.5) * (w - 60) / 4 - 8, base - 230, 9, 9), '#d8b060', { lw: 3, tex: false }); }
  shape(ctx, c => c.rect(x - w / 2 - 20, base - 350, w + 40, 30), '#5c3a21', { lw: 6 });
}
function shop(ctx, cam, t, o = {}) {
  ctx.fillStyle = '#2a3430'; ctx.fillRect(0, 0, W, H);
  const L = shopLayer();
  F.withCam(ctx, cam, 0.9, x => {
    F.drawLayer(x, L);
    for (let i = 0; i < 6; i++) glow(x, -560 + (i % 3) * 220 + (i > 2 ? 1120 : 0), -1000 + (i % 2) * 280, 260, '140,230,180', 0.12 + 0.04 * Math.sin(t * 2 + i));
    motes(x, t, -800, -1200, 1600, 1100, 30, 9, 0.35);
  }, [200, -500]);
  F.withCam(ctx, cam, 1, x => { if (o.back) o.back(x); if (o.counter !== false) counter(x, o.counterX || 300, 150); if (o.fg) o.fg(x); });
  if (o.front) F.withCam(ctx, cam, 1.3, o.front, [cam.x, cam.y]);
  ctx.save(); ctx.globalCompositeOperation = 'soft-light'; ctx.fillStyle = 'rgba(90,200,160,0.18)'; ctx.fillRect(0, 0, W, H); ctx.restore();
}

// ================================================================ SURGERY (Doctor 3)
function surgeryLayer() {
  return F.layer('surgery', -1400, -1700, 3200, 2700, 1.0, x => {
    E.stoneWall(x, -1400, -1700, 1800, 0, '#6e6a68', 51, 160, 80);
    // vaulted arches
    for (const ax of [-700, 500]) { shape(x, c => { c.moveTo(ax - 420, 0); c.lineTo(ax - 420, -900); c.arc(ax, -900, 420, Math.PI, 0); c.lineTo(ax + 420, 0); c.lineTo(ax + 340, 0); c.lineTo(ax + 340, -900); c.arc(ax, -900, 340, 0, Math.PI, true); c.lineTo(ax - 340, 0); c.closePath(); }, '#5a5654', { lw: 5, texA: 0.3 }); }
    // tool rack silhouettes (PG: saws, pliers, augers as shapes)
    shape(x, c => c.rect(-250, -1100, 520, 26), PAL.woodDark, { lw: 4 });
    const tools = [[-210, 'saw'], [-120, 'pliers'], [-30, 'auger'], [60, 'pliers'], [150, 'saw'], [230, 'auger']];
    for (const [tx, k] of tools) {
      line(x, [[tx, -1074], [tx, -1040]], 3);
      if (k === 'saw') { shape(x, c => { c.moveTo(tx - 14, -1040); c.lineTo(tx + 14, -1040); c.lineTo(tx + 10, -880); c.lineTo(tx - 10, -890); c.closePath(); }, '#a8aab0', { lw: 3.5, tex: false }); shape(x, c => c.rect(tx - 16, -1060, 32, 26), PAL.wood, { lw: 3, tex: false }); }
      if (k === 'pliers') { tube(x, [[tx, -1040], [tx - 12, -930]], 8, '#8a8c92', 3); tube(x, [[tx, -1040], [tx + 12, -930]], 8, '#8a8c92', 3); }
      if (k === 'auger') { tube(x, [[tx - 24, -1040], [tx + 24, -1040]], 10, PAL.wood, 3); tube(x, [[tx, -1040], [tx, -900]], 7, '#8a8c92', 3); }
    }
    // high barred window with cold moonlight
    shape(x, c => c.rect(-1100, -1450, 260, 200), '#9fb4c8', { lw: 6, tex: false });
    for (let i = 1; i < 4; i++) line(x, [[-1100 + i * 65, -1450], [-1100 + i * 65, -1250]], 8, '#3a3a40');
    E.planks(x, -1400, 0, 1800, 1000, 13, '#5a4a3e');
  });
}
function opTable(ctx, x, base) {
  shape(ctx, c => c.rect(x - 330, base - 260, 660, 44), PAL.wood, { lw: 6, shade: { x0: 0, y0: base - 260, x1: 0, y1: base - 216, a: 0.3 } });
  for (const lx of [-300, 270]) shape(ctx, c => c.rect(x + lx, base - 218, 34, 218), PAL.woodDark, { lw: 5 });
  shape(ctx, c => c.roundRect(x - 320, base - 290, 170, 36, 14), '#e8e0d0', { lw: 4 });
}
function surgery(ctx, cam, t, o = {}) {
  ctx.fillStyle = '#1c1a1e'; ctx.fillRect(0, 0, W, H);
  const L = surgeryLayer();
  F.withCam(ctx, cam, 0.9, x => {
    F.drawLayer(x, L);
    rays(x, -970, -1350, Math.PI * 0.42, 0.35, 1600, 5, 0.06, 8);
    E.candle(x, -560, -620, 70, t, 9); E.candle(x, 760, -560, 90, t, 10);
  }, [200, -500]);
  F.withCam(ctx, cam, 1, x => { if (o.table !== false) opTable(x, o.tableX || 200, 150); if (o.fg) o.fg(x); });
  if (o.front) F.withCam(ctx, cam, 1.3, o.front, [cam.x, cam.y]);
  // cold shadows, warm candle pools
  ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.fillStyle = 'rgba(120,130,170,0.35)'; ctx.fillRect(0, 0, W, H);
  ctx.globalCompositeOperation = 'soft-light'; const g = ctx.createRadialGradient(W * 0.5, H * 0.55, 50, W * 0.5, H * 0.55, H * 0.6); g.addColorStop(0, 'rgba(255,180,90,0.5)'); g.addColorStop(1, 'rgba(255,180,90,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); ctx.restore();
}

module.exports = { street, study, shop, surgery, desk, chair, counter, opTable, skyFill, streetLayers, ST };
