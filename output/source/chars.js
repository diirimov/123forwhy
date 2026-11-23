// Band member rigs: Morten (voice), Magne (keys), Pål (guitar). Original stylised designs.
const L = require('./lib');
const { shape, line, limb, ellipse, mix, shade, S, clamp, lerp } = L;

const SKIN = '#f1c7a6';
const DESIGN = {
  morten: {
    '80s': { hair: '#2a1b14', hairHi: '#5a3a28', jacket: '#1e1e26', jacketHi: '#3b3b4a', shirt: '#f4f1ea', pants: '#23222b', shoe: '#111', iris: '#3d6f8e', face: 'narrow', hairStyle: 'quiff', cuff: true },
    late: { hair: '#4a3a33', hairHi: '#857065', jacket: '#24252e', jacketHi: '#40424f', shirt: '#2f3038', pants: '#1f1f26', shoe: '#111', iris: '#3d6f8e', face: 'narrow', hairStyle: 'short', cuff: false },
  },
  magne: {
    '80s': { hair: '#e9c66a', hairHi: '#fbe6a6', jacket: '#5d94c9', jacketHi: '#8dbbe6', shirt: '#f7f4ee', pants: '#3a3f55', shoe: '#e9e6df', iris: '#4f7c5a', face: 'round', hairStyle: 'spiky', tie: '#c8323c' },
    late: { hair: '#cdb27a', hairHi: '#e8d6aa', jacket: '#3e6189', jacketHi: '#6087b2', shirt: '#e9e4da', pants: '#2c2f3d', shoe: '#2a2a2a', iris: '#4f7c5a', face: 'round', hairStyle: 'spikyShort', glasses: true },
  },
  pal: {
    '80s': { hair: '#6a3f24', hairHi: '#9a6640', jacket: '#8a2736', jacketHi: '#b94a58', shirt: '#2b2d3a', stripes: '#d9d4c7', pants: '#2b2a33', shoe: '#5a3a26', iris: '#5b4a35', face: 'oval', hairStyle: 'curly' },
    late: { hair: '#5a3d2c', hairHi: '#8a6a52', jacket: '#6a2531', jacketHi: '#94404d', shirt: '#25262e', stripes: '#9a958b', pants: '#25242c', shoe: '#3a2a20', iris: '#5b4a35', face: 'oval', hairStyle: 'curlyShort', cap: false },
  },
};

// two-bone IK: from shoulder s to target t, lengths a,b, bend sign
function ik(s, t, a, b, bend = 1) {
  let dx = t[0] - s[0], dy = t[1] - s[1]; let d = Math.hypot(dx, dy);
  const dm = Math.min(d, a + b - 0.01); if (d < 1e-3) { d = 1e-3; }
  const ang = Math.atan2(dy, dx);
  const cosA = clamp((a * a + dm * dm - b * b) / (2 * a * dm), -1, 1);
  const A = ang + bend * Math.acos(cosA);
  const e = [s[0] + Math.cos(A) * a, s[1] + Math.sin(A) * a];
  const h = [s[0] + Math.cos(ang) * dm, s[1] + Math.sin(ang) * dm];
  return [e, h];
}

