// The film: 41 shots locked to the soundtrack grid (132 BPM, bars of 1.818 s).
const C = require('./core');
const { W, H, clamp, lerp, seg, smooth, smoother, outQ, outC, inQ, outBack, outElastic, spring, kick, pulse, hash, rand, mixh } = C;
const D = require('./draw');
const { INK, PAL, shape, tube, line, curve, ell, poly, glow, rays, star, sparkle, speedLines, motes } = D;
const K = require('./chars');
const F = require('./film');
const S = require('./scenes');
const E = require('./env');
const PR = require('./props');

const B = n => C.bt(n, 0), T = (n, s) => C.bt(n, s);
const SFX = [];                                   // audio cue list (filled while defining shots)
const sfx = (t, kind, gain = 1) => SFX.push({ t, kind, gain });

// ---------------------------------------------------------------- helpers
function blink(t, seed, base = 0) {
  const per = 1.6 + (hash(seed) * 0.5 + 0.5) * 1.6, ph = (t + hash(seed * 3) * 3) % per;
  return ph < 0.075 ? 1 : base;
}
const SICK = { sick: 0.9, lid: 0.42, mouth: 'frown', brows: 'sad', look: [0.25, 0.15] };
function person(ctx, who, P) {
  const sp = K.SPECS[who];
  D.contactShadow(ctx, P.x, P.y + 4, 115 * P.s * (sp.bodyW || 1), 0.3 * (P.alpha === undefined ? 1 : P.alpha));
  K.drawPerson(ctx, who, P);
}
const V = (t, o = {}) => K.P0(Object.assign({ t }, o));
function hold(keys, t) { // stepped pose keys: [{t, ...pose}] with springy transition into each
  let a = keys[0];
  for (let i = 1; i < keys.length; i++) if (t >= keys[i].t) a = keys[i];
  return a;
}
function poseSeq(keys, t, dur = 0.12) {   // blend from previous key to current with a spring
  let i = 0; while (i + 1 < keys.length && t >= keys[i + 1].t) i++;
  if (i === 0) return keys[0];
  const k = clamp(spring((t - keys[i].t), 18, 9));
  const kk = Math.min(1.08, (t - keys[i].t) >= dur * 4 ? 1 : k);
  return K.blend(keys[i - 1], keys[i], kk);
}
// screen-space overlay helpers
function vignetteDark(ctx, a = 0.6) {
  const g = ctx.createRadialGradient(W / 2, H / 2, H * 0.2, W / 2, H / 2, H * 0.7);
  g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, `rgba(20,8,4,${a})`); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
}
function parchmentBG(ctx, col = '#ead5a6') {
  ctx.fillStyle = col; ctx.fillRect(0, 0, W, H);
  ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.globalAlpha = 0.25; ctx.fillStyle = ctx.createPattern(D.grainTex(), 'repeat'); ctx.fillRect(0, 0, W, H); ctx.restore();
}
function woodTable(ctx, base = '#6b4428') {
  ctx.fillStyle = base; ctx.fillRect(0, 0, W, H);
  const r = rand(5);
  for (let y = -40; y < H; y += 190) {
    shape(ctx, c => c.rect(-20, y, W + 40, 186), mixh(base, r() < 0.5 ? '#8a5a34' : '#4a2e1a', 0.4 * r()), { lw: 5, texA: 0.35 });
    ctx.save(); ctx.globalAlpha = 0.25; for (let k = 0; k < 6; k++) { const yy = y + 20 + k * 28; curve(ctx, [-20, yy], [W / 2, yy + (r() - 0.5) * 30], [W + 20, yy + (r() - 0.5) * 20], 2.5, '#2a1810'); } ctx.restore();
  }
}
// draw a world function through a camera (p = 1)
const cam1 = (ctx, cam, fn) => F.withCam(ctx, cam, 1, fn);
function shakeCam(cam, t, hits, amp = 22) { let sx = 0, sy = 0; for (const h of hits) { sx += kick(t, h, amp); sy += kick(t, h, amp * 0.6, 7); } return Object.assign({}, cam, { sx, sy }); }
// house-layer (p=0.82) x -> world x for the current camera
function houseX(lx, cam) { const z = cam.z, ofs = cam.x * 0.82 + 540 * 0.18; const sx = (lx - ofs) * Math.pow(z, 0.82); return cam.x + sx / z; }

// ================================================================ SHOTS
const SH = [];
const shot = (t0, t1, name, draw, o = {}) => SH.push(Object.assign({ t0, t1, name, draw }, o));

// ---- 0:00 S01 street, sick villager trudging; push in --------------------------------------
shot(0, T(0, 8), 'street_open', (ctx, t, lt) => {
  const cam = shakeCam(F.camAt([{ t: 0, x: 600, y: -330, z: 0.92 }, { t: T(0, 8) + 0.1, x: 520, y: -120, z: 1.45, e: inQ }], t), t, [T(0, 6)], 10);
  const vx = 330 + lt * 120;
  S.street(ctx, cam, t, { fg: x => {
    person(x, 'extraB', V(t, Object.assign({ x: 980 - lt * 70, y: 40, s: 0.78, face: -1, lid: blink(t, 4) }, K.walk(t * 7 + 1, 0.8))));
    person(x, 'extraA', V(t, Object.assign({ x: 160 + lt * 40, y: 30, s: 0.72, face: 1, mouth: 'smile', lid: blink(t, 5) }, K.walk(t * 7, 0.7))));
    const cough = pulse(t, T(0, 6), 0.3);
    person(x, 'villager', V(t, Object.assign({ x: vx, y: 180, s: 1, ...SICK, lid: Math.max(SICK.lid, blink(t, 1)), lean: 6 + cough * 14, tilt: cough * 10, mouth: cough > 0.2 ? 'cough' : 'frown' }, K.walk(t * 5.2, 0.55))));
    if (t > T(0, 6)) PR.puff(x, vx + 95, -175 + (t - T(0, 6)) * -40, 22 + (t - T(0, 6)) * 60, clamp(1 - (t - T(0, 6)) * 2.5));
  } });
});
sfx(T(0, 6), 'cough_puff', 0.6);

// ---- 0:00.9 S02 sneeze close-up ------------------------------------------------------------
const SNZ = T(0, 12);
shot(T(0, 8), B(1), 'sneeze', (ctx, t, lt) => {
  const pre = seg(t, T(0, 8), SNZ), post = t >= SNZ;
  const cam = shakeCam({ x: 455 + (post ? 20 : 0), y: -140, z: 2.45 + 0.25 * pre + (post ? 0.15 * outC(seg(t, SNZ, SNZ + 0.2)) : 0) }, t, [SNZ], 34);
  S.street(ctx, cam, t, { props: false, fg: x => {
    const P = post
      ? { tilt: 14 - 10 * seg(t, SNZ + 0.15, B(1)), lean: 12 - 8 * seg(t, SNZ + 0.15, B(1)), eyes: t < SNZ + 0.25 ? 'closed' : 'open', mouth: t < SNZ + 0.3 ? 'gasp' : 'frown', open: 0.6, tail: 40 * (1 - seg(t, SNZ, SNZ + 0.6)), lid: 0.5, sick: 1, brows: 'sad' }
      : { tilt: -16 * smooth(pre), lean: -8 * smooth(pre), lid: 0.3 + 0.6 * pre, mouth: 'sneeze', open: pre, brows: 'worried', sick: 1, look: [0.1, -0.6] };
    person(x, 'villager', V(t, Object.assign({ x: 470, y: 180, s: 1, armL: [10, 30], armR: [-10, 30], bob: Math.sin(t * 3) * 2 }, P)));
    if (post) { const k = t - SNZ; for (let i = 0; i < 5; i++) PR.puff(x, 560 + k * (380 + i * 90), -200 + (i - 2) * 26 + k * 60 * (i - 2), 16 + k * 120, clamp(1 - k * 2.2), '#f6efe0'); }
  } });
  if (!post) speedLines(ctx, 540, 700, 22, 520, 1300, 0.12 * pre, 3);
});
sfx(SNZ, 'impact_soft', 0.9);

// ---- 0:01.8 S03 creepy tools insert ----------------------------------------------------------
shot(B(1), T(1, 8), 'tools', (ctx, t, lt) => {
  woodTable(ctx, '#3b2a22');
  const cam = { x: 540, y: 960, z: 1.02 + lt * 0.14, r: -3 + lt * 5 };
  cam1(ctx, cam, x => {
    // velvet cloth
    shape(x, c => c.roundRect(110, 330, 860, 1260, 40), '#5c1d1c', { lw: 6, shade: { x0: 0, y0: 330, x1: 0, y1: 1600, a: 0.35 } });
    const items = [
      [B(1), -1, 380, 640, -30, (c, g) => PR.fleam(c, t, g), 3.2],
      [T(1, 2), 1, 720, 760, 15, (c, g) => PR.bowl(c, 0, 0, 1.5), 1],
      [T(1, 4), 0, 560, 1060, 10, (c, g) => PR.braceDrill(c, t * 2, g), 2.0],
      [T(1, 6), 1, 360, 1250, -20, (c, g) => PR.pliers(c), 1.9],
    ];
    for (const [ti, dir, ix, iy, rot, fn, s] of items) {
      if (t < ti) continue;
      const k = outBack(seg(t, ti, ti + 0.16), 1.6);
      const px = dir === 0 ? ix : lerp(ix + dir * 900, ix, k), py = dir === 0 ? lerp(iy - 1200, iy, k) : iy;
      x.save(); x.translate(px, py); x.rotate((rot + (1 - k) * 25 * (dir || 1)) * C.D2R); x.scale(s, s);
      fn(x, pulse(t, ti + 0.12, 0.25)); x.restore();
    }
  });
  vignetteDark(ctx, 0.55);
});
for (const s of [0, 2, 4, 6]) sfx(T(1, s), s === 0 ? 'whoosh' : 'clink', 0.5);

// ---- 0:02.7 S04 leech jar insert ------------------------------------------------------------
shot(T(1, 8), B(2), 'jar_tease', (ctx, t, lt) => {
  const cam = { x: 260, y: -700, z: 1.5 + lt * 0.25, r: 2 - lt * 3 };
  S.shop(ctx, cam, t, { counter: false });
  const slap = T(1, 12);
  F.withCam(ctx, { x: 540, y: 960, z: 1 + lt * 0.22 }, 1, x => {
    glow(x, 540, 900, 520, '140,230,180', 0.25);
    PR.leechJar(x, 540, 1350, 2.4, t, { n: 7, eyes: true });
    if (t > slap) { // one leech slaps against the glass
      const k = t - slap, sq = 1 + 0.4 * Math.exp(-k * 12) * Math.cos(k * 40);
      x.save(); x.translate(560, 1000); x.scale(sq, 1 / sq); PR.leech(x, 0, 0, 240, t, 9, { eyes: true, smile: true, amp: 0.4, ang: -10 }); x.restore();
    }
  });
  vignetteDark(ctx, 0.5);
});
sfx(T(1, 12), 'squelch', 0.5);

