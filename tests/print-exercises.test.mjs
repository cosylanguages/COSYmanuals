// Exercises must survive on paper: every quiz / concept-check panel has a print key,
// and the print rules that turn buttons into a), b), c) and tick boxes stay in components.css.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

test('every quiz panel has a print key (run: python3 scripts/add_print_key.py manuals)', () => {
  const r = spawnSync('python3', ['scripts/add_print_key.py', '--check', 'manuals'], { cwd: ROOT, encoding: 'utf8' });
  assert.equal(r.status, 0, r.stdout.split('\n').slice(0, 10).join('\n'));
});

test('print rules keep exercises on paper', () => {
  const css = fs.readFileSync(path.join(ROOT, 'shared/styles/components.css'), 'utf8');
  const print = css.slice(css.indexOf('Exercises on paper'));
  for (const needle of ['.mflip .hint', '.qopt::before', '.checklist', '.print-key', '.pk-ans']) {
    assert.ok(print.includes(needle), `missing print rule for ${needle}`);
  }
});

test('print stylesheets no longer hide the exercises', () => {
  for (const f of ['shared/styles/print.css', ...fs.readdirSync(path.join(ROOT, 'manuals'))
      .map((l) => `manuals/${l}/print/print.css`).filter((p) => fs.existsSync(path.join(ROOT, p)))]) {
    const hide = fs.readFileSync(path.join(ROOT, f), 'utf8').split('display: none !important')[0];
    for (const sel of ['.quiz-panel,', '.ccq-panel,', '.checklist,']) {
      assert.ok(!hide.includes(sel), `${f} still hides ${sel}`);
    }
  }
});
