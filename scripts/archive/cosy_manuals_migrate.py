#!/usr/bin/env python3
"""
cosy_manuals_migrate.py  --  COSYlanguages -> COSYmanuals manual migration tool.

Lives in COSYmanuals at scripts/cosy_manuals_migrate.py.  Stdlib only (Python 3.9+).

Subcommands
  audit   Report which REAL manual pages in a COSYlanguages checkout have no REAL
          counterpart in this repo.  Exit code 1 if any are missing (use as a gate).
  migrate Copy the missing pages (and the assets they need) from a COSYlanguages
          checkout into this repo, rewriting every relative link/asset reference.
          Never overwrites an existing REAL page unless --force is given.
          Replaces redirect stubs and fills gaps.
  verify  Check that every relative href/src in manuals/**/*.html resolves to a file.
          --json-out F saves a baseline; --baseline F fails only on NEW broken links; --fix repairs the safe ones.
  make-indexes  Create missing manuals/<iso>/index.html and manuals/<iso>/<type>/index.html landing pages.

A "redirect stub" is an HTML page with <meta http-equiv="refresh"> and < 400 chars of
visible text ("Page Moved").  A stub is NOT counted as migrated content.

Examples
  python3 scripts/cosy_manuals_migrate.py audit   --source ../COSYlanguages
  python3 scripts/cosy_manuals_migrate.py audit   --source ../COSYlanguages --iso fr --type grammar --level a2
  python3 scripts/cosy_manuals_migrate.py migrate --source ../COSYlanguages --iso fr --type grammar --level a2 --dry-run
  python3 scripts/cosy_manuals_migrate.py migrate --source ../COSYlanguages --iso fr --type grammar --level a2
  python3 scripts/cosy_manuals_migrate.py verify  --iso fr --type grammar --level a2
"""
import argparse, collections, json, os, re, shutil, subprocess, sys
from urllib.parse import urlsplit, urlunsplit

ISOS = {'ba', 'br', 'cv', 'de', 'el', 'en', 'es', 'fr', 'hy', 'it', 'ka', 'pt', 'ru', 'tt'}
TYPES = ('grammar', 'vocabulary', 'communication')
LEVEL_RE = re.compile(r'[abc][12]')
SITE = 'https://cosylanguages.github.io/COSYlanguages/'

# Legacy flat folders in COSYlanguages/manuals/  ->  (iso, type); they all map to level a1.
LEGACY = {
    'grammaire-francaise': ('fr', 'grammar'), 'lexique-francais': ('fr', 'vocabulary'),
    'elliniki-grammatiki': ('el', 'grammar'), 'leksilogio-ellinikon': ('el', 'vocabulary'),
    'grammatika-russkogo-yazyka': ('ru', 'grammar'), 'leksika-russkogo-yazyka': ('ru', 'vocabulary'),
    'deutsche-grammatik': ('de', 'grammar'), 'deutscher-wortschatz': ('de', 'vocabulary'),
    'gramatica-espanola': ('es', 'grammar'), 'vocabulario-espanol': ('es', 'vocabulary'),
    'grammatica-italiana': ('it', 'grammar'), 'lessico-italiano': ('it', 'vocabulary'),
    'gramatica-portuguesa': ('pt', 'grammar'), 'vocabulario-portugues': ('pt', 'vocabulary'),
    'hayots-lezvi-kerakanutyun': ('hy', 'grammar'), 'hayots-lezvi-barapashar': ('hy', 'vocabulary'),
    'qartuli-gramatika': ('ka', 'grammar'), 'qartuli-leqsika': ('ka', 'vocabulary'),
    'tatar-teli-grammatikasy': ('tt', 'grammar'), 'tatar-teli-leksikasy': ('tt', 'vocabulary'),
    'bashqort-tele-grammatikahy': ('ba', 'grammar'), 'bashqort-tele-leksikahy': ('ba', 'vocabulary'),
    'chavash-grammatika': ('cv', 'grammar'), 'chavash-leksiki': ('cv', 'vocabulary'),
    'yezhadur-brezhoneg': ('br', 'grammar'), 'geriou-brezhoneg': ('br', 'vocabulary'),
    'vocabulary-manual': ('en', 'vocabulary'), 'communication-manual': ('en', 'communication'),
}
# Legacy English level folders: grammar-a2, vocabulary-c1, ...
EN_LEVEL_FOLDER = re.compile(r'(grammar|vocabulary)-([abc][12])')

