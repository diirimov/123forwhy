// usage: node tools/shot.mjs out.png test:<name>:<t> | frame:<t> [...more]
import { createRequire } from 'module'; const require = createRequire(import.meta.url); const { chromium } = require('/opt/node-tools/node_modules/playwright/index.js');
import fs from 'fs'; import path from 'path';
const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const [out, ...specs] = process.argv.slice(2);
const b = await chromium.launch({ args: ['--allow-file-access-from-files', '--disable-gpu'] });
const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
p.on('console', m => { if (m.type() === 'error') console.log('ERR', m.text()); });
p.on('pageerror', e => console.log('PAGEERR', e.message));
await p.goto('file://' + root + '/' + (process.env.PAGE || 'index.html'));
await p.waitForFunction(() => window.isReady && window.isReady());
let i = 0;
for (const s of specs) {
  const [kind, a, b2] = s.split(':');
  const t0 = Date.now();
  if (kind === 'test') await p.evaluate(([n, t]) => window.renderTest(n, +t), [a, b2]);
  else await p.evaluate(t => window.renderFrame(+t), a);
  const data = await p.evaluate(() => document.getElementById('c').toDataURL('image/png'));
  const f = specs.length > 1 ? out.replace('.png', `_${String(i).padStart(2, '0')}.png`) : out;
  fs.writeFileSync(f, Buffer.from(data.split(',')[1], 'base64')); i++;
  console.log(f, Date.now() - t0, 'ms');
}
await b.close();
