/**
 * migrate_topics_to_storage.js
 *
 * Scans manuals/{lang}/{subject}/{level}/topics/*.html and uploads raw static HTML files
 * to Supabase Storage bucket 'manual-topics' at path: {lang}/{level}/{subject}/{storageKeyFilename}
 *
 * Usage:
 *   node scripts/migrate_topics_to_storage.js [--dry-run]
 *   node scripts/migrate_topics_to_storage.js --execute
 *
 * Requirements (when running with --execute):
 *   Environment variables SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Parse CLI flags
const args = process.argv.slice(2);
const isExecute = args.includes('--execute');
const isDryRun = !isExecute || args.includes('--dry-run');

console.log('----------------------------------------------------');
console.log(`MODE: ${isDryRun ? 'DRY-RUN (No files uploaded or deleted)' : 'EXECUTE (Live Upload & Git Branch/Delete)'}`);
console.log('----------------------------------------------------');

const MANUALS_DIR = path.join(__dirname, '..', 'manuals');
const DATA_DIR = path.join(__dirname, '..', 'data');

// Character replacement map for transliterating accented characters to closest ASCII
const CHAR_MAP = {
  'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
  'à': 'a', 'á': 'a', 'â': 'a', 'ä': 'a', 'ã': 'a', 'å': 'a',
  'ù': 'u', 'ú': 'u', 'û': 'u', 'ü': 'u',
  'ì': 'i', 'í': 'i', 'î': 'i', 'ï': 'i',
  'ò': 'o', 'ó': 'o', 'ô': 'o', 'ö': 'o', 'õ': 'o', 'ø': 'o',
  'ñ': 'n', 'ç': 'c'
};

/**
 * Normalizes string to NFC and transliterates non-ASCII characters outside [A-Za-z0-9/_.-]
 * to produce a 100% Supabase Storage InvalidKey-safe key.
 */
function toStorageSafeKey(originalPath) {
  if (!originalPath) return originalPath;
  let normalized = originalPath.normalize('NFC');
  let result = '';
  for (let i = 0; i < normalized.length; i++) {
    const ch = normalized[i];
    if (/[A-Za-z0-9/_.-]/.test(ch)) {
      result += ch;
    } else if (CHAR_MAP[ch]) {
      result += CHAR_MAP[ch];
    } else if (CHAR_MAP[ch.toLowerCase()]) {
      result += CHAR_MAP[ch.toLowerCase()].toUpperCase();
    } else {
      // Fallback: strip unrecognized non-ASCII characters
      console.warn(`Warning: Stripping unmapped character '${ch}' (U+${ch.charCodeAt(0).toString(16).padStart(4, '0')}) from path "${originalPath}"`);
    }
  }
  return result;
}

// Helper to recursively find topic HTML files
function findTopicFiles(dir) {
  let results = [];
  if (!fs.existsSync(dir)) return results;

  const list = fs.readdirSync(dir);
  for (const file of list) {
    const fullPath = path.join(dir, file);
    const stat = fs.statSync(fullPath);
    if (stat.isDirectory()) {
      results = results.concat(findTopicFiles(fullPath));
    } else if (file.endsWith('.html')) {
      // Check if relative path matches manuals/{lang}/{subject}/{level}/topics/*.html
      const relPath = path.relative(MANUALS_DIR, fullPath).replace(/\\/g, '/');
      const parts = relPath.split('/');
      // Expected structure: [lang, subject, level, 'topics', filename]
      if (parts.length === 5 && parts[3] === 'topics') {
        const [lang, subject, level, , filename] = parts;
        const repoRelPath = path.relative(path.join(__dirname, '..'), fullPath).replace(/\\/g, '/');

        // Target storage key format: {lang}/{level}/{subject}/{filename}
        const rawStorageKey = `${lang}/${level}/${subject}/${filename}`;
        const storageKey = toStorageSafeKey(rawStorageKey);

        results.push({
          sourcePath: fullPath,
          relSourcePath: repoRelPath,
          storageKey,
          language: lang,
          level,
          subject,
          filename
        });
      }
    }
  }
  return results;
}

const topicFiles = findTopicFiles(MANUALS_DIR);
console.log(`Discovered ${topicFiles.length} topic HTML file(s) under manuals/`);

if (topicFiles.length === 0) {
  console.log('No topic files found matching pattern manuals/{lang}/{subject}/{level}/topics/*.html.');
  process.exit(0);
}

if (isDryRun) {
  console.log('\n[DRY-RUN] Source Path -> Destination Storage Key Mappings:');
  let sanitizedCount = 0;
  topicFiles.forEach(item => {
    const isSanitized = item.relSourcePath.includes('pretérito') || item.relSourcePath.includes('beajoù') || item.relSourcePath.includes('micherioù');
    if (isSanitized) sanitizedCount++;
    console.log(`  ${item.relSourcePath} -> ${item.storageKey}`);
  });
  console.log(`\n[DRY-RUN] Total topic files that WOULD be uploaded: ${topicFiles.length}`);
  console.log(`[DRY-RUN] Dry run complete. Pass --execute to run the actual migration.`);
  process.exit(0);
}

