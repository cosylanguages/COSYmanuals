const assert = require('assert');
const fs = require('fs');
const path = require('path');

const root = path.join(__dirname, '..');
const read = (file) => fs.readFileSync(path.join(root, file), 'utf8');

const index = read('index.html');
const manualCore = read('shared/studio/manual-core.js');
const generator = read('scripts/manual_to_record.py');

assert.match(index, /redirect=\$\{encodeURIComponent\(returnUrl\)\}&v=20261125-1/);
assert.match(manualCore, /redirect=' \+ encodeURIComponent\(manualUrl\) \+ '&v=20261125-1'/);
assert.match(generator, /\+ "&v=20261125-1"/);

console.log('✔ Manuals sign-in links return to the requested manual and bust the cached login HTML.');