# Flat hub pages in COSYlanguages/manuals/  ->  manuals/<iso>/index-<level>.html in COSYmanuals
HUB_NAMES = {'bashqort': 'ba', 'brezhoneg': 'br', 'chavash': 'cv', 'deutsch': 'de', 'ellinika': 'el', 'english': 'en',
             'espanol': 'es', 'francaise': 'fr', 'hayots': 'hy', 'italiano': 'it', 'portugues': 'pt', 'qartuli': 'ka',
             'russkiy': 'ru', 'tatar': 'tt'}
HUB_RE = re.compile(r'manuals/(?:[a-z]{2}/)?([a-z]+)-(a0-a1|a2|b1|b2|c1|c2)\.html')

SRC_ROOT = None
ROOT_DIRS = {'css', 'practice', 'languages', 'images', 'js', 'comparative', 'hybrid', 'apps', 'sounds', 'data'}
CSS_RENAME_DIR = 'shared/styles/'     # css/<name>  ->  shared/styles/<name>
CSS_COPY_IF_MISSING = {'lang-accents.css', 'home.css'}   # exist in COSYlanguages/css, not in shared/styles


# --------------------------------------------------------------------------- helpers
def read(p):
    with open(p, encoding='utf-8', errors='ignore') as f:
        return f.read()


def text_len(s):
    s = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', s, flags=re.S)
    s = re.sub(r'<[^>]+>', ' ', s)
    return len(re.sub(r'\s+', ' ', s).strip())


def is_stub(s):
    return bool(re.search(r'http-equiv=["\']refresh', s, re.I)) and text_len(s) < 400


def page_title(s):
    m = re.search(r'<title>(.*?)</title>', s, re.S | re.I)
    if not m:
        return ''
    t = re.sub(r'<[^>]+>', '', m.group(1))
    t = re.split(r'\s+[\u00b7|\u2013\u2014-]\s+', t)[0]      # drop " · COSYlanguages" style suffixes
    return re.sub(r'[^\w]+', ' ', t.lower()).strip()


def git_files(root, sub):
    """Tracked + untracked (non-ignored) files under `sub`, so uncommitted work is visible to audit/verify."""
    try:
        out = subprocess.check_output(['git', '-C', root, '-c', 'core.quotePath=false', 'ls-files', '--cached', '--others', '--exclude-standard', sub],
                                      stderr=subprocess.DEVNULL).decode()
        return sorted(set(f for f in out.split('\n') if f and os.path.exists(os.path.join(root, f))))
    except Exception:
        out = []
        base = os.path.join(root, sub)
        for d, _, fs in os.walk(base):
            for f in fs:
                out.append(os.path.relpath(os.path.join(d, f), root).replace(os.sep, '/'))
        return sorted(out)


def classify(rel):
    """rel = path inside source repo starting with manuals/.  Return (iso,type,level,subpath) or None."""
    p = rel.split('/')
    if len(p) < 3 or p[0] != 'manuals':
        return None
    x = p[1]
    if x in ISOS and len(p) >= 4 and p[2] in TYPES:
        if LEVEL_RE.fullmatch(p[3]):
            if len(p) >= 5:
                return (x, p[2], p[3], '/'.join(p[4:]))
            return None
        else:
            return (x, p[2], 'a1', '/'.join(p[3:]))
    if x in LEGACY:
        return (LEGACY[x][0], LEGACY[x][1], 'a1', '/'.join(p[2:]))
    m = EN_LEVEL_FOLDER.fullmatch(x)
    if m:
        return ('en', m.group(1), m.group(2), '/'.join(p[2:]))
    return None


def dest_of(rel):
    k = classify(rel)
    return None if not k else f'manuals/{k[0]}/{k[1]}/{k[2]}/{k[3]}'


def _in(value, spec):
    return not spec or value in spec.split(',')


def matches(k, a):
    """--iso/--type/--level accept comma-separated lists, e.g. --iso es,it,pt --level a1,a2"""
    return _in(k[0], a.iso) and _in(k[1], a.type) and _in(k[2], a.level)


def map_source_target(resolved):
    """Map a path in the COSYlanguages tree to the equivalent path in COSYmanuals, or None."""
    parts = resolved.split('/')
    m = HUB_RE.fullmatch(resolved) or re.fullmatch(r'manuals/(?:.*/)?([a-z]+)-(a0-a1|a2|b1|b2|c1|c2)\.html', resolved)
    if m and m.group(1) in HUB_NAMES:        # also repairs dead links such as manuals/fr/grammar/francaise-a2.html
        return f'manuals/{HUB_NAMES[m.group(1)]}/index-{m.group(2)}.html'
    if parts[0] == 'manuals':
        d = dest_of(resolved)
        return d if d else resolved          # unclassified manuals/ files keep their path (identity)
    if parts[0] in LEGACY or EN_LEVEL_FOLDER.fullmatch(parts[0] or ''):   # legacy folder at repo root
        return dest_of('manuals/' + resolved)
    return None


