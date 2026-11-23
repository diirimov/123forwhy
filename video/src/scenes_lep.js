// ---------- LEPROSY (B17–B28) ----------
const LEP_SKY = [[0, '#0c1518'], [.5, '#2c4446'], [.85, '#6f8f8a'], [1, '#a9c2b8']];
const WOOD = []; for (let b = 17; b <= 24; b++) for (const s of [0, 3, 6]) WOOD.push(TB(b, s));
const LEPER_C = { tunic: '#6f7a78', hood: '#55605e', legs: '#3a3f40', skin: '#d8c4ae' };
function leper(ctx, x, y, s, face, t, o = {}) {
  const hitAgo = sinceLast(t, WOOD);
  const raise = Math.exp(-hitAgo / .12);
  const pose = o.pose || poseWalk((t / BEAT) * .5, .55, .12);
  pose.la = [lerp(1.3, 2.4, raise), .5];
  drawPerson(ctx, { x, y, s, face, pose, c: LEPER_C, head: 'hood', robe: true, ex: o.ex || { eyes: 'sick', mouth: 'frown', brow: 1, look: [0, .4] }, t, hold: clapper, back: o.back, view: o.view, patches: o.patches });
  if (o.rings !== false && hitAgo < .6) {
    const hx = x + face * 60 * s, hy = y - 240 * s;
    ctx.save(); ctx.strokeStyle = 'rgba(210,245,235,.7)'; ctx.lineWidth = 4;
    for (let r = 0; r < 2; r++) { const k = clamp(hitAgo / .6 - r * .2); ctx.globalAlpha = (1 - k) * .8; ell(ctx, hx, hy, 30 * s + k * 160 * s, (30 * s + k * 160 * s) * .8); ctx.stroke(); }
    ctx.restore();
  }
}
function deadTree(ctx, x, y, s) {
  const br = (x0, y0, a, len, w, d) => {
    if (d > 6 || len < 8) return;
    const x1 = x0 + Math.sin(a) * len, y1 = y0 - Math.cos(a) * len;
    ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x1, y1); ctx.lineWidth = w; ctx.strokeStyle = '#141a1b'; ctx.lineCap = 'round'; ctx.stroke();
    br(x1, y1, a - .45 + hash(d * 7 + len) * .2, len * .72, w * .66, d + 1);
    br(x1, y1, a + .5 - hash(d * 3 + len) * .2, len * .68, w * .62, d + 1);
  };
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); br(0, 0, -.05, 220, 34, 0); ctx.restore();
}
function grade(ctx, col, a, mode = 'color') { ctx.save(); ctx.globalCompositeOperation = mode; ctx.globalAlpha = a; ctx.fillStyle = col; ctx.fillRect(0, 0, W, H); ctx.restore(); }
function mist(ctx, t, y, col, a, n = 6, sp = 60, seed = 1) {
  ctx.save(); ctx.filter = 'blur(24px)'; ctx.fillStyle = col;
  for (let k = 0; k < n; k++) { ctx.globalAlpha = a * (.6 + hash(k + seed) * .4); ell(ctx, ((k * 470 + t * sp * (1 + hash(k + seed * 3))) % 2400) - 700, y + (hash(k + seed * 5) - .5) * 160, 420, 70); ctx.fill(); }
  ctx.restore();
}

