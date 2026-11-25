// TIMELINE: shot sequencing, transitions, title, captions, impact frames, film post.
'use strict';
const CAN = document.getElementById('c'), CTX = CAN.getContext('2d');
let READY = false;
KICKS = BEATMAP.kicks.slice().sort((a, b) => a - b);
(async () => {
  initGrain();
  await document.fonts.load('700 80px Cinzel'); await document.fonts.load('900 80px Cinzel');
  await document.fonts.load('900 60px Inter'); await document.fonts.load('800 60px Inter'); await document.fonts.load('700 30px Inter');
  READY = true;
})();
window.isReady = () => READY;
window.renderTest = (name, t) => { CTX.setTransform(1, 0, 0, 1, 0, 0); CTX.clearRect(0, 0, W, H); TESTS[name](CTX, t); };
window.renderFrame = (t) => { CTX.setTransform(1, 0, 0, 1, 0, 0); CTX.globalAlpha = 1; CTX.filter = 'none'; CTX.globalCompositeOperation = 'source-over'; FILM(CTX, t); };

// ------------------------------------------------------------------ shot table
const SHOTS = [
  [s01, 0, EV.slam1], [s02, EV.slam1, 7.06], [s03, 7.06, EV.scan1], [s04, EV.scan1, EV.fire1], [s05, EV.fire1, EV.slam2],
  [s06, EV.slam2, EV.shriek1], [s07, EV.shriek1, EV.riser], [s08, EV.riser, EV.predrop], [s09, EV.predrop, EV.drop1],
  [s10, EV.drop1, 30.0], [s11, 30.0, EV.scan3], [s12, EV.scan3, EV.clank], [s13, EV.clank, EV.slam4], [s14, EV.slam4, EV.wail5],
  [s15, EV.wail5, EV.drop2], [s16, EV.drop2, EV.wail6], [s17, EV.wail6, EV.scan4], [s18, EV.scan4, EV.bar32], [s19, EV.bar32, EV.final], [s20, EV.final, 60.01],
];
// transitions at boundaries: [boundary time, start offset, end offset, type, opts]
const TRANS = {
  [7.06]: [-0.3, 0.15, 'light'], [EV.scan1]: [-0.05, 0.42, 'scan'], [EV.fire1]: [-0.22, 0.12, 'iris', { cx: 540, cy: 900 }],
  [EV.shriek1]: [-0.1, 0.16, 'whip'], [EV.riser]: [-0.18, 0.2, 'zoom'], [30.0]: [-0.25, 0.2, 'zoom'], [EV.scan3]: [-0.02, 0.42, 'scan'],
  [EV.wail5]: [-0.2, 0.3, 'zoom'], [EV.wail6]: [-0.12, 0.3, 'light'], [EV.bar32]: [-0.12, 0.2, 'light'],
};
const SILENCE = [[EV.sil1, EV.drop1], [EV.sil2, EV.drop2], [EV.sil3, EV.final]];
// impact frames: [time, strength, color]
const IMPACTS = [[0.0, 0.0, '#ffc890'], [0.02, 0.45, '#000000'], [EV.slam1, 0.9, '#ffd8a0'], [EV.fire1, 0.6, '#ff9a4a'], [EV.slam2, 0.7, '#ffd8a0'], [EV.predrop, 0.6, '#ffb070'],
  [EV.drop1, 1.0, '#fff0d0'], [EV.slam3, 0.7, '#ffd8a0'], [EV.clank, 0.5, '#ffb070'], [EV.slam4, 0.8, '#ffd8a0'], [EV.drop2, 1.0, '#ffe0c0'],
  [EV.scan4, 0.35, '#ffd8c0'], [EV.roarClimax, 0.7, '#ff9a4a'], [EV.final, 1.0, '#fff0d0'], [EV.w_bull, 0.35, '#ffc890']];

function shotAt(t) { for (let i = 0; i < SHOTS.length; i++) if (t < SHOTS[i][2]) return i; return SHOTS.length - 1; }

