const fs = require('fs');
const path = require('path');
const vm = require('vm');

const WORKBOOK_DATA_PATH = path.join(__dirname, '../student-workbooks/data/workbook_data.js');
const OUTPUT_BASE_DIR = path.join(__dirname, '../student-workbooks/data/workbooks');
const UNMAPPED_FILE_PATH = path.join(__dirname, '../student-workbooks/data/UNMAPPED.md');

function run() {
  // 1. Read and parse workbook_data.js
  const rawContent = fs.readFileSync(WORKBOOK_DATA_PATH, 'utf8');
  const context = {};
  vm.createContext(context);

  // Evaluate code to extract WORKBOOK_TOPICS
  const topics = vm.runInContext(rawContent + ';\nWORKBOOK_TOPICS;', context);

  if (!Array.isArray(topics)) {
    console.error('Error: WORKBOOK_TOPICS is not an array.');
    process.exit(1);
  }

  const totalTopics = topics.length;
  const groups = {};
  const unmapped = [];

  // 2. Group items by lang and level
  for (const topic of topics) {
    if (!topic.lang || !topic.level) {
      unmapped.push(topic);
      continue;
    }

    const lang = String(topic.lang).toLowerCase();
    const level = String(topic.level).toLowerCase();
    const key = `${lang}/${level}`;

    if (!groups[key]) {
      groups[key] = { language: lang, level: level, topics: [] };
    }
    groups[key].topics.push(topic);
  }

  // 3. Write one JSON file per lang/level
  let filesProduced = 0;
  for (const [key, data] of Object.entries(groups)) {
    const langDir = path.join(OUTPUT_BASE_DIR, data.language);
    fs.mkdirSync(langDir, { recursive: true });

    const filePath = path.join(langDir, `${data.level}.json`);
    fs.writeFileSync(filePath, JSON.stringify(data, null, 2) + '\n', 'utf8');
    filesProduced++;
  }

  // Write UNMAPPED.md if any items were skipped (or document none skipped)
  let unmappedMdContent = '# Unmapped Workbook Topics\n\n';
  if (unmapped.length === 0) {
    unmappedMdContent += 'No unmapped topics found. All topics had valid `lang` and `level` fields.\n';
  } else {
    unmappedMdContent += `The following ${unmapped.length} topic(s) were missing \`lang\` or \`level\` and were skipped during normalization:\n\n`;
    for (const item of unmapped) {
      unmappedMdContent += `- **ID:** \`${item.id || 'N/A'}\` | **Title:** ${item.title || 'N/A'} | **Lang:** \`${item.lang || 'MISSING'}\` | **Level:** \`${item.level || 'MISSING'}\`\n`;
    }
  }
  fs.writeFileSync(UNMAPPED_FILE_PATH, unmappedMdContent, 'utf8');

  // 4. Update workbook_data.js header comment if not already updated
  const deprecationComment = `/**
 * SUPERSEDED / DEPRECATED:
 * As of September 11, 2026, WORKBOOK_TOPICS in this file has been superseded
 * by modular JSON files in student-workbooks/data/workbooks/{lang}/{level}.json.
 * Please refer to student-workbooks/data/workbooks/ for active topic datasets.
 */
`;

  if (!rawContent.includes('SUPERSEDED / DEPRECATED:')) {
    fs.writeFileSync(WORKBOOK_DATA_PATH, deprecationComment + rawContent, 'utf8');
  }

  // 5. Print Summary
  console.log('==============================================');
  console.log('WORKBOOK NORMALIZATION SUMMARY');
  console.log('==============================================');
  console.log(`Total topics processed: ${totalTopics}`);
  console.log(`Lang/level JSON files produced: ${filesProduced}`);
  console.log(`Skipped/unmapped topics: ${unmapped.length}`);
  if (unmapped.length > 0) {
    console.log(`Unmapped topics logged to: ${UNMAPPED_FILE_PATH}`);
  }
  console.log('==============================================');
}

run();