// EXECUTE MODE
const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
  console.error('Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables are required for --execute mode.');
  process.exit(1);
}

const BUCKET = 'manual-topics';
const storageBaseUrl = `${SUPABASE_URL.replace(/\/$/, '')}/storage/v1/object/${BUCKET}`;

async function uploadFile(targetKey, fileBuffer, contentType = 'text/html') {
  const safeKey = toStorageSafeKey(targetKey);
  const targetUrl = `${storageBaseUrl}/${safeKey}`;

  const response = await fetch(targetUrl, {
    method: 'POST',
    headers: {
      'Content-Type': contentType,
      'apikey': SUPABASE_SERVICE_ROLE_KEY,
      'Authorization': `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
      'x-upsert': 'true'
    },
    body: fileBuffer
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Upload failed (${response.status} ${response.statusText}): ${errorText}`);
  }
  return true;
}

async function runMigration() {
  let successCount = 0;
  const failedFiles = [];
  const manifestEntries = [];

  console.log(`Beginning upload of ${topicFiles.length} files to Supabase Storage bucket '${BUCKET}'...`);

  for (let i = 0; i < topicFiles.length; i++) {
    const item = topicFiles[i];
    const fileContents = fs.readFileSync(item.sourcePath);

    try {
      await uploadFile(item.storageKey, fileContents, 'text/html');
      successCount++;
      manifestEntries.push({
        originalRepoPath: item.relSourcePath,
        storageKey: item.storageKey,
        language: item.language,
        level: item.level,
        subject: item.subject
      });

      if ((i + 1) % 100 === 0 || i === topicFiles.length - 1) {
        console.log(`Progress: ${i + 1}/${topicFiles.length} uploaded successfully.`);
      }
    } catch (err) {
      console.error(`Failed to upload ${item.relSourcePath} -> ${item.storageKey}: ${err.message}`);
      failedFiles.push({ file: item.relSourcePath, error: err.message });
    }
  }

  // Ensure failure output is printed strictly AFTER all progress logs
  if (failedFiles.length > 0 || successCount !== topicFiles.length) {
    console.error(`\nUpload Phase Summary: ${successCount}/${topicFiles.length} uploaded successfully.`);
    console.error(`CRITICAL: Upload count mismatch! Expected ${topicFiles.length}, successfully uploaded ${successCount}.`);
    console.error('Failed files list:');
    failedFiles.forEach(f => console.error(`  - ${f.file}: ${f.error}`));
    console.error('Migration aborted. No repository files were deleted.');
    process.exit(1);
  }

  console.log(`\nUpload Phase Summary: All ${successCount}/${topicFiles.length} topic files uploaded successfully!`);

  // MANIFEST GENERATION & UPLOAD
  const manifestData = {
    generatedAt: new Date().toISOString(),
    totalTopics: manifestEntries.length,
    topics: manifestEntries
  };
  const manifestJsonString = JSON.stringify(manifestData, null, 2);
  const manifestBuffer = Buffer.from(manifestJsonString, 'utf-8');

  console.log('\nUploading manifest to Supabase Storage at "_manifest/manual-topics-manifest.json"...');
  try {
    await uploadFile('_manifest/manual-topics-manifest.json', manifestBuffer, 'application/json');
    console.log('Manifest uploaded successfully to Supabase Storage!');
  } catch (err) {
    console.error('Failed to upload manifest to Supabase Storage:', err.message);
    process.exit(1);
  }

  // SAVE MANIFEST TO REPO BEFORE DELETION
  if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
  }
  const repoManifestPath = path.join(DATA_DIR, 'manual-topics-manifest.json');
  fs.writeFileSync(repoManifestPath, manifestJsonString, 'utf-8');
  console.log(`Manifest saved locally at "${path.relative(path.join(__dirname, '..'), repoManifestPath)}"`);

  // GIT BACKUP BRANCH & DELETION
  console.log('\nCreating git backup branch "pre-storage-migration-backup"...');
  try {
    execSync('git branch -f pre-storage-migration-backup', { stdio: 'inherit' });
    console.log('Backup branch "pre-storage-migration-backup" successfully created.');
  } catch (err) {
    console.error('Failed to create backup branch "pre-storage-migration-backup":', err.message);
    process.exit(1);
  }

  console.log('Deleting uploaded topic HTML files from local workspace...');
  for (const item of topicFiles) {
    if (fs.existsSync(item.sourcePath)) {
      fs.unlinkSync(item.sourcePath);
    }
  }

  console.log('Committing deletion changes and manifest to git...');
  try {
    execSync('git add data/manual-topics-manifest.json', { stdio: 'inherit' });
    execSync('git add -u', { stdio: 'inherit' });
    execSync('git commit -m "Move topic pages to gated Supabase Storage [skip ci]"', { stdio: 'inherit' });
    console.log('Commit created successfully with message "Move topic pages to gated Supabase Storage [skip ci]".');
  } catch (err) {
    console.error('Failed to commit deletion:', err.message);
    process.exit(1);
  }

  console.log('\nMigration completed successfully!');
}

runMigration().catch(err => {
  console.error('Unexpected error during migration:', err);
  process.exit(1);
});
