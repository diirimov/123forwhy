// V2 environments + cinematic helpers: depth of field, cast shadows, foreground props, light.
const C = require('./core');
const { W, H, clamp, lerp, rand, hash, mixh } = C;
const D = require('./draw');
const { INK, PAL, shape, tube, line, curve, ell, poly, glow, rays, motes, sparkle } = D;
const E = require('./env');
const F = require('./film');
const S = require('./scenes');
const PR = require('./props');

// ---------------------------------------------------------------- cinematic helpers
const OFF = [C.canvas(), C.canvas(), C.canvas()];
// draw fn (screen-space) into an offscreen buffer and composite it blurred: depth of field
function dof(ctx, blur, fn, slot = 0) {
  if (blur < 0.3) { fn(ctx); return; }
  const o = OFF[slot], x = o.getContext('2d');
  x.setTransform(1, 0, 0, 1, 0, 0); x.globalAlpha = 1; x.globalCompositeOperation = 'source-over'; x.filter = 'none'; x.clearRect(0, 0, W, H);
  fn(x);
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.filter = `blur(${blur.toFixed(1)}px)`; ctx.drawImage(o, 0, 0); ctx.filter = 'none'; ctx.restore();
}
// soft cast shadow of whatever fn draws, using the CURRENT world transform plus a skew (wall/floor projection)
function castShadow(ctx, fn, o = {}) {
  const off = OFF[2], x = off.getContext('2d');
  x.setTransform(1, 0, 0, 1, 0, 0); x.globalAlpha = 1; x.globalCompositeOperation = 'source-over'; x.filter = 'none'; x.clearRect(0, 0, W, H);
  const m = ctx.getTransform(); x.setTransform(m);
  const ax = o.ax || 0, ay = o.ay || 0;     // anchor (feet line) in world units
  x.translate(ax + (o.dx || 0), ay + (o.dy || 0)); x.transform(o.sx || 1, 0, o.skew || 0, o.sy || 1, 0, 0); x.translate(-ax, -ay);
  fn(x);
  x.setTransform(1, 0, 0, 1, 0, 0); x.globalCompositeOperation = 'source-in'; x.fillStyle = o.color || 'rgb(30,15,10)'; x.fillRect(0, 0, W, H);
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = o.alpha || 0.3; ctx.filter = `blur(${o.blur || 8}px)`; ctx.drawImage(off, 0, 0); ctx.restore();
}
// light pool (multiply darkness everywhere except a soft circle) -> chiaroscuro
function lightPool(ctx, x, y, r, dark = 0.55, color = '20,10,8') {
  const g = ctx.createRadialGradient(x, y, r * 0.15, x, y, r);
  g.addColorStop(0, `rgba(${color},0)`); g.addColorStop(1, `rgba(${color},${dark})`);
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); ctx.restore();
}
function warmWash(ctx, c = 'rgba(255,170,80,0.22)', op = 'soft-light') { ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalCompositeOperation = op; ctx.fillStyle = c; ctx.fillRect(0, 0, W, H); ctx.restore(); }