class Index:
    """Index of REAL pages already present in this repo (COSYmanuals)."""

    def __init__(self, repo):
        self.repo = repo
        self.real = set()       # (iso,type,level,basename)
        self.titles = set()     # (iso,type,level,normalised <title>)
        self.real_paths = set()
        self.stub_paths = set()
        for f in git_files(repo, 'manuals'):
            if not f.endswith('.html'):
                continue
            k = classify(f)
            if not k:
                continue
            s = read(os.path.join(repo, f))
            if is_stub(s):
                self.stub_paths.add(f)
            else:
                self.real.add(k[:3] + (os.path.basename(k[3]),))
                self.real_paths.add(f)
                t = page_title(s)
                if t:
                    self.titles.add(k[:3] + (t,))


def is_present(idx, k, content):
    """Present = a real page with the same basename OR the same title exists at the same iso/type/level."""
    if k[:3] + (os.path.basename(k[3]),) in idx.real:
        return 'name'
    t = page_title(content)
    if t and k[:3] + (t,) in idx.titles:
        return 'title'
    return None


def source_pages(src, a):
    """Yield (src_rel, key) for REAL html pages in the source matching the filters."""
    for f in git_files(src, 'manuals'):
        if not f.endswith('.html'):
            continue
        k = classify(f)
        if not k or not matches(k, a):
            continue
        if is_stub(read(os.path.join(src, f))):
            continue
        yield f, k


# --------------------------------------------------------------------------- audit
def cmd_audit(a):
    idx = Index(a.repo)
    tot = collections.Counter()
    miss = collections.defaultdict(list)
    for f, k in source_pages(a.source, a):
        tot[k[:3]] += 1
        if not is_present(idx, k, read(os.path.join(a.source, f))):
            miss[k[:3]].append(f)
    print(f"{'iso':4} {'type':13} {'lvl':3} {'source real pages':>17} {'missing in COSYmanuals':>23}")
    T = M = 0
    for k in sorted(tot):
        T += tot[k]
        M += len(miss[k])
        flag = '' if not miss[k] else '  <-- GAP'
        print(f'{k[0]:4} {k[1]:13} {k[2]:3} {tot[k]:17d} {len(miss[k]):23d}{flag}')
    print(f"{'ALL':4} {'':13} {'':3} {T:17d} {M:23d}")
    if a.out:
        rows = sorted(f for v in miss.values() for f in v)
        with open(a.out, 'w') as fh:
            fh.write('\n'.join(rows) + ('\n' if rows else ''))
        print(f'wrote {len(rows)} missing source paths to {a.out}')
    # files under manuals/ that the level-based migration does NOT cover
    uncl = collections.defaultdict(list)
    for f in git_files(a.source, 'manuals'):
        if classify(f) or f.endswith('.md') and f.count('/') == 1:
            continue
        m = HUB_RE.fullmatch(f)
        if m and m.group(1) in HUB_NAMES:
            uncl['hub page (mapped to manuals/<iso>/index-<level>.html)'].append(f); continue
        p = f.split('/')
        if len(p) == 3 and p[1] in ISOS and p[2] == 'index.html':
            uncl['iso landing page manuals/<iso>/index.html'].append(f)
        elif len(p) == 4 and p[1] in ISOS and p[2] in TYPES and p[3] == 'index.html':
            uncl['type index manuals/<iso>/<type>/index.html'].append(f)
        elif f.endswith('.pdf'):
            uncl['pdf'].append(f)
        elif len(p) >= 4 and p[1] == 'tt':
            uncl['tt non-standard layout (bulek-N / topics / assets)'].append(f)
        elif f.endswith('.html') and is_stub(read(os.path.join(a.source, f))):
            uncl['redirect stub (ignore)'].append(f)
        else:
            uncl['other'].append(f)
    if uncl and not (a.iso or a.type or a.level):
        print('\nunclassified files under source manuals/ (not covered by the level-based migration):')
        for k2, v in sorted(uncl.items()):
            print(f'  {len(v):5d}  {k2}')
        if a.unclassified_out:
            with open(a.unclassified_out, 'w') as fh:
                for k2, v in sorted(uncl.items()):
                    for f in v:
                        fh.write(f'{k2}\t{f}\n')
    allowed = a.allow_missing or 0
    sys.exit(1 if M > allowed else 0)


