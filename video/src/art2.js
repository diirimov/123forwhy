// ---------- more art: props, sets, typography helpers ----------
const helmet = (ctx, hx, hy) => {
  ctx.beginPath(); ctx.moveTo(hx - 34, hy - 2); ctx.quadraticCurveTo(hx - 34, hy - 50, hx + 2, hy - 50); ctx.quadraticCurveTo(hx + 36, hy - 50, hx + 34, hy - 2); ctx.closePath();
  const g = ctx.createLinearGradient(hx - 34, 0, hx + 34, 0); g.addColorStop(0, '#6d7480'); g.addColorStop(.4, '#c9d0d8'); g.addColorStop(1, '#5b616b'); fillStroke(ctx, g, 5);
  ell(ctx, hx, hy - 2, 46, 8); fillStroke(ctx, '#8a919b', 4.5);
  ctx.beginPath(); ctx.moveTo(hx + 2, hy - 50); ctx.lineTo(hx + 2, hy - 4); ctx.lineWidth = 4; ctx.strokeStyle = 'rgba(0,0,0,.4)'; ctx.stroke();
};
const tonsure = (ctx, hx, hy) => { ctx.beginPath(); ctx.moveTo(hx - 31, hy + 4); ctx.quadraticCurveTo(hx - 32, hy - 18, hx - 20, hy - 24); ctx.lineTo(hx - 10, hy - 10); ctx.quadraticCurveTo(hx - 18, hy, hx - 20, hy + 12); ctx.closePath(); fillStroke(ctx, '#d8d0c0', 4); };
const halberd = (ctx, x, y) => {
  ctx.save(); ctx.translate(x, y);
  ctx.beginPath(); ctx.moveTo(0, 130); ctx.lineTo(0, -230); ctx.lineWidth = 11; ctx.strokeStyle = INK; ctx.stroke(); ctx.lineWidth = 6; ctx.strokeStyle = '#7a5634'; ctx.stroke();
  ctx.beginPath(); ctx.moveTo(0, -230); ctx.lineTo(-8, -290); ctx.lineTo(8, -230); ctx.closePath(); fillStroke(ctx, '#b9c0c8', 4);
  ctx.beginPath(); ctx.moveTo(4, -220); ctx.quadraticCurveTo(52, -230, 50, -186); ctx.lineTo(4, -196); ctx.closePath(); fillStroke(ctx, '#c9d0d8', 4);
  ctx.restore();
};
const clapper = (ctx, x, y) => { ctx.save(); ctx.translate(x, y); rr(ctx, -8, -46, 16, 46, 4); fillStroke(ctx, '#8a6a42', 4); rr(ctx, 6, -44, 12, 36, 3); fillStroke(ctx, '#a07a4a', 4); ctx.restore(); };
const handbell = (ctx, x, y) => { ctx.save(); ctx.translate(x, y); ctx.scale(.5, .5); drawBell(ctx, 0, 0, 1, Math.sin(performanceT * 20) * .4, '#b8902f'); ctx.restore(); };
let performanceT = 0;