function facePath(type) {
  return g => {
    if (type === 'narrow') { // high cheekbones, tapered jaw
      g.moveTo(0, -96); g.bezierCurveTo(44, -96, 62, -60, 62, -18); g.bezierCurveTo(62, 18, 50, 46, 34, 70); g.bezierCurveTo(22, 88, 10, 94, 0, 94);
      g.bezierCurveTo(-10, 94, -22, 88, -34, 70); g.bezierCurveTo(-50, 46, -62, 18, -62, -18); g.bezierCurveTo(-62, -60, -44, -96, 0, -96);
    } else if (type === 'round') {
      g.moveTo(0, -94); g.bezierCurveTo(50, -94, 68, -58, 68, -14); g.bezierCurveTo(68, 30, 56, 62, 36, 80); g.bezierCurveTo(24, 90, 12, 92, 0, 92);
      g.bezierCurveTo(-12, 92, -24, 90, -36, 80); g.bezierCurveTo(-56, 62, -68, 30, -68, -14); g.bezierCurveTo(-68, -58, -50, -94, 0, -94);
    } else { // oval, long
      g.moveTo(0, -100); g.bezierCurveTo(46, -100, 60, -62, 60, -16); g.bezierCurveTo(60, 26, 52, 60, 34, 80); g.bezierCurveTo(22, 94, 10, 98, 0, 98);
      g.bezierCurveTo(-10, 98, -22, 94, -34, 80); g.bezierCurveTo(-52, 60, -60, 26, -60, -16); g.bezierCurveTo(-60, -62, -46, -100, 0, -100);
    }
  };
}

// hair: back layer and front layer
function mop(g, R, bump, n, a0, a1, cy, sx = 1) {
  const steps = 120;
  for (let i = 0; i <= steps; i++) { const a = a0 + (a1 - a0) * i / steps; const r = R + bump * Math.abs(Math.sin(a * n)); const x = Math.cos(a) * r * sx, y = Math.sin(a) * r + cy; i ? g.lineTo(x, y) : g.moveTo(x, y); }
}
function hairBack(g, d, seed) {
  const c = d.hair;
  if (d.hairStyle === 'quiff') shape(g, g => { g.moveTo(-66, 10); g.bezierCurveTo(-82, -60, -70, -140, -10, -156); g.bezierCurveTo(50, -170, 96, -130, 80, -60); g.bezierCurveTo(78, -20, 74, 6, 66, 14); g.closePath(); }, c, { seed });
  else if (d.hairStyle === 'curly' || d.hairStyle === 'curlyShort') {
    const k = d.hairStyle === 'curly' ? 1 : .86;
    shape(g, g => { mop(g, 84 * k, 18 * k, 7, Math.PI * .92, Math.PI * 2.08, -22); g.closePath(); }, c, { seed });
  } else if (d.hairStyle === 'short') shape(g, g => { g.moveTo(-64, -6); g.bezierCurveTo(-72, -90, -30, -120, 4, -118); g.bezierCurveTo(54, -116, 76, -80, 66, -6); g.closePath(); }, c, { seed });
  else shape(g, g => { g.moveTo(-68, -10); g.bezierCurveTo(-74, -90, -30, -116, 0, -116); g.bezierCurveTo(40, -116, 74, -90, 68, -10); g.closePath(); }, c, { seed });
}
function hairFront(g, d, seed) {
  const c = d.hair, hi = d.hairHi;
  const sh = g2 => { g2.globalAlpha = .85; g2.strokeStyle = hi; g2.lineWidth = 6; g2.lineCap = 'round'; };
  switch (d.hairStyle) {
    case 'quiff': // tall swept-up 80s volume, forehead visible, sweeps to his left
      shape(g, g => { g.moveTo(-64, -14); g.bezierCurveTo(-74, -90, -46, -150, 6, -162); g.bezierCurveTo(58, -172, 98, -136, 84, -82); g.bezierCurveTo(78, -50, 70, -34, 64, -16); g.bezierCurveTo(58, -50, 44, -66, 22, -70); g.bezierCurveTo(0, -76, -30, -64, -44, -44); g.bezierCurveTo(-52, -34, -58, -24, -64, -14); }, c, {
        seed, shadeFn: g2 => { sh(g2); g2.beginPath(); g2.moveTo(-36, -96); g2.bezierCurveTo(-20, -140, 30, -156, 66, -130); g2.moveTo(-40, -66); g2.bezierCurveTo(-24, -106, 20, -118, 56, -100); g2.moveTo(-10, -132); g2.quadraticCurveTo(20, -146, 44, -142); g2.stroke(); }
      });
      break;
    case 'short':
      shape(g, g => { g.moveTo(-64, -30); g.bezierCurveTo(-66, -96, -20, -122, 10, -120); g.bezierCurveTo(54, -118, 70, -86, 66, -40); g.bezierCurveTo(50, -70, 14, -80, -16, -74); g.bezierCurveTo(-38, -66, -54, -50, -64, -30); }, c, { seed, shadeFn: g2 => { sh(g2); g2.beginPath(); g2.moveTo(-30, -100); g2.quadraticCurveTo(10, -118, 46, -104); g2.stroke(); } });
      break;
    case 'spiky': case 'spikyShort': {
      const k = d.hairStyle === 'spiky' ? 1 : .55;
      shape(g, g => {
        g.moveTo(-68, -18); g.bezierCurveTo(-76, -60, -70, -86, -60, -96);
        const tips = [[-86, -118], [-44, -116], [-46, -160], [-14, -124], [4, -174], [26, -126], [56, -160], [58, -114], [94, -116], [70, -84]];
        tips.forEach(([x, y], i) => { const yy = i % 2 ? y : lerp(-110, y, k); g.lineTo(x, yy); });
        g.bezierCurveTo(76, -60, 72, -40, 68, -18); g.bezierCurveTo(54, -58, 24, -70, -2, -68); g.bezierCurveTo(-30, -66, -54, -50, -68, -18);
      }, c, { seed, shadeFn: g2 => { sh(g2); g2.lineWidth = 5; g2.beginPath(); g2.moveTo(-30, -96); g2.lineTo(-38, -136); g2.moveTo(6, -98); g2.lineTo(4, -150); g2.moveTo(36, -96); g2.lineTo(50, -138); g2.stroke(); } });
      break;
    }
    case 'curly': case 'curlyShort': {
      const k = d.hairStyle === 'curly' ? 1 : .86;
      shape(g, g => { mop(g, 80 * k, 16 * k, 8, Math.PI * 1.02, Math.PI * 1.98, -30 * k); g.bezierCurveTo(56, -46, 30, -58, 0, -56); g.bezierCurveTo(-30, -58, -56, -46, -78 * k, -26); g.closePath(); }, c, {
        seed, shadeFn: g2 => { sh(g2); g2.lineWidth = 4.5; const r = rngLocal(seed); for (let i = 0; i < 16; i++) { const a = Math.PI * (1.08 + r() * .84), rr = 30 + r() * 52; const x = Math.cos(a) * rr, y = Math.sin(a) * rr - 30; g2.beginPath(); g2.arc(x, y, 7 + r() * 5, a + 1.2, a + 4.2); g2.stroke(); } }
      });
      break;
    }
  }
}
function rngLocal(s) { return L.rng(s * 977 + 13); }

