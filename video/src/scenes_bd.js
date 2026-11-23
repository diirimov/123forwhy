// ---------- disease vignettes (reused in hook, montage, finale) ----------
function vigBD(ctx, t, o = {}) {
  const k = o.zoom || 1;
  ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(k, k); ctx.rotate(o.rot || 0); ctx.translate(-W / 2, -H / 2);
  ctx.fillStyle = vgrad(ctx, 0, H, [[0, '#14040a'], [.5, '#5a0d16'], [1, '#120306']]); ctx.fillRect(-400, -400, W + 800, H + 800);
  drawMoon(ctx, W / 2, 620, 300, '#d8452e', 'rgba(255,60,30,.35)');
  drawClouds(ctx, t, { y0: 300, y1: 900, n: 6, col: '#240810', a: .7, seed: 8 });
  drawDoctor(ctx, { x: W / 2, y: 1640, s: 2.25, t, ph: 0, turn: Math.sin(t * 1.5) * .15, eyeGlow: 1, lamp: .7 });
  for (let i = 0; i < 4; i++) drawRat(ctx, ((i * 300 + t * 520) % 1500) - 200, 1720 + i % 2 * 70, 1.4, 1, t * 4 + i * .3, t, {});
  ctx.fillStyle = vgrad(ctx, 1500, H, [[0, 'rgba(60,0,10,0)'], [1, 'rgba(40,0,6,.9)']]); ctx.fillRect(-400, 1500, W + 800, 800);
  ctx.restore();
}
function vigLEP(ctx, t, o = {}) {
  const k = o.zoom || 1;
  ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(k, k); ctx.rotate(o.rot || 0); ctx.translate(-W / 2, -H / 2);
  ctx.fillStyle = vgrad(ctx, 0, H, [[0, '#0d1a1e'], [.55, '#3f6b6c'], [1, '#0b1416']]); ctx.fillRect(-400, -400, W + 800, H + 800);
  drawClouds(ctx, t, { y0: 500, y1: 1200, n: 8, col: '#a9c9c2', a: .18, seed: 21, speed: 1.5 });
  // ripples from the clapper
  const ke = beatPhase(t);
  ctx.strokeStyle = 'rgba(200,240,230,.5)'; ctx.lineWidth = 5;
  for (let r = 0; r < 3; r++) { ctx.globalAlpha = (1 - ((ke + r / 3) % 1)) * .6; ell(ctx, 650, 1060, 60 + ((ke + r / 3) % 1) * 520, (60 + ((ke + r / 3) % 1) * 520) * .9); ctx.stroke(); }
  ctx.globalAlpha = 1;
  drawPerson(ctx, { x: W / 2 - 60, y: 1620, s: 3.6, face: 1, pose: { lean: .08, bob: bounce(t, 4), lt: [.1, .05], rt: [-.1, .1], la: [2.3 + Math.sin(t * TAU / BEAT) * .2, .5], ra: [.3, .5] }, c: { tunic: '#6f7a78', hood: '#55605e', legs: '#3a3f40', skin: '#d8c4ae' }, head: 'hood', robe: true, ex: { eyes: 'sick', mouth: 'frown', brow: 1 }, t, hold: clapper, shadow: false });
  ctx.fillStyle = vgrad(ctx, 1300, H, [[0, 'rgba(180,220,210,0)'], [1, 'rgba(170,210,200,.55)']]); ctx.fillRect(-400, 1300, W + 800, 900);
  ctx.restore();
}
function vigSW(ctx, t, o = {}) {
  const k = o.zoom || 1;
  ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(k, k); ctx.rotate(o.rot || 0); ctx.translate(-W / 2, -H / 2);
  ctx.fillStyle = vgrad(ctx, 0, H, [[0, '#2a1004'], [.5, '#b5541a'], [1, '#2a0d04']]); ctx.fillRect(-400, -400, W + 800, H + 800);
  ctx.save(); ctx.globalAlpha = .25; ctx.translate(W / 2, 900); ctx.rotate(t * .3);
  for (let i = 0; i < 16; i++) { ctx.rotate(TAU / 16); ctx.fillStyle = i % 2 ? '#ffcf6a' : '#ff8a2a'; ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(-90, -1400); ctx.lineTo(90, -1400); ctx.fill(); }
  ctx.restore();
  drawClock(ctx, W / 2, 470, 250, t * 4, t * 24, t);
  drawPerson(ctx, { x: W / 2 - 110, y: 2520, s: 6.0, face: 1, pose: { lean: 0, bob: 0, lt: [0, 0], rt: [0, 0], la: [.2, .3], ra: [.2, .3] }, c: { tunic: '#7a2a2a', skin: '#f0b890' }, head: 'hair', ex: { eyes: 'wide', mouth: 'grit', brow: 1.2, look: [.6, -.2] }, sweat: 1, flush: .8, t: t * 1.8, shadow: false });
  ctx.restore();
}
function numeral(ctx, str, x, y, size, a = 1) { ctx.save(); ctx.globalAlpha *= a; fancyText(ctx, str, x, y, { size, font: FONTS.goth, color: '#f6ead0', glow: 'rgba(0,0,0,.8)', strokeW: size * .1 }); ctx.restore(); }