// ---- sea + ship ----
function drawSea(ctx, t, y0, w, h, moonX) {
  ctx.fillStyle = vgrad(ctx, y0, y0 + h, [[0, '#1a2440'], [1, '#05070f']]); ctx.fillRect(-w / 2, y0, w, h);
  ctx.save(); ctx.globalCompositeOperation = 'lighter';
  for (let i = 0; i < 70; i++) {
    const yy = y0 + 10 + Math.pow(hash(i), 1.6) * h * .9, ww = 30 + hash(i + 3) * 160 * (1 + (yy - y0) / h);
    const xx = moonX + (hash(i + 7) - .5) * 300 * (1 + (yy - y0) / 300) + Math.sin(t * 1.5 + i) * 20;
    ctx.globalAlpha = .12 + hash(i + 2) * .25; ctx.fillStyle = '#ff9a7a'; ctx.fillRect(xx - ww / 2, yy, ww, 3 + (yy - y0) / h * 4);
  }
  ctx.restore();
  ctx.strokeStyle = 'rgba(120,150,200,.18)'; ctx.lineWidth = 3;
  for (let i = 0; i < 40; i++) { const yy = y0 + hash(i + 50) * h, xx = (hash(i + 60) - .5) * w; ctx.beginPath(); ctx.moveTo(xx, yy); ctx.quadraticCurveTo(xx + 20, yy - 6 + Math.sin(t * 2 + i) * 3, xx + 40, yy); ctx.stroke(); }
}
function drawShip(ctx, x, y, s, t) {
  ctx.save(); ctx.translate(x, y + Math.sin(t * 1.3) * 8); ctx.rotate(Math.sin(t * 1.1) * .025); ctx.scale(s, s);
  // mast + furled sail
  ctx.beginPath(); ctx.moveTo(20, -120); ctx.lineTo(20, -620); ctx.lineWidth = 18; ctx.strokeStyle = INK; ctx.stroke(); ctx.lineWidth = 10; ctx.strokeStyle = '#5a3d26'; ctx.stroke();
  ctx.beginPath(); ctx.moveTo(-200, -540); ctx.quadraticCurveTo(20, -500, 240, -560); ctx.lineWidth = 14; ctx.strokeStyle = INK; ctx.stroke(); ctx.lineWidth = 8; ctx.strokeStyle = '#5a3d26'; ctx.stroke();
  ctx.beginPath(); ctx.moveTo(-190, -536); ctx.quadraticCurveTo(20, -470, 230, -556); ctx.quadraticCurveTo(20, -500, -190, -536); fillStroke(ctx, '#b8a27c', 5);
  ctx.strokeStyle = 'rgba(20,10,10,.8)'; ctx.lineWidth = 2.5; for (const [a, b] of [[-260, -130], [300, -120], [20, -620]]) { ctx.beginPath(); ctx.moveTo(20, -600); ctx.lineTo(a, b); ctx.stroke(); }
  // hull
  ctx.beginPath(); ctx.moveTo(-330, -170); ctx.quadraticCurveTo(-300, -40, -150, -10); ctx.lineTo(220, -10); ctx.quadraticCurveTo(340, -40, 380, -190); ctx.lineTo(300, -150); ctx.lineTo(-260, -140); ctx.closePath();
  const hg = ctx.createLinearGradient(0, -190, 0, -10); hg.addColorStop(0, '#6b4528'); hg.addColorStop(1, '#2a1a12'); fillStroke(ctx, hg, 7);
  ctx.strokeStyle = 'rgba(0,0,0,.45)'; ctx.lineWidth = 3; for (const yy of [-110, -75, -45]) { ctx.beginPath(); ctx.moveTo(-290, yy); ctx.quadraticCurveTo(20, yy + 18, 330, yy - 8); ctx.stroke(); }
  // castles
  rr(ctx, -330, -230, 120, 70, 6); fillStroke(ctx, '#5a3a22', 5); rr(ctx, 260, -250, 120, 80, 6); fillStroke(ctx, '#5a3a22', 5);
  // oars
  for (let k = 0; k < 9; k++) { const ox = -200 + k * 50, a = Math.sin(t * 2 + k * .3) * .15; ctx.beginPath(); ctx.moveTo(ox, -70); ctx.lineTo(ox - 70 + a * 100, 40); ctx.lineWidth = 6; ctx.strokeStyle = INK; ctx.stroke(); }
  // lanterns
  for (const [lx, ly] of [[-270, -250], [320, -270]]) { ell(ctx, lx, ly, 10, 14); ctx.fillStyle = '#ffcf7a'; ctx.fill(); glow(ctx, lx, ly, 120, 'rgba(255,170,80,.6)'); }
  ctx.restore();
}

