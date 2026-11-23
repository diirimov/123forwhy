// ---------- ENGLISH SWEATING SICKNESS (B29–B40) ----------
function feastRoom(ctx, t, o = {}) {
  drawRoom(ctx, { wall: '#7a4a2a', winX: 700, winY: -1250, winCol: '#2a1e3a' });
  // banners
  for (const bx of [-560, 120]) { ctx.beginPath(); ctx.moveTo(bx, -1300); ctx.lineTo(bx + 220, -1300); ctx.lineTo(bx + 220, -820); ctx.lineTo(bx + 110, -880); ctx.lineTo(bx, -820); ctx.closePath(); fillStroke(ctx, '#8a1e22', 6); ctx.beginPath(); ctx.rect(bx + 20, -1300, 50, 420); ctx.fillStyle = '#e8dcc0'; ctx.fill(); }
  // chandelier
  ctx.beginPath(); ctx.moveTo(-100, -1500); ctx.lineTo(-100, -1150); ctx.lineWidth = 6; ctx.strokeStyle = INK; ctx.stroke();
  ell(ctx, -100, -1150, 220, 30); fillStroke(ctx, '#3a2a1c', 6);
  for (let k = -2; k <= 2; k++) drawCandle(ctx, -100 + k * 90, -1170, .5, t + k, 60);
}
function guests(ctx, t, o = {}) {
  const jumpT = o.jumps || [];
  [[-640, -1], [-380, 1], [560, -1], [820, -1]].forEach(([x, face], i) => {
    const f = townsfolk(i + 500);
    const j = Math.exp(-sinceLast(t, jumpT) / .18);
    const rec = o.recoil ? E.out(clamp(o.recoil(t))) : 0;
    drawPerson(ctx, { x: x + (x < 0 ? -1 : 1) * rec * 120, y: -110 - j * 60, s: 2.1, face: x < 0 ? 1 : -1, pose: rec > 0 ? poseRecoil(rec) : { ...poseIdle(t + i), la: [1.3, 1.0], ra: [.8, .9] }, c: f.c, head: i % 2 ? 'tudor' : 'coif', robe: i % 2 === 0, ex: { eyes: rec > .2 ? 'wide' : 'normal', mouth: rec > .2 ? 'o' : 'smile', brow: rec > .2 ? 1.3 : 0 }, t, shadow: false });
  });
}
function feastTable(ctx, t, o = {}) {
  drawTable(ctx, 0, -40, 2100, { col: '#5a3a22', cloth: '#e6d8b8' });
  // food
  for (const [x, kind] of [[-760, 'bread'], [-420, 'pie'], [300, 'roast'], [680, 'bread'], [-120, 'fruit']]) {
    const y = -80 - (o.jump ? o.jump(t) * 40 : 0);
    if (kind === 'bread') { ell(ctx, x, y, 70, 34); fillStroke(ctx, '#c88a3a', 5); ctx.strokeStyle = 'rgba(80,40,10,.5)'; ctx.lineWidth = 3; for (const d of [-25, 0, 25]) { ctx.beginPath(); ctx.moveTo(x + d - 8, y - 20); ctx.lineTo(x + d + 8, y + 10); ctx.stroke(); } }
    if (kind === 'pie') { ctx.beginPath(); ctx.ellipse(x, y + 10, 90, 30, 0, Math.PI, 0); fillStroke(ctx, '#d8a04a', 5); }
    if (kind === 'roast') { ell(ctx, x, y, 90, 50); fillStroke(ctx, '#a8522a', 5); limb(ctx, [[x + 70, y - 20], [x + 120, y - 50]], 14, '#f2e6d0', 4); }
    if (kind === 'fruit') for (let k = 0; k < 4; k++) { ell(ctx, x + k * 34 - 50, y - (k % 2) * 20, 22, 22); fillStroke(ctx, ['#c8302a', '#e0a030', '#6a9a3a', '#c8302a'][k], 4); }
  }
}
function host(ctx, t, x, y, s, o = {}) {
  const sw = o.sweat || 0;
  drawPerson(ctx, { x, y, s, face: o.face || 1, rot: o.rot || 0, pose: o.pose, c: { tunic: '#6a1e3a', skin: '#efbd96', hat: '#1d1a22', belt: '#c9a043' }, head: 'tudor', ex: o.ex, sweat: sw, flush: sw * .7, t: t * 1.6, hold: o.hold, shadow: false });
}