function renderShots(ctx, t) {
  // silence windows -> near-black with a breath of embers
  for (const [a, b] of SILENCE) if (t >= a && t < b) {
    ctx.fillStyle = '#030202'; ctx.fillRect(0, 0, W, H);
    motes(ctx, t, 18, 999, { vy: -40, size: [0.8, 2], col: '#ff9a4a', a: 0.5 * (1 - inv(a, b, t)), life: 3 }); return;
  }
  const i = shotAt(t);
  // transition into shot i (at its start) or out of shot i (at its end)?
  for (const [k, sh] of [[i, SHOTS[i]], [i + 1, SHOTS[i + 1]]]) {
    if (!sh) continue;
    const bt = sh[1], tr = TRANS[bt];
    if (!tr) continue;
    const [o0, o1, type, opt] = tr;
    if (t >= bt + o0 && t < bt + o1) {
      const A = SHOTS[k - 1][0], B = sh[0], u = (t - (bt + o0)) / (o1 - o0);
      return blend(ctx, t, A, B, type, u, opt || {});
    }
  }
  SHOTS[i][0](ctx, t);
}

function blend(ctx, t, A, B, type, u, opt) {
  const cA = cvs('tA'), cB = cvs('tB');
  A(cA.getContext('2d'), t); B(cB.getContext('2d'), t);
  const k = ease.io3(u);
  ctx.save();
  if (type === 'light') {
    ctx.drawImage(cA, 0, 0); ctx.globalAlpha = k; ctx.drawImage(cB, 0, 0); ctx.globalAlpha = 1;
    ctx.globalCompositeOperation = 'screen'; ctx.fillStyle = rgba('#ffb070', 0.18 * Math.sin(Math.PI * u)); ctx.fillRect(0, 0, W, H);
  } else if (type === 'scan') {
    const y = lerp(-40, H + 40, k);
    ctx.drawImage(cA, 0, 0); ctx.save(); ctx.beginPath(); ctx.rect(0, 0, W, y); ctx.clip(); ctx.drawImage(cB, 0, 0); ctx.restore();
    ctx.globalCompositeOperation = 'screen';
    ctx.fillStyle = linGrad(ctx, 0, y - 120, 0, y + 6, [[0, 'rgba(127,214,255,0)'], [0.85, 'rgba(160,225,255,0.35)'], [1, 'rgba(230,248,255,1)']]); ctx.fillRect(0, y - 120, W, 126);
    ctx.fillStyle = 'rgba(200,240,255,0.9)'; ctx.fillRect(0, y - 2, W, 3);
  } else if (type === 'iris') {
    ctx.drawImage(cA, 0, 0); const r = lerp(0, 1400, ease.in3(u));
    ctx.save(); ctx.beginPath(); ctx.arc(opt.cx, opt.cy, r, 0, 6.283); ctx.clip(); ctx.drawImage(cB, 0, 0); ctx.restore();
    ctx.globalCompositeOperation = 'screen'; ctx.strokeStyle = rgba('#ffc890', 0.9 * (1 - u)); ctx.lineWidth = 14; ctx.filter = 'blur(4px)'; ctx.beginPath(); ctx.arc(opt.cx, opt.cy, r, 0, 6.283); ctx.stroke();
  } else if (type === 'whip') {
    const x = -k * W;
    for (let j = 0; j < 5; j++) { ctx.globalAlpha = 0.28; ctx.drawImage(cA, x + j * 26 * Math.sin(Math.PI * u), 0); ctx.drawImage(cB, x + W + j * 26 * Math.sin(Math.PI * u), 0); }
  } else if (type === 'zoom') {
    ctx.save(); ctx.globalAlpha = 1 - k; ctx.translate(W / 2, H / 2); ctx.scale(1 + k * 0.6, 1 + k * 0.6); ctx.translate(-W / 2, -H / 2); ctx.filter = `blur(${k * 8}px)`; ctx.drawImage(cA, 0, 0); ctx.restore();
    ctx.save(); ctx.globalAlpha = k; ctx.translate(W / 2, H / 2); ctx.scale(lerp(0.82, 1, k), lerp(0.82, 1, k)); ctx.translate(-W / 2, -H / 2); ctx.drawImage(cB, 0, 0); ctx.restore();
  }
  ctx.restore();
}