// S10 — lone figure in the mist, title (B17–B18)
scene(TB(17), TB(19), (ctx, t) => {
  const lt = t - TB(17), p = prog(lt, 0, 3.75);
  const lx = lerp(260, -180, p);
  const cam = { x: lx * .6 + 40, y: -420, z: lerp(.9, 1.05, E.inOut(p)), r: -.015 };
  ctx.save(); applyCam(ctx, cam, .05); drawSky(ctx, { y0: -1700, y1: 200, stops: LEP_SKY }); ctx.restore();
  ctx.save(); applyCam(ctx, cam, .12); glow(ctx, -200, -950, 500, 'rgba(220,240,230,.25)'); drawClouds(ctx, t, { y0: -1400, y1: -500, n: 9, col: '#8fa9a3', a: .25, seed: 41 }); ctx.restore();
  ctx.save(); applyCam(ctx, cam, .3);
  ctx.fillStyle = '#2f4446'; drawWall(ctx, -1500, 1500, -120, 220, null, 0, { stone: '#3d5254' });
  ctx.drawImage(ENV.sky1Blur, -1800, -880 - 320, 3600, 900); ctx.restore();
  ctx.save(); applyCam(ctx, cam, .55); mist(ctx, t, -200, '#cfe3dc', .35, 7, 40, 3); ctx.restore();
  ctx.save(); applyCam(ctx, cam, 1);
  ctx.fillStyle = vgrad(ctx, -40, 900, [[0, '#4a5d58'], [1, '#141c1c']]); ctx.fillRect(-2500, -40, 5000, 1400);
  ctx.beginPath(); ctx.moveTo(-2000, 60); ctx.quadraticCurveTo(0, -10, 2000, 120); ctx.lineTo(2000, 300); ctx.quadraticCurveTo(0, 200, -2000, 330); ctx.closePath(); ctx.fillStyle = '#6a7a70'; ctx.fill();
  deadTree(ctx, 620, 40, 1.3);
  leper(ctx, lx, 260, 2.6, -1, t);
  ctx.restore();
  ctx.save(); applyCam(ctx, cam, 1.4); mist(ctx, t, 520, '#d8ebe4', .4, 6, 90, 7); ctx.restore();
  bigTitle(ctx, ['LEPROSY'], t, TB(17), { size: 250, y: 470, color: '#cfeee2', glow: 'rgba(120,230,200,.75)', tilt: -.02 });
  subLine(ctx, 'Feared for centuries', t, TB(18, 2), TB(19) - .15, 680, { size: 92, color: '#e6f2ec', glow: 'rgba(0,0,0,.7)' });
}, { post: { vig: .6, grain: .26 } });

