// Renders template/promo.html with a concept JSON to MP4 (silent) or PNG stills.
// Usage:
//   node render.js --config concept.json --format landscape|vertical --out silent.mp4
//   node render.js --config concept.json --format vertical --stills outdir 3.5 8.2 13 17.8 24.5 29
// Needs: Playwright with Chromium, ffmpeg, the Inter / Inter Display fonts installed.
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const FPS = 30, DURATION = 30;
const STILLS = [2.2, 3.5, 7.8, 11, 13, 17.8, 22.5, 24.5, 29];

function arg(name, def) { const i = process.argv.indexOf(name); return i > -1 ? process.argv[i + 1] : def; }

(async () => {
  const cfgPath = path.resolve(arg('--config'));
  const format = arg('--format', 'landscape');
  const config = JSON.parse(fs.readFileSync(cfgPath, 'utf8'));
  // image paths in the config are relative to the config file
  for (const k of ['phoneImage', 'logoImage'])
    if (config[k]) config[k] = 'file://' + path.resolve(path.dirname(cfgPath), config[k]);

  const V = format === 'vertical';
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: V ? 1080 : 1920, height: V ? 1920 : 1080 } });
  await page.goto('file://' + path.join(__dirname, '..', 'template', 'promo.html'));
  await page.evaluate(([c, f]) => init(c, f), [config, format]);
  await page.evaluate(async () => {
    await document.fonts.ready;
    await Promise.all([...document.images].map(i => i.complete ? 0 : new Promise(r => { i.onload = i.onerror = r; })));
  });
  await page.waitForTimeout(200);

  const si = process.argv.indexOf('--stills');
  if (si > -1) {
    const dir = process.argv[si + 1]; fs.mkdirSync(dir, { recursive: true });
    let times = process.argv.slice(si + 2).filter(a => !a.startsWith('--') && !isNaN(Number(a))).map(Number);
    if (!times.length) times = STILLS;
    for (const t of times) {
      await page.evaluate(x => render(x), t);
      await page.screenshot({ path: path.join(dir, `${format}_t${t.toFixed(1).padStart(4, '0')}.png`) });
    }
    await browser.close(); return;
  }

  const out = arg('--out', `${format}.mp4`);
  const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-',
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '16', '-preset', 'medium', '-movflags', '+faststart', out],
    { stdio: ['pipe', 'inherit', 'inherit'] });
  const total = FPS * DURATION;
  for (let i = 0; i < total; i++) {
    await page.evaluate(t => render(t), i / FPS);
    const buf = await page.screenshot({ type: 'png' });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 150 === 0) process.stderr.write(`${format}: frame ${i}/${total}\n`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
})();