// ------------------------------------------------------------------ typography
function bronzeText(ctx, text, x, y, size, opt = {}) {
  ctx.save();
  ctx.font = `${opt.weight || 800} ${size}px Cinzel`; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
  if (opt.track) ctx.letterSpacing = `${opt.track}px`;
  ctx.shadowColor = rgba(opt.glowCol || '#ff8a3a', 0.6 * (opt.glow ?? 1)); ctx.shadowBlur = 40;
  ctx.fillStyle = linGrad(ctx, 0, y - size * 0.85, 0, y + size * 0.1, [[0, '#fff2cf'], [0.45, '#e9b468'], [0.75, '#a8692e'], [1, '#5a3214']]);
  ctx.fillText(text, x, y);
  ctx.shadowBlur = 0; ctx.lineWidth = 2; ctx.strokeStyle = rgba('#2a1406', 0.7); ctx.strokeText(text, x, y);
  ctx.restore();
}
function trackedText(ctx, text, x, y, font, track, col) {
  ctx.save(); ctx.font = font; ctx.textAlign = 'center'; ctx.letterSpacing = `${track}px`; ctx.fillStyle = col;
  ctx.shadowColor = 'rgba(0,0,0,0.85)'; ctx.shadowBlur = 16; ctx.fillText(text, x + track / 2, y); ctx.restore();
}
function title01(ctx, t) {
  const out = ease.in2(inv(2.95, 3.45, t));
  if (out >= 1) return;
  ctx.save(); ctx.globalAlpha = 1 - out; ctx.translate(W / 2, -out * 180 + 500); ctx.scale(1 + out * 0.12, 1 + out * 0.12); ctx.translate(-W / 2, -500);
  // THE
  const a1 = ease.out3(inv(EV.w_the, EV.w_the + 0.3, t));
  if (a1 > 0) { ctx.save(); ctx.globalAlpha *= a1; trackedText(ctx, 'THE', W / 2, 330 + (1 - a1) * 20, '600 50px Cinzel', 22, '#f2dcb4'); ctx.restore(); }
  // BRAZEN: light-sweep reveal
  const a2 = inv(EV.w_brazen, EV.w_brazen + 0.42, t);
  if (a2 > 0) {
    const L = cvs('ttl'), g = L.getContext('2d'); bronzeText(g, 'BRAZEN', W / 2, 505, 172, { weight: 800, track: 6 });
    g.globalCompositeOperation = 'destination-in'; const sx = lerp(-200, W + 300, ease.out3(a2));
    g.fillStyle = linGrad(g, sx - 260, 0, sx, 0, [[0, '#fff'], [1, 'rgba(255,255,255,0)']]); g.fillRect(0, 0, W, H);
    ctx.drawImage(L, 0, 0);
    if (a2 < 1) { ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.globalAlpha *= Math.sin(Math.PI * a2); glow(ctx, sx - 60, 450, 160, '#ffd890', 0.8); ctx.restore(); }
  }
  // BULL: slam
  const a3 = inv(EV.w_bull, EV.w_bull + 0.22, t);
  if (a3 > 0) { const s = lerp(1.45, 1, ease.out5(a3)); ctx.save(); ctx.globalAlpha *= clamp(a3 * 3); ctx.translate(W / 2, 640); ctx.scale(s, s); ctx.translate(-W / 2, -640);
    bronzeText(ctx, 'BULL', W / 2, 700, 236, { weight: 900, track: 10, glow: 1 + kick(t, EV.w_bull, 5) * 2 }); ctx.restore(); }
  // SIMULATION: tracking collapses in
  const a4 = ease.out3(inv(EV.w_sim, EV.w_sim + 0.5, t));
  if (a4 > 0) { ctx.save(); ctx.globalAlpha *= a4; trackedText(ctx, 'SIMULATION', W / 2, 800, '800 46px Inter', lerp(60, 24, a4), '#f0a548'); ctx.restore();
    ctx.save(); ctx.globalAlpha *= a4; ctx.fillStyle = rgba('#e9b468', 0.8); ctx.fillRect(W / 2 - 160 * a4, 838, 320 * a4, 3); ctx.restore(); }
  ctx.restore();
}
// big cinematic word (HEATSTROKE / THE BRAZEN BULL)
function bigWord(ctx, t, text, t0, t1, y, size, opt = {}) {
  if (t < t0 || t > t1) return;
  const a = inv(t0, t0 + 0.6, t), o = 1 - inv(t1 - 0.25, t1, t);
  const L = cvs('bigw'), g = L.getContext('2d');
  bronzeText(g, text, W / 2, y, size, { weight: 900, track: opt.track || 8, glowCol: opt.glowCol || '#ff4a1a', glow: 1.4 });
  g.globalCompositeOperation = 'destination-in'; const sx = lerp(-300, W + 400, ease.out3(a));
  g.fillStyle = linGrad(g, sx - 320, 0, sx, 0, [[0, '#fff'], [1, 'rgba(255,255,255,0)']]); g.fillRect(0, 0, W, H);
  ctx.save(); ctx.globalAlpha = o; ctx.drawImage(L, 0, 0);
  if (a < 1) { ctx.globalCompositeOperation = 'screen'; ctx.globalAlpha = o * Math.sin(Math.PI * a); glow(ctx, sx - 80, y - size * 0.35, 220, '#ffd08a', 0.9); }
  if (opt.sub) { ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = o * ease.out3(inv(t0 + 0.35, t0 + 0.8, t)); trackedText(ctx, opt.sub, W / 2, y + 70, '700 32px Inter', 14, '#e8c9a0'); }
  ctx.restore();
}