// S16 — feast, sudden sweat, title (B29–B30)
scene(TB(29), TB(31), (ctx, t) => {
  const lt = t - TB(29), p = prog(lt, 0, 3.75);
  const hit = TB(29) + .04;
  const cam = { x: lerp(-40, 40, p), y: lerp(-520, -560, p), z: lerp(1.0, 1.1, E.inOut(p)) * (1 + kickEnv(t) * .025), r: lerp(.02, -.02, p) };
  const sh = shakeAt(t, [TB(29), TB(30)], 22, .14); cam.x += sh.x; cam.y += sh.y;
  ctx.save(); applyCam(ctx, cam, 1);
  feastRoom(ctx, t);
  guests(ctx, t, { recoil: tt => (tt - TB(30)) / .3 });
  const sw = clamp((t - hit) / .25);
  host(ctx, t, 0, -110, 2.5, { sweat: sw, pose: { lean: -.05 * sw, bob: bounce(t, 3), lt: [0, 0], rt: [0, 0], la: [lerp(2.7, 2.2, sw), lerp(.4, 1.0, sw)], ra: [lerp(.3, 1.4, sw), lerp(.4, 1.2, sw)] },
    ex: sw > 0 ? { eyes: 'wide', mouth: 'grit', brow: 1.3, look: [.2, -.4] } : { eyes: 'normal', mouth: 'smile', brow: -.2 }, hold: (c2, hx, hy) => drawGoblet(c2, hx, hy + 8, 1, lerp(0, .5, sw)) });
  feastTable(ctx, t);
  ctx.restore();
  // heat shimmer lines
  ctx.save(); ctx.globalAlpha = .35 * sw; ctx.strokeStyle = '#ffd28a'; ctx.lineWidth = 5;
  for (let k = 0; k < 8; k++) { const x = 140 + k * 110, ph = (t * 1.2 + hash(k)) % 1; ctx.beginPath(); for (let y = 0; y < 300; y += 10) ctx.lineTo(x + Math.sin(y * .05 + t * 6 + k) * 12, 1300 - ph * 500 - y); ctx.stroke(); }
  ctx.restore();
  grade(ctx, '#ff8a2a', .18, 'soft-light');
  bigTitle(ctx, ['ENGLISH', 'SWEATING', 'SICKNESS'], t, TB(29), { sizes: [150, 175, 175], y: 330, steps: [0, 3, 6], color: '#ffb340', glow: 'rgba(255,120,20,.85)' });
  yearStamp(ctx, '1485', t, TB(30), W / 2 + 255, 1030, { size: 100, sub: 'England', rot: .08 });
}, { post: { vig: .55 } });

// S17 — it struck fast (B31–B32)
const STOMP31 = [0, 3, 6, 8, 11].map(s => TB(31, s));
scene(TB(31), TB(33), (ctx, t) => {
  const lt = t - TB(31), p = prog(lt, 0, 3.75);
  const push = E.in(prog(t, TB(32), TB(33)));
  const cam = { x: lerp(0, 40, push), y: lerp(-560, -760, push), z: lerp(1.1, 2.3, push) * (1 + kickEnv(t) * .03), r: Math.sin(lt * 2.2) * .03 + push * .05 };
  const sh = shakeAt(t, STOMP31, 16, .08); cam.x += sh.x; cam.y += sh.y;
  ctx.save(); applyCam(ctx, cam, 1);
  feastRoom(ctx, t);
  guests(ctx, t, { jumps: STOMP31, recoil: () => 1 });
  const stagger = Math.sin(t * 5) * .12;
  host(ctx, t, Math.sin(t * 2.5) * 30, -110, 2.5, { sweat: 1, rot: stagger * .5, pose: { lean: stagger, bob: bounce(t, 6), lt: [.1, .1], rt: [-.1, .2], la: [2.8 + Math.sin(t * 9) * .2, 1.6], ra: [2.1 + Math.sin(t * 7) * .2, 1.2] }, ex: { eyes: 'wide', mouth: 'scream', brow: 1.4, look: [Math.sin(t * 5), -.3] } });
  feastTable(ctx, t, { jump: tt => Math.exp(-sinceLast(tt, STOMP31) / .12) });
  // sweat spray: drops emitted on every 16th
  for (let k = 0; k < 60; k++) {
    const st = TB(31) + k * S16 * .5, d = t - st; if (d < 0 || d > 1.2) continue;
    const a = -Math.PI / 2 + (hash(k) - .5) * 2.6, v = 600 + hash(k + 4) * 700;
    const x = Math.cos(a) * v * d, y = -540 + Math.sin(a) * v * d + 900 * d * d;
    ctx.save(); ctx.translate(x, y); ctx.rotate(Math.atan2(Math.sin(a) * v + 1800 * d, Math.cos(a) * v) + Math.PI / 2); ctx.globalAlpha = 1 - d / 1.2;
    ctx.beginPath(); ctx.moveTo(0, -18); ctx.quadraticCurveTo(12, 0, 0, 10); ctx.quadraticCurveTo(-12, 0, 0, -18); ctx.fillStyle = '#bfe8ff'; ctx.fill(); ctx.lineWidth = 3; ctx.strokeStyle = '#1d3a52'; ctx.stroke(); ctx.restore();
  }
  // flying goblets
  for (const [k, gx] of [[0, -500], [1, 640]]) { const d = t - STOMP31[k * 2]; if (d < 0) continue; drawGoblet(ctx, gx + d * 500 * (gx < 0 ? -1 : 1), -150 - d * 700 + d * d * 1400, 1.2, d * 9); }
  ctx.restore();
  grade(ctx, '#ff8a2a', .2, 'soft-light');
  caption(ctx, ['IT STRUCK FAST.'], t, TB(31) + .04, TB(32, 14), { y: 430, size: 112 });
}, { post: { vig: .6 } });