// ---------------------------------------------------------------- props (v2)
function lantern(ctx, x, y, t, s = 1) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  line(ctx, [[0, -400], [0, -60]], 4);
  shape(ctx, c => { c.moveTo(-40, -60); c.lineTo(40, -60); c.lineTo(52, 60); c.lineTo(-52, 60); c.closePath(); }, '#ffd88a', { lw: 5, tex: false });
  for (const sx of [-1, 0, 1]) line(ctx, [[sx * 30, -60], [sx * 40, 60]], 4, '#3a2a1a');
  shape(ctx, c => { c.moveTo(-58, -60); c.lineTo(0, -110); c.lineTo(58, -60); c.closePath(); }, '#4a3a2a', { lw: 5, tex: false });
  shape(ctx, c => c.rect(-58, 56, 116, 18), '#4a3a2a', { lw: 4, tex: false });
  const fl = 1 + 0.08 * Math.sin(t * 19) + 0.05 * Math.sin(t * 31);
  shape(ctx, c => { c.moveTo(0, -30 * fl); c.quadraticCurveTo(14, 10, 0, 22); c.quadraticCurveTo(-14, 10, 0, -30 * fl); }, '#fff0b0', { lw: 0, tex: false });
  ctx.restore();
  glow(ctx, x, y + 10 * s, 420 * s, '255,190,110', 0.4);
}
function pillow(ctx, x, y, s = 1) { shape(ctx, c => { c.moveTo(x - 120 * s, y); c.quadraticCurveTo(x - 140 * s, y - 70 * s, x - 90 * s, y - 80 * s); c.quadraticCurveTo(x, y - 95 * s, x + 90 * s, y - 80 * s); c.quadraticCurveTo(x + 140 * s, y - 70 * s, x + 120 * s, y); c.quadraticCurveTo(x, y + 14 * s, x - 120 * s, y); }, '#efe6d2', { lw: 5, shade: { x0: x, y0: y - 90 * s, x1: x, y1: y, a: 0.25 } }); }
function examTable(ctx, x, base, w = 820) {
  shape(ctx, c => c.rect(x - w / 2, base - 300, w, 56), PAL.wood, { lw: 6, shade: { x0: 0, y0: base - 300, x1: 0, y1: base - 244, a: 0.3 }, hi: { x: x - w * 0.2, y: base - 296, r: 200, a: 0.2 } });
  for (const lx of [-w / 2 + 30, w / 2 - 70]) shape(ctx, c => c.rect(x + lx, base - 246, 40, 246), PAL.woodDark, { lw: 5 });
  shape(ctx, c => c.rect(x - w / 2 + 60, base - 120, w - 120, 22), PAL.woodDark, { lw: 4 });
  // straps hanging off the side (ominous)
  for (const sx of [-0.2, 0.25]) { tube(ctx, [[x + sx * w, base - 250], [x + sx * w + 8, base - 160]], 16, '#5a3520', 3.5); shape(ctx, c => c.rect(x + sx * w - 6, base - 170, 28, 20), '#c9a050', { lw: 3, tex: false }); }
}
function flask(ctx, liquid = '#e8c050', t = 0, slosh = 0) {   // uroscopy flask (matula)
  shape(ctx, c => { c.moveTo(-14, -120); c.lineTo(-14, -70); c.bezierCurveTo(-70, -50, -70, 40, 0, 44); c.bezierCurveTo(70, 40, 70, -50, 14, -70); c.lineTo(14, -120); c.closePath(); }, 'rgba(225,245,240,0.55)', { lw: 5, tex: false });
  ctx.save(); ctx.beginPath(); ctx.moveTo(-14, -120); ctx.lineTo(-14, -70); ctx.bezierCurveTo(-70, -50, -70, 40, 0, 44); ctx.bezierCurveTo(70, 40, 70, -50, 14, -70); ctx.lineTo(14, -120); ctx.closePath(); ctx.clip();
  ctx.fillStyle = liquid; ctx.beginPath(); ctx.moveTo(-80, 50); ctx.lineTo(-80, -10 + Math.sin(t * 8) * 10 * slosh); ctx.quadraticCurveTo(0, -10 - Math.sin(t * 8 + 1) * 18 * slosh, 80, -10 - Math.sin(t * 8) * 10 * slosh); ctx.lineTo(80, 50); ctx.fill(); ctx.restore();
  ctx.save(); ctx.globalAlpha = 0.6; tube(ctx, [[-36, -30], [-30, 10]], 8, '#ffffff', 0); ctx.restore();
}
function staff(ctx) { tube(ctx, [[0, -200], [0, 200]], 22, PAL.woodLight, 4.5); }
function hourglass(ctx, x, y, s, flow, t) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  shape(ctx, c => c.rect(-70, -130, 140, 18), PAL.woodDark, { lw: 4 }); shape(ctx, c => c.rect(-70, 112, 140, 18), PAL.woodDark, { lw: 4 });
  for (const sx of [-60, 52]) shape(ctx, c => c.rect(sx, -112, 8, 224), PAL.wood, { lw: 3 });
  shape(ctx, c => { c.moveTo(-46, -112); c.lineTo(46, -112); c.quadraticCurveTo(40, -30, 6, 0); c.quadraticCurveTo(40, 30, 46, 112); c.lineTo(-46, 112); c.quadraticCurveTo(-40, 30, -6, 0); c.quadraticCurveTo(-40, -30, -46, -112); c.closePath(); }, 'rgba(225,245,250,0.45)', { lw: 4, tex: false });
  const top = 1 - flow, bot = flow;
  ctx.fillStyle = '#d9a64a';
  if (top > 0.02) { ctx.beginPath(); const yy = -112 + (1 - top) * 100; ctx.moveTo(-40 * (1 - (yy + 112) / 120) - 6, yy); ctx.lineTo(40 * (1 - (yy + 112) / 120) + 6, yy); ctx.lineTo(6, -4); ctx.lineTo(-6, -4); ctx.fill(); }
  if (flow > 0 && flow < 1) { ctx.fillRect(-2, -4, 4, 110); }
  if (bot > 0.02) { ctx.beginPath(); ctx.moveTo(-42, 110); ctx.quadraticCurveTo(0, 110 - 90 * bot, 42, 110); ctx.fill(); }
  ctx.restore();
}
function wineMug(ctx) { shape(ctx, c => { c.moveTo(-34, -60); c.lineTo(34, -60); c.lineTo(28, 40); c.lineTo(-28, 40); c.closePath(); }, '#8a5a34', { lw: 4.5, shade: { x0: -30, y0: 0, x1: 30, y1: 0, a: 0.3 } }); for (const yy of [-40, 20]) line(ctx, [[-33, yy], [33, yy]], 5, '#5a5550'); shape(ctx, ell(0, -60, 34, 9), '#6a1a2a', { lw: 3.5, tex: false }); }
function dish(ctx, x, y, s = 1) { shape(ctx, ell(x, y, 110 * s, 30 * s), '#c9cdd2', { lw: 5, tex: false, hi: { x: x - 40 * s, y: y - 10 * s, r: 50 * s, a: 0.5 } }); shape(ctx, ell(x, y - 4 * s, 86 * s, 20 * s), '#e2e6ea', { lw: 3, tex: false }); }
function ladder(ctx, x, top, base) { for (const sx of [-55, 55]) shape(ctx, c => c.rect(x + sx - 10, top, 20, base - top), PAL.wood, { lw: 4 }); for (let y = top + 60; y < base; y += 110) line(ctx, [[x - 55, y], [x + 55, y]], 12, PAL.woodDark); }
function bottleRow(ctx, x, y, n, seed) { const r = rand(seed); for (let i = 0; i < n; i++) { const h = 80 + r() * 70, w = 28 + r() * 18, bx = x + i * 70; shape(ctx, c => { c.moveTo(bx - w, y); c.lineTo(bx - w, y - h * 0.6); c.quadraticCurveTo(bx - w, y - h * 0.8, bx - 10, y - h * 0.85); c.lineTo(bx - 10, y - h); c.lineTo(bx + 10, y - h); c.lineTo(bx + 10, y - h * 0.85); c.quadraticCurveTo(bx + w, y - h * 0.8, bx + w, y - h * 0.6); c.lineTo(bx + w, y); c.closePath(); }, ['#6a8a5a', '#8a5a3a', '#4a6a8a', '#9a7a3a'][Math.floor(r() * 4)], { lw: 4, tex: false, hi: { x: bx - w * 0.4, y: y - h * 0.5, r: w, a: 0.5 } }); } }