// S2 — three flashes + triptych (B3)
scene(TB(3), TB(4), (ctx, t) => {
  const hits = [TB(3, 0), TB(3, 4), TB(3, 8), TB(3, 12)];
  let i = 0; for (let k = 0; k < 4; k++) if (t >= hits[k]) i = k;
  const lt = t - hits[i];
  const pop = 1.12 - .12 * E.out5(clamp(lt / .14));
  if (i < 3) {
    [vigBD, vigLEP, vigSW][i](ctx, t, { zoom: pop + lt * .12, rot: (i - 1) * .02 });
    numeral(ctx, ['I', 'II', 'III'][i], W / 2, 330, 260, clamp(lt / .06));
  } else {
    const fns = [vigBD, vigLEP, vigSW];
    for (let k = 0; k < 3; k++) {
      const d = clamp((lt - k * .05) / .16), off = (1 - E.out5(d)) * (k % 2 ? -1 : 1) * H;
      ctx.save(); ctx.beginPath(); ctx.rect(k * 360, 0, 360, H); ctx.clip(); ctx.translate(0, off);
      ctx.translate(k * 360 - 360, 0); fns[k](ctx, t, { zoom: 1 + lt * .1 }); ctx.restore();
      ctx.save(); ctx.translate(0, off); numeral(ctx, ['I', 'II', 'III'][k], k * 360 + 180, 330, 170); ctx.restore();
    }
    ctx.fillStyle = INK; ctx.fillRect(357, 0, 8, H); ctx.fillRect(717, 0, 8, H);
  }
  // white-hot impact frame edge
  const f = clamp(1 - lt / .08); if (f > 0) { ctx.fillStyle = `rgba(255,230,200,${f * .35})`; ctx.fillRect(0, 0, W, H); }
}, { post: { vig: .5 } });

// S3 — crowd rushes at camera, shutters slam, camera dives into a dark doorway (B4)
const S3_SHUT = (() => null)();
scene(TB(4), TB(5), (ctx, t) => {
  const lt = t - TB(4);
  const dive = E.in(prog(t, TB(4, 8), TB(5)));
  const door = { x: 140, y: -150 };
  const cam = { x: lerp(60, door.x, dive), y: lerp(-420, door.y, dive), z: lerp(.95, 9, dive) * (1 + kickEnv(t) * .02), r: lerp(.02, -.15, dive) };
  const sh = shakeAt(t, [TB(4, 0), TB(4, 3), TB(4, 6)], 10, .08); cam.x += sh.x; cam.y += sh.y;
  streetBackdrop(ctx, t, cam);
  const shutT = [TB(4, 0), TB(4, 3), TB(4, 6)];
  const shutWins = S3wins();
  streetMain(ctx, t, cam, { litFn: w => { const j = shutWins.findIndex(s => s.x === w.x - 1800 && s.y === w.y - ENV.row.baseY); if (j >= 0 && j < 3 && t > shutT[j] + .06) return false; return w.lit; } });
  ctx.save(); applyCam(ctx, cam, 1);
  shutWins.slice(0, 3).forEach((w, j) => { const p = prog(t, shutT[j] - .03, shutT[j] + .06); if (t < shutT[j] - .2) return; drawShutterPair(ctx, w.x, w.y, w.w, w.h, 1 - E.in(p)); });
  // dark doorway target
  ctx.fillStyle = '#05030a'; rr(ctx, door.x - 70, door.y - 170, 140, 340, 60); ctx.fill();
  // crowd rushing toward camera (front view), staggered
  const crowd = [];
  for (let i = 0; i < 16; i++) {
    const ti = (lt * .9 + hash(i * 3) * 1.2) % 1.6 / 1.6;
    crowd.push({ i, ti });
  }
  crowd.sort((a, b) => a.ti - b.ti).forEach(({ i, ti }) => {
    const f = townsfolk(i + 40);
    const y = lerp(10, 760, E.in(ti)), s = lerp(.6, 3.2, E.in(ti)), x = lerp((hash(i) - .5) * 1400, (hash(i) - .5) * 2600, ti) + 60;
    drawPerson(ctx, { x, y, s, view: 'front', pose: posePanic(lt / BEAT * .5 + hash(i), t + i), c: f.c, head: f.head, robe: f.robe, ex: { eyes: 'wide', mouth: i % 2 ? 'scream' : 'o', brow: 1.2 }, t });
  });
  ctx.restore();
  // darkness of the dive
  if (dive > 0) { ctx.fillStyle = `rgba(3,1,6,${E.in(dive)})`; ctx.fillRect(0, 0, W, H); }
}, { mb: (lt, t) => t > TB(4, 9) ? 4 : 1, post: { vig: .6 } });
let _S3W = null;
function S3wins() {
  if (_S3W) return _S3W;
  _S3W = ENV.row.wins.filter(w => w.type === 'win' && w.lit).map(w => ({ x: w.x - 1800, y: w.y - ENV.row.baseY, w: w.w, h: w.h }))
    .filter(w => w.x > -500 && w.x < 600 && w.y > -620 && w.y < -150).sort((a, b) => a.x - b.x);
  // spread choice: left, center, right
  if (_S3W.length >= 3) _S3W = [_S3W[0], _S3W[Math.floor(_S3W.length / 2)], _S3W[_S3W.length - 1]];
  return _S3W;
}