// face features
function face(g, d, p) {
  const lx = (p.look?.[0] || 0) * 10, ly = (p.look?.[1] || 0) * 6;
  const blink = p.blink || 0; const closed = p.eyesClosed ? 1 : blink;
  const ex = 27;
  // eyes
  for (const s of [-1, 1]) {
    const x = s * ex + lx * .6, y = -6 + ly * .4;
    if (closed > .8) { line(g, g => { g.moveTo(x - 13, y + 1); g.quadraticCurveTo(x, y + 7, x + 13, y + 1); }, 4.5); }
    else {
      const hh = 11 * (1 - closed);
      shape(g, g => { g.moveTo(x - 15, y); g.quadraticCurveTo(x, y - hh * 1.5, x + 15, y); g.quadraticCurveTo(x, y + hh * 1.1, x - 15, y); }, '#fbf8f2', { lw: 3 });
      g.save(); g.beginPath(); g.moveTo(x - 15, y); g.quadraticCurveTo(x, y - hh * 1.5, x + 15, y); g.quadraticCurveTo(x, y + hh * 1.1, x - 15, y); g.clip();
      g.fillStyle = S.mode === 'color' ? d.iris : '#555'; g.beginPath(); ellipse(g, x + lx * .5, y + ly * .4, 8, 8); g.fill();
      g.fillStyle = '#111'; g.beginPath(); ellipse(g, x + lx * .5, y + ly * .4, 3.8, 3.8); g.fill();
      if (S.mode === 'color') { g.fillStyle = 'rgba(255,255,255,.9)'; g.beginPath(); ellipse(g, x + lx * .5 + 2.5, y + ly * .4 - 3, 2, 2); g.fill(); }
      g.restore();
      line(g, g => { g.moveTo(x - 16, y + 1); g.quadraticCurveTo(x, y - hh * 1.55, x + 16, y - 1); }, 5.5);
    }
    // brows
    const br = p.brows || 'neutral';
    const by = y - 24 - (br === 'up' ? 7 : 0);
    const tiltIn = br === 'sad' ? -7 : br === 'focus' ? 6 : 0;
    line(g, g => { g.moveTo(x - 16 * s * -1 * -1 - 0, by + (s < 0 ? tiltIn : 0) * 0); }, 0.01);
    line(g, g => {
      const inner = x - s * 15, outer = x + s * 17;
      g.moveTo(inner, by + tiltIn); g.quadraticCurveTo(x, by - 5, outer, by + 2 - tiltIn * .3);
    }, d.hairStyle === 'spiky' || d.hairStyle === 'spikyShort' ? 6 : 7.5, S.mode === 'color' ? shade(d.hair, -.45) : undefined);
  }
  // nose
  line(g, g => { g.moveTo(lx * .9 + 2, 6); g.quadraticCurveTo(lx * 1.2 + 9, 30, lx * .9 + 1, 34); }, 4);
  // mouth
  const m = p.mouth || 'closed', mx = lx * .8, my = 56 + ly * .3;
  if (m === 'closed') line(g, g => { g.moveTo(mx - 14, my); g.quadraticCurveTo(mx, my + 3, mx + 14, my); }, 4.5);
  else if (m === 'smile') { line(g, g => { g.moveTo(mx - 19, my - 4); g.quadraticCurveTo(mx, my + 13, mx + 19, my - 4); }, 4.5); }
  else if (m === 'sad') line(g, g => { g.moveTo(mx - 13, my + 5); g.quadraticCurveTo(mx, my - 4, mx + 13, my + 5); }, 4.5);
  else if (m === 'grin') shape(g, g => { g.moveTo(mx - 22, my - 6); g.quadraticCurveTo(mx, my + 22, mx + 22, my - 6); g.closePath(); }, '#6e2a2a', { lw: 4.5 });
  else { // sing/open with amount
    const o = clamp(p.open ?? .7, 0, 1.2);
    shape(g, g => { ellipse(g, mx, my + 4 * o, 10 + o * 5, 4 + o * 15); }, '#5a1f24', { lw: 4.5 });
    if (S.mode === 'color') { g.save(); g.beginPath(); ellipse(g, mx, my + 4 * o, 10 + o * 5, 4 + o * 15); g.clip(); g.fillStyle = '#f4f0ea'; g.fillRect(mx - 20, my + 4 * o - 4 - o * 15, 40, 6); g.restore(); }
  }
  if (d.glasses) {
    for (const s of [-1, 1]) { const x = s * ex + lx * .6; line(g, g => { g.roundRect(x - 21, -22, 42, 32, 9); }, 4.5); }
    line(g, g => { g.moveTo(-6 + lx * .6, -8); g.lineTo(6 + lx * .6, -8); }, 4);
  }
  if (p.stubble && S.mode === 'color') { g.save(); g.globalAlpha = .12; g.fillStyle = '#3a2a22'; g.beginPath(); ellipse(g, 0, 62, 44, 30); g.fill(); g.restore(); }
}

