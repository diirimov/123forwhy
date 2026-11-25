// V2 film: rebuilt opening, complete mini-stories per treatment, acting synced to the analysed soundtrack.
const C = require('./core');
const { W, H, clamp, lerp, seg, smooth, smoother, outQ, outC, inQ, inC, outBack, outElastic, spring, kick, pulse, hash, rand, mixh } = C;
const D = require('./draw');
const { INK, PAL, shape, tube, line, curve, ell, poly, glow, rays, star, sparkle, speedLines, motes } = D;
const K = require('./chars2');
const F = require('./film');
const S = require('./scenes');
const S2 = require('./scenes2');
const E = require('./env');
const PR = require('./props');

const B = n => C.bt(n, 0), T = (n, s) => C.bt(n, s);
const SFX = []; const sfx = (t, kind, gain = 1) => SFX.push({ t, kind, gain });
const SH = []; const shot = (t0, t1, name, draw) => SH.push({ t0, t1, name, draw });

function person(ctx, who, P, shadow = true) {
  const sp = K.SPECS[who];
  if (shadow && !P.rot) D.contactShadow(ctx, P.x, (P.y || 0) + 4, 115 * (P.s || 1) * (sp.bodyW || 1), 0.32 * (P.alpha === undefined ? 1 : P.alpha));
  K.drawPerson(ctx, who, P);
}
const V = (t, o) => Object.assign({ t }, o);
const cam1 = (ctx, cam, fn) => F.withCam(ctx, cam, 1, fn);
function shake(cam, t, hits, amp = 22) { let sx = 0, sy = 0; for (const h of hits) { sx += kick(t, h, amp); sy += kick(t, h, amp * 0.6, 7); } return Object.assign({}, cam, { sx, sy }); }
function vignette(ctx, a = 0.6) { const g = ctx.createRadialGradient(W / 2, H / 2, H * 0.2, W / 2, H / 2, H * 0.72); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, `rgba(20,8,4,${a})`); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); }
function parchment(ctx, col = '#ead5a6') { ctx.fillStyle = col; ctx.fillRect(0, 0, W, H); ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.globalAlpha = 0.25; ctx.fillStyle = ctx.createPattern(D.grainTex(), 'repeat'); ctx.fillRect(0, 0, W, H); ctx.restore(); }
function woodTable(ctx, base = '#6b4428') {
  ctx.fillStyle = base; ctx.fillRect(0, 0, W, H); const r = rand(5);
  for (let y = -40; y < H; y += 190) { shape(ctx, c => c.rect(-20, y, W + 40, 186), mixh(base, r() < 0.5 ? '#8a5a34' : '#4a2e1a', 0.4 * r()), { lw: 5, texA: 0.35 }); ctx.save(); ctx.globalAlpha = 0.25; for (let k = 0; k < 6; k++) { const yy = y + 20 + k * 28; curve(ctx, [-20, yy], [W / 2, yy + (r() - 0.5) * 30], [W + 20, yy + (r() - 0.5) * 20], 2.5, '#2a1810'); } ctx.restore(); }
}
// camera that frames a head at a given screen height
const frameHead = (hx, hy, z, sy = 820, dx = 0) => ({ x: hx + dx / z, y: hy + (960 - sy) / z, z });
const P_ = (who, o) => K.P0(o);

// ================================================================ OPENING (0 - 5.45)
// patient lying on the examination table (rot -90 about the hip -> face up)
const PAT = { x: 40, y: -5, s: 1 };
const patHead = () => ({ x: PAT.x - (150 + 170 * 0.38) * 1, y: PAT.y - 165 });     // world head centre when lying
function lyingPatient(x, t, o = {}) {
  shape(x, c => { const hx = patHead().x; c.moveTo(hx - 170, -100); c.quadraticCurveTo(hx - 180, -150, hx - 120, -150); c.lineTo(hx + 90, -150); c.quadraticCurveTo(hx + 140, -150, hx + 130, -100); c.closePath(); }, '#efe6d2', { lw: 5, shade: { x0: 0, y0: -150, x1: 0, y1: -100, a: 0.25 } });
  person(x, 'villager', V(t, Object.assign({ x: PAT.x, y: PAT.y, s: 1, rot: -90, piv: 'hip', armL: [8, 6], armR: [-4, 10], legL: [2, 2], legR: [-2, 2], breath: 1.6 }, o)), false);
}
function examDoctors(x, t, o = {}) {
  // doc3 stands behind the table (drawn before it), doc1 head end, doc2 foot end
  if (o.behind) person(x, 'doc3', V(t, Object.assign({ x: 140, y: -40, s: 1.12, face: -1, brows: 'calm', lid: 0.5, mouth: 'flat', look: [0.2, 0.8], armL: [30, 60], armR: [25, 70], tilt: 6 }, o.d3 || {})), false);
}
function examFront(x, t, o) {
  person(x, 'doc1', V(t, Object.assign({ x: -430, y: 260, s: 1.1, face: 1, brows: 'angry', mouth: 'smirk', lean: 14, look: [0.6, 0.6], armR: [70, 50], armL: [40, 70] }, o.d1 || {})));
  person(x, 'doc2', V(t, Object.assign({ x: 470, y: 260, s: 1.05, face: -1, eyes: 'happy', mouth: 'grin', brows: 'raised', lean: 12, armR: [60, 80], armL: [50, 90], handR: 'open', handL: 'open' }, o.d2 || {})));
}
function wallShadows(x, t, k = 1) {
  S2.castShadow(x, y => {
    K.drawPerson(y, 'doc1', V(t, { x: -430, y: 260, s: 1.1, face: 1, lean: 14, armR: [70, 50] }));
    K.drawPerson(y, 'doc3', V(t, { x: 140, y: -40, s: 1.12, face: -1, armL: [30, 60] }));
    K.drawPerson(y, 'doc2', V(t, { x: 470, y: 260, s: 1.05, face: -1, lean: 12, armR: [60, 80] }));
  }, { ax: 0, ay: 260, dx: 0, dy: -300, sx: 1.35, sy: 1.5, skew: -0.25, alpha: 0.34 * k, blur: 10 });
}
const HOOKLEAP = T(0, 6);
// O1: extreme close-up, camera rolled so his face is upright
shot(0, T(0, 8), 'o_ecu', (ctx, t, lt) => {
  const h = patHead();
  const cam = shake({ x: h.x + 10, y: h.y - 10, z: 3.9 + lt * 0.25 + (t > HOOKLEAP ? 0.35 * outC(seg(t, HOOKLEAP, HOOKLEAP + 0.12)) : 0), r: 90 }, t, [HOOKLEAP], 14);
  const dart = Math.floor(t / C.S16) % 3 - 1;
  S2.exam(ctx, cam, t, { blur: 9, shadows: x => examDoctors(x, t, { behind: true }), fg: x => {
    lyingPatient(x, t, { eyes: t > HOOKLEAP ? 'wide' : 'open', lid: 0, look: t > HOOKLEAP ? [0.2, -0.9] : [dart * 0.8, -0.5], brows: 'shock', mouth: t > HOOKLEAP ? 'eek' : 'teeth', sweat: 1, shiver: 0.4, tail: 20 });
  } });
  // doctors' shadows sweeping across his face
  const g = ctx.createLinearGradient(0, 0, W, 0), p = (t * 0.9) % 1;
  g.addColorStop(clamp(p - 0.25), 'rgba(20,10,8,0)'); g.addColorStop(clamp(p), 'rgba(20,10,8,0.45)'); g.addColorStop(clamp(p + 0.25), 'rgba(20,10,8,0)');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
});
sfx(HOOKLEAP, 'hit_low', 0.5);
// O2: rapid cinematic zoom-out + roll revealing the three doctors
shot(T(0, 8), B(1), 'o_reveal', (ctx, t, lt) => {
  const u = outC(seg(t, T(0, 8), B(1) - 0.05)), h = patHead();
  const cam = { x: lerp(h.x + 10, 0, u), y: lerp(h.y - 10, -380, u), z: lerp(4.2, 0.92, u), r: lerp(90, 0, smoother(seg(t, T(0, 8), T(0, 14)))) };
  S2.exam(ctx, cam, t, { blur: lerp(9, 2, u), shadows: x => { wallShadows(x, t, u); examDoctors(x, t, { behind: true, d3: { mouth: 'smirk', look: [0.3, 0.9] } }); }, fg: x => {
    lyingPatient(x, t, { eyes: 'wide', lid: 0, look: [Math.sin(t * 9), -0.6], brows: 'shock', mouth: 'eek', sweat: 1, shiver: 0.4 });
    examFront(x, t, { d1: { lean: 18, armR: [100, -10], handR: 'grip', propR: { fn: c => PR.magnifier(c, t), rot: 0, s: 0.8 }, look: [0.8, 0.6] }, d2: { armR: [70 + 15 * Math.sin(t * 14), 90], armL: [60 - 15 * Math.sin(t * 14), 95], handR: 'open', handL: 'open' } });
  } });
});
sfx(T(0, 8), 'whoosh', 0.7);
// O3: the reveal - jar thrust, lancet flick, drill raise (staggered on 16ths)
const R1 = B(1), R2 = T(1, 4), R3 = T(1, 6);
shot(B(1), T(1, 8), 'o_tools', (ctx, t, lt) => {
  const cam = shake({ x: 20, y: -300, z: 1.0 + lt * 0.08 }, t, [R1, R2, R3], 14);
  // anticipation (wind back) -> thrust with overshoot
  const thrust = (t0) => t < t0 - 0.12 ? 0 : t < t0 ? -0.35 * smooth(seg(t, t0 - 0.12, t0)) : clamp(spring(t - t0, 22, 9), -0.5, 1.2);
  const j = thrust(R1), l = thrust(R2), d = thrust(R3);
  S2.exam(ctx, cam, t, { blur: 2.5, shadows: x => { wallShadows(x, t, 1); examDoctors(x, t, { behind: true, d3: { armR: [lerp(25, 165, d), lerp(70, 20, d)], handR: 'grip', propR: { fn: c => PR.braceDrill(c, t * 3, pulse(t, R3 + 0.08, 0.3)), rot: 180, s: 0.9 }, mouth: 'smirk', lidLow: 0.3 } }); }, fg: x => {
    const look = t < R2 ? [0.9, -0.3] : t < R3 ? [-0.9, -0.2] : [0.1, -1];
    lyingPatient(x, t, { eyes: 'wide', lid: 0, look, brows: 'shock', mouth: 'eek', sweat: 1, shiver: 0.5 });
    examFront(x, t, {
      d1: { lean: 10, armR: [lerp(30, 120, l), lerp(80, 10, l)], handR: 'grip', propR: { fn: c => PR.fleam(c, t, pulse(t, R2 + 0.06, 0.3)), rot: 180, s: 1.3 }, armL: [lerp(20, 70, l), 60], handL: 'grip', propL: { fn: c => PR.bowl(c, 0, 20, 0.45), rot: 180 }, mouth: 'grin', brows: 'raised' },
      d2: { lean: 8 + 12 * j, armR: [lerp(40, 125, j), lerp(90, 10, j)], handR: 'grip', propR: { fn: c => PR.leechJar(c, 0, 0, 0.62, t, { n: 5, eyes: true }), rot: 180 }, armL: [30, 60], eyes: j > 0.5 ? 'happy' : 'open', mouth: 'grin' },
    });
  } });
});
sfx(R1, 'whoosh', 0.5); sfx(R2, 'shing', 0.5); sfx(R3, 'glint', 0.6);
// O4: the patient freaks out and leaps off the table
const LEAP = T(1, 12);
shot(T(1, 8), B(2), 'o_freak', (ctx, t, lt) => {
  const up = spring(t - T(1, 8), 24, 9);
  const cam = shake({ x: -60 - 200 * outC(seg(t, LEAP, B(2))), y: -360, z: 1.35 }, t, [T(1, 8), LEAP], 22);
  S2.exam(ctx, cam, t, { blur: 3, shadows: x => examDoctors(x, t, { behind: true, d3: { armL: [-10, 40], armR: [20, 50], brows: 'raised', mouth: 'o', lean: -6 } }), fg: x => {
    if (t < LEAP) {
      // springs bolt upright (sit-up) with squash & stretch, then crouches to jump (anticipation)
      const crouch = seg(t, LEAP - 0.14, LEAP);
      person(x, 'villager', V(t, { x: PAT.x - 60, y: -21 + 40 * crouch, s: 1, sit: 1, squash: 0.25 * crouch - 0.2 * Math.max(0, 1 - up), eyes: 'wide', lid: 0, brows: 'shock', mouth: 'scream', open: 1, tail: 80, armL: [-150, 30], armR: [150, 30], handL: 'spread', handR: 'spread', sweat: 1, face: -1, look: [-0.5, -0.4] }), false);
    } else {
      const k = seg(t, LEAP, B(2)), jx = lerp(PAT.x - 60, -880, outQ(k)), jy = lerp(-21, 260, k) - Math.sin(Math.PI * k) * 320;
      person(x, 'villager', V(t, Object.assign({ x: jx, y: jy, face: -1, eyes: 'wide', lid: 0, brows: 'shock', mouth: 'scream', open: 1, tail: 90, squash: -0.2 * Math.sin(Math.PI * k), vx: -2400, lean: 25 }, K.flail(t))), false);
    }
    examFront(x, t, { d1: { lean: -14, brows: 'raised', mouth: 'o', eyes: 'wide', armR: [140, 30], handR: 'spread', armL: [100, 40] }, d2: { lean: -16, brows: 'raised', mouth: 'o', eyes: 'wide', armR: [150, 20], armL: [110, 30], handR: 'spread', handL: 'spread', propR: { fn: c => PR.leechJar(c, 0, 0, 0.55, t, { n: 4 }), rot: 180 } } });
  } });
});
sfx(T(1, 8), 'swish', 0.6); sfx(LEAP, 'whoosh', 0.6);
// O5: escape attempt - running in place, held by the hood tail (build: snare roll)
shot(B(2), T(2, 8), 'o_escape', (ctx, t, lt) => {
  const u = seg(t, B(2), T(2, 8));
  const cam = { x: -470, y: -260, z: 1.25 + 0.35 * inQ(u), sx: Math.sin(t * 60) * 5 * u, sy: Math.cos(t * 53) * 4 * u };
  S2.exam(ctx, cam, t, { blur: 3.5, poolX: -120, fg: x => {
    const vx = -760;
    for (let i = 0; i < 4; i++) { const k = (t * 4 + i / 4) % 1; PR.puff(x, vx + 60 + k * 160, 250, 24 + k * 40, (1 - k) * 0.8, '#cbb48e'); }
    person(x, 'villager', V(t, Object.assign({ x: vx, y: 260, face: -1, eyes: 'wide', lid: 0, brows: 'shock', mouth: 'scream', open: 0.8 + 0.2 * Math.sin(t * 30), tail: -10, sweat: 1, vx: -3000 }, K.run(t * 34, 1.15), K.flail(t, 1), { lean: 34 })));
    // doc3 calmly holding the end of his hood tail
    person(x, 'doc3', V(t, { x: -120, y: 260, s: 1.12, face: -1, lid: 0.55, brows: 'calm', mouth: 'smirk', armR: [95, -10], handR: 'grip', armL: [20, 40], look: [0.6, 0.2], lean: -6 }));
    tube(x, [[vx + 70, -150], [-200, -150 + Math.sin(t * 30) * 8], [-277, -135]], 13, K.SPECS.villager.hoodDark, 4.5);
    person(x, 'doc1', V(t, { x: 360, y: 240, s: 1.1, face: -1, eyes: 'happy', mouth: 'chuckle', open: Math.abs(Math.sin(t * 14)), brows: 'raised', armR: [-30, -100], armL: [-30, -100], bob: Math.abs(Math.sin(t * 14)) * 6 }));
  } });
  speedLines(ctx, 540, 900, 18, 500, 1400, 0.18 * u, 7);
});
sfx(B(2), 'riser_soft', 0.45);
// O6: yanked back -> GASP (soundtrack gasp 4.962) -> doc1 lunges in -> zoom through into treatment 1
const GASP = 4.962;
shot(T(2, 8), B(3), 'o_gasp', (ctx, t, lt) => {
  const yank = seg(t, T(2, 8), T(2, 8) + 0.2);
  if (t < GASP - 0.02) {
    const cam = shake({ x: -300, y: -330, z: 1.3 }, t, [T(2, 8) + 0.2], 30);
    S2.exam(ctx, cam, t, { blur: 3, fg: x => {
      const vx = lerp(-760, -260, outBack(yank, 1.2));
      person(x, 'doc3', V(t, { x: -60, y: 260, s: 1.12, face: -1, lid: 0.5, brows: 'calm', mouth: 'flat', armR: [lerp(95, 40, yank), 40], handR: 'grip' }));
      person(x, 'villager', V(t, { x: vx, y: 260, face: 1, eyes: 'wide', lid: 0, brows: 'shock', mouth: 'o', tail: 50, squash: 0.25 * pulse(t, T(2, 8) + 0.2, 0.2), lean: -20, armL: [-60, 40], armR: [60, 40], handL: 'spread', handR: 'spread', vx: 2500 * (1 - yank) }));
    } });
  } else {
    const k = seg(t, GASP, B(3));
    const h = { x: 0, y: -380 };
    const cam = shake({ x: 0, y: -300, z: 2.5 + 1.8 * inC(seg(t, B(3) - 0.2, B(3))), r: -8 * inC(seg(t, B(3) - 0.2, B(3))) }, t, [GASP], 34);
    S2.exam(ctx, cam, t, { blur: 6, fg: x => {
      person(x, 'villager', V(t, { x: 0, y: 260, eyes: 'wide', lid: 0, pupil: 0.6, brows: 'shock', mouth: 'gasp', open: 1, tail: 90, sweat: 1, headSq: -0.12 * pulse(t, GASP, 0.25), armL: [-70, 30], armR: [70, 30], handL: 'spread', handR: 'spread', look: [0.6, -0.2] }));
      if (t > GASP + 0.2) { const l = outBack(seg(t, GASP + 0.2, GASP + 0.4)); person(x, 'doc1', V(t, { x: lerp(700, 330, l), y: 260, s: 1.1, face: -1, lean: 22, eyes: 'open', brows: 'angry', mouth: 'grin', armR: [110, 10], handR: 'grip', propR: { fn: c => PR.fleam(c, t, 1), rot: 180, s: 1.4 } })); }
    } });
    speedLines(ctx, 540, 820, 36, 420, 1400, 0.3, 12);
  }
});
sfx(T(2, 8) + 0.2, 'thud', 0.6);