// ---- 0:03.6 S05 three doctor silhouettes (build) ---------------------------------------------
let SIL = null;
shot(B(2), T(2, 8), 'silhouettes', (ctx, t, lt) => {
  const u = seg(t, B(2), T(2, 8));
  ctx.fillStyle = '#1a0f0c'; ctx.fillRect(0, 0, W, H);
  const cam = shakeCam({ x: 540, y: 1000, z: 0.95 + 0.4 * inQ(u) }, t, [], 0);
  cam.sx = Math.sin(t * 60) * 5 * u; cam.sy = Math.cos(t * 53) * 4 * u;
  cam1(ctx, cam, x => {
    // glowing doorway
    const g = x.createRadialGradient(540, 900, 50, 540, 900, 700); g.addColorStop(0, '#ffb85a'); g.addColorStop(0.5, '#c0602a'); g.addColorStop(1, '#3a1a10');
    shape(x, c => { c.moveTo(140, 1500); c.lineTo(140, 620); c.arc(540, 620, 400, Math.PI, 0); c.lineTo(940, 1500); c.closePath(); }, g, { lw: 8, tex: false });
    rays(x, 540, 600, Math.PI / 2, 1.2, 1300, 9, 0.12, 4);
    // floor fog
    for (let i = 0; i < 6; i++) PR.puff(x, 100 + i * 180 + Math.sin(t + i) * 30, 1480 + (i % 2) * 30, 90, 0.35, '#7a4a3a');
  });
  // silhouettes: draw doctors to an offscreen canvas, flatten to dark, add rim
  if (!SIL) SIL = C.canvas();
  const sx = SIL.getContext('2d'); sx.setTransform(1, 0, 0, 1, 0, 0); sx.clearRect(0, 0, W, H);
  cam1(sx, cam, x => {
    const step = outQ(u) * 60;
    K.drawPerson(x, 'doc2', V(t, { x: 300, y: 1480 + step * 0.4, s: 1.05, face: 1, armR: [150, 20], bob: Math.abs(Math.sin(t * 7)) * 6 }));
    K.drawPerson(x, 'doc3', V(t, { x: 780, y: 1480 + step * 0.4, s: 1.05, face: -1, armR: [40, 60] }));
    K.drawPerson(x, 'doc1', V(t, { x: 540, y: 1520 + step, s: 1.12, face: 1, armR: [-10, 20] }));
  });
  sx.globalCompositeOperation = 'source-atop'; sx.fillStyle = '#140a08'; sx.fillRect(0, 0, W, H); sx.globalCompositeOperation = 'source-over';
  ctx.drawImage(SIL, 0, 0);
  // glints: spectacles, goggles, eyes
  cam1(ctx, cam, x => {
    const gl = 0.5 + 0.5 * Math.sin(t * 9);
    const pts = [[512, 1520 - 495 * 1.12 + 0, 1], [565, 1520 - 495 * 1.12, 1], [270, 1480 - 395 * 1.05, 0.8], [330, 1480 - 395 * 1.05, 0.8], [760, 1480 - 600 * 1.05, 0.6], [800, 1480 - 600 * 1.05, 0.6]];
    for (const [px, py, s] of pts) { glow(x, px, py + 60 * u, 50 * s, '255,240,200', 0.6 * gl); sparkle(x, px, py + 60 * u, 18 * s * gl, 0.9); }
  });
  vignetteDark(ctx, 0.7);
});

// ---- 0:04.5 S06 villager realises: dart, GASP, crash zoom --------------------------------------
const GASP1 = 4.962;
shot(T(2, 8), B(3), 'realise', (ctx, t, lt) => {
  const g = t >= GASP1, gk = seg(t, GASP1, GASP1 + 0.12);
  const cam = shakeCam({ x: 470, y: -140, z: 2.3 + (g ? 0.7 * outC(gk) : lt * 0.3) }, t, [GASP1], 30);
  S.street(ctx, cam, t, { props: false, fg: x => {
    const dart = Math.floor((t - T(2, 8)) / C.S16) % 2 ? 0.8 : -0.8;
    person(x, 'villager', V(t, g
      ? { x: 470, y: 180, eyes: 'wide', mouth: 'gasp', open: 1, brows: 'worried', sweat: 1, sick: 0.6, tail: 60, squash: -0.08 * (1 - gk), armL: [40, 120], armR: [-40, 120] }
      : { x: 470, y: 180, ...SICK, lid: 0.25, look: [dart, -0.1], sweat: 0.8, mouth: 'teeth', brows: 'worried', shiver: 0.4 }));
  } });
  if (g) speedLines(ctx, 540, 760, 40, 420, 1400, 0.35, 12);
  if (t > B(3) - 0.06) { ctx.fillStyle = `rgba(255,248,230,${seg(t, B(3) - 0.06, B(3))})`; ctx.fillRect(0, 0, W, H); }
});
sfx(T(2, 8), 'riser_soft', 0.4);

// ================================================================ TREATMENT 1: BLOODLETTING
// ---- 0:05.45 S07 drop: the study, doctor spins round ---------------------------------------
const D1 = B(3);
shot(D1, B(4), 'study_wide', (ctx, t, lt) => {
  const cam = shakeCam(F.camAt([{ t: D1, x: 120, y: -260, z: 0.74 }, { t: B(4), x: 120, y: -200, z: 0.9 }], t), t, [D1], 18);
  S.study(ctx, cam, t, { fg: x => {
    const spin = seg(t, D1, D1 + 0.18), face = spin < 0.5 ? 1 : -1, sx = Math.abs(Math.cos(spin * Math.PI));
    const lean = t > D1 + 0.9 ? 10 * smooth(seg(t, D1 + 0.9, D1 + 1.2)) : 0;
    const dp = V(t, { x: 380 - 60 * smooth(seg(t, D1 + 0.9, D1 + 1.3)), y: 230, s: 1.08, face: face * Math.max(0.15, sx), brows: 'angry', mouth: t > D1 + 0.3 ? 'flat' : 'smirk', lid: blink(t, 7, 0.1), lean, armR: spin < 1 ? [-20, 20] : [95 + 8 * Math.sin(t * 4), 25], armL: [10, 30], look: [0.4, 0.1] });
    person(x, 'doc1', dp);
    if (spin > 0 && spin < 1) speedLines(x, 380, -150, 10, 140, 330, 0.5, 8, '255,240,210', 5);
    const enter = seg(t, D1, D1 + 0.9);
    const vp = V(t, Object.assign({ x: -560 + 400 * outQ(enter), y: 250, ...SICK, sweat: 0.6 * seg(t, D1 + 0.8, D1 + 1.2), lid: Math.max(0.42, blink(t, 2)) }, enter < 1 ? K.walk(t * 6, 0.6) : { bob: Math.sin(t * 3) * 2, armL: [10, 20], armR: [-5, 20] }));
    person(x, 'villager', vp);
  } });
});
sfx(D1, 'stamp', 1); sfx(D1 + 0.02, 'swish', 0.6);

// ---- 0:07.27 S08 magnifying glass, giant eye --------------------------------------------------
shot(B(4), T(4, 8), 'magnifier', (ctx, t, lt) => {
  const pop = T(4, 6);
  const cam = shakeCam({ x: 60, y: -170, z: 1.75 + lt * 0.12 }, t, [pop], 14);
  S.study(ctx, cam, t, { desk: false, fg: x => {
    person(x, 'villager', V(t, { x: -150, y: 250, ...SICK, lean: -10 - 6 * seg(t, pop, pop + 0.2), sweat: 1, mouth: 'teeth', brows: 'worried', lid: 0.15, look: [0.7, 0], tail: 15 }));
    person(x, 'doc1', V(t, { x: 260, y: 250, s: 1.08, face: -1, lean: 14, brows: 'angry', mouth: 'flat', armR: [120, -30], look: [0.6, 0] }));
    // magnifier in front of doctor's eye with a giant eye inside
    const ex = 120, ey = -330, R = 95 * (1 + 0.25 * outElastic(seg(t, pop, pop + 0.5)) * (t > pop ? 1 : 0));
    tube(x, [[ex + 40, ey + 70], [ex + 120, ey + 200]], 22, '#7a4a2a', 5);
    shape(x, ell(ex, ey, R, R), '#fffaf0', { lw: 0, tex: false });
    x.save(); x.beginPath(); x.arc(ex, ey, R, 0, 7); x.clip();
    shape(x, ell(ex, ey, R * 0.78, R * 0.9), '#fffaf0', { lw: 6, tex: false });
    const lk = Math.sin(t * 5) * 0.2;
    x.fillStyle = '#4a6a7a'; x.beginPath(); x.arc(ex - R * 0.25 + lk * 20, ey, R * 0.38, 0, 7); x.fill(); x.fillStyle = INK; x.beginPath(); x.arc(ex - R * 0.25 + lk * 20, ey, R * 0.2, 0, 7); x.fill();
    x.fillStyle = 'white'; x.beginPath(); x.arc(ex - R * 0.35, ey - R * 0.12, R * 0.08, 0, 7); x.fill();
    x.lineWidth = 10; x.strokeStyle = '#efe7da'; x.beginPath(); x.moveTo(ex - R * 0.9, ey - R * 0.95); x.quadraticCurveTo(ex, ey - R * 1.25, ex + R * 0.9, ey - R * 0.75); x.stroke();
    x.restore();
    shape(x, c => { c.arc(ex, ey, R + 14, 0, Math.PI * 2); c.arc(ex, ey, R, 0, Math.PI * 2, true); }, '#c9973a', { lw: 5, rule: 'evenodd', tex: false });
    x.save(); x.globalAlpha = 0.5; tube(x, [[ex - R * 0.6, ey - R * 0.3], [ex - R * 0.3, ey - R * 0.65]], 12, '#ffffff', 0); x.restore();
  } });
});
sfx(T(4, 6), 'boing_small', 0.45);

// ---- 0:08.18 S09 the book slams open: TOO MUCH BLOOD --------------------------------------------
shot(T(4, 8), T(5, 8), 'book', (ctx, t, lt) => {
  woodTable(ctx, '#5a3a24');
  const slam = T(4, 8);
  const taps = [T(4, 12), B(5), T(5, 4)];
  const cam = shakeCam({ x: 540, y: 960, z: 1.06 + lt * 0.08, r: -4 + lt * 2.5 }, t, [slam], 26);
  cam1(ctx, cam, x => {
    E.candle(x, 950, 420, 120, t, 3);
    const open = outBack(seg(t, slam, slam + 0.14), 1.2);
    PR.openBook(x, 540, 980, 860, 1060, t, { open });
    let tb = 0; for (const tp of taps) tb += pulse(t, tp, 0.12);
    if (open > 0.9) {
      x.save(); x.translate(0, tb * 4);
      // left page: blackletter heading + text lines + red initial
      x.font = '62px "Unifraktur"'; x.fillStyle = '#5a1a12'; x.textAlign = 'center'; x.fillText('De Sanguine', 330, 560);
      shape(x, c => c.rect(150, 610, 90, 90), '#a3342b', { lw: 3, tex: false }); x.font = '70px "Unifraktur"'; x.fillStyle = '#f0dfb4'; x.fillText('B', 195, 680);
      x.globalAlpha = 0.65; for (let i = 0; i < 14; i++) { const yy = 640 + i * 44, x0 = i < 3 ? 260 : 150; x.beginPath(); x.moveTo(x0, yy); for (let k = 0; x0 + k * 14 < 500; k++) x.lineTo(x0 + k * 14, yy + Math.sin(k * 1.7 + i) * 4); x.lineWidth = 3; x.strokeStyle = '#3a2418'; x.stroke(); }
      x.globalAlpha = 1;
      // right page: figure with too much blood (red, swollen)
      PR.figure(x, 760, 1020, 1.35, '#f08a7a');
      for (let i = 0; i < 7; i++) { const a = i * 0.9 + t * 0.5, rx = 760 + Math.cos(a) * 190, ry = 900 + Math.sin(a) * 210; shape(x, c => { c.moveTo(rx, ry - 26); c.quadraticCurveTo(rx + 20, ry, rx, ry + 12); c.quadraticCurveTo(rx - 20, ry, rx, ry - 26); }, '#b3302a', { lw: 3.5, tex: false }); }
      x.save(); x.translate(760, 1340); x.rotate(-0.08); x.font = '46px "IM Fell SC"'; x.fillStyle = '#8a1a12'; x.fillText('nimis sanguinis!', 0, 0); x.restore();
      x.restore();
    }
    // doctor's pointing hand (from bottom right)
    const tp = taps.reduce((a, tt) => a + pulse(t, tt, 0.14), 0);
    const hx = 860 - 60 * smooth(seg(t, slam + 0.15, slam + 0.35)), hy = 1220 + 220 * (1 - smooth(seg(t, slam + 0.1, slam + 0.35))) + tp * 18;
    tube(x, [[1180, 1700], [hx + 90, hy + 120]], 70, '#3b2c41', 6);
    shape(x, c => c.roundRect(hx + 50, hy + 70, 80, 34, 10), '#b2392d', { lw: 4, tex: false });
    shape(x, ell(hx + 60, hy + 50, 44, 40), '#eec09a', { lw: 5, tex: false });
    tube(x, [[hx + 40, hy + 30], [hx - 10, hy - 30]], 22, '#eec09a', 5);
    if (open > 0.9) for (let i = 0; i < 6; i++) { const k = seg(t, slam, slam + 0.5); PR.puff(x, 540 + (i - 2.5) * 170 * (1 + k), 470 + (i % 2) * 980 - k * 60, 40 + k * 60, (1 - k) * 0.8, '#e8d8b8'); }
  });
  vignetteDark(ctx, 0.55);
});
sfx(T(4, 8), 'book_slam', 1); for (const tp of [T(4, 12), B(5), T(5, 4)]) sfx(tp, 'tap', 0.35);

