// V4 WORLD: Mediterranean map, Akragas, Perillus' workshop, Phalaris' throne room, golden courtyard.
'use strict';
POSES.seated = Object.assign({}, POSES.seated, { y: 540, nF: [-600, G], fF: [-520, G] });
POSES.seatedPoint = Object.assign({}, POSES.seatedPoint, { y: 540, nF: [-600, G], fF: [-520, G] });

// ------------------------------------------------------------------ engraved bronze map (Athens -> Akragas)
const MAP = {
  italy: [[380, 120], [470, 170], [560, 260], [640, 360], [720, 470], [790, 560], [830, 640], [800, 700], [760, 690], [740, 740], [700, 820], [660, 815], [650, 760], [610, 715], [565, 645], [505, 560], [430, 470], [380, 390], [350, 290], [340, 180]],
  sicily: [[560, 880], [640, 866], [720, 862], [770, 850], [745, 905], [728, 985], [650, 1020], [570, 1004], [505, 965], [470, 918]],
  greece: [[880, 760], [940, 800], [985, 880], [1010, 960], [990, 1040], [1050, 1095], [1010, 1170], [955, 1150], [935, 1090], [890, 1040], [870, 960], [860, 860]],
  africa: [[-40, 1480], [200, 1440], [420, 1400], [560, 1360], [640, 1390], [820, 1440], [1120, 1470], [1120, 2000], [-40, 2000]],
};
function mapScene(ctx, t, zoom, opt = {}) {
  const k = zoom, cx = lerp(540, 600, k), cy = lerp(960, 960, k), s = lerp(1, 3.0, k);
  ctx.save(); ctx.fillStyle = '#0c0806'; ctx.fillRect(0, 0, W, H);
  ctx.translate(W / 2, H / 2); ctx.scale(s, s); ctx.translate(-cx, -cy);
  // sea: hammered bronze with engraved wave lines
  ctx.fillStyle = radGrad(ctx, 600, 900, 50, 1300, [[0, '#3a2412'], [1, '#160c06']]); ctx.fillRect(-200, -200, 1500, 2400);
  ctx.strokeStyle = 'rgba(224,170,96,0.14)'; ctx.lineWidth = 1.5 / s * 1.4;
  for (let y = 0; y < 1900; y += 34) { ctx.beginPath(); for (let x = -100; x < 1200; x += 20) ctx.lineTo(x, y + Math.sin(x * 0.03 + t * 1.5 + y) * 4); ctx.stroke(); }
  const land = (pts, glowA) => { ctx.fillStyle = linGrad(ctx, 0, 100, 0, 1500, [[0, '#8a5a2a'], [1, '#5a3618']]); ctx.beginPath(); crPath(ctx, pts, true); ctx.fill();
    ctx.save(); ctx.clip(); ctx.strokeStyle = 'rgba(0,0,0,0.25)'; ctx.lineWidth = 2; for (let i = -1500; i < 1500; i += 16) { ctx.beginPath(); ctx.moveTo(i, 0); ctx.lineTo(i + 1500, 1500); ctx.stroke(); } ctx.restore();
    ctx.strokeStyle = rgba('#f0c878', 0.9); ctx.lineWidth = 3 / s * 1.5; ctx.beginPath(); crPath(ctx, pts, true); ctx.stroke();
    if (glowA) { ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.filter = 'blur(8px)'; ctx.strokeStyle = rgba('#ffb060', glowA); ctx.lineWidth = 12; ctx.stroke(); ctx.restore(); } };
  land(MAP.italy); land(MAP.greece); land(MAP.africa); land(MAP.sicily, 0.4 + 0.5 * (opt.pulse || 0));
  // route Athens -> Akragas (dashed, drawing on)
  const route = curvePts([[1000, 1060], [900, 1180], [760, 1120], [640, 1040], [600, 1000]], 60);
  const n = Math.floor(route.length * clamp(opt.route ?? 1));
  ctx.save(); ctx.setLineDash([14, 12]); ctx.strokeStyle = rgba('#ffd890', 0.9); ctx.lineWidth = 4; ctx.beginPath(); route.slice(0, n).forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)); ctx.stroke(); ctx.restore();
  if (n > 1) { const [x, y] = route[n - 1]; // small ship
    ctx.save(); ctx.translate(x, y); ctx.fillStyle = '#e8c070'; ctx.beginPath(); ctx.moveTo(-18, 0); ctx.lineTo(18, 0); ctx.lineTo(10, 8); ctx.lineTo(-10, 8); ctx.closePath(); ctx.fill();
    ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(0, -26); ctx.lineTo(14, -6); ctx.closePath(); ctx.fill(); ctx.restore(); }
  // cities
  const city = (x, y, name, a, big) => { ctx.save(); ctx.globalAlpha = a; ctx.fillStyle = '#ffe0a0'; ctx.beginPath(); ctx.arc(x, y, big ? 9 : 6, 0, 6.283); ctx.fill();
    ctx.strokeStyle = '#ffe0a0'; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(x, y, (big ? 18 : 12) + 6 * Math.sin(t * 4), 0, 6.283); ctx.stroke();
    ctx.font = `700 ${big ? 30 : 22}px Cinzel`; ctx.textAlign = 'center'; ctx.fillText(name, x, y + (big ? 52 : -22)); ctx.restore(); };
  city(1000, 1060, 'ATHENS', 1, false); city(600, 1000, 'AKRAGAS', 0.4 + 0.6 * clamp(opt.route ?? 1), true);
  ctx.save(); ctx.globalAlpha = 0.55; ctx.font = '600 34px Cinzel'; ctx.fillStyle = '#f0c878'; ctx.textAlign = 'center'; ctx.letterSpacing = '10px';
  ctx.fillText('SICILIA', 660, 925); ctx.fillText('MARE NOSTRUM', 560, 1250); ctx.restore();
  // compass rose
  ctx.save(); ctx.translate(250, 1180); ctx.rotate(t * 0.05); ctx.strokeStyle = 'rgba(240,200,120,0.6)'; ctx.lineWidth = 2;
  for (let i = 0; i < 8; i++) { ctx.rotate(Math.PI / 4); ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(0, i % 2 ? -40 : -70); ctx.stroke(); } ctx.beginPath(); ctx.arc(0, 0, 50, 0, 6.283); ctx.stroke(); ctx.restore();
  ctx.restore();
  vignette(ctx, 0.7);
}

