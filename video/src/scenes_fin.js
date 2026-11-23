// ---------- FINALE (B41–B48) ----------
const PAGES = [
  { num: 'I', name: 'The Black Death', year: 'Anno 1347', lines: ['Carried by fleas on rats,', 'it swept from Sicily', 'across all of Europe.'], col: '#8a1a14' },
  { num: 'II', name: 'Leprosy', year: 'Feared for centuries', lines: ['The sick were shunned,', 'made to carry clappers', 'and cast out of towns.'], col: '#2f6a66' },
  { num: 'III', name: 'The Sweating Sickness', year: 'Anno 1485', lines: ['A sudden fever and sweat.', 'Death could come', 'within hours.'], col: '#a8601a' },
];
function pageIllus(ctx, idx, x, y, w, h, t) { // inked illustration inside a frame on the right page
  ctx.save(); ctx.translate(x, y);
  rr(ctx, -w / 2, -h / 2, w, h, 6); ctx.fillStyle = '#efdcae'; ctx.fill(); ctx.lineWidth = 5; ctx.strokeStyle = PAGES[idx].col; ctx.stroke();
  ctx.beginPath(); ctx.rect(-w / 2 + 6, -h / 2 + 6, w - 12, h - 12); ctx.clip();
  if (idx === 0) {
    drawMoon(ctx, 60, -h * .28, 60, '#d8452e', 'rgba(255,60,30,.2)');
    drawDoctor(ctx, { x: -10, y: h * .44, s: .78, t, ph: (t / BEAT) * .5, turn: Math.sin(t * 2) * .3, eyeGlow: .8, lamp: .5 });
    for (let k = 0; k < 3; k++) drawRat(ctx, ((t * 260 + k * 160) % (w + 200)) - w / 2 - 100, h * .45 - k * 10, .55, 1, t * 5 + k, t);
  } else if (idx === 1) {
    ctx.fillStyle = 'rgba(80,120,110,.25)'; ctx.fillRect(-w, -h, w * 2, h * 2);
    drawWall(ctx, -w, w, h * .25, 200, 120, 0, { stone: '#8a8a80', inside: '#e8b860' });
    leper(ctx, -60 + Math.sin(t) * 10, h * .42, 1.05, 1, t, {});
  } else {
    drawClock(ctx, 0, -h * .2, 120, t * 3, t * 18, t);
    drawPerson(ctx, { x: -20, y: h * .62, s: 1.4, face: 1, pose: { lean: Math.sin(t * 4) * .1, bob: bounce(t, 5), lt: [0, 0], rt: [0, 0], la: [2.7, 1.6], ra: [2.2, 1.2] }, c: { tunic: '#6a1e3a', skin: '#efbd96' }, head: 'tudor', ex: { eyes: 'wide', mouth: 'scream', brow: 1.3 }, sweat: 1, flush: .6, t: t * 1.6, shadow: false });
  }
  ctx.restore();
  // sepia ink wash over the illustration
  ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.globalAlpha = .28; ctx.fillStyle = '#c8a070'; ctx.fillRect(x - w / 2, y - h / 2, w, h); ctx.restore();
}
function pageText(ctx, idx, x, y, w, h, t, a = 1) {
  const P = PAGES[idx];
  ctx.save(); ctx.globalAlpha *= a; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillStyle = P.col; ctx.font = `150px ${FONTS.goth}`; ctx.fillText(P.num, x, y - h * .32);
  ctx.fillStyle = '#2a1a10'; ctx.font = `${idx === 2 ? 50 : 62}px ${FONTS.fellsc}`; ctx.fillText(P.name, x, y - h * .12);
  ctx.fillStyle = P.col; ctx.font = `italic 40px ${FONTS.fell}`; ctx.fillText(P.year, x, y - h * .02);
  ctx.fillStyle = '#3a2a1a'; ctx.font = `38px ${FONTS.fell}`; P.lines.forEach((l, i) => ctx.fillText(l, x, y + h * .1 + i * 52));
  ctx.strokeStyle = P.col; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(x - w * .3, y + h * .37); ctx.lineTo(x + w * .3, y + h * .37); ctx.stroke();
  ctx.restore();
}
function drawOpenBook(ctx, t, pageIdx, flip, flipTo, cover) {
  const PW = 470, PH = 720;
  // shadow + cover boards
  ctx.save(); ctx.shadowColor = 'rgba(0,0,0,.7)'; ctx.shadowBlur = 60; ctx.shadowOffsetY = 30;
  rr(ctx, -PW - 30, -PH / 2 - 26, PW * 2 + 60, PH + 52, 20); ctx.fillStyle = '#4a1a16'; ctx.fill(); ctx.restore();
  rr(ctx, -PW - 30, -PH / 2 - 26, PW * 2 + 60, PH + 52, 20); fillStroke(ctx, null, 7);
  // pages
  for (const side of [-1, 1]) {
    ctx.beginPath(); ctx.moveTo(0, -PH / 2 + 6); ctx.quadraticCurveTo(side * PW * .5, -PH / 2 - 14, side * PW, -PH / 2); ctx.lineTo(side * PW, PH / 2); ctx.quadraticCurveTo(side * PW * .5, PH / 2 - 16, 0, PH / 2 + 6); ctx.closePath();
    const g = ctx.createLinearGradient(0, 0, side * PW, 0); g.addColorStop(0, '#b89a62'); g.addColorStop(.12, '#ecd9aa'); g.addColorStop(1, '#e2c994'); fillStroke(ctx, g, 4);
  }
  // content: left text, right illustration
  pageText(ctx, pageIdx, -PW / 2, 0, PW, PH, t);
  pageIllus(ctx, pageIdx, PW / 2, -10, PW * .78, PH * .82, t);
  // flipping sheet (right -> left), reveals next content underneath on the right first
  if (flip > 0 && flip < 1) {
    ctx.save(); ctx.beginPath(); ctx.rect(0, -PH, PW + 10, PH * 2); ctx.clip();
    ctx.beginPath(); ctx.rect(-10, -PH / 2 - 10, PW + 20, PH + 20); ctx.fillStyle = '#e8d3a3'; ctx.fill();
    pageIllus(ctx, flipTo, PW / 2, -10, PW * .78, PH * .82, t);
    ctx.restore();
    ctx.save(); ctx.beginPath(); ctx.rect(-PW - 10, -PH, PW + 10, PH * 2); ctx.clip();
    if (flip > .5) { pageText(ctx, flipTo, -PW / 2, 0, PW, PH, t); }
    ctx.restore();
    const a = flip * Math.PI, wv = Math.cos(a) * PW, lift = Math.sin(a) * 60;
    ctx.beginPath(); ctx.moveTo(0, -PH / 2); ctx.lineTo(wv, -PH / 2 - lift); ctx.lineTo(wv, PH / 2 + lift * .3); ctx.lineTo(0, PH / 2); ctx.closePath();
    const g = ctx.createLinearGradient(0, 0, wv, 0); g.addColorStop(0, '#c8ac74'); g.addColorStop(1, flip < .5 ? '#f4e4bc' : '#d6bd88'); fillStroke(ctx, g, 4);
  }
  // spine shadow
  ctx.fillStyle = vgrad(ctx, 0, 1, [[0, 'rgba(0,0,0,0)'], [1, 'rgba(0,0,0,0)']]);
  const sg = ctx.createLinearGradient(-40, 0, 40, 0); sg.addColorStop(0, 'rgba(60,30,10,0)'); sg.addColorStop(.5, 'rgba(60,30,10,.45)'); sg.addColorStop(1, 'rgba(60,30,10,0)'); ctx.fillStyle = sg; ctx.fillRect(-40, -PH / 2, 80, PH);
  // front cover swinging open
  if (cover < 1) {
    const a = cover * Math.PI, wv = Math.cos(a) * (PW + 30);
    ctx.beginPath(); ctx.moveTo(0, -PH / 2 - 26); ctx.lineTo(wv, -PH / 2 - 26 - Math.sin(a) * 80); ctx.lineTo(wv, PH / 2 + 26 + Math.sin(a) * 30); ctx.lineTo(0, PH / 2 + 26); ctx.closePath();
    fillStroke(ctx, cover < .5 ? '#5a1e18' : '#3a120e', 7);
    if (cover < .5) { ctx.save(); ctx.translate(wv / 2, 0); ctx.scale(Math.cos(a), 1); ctx.strokeStyle = '#c9a043'; ctx.lineWidth = 6; rr(ctx, -PW * .4, -PH * .4, PW * .8, PH * .8, 10); ctx.stroke(); ctx.fillStyle = '#c9a043'; ctx.font = `90px ${FONTS.goth}`; ctx.textAlign = 'center'; ctx.fillText('Physick', 0, -40); ctx.font = `40px ${FONTS.fellsc}`; ctx.fillText('of the Plagues', 0, 30); ctx.restore(); }
  }
}
// S22 — the medical book (B41–B44)
scene(TB(41), TB(45), (ctx, t) => {
  const lt = t - TB(41);
  const cover = E.outBack(clamp(lt / .32));
  const flips = [TB(42), TB(43)];
  let page = 0, flip = 0, flipTo = 0;
  for (let k = 0; k < 2; k++) { if (t >= flips[k] + .32) page = k + 1; else if (t >= flips[k] - .02) { page = k; flipTo = k + 1; flip = E.inOut(clamp((t - flips[k] + .02) / .34)); } }
  // B44: page buzz — fast flips through all three on beats
  if (t >= TB(44)) { const b = Math.floor((t - TB(44)) / BEAT); page = [0, 1, 2, 2][b]; flip = 0; }
  const p = prog(lt, 0, 7.5);
  const cam = { x: Math.sin(lt * .5) * 60, y: lerp(60, -20, p), z: (lerp(1.0, 1.08, p) + (t >= TB(44) ? E.in(prog(t, TB(44, 8), TB(45))) * .9 : 0)) * (1 + kickEnv(t) * .03), r: lerp(-.06, .04, E.inOut(p)) };
  const sh = shakeAt(t, [TB(41), TB(42), TB(43)], 26, .15); cam.x += sh.x; cam.y += sh.y;
  // desk
  ctx.fillStyle = '#1a0e08'; ctx.fillRect(0, 0, W, H);
  ctx.save(); applyCam(ctx, cam, 1);
  ctx.fillStyle = '#3a2214'; ctx.fillRect(-1400, -1400, 2800, 2800);
  ctx.strokeStyle = 'rgba(0,0,0,.35)'; ctx.lineWidth = 3; for (let y = -1400; y < 1400; y += 38) { ctx.beginPath(); ctx.moveTo(-1400, y); for (let x = -1400; x < 1400; x += 100) ctx.lineTo(x, y + Math.sin(x * .01 + y) * 6); ctx.stroke(); }
  drawCandle(ctx, -420, -560, 1.1, t, 120); drawCandle(ctx, 450, 620, 1.2, t + 3, 90);
  ctx.save(); ctx.rotate(-.06); ctx.scale(1.02, 1.02); drawOpenBook(ctx, t, page, flip, flipTo, cover); ctx.restore();
  // dust burst from the slam
  for (let k = 0; k < 50; k++) { const d = lt; if (d > 1.6) break; const a = hash(k) * TAU, r = E.out(clamp(d / 1.4)) * (300 + hash(k + 3) * 600); ctx.save(); ctx.globalAlpha = (1 - d / 1.6) * .35; ctx.fillStyle = '#e8d0a0'; ell(ctx, Math.cos(a) * r, Math.sin(a) * r * .7, 6 + d * 10, 6 + d * 10); ctx.fill(); ctx.restore(); }
  ctx.restore();
  ctx.save(); ctx.globalCompositeOperation = 'lighter'; for (let k = 0; k < 40; k++) { const x = (hash(k) * W + t * 25 * (hash(k + 1) - .3)) % W, y = (hash(k + 2) * H - t * 40 * hash(k + 3) + H * 4) % H; ctx.globalAlpha = .35 * hash(k + 4); ell(ctx, x, y, 2.5, 2.5); ctx.fillStyle = '#ffe0a8'; ctx.fill(); } ctx.restore();
  const f = clamp(1 - lt / .12); if (f > 0) { ctx.fillStyle = `rgba(255,200,120,${f * .4})`; ctx.fillRect(0, 0, W, H); }
}, { mb: lt => lt < .3 ? 3 : 1, post: { vig: .7, paper: .3 } });

