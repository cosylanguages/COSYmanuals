/* Manuals studio UI. All logic lives in manual-core.js; this file only wires the form. */
(function () {
  'use strict';
  var M = window.CosyManualCore, Core = window.CosyStudioCore;
  var form = document.getElementById('ms-form');
  var store = Core.createDraftStore({ prefix: 'cosy-manuals-studio:' });
  var DRAFT = 'current';
  var timer = null;

  function lines(s) { return String(s || '').split('\n').map(function (l) { return l.trim(); }).filter(Boolean); }
  function fill(sel, values, labels) {
    sel.innerHTML = '';
    values.forEach(function (v) { var o = document.createElement('option'); o.value = v; o.textContent = labels ? labels[v] + ' (' + v + ')' : v; sel.appendChild(o); });
  }
  fill(form.iso, Object.keys(M.LANGUAGES), M.LANGUAGES);
  fill(form.module, M.MODULES);
  fill(form.level, M.LEVELS);

  function read() {
    var f = form;
    var paras = f.paragraphs.value.split(/\n\s*\n/).map(function (p) { return p.replace(/\s*\n\s*/g, ' ').trim(); }).filter(Boolean);
    return {
      iso: f.iso.value, module: f.module.value, level: f.level.value,
      slug: f.slug.value.trim(), title: f.title.value.trim(), subtitle: f.subtitle.value.trim(), eyebrow: f.eyebrow.value.trim(),
      formula: { formula: f.formula.value.trim(), examples: lines(f.formulaExamples.value) },
      outcome: f.outcome.value.trim(), notice: f.notice.value.trim(),
      ccqs: M.parseQuestions(f.ccqs.value),
      rule: { paragraphs: paras, table: M.parseTable(f.table.value) },
      why: f.why.value.trim(), native: f.native.value.trim(), pronunciation: f.pronunciation.value.trim(),
      examples: lines(f.examples.value),
      mistakes: M.parseMistakes(f.mistakes.value),
      connects: f.connects.value.trim(), checklist: lines(f.checklist.value),
      quiz: M.parseQuestions(f.quiz.value),
      prev: f.prevSlug.value.trim() ? { slug: f.prevSlug.value.trim() } : null,
      next: f.nextSlug.value.trim() ? { slug: f.nextSlug.value.trim() } : null
    };
  }

  function write(t) {
    var f = form;
    f.iso.value = t.iso; f.module.value = t.module; f.level.value = t.level;
    f.slug.value = t.slug || ''; f.title.value = t.title || ''; f.subtitle.value = t.subtitle || ''; f.eyebrow.value = t.eyebrow || '';
    f.formula.value = (t.formula && t.formula.formula) || '';
    f.formulaExamples.value = ((t.formula && t.formula.examples) || []).join('\n');
    f.outcome.value = t.outcome || ''; f.notice.value = t.notice || '';
    f.ccqs.value = M.formatQuestions(t.ccqs);
    f.paragraphs.value = ((t.rule && t.rule.paragraphs) || []).join('\n\n');
    f.table.value = M.formatTable(t.rule && t.rule.table);
    f.why.value = t.why || ''; f.native.value = t.native || ''; f.pronunciation.value = t.pronunciation || '';
    f.examples.value = (t.examples || []).join('\n');
    f.mistakes.value = M.formatMistakes(t.mistakes);
    f.connects.value = t.connects || ''; f.checklist.value = (t.checklist || []).join('\n');
    f.quiz.value = M.formatQuestions(t.quiz);
    f.prevSlug.value = (t.prev && t.prev.slug) || ''; f.nextSlug.value = (t.next && t.next.slug) || '';
  }

  function download(name, mime, body) {
    var a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([body], { type: mime }));
    a.download = name; document.body.appendChild(a); a.click(); a.remove();
    setTimeout(function () { URL.revokeObjectURL(a.href); }, 1000);
  }

  function refresh() {
    var t = read();
    var checks = M.getReadiness(t);
    var sum = Core.summarizeChecks(checks);
    var ul = document.getElementById('ms-checks');
    ul.innerHTML = '';
    checks.forEach(function (c) {
      var li = document.createElement('li'); li.className = c.level;
      li.textContent = c.label;
      if (c.detail && c.level !== 'ok') { var s = document.createElement('small'); s.textContent = c.detail; li.appendChild(s); }
      ul.appendChild(li);
    });
    ['ms-page', 'ms-record', 'ms-stub'].forEach(function (id) { document.getElementById(id).disabled = !sum.canPublish; });
    document.getElementById('ms-path').textContent = /^[a-z0-9-]+$/.test(t.slug) ? M.topicPath(t) : '';
    // The preview is sandboxed with no scripts: author text can never run in the studio.
    document.getElementById('ms-preview').srcdoc = M.renderTopicPage(t, { previewBase: new URL('../../', location.href).href + 'manuals/' + t.iso + '/' + t.module + '/' + t.level + '/topics/' });
    if (store.save(DRAFT, t)) {
      document.getElementById('ms-saved').textContent = 'Draft saved in this browser';
    } else {
      document.getElementById('ms-saved').textContent = 'Draft not saved (browser storage unavailable)';
    }
    return { t: t, sum: sum };
  }

  form.addEventListener('input', function () { clearTimeout(timer); timer = setTimeout(refresh, 250); });
  document.getElementById('ms-page').onclick = function () { var r = refresh(); if (r.sum.canPublish) download(r.t.slug + '.html', 'text/html', M.renderTopicPage(r.t)); };
  document.getElementById('ms-stub').onclick = function () { var r = refresh(); if (r.sum.canPublish) download(r.t.slug + '.html', 'text/html', M.renderStub(r.t)); };
  document.getElementById('ms-record').onclick = function () {
    var r = refresh();
    if (r.sum.canPublish) download(M.canonicalId(r.t).replace(/:/g, '_') + '.json', 'application/json', JSON.stringify(M.toProtectedRecord(r.t), null, 2));
  };
  document.getElementById('ms-new').onclick = function () {
    if (confirm('Start a new topic? The current draft will be replaced.')) { store.remove(DRAFT); write(M.createBlankTopic()); refresh(); }
  };

  var saved = store.load(DRAFT);
  write(saved && saved.value ? Object.assign(M.createBlankTopic(), saved.value) : M.createBlankTopic());
  refresh();

  // Show the verified role when a configured Supabase client exists; never trust stored roles.
  if (window.supabaseClient) {
    Core.resolveVerifiedUser(window.supabaseClient).then(function (u) {
      if (u) document.getElementById('ms-who').textContent = 'Signed in as ' + u.email + ' (' + u.role + '). Nothing is published from here.';
    });
  }
})();