// ---- 0:10.0 S10 smug "obviously" ---------------------------------------------------------------
shot(T(5, 8), B(6), 'smug', (ctx, t, lt) => {
  const gl = T(5, 12);
  const cam = { x: 320, y: -150, z: 2.5 + lt * 0.2 };
  S.study(ctx, cam, t, { desk: false, fg: x => {
    const push = seg(t, T(5, 8) + 0.1, T(5, 8) + 0.35);
    person(x, 'doc1', V(t, { x: 300, y: 250, s: 1.08, face: -1, brows: 'skeptic', mouth: 'smirk', lid: 0.35, tilt: -6 + 4 * Math.sin(t * 6), armR: [160 - 10 * push, 125], look: [0.2, 0] }));
    if (t > gl) sparkle(x, 268, -380, 50 * pulse(t, gl, 0.4), 1);
  } });
});
sfx(T(5, 12), 'glint', 0.5);

// ---- 0:10.9 S11 the four humours chart ------------------------------------------------------------
const HUM = [
  { t: B(6), name: 'Blood', c: '#b3302a', x: 290, y: 600, k: 'drop' },
  { t: T(6, 4), name: 'Phlegm', c: '#9cc4d8', x: 790, y: 600, k: 'blob' },
  { t: T(6, 8), name: 'Yellow Bile', c: '#e6b23a', x: 290, y: 1320, k: 'flame' },
  { t: T(6, 12), name: 'Black Bile', c: '#3a2a3a', x: 790, y: 1320, k: 'drop' },
];
function humourIcon(x, h, s, t) {
  x.save(); x.translate(h.x, h.y); x.scale(s, s);
  shape(x, ell(0, 0, 150, 150), '#f3e4c0', { lw: 6, shade: { x0: 0, y0: -150, x1: 0, y1: 150, a: 0.2 } });
  x.save(); x.setLineDash([10, 8]); shape(x, ell(0, 0, 128, 128), null, { lw: 3, ink: '#8a5a30' }); x.restore();
  const wob = Math.sin(t * 4 + h.x) * 4;
  if (h.k === 'drop') shape(x, c => { c.moveTo(0, -80 + wob); c.quadraticCurveTo(70, 10, 0, 60); c.quadraticCurveTo(-70, 10, 0, -80 + wob); }, h.c, { lw: 5, tex: false, hi: { x: -20, y: -10, r: 40, a: 0.5 } });
  if (h.k === 'blob') shape(x, c => { c.moveTo(-60, 30); c.bezierCurveTo(-90, -40, -20, -80 + wob, 20, -50); c.bezierCurveTo(80, -60, 90, 20, 50, 50); c.bezierCurveTo(10, 70, -40, 60, -60, 30); }, h.c, { lw: 5, tex: false, hi: { x: -10, y: -20, r: 40, a: 0.5 } });
  if (h.k === 'flame') shape(x, c => { c.moveTo(0, -90 + wob); c.bezierCurveTo(30, -40, 70, -10, 50, 40); c.quadraticCurveTo(30, 70, 0, 70); c.quadraticCurveTo(-30, 70, -50, 40); c.bezierCurveTo(-60, 0, -10, -20, 0, -90 + wob); }, h.c, { lw: 5, tex: false, hi: { x: -10, y: 10, r: 40, a: 0.5 } });
  x.font = '50px "IM Fell SC"'; x.fillStyle = '#3a1a10'; x.textAlign = 'center'; x.fillText(h.name, 0, 205);
  x.restore();
}
shot(B(6), B(8), 'humours', (ctx, t, lt) => {
  parchmentBG(ctx);
  // camera visits each humour as it appears, then pulls back for the scales
  const keys = [{ t: B(6) - 0.01, x: 540, y: 960, z: 1.12 }];
  HUM.forEach(h => keys.push({ t: h.t + 0.16, x: lerp(540, h.x, 0.45), y: lerp(960, h.y, 0.45), z: 1.32, e: outC }));
  keys.push({ t: B(7) + 0.2, x: 540, y: 980, z: 1.0, e: outC }, { t: B(8), x: 540, y: 1000, z: 1.08 });
  const tip = T(7, 4);
  const cam = shakeCam(F.camAt(keys, t), t, [tip, T(7, 8)], 16);
  cam1(ctx, cam, x => {
    x.font = '88px "Unifraktur"'; x.fillStyle = '#4a1a10'; x.textAlign = 'center'; x.fillText('The Four Humours', 540, 300);
    line(x, [[220, 340], [860, 340]], 3, '#8a5a30');
    // central patient + balance scale
    const sc = seg(t, B(7), B(7) + 0.2);
    const tilt = t < tip ? 0 : -16 * outElastic(seg(t, tip, tip + 0.6));
    if (sc < 1) { x.save(); x.globalAlpha = 1 - sc; PR.figure(x, 540, 980 + Math.sin(t * 3) * 6, 1.3); x.restore(); }
    for (const h of HUM) {
      if (t < h.t) continue;
      const k = outBack(seg(t, h.t, h.t + 0.2), 2.2);
      x.save(); x.globalAlpha = 0.6; x.setLineDash([12, 10]); line(x, [[540, 960], [lerp(540, h.x, k), lerp(960, h.y, k)]], 4, '#8a5a30'); x.restore();
      humourIcon(x, h, k * (h.name === 'Blood' && t > tip ? 1 + 0.12 * Math.sin(t * 14) : 1), t);
    }
    if (sc > 0) {
      x.save(); x.globalAlpha = sc; x.translate(540, 1000); x.scale(0.6 + 0.4 * outBack(sc), 0.6 + 0.4 * outBack(sc));
      shape(x, c => c.rect(-14, -220, 28, 360), PAL.woodDark, { lw: 5 }); shape(x, c => c.rect(-90, 130, 180, 30), PAL.woodDark, { lw: 5 });
      x.save(); x.translate(0, -220); x.rotate(tilt * C.D2R);
      shape(x, c => c.rect(-230, -10, 460, 20), '#c9973a', { lw: 5, tex: false });
      for (const sd of [-1, 1]) {
        x.save(); x.translate(sd * 220, 0); x.rotate(-tilt * C.D2R);
        line(x, [[0, 0], [-70, 150]], 3); line(x, [[0, 0], [70, 150]], 3);
        shape(x, c => { c.moveTo(-90, 150); c.quadraticCurveTo(0, 210, 90, 150); c.closePath(); }, '#c9973a', { lw: 5, tex: false });
        if (sd < 0) shape(x, c => { c.moveTo(0, 30); c.quadraticCurveTo(80, 110, 0, 160); c.quadraticCurveTo(-80, 110, 0, 30); }, '#b3302a', { lw: 5, tex: false, hi: { x: -20, y: 100, r: 40, a: 0.5 } });
        else { shape(x, ell(-30, 140, 22, 18), '#9cc4d8', { lw: 4, tex: false }); shape(x, ell(10, 145, 18, 14), '#e6b23a', { lw: 4, tex: false }); shape(x, ell(40, 140, 16, 13), '#3a2a3a', { lw: 4, tex: false }); }
        x.restore();
      }
      x.restore(); x.restore();
    }
    if (t > T(7, 8)) {   // red verdict stamp
      const k = outBack(seg(t, T(7, 8), T(7, 8) + 0.12), 2.5);
      x.save(); x.translate(540, 560); x.rotate(-0.12); x.scale(k, k);
      x.lineWidth = 10; x.strokeStyle = '#b3302a'; x.strokeRect(-260, -70, 520, 140);
      x.font = '84px "Cinzel Black"'; x.fillStyle = '#b3302a'; x.textAlign = 'center'; x.textBaseline = 'middle'; x.fillText('TOO MUCH!', 0, 6);
      x.restore();
    }
  });
  // doctor cameo chuckling in a round portrait (chuckles at 12.27 / 12.50)
  const cin = seg(t, 12.15, 12.3), cout = seg(t, 12.95, 13.1);
  if (cin > 0 && cout < 1) {
    const px = lerp(-200, 220, outBack(cin)) - 420 * inQ(cout), py = 1580;
    ctx.save(); ctx.beginPath(); ctx.arc(px, py, 175, 0, 7); ctx.fillStyle = '#4a3020'; ctx.fill(); ctx.clip();
    const ch = pulse(t, 12.27, 0.2) + pulse(t, 12.5, 0.2);
    F.withCam(ctx, { x: 300 - (px - 540) / 1.6, y: -330 - (py - 960) / 1.6, z: 1.6 }, 1, x => person(x, 'doc1', V(t, { x: 300, y: 250, s: 1.08, face: -1, eyes: 'happy', mouth: 'chuckle', open: ch, tilt: -8 + ch * 6, bob: ch * 8 })));
    ctx.restore();
    ctx.lineWidth = 10; ctx.strokeStyle = '#c9973a'; ctx.beginPath(); ctx.arc(px, py, 175, 0, 7); ctx.stroke();
    ctx.lineWidth = 4; ctx.strokeStyle = INK; ctx.beginPath(); ctx.arc(px, py, 181, 0, 7); ctx.stroke();
  }
});
for (const h of HUM) sfx(h.t, 'pop', 0.5); sfx(T(7, 4), 'clunk', 0.8); sfx(T(7, 8), 'stamp', 0.7);

// ---- 0:14.5 S12 sharpening the fleam ----------------------------------------------------------
const STROKES = [B(8), T(8, 4), T(8, 8), T(8, 12)];
shot(B(8), B(9), 'sharpen', (ctx, t, lt) => {
  const cam = shakeCam({ x: 570 + lt * 30, y: -130, z: 1.8 + lt * 0.08, r: 1 - lt }, t, STROKES, 6);
  S.study(ctx, cam, t, { desk: false, fg: x => {
    shape(x, c => c.rect(420, -60, 560, 40), PAL.wood, { lw: 6 }); shape(x, c => c.rect(440, -22, 520, 300), PAL.woodDark, { lw: 6 });
    shape(x, c => c.rect(640, -110, 200, 52), '#8a8e94', { lw: 5, hi: { x: 700, y: -100, r: 60, a: 0.4 } });
    if (t > T(8, 12)) { const k = outBack(seg(t, T(8, 12), T(8, 12) + 0.2)); PR.bowl(x, lerp(1300, 900, k), -60, 0.9); }
    let st = 0; for (const s of STROKES) st += Math.max(0, 1 - Math.abs(t - s - 0.06) / 0.12);
    const ph = (t - B(8)) / (BEAT_S()) * Math.PI;
    const ax = Math.sin(ph) * 22;
    person(x, 'doc1', V(t, { x: 470, y: 250, s: 1.08, face: 1, lean: 8, brows: 'angry', mouth: 'smirk', lid: 0.38, look: [0.5, 0.6], armR: [70 + ax, 40 - ax * 0.5], armL: [55, 60], propR: { fn: (c) => PR.fleam(c, t, st), rot: 100, s: 1.2 } }));
    for (const s of STROKES) if (t > s && t < s + 0.3) sparkle(x, 760, -120, 60 * pulse(t, s, 0.3), 1);
  } });
});
function BEAT_S() { return C.BEAT; }
for (const s of STROKES) sfx(s, 'shing', 0.45); sfx(T(8, 12), 'clink', 0.6);