// S23 — NO ANTIBIOTICS / NO REAL CURES / JUST FEAR (B45–B46)
const STATE = [[TB(45, 0), 'NO ANTIBIOTICS.', vigBD], [TB(45, 8), 'NO REAL CURES.', vigLEP], [TB(46, 0), 'JUST FEAR.', vigSW]];
scene(TB(45), TB(47), (ctx, t) => {
  let i = 0; for (let k = 0; k < 3; k++) if (t >= STATE[k][0]) i = k;
  const lt = t - STATE[i][0];
  NOTEXT = true; STATE[i][2](ctx, t, { zoom: 1.15 + lt * .12, rot: (i - 1) * .03 }); NOTEXT = false;
  ctx.save(); ctx.globalAlpha = .55; ctx.fillStyle = '#080406'; ctx.fillRect(0, 0, W, H); ctx.restore();
  const size = i === 2 ? 190 : 118;
  const s = slam(lt, .2);
  ctx.save(); ctx.translate(W / 2, 900 + (i === 2 ? 0 : 0)); ctx.scale(s.s * (1 + lt * .03), s.s * (1 + lt * .03)); ctx.rotate(s.rot * .5 + (i - 1) * .02); ctx.globalAlpha = s.a;
  const words = STATE[i][1].split(' ');
  if (i === 2) fancyText(ctx, STATE[i][1], 0, 0, { size, font: FONTS.goth, color: '#ff4a36', glow: 'rgba(255,30,20,.9)', glowR: 60, strokeW: 18, track: 6 });
  else { fancyText(ctx, words[0], 0, -size * .62, { size, font: FONTS.cin, weight: 900, color: '#f6ead0', glow: 'rgba(255,60,30,.6)', strokeW: 16, track: 4 }); fancyText(ctx, words.slice(1).join(' '), 0, size * .55, { size, font: FONTS.cin, weight: 900, color: '#f6ead0', glow: 'rgba(255,60,30,.6)', strokeW: 16, track: 4 }); }
  ctx.restore();
  const f = clamp(1 - lt / .07); if (f > 0) { ctx.fillStyle = `rgba(255,230,200,${f * .3})`; ctx.fillRect(0, 0, W, H); }
}, { post: { vig: .6 } });

