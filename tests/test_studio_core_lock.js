'use strict';
/* Run: node tests/test_studio_core_lock.js
 * studio-core.js is vendored from COSYstudio. Fail if it was edited locally. */
const assert = require('assert');
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const dir = path.join(__dirname, '..', 'shared', 'studio');
const lock = JSON.parse(fs.readFileSync(path.join(dir, 'studio-core.lock.json'), 'utf8'));
const actual = crypto.createHash('sha256').update(fs.readFileSync(path.join(dir, 'studio-core.js'))).digest('hex');
assert.strictEqual(actual, lock.sha256,
  'studio-core.js differs from the COSYstudio copy pinned in studio-core.lock.json. ' +
  'Change it in COSYstudio (packages/studio-core), then re-copy it here and update the lock.');
assert.match(lock.commit, /^[0-9a-f]{40}$/);
console.log('studio-core.js matches COSYstudio@' + lock.commit.slice(0, 7));