// ---- cathedral facade ----
function drawCathedral(ctx, x, by, s, doorOpen) {
  ctx.save(); ctx.translate(x, by); ctx.scale(s, s);
  const stone = ctx.createLinearGradient(-500, 0, 500, 0); stone.addColorStop(0, '#5a5262'); stone.addColorStop(.5, '#7f7584'); stone.addColorStop(1, '#4a4352');
  for (const tx of [-460, 260]) { // towers
    ctx.beginPath(); ctx.rect(tx, -1250, 200, 1250); fillStroke(ctx, stone, 7);
    ctx.beginPath(); ctx.moveTo(tx - 10, -1250); ctx.lineTo(tx + 100, -1700); ctx.lineTo(tx + 210, -1250); ctx.closePath(); fillStroke(ctx, '#3a3446', 7);
    for (let k = 0; k < 3; k++) { ctx.beginPath(); ctx.moveTo(tx + 70, -400 - k * 270); ctx.lineTo(tx + 70, -520 - k * 270); ctx.arc(tx + 100, -520 - k * 270, 30, Math.PI, 0); ctx.lineTo(tx + 130, -400 - k * 270); ctx.closePath(); fillStroke(ctx, '#1a1420', 5); }
  }
  ctx.beginPath(); ctx.moveTo(-260, 0); ctx.lineTo(-260, -900); ctx.lineTo(0, -1200); ctx.lineTo(260, -900); ctx.lineTo(260, 0); ctx.closePath(); fillStroke(ctx, stone, 7);
  // rose window
  ell(ctx, 0, -820, 150, 150); fillStroke(ctx, '#2a1430', 7);
  ctx.save(); ctx.globalCompositeOperation = 'lighter';
  for (let k = 0; k < 12; k++) { const a = k * TAU / 12; ctx.beginPath(); ctx.moveTo(0, -820); ctx.arc(0, -820, 135, a, a + TAU / 12 - .06); ctx.closePath(); ctx.fillStyle = ['rgba(200,40,60,.55)', 'rgba(60,80,200,.5)', 'rgba(220,170,60,.5)'][k % 3]; ctx.fill(); }
  ctx.restore();
  glow(ctx, 0, -820, 400, 'rgba(255,120,80,.25)');
  ell(ctx, 0, -820, 40, 40); fillStroke(ctx, '#f2c96a', 5);
  // portal
  ctx.beginPath(); ctx.moveTo(-190, 0); ctx.lineTo(-190, -380); ctx.quadraticCurveTo(-190, -600, 0, -660); ctx.quadraticCurveTo(190, -600, 190, -380); ctx.lineTo(190, 0); ctx.closePath(); fillStroke(ctx, '#3d3546', 7);
  ctx.beginPath(); ctx.moveTo(-140, 0); ctx.lineTo(-140, -360); ctx.quadraticCurveTo(-140, -530, 0, -580); ctx.quadraticCurveTo(140, -530, 140, -360); ctx.lineTo(140, 0); ctx.closePath();
  ctx.fillStyle = '#ffb35a'; ctx.fill(); glow(ctx, 0, -200, 420, 'rgba(255,150,60,.6)', 1 - (1 - doorOpen) * .9);
  // doors (each swings: width scales with open)
  for (const side of [-1, 1]) {
    const w = 140 * (1 - doorOpen * .85);
    ctx.save(); ctx.beginPath(); ctx.moveTo(-140, 0); ctx.lineTo(-140, -360); ctx.quadraticCurveTo(-140, -530, 0, -580); ctx.quadraticCurveTo(140, -530, 140, -360); ctx.lineTo(140, 0); ctx.closePath(); ctx.clip();
    ctx.beginPath(); ctx.rect(side < 0 ? -140 : 140 - w, -600, w, 600); fillStroke(ctx, '#4a2c1c', 6);
    ctx.strokeStyle = 'rgba(0,0,0,.4)'; ctx.lineWidth = 4; for (let k = 1; k < 4; k++) { const xx = side < 0 ? -140 + w * k / 4 : 140 - w * k / 4; ctx.beginPath(); ctx.moveTo(xx, 0); ctx.lineTo(xx, -600); ctx.stroke(); }
    ctx.strokeStyle = '#2a2a2e'; ctx.lineWidth = 10; for (const yy of [-120, -320]) { ctx.beginPath(); ctx.moveTo(side < 0 ? -140 : 140, yy); ctx.lineTo(side < 0 ? -140 + w * .8 : 140 - w * .8, yy); ctx.stroke(); }
    ctx.restore();
  }
  ctx.restore();
}