// S4 — harbor, galley arrives, rats run down the mooring rope (B5–B6)
scene(TB(5), TB(7), (ctx, t) => {
  const lt = t - TB(5), p = E.inOut(prog(lt, 0, 3.75));
  const cam = { x: lerp(-60, 160, p), y: lerp(-360, -160, p), z: lerp(.82, 1.12, p) * (1 + kickEnv(t) * .012), r: lerp(-.03, .02, p) };
  const sh = shakeAt(t, [TB(5), TB(6)], 12, .12); cam.x += sh.x; cam.y += sh.y;
  ctx.save(); applyCam(ctx, cam, .08); drawSky(ctx, { y0: -1800, y1: 0, stops: [[0, '#07060f'], [.6, '#2a0f1e'], [1, '#6a1d22']] }); ctx.restore();
  ctx.save(); applyCam(ctx, cam, .15); drawStars(ctx, 160, 12, .7); drawMoon(ctx, -260, -1080, 150, '#e8623e', 'rgba(255,80,40,.3)'); drawClouds(ctx, t, { y0: -1300, y1: -600, n: 8, col: '#2a0c18', a: .6, seed: 4 }); ctx.restore();
  ctx.save(); applyCam(ctx, cam, .4); ctx.drawImage(ENV.sky1Blur, -1800, -880 - 120); ctx.restore();
  ctx.save(); applyCam(ctx, cam, 1);
  drawSea(ctx, t, -140, 4000, 1400, -260);
  drawShip(ctx, lerp(-420, -260, E.out(prog(lt, 0, 2))), 40, 1.05, t);
  // dock
  ctx.save(); ctx.translate(0, 0);
  ctx.beginPath(); ctx.moveTo(140, 230); ctx.lineTo(2200, 160); ctx.lineTo(2200, 1400); ctx.lineTo(-200, 1400); ctx.closePath(); fillStroke(ctx, '#4a3424', 7);
  ctx.strokeStyle = 'rgba(0,0,0,.45)'; ctx.lineWidth = 4; for (let k = 0; k < 14; k++) { const y = 250 + k * 80; ctx.beginPath(); ctx.moveTo(140 - k * 25, y); ctx.lineTo(2200, y - 70); ctx.stroke(); }
  for (const px of [160, 520]) { rr(ctx, px - 30, 140, 60, 260, 10); fillStroke(ctx, '#5c4130', 6); }
  ctx.restore();
  // rope (ship deck -> post)
  const sx = lerp(-420, -260, E.out(prog(lt, 0, 2))) + 330, sy = -200 + Math.sin(t * 1.3) * 8, px = 160, py = 160;
  const ropeAt = u => [lerp(sx, px, u), lerp(sy, py, u) + Math.sin(u * Math.PI) * 70];
  ctx.beginPath(); for (let u = 0; u <= 1.001; u += .05) { const [x, y] = ropeAt(u); u === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y); }
  ctx.lineWidth = 12; ctx.strokeStyle = INK; ctx.stroke(); ctx.lineWidth = 6; ctx.strokeStyle = '#a8865a'; ctx.stroke();
  // rats on rope, then across the dock toward camera
  for (let i = 0; i < 9; i++) {
    const st = lt - .25 - i * .36; if (st < 0) continue;
    const ph = (st / S16) * .5;
    if (st < 1.0) { const u = st / 1.0, [x, y] = ropeAt(u); const [x2, y2] = ropeAt(Math.min(1, u + .02)); ctx.save(); ctx.translate(x, y - 6); ctx.rotate(Math.atan2(y2 - y, x2 - x)); drawRat(ctx, 0, 0, .55, 1, ph, t); ctx.restore(); }
    else { const v = st - 1.0; drawRat(ctx, px + v * 380 + i * 6, py + 40 + v * 330 + (i % 3) * 30 - Math.abs(Math.sin(ph * Math.PI)) * 14, .7 + v * .55, 1, ph, t); }
  }
  ctx.restore();
  ctx.fillStyle = vgrad(ctx, 0, 700, [[0, 'rgba(5,0,5,.7)'], [1, 'rgba(5,0,5,0)']]); ctx.fillRect(0, 0, W, 700);
  bigTitle(ctx, ['BLACK', 'DEATH'], t, TB(5), { size: 250, y: 420, steps: [0, 3], color: '#ee3b2c' });
  yearStamp(ctx, '1347', t, TB(6), W / 2, 960, { size: 120, sub: 'Messina, Sicily' });
}, { post: { vig: .6 } });

