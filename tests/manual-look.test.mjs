// Every manual page loads the shared look last, and the self-hosted fonts it names exist.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

test('every manual page links manual-look.css (run: python3 scripts/add_manual_look.py manuals)', () => {
  const r = spawnSync('python3', ['scripts/add_manual_look.py', '--check', 'manuals'], { cwd: ROOT, encoding: 'utf8' });
  assert.equal(r.status, 0, r.stdout.split('\n').slice(0, 10).join('\n'));
});

test('fonts referenced by manual-look.css are in shared/fonts', () => {
  const css = fs.readFileSync(path.join(ROOT, 'shared/styles/manual-look.css'), 'utf8');
  const files = [...css.matchAll(/url\('\.\.\/fonts\/([^']+)'\)/g)].map((m) => m[1]);
  assert.ok(files.length >= 10, 'expected the @font-face blocks');
  for (const f of files) assert.ok(fs.existsSync(path.join(ROOT, 'shared/fonts', f)), `missing font ${f}`);
});

test('every topic page carries data-level (run: python3 scripts/add_level_stamp.py manuals)', () => {
  const r = spawnSync('python3', ['scripts/add_level_stamp.py', '--check', 'manuals'], { cwd: ROOT, encoding: 'utf8' });
  assert.equal(r.status, 0, r.stdout.split('\n').slice(0, 10).join('\n'));
});

test('English grammar pages with a practice banner carry a print QR (run: python3 scripts/add_page_qr.py manuals/en/grammar)', () => {
  const r = spawnSync('python3', ['scripts/add_page_qr.py', '--check', 'manuals/en/grammar'], { cwd: ROOT, encoding: 'utf8' });
  assert.equal(r.status, 0, r.stdout.split('\n').slice(0, 10).join('\n'));
});

test('English grammar topic pages carry data-doodle (run: python3 scripts/add_page_doodle.py manuals/en/grammar)', () => {
  const r = spawnSync('python3', ['scripts/add_page_doodle.py', '--check', 'manuals/en/grammar'], { cwd: ROOT, encoding: 'utf8' });
  assert.equal(r.status, 0, r.stdout.split('\n').slice(0, 10).join('\n'));
});

test('English A1 pages listed in add_gv_open.py keep their opening (run: python3 scripts/add_gv_open.py)', () => {
  const r = spawnSync('python3', ['scripts/add_gv_open.py', '--check'], { cwd: ROOT, encoding: 'utf8' });
  assert.equal(r.status, 0, r.stdout.split('\n').slice(0, 10).join('\n'));
});

for (const lang of ['fr', 'ru']) {
  test(`${lang} grammar pages with a practice banner carry a print QR (run: python3 scripts/add_page_qr.py manuals/${lang}/grammar)`, () => {
    const r = spawnSync('python3', ['scripts/add_page_qr.py', '--check', `manuals/${lang}/grammar`], { cwd: ROOT, encoding: 'utf8' });
    assert.equal(r.status, 0, r.stdout.split('\n').slice(0, 10).join('\n'));
  });
}

test('print booklets load visuals.css (openings and QR blocks are unstyled and huge without it)', () => {
  const dir = path.join(ROOT, 'manuals');
  const bad = [];
  for (const lang of fs.readdirSync(dir)) {
    const f = path.join(dir, lang, 'print', 'full.html');
    if (fs.existsSync(f) && !fs.readFileSync(f, 'utf8').includes('shared/styles/visuals.css')) bad.push(lang);
  }
  assert.deepEqual(bad, []);
});

test('English openings come from a lesson that teaches their grammar id (needs ../cosyplatform; skipped without it)', (t) => {
  if (!fs.existsSync(path.join(ROOT, '..', 'cosyplatform', 'curriculums'))) return t.skip('cosyplatform not next to this repo');
  const r = spawnSync('python3', ['scripts/check_open_vocab.py'], { cwd: ROOT, encoding: 'utf8' });
  assert.equal(r.status, 0, r.stdout.split('\n').slice(0, 10).join('\n'));
});

test('French and Russian A1 openings stay in place (run: python3 scripts/add_gv_open_fr_ru.py; needs ../cosyplatform, skipped without it)', (t) => {
  if (!fs.existsSync(path.join(ROOT, '..', 'cosyplatform', 'curriculums'))) return t.skip('cosyplatform not next to this repo');
  const r = spawnSync('python3', ['scripts/add_gv_open_fr_ru.py', '--check'], { cwd: ROOT, encoding: 'utf8' });
  assert.equal(r.status, 0, r.stdout.split('\n').slice(0, 10).join('\n'));
});
