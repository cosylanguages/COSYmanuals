/**
 * migrate_topics_to_storage.js
 *
 * Scans manuals/{lang}/{subject}/{level}/topics/*.html and uploads raw static HTML files
 * to Supabase Storage bucket 'manual-topics' at path: {lang}/{level}/{subject}/{original-filename}
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
        // Upload destination format: {lang}/{level}/{subject}/{filename}
        const destPath = `${lang}/${level}/${subject}/${filename}`;
        results.push({
          sourcePath: fullPath,
          relSourcePath: path.relative(path.join(__dirname, '..'), fullPath).replace(/\\/g, '/'),
          destPath,
          lang,
          subject,
          level,
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
  console.log('\n[DRY-RUN] Source Path -> Destination Path Mappings:');
  topicFiles.forEach(item => {
    console.log(`  ${item.relSourcePath} -> ${item.destPath}`);
  });
  console.log(`\n[DRY-RUN] Total topic files that WOULD be uploaded: ${topicFiles.length}`);
  console.log('[DRY-RUN] Dry run complete. Pass --execute to run the actual migration.');
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

async function uploadFile(item) {
  const fileContents = fs.readFileSync(item.sourcePath);
  const targetUrl = `${storageBaseUrl}/${item.destPath}`;

  const response = await fetch(targetUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'text/html',
      'apikey': SUPABASE_SERVICE_ROLE_KEY,
      'Authorization': `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
      'x-upsert': 'true'
    },
    body: fileContents
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

  console.log(`Beginning upload of ${topicFiles.length} files to Supabase Storage bucket '${BUCKET}'...`);

  for (let i = 0; i < topicFiles.length; i++) {
    const item = topicFiles[i];
    try {
      await uploadFile(item);
      successCount++;
      if ((i + 1) % 100 === 0 || i === topicFiles.length - 1) {
        console.log(`Progress: ${i + 1}/${topicFiles.length} uploaded successfully.`);
      }
    } catch (err) {
      console.error(`Failed to upload ${item.relSourcePath} -> ${item.destPath}: ${err.message}`);
      failedFiles.push({ file: item.relSourcePath, error: err.message });
    }
  }

  console.log(`\nUpload Phase Summary: ${successCount}/${topicFiles.length} uploaded successfully.`);

  // VERIFICATION CHECK
  if (successCount !== topicFiles.length || failedFiles.length > 0) {
    console.error(`\nCRITICAL: Upload count mismatch! Expected ${topicFiles.length}, successfully uploaded ${successCount}.`);
    console.error('Failed files list:');
    failedFiles.forEach(f => console.error(`  - ${f.file}: ${f.error}`));
    console.error('Migration aborted. No repository files were deleted.');
    process.exit(1);
  }

  console.log('Verification successful! Upload count matches source file count exactly.');

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

  console.log('Committing deletion changes to git...');
  try {
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