// ---------------------------------------------------------------- EXAM CHAMBER (opening)
function examLayer(blur) {
  return F.layer('exam' + (blur ? '_b' : ''), -1400, -1800, 3000, 2800, blur ? 0.5 : 1.0, x => {
    E.stoneWall(x, -1400, -1800, 1600, 0, '#8e8070', 61, 150, 76);
    shape(x, c => c.rect(-1400, -1800, 3000, 120), PAL.beam, { lw: 5 });
    for (const px of [-900, 900]) shape(x, c => c.rect(px, -1800, 70, 1800), PAL.beam, { lw: 5, shade: { x0: px, y0: 0, x1: px + 70, y1: 0, a: 0.35 } });
    // shelves: jars, skull-free bottles, books
    for (let i = 0; i < 3; i++) { E.shelf(x, -820, -1300 + i * 220, 560, 70 + i, i === 1 ? 'jars' : 'books'); }
    shape(x, c => c.rect(420, -1350, 440, 560), '#e6cf9f', { lw: 5, shade: { x0: 420, y0: -1350, x1: 860, y1: -790, a: 0.25 } });
    x.font = '40px "Unifraktur"'; x.fillStyle = '#5a2a18'; x.textAlign = 'center'; x.fillText('Anatomia', 640, -1290);
    x.save(); x.translate(640, -1050); x.scale(0.9, 0.9);
    shape(x, ell(0, -160, 46, 52), '#f2e8d2', { lw: 4, tex: false }); line(x, [[0, -105], [0, 60]], 6); for (let i = 0; i < 5; i++) curve(x, [-60, -80 + i * 24], [0, -64 + i * 24], [60, -80 + i * 24], 4);
    line(x, [[-60, -90], [-110, 20]], 5); line(x, [[60, -90], [110, 20]], 5); line(x, [[-20, 60], [-40, 200]], 5); line(x, [[20, 60], [40, 200]], 5);
    x.restore();
    // hanging herbs
    for (let i = 0; i < 7; i++) { const hx = -600 + i * 190; line(x, [[hx, -1680], [hx, -1560 - (i % 3) * 30]], 3); for (let k = 0; k < 5; k++) tube(x, [[hx, -1560 - (i % 3) * 30], [hx - 26 + k * 13, -1470 - (i % 3) * 30]], 7, ['#6d7438', '#8a8a3a', '#5a6a3a'][k % 3], 2.5); }
    E.planks(x, -1400, 0, 1600, 1000, 17, '#6a4a32');
    shape(x, c => c.rect(-1400, -40, 3000, 40), PAL.woodDark, { lw: 4, tex: false });
  });
}
function exam(ctx, cam, t, o = {}) {
  ctx.fillStyle = '#2a1e18'; ctx.fillRect(0, 0, W, H);
  const blur = o.blur || 0;
  dof(ctx, blur, x => F.withCam(x, cam, 0.88, y => { F.drawLayer(y, examLayer(blur > 2)); motes(y, t, -700, -1200, 1400, 1100, 40, 21, 0.45); }, [0, -500]));
  F.withCam(ctx, cam, 1, x => {
    if (o.shadows) o.shadows(x);
    examTable(x, 0, 200);
    if (o.fg) o.fg(x);
  });
  F.withCam(ctx, cam, 0.95, x => lantern(x, 0, -980 + Math.sin(t * 1.3) * 6, t, 1.2), [0, -500]);
  if (o.front) dof(ctx, o.frontBlur === undefined ? 10 : o.frontBlur, x => F.withCam(x, cam, 1.35, o.front, [cam.x, cam.y]), 1);
  lightPool(ctx, W / 2 + (o.poolX || 0), H * 0.42, H * 0.62, 0.6);
  warmWash(ctx);
}

