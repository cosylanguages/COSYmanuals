import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const { readManualMetadata, publishDrafts } = require('../scripts/publish_to_supabase.js');

function fixture() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'cosymanuals-publish-'));
  fs.mkdirSync(path.join(root, 'drafts'));
  fs.mkdirSync(path.join(root, 'catalog'));
  fs.writeFileSync(path.join(root, 'catalog', 'manifest.json'), JSON.stringify([{
    id: 'en-a1-grammar',
    title: 'English A1 Grammar',
    language: 'en',
    level: 'A1',
    short_description: 'Starter grammar.'
  }]));
  fs.writeFileSync(path.join(root, 'drafts', 'en-a1-grammar.md'), '# A1 grammar\n');
  return root;
}

test('publisher reads valid metadata from the central manifest', () => {
  const root = fixture();
  try {
    assert.equal(readManualMetadata('en-a1-grammar', path.join(root, 'catalog')).level, 'A1');
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});

test('publisher rejects unknown manual IDs rather than guessing metadata', () => {
  const root = fixture();
  try {
    assert.throws(
      () => readManualMetadata('fr-c2-missing', path.join(root, 'catalog')),
      /No entry for fr-c2-missing/
    );
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});

test('dry-run validates drafts without Supabase credentials or network access', async () => {
  const root = fixture();
  const originalFetch = globalThis.fetch;
  globalThis.fetch = async () => { throw new Error('fetch must not be called in dry-run'); };
  try {
    await assert.doesNotReject(() => publishDrafts({ rootDir: root, dryRun: true }));
  } finally {
    globalThis.fetch = originalFetch;
    fs.rmSync(root, { recursive: true, force: true });
  }
});

test('dry-run rejects an empty draft', async () => {
  const root = fixture();
  fs.writeFileSync(path.join(root, 'drafts', 'en-a1-grammar.md'), '  \n');
  try {
    await assert.rejects(
      () => publishDrafts({ rootDir: root, dryRun: true }),
      /1 of 1 manual\(s\) failed/
    );
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});