// ---- city wall + gate ----
function drawWall(ctx, x0, x1, by, h, gateX, gateOpen, o = {}) {
  const stone = o.stone || '#6d6a66';
  ctx.beginPath(); ctx.rect(x0, by - h, x1 - x0, h); const g = ctx.createLinearGradient(0, by - h, 0, by); g.addColorStop(0, shade(stone, .1)); g.addColorStop(1, shade(stone, -.3)); fillStroke(ctx, g, 7);
  ctx.strokeStyle = 'rgba(20,20,25,.4)'; ctx.lineWidth = 3;
  for (let yy = by - h + 40; yy < by; yy += 40) { ctx.beginPath(); ctx.moveTo(x0, yy); ctx.lineTo(x1, yy); ctx.stroke(); for (let xx = x0 + ((yy / 40) % 2 ? 0 : 35); xx < x1; xx += 70) { ctx.beginPath(); ctx.moveTo(xx, yy); ctx.lineTo(xx, yy - 40); ctx.stroke(); } }
  // crenellations
  for (let xx = x0; xx < x1; xx += 90) { ctx.beginPath(); ctx.rect(xx, by - h - 50, 55, 52); fillStroke(ctx, shade(stone, .05), 6); }
  if (gateX != null) {
    // towers
    for (const tx of [gateX - 300, gateX + 160]) { ctx.beginPath(); ctx.rect(tx, by - h - 180, 140, h + 180); fillStroke(ctx, shade(stone, -.05), 7); for (let xx = tx; xx < tx + 140; xx += 50) { ctx.beginPath(); ctx.rect(xx, by - h - 225, 32, 48); fillStroke(ctx, shade(stone, -.02), 5); } ctx.beginPath(); ctx.rect(tx + 58, by - h - 100, 22, 60); fillStroke(ctx, '#141118', 4); }
    // arch
    ctx.beginPath(); ctx.moveTo(gateX - 160, by); ctx.lineTo(gateX - 160, by - h * .55); ctx.quadraticCurveTo(gateX - 160, by - h * .95, gateX, by - h * .95); ctx.quadraticCurveTo(gateX + 160, by - h * .95, gateX + 160, by - h * .55); ctx.lineTo(gateX + 160, by); ctx.closePath();
    ctx.save(); ctx.fillStyle = o.inside || '#ffb35a'; ctx.fill(); ctx.clip();
    if (o.insideFn) o.insideFn(ctx);
    for (const side of [-1, 1]) {
      const w = 160 * (1 - gateOpen * .9);
      ctx.beginPath(); ctx.rect(side < 0 ? gateX - 160 : gateX + 160 - w, by - h, w, h); fillStroke(ctx, '#4a2e1c', 7);
      ctx.strokeStyle = 'rgba(0,0,0,.45)'; ctx.lineWidth = 4; for (let k = 1; k < 4; k++) { const xx = side < 0 ? gateX - 160 + w * k / 4 : gateX + 160 - w * k / 4; ctx.beginPath(); ctx.moveTo(xx, by); ctx.lineTo(xx, by - h); ctx.stroke(); }
      ctx.strokeStyle = '#26262b'; ctx.lineWidth = 12; for (const yy of [by - 80, by - h * .55]) { ctx.beginPath(); ctx.moveTo(side < 0 ? gateX - 160 : gateX + 160, yy); ctx.lineTo(side < 0 ? gateX - 160 + w * .85 : gateX + 160 - w * .85, yy); ctx.stroke(); }
    }
    ctx.restore();
    ctx.beginPath(); ctx.moveTo(gateX - 160, by); ctx.lineTo(gateX - 160, by - h * .55); ctx.quadraticCurveTo(gateX - 160, by - h * .95, gateX, by - h * .95); ctx.quadraticCurveTo(gateX + 160, by - h * .95, gateX + 160, by - h * .55); ctx.lineTo(gateX + 160, by); ctx.lineWidth = 8; ctx.strokeStyle = INK; ctx.stroke();
  }
}
function drawHut(ctx, x, by, s, seed) {
  ctx.save(); ctx.translate(x, by); ctx.scale(s, s);
  ctx.beginPath(); ctx.rect(-90, -110, 180, 110); fillStroke(ctx, '#6e5a44', 5);
  ctx.beginPath(); ctx.moveTo(-120, -100); ctx.lineTo(0, -230); ctx.lineTo(120, -100); ctx.closePath(); fillStroke(ctx, '#8a7a50', 5);
  ctx.strokeStyle = 'rgba(60,40,20,.5)'; ctx.lineWidth = 3; for (let k = -100; k < 110; k += 18) { ctx.beginPath(); ctx.moveTo(k, -104); ctx.lineTo(k * .2, -220); ctx.stroke(); }
  rr(ctx, -30, -80, 50, 80, 4); fillStroke(ctx, '#2a1e18', 4);
  ctx.restore();
}
function drawFire(ctx, x, y, s, t) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  glow(ctx, 0, -30, 300, 'rgba(255,140,50,.55)');
  for (const [a, b] of [[-30, 30], [30, -30]]) { ctx.beginPath(); ctx.moveTo(a, 0); ctx.lineTo(b, -14); ctx.lineWidth = 12; ctx.strokeStyle = '#3a2416'; ctx.stroke(); }
  for (let k = 0; k < 5; k++) { const ph = t * 6 + k * 1.7, hh = 50 + Math.sin(ph) * 14 + k * 4; ctx.beginPath(); ctx.moveTo(-22 + k * 10, 0); ctx.quadraticCurveTo(-30 + k * 12 + Math.sin(ph) * 8, -hh * .6, -10 + k * 6, -hh); ctx.quadraticCurveTo(k * 8, -hh * .4, 18 - k * 4, 0); ctx.fillStyle = ['#ff7a2a', '#ffb33a', '#ffd86a', '#ff9a30', '#fff0a0'][k]; ctx.fill(); }
  ctx.restore();
}

