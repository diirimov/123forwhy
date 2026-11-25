// Frame compositor + parallel renderer.
//   node src/render.js stills 0.5,5.6,12.3 [scale]     -> out/stills/*.png
//   node src/render.js segment <f0> <f1> <out.mp4>      -> one encoded segment
//   node src/render.js all [workers]                     -> out/video_noaudio.mp4
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const C = require('./core');
const { W, H, FPS, NFRAMES, clamp, outQ, inQ } = C;
const F = require('./film');
const SHOTS = require(process.env.SHOTS === 'v1' ? './shots' : './shots2');

const main = C.canvas(), comp = C.canvas(), tmp = C.canvas();
const WHIP = 0.1;

function shotAt(t) { const S = SHOTS.SH; for (const s of S) if (t >= s.t0 && t < s.t1) return s; return S[S.length - 1]; }
function drawShot(cv, t) {
  const x = cv.getContext('2d'); x.setTransform(1, 0, 0, 1, 0, 0); x.globalAlpha = 1; x.globalCompositeOperation = 'source-over';
  x.clearRect(0, 0, W, H);
  const s = shotAt(t); x.save(); s.draw(x, t, t - s.t0); x.restore();
  return s;
}

function renderFrame(f) {
  const t = f / FPS;
  drawShot(main, t);
  let src = main;
  // whip transitions (motion-blurred slide out / in)
  for (const tr of SHOTS.TRANS) {
    if (!tr.kind.startsWith('whip')) continue;
    const dt = t - tr.t; if (dt < -WHIP || dt >= WHIP) continue;
    const dir = { whipL: [-1, 0], whipR: [1, 0], whipU: [0, -1], whipD: [0, 1] }[tr.kind];
    const k = dt < 0 ? inQ((dt + WHIP) / WHIP) : 1 - outQ(dt / WHIP);
    const off = (dt < 0 ? 1 : -1) * k * 0.55, blur = k * 260;
    const x = comp.getContext('2d'); x.setTransform(1, 0, 0, 1, 0, 0); x.globalAlpha = 1;
    x.fillStyle = '#20120c'; x.fillRect(0, 0, W, H);
    const n = 7;
    for (let i = 0; i < n; i++) { const kk = i / (n - 1) - 0.5; x.globalAlpha = 1 / (i + 1); x.drawImage(main, dir[0] * (off * W + blur * kk), dir[1] * (off * H + blur * kk)); }
    x.globalAlpha = 1; src = comp;
  }
  // beat pulse (gentle zoom on each beat in the groove sections)
  let z = 1;
  for (const [a, b] of SHOTS.PULSE) if (t >= a && t < b) { const bt = Math.floor(t / C.BEAT) * C.BEAT; z = 1 + 0.014 * Math.exp(-(t - bt) * 16); }
  const out = tmp.getContext('2d'); out.setTransform(1, 0, 0, 1, 0, 0); out.globalAlpha = 1; out.globalCompositeOperation = 'source-over';
  out.fillStyle = '#20120c'; out.fillRect(0, 0, W, H);
  out.drawImage(src, (W - W * z) / 2, (H - H * z) / 2, W * z, H * z);
  F.post(out, t);
  // flashes
  for (const tr of SHOTS.TRANS) if (tr.kind === 'flash') { const a = Math.max(0, 1 - Math.abs(t - tr.t) / 0.1); if (a > 0) { out.fillStyle = `rgba(255,248,232,${0.8 * a})`; out.fillRect(0, 0, W, H); } }
  // text layers (clean, on top of the grade)
  for (const s of SHOTS.STAMPS) F.drawStamp(out, s, t);
  for (const s of SHOTS.SFXTEXT) F.drawSfxText(out, s, t);
  for (const s of SHOTS.SUBS) F.drawSub(out, s, t);
  return tmp;
}

async function segment(f0, f1, file) {
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', `${W}x${H}`, '-r', String(FPS), '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-g', '120', file], { stdio: ['pipe', 'inherit', 'inherit'] });
  const t0 = Date.now();
  for (let f = f0; f < f1; f++) {
    const cv = renderFrame(f);
    const buf = cv.data();
    if (!ff.stdin.write(Buffer.from(buf))) await new Promise(r => ff.stdin.once('drain', r));
    if ((f - f0) % 120 === 0) process.stderr.write(`[${f0}-${f1}] frame ${f} ${((Date.now() - t0) / (f - f0 + 1)).toFixed(0)} ms/f\n`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
}

async function all(workers = 4) {
  const dir = path.join(__dirname, '..', 'out'); fs.mkdirSync(dir, { recursive: true });
  // split by shot boundaries roughly evenly so each worker keeps its caches warm
  const per = Math.ceil(NFRAMES / workers), jobs = [];
  for (let i = 0; i < workers; i++) {
    const a = i * per, b = Math.min(NFRAMES, (i + 1) * per), file = path.join(dir, `seg_${i}.mp4`);
    jobs.push(new Promise((res, rej) => { const p = spawn('node', ['--max-old-space-size=6000', __filename, 'segment', a, b, file], { stdio: 'inherit' }); p.on('close', c => c === 0 ? res(file) : rej(new Error('segment ' + i))); }));
  }
  const files = await Promise.all(jobs);
  fs.writeFileSync(path.join(dir, 'segs.txt'), files.map(f => `file '${f}'`).join('\n'));
  await new Promise(r => spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', path.join(dir, 'segs.txt'), '-c', 'copy', path.join(dir, 'video_noaudio.mp4')], { stdio: 'inherit' }).on('close', r));
  fs.writeFileSync(path.join(dir, 'sfx_cues.json'), JSON.stringify(SHOTS.SFX.sort((a, b) => a.t - b.t), null, 1));
}

if (require.main === module) {
  const [cmd, a, b, c] = process.argv.slice(2);
  if (cmd === 'stills') {
    const dir = path.join(__dirname, '..', 'out', 'stills'); fs.mkdirSync(dir, { recursive: true });
    const sc = parseFloat(b || '0.5');
    for (const ts of a.split(',')) {
      const t = parseFloat(ts), cv = renderFrame(Math.round(t * FPS));
      const o = C.canvas(W * sc, H * sc); o.getContext('2d').drawImage(cv, 0, 0, W * sc, H * sc);
      fs.writeFileSync(path.join(dir, `s_${t.toFixed(2)}.png`), o.toBuffer('image/png'));
    }
  } else if (cmd === 'segment') segment(+a, +b, c);
  else if (cmd === 'all') all(+(a || 4)).then(() => console.log('done'));
  else if (cmd === 'cues') { fs.writeFileSync(path.join(__dirname, '..', 'out', 'sfx_cues.json'), JSON.stringify(SHOTS.SFX.sort((a, b) => a.t - b.t), null, 1)); }
}
module.exports = { renderFrame };
