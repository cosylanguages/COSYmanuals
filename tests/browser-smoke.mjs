import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';
import AxeBuilder from '@axe-core/playwright';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const PAGES = [
  '/manuals/en/grammar/a1/topics/part-1-building-blocks.html',
  '/manuals/fr/grammar/a1/topics/genre-des-noms-1.html'
];
const MIME = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.json': 'application/json; charset=utf-8', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp' };

const server = http.createServer((req, res) => {
  let pathname;
  try { pathname = decodeURIComponent(new URL(req.url, 'http://127.0.0.1').pathname); }
  catch { res.writeHead(400).end('Bad request'); return; }
  const file = path.resolve(ROOT, '.' + pathname);
  if (!file.startsWith(ROOT + path.sep) && file !== ROOT) { res.writeHead(403).end('Forbidden'); return; }
  try {
    const stat = fs.statSync(file);
    const target = stat.isDirectory() ? path.join(file, 'index.html') : file;
    res.writeHead(200, { 'Content-Type': MIME[path.extname(target)] || 'application/octet-stream' });
    fs.createReadStream(target).pipe(res);
  } catch { res.writeHead(404).end('Not found'); }
});

const listen = () => new Promise((resolve, reject) => {
  server.once('error', reject);
  server.listen(0, '127.0.0.1', () => resolve(server.address().port));
});

let browser;
try {
  const port = await listen();
  browser = await chromium.launch({ headless: true });
  const errors = [];
  for (const route of PAGES) {
    const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
    page.on('pageerror', error => errors.push(route + ': browser error: ' + error.message));
    const response = await page.goto('http://127.0.0.1:' + port + route, { waitUntil: 'networkidle' });
    if (!response || !response.ok()) errors.push(route + ': page failed to load');

    for (const width of [390, 768, 1280]) {
      await page.setViewportSize({ width, height: 844 });
      const layout = await page.evaluate(() => ({
        viewport: document.documentElement.clientWidth,
        scroll: document.documentElement.scrollWidth
      }));
      if (layout.scroll > layout.viewport + 2) {
        errors.push(route + ': horizontal overflow at ' + width + 'px (scroll width ' + layout.scroll + ')');
      }
    }

    await page.setViewportSize({ width: 1280, height: 844 });
    await page.keyboard.press('Tab');
    const focus = await page.evaluate(() => ({
      tag: document.activeElement && document.activeElement.tagName,
      visible: !!document.activeElement && document.activeElement !== document.body
    }));
    if (!focus.visible) errors.push(route + ': first Tab did not move focus to an interactive element');

    try {
      const axe = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']).analyze();
      for (const item of axe.violations) {
        errors.push(route + ': axe ' + item.id + ' (' + item.impact + '): ' + item.help);
      }
    } catch (error) {
      errors.push(route + ': axe scan failed: ' + error.message);
    }

    const pdfPath = path.join(os.tmpdir(), 'cosymanuals-' + (route.includes('/fr/') ? 'fr' : 'en') + '.pdf');
    await page.emulateMedia({ media: 'print' });
    await page.pdf({ path: pdfPath, format: 'A4', printBackground: true });
    if (!fs.existsSync(pdfPath) || fs.statSync(pdfPath).size < 1000) {
      errors.push(route + ': print/PDF output is missing or unexpectedly small');
    }
    fs.rmSync(pdfPath, { force: true });
    await page.close();
  }

  if (errors.length) {
    console.error('Browser smoke checks found ' + errors.length + ' issue(s):');
    for (const error of errors) console.error('- ' + error);
    process.exitCode = 1;
  } else {
    console.log('Browser smoke checks passed: keyboard focus, mobile/tablet/desktop overflow, axe WCAG 2.1 A/AA, and A4 PDF generation for English and French sample pages.');
  }
} finally {
  if (browser) await browser.close();
  server.close();
}
