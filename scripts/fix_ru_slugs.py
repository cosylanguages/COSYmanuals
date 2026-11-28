"""Point Russian links with mixed Cyrillic slugs at the ASCII pages that now exist."""
import glob
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RULES = [
    ('otritsatelnye-mestoimeniya', 'ot-otritsatelnye-mestoimeniya-s-predlogami.html'),
    ('povtoryayushchiesya', 'vidy-glagola-povtoryayushchiesya-deystviya.html'),
    ('повторяющиеся', 'vidy-glagola-povtoryayushchiesya-deystviya.html'),
    ('prichastiya-nastoyashchego', 'deystvitelnye-prichastiya-nastoyashchego-i-proshedshego.html'),
    ('причастия', 'deystvitelnye-prichastiya-nastoyashchego-i-proshedshego.html'),
    ('perenos-v-grammatike', 'metaforicheskiy-perenos-v-grammatike.html'),
    ('перенос', 'metaforicheskiy-perenos-v-grammatike.html'),
    ('smyslovoy-tsentr', 'poryadok-slov-smyslovoy-tsentr.html'),
    ('смысловой', 'poryadok-slov-smyslovoy-tsentr.html'),
]


def main():
    fixed = 0
    for path in glob.glob(os.path.join(ROOT, 'manuals/ru/**/*.html'), recursive=True):
        d = os.path.dirname(path)
        html = open(path, encoding='utf-8').read()
        out = html
        for href in set(re.findall(r'href="([^":]+\.html)"', html)):
            if href.startswith(('http', 'mailto')):
                continue
            if os.path.exists(os.path.normpath(os.path.join(d, href))):
                continue
            for needle, slug in RULES:
                if needle in href:
                    out = out.replace(f'href="{href}"', f'href="{slug}"')
                    fixed += 1
                    break
        if out != html:
            open(path, 'w', encoding='utf-8').write(out)
    print(f'fixed {fixed} links')


if __name__ == '__main__':
    main()
