/**
 * COSYmanuals Grammar Embed
 * -------------------------
 * Renders a grammar explanation by id, so content never has to be re-authored.
 *
 *   <div data-grammar-embed="en-a1-adjectives"></div>
 *
 * Every grammar page in COSYmanuals carries a stable id `<lang>-<level>-<slug>`
 * (see data/grammar-points.json). The id maps deterministically to
 * `manuals/<lang>/grammar/<level>/topics/<slug>.html`, so the embed needs no
 * lookup table; the registry is only a human/SEO reference.
 *
 * The explanation is rendered inside a Shadow DOM: the manual's own stylesheets
 * apply to it, and neither they nor the host page's CSS leak across the boundary.
 *
 * Options (data attributes on the host element):
 *   data-grammar-embed        required, the grammar-point id
 *   data-grammar-embed-chrome "off" hides the "source" header line
 *   data-grammar-embed-url    override the base URL (default: GitHub Pages)
 *
 * Programmatic API: window.COSYGrammarEmbed.render(el) / .renderAll() / .idToPath(id)
 */
(function () {
  'use strict';

  const DEFAULT_BASE = 'https://cosylanguages.github.io/COSYmanuals/';
  const STYLES = [
    'shared/styles/lang-accents.css',
    'shared/styles/tokens.css',
    'shared/styles/base.css',
    'shared/styles/components.css',
    'shared/styles/layout.css'
  ];
  // Interactive-only widgets that need the full page's app.js; dropped from embeds.
  const DROP = [
    '[data-ecosystem-strip]', 'nav', 'header.sd-sticky-header', 'footer',
    '.pager', '.quiz-panel', '.ccq-panel', '.checklist', '.practice-cta-banner',
    'script', 'noscript'
  ];
  const ID_RE = /^([a-z]{2,3})-([a-z0-9]+)-(.+)$/;
  const docCache = new Map();

  function idToPath(id) {
    const m = ID_RE.exec(String(id || '').trim());
    if (!m) return null;
    return 'manuals/' + m[1] + '/grammar/' + m[2] + '/topics/' + m[3] + '.html';
  }

  function baseUrl(host) {
    const override = host && host.getAttribute('data-grammar-embed-url');
    return override || DEFAULT_BASE;
  }

  function absoluteUrl(base, path) {
    return new URL(path, base).href;
  }

  function absolutize(root, pageUrl) {
    root.querySelectorAll('[href]').forEach(function (a) {
      const v = a.getAttribute('href');
      if (v && !/^([a-z]+:|\/\/|#)/i.test(v)) a.setAttribute('href', new URL(v, pageUrl).href);
    });
    root.querySelectorAll('[src]').forEach(function (el) {
      const v = el.getAttribute('src');
      if (v && !/^([a-z]+:|\/\/|data:)/i.test(v)) el.setAttribute('src', new URL(v, pageUrl).href);
    });
  }

  function extractContent(doc) {
    const main = doc.querySelector('main[data-grammar-point]') ||
      doc.querySelector('main') ||
      doc.querySelector('.container');
    if (!main) return null;
    const clone = main.cloneNode(true);
    DROP.forEach(function (sel) {
      clone.querySelectorAll(sel).forEach(function (n) { n.remove(); });
    });
    return clone;
  }

  async function fetchDoc(id, base) {
    const path = idToPath(id);
    if (!path) throw new Error('Invalid grammar-point id: ' + id);
    const url = absoluteUrl(base, path);
    if (docCache.has(url)) return docCache.get(url);
    const promise = fetch(url, { mode: 'cors' }).then(function (res) {
      if (!res.ok) throw new Error('HTTP ' + res.status);
      return res.text();
    }).then(function (htmlText) {
      return { doc: new DOMParser().parseFromString(htmlText, 'text/html'), url: url };
    });
    docCache.set(url, promise);
    return promise;
  }

  function titleFromDoc(doc) {
    const h1 = doc.querySelector('main h1, h1');
    return h1 ? h1.textContent.trim() : '';
  }

  function shadowFor(host) {
    if (!host.shadowRoot) host.attachShadow({ mode: 'open' });
    return host.shadowRoot;
  }

  function styleLinks(base, levelPath) {
    const links = STYLES.map(function (rel) { return absoluteUrl(base, rel); });
    if (levelPath) links.push(absoluteUrl(base, levelPath));
    return links;
  }

  function levelStylePath(id) {
    const m = ID_RE.exec(id);
    return m ? 'manuals/' + m[1] + '/grammar/' + m[2] + '/assets/style.css' : null;
  }

  function embedStyle() {
    return [
      ':host{display:block;font-family:inherit;}',
      '.cosy-embed{border:1px solid rgba(0,0,0,.12);border-radius:8px;padding:4px 20px 12px;background:#fff;color:#111;}',
      '.cosy-embed__bar{display:flex;justify-content:space-between;align-items:baseline;gap:12px;',
      'flex-wrap:wrap;border-bottom:1px solid rgba(0,0,0,.08);margin:0 -20px 12px;padding:10px 20px;}',
      '.cosy-embed__bar a{font-weight:700;text-decoration:none;}',
      '.cosy-embed__src{font-size:.8rem;opacity:.7;}',
      '.cosy-embed__status{padding:16px 20px;opacity:.75;font-style:italic;}',
      '.cosy-embed__err{border-color:rgba(180,0,0,.4);}',
      '.cosy-embed .page-head .eyebrow{display:none;}',
      '.cosy-embed h1{font-size:1.4rem;margin:.2em 0;}'
    ].join('');
  }

  async function render(host) {
    const id = host.getAttribute('data-grammar-embed');
    if (!id || host.__cosyEmbedDone) return;
    host.__cosyEmbedDone = true;
    const base = baseUrl(host);
    const shadow = shadowFor(host);
    const showChrome = host.getAttribute('data-grammar-embed-chrome') !== 'off';

    const linkEls = styleLinks(base, levelStylePath(id)).map(function (href) {
      const l = document.createElement('link');
      l.rel = 'stylesheet';
      l.href = href;
      return l;
    });
    const style = document.createElement('style');
    style.textContent = embedStyle();

    const wrap = document.createElement('div');
    wrap.className = 'cosy-embed';
    wrap.innerHTML = '<div class="cosy-embed__status" role="status">Loading grammar explanation…</div>';

    shadow.append(style);
    linkEls.forEach(function (l) { shadow.append(l); });
    shadow.append(wrap);

    let doc, url;
    try {
      const got = await fetchDoc(id, base);
      doc = got.doc;
      url = got.url;
    } catch (err) {
      wrap.classList.add('cosy-embed__err');
      wrap.innerHTML = '';
      const p = document.createElement('div');
      p.className = 'cosy-embed__status';
      p.textContent = 'Grammar explanation “' + id + '” is unavailable right now.';
      wrap.append(p);
      return;
    }

    const content = extractContent(doc);
    wrap.innerHTML = '';
    if (showChrome) {
      const bar = document.createElement('div');
      bar.className = 'cosy-embed__bar';
      const a = document.createElement('a');
      a.href = url;
      a.textContent = '📘 ' + (titleFromDoc(doc) || id);
      const src = document.createElement('span');
      src.className = 'cosy-embed__src';
      src.textContent = 'COSYmanuals · ' + id;
      bar.append(a, src);
      wrap.append(bar);
    }
    if (content) {
      absolutize(content, url);
      wrap.append(content);
    } else {
      const p = document.createElement('div');
      p.className = 'cosy-embed__status';
      p.textContent = 'No explanation content found for “' + id + '”.';
      wrap.append(p);
    }
  }

  function renderAll(root) {
    (root || document).querySelectorAll('[data-grammar-embed]').forEach(render);
  }

  window.COSYGrammarEmbed = { render: render, renderAll: renderAll, idToPath: idToPath };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { renderAll(); });
  } else {
    renderAll();
  }
})();
