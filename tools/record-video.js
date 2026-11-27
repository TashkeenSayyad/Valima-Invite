// Renders the invitation's opening as a 1080x1920 video, frame by frame.
// Usage: node tools/record-video.js <frames-dir>   then ffmpeg (see README).
// Time is frozen and stepped 1/30 s per frame, so every frame is sharp and smooth.
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const FPS = 30;
const out = process.argv[2] || 'frames';
const page_url = 'file://' + path.resolve(__dirname, '..', 'index.html') + (process.argv[3] || '');

// Timeline (seconds)
const TAP_AT = 2.6, CLICK_AT = 2.95, SCROLL_AT = 9.2, SCROLL_FOR = 5.4, END_AT = 16.8;

(async () => {
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 540, height: 960 }, deviceScaleFactor: 2 });
  const page = await ctx.newPage();
  const startTime = Date.now();
  await page.clock.install({ time: startTime });
  await page.goto(page_url);
  await page.evaluate(() => document.fonts.ready);
  // load the couple photo up front so it is ready when the camera reaches it
  await page.evaluate(() => document.querySelectorAll('img[loading="lazy"]').forEach((i) => { i.loading = 'eager'; }));
  await page.waitForTimeout(1500);
  // Stop real time from flowing: from here on time only moves one frame at a time.
  await page.clock.pauseAt(startTime + 60_000);
  await page.addStyleTag({ content: `
    .controls{display:none!important}
    .opening{animation:introZoom 2.9s cubic-bezier(.3,0,.3,1) both}
    @keyframes introZoom{from{transform:scale(1)}to{transform:scale(1.04)}}
    .tap{position:fixed;width:70px;height:70px;margin:-35px 0 0 -35px;border-radius:50%;
      border:3px solid rgba(255,255,255,.95);background:rgba(255,255,255,.35);
      box-shadow:0 0 0 2px rgba(143,106,34,.35);z-index:99;pointer-events:none;
      animation:tap .7s ease-out forwards}
    @keyframes tap{0%{transform:scale(.4);opacity:0}30%{opacity:1}100%{transform:scale(1.5);opacity:0}}` });

  // Drive every CSS animation/transition from our virtual time.
  await page.evaluate(() => {
    const seen = new WeakMap();
    window.__step = (t) => {
      for (const a of document.getAnimations()) {
        if (!seen.has(a)) { seen.set(a, t); a.pause(); }
        a.currentTime = t - seen.get(a);
      }
    };
  });

  const total = Math.round(END_AT * FPS);
  let tapped = false, clicked = false, scrolled = false;
  for (let f = 0; f < total; f++) {
    const t = f / FPS;
    if (!tapped && t >= TAP_AT) {
      tapped = true;
      await page.evaluate(() => {
        const r = document.getElementById('openBtn').getBoundingClientRect();
        const d = document.createElement('div'); d.className = 'tap';
        d.style.left = (r.left + r.width / 2) + 'px'; d.style.top = (r.top + r.height / 2) + 'px';
        document.body.appendChild(d);
      });
    }
    if (!clicked && t >= CLICK_AT) { clicked = true; await page.evaluate(() => document.getElementById('openBtn').click()); }
    if (!scrolled && t >= SCROLL_AT) {
      scrolled = true;
      await page.evaluate((dur) => {
        const target = document.querySelector('.venue-line').getBoundingClientRect().bottom + scrollY - innerHeight * 0.9;
        const start = scrollY, t1 = performance.now();
        const ease = k => k < .5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2;
        (function step(now) {
          const k = Math.min(1, (now - t1) / dur);
          scrollTo(0, start + (target - start) * ease(k));
          if (k < 1) requestAnimationFrame(step);
        })(t1);
      }, SCROLL_FOR * 1000);
    }
    if (f > 0) await page.clock.runFor(1000 / FPS);
    await page.evaluate((ms) => window.__step(ms), t * 1000);
    await page.screenshot({ path: path.join(out, `f${String(f).padStart(4, '0')}.jpg`), type: 'jpeg', quality: 93 });
    if (f % 60 === 0) process.stdout.write(`${f}/${total} `);
  }
  await browser.close();
  console.log('done');
})();
