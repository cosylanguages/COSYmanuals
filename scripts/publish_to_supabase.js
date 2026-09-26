/**
 * publish_to_supabase.js
 *
 * Publisher script for COSYmanuals.
 * Reads Markdown manuals from:
 *   1. Local gitignored `drafts/` folder (e.g. `drafts/en-b1-grammar.md`)
 *   2. Extracted manuals in `manuals/<lang>/<course_type>/<level>/*.md`
 *      (e.g. `manuals/en/general/a1/grammar.md`)
 *
 * Derives manual_id, language, and level from the path or metadata in `catalog/*.json`
 * and upserts them into Supabase `manual_content` table using service role key.
 *
 * Requirements:
 * - Environment variables: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
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
  process.exit(1);
}

const DRAFTS_DIR = path.join(__dirname, '..', 'drafts');
const MANUALS_DIR = path.join(__dirname, '..', 'manuals');
const CATALOG_DIR = path.join(__dirname, '..', 'catalog');

// Helper to scan for valid aggregated manual files under manuals/
function findExtractedManuals(dir) {
  let results = [];
  if (!fs.existsSync(dir)) return results;

  const list = fs.readdirSync(dir);
  for (const item of list) {
    const fullPath = path.join(dir, item);
    const stat = fs.statSync(fullPath);
    if (stat.isDirectory()) {
      results = results.concat(findExtractedManuals(fullPath));
    } else if (item.endsWith('.md') && item !== 'README.md') {
      const relPath = path.relative(MANUALS_DIR, fullPath).replace(/\\/g, '/');
      const parts = relPath.split('/');
      // Expected structure: [lang, course_type, level, subject.md]
      if (parts.length === 4 && ['grammar.md', 'vocabulary.md', 'communication.md'].includes(parts[3])) {
        const [lang, courseType, level, subjectFilename] = parts;
        const subject = subjectFilename.replace('.md', '');
        const derivedManualId = `${lang}-${courseType}-${level.toLowerCase()}-${subject}`;
        results.push({
          filePath: fullPath,
          sourceType: 'manuals',
          manualId: derivedManualId,
          language: lang,
          level: level.toUpperCase()
        });
      }
    }
  }
  return results;
}

// Helper to fetch existing manual records from Supabase for skip/change detection
async function fetchExistingManualsMap(endpoint) {
  try {
    const response = await fetch(`${endpoint}?select=manual_id,markdown_content`, {
      method: 'GET',
      headers: {
        'apikey': SUPABASE_SERVICE_ROLE_KEY,
        'Authorization': `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`
      }
    });

    if (response.ok) {
      const data = await response.json();
      const map = new Map();
      if (Array.isArray(data)) {
        data.forEach(item => map.set(item.manual_id, item.markdown_content));
      }
      return map;
    }
  } catch (err) {
    // If GET fails or map cannot be fetched, proceed with default upserts
  }
  return new Map();
}

async function collectManualItems() {
  const itemsMap = new Map();

  // 1. Collect extracted manuals from manuals/<lang>/<course_type>/<level>/*.md
  const extracted = findExtractedManuals(MANUALS_DIR);
  for (const item of extracted) {
    itemsMap.set(item.manualId, item);
  }

  // 2. Collect drafts from drafts/*.md (drafts take precedence if manual_id overlaps)
  if (fs.existsSync(DRAFTS_DIR)) {
    const draftFiles = fs.readdirSync(DRAFTS_DIR).filter(f => f.endsWith('.md'));
    for (const file of draftFiles) {
      const manualId = path.basename(file, '.md');
      const fullPath = path.join(DRAFTS_DIR, file);
      itemsMap.set(manualId, {
        filePath: fullPath,
        sourceType: 'drafts',
        manualId,
        language: 'en',
        level: 'A1'
      });
    }
  }

  // 3. Apply overrides from catalog/*.json if present
  for (const [manualId, item] of itemsMap.entries()) {
    const metadataPath = path.join(CATALOG_DIR, `${manualId}.json`);
    if (fs.existsSync(metadataPath)) {
      try {
        const meta = JSON.parse(fs.readFileSync(metadataPath, 'utf-8'));
        if (meta.language) item.language = meta.language;
        if (meta.level) item.level = meta.level;
      } catch (err) {
        console.warn(`Warning: Could not parse metadata for ${manualId}.json:`, err.message);
      }
    }
  }

  return Array.from(itemsMap.values());
}

async function publishManuals() {
  const manualItems = await collectManualItems();

  console.log(`Discovered ${manualItems.length} manual document(s) to process.`);

  if (manualItems.length === 0) {
    console.log('No manual documents found.');
    return;
  }

  const endpoint = `${SUPABASE_URL.replace(/\/$/, '')}/rest/v1/manual_content`;
  const existingMap = await fetchExistingManualsMap(endpoint);

  let publishedCount = 0;
  let skippedCount = 0;
  let failedCount = 0;
  const failureReasons = [];

  for (const item of manualItems) {
    const markdownContent = fs.readFileSync(item.filePath, 'utf-8');

    // Skip if existing content in Supabase matches local content exactly
    if (existingMap.has(item.manualId) && existingMap.get(item.manualId) === markdownContent) {
      skippedCount++;
      continue;
    }

    const payload = {
      manual_id: item.manualId,
      language: item.language,
      level: item.level,
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
        failedCount++;
        failureReasons.push({ manualId: item.manualId, reason: `${response.status} ${response.statusText}: ${errorText}` });
      } else {
        publishedCount++;
      }
    } catch (err) {
      failedCount++;
      failureReasons.push({ manualId: item.manualId, reason: err.message });
    }
  }

  // Summary Logging
  console.log('\n================================================----');
  console.log('Publish to Supabase Summary:');
  console.log(`  Published: ${publishedCount}`);
  console.log(`  Skipped (No Change): ${skippedCount}`);
  console.log(`  Failed: ${failedCount}`);

  if (failedCount > 0) {
    console.log('\nFailure Details:');
    failureReasons.forEach(f => console.log(`  - ${f.manualId}: ${f.reason}`));
    process.exit(1);
  }
  console.log('================================================----');
}

publishManuals().catch(err => {
  console.error('Unexpected error in publish script:', err);
  process.exit(1);
});