// ================================================================ TREATMENT 1: BLOODLETTING (5.45 - 21.82)
const DROP1 = B(3);
// B1: in the chair; uroscopy - the doctor studies a flask against the window
shot(B(3), B(4), 'b_uroscopy', (ctx, t, lt) => {
  const cam = shake(F.camAt([{ t: DROP1, x: 40, y: -330, z: 0.95 }, { t: B(4), x: 60, y: -300, z: 1.12 }], t), t, [DROP1], 20);
  const plop = seg(t, DROP1, DROP1 + 0.25);
  S2.room('study', ctx, cam, t, { blur: 1.5, chair: -200, front: x => { E.candle(x, cam.x + 420, cam.y + 900, 120, t, 5); S2.bottleRow(x, cam.x - 560, cam.y + 950, 3, 4); }, fg: x => {
    person(x, 'villager', V(t, { x: -200, y: 140, sit: 1, squash: 0.3 * Math.max(0, 1 - spring(t - DROP1, 20, 8)) - 0.05, sick: 0.9, lid: 0.35, mouth: 'frown', brows: 'worried', look: [0.8, -0.6], armL: [20, 30], armR: [30, 40], handR: 'fist', bob: (1 - plop) * 200 }), true);
    const swirl = Math.sin(t * 7) * 12;
    person(x, 'doc1', V(t, Object.assign({ x: 260, y: 250, s: 1.1, face: -1, brows: 'skeptic', mouth: 'flat', lid: 0.35, lidLow: 0.3, look: [-0.2, -0.9], armR: [168 + swirl * 0.3, 20], handR: 'grip', propR: { fn: c => S2.flask(c, '#e7c25a', t, 1), rot: 180, s: 0.9 }, armL: [-30, -110], handL: 'fist', tilt: -8 }, K.idle(t, 3))));
    rays(x, -380, -1000, Math.PI * 0.32, 0.4, 1600, 5, 0.06, 9);
  } });
});
sfx(DROP1, 'thud', 0.7);
// B2: the verdict - astrology chart + book: TOO MUCH BLOOD
shot(B(4), T(4, 8), 'b_chart', (ctx, t, lt) => {
  const tap = T(4, 4), leap = T(4, 6);
  const cam = shake({ x: 110, y: -470, z: 1.2 + lt * 0.08 }, t, [tap, leap], 10);
  S2.room('study', ctx, cam, t, { blur: 0, desk: false, fg: x => {
    person(x, 'doc1', V(t, { x: 330, y: 250, s: 1.1, face: -1, brows: 'raised', mouth: t > leap ? 'grin' : 'o', lid: 0.1, look: [-0.8, -0.6], armR: [155 - 10 * pulse(t, tap, 0.15), 30], handR: 'point', armL: [-30, -110], handL: 'fist', tilt: -6, lean: -6 }));
    if (t > leap) for (let i = 0; i < 5; i++) sparkle(x, -100 + i * 90, -900 + Math.sin(i * 2 + t * 5) * 60, 28 * pulse(t, leap, 0.6), 1);
  } });
});
sfx(T(4, 4), 'tap', 0.5); sfx(T(4, 6), 'glint', 0.5);
shot(T(4, 8), T(5, 8), 'b_book', (ctx, t, lt) => {
  woodTable(ctx, '#5a3a24');
  const slam = T(4, 8), taps = [T(4, 12), B(5), T(5, 4)];
  cam1(ctx, shake({ x: 540, y: 960, z: 1.06 + lt * 0.08, r: -4 + lt * 2.5 }, t, [slam], 26), x => {
    E.candle(x, 950, 420, 120, t, 3);
    const open = outBack(seg(t, slam, slam + 0.14), 1.2);
    PR.openBook(x, 540, 980, 860, 1060, t, { open });
    if (open > 0.9) {
      let tb = 0; for (const tp of taps) tb += pulse(t, tp, 0.12);
      x.save(); x.translate(0, tb * 4);
      x.font = '62px "Unifraktur"'; x.fillStyle = '#5a1a12'; x.textAlign = 'center'; x.fillText('De Sanguine', 330, 560);
      shape(x, c => c.rect(150, 610, 90, 90), '#a3342b', { lw: 3, tex: false }); x.font = '70px "Unifraktur"'; x.fillStyle = '#f0dfb4'; x.fillText('B', 195, 680);
      x.globalAlpha = 0.65; for (let i = 0; i < 14; i++) { const yy = 640 + i * 44, x0 = i < 3 ? 260 : 150; x.beginPath(); x.moveTo(x0, yy); for (let k = 0; x0 + k * 14 < 500; k++) x.lineTo(x0 + k * 14, yy + Math.sin(k * 1.7 + i) * 4); x.lineWidth = 3; x.strokeStyle = '#3a2418'; x.stroke(); }
      x.globalAlpha = 1;
      // the moon + zodiac wheel: the "right day" to bleed
      x.save(); x.translate(760, 760); x.rotate(t * 0.4); for (let i = 0; i < 12; i++) { x.rotate(Math.PI / 6); line(x, [[0, -60], [0, -150]], 2.5, '#8a5a30'); } x.restore();
      shape(x, ell(760, 760, 60, 60), '#f2dfa0', { lw: 4, tex: false }); shape(x, ell(780, 750, 52, 56), '#f0dfb4', { lw: 0, tex: false });
      PR.figure(x, 760, 1160, 1.05, '#f08a7a');
      for (let i = 0; i < 6; i++) { const a = i * 1.05 + t * 0.6, rx = 760 + Math.cos(a) * 150, ry = 1080 + Math.sin(a) * 150; shape(x, c => { c.moveTo(rx, ry - 22); c.quadraticCurveTo(rx + 16, ry, rx, ry + 10); c.quadraticCurveTo(rx - 16, ry, rx, ry - 22); }, '#b3302a', { lw: 3, tex: false }); }
      x.restore();
    }
    // doctor's pointing hand (detailed) taps the diagram
    const tp = taps.reduce((a, tt) => a + pulse(t, tt, 0.14), 0);
    const hx = 860 - 60 * smooth(seg(t, slam + 0.15, slam + 0.35)), hy = 1180 + 220 * (1 - smooth(seg(t, slam + 0.1, slam + 0.35))) + tp * 18;
    tube(x, [[1200, 1720], [hx + 80, hy + 130]], 74, '#3b2c41', 6);
    x.save(); x.translate(hx + 60, hy + 80); x.rotate(2.6); x.scale(1.9, 1.9); K.hand(x, 'point', '#eec09a', 1); x.restore();
    if (open > 0.9) for (let i = 0; i < 6; i++) { const k = seg(t, slam, slam + 0.5); PR.puff(x, 540 + (i - 2.5) * 170 * (1 + k), 470 + (i % 2) * 980 - k * 60, 40 + k * 60, (1 - k) * 0.8, '#e8d8b8'); }
  });
  vignette(ctx, 0.55);
});
sfx(T(4, 8), 'book_slam', 1); for (const tp of [T(4, 12), B(5), T(5, 4)]) sfx(tp, 'tap', 0.35);
// B2c: "obviously" - he pushes up his spectacles (glint on the beat)
shot(T(5, 8), B(6), 'b_smug', (ctx, t, lt) => {
  const gl = T(5, 12), h = { x: 300, y: K.headY('doc1', { y: 250, s: 1.1 }) };
  const cam = frameHead(h.x, h.y, 2.5 + lt * 0.2, 840);
  S2.room('study', ctx, cam, t, { blur: 8, desk: false, fg: x => {
    const push = seg(t, T(5, 8) + 0.05, gl);
    person(x, 'doc1', V(t, { x: 300, y: 250, s: 1.1, face: -1, brows: 'skeptic', mouth: 'smirk', lid: 0.35, lidLow: 0.3, tilt: -6 + 4 * Math.sin(t * 6), armR: [lerp(40, 168, smooth(push)), lerp(60, 145, smooth(push))], handR: 'point', look: [0.2, 0] }));
    if (t > gl) sparkle(x, 262, h.y - 2, 60 * pulse(t, gl, 0.45), 1);
  } });
});
sfx(T(5, 12), 'glint', 0.5);
// B3: the four humours: a glass-body diagram, blood overflowing (+ doctor cameo chuckle at 12.27/12.50)
const HUM = [
  { t: B(6), name: 'Blood', c: '#b3302a' }, { t: T(6, 4), name: 'Phlegm', c: '#a8cfe0' },
  { t: T(6, 8), name: 'Yellow bile', c: '#e6b23a' }, { t: T(6, 12), name: 'Black bile', c: '#3a2a3a' },
];
shot(B(6), B(8), 'b_humours', (ctx, t, lt) => {
  parchment(ctx);
  const over = T(7, 4), stamp = T(7, 8);
  const cam = shake(F.camAt([{ t: B(6), x: 540, y: 980, z: 1.18 }, { t: B(7), x: 540, y: 960, z: 1.05 }, { t: B(8), x: 540, y: 940, z: 1.12 }], t), t, [over, stamp], 16);
  cam1(ctx, cam, x => {
    x.font = '84px "Unifraktur"'; x.fillStyle = '#4a1a10'; x.textAlign = 'center'; x.fillText('The Four Humours', 540, 300);
    line(x, [[220, 340], [860, 340]], 3, '#8a5a30');
    // glass silhouette of the patient
    const body = c => { c.moveTo(540, 470); c.bezierCurveTo(660, 470, 680, 620, 600, 680); c.lineTo(700, 740); c.lineTo(720, 1200); c.lineTo(640, 1200); c.lineTo(630, 1500); c.lineTo(450, 1500); c.lineTo(440, 1200); c.lineTo(360, 1200); c.lineTo(380, 740); c.lineTo(480, 680); c.bezierCurveTo(400, 620, 420, 470, 540, 470); c.closePath(); };
    shape(x, body, 'rgba(255,250,235,0.6)', { lw: 6, tex: false });
    x.save(); x.beginPath(); body(x); x.clip();
    // layered fluids filling up, blood keeps rising past its share (imbalance)
    let y = 1500;
    HUM.forEach((h, i) => {
      if (t < h.t) return;
      const k = outC(seg(t, h.t, h.t + 0.3));
      let share = i === 0 ? 200 + 520 * smooth(seg(t, B(7), over + 0.2)) : 170;
      const hh = share * k; x.fillStyle = h.c;
      x.beginPath(); x.moveTo(300, y); x.lineTo(300, y - hh + Math.sin(t * 5 + i) * 6); for (let px = 300; px <= 780; px += 20) x.lineTo(px, y - hh + Math.sin(t * 5 + px * 0.03 + i) * 6); x.lineTo(780, y); x.closePath(); x.fill();
      y -= hh;
    });
    x.restore();
    shape(x, body, null, { lw: 6 });
    // labels popping in on each beat
    HUM.forEach((h, i) => {
      if (t < h.t) return; const k = outBack(seg(t, h.t, h.t + 0.2), 2.4);
      const lx = i % 2 ? 860 : 220, ly = 640 + Math.floor(i / 2) * 360 + (i % 2) * 120;
      x.save(); x.translate(lx, ly); x.scale(k, k);
      shape(x, ell(0, 0, 112, 112), '#f3e4c0', { lw: 5 }); shape(x, c => { c.moveTo(0, -55); c.quadraticCurveTo(48, 10, 0, 42); c.quadraticCurveTo(-48, 10, 0, -55); }, h.c, { lw: 4, tex: false, hi: { x: -14, y: -6, r: 30, a: 0.5 } });
      x.font = '38px "IM Fell SC"'; x.fillStyle = '#3a1a10'; x.textAlign = 'center'; x.fillText(h.name, 0, 160); x.restore();
    });
    if (t > over) { // overflow drips from the head
      for (let i = 0; i < 4; i++) { const k = ((t - over) * 1.5 + i * 0.25) % 1; shape(x, c => { const dx = 500 + i * 30, dy = 470 + k * 300; c.moveTo(dx, dy - 22); c.quadraticCurveTo(dx + 16, dy, dx, dy + 10); c.quadraticCurveTo(dx - 16, dy, dx, dy - 22); }, '#b3302a', { lw: 3, tex: false }); }
    }
    if (t > stamp) { const k = outBack(seg(t, stamp, stamp + 0.12), 2.5); x.save(); x.translate(540, 1640); x.rotate(-0.08); x.scale(k, k); x.lineWidth = 10; x.strokeStyle = '#b3302a'; x.strokeRect(-300, -64, 600, 128); x.font = '70px "Cinzel Black"'; x.fillStyle = '#b3302a'; x.textAlign = 'center'; x.textBaseline = 'middle'; x.fillText('IMBALANCE!', 0, 6); x.restore(); }
  });
  // doctor cameo chuckling (soundtrack chuckles at 12.273 / 12.500)
  const cin = seg(t, 12.12, 12.27), cout = seg(t, 12.95, 13.1);
  if (cin > 0 && cout < 1) {
    const px = lerp(-200, 210, outBack(cin)) - 420 * inQ(cout), py = 1500;
    ctx.save(); ctx.beginPath(); ctx.arc(px, py, 170, 0, 7); ctx.fillStyle = '#4a3020'; ctx.fill(); ctx.clip();
    const ch = pulse(t, 12.273, 0.2) + pulse(t, 12.5, 0.2);
    F.withCam(ctx, { x: 300 - (px - 540) / 1.6, y: -320 - (py - 960) / 1.6, z: 1.6 }, 1, x => person(x, 'doc1', V(t, { x: 300, y: 250, s: 1.08, face: -1, eyes: 'happy', mouth: 'chuckle', open: ch, tilt: -8 + ch * 8, bob: ch * 10, armR: [150, 60], handR: 'open' }), false));
    ctx.restore(); ctx.lineWidth = 10; ctx.strokeStyle = '#c9973a'; ctx.beginPath(); ctx.arc(px, py, 170, 0, 7); ctx.stroke();
  }
});
for (const h of HUM) sfx(h.t, 'pop', 0.45); sfx(T(7, 4), 'clunk', 0.6); sfx(T(7, 8), 'stamp', 0.7);
// B4: preparation - tourniquet tug-tug, staff to grip, bowl placed
const TUG = [B(8), T(8, 4)], STAFF = T(8, 8), BOWL = T(8, 12);
shot(B(8), B(9), 'b_prep', (ctx, t, lt) => {
  const cam = shake({ x: -20, y: -260, z: 1.6 + lt * 0.08 }, t, [...TUG, STAFF, BOWL], 9);
  S2.room('study', ctx, cam, t, { blur: 4, chair: -230, front: x => S2.bottleRow(x, cam.x + 300, cam.y + 980, 3, 7), fg: x => {
    const tug = TUG.reduce((a, tt) => a + pulse(t, tt, 0.18), 0);
    const hasStaff = t > STAFF;
    person(x, 'villager', V(t, { x: -230, y: 140, sit: 1, sick: 0.9, eyes: 'wide', lid: 0, brows: 'worried', mouth: tug > 0.3 ? 'eek' : 'teeth', look: [0.9, 0.3], armR: [100, -5], handR: hasStaff ? 'grip' : 'open', propR: hasStaff ? { fn: c => S2.staff(c), rot: 90 } : null, armL: [20, 30], squash: tug * 0.06, sweat: 1, shiver: 0.3 }));
    // tourniquet band on the upper arm
    shape(x, c => c.roundRect(-95, -312, 30, 46, 6), '#e8dcc0', { lw: 4 });
    person(x, 'doc1', V(t, { x: 220, y: 250, s: 1.1, face: -1, brows: 'angry', mouth: 'smirk', lid: 0.3, look: [-0.6, 0.6], lean: 22 + tug * 6, armR: [80 - tug * 25, 60], handR: 'grip', armL: [60 + tug * 15, 70], handL: 'grip', ...K.idle(t, 5, 0.5) }));
    if (t > BOWL) { const k = outBack(seg(t, BOWL, BOWL + 0.2)); PR.bowl(x, lerp(400, 40, k), -40, 0.7); }
  } });
});
for (const tt of TUG) sfx(tt, 'swish', 0.45); sfx(STAFF, 'tap', 0.4); sfx(BOWL, 'clink', 0.55);
// B5: lancet glint + eyes squeezed shut
shot(B(9), T(9, 8), 'b_brace', (ctx, t, lt) => {
  const h = { x: -230, y: K.headY('villager', { y: 140, sit: 1 }) };
  const cam = shake(frameHead(h.x, h.y, 2.4 + lt * 0.3, 860), t, [B(9), T(9, 4)], 16);
  S2.room('study', ctx, cam, t, { blur: 7, chair: -230, fg: x => {
    person(x, 'villager', V(t, { x: -230, y: 140, sit: 1, sick: 0.9, eyes: 'squeeze', brows: 'worried', mouth: 'eek', armR: [100, -5], handR: 'grip', propR: { fn: c => S2.staff(c), rot: 90 }, sweat: 1, shiver: 0.6, tilt: -12, turn: -0.5 }));
  } });
  ctx.save(); ctx.translate(820, 640); ctx.rotate(-0.6); ctx.scale(2.2, 2.2); PR.fleam(ctx, t, pulse(t, T(9, 4), 0.3) + pulse(t, B(9), 0.3)); ctx.restore();
});
sfx(B(9), 'shing', 0.5); sfx(T(9, 4), 'shing', 0.45);
// B6: the treatment, told in shadow on the wall (non-graphic) + hourglass
shot(T(9, 8), B(10), 'b_shadowplay', (ctx, t, lt) => {
  ctx.fillStyle = '#2a1c16'; ctx.fillRect(0, 0, W, H);
  const cam = { x: 0, y: -500, z: 1.0 + lt * 0.1 };
  cam1(ctx, cam, x => {
    E.stoneWall(x, -700, -1500, 700, 400, '#b8a184', 77, 150, 74);
    const g = x.createRadialGradient(80, -500, 50, 80, -500, 900); g.addColorStop(0, 'rgba(255,200,120,0.55)'); g.addColorStop(1, 'rgba(40,20,10,0.75)');
    x.fillStyle = g; x.fillRect(-700, -1500, 1400, 1900);
    // big soft silhouettes: patient seated gripping the staff, doctor leaning in; flick on the hook leap
    const flick = pulse(t, T(9, 14), 0.2);
    S2.castShadow(x, y => {
      K.drawPerson(y, 'villager', V(t, { x: -260, y: 300, s: 1.5, sit: 1, armR: [100, -5], propR: { fn: c => S2.staff(c), rot: 90 }, tilt: -10 - 8 * flick, shiver: 0.5 }));
      K.drawPerson(y, 'doc1', V(t, { x: 300, y: 330, s: 1.6, face: -1, lean: 24 + 6 * flick, armR: [85 + 20 * flick, 40], propR: { fn: c => PR.fleam(c, t, 0), rot: 180, s: 1.2 } }));
    }, { ax: 0, ay: 330, dx: 0, dy: -60, sx: 1.0, sy: 1.0, skew: 0, alpha: 0.82, blur: 5, color: 'rgb(25,12,8)' });
  });
  S2.hourglass(ctx, 860, 1520, 1.25, seg(t, T(9, 8), B(10) + 1.6), t);
  vignette(ctx, 0.5);
});
sfx(T(9, 14), 'swish', 0.4);
// B7: consequence - pale, swaying; the doctor is delighted
shot(B(10), B(11), 'b_pale', (ctx, t, lt) => {
  const cam = { x: 40, y: -260, z: 1.08 + lt * 0.08 };
  S2.room('study', ctx, cam, t, { blur: 1.2, chair: -200, fg: x => {
    const sway = Math.sin(t * 2.6) * 9;
    person(x, 'villager', V(t, { x: -200, y: 140, sit: 1, pale: smooth(seg(t, B(10), B(10) + 0.7)), lid: 0.62, mouth: 'wavy', brows: 'sad', rot: sway, armL: [5, 5], armR: [-5, 5], handL: 'relaxed', handR: 'relaxed', tail: -10, look: [0.1, 0.5] }));
    shape(x, c => c.roundRect(-95, -312, 30, 46, 6), '#e8dcc0', { lw: 4 });
    person(x, 'doc1', V(t, { x: 300, y: 250, s: 1.1, face: -1, eyes: 'happy', mouth: 'smile', brows: 'raised', armL: [-35, -120], armR: [-35, -120], handL: 'fist', handR: 'fist', tilt: -6, lean: -6, bob: Math.abs(Math.sin(t * 5)) * 4 }));
    PR.bowl(x, 560, -170, 0.75, true);
    sparkle(x, 380, -560 + Math.sin(t * 3) * 10, 30 + 10 * Math.sin(t * 8), 0.9);
  } });
});
// B8: stop-time: three punches -> topples -> shoved toward the leech shop ("oh!" 21.36)
const P3 = [B(11), T(11, 3), T(11, 6)];
shot(B(11), B(12), 'b_stoptime', (ctx, t, lt) => {
  const i = t < P3[1] ? 0 : t < P3[2] ? 1 : 2, out = t > T(11, 8);
  const cam = out ? F.camAt([{ t: T(11, 8), x: -380, y: -300, z: 1.0 }, { t: B(12), x: -560, y: -290, z: 1.18 }], t) : shake({ x: -200, y: -230, z: [1.35, 1.55, 1.8][i] + (t - P3[i]) * 0.1, r: [-3, 3, 0][i] }, t, P3, 26);
  S2.room('study', ctx, cam, t, { blur: out ? 1 : 2.5, chair: -200, fg: x => {
    if (!out) {
      const poses = [{ rot: -16, eyes: 'spiral', tilt: -12, armL: [40, 40] }, { rot: 18, eyes: 'spiral', tilt: 14, tail: 30, armR: [-40, 40] }, { rot: 62, eyes: 'dead', tilt: 20, tail: 50, armL: [120, 20], armR: [100, 20], handL: 'spread', handR: 'spread' }];
      person(x, 'villager', V(t, Object.assign({ x: -200, y: 140, sit: 1, pale: 1, mouth: 'wavy' }, poses[i])));
      person(x, 'doc1', V(t, { x: 330, y: 250, s: 1.1, face: -1, brows: 'raised', mouth: 'smile', eyes: 'happy', armR: [150, 20], handR: 'thumb', armL: [-35, -120], handL: 'fist' }));
    } else {
      const k = seg(t, T(11, 8), B(12)), oh = t > 21.36;
      // the far door opens onto the green glow of the leech shop
      shape(x, c => c.rect(-1060, -560, 280, 560), '#123024', { lw: 6 }); D.glow(x, -920, -300, 420, '120,230,170', 0.6 * smooth(seg(t, T(11, 9), T(11, 11))));
      x.save(); x.translate(-1060, -560); x.scale(1 - 0.85 * smooth(seg(t, T(11, 8), T(11, 10))), 1); shape(x, c => c.rect(0, 0, 280, 560), PAL.wood, { lw: 6 }); x.restore();
      person(x, 'villager', V(t, Object.assign({ x: lerp(-320, -760, outQ(k)), y: 230, pale: 1, mouth: oh ? 'o' : 'wavy', eyes: oh ? 'wide' : 'open', lid: oh ? 0 : 0.6, brows: oh ? 'shock' : 'worried', face: -1, tail: 30, vx: -700, headSq: oh ? 0.1 * pulse(t, 21.36, 0.2) : 0 }, K.walk(t * 9, 0.9))));
      person(x, 'doc1', V(t, { x: lerp(-60, -420, outQ(k)), y: 250, s: 1.1, face: -1, brows: 'raised', mouth: 'smile', eyes: 'happy', armR: [95, 0], handR: 'open', armL: [80, 10], handL: 'open', lean: 14, vx: -500 }));
    }
  } });
});
for (const p of P3) sfx(p, 'freeze_hit', 0.7); sfx(T(11, 8), 'door', 0.5);