// ---- 0:16.4 S13 villager panics in the chair ----------------------------------------------------
shot(B(9), T(9, 8), 'panic', (ctx, t, lt) => {
  const hits = [B(9), T(9, 4)];
  const cam = shakeCam({ x: -160, y: -170, z: 2.3 + lt * 0.25 }, t, hits, 20);
  S.study(ctx, cam, t, { desk: false, chair: -160, fg: x => {
    const dart = Math.floor((t - B(9)) / (2 * C.S16)) % 2 ? 0.8 : -0.8;
    person(x, 'villager', V(t, { x: -160, y: 140, ...SICK, legL: [80, 80], legR: [75, 85], lid: 0.08, eyes: 'wide', look: [dart, 0], mouth: 'teeth', brows: 'worried', sweat: 1, shiver: 0.7, tail: 25, armL: [40, 50], armR: [30, 50] }));
  } });
});

// ---- 0:17.3 S14 the blade approaches (cut before contact) ---------------------------------------
shot(T(9, 8), B(10), 'approach', (ctx, t, lt) => {
  const cam = { x: -110, y: -200, z: 2.0 + lt * 0.5 };
  S.study(ctx, cam, t, { desk: false, chair: -250, fg: x => {
    person(x, 'villager', V(t, { x: -250, y: 140, ...SICK, legL: [80, 80], legR: [75, 85], eyes: 'closed', mouth: 'teeth', brows: 'worried', sweat: 1, shiver: 0.5, armR: [95, 0], armL: [30, 40], tilt: -10 }));
    const ap = smooth(seg(t, T(9, 8), B(10) - 0.1));
    const hx = lerp(560, 210, ap), hy = -290;
    tube(x, [[700, -150], [hx + 40, hy + 20]], 44, '#3b2c41', 5);
    shape(x, ell(hx + 20, hy + 10, 26, 24), '#eec09a', { lw: 4.5, tex: false });
    x.save(); x.translate(hx, hy); x.rotate(-1.6); PR.fleam(x, t, pulse(t, T(9, 14), 0.25)); x.restore();
  } });
  vignetteDark(ctx, 0.3 + 0.4 * seg(t, T(9, 8), B(10)));
});
sfx(T(9, 14), 'glint', 0.6);

// ---- 0:18.2 S15 result: pale, weak, doctor proud -------------------------------------------------
shot(B(10), B(11), 'pale', (ctx, t, lt) => {
  const cam = { x: 60, y: -230, z: 1.05 + lt * 0.1 };
  S.study(ctx, cam, t, { chair: -180, fg: x => {
    const sway = Math.sin(t * 2.4) * 9;
    person(x, 'villager', V(t, { x: -180, y: 140, sick: 0.4, pale: smooth(seg(t, B(10), B(10) + 0.6)), lid: 0.62, mouth: 'wavy', brows: 'sad', rot: sway, legL: [80, 80], legR: [75, 85], armL: [5, 5], armR: [-5, 5], tail: -10, look: [0.1, 0.5] }));
    person(x, 'doc1', V(t, { x: 330, y: 250, s: 1.08, face: -1, brows: 'raised', mouth: 'smile', eyes: 'happy', tilt: -6, armL: [-35, -120], armR: [-35, -120], bob: Math.sin(t * 5) * 3, lean: -4 }));
    sparkle(x, 400, -480 + Math.sin(t * 3) * 10, 30 + 10 * Math.sin(t * 8), 0.9);
    PR.bowl(x, 700, -180, 0.8, true);
  } });
});

// ---- 0:20.0 S16 stop-time punches, out the door --------------------------------------------------
const P3 = [B(11), T(11, 3), T(11, 6)];
shot(B(11), B(12), 'stoptime', (ctx, t, lt) => {
  const i = t < P3[1] ? 0 : t < P3[2] ? 1 : 2, out = t > T(11, 8);
  const z = [1.3, 1.5, 1.7][i];
  const cam = out ? F.camAt([{ t: T(11, 8), x: -300, y: -230, z: 1.0 }, { t: B(12), x: -420, y: -220, z: 1.15 }], t) : shakeCam({ x: -180, y: -200, z: z + (t - P3[i]) * 0.1 }, t, P3, 26);
  S.study(ctx, cam, t, { chair: out ? -180 : -180, desk: !out ? true : true, fg: x => {
    if (!out) {
      const poses = [{ rot: -16, eyes: 'spiral', tilt: -12 }, { rot: 18, eyes: 'spiral', tilt: 14, tail: 30 }, { rot: 60, eyes: 'dead', tilt: 20, tail: 50 }];
      person(x, 'villager', V(t, Object.assign({ x: -180, y: 140, pale: 1, mouth: 'wavy', legL: [80, 80], legR: [75, 85], armL: [20, 10], armR: [-20, 10] }, poses[i])));
      person(x, 'doc1', V(t, { x: 330, y: 250, s: 1.08, face: -1, brows: 'raised', mouth: 'smile', eyes: 'happy', armR: [150, 20], armL: [-35, -120] }));
    } else {
      // doctor shows him the door
      const k = seg(t, T(11, 8), B(12));
      shape(x, c => c.rect(-820, -560, 260, 560), '#2a1a12', { lw: 6 });
      glow(x, -690, -300, 380, '255,220,150', 0.5);
      x.save(); x.translate(-820, -560); x.scale(1 - 0.85 * smooth(seg(t, T(11, 8), T(11, 9))), 1); shape(x, c => c.rect(0, 0, 260, 560), PAL.wood, { lw: 6 }); x.restore();
      const oh = t > 21.36;
      person(x, 'villager', V(t, Object.assign({ x: lerp(-300, -700, outQ(k)), y: 220, pale: 1, mouth: oh ? 'o' : 'wavy', eyes: oh ? 'wide' : 'open', lid: oh ? 0 : 0.6, brows: 'worried', face: -1, tail: 30 }, K.walk(t * 8, 0.8))));
      person(x, 'doc1', V(t, { x: lerp(-60, -380, outQ(k)), y: 240, s: 1.08, face: -1, brows: 'raised', mouth: 'smile', eyes: 'happy', armR: [95, 0], lean: 10 }));
    }
  } });
});
for (const p of P3) sfx(p, 'freeze_hit', 0.7);
sfx(T(11, 8), 'door', 0.5);

// ================================================================ TREATMENT 2: LEECHES
const SHOPX = () => { const h = E.HOUSES.find(h => h.i === 9) || { x: 985, w: 330 }; return h; };
// ---- 0:21.8 S17 street: staggering to the leech shop -------------------------------------------
shot(B(12), B(13), 'to_shop', (ctx, t, lt) => {
  const h = SHOPX();
  const cam = F.camAt([{ t: B(12), x: 980, y: -150, z: 1.15 }, { t: B(13), x: 1120, y: -170, z: 1.3 }], t);
  const doorLX = h.x + h.w / 2;
  const doorX = houseX(doorLX, cam);
  S.street(ctx, cam, t, {
    houses: x => {
      const op = smooth(seg(t, T(12, 12), T(12, 15)));
      if (op > 0) {
        x.save(); x.beginPath(); x.moveTo(doorLX - 44, 0); x.lineTo(doorLX - 44, -170); x.arc(doorLX, -170, 44, Math.PI, 0); x.lineTo(doorLX + 44, 0); x.closePath(); x.clip();
        x.fillStyle = '#16261f'; x.fillRect(doorLX - 60, -260, 120, 260);
        glow(x, doorLX, -100, 200, '120,230,170', 0.6 * op);
        x.save(); x.translate(doorLX - 44, 0); x.scale(1 - 0.9 * op, 1); shape(x, c => c.rect(0, -214, 88, 214), PAL.wood, { lw: 4 }); x.restore();
        x.restore();
      }
    },
    fg: x => {
      const arrive = seg(t, B(12), T(12, 10));
      const vx = lerp(doorX - 520, doorX - 80, outQ(arrive));
      const look = t > T(12, 10);
      person(x, 'villager', V(t, Object.assign({ x: vx, y: 200, pale: 0.8, lid: look ? 0.1 : 0.55, eyes: look ? 'wide' : 'open', mouth: look ? 'o' : 'wavy', brows: 'worried', look: look ? [0.3, -0.8] : [0.5, 0.2], tilt: look ? -10 : Math.sin(t * 4) * 6, sweat: look ? 1 : 0 }, arrive < 1 ? K.walk(t * 6.5, 0.7) : { bob: 0 })));
      person(x, 'extraA', V(t, Object.assign({ x: doorX + 420 - lt * 60, y: 60, s: 0.75, face: -1, look: [-0.5, 0], brows: 'raised', mouth: 'o' }, K.walk(t * 6, 0.6))));
    } });
});
sfx(B(12), 'whoosh', 0.6); sfx(T(12, 12), 'creak', 0.5);

// ---- 0:23.6 S18 inside the shop: the doctor pops up ----------------------------------------------
const POP2 = T(13, 8);
shot(B(13), B(14), 'shop_pop', (ctx, t, lt) => {
  const cam = shakeCam(F.camAt([{ t: B(13), x: 20, y: -230, z: 1.15 }, { t: B(14), x: 50, y: -220, z: 1.25 }], t), t, [POP2], 20);
  S.shop(ctx, cam, t, { counterX: 320, back: x => {
    if (t > POP2 - 0.02) {
      const k = spring(t - POP2, 16, 6);
      person(x, 'doc2', V(t, { x: 330, y: 60 + (1 - Math.min(1.1, k)) * 420, s: 1.05, face: -1, eyes: 'open', mouth: 'grin', brows: 'raised', armR: [170, 10], propR: { fn: c => PR.leechJar(c, 0, 0, 0.55, t, { n: 5 }), rot: 180 }, armL: [-60, 40] }));
      for (let i = 0; i < 6; i++) sparkle(x, 330 + Math.cos(i + t * 3) * 260, -800 + Math.sin(i * 2 + t * 3) * 120, 26 * pulse(t, POP2, 0.8), 1);
    }
  }, fg: x => {
    const enter = seg(t, B(13), T(13, 6));
    const jump = t > POP2 ? pulse(t, POP2, 0.35) : 0;
    person(x, 'villager', V(t, Object.assign({ x: lerp(-700, -260, outQ(enter)), y: 250, pale: 0.6, lid: t > POP2 ? 0 : 0.3, eyes: t > POP2 ? 'wide' : 'open', mouth: t > POP2 ? 'scream' : 'flat', open: 1, brows: 'worried', look: t > POP2 ? [0.8, -0.2] : [Math.sin(t * 3), -0.2], bob: jump * 60, squash: -jump * 0.15, tail: t > POP2 ? 50 : 0, sweat: t > POP2 ? 1 : 0.3, armL: t > POP2 ? [150, 30] : [10, 20], armR: t > POP2 ? [-150, 30] : [-10, 20] }, enter < 1 ? K.walk(t * 6, 0.6) : {})));
  } });
});
sfx(POP2, 'pop_big', 0.9);

// ---- 0:25.5 S19a presenting the jar --------------------------------------------------------------
shot(B(14), T(14, 8), 'present', (ctx, t, lt) => {
  const cam = { x: 290, y: -230, z: 1.55 + lt * 0.15 };
  S.shop(ctx, cam, t, { counterX: 330, back: x => person(x, 'doc2', V(t, { x: 330, y: 60, s: 1.05, face: -1, eyes: 'open', mouth: 'grin', brows: 'raised', tilt: 6 * Math.sin(t * 4), bob: Math.abs(Math.sin(t * 6.9)) * 6, armR: [128 + 6 * Math.sin(t * 5), 32], armL: [-40, 50], propR: { fn: c => PR.leechJar(c, 0, 0, 0.95, t, { n: 6, eyes: true }), rot: 180 } })) });
});
// ---- 0:26.4 S19b villager recoils ----------------------------------------------------------------
shot(T(14, 8), B(15), 'recoil', (ctx, t, lt) => {
  const hit = T(14, 8);
  const cam = shakeCam({ x: -230, y: -90, z: 2.2 + 0.25 * outC(seg(t, hit, hit + 0.2)) }, t, [hit], 26);
  S.shop(ctx, cam, t, { counter: false, fg: x => person(x, 'villager', V(t, { x: -260, y: 250, pale: 0.4, eyes: 'wide', mouth: 'scream', open: 1, brows: 'worried', lean: -16, tail: 60, sweat: 1, armL: [150, 40], armR: [-150, 40], look: [0.9, 0], shiver: 0.4 })) });
  speedLines(ctx, 540, 700, 30, 450, 1400, 0.25, 21);
});
sfx(T(14, 8), 'whoosh', 0.5);

