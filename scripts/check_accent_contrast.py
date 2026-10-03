#!/usr/bin/env python3
"""
Accent Contrast Checker for COSYmanuals
---------------------------------------
Audits WCAG 2.1 AA text-to-background contrast ratios (>= 4.5:1) for all 14 language
themes defined in `shared/styles/lang-accents.css`.

For each language theme (`[data-lang-theme="<iso>"]`), checks:
  1. White (#ffffff) on --accent
  2. White (#ffffff) on --accent-dark
  3. --accent on White (#ffffff)
  4. --accent-dark on --accent-pale
  5. White (#ffffff) on --accent-700 (color-mix 70% --accent, 30% #000000)
  6. White (#ffffff) on --accent-900 (color-mix 40% --accent, 60% #000000)

Usage:
    python3 scripts/check_accent_contrast.py

Exit Codes:
    0: All theme contrast ratios meet or exceed 4.5:1.
    1: One or more contrast ratios fall below 4.5:1.
"""

import os
import re
import sys


def rel_luminance(r: int, g: int, b: int) -> float:
    """Calculates WCAG 2.1 relative luminance for RGB (0-255)."""
    def srgb_linear(c: float) -> float:
        c_norm = c / 255.0
        return c_norm / 12.92 if c_norm <= 0.04045 else ((c_norm + 0.055) / 1.055) ** 2.4

    r_lin = srgb_linear(r)
    g_lin = srgb_linear(g)
    b_lin = srgb_linear(b)
    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin


def contrast_ratio(rgb1: tuple, rgb2: tuple) -> float:
    """Calculates WCAG 2.1 contrast ratio between two RGB tuples."""
    l1 = rel_luminance(*rgb1)
    l2 = rel_luminance(*rgb2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def parse_hex(hex_str: str) -> tuple:
    """Parses a hex color string into (r, g, b) tuple."""
    h = hex_str.strip().lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def rgb_to_hex(rgb: tuple) -> str:
    """Formats an RGB tuple as hex string."""
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


def mix_colors(rgb_a: tuple, rgb_b: tuple, weight_a: float) -> tuple:
    """Simulates CSS color-mix(in srgb, color_a weight_a%, color_b)."""
    weight_b = 1.0 - weight_a
    r = round(rgb_a[0] * weight_a + rgb_b[0] * weight_b)
    g = round(rgb_a[1] * weight_a + rgb_b[1] * weight_b)
    b = round(rgb_a[2] * weight_a + rgb_b[2] * weight_b)
    return (r, g, b)


def parse_language_themes(css_path: str) -> dict:
    """Parses language themes from lang-accents.css."""
    if not os.path.exists(css_path):
        print(f"Error: Could not find CSS file at {css_path}")
        sys.exit(1)

    with open(css_path, 'r', encoding='utf-8') as f:
        content = f.read()

    theme_blocks = re.findall(r'\[data-lang-theme="([a-z]{2})"\]\s*\{([^}]+)\}', content)
    themes = {}

    for lang, block in theme_blocks:
        accent_m = re.search(r'--accent:\s*(#[0-9a-fA-F]{3,6});', block)
        accent_dark_m = re.search(r'--accent-dark:\s*(#[0-9a-fA-F]{3,6});', block)
        accent_pale_m = re.search(r'--accent-pale:\s*(#[0-9a-fA-F]{3,6});', block)

        if accent_m and accent_dark_m and accent_pale_m:
            themes[lang] = {
                '--accent': accent_m.group(1),
                '--accent-dark': accent_dark_m.group(1),
                '--accent-pale': accent_pale_m.group(1),
            }

    return themes


def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    css_path = os.path.join(repo_root, 'shared', 'styles', 'lang-accents.css')

    themes = parse_language_themes(css_path)
    expected_langs = {'ba', 'br', 'cv', 'de', 'el', 'en', 'es', 'fr', 'hy', 'it', 'ka', 'pt', 'ru', 'tt'}

    missing_langs = expected_langs - set(themes.keys())
    if missing_langs:
        print(f"Error: Missing theme blocks for languages: {sorted(list(missing_langs))}")
        sys.exit(1)

    white = (255, 255, 255)
    black = (0, 0, 0)
    failures = []

    print(f"Auditing contrast ratios for {len(themes)} language themes in {css_path}...\n")

    for lang in sorted(themes.keys()):
        t = themes[lang]
        acc_rgb = parse_hex(t['--accent'])
        dark_rgb = parse_hex(t['--accent-dark'])
        pale_rgb = parse_hex(t['--accent-pale'])

        acc700_rgb = mix_colors(acc_rgb, black, 0.70)
        acc900_rgb = mix_colors(acc_rgb, black, 0.40)

        tests = [
            ("white on --accent", white, acc_rgb),
            ("white on --accent-dark", white, dark_rgb),
            ("--accent on white", acc_rgb, white),
            ("--accent-dark on --accent-pale", dark_rgb, pale_rgb),
            ("white on --accent-700", white, acc700_rgb),
            ("white on --accent-900", white, acc900_rgb),
        ]

        print(f"[{lang.upper()}] Theme:")
        lang_failed = False

        for name, fg_rgb, bg_rgb in tests:
            ratio = contrast_ratio(fg_rgb, bg_rgb)
            status = "PASS" if ratio >= 4.5 else "FAIL"
            print(f"  - {name:<30}: {ratio:>5.2f}:1 [{status}] (FG: {rgb_to_hex(fg_rgb)}, BG: {rgb_to_hex(bg_rgb)})")

            if ratio < 4.5:
                lang_failed = True
                failures.append({
                    'lang': lang,
                    'test': name,
                    'ratio': ratio,
                    'fg': rgb_to_hex(fg_rgb),
                    'bg': rgb_to_hex(bg_rgb),
                })

        if lang_failed:
            print(f"  ❌ Theme {lang} has failing contrast ratios!\n")
        else:
            print(f"  ✅ Theme {lang} passed all contrast checks.\n")

    if failures:
        print("=" * 80)
        print("SUMMARY OF CONTRAST FAILURES (Ratio < 4.5:1):")
        print("-" * 80)
        for f in failures:
            print(f"[{f['lang'].upper()}] {f['test']}: {f['ratio']:.2f}:1 (FG: {f['fg']}, BG: {f['bg']})")
        print("=" * 80)
        sys.exit(1)
    else:
        print("All 14 language themes passed all WCAG AA contrast ratio checks (>= 4.5:1)!")
        sys.exit(0)


if __name__ == '__main__':
    main()