// S5 — low alley, rats & leaping fleas (B7–B8)
function alleyProj(X, Y, Z, cam) { const d = Math.max(30, Z - cam.z); const f = 900 / d; return [W / 2 + (X - cam.x) * f, cam.hy + (Y - cam.y) * f, f]; }
scene(TB(7), TB(9), (ctx, t) => {
  const lt = t - TB(7);
  const cz = lt * 260 + E.in(prog(t, TB(8, 8), TB(8, 14))) * 900;
  const cam = { x: Math.sin(lt * 1.3) * 20, y: -160 + Math.sin(lt * TAU / BEAT) * 4, z: cz, hy: 860 };
  ctx.save();
  const sh = shakeAt(t, KICKS.filter(k => k >= TB(7) && k < TB(9)), 5, .08); ctx.translate(sh.x, sh.y);
  ctx.translate(W / 2, H / 2); ctx.rotate(-.04 + Math.sin(lt * .8) * .02); ctx.translate(-W / 2, -H / 2);
  ctx.fillStyle = '#07050c'; ctx.fillRect(-200, -200, W + 400, H + 400);
  // far end: moonlit street opening
  const [fx0, fy0, ff] = alleyProj(-300, -900, 5200, cam), [fx1, fy1] = alleyProj(300, 0, 5200, cam);
  ctx.fillStyle = vgrad(ctx, fy0, fy1, [[0, '#2a3a70'], [1, '#8a6a9a']]); ctx.fillRect(fx0, fy0, fx1 - fx0, fy1 - fy0);
  glow(ctx, (fx0 + fx1) / 2, (fy0 + fy1) / 2, 400, 'rgba(150,170,255,.45)');
  // segments from far to near
  const seg = 260;
  const zStart = Math.floor(cam.z / seg) * seg;
  for (let Z = zStart + seg * 20; Z >= zStart; Z -= seg) {
    if (Z - cam.z < 40) continue;
    const id = Math.round(Z / seg);
    for (const side of [-1, 1]) {
      const X = side * 300;
      const a = alleyProj(X, 0, Z, cam), b = alleyProj(X, 0, Z + seg, cam), c = alleyProj(X, -1000, Z + seg, cam), d = alleyProj(X, -1000, Z, cam);
      const fog = clamp((Z - cam.z) / 5000);
      const base = hash(id * 3 + side) < .5 ? '#5d4a3e' : '#6e5a48';
      ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.lineTo(c[0], c[1]); ctx.lineTo(d[0], d[1]); ctx.closePath();
      ctx.fillStyle = mix(side < 0 ? base : mix(base, '#000000', .25), '#1a1530', fog * .85); ctx.fill();
      ctx.strokeStyle = 'rgba(0,0,0,.5)'; ctx.lineWidth = 2;
      for (let yy = -100; yy > -1000; yy -= 100) { const p1 = alleyProj(X, yy, Z, cam), p2 = alleyProj(X, yy, Z + seg, cam); ctx.beginPath(); ctx.moveTo(p1[0], p1[1]); ctx.lineTo(p2[0], p2[1]); ctx.stroke(); }
      ctx.lineWidth = 5; ctx.strokeStyle = 'rgba(10,6,8,.8)'; ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(d[0], d[1]); ctx.stroke();
      if (hash(id * 7 + side) < .45) { // window or door
        const isDoor = hash(id * 11 + side) < .4;
        const y0 = isDoor ? 0 : -520, y1 = isDoor ? -330 : -700;
        const w0 = alleyProj(X, y0, Z + seg * .3, cam), w1 = alleyProj(X, y0, Z + seg * .7, cam), w2 = alleyProj(X, y1, Z + seg * .7, cam), w3 = alleyProj(X, y1, Z + seg * .3, cam);
        ctx.beginPath(); ctx.moveTo(w0[0], w0[1]); ctx.lineTo(w1[0], w1[1]); ctx.lineTo(w2[0], w2[1]); ctx.lineTo(w3[0], w3[1]); ctx.closePath();
        const lit = !isDoor && hash(id * 13 + side) < .5;
        ctx.fillStyle = lit ? mix('#ffb04a', '#1a1530', fog) : '#120c10'; ctx.fill(); ctx.lineWidth = 3; ctx.strokeStyle = INK; ctx.stroke();
        if (lit) glow(ctx, (w0[0] + w2[0]) / 2, (w0[1] + w2[1]) / 2, 140 * w0[2], 'rgba(255,150,60,.5)', 1 - fog);
      }
    }
    // ground slab
    const g0 = alleyProj(-300, 0, Z, cam), g1 = alleyProj(300, 0, Z, cam), g2 = alleyProj(300, 0, Z + seg, cam), g3 = alleyProj(-300, 0, Z + seg, cam);
    ctx.beginPath(); ctx.moveTo(g0[0], g0[1]); ctx.lineTo(g1[0], g1[1]); ctx.lineTo(g2[0], g2[1]); ctx.lineTo(g3[0], g3[1]); ctx.closePath();
    ctx.fillStyle = mix(id % 2 ? '#3a3440' : '#332e3a', '#1a1530', clamp((Z - cam.z) / 5000) * .8); ctx.fill();
    ctx.strokeStyle = 'rgba(0,0,0,.4)'; ctx.lineWidth = 2; for (let k = -2; k <= 2; k++) { const q0 = alleyProj(k * 120, 0, Z, cam), q1 = alleyProj(k * 120, 0, Z + seg, cam); ctx.beginPath(); ctx.moveTo(q0[0], q0[1]); ctx.lineTo(q1[0], q1[1]); ctx.stroke(); }
    // rats & fleas living at this depth band
    for (let i = 0; i < 26; i++) {
      const rz = cam.z + 4600 - ((lt * (520 + hash(i) * 260) + hash(i + 1) * 4600) % 4600);
      if (rz < Z || rz >= Z + seg) continue;
      const rx = (hash(i + 2) - .5) * 460, pr = alleyProj(rx, 0, rz, cam);
      const ph = lt / S16 * .5 + hash(i);
      drawRat(ctx, pr[0], pr[1] - Math.abs(Math.sin(ph * Math.PI)) * 10 * pr[2], pr[2] * .9, rx > 0 ? -1 : 1, ph, t, { eyeGlow: 1 });
      // fleas jumping off this rat
      const nF = Math.floor(1 + prog(t, TB(7), TB(8, 14)) * 5);
      for (let k = 0; k < nF; k++) {
        const jp = (lt * (1.6 + hash(i * 5 + k) * 1.2) + hash(i * 9 + k)) % 1;
        const fx = rx + (hash(i * 3 + k) - .5) * 300 * jp, fy = -Math.sin(jp * Math.PI) * (180 + hash(k + i) * 200), fz = rz - jp * 500;
        const q = alleyProj(fx, fy, fz, cam); if (fz - cam.z < 60) continue;
        drawFlea(ctx, q[0], q[1], q[2] * 1.3, jp * 6, 1);
      }
    }
  }
  ctx.restore();
  // near foreground fog
  ctx.fillStyle = vgrad(ctx, 1200, H, [[0, 'rgba(10,8,20,0)'], [1, 'rgba(10,8,20,.85)']]); ctx.fillRect(0, 1200, W, H - 1200);
  caption(ctx, ['FLEAS RODE ON RATS.'], t, TB(7, 0) + .1, TB(8, 10), { y: 520, size: 84 });
  // fill swarm toward camera
  const sw = prog(t, TB(8, 8), TB(8, 14));
  for (let k = 0; k < Math.floor(sw * 60); k++) { const a = hash(k) * TAU, r = (sw * 1.4 - hash(k + 5) * .4) * 1300; if (r < 0) continue; drawFlea(ctx, W / 2 + Math.cos(a) * r, 860 + Math.sin(a) * r * 1.3, 1.5 + r / 300, a, 1); }
  // hard cut to darkness in the gap, single glowing flea
  if (t >= TB(8, 14)) { ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); drawFlea(ctx, W / 2, H / 2, 3 + (t - TB(8, 14)) * 8, .3, 1); }
}, { mb: (lt, t) => (t > TB(8, 8) && t < TB(8, 14)) ? 3 : 1, post: { vig: .7 } });