function head(g, who, d, p, seed) {
  const back = p.back;
  hairBack(g, d, seed + 1);
  // ears
  if (!back) for (const s of [-1, 1]) shape(g, g => { ellipse(g, s * (d.face === 'round' ? 66 : 60), 0, 11, 20); }, SKIN, { lw: 4.5, seed: seed + 2 });
  if (back) {
    shape(g, facePath(d.face), d.hair, { seed: seed + 3 });
    hairFront(g, d, seed + 4);
    return;
  }
  shape(g, facePath(d.face), SKIN, {
    seed: seed + 3, lw: 6, shadeFn: g2 => {
      // soft form shading on the shadow side + under-hair shadow
      const k = p.light ?? 1; const sx = (p.lightDir ?? 1);
      const gr = g2.createLinearGradient(-70 * sx, 0, 70 * sx, 0); gr.addColorStop(0, 'rgba(255,240,225,0)'); gr.addColorStop(.62, 'rgba(160,90,80,0)'); gr.addColorStop(1, `rgba(120,60,70,${.32 * k})`);
      g2.fillStyle = gr; g2.fillRect(-80, -110, 160, 220);
      g2.fillStyle = 'rgba(120,50,60,.12)'; g2.beginPath(); ellipse(g2, 0, -70, 70, 22); g2.fill();
      if (who === 'morten') { g2.fillStyle = 'rgba(150,70,70,.16)'; g2.beginPath(); ellipse(g2, -38, 26, 12, 22, .3); ellipse(g2, 38, 26, 12, 22, -.3); g2.fill(); }
    }
  });
  face(g, d, p);
  hairFront(g, d, seed + 4);
}

