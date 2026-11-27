// THE PIED PIPER OF HAMELIN -- renderer
//   node render.js stills <outdir> t1 t2 ...          single frames (jpg)
//   node render.js sheet <out.jpg> t0 t1 n [cols]      contact sheet
//   node render.js range <f0> <f1> <out.mp4>           encode a frame range (worker)
//   node render.js final [workers]                     full film: parallel chunks -> concat -> mux approved soundtrack
'use strict';
const fs = require('fs'), path = require('path'), { spawn, spawnSync } = require('child_process');
const { createCanvas } = require('@napi-rs/canvas');
const C = require('./src/core');
const F = require('./src/film');

const [mode, ...args] = process.argv.slice(2);
const cv = createCanvas(C.W, C.H), g = cv.getContext('2d');

async function range(f0, f1, out) {
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', `${C.W}x${C.H}`, '-r', '60', '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '15', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
    '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const t0 = Date.now();
  for (let f = f0; f < f1; f++) {
    F.renderFrame(g, f / 60);
    if (!ff.stdin.write(Buffer.from(cv.data()))) await new Promise(r => ff.stdin.once('drain', r));
    if (global.gc && f % 20 === 0) global.gc();          // native canvas objects are only freed on GC
    if ((f - f0) % 300 === 0) console.log(path.basename(out), f, ((Date.now() - t0) / (f - f0 + 1)).toFixed(0) + ' ms/f');
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));
}

(async () => {
  if (mode === 'stills') {
    const dir = args[0]; fs.mkdirSync(dir, { recursive: true });
    for (const ts of args.slice(1)) { const t = parseFloat(ts); F.renderFrame(g, t); fs.writeFileSync(path.join(dir, `t${t.toFixed(3)}.jpg`), cv.toBuffer('image/jpeg', 90)); }
  } else if (mode === 'sheet') {
    const [out, a, b, n, cols] = args; const N = +n, CO = +(cols || 6), sw = 270, sh = 480;
    const sheet = createCanvas(sw * CO, sh * Math.ceil(N / CO) + 0), sg = sheet.getContext('2d');
    for (let i = 0; i < N; i++) {
      const t = +a + (+b - +a) * (N === 1 ? 0 : i / (N - 1));
      const S = F.renderFrame(g, t);
      sg.drawImage(cv, (i % CO) * sw, Math.floor(i / CO) * sh, sw, sh);
      sg.fillStyle = 'rgba(0,0,0,.6)'; sg.fillRect((i % CO) * sw, Math.floor(i / CO) * sh, 120, 26);
      sg.fillStyle = '#fff'; sg.font = '18px sans-serif'; sg.fillText(`${t.toFixed(2)} ${S.id}`, (i % CO) * sw + 4, Math.floor(i / CO) * sh + 19);
    }
    fs.writeFileSync(out, sheet.toBuffer('image/jpeg', 85));
  } else if (mode === 'range') {
    await range(+args[0], +args[1], args[2]);
  } else if (mode === 'final') {
    const nw = +(args[0] || 4); const N = C.NFRAMES; const dir = path.join(__dirname, 'build'); fs.mkdirSync(dir, { recursive: true });
    const per = Math.ceil(N / nw); const parts = [];
    const t0 = Date.now();
    await Promise.all(Array.from({ length: nw }, (_, i) => new Promise(res => {
      const f0 = i * per, f1 = Math.min(N, (i + 1) * per); const out = path.join(dir, `part${i}.mp4`); parts.push(out);
      const p = spawn(process.execPath, ['--expose-gc', '--max-old-space-size=2048', __filename, 'range', f0, f1, out], { stdio: 'inherit' }); p.on('close', res);
    })));
    parts.sort();
    fs.writeFileSync(path.join(dir, 'list.txt'), parts.map(p => `file '${p}'`).join('\n'));
    const silent = path.join(dir, 'silent.mp4');
    spawnSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', path.join(dir, 'list.txt'), '-c', 'copy', silent], { stdio: 'inherit' });
    const final = path.join(__dirname, 'PIED_PIPER_V2_FINAL_1080P60.mp4');
    spawnSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', silent, '-i', path.join(__dirname, 'audio/PIED_PIPER_V2_MIX.wav'),
      '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '320k', '-ar', '48000', '-af', 'apad', '-shortest',
      '-movflags', '+faststart', final], { stdio: 'inherit' });
    console.log('final', final, ((Date.now() - t0) / 1000).toFixed(0) + 's');
  }
})();