// ================================================================ TREATMENT 2: LEECHES (21.82 - 38.18)
// L1: the leech doctor slides down a ladder to greet him
const LAND = T(12, 6);
shot(B(12), B(13), 'l_greet', (ctx, t, lt) => {
  const cam = shake(F.camAt([{ t: B(12), x: 20, y: -330, z: 1.08 }, { t: B(13), x: 60, y: -290, z: 1.2 }], t), t, [LAND], 18);
  S2.room('shop', ctx, cam, t, { blur: 1.5, counter: false, front: x => { E.jar(x, cam.x + 430, cam.y + 960, 60, 180, '#7fb5a0', true, 3, t); }, fg: x => {
    S2.ladder(x, 420, -1300, 260);
    const k = seg(t, B(12), LAND), land = t > LAND;
    const y = land ? 250 : lerp(-900, 250, inQ(k));
    person(x, 'doc2', V(t, land
      ? { x: 380, y, s: 1.05, face: -1, eyes: 'happy', mouth: 'grin', brows: 'raised', squash: 0.3 * Math.exp(-(t - LAND) * 9) * Math.cos((t - LAND) * 30), armL: [-140, 20], armR: [140, 20], handL: 'open', handR: 'open', bob: 0 }
      : { x: 420, y, s: 1.05, face: -1, eyes: 'happy', mouth: 'grin', armL: [-170, 10], armR: [170, 10], handL: 'grip', handR: 'grip', squash: -0.15 }));
    const enter = seg(t, B(12), T(12, 10));
    person(x, 'villager', V(t, Object.assign({ x: lerp(-560, -230, outQ(enter)), y: 260, pale: 0.8, lid: land ? 0.1 : 0.5, eyes: land ? 'wide' : 'open', mouth: land ? 'o' : 'wavy', brows: land ? 'shock' : 'sad', look: [0.9, -0.2], sweat: land ? 1 : 0, vx: enter < 1 ? 600 : 0 }, enter < 1 ? K.walk(t * 7, 0.7) : K.idle(t, 9))));
  } });
});
sfx(LAND, 'thud', 0.6);
// L2: fishing a leech out of the jar with tweezers -> right under his nose (24.55)
const FISH = T(13, 8);
shot(B(13), B(14), 'l_fish', (ctx, t, lt) => {
  const cam = shake({ x: -20, y: -330, z: 1.45 + lt * 0.1 }, t, [FISH], 12);
  S2.room('shop', ctx, cam, t, { blur: 4, counterX: 250, back: x => {
    const pull = seg(t, FISH - 0.25, FISH + 0.1);
    person(x, 'doc2', V(t, { x: 250, y: 60, s: 1.05, face: -1, eyes: 'open', mouth: 'grin', brows: 'raised', look: [-0.4, 0.4], armL: [40, 80], handL: 'grip', propL: { fn: c => PR.leechJar(c, 0, 0, 0.6, t, { n: 5 }), rot: 180 }, armR: [lerp(40, 110, outBack(pull)), lerp(80, 20, pull)], handR: 'grip', propR: { fn: c => { PR.tweezers(c); PR.leech(c, 0, -110, 110, t, 4, { eyes: true, smile: true, amp: 1.4, ang: 80 }); }, rot: 180, s: 1.1 } }));
  }, fg: x => {
    const cross = t > FISH + 0.1;
    person(x, 'villager', V(t, { x: -250, y: 260, pale: 0.6, eyes: cross ? 'open' : 'wide', look: cross ? [0.9, 0.3] : [0.7, -0.1], lid: 0, brows: 'worried', mouth: cross ? 'eek' : 'o', lean: -8 - 8 * seg(t, FISH, FISH + 0.3), armL: [-40, 80], armR: [40, 90], handL: 'fist', handR: 'fist', sweat: 1, ...K.idle(t, 11, 0.6) }));
  } });
});
sfx(T(13, 8), 'squelch', 0.5);
// L3: ECU - the leech wriggles, cross-eyed patient (explanation line)
shot(B(14), B(15), 'l_ecu', (ctx, t, lt) => {
  const h = { x: -250, y: K.headY('villager', { y: 260 }) };
  const cam = frameHead(h.x, h.y, 3.0 + lt * 0.25, 900, -160);
  S2.room('shop', ctx, cam, t, { blur: 9, counter: false, fg: x => {
    person(x, 'villager', V(t, { x: -250, y: 260, pale: 0.6, eyes: 'open', lid: 0, pupil: 0.8, look: [0.6, 0.5], brows: 'worried', mouth: 'wavy', sweat: 1, tilt: -6 }));
  } });
  ctx.save(); ctx.translate(820, 980); ctx.rotate(Math.sin(t * 5) * 0.18); ctx.scale(1.6, 1.6); PR.tweezers(ctx); PR.leech(ctx, 0, -120, 150, t, 2, { eyes: true, smile: true, amp: 1.5, ang: 85 }); ctx.restore();
});
// L4: he tries to back away; she pins his wrist to the cushion with a grin
shot(B(15), 28.6, 'l_wrist', (ctx, t, lt) => {
  const grab = T(15, 4);
  const cam = shake({ x: -40, y: -300, z: 1.3 + lt * 0.08 }, t, [grab], 14);
  S2.room('shop', ctx, cam, t, { blur: 2.5, counterX: 260, back: x => {
    shape(x, c => c.roundRect(0, -260, 260, 70, 30), '#7a2a2a', { lw: 5 });
    const g = outBack(seg(t, grab - 0.1, grab + 0.1));
    person(x, 'doc2', V(t, { x: 290, y: 60, s: 1.05, face: -1, eyes: 'happy', mouth: 'grin', lean: 14, armR: [lerp(40, 105, g), 20], handR: 'grip', armL: [40, 80], handL: 'grip', propL: { fn: c => PR.tweezers(c), rot: 180 } }));
  }, fg: x => {
    const g = seg(t, grab, grab + 0.15);
    person(x, 'villager', V(t, { x: lerp(-330, -160, g), y: 260, pale: 0.6, eyes: 'wide', lid: 0, brows: 'shock', mouth: 'eek', lean: lerp(-14, 10, g), armR: [lerp(30, 95, g), 0], handR: 'spread', armL: [-60, 60], handL: 'spread', sweat: 1, tail: 40 }));
  } });
});
sfx(T(15, 4), 'swish', 0.5);
// L5: she giggles (soundtrack chuckles at 28.636 / 28.864)
shot(28.6, B(16), 'l_chuckle', (ctx, t, lt) => {
  const h = { x: 330, y: K.headY('doc2', { y: 60, s: 1.05 }) };
  const cam = frameHead(h.x, h.y, 2.6, 820);
  S2.room('shop', ctx, cam, t, { blur: 6, counterX: 330, back: x => {
    const ch = pulse(t, 28.636, 0.2) + pulse(t, 28.864, 0.2);
    person(x, 'doc2', V(t, { x: 330, y: 60, s: 1.05, face: -1, eyes: 'happy', mouth: 'chuckle', open: ch, brows: 'raised', tilt: -6 + ch * 8, bob: ch * 14, headSq: -0.06 * ch, armR: [130, 60], handR: 'open', armL: [40, 80] }));
  } });
});
// L6: three leeches placed on the arm on the beats of the mini-break
const PLACE = [T(16, 4), T(16, 8), T(16, 12)], SPOTS = [[440, 1040], [590, 1050], [730, 1040]];
function arm(ctx, t, o = {}) {
  shape(ctx, c => c.roundRect(60, 900, 960, 360, 120), '#7a2a2a', { lw: 6, shade: { x0: 0, y0: 900, x1: 0, y1: 1260, a: 0.35 } });
  const fl = o.flinch || 0, skin = o.pale ? mixh('#f1c49b', '#c3d3a0', o.pale) : '#f1c49b';
  ctx.save(); ctx.translate(0, Math.sin(t * 70) * fl * 4);
  tube(ctx, [[-60, 1060], [300, 1060]], 170, '#7d8a3d', 6);
  ctx.save(); ctx.globalAlpha = 0.4; for (let i = 0; i < 4; i++) curve(ctx, [40 + i * 60, 990], [60 + i * 60, 1060], [40 + i * 60, 1130], 4, '#4b5126'); ctx.restore();
  tube(ctx, [[300, 1062], [860, 1050]], 130, skin, 6);
  ctx.save(); ctx.translate(860, 1050); ctx.rotate(-1.57); ctx.scale(3.0, 3.0); K.hand(ctx, fl > 0.3 ? 'spread' : 'open', skin, 1); ctx.restore();
  ctx.restore();
}
shot(B(16), B(17), 'l_place', (ctx, t, lt) => {
  woodTable(ctx, '#4a3020');
  cam1(ctx, shake({ x: 540, y: 1000, z: 1.12 + lt * 0.06, r: 3 - lt * 2 }, t, PLACE, 8), x => {
    let fl = 0; for (const p of PLACE) fl += pulse(t, p, 0.25);
    arm(x, t, { flinch: fl });
    PLACE.forEach((p, i) => {
      if (t < p) return;
      const k = t - p, sq = 1 + 0.5 * Math.exp(-k * 14) * Math.cos(k * 45);
      x.save(); x.translate(SPOTS[i][0], SPOTS[i][1]); x.scale(sq, 1 / sq); PR.leech(x, 0, 0, 175, t, i, { amp: 0.35, ang: 20 - i * 18, eyes: true, smile: true, fat: 1.15 }); x.restore();
      if (k < 0.3) for (let j = 0; j < 4; j++) sparkle(x, SPOTS[i][0] + Math.cos(j * 1.6) * 90 * (0.5 + k * 2), SPOTS[i][1] + Math.sin(j * 1.6) * 90 * (0.5 + k * 2), 22 * (1 - k / 0.3), 1);
    });
    const next = PLACE.find(p => t < p + 0.1) || PLACE[2], idx = PLACE.indexOf(next), tgt = SPOTS[idx];
    const a = seg(t, next - 0.32, next), hx = lerp(900, tgt[0] + 40, smooth(a)), hy = lerp(420, tgt[1] - 200, smooth(a)) + (t > next ? -200 * seg(t, next, next + 0.2) : 0);
    tube(x, [[1200, 200], [hx + 60, hy - 120]], 70, '#d39a35', 6);
    x.save(); x.translate(hx + 40, hy - 90); x.rotate(0.6); x.scale(2.0, 2.0); K.hand(x, 'grip', '#f3c9a2', 1); x.restore();
    x.save(); x.translate(hx + 10, hy - 40); x.rotate(0.5); x.scale(1.2, 1.2); PR.tweezers(x); x.restore();
    if (t < next) PR.leech(x, hx, hy + 30, 130, t, 7, { amp: 1.4, ang: 70, eyes: true });
  });
});
for (const p of PLACE) sfx(p, 'plop', 0.55);
// L7: his face while they drink
shot(B(17), T(17, 8), 'l_face', (ctx, t, lt) => {
  const h = { x: -160, y: K.headY('villager', { y: 260 }) };
  const cam = frameHead(h.x, h.y, 2.5 + lt * 0.15, 840);
  S2.room('shop', ctx, cam, t, { blur: 7, counter: false, fg: x => {
    const tw = Math.floor(t * 9) % 3 === 0 ? 0.65 : 0.12;
    person(x, 'villager', V(t, { x: -160, y: 260, pale: 0.4 + 0.3 * lt, lid: tw, mouth: 'wavy', brows: 'worried', look: [0.6, 0.9], sweat: 1, tilt: 8, shiver: 0.25 }));
  } });
  S2.hourglass(ctx, 860, 1560, 1.1, seg(t, B(17) - 0.5, B(18)), t);
});
// L8: they swell, then drop off when full - into the dish
shot(T(17, 8), B(18), 'l_full', (ctx, t, lt) => {
  woodTable(ctx, '#4a3020');
  const gulps = [T(17, 8), T(17, 12)], DROP = T(17, 14);
  cam1(ctx, shake({ x: 590, y: 1060, z: 1.4 + lt * 0.1 }, t, [...gulps, DROP], 8), x => {
    arm(x, t, { pale: 0.6 });
    S2.dish(x, 590, 1420, 1.6);
    const fat = 1.15 + 0.6 * smooth(seg(t, T(17, 8), DROP));
    SPOTS.forEach((s, i) => {
      const g = gulps.reduce((a, gt) => a + pulse(t, gt + i * 0.04, 0.15), 0);
      const fall = seg(t, DROP + i * 0.04, DROP + i * 0.04 + 0.22);
      const y = s[1] + 360 * inQ(fall), ang = 20 - i * 18 + fall * 60;
      x.save(); x.translate(s[0] + (i - 1) * 40 * fall, y); x.scale(1 + g * 0.18, 1 + g * 0.18); PR.leech(x, 0, 0, 175, t, i, { amp: 0.15, ang, eyes: true, smile: true, fat }); x.restore();
    });
    for (let i = 0; i < 6; i++) { const k = (t * 1.2 + i / 6) % 1; x.save(); x.globalAlpha = 1 - k; star(x, 590 + Math.cos(i) * 260, 900 - k * 220, 16, t, '#ffe27a', 3); x.restore(); }
  });
});
for (const g of [T(17, 8), T(17, 12)]) sfx(g, 'gulp', 0.45); sfx(T(17, 14), 'plop', 0.6);
// L9: woozy - and she reaches for MORE leeches -> he bolts out of the door (groove back 32.73)
const BOLT = T(18, 6);
shot(B(18), B(19), 'l_bolt', (ctx, t, lt) => {
  const cam = shake({ x: 40 - 200 * outC(seg(t, BOLT, B(19))), y: -310, z: 1.12 }, t, [BOLT], 16);
  S2.room('shop', ctx, cam, t, { blur: 1.8, counterX: 330, back: x => {
    const reach = smooth(seg(t, B(18), BOLT));
    person(x, 'doc2', V(t, { x: 340, y: 60, s: 1.05, face: -1, eyes: 'happy', mouth: 'grin', brows: 'raised', armR: [lerp(40, 120, reach), 20], handR: 'grip', propR: { fn: c => PR.leechJar(c, 0, 0, 0.6, t, { n: 6, eyes: true }), rot: 180 }, armL: [-20, 90], handL: 'point', lean: -4 }));
  }, fg: x => {
    if (t < BOLT) person(x, 'villager', V(t, { x: -200, y: 260, pale: 0.9, lid: 0.55 - 0.55 * seg(t, BOLT - 0.3, BOLT), eyes: t > BOLT - 0.3 ? 'wide' : 'open', mouth: t > BOLT - 0.3 ? 'eek' : 'wavy', brows: t > BOLT - 0.3 ? 'shock' : 'sad', rot: Math.sin(t * 3) * 6, armL: [5, 10], armR: [-5, 10], tail: 10, squash: 0.15 * seg(t, BOLT - 0.15, BOLT) }));
    else { const k = seg(t, BOLT, BOLT + 0.5); person(x, 'villager', V(t, Object.assign({ x: lerp(-200, -1400, inQ(k)), y: 260, face: -1, pale: 0.9, eyes: 'wide', mouth: 'scream', open: 1, brows: 'shock', tail: 90, vx: -3000 }, K.run(t * 30, 1.2), K.flail(t), { lean: 30 }))); for (let i = 0; i < 5; i++) PR.puff(x, -200 - i * 120 * k, 250, 40 + k * 40, (1 - k) * 0.8, '#bfae8a'); }
  } });
});
sfx(T(18, 6), 'zip', 0.7);
// L10: the chase through a dusk alley (side tracking, posts whipping past)
const CH0 = B(19), chaseX = t => 400 + (t - CH0) * 640;
shot(B(19), B(20), 'l_chase', (ctx, t, lt) => {
  const vx = chaseX(t);
  S2.alley(ctx, { x: vx - 120, y: -230, z: 1.0 }, t, { fg: x => {
    person(x, 'doc2', V(t, Object.assign({ x: vx - 560 + Math.sin(t * 3) * 30, y: 250, s: 1.05, face: 1, eyes: 'happy', mouth: 'grin', brows: 'raised', propR: { fn: c => PR.leechJar(c, 0, 0, 0.5, t, { n: 4, eyes: true }), rot: 180 }, vx: 640 }, K.run(t * 15, 0.85), { armR: [130 + Math.sin(t * 15) * 20, 20], handR: 'grip', armL: [-60, 60], handL: 'open' })));
    person(x, 'villager', V(t, Object.assign({ x: vx, y: 260, pale: 0.6, eyes: 'wide', mouth: 'scream', open: 1, brows: 'shock', sweat: 1, tail: 70, look: [-0.8, 0], turn: -0.5, vx: 640 }, K.run(t * 17, 1), K.flail(t))));
    for (let i = 0; i < 5; i++) { const k = ((t * 3 + i / 5) % 1); PR.puff(x, vx - 60 - k * 300, 255 - k * 30, 30 + k * 40, (1 - k) * 0.7, '#bfae8a'); }
  } });
});
// L11: relief... "oh!" (37.727) ... the low beam (BONK at the drop 38.18)
const OH2 = 37.727, BONK = B(21);
const vxRun = t => chaseX(B(20)) + (t - B(20)) * 430;
const BEAMX = () => vxRun(BONK) + 215;
function beamEnd(x, bx, wob = 0) {
  shape(x, c => c.rect(bx - 28 + wob * 0.3, -1600, 56, 1400), PAL.beam, { lw: 6, shade: { x0: bx - 28, y0: 0, x1: bx + 28, y1: 0, a: 0.35 } });
  x.save(); x.translate(bx + wob, -150); x.rotate(wob * 0.01);
  shape(x, c => c.roundRect(-62, -80, 124, 150, 10), '#6a4428', { lw: 7, shade: { x0: -60, y0: 0, x1: 60, y1: 0, a: 0.3 } });
  for (let r = 1; r < 4; r++) { x.save(); x.globalAlpha = 0.6; x.beginPath(); x.ellipse(0, -5, 14 * r, 18 * r, 0, 0, 7); x.lineWidth = 3; x.strokeStyle = '#3a2414'; x.stroke(); x.restore(); }
  x.restore();
}
shot(B(20), B(21), 'l_relief', (ctx, t, lt) => {
  const vx = vxRun(t), see = t > OH2;
  const cam = see ? shake({ x: vx + 120 + 200 * outC(seg(t, OH2, BONK)), y: -70, z: 2.1 - 0.9 * outC(seg(t, OH2 + 0.1, BONK)) }, t, [OH2], 16) : { x: vx + 30, y: -60, z: 1.6 };
  S2.alley(ctx, cam, t, { posts: !see, blur: see ? 0 : 2, fg: x => {
    if (!see) person(x, 'doc2', V(t, { x: vx - 900, y: 260, s: 1.0, face: 1, eyes: 'closed', mouth: 'o', lean: 28, armL: [10, 10], armR: [10, 10], handL: 'open', handR: 'open', bob: Math.sin(t * 9) * 4 }));
    person(x, 'villager', V(t, Object.assign({ x: vx, y: 260, pale: 0.4, brows: see ? 'shock' : 'raised', eyes: see ? 'wide' : 'happy', mouth: see ? 'o' : 'smirk', turn: see ? 0.4 : -0.7, look: see ? [1, -0.3] : [-1, 0], tail: 40, vx: 430, headSq: see ? 0.1 * pulse(t, OH2, 0.2) : 0 }, K.run(t * 14, see ? 0.8 : 0.6))));
    beamEnd(x, BEAMX());
  } });
});

