// ---------- cached environments ----------
const ENV = {};
function tintLayer(c, col, a, mode = 'multiply') {
  const g = c.getContext('2d'); g.save(); g.globalCompositeOperation = 'source-atop'; g.globalAlpha = 1;
  const tmp = mkCanvas(c.width, c.height), tg = tmp.getContext('2d'); tg.fillStyle = col; tg.fillRect(0, 0, c.width, c.height);
  g.globalCompositeOperation = mode; g.globalAlpha = a; g.drawImage(tmp, 0, 0);
  g.globalCompositeOperation = 'destination-in'; g.globalAlpha = 1; g.drawImage(c, 0, 0); // keep alpha
  g.restore();
}
function blurCopy(c, px) { const o = mkCanvas(c.width, c.height), g = o.getContext('2d'); g.filter = `blur(${px}px)`; g.drawImage(c, 0, 0); return o; }

// A street row: houses standing on y = baseY inside a canvas. Returns {c, wins:[{x,y,w,h,lit}], ox, oy}
function makeRow(seed, width, height, opts = {}) {
  const c = mkCanvas(width, height), g = c.getContext('2d');
  const r = rngFrom(seed);
  const baseY = height - (opts.pad || 10);
  let x = -30; const wins = []; const houses = [];
  while (x < width) {
    const w = (opts.wMin || 210) + r() * (opts.wVar || 120), h = (opts.hMin || 300) + r() * (opts.hVar || 220);
    if (opts.tower && x > opts.tower[0] - 100 && !houses.towerDone) {
      const info = drawTower(g, x + 20, baseY, opts.tower[1], opts.tower[2]);
      houses.towerDone = true; houses.tower = { x: x + 20, w: opts.tower[1], h: opts.tower[2], bell: info.bell };
      x += opts.tower[1] + 50; continue;
    }
    const hs = drawHouse(g, x, baseY, w, h, Math.floor(r() * 1e6));
    for (const wv of hs.wins) wins.push({ ...wv, lit: r() < (opts.litP || .55), ph: r() * 10 });
    houses.push(hs);
    x += w + 14 + r() * 26;
  }
  return { c, wins, baseY, houses, tower: houses.tower };
}
function makeSkyline(seed, width, height, col, opts = {}) {
  const c = mkCanvas(width, height), g = c.getContext('2d'); const r = rngFrom(seed);
  g.fillStyle = col; let x = 0;
  const lights = [];
  while (x < width) {
    const w = 60 + r() * 140, h = (opts.hMin || 120) + r() * (opts.hVar || 220);
    g.beginPath(); g.moveTo(x, height); g.lineTo(x, height - h); g.lineTo(x + w / 2, height - h - w * .6); g.lineTo(x + w, height - h); g.lineTo(x + w, height); g.closePath(); g.fill();
    if (r() < .12) { g.beginPath(); g.moveTo(x + w / 2 - 20, height - h - w * .3); g.lineTo(x + w / 2, height - h - w * .6 - 160 - r() * 140); g.lineTo(x + w / 2 + 20, height - h - w * .3); g.fill(); }
    for (let k = 0; k < 2; k++) if (r() < .5) lights.push([x + r() * w * .8 + 6, height - h * r() * .8 - 10]);
    x += w - 8;
  }
  return { c, lights };
}
function drawWins(ctx, wins, t, o = {}) {
  for (const w of wins) {
    let lit = w.lit; if (o.litFn) lit = o.litFn(w);
    if (!lit || w.type === 'door') continue;
    const fl = .85 + Math.sin(t * 7 + w.ph) * .08 + Math.sin(t * 13 + w.ph * 2) * .05;
    const a = (typeof lit === 'number' ? lit : 1) * fl;
    ctx.save(); ctx.globalAlpha = a;
    const g = ctx.createLinearGradient(0, w.y, 0, w.y + w.h); g.addColorStop(0, o.c1 || '#ffe2a0'); g.addColorStop(1, o.c2 || '#ff9a3a');
    ctx.fillStyle = g; ctx.fillRect(w.x + 3, w.y + 3, w.w - 6, w.h - 6);
    ctx.strokeStyle = 'rgba(40,20,10,.8)'; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(w.x + w.w / 2, w.y); ctx.lineTo(w.x + w.w / 2, w.y + w.h); ctx.moveTo(w.x, w.y + w.h / 2); ctx.lineTo(w.x + w.w, w.y + w.h / 2); ctx.stroke();
    ctx.restore();
    glow(ctx, w.x + w.w / 2, w.y + w.h / 2, Math.max(w.w, w.h) * 1.6, o.glow || 'rgba(255,160,60,.35)', a);
  }
}

function buildEnvs() {
  // ---- TOWN (dusk/night) : main street row with bell tower
  const row = makeRow(11, 3600, 1500, { tower: [1500, 230, 900], litP: .6 });
  tintLayer(row.c, '#3b3f78', .55);
  tintLayer(row.c, '#ff6a3a', .10, 'soft-light');
  ENV.row = row;
  const back = makeRow(77, 3600, 1300, { wMin: 160, wVar: 90, hMin: 360, hVar: 300, litP: .35 });
  tintLayer(back.c, '#2a2850', .72);
  ENV.back = back; ENV.backBlur = blurCopy(back.c, 2.5);
  const sky1 = makeSkyline(3, 3600, 900, '#231a36', { hMin: 160, hVar: 260 }); ENV.sky1 = sky1; ENV.sky1Blur = blurCopy(sky1.c, 4);
  const ground = mkCanvas(3600, 1300); cobbles(ground.getContext('2d'), 0, 0, 3600, 1300, 5, '#6d6158'); tintLayer(ground, '#2e2f5a', .55); ENV.ground = ground;
  // ---- LEPROSY grey-teal versions
  const rowL = makeRow(31, 3600, 1500, { litP: .3 }); tintLayer(rowL.c, '#5d7f86', .62); ENV.rowL = rowL;
  const groundL = mkCanvas(3600, 1300); cobbles(groundL.getContext('2d'), 0, 0, 3600, 1300, 9, '#7a7d76'); tintLayer(groundL, '#4f6b70', .5); ENV.groundL = groundL;
}