// S6 — DROP 1: map of Europe, plague front pulses on every kick (B9–B10)
let MAP = null;
function buildMap() {
  const MW = 1500, MH = Math.round(1500 / 1.11);
  const c = mkCanvas(MW, MH), g = c.getContext('2d');
  g.fillStyle = '#cdb27a'; g.fillRect(0, 0, MW, MH);
  // sea hatch
  g.strokeStyle = 'rgba(70,50,30,.25)'; g.lineWidth = 2; for (let y = 10; y < MH; y += 22) for (let x = (y / 22 % 2) * 30; x < MW; x += 60) { g.beginPath(); g.moveTo(x, y); g.quadraticCurveTo(x + 10, y - 6, x + 20, y); g.stroke(); }
  const land = mkCanvas(MW, MH), lg = land.getContext('2d');
  lg.fillStyle = '#000';
  for (const poly of EUROPE.polys) { lg.beginPath(); poly.forEach(([x, y], i) => i ? lg.lineTo(x * MW, y * MH) : lg.moveTo(x * MW, y * MH)); lg.closePath(); lg.fill(); }
  // land fill with parchment & outline
  g.save(); g.shadowColor = 'rgba(60,40,20,.6)'; g.shadowBlur = 18;
  for (const poly of EUROPE.polys) { g.beginPath(); poly.forEach(([x, y], i) => i ? g.lineTo(x * MW, y * MH) : g.moveTo(x * MW, y * MH)); g.closePath(); g.fillStyle = '#ecd9a8'; g.fill(); }
  g.restore();
  g.strokeStyle = '#3a2a1e'; g.lineWidth = 3;
  for (const poly of EUROPE.polys) { g.beginPath(); poly.forEach(([x, y], i) => i ? g.lineTo(x * MW, y * MH) : g.moveTo(x * MW, y * MH)); g.closePath(); g.stroke(); }
  // compass
  g.save(); g.translate(MW * .1, MH * .82); g.strokeStyle = '#3a2a1e'; g.lineWidth = 3; ell(g, 0, 0, 70, 70); g.stroke();
  for (let k = 0; k < 8; k++) { g.rotate(Math.PI / 4); g.beginPath(); g.moveTo(0, -(k % 2 ? 50 : 95)); g.lineTo(10, 0); g.lineTo(-10, 0); g.closePath(); g.fillStyle = k % 2 ? '#8a6a3a' : '#3a2a1e'; g.fill(); }
  g.restore();
  // arrival raster
  const RW = 375, RH = Math.round(375 / 1.11);
  const small = mkCanvas(RW, RH), sg = small.getContext('2d'); sg.drawImage(land, 0, 0, RW, RH);
  const mask = sg.getImageData(0, 0, RW, RH).data;
  const arr = new Float32Array(RW * RH);
  for (let y = 0; y < RH; y++) for (let x = 0; x < RW; x++) {
    const i = y * RW + x; if (mask[i * 4 + 3] < 100) { arr[i] = 9999; continue; }
    const u = x / RW, v = y / RH; let best = 9999;
    for (const [sx, sy, yr] of EUROPE.seeds) {
      let dx = u - sx, dy = (v - sy) / 1.11; let d = Math.sqrt(dx * dx + dy * dy);
      if (u > .62 && v < .45) d *= 2.2; // slow toward Russia
      best = Math.min(best, yr + d / .62);
    }
    arr[i] = best + (vnoise(u * 18 + 3) * vnoise(v * 18 + 7)) * .35 + vnoise(u * 40 + v * 33) * .08;
  }
  MAP = { c, MW, MH, RW, RH, arr, small, sctx: small.getContext('2d'), img: small.getContext('2d').createImageData(RW, RH) };
}
function mapYearAt(t) { // steps forward on every kick
  const ks = KICKS.filter(k => k >= TB(9) && k < TB(11));
  let y = 1347.25;
  for (const k of ks) y += .52 * E.out5(clamp((t - k) / .16));
  return y;
}
function drawMapSpread(ctx, year) {
  const { RW, RH, arr, img, sctx } = MAP, d = img.data;
  for (let i = 0; i < arr.length; i++) {
    const a = arr[i], o = i * 4;
    if (a > year) { d[o + 3] = 0; continue; }
    const edge = clamp(1 - (year - a) / .12);
    d[o] = lerp(70, 255, edge); d[o + 1] = lerp(6, 90, edge); d[o + 2] = lerp(10, 30, edge); d[o + 3] = lerp(215, 255, edge);
  }
  sctx.putImageData(img, 0, 0);
  ctx.save(); ctx.imageSmoothingEnabled = true; ctx.globalCompositeOperation = 'multiply'; ctx.drawImage(MAP.small, 0, 0, MAP.MW, MAP.MH); ctx.restore();
  ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.globalAlpha = .35; ctx.filter = 'blur(6px)'; ctx.drawImage(MAP.small, 0, 0, MAP.MW, MAP.MH); ctx.restore();
}
scene(TB(9), TB(11), (ctx, t) => {
  if (!MAP) buildMap();
  const lt = t - TB(9), p = E.out(prog(lt, 0, 3.5));
  const mc = EUROPE.cities.Messina;
  const cam = { x: lerp(mc[0] * MAP.MW, MAP.MW * .52, p), y: lerp(mc[1] * MAP.MH, MAP.MH * .5, p), z: lerp(2.6, .76, p) * (1 + kickEnv(t) * .025), r: lerp(-.08, .02, p) };
  const sh = shakeAt(t, [TB(9)], 30, .2); cam.x += sh.x; cam.y += sh.y;
  ctx.fillStyle = '#1a1008'; ctx.fillRect(0, 0, W, H);
  ctx.save(); applyCam(ctx, cam, 1);
  ctx.drawImage(MAP.c, 0, 0);
  const year = mapYearAt(t);
  drawMapSpread(ctx, year);
  // cities
  for (const [n, [x, y]] of Object.entries(EUROPE.cities)) {
    ell(ctx, x * MAP.MW, y * MAP.MH, 9, 9); fillStroke(ctx, '#2a1a10', 3);
    ctx.font = `28px ${FONTS.fellsc}`; ctx.fillStyle = '#2a1a10'; ctx.textAlign = 'left'; ctx.fillText(n, x * MAP.MW + 14, y * MAP.MH - 8);
  }
  // ships icons along routes
  ctx.restore();
  ctx.fillStyle = vgrad(ctx, 0, 520, [[0, 'rgba(15,5,2,.85)'], [1, 'rgba(15,5,2,0)']]); ctx.fillRect(0, 0, W, 520);
  // year counter
  const yr = Math.min(1351, Math.floor(year));
  const yp = sinceLast(t, KICKS.filter(k => k >= TB(9)));
  ctx.save(); ctx.translate(W / 2, 300); const ys = 1 + Math.exp(-yp / .08) * .12; ctx.scale(ys, ys);
  fancyText(ctx, String(yr), 0, 0, { size: 190, font: FONTS.cin, weight: 900, color: '#f6e2b0', glow: 'rgba(255,60,30,.7)', strokeW: 22, track: 8 });
  ctx.restore();
  caption(ctx, ['IT SPREAD FAST.'], t, TB(9) + .05, TB(10, 14), { y: 1380, size: 104 });
  const f = clamp(1 - lt / .12); if (f > 0) { ctx.fillStyle = `rgba(255,80,40,${f * .4})`; ctx.fillRect(0, 0, W, H); }
}, { mb: (lt) => lt < .5 ? 3 : 1, post: { vig: .55, paper: .45 } });