// captions: clean masked rise, amber/red key words, max 2 lines, TikTok-safe zone
const CAPS = [
  [3.72, 6.8, 'AN ANCIENT GREEK *LEGEND*'], [7.2, 10.45, 'EXTREME *HEAT*'], [10.78, 13.95, 'YOUR BODY TRIES TO *COOL DOWN*'],
  [14.25, 17.15, 'BLOOD VESSELS *WIDEN*'], [17.42, 20.9, 'YOUR HEART WORKS *HARDER*'], [21.08, 22.9, 'WATER AND SALTS ARE *LOST*'],
  [23.03, 24.66, 'WEAKNESS CAN *SET IN*'], [24.8, 26.24, 'HEAT STRESS *INCREASES*'], [26.62, 29.95, 'THE NERVOUS SYSTEM IS *AFFECTED*'],
  [30.12, 33.05, 'DIZZINESS AND *CONFUSION*'], [33.66, 37.0, 'THE BODY STRUGGLES TO *COOL ITSELF*'],
  [40.74, 43.6, 'BRAIN FUNCTION CAN BE *IMPAIRED*'], [43.82, 47.38, 'VITAL ORGANS ARE *AT RISK*'],
  [47.8, 50.9, 'SEVERE HEATSTROKE IS A ^MEDICAL EMERGENCY^'], [51.1, 54.66, 'CONSCIOUSNESS CAN BE *LOST*'],
  [54.86, 56.44, 'EXTREME HEAT CAN BE ^FATAL^'], [58.36, 59.86, 'A LEGEND OF *ANCIENT CRUELTY*'],
];
const CAP_Y = 1395, CAP_SIZE = 64, CAP_MAXW = 800;
function layoutCaption(ctx, text) {
  ctx.font = `900 ${CAP_SIZE}px Inter`;
  const words = []; let mode = 0;
  text.split(' ').forEach(w => {
    let m = mode, s = w;
    if (s.startsWith('*')) { m = 1; s = s.slice(1); } if (s.startsWith('^')) { m = 2; s = s.slice(1); }
    let end = false; if (s.endsWith('*') || s.endsWith('^')) { s = s.slice(0, -1); end = true; }
    words.push([s, m]); mode = end ? 0 : m;
  });
  const lines = [[]]; let wsum = 0; const sp = ctx.measureText(' ').width;
  for (const [s, m] of words) { const w = ctx.measureText(s).width; if (wsum + w > CAP_MAXW && lines[lines.length - 1].length) { lines.push([]); wsum = 0; } lines[lines.length - 1].push([s, m, w]); wsum += w + sp; }
  return { lines, sp };
}
function captions(ctx, t) {
  for (const [t0, t1, text] of CAPS) {
    if (t < t0 - 0.01 || t > t1) continue;
    const { lines, sp } = layoutCaption(ctx, text);
    const lh = CAP_SIZE * 1.12, y0 = CAP_Y - (lines.length - 1) * lh / 2;
    const o = 1 - ease.in2(inv(t1 - 0.2, t1, t));
    // rule
    const rk = ease.out3(inv(t0, t0 + 0.35, t));
    ctx.save(); ctx.globalAlpha = o; ctx.fillStyle = 'rgba(233,180,104,0.9)'; ctx.fillRect(W / 2 - 60 * rk, y0 - CAP_SIZE - 22, 120 * rk, 4); ctx.restore();
    lines.forEach((ln, li) => {
      const k = ease.out5(inv(t0 + li * 0.08, t0 + li * 0.08 + 0.42, t));
      const total = ln.reduce((a, [, , w]) => a + w, 0) + sp * (ln.length - 1);
      let x = W / 2 - total / 2; const y = y0 + li * lh;
      ctx.save(); ctx.beginPath(); ctx.rect(0, y - CAP_SIZE * 1.05, W, CAP_SIZE * 1.35); ctx.clip();
      ctx.globalAlpha = o * clamp(k * 1.4); ctx.translate(0, (1 - k) * CAP_SIZE * 0.9);
      ctx.font = `900 ${CAP_SIZE}px Inter`; ctx.textBaseline = 'alphabetic'; ctx.textAlign = 'left';
      for (const [s, m, w] of ln) {
        ctx.shadowColor = 'rgba(0,0,0,0.9)'; ctx.shadowBlur = 22; ctx.shadowOffsetY = 3;
        ctx.fillStyle = m === 1 ? '#f2a645' : m === 2 ? '#ff5a3c' : '#f6ecdc'; ctx.fillText(s, x, y);
        x += w + sp;
      }
      ctx.restore();
    });
  }
}