// S11 — first signs: pale numb patches (B19–B20)
function drawHand(ctx, x, y, s, rot, patch, t) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
  const skin = '#e3b998';
  // fingers
  [[-62, -150, -.16, 110], [-20, -175, -.05, 130], [24, -170, .05, 124], [62, -140, .16, 100]].forEach(([fx, fy, a, L]) => {
    ctx.save(); ctx.translate(fx, -40); ctx.rotate(a + Math.sin(t * 2 + fx) * .02); rr(ctx, -19, -L, 38, L + 20, 19); fillStroke(ctx, skin, 6);
    rr(ctx, -11, -L + 6, 22, 22, 8); ctx.fillStyle = '#f2d6c0'; ctx.fill(); ctx.restore();
  });
  ctx.beginPath(); ctx.moveTo(-90, -50); ctx.quadraticCurveTo(-100, 90, -40, 140); ctx.lineTo(60, 140); ctx.quadraticCurveTo(100, 80, 90, -50); ctx.quadraticCurveTo(0, -80, -90, -50); ctx.closePath();
  const g = ctx.createLinearGradient(-90, 0, 90, 0); g.addColorStop(0, shade(skin, -.12)); g.addColorStop(1, shade(skin, .06)); fillStroke(ctx, g, 6);
  ctx.save(); ctx.translate(-88, 30); ctx.rotate(-.9); rr(ctx, -20, -90, 40, 110, 20); fillStroke(ctx, skin, 6); ctx.restore();
  rr(ctx, -70, 120, 140, 200, 30); fillStroke(ctx, '#5a3a2a', 6); // sleeve
  if (patch > 0) {
    ctx.save(); ctx.globalAlpha = patch;
    for (const [px, py, rx, ry] of [[-20, 10, 38, 26], [36, 60, 22, 16], [-48, 80, 16, 12], [10, -150, 12, 16]]) {
      ctx.beginPath(); for (let k = 0; k <= 12; k++) { const a = k / 12 * TAU, rr2 = 1 + vnoise(k * 1.7 + px) * .25; ctx.lineTo(px + Math.cos(a) * rx * rr2, py + Math.sin(a) * ry * rr2); }
      ctx.closePath(); ctx.fillStyle = '#efe3cf'; ctx.fill(); ctx.lineWidth = 2.5; ctx.strokeStyle = 'rgba(160,120,100,.6)'; ctx.stroke();
    }
    ctx.restore();
  }
  ctx.restore();
}
scene(TB(19), TB(21), (ctx, t) => {
  const lt = t - TB(19);
  const ans = [2, 3, 6, 8, 9, 10, 12, 14].map(s => TB(20, s));
  const toFace = E.inOut(prog(t, TB(20) - .25, TB(20) + .35));
  const cam = { x: lerp(-40, -60, toFace), y: lerp(-300, -520, toFace), z: lerp(1.25, 1.5, toFace) + lt * .02, r: lerp(.03, -.02, toFace) };
  ctx.save(); applyCam(ctx, cam, 1);
  drawRoom(ctx, { wall: '#3a3a3a', winX: 520, winY: -1300, winCol: '#16263a' });
  grade(ctx, '#2a5a5a', .0);
  drawCandle(ctx, -420, -260, 1.3, t, 120);
  drawTable(ctx, 0, -230, 900, { col: '#4a3224' });
  // basin with water + ripples on answer notes
  ell(ctx, 40, -270, 200, 50); fillStroke(ctx, '#8a7a6a', 6); ell(ctx, 40, -278, 172, 38); ctx.fillStyle = '#3f5a62'; ctx.fill();
  ctx.save(); ell(ctx, 40, -278, 172, 38); ctx.clip(); ctx.strokeStyle = 'rgba(210,240,240,.6)'; ctx.lineWidth = 3;
  for (const a of ans.concat([TB(19, 0), TB(19, 3), TB(19, 6)])) { const d = t - a; if (d < 0 || d > .8) continue; ctx.globalAlpha = 1 - d / .8; ell(ctx, 40, -278, 20 + d * 260, (20 + d * 260) * .22); ctx.stroke(); }
  ctx.restore();
  // the man (side) looking at his raised hand
  const worried = t > TB(20) + .1;
  drawPerson(ctx, { x: -180, y: 60, s: 3.2, face: 1, pose: { lean: .12, bob: 0, lt: [0, 0], rt: [0, 0], la: [2.05, 1.25], ra: [.4, .6] }, c: { tunic: '#5a3a2a', skin: '#e3b998', hair: '#3a2418' }, head: 'hair', ex: { eyes: worried ? 'wide' : 'normal', mouth: worried ? 'wavy' : 'flat', brow: worried ? 1.3 : .2, look: [1, -.3] }, pale: worried ? .25 : 0, patchHand: true, t });
  ctx.restore();
  // close-up insert of the hand during bar 19
  const ins = 1 - toFace;
  if (ins > 0) {
    ctx.save(); ctx.globalAlpha = ins;
    ctx.fillStyle = 'rgba(8,12,14,.55)'; ctx.fillRect(0, 0, W, H);
    drawHand(ctx, W / 2 + Math.sin(lt * 1.4) * 20, 1120 + Math.sin(lt * 2) * 10, 2.0 + lt * .08, -.12 + Math.sin(lt) * .04, E.out(prog(t, TB(19, 6), TB(19, 12))), t);
    glow(ctx, 260, 700, 600, 'rgba(255,170,90,.25)');
    ctx.restore();
  }
  grade(ctx, '#3a7a78', .28);
  caption(ctx, ['IT BEGAN WITH', 'PALE, NUMB PATCHES.'], t, TB(19) + .05, TB(20, 14), { y: 470, size: 80 });
}, { post: { vig: .65 } });