// ================================================================ TREATMENT 3: TREPANATION (38.18 - 54.55)
shot(B(21), B(22), 't_bonk', (ctx, t, lt) => {
  const vx = vxRun(BONK), fall = seg(t, BONK + 0.35, BONK + 1.25), land = BONK + 1.25;
  const cam = shake({ x: vx + 60, y: -120 + 200 * fall, z: 1.45 + lt * 0.08, r: 3 * Math.sin(lt * 2) }, t, [BONK, land], 40);
  S2.alley(ctx, cam, t, { posts: false, fg: x => {
    const sq = Math.exp(-lt * 10) * Math.cos(lt * 50);
    person(x, 'villager', V(t, { x: vx, y: 260, pale: 0.3, eyes: lt < 0.3 ? 'squeeze' : 'spiral', mouth: lt < 0.3 ? 'eek' : 'wavy', brows: 'worried', squash: sq * 0.25, headSq: sq * 0.2, rot: -88 * inQ(fall), bump: outBack(seg(t, BONK + 0.1, BONK + 0.4)), tail: 30 + sq * 40, armL: [20 + 60 * fall, 20], armR: [-20 + 60 * fall, 20], handL: 'spread', handR: 'spread', legL: [10 * fall, 0], legR: [-10 * fall, 0] }));
    if (lt > 0.25) PR.dizzy(x, vx + 20 - 300 * inQ(fall), -480 + 420 * inQ(fall), t, 120);
    if (t > land) PR.dust(x, vx - 260, 250, t - land, 6, 60, 3);
    beamEnd(x, BEAMX(), Math.exp(-lt * 6) * Math.sin(lt * 40) * 10);
  } });
  if (lt < 0.05) { ctx.fillStyle = 'rgba(255,250,235,0.85)'; ctx.fillRect(0, 0, W, H); }
});
sfx(BONK, 'bonk', 1); sfx(BONK + 1.25, 'thud', 0.8);
// T2: a long shadow; the surgeon picks him up like a sack
shot(B(22), B(23), 't_carry', (ctx, t, lt) => {
  const vx = vxRun(BONK), lift = T(22, 10);
  const u = smoother(seg(t, B(22) + 0.2, lift));
  const cam = { x: lerp(vx - 250, vx - 60, u) + 430 * seg(t, lift, B(23)), y: lerp(230, -60, u), z: lerp(2.0, 1.1, u), r: lerp(-6, 0, u) };
  S2.alley(ctx, cam, t, { posts: false, blur: 1.5, fg: x => {
    const dc = seg(t, B(22), B(22) + 0.5);
    if (t < lift) {
      person(x, 'villager', V(t, { x: vx, y: 260, pale: 0.3, eyes: 'spiral', mouth: 'wavy', rot: -88, bump: 1, armL: [80, 20], armR: [40, 20] }));
      PR.dizzy(x, vx - 300, 70, t, 90, 3);
      person(x, 'doc3', V(t, { x: vx + 140, y: 270, s: 1.12, face: -1, lid: 0.5, brows: 'calm', mouth: 'flat', look: [0.3, 0.9], tilt: -8, alpha: dc, lean: 18 * seg(t, lift - 0.4, lift), armR: [40, 70], handR: 'grip', propR: { fn: c => { tube(c, [[0, 0], [0, 60]], 6, '#3a3a3a', 3); shape(c, c2 => c2.roundRect(-30, 60, 60, 80, 12), '#2a2a2a', { lw: 4, tex: false }); shape(c, ell(0, 100, 20, 28), '#ffcf5a', { lw: 0, tex: false }); D.glow(c, 0, 100, 160, '255,190,100', 0.6); }, rot: 180 } }));
    } else {
      const k = seg(t, lift, B(23));
      person(x, 'doc3', V(t, Object.assign({ x: vx + 140 + 420 * k, y: 270, s: 1.12, face: 1, lid: 0.5, brows: 'calm', mouth: 'smirk', armL: [160, 30], armR: [150, 40], handL: 'grip', handR: 'grip', vx: 300 }, K.walk(t * 6, 0.5), { armL: [160, 30], armR: [150, 40] })));
      person(x, 'villager', V(t, { x: vx + 140 + 420 * k - 60, y: 7, s: 0.95, rot: -90, piv: 'hip', eyes: 'spiral', mouth: 'wavy', bump: 1, armL: [-30, 20], armR: [-40, 20], legL: [10, 30], legR: [-10, 30], handL: 'relaxed', handR: 'relaxed', tail: -30 }));
    }
  } });
  const sh = seg(t, B(22), B(22) + 0.6), g = ctx.createLinearGradient(W, 0, 0, 0);
  g.addColorStop(0, 'rgba(20,20,40,0.5)'); g.addColorStop(sh, 'rgba(20,20,40,0.3)'); g.addColorStop(Math.min(1, sh + 0.2), 'rgba(20,20,40,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
});
sfx(B(22), 'drone_low', 0.6);
// T3: the cellar - strapped in, a mug of wine (no anaesthesia), a chalk X
const GULP = T(23, 4), CHALK = T(23, 10);
function strapped(x, t, o = {}) {
  // chair built around the seated skeleton: feet on the floor (y=260), hips at 260 - shin
  const hipW = 260 - K.SPECS.villager.legL * 0.48;
  shape(x, c => c.rect(-150, hipW - 470, 32, 470 + 60), PAL.woodDark, { lw: 5 });
  shape(x, c => c.rect(-175, hipW + 6, 270, 34), PAL.wood, { lw: 5 });
  for (const lx of [-165, 70]) shape(x, c => c.rect(lx, hipW + 38, 26, 260 - hipW - 38), PAL.woodDark, { lw: 4 });
  person(x, 'villager', V(t, Object.assign({ x: -40, y: 260, sit: 1, pale: 0.3, bump: 1, armL: [20, 40], armR: [30, 40], legL: [0, 0], legR: [0, 0] }, o)));
  for (const yy of [hipW - 120, hipW - 50]) { shape(x, c => c.roundRect(-175, yy, 240, 24, 8), '#5a3520', { lw: 4 }); shape(x, c => c.rect(-70, yy + 2, 22, 20), '#c9a050', { lw: 3, tex: false }); }
}
shot(B(23), B(24), 't_cellar', (ctx, t, lt) => {
  const cam = shake(F.camAt([{ t: B(23), x: 150, y: -190, z: 1.15 }, { t: B(24), x: 130, y: -160, z: 1.35 }], t), t, [GULP, CHALK], 10);
  S2.room('surgery', ctx, cam, t, { blur: 1.5, table: false, front: x => { E.candle(x, cam.x - 430, cam.y + 980, 140, t, 6); }, fg: x => {
    const drink = seg(t, GULP - 0.3, GULP + 0.35);
    strapped(x, t, { eyes: drink > 0.3 && drink < 0.9 ? 'closed' : 'open', lid: 0.3, mouth: drink > 0.2 && drink < 0.9 ? 'ooh' : 'wavy', brows: 'worried', armR: [lerp(30, 160, Math.sin(Math.PI * drink)), 50], handR: 'grip', propR: drink > 0 && drink < 1 ? { fn: c => S2.wineMug(c), rot: 180 } : null, tilt: -14 * Math.sin(Math.PI * drink), chalk: outC(seg(t, CHALK, CHALK + 0.2)), headSq: 0.08 * pulse(t, GULP, 0.2) });
    const mark = seg(t, CHALK - 0.25, CHALK + 0.2);
    person(x, 'doc3', V(t, Object.assign({ x: 330, y: 260, s: 1.12, face: -1, lid: 0.5, brows: 'calm', mouth: 'flat', look: [-0.6, 0.2], armR: [lerp(40, 125, Math.sin(Math.PI * mark)), lerp(60, 30, mark)], handR: 'grip', propR: mark > 0 ? { fn: c => shape(c, c2 => c2.roundRect(-8, -6, 16, 40, 4), '#f4f0e6', { lw: 3, tex: false }), rot: 180 } : null, armL: [30, 80], handL: 'relaxed' }, K.idle(t, 13, 0.6))));
  } });
});
sfx(GULP, 'gulp', 0.5); sfx(CHALK, 'tap', 0.4);
// T4: the tool roll unrolls; double punch zooms the brace drill
const UNROLL = B(24), DP = [T(24, 12), T(24, 14)];
shot(B(24), B(25), 't_tools', (ctx, t, lt) => {
  woodTable(ctx, '#3a2a20');
  const dz = DP.reduce((a, p) => a + (t > p ? 0.18 : 0), 0);
  cam1(ctx, shake({ x: 540 + (t > DP[0] ? 80 : 0), y: 960 + (t > DP[0] ? -60 : 0), z: 1.0 + lt * 0.08 + dz, r: -2 }, t, [UNROLL, ...DP], 18), x => {
    const u = outC(seg(t, UNROLL, UNROLL + 0.3)), x1 = lerp(150, 980, u);
    shape(x, c => c.roundRect(100, 640, x1 - 100, 700, 26), '#7b4b2b', { lw: 7, shade: { x0: 0, y0: 640, x1: 0, y1: 1340, a: 0.3 } });
    for (let i = 0; i < 6; i++) { const lx = 170 + i * 135; if (lx < x1 - 60) { shape(x, c => c.rect(lx - 40, 760, 80, 480), '#8e5a34', { lw: 4 }); x.save(); x.setLineDash([8, 8]); line(x, [[lx - 34, 770], [lx - 34, 1230]], 2.5, '#d8b070'); x.restore(); } }
    shape(x, ell(x1, 990, 60, 360), '#6a3c22', { lw: 7 });
    x.save(); x.beginPath(); x.rect(100, 600, x1 - 60, 800); x.clip();
    const tools = [[230, (c, g) => PR.braceDrill(c, 0, g), 1.25, 0], [430, (c, g) => { c.rotate(-1.57); PR.saw(c); }, 1.2, 1], [610, (c, g) => PR.pliers(c), 1.3, 2], [800, (c, g) => PR.fleam(c, t, g), 2.0, 3]];
    tools.forEach(([tx, fn, s, i]) => { x.save(); x.translate(tx, 990); x.scale(s, s); fn(x, pulse(t, UNROLL + 0.15 + i * 0.12, 0.3) + (i === 0 ? pulse(t, DP[0], 0.25) + pulse(t, DP[1], 0.25) : 0)); x.restore(); });
    x.restore();
    // the surgeon's hand selects the drill on the second punch
    if (t > DP[1] - 0.15) { const k = outBack(seg(t, DP[1] - 0.15, DP[1] + 0.05)); x.save(); x.translate(lerp(560, 260, k), lerp(380, 800, k)); x.scale(2.4, 2.4); x.rotate(3.0); K.hand(x, 'open', '#e6bb95', 1); x.restore(); tube(x, [[700, 0], [lerp(560, 260, k) + 40, lerp(380, 800, k) - 60]], 80, '#3e4a52', 6); }
  });
  vignette(ctx, 0.6);
});
sfx(UNROLL, 'unroll', 0.8); for (const p of DP) sfx(p, 'shing', 0.6);
// T5/T6: rising hits - his eyes on the drill; the drill set on the chalk X
shot(B(25), T(25, 8), 't_eyes', (ctx, t, lt) => {
  const h = { x: -40, y: K.headY('villager', { y: 260, sit: 1 }) };
  const cam = shake(frameHead(h.x, h.y, 3.6 + lt * 0.5, 900), t, [B(25)], 16);
  S2.room('surgery', ctx, cam, t, { blur: 9, table: false, fg: x => strapped(x, t, { eyes: 'wide', lid: 0, pupil: 0.6, look: [0.5, -0.95], brows: 'shock', mouth: 'eek', sweat: 1, shiver: 0.5, chalk: 1 }) });
  ctx.save(); ctx.translate(700, 180 + 60 * outC(seg(t, B(25), T(25, 8)))); ctx.rotate(0.2); ctx.scale(2.2, 2.2); PR.braceDrill(ctx, t * 2, 0.4 * pulse(t, B(25) + 0.1, 0.3)); ctx.restore();
});
shot(T(25, 8), B(26), 't_place', (ctx, t, lt) => {
  const h = { x: -40, y: K.headY('villager', { y: 260, sit: 1 }) };
  const cam = shake(frameHead(h.x + 160, h.y, 2.2 + lt * 0.3, 1000), t, [T(25, 8)], 14);
  S2.room('surgery', ctx, cam, t, { blur: 7, table: false, fg: x => {
    strapped(x, t, { eyes: 'squeeze', brows: 'worried', mouth: 'eek', sweat: 1, shiver: 0.6, chalk: 1, tilt: -6 });
    person(x, 'doc3', V(t, { x: 330, y: 260, s: 1.12, face: -1, lid: 0.55, brows: 'calm', mouth: 'flat', look: [-0.6, -0.3], lean: 16, armR: [150, 30], handR: 'grip', armL: [120, 40], handL: 'grip', propR: { fn: c => PR.braceDrill(c, t * 1.5, pulse(t, T(25, 12), 0.3)), rot: 200, s: 0.95 } }));
  } });
});
sfx(B(25), 'hit_low', 0.6); sfx(T(25, 8), 'hit_low', 0.7); sfx(T(25, 12), 'glint', 0.5);
// T7: the operation in shadow-play behind a linen screen (cranks on the 8ths) - non-graphic
shot(B(26), 48.55, 't_shadow', (ctx, t, lt) => {
  ctx.fillStyle = '#20181a'; ctx.fillRect(0, 0, W, H);
  cam1(ctx, { x: 0, y: -520, z: 1.0 + lt * 0.12 }, x => {
    const g = x.createRadialGradient(60, -560, 40, 60, -560, 900); g.addColorStop(0, '#f6e2b8'); g.addColorStop(1, '#8a6a52');
    shape(x, c => c.rect(-620, -1400, 1240, 1500), g, { lw: 8 });
    for (let i = -5; i <= 5; i++) { x.save(); x.globalAlpha = 0.25; line(x, [[i * 115, -1400], [i * 115 + Math.sin(t + i) * 6, 100]], 3, '#6a4a32'); x.restore(); }
    const crank = t * 2 * Math.PI * (C.BPM / 60) / 2;
    S2.castShadow(x, y => {
      K.drawPerson(y, 'villager', V(t, { x: -180, y: 250, s: 1.45, sit: 1, legL: [0, -30 + 30 * Math.sin(t * 22)], legR: [0, -30 + 30 * Math.sin(t * 22 + 2)], armL: [20, 40], armR: [30, 40], tilt: -6 }));
      K.drawPerson(y, 'doc3', V(t, { x: 260, y: 300, s: 1.55, face: -1, lean: 20, armR: [150, 30], armL: [120, 40], propR: { fn: c => PR.braceDrill(c, crank, 0), rot: 200, s: 0.95 } }));
    }, { ax: 0, ay: 300, dx: 0, dy: -40, alpha: 0.85, blur: 4, color: 'rgb(30,15,12)' });
  });
  vignette(ctx, 0.55);
});
// T8: GASP (soundtrack 48.636)
shot(48.55, B(27), 't_gasp', (ctx, t, lt) => {
  const g = 48.636, h = { x: -40, y: K.headY('villager', { y: 260, sit: 1 }) };
  const cam = shake(frameHead(h.x, h.y, 3.4 + 0.6 * outC(seg(t, g, g + 0.12)), 880), t, [g], 30);
  S2.room('surgery', ctx, cam, t, { blur: 9, table: false, fg: x => strapped(x, t, { eyes: 'wide', lid: 0, pupil: 0.5, brows: 'shock', mouth: 'gasp', open: 1, tail: 70, sweat: 1, headSq: -0.12 * pulse(t, g, 0.25), chalk: 1 }) });
  speedLines(ctx, 540, 760, 36, 420, 1400, 0.3, 31);
});
// T9: CLIMAX - the clean anatomy plate: a small disc of bone lifts out (49.09)
function plate(ctx, t, o = {}) {
  parchment(ctx, '#ecd9ad');
  cam1(ctx, o.cam, x => {
    x.lineWidth = 4; x.strokeStyle = '#8a3a2a'; x.strokeRect(90, 170, 900, 1500); x.lineWidth = 2; x.strokeRect(110, 190, 860, 1460);
    x.font = '42px "IM Fell SC"'; x.fillStyle = '#6a2a18'; x.textAlign = 'center'; x.fillText('PLATE III  ·  TREPANATION', 540, 1600);
    const cx = 540, cy = 930;
    shape(x, c => { c.moveTo(cx - 250, cy + 360); c.bezierCurveTo(cx - 330, cy + 100, cx - 330, cy - 330, cx, cy - 360); c.bezierCurveTo(cx + 270, cy - 360, cx + 330, cy - 150, cx + 300, cy - 20); c.lineTo(cx + 360, cy + 60); c.lineTo(cx + 300, cy + 90); c.quadraticCurveTo(cx + 320, cy + 180, cx + 260, cy + 230); c.quadraticCurveTo(cx + 150, cy + 300, cx + 120, cy + 360); c.closePath(); }, '#f1c49b', { lw: 6, shade: { x0: cx + 300, y0: cy - 300, x1: cx - 300, y1: cy + 300, a: 0.2 } });
    shape(x, c => { c.ellipse(cx - 20, cy - 80, 270, 240, 0, Math.PI * 1.02, Math.PI * 1.98); c.ellipse(cx - 20, cy - 80, 230, 200, 0, Math.PI * 1.98, Math.PI * 1.02, true); c.closePath(); }, '#f6eedc', { lw: 5, tex: false });
    x.font = '34px "IM Fell SC"'; x.fillStyle = '#6a2a18'; x.textAlign = 'left'; x.fillText('skull', cx + 240, cy - 290);
    shape(x, ell(cx + 200, cy + 20, 26, 20), '#fffaf0', { lw: 4, tex: false }); shape(x, ell(cx - 40, cy + 70, 40, 60), '#e8b48c', { lw: 4, tex: false });
    const hx = cx - 20, hy = cy - 300, lid = o.lid || 0;
    x.save(); x.setLineDash([12, 10]); shape(x, ell(hx, hy, 70, 26), null, { lw: 5, ink: '#a3342b' }); x.restore();
    if (lid > 0) { x.save(); x.translate(hx, hy - lid * 260); x.rotate(lid * 0.6); shape(x, ell(0, 0, 70, 24), '#f6eedc', { lw: 5, tex: false }); x.restore(); for (let i = 0; i < 5; i++) sparkle(x, hx + Math.cos(i * 1.3) * 160 * lid, hy - 60 - Math.sin(i * 1.3) * 120 * lid, 30 * (1 - Math.abs(lid - 0.5)), 1); }
    x.font = '40px "IM Fell SC"'; x.fillStyle = '#6a2a18'; x.textAlign = 'left'; x.fillText('a small round opening', hx + 100, hy - 150);
    line(x, [[hx + 95, hy - 160], [hx + 60, hy - 30]], 3, '#6a2a18');
    const dy = o.drill === undefined ? 0 : o.drill;
    x.save(); x.translate(hx, hy - 520 + dy * 180); x.scale(1.4, 1.4); PR.braceDrill(x, t * 6 * (o.spin || 1), 0); x.restore();
    for (const s of [-1, 1]) { x.save(); x.translate(hx + s * 150, hy - 420 + dy * 160); x.rotate(t * 4 * s); curve(x, [-40, 0], [0, -40], [40, 0], 5, '#a3342b'); shape(x, poly([[40, 0], [26, -16], [56, -10]]), '#a3342b', { lw: 0, tex: false }); x.restore(); }
  });
}
shot(B(27), B(28), 't_plate', (ctx, t, lt) => {
  const p = B(27);
  plate(ctx, t, { cam: shake({ x: 540, y: 760 + 120 * smooth(seg(t, p + 0.6, B(28))), z: 1.45 - lt * 0.25, r: -6 * (1 - outC(seg(t, p, p + 0.5))) }, t, [p], 26), drill: 1, spin: 2, lid: outBack(seg(t, p + 0.05, p + 0.5)) });
  if (t - p < 0.05) { ctx.fillStyle = 'rgba(255,250,235,0.8)'; ctx.fillRect(0, 0, W, H); }
});
sfx(B(27), 'pop_big', 0.9);
// T10: bandaging (the bandage winds round on the beats); the surgeon is pleased
shot(B(28), B(29), 't_bandage', (ctx, t, lt) => {
  const h = { x: -40, y: K.headY('villager', { y: 260, sit: 1 }) };
  const cam = frameHead(h.x + 120, h.y, 1.7 + lt * 0.1, 860);
  S2.room('surgery', ctx, cam, t, { blur: 4, table: false, fg: x => {
    const wind = seg(t, B(28), B(28) + 1.2), beat = Math.floor((t - B(28)) / C.BEAT);
    strapped(x, t, { eyes: beat % 2 ? 'spiral' : 'open', lid: 0.3, brows: 'raised', mouth: 'flat', bandage: smooth(wind), chalk: 1 - wind, rot: Math.sin(t * C.BPM / 60 * Math.PI) * 4 });
    const a = t * 2 * Math.PI * (C.BPM / 60) / 2;
    person(x, 'doc3', V(t, { x: 300, y: 260, s: 1.12, face: -1, lid: 0.5, brows: 'calm', mouth: wind >= 1 ? 'smirk' : 'flat', look: [-0.6, -0.3], lean: 12, armR: [140 + 20 * Math.sin(a), 40], handR: 'grip', armL: [110 + 20 * Math.cos(a), 50], handL: 'grip' }));
  } });
});
// T11: the healed skull in a museum spotlight
shot(B(29), B(30), 't_skull', (ctx, t, lt) => {
  ctx.fillStyle = '#1e1416'; ctx.fillRect(0, 0, W, H);
  cam1(ctx, { x: 540, y: 1180, z: 1.05 + lt * 0.12, r: Math.sin(lt * 1.6) * 3 }, x => {
    for (const s of [-1, 1]) for (let i = 0; i < 4; i++) shape(x, c => c.rect(540 + s * (380 + i * 60) - 40, -100, 90, 2200), mixh('#5a1a22', '#3a0e14', i / 4), { lw: 4, shade: { x0: 540 + s * (380 + i * 60) - 40, y0: 0, x1: 540 + s * (380 + i * 60) + 50, y1: 0, a: 0.4 } });
    rays(x, 540, -100, Math.PI / 2, 0.55, 1900, 6, 0.16, 12);
    shape(x, c => c.rect(300, 1300, 480, 700), '#d8ccb4', { lw: 6, shade: { x0: 300, y0: 0, x1: 780, y1: 0, a: 0.4 } }); shape(x, c => c.rect(270, 1270, 540, 50), '#e8dcc4', { lw: 6 });
    shape(x, c => c.roundRect(310, 1180, 460, 110, 50), '#8a1f2a', { lw: 6, hi: { x: 480, y: 1200, r: 120, a: 0.3 } });
    const sy = 1000 + Math.sin(t * 2) * 6;
    shape(x, c => { c.moveTo(540, sy - 230); c.bezierCurveTo(720, sy - 230, 760, sy - 40, 700, sy + 40); c.lineTo(690, sy + 120); c.quadraticCurveTo(620, sy + 190, 540, sy + 190); c.quadraticCurveTo(460, sy + 190, 390, sy + 120); c.lineTo(380, sy + 40); c.bezierCurveTo(320, sy - 40, 360, sy - 230, 540, sy - 230); c.closePath(); }, '#f2e8d2', { lw: 7, shade: { x0: 700, y0: sy - 200, x1: 380, y1: sy + 180, a: 0.3 }, hi: { x: 500, y: sy - 140, r: 150, a: 0.5 } });
    for (const s of [-1, 1]) shape(x, ell(540 + s * 85, sy + 10, 55, 60), '#3a2a2a', { lw: 5, tex: false });
    shape(x, poly([[540, sy + 70], [520, sy + 110], [560, sy + 110]]), '#3a2a2a', { lw: 4, tex: false });
    for (let i = -3; i <= 3; i++) line(x, [[540 + i * 26, sy + 140], [540 + i * 26, sy + 175]], 4);
    shape(x, ell(600, sy - 150, 52, 30, -0.25), '#c8b896', { lw: 6, tex: false }); shape(x, ell(600, sy - 146, 36, 18, -0.25), '#2a1e1e', { lw: 4, tex: false });
    // magnifier sweeps over the smooth, healed edge
    const mk = smooth(seg(t, B(29) + 0.3, B(29) + 1.0));
    x.save(); x.translate(lerp(900, 640, mk), lerp(700, sy - 120, mk)); x.rotate(-0.5); PR.magnifier(x, t); x.restore();
    for (let i = 0; i < 7; i++) sparkle(x, 540 + Math.cos(i * 0.9 + t) * 300, sy - 60 + Math.sin(i * 1.7 + t * 1.3) * 260, 26 * (0.5 + 0.5 * Math.sin(t * 5 + i)), 0.9);
    shape(x, c => c.roundRect(380, 1420, 320, 110, 12), '#c9973a', { lw: 5, hi: { x: 470, y: 1440, r: 120, a: 0.5 } });
    x.font = '50px "Cinzel Black"'; x.fillStyle = '#4a2a10'; x.textAlign = 'center'; x.textBaseline = 'middle'; x.fillText('HEALED', 540, 1462); x.font = '30px "IM Fell SC"'; x.fillText('the bone grew back', 540, 1505);
  });
  vignette(ctx, 0.55);
});
sfx(B(29), 'shimmer', 0.6);

// ================================================================ ENDING (54.55 - 60) golden hour
shot(B(30), B(31), 'e_home', (ctx, t, lt) => {
  const vx = 3300 + lt * 170;
  S2.golden(ctx, { x: vx + 40, y: -60, z: 1.2 + lt * 0.05 }, t, { fg: x => {
    person(x, 'extraB', V(t, { x: vx + 380, y: 40, s: 0.8, face: -1, brows: 'raised', mouth: 'o', look: [-0.6, 0.2], lid: K.blink(t, 8), armR: [120, 60], handR: 'open' }));
    person(x, 'extraA', V(t, { x: vx + 230, y: 20, s: 0.75, face: -1, brows: 'worried', mouth: 'frown', look: [-0.6, 0.3], tilt: 6, armR: [80, 90], handR: 'point' }));
    const tw = Math.floor(t * 6) % 3 === 0 ? 0.7 : 0.05;
    person(x, 'villager', V(t, Object.assign({ x: vx, y: 250, bandage: 1, lid: tw, mouth: 'flat', brows: 'worried', look: [0.4, 0], shiver: 0.2, vx: 170 }, K.walk(t * 6, 0.5), { armL: [3, 5], armR: [-3, 5] })));
  } });
});
const P4 = [B(31), T(31, 3), T(31, 6)], CH3 = [57.273, 57.5], DX = 4050;
function clinicDoor(x, t, open) {
  shape(x, c => { c.moveTo(DX - 230, 70); c.lineTo(DX - 230, -480); c.arc(DX, -480, 230, Math.PI, 0); c.lineTo(DX + 230, 70); c.closePath(); }, '#b3a385', { lw: 7, texA: 0.3 });
  x.save(); x.beginPath(); x.moveTo(DX - 180, 70); x.lineTo(DX - 180, -480); x.arc(DX, -480, 180, Math.PI, 0); x.lineTo(DX + 180, 70); x.closePath(); x.clip();
  x.fillStyle = '#24160f'; x.fillRect(DX - 200, -700, 400, 800); D.glow(x, DX, -250, 420, '255,180,100', 0.55); x.restore();
  x.save(); x.translate(DX + 180, 70); x.scale(-(1 - 0.85 * open), 1);
  shape(x, c => { c.moveTo(0, 0); c.lineTo(0, -550); c.arc(180, -480, 180, Math.PI * 1.1, Math.PI * 1.5); c.lineTo(360, -660); c.lineTo(360, 0); c.closePath(); }, PAL.wood, { lw: 6, shade: { x0: 0, y0: 0, x1: 360, y1: 0, a: 0.3 } });
  for (let k = 1; k < 4; k++) line(x, [[k * 90, -640], [k * 90, 0]], 3, PAL.woodDark);
  x.restore(); E.sign(x, DX + 200, -640, t, 'bowl');
}
function doctorsAt(x, t, mode, k = 1) {
  const ch = pulse(t, CH3[0], 0.2) + pulse(t, CH3[1], 0.2);
  if (mode === 'one') { person(x, 'doc1', V(t, { x: DX - 40, y: 60, s: 0.95, face: -1, eyes: 'happy', mouth: 'smile', brows: 'raised', lean: 14, armR: [120 + 25 * Math.sin(t * 14), 70], handR: 'open' })); return; }
  const sad = mode === 'sad';
  person(x, 'doc3', V(t, { x: DX + 110, y: 40, s: 0.95 * k, face: -1, lid: 0.5, mouth: sad ? 'frown' : ch > 0.3 ? 'grin' : 'smirk', brows: 'calm', armR: sad ? [20, 30] : [150, 20], handR: 'grip', propR: sad ? null : { fn: c => PR.braceDrill(c, t * 4, 0), rot: 180, s: 0.6 } }));
  person(x, 'doc1', V(t, { x: DX - 20, y: 60, s: 0.95 * k, face: -1, eyes: sad ? 'open' : 'happy', mouth: sad ? 'frown' : 'chuckle', open: ch, brows: sad ? 'sad' : 'raised', lean: sad ? 0 : 12, look: [-1, 0], armR: sad ? [20, 30] : [120 + 25 * Math.sin(t * 14), 70], handR: sad ? 'relaxed' : 'open', bob: ch * 10 }));
  person(x, 'doc2', V(t, { x: DX - 150, y: 80, s: 0.9 * k, face: -1, eyes: sad ? 'open' : 'happy', mouth: sad ? 'o' : 'chuckle', open: ch, brows: sad ? 'sad' : 'raised', look: [-1, 0], bob: ch * 12, armR: [160, 10], handR: 'grip', propR: { fn: c => PR.leechJar(c, 0, 0, 0.45, t, { n: 4 }), rot: 180 } }));
}
shot(B(31), B(32), 'e_next', (ctx, t, lt) => {
  const i = t < P4[1] ? 0 : t < P4[2] ? 1 : 2, late = t > T(31, 8);
  const cam = shake({ x: DX - 240, y: -170, z: late ? 1.05 + (t - T(31, 8)) * 0.05 : 1.2 + i * 0.16 }, t, [...P4, CH3[0]], 22);
  S2.golden(ctx, cam, t, { fg: x => {
    clinicDoor(x, t, late ? smooth(seg(t, T(31, 8), T(31, 10))) : 0.3);
    doctorsAt(x, t, late ? 'all' : 'one', late ? outBack(seg(t, T(31, 8), T(31, 8) + 0.2)) : 1);
    const poses = [
      { eyes: 'wide', mouth: 'o', brows: 'raised', tail: 20, armL: [10, 20], armR: [-10, 20] },
      { eyes: 'wide', mouth: 'eek', brows: 'shock', sweat: 1, tail: 60, armL: [-90, 40], armR: [90, 40], handL: 'spread', handR: 'spread', lean: -8 },
      { eyes: 'wide', mouth: 'scream', open: 1, brows: 'shock', sweat: 1, tail: 90, armL: [-160, 30], armR: [160, 30], handL: 'spread', handR: 'spread', bob: 60, squash: -0.15, lean: -12 },
    ];
    person(x, 'villager', V(t, Object.assign({ x: DX - 560, y: 260, bandage: 1, face: 1, look: [1, -0.2] }, poses[i], late ? { shiver: 0.6 } : {})));
  } });
});
for (const p of P4) sfx(p, 'freeze_hit', 0.8); sfx(T(31, 8), 'door', 0.5);
// final gag & loop: he bolts... and the surgeon's hand hooks his hood tail and drags him back inside (door slams)
const YANK = T(32, 8);
shot(B(32), 60.0001, 'e_bolt', (ctx, t, lt) => {
  const cam = shake(F.camAt([{ t: B(32), x: DX - 240, y: -170, z: 1.05 }, { t: 60, x: DX - 300, y: -190, z: 0.98 }], t), t, [59.65], 12);
  S2.golden(ctx, cam, t, { fg: x => {
    const shut = smooth(seg(t, 59.45, 59.65));
    clinicDoor(x, t, 1 - shut);
    if (t < 59.5) doctorsAt(x, t, t < B(32) + 0.25 || t > YANK ? 'all' : 'sad');
    const go = seg(t, B(32) + 0.08, YANK);
    if (t < YANK) {
      const vx = DX - 560 - 900 * inQ(go);
      person(x, 'villager', V(t, Object.assign({ x: vx, y: 260, bandage: 1, face: -1, eyes: 'wide', mouth: 'scream', open: 1, brows: 'shock', tail: 90, vx: -2400 }, K.run(t * 30, 1.2), K.flail(t), { lean: 30 })));
    } else if (t < 59.5) {
      const k = seg(t, YANK, 59.45), vx = lerp(DX - 1460, DX, inQ(k));
      person(x, 'villager', V(t, { x: vx, y: 260 - Math.sin(Math.PI * k) * 120, bandage: 1, face: -1, eyes: 'wide', mouth: 'scream', open: 1, brows: 'shock', tail: -60, rot: 30, armL: [-160, 30], armR: [160, 30], handL: 'spread', handR: 'spread', vx: 3000 }));
      D.tubeCurve(x, [[vx + 70, -150], [(vx + DX) / 2, -150 + 60 * (1 - k)], [DX - 60, -330]], 12, K.SPECS.villager.hoodDark, 4);
    }
    if (t > B(32) + 0.08 && t < YANK + 0.3) { const k = t - B(32) - 0.08; for (let i = 0; i < 6; i++) PR.puff(x, DX - 560 - i * 150 - k * 60, 240 - (i % 2) * 40, 50 + k * 50, clamp(1 - k * 0.9), '#dcc9a3'); }
  } });
});
sfx(B(32) + 0.08, 'zip', 0.8); sfx(T(32, 8), 'whoosh', 0.7); sfx(59.65, 'door_slam', 0.9);

// ================================================================ text: narration caption + subtitles
const NARR_T0 = 0.15;
const NARR_WORDS = [['IN', 0.0], ['MEDIEVAL', 0.14], ['TIMES,', 0.71], ['SURVIVING', 1.51], ['YOUR', 2.09], ['DOCTOR', 2.27], ['WAS', 2.96], ['A', 3.10], ['CHALLENGE.', 3.18]];
const SUBS = [
  { t0: NARR_T0, t1: 4.5, text: NARR_WORDS.map(w => w[0]).join(' '), em: ['SURVIVING', 'CHALLENGE'], words: NARR_WORDS.map(w => NARR_T0 + w[1]), y: 300, size: 80 },
  [5.75, B(4) - 0.04, 'DIAGNOSIS: A FEVER.', ['FEVER']],
  [B(4), B(6) - 0.04, 'HIS VERDICT: "TOO MUCH BLOOD."', ['BLOOD'], '#ff6a4d'],
  [B(6), B(8) - 0.04, 'DOCTORS THOUGHT ILLNESS CAME FROM UNBALANCED BODY FLUIDS.', ['UNBALANCED']],
  [B(8), B(10) - 0.04, 'THE CURE: OPEN A VEIN AND LET SOME BLOOD OUT.', ['VEIN'], '#ff6a4d'],
  [B(10), B(12) - 0.04, 'IT OFTEN LEFT PATIENTS WEAKER, NOT BETTER.', ['WEAKER']],
  [B(12), B(14) - 0.04, 'SECOND OPINION: LEECHES!', ['LEECHES'], '#9fe07a'],
  [B(14), B(16) - 0.04, 'LEECH THERAPY WAS JUST ANOTHER FORM OF BLOODLETTING.', ['BLOODLETTING'], '#ff6a4d'],
  [T(16, 4), B(18) - 0.04, 'THEY LATCHED ON AND DRANK UNTIL FULL, THEN DROPPED OFF.', ['DRANK', 'FULL'], '#9fe07a'],
  [B(18), B(20) - 0.04, 'EVEN WEAKER. SO HE RAN.', ['RAN']],
  [B(20), 37.7, 'FREEDOM...?', ['FREEDOM']],
  [B(21), T(22, 8) - 0.04, 'THEN HE INJURED HIS HEAD...', ['HEAD']],
  [T(22, 8), B(24) - 0.04, '...WHICH MEANT A VISIT TO THE SURGEON.', ['SURGEON']],
  [B(24), B(26) - 0.04, 'TREPANATION: BORING A HOLE IN THE SKULL.', ['TREPANATION'], '#ff9a4d'],
  [B(26), B(28) - 0.04, 'USED FOR HEAD INJURIES. NO ANAESTHESIA.', ['NO', 'ANAESTHESIA']],
  [B(28), B(29) - 0.04, 'AMAZINGLY, MANY SURVIVED.', ['SURVIVED'], '#9fe07a'],
  [B(29), B(30) - 0.04, 'ARCHAEOLOGISTS FIND SKULLS THAT HEALED.', ['HEALED'], '#9fe07a'],
  [B(30), 57.22, 'STILL FEELING SICK?', ['SICK']],
  [57.27, 60.0, 'SUDDENLY, BEING SICK SOUNDED SAFER.', ['SAFER'], '#9fe07a'],
].map(s => Array.isArray(s) ? { t0: s[0], t1: s[1], text: s[2], em: s[3], color: s[4] } : s);
const STAMPS = [
  { t0: B(3), t1: B(4) - 0.1, kicker: 'TREATMENT Nº1', title: 'Bloodletting' },
  { t0: B(12), t1: B(13) - 0.1, kicker: 'TREATMENT Nº2', title: 'Leeches' },
  { t0: B(23), t1: B(24) - 0.1, kicker: 'TREATMENT Nº3', title: 'Trepanation' },
];
const SFXTEXT = [
  { t0: BONK, t1: BONK + 0.65, text: 'BONK!', x: 600, y: 520, size: 190, rot: 8 },
  { t0: B(27), t1: B(27) + 0.4, text: 'POP!', x: 760, y: 420, size: 130, rot: -8, c1: '#ffffff', c2: '#9fe07a' },
];
const TRANS = [
  [B(3), 'flash'], [T(4, 8), 'whipL'], [B(6), 'whipR'], [B(8), 'whipL'], [T(9, 8), 'whipU'], [B(10), 'flash'],
  [B(12), 'whipL'], [B(16), 'whipU'], [B(19), 'whipL'], [B(21), 'flash'], [B(23), 'whipD'], [B(24), 'whipL'],
  [B(26), 'whipR'], [B(27), 'flash'], [B(29), 'whipR'], [B(30), 'whipL'],
].map(([t, kind]) => ({ t, kind }));
for (const tr of TRANS) if (tr.kind.startsWith('whip')) sfx(tr.t - 0.06, 'whoosh', 0.45);
const PULSE = [[B(3), B(11)], [B(12), B(16)], [B(18), B(20)], [B(21), B(25)], [B(27), B(31)]];

module.exports = { SH, SUBS, STAMPS, SFXTEXT, TRANS, PULSE, SFX, NARR_T0 };