# --------------------------------------------------------------------------- link rewriting
SKIP = re.compile(r'^(#|https?:|//|mailto:|tel:|javascript:|data:|\{\{|\$\{|<%)', re.I)
ATTR = re.compile(r'''(?P<attr>\b(?:href|src|action|poster)\s*=\s*)(?P<q>["'])(?P<url>.*?)(?P=q)''', re.S | re.I)
METAREFRESH = re.compile(r'''(?P<pre>content\s*=\s*["']\s*\d+\s*;\s*url\s*=\s*)(?P<url>[^"']+)''', re.I)
JS_REPLACE = re.compile(r'''(?P<pre>location\.replace\(\s*["'])(?P<url>[^"']+)''')


def rewrite_url(url, src_rel, dst_rel, stats, cssroot_ok):
    """Rewrite one relative URL found in source page src_rel so it works from dst_rel."""
    if SKIP.match(url.strip()) or not url.strip():
        return url
    parts = urlsplit(url)
    path = parts.path
    if not path:
        return url
    if path.endswith('.html.html'):          # typo present in some COSYlanguages pages
        path = path[:-5]
        stats['typo_fixed'] += 1
    resolved = os.path.normpath(os.path.join(os.path.dirname(src_rel), path)).replace(os.sep, '/')
    # source pages with a wrong `../` depth: escaping above the repo root, or manuals/css/..., manuals/languages/...
    if resolved.startswith('../'):
        resolved = re.sub(r'^(\.\./)+', '', resolved)
        stats['depth_fixed'] += 1
    else:
        seg = resolved.split('/')
        if seg[0] == 'manuals' and len(seg) > 2 and seg[1] in ROOT_DIRS and SRC_ROOT and not os.path.exists(os.path.join(SRC_ROOT, resolved)):
            resolved = '/'.join(seg[1:])
            stats['depth_fixed'] += 1
    trailing = path.endswith('/')
    # 1) inside manuals/ (or a legacy folder) -> map to the new location, relative to dest page
    mapped = map_source_target(resolved)
    if mapped:
        new = os.path.relpath(mapped, os.path.dirname(dst_rel)).replace(os.sep, '/')
        stats['internal'] += 1
        return urlunsplit(('', '', new + ('/' if trailing and not new.endswith('/') else ''), parts.query, parts.fragment))
    top = resolved.split('/')[0]
    # 2) shared css
    if top == 'css' and resolved.count('/') == 1:
        name = resolved.split('/')[1]
        if name.endswith('.css') and cssroot_ok(name):
            new = os.path.relpath(CSS_RENAME_DIR + name, os.path.dirname(dst_rel)).replace(os.sep, '/')
            stats['css'] += 1
            return urlunsplit(('', '', new, parts.query, parts.fragment))
    # 3) anything else that lives in COSYlanguages (practice, index.html, languages, images ...) -> absolute URL
    stats['absolute'] += 1
    stats['absolute_targets'][top] += 1
    return SITE + resolved + (('?' + parts.query) if parts.query else '') + (('#' + parts.fragment) if parts.fragment else '')


def rewrite_html(s, src_rel, dst_rel, stats, cssroot_ok):
    def fix_attr(m):
        new = rewrite_url(m.group('url'), src_rel, dst_rel, stats, cssroot_ok)
        return f"{m.group('attr')}{m.group('q')}{new}{m.group('q')}"
    s = ATTR.sub(fix_attr, s)
    s = METAREFRESH.sub(lambda m: m.group('pre') + rewrite_url(m.group('url'), src_rel, dst_rel, stats, cssroot_ok), s)
    s = JS_REPLACE.sub(lambda m: m.group('pre') + rewrite_url(m.group('url'), src_rel, dst_rel, stats, cssroot_ok), s)

    # links that now leave the repo should open in a new tab, like every other cross-repo link in COSYmanuals
    def add_target(m):
        tag = m.group(0)
        if SITE not in tag or re.search(r'\btarget\s*=', tag):
            return tag
        return tag[:-1] + ' target="_blank" rel="noopener">'
    return re.sub(r'<a\b[^>]*>', add_target, s)