// S12 — fear: townsfolk recoil, shutters slam (B21–B22)
let _S12W = null;
function S12wins() {
  if (_S12W) return _S12W;
  const c = ENV.rowL.wins.filter(w => w.type === 'win').map(w => ({ x: w.x - 1800, y: w.y - ENV.rowL.baseY, w: w.w, h: w.h })).filter(w => w.x > -700 && w.x < 700 && w.y > -650 && w.y < -150).sort((a, b) => a.x - b.x);
  _S12W = [0, 1, 2, 3, 4, 5].map(k => c[Math.floor(k * (c.length - 1) / 5)]); return _S12W;
}
scene(TB(21), TB(23), (ctx, t) => {
  const lt = t - TB(21), p = prog(lt, 0, 3.75);
  const cam = { x: lerp(-140, 120, E.inOut(p)), y: lerp(-380, -300, p), z: lerp(.95, 1.12, E.inOut(p)) * (1 + kickEnv(t) * .012), r: lerp(-.03, .02, p) };
  const slams = [TB(21, 0), TB(21, 3), TB(21, 6), TB(22, 0), TB(22, 3), TB(22, 6)];
  const sh = shakeAt(t, slams, 7, .07); cam.x += sh.x; cam.y += sh.y;
  streetBackdrop(ctx, t, cam, { sky: LEP_SKY, moon: false, stars: false, cloudCol: '#8fa9a3', fog1: 'rgba(170,200,190,.45)', fog2: 'rgba(150,180,175,.5)' });
  streetMain(ctx, t, cam, { row: ENV.rowL, ground: ENV.groundL, litFn: () => false });
  ctx.save(); applyCam(ctx, cam, 1);
  const sw = S12wins();
  sw.forEach((w, j) => { if (!w) return; drawShutterPair(ctx, w.x, w.y, w.w, w.h, 1 - E.in(prog(t, slams[j] - .04, slams[j] + .05))); });
  const lx = lerp(-80, 140, p);
  // townsfolk on both sides recoiling from the leper
  const folks = [[-620, 260, 1, 1.9], [-430, 380, 1, 2.2], [520, 250, -1, 1.9], [700, 380, -1, 2.3], [-820, 330, 1, 2.0], [880, 300, -1, 2.0]];
  folks.forEach(([x, y, face, s], i) => {
    const f = townsfolk(i + 300), k = E.outBack(clamp((t - TB(21) - i * .12) / .5));
    const pose = i === 2 ? posePoint(t) : poseRecoil(k);
    drawPerson(ctx, { x: x - face * k * 60, y, s: s * f.s, face, pose, c: f.c, head: f.head, robe: f.robe, ex: { eyes: 'wide', mouth: i % 2 ? 'o' : 'grit', brow: 1.3, look: [0, 0] }, t });
  });
  // mother pulls child away
  const mk = E.out(prog(t, TB(22), TB(22, 10)));
  drawPerson(ctx, { x: -260 - mk * 300, y: 470, s: 1.25, face: -1, pose: poseRun(lt / BEAT * .5, .6 * mk), c: { tunic: '#b8902f', skin: '#f1c9a2' }, head: 'hair', ex: { eyes: 'wide', mouth: 'o', brow: 1 }, t });
  drawPerson(ctx, { x: -120 - mk * 300, y: 480, s: 2.3, face: -1, pose: { ...poseRun(lt / BEAT * .5, .5 * mk), ra: [1.2, .2] }, c: { tunic: '#2f5d72', skin: '#e0ab7e', apron: '#e7dcc4' }, head: 'coif', robe: true, ex: { eyes: 'wide', mouth: 'frown', brow: 1.2 }, t });
  leper(ctx, lx, 330, 2.4, 1, t, { pose: poseWalk((t / BEAT) * .5, .5, .16) });
  ctx.restore();
  grade(ctx, '#4a8a86', .3);
  caption(ctx, ['THE FEAR WAS OFTEN', 'OVERWHELMING.'], t, TB(21) + .05, TB(22, 14), { y: 470, size: 82 });
}, { post: { vig: .62 } });

// S13 — guards march him to the gate (B23–B24)
const STOMP23 = [0, 3, 6, 8, 11].map(s => TB(23, s));
scene(TB(23), TB(25), (ctx, t) => {
  const lt = t - TB(23), p = prog(lt, 0, 3.5);
  const cam = { x: lerp(-200, 700, E.inOut(p)), y: -330, z: lerp(.95, 1.15, p) * (1 + kickEnv(t) * .02), r: .02 };
  const sh = shakeAt(t, STOMP23.concat([TB(24, 0), TB(24, 3), TB(24, 6)]), 10, .07); cam.x += sh.x; cam.y += sh.y;
  streetBackdrop(ctx, t, cam, { sky: LEP_SKY, moon: false, stars: false, cloudCol: '#8fa9a3', fog1: 'rgba(170,200,190,.45)', fog2: 'rgba(150,180,175,.5)' });
  streetMain(ctx, t, cam, { row: ENV.rowL, ground: ENV.groundL, litFn: () => false });
  ctx.save(); applyCam(ctx, cam, 1);
  drawWall(ctx, 1150, 2600, 0, 620, 1600, .75, { stone: '#7a7c78', inside: '#a9c2b8' });
  const gx = lerp(-300, 900, E.inOut(p));
  const march = (t / BEAT) * .5;
  const thump = Math.exp(-sinceLast(t, STOMP23.concat([TB(24, 0), TB(24, 3), TB(24, 6)])) / .08);
  [[gx - 230, 300, 2.1], [gx + 230, 340, 2.25]].forEach(([x, y, s], i) => {
    drawPerson(ctx, { x, y, s, face: 1, pose: { ...poseWalk(march + i * .5, .85, .05), la: [.25, .2], ra: [.35, .4] }, c: { tunic: '#3f4a6b', legs: '#2c3440', skin: '#e0ab7e', belt: '#2a1a12' }, head: 'hair', headFn: helmet, ex: { eyes: 'normal', mouth: 'flat', brow: -1 }, t, hold: (c2, hx, hy) => halberd(c2, hx, hy - thump * 12) });
  });
  leper(ctx, gx, 320, 2.15, 1, t, { pose: poseWalk(march, .5, .2) });
  ctx.restore();
  grade(ctx, '#4a8a86', .3);
  // percussive fill: dust puffs at feet on stomps
  if (t >= TB(24, 14)) { ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); }
}, { post: { vig: .62 } });

