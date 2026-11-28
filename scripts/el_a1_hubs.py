"""Link every Greek A1 topic page from a part hub."""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, 'manuals/el/grammar/a1')

ADD = {
    'meros-2': ['arnitikes-protaseis-den-vs-min', 'ypotaktiki-me-na', 'part-1-building-blocks'],
    'meros-4': ['aitiologikoi-apotelesmatikoi-syndesmoi'],
}


def title_of(slug):
    html = open(os.path.join(BASE, 'topics', slug + '.html'), encoding='utf-8').read()
    m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.S)
    return re.sub(r'\s+', ' ', re.sub('<[^>]+>', '', m.group(1))).strip() if m else slug


def main():
    for hub, slugs in ADD.items():
        path = os.path.join(BASE, hub + '.html')
        html = open(path, encoding='utf-8').read()
        linked = set(re.findall(r'topics/([a-z0-9-]+)\.html', html))
        cards = ''.join(f'    <li><a href="topics/{s}.html">{title_of(s)}</a></li>\n'
                        for s in slugs if s not in linked)
        if not cards:
            continue
        if '</ul>' in html:
            html = html.replace('</ul>', cards + '</ul>', 1)
        else:
            html = html.replace('</main>', f'<ul>\n{cards}</ul>\n</main>', 1)
        open(path, 'w', encoding='utf-8').write(html)


if __name__ == '__main__':
    main()