// ---- interior pieces ----
function drawRoom(ctx, o = {}) { // back wall with timber + window
  const wall = o.wall || '#5a4636';
  ctx.fillStyle = vgrad(ctx, -1400, 600, [[0, shade(wall, -.4)], [1, wall]]); ctx.fillRect(-1600, -1500, 3200, 2100);
  ctx.strokeStyle = 'rgba(20,12,8,.55)'; ctx.lineWidth = 3;
  for (let y = -1400; y < 0; y += 54) { ctx.beginPath(); ctx.moveTo(-1600, y); ctx.lineTo(1600, y); ctx.stroke(); for (let x = -1600 + ((y / 54) % 2 ? 0 : 60); x < 1600; x += 120) { ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x, y + 54); ctx.stroke(); } }
  ctx.strokeStyle = '#2a1a12'; ctx.lineWidth = 34; for (const x of [-900, 900]) { ctx.beginPath(); ctx.moveTo(x, -1500); ctx.lineTo(x, 0); ctx.stroke(); }
  ctx.beginPath(); ctx.moveTo(-1600, -1100); ctx.lineTo(1600, -1100); ctx.stroke();
  if (o.window !== false) {
    const wx = o.winX || 420, wy = o.winY || -820;
    ctx.beginPath(); ctx.moveTo(wx - 120, wy + 260); ctx.lineTo(wx - 120, wy); ctx.arc(wx, wy, 120, Math.PI, 0); ctx.lineTo(wx + 120, wy + 260); ctx.closePath();
    ctx.fillStyle = o.winCol || '#1a2a50'; ctx.fill(); fillStroke(ctx, null, 10);
    if (o.moon !== false) { ell(ctx, wx + 30, wy + 30, 40, 40); ctx.fillStyle = '#f2e2b8'; ctx.fill(); glow(ctx, wx + 30, wy + 30, 200, 'rgba(180,200,255,.2)'); }
    ctx.strokeStyle = INK; ctx.lineWidth = 8; ctx.beginPath(); ctx.moveTo(wx, wy - 120); ctx.lineTo(wx, wy + 260); ctx.moveTo(wx - 120, wy + 110); ctx.lineTo(wx + 120, wy + 110); ctx.stroke();
  }
  // floor
  ctx.fillStyle = vgrad(ctx, 0, 900, [[0, shade(o.floor || '#4a3424', -.2)], [1, shade(o.floor || '#4a3424', -.6)]]); ctx.fillRect(-1600, 0, 3200, 1200);
  ctx.strokeStyle = 'rgba(0,0,0,.35)'; ctx.lineWidth = 3; for (let x = -1600; x < 1600; x += 140) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x * 1.6, 1200); ctx.stroke(); }
  ctx.beginPath(); ctx.moveTo(-1600, 0); ctx.lineTo(1600, 0); ctx.lineWidth = 8; ctx.strokeStyle = INK; ctx.stroke();
}
function drawTable(ctx, x, y, w, o = {}) {
  ctx.beginPath(); ctx.rect(x - w / 2, y - 30, w, 34); fillStroke(ctx, o.col || '#6b4428', 6);
  ctx.fillStyle = 'rgba(0,0,0,.25)'; ctx.fillRect(x - w / 2 + 4, y, w - 8, 12);
  for (const lx of [x - w / 2 + 40, x + w / 2 - 60]) { ctx.beginPath(); ctx.rect(lx, y + 4, 20, 190); fillStroke(ctx, shade(o.col || '#6b4428', -.2), 5); }
  if (o.cloth) { ctx.beginPath(); ctx.moveTo(x - w / 2 - 10, y - 30); ctx.lineTo(x + w / 2 + 10, y - 30); ctx.lineTo(x + w / 2 + 20, y + 60); ctx.quadraticCurveTo(x, y + 80, x - w / 2 - 20, y + 60); ctx.closePath(); fillStroke(ctx, o.cloth, 5); }
}
function drawBed(ctx, x, y, s) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  ctx.beginPath(); ctx.rect(-320, -260, 40, 300); fillStroke(ctx, '#5a3a22', 6);
  ctx.beginPath(); ctx.rect(280, -170, 40, 210); fillStroke(ctx, '#5a3a22', 6);
  ctx.beginPath(); ctx.rect(-290, -110, 580, 80); fillStroke(ctx, '#6b4428', 6);
  ctx.beginPath(); ctx.moveTo(-280, -110); ctx.quadraticCurveTo(-290, -170, -250, -160); ctx.lineTo(270, -150); ctx.quadraticCurveTo(300, -130, 285, -110); ctx.closePath(); fillStroke(ctx, '#e6dcc6', 5);
  ell(ctx, -210, -170, 70, 30); fillStroke(ctx, '#f2ead8', 5);
  ctx.restore();
}
function drawHumours(ctx, x, y, r, rot) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot);
  const Q = [['Blood', '#b3262a'], ['Yellow Bile', '#d8a72f'], ['Black Bile', '#2a2a2e'], ['Phlegm', '#9ab8c8']];
  Q.forEach(([n, c], i) => {
    ctx.beginPath(); ctx.moveTo(0, 0); ctx.arc(0, 0, r, i * Math.PI / 2, (i + 1) * Math.PI / 2); ctx.closePath(); fillStroke(ctx, c, 6);
    ctx.save(); ctx.rotate(i * Math.PI / 2 + Math.PI / 4); ctx.fillStyle = i === 2 ? '#e8dcc0' : INK; ctx.font = `${r * .13}px ${FONTS.fellsc}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(n, r * .58, 0); ctx.restore();
  });
  ell(ctx, 0, 0, r * .18, r * .18); fillStroke(ctx, '#e8d3a3', 5);
  ctx.restore();
}
function drawGear(ctx, x, y, r, teeth, rot, col = '#8a6a3a') {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.beginPath();
  for (let k = 0; k < teeth * 2; k++) { const a = k * Math.PI / teeth, rr2 = k % 2 ? r : r * 1.14; ctx.lineTo(Math.cos(a - .08) * rr2, Math.sin(a - .08) * rr2); ctx.lineTo(Math.cos(a + .08) * rr2, Math.sin(a + .08) * rr2); }
  ctx.closePath(); const g = ctx.createRadialGradient(-r * .3, -r * .3, r * .1, 0, 0, r * 1.1); g.addColorStop(0, shade(col, .3)); g.addColorStop(1, shade(col, -.3)); fillStroke(ctx, g, 6);
  ell(ctx, 0, 0, r * .62, r * .62); ctx.fillStyle = 'rgba(0,0,0,.35)'; ctx.fill();
  for (let k = 0; k < 4; k++) { ctx.save(); ctx.rotate(k * Math.PI / 2); ctx.beginPath(); ctx.rect(-r * .07, 0, r * .14, r * .62); fillStroke(ctx, shade(col, -.1), 4); ctx.restore(); }
  ell(ctx, 0, 0, r * .16, r * .16); fillStroke(ctx, shade(col, .2), 4);
  ctx.restore();
}
function drawHourglass(ctx, x, y, s, fill, t) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  for (const yy of [-150, 150]) { rr(ctx, -110, yy - 16, 220, 32, 8); fillStroke(ctx, '#6b4428', 5); }
  for (const xx of [-95, 95]) { ctx.beginPath(); ctx.rect(xx - 8, -140, 16, 280); fillStroke(ctx, '#5a3a22', 4); }
  ctx.beginPath(); ctx.moveTo(-75, -134); ctx.quadraticCurveTo(-70, -30, -8, 0); ctx.quadraticCurveTo(-70, 30, -75, 134); ctx.lineTo(75, 134); ctx.quadraticCurveTo(70, 30, 8, 0); ctx.quadraticCurveTo(70, -30, 75, -134); ctx.closePath();
  ctx.fillStyle = 'rgba(200,230,255,.18)'; ctx.fill();
  ctx.save(); ctx.clip(); ctx.fillStyle = '#e8b85a';
  const top = -134 + (1 - fill) * 0 + fill * 120; ctx.fillRect(-80, -134 + 134 * fill * .9 + 0, 160, 134 - 134 * fill * .9 - 6);
  const bot = 134 - 120 * fill; ctx.beginPath(); ctx.moveTo(-75, 134); ctx.quadraticCurveTo(0, bot - 30, 75, 134); ctx.fill();
  ctx.fillRect(-3, 0, 6, 134); ctx.restore();
  ctx.beginPath(); ctx.moveTo(-75, -134); ctx.quadraticCurveTo(-70, -30, -8, 0); ctx.quadraticCurveTo(-70, 30, -75, 134); ctx.moveTo(75, 134); ctx.quadraticCurveTo(70, 30, 8, 0); ctx.quadraticCurveTo(70, -30, 75, -134); ctx.lineWidth = 6; ctx.strokeStyle = INK; ctx.stroke();
  ctx.restore();
}
function qmark(ctx, x, y, s, a) { ctx.save(); ctx.globalAlpha *= a; ctx.translate(x, y); ctx.scale(s, s); fancyText(ctx, '?', 0, 0, { size: 90, font: FONTS.goth, color: '#ffe6a0', strokeW: 10 }); ctx.restore(); }

// ---- typography helpers ----
function bigTitle(ctx, lines, t, tIn, o = {}) { // blackletter disease title, lines slam on staggered steps
  if (NOTEXT) return;
  const steps = o.steps || lines.map((_, i) => i * 3);
  lines.forEach((ln, i) => {
    const ti = tIn + steps[i] * S16, s = slam(t - ti, .24); if (!s) return;
    const size = (o.sizes || [])[i] || o.size || 220, y = (o.y || 560) + i * size * .92 + (o.dy ? o.dy(t) : 0);
    ctx.save(); ctx.translate(W / 2 + (o.x || 0), y); ctx.scale(s.s, s.s); ctx.rotate(s.rot + (o.tilt || -0.03) * (i % 2 ? -1 : 1)); ctx.globalAlpha *= s.a * (o.alpha == null ? 1 : o.alpha);
    // impact streak
    const k = clamp(1 - (t - ti) / .25);
    if (k > 0) { ctx.save(); ctx.globalAlpha *= k * .7; ctx.fillStyle = o.glow || 'rgba(255,40,30,.9)'; ctx.fillRect(-W, -size * .05, W * 2, size * .1); ctx.restore(); }
    fancyText(ctx, ln, 0, 0, { size, font: FONTS.goth, color: o.color || '#e83a2e', grad: o.grad, glow: o.glow || 'rgba(255,30,20,.85)', glowR: size * .35, strokeW: size * .1, track: o.track || 4 });
    ctx.restore();
  });
}
function yearStamp(ctx, str, t, tIn, x, y, o = {}) {
  if (NOTEXT) return;
  const lt = t - tIn; if (lt < 0) return;
  const p = E.out5(clamp(lt / .18)), s = lerp(2.4, 1, p);
  ctx.save(); ctx.translate(x, y); ctx.rotate(o.rot || -.09); ctx.scale(s, s); ctx.globalAlpha *= clamp(lt / .06) * (o.alpha == null ? 1 : o.alpha);
  const size = o.size || 150, w = measure(ctx, str, { size, font: FONTS.cin, weight: 900, track: 6 }) + 70;
  ctx.strokeStyle = o.color || '#e8d6a8'; ctx.lineWidth = 9; rr(ctx, -w / 2, -size * .62, w, size * 1.24, 12); ctx.stroke();
  ctx.lineWidth = 3; rr(ctx, -w / 2 + 12, -size * .62 + 12, w - 24, size * 1.24 - 24, 8); ctx.stroke();
  fancyText(ctx, str, 0, size * .04, { size, font: FONTS.cin, weight: 900, color: o.color || '#e8d6a8', strokeW: 0, track: 6, glow: o.glow });
  if (o.sub) fancyText(ctx, o.sub, 0, size * .95, { size: size * .3, font: FONTS.fell, color: o.color || '#e8d6a8', strokeW: size * .04, track: 8 });
  ctx.restore();
}
function subLine(ctx, str, t, tIn, tOut, y, o = {}) { // elegant italic subtitle
  if (NOTEXT) return;
  if (t < tIn || t > tOut + .3) return;
  const a = clamp((t - tIn) / .25) * (1 - clamp((t - tOut) / .3));
  ctx.save(); ctx.globalAlpha *= a; const dy = (1 - E.out(clamp((t - tIn) / .35))) * 30;
  fancyText(ctx, str, W / 2, y + dy, { size: o.size || 78, font: o.font || FONTS.fell, color: o.color || '#f3e6c8', strokeW: (o.size || 78) * .12, glow: o.glow, track: o.track || 1 });
  ctx.restore();
}
