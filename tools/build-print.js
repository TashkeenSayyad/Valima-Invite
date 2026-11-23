// Builds the printed invitation card from print/card.html:
//   print/valima-card-A5-print.pdf   (2 pages, 154 x 216 mm = A5 + 3 mm bleed, fonts embedded)
//   print/valima-card-front.png / -back.png   (300 dpi previews)
// Usage: node tools/build-print.js      (needs Playwright, Python 3 with the qrcode package)
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const SITE_URL = 'https://tashkeensayyad.github.io/Valima-Invite/';

const index = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8');
const grab = (re, what) => { const m = index.match(re); if (!m) throw new Error('not found in index.html: ' + what); return m[0]; };
// Gold gradients and the T ✦ A monogram come straight from the website's artwork
const goldDefs = '<defs>' + grab(/<linearGradient id="goldLine"[\s\S]*?<\/linearGradient>/, 'goldLine')
  + grab(/<radialGradient id="goldBead"[\s\S]*?<\/radialGradient>/, 'goldBead') + '</defs>';
const monogram = grab(/<symbol id="monogram"[\s\S]*?<\/symbol>/, 'monogram');

// QR code to the website, drawn as an SVG path in the site's deep gold
const qr = execFileSync('python3', ['-I', '-c', `
import qrcode, sys
q = qrcode.QRCode(border=1, error_correction=qrcode.constants.ERROR_CORRECT_M)
q.add_data(sys.argv[1]); q.make(fit=True)
m = q.get_matrix(); n = len(m)
d = "".join(f"M{x} {y}h1v1h-1z" for y, row in enumerate(m) for x, v in enumerate(row) if v)
print(f'<svg viewBox="0 0 {n} {n}" shape-rendering="crispEdges"><rect width="{n}" height="{n}" fill="#fffdf6"/><path d="{d}" fill="#6e4d14"/></svg>')
`, SITE_URL]).toString().trim();

const html = fs.readFileSync(path.join(ROOT, 'print', 'card.html'), 'utf8')
  .replace('{{GOLD_DEFS}}', goldDefs).replace('{{MONOGRAM}}', monogram).replaceAll('{{QR}}', qr);
const built = path.join(ROOT, 'print', '.card.built.html');
fs.writeFileSync(built, html);

// Two versions: Sindhi back (default) and English back
const VARIANTS = [
  { cls: '', pdf: 'valima-card-A5-print.pdf', back: 'back' },
  { cls: 'en', pdf: 'valima-card-A5-print-english.pdf', back: 'back-english' },
];

(async () => {
  const browser = await chromium.launch();
  for (const v of VARIANTS) {
    const page = await browser.newPage();
    await page.goto('file://' + built);
    await page.evaluate((c) => { if (c) document.body.classList.add(c); }, v.cls);
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(600);
    const pdf = path.join(ROOT, 'print', v.pdf);
    await page.pdf({ path: pdf, width: '154mm', height: '216mm', printBackground: true, preferCSSPageSize: true });
    console.log('wrote', path.relative(ROOT, pdf));

    // 300 dpi previews: 154 mm = 582 CSS px; 1819 px / 582 px ≈ 3.125
    const shot = await browser.newPage({ viewport: { width: 582, height: 816 }, deviceScaleFactor: 3.125 });
    await shot.goto('file://' + built);
    await shot.evaluate((c) => { if (c) document.body.classList.add(c); }, v.cls);
    await shot.evaluate(() => document.fonts.ready);
    await shot.waitForTimeout(600);
    const pages = shot.locator('.page:visible');
    const sides = v.cls ? [[1, v.back]] : [[0, 'front'], [1, v.back]];
    for (const [i, side] of sides) {
      const out = path.join(ROOT, 'print', `valima-card-${side}.png`);
      await pages.nth(i).screenshot({ path: out });
      console.log('wrote', path.relative(ROOT, out));
    }
  }
  await browser.close();
  fs.unlinkSync(built);
})();