// ---- 0:27.3 S20 ECU: live leeches --------------------------------------------------------------
shot(B(15), 28.6, 'jar_ecu', (ctx, t, lt) => {
  ctx.fillStyle = '#20302a'; ctx.fillRect(0, 0, W, H);
  F.withCam(ctx, { x: 540, y: 960, z: 1 + lt * 0.12, r: -2 + lt * 2 }, 1, x => {
    glow(x, 540, 900, 700, '140,230,180', 0.35);
    x.save(); x.translate(540, 1500); x.scale(4.2, 4.2); x.translate(-540, -1500); PR.leechJar(x, 540, 1500, 1, t, { n: 6, eyes: true }); x.restore();
    // a leech waves at camera
    x.save(); x.translate(560, 980); x.rotate(Math.sin(t * 6) * 0.25); PR.leech(x, 0, 0, 300, t, 3, { eyes: true, smile: true, amp: 0.6, ang: -70 }); x.restore();
  });
  vignetteDark(ctx, 0.6);
});
sfx(B(15), 'squelch', 0.5);

// ---- 0:28.6 S21 doctor chuckles (synced to the two chuckles) --------------------------------------
shot(28.6, B(16), 'chuckle2', (ctx, t, lt) => {
  const cam = { x: 320, y: -272, z: 2.6 };
  S.shop(ctx, cam, t, { counterX: 330, back: x => {
    const ch = pulse(t, 28.636, 0.2) + pulse(t, 28.864, 0.2);
    person(x, 'doc2', V(t, { x: 330, y: 60, s: 1.05, face: -1, eyes: 'happy', mouth: 'chuckle', open: ch, brows: 'raised', tilt: -6 + ch * 8, bob: ch * 14, armR: [100, 60], armL: [-40, 50] }));
  } });
});

// ---- 0:29.1 S22 leeches placed on the arm (PG) ---------------------------------------------------
const PLACE = [T(16, 4), T(16, 8), T(16, 12)];
function arm(ctx, t, o = {}) {
  // cushion + forearm lying across the frame
  shape(ctx, c => c.roundRect(60, 900, 960, 360, 120), '#7a2a2a', { lw: 6, shade: { x0: 0, y0: 900, x1: 0, y1: 1260, a: 0.35 } });
  const fl = o.flinch || 0;
  ctx.save(); ctx.translate(0, Math.sin(t * 70) * fl * 4);
  tube(ctx, [[-60, 1060], [300, 1060]], 170, '#7d8a3d', 6);               // sleeve
  ctx.save(); ctx.globalAlpha = 0.4; for (let i = 0; i < 4; i++) curve(ctx, [40 + i * 60, 990], [60 + i * 60, 1060], [40 + i * 60, 1130], 4, '#4b5126'); ctx.restore();
  tube(ctx, [[300, 1062], [860, 1050]], 130, o.pale ? mixh('#f1c49b', '#c3d3a0', 0.6) : '#f1c49b', 6);   // forearm
  shape(ctx, c => { c.ellipse(900, 1046, 95, 82, 0, 0, Math.PI * 2); }, o.pale ? mixh('#f1c49b', '#c3d3a0', 0.6) : '#f1c49b', { lw: 6, tex: false });
  for (let i = 0; i < 4; i++) tube(ctx, [[940, 1000 + i * 30], [1000 + (i === 0 ? -20 : 0), 990 + i * 34]], 26, '#f1c49b', 5);
  ctx.restore();
}
shot(B(16), B(17), 'arm_place', (ctx, t, lt) => {
  woodTable(ctx, '#4a3020');
  const cam = shakeCam({ x: 540, y: 1000, z: 1.12 + lt * 0.06, r: 3 - lt * 2 }, t, PLACE, 8);
  cam1(ctx, cam, x => {
    let fl = 0; for (const p of PLACE) fl += pulse(t, p, 0.25);
    arm(x, t, { flinch: fl });
    const spots = [[440, 1040], [590, 1050], [730, 1040]];
    PLACE.forEach((p, i) => {
      if (t < p) return;
      const k = t - p, sq = 1 + 0.5 * Math.exp(-k * 14) * Math.cos(k * 45);
      x.save(); x.translate(spots[i][0], spots[i][1]); x.scale(sq, 1 / sq); PR.leech(x, 0, 0, 175, t, i, { amp: 0.35, ang: 20 - i * 18, eyes: true, smile: true, fat: 1.25 }); x.restore();
      if (k < 0.3) for (let j = 0; j < 4; j++) sparkle(x, spots[i][0] + Math.cos(j * 1.6) * 90 * (0.5 + k * 2), spots[i][1] + Math.sin(j * 1.6) * 90 * (0.5 + k * 2), 22 * (1 - k / 0.3), 1);
    });
    // doctor's hand with tweezers bringing the next leech
    const next = PLACE.find(p => t < p + 0.1) || PLACE[2];
    const idx = PLACE.indexOf(next), tgt = spots[idx];
    const a = seg(t, next - 0.32, next), hx = lerp(900, tgt[0] + 40, smooth(a)), hy = lerp(420, tgt[1] - 200, smooth(a)) + (t > next ? -200 * seg(t, next, next + 0.2) : 0);
    tube(x, [[1200, 200], [hx + 60, hy - 120]], 70, '#d39a35', 6);
    shape(x, ell(hx + 40, hy - 90, 40, 38), '#f3c9a2', { lw: 5, tex: false });
    x.save(); x.translate(hx + 20, hy - 60); x.rotate(0.5); PR.tweezers(x); x.restore();
    if (t < next) PR.leech(x, hx, hy + 30, 120, t, 7, { amp: 1.4, ang: 70, eyes: true });
  });
});
for (const p of PLACE) sfx(p, 'plop', 0.55);

// ---- 0:30.9 S23 villager's reaction ------------------------------------------------------------
shot(B(17), T(17, 8), 'twitch', (ctx, t, lt) => {
  const cam = { x: -240, y: -90, z: 2.5 + lt * 0.15 };
  S.shop(ctx, cam, t, { counter: false, fg: x => {
    const tw = Math.floor(t * 9) % 3 === 0 ? 0.65 : 0.15;
    person(x, 'villager', V(t, { x: -260, y: 250, pale: 0.7, lid: tw, mouth: 'wavy', brows: 'worried', look: [0.5, 0.9], sweat: 1, tilt: 8, shiver: 0.25 }));
  } });
});
// ---- 0:31.8 S24 the leeches get plump and happy ---------------------------------------------------
shot(T(17, 8), B(18), 'plump', (ctx, t, lt) => {
  woodTable(ctx, '#4a3020');
  const gulps = [T(17, 8), T(17, 12)];
  cam1(ctx, shakeCam({ x: 590, y: 1010, z: 1.5 + lt * 0.1 }, t, gulps, 6), x => {
    arm(x, t, { pale: true });
    const spots = [[440, 1040], [590, 1050], [730, 1040]];
    const fat = 1 + 0.45 * smooth(seg(t, T(17, 8), B(18)));
    spots.forEach((s, i) => { const g = gulps.reduce((a, gt) => a + pulse(t, gt + i * 0.04, 0.15), 0); x.save(); x.translate(s[0], s[1]); x.scale(1 + g * 0.2, 1 + g * 0.2); PR.leech(x, 0, 0, 175, t, i, { amp: 0.2, ang: 20 - i * 18, eyes: true, smile: true, fat: fat * 1.05 }); x.restore(); });
    for (let i = 0; i < 6; i++) { const k = (t * 1.2 + i / 6) % 1; x.save(); x.globalAlpha = 1 - k; star(x, 590 + Math.cos(i) * 260, 900 - k * 220, 16, t, '#ffe27a', 3); x.restore(); }
  });
});
for (const g of [T(17, 8), T(17, 12)]) sfx(g, 'gulp', 0.45);

// ---- 0:32.7 S25 the chase (side tracking) ------------------------------------------------------
const CHASE0 = B(18);
const chaseX = t => 1500 + (t - CHASE0) * 620;
shot(B(18), B(19), 'chase', (ctx, t, lt) => {
  const vx = chaseX(t);
  const cam = { x: vx - 120, y: -90, z: 0.98 };
  S.street(ctx, cam, t, { fg: x => {
    const dx = vx - 520 + Math.sin(t * 3) * 30;
    person(x, 'doc2', V(t, Object.assign({ x: dx, y: 230, s: 1.05, face: 1, eyes: 'open', mouth: 'grin', brows: 'raised', propR: { fn: c => PR.leechJar(c, 0, 0, 0.5, t, { n: 4 }), rot: 180 } }, K.run(t * 15, 0.85), { armR: [130 + Math.sin(t * 15) * 20, 20] })));
    person(x, 'villager', V(t, Object.assign({ x: vx, y: 250, pale: 0.5, eyes: 'wide', mouth: 'scream', open: 1, brows: 'worried', sweat: 1, tail: 70, look: [-0.8, 0] }, K.run(t * 17, 1), K.flail(t))));
    // leeches pinging off
    [0.3, 0.75, 1.2].forEach((dt, i) => { const k = t - CHASE0 - dt; if (k > 0 && k < 0.9) PR.leech(x, vx - 40 - k * 500, -320 + 900 * k * k - 500 * k, 90, t, i, { eyes: true, ang: k * 700 }); });
    for (let i = 0; i < 5; i++) { const k = ((t * 3 + i / 5) % 1); PR.puff(x, vx - 60 - k * 300, 250 - k * 30, 30 + k * 40, (1 - k) * 0.7, '#d9c49e'); }
  } });
});
sfx(B(18), 'whoosh', 0.6); for (const dt of [0.3, 0.75, 1.2]) sfx(B(18) + dt, 'pop', 0.4);

// ---- 0:34.5 S26 low tracking close-up ------------------------------------------------------------
shot(B(19), B(20), 'chase_cu', (ctx, t, lt) => {
  const vx = chaseX(t);
  const cam = { x: vx + 40, y: -60, z: 1.7 + Math.sin(t * 15) * 0.01, r: -4 };
  S.street(ctx, cam, t, { fg: x => {
    person(x, 'doc2', V(t, Object.assign({ x: vx - 640, y: 120, s: 0.95, face: 1, eyes: 'open', mouth: 'grin', propR: { fn: c => PR.leechJar(c, 0, 0, 0.5, t, { n: 4 }), rot: 180 } }, K.run(t * 15, 0.85), { armR: [140, 20] })));
    person(x, 'villager', V(t, Object.assign({ x: vx, y: 250, pale: 0.4, eyes: 'wide', mouth: 'scream', open: 1, brows: 'worried', sweat: 1, tail: 75, turn: -0.6, look: [-1, 0] }, K.run(t * 17, 1), K.flail(t))));
  } });
});