// S14 — DROP 2: the gate slams; cast out (B25–B26)
scene(TB(25), TB(27), (ctx, t) => {
  const lt = t - TB(25), p = E.inOut(prog(lt, .5, 3.6));
  const cam = { x: lerp(30, -60, p), y: lerp(-330, 120, p), z: lerp(1.3, .66, p) * (1 + kickEnv(t) * .028), r: lerp(.0, -.02, p) };
  const sh = shakeAt(t, [TB(25)], 38, .2); cam.x += sh.x; cam.y += sh.y;
  ctx.save(); applyCam(ctx, cam, .05); drawSky(ctx, { y0: -1900, y1: 200, stops: [[0, '#081012'], [.5, '#1f3436'], [1, '#5a7472']] }); ctx.restore();
  ctx.save(); applyCam(ctx, cam, .12); drawMoon(ctx, 380, -1250, 110, '#e6efe8', 'rgba(200,240,230,.25)'); drawClouds(ctx, t, { y0: -1500, y1: -800, n: 8, col: '#3a5254', a: .5, seed: 51 }); ctx.restore();
  // city inside the walls (warm)
  ctx.save(); applyCam(ctx, cam, .85); ctx.drawImage(ENV.row.c, -1800, -ENV.row.baseY - 380); drawWins(ctx, ENV.row.wins.map(w => ({ ...w, x: w.x - 1800, y: w.y - ENV.row.baseY - 380 })), t); ctx.restore();
  ctx.save(); applyCam(ctx, cam, 1);
  const gateOpen = t < TB(25) ? .2 : .2 * (1 - E.in(clamp(lt / .05)));
  drawWall(ctx, -2200, 2200, 0, 640, 0, gateOpen, { stone: '#6e7470', inside: '#ffb35a' });
  ctx.fillStyle = vgrad(ctx, 0, 1300, [[0, '#33423f'], [1, '#0d1314']]); ctx.fillRect(-2500, 0, 5000, 1500);
  // dust burst from the slam
  for (let k = 0; k < 40; k++) { const d = lt; if (d > 1.5) break; const a = hash(k) * Math.PI, r = E.out(clamp(d / 1.2)) * (200 + hash(k + 3) * 500); ctx.save(); ctx.globalAlpha = (1 - d / 1.5) * .45; ctx.fillStyle = '#b8b0a0'; ell(ctx, Math.cos(a) * r * (k % 2 ? 1 : -1), 10 - Math.sin(a) * r * .3, 50 + d * 80, 30 + d * 40); ctx.fill(); ctx.restore(); }
  // outcast camp
  drawHut(ctx, -620, 560, 1.5, 1); drawHut(ctx, 640, 640, 1.7, 2); drawHut(ctx, -980, 820, 1.9, 3);
  drawFire(ctx, -180, 760, 1.6, t);
  [[-420, 800, 1, 2.0], [60, 820, -1, 2.0], [-260, 930, 1, 2.3]].forEach(([x, y, face, s], i) => drawPerson(ctx, { x, y, s, face, pose: { ...poseIdle(t + i), la: [1.2, .8], ra: [.9, .9] }, c: { tunic: '#5f6866', hood: ['#4d5654', '#5a5248', '#46504e'][i], legs: '#333', skin: '#d8c4ae' }, head: 'hood', robe: true, ex: { eyes: 'tired', mouth: 'frown', brow: .9 }, t }));
  // our man, back to camera, facing the closed gate
  leper(ctx, 40, 200, 1.9, 1, t, { view: 'front', back: true, pose: { lean: 0, bob: 0, lt: [0, 0], rt: [0, 0], la: [.2, .3], ra: [.2, .3] }, rings: false });
  ctx.restore();
  grade(ctx, '#3f7a76', .25);
  const f = clamp(1 - lt / .1); if (f > 0) { ctx.fillStyle = `rgba(230,255,245,${f * .35})`; ctx.fillRect(0, 0, W, H); }
  caption(ctx, ['MANY SUFFERERS', 'WERE CAST OUT.'], t, TB(25) + .06, TB(26, 14), { y: 450, size: 96 });
}, { mb: lt => lt < .25 ? 3 : 1, post: { vig: .62 } });