// ---------------------------------------------------------------- DUSK ALLEY (chase + bonk)
const AL = { x0: -800, x1: 7400 };
function alleyLayer() {
  return F.layer('alley', AL.x0, -1700, AL.x1 - AL.x0, 2000, 0.9, x => {
    // back wall: plaster & stone with doors, arches, lanterns
    shape(x, c => c.rect(AL.x0, -1700, AL.x1 - AL.x0, 1720), '#b9a58a', { lw: 0, texA: 0.35 });
    const r = rand(33);
    for (let px = AL.x0; px < AL.x1; px += 520) {
      const kind = Math.floor(r() * 3);
      shape(x, c => c.rect(px, -1700, 40, 1720), PAL.beam, { lw: 5 });
      if (kind === 0) { shape(x, c => { c.moveTo(px + 170, 0); c.lineTo(px + 170, -260); c.arc(px + 260, -260, 90, Math.PI, 0); c.lineTo(px + 350, 0); c.closePath(); }, '#5c3a21', { lw: 5, shade: { x0: px + 170, y0: 0, x1: px + 350, y1: 0, a: 0.3 } }); }
      if (kind === 1) { shape(x, c => { c.moveTo(px + 120, 0); c.lineTo(px + 120, -420); c.arc(px + 280, -420, 160, Math.PI, 0); c.lineTo(px + 440, 0); c.closePath(); }, '#2e2530', { lw: 6 }); }
      if (kind === 2) { E.stoneWall(x, px + 60, -600, px + 500, 0, '#9a8b78', px, 110, 60); }
      shape(x, c => c.rect(px + 200, -1100, 120, 160), '#f2c46a', { lw: 5, tex: false }); line(x, [[px + 260, -1100], [px + 260, -940]], 4); line(x, [[px + 200, -1020], [px + 320, -1020]], 4);
      glow(x, px + 260, -1020, 220, '255,190,110', 0.3);
      // overhead laundry across the alley
      line(x, [[px, -1350], [px + 260, -1300], [px + 520, -1350]], 3);
      for (let k = 0; k < 3; k++) { const lx = px + 80 + k * 140; shape(x, c => { c.moveTo(lx, -1330); c.lineTo(lx + 60, -1330); c.lineTo(lx + 64, -1240); c.lineTo(lx - 4, -1240); c.closePath(); }, ['#e8e0d0', '#c96a4a', '#7a9ab0'][k], { lw: 3.5 }); }
    }
    E.ground(x, AL.x0, AL.x1, 0, 300, 44);
  });
}
function alley(ctx, cam, t, o = {}) {
  const g = ctx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, '#3a2c4a'); g.addColorStop(0.6, '#a5607a'); g.addColorStop(1, '#e8a070');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  dof(ctx, o.blur || 0, x => F.withCam(x, cam, 0.9, y => F.drawLayer(y, alleyLayer()), [0, -400]));
  const G = F.layer('alley_ground', AL.x0, -20, AL.x1 - AL.x0, 1500, 1.0, y => E.ground(y, AL.x0, AL.x1, -20, 1500, 55));
  F.withCam(ctx, cam, 1, x => {
    F.drawLayer(x, G);
    if (o.fg) o.fg(x);
  });
  // near posts and barrels sliding past faster than the subject plane (true parallax)
  if (o.posts !== false) dof(ctx, 9, x => F.withCam(x, cam, 1.6, y => {
    const base = Math.floor(cam.x * 1.6 / 1500) * 1500;
    for (let k = -2; k < 4; k++) { const px = base + k * 1500; shape(y, c => c.rect(px, -1600, 56, 2600), '#4a3020', { lw: 5, shade: { x0: px, y0: 0, x1: px + 56, y1: 0, a: 0.4 } }); E.barrel(y, px + 420, 760, 1.3); }
  }, [0, cam.y]), 1);
  // dusk grade: blue shadows + warm lantern pools
  ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.fillStyle = 'rgba(120,110,170,0.45)'; ctx.fillRect(0, 0, W, H); ctx.restore();
  warmWash(ctx, 'rgba(255,150,90,0.25)');
}

