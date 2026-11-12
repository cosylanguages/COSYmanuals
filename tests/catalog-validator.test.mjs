import test from 'node:test';
import assert from 'node:assert/strict';
import { validateManifest } from '../scripts/validate-catalog.mjs';

const validEntry = {
  id: 'en-a1-grammar',
  title: 'English A1 Grammar',
  language: 'en',
  level: 'A1',
  short_description: 'Foundational grammar reference.'
};

test('accepts a valid catalog manifest', () => {
  assert.deepEqual(validateManifest([validEntry]), []);
});

test('rejects non-array manifests', () => {
  assert.match(validateManifest({})[0], /JSON array/);
});

test('rejects duplicate IDs', () => {
  assert.ok(validateManifest([validEntry, { ...validEntry }]).some(error => /duplicate id/.test(error)));
});

test('rejects unsafe IDs, invalid languages, and unsupported levels', () => {
  const errors = validateManifest([{ ...validEntry, id: '../secret', language: 'EN', level: 'D1' }]);
  assert.ok(errors.some(error => /id must look like/.test(error)));
  assert.ok(errors.some(error => /language must be/.test(error)));
  assert.ok(errors.some(error => /level must be/.test(error)));
});

test('requires non-empty title and description', () => {
  const errors = validateManifest([{ ...validEntry, title: ' ', short_description: '' }]);
  assert.equal(errors.filter(error => /non-empty string/.test(error)).length, 2);
});