// ---- 0:36.4 S27 relief... "oh!" -------------------------------------------------------------------
const OH2 = 37.727, BONK = B(21);
const BEAMX = () => chaseX(B(20)) + (B(21) - B(20)) * 420 + 215;
function beamEnd(x, bx, wob = 0) {
  shape(x, c => c.rect(bx - 28 + wob * 0.3, -1600, 56, 1400), PAL.beam, { lw: 6, shade: { x0: bx - 28, y0: 0, x1: bx + 28, y1: 0, a: 0.35 } });
  x.save(); x.translate(bx + wob, -150); x.rotate(wob * 0.01);
  shape(x, c => c.roundRect(-62, -80, 124, 150, 10), '#6a4428', { lw: 7, shade: { x0: -60, y0: 0, x1: 60, y1: 0, a: 0.3 } });
  for (let r = 1; r < 4; r++) { x.save(); x.globalAlpha = 0.6; x.beginPath(); x.ellipse(0, -5, 14 * r, 18 * r, 0, 0, 7); x.lineWidth = 3; x.strokeStyle = '#3a2414'; x.stroke(); x.restore(); }
  x.restore();
}
shot(B(20), B(21), 'relief', (ctx, t, lt) => {
  const vx = chaseX(B(20)) + (t - B(20)) * 420;
  const see = t > OH2;
  const cam = see ? shakeCam({ x: vx + 120 + 200 * outC(seg(t, OH2, BONK)), y: -70, z: 2.1 - 0.9 * outC(seg(t, OH2 + 0.1, BONK)) }, t, [OH2], 16) : { x: vx + 30, y: -60, z: 1.6 };
  S.street(ctx, cam, t, { fg: x => {
    if (!see) person(x, 'doc2', V(t, { x: vx - 900, y: 60, s: 0.7, face: 1, eyes: 'closed', mouth: 'o', lean: 25, armL: [10, 10], armR: [10, 10], bob: Math.sin(t * 9) * 4 }));
    person(x, 'villager', V(t, Object.assign({ x: vx, y: 250, pale: 0.3, brows: see ? 'worried' : 'raised', eyes: see ? 'wide' : 'happy', mouth: see ? 'o' : 'smirk', turn: see ? 0.4 : -0.7, look: see ? [1, -0.3] : [-1, 0], tail: 40 }, K.run(t * 14, see ? 0.8 : 0.6))));
    beamEnd(x, BEAMX());
  } });
});
sfx(OH2 - 0.05, 'whoosh', 0.3);

// ---- 0:38.2 S28 BONK --------------------------------------------------------------------------
shot(B(21), B(22), 'bonk', (ctx, t, lt) => {
  const vx = chaseX(B(20)) + (B(21) - B(20)) * 420;
  const fall = seg(t, BONK + 0.35, BONK + 1.25), land = BONK + 1.25;
  const cam = shakeCam({ x: vx + 60, y: -120 + 200 * fall, z: 1.45 + lt * 0.08, r: 3 * Math.sin(lt * 2) }, t, [BONK, land], 40);
  S.street(ctx, cam, t, { fg: x => {
    const sq = Math.exp(-lt * 10) * Math.cos(lt * 50);
    person(x, 'villager', V(t, { x: vx, y: 250, pale: 0.3, eyes: lt < 0.3 ? 'closed' : 'spiral', mouth: lt < 0.3 ? 'teeth' : 'wavy', brows: 'worried', squash: sq * 0.25, rot: -88 * inQ(fall), bump: outBack(seg(t, BONK + 0.1, BONK + 0.4)), tail: 30 + sq * 40, armL: [20 + 60 * fall, 20], armR: [-20 + 60 * fall, 20], legL: [10 * fall, 0], legR: [-10 * fall, 0] }));
    if (lt > 0.25) PR.dizzy(x, vx + 20 - 300 * inQ(fall), -480 + 420 * inQ(fall), t, 120);
    if (t > land) PR.dust(x, vx - 260, 250, t - land, 6, 60, 3);
    beamEnd(x, BEAMX(), Math.exp(-lt * 6) * Math.sin(lt * 40) * 10);
  } });
  if (lt < 0.05) { ctx.fillStyle = 'rgba(255,250,235,0.85)'; ctx.fillRect(0, 0, W, H); }
});
sfx(BONK, 'bonk', 1); sfx(BONK + 1.25, 'thud', 0.8);

// ================================================================ TREATMENT 3: TREPANATION
// ---- 0:40.0 S29 a shadow falls: Doctor 3 looms ----------------------------------------------------
shot(B(22), B(23), 'looms', (ctx, t, lt) => {
  const vx = chaseX(B(20)) + (B(21) - B(20)) * 420;
  const u = smoother(seg(t, B(22) + 0.2, B(23) - 0.1));
  const cam = { x: lerp(vx - 250, vx - 30, u), y: lerp(230, -40, u), z: lerp(2.0, 1.15, u), r: lerp(-6, 0, u) };
  S.street(ctx, cam, t, { fg: x => {
    person(x, 'villager', V(t, { x: vx, y: 250, pale: 0.3, eyes: 'spiral', mouth: 'wavy', rot: -88, bump: 1, armL: [80, 20], armR: [40, 20] }));
    PR.dizzy(x, vx - 300, 70, t, 90, 3);
    const dc = seg(t, B(22), B(22) + 0.5);
    person(x, 'doc3', V(t, { x: vx + 120, y: 270, s: 1.12, face: -1, lid: 0.5, brows: 'calm', mouth: 'flat', look: [0.3, 0.9], tilt: -8, alpha: dc, armR: [40, 70], propR: { fn: c => { tube(c, [[0, 0], [0, 60]], 6, '#3a3a3a', 3); shape(c, c2 => c2.roundRect(-30, 60, 60, 80, 12), '#2a2a2a', { lw: 4, tex: false }); shape(c, ell(0, 100, 20, 28), '#ffcf5a', { lw: 0, tex: false }); glow(c, 0, 100, 160, '255,190,100', 0.6); }, rot: 180 } }));
  } });
  // long cold shadow sweeping in
  const sh = seg(t, B(22), B(22) + 0.6);
  const g = ctx.createLinearGradient(W, 0, 0, 0); g.addColorStop(0, 'rgba(20,20,40,0.55)'); g.addColorStop(sh, 'rgba(20,20,40,0.35)'); g.addColorStop(Math.min(1, sh + 0.2), 'rgba(20,20,40,0)');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
});
sfx(B(22), 'drone_low', 0.6);

// ---- 0:41.8 S30 the surgeon's cellar --------------------------------------------------------------
shot(B(23), B(24), 'cellar', (ctx, t, lt) => {
  const cam = F.camAt([{ t: B(23), x: 160, y: -300, z: 0.85 }, { t: B(24), x: 200, y: -290, z: 0.98 }], t);
  S.surgery(ctx, cam, t, { tableX: 160, fg: x => {
    person(x, 'villager', V(t, { x: 40, y: -110, s: 0.95, pale: 0.3, bump: 1, eyes: 'spiral', mouth: 'wavy', legL: [80, 85], legR: [75, 90], armL: [10, 10], armR: [-10, 10], rot: Math.sin(t * 2) * 6 }));
    PR.dizzy(x, 40, -600, t, 90, 3);
    const turn = smooth(seg(t, T(23, 10), T(23, 14)));
    const rub = Math.sin(t * 6) * 12;
    person(x, 'doc3', V(t, { x: 520, y: 260, s: 1.12, face: turn > 0.5 ? -1 : 1, turn: lerp(0.3, -0.4, turn), lid: 0.5, brows: 'calm', mouth: 'flat', look: turn > 0.5 ? [-0.4, 0] : [0.3, 0.6], armR: [70 + rub, 60], armL: [60 - rub, 70], propR: { fn: c => PR.braceDrill(c, t * 2, 0), rot: 90, s: 0.8 } }));
  } });
});
sfx(B(23), 'stamp', 0.9);

// ---- 0:43.6 S31 the tool roll -----------------------------------------------------------------
const UNROLL = B(24), DP = [T(24, 12), T(24, 14)];
shot(B(24), B(25), 'toolroll', (ctx, t, lt) => {
  woodTable(ctx, '#3a2a20');
  const dz = DP.reduce((a, p) => a + (t > p ? 0.18 : 0), 0);
  const cam = shakeCam({ x: 540 + (t > DP[0] ? 80 : 0), y: 960 + (t > DP[0] ? -60 : 0), z: 1.0 + lt * 0.08 + dz, r: -2 }, t, [UNROLL, ...DP], 18);
  cam1(ctx, cam, x => {
    const u = outC(seg(t, UNROLL, UNROLL + 0.3));
    const x1 = lerp(150, 980, u);
    shape(x, c => c.roundRect(100, 640, x1 - 100, 700, 26), '#7b4b2b', { lw: 7, shade: { x0: 0, y0: 640, x1: 0, y1: 1340, a: 0.3 } });
    for (let i = 0; i < 6; i++) { const lx = 170 + i * 135; if (lx < x1 - 60) { shape(x, c => c.rect(lx - 40, 760, 80, 480), '#8e5a34', { lw: 4 }); x.save(); x.setLineDash([8, 8]); line(x, [[lx - 34, 770], [lx - 34, 1230]], 2.5, '#d8b070'); x.restore(); } }
    shape(x, ell(x1, 990, 60, 360), '#6a3c22', { lw: 7 });
    x.save(); x.beginPath(); x.rect(100, 600, x1 - 60, 800); x.clip();
    const tools = [[230, (c, g) => PR.braceDrill(c, 0, g), 1.25, 0], [430, (c, g) => { c.rotate(-1.57); PR.saw(c); }, 1.2, 1], [610, (c, g) => PR.pliers(c), 1.3, 2], [800, (c, g) => PR.fleam(c, t, g), 2.0, 3]];
    tools.forEach(([tx, fn, s, i]) => { x.save(); x.translate(tx, 990); x.scale(s, s); const gl = pulse(t, UNROLL + 0.15 + i * 0.12, 0.3) + (i === 0 ? pulse(t, DP[0], 0.25) + pulse(t, DP[1], 0.25) : 0); fn(x, gl); x.restore(); });
    x.restore();
  });
  vignetteDark(ctx, 0.6);
});
sfx(UNROLL, 'unroll', 0.8); for (const p of DP) sfx(p, 'shing', 0.6);

// ---- 0:45.5 S32a/b rising tension: eyes, drill ---------------------------------------------------
shot(B(25), T(25, 8), 'eyes', (ctx, t, lt) => {
  const cam = shakeCam({ x: 70, y: -430, z: 4.0 + lt * 0.5 }, t, [B(25)], 16);
  S.surgery(ctx, cam, t, { table: false, fg: x => person(x, 'villager', V(t, { x: 40, y: -110, s: 0.95, pale: 0.4, bump: 1, eyes: 'wide', look: [0.6, -0.9], brows: 'worried', mouth: 'teeth', sweat: 1, shiver: 0.4, legL: [80, 85], legR: [75, 90] })) });
});
shot(T(25, 8), B(26), 'drill_cu', (ctx, t, lt) => {
  const cam = shakeCam({ x: 520, y: -180, z: 3.4 + lt * 0.5 }, t, [T(25, 8)], 16);
  S.surgery(ctx, cam, t, { table: false, fg: x => person(x, 'doc3', V(t, { x: 520, y: 260, s: 1.12, face: -1, turn: -0.4, lid: 0.55, brows: 'calm', mouth: 'flat', look: [-0.6, 0] })) });
  ctx.save(); ctx.translate(250, 760); ctx.scale(2.6, 2.6); ctx.rotate(0.15); PR.braceDrill(ctx, t * 3, pulse(t, T(25, 12), 0.3)); ctx.restore();
});
sfx(B(25), 'hit_low', 0.6); sfx(T(25, 8), 'hit_low', 0.7); sfx(T(25, 12), 'glint', 0.5);