// S7 — streets empty, shutters slam, windows die (B11–B12)
scene(TB(11), TB(13), (ctx, t) => {
  const lt = t - TB(11), p = E.inOut(prog(lt, 0, 3.75));
  const cam = { x: lerp(-650, 250, p), y: -330 + Math.sin(lt * 2) * 10, z: .93 * (1 + kickEnv(t) * .015), r: .025 };
  const slams = [TB(11, 0), TB(11, 3), TB(11, 6), TB(12, 0), TB(12, 3), TB(12, 6)];
  const sh = shakeAt(t, slams, 9, .08); cam.x += sh.x; cam.y += sh.y;
  streetBackdrop(ctx, t, cam, { sky: [[0, '#070816'], [.5, '#21122e'], [.8, '#5a1a2a'], [1, '#8a2a2a']] });
  const sw = S7wins();
  streetMain(ctx, t, cam, { litFn: w => {
    const wx = w.x - 1800, wy = w.y - ENV.row.baseY;
    const j = sw.findIndex(s => s.x === wx && s.y === wy);
    if (j >= 0) return t < slams[j] + .05 ? w.lit : false;
    const off = TB(11) + hash(w.x * .37 + w.y) * 3.4; return w.lit && t < off;
  } });
  ctx.save(); applyCam(ctx, cam, 1);
  sw.forEach((w, j) => { if (t < slams[j] - .25) return; drawShutterPair(ctx, w.x, w.y, w.w, w.h, 1 - E.in(prog(t, slams[j] - .04, slams[j] + .05))); });
  // fleeing townsfolk (gone by B12)
  for (let i = 0; i < 12; i++) {
    const f = townsfolk(i + 70), dir = hash(i + 3) < .5 ? -1 : 1, d = hash(i + 9);
    const start = -900 + hash(i) * 1600 + cam.x * .3;
    const x = start + dir * lt * (520 + hash(i + 1) * 300), y = 80 + d * 300;
    drawPerson(ctx, { x, y, s: (1.2 + d * .7) * f.s, face: dir, pose: poseRun(lt / BEAT * .5 + hash(i)), c: f.c, head: f.head, robe: f.robe, ex: { eyes: 'wide', mouth: 'o', brow: 1 }, t });
  }
  // the dead-cart and bell ringer crossing slowly
  const cx = lerp(-1100, 700, lt / 3.75);
  drawCart(ctx, cx, 330, 1.25, -lt * 2.2, true);
  performanceT = t;
  drawPerson(ctx, { x: cx + 390, y: 360, s: 1.7, face: 1, pose: { ...poseWalk(lt / BEAT * .5, .8), la: [1.9 + Math.sin(t * 20) * .25, .3] }, c: { tunic: '#2b2a30', hood: '#1e1d22', legs: '#1b1a1f', skin: '#d8b89a' }, head: 'hood', robe: true, ex: { eyes: 'tired', mouth: 'flat', brow: .4 }, t, hold: handbell });
  // tumbling hat
  if (t > TB(12)) { const hp = t - TB(12); ctx.save(); ctx.translate(cam.x - 700 + hp * 700, 420 - Math.abs(Math.sin(hp * 6)) * 60); ctx.rotate(hp * 7); ell(ctx, 0, 0, 50, 12); fillStroke(ctx, '#5a3d2a', 5); ctx.beginPath(); ctx.moveTo(-22, -4); ctx.quadraticCurveTo(0, -46, 22, -4); fillStroke(ctx, '#6a4a32', 5); ctx.restore(); }
  ctx.restore();
  caption(ctx, ['CITIES EMPTIED.'], t, TB(12) + .02, TB(13) - .25, { y: 560, size: 110 });
}, { post: { vig: .62 } });
let _S7W = null;
function S7wins() {
  if (_S7W) return _S7W;
  const c = ENV.row.wins.filter(w => w.type === 'win' && w.lit).map(w => ({ x: w.x - 1800, y: w.y - ENV.row.baseY, w: w.w, h: w.h }))
    .filter(w => w.x > -1000 && w.x < 900 && w.y > -700 && w.y < -150).sort((a, b) => a.x - b.x);
  _S7W = [0, 1, 2, 3, 4, 5].map(k => c[Math.floor(k * (c.length - 1) / 5)]);
  return _S7W;
}