// ------------------------------------------------------------------ Doric temple (frontal-oblique), used in Akragas
function temple(g, x, y, w, h, lit, col = '#c89a62') {
  g.save(); g.translate(x, y);
  const cols = 6, cw = w / (cols * 1.6);
  g.fillStyle = mix('#3a2614', col, 0.5); g.fillRect(-w * 0.55, -h * 0.08, w * 1.1, h * 0.08);          // stylobate
  for (let i = 0; i < cols; i++) { const cx = -w / 2 + cw / 2 + i * (w - cw) / (cols - 1);
    g.fillStyle = linGrad(g, cx - cw / 2, 0, cx + cw / 2, 0, [[0, mix('#2a1a0e', col, 0.4)], [0.35, mix(col, '#ffe8c0', lit)], [1, mix('#2a1a0e', col, 0.3)]]);
    g.fillRect(cx - cw / 2, -h * 0.75, cw, h * 0.67); }
  g.fillStyle = mix('#3a2614', col, 0.7); g.fillRect(-w * 0.56, -h * 0.86, w * 1.12, h * 0.12);          // entablature
  g.fillStyle = mix('#2a1a0e', col, 0.6); g.beginPath(); g.moveTo(-w * 0.58, -h * 0.86); g.lineTo(0, -h); g.lineTo(w * 0.58, -h * 0.86); g.closePath(); g.fill();
  g.fillStyle = rgba('#ffe0b0', 0.25 * lit); g.fillRect(-w * 0.56, -h * 0.86, w * 1.12, 4);
  g.restore();
}
function house(g, x, y, w, h, roofCol = '#9a4a28') {
  g.fillStyle = '#c8a880'; g.fillRect(x, y - h, w, h); g.fillStyle = 'rgba(0,0,0,0.25)'; g.fillRect(x + w * 0.6, y - h, w * 0.4, h);
  g.fillStyle = roofCol; g.beginPath(); g.moveTo(x - 6, y - h); g.lineTo(x + w / 2, y - h - h * 0.45); g.lineTo(x + w + 6, y - h); g.closePath(); g.fill();
  g.fillStyle = '#2a1a10'; g.fillRect(x + w * 0.25, y - h * 0.5, w * 0.16, h * 0.3);
}
// small walking citizen (tiny scale figure, cloth + legs cycle)
function walker(g, x, y, sc, t, k, dir = 1) {
  const r = mulberry(k * 17 + 3), col = ['#e8d8b0', '#b8602a', '#5a7a8a', '#8a9a5a', '#d8b060', '#9a4a4a'][k % 6];
  const ph = t * 6 + k, step = Math.sin(ph) * 0.45;
  g.save(); g.translate(x, y); g.scale(sc * dir, sc);
  g.strokeStyle = '#5a3a24'; g.lineWidth = 14; g.lineCap = 'round';
  g.beginPath(); g.moveTo(0, -120); g.lineTo(Math.sin(step) * 60, 0); g.stroke(); g.beginPath(); g.moveTo(0, -120); g.lineTo(-Math.sin(step) * 60, 0); g.stroke();
  g.fillStyle = col; g.beginPath(); g.moveTo(-36, -260); g.lineTo(36, -260); g.lineTo(48 + Math.sin(ph) * 6, -90); g.lineTo(-48 + Math.sin(ph + 1) * 6, -90); g.closePath(); g.fill();
  g.fillStyle = 'rgba(0,0,0,0.25)'; g.fillRect(4, -260, 32, 170);
  g.fillStyle = '#b88060'; g.beginPath(); g.arc(-4, -292, 30, 0, 6.283); g.fill();
  g.fillStyle = r() < 0.5 ? '#2a1a10' : '#6a6a6a'; g.beginPath(); g.arc(2, -302, 28, Math.PI, 0); g.fill();
  if (k % 3 === 0) { g.fillStyle = col; g.fillRect(-40, -250, 18, 120); }           // draped mantle
  g.restore();
}
function akragas(ctx, t, cam = {}) {
  const cx = cam.x || 0, up = cam.up || 0;
  // golden late-afternoon sky over the sea
  ctx.fillStyle = linGrad(ctx, 0, 0, 0, 1100, [[0, '#2a1830'], [0.45, '#a85a3a'], [0.8, '#f0a860'], [1, '#ffd8a0']]); ctx.fillRect(0, 0, W, H);
  glow(ctx, 760 - cx * 0.05, 960 + up * 0.1, 420, '#fff0c0', 0.7);
  // sea band
  ctx.fillStyle = linGrad(ctx, 0, 980, 0, 1150, [[0, '#c88a5a'], [1, '#5a4a5a']]); ctx.fillRect(0, 980 + up * 0.2, W, 200);
  ctx.save(); ctx.strokeStyle = 'rgba(255,230,180,0.35)'; ctx.lineWidth = 2; for (let i = 0; i < 10; i++) { const y = 1000 + i * 14 + up * 0.2; ctx.beginPath(); ctx.moveTo(300 + Math.sin(t + i) * 40 - cx * 0.1, y); ctx.lineTo(900 + Math.sin(t * 1.3 + i) * 40 - cx * 0.1, y); ctx.stroke(); } ctx.restore();
  // far ridge with the temple row (parallax 0.3)
  ctx.save(); ctx.translate(-cx * 0.3, up * 0.3);
  ctx.fillStyle = '#6a3a2a'; ctx.beginPath(); ctx.moveTo(-100, 1150); for (let x = -100; x <= 1300; x += 60) ctx.lineTo(x, 1090 - Math.sin(x * 0.004) * 60 - Math.sin(x * 0.013) * 14); ctx.lineTo(1300, 1300); ctx.lineTo(-100, 1300); ctx.closePath(); ctx.fill();
  temple(ctx, 220, 1040, 220, 140, 0.8); temple(ctx, 640, 1010, 300, 190, 1.0); temple(ctx, 1000, 1050, 180, 120, 0.7);
  ctx.restore();
  // city on the slope (parallax 0.6)
  ctx.save(); ctx.translate(-cx * 0.6, up * 0.6);
  ctx.fillStyle = '#7a4a30'; ctx.beginPath(); ctx.moveTo(-200, 1500); ctx.quadraticCurveTo(500, 1180, 1400, 1360); ctx.lineTo(1400, 1700); ctx.lineTo(-200, 1700); ctx.closePath(); ctx.fill();
  const r = mulberry(8);
  for (let i = 0; i < 46; i++) { const x = -150 + r() * 1450, y = 1330 + r() * 260 - (x > 200 && x < 900 ? 40 : 0); house(ctx, x, y, 40 + r() * 50, 30 + r() * 30, ['#9a4a28', '#b0582e', '#8a3a22'][i % 3]); }
  // city wall
  ctx.fillStyle = '#8a6a4a'; ctx.fillRect(-200, 1600, 1600, 50); for (let x = -200; x < 1400; x += 120) ctx.fillRect(x, 1560, 60, 50);
  // cypress trees
  for (let i = 0; i < 7; i++) { const x = 40 + i * 170 + r() * 40, y = 1600; ctx.fillStyle = '#2a3a20'; ctx.beginPath(); ctx.ellipse(x, y - 90, 22, 100, 0, 0, 6.283); ctx.fill(); }
  ctx.restore();
  // foreground road with citizens + banners (parallax 1)
  ctx.save(); ctx.translate(-cx, up);
  ctx.fillStyle = linGrad(ctx, 0, 1640, 0, H, [[0, '#a87a52'], [1, '#4a2e1a']]); ctx.fillRect(-300, 1640, 1700, 400);
  for (let i = 0; i < 9; i++) { const dir = i % 2 ? 1 : -1, speed = 40 + (i * 13) % 30, x = ((i * 190 + t * speed * dir) % 1500 + 1500) % 1500 - 200;
    walker(ctx, x, 1760 + (i % 3) * 50, 0.42 + (i % 3) * 0.08, t, i, dir); }
  // banners on poles fluttering
  for (const bx of [80, 980]) { ctx.fillStyle = '#5a3a1e'; ctx.fillRect(bx, 1300, 10, 420); const pts = []; for (let k = 0; k <= 10; k++) pts.push([bx + 10 + k * 18, 1310 + Math.sin(t * 5 + k * 0.7) * 10 * (k / 10)]);
    for (let k = 10; k >= 0; k--) pts.push([bx + 10 + k * 18, 1400 + Math.sin(t * 5 + k * 0.7 + 0.5) * 10 * (k / 10)]); ctx.fillStyle = '#9a2a1e'; ctx.beginPath(); crPath(ctx, pts, true); ctx.fill(); }
  ctx.restore();
  // birds
  ctx.save(); ctx.strokeStyle = 'rgba(40,20,20,0.7)'; ctx.lineWidth = 3; for (let i = 0; i < 6; i++) { const x = ((t * 60 + i * 170) % 1300) - 100, y = 500 + i * 40 + Math.sin(t * 2 + i) * 20, f = Math.sin(t * 10 + i) * 10;
    ctx.beginPath(); ctx.moveTo(x - 16, y - f); ctx.quadraticCurveTo(x - 6, y - 6, x, y); ctx.quadraticCurveTo(x + 6, y - 6, x + 16, y - f); ctx.stroke(); } ctx.restore();
  // warm haze
  ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.fillStyle = linGrad(ctx, 0, 900, 0, 1500, [[0, 'rgba(255,200,140,0.0)'], [0.5, 'rgba(255,200,140,0.18)'], [1, 'rgba(255,200,140,0)']]); ctx.fillRect(0, 0, W, H); ctx.restore();
}