// pose: {x,y,s,flip,lean,bob,hl:[x,y],hr:[x,y],fl,fr, head:{tilt,look,blink,mouth,open,brows,eyesClosed}, back, era}
function drawMember(g, who, p) {
  const era = p.era || '80s'; const d = DESIGN[who][era];
  const seed = ({ morten: 10, magne: 40, pal: 70 })[who];
  g.save(); g.translate(p.x, p.y); g.scale(p.s * (p.flip || 1), p.s);
  g.rotate(p.lean || 0);
  const bob = p.bob || 0;
  const hip = -300 + bob;
  // legs
  const fl = p.fl || [-34, 0], fr = p.fr || [34, 0];
  for (const [hx, f] of [[-30, fl], [30, fr]]) {
    const [k, a] = ik([hx, hip], f, 152, 150, hx < 0 ? 1 : -1);
    limb(g, [[hx, hip], k, a], 50, d.pants, { lw: 6 });
    shape(g, g => { g.ellipse(a[0] + (hx < 0 ? -8 : 8), a[1] - 6, 32, 15, 0, 0, Math.PI * 2); }, d.shoe, { lw: 5, seed: seed + 9 });
  }
  const back = p.back;
  // torso
  const sh = -560 + bob;
  const torso = g => { g.moveTo(-72, sh + 10); g.bezierCurveTo(-74, sh - 8, -60, sh - 16, -40, sh - 18); g.lineTo(40, sh - 18); g.bezierCurveTo(60, sh - 16, 74, sh - 8, 72, sh + 10); g.lineTo(58, hip + 22); g.lineTo(-58, hip + 22); g.closePath(); };
  // back arm when holding things behind? arms
  const armPts = (side, target, bend) => { const s0 = [side * 64, sh + 4]; const [e, h] = ik(s0, target, 128, 122, bend); return [s0, e, h]; };
  const hl = p.hl || [-82, hip - 20], hr = p.hr || [82, hip - 20];
  const AL = armPts(-1, hl, p.bl ?? 1), AR = armPts(1, hr, p.br ?? -1);
  if (p.behindL) { limb(g, AL, 40, d.jacket, { hi: 1 }); shape(g, g => ellipse(g, AL[2][0], AL[2][1], 15, 15), SKIN, { lw: 4.5 }); }
  shape(g, torso, d.jacket, {
    seed: seed + 5, shadeFn: g2 => {
      if (who === 'morten') { g2.globalAlpha = .45; g2.strokeStyle = d.jacketHi; g2.lineWidth = 6; g2.beginPath(); g2.moveTo(-50, sh + 40); g2.quadraticCurveTo(-56, sh + 120, -44, hip); g2.stroke(); }
      const gr = g2.createLinearGradient(-70, 0, 70, 0); gr.addColorStop(0, 'rgba(255,255,255,.10)'); gr.addColorStop(.7, 'rgba(0,0,0,0)'); gr.addColorStop(1, 'rgba(0,0,30,.28)'); g2.fillStyle = gr; g2.fillRect(-80, sh - 30, 160, 330);
    }
  });
  if (!back) {
    // shirt V / stripes
    shape(g, g => { g.moveTo(-30, sh - 16); g.lineTo(30, sh - 16); g.lineTo(14, hip + 20); g.lineTo(-14, hip + 20); g.closePath(); }, d.shirt, {
      lw: 5, seed: seed + 6, shadeFn: d.stripes ? g2 => { g2.strokeStyle = d.stripes; g2.lineWidth = 6; for (let y = sh - 10; y < hip + 20; y += 18) { g2.beginPath(); g2.moveTo(-40, y); g2.lineTo(40, y); g2.stroke(); } } : null
    });
    if (d.tie) shape(g, g => { g.moveTo(-7, sh - 12); g.lineTo(7, sh - 12); g.lineTo(9, sh + 110); g.lineTo(0, sh + 124); g.lineTo(-9, sh + 110); g.closePath(); }, d.tie, { lw: 4.5 });
    // lapels
    shape(g, g => { g.moveTo(-30, sh - 16); g.lineTo(-52, sh - 6); g.lineTo(-24, sh + 90); g.lineTo(-14, hip + 20); g.closePath(); }, d.jacketHi, { lw: 5, seed: seed + 7 });
    shape(g, g => { g.moveTo(30, sh - 16); g.lineTo(52, sh - 6); g.lineTo(24, sh + 90); g.lineTo(14, hip + 20); g.closePath(); }, d.jacketHi, { lw: 5, seed: seed + 8 });
  }
  // neck
  shape(g, g => { g.rect(-20, sh - 52, 40, 40); }, back ? shade(SKIN, -.1) : SKIN, { lw: 5 });
  // head
  g.save(); g.translate(0, sh - 120); g.rotate(p.head?.tilt || 0);
  head(g, who, d, { ...(p.head || {}), back }, seed);
  g.restore();
  // held props between body and arms
  if (p.prop) p.prop(g, { hl, hr, sh, hip, d });
  if (!p.behindL) { limb(g, AL, 40, d.jacket, { hi: 1 }); shape(g, g => ellipse(g, AL[2][0], AL[2][1], 15, 15), SKIN, { lw: 4.5 }); }
  limb(g, AR, 40, d.jacket, { hi: 1 });
  if (d.cuff && S.mode === 'color') { g.save(); const h = AR[2], e = AR[1]; const t = .82; g.translate(lerp(e[0], h[0], t), lerp(e[1], h[1], t)); g.rotate(Math.atan2(h[1] - e[1], h[0] - e[0])); g.fillStyle = '#c9c9d1'; g.fillRect(-6, -22, 12, 44); g.restore(); }
  shape(g, g => ellipse(g, AR[2][0], AR[2][1], 15, 15), SKIN, { lw: 4.5 });
  if (p.front) p.front(g, { hl, hr, sh, hip, d });
  g.restore();
}