// S8 — plague doctor stalks through the fog (B13–B14)
scene(TB(13), TB(15), (ctx, t) => {
  if (!ENV.rowBlur) ENV.rowBlur = blurCopy(ENV.row.c, 7);
  const lt = t - TB(13), p = prog(lt, 0, 3.75);
  const cam = { x: Math.sin(lt * .7) * 40, y: -260 - p * 60, z: lerp(1.0, 1.18, E.inOut(p)) * (1 + kickEnv(t) * .02), r: -.03 + Math.sin(lt * .5) * .02 };
  ctx.save(); applyCam(ctx, cam, .05); drawSky(ctx, { y0: -1700, y1: 300, stops: [[0, '#05040a'], [.6, '#1d0b16'], [1, '#4a1420']] }); ctx.restore();
  ctx.save(); applyCam(ctx, cam, .15); drawMoon(ctx, 300, -1000, 110, '#d4503a', 'rgba(255,60,40,.25)'); ctx.restore();
  ctx.save(); applyCam(ctx, cam, .7); ctx.globalAlpha = .75; ctx.drawImage(ENV.rowBlur, -1800, -ENV.row.baseY - 40); ctx.globalAlpha = 1; ctx.restore();
  ctx.save(); applyCam(ctx, cam, 1);
  ctx.drawImage(ENV.ground, -1800, -12);
  ctx.fillStyle = vgrad(ctx, -900, 200, [[0, 'rgba(90,40,60,0)'], [1, 'rgba(110,60,80,.6)']]); ctx.fillRect(-2000, -900, 4000, 1100);
  // fog wisps behind
  for (let k = 0; k < 6; k++) { ctx.save(); ctx.globalAlpha = .22; ctx.fillStyle = '#c9a0b0'; ell(ctx, ((k * 500 + lt * 90) % 2600) - 1300, -40 + k * 30, 420, 60); ctx.fill(); ctx.restore(); }
  const dy = lerp(160, 380, p), ds = lerp(1.35, 2.05, p);
  const turnT = TB(14, 12);
  const turn = t < turnT ? .85 + Math.sin(lt * 2) * .05 : lerp(.85, 0, E.outBack(clamp((t - turnT) / .18)));
  const glowA = t < turnT ? .5 : 1 + Math.exp(-(t - turnT) / .2) * 1.5;
  drawDoctor(ctx, { x: Math.sin(lt * .6) * 30, y: dy, s: ds, t, ph: t < turnT ? lt / BEAT * .5 : turnT / BEAT * .5 - (turnT - TB(13)) * 0, turn, eyeGlow: glowA });
  // rats crossing foreground
  for (let i = 0; i < 4; i++) { const st = (lt * 1.1 + i * .27) % 1.6; drawRat(ctx, -900 + st * 1300, 560 + i * 40, 1.3 + i * .1, 1, st * 9, t); }
  ctx.restore();
  // near fog drifting
  for (let k = 0; k < 5; k++) { ctx.save(); ctx.globalAlpha = .28; ctx.filter = 'blur(20px)'; ctx.fillStyle = '#b48aa0'; ell(ctx, ((k * 420 - lt * 160) % 2000 + 2000) % 2000 - 400, 1500 + k * 80, 380, 90); ctx.fill(); ctx.restore(); }
  if (t > turnT) { const f = Math.exp(-(t - turnT) / .12) * .3; ctx.fillStyle = `rgba(255,40,30,${f})`; ctx.fillRect(0, 0, W, H); }
}, { post: { vig: .72 } });