// ---- 0:47.3 S33 anatomical plate (clean, no gore) ----------------------------------------------
function plate(ctx, t, o = {}) {
  parchmentBG(ctx, '#ecd9ad');
  const cam = o.cam;
  cam1(ctx, cam, x => {
    // frame + caption like an old anatomy plate
    x.lineWidth = 4; x.strokeStyle = '#8a3a2a'; x.strokeRect(90, 170, 900, 1500); x.lineWidth = 2; x.strokeRect(110, 190, 860, 1460);
    x.font = '42px "IM Fell SC"'; x.fillStyle = '#6a2a18'; x.textAlign = 'center'; x.fillText('PLATE III  ·  THE SKULL', 540, 1600);
    // head profile (our villager, hood off) with cross-section
    const cx = 540, cy = 930;
    shape(x, c => { c.moveTo(cx - 250, cy + 360); c.bezierCurveTo(cx - 330, cy + 100, cx - 330, cy - 330, cx, cy - 360); c.bezierCurveTo(cx + 270, cy - 360, cx + 330, cy - 150, cx + 300, cy - 20); c.lineTo(cx + 360, cy + 60); c.lineTo(cx + 300, cy + 90); c.quadraticCurveTo(cx + 320, cy + 180, cx + 260, cy + 230); c.quadraticCurveTo(cx + 150, cy + 300, cx + 120, cy + 360); c.closePath(); }, '#f1c49b', { lw: 6, shade: { x0: cx + 300, y0: cy - 300, x1: cx - 300, y1: cy + 300, a: 0.2 } });
    // skull layer (bone band) and brain area, clean diagram colours
    shape(x, c => { c.ellipse(cx - 20, cy - 80, 270, 240, 0, Math.PI * 1.02, Math.PI * 1.98); c.ellipse(cx - 20, cy - 80, 230, 200, 0, Math.PI * 1.98, Math.PI * 1.02, true); c.closePath(); }, '#f6eedc', { lw: 5, tex: false });
    shape(x, c => { c.ellipse(cx - 20, cy - 80, 228, 198, 0, Math.PI * 1.02, Math.PI * 1.98); c.closePath(); }, '#e9b8b0', { lw: 4, tex: false });
    x.save(); x.globalAlpha = 0.5; for (let i = 0; i < 6; i++) curve(x, [cx - 200 + i * 70, cy - 120], [cx - 170 + i * 70, cy - 220], [cx - 140 + i * 70, cy - 110], 3, '#a86a64'); x.restore();
    // eye + ear hints
    shape(x, ell(cx + 200, cy + 20, 26, 20), '#fffaf0', { lw: 4, tex: false }); shape(x, ell(cx - 40, cy + 70, 40, 60), '#e8b48c', { lw: 4, tex: false });
    // the opening (dotted circle) + label
    const hx = cx - 20, hy = cy - 300;
    const lid = o.lid || 0;
    x.save(); x.setLineDash([12, 10]); shape(x, ell(hx, hy, 70, 26), null, { lw: 5, ink: '#a3342b' }); x.restore();
    if (lid > 0) { // the little disc pops up like a lid (diagram style)
      x.save(); x.translate(hx, hy - lid * 260); x.rotate(lid * 0.6); shape(x, ell(0, 0, 70, 24), '#f6eedc', { lw: 5, tex: false }); x.restore();
      for (let i = 0; i < 5; i++) sparkle(x, hx + Math.cos(i * 1.3) * 160 * lid, hy - 60 - Math.sin(i * 1.3) * 120 * lid, 30 * (1 - Math.abs(lid - 0.5)), 1);
    }
    x.font = '40px "IM Fell SC"'; x.fillStyle = '#6a2a18'; x.textAlign = 'left'; x.fillText('a small opening', hx + 120, hy - 140);
    line(x, [[hx + 115, hy - 150], [hx + 60, hy - 30]], 3, '#6a2a18');
    // drill icon with motion arrows
    const dy = o.drill === undefined ? 0 : o.drill;
    x.save(); x.translate(hx, hy - 520 + dy * 180); x.scale(1.4, 1.4); PR.braceDrill(x, t * 6 * (o.spin || 1), 0); x.restore();
    for (const s of [-1, 1]) { x.save(); x.translate(hx + s * 150, hy - 420 + dy * 160); x.rotate(t * 4 * s); curve(x, [-40, 0], [0, -40], [40, 0], 5, '#a3342b'); shape(x, poly([[40, 0], [26, -16], [56, -10]]), '#a3342b', { lw: 0, tex: false }); x.restore(); }
    if (o.after) o.after(x);
  });
}
shot(B(26), 48.55, 'plate', (ctx, t, lt) => {
  plate(ctx, t, { cam: { x: 540, y: 820 - lt * 40, z: 1.15 + lt * 0.12, r: 1 }, drill: smooth(seg(t, B(26), T(26, 8) + 0.1)), spin: 1 });
});
// ---- 0:48.6 S34 gasp ----------------------------------------------------------------------------
shot(48.55, B(27), 'gasp2', (ctx, t, lt) => {
  const g = 48.636;
  const cam = shakeCam({ x: 40, y: -430, z: 3.2 + 0.6 * outC(seg(t, g, g + 0.12)) }, t, [g], 30);
  S.surgery(ctx, cam, t, { table: false, fg: x => person(x, 'villager', V(t, { x: 40, y: -110, s: 0.95, bump: 1, eyes: 'wide', mouth: 'gasp', open: 1, brows: 'worried', tail: 60, sweat: 1, armL: [150, 110], armR: [-150, 110] })) });
  speedLines(ctx, 540, 760, 36, 420, 1400, 0.3, 31);
});
// ---- 0:49.1 S35 climax: the lid pops -------------------------------------------------------------
shot(B(27), T(27, 8), 'plate_pop', (ctx, t, lt) => {
  const p = B(27);
  plate(ctx, t, { cam: shakeCam({ x: 540, y: 760, z: 1.45 - lt * 0.25, r: -6 * (1 - outC(seg(t, p, p + 0.5))) }, t, [p], 26), drill: 1, spin: 2, lid: outBack(seg(t, p + 0.05, p + 0.5)) });
  if (t - p < 0.05) { ctx.fillStyle = 'rgba(255,250,235,0.8)'; ctx.fillRect(0, 0, W, H); }
});
sfx(B(27), 'pop_big', 0.9);
// ---- 0:50.0 S35b the surgeon wipes his hands, patient bandaged -----------------------------------
shot(T(27, 8), B(28), 'done', (ctx, t, lt) => {
  const cam = { x: 260, y: -340, z: 1.15 + lt * 0.1 };
  S.surgery(ctx, cam, t, { tableX: 160, fg: x => {
    person(x, 'villager', V(t, { x: 40, y: -110, s: 0.95, bandage: 1, eyes: Math.floor(t * 4) % 2 ? 'open' : 'closed', lid: 0.2, mouth: 'flat', brows: 'raised', legL: [80, 85], legR: [75, 90], look: [0.5, -0.3] }));
    const rub = Math.sin(t * 9) * 16;
    person(x, 'doc3', V(t, { x: 480, y: 260, s: 1.12, face: -1, lid: 0.55, brows: 'calm', mouth: 'smirk', armR: [80 + rub, 50], armL: [80 - rub, 60], propR: { fn: c => shape(c, c2 => c2.roundRect(-30, -10, 60, 70, 12), '#efe4d0', { lw: 4 }), rot: 0 } }));
  } });
});

// ---- 0:50.9 S36 the healed skull (museum spotlight) ----------------------------------------------
shot(B(28), B(29), 'skull', (ctx, t, lt) => {
  ctx.fillStyle = '#1e1416'; ctx.fillRect(0, 0, W, H);
  const cam = { x: 540, y: 1180, z: 1.05 + lt * 0.12, r: Math.sin(lt * 1.6) * 3 };
  cam1(ctx, cam, x => {
    // velvet curtains
    for (const s of [-1, 1]) for (let i = 0; i < 4; i++) shape(x, c => c.rect(540 + s * (380 + i * 60) - 40, -100, 90, 2200), mixh('#5a1a22', '#3a0e14', i / 4), { lw: 4, shade: { x0: 540 + s * (380 + i * 60) - 40, y0: 0, x1: 540 + s * (380 + i * 60) + 50, y1: 0, a: 0.4 } });
    rays(x, 540, -100, Math.PI / 2, 0.55, 1900, 6, 0.16, 12);
    // pedestal + cushion
    shape(x, c => c.rect(300, 1300, 480, 700), '#d8ccb4', { lw: 6, shade: { x0: 300, y0: 0, x1: 780, y1: 0, a: 0.4 } });
    shape(x, c => c.rect(270, 1270, 540, 50), '#e8dcc4', { lw: 6 });
    shape(x, c => c.roundRect(310, 1180, 460, 110, 50), '#8a1f2a', { lw: 6, hi: { x: 480, y: 1200, r: 120, a: 0.3 } });
    // skull (clean, cartoon) with neat healed hole
    const sy = 1000 + Math.sin(t * 2) * 6;
    shape(x, c => { c.moveTo(540, sy - 230); c.bezierCurveTo(720, sy - 230, 760, sy - 40, 700, sy + 40); c.lineTo(690, sy + 120); c.quadraticCurveTo(620, sy + 190, 540, sy + 190); c.quadraticCurveTo(460, sy + 190, 390, sy + 120); c.lineTo(380, sy + 40); c.bezierCurveTo(320, sy - 40, 360, sy - 230, 540, sy - 230); c.closePath(); }, '#f2e8d2', { lw: 7, shade: { x0: 700, y0: sy - 200, x1: 380, y1: sy + 180, a: 0.3 }, hi: { x: 500, y: sy - 140, r: 150, a: 0.5 } });
    for (const s of [-1, 1]) shape(x, ell(540 + s * 85, sy + 10, 55, 60), '#3a2a2a', { lw: 5, tex: false });
    shape(x, poly([[540, sy + 70], [520, sy + 110], [560, sy + 110]]), '#3a2a2a', { lw: 4, tex: false });
    for (let i = -3; i <= 3; i++) line(x, [[540 + i * 26, sy + 140], [540 + i * 26, sy + 175]], 4);
    // healed hole: smooth bevelled rim
    shape(x, ell(600, sy - 150, 52, 30, -0.25), '#c8b896', { lw: 6, tex: false });
    shape(x, ell(600, sy - 146, 36, 18, -0.25), '#2a1e1e', { lw: 4, tex: false });
    for (let i = 0; i < 7; i++) sparkle(x, 540 + Math.cos(i * 0.9 + t) * 300, sy - 60 + Math.sin(i * 1.7 + t * 1.3) * 260, 26 * (0.5 + 0.5 * Math.sin(t * 5 + i)), 0.9);
    // brass plaque
    shape(x, c => c.roundRect(380, 1420, 320, 110, 12), '#c9973a', { lw: 5, hi: { x: 470, y: 1440, r: 120, a: 0.5 } });
    x.font = '50px "Cinzel Black"'; x.fillStyle = '#4a2a10'; x.textAlign = 'center'; x.textBaseline = 'middle'; x.fillText('HEALED', 540, 1462); x.font = '30px "IM Fell SC"'; x.fillText('the bone grew back', 540, 1505);
  });
  vignetteDark(ctx, 0.55);
});
sfx(B(28), 'shimmer', 0.6);

// ---- 0:52.7 S37 a shaky thumbs-up ---------------------------------------------------------------
shot(B(29), B(30), 'thumbs', (ctx, t, lt) => {
  const cam = { x: 200, y: -380, z: 1.35 + lt * 0.12 };
  S.surgery(ctx, cam, t, { tableX: 160, fg: x => {
    const tw = Math.floor(t * 7) % 4 === 0 ? 0.7 : 0.05;
    person(x, 'villager', V(t, { x: 40, y: -110, s: 0.95, bandage: 1, lid: tw, mouth: 'smile', brows: 'worried', legL: [80, 85], legR: [75, 90], shiver: 0.35, armR: [150, 40], look: [0.6, -0.1], propR: { fn: c => { shape(c, c2 => c2.roundRect(-8, -50, 18, 40, 9), '#f1c49b', { lw: 4, tex: false }); }, rot: 180 } }));
    const clap = Math.abs(Math.sin(t * 5));
    person(x, 'doc3', V(t, { x: 470, y: 260, s: 1.12, face: -1, lid: 0.55, brows: 'calm', mouth: 'smirk', armR: [70 + clap * 18, 60], armL: [70 - clap * 18, 60] }));
  } });
});

// ---- 0:54.5 S38 walking home, traumatised --------------------------------------------------------
shot(B(30), B(31), 'walk_home', (ctx, t, lt) => {
  const vx = 3300 + lt * 170;
  const cam = { x: vx + 40, y: -60, z: 1.15 + lt * 0.05 };
  S.street(ctx, cam, t, { fg: x => {
    person(x, 'extraB', V(t, { x: vx + 380, y: 40, s: 0.8, face: -1, brows: 'raised', mouth: 'o', look: [-0.6, 0.2], lid: blink(t, 8) }));
    person(x, 'extraA', V(t, { x: vx + 230, y: 20, s: 0.75, face: -1, brows: 'worried', mouth: 'frown', look: [-0.6, 0.3], tilt: 6 }));
    const tw = Math.floor(t * 6) % 3 === 0 ? 0.7 : 0.05;
    person(x, 'villager', V(t, Object.assign({ x: vx, y: 250, bandage: 1, lid: tw, mouth: 'flat', brows: 'worried', look: [0.4, 0], shiver: 0.2 }, K.walk(t * 6, 0.5), { armL: [3, 5], armR: [-3, 5] })));
  } });
});

