/**
 * Grammar embed test
 * ------------------
 * Serves the repo locally, loads a page that embeds two grammar points by id,
 * and asserts the explanation content renders inside the Shadow DOM, that ids
 * resolve to real files, and that an unknown id degrades gracefully.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8'
};

const KNOWN = 'en-a1-adjectives';
const KNOWN_PATH = 'manuals/en/grammar/a1/topics/adjectives.html';
const KNOWN_FR = 'fr-a1-genre-des-noms-1';
const KNOWN_FR_PATH = 'manuals/fr/grammar/a1/topics/genre-des-noms-1.html';

test('registry lists a stable id for a known grammar point', () => {
  const registry = JSON.parse(fs.readFileSync(path.join(ROOT, 'data', 'grammar-points.json'), 'utf8'));
  const index = JSON.parse(fs.readFileSync(path.join(ROOT, 'data', 'grammar-points.index.json'), 'utf8'));
  const point = registry.points.find((p) => p.id === KNOWN);
  assert.ok(point, 'registry should contain ' + KNOWN);
  assert.equal(point.path, KNOWN_PATH);
  assert.equal(index[KNOWN], KNOWN_PATH);
  assert.ok(fs.existsSync(path.join(ROOT, KNOWN_PATH)), 'mapped file must exist');
});

test('every registry id maps to an existing file and carries a stamped id', () => {
  const registry = JSON.parse(fs.readFileSync(path.join(ROOT, 'data', 'grammar-points.json'), 'utf8'));
  const missing = [];
  const unstamped = [];
  for (const p of registry.points) {
    const abs = path.join(ROOT, p.path);
    if (!fs.existsSync(abs)) { missing.push(p.id); continue; }
    const text = fs.readFileSync(abs, 'utf8');
    if (!text.includes('data-grammar-point="' + p.id + '"')) unstamped.push(p.id);
  }
  assert.deepEqual(missing, [], 'all ids resolve to files');
  assert.deepEqual(unstamped, [], 'all pages carry their id');
});

function makeServer() {
  return http.createServer((req, res) => {
    let pathname;
    try { pathname = decodeURIComponent(new URL(req.url, 'http://127.0.0.1').pathname); }
    catch { res.writeHead(400).end('Bad request'); return; }
    const file = path.resolve(ROOT, '.' + pathname);
    if (!file.startsWith(ROOT + path.sep) && file !== ROOT) { res.writeHead(403).end('Forbidden'); return; }
    try {
      const stat = fs.statSync(file);
      const target = stat.isDirectory() ? path.join(file, 'index.html') : file;
      res.writeHead(200, {
        'Content-Type': MIME[path.extname(target)] || 'application/octet-stream',
        'Access-Control-Allow-Origin': '*'
      });
      fs.createReadStream(target).pipe(res);
    } catch { res.writeHead(404).end('Not found'); }
  });
}

const listen = (server) => new Promise((resolve, reject) => {
  server.once('error', reject);
  server.listen(0, '127.0.0.1', () => resolve(server.address().port));
});

test('embeds a grammar explanation by id inside shadow DOM', async () => {
  const server = makeServer();
  const port = await listen(server);
  const base = `http://127.0.0.1:${port}/`;
  const page = `<div data-grammar-embed="${KNOWN}" data-grammar-embed-url="${base}"></div>
<div data-grammar-embed="${KNOWN_FR}" data-grammar-embed-url="${base}"></div>
<div data-grammar-embed="xx-a1-does-not-exist" data-grammar-embed-url="${base}"></div>
<script src="/shared/js/grammar-embed.js"></script>`;
  fs.writeFileSync(path.join(ROOT, '__embed_test.html'), page);

  let browser;
  try {
    browser = await chromium.launch({ headless: true });
    const ctx = await browser.newContext();
    const p = await ctx.newPage();
    const errors = [];
    p.on('pageerror', (e) => errors.push(e.message));
    await p.goto(base + '__embed_test.html', { waitUntil: 'networkidle' });
    await p.waitForFunction(() => {
      const hosts = document.querySelectorAll('[data-grammar-embed]');
      return Array.from(hosts).every((h) => h.shadowRoot &&
        h.shadowRoot.querySelector('.cosy-embed') &&
        !h.shadowRoot.querySelector('.cosy-embed__status[role="status"]'));
    }, null, { timeout: 15000 });

    const result = await p.evaluate((ids) => {
      const out = {};
      for (const id of ids) {
        const host = document.querySelector(`[data-grammar-embed="${id}"]`);
        const root = host.shadowRoot;
        out[id] = {
          hasEmbed: !!root.querySelector('.cosy-embed'),
          heading: (root.querySelector('.cosy-embed h1') || {}).textContent || '',
          text: (root.querySelector('.cosy-embed') || {}).textContent || '',
          linkHref: (root.querySelector('.cosy-embed__bar a') || {}).href || ''
        };
      }
      return out;
    }, [KNOWN, KNOWN_FR, 'xx-a1-does-not-exist']);

    assert.deepEqual(errors, [], 'no page errors');
    assert.match(result[KNOWN].text, /adjectives go before the noun/i, 'EN explanation renders');
    assert.equal(result[KNOWN].heading.trim(), 'Adjectives');
    assert.match(result[KNOWN].linkHref, /adjectives\.html$/, 'source link points at the page');
    assert.match(result[KNOWN_FR].text, /genre/i, 'FR explanation renders');
    assert.match(result['xx-a1-does-not-exist'].text, /unavailable/i, 'unknown id degrades gracefully');
  } finally {
    if (browser) await browser.close();
    server.close();
    fs.rmSync(path.join(ROOT, '__embed_test.html'), { force: true });
  }
});
