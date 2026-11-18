/**
 * COSYmanuals Print Booklet control
 * ---------------------------------
 * Adds an offline control bar to a print booklet page:
 *   • "Print / Save as PDF" — opens the browser print dialog (works offline).
 *   • "Download PDF"        — links to the pre-built PDF when one is published.
 *   • a live table of contents built from the booklet's units.
 *
 * Mount on any page that has `.booklet-unit` sections (see
 * `scripts/build_print_booklets.mjs`). Safe to include on non-booklet pages:
 * it no-ops when there are no units.
 *
 * Optional: data-booklet-pdf="/path/to.pdf" sets the download target.
 */
(function () {
  'use strict';

  function slugFromId(id) { return id; }

  function buildToc(units) {
    const nav = document.createElement('nav');
    nav.className = 'booklet-toc no-print';
    nav.setAttribute('aria-label', 'Booklet contents');
    const h = document.createElement('h2');
    h.textContent = 'Contents';
    nav.append(h);
    const ol = document.createElement('ol');
    units.forEach(function (u) {
      const li = document.createElement('li');
      const a = document.createElement('a');
      a.href = '#' + slugFromId(u.id);
      a.textContent = u.title;
      li.append(a);
      ol.append(li);
    });
    nav.append(ol);
    return nav;
  }

  function buildBar(pdfHref) {
    const bar = document.createElement('div');
    bar.className = 'booklet-actions no-print';
    bar.setAttribute('role', 'group');
    bar.setAttribute('aria-label', 'Offline options');

    const print = document.createElement('button');
    print.type = 'button';
    print.className = 'print-btn';
    print.textContent = '🖨️ Print / Save as PDF';
    print.addEventListener('click', function () { window.print(); });
    bar.append(print);

    if (pdfHref) {
      const dl = document.createElement('a');
      dl.className = 'print-btn';
      dl.href = pdfHref;
      dl.setAttribute('download', '');
      dl.textContent = '⬇️ Download PDF';
      bar.append(dl);
    }
    return bar;
  }

  function init(root) {
    const scope = root || document;
    const units = Array.from(scope.querySelectorAll('.booklet-unit')).map(function (s) {
      const t = s.querySelector('.booklet-unit__title');
      return { id: s.id, title: t ? t.textContent.replace(/^\s*\d+\s*/, '').trim() : s.id };
    });
    if (!units.length) return;

    const host = scope.querySelector('main.container') || scope.body || scope;
    const head = host.querySelector('.page-head');
    const pdfHref = document.body.getAttribute('data-booklet-pdf');
    const bar = buildBar(pdfHref);
    if (head && head.parentNode) head.parentNode.insertBefore(bar, head.nextSibling);
    else host.insertBefore(bar, host.firstChild);

    const toc = buildToc(units);
    const firstUnit = scope.querySelector('.booklet-unit');
    if (firstUnit && firstUnit.parentNode) firstUnit.parentNode.insertBefore(toc, firstUnit);
    else host.append(toc);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { init(); });
  } else {
    init();
  }

  window.COSYPrintBooklet = { init: init };
})();