# --------------------------------------------------------------------------- migrate
def cmd_migrate(a):
    global SRC_ROOT
    SRC_ROOT = a.source
    idx = Index(a.repo)
    css_have = set(os.listdir(os.path.join(a.repo, 'shared/styles'))) if os.path.isdir(os.path.join(a.repo, 'shared/styles')) else set()
    css_src = os.path.join(a.source, 'css')

    def cssroot_ok(name):
        return name in css_have or (name in CSS_COPY_IF_MISSING and os.path.exists(os.path.join(css_src, name)))

    stats = collections.Counter(); stats['absolute_targets'] = collections.Counter()
    done, replaced, skipped_present, conflicts, asset_copied = [], [], [], [], []
    folders = set()

    for f, k in source_pages(a.source, a):
        dst = dest_of(f)
        present = bool(is_present(idx, k, read(os.path.join(a.source, f))))
        dst_exists_real = dst in idx.real_paths
        dst_is_stub = dst in idx.stub_paths
        if present and not a.force:
            skipped_present.append(f)
            continue
        if dst_exists_real and not a.force:
            conflicts.append(f)
            continue
        out = rewrite_html(read(os.path.join(a.source, f)), f, dst, stats, cssroot_ok)
        (replaced if dst_is_stub else done).append(dst)
        folders.add((k[0], k[1], k[2]))
        if not a.dry_run:
            os.makedirs(os.path.dirname(os.path.join(a.repo, dst)), exist_ok=True)
            with open(os.path.join(a.repo, dst), 'w', encoding='utf-8') as fh:
                fh.write(out)

    # optional: type-level index pages (manuals/<iso>/<type>/index.html) and iso landing pages (manuals/<iso>/index.html)
    if a.indexes:
        for f in git_files(a.source, 'manuals'):
            p3 = f.split('/')
            is_type_idx = len(p3) == 4 and p3[1] in ISOS and p3[2] in TYPES and p3[3] == 'index.html'
            is_iso_idx = len(p3) == 3 and p3[1] in ISOS and p3[2] == 'index.html'
            if not (is_type_idx or is_iso_idx):
                continue
            if not _in(p3[1], a.iso) or (is_type_idx and not _in(p3[2], a.type)):
                continue
            if p3[1] == 'tt':          # Tatar source uses bulek-N.html pages; use `make-indexes` instead
                continue
            if os.path.exists(os.path.join(a.repo, f)) and not a.force:
                continue
            body = read(os.path.join(a.source, f))
            if is_stub(body):
                continue
            done.append(f)
            if not a.dry_run:
                os.makedirs(os.path.dirname(os.path.join(a.repo, f)), exist_ok=True)
                with open(os.path.join(a.repo, f), 'w', encoding='utf-8') as fh:
                    fh.write(rewrite_html(body, f, f, stats, cssroot_ok))

    # assets (css/js/json/images) that live in the migrated level folders
    for (iso, ty, lv) in sorted(folders):
        for f in git_files(a.source, f'manuals/{iso}/{ty}/{lv}'):
            if f.endswith(('.html', '.md')) or '/_schema/' in f:
                continue
            dst = dest_of(f)
            if dst and not os.path.exists(os.path.join(a.repo, dst)):
                asset_copied.append(dst)
                if not a.dry_run:
                    os.makedirs(os.path.dirname(os.path.join(a.repo, dst)), exist_ok=True)
                    shutil.copy2(os.path.join(a.source, f), os.path.join(a.repo, dst))
    # shared css that manual pages reference but shared/styles lacks
    for name in sorted(CSS_COPY_IF_MISSING):
        srcp = os.path.join(css_src, name)
        if stats['css'] and name not in css_have and os.path.exists(srcp):
            if not a.dry_run:
                os.makedirs(os.path.join(a.repo, 'shared/styles'), exist_ok=True)
                shutil.copy2(srcp, os.path.join(a.repo, 'shared/styles', name))
            asset_copied.append('shared/styles/' + name)

    print(('DRY RUN - ' if a.dry_run else '') + 'migrate summary')
    print(f'  pages created           : {len(done)}')
    print(f'  redirect stubs replaced : {len(replaced)}')
    print(f'  skipped (already real)  : {len(skipped_present)}')
    print(f'  CONFLICTS (dest is real, different name/layout; not overwritten): {len(conflicts)}')
    print(f'  assets copied           : {len(asset_copied)}')
    if stats['depth_fixed'] or stats['typo_fixed']:
        print(f'  source defects repaired : wrong-depth links={stats["depth_fixed"]} .html.html typos={stats["typo_fixed"]}')
    print(f'  links rewritten         : internal={stats["internal"]} shared-css={stats["css"]} absolute-to-COSYlanguages={stats["absolute"]}')
    if stats['absolute_targets']:
        print('  absolute link targets   :', dict(stats['absolute_targets'].most_common()))
    for c in conflicts[:20]:
        print('   conflict:', c)
    # warn about hard-coded paths inside copied JS
    for d in asset_copied:
        if d.endswith('.js') and not a.dry_run:
            js = read(os.path.join(a.repo, d))
            if re.search(r'\.\./\.\./\.\./|/practice/|/css/', js):
                print(f'  WARNING: review hard-coded relative paths in {d}')
    if a.report:
        with open(a.report, 'w') as fh:
            json.dump({'created': done, 'replaced_stubs': replaced, 'skipped': skipped_present,
                       'conflicts': conflicts, 'assets': asset_copied}, fh, indent=1)