// instruments
function guitar(g, x, y, ang, sc = 1, col = '#c0392b') {
  g.save(); g.translate(x, y); g.rotate(ang); g.scale(sc, sc);
  shape(g, g => { g.rect(-6, -340, 26, 260); }, '#3a2618', { lw: 5 });
  shape(g, g => { g.roundRect(-10, -380, 34, 50, 8); }, '#2a1a12', { lw: 5 });
  shape(g, g => { g.moveTo(0, -100); g.bezierCurveTo(70, -110, 90, -40, 60, 0); g.bezierCurveTo(100, 40, 90, 120, 10, 120); g.bezierCurveTo(-70, 120, -90, 40, -50, 0); g.bezierCurveTo(-80, -40, -60, -110, 0, -100); }, col, {
    seed: 5, shadeFn: g2 => { g2.fillStyle = 'rgba(255,255,255,.18)'; g2.beginPath(); ellipse(g2, -20, -40, 22, 40, .4); g2.fill(); }
  });
  shape(g, g => { g.rect(-20, 30, 50, 14); }, '#222', { lw: 4 });
  shape(g, g => { g.rect(-14, -20, 38, 10); }, '#ddd', { lw: 3 });
  line(g, g => { for (let i = 0; i < 4; i++) { g.moveTo(-1 + i * 5.5, -370); g.lineTo(-1 + i * 5.5, 36); } }, 1.5, '#eee');
  g.restore();
}
function keyboard(g, x, y, w, pressed = [], sc = 1, col = '#24242c') {
  g.save(); g.translate(x, y); g.scale(sc, sc);
  shape(g, g => { g.roundRect(-w / 2, -40, w, 80, 10); }, col, { lw: 6 });
  shape(g, g => { g.rect(-w / 2 + 16, -10, w - 32, 44); }, '#f7f5ef', { lw: 4 });
  const n = Math.floor((w - 32) / 22);
  g.save(); g.strokeStyle = S.mode === 'color' ? '#555' : S.graphite; g.lineWidth = 2;
  for (let i = 0; i < n; i++) {
    const kx = -w / 2 + 16 + i * 22;
    if (pressed.includes(i)) { g.fillStyle = S.mode === 'color' ? '#ffd36e' : '#999'; g.fillRect(kx + 1, -9, 21, 42); }
    g.beginPath(); g.moveTo(kx, -10); g.lineTo(kx, 34); g.stroke();
    if ([1, 2, 4, 5, 6].includes(i % 7)) { g.fillStyle = S.mode === 'color' ? '#1a1a1f' : S.graphite; g.fillRect(kx - 6, -10, 12, 26); }
  }
  g.restore();
  // panel lights
  if (S.mode === 'color') for (let i = 0; i < 6; i++) { g.fillStyle = i % 2 ? '#ff5a4e' : '#5ef0c0'; g.fillRect(-w / 2 + 30 + i * 26, -30, 12, 6); }
  g.restore();
}
function micStand(g, x, y, h, sc = 1) {
  g.save(); g.translate(x, y); g.scale(sc, sc);
  line(g, g => { g.moveTo(0, 0); g.lineTo(0, -h); g.moveTo(-50, 0); g.lineTo(0, -16); g.lineTo(50, 0); }, 8, '#2a2a30');
  shape(g, g => { g.roundRect(-14, -h - 46, 28, 54, 12); }, '#3a3a44', { lw: 5 });
  g.restore();
}
function handMic(g, x, y, ang = -.4, sc = 1) {
  g.save(); g.translate(x, y); g.rotate(ang); g.scale(sc, sc);
  shape(g, g => { g.moveTo(-8, 0); g.lineTo(8, 0); g.lineTo(6, 70); g.lineTo(-6, 70); g.closePath(); }, '#202026', { lw: 4 });
  shape(g, g => { ellipse(g, 0, -10, 17, 20); }, '#9aa0aa', { lw: 4.5, shadeFn: g2 => { g2.strokeStyle = 'rgba(0,0,0,.35)'; g2.lineWidth = 2; for (let i = -16; i < 16; i += 6) { g2.beginPath(); g2.moveTo(i, -32); g2.lineTo(i, 12); g2.stroke(); } } });
  g.restore();
}

module.exports = { drawMember, DESIGN, guitar, keyboard, micStand, handMic, SKIN, ik };
