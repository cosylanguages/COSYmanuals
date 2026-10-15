/**
 * load_records_to_supabase.js
 *
 * Upserts lesson JSON records into Supabase `lessons` table using SUPABASE_URL
 * and SUPABASE_SERVICE_ROLE_KEY.
 *
 * Usage:
 *   node scripts/load_records_to_supabase.js drafts/fr_grammar_records.json
 */

const fs = require('fs');
const path = require('path');

try {
  require('dotenv').config();
} catch (e) {
  // dotenv optional
}

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

const jsonPath = process.argv[2];

if (!jsonPath) {
  console.error('Usage: node scripts/load_records_to_supabase.js <path-to-json-records>');
  process.exit(1);
}

if (!fs.existsSync(jsonPath)) {
  console.error(`Error: File not found: ${jsonPath}`);
  process.exit(1);
}

if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
  console.log('Notice: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY environment variables not provided.');
  console.log('Skipping remote Supabase network push. Local protected records export saved in:', jsonPath);
  process.exit(0);
}

async function loadRecords() {
  const data = JSON.parse(fs.readFileSync(jsonPath, 'utf-8'));
  const records = Array.isArray(data) ? data : [data];

  console.log(`Loaded ${records.length} records from ${jsonPath}. Batch upserting to Supabase...`);

  const endpoint = `${SUPABASE_URL.replace(/\/$/, '')}/rest/v1/lessons`;

  // Upsert in batches of 50
  const BATCH_SIZE = 50;
  let successCount = 0;

  for (let i = 0; i < records.length; i += BATCH_SIZE) {
    const batch = records.slice(i, i + BATCH_SIZE);

    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'apikey': SUPABASE_SERVICE_ROLE_KEY,
          'Authorization': `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
          'Prefer': 'resolution=merge-duplicates'
        },
        body: JSON.stringify(batch)
      });

      if (!response.ok) {
        const errText = await response.text();
        console.error(`Failed batch ${i / BATCH_SIZE + 1}: ${response.status} ${response.statusText}`, errText);
      } else {
        successCount += batch.length;
        console.log(`Upserted batch ${Math.floor(i / BATCH_SIZE) + 1}/${Math.ceil(records.length / BATCH_SIZE)} (${successCount}/${records.length})`);
      }
    } catch (err) {
      console.error(`Error posting batch ${i / BATCH_SIZE + 1}:`, err.message);
    }
  }

  console.log(`Finished processing. Successfully upserted ${successCount}/${records.length} records.`);
}

loadRecords().catch(err => {
  console.error('Unexpected error loading records:', err);
  process.exit(1);
});