// S9 — Europe was terrified: crowd before the cathedral (B15–B16)
scene(TB(15), TB(17), (ctx, t) => {
  const lt = t - TB(15), p = E.inOut(prog(lt, 0, 3.3));
  const cam = { x: Math.sin(lt * .6) * 30, y: lerp(120, -620, p), z: lerp(1.35, .72, p) * (1 + kickEnv(t) * .015), r: lerp(.04, -.01, p) };
  const slamT = TB(16, 12);
  const sh = shakeAt(t, [slamT], 26, .16); cam.x += sh.x; cam.y += sh.y;
  ctx.save(); applyCam(ctx, cam, .05); drawSky(ctx, { y0: -2000, y1: 200, stops: [[0, '#12030a'], [.5, '#5a0e16'], [.85, '#c0301e'], [1, '#e8642a']] }); ctx.restore();
  ctx.save(); applyCam(ctx, cam, .15); drawClouds(ctx, t, { y0: -1700, y1: -700, n: 10, col: '#3a0810', a: .65, seed: 31, speed: 2 }); ctx.restore();
  ctx.save(); applyCam(ctx, cam, .35); ctx.drawImage(ENV.sky1Blur, -1800, -880 - 140); ctx.restore();
  ctx.save(); applyCam(ctx, cam, 1);
  const doorOpen = t < slamT ? 1 : 1 - E.in(clamp((t - slamT) / .08));
  drawCathedral(ctx, 0, -40, .62, doorOpen);
  ctx.drawImage(ENV.ground, -1800, -50);
  ctx.fillStyle = vgrad(ctx, -50, 900, [[0, 'rgba(40,0,0,.3)'], [1, 'rgba(10,0,0,.8)']]); ctx.fillRect(-1800, -50, 3600, 950);
  // crowd (back view) in rows, swaying, some holding candles
  for (let row = 0; row < 4; row++) {
    for (let i = 0; i < 9; i++) {
      const id = row * 20 + i, f = townsfolk(id + 200);
      const x = (i - 4) * 210 + (row % 2) * 100 + (hash(id) - .5) * 60, y = 120 + row * 170;
      const sway = Math.sin((t / BEAT) * Math.PI + id) * .06;
      performanceT = t;
      drawPerson(ctx, { x, y, s: (1.25 + row * .32) * f.s, view: 'front', back: true, pose: { ...posePray(t), lean: sway, la: [2.2 + Math.sin(t * 3 + id) * .2, .3], ra: [2.0 + Math.sin(t * 3.3 + id) * .2, .4] }, c: f.c, head: f.head, robe: f.robe, t,
        hold: id % 3 === 0 ? (c2, hx, hy) => drawCandle(c2, hx, hy + 30, .45, t + id, 50) : null });
    }
  }
  ctx.restore();
  caption(ctx, ['EUROPE WAS', 'TERRIFIED.'], t, TB(15) + .05, TB(16, 11), { y: 520, size: 104 });
  if (t > slamT) { ctx.fillStyle = `rgba(0,0,0,${E.in(prog(t, slamT + .05, TB(17)))})`; ctx.fillRect(0, 0, W, H); }
}, { post: { vig: .6 } });
