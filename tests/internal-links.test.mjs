import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { findBrokenLinks } from '../scripts/check-internal-links.mjs';

test('detects missing local targets and ignores external URLs', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'cosymanuals-links-'));
  try {
    fs.mkdirSync(path.join(root, 'pages'), { recursive: true });
    fs.writeFileSync(path.join(root, 'pages', 'index.html'),
      '<a href="./next.html">Next</a><a href="./missing.html">Missing</a><img src="https://example.com/a.png">');
    fs.writeFileSync(path.join(root, 'pages', 'next.html'), '<p>OK</p>');
    const broken = findBrokenLinks(root);
    assert.equal(broken.length, 1);
    assert.equal(broken[0].target, './missing.html');
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});
