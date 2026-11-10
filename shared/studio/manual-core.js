/**
 * shared/studio/manual-core.js
 * Manual topic authoring for the COSYmanuals studio. Pure logic, no DOM, so the
 * same code runs in the browser and in tests.
 *
 * A "topic" is structured data for one manual topic page. This module:
 *   - checks it against the topic standard (the 11 sections, see
 *     manuals/en/grammar/a1/GRAMMAR_STANDARD.md and CONTENT_ARCHITECTURE.md §3)
 *   - renders the full page using the components the existing pages use
 *   - exports the same artifacts as scripts/manual_to_record.py:
 *       toProtectedRecord  -> the record (kind 'manual') carrying the body
 *       renderStub         -> the public "Protected Manual Shell" stub
 *
 * It decides nothing about WHERE the body is published. Full pages are public
 * if committed to git, so publishing is a separate, explicit step.
 */
(function (root, factory) {
  if (typeof module === 'object' && typeof module.exports === 'object') {
    module.exports = factory(require('./studio-core.js'));
  } else {
    root.CosyManualCore = factory(root.CosyStudioCore);
  }
})(typeof self !== 'undefined' ? self : this, function (Core) {
  'use strict';

  const LANGUAGES = {
    ba: 'Bashkir', br: 'Breton', cv: 'Chuvash', de: 'German', el: 'Greek', en: 'English',
    es: 'Spanish', fr: 'French', hy: 'Armenian', it: 'Italian', ka: 'Georgian',
    pt: 'Portuguese', ru: 'Russian', tt: 'Tatar'
  };
  const MODULES = ['grammar', 'vocabulary', 'communication'];
  const LEVELS = ['a1', 'a2', 'b1', 'b2', 'c1', 'c2'];
  const SLUG_RE = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

  /** Raw teacher-note dumps the repo's check_no_raw_teacher_notes.py rejects. */
  const FORBIDDEN_PATTERNS = ['pronunciation: [{', 'code: "', '&quot;point&quot;'];

  const MIN = { ccqs: 3, quiz: 3, mistakes: 2, checklist: 2, optionsPerQuestion: 2 };

  // ---- Text helpers ------------------------------------------------------

  function escapeHtml(value) {
    return String(value === undefined || value === null ? '' : value)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  /** Escape, then allow only **bold** and *italic*. Nothing else becomes markup. */
  function inline(value) {
    return escapeHtml(value)
      .replace(/\*\*([^*\n]+)\*\*/g, '<b>$1</b>')
      .replace(/(^|[^*])\*([^*\n]+)\*(?!\*)/g, '$1<em>$2</em>');
  }

  function text(v) { return typeof v === 'string' ? v.trim() : ''; }
  function list(v) { return Array.isArray(v) ? v : []; }

  function allStrings(value, out) {
    if (typeof value === 'string') out.push(value);
    else if (Array.isArray(value)) value.forEach(function (v) { allStrings(v, out); });
    else if (value && typeof value === 'object') Object.keys(value).forEach(function (k) { allStrings(value[k], out); });
    return out;
  }

  // ---- Model -------------------------------------------------------------

  function createBlankTopic(overrides) {
    return Object.assign({
      iso: 'en', module: 'grammar', level: 'a1', slug: '', title: '', subtitle: '', eyebrow: '',
      formula: { formula: '', examples: ['', ''] },
      outcome: '',
      notice: '',
      ccqs: [0, 1, 2].map(blankQuestion),
      rule: { paragraphs: [''], table: null },
      why: '', native: '', pronunciation: '',
      examples: ['', ''],
      mistakes: [{ wrong: '', right: '' }, { wrong: '', right: '' }],
      connects: '',
      checklist: ['', ''],
      quiz: [0, 1, 2].map(blankQuestion),
      prev: null, next: null
    }, overrides || {});
  }

  function blankQuestion() {
    return { question: '', options: ['', '', ''], correct: 0, explanation: '' };
  }

  function topicPath(t) {
    return 'manuals/' + t.iso + '/' + t.module + '/' + t.level + '/topics/' + t.slug + '.html';
  }

  function canonicalId(t) { return t.iso + ':' + t.level + ':manual:' + t.slug; }

  function platformUrl(t) {
    return 'https://cosyplatform.com/courses/' + t.iso + '/' + t.level + '/' + t.slug;
  }

  // ---- Readiness ---------------------------------------------------------

  function checkQuestions(label, qs, min, add) {
    const items = list(qs);
    const filled = items.filter(function (q) { return q && text(q.question); });
    add(label, filled.length >= min ? 'ok' : 'error', label,
      filled.length >= min ? filled.length + ' questions' : 'Needs at least ' + min + ' questions (has ' + filled.length + ').');
    items.forEach(function (q, i) {
      if (!q || !text(q.question)) return;
      const opts = list(q.options).map(text).filter(Boolean);
      const n = i + 1;
      if (opts.length < MIN.optionsPerQuestion) add(label + '-opts-' + n, 'error', label + ' ' + n, 'Needs at least ' + MIN.optionsPerQuestion + ' answer options.');
      else if (!Number.isInteger(q.correct) || q.correct < 0 || q.correct >= list(q.options).length || !text(list(q.options)[q.correct])) {
        add(label + '-correct-' + n, 'error', label + ' ' + n, 'Mark which answer is correct.');
      }
      if (!text(q.explanation)) add(label + '-expl-' + n, 'error', label + ' ' + n, 'Add an explanation of the correct answer.');
    });
  }

  /** Checks for the topic standard. Same shape every COSY studio uses. */
  function getReadiness(topic) {
    const t = topic || {};
    const checks = [];
    const add = function (id, level, label, detail) { checks.push(Core.makeCheck(id, level, label, detail)); };

    const idProblems = [];
    if (!LANGUAGES[t.iso]) idProblems.push('Choose a language.');
    if (MODULES.indexOf(t.module) === -1) idProblems.push('Choose grammar, vocabulary or communication.');
    if (LEVELS.indexOf(t.level) === -1) idProblems.push('Choose a CEFR level.');
    if (!SLUG_RE.test(t.slug || '')) idProblems.push('Slug must be lowercase letters, numbers and single hyphens.');
    add('identity', idProblems.length ? 'error' : 'ok', 'Language, module, level and slug', idProblems.join(' '));

    add('title', text(t.title) ? 'ok' : 'error', 'Title', text(t.title) ? '' : 'Add a title.');
    add('subtitle', text(t.subtitle) ? 'ok' : 'warn', 'Subtitle', text(t.subtitle) ? '' : 'A subtitle appears under the title and in the page description.');

    const f = t.formula || {};
    const fx = list(f.examples).map(text).filter(Boolean);
    add('formula', text(f.formula) && fx.length >= 2 ? 'ok' : 'error', '1 Formula and key examples',
      text(f.formula) && fx.length >= 2 ? '' : 'Needs a formula and at least 2 examples.');
    add('outcome', text(t.outcome) ? 'ok' : 'warn', 'What you can communicate', text(t.outcome) ? '' : 'Say what the learner can do after this page.');
    add('notice', text(t.notice) ? 'ok' : 'error', '3 Guided observation', text(t.notice) ? '' : 'Add the "What do you notice?" question.');
    checkQuestions('ccq', t.ccqs, MIN.ccqs, add);

    const r = t.rule || {};
    const paras = list(r.paragraphs).map(text).filter(Boolean);
    const table = r.table && list(r.table.headers).length && list(r.table.rows).length;
    add('rule', paras.length || table ? 'ok' : 'error', '5 Main rule', paras.length || table ? '' : 'Add a rule paragraph or a table.');
    if (table) {
      const cols = r.table.headers.length;
      const ragged = r.table.rows.some(function (row) { return list(row).length !== cols; });
      add('table-shape', ragged ? 'error' : 'ok', 'Rule table', ragged ? 'Every row needs ' + cols + ' cells.' : '');
    }

    add('native', text(t.native) ? 'ok' : 'error', '6 Think like a native speaker', text(t.native) ? '' : 'Explain the logic of this structure.');
    add('why', text(t.why) ? 'ok' : 'warn', 'Why this matters', text(t.why) ? '' : 'Optional but expected.');

    const mistakes = list(t.mistakes).filter(function (m) { return m && text(m.wrong) && text(m.right); });
    add('mistakes', mistakes.length >= MIN.mistakes ? 'ok' : 'error', '7 Common mistakes',
      mistakes.length >= MIN.mistakes ? mistakes.length + ' pairs' : 'Needs at least ' + MIN.mistakes + ' wrong/right pairs.');
    add('connects', text(t.connects) ? 'ok' : 'warn', '9 Connects to', text(t.connects) ? '' : 'Link this topic to what the learner already knows.');
    const checklist = list(t.checklist).map(text).filter(Boolean);
    add('checklist', checklist.length >= MIN.checklist ? 'ok' : 'error', '10 Self-assessment checklist',
      checklist.length >= MIN.checklist ? checklist.length + ' items' : 'Needs at least ' + MIN.checklist + ' items.');
    checkQuestions('quiz', t.quiz, MIN.quiz, add);

    const leaks = FORBIDDEN_PATTERNS.filter(function (p) { return allStrings(t, []).join('\n').indexOf(p) !== -1; });
    add('teacher-notes', leaks.length ? 'error' : 'ok', 'No raw teacher notes',
      leaks.length ? 'Contains a raw teacher-note dump (' + leaks.join(', ') + ').' : '');
    return checks;
  }

  // ---- Rendering ---------------------------------------------------------

  const OPTION_LETTERS = 'abcdefghijklmnopqrstuvwxyz';

  function renderQuestions(qs, startClass) {
    return list(qs).filter(function (q) { return q && text(q.question); }).map(function (q, i) {
      const opts = list(q.options).map(text).filter(Boolean);
      return '<div class="qitem">\n' +
        ' <div class="qtext">' + (i + 1) + '. ' + inline(q.question) + '</div>\n' +
        ' <div class="qopts">' + opts.map(function (o) { return '<button type="button" class="qopt">' + inline(o) + '</button>'; }).join('') + '</div>\n' +
        ' <div class="qexplain">' + inline(q.explanation) + '</div>\n</div>';
    }).join('');
  }

  function quizData(qs) {
    return escapeHtml(JSON.stringify(list(qs).filter(function (q) { return q && text(q.question); })
      .map(function (q) { return { correct: q.correct }; })));
  }

  /** The text between <main> and </main>: this is what a protected record stores as `body`. */
  function renderMain(topic) {
    const t = topic;
    const f = t.formula || {};
    const out = [];
    out.push('<div class="page-head">\n' +
      (text(t.eyebrow) ? ' <span class="eyebrow">' + escapeHtml(t.eyebrow) + '</span>\n' : '') +
      ' <h1>' + escapeHtml(t.title) + '</h1>\n' +
      (text(t.subtitle) ? ' <p class="subtitle">' + escapeHtml(t.subtitle) + '</p>\n' : '') +
      ' <hr class="rule">\n</div>');

    out.push('<div class="box mint">\n <h3>⚡ Formula &amp; Key Examples</h3>\n' +
      ' <p><code>' + escapeHtml(f.formula) + '</code></p>\n <ul>' +
      list(f.examples).map(text).filter(Boolean).map(function (e) { return '<li>' + inline(e) + '</li>'; }).join('') + '</ul>\n</div>');

    if (text(t.outcome)) {
      out.push('<div class="box outcome-banner"><strong>🎯 What you can communicate after this page:</strong> ' + inline(t.outcome) + '</div>');
    }

    out.push('<div class="box platform-link">\n <!-- TODO: Verify COSYplatform lesson availability for ' + escapeHtml(t.iso + '/' + t.level + '/' + t.slug) + ' -->\n' +
      ' <strong>📖 Full Interactive Lesson:</strong>\n Practice this topic on COSYplatform:\n' +
      ' <a href="' + escapeHtml(platformUrl(t)) + '" target="_blank" rel="noopener">Open Lesson on COSYplatform →</a>\n</div>');

    out.push('<div class="box mint">\n <h3>👀 What do you notice?</h3>\n <p>' + inline(t.notice) + '</p>\n</div>');

    out.push('<div class="ccq-panel" data-quiz="' + quizData(t.ccqs) + '">\n' +
      ' <div class="quiz-head"><h3>💡 Check your understanding</h3><span class="quiz-score">Score: 0 / ' +
      list(t.ccqs).filter(function (q) { return q && text(q.question); }).length + '</span></div>\n' + renderQuestions(t.ccqs) + '\n</div>');

    const r = t.rule || {};
    if (r.table && list(r.table.headers).length && list(r.table.rows).length) {
      out.push('<div class="table-wrap" tabindex="0" role="region" aria-label="' + escapeHtml(t.title) + '"><table>\n<thead><tr>' +
        r.table.headers.map(function (h) { return '<th scope="col">' + inline(h) + '</th>'; }).join('') + '</tr></thead>\n<tbody>' +
        r.table.rows.map(function (row) { return '<tr>' + list(row).map(function (c) { return '<td>' + inline(c) + '</td>'; }).join('') + '</tr>'; }).join('') +
        '</tbody>\n</table></div>');
    }
    const paras = list(r.paragraphs).map(text).filter(Boolean);
    if (paras.length) out.push('<div class="box rule-box">' + paras.map(function (p) { return '<p>' + inline(p) + '</p>'; }).join('') + '</div>');

    if (text(t.why)) out.push('<div class="box why">\n <h3>&#9733; Why this matters</h3>\n <p>' + inline(t.why) + '</p>\n</div>');
    out.push('<div class="box native">\n <h3>&#128173; Think like a native speaker</h3>\n <p>' + inline(t.native) + '</p>\n</div>');
    if (text(t.pronunciation)) out.push('<div class="pron-callout">\n <h3>🗣️ Pronunciation Note</h3>\n <p>' + inline(t.pronunciation) + '</p>\n</div>');

    const ex = list(t.examples).map(text).filter(Boolean);
    if (ex.length) out.push('<div class="examples"><span class="label">More examples</span><ul>' + ex.map(function (e) { return '<li>' + inline(e) + '</li>'; }).join('') + '</ul></div>');

    out.push('<div class="mistakes">\n <div class="m-title">&#9888;&#65039; Common mistakes</div>\n' +
      list(t.mistakes).filter(function (m) { return m && text(m.wrong) && text(m.right); }).map(function (m) {
        return ' <div class="mflip">\n  <div class="wrong-line"><span class="x">&#10060;</span><span class="wrong-text">' + inline(m.wrong) + '</span></div>\n' +
          '  <span class="hint">tap to see the correct form</span>\n' +
          '  <div class="right-line"><span class="c">&#9989;</span><span>' + inline(m.right) + '</span></div>\n </div>';
      }).join('\n') + '\n</div>');

    if (text(t.connects)) out.push('<div class="box connect">\n <h3>🔗 Connects to what you already know</h3>\n <p>' + inline(t.connects) + '</p>\n</div>');

    out.push('<div class="checklist" data-key="' + escapeHtml(t.slug) + '">\n <h3>&#127919; Can you already use this?</h3>\n ' +
      list(t.checklist).map(text).filter(Boolean).map(function (c) { return '<label class="check-item"><input type="checkbox"><span>' + inline(c) + '</span></label>'; }).join('') +
      '\n <div class="check-progress"></div>\n</div>');

    out.push('<div class="quiz-panel" data-quiz="' + quizData(t.quiz) + '">\n <div class="quiz-head"><h2>Quick check</h2><span class="quiz-score">Score: 0 / ' +
      list(t.quiz).filter(function (q) { return q && text(q.question); }).length + '</span></div>\n' + renderQuestions(t.quiz) +
      '\n <p class="celebration-msg">🎉 Progress Celebration: You have completed this topic!</p>\n <button type="button" class="quiz-reset">Reset quiz</button>\n</div>');

    const pager = [];
    if (t.prev && text(t.prev.slug)) pager.push('<a class="prev" href="../topics/' + escapeHtml(t.prev.slug) + '.html"><span class="dir">&larr; Previous</span><span class="ttl">' + escapeHtml(t.prev.title || t.prev.slug) + '</span></a>');
    if (t.next && text(t.next.slug)) pager.push('<a class="next" href="../topics/' + escapeHtml(t.next.slug) + '.html"><span class="dir">Next &rarr;</span><span class="ttl">' + escapeHtml(t.next.title || t.next.slug) + '</span></a>');
    if (pager.length) out.push('<div class="pager">' + pager.join('') + '</div>');

    return out.join('\n\n');
  }

  /**
   * The full page. `previewBase` (preview only) makes relative CSS/JS resolve
   * from the studio page; a published page never has it.
   */
  function renderTopicPage(topic, options) {
    const t = topic;
    const opts = options || {};
    const langName = LANGUAGES[t.iso] || t.iso;
    const moduleName = t.module ? t.module.charAt(0).toUpperCase() + t.module.slice(1) : '';
    return '<!DOCTYPE html>\n<html lang="' + escapeHtml(t.iso) + '" data-lang-theme="' + escapeHtml(t.iso) + '">\n<head>\n' +
      '<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n' +
      '<title>' + escapeHtml(t.title) + ' · COSYlanguages</title>\n' +
      '<meta name="description" content="' + escapeHtml(t.subtitle) + '">\n' +
      (opts.previewBase ? '<base href="' + escapeHtml(opts.previewBase) + '">\n' : '') +
      ['lang-accents', 'tokens', 'base', 'components', 'layout'].map(function (s) { return '<link rel="stylesheet" href="../../../../../shared/styles/' + s + '.css">'; }).join('\n') + '\n' +
      '<link rel="stylesheet" href="../assets/style.css">\n</head>\n<body>\n' +
      '<nav id="cosy-nav" aria-label="Main navigation"></nav>\n\n<main class="container">' + renderMain(t) + '</main>' +
      '<footer class="site">\n <div class="container">\n' +
      ' <div>COSYlanguages · ' + escapeHtml(langName) + ' ' + escapeHtml(moduleName) + ' Manual, Level ' + escapeHtml(String(t.level).toUpperCase()) + ' · interactive web edition</div>\n' +
      ' <div><a href="../index.html">&larr; Back to the ' + escapeHtml(String(t.level).toUpperCase()) + ' index</a></div>\n </div>\n</footer>\n' +
      '<script src="../assets/app.js"></script>\n</body>\n</html>\n';
  }

  // ---- Exports that match scripts/manual_to_record.py --------------------

  function summaryOf(t) {
    return text(t.subtitle) || ('Protected manual topic: ' + t.title);
  }

  /** The protected record: same fields manual_to_record.py writes. `body` is the <main> content. */
  function toProtectedRecord(topic, now) {
    return {
      id: canonicalId(topic),
      language: topic.iso,
      cefr: topic.level,
      kind: 'manual',
      slug: topic.slug,
      title: text(topic.title),
      summary: summaryOf(topic),
      body: renderMain(topic),
      updated_at: (now || new Date()).toISOString()
    };
  }

  /** The public stub that replaces a full page. Mirrors manual_to_record.py's template. */
  function renderStub(topic) {
    const lang = topic.iso, cefr = topic.level, course = topic.module;
    const title = text(topic.title);
    const summary = summaryOf(topic);
    const id = canonicalId(topic);
    const rel = '../../../../../';
    return '<!DOCTYPE html>\n<html lang="' + escapeHtml(lang) + '" data-lang-theme="' + escapeHtml(lang) + '">\n<head>\n' +
      '<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n' +
      '<title>' + escapeHtml(title) + ' · Protected Manual Shell · COSYmanuals</title>\n' +
      '<meta name="description" content="' + escapeHtml(summary) + '">\n' +
      ['lang-accents', 'tokens', 'base', 'components', 'layout'].map(function (s) { return '<link rel="stylesheet" href="' + rel + 'shared/styles/' + s + '.css">'; }).join('\n') + '\n' +
      '</head>\n<body>\n<nav id="cosy-nav" aria-label="Navigation principale"></nav>\n\n<main class="container">\n' +
      '<div class="page-head" style="margin-top: 2rem;">\n <span class="eyebrow">' + escapeHtml(lang.toUpperCase()) + ' ' + escapeHtml(cefr.toUpperCase()) + ' Manual</span>\n' +
      ' <h1>' + escapeHtml(title) + '</h1>\n <p class="subtitle">' + escapeHtml(summary) + '</p>\n <hr class="rule">\n</div>\n\n' +
      '<div class="box gated-content-notice" style="background: var(--surface-2, #f8f9fa); border: 2px dashed var(--border-color, #ccc); padding: 2rem; border-radius: 8px; text-align: center; margin: 2rem 0;">\n' +
      '  <div style="font-size: 2.5rem; margin-bottom: 1rem;">🔒</div>\n  <h2 style="margin-bottom: 0.5rem; font-size: 1.5rem;">Protected Ecosystem Content</h2>\n' +
      '  <p style="max-width: 600px; margin: 0 auto 1.5rem auto; color: var(--text-muted, #666);">\n    Full lesson text, rule guides, answer keys, and teacher materials for <strong>' + escapeHtml(title) + '</strong> are protected and hosted in Supabase database tables with Row Level Security.\n  </p>\n' +
      '  <div style="display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;">\n' +
      '    <a href="https://cosylanguages.github.io/COSYlanguages/login.html?redirect=' + escapeHtml(id) + '" class="btn-primary" style="background: var(--cosy-manuals-accent, #6b202b); color: #fff; padding: 0.75rem 1.5rem; border-radius: 6px; text-decoration: none; font-weight: bold;">Log In to Access Content</a>\n' +
      '    <a href="' + rel + 'manuals/' + escapeHtml(lang) + '/' + escapeHtml(course) + '/' + escapeHtml(cefr) + '/index.html" class="btn-secondary" style="border: 1px solid var(--border-color, #ccc); color: var(--text-color, #333); padding: 0.75rem 1.5rem; border-radius: 6px; text-decoration: none;">Return to ' + escapeHtml(cefr.toUpperCase()) + ' Index</a>\n  </div>\n</div>\n</main>\n\n' +
      '<footer class="cosy-ecosystem-footer-note" style="text-align: center; padding: 2rem 0; color: var(--text-muted, #888); font-size: 0.875rem;">\n  Part of the COSY Family · Upstream Curriculum Owner: COSYplatform\n</footer>\n</body>\n</html>\n';
  }

  // ---- Plain-text editing formats ---------------------------------------
  // Questions:  "Question?" then "- option" lines, "- *right option", and "? explanation".
  // Table:      first line headers, then rows; cells split by " | ".
  // Mistakes:   "wrong => right" per line.

  function parseQuestions(src) {
    return String(src || '').split(/\n\s*\n/).map(function (b) { return b.trim(); }).filter(Boolean).map(function (block) {
      const q = { question: '', options: [], correct: -1, explanation: '' };
      block.split('\n').forEach(function (raw) {
        const line = raw.trim();
        if (!line) return;
        if (line.indexOf('- ') === 0 || line === '-') {
          let o = line.slice(1).trim();
          if (o.charAt(0) === '*') { q.correct = q.options.length; o = o.slice(1).trim(); }
          q.options.push(o);
        } else if (line.charAt(0) === '?') q.explanation = line.slice(1).trim();
        else q.question = q.question ? q.question + ' ' + line : line;
      });
      return q;
    });
  }

  function formatQuestions(qs) {
    return list(qs).map(function (q) {
      return [q.question].concat(list(q.options).map(function (o, i) { return '- ' + (i === q.correct ? '*' : '') + o; }))
        .concat(q.explanation ? ['? ' + q.explanation] : []).join('\n');
    }).join('\n\n');
  }

  function parseTable(src) {
    const rows = String(src || '').split('\n').map(function (l) { return l.trim(); }).filter(Boolean)
      .map(function (l) { return l.split('|').map(function (c) { return c.trim(); }); });
    return rows.length > 1 ? { headers: rows[0], rows: rows.slice(1) } : null;
  }
  function formatTable(t) {
    if (!t) return '';
    return [t.headers].concat(t.rows).map(function (r) { return r.join(' | '); }).join('\n');
  }

  function parseMistakes(src) {
    return String(src || '').split('\n').map(function (l) { return l.trim(); }).filter(Boolean).map(function (l) {
      const i = l.indexOf('=>');
      return i === -1 ? { wrong: l, right: '' } : { wrong: l.slice(0, i).trim(), right: l.slice(i + 2).trim() };
    });
  }
  function formatMistakes(ms) {
    return list(ms).map(function (m) { return m.wrong + ' => ' + m.right; }).join('\n');
  }

  return {
    parseQuestions: parseQuestions, formatQuestions: formatQuestions, parseTable: parseTable, formatTable: formatTable,
    parseMistakes: parseMistakes, formatMistakes: formatMistakes,
    LANGUAGES: LANGUAGES, MODULES: MODULES, LEVELS: LEVELS, MIN: MIN, FORBIDDEN_PATTERNS: FORBIDDEN_PATTERNS,
    escapeHtml: escapeHtml, inline: inline,
    createBlankTopic: createBlankTopic, blankQuestion: blankQuestion,
    topicPath: topicPath, canonicalId: canonicalId, platformUrl: platformUrl,
    getReadiness: getReadiness,
    renderMain: renderMain, renderTopicPage: renderTopicPage,
    toProtectedRecord: toProtectedRecord, renderStub: renderStub
  };
});
