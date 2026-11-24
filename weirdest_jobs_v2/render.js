// node render.js stills <outdir> t1 t2 ...   | node render.js video <out.mp4> f0 f1   | node render.js eval <outdir> <jsExpr returning dataURL>
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path'), { spawn } = require('child_process');
(async () => {
  const [mode, out, ...rest] = process.argv.slice(2);
  const browser = await chromium.launch({ args: ['--allow-file-access-from-files', '--disable-web-security', '--enable-gpu-rasterization', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: 540, height: 960 } });
  page.on('console', m => console.log('[page]', m.text())); page.on('pageerror', e => { console.error('[pageerror]', e.message); process.exitCode = 1; });
  await page.goto('file://' + path.resolve(__dirname, 'index.html'));
  await page.evaluate(() => document.fonts.ready);
  const ok = await page.evaluate(() => window.boot && window.boot()); if (!ok) console.error('FONTS NOT LOADED');
  const grab = async (t, fmt, q) => page.evaluate(([t, fmt, q]) => { renderAt(t); return document.getElementById('cv').toDataURL(fmt, q); }, [t, fmt, q]);
  if (mode === 'stills') {
    fs.mkdirSync(out, { recursive: true });
    for (const ts of rest) { const t = parseFloat(ts); const d = await grab(t, 'image/jpeg', .9); fs.writeFileSync(path.join(out, `t${t.toFixed(3)}.jpg`), Buffer.from(d.split(',')[1], 'base64')); }
  } else if (mode === 'eval') {
    const d = await page.evaluate(rest[0]); fs.writeFileSync(out, Buffer.from(d.split(',')[1], 'base64'));
  } else {
    const [f0, f1] = rest.map(Number);
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', '60', '-c:v', 'mjpeg', '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '14', '-pix_fmt', 'yuv420p', '-r', '60', out]);
    const t0 = Date.now();
    for (let f = f0; f < f1; f++) {
      const d = await grab(f / 60, 'image/jpeg', .95);
      if (!ff.stdin.write(Buffer.from(d.split(',')[1], 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
      if ((f - f0) % 240 === 0) console.log(out, f, ((Date.now() - t0) / (f - f0 + 1)).toFixed(0) + 'ms/f');
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
  }
  await browser.close();
})();