// ---------------------------------------------------------------- golden-hour street (ending only)
function golden(ctx, cam, t, o = {}) {
  S.street(ctx, cam, t, Object.assign({ warm: 1 }, o));
  ctx.save(); ctx.globalCompositeOperation = 'soft-light'; const g = ctx.createLinearGradient(0, 0, W, H); g.addColorStop(0, 'rgba(255,170,70,0.55)'); g.addColorStop(1, 'rgba(120,60,90,0.35)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); ctx.restore();
  rays(ctx, W * 0.85, 0, Math.PI * 0.62, 0.5, 2200, 7, 0.07, 3);
}

// interiors with DOF + optional blurred foreground
function room(kind, ctx, cam, t, o = {}) {
  const fn = { study: S.study, shop: S.shop, surgery: S.surgery }[kind];
  if (!o.blur) { const oo = Object.assign({}, o); if (kind === 'study' && o.chair) { oo.chair = null; const fg0 = o.fg; oo.fg = x => { chair2(x, o.chair, 140); if (fg0) fg0(x); }; } fn(ctx, cam, t, oo); }
  else {
    // background (blurred) then sharp subject plane
    const bg = Object.assign({}, o, { fg: null, front: null, desk: o.desk === false ? false : o.blurDesk ? o.desk : false, counter: false, table: false, chair: null, back: null });
    dof(ctx, o.blur, x => fn(x, cam, t, bg));
    F.withCam(ctx, cam, 1, x => { if (o.back) o.back(x); if (kind === 'shop' && o.counter !== false) S.counter(x, o.counterX || 300, 150); if (kind === 'surgery' && o.table !== false) S.opTable(x, o.tableX || 200, 150); if (kind === 'study' && o.chair) chair2(x, o.chair, 140); if (kind === 'study' && o.desk !== false && !o.blurDesk) S.desk(x, 760, 120, t); if (o.fg) o.fg(x); });
  }
  if (o.front) dof(ctx, o.frontBlur === undefined ? 10 : o.frontBlur, x => F.withCam(x, cam, 1.35, o.front, [cam.x, cam.y]), 1);
}
// chair built around the rig's seated pose: feet on the floor at feetY, seat top = hip height
const SHIN = 165 * 0.48;
function chair2(x, cx, feetY, cushion = '#8a2f2a') {
  const seat = feetY - SHIN + 4;
  shape(x, c => c.rect(cx - 112, seat - 360, 28, 360 + (feetY - seat)), PAL.woodDark, { lw: 5, shade: { x0: cx - 112, y0: 0, x1: cx - 84, y1: 0, a: 0.3 } });
  shape(x, c => c.roundRect(cx - 120, seat - 330, 44, 250, 14), cushion, { lw: 5 });
  shape(x, c => c.rect(cx - 125, seat, 230, 34), PAL.wood, { lw: 5, hi: { x: cx, y: seat, r: 90, a: 0.2 } });
  for (const lx of [-118, 80]) shape(x, c => c.rect(cx + lx, seat + 32, 24, feetY - seat - 30), PAL.woodDark, { lw: 4 });
}

module.exports = { chair2, dof, castShadow, lightPool, warmWash, lantern, pillow, examTable, flask, staff, hourglass, wineMug, dish, ladder, bottleRow, exam, alley, golden, room };
