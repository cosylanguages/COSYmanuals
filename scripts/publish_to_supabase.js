/**
 * publish_to_supabase.js
 *
 * Local-only publisher script for COSYmanuals.
 * Reads Markdown manuals from gitignored `drafts/` folder and upserts them into
 * Supabase `manual_content` table using service role key.
 *
 * Requirements:
 * - Environment variables: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
 * - Local drafts in `drafts/` (e.g. `drafts/en-b1-grammar.md`)
 */

const fs = require('fs');
const path = require('path');

// Try loading dotenv if available
try {
  require('dotenv').config();
} catch (e) {
  // dotenv optional
}

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
  console.error('Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables are required.');
  console.error('Create a local .env file (gitignored) with these credentials.');
  process.exit(1);
}

const DRAFTS_DIR = path.join(__dirname, '..', 'drafts');
const CATALOG_DIR = path.join(__dirname, '..', 'catalog');

async function publishDrafts() {
  if (!fs.existsSync(DRAFTS_DIR)) {
    console.log(`Drafts directory "${DRAFTS_DIR}" does not exist. Creating empty drafts/ directory...`);
    fs.mkdirSync(DRAFTS_DIR, { recursive: true });
    console.log('No drafts to publish.');
    return;
  }

  const files = fs.readdirSync(DRAFTS_DIR).filter(f => f.endsWith('.md'));

  if (files.length === 0) {
    console.log('No Markdown (.md) files found in drafts/ folder.');
    return;
  }

  console.log(`Found ${files.length} draft manual(s) to publish: ${files.join(', ')}`);

  for (const file of files) {
    const manualId = path.basename(file, '.md');
    const filePath = path.join(DRAFTS_DIR, file);
    const markdownContent = fs.readFileSync(filePath, 'utf-8');

    // Read metadata from catalog if available
    let language = 'en';
    let level = 'A1';
    const metadataPath = path.join(CATALOG_DIR, `${manualId}.json`);
    if (fs.existsSync(metadataPath)) {
      try {
        const meta = JSON.parse(fs.readFileSync(metadataPath, 'utf-8'));
        if (meta.language) language = meta.language;
        if (meta.level) level = meta.level;
      } catch (err) {
        console.warn(`Warning: Could not parse metadata for ${manualId}.json:`, err.message);
      }
    }

    console.log(`Publishing "${manualId}" (Language: ${language}, Level: ${level})...`);

    // Upsert to Supabase manual_content table using REST API
    const endpoint = `${SUPABASE_URL.replace(/\/$/, '')}/rest/v1/manual_content`;

    const payload = {
      manual_id: manualId,
      language: language,
      level: level,
      markdown_content: markdownContent,
      updated_at: new Date().toISOString()
    };

    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'apikey': SUPABASE_SERVICE_ROLE_KEY,
          'Authorization': `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
          'Prefer': 'resolution=merge-duplicates'
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`Failed to publish "${manualId}": ${response.status} ${response.statusText}`, errorText);
      } else {
        console.log(`Successfully published "${manualId}" to Supabase!`);
      }
    } catch (err) {
      console.error(`Network or fetch error publishing "${manualId}":`, err.message);
    }
  }
}

publishDrafts().catch(err => {
  console.error('Unexpected error in publish script:', err);
  process.exit(1);
});