# --------------------------------------------------------------------------- verify
def cmd_verify(a):
    root = a.repo
    files = [f for f in git_files(root, 'manuals') + [os.path.relpath(os.path.join(d, x), root).replace(os.sep, '/')
                                                        for d, _, fs in os.walk(os.path.join(root, 'manuals')) for x in fs]
             if f.endswith('.html')]
    files = sorted(set(files))
    if getattr(a, 'fix_stubs', False):
        fixed = 0
        for f in git_files(root, 'manuals'):
            if not f.endswith('.html'):
                continue
            body = read(os.path.join(root, f))
            if not is_stub(body):
                continue
            m_target = re.search(r'url\s*=\s*([^\"\' >]+)', body, re.I)
            if not m_target:
                continue
            target = m_target.group(1)
            pdir = os.path.dirname(f)
            resolved = os.path.normpath(os.path.join(pdir, target)).replace(os.sep, '/')
            if not os.path.exists(os.path.join(root, resolved)):
                iso = f.split('/')[1]
                if target.startswith(f'{iso}/'):
                    new_target = target[len(iso)+1:]
                    resolved2 = os.path.normpath(os.path.join(pdir, new_target)).replace(os.sep, '/')
                    if os.path.exists(os.path.join(root, resolved2)):
                        body2 = body.replace(target, new_target)
                        with open(os.path.join(root, f), 'w', encoding='utf-8') as fh:
                            fh.write(body2)
                        fixed += 1
        print(f'--fix-stubs: repaired {fixed} redirect stubs')
        return cmd_verify(argparse.Namespace(**{**vars(a), 'fix_stubs': False}))

    if getattr(a, 'relink', False):
        relinked = 0
        for f in git_files(root, 'manuals'):
            if not f.endswith('.html'):
                continue
            path_f = os.path.join(root, f)
            body = read(path_f)
            if is_stub(body):
                continue
            pdir = os.path.dirname(f)

            def relink_url(match):
                u = match.group('url').strip()
                if not u or SKIP.match(u):
                    return match.group(0)
                pu = urlsplit(u)
                p = pu.path
                if not p:
                    return match.group(0)
                resolved = os.path.normpath(os.path.join(pdir, p)).replace(os.sep, '/')
                if os.path.exists(os.path.join(root, resolved)) or os.path.exists(os.path.join(root, resolved, 'index.html')):
                    return match.group(0)

                clean = re.sub(r'^(\.\./)+', '', resolved)
                clean_manuals = clean if clean.startswith('manuals/') else ('manuals/' + clean)
                mapped = map_source_target(clean_manuals)
                if mapped and os.path.exists(os.path.join(root, mapped)):
                    new_rel = os.path.relpath(mapped, pdir).replace(os.sep, '/')
                    if pu.query: new_rel += '?' + pu.query
                    if pu.fragment: new_rel += '#' + pu.fragment
                    return f"{match.group('attr')}{match.group('q')}{new_rel}{match.group('q')}"

                top = clean.split('/')[0]
                extra_dirs = {'about', 'apps', 'notebook', 'placement-quiz.html', 'privacy.html'}
                if resolved.startswith('../') or top in ROOT_DIRS or top in extra_dirs:
                    abs_url = SITE + clean + (('?' + pu.query) if pu.query else '') + (('#' + pu.fragment) if pu.fragment else '')
                    return f"{match.group('attr')}{match.group('q')}{abs_url}{match.group('q')}"
                return match.group(0)

            body2 = ATTR.sub(relink_url, body)
            def add_target(m_a):
                tag = m_a.group(0)
                if SITE in tag and not re.search(r'\btarget\s*=', tag):
                    return tag[:-1] + ' target="_blank" rel="noopener">'
                return tag
            body2 = re.sub(r'<a\b[^>]*>', add_target, body2)
            if body2 != body:
                with open(path_f, 'w', encoding='utf-8') as fh:
                    fh.write(body2)
                relinked += 1
        print(f'--relink: rewritten references in {relinked} files')
        return cmd_verify(argparse.Namespace(**{**vars(a), 'relink': False}))

    broken = collections.defaultdict(list)
    n = 0
    for f in files:
        k = classify(f)
        if a.iso or a.type or a.level:
            if not k or not matches(k, a):
                continue
        s = read(os.path.join(root, f))
        if is_stub(s):
            continue
        n += 1
        for m in ATTR.finditer(s):
            u = m.group('url').strip()
            if not u or SKIP.match(u):
                continue
            p = urlsplit(u).path
            if not p:
                continue
            t = os.path.normpath(os.path.join(os.path.dirname(f), p))
            ok = os.path.exists(os.path.join(root, t)) or os.path.exists(os.path.join(root, t, 'index.html'))
            if not ok:
                broken[u].append(f)
    if a.fix:
        by_iso = collections.defaultdict(lambda: collections.defaultdict(list))
        for f in git_files(root, 'manuals'):
            k2 = classify(f)
            if k2 and f.endswith('.html'):
                by_iso[k2[0]][os.path.basename(f)].append(f)
        fixed = 0
        # landing pages manuals/<iso>/index.html that link "<iso>/<type>/index.html" instead of "<type>/index.html"
        for iso in ISOS:
            lp = os.path.join(root, 'manuals', iso, 'index.html')
            if os.path.exists(lp):
                body = read(lp)
                body2 = re.sub(r'''(href\s*=\s*["'])''' + iso + r'''/((?:grammar|vocabulary|communication)/[^"']*)''', r'\1\2', body)
                if body2 != body:
                    with open(lp, 'w', encoding='utf-8') as fh:
                        fh.write(body2)
                    fixed += 1
        for u, fs in list(broken.items()):
            pu = urlsplit(u)
            base = os.path.basename(pu.path)
            if not base.endswith('.html') or base == 'index.html':
                continue
            for f in fs:
                iso = f.split('/')[1]
                cands = by_iso[iso].get(base, [])
                if len(cands) != 1:            # ambiguous or none -> leave for a human
                    continue
                new = os.path.relpath(cands[0], os.path.dirname(f)).replace(os.sep, '/')
                path = os.path.join(root, f)
                body = read(path)
                body2 = re.sub(r'''(\b(?:href|src)\s*=\s*)(["'])''' + re.escape(u) + r'''\2''',
                               lambda m: f'{m.group(1)}{m.group(2)}{new}{("?" + pu.query) if pu.query else ""}{("#" + pu.fragment) if pu.fragment else ""}{m.group(2)}', body)
                if body2 != body:
                    with open(path, 'w', encoding='utf-8') as fh:
                        fh.write(body2)
                    fixed += 1
        print(f'--fix: repaired {fixed} references (unique same-language basename match); re-run verify to see what is left')
        return cmd_verify(argparse.Namespace(**{**vars(a), 'fix': False}))
    pairs = sorted({(f, u) for u, fs in broken.items() for f in fs})
    total = len(pairs)
    print(f'verified {n} real pages; broken relative references: {total} ({len(broken)} distinct targets)')
    for u, fs in sorted(broken.items(), key=lambda kv: -len(kv[1]))[:a.top]:
        print(f'  {len(fs):5d}x  {u}    e.g. {fs[0]}')
    if a.json_out:
        with open(a.json_out, 'w') as fh:
            json.dump(pairs, fh, indent=0)
        print(f'wrote {total} broken (page, target) pairs to {a.json_out}')
    if a.baseline:
        base = {tuple(x) for x in json.load(open(a.baseline))}
        new = [p for p in pairs if tuple(p) not in base]
        print(f'NEW broken references vs baseline: {len(new)}')
        for f, u in new[:a.top]:
            print(f'   NEW  {f}  ->  {u}')
        sys.exit(1 if new else 0)
    sys.exit(1 if total else 0)