// ------------------------------------------------------------------ Perillus' workshop
function workshop(ctx, t, cam = {}) {
  const cx = cam.x || 0, forge = 0.7 + 0.3 * Math.sin(t * 9) * Math.sin(t * 5.3);
  ctx.fillStyle = linGrad(ctx, 0, 0, 0, H, [[0, '#1a120c'], [1, '#2a1a10']]); ctx.fillRect(0, 0, W, H);
  // stone wall blocks
  ctx.save(); ctx.translate(-cx * 0.4, 0); const r = mulberry(21);
  for (let y = 0; y < 1500; y += 90) for (let x = -200 + (y / 90 % 2) * 70; x < 1400; x += 140) { ctx.fillStyle = rgba('#5a4030', 0.35 + r() * 0.25); ctx.fillRect(x + 3, y + 3, 134, 84); }
  // window light shaft from the upper left
  ctx.fillStyle = '#ffe0a8'; ctx.fillRect(140, 180, 160, 220);
  ctx.restore();
  shaft(ctx, 220 - cx * 0.4, 290, 160, 620 - cx * 0.4, 1700, 520, '#ffd8a0', 0.28);
  // tool rack: hammers, tongs, chisels hanging
  ctx.save(); ctx.translate(-cx * 0.5, 0);
  ctx.fillStyle = '#4a2e18'; ctx.fillRect(560, 420, 460, 26);
  const tools = [['h', 600], ['t', 670], ['h', 740], ['c', 800], ['c', 840], ['t', 900], ['h', 970]];
  for (const [k, x] of tools) { ctx.fillStyle = '#5a3a1e'; ctx.fillRect(x - 6, 446, 12, k === 'c' ? 120 : 200);
    ctx.fillStyle = '#8a8a82'; if (k === 'h') ctx.fillRect(x - 30, 620, 60, 34); else if (k === 't') { ctx.fillRect(x - 14, 600, 8, 90); ctx.fillRect(x + 6, 600, 8, 90); } else ctx.fillRect(x - 4, 560, 8, 40); }
  // shelf with clay study models of the bull
  ctx.fillStyle = '#4a2e18'; ctx.fillRect(100, 760, 380, 22);
  for (let i = 0; i < 2; i++) { ctx.save(); ctx.translate(200 + i * 160, 760); ctx.scale(0.14, 0.14); ctx.fillStyle = '#8a5a3a'; ctx.beginPath(); crPath(ctx, BULL.body, true); ctx.fill(); ctx.restore(); }
  ctx.restore();
  // forge: glowing coals at right
  ctx.save(); ctx.translate(-cx * 0.7, 0);
  ctx.fillStyle = '#2a1a12'; ctx.fillRect(820, 1050, 320, 300); ctx.fillStyle = '#3a261a'; ctx.fillRect(860, 600, 220, 450);
  ctx.fillStyle = radGrad(ctx, 980, 1120, 10, 200, [[0, '#ffe0a0'], [0.4, '#ff7a20'], [1, 'rgba(120,20,0,0)']]); ctx.fillRect(820, 980, 320, 260);
  glow(ctx, 980, 1120, 600 * forge, '#ff7a2a', 0.5 * forge);
  ctx.restore();
  // floor
  ctx.fillStyle = linGrad(ctx, 0, 1500, 0, H, [[0, '#3a2818'], [1, '#1a100a']]); ctx.fillRect(0, 1500, W, 420);
  motes(ctx, t, 40, 9, { x0: 800 - cx * 0.7, x1: 1100 - cx * 0.7, y0: 900, y1: 1200, vy: -120, size: [1, 2.6], col: '#ffb060', a: 0.8, life: 2.2 });
  motes(ctx, t, 40, 13, { x0: 150, x1: 700, y0: 300, y1: 1600, vy: -10, vx: 6, size: [0.8, 2], col: '#ffe8c0', a: 0.5, life: 8 });
}
function anvil(g, x, y, sc) {
  g.save(); g.translate(x, y); g.scale(sc, sc);
  g.fillStyle = '#3a3a3a'; g.beginPath(); g.moveTo(-200, -120); g.lineTo(160, -120); g.quadraticCurveTo(260, -110, 300, -80); g.lineTo(140, -70); g.lineTo(110, 0); g.lineTo(150, 120); g.lineTo(-140, 120); g.lineTo(-100, 0); g.lineTo(-140, -70); g.closePath(); g.fill();
  g.fillStyle = 'rgba(255,255,255,0.25)'; g.fillRect(-200, -120, 400, 10); g.restore();
}