// S18 — the clock: hours, not weeks (B33–B35)
scene(TB(33), TB(36), (ctx, t) => {
  const lt = t - TB(33), p = prog(lt, 0, 5.625);
  const cam = { x: 0, y: 0, z: lerp(.92, 1.35, E.inOut(p)) * (1 + kickEnv(t) * .02), r: lerp(-.12, .08, E.inOut(p)) };
  ctx.fillStyle = vgrad(ctx, 0, H, [[0, '#06080c'], [.5, '#20201c'], [1, '#060506']]); ctx.fillRect(0, 0, W, H);
  ctx.save(); ctx.translate(W / 2, H / 2); ctx.rotate(cam.r); ctx.scale(cam.z, cam.z);
  // gears behind (parallax-ish)
  const tick = (t / BEAT) + E.outBack(clamp(beatPhase(t) / .3)) * 0; const gr = Math.floor(t / BEAT) * .26 + E.outBack(clamp(beatPhase(t) / .25)) * .26;
  ctx.save(); ctx.globalAlpha = .6; ctx.filter = 'blur(3px)';
  drawGear(ctx, -380, -520, 260, 18, gr, '#5a4a30'); drawGear(ctx, 360, -380, 190, 14, -gr * 1.3, '#5a4a30'); drawGear(ctx, 300, 560, 230, 16, gr * 1.1, '#5a4a30'); drawGear(ctx, -420, 480, 170, 12, -gr * 1.5, '#5a4a30');
  ctx.restore();
  drawGear(ctx, -330, 120, 140, 12, -gr * 1.7, '#8a6a3a'); drawGear(ctx, 380, 40, 110, 10, gr * 2.1, '#8a6a3a');
  // the clock, hands spinning wildly
  const hA = lt * TAU * .8, mA = lt * TAU * 4.3;
  glow(ctx, 0, -160, 700, 'rgba(255,190,90,.25)');
  drawClock(ctx, 0, -160, 340, hA, mA, t);
  // hourglass draining
  drawHourglass(ctx, 0, 470, 1.15, prog(lt, 0, 5.4), t);
  ctx.restore();
  // drifting dust in the light
  ctx.save(); ctx.globalCompositeOperation = 'lighter'; for (let k = 0; k < 50; k++) { const x = (hash(k) * W + t * 20 * (hash(k + 1) - .5)) % W, y = (hash(k + 2) * H - t * 30 * hash(k + 3) + H) % H; ctx.globalAlpha = .3 * hash(k + 4); ell(ctx, x, y, 2.5, 2.5); ctx.fillStyle = '#ffd8a0'; ctx.fill(); } ctx.restore();
  grade(ctx, '#2a8a8a', .12, 'soft-light');
  caption(ctx, ['HOURS,', 'NOT WEEKS.'], t, TB(33) + .05, TB(35, 14), { y: 1400, size: 104 });
}, { post: { vig: .7 } });

