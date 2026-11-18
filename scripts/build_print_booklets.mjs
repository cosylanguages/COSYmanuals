#!/usr/bin/env node
/**
 * Build full print booklets
 * -------------------------
 * For every language that has grammar topics, assemble one printable booklet at
 * `manuals/<lang>/print/full.html` containing every grammar explanation in
 * reading order. The booklet is self-contained (shared styles + print.css) and
 * is the single source for the downloadable PDF of the whole grammar manual.
 *
 * The per-language download control (`shared/js/print-booklet.js`) and the PDF
 * builder (`scripts/build_manual_pdfs.mjs`) both point at this file.
 *
 * Run: node scripts/build_print_booklets.mjs
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const REGISTRY = path.join(ROOT, 'data', 'grammar-points.json');
const SITE = 'https://cosylanguages.github.io/COSYmanuals/';

const LANG_NAMES = {
  ba: 'Bashkir', br: 'Breton', cv: 'Chuvash', de: 'German', el: 'Greek',
  en: 'English', es: 'Spanish', fr: 'French', hy: 'Armenian', it: 'Italian',
  ka: 'Georgian', pt: 'Portuguese', ru: 'Russian', tt: 'Tatar'
};

const DROP = /<(script|noscript|style)\b[\s\S]*?<\/\1>/gi;
const STRIP_TAGS = /<(nav|header|footer)\b[^>]*class="[^"]*(cosy-nav|sd-sticky-header|site)[^"]*"[^>]*>[\s\S]*?<\/\1>/gi;

function esc(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function mainInner(html, sourcePath) {
  const m = /<main\b[^>]*>([\s\S]*?)<\/main>/i.exec(html) ||
    /<div\b[^>]*class="[^"]*\bcontainer\b[^"]*"[^>]*>([\s\S]*?)<\/div>/i.exec(html);
  if (!m) return '';
  const pageUrl = SITE + sourcePath;
  return m[1]
    .replace(DROP, '')
    .replace(STRIP_TAGS, '')
    .replace(/<div\b[^>]*data-ecosystem-strip[^>]*>[\s\S]*?<\/div>/gi, '')
    .replace(/<a\b[^>]*class="[^"]*btn-practice-link[^"]*"[^>]*>[\s\S]*?<\/a>/gi, '')
    // Inlined content keeps page-relative links; rebase them on the source page.
    .replace(/\b(href|src)="([^"]*)"/gi, function (all, attr, val) {
      if (!val || /^([a-z]+:|\/\/|#|data:)/i.test(val)) return all;
      try { return attr + '="' + new URL(val, pageUrl).href + '"'; }
      catch { return all; }
    })
    .trim();
}

const LEVEL_ORDER = ['a0', 'a1', 'a2', 'b1', 'b2', 'c1', 'c2'];

function build() {
  const registry = JSON.parse(fs.readFileSync(REGISTRY, 'utf8'));
  const byLang = new Map();
  for (const p of registry.points) {
    if (!byLang.has(p.lang)) byLang.set(p.lang, []);
    byLang.get(p.lang).push(p);
  }

  const built = [];
  for (const [lang, points] of [...byLang.entries()].sort()) {
    points.sort((a, b) => {
      const la = LEVEL_ORDER.indexOf(a.level) - LEVEL_ORDER.indexOf(b.level);
      return la !== 0 ? la : a.id.localeCompare(b.id);
    });

    const sections = points.map((p, i) => {
      const abs = path.join(ROOT, p.path);
      const html = fs.readFileSync(abs, 'utf8');
      const body = mainInner(html, p.path);
      const title = p.title || p.slug;
      return `  <section class="booklet-unit" id="${esc(p.id)}">
    <h2 class="booklet-unit__title"><span class="booklet-unit__num">${i + 1}</span> ${esc(title)}</h2>
${body}
  </section>`;
    }).join('\n');

    const name = LANG_NAMES[lang] || lang.toUpperCase();
    const page = `<!doctype html>
<html lang="${lang}" data-lang-theme="${lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(name)} Grammar Manual — Full Print Booklet · COSYmanuals</title>
<meta name="description" content="Complete ${esc(name)} grammar manual for offline lessons. Print or save as PDF.">
<link rel="stylesheet" href="../../../shared/styles/lang-accents.css">
<link rel="stylesheet" href="../../../shared/styles/tokens.css">
<link rel="stylesheet" href="../../../shared/styles/base.css">
<link rel="stylesheet" href="../../../shared/styles/components.css">
<link rel="stylesheet" href="../../../shared/styles/layout.css">
<link rel="stylesheet" href="../../../shared/styles/print.css">
<link rel="stylesheet" href="print.css">
<link rel="stylesheet" href="https://cosylanguages.github.io/COSYlanguages/css/ecosystem-strip.css">
<style>
.booklet-unit{page-break-before:always;break-before:page;}
.booklet-unit:first-of-type{page-break-before:avoid;break-before:avoid;}
.booklet-unit__title{display:flex;gap:.6rem;align-items:baseline;border-bottom:2px solid var(--cosy-manuals-accent,#6b202b);padding-bottom:.3rem;}
.booklet-unit__num{font-size:.8em;opacity:.6;}
.booklet-unit .sd-sticky-header,.booklet-unit .pager{display:none;}
</style>
</head>
<body data-booklet-pdf="full.pdf">
<div data-ecosystem-strip data-self="manuals" class="no-print"></div>
<main class="container">
  <div class="page-head">
    <span class="eyebrow">COSYmanuals · ${esc(name)} · ${points.length} grammar points</span>
    <h1>${esc(name)} Grammar Manual (full booklet)</h1>
    <p class="subtitle">Complete reference for offline lessons — print or save as PDF.</p>
    <hr class="rule">
  </div>
${sections}
</main>
<script src="../../../shared/js/print-booklet.js" defer></script>
<script src="https://cosylanguages.github.io/COSYlanguages/js/ecosystem-strip.js" defer></script>
</body>
</html>
`;
    const out = path.join(ROOT, 'manuals', lang, 'print', 'full.html');
    fs.mkdirSync(path.dirname(out), { recursive: true });
    fs.writeFileSync(out, page, 'utf8');
    built.push({ lang, points: points.length, out: path.relative(ROOT, out) });
  }

  for (const b of built) console.log(`${b.lang}: ${b.points} points -> ${b.out}`);
  console.log(`Built ${built.length} booklets`);
}

build();