// ------------------------------------------------------------------ Phalaris' throne room
function throneRoom(ctx, t, cam = {}) {
  const cx = cam.x || 0;
  ctx.fillStyle = linGrad(ctx, 0, 0, 0, H, [[0, '#120a0c'], [1, '#2a1410']]); ctx.fillRect(0, 0, W, H);
  // back wall with purple drapes swaying
  ctx.save(); ctx.translate(-cx * 0.3, 0);
  for (let i = 0; i < 4; i++) { const x0 = 40 + i * 280, pts = []; for (let y = 0; y <= 1500; y += 50) pts.push([x0 + Math.sin(y * 0.01 + t * 1.2 + i) * 10, y]);
    for (let y = 1500; y >= 0; y -= 50) pts.push([x0 + 220 + Math.sin(y * 0.01 + t * 1.2 + i + 1) * 12, y]);
    ctx.fillStyle = linGrad(ctx, x0, 0, x0 + 220, 0, [[0, '#2a0c20'], [0.5, '#6a1a4a'], [1, '#2a0c20']]); ctx.beginPath(); crPath(ctx, pts, true); ctx.fill(); }
  ctx.restore();
  // columns (parallax 0.6)
  ctx.save(); ctx.translate(-cx * 0.6, 0); for (const x of [60, 1020]) column(ctx, x, 1600, 150, 1550, 0.35); ctx.restore();
  // throne dais + throne
  ctx.fillStyle = '#3a261c'; ctx.fillRect(220, 1440, 640, 90); ctx.fillStyle = '#4a3226'; ctx.fillRect(170, 1530, 740, 90);
  ctx.fillStyle = linGrad(ctx, 360, 700, 720, 700, [[0, '#5a3a1e'], [0.5, '#a87a3a'], [1, '#4a2e16']]); ctx.beginPath(); ctx.moveTo(380, 1440); ctx.lineTo(380, 760); ctx.quadraticCurveTo(540, 660, 700, 760); ctx.lineTo(700, 1440); ctx.closePath(); ctx.fill();
  ctx.fillStyle = '#e0b060'; ctx.beginPath(); ctx.arc(540, 790, 26, 0, 6.283); ctx.fill();
  // braziers
  for (const bx of [140, 940]) { ctx.fillStyle = '#4a3020'; ctx.fillRect(bx - 12, 1300, 24, 240); ctx.fillStyle = '#6a4224'; ctx.beginPath(); ctx.ellipse(bx, 1300, 70, 22, 0, 0, 6.283); ctx.fill();
    const f = 0.8 + 0.2 * Math.sin(t * 11 + bx); glow(ctx, bx, 1260, 300 * f, '#ff8a3a', 0.55); ctx.fillStyle = '#ffb060'; ctx.beginPath(); ctx.ellipse(bx, 1250, 30, 50 * f, 0, 0, 6.283); ctx.fill(); }
  // mosaic floor
  ctx.fillStyle = linGrad(ctx, 0, 1600, 0, H, [[0, '#3a2a1e'], [1, '#160e0a']]); ctx.fillRect(0, 1620, W, 300);
  ctx.save(); ctx.strokeStyle = 'rgba(224,170,96,0.2)'; ctx.lineWidth = 3; for (let i = 0; i < 12; i++) { ctx.beginPath(); ctx.moveTo(540, 1620); ctx.lineTo(-600 + i * 200, H); ctx.stroke(); } ctx.restore();
  motes(ctx, t, 40, 15, { vy: -12, vx: 4, size: [0.8, 2], col: '#ffd8a0', a: 0.4, life: 9 });
}

