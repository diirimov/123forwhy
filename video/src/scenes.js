// ---------- shared scene pieces ----------
function streetBackdrop(ctx, t, cam, o = {}) {
  const sky = o.sky || [[0, '#0b0d24'], [.45, '#2b1a3c'], [.75, '#7a2d3a'], [1, '#c8553a']];
  ctx.save(); applyCam(ctx, cam, .05); drawSky(ctx, { y0: -1700, y1: 300, stops: sky }); ctx.restore();
  ctx.save(); applyCam(ctx, cam, .12);
  if (o.stars !== false) drawStars(ctx, 140, 7, .8);
  if (o.moon !== false) drawMoon(ctx, o.moonX || 260, o.moonY || -1050, o.moonR || 120, o.moonCol || '#f6dcb0', o.moonGlow || 'rgba(255,170,120,.28)');
  drawClouds(ctx, t, { y0: -1300, y1: -500, n: 9, col: o.cloudCol || '#3a2440', a: .55, seed: 3 });
  ctx.restore();
  ctx.save(); applyCam(ctx, cam, .3); ctx.drawImage(ENV.sky1Blur, -1800, -880 - 300); ctx.restore();
  // fog band
  ctx.save(); applyCam(ctx, cam, .45); ctx.fillStyle = vgrad(ctx, -700, -100, [[0, 'rgba(120,70,110,0)'], [1, o.fog1 || 'rgba(150,80,110,.45)']]); ctx.fillRect(-3000, -700, 6000, 800); ctx.restore();
  ctx.save(); applyCam(ctx, cam, .62); ctx.drawImage(ENV.backBlur, -1800, -1300 - 70); drawWins(ctx, ENV.back.wins.map(w => ({ ...w, x: w.x - 1800, y: w.y - 1370 })), t, { glow: 'rgba(255,140,60,.25)' }); ctx.restore();
  ctx.save(); applyCam(ctx, cam, .78); ctx.fillStyle = vgrad(ctx, -500, 0, [[0, 'rgba(60,40,80,0)'], [1, o.fog2 || 'rgba(70,45,90,.55)']]); ctx.fillRect(-3000, -500, 6000, 520); ctx.restore();
}
function streetMain(ctx, t, cam, o = {}) {
  const row = o.row || ENV.row;
  ctx.save(); applyCam(ctx, cam, 1);
  ctx.drawImage(row.c, -1800, -row.baseY);
  drawWins(ctx, row.wins.map(w => ({ ...w, x: w.x - 1800, y: w.y - row.baseY })), t, { litFn: o.litFn });
  ctx.drawImage(o.ground || ENV.ground, -1800, -12);
  // ground light pool / shadow gradient toward camera
  ctx.fillStyle = vgrad(ctx, -12, 1300, [[0, 'rgba(0,0,0,.35)'], [.1, 'rgba(0,0,0,0)'], [1, 'rgba(0,0,0,.6)']]); ctx.fillRect(-1800, -12, 3600, 1312);
  ctx.restore();
}
function rowWin(i, row = ENV.row) { const w = row.wins[i]; return { x: w.x - 1800, y: w.y - row.baseY, w: w.w, h: w.h }; }

// ---------- SCENES ----------
const SCENES = [];
function scene(t0, t1, fn, o = {}) { SCENES.push({ t0, t1, fn, ...o }); }

// S1 — bell tower & title (B1–B2)
scene(TB(1), TB(3), (ctx, t) => {
  const lt = t;
  const towerX = ENV.row.tower.x - 1800 + ENV.row.tower.w / 2, bellY = ENV.row.tower.bell[1] - ENV.row.baseY;
  const p = E.inOut(prog(lt, 0, 3.75));
  const cam = { x: lerp(towerX, towerX - 120, p), y: lerp(bellY + 60, -300, p), z: lerp(2.3, .78, p), r: lerp(-.06, .02, p) };
  const sh = shakeAt(t, KICKS.filter(k => k < TB(3)), 6, .1); cam.x += sh.x; cam.y += sh.y;
  cam.z *= 1 + kickEnv(t) * .015;
  streetBackdrop(ctx, t, cam);
  streetMain(ctx, t, cam);
  // bell swinging on every beat
  ctx.save(); applyCam(ctx, cam, 1);
  const ang = Math.sin((t / BEAT) * Math.PI) * .55;
  drawBell(ctx, towerX, bellY - 40, 1.2, ang);
  // bell shockwaves on kick
  const ke = kickEnv(t, .3);
  ctx.globalAlpha = ke * .6; ctx.strokeStyle = '#ffcf80'; ctx.lineWidth = 6;
  for (let k = 0; k < 2; k++) { ell(ctx, towerX, bellY + 20, 120 + (1 - ke) * 260 + k * 80, (120 + (1 - ke) * 260 + k * 80) * .6); ctx.stroke(); }
  ctx.globalAlpha = 1;
  // townsfolk panicking in the street
  for (let i = 0; i < 14; i++) {
    const f = townsfolk(i + 1), dir = i % 2 ? 1 : -1, depth = hash(i + 4);
    const sp = 260 + hash(i) * 160;
    const x = ((hash(i + 1) * 3000 + dir * t * sp) % 3000 + 3000) % 3000 - 1500;
    const y = 60 + depth * 360;
    const ph = t / (BEAT) * .5 + hash(i + 2);
    drawPerson(ctx, { x, y, s: (1.25 + depth * .8) * f.s, face: dir, pose: i % 3 === 0 ? posePanic(ph, t + i) : poseRun(ph), c: f.c, head: f.head, robe: f.robe, ex: { eyes: 'wide', mouth: i % 2 ? 'scream' : 'o', brow: 1 }, t });
  }
  ctx.restore();
  // title: "3" / "SCARIEST" / "DISEASES" on hook hits; "OF THE MIDDLE AGES" on B2
  const T0 = [TB(1, 0), TB(1, 3), TB(1, 6), TB(2, 0)];
  const words = [['3', 250, '#ffcf6a', 360], ['SCARIEST', 120, '#f6ead0', 520], ['DISEASES', 175, '#ff5a4a', 665], ['OF THE MIDDLE AGES', 74, '#f6ead0', 805]];
  words.forEach(([wd, size, col, y], i) => {
    const s = slam(t - T0[i], .2); if (!s) return;
    const drift = (t - T0[i]) * 8;
    ctx.save(); ctx.translate(W / 2, y + (i === 0 ? -40 : 0) - drift * .3); ctx.scale(s.s, s.s); ctx.rotate(s.rot * .4 + (i === 1 ? -.03 : i === 2 ? .025 : 0)); ctx.globalAlpha = s.a;
    fancyText(ctx, wd, 0, 0, { size, weight: 900, font: i === 2 ? FONTS.goth : FONTS.cin, color: col, glow: i === 2 ? 'rgba(255,40,30,.8)' : 'rgba(255,170,80,.5)', glowR: 40, track: i === 3 ? 6 : 3, strokeW: size * .13 });
    ctx.restore();
  });
}, { post: { vig: .55 } });