// S24 — the city under a dark sky, pull back (B47)
scene(TB(47), TB(48), (ctx, t) => {
  const lt = t - TB(47), p = E.out(prog(lt, 0, 1.875));
  const towerX = ENV.row.tower.x - 1800 + ENV.row.tower.w / 2;
  const cam = { x: lerp(towerX - 200, towerX - 100, p), y: lerp(-500, -760, p), z: lerp(1.25, .5, p) * (1 + kickEnv(t) * .02), r: lerp(.05, 0, p) };
  const sh = shakeAt(t, [0, 3, 6, 8, 11].map(s => TB(47, s)), 8, .07); cam.x += sh.x; cam.y += sh.y;
  streetBackdrop(ctx, t, cam, { sky: [[0, '#040306'], [.5, '#1c0810'], [.85, '#5a1018'], [1, '#8a2018']], moonCol: '#c8402a', moonX: 900, moonY: -1150, cloudCol: '#1a0508' });
  streetMain(ctx, t, cam, { litFn: w => w.lit && hash(w.x + w.y) < .35 });
  ctx.save(); applyCam(ctx, cam, 1);
  drawBell(ctx, towerX, ENV.row.tower.bell[1] - ENV.row.baseY - 40, 1.2, Math.sin((t / BEAT) * Math.PI) * .5);
  ctx.restore();
  // rain
  ctx.save(); ctx.strokeStyle = 'rgba(200,190,220,.25)'; ctx.lineWidth = 2; for (let k = 0; k < 140; k++) { const x = (hash(k) * W * 1.3 + t * 300) % (W * 1.3) - 100, y = (hash(k + 1) * H + t * 2200) % H; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x - 14, y + 60); ctx.stroke(); } ctx.restore();
  caption(ctx, ['THE MIDDLE AGES', 'WERE BRUTAL.'], t, TB(47) + .03, TB(48) - .12, { y: 760, size: 104 });
}, { post: { vig: .7 } });

