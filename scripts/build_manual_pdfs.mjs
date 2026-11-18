#!/usr/bin/env node
/**
 * Build downloadable PDF manuals
 * ------------------------------
 * Renders each language's full print booklet (`manuals/<lang>/print/full.html`,
 * built by `scripts/build_print_booklets.mjs`) to an A4 PDF next to it as
 * `manuals/<lang>/print/full.pdf`. The booklet pages link to that file via the
 * "Download PDF" button.
 *
 * Requires a browser for rendering. Playwright's Chromium is used when present
 * (installed in CI); otherwise the system Chromium is used.
 *
 * Run:
 *   node scripts/build_print_booklets.mjs
 *   node scripts/build_manual_pdfs.mjs            # all languages
 *   node scripts/build_manual_pdfs.mjs en fr      # only these languages
 *
 * The PDFs are build artifacts. Commit them only if you want offline downloads
 * to work straight from GitHub Pages without a client-side print step.
 */
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.webp': 'image/webp',
  '.woff2': 'font/woff2',
  '.woff': 'font/woff'
};

async function loadChromium() {
  try {
    const pw = await import('playwright');
    return pw.chromium;
  } catch {
    return null;
  }
}

function startServer() {
  return new Promise((resolve, reject) => {
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
    server.once('error', reject);
    server.listen(0, '127.0.0.1', () => resolve(server));
  });
}

async function renderWithPlaywright(chromium, url, outPath, browserRef) {
  if (!browserRef.browser) browserRef.browser = await chromium.launch({ headless: true });
  const page = await browserRef.browser.newPage();
  await page.goto(url, { waitUntil: 'networkidle' });
  await page.emulateMedia({ media: 'print' });
  await page.pdf({ path: outPath, format: 'A4', printBackground: true, margin: { top: '16mm', bottom: '16mm', left: '14mm', right: '14mm' } });
  await page.close();
}

async function renderWithSystemChromium(execPath, url, outPath) {
  const { spawnSync } = await import('node:child_process');
  const args = [
    '--headless', '--disable-gpu', '--no-sandbox', '--no-pdf-header-footer',
    '--print-to-pdf=' + outPath, url
  ];
  const r = spawnSync(execPath, args, { stdio: 'inherit' });
  if (r.status !== 0) throw new Error('chromium exited with ' + r.status);
}

async function main() {
  const langs = process.argv.slice(2);
  const server = await startServer();
  const port = server.address().port;
  const base = `http://127.0.0.1:${port}/`;

  const chromium = await loadChromium();
  const sysCandidates = ['chromium', 'chromium-browser', 'google-chrome', 'google-chrome-stable'];
  let sysChromium = null;
  if (!chromium) {
    const { spawnSync } = await import('node:child_process');
    for (const c of sysCandidates) {
      const r = spawnSync('which', [c], { encoding: 'utf8' });
      if (r.status === 0 && r.stdout.trim()) { sysChromium = r.stdout.trim(); break; }
    }
    if (!sysChromium) {
      console.error('No browser available. Install Playwright Chromium (`npx playwright install chromium`) or system Chromium.');
      server.close();
      process.exit(1);
    }
  }

  const dirs = fs.readdirSync(path.join(ROOT, 'manuals'))
    .filter((l) => fs.existsSync(path.join(ROOT, 'manuals', l, 'print', 'full.html')))
    .filter((l) => !langs.length || langs.includes(l))
    .sort();

  const browserRef = {};
  const results = [];
  try {
    for (const lang of dirs) {
      const rel = `manuals/${lang}/print/full.html`;
      const out = path.join(ROOT, 'manuals', lang, 'print', 'full.pdf');
      try {
        if (chromium) await renderWithPlaywright(chromium, base + rel, out, browserRef);
        else await renderWithSystemChromium(sysChromium, base + rel, out);
        const kb = Math.round(fs.statSync(out).size / 1024);
        results.push(`${lang}: ${kb} KB`);
      } catch (err) {
        results.push(`${lang}: FAILED (${err.message})`);
      }
    }
  } finally {
    if (browserRef.browser) await browserRef.browser.close();
    server.close();
  }

  for (const r of results) console.log(r);
  console.log(`Rendered ${results.length} PDFs`);
}

main();