// S19 — the break: collapse into bed, the clock ticks (B36)
const TICKS36 = [4, 6, 8, 10].map(s => TB(36, s));
scene(TB(36), TB(37), (ctx, t) => {
  const lt = t - TB(36);
  const pick = E.in(prog(t, TB(36, 12), TB(37)));
  const cam = { x: lerp(-20, 20, pick), y: lerp(-470, -380, pick), z: (1.12 + pick * .3), r: .015 };
  const sh = shakeAt(t, [TB(36)], 28, .14); cam.x += sh.x; cam.y += sh.y;
  ctx.save(); applyCam(ctx, cam, 1);
  drawRoom(ctx, { wall: '#3a2c24', winX: -620, winY: -1200, winCol: '#121a2e' });
  // wall clock ticking with the woodblocks
  const ticks = TICKS36.filter(k => t >= k).length;
  const sec = (ticks + E.outBack(clamp(sinceLast(t, TICKS36) / .1)) * (ticks > 0 ? 0 : 0)) * TAU / 12;
  drawClock(ctx, 260, -980, 140, TAU * .35, sec, t);
  drawCandle(ctx, 700, -240, 1, t, 90);
  drawTable(ctx, 700, -200, 260, { col: '#4a3224' });
  drawBed(ctx, -60, 0, 1.6);
  // the fall: standing -> lying across the bed
  const fall = E.outBack(clamp(lt / .22));
  const rot = lerp(0, -1.5, fall);
  drawPerson(ctx, { x: lerp(-60, 60, fall), y: lerp(40, -205, fall), s: 2.2, face: 1, rot, pose: { lean: 0, bob: 0, lt: [lerp(0, .3, fall), .2], rt: [0, .1], la: [lerp(2.6, .25, fall), .4], ra: [lerp(2.2, .1, fall), .3] }, c: { tunic: '#e8dcc6', skin: '#efbd96' }, head: 'hair', ex: { eyes: lt > .25 ? 'closed' : 'wide', mouth: lt > .25 ? 'frown' : 'scream', brow: 1 }, sweat: 1, flush: .6, t, shadow: false });
  // blanket over him once down
  if (fall > .9) { ctx.beginPath(); ctx.moveTo(-180, -200); ctx.quadraticCurveTo(100, -250, 400, -210); ctx.lineTo(420, -170); ctx.lineTo(-180, -170); ctx.closePath(); fillStroke(ctx, '#8a3a2a', 5); }
  ctx.restore();
  // tick rings
  for (const k of TICKS36) { const d = t - k; if (d < 0 || d > .4) continue; ctx.save(); ctx.globalAlpha = 1 - d / .4; ctx.strokeStyle = '#ffd8a0'; ctx.lineWidth = 4; const s2 = cam.z; ell(ctx, W / 2 + (260 - cam.x) * s2, H / 2 + (-980 - cam.y) * s2, 180 + d * 300, 180 + d * 300); ctx.stroke(); ctx.restore(); }
  grade(ctx, '#ff7a2a', .1, 'soft-light');
  const f = clamp(1 - lt / .08); if (f > 0) { ctx.fillStyle = `rgba(255,200,150,${f * .3})`; ctx.fillRect(0, 0, W, H); }
}, { post: { vig: .72 } });

