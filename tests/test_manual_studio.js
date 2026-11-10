'use strict';
/* Run: node tests/test_manual_studio.js
 * Checks manual-core against the rules and against scripts/manual_to_record.py. */
const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawnSync } = require('child_process');
const M = require('../shared/studio/manual-core.js');
const Core = require('../shared/studio/studio-core.js');

let passed = 0;
function test(name, fn) { try { fn(); passed++; console.log('ok   ' + name); } catch (e) { console.error('FAIL ' + name + '\n  ' + e.message); process.exitCode = 1; } }

function q(n) { return { question: 'Q' + n + ' is it?', options: ['yes', 'no', 'maybe'], correct: 1, explanation: 'Because **no**.' }; }
function good() {
  return M.createBlankTopic({
    slug: 'to-be-test', title: 'To Be & Not To Be', subtitle: 'Use am, is, are.', eyebrow: 'A1 · Grammar',
    formula: { formula: 'I am / you are', examples: ['I am Anna.', 'You are late.'] },
    outcome: 'Say who you are.', notice: 'What changes after I?',
    ccqs: [q(1), q(2), q(3)],
    rule: { paragraphs: ['Use *am* with I.'], table: { headers: ['Pronoun', 'Form'], rows: [['I', 'am'], ['you', 'are']] } },
    why: 'It is everywhere.', native: 'Think of it as an equals sign.', pronunciation: "I'm = /aɪm/",
    examples: ['She is a doctor.'],
    mistakes: [{ wrong: 'I is Anna', right: 'I am Anna' }, { wrong: 'He are', right: 'He is' }],
    connects: 'Builds on greetings.', checklist: ['I can say my name', 'I can ask who someone is'],
    quiz: [q(1), q(2), q(3)], prev: { slug: 'alphabet', title: 'Alphabet' }, next: { slug: 'articles' }
  });
}

test('a complete topic is ready to publish', () => {
  const s = Core.summarizeChecks(M.getReadiness(good()));
  assert.strictEqual(s.errors, 0, JSON.stringify(M.getReadiness(good()).filter(c => c.level === 'error')));
  assert.ok(s.canPublish);
});
test('a blank topic is not ready', () => assert.ok(Core.summarizeChecks(M.getReadiness(M.createBlankTopic())).errors > 5));
test('bad slug is an error', () => { const t = good(); t.slug = 'Bad Slug'; assert.ok(M.getReadiness(t).some(c => c.id === 'identity' && c.level === 'error')); });
test('ragged table is an error', () => { const t = good(); t.rule.table.rows[0] = ['I']; assert.ok(M.getReadiness(t).some(c => c.id === 'table-shape' && c.level === 'error')); });
test('correct answer must point at a real option', () => { const t = good(); t.quiz[0].correct = 7; assert.ok(M.getReadiness(t).some(c => /^quiz-correct/.test(c.id))); });
test('missing explanation is an error', () => { const t = good(); t.ccqs[1].explanation = ''; assert.ok(M.getReadiness(t).some(c => /^ccq-expl/.test(c.id))); });
test('raw teacher-note dumps are rejected', () => { const t = good(); t.native = 'pronunciation: [{ x }]'; assert.ok(M.getReadiness(t).some(c => c.id === 'teacher-notes' && c.level === 'error')); });

test('author text is escaped; only bold/italic become markup', () => {
  const t = good(); t.notice = '<script>alert(1)</script> **b** *i*';
  const html = M.renderTopicPage(t);
  assert.ok(!html.includes('<script>alert'));
  assert.ok(html.includes('&lt;script&gt;') && html.includes('<b>b</b>') && html.includes('<em>i</em>'));
});
test('answer key lives in data-quiz, not in a visible label', () => {
  assert.ok(M.renderMain(good()).includes('data-quiz="[{&quot;correct&quot;:1}'));
});

test('path and id', () => {
  const t = good();
  assert.strictEqual(M.topicPath(t), 'manuals/en/grammar/a1/topics/to-be-test.html');
  assert.strictEqual(M.canonicalId(t), 'en:a1:manual:to-be-test');
});

test('text formats round-trip', () => {
  const qs = [q(1), q(2)];
  assert.deepStrictEqual(M.parseQuestions(M.formatQuestions(qs)), qs);
  const tb = { headers: ['A', 'B'], rows: [['1', '2']] };
  assert.deepStrictEqual(M.parseTable(M.formatTable(tb)), tb);
  const ms = [{ wrong: 'a', right: 'b' }];
  assert.deepStrictEqual(M.parseMistakes(M.formatMistakes(ms)), ms);
  assert.strictEqual(M.parseTable('only one line'), null);
});
test('question with no marked answer is flagged, not guessed', () => {
  const [one] = M.parseQuestions('Q?\n- a\n- b\n? why');
  assert.strictEqual(one.correct, -1);
  const t = good(); t.quiz[0] = one;
  assert.ok(M.getReadiness(t).some(c => /^quiz-correct/.test(c.id)));
});

function pyAvailable() { return spawnSync('python3', ['--version']).status === 0; }
if (pyAvailable()) {
  test('record and stub match scripts/manual_to_record.py', () => {
    const t = good();
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'manual-'));
    const file = path.join(dir, M.topicPath(t));
    fs.mkdirSync(path.dirname(file), { recursive: true });
    fs.writeFileSync(file, M.renderTopicPage(t));
    const py = spawnSync('python3', ['-I', '-c',
      'import sys,json;sys.path.insert(0,sys.argv[1]);import manual_to_record as m;import os;os.chdir(sys.argv[2]);r,s=m.extract_record_and_stub(sys.argv[3]);print(json.dumps({"r":r,"s":s}))',
      path.resolve(__dirname, '../scripts'), dir, M.topicPath(t)], { encoding: 'utf8' });
    assert.strictEqual(py.status, 0, py.stderr);
    const out = JSON.parse(py.stdout);
    const rec = M.toProtectedRecord(t, new Date(out.r.updated_at));
    ['id', 'language', 'cefr', 'kind', 'slug', 'title', 'summary', 'body'].forEach(k => assert.strictEqual(rec[k], out.r[k], 'record.' + k));
    // Only intended difference: the JS stub escapes '&' in the title (the Python one does not).
    assert.strictEqual(M.renderStub(t).split('&amp;').join('&'), out.s);
  });
} else { console.log('skip python comparison (python3 missing)'); }

console.log('\n' + passed + ' passed');