LANG_NAMES = {'ba': 'Bashkir', 'br': 'Breton', 'cv': 'Chuvash', 'de': 'German', 'el': 'Greek', 'en': 'English', 'es': 'Spanish',
              'fr': 'French', 'hy': 'Armenian', 'it': 'Italian', 'ka': 'Georgian', 'pt': 'Portuguese', 'ru': 'Russian', 'tt': 'Tatar'}
TYPE_NAMES = {'grammar': 'Grammar', 'vocabulary': 'Vocabulary', 'communication': 'Communication'}
PAGE = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} \u00b7 COSYmanuals</title>
<link rel="stylesheet" href="{up}shared/styles/tokens.css">
<link rel="stylesheet" href="{up}shared/styles/base.css">
<link rel="stylesheet" href="{up}shared/styles/layout.css">
<link rel="stylesheet" href="{up}shared/styles/components.css">
</head>
<body>
<main class="container" style="max-width:720px;margin:2rem auto;padding:0 1rem">
<h1>{title}</h1>
<ul>
{items}
</ul>
</main>
</body>
</html>
'''


def cmd_make_indexes(a):
    """Create manuals/<iso>/<type>/index.html and manuals/<iso>/index.html where missing (never overwrites)."""
    made = []
    for iso in sorted(ISOS):
        isodir = os.path.join(a.repo, 'manuals', iso)
        if not os.path.isdir(isodir):
            continue
        entries = []
        for ty in TYPES:
            tdir = os.path.join(isodir, ty)
            if not os.path.isdir(tdir):
                continue
            levels = sorted(l for l in os.listdir(tdir) if LEVEL_RE.fullmatch(l) and os.path.exists(os.path.join(tdir, l, 'index.html')))
            if not levels:
                continue
            tpath = os.path.join(tdir, 'index.html')
            if not os.path.exists(tpath):
                items = '\n'.join(f'<li><a href="{l}/index.html">{l.upper()}</a></li>' for l in levels)
                with open(tpath, 'w', encoding='utf-8') as fh:
                    fh.write(PAGE.format(title=f'{LANG_NAMES[iso]} {TYPE_NAMES[ty]}', up='../../../', items=items))
                made.append(os.path.relpath(tpath, a.repo))
            entries.append(f'<li><a href="{ty}/index.html">{TYPE_NAMES[ty]}</a></li>')
        hubs = sorted(h for h in os.listdir(isodir) if re.fullmatch(r'index-[a-z0-9-]+\.html', h))
        entries += [f'<li><a href="{h}">Level hub: {h[6:-5].upper()}</a></li>' for h in hubs]
        ipath = os.path.join(isodir, 'index.html')
        if entries and not os.path.exists(ipath):
            with open(ipath, 'w', encoding='utf-8') as fh:
                fh.write(PAGE.format(title=f'{LANG_NAMES[iso]} manuals', up='../../', items='\n'.join(entries)))
            made.append(os.path.relpath(ipath, a.repo))
    print(f'created {len(made)} index pages'); [print('  ', m) for m in made]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    for name, fn in (('audit', cmd_audit), ('migrate', cmd_migrate), ('verify', cmd_verify), ('make-indexes', cmd_make_indexes)):
        p = sub.add_parser(name)
        p.add_argument('--repo', default='.', help='path to the COSYmanuals checkout (default .)')
        if name in ('audit', 'migrate'):
            p.add_argument('--source', required=True, help='path to a COSYlanguages checkout')
        p.add_argument('--iso'); p.add_argument('--type'); p.add_argument('--level')
        if name == 'audit':
            p.add_argument('--out', help='write list of missing source paths'); p.add_argument('--allow-missing', type=int, default=0)
            p.add_argument('--unclassified-out', help='write list of unclassified source files (TSV)')
        if name == 'migrate':
            p.add_argument('--dry-run', action='store_true'); p.add_argument('--force', action='store_true')
            p.add_argument('--indexes', action='store_true', help='also migrate manuals/<iso>/index.html and manuals/<iso>/<type>/index.html if missing')
            p.add_argument('--report', help='write JSON report')
        if name == 'verify':
            p.add_argument('--top', type=int, default=25)
            p.add_argument('--fix', action='store_true', help='auto-repair broken refs that have exactly one same-basename match in the same language')
            p.add_argument('--fix-stubs', action='store_true', help='repair redirect stubs whose target moved one folder down')
            p.add_argument('--relink', action='store_true', help='rewrite COSYlanguages root-path links to absolute URLs and legacy hub names')
            p.add_argument('--json-out', help='write broken (page,target) pairs as JSON')
            p.add_argument('--baseline', help='JSON from an earlier --json-out; exit 1 only for NEW broken references')
        p.set_defaults(fn=fn)
    a = ap.parse_args()
    a.fn(a)


if __name__ == '__main__':
    main()