// S20 — the healer has no answers (B37–B38)
scene(TB(37), TB(39), (ctx, t) => {
  const lt = t - TB(37), p = prog(lt, 0, 3.75);
  const cam = { x: lerp(-60, 60, E.inOut(p)), y: -560, z: lerp(1.0, 1.2, E.inOut(p)) * (1 + kickEnv(t) * .02), r: lerp(.03, -.03, p) };
  ctx.save(); applyCam(ctx, cam, 1);
  drawRoom(ctx, { wall: '#4a3020', window: false });
  // doorway full of worried townsfolk
  ctx.beginPath(); ctx.moveTo(60, 0); ctx.lineTo(60, -900); ctx.quadraticCurveTo(330, -1100, 600, -900); ctx.lineTo(600, 0); ctx.closePath(); ctx.fillStyle = '#1a1220'; ctx.fill(); fillStroke(ctx, null, 10);
  ctx.save(); ctx.clip();
  for (let i = 0; i < 6; i++) { const f = townsfolk(i + 600); drawPerson(ctx, { x: 110 + i * 90 + (i % 2) * 30, y: -40 + (i % 2) * 90, s: 2.3 * f.s, view: 'front', pose: poseIdle(t + i, 1.5), c: f.c, head: f.head, robe: f.robe, ex: { eyes: 'wide', mouth: ['o', 'wavy', 'frown'][i % 3], brow: 1.2, look: [-.6, 0] }, t, shadow: false }); }
  ctx.restore();
  // healer flipping pages
  const shrug = t > TB(38) ? Math.exp(-sinceLast(t, [TB(38), TB(38, 8)]) / .3) : 0;
  drawTable(ctx, -190, -180, 520, { col: '#5a3a24' });
  drawPerson(ctx, { x: -380, y: 40, s: 2.8, face: 1, pose: { lean: .1, bob: bounce(t, 4), lt: [0, 0], rt: [0, 0], la: shrug > .05 ? [2.2, -.6] : [1.3, 1.2 + Math.sin(t * TAU / BEAT) * .3], ra: shrug > .05 ? [2.0, -.5] : [.9, 1.0] }, c: { tunic: '#2a2a3a', skin: '#e8b48f', hat: '#1d1a22' }, robe: true, head: 'cap', ex: { eyes: 'normal', mouth: shrug > .05 ? 'wavy' : 'flat', brow: shrug > .05 ? 1.4 : .3, look: [.8, .6] }, t });
  // book with pages flipping on beats
  ctx.save(); ctx.translate(-150, -250);
  ctx.beginPath(); ctx.moveTo(-170, 0); ctx.lineTo(0, 12); ctx.lineTo(170, 0); ctx.lineTo(160, -40); ctx.lineTo(0, -28); ctx.lineTo(-160, -40); ctx.closePath(); fillStroke(ctx, '#e8d3a3', 5);
  const fp = beatPhase(t); const ang = E.inOut(clamp(fp / .45));
  ctx.beginPath(); ctx.moveTo(0, 12); ctx.lineTo(0, -28); ctx.lineTo(Math.cos(ang * Math.PI) * 160, -40 - Math.sin(ang * Math.PI) * 90); ctx.lineTo(Math.cos(ang * Math.PI) * 170, -Math.sin(ang * Math.PI) * 90); ctx.closePath(); fillStroke(ctx, '#f2e2b8', 4);
  ctx.restore();
  ctx.restore();
  if (t > TB(38)) for (let k = 0; k < 3; k++) { const d = t - TB(38, k * 4 + 2); if (d < 0) continue; qmark(ctx, 620 + k * 120, 760 - k * 60 - d * 30, E.outBack(clamp(d / .2)) * 1.3, clamp(1.4 - d * .6)); }
  grade(ctx, '#ff7a2a', .12, 'soft-light');
  caption(ctx, ['PEOPLE FEARED', 'SUDDEN DEATH.'], t, TB(37) + .05, TB(38, 14), { y: 1380, size: 100 });
}, { post: { vig: .65 } });

// S21 — accelerating flash-back montage (B39–B40)
function sceneFrame(ctx, tt, zoom, rot) {
  const s = sceneAt(tt);
  ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(zoom, zoom); ctx.rotate(rot); ctx.translate(-W / 2, -H / 2);
  NOTEXT = true; s.fn(ctx, tt, tt - s.t0); NOTEXT = false; ctx.restore();
}
const MONT = [];
for (let s = 0; s < 16; s += 2) MONT.push(TB(39, s));
for (let s = 0; s < 12; s += 2) MONT.push(TB(40, s));
const MONT_SRC = [20.6, 32.3, 57.5, 24.9, 46.2, 61.5, 16.8, 39.2, 58.6, 25.8, 34.4, 66.0, 47.5, 29.3];
scene(TB(39), TB(41), (ctx, t) => {
  if (t >= TB(40, 12)) { ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); return; }
  let i = 0; for (let k = 0; k < MONT.length; k++) if (t >= MONT[k]) i = k;
  const lt = t - MONT[i];
  const z = 1.08 + i * .03 + lt * .35;
  sceneFrame(ctx, MONT_SRC[i] + lt * .5, z, (i % 2 ? 1 : -1) * .03);
  const f = clamp(1 - lt / .07); if (f > 0) { ctx.fillStyle = `rgba(0,0,0,${f * .5})`; ctx.fillRect(0, 0, W, H); }
  // build ring: tunnel of light growing toward the drop
  const b = prog(t, TB(39), TB(40, 12));
  ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.globalAlpha = b * .5;
  const g = ctx.createRadialGradient(W / 2, H / 2, 0, W / 2, H / 2, 900); g.addColorStop(0, 'rgba(255,180,90,.0)'); g.addColorStop(.7, 'rgba(255,120,40,.0)'); g.addColorStop(1, 'rgba(255,100,30,.6)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); ctx.restore();
}, { post: { vig: .7 } });
