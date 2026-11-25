// A double-escaped entity (&amp;rarr;) shows up as literal text such as "&rarr;" on the page.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const BAD = /&amp;(?:rarr|larr|copy|middot|amp|quot|#x27|nbsp|mdash|ndash|hellip|lsquo|rsquo);/;

function* htmlFiles(dir) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) yield* htmlFiles(p);
    else if (e.name.endsWith('.html')) yield p;
  }
}

test('no double-escaped entities in manual pages', () => {
  const bad = [];
  for (const f of htmlFiles(path.join(ROOT, 'manuals'))) {
    const text = fs.readFileSync(f, 'utf8').replace(/<(script|style)\b[\s\S]*?<\/\1>/gi, '');
    if (BAD.test(text)) bad.push(path.relative(ROOT, f));
  }
  assert.deepEqual(bad.slice(0, 10), [], `${bad.length} page(s) with double-escaped entities`);
});