// S25 — end card on the stop-time hits (B48)
scene(TB(48), DUR + 1, (ctx, t) => {
  const lt = t - TB(48);
  const hits = [TB(48, 0), TB(48, 3), TB(48, 6)], fin = TB(48, 12);
  const finK = t >= fin ? Math.exp(-(t - fin) / .25) : 0;
  const roll = t >= TB(48, 8) && t < fin ? (t - TB(48, 8)) / (fin - TB(48, 8)) : 0;
  ctx.fillStyle = vgrad(ctx, 0, H, [[0, '#0a0406'], [.5, '#2a0a0e'], [1, '#0a0406']]); ctx.fillRect(0, 0, W, H);
  glow(ctx, W / 2, 1150, 900, 'rgba(255,60,30,.25)', 1 + finK);
  const zoom = 1 + lt * .03 + finK * .04 + (t >= fin ? (t - fin) * .06 : 0);
  ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(zoom, zoom); ctx.translate(-W / 2, -H / 2);
  const rsh = roll > 0 ? (hash(Math.floor(t * 60)) - .5) * 10 * roll : 0;
  // question lines
  const Q = [['WHICH ONE WAS', 0, 98], ['THE MOST', 1, 98], ['TERRIFYING?', 2, 150]];
  Q.forEach(([s, k, size], j) => { const sl = slam(t - hits[k], .18); if (!sl) return; ctx.save(); ctx.translate(W / 2 + rsh, 360 + j * 130 + (j === 2 ? 30 : 0)); ctx.scale(sl.s, sl.s); ctx.globalAlpha = sl.a;
    fancyText(ctx, s, 0, 0, { size, font: j === 2 ? FONTS.goth : FONTS.cin, weight: 900, color: j === 2 ? '#ff4a36' : '#f6ead0', glow: j === 2 ? `rgba(255,30,20,${.8 + finK * .2})` : 'rgba(0,0,0,.6)', glowR: j === 2 ? 50 + finK * 60 : 20, strokeW: size * .12, track: 4 }); ctx.restore(); });
  // three medallions
  const fns = [vigBD, vigLEP, vigSW], names = [['BLACK', 'DEATH'], ['LEPROSY'], ['SWEATING', 'SICKNESS']];
  for (let k = 0; k < 3; k++) {
    const sl = slam(t - hits[k], .2); if (!sl) continue;
    const cx = [W / 2 - 320, W / 2, W / 2 + 320][k], cy = [1060, 1160, 1060][k], r = 145 * (1 + finK * .12);
    ctx.save(); ctx.translate(cx + rsh * (k - 1), cy); ctx.scale(sl.s, sl.s); ctx.globalAlpha = sl.a;
    ctx.save(); ell(ctx, 0, 0, r, r); ctx.clip(); const FOC = [[540, 1060], [470, 1000], [540, 1420]][k]; ctx.scale(.42, .42); ctx.translate(-FOC[0], -FOC[1]); NOTEXT = true; fns[k](ctx, t, { zoom: 1.15 }); NOTEXT = false; ctx.restore();
    ell(ctx, 0, 0, r, r); ctx.lineWidth = 12; ctx.strokeStyle = '#c9a043'; ctx.stroke(); ell(ctx, 0, 0, r + 8, r + 8); ctx.lineWidth = 4; ctx.strokeStyle = INK; ctx.stroke();
    fancyText(ctx, ['I', 'II', 'III'][k], 0, -r - 40, { size: 70, font: FONTS.goth, color: '#f6ead0', strokeW: 9 });
    names[k].forEach((nm, j) => fancyText(ctx, nm, 0, r + 50 + j * 50, { size: 44, font: FONTS.cin, weight: 900, color: '#f6ead0', strokeW: 7, track: 2 }));
    ctx.restore();
  }
  ctx.restore();
  if (finK > 0) { ctx.fillStyle = `rgba(255,120,80,${finK * .3})`; ctx.fillRect(0, 0, W, H); }
}, { post: { vig: .6 } });