// ---- 0:56.4 S39 "Next!": three punches, three doctors -------------------------------------------
const P4 = [B(31), T(31, 3), T(31, 6)], CH3 = [57.273, 57.5];
const DX = 4050;            // a dedicated clinic doorway in the subject plane
function clinicDoor(x, t, open) {
  // stone surround + dark warm interior + door leaf swinging open
  shape(x, c => { c.moveTo(DX - 230, 70); c.lineTo(DX - 230, -480); c.arc(DX, -480, 230, Math.PI, 0); c.lineTo(DX + 230, 70); c.closePath(); }, '#b3a385', { lw: 7, texA: 0.3 });
  x.save(); x.beginPath(); x.moveTo(DX - 180, 70); x.lineTo(DX - 180, -480); x.arc(DX, -480, 180, Math.PI, 0); x.lineTo(DX + 180, 70); x.closePath(); x.clip();
  x.fillStyle = '#24160f'; x.fillRect(DX - 200, -700, 400, 800); glow(x, DX, -250, 420, '255,180,100', 0.55);
  x.restore();
  x.save(); x.translate(DX + 180, 70); x.scale(-(1 - 0.85 * open), 1);
  shape(x, c => { c.moveTo(0, 0); c.lineTo(0, -550); c.arc(180, -480, 180, Math.PI * 1.1, Math.PI * 1.5); c.lineTo(360, -660); c.lineTo(360, 0); c.closePath(); }, PAL.wood, { lw: 6, shade: { x0: 0, y0: 0, x1: 360, y1: 0, a: 0.3 } });
  for (let k = 1; k < 4; k++) line(x, [[k * 90, -640], [k * 90, 0]], 3, PAL.woodDark);
  x.restore();
  E.sign(x, DX + 200, -640, t, 'bowl');
}
function doctorsAt(x, t, mode, k = 1) {
  const ch = pulse(t, CH3[0], 0.2) + pulse(t, CH3[1], 0.2);
  if (mode === 'one') { person(x, 'doc1', V(t, { x: DX - 40, y: 60, s: 0.95, face: -1, eyes: 'happy', mouth: 'smile', brows: 'raised', lean: 14, armR: [120 + 25 * Math.sin(t * 14), 70] })); return; }
  const sad = mode === 'sad';
  person(x, 'doc3', V(t, { x: DX + 110, y: 40, s: 0.95 * k, face: -1, lid: 0.5, mouth: sad ? 'frown' : ch > 0.3 ? 'grin' : 'smirk', brows: 'calm', armR: sad ? [20, 30] : [150, 20], propR: sad ? null : { fn: c => PR.braceDrill(c, t * 4, 0), rot: 180, s: 0.6 } }));
  person(x, 'doc1', V(t, { x: DX - 20, y: 60, s: 0.95 * k, face: -1, eyes: sad ? 'open' : 'happy', mouth: sad ? 'frown' : 'chuckle', open: ch, brows: sad ? 'sad' : 'raised', lean: sad ? 0 : 12, look: [-1, 0], armR: sad ? [20, 30] : [120 + 25 * Math.sin(t * 14), 70], bob: ch * 10 }));
  person(x, 'doc2', V(t, { x: DX - 150, y: 80, s: 0.9 * k, face: -1, eyes: sad ? 'open' : 'happy', mouth: sad ? 'o' : 'chuckle', open: ch, brows: sad ? 'sad' : 'raised', look: [-1, 0], bob: ch * 12, armR: [160, 10], propR: { fn: c => PR.leechJar(c, 0, 0, 0.45, t, { n: 4 }), rot: 180 } }));
}
shot(B(31), B(32), 'next', (ctx, t, lt) => {
  const i = t < P4[1] ? 0 : t < P4[2] ? 1 : 2;
  const late = t > T(31, 8);
  const cam = shakeCam({ x: DX - 240, y: -170, z: late ? 1.05 + (t - T(31, 8)) * 0.05 : 1.2 + i * 0.16 }, t, [...P4, CH3[0]], 22);
  S.street(ctx, cam, t, { fg: x => {
    clinicDoor(x, t, late ? smooth(seg(t, T(31, 8), T(31, 10))) : 0.3);
    doctorsAt(x, t, late ? 'all' : 'one', late ? outBack(seg(t, T(31, 8), T(31, 8) + 0.2)) : 1);
    const poses = [
      { eyes: 'wide', mouth: 'o', brows: 'raised', tail: 20, armL: [10, 20], armR: [-10, 20] },
      { eyes: 'wide', mouth: 'scream', open: 0.6, brows: 'worried', sweat: 1, tail: 60, armL: [90, 40], armR: [-90, 40], lean: -8 },
      { eyes: 'wide', mouth: 'scream', open: 1, brows: 'worried', sweat: 1, tail: 90, armL: [160, 30], armR: [-160, 30], bob: 60, squash: -0.15, lean: -12 },
    ];
    person(x, 'villager', V(t, Object.assign({ x: DX - 560, y: 260, bandage: 1, face: 1, look: [1, -0.2] }, poses[i], late ? { shiver: 0.6 } : {})));
  } });
});
for (const p of P4) sfx(p, 'freeze_hit', 0.8); sfx(T(31, 8), 'door', 0.5);

// ---- 0:58.2 S40 he bolts (left, back where he came from); the dust settles -> loops to 0:00 -------
shot(B(32), 60.0001, 'bolt', (ctx, t, lt) => {
  const cam = F.camAt([{ t: B(32), x: DX - 240, y: -170, z: 1.05 }, { t: 59.2, x: DX - 420, y: -190, z: 0.95 }, { t: 60, x: DX - 460, y: -200, z: 0.93 }], t);
  S.street(ctx, cam, t, { fg: x => {
    clinicDoor(x, t, 1);
    doctorsAt(x, t, t > B(32) + 0.25 ? 'sad' : 'all');
    const go = seg(t, B(32) + 0.08, B(32) + 0.5);
    const vx = DX - 560 - 2600 * inQ(go);
    if (go < 1) person(x, 'villager', V(t, Object.assign({ x: vx, y: 260, bandage: 1, face: -1, eyes: 'wide', mouth: 'scream', open: 1, brows: 'worried', tail: 90 }, K.run(t * 30, 1.2), K.flail(t), { lean: 30 })));
    if (t > B(32) + 0.08) { const k = t - B(32) - 0.08; for (let i = 0; i < 7; i++) PR.puff(x, DX - 560 - i * 170 - k * 60, 240 - (i % 2) * 40, 50 + k * 50 + i * 6, clamp(1 - k * 0.55) * (i < 7 * Math.min(1, k * 4) ? 1 : 0), '#dcc9a3'); }
  } });
  if (t > B(32) + 0.08 && t < B(32) + 0.5) speedLines(ctx, 540, 1100, 18, 380, 1300, 0.25, 41);
});
sfx(B(32) + 0.08, 'zip', 0.9);

// ================================================================ text layers, transitions
const SUBS = [
  [0.02, B(1) - 0.02, 'MEDIEVAL MEDICINE WAS INSANE.', ['INSANE']],
  [B(1), 5.36, 'THREE TREATMENTS WORSE THAN THE DISEASE.', ['DISEASE']],
  [5.72, T(4, 8) - 0.04, 'YOU HAVE A FEVER.', ['FEVER']],
  [T(4, 8), B(6) - 0.04, 'TOO MUCH BLOOD, OBVIOUSLY.', ['BLOOD'], '#ff6a4d'],
  [B(6), B(8) - 0.04, 'DOCTORS BELIEVED ILLNESS CAME FROM IMBALANCE.', ['IMBALANCE']],
  [B(8), B(10) - 0.04, 'SO THEY REMOVED BLOOD...', ['REMOVED']],
  [B(10), B(12) - 0.04, '...WHICH OFTEN MADE PEOPLE EVEN WEAKER.', ['EVEN', 'WEAKER']],
  [B(12), T(13, 8) - 0.04, 'NEED A SECOND OPINION?', ['SECOND', 'OPINION']],
  [T(13, 8), B(15) - 0.04, 'MEET THE LEECHES.', ['LEECHES'], '#9fe07a'],
  [B(15), B(16) - 0.04, 'YES, REAL LIVE LEECHES.', ['LIVE'], '#9fe07a'],
  [T(16, 4), B(18) - 0.04, 'THEY WERE USED TO SUCK BLOOD FROM THE BODY.', ['SUCK', 'BLOOD'], '#ff6a4d'],
  [B(18), B(20) - 0.04, 'BECAUSE APPARENTLY THAT WAS MEDICINE.', ['MEDICINE']],
  [B(21), T(22, 8) - 0.04, 'AND IF YOU INJURED YOUR HEAD...', ['HEAD']],
  [T(22, 8), B(24) - 0.04, '...THINGS GOT EVEN WORSE.', ['EVEN', 'WORSE']],
  [B(24), B(26) - 0.04, 'TREPANATION.', ['TREPANATION'], '#ff9a4d'],
  [B(26), B(28) - 0.04, 'DOCTORS SOMETIMES DRILLED INTO THE SKULL.', ['DRILLED']],
  [B(28), B(30) - 0.04, 'SURPRISINGLY, SOME PEOPLE SURVIVED.', ['SURVIVED'], '#9fe07a'],
  [B(30), 57.22, 'STILL FEELING SICK?', ['SICK']],
  [57.27, 60.0, 'SUDDENLY, BEING SICK SOUNDED SAFER.', ['SAFER'], '#9fe07a'],
].map(([t0, t1, text, em, color]) => ({ t0, t1, text, em, color }));
const STAMPS = [
  { t0: B(3), t1: B(4) - 0.1, kicker: 'TREATMENT Nº1', title: 'Bloodletting' },
  { t0: B(12), t1: B(13) - 0.1, kicker: 'TREATMENT Nº2', title: 'Leeches' },
  { t0: B(23), t1: B(24) - 0.1, kicker: 'TREATMENT Nº3', title: 'Trepanation' },
];
const SFXTEXT = [
  { t0: SNZ, t1: SNZ + 0.42, text: 'ACHOO!', x: 760, y: 560, size: 150, rot: -10 },
  { t0: BONK, t1: BONK + 0.65, text: 'BONK!', x: 600, y: 520, size: 190, rot: 8 },
  { t0: B(27), t1: B(27) + 0.4, text: 'POP!', x: 760, y: 420, size: 130, rot: -8, c1: '#ffffff', c2: '#9fe07a' },
];
// transitions at shot boundaries: whip = motion-blurred slide, flash = white pop
const TRANS = [
  [B(1), 'whipL'], [T(1, 8), 'whipU'], [B(3), 'flash'], [T(4, 8), 'whipL'], [B(6), 'whipR'], [B(8), 'whipL'],
  [B(10), 'flash'], [B(12), 'whipL'], [T(14, 8), 'whipR'], [B(16), 'whipU'], [B(18), 'whipL'], [B(21), 'flash'],
  [B(23), 'whipD'], [B(26), 'whipL'], [B(27), 'flash'], [B(28), 'whipR'], [B(30), 'whipL'],
].map(([t, kind]) => ({ t, kind }));
for (const tr of TRANS) if (tr.kind.startsWith('whip')) sfx(tr.t - 0.06, 'whoosh', 0.45);
// subtle beat pulse in the groove sections
const PULSE = [[B(3), B(11)], [B(12), B(16)], [B(18), B(20)], [B(21), B(25)], [B(27), B(31)]];

module.exports = { SH, SUBS, STAMPS, SFXTEXT, TRANS, PULSE, SFX };
