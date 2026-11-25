// Parallel frame renderer: node tools/render.mjs <outdir> [workers=3] [fps=60] [start=0] [end=3600] [scale=1]
import { createRequire } from 'module'; const require = createRequire(import.meta.url);
const { chromium } = require('/opt/node-tools/node_modules/playwright/index.js');
import { spawn } from 'child_process'; import fs from 'fs'; import path from 'path';
const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const [outdir, nw = '3', fpsS = '60', s0 = '0', s1 = '3600', scaleS = '1'] = process.argv.slice(2);
const fps = +fpsS, F0 = +s0, F1 = +s1, N = +nw, scale = +scaleS;
fs.mkdirSync(outdir, { recursive: true });
const per = Math.ceil((F1 - F0) / N);
const t0 = Date.now();
async function worker(k) {
  const a = F0 + k * per, b = Math.min(F1, a + per); if (a >= b) return null;
  const out = path.join(outdir, `chunk_${String(k).padStart(2, '0')}.mp4`);
  const vf = scale !== 1 ? ['-vf', `scale=${Math.round(1080 * scale / 2) * 2}:${Math.round(1920 * scale / 2) * 2}:flags=lanczos`] : [];
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'png', '-i', '-', ...vf,
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '14', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-r', String(fps), out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const br = await chromium.launch({ args: ['--allow-file-access-from-files', '--disable-gpu'] });
  const p = await br.newPage({ viewport: { width: 1080, height: 1920 } });
  p.on('pageerror', e => console.log(`[w${k}] PAGEERR`, e.message));
  await p.goto('file://' + root + '/index.html'); await p.waitForFunction(() => window.isReady && window.isReady());
  for (let f = a; f < b; f++) {
    const t = f / fps;
    const data = await p.evaluate(t => { window.renderFrame(t); return document.getElementById('c').toDataURL('image/png'); }, t);
    const buf = Buffer.from(data.slice(data.indexOf(',') + 1), 'base64');
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if ((f - a) % 120 === 0) console.log(`[w${k}] frame ${f} (${((f - a) / (b - a) * 100).toFixed(0)}%) ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await br.close();
  return out;
}
const outs = (await Promise.all([...Array(N).keys()].map(worker))).filter(Boolean);
fs.writeFileSync(path.join(outdir, 'list.txt'), outs.map(o => `file '${path.basename(o)}'`).join('\n'));
console.log('done', ((Date.now() - t0) / 1000).toFixed(0), 's');
