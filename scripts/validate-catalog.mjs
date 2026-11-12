#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export const VALID_LEVELS = new Set(['A0', 'A1', 'A2', 'B1', 'B2', 'C1', 'C2']);

export function validateManifest(manifest) {
  const errors = [];
  if (!Array.isArray(manifest)) {
    return ['Manifest must be a JSON array.'];
  }

  const ids = new Set();
  for (const [index, entry] of manifest.entries()) {
    const where = `manifest entry ${index + 1}`;
    if (!entry || typeof entry !== 'object' || Array.isArray(entry)) {
      errors.push(`${where}: expected an object.`);
      continue;
    }

    if (typeof entry.id !== 'string' || !/^[a-z]{2}-[a-z0-9]+(?:-[a-z0-9]+)*$/.test(entry.id)) {
      errors.push(`${where}: id must look like en-b1-grammar.`);
    } else if (ids.has(entry.id)) {
      errors.push(`${where}: duplicate id "${entry.id}".`);
    } else {
      ids.add(entry.id);
    }

    for (const field of ['title', 'short_description']) {
      if (typeof entry[field] !== 'string' || !entry[field].trim()) {
        errors.push(`${where}: "${field}" must be a non-empty string.`);
      }
    }

    if (typeof entry.language !== 'string' || !/^[a-z]{2}$/.test(entry.language)) {
      errors.push(`${where}: language must be a two-letter lowercase code.`);
    }
    if (!VALID_LEVELS.has(entry.level)) {
      errors.push(`${where}: level must be one of ${[...VALID_LEVELS].join(', ')}.`);
    }
  }
  return errors;
}

function run() {
  const root = process.cwd();
  const manifestPath = path.join(root, 'catalog', 'manifest.json');
  let manifest;
  try {
    manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
  } catch (error) {
    console.error(`Cannot read/parse ${manifestPath}: ${error.message}`);
    process.exitCode = 1;
    return;
  }

  const errors = validateManifest(manifest);
  if (errors.length) {
    console.error(`Catalog validation failed with ${errors.length} error(s):`);
    for (const error of errors) console.error(`- ${error}`);
    process.exitCode = 1;
    return;
  }

  console.log(`Catalog validation passed: ${manifest.length} entries, unique IDs, valid required fields.`);
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) run();