// ------------------------------------------------------------------ golden-hour courtyard (return to the legend: daylight, not night)
function courtyardGold(ctx, t, cam) {
  courtyard(ctx, cam, t, { fire: 0.3, eyeGlow: 0.1 });
  ctx.save(); ctx.globalCompositeOperation = 'soft-light'; ctx.fillStyle = linGrad(ctx, 0, 0, 0, H, [[0, '#ffb070'], [0.6, '#ffd8a0'], [1, '#8a4a2a']]); ctx.fillRect(0, 0, W, H); ctx.restore();
  ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.fillStyle = linGrad(ctx, 0, 0, 0, cam.hz, [[0, 'rgba(255,150,80,0.35)'], [1, 'rgba(255,210,150,0.55)']]); ctx.fillRect(0, 0, W, cam.hz); ctx.restore();
  shaft(ctx, 1080, 200, 80, 300, 1700, 600, '#ffd8a0', 0.25);
}

TESTS.world4 = (ctx, t) => {
  const tiles = [(g) => mapScene(g, t, 0.3, { route: 0.7, pulse: 0.5 }), (g) => akragas(g, t), (g) => { workshop(g, t); anvil(g, 420, 1500, 0.9); }, (g) => throneRoom(g, t)];
  tiles.forEach((fn, i) => { const L = cvs('wt' + i), g = L.getContext('2d'); fn(g); ctx.drawImage(L, (i % 2) * 540, Math.floor(i / 2) * 960, 540, 960); });
};