// S15 — the healer and the humours (B27–B28)
scene(TB(27), TB(29), (ctx, t) => {
  const lt = t - TB(27), p = prog(lt, 0, 3.75);
  const cam = { x: lerp(-80, 60, p), y: lerp(-560, -620, p), z: lerp(1.05, 1.22, E.inOut(p)) * (1 + kickEnv(t) * .02), r: lerp(-.03, .02, p) };
  ctx.save(); applyCam(ctx, cam, 1);
  drawRoom(ctx, { wall: '#4a3a2c', winX: -520, winY: -1250 });
  // shelves with jars
  ctx.fillStyle = '#3a2618'; ctx.fillRect(250, -1050, 600, 24); ctx.fillRect(250, -820, 600, 24);
  for (let k = 0; k < 6; k++) { rr(ctx, 280 + k * 95, -1050 - 70 - (k % 2) * 20, 60, 70 + (k % 2) * 20, 10); fillStroke(ctx, ['#5a7a5a', '#8a5a3a', '#6a6a8a'][k % 3], 4); }
  drawTable(ctx, 120, -200, 1100, { col: '#5a3a24' });
  // open book on desk
  ctx.save(); ctx.translate(260, -260); ctx.rotate(-.04);
  ctx.beginPath(); ctx.moveTo(-200, 0); ctx.lineTo(0, 10); ctx.lineTo(200, 0); ctx.lineTo(190, -50); ctx.lineTo(0, -40); ctx.lineTo(-190, -50); ctx.closePath(); fillStroke(ctx, '#e8d3a3', 5);
  ctx.strokeStyle = 'rgba(60,40,20,.5)'; ctx.lineWidth = 2; for (let k = 0; k < 4; k++) { ctx.beginPath(); ctx.moveTo(-170, -38 + k * 9); ctx.lineTo(-30, -30 + k * 9); ctx.moveTo(30, -30 + k * 9); ctx.lineTo(170, -38 + k * 9); ctx.stroke(); }
  ctx.restore();
  drawCandle(ctx, 640, -230, 1.1, t, 110);
  // healer monk scratching head
  const scratch = Math.sin(t * 16) * .15;
  const qa = t > TB(28);
  drawPerson(ctx, { x: -260, y: 0, s: 2.9, face: 1, pose: { lean: .1, bob: bounce(t, 3), lt: [0, 0], rt: [0, 0], la: qa ? [2.9 + scratch, 1.7] : [1.4, 1.1], ra: [.5, .8] }, c: { tunic: '#6b4a2e', skin: '#e8b48f', belt: '#c9b07a' }, robe: true, head: 'none', headFn: tonsure, ex: { eyes: qa ? 'normal' : 'normal', mouth: qa ? 'wavy' : 'flat', brow: qa ? 1.2 : -.2, look: [qa ? -.4 : .6, -1] }, t });
  ctx.restore();
  // humours wheel turning a quarter on every beat
  const beats = Math.floor((t - TB(27)) / BEAT), fr = ((t - TB(27)) / BEAT) % 1;
  const rot = (beats + E.outBack(clamp(fr / .35))) * Math.PI / 2;
  ctx.save(); ctx.globalAlpha = clamp(lt / .2);
  glow(ctx, W / 2 + 140, 640, 500, 'rgba(255,200,120,.25)');
  drawHumours(ctx, W / 2 + 140, 640, 240, rot);
  ctx.restore();
  if (qa) for (let k = 0; k < 4; k++) { const ti = TB(28, k * 4), d = t - ti; if (d < 0) continue; qmark(ctx, 300 + k * 160, 980 - k * 40 - d * 30, E.outBack(clamp(d / .2)) * (1 + .1 * Math.sin(d * 8)), clamp(1.2 - d * .5)); }
  caption(ctx, ['MEDICINE BARELY', 'UNDERSTOOD IT.'], t, TB(27) + .05, TB(28, 14), { y: 1330, size: 86 });
}, { post: { vig: .66 } });
