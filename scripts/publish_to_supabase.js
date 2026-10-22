/**
 * Publish local Markdown drafts to the protected Supabase manual_content table.
 *
 * Required environment variables:
 *   SUPABASE_URL
 *   SUPABASE_SERVICE_ROLE_KEY
 *
 * Drafts are read only from the gitignored drafts/ directory. Metadata is read
 * from catalog/<manual-id>.json when present, otherwise from catalog/manifest.json.
 * Never commit draft content or service-role credentials.
 */

'use strict';

const fs = require('node:fs');
const path = require('node:path');

try {
  require('dotenv').config();
} catch {
  // dotenv is optional; environment variables may be supplied by the shell.
}

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;
const ROOT_DIR = path.resolve(__dirname, '..');
const DRAFTS_DIR = path.join(ROOT_DIR, 'drafts');
const CATALOG_DIR = path.join(ROOT_DIR, 'catalog');
const ALLOWED_LEVELS = new Set(['A0', 'A1', 'A2', 'B1', 'B2', 'C1', 'C2']);

function fail(message) {
  console.error(`Error: ${message}`);
  process.exitCode = 1;
}

function getSupabaseEndpoint() {
  if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
    throw new Error(
      'SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required. ' +
      'Set them in your shell or in a local, gitignored .env file.'
    );
  }

  let parsed;
  try {
    parsed = new URL(SUPABASE_URL);
  } catch {
    throw new Error('SUPABASE_URL must be a valid HTTPS URL.');
  }

  if (parsed.protocol !== 'https:' || parsed.username || parsed.password ||
      parsed.search || parsed.hash) {
    throw new Error('SUPABASE_URL must be an HTTPS project URL without credentials, query, or fragment.');
  }

  return `${parsed.origin}/rest/v1/manual_content`;
}

function readManualMetadata(manualId, catalogDir = CATALOG_DIR) {
  const metadataPath = path.join(catalogDir, `${manualId}.json`);
  let metadata;

  if (fs.existsSync(metadataPath)) {
    try {
      metadata = JSON.parse(fs.readFileSync(metadataPath, 'utf8'));
    } catch (error) {
      throw new Error(`Invalid JSON in catalog/${manualId}.json: ${error.message}`);
    }
  } else {
    const manifestPath = path.join(catalogDir, 'manifest.json');
    if (!fs.existsSync(manifestPath)) {
      throw new Error(`Neither catalog/${manualId}.json nor catalog/manifest.json exists.`);
    }

    let manifest;
    try {
      manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
    } catch (error) {
      throw new Error(`Invalid JSON in catalog/manifest.json: ${error.message}`);
    }

    if (!Array.isArray(manifest)) {
      throw new Error('catalog/manifest.json must contain a JSON array.');
    }
    metadata = manifest.find((entry) => entry && entry.id === manualId);
    if (!metadata) {
      throw new Error(`No entry for ${manualId} found in catalog/manifest.json.`);
    }
  }

  if (metadata.id && metadata.id !== manualId) {
    throw new Error(`Catalog ID mismatch for ${manualId}.`);
  }
  if (typeof metadata.language !== 'string' || !/^[a-z]{2}$/.test(metadata.language)) {
    throw new Error(`Catalog metadata for ${manualId} must contain a two-letter lowercase language code.`);
  }
  if (!ALLOWED_LEVELS.has(metadata.level)) {
    throw new Error(`Catalog metadata for ${manualId} must contain a valid CEFR level (A0-C2).`);
  }

  return metadata;
}

async function publishDrafts(options = {}) {
  const rootDir = path.resolve(options.rootDir || ROOT_DIR);
  const draftsDir = path.join(rootDir, 'drafts');
  const catalogDir = path.join(rootDir, 'catalog');
  const dryRun = options.dryRun ?? process.argv.includes('--dry-run');
  const endpoint = dryRun ? null : getSupabaseEndpoint();

  if (!fs.existsSync(draftsDir)) {
    console.log('No drafts/ directory found. Nothing to publish.');
    return;
  }

  const files = fs.readdirSync(draftsDir)
    .filter((file) => file.endsWith('.md'))
    .sort();

  if (files.length === 0) {
    console.log('No Markdown drafts found in drafts/. Nothing to publish.');
    return;
  }

  console.log(`Found ${files.length} draft manual(s).`);
  let failures = 0;

  for (const file of files) {
    const manualId = path.basename(file, '.md');

    if (!/^[a-z]{2}-[a-z0-9]+(?:-[a-z0-9]+)*$/.test(manualId)) {
      console.error(`Skipping "${file}": filename must use a safe manual ID such as en-b1-grammar.`);
      failures += 1;
      continue;
    }

    try {
      const metadata = readManualMetadata(manualId, catalogDir);
      const markdownContent = fs.readFileSync(path.join(draftsDir, file), 'utf8');

      if (!markdownContent.trim()) {
        throw new Error('Draft is empty; refusing to publish.');
      }

      if (dryRun) {
        console.log(`DRY RUN: validated ${manualId} (${metadata.language}, ${metadata.level}); no network request made.`);
        continue;
      }

      console.log(`Publishing ${manualId} (${metadata.language}, ${metadata.level})...`);

      const response = await fetch(`${endpoint}?on_conflict=manual_id`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          apikey: SUPABASE_SERVICE_ROLE_KEY,
          Authorization: `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
          Prefer: 'resolution=merge-duplicates,return=minimal'
        },
        body: JSON.stringify({
          manual_id: manualId,
          language: metadata.language,
          level: metadata.level,
          markdown_content: markdownContent,
          updated_at: new Date().toISOString()
        })
      });

      if (!response.ok) {
        const details = (await response.text()).slice(0, 1000);
        throw new Error(`Supabase returned HTTP ${response.status} ${response.statusText}: ${details}`);
      }

      console.log(`Published ${manualId} successfully.`);
    } catch (error) {
      failures += 1;
      console.error(`Failed to publish ${manualId}: ${error.message}`);
    }
  }

  if (failures > 0) {
    throw new Error(`${failures} of ${files.length} manual(s) failed to publish. Review the errors above.`);
  }

  console.log(`All ${files.length} manual(s) published successfully.`);
}

if (require.main === module) {
  publishDrafts().catch((error) => {
    fail(error.message);
  });
}

module.exports = { getSupabaseEndpoint, readManualMetadata, publishDrafts };
