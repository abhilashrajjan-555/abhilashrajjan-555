// Renders index.html frame by frame to MP4.
// Usage: node render.js out.mp4            (full 30s video, no audio)
//        node render.js --stills dir 1 5 9  (PNG stills at given seconds)
//        add --vertical for the 9:16 version (vertical.html, 1080x1920)
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const FPS = 30, DURATION = 30;

(async () => {
  let args = process.argv.slice(2);
  const vertical = args.includes('--vertical');
  args = args.filter(a => a !== '--vertical');
  const W = vertical ? 1080 : 1920, H = vertical ? 1920 : 1080;
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: W, height: H } });
  await page.goto('file://' + path.join(__dirname, vertical ? 'vertical.html' : 'index.html'));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(300);

  if (args[0] === '--stills') {
    const dir = args[1]; fs.mkdirSync(dir, { recursive: true });
    for (const s of args.slice(2)) {
      await page.evaluate(t => render(t), Number(s));
      await page.screenshot({ path: path.join(dir, `t${String(s).padStart(5, '0')}.png`) });
    }
    await browser.close(); return;
  }

  const out = args[0] || 'call-eva.mp4';
  const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-',
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '16', '-preset', 'medium', '-movflags', '+faststart', out],
    { stdio: ['pipe', 'inherit', 'inherit'] });
  const total = FPS * DURATION;
  for (let i = 0; i < total; i++) {
    await page.evaluate(t => render(t), i / FPS);
    const buf = await page.screenshot({ type: 'png' });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 90 === 0) process.stderr.write(`frame ${i}/${total}\n`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
})();