// ------------------------------------------------------------------ FILM
const FRAME = { c: null };
function FILM(ctx, t) {
  const F = cvs('frame'), g = F.getContext('2d');
  renderShots(g, t);
  // drops: subtle kick-synced exposure breathing (not a zoom on every beat)
  const inDrop = (t > EV.drop1 && t < 40.5) || (t > EV.drop2 && t < EV.sil3);
  if (inDrop) { g.save(); g.globalCompositeOperation = 'screen'; g.globalAlpha = 0.07 * kickPulse(t, 10); g.fillStyle = '#ffd8b0'; g.fillRect(0, 0, W, H); g.restore(); }
  // impact frames: punch + shake + flash (strength-scaled, each decays fast)
  let punch = 0, sx = 0, sy = 0, flash = 0, fcol = '#fff';
  for (const [ti, s, c] of IMPACTS) {
    if (t < ti || t > ti + 0.5) continue;
    const d = t - ti, e = Math.exp(-d * 14) * s;
    punch += 0.045 * e; flash = Math.max(flash, Math.exp(-d * 22) * s * 0.55); if (Math.exp(-d * 22) * s * 0.55 >= flash) fcol = c;
    const sh = Math.exp(-d * 10) * s * 22; sx += vnoise(t * 60 + ti) * sh; sy += vnoise(t * 60 + ti + 50) * sh;
  }
  ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
  ctx.save(); ctx.translate(W / 2 + sx, H / 2 + sy); ctx.scale(1 + punch, 1 + punch); ctx.translate(-W / 2, -H / 2); ctx.drawImage(F, 0, 0); ctx.restore();
  if (flash > 0.01 && fcol !== '#000000') { ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.globalAlpha = flash; ctx.fillStyle = fcol; ctx.fillRect(0, 0, W, H); ctx.restore(); }
  // bloom on bright content
  bloom(ctx, CAN === ctx.canvas ? F : F, 0.32, 40, 0.35);
  vignette(ctx, 0.55);
  // typography layer (unshaken)
  if (t < 3.5) title01(ctx, t);
  bigWord(ctx, t, 'HEATSTROKE', EV.clank, 40.5, 560, 112, { track: 6 });
  bigWord(ctx, t, 'THE BRAZEN BULL', EV.bar32 + 0.15, EV.sil3, 470, 96, { track: 6, glowCol: '#ff8a3a', sub: 'AN ANCIENT GREEK LEGEND' });
  captions(ctx, t);
  grain(ctx, Math.floor(t * 60), 0.07);
}
window.FILM = FILM;
