#!/usr/bin/env python3
"""
Check Accent Contrast Script for COSYmanuals
--------------------------------------------
Computes contrast ratios for all language themes in shared/styles/lang-accents.css:
1. White (#FFFFFF) text on --accent
2. White (#FFFFFF) text on --accent-dark
3. --accent text on White (#FFFFFF)
4. --accent-dark text on --accent-pale

Enforces WCAG AA threshold >= 4.5:1 for normal text.
Reports failures and exits with non-zero status if any contrast check fails.
"""

import re
import sys

def srgb_to_linear(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def relative_luminance(hex_str):
    hex_str = hex_str.strip().lstrip('#')
    if len(hex_str) == 3:
        hex_str = ''.join([c*2 for c in hex_str])
    r, g, b = [int(hex_str[i:i+2], 16) for i in (0, 2, 4)]
    return 0.2126 * srgb_to_linear(r) + 0.7152 * srgb_to_linear(g) + 0.0722 * srgb_to_linear(b)

def contrast_ratio(hex1, hex2):
    l1 = relative_luminance(hex1)
    l2 = relative_luminance(hex2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)

def parse_lang_accents(filepath="shared/styles/lang-accents.css"):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    theme_blocks = re.findall(r'(\[data-lang-theme="([^"]+)"\]|:root)\s*\{([^}]+)\}', content)

    themes = {}
    for selector, lang_code, block in theme_blocks:
        key = lang_code if lang_code else "root"
        acc = re.search(r'--accent:\s*(#[0-9a-fA-F]{3,8})', block)
        dark = re.search(r'--accent-dark:\s*(#[0-9a-fA-F]{3,8})', block)
        pale = re.search(r'--accent-pale:\s*(#[0-9a-fA-F]{3,8})', block)

        if acc and dark and pale:
            themes[key] = {
                "accent": acc.group(1),
                "accent_dark": dark.group(1),
                "accent_pale": pale.group(1)
            }
    return themes

def main():
    themes = parse_lang_accents()
    print(f"Auditing contrast for {len(themes)} language theme blocks...\n")

    threshold = 4.5
    failures = []

    for key, colors in themes.items():
        acc = colors["accent"]
        dark = colors["accent_dark"]
        pale = colors["accent_pale"]

        c1 = contrast_ratio("#FFFFFF", acc)
        c2 = contrast_ratio("#FFFFFF", dark)
        c3 = contrast_ratio(acc, "#FFFFFF")
        c4 = contrast_ratio(dark, pale)

        print(f"[{key.upper()}] accent: {acc}, dark: {dark}, pale: {pale}")
        print(f"  - White on --accent:        {c1:.2f}:1 {'✓' if c1 >= threshold else '✗ FAIL'}")
        print(f"  - White on --accent-dark:   {c2:.2f}:1 {'✓' if c2 >= threshold else '✗ FAIL'}")
        print(f"  - --accent on White:        {c3:.2f}:1 {'✓' if c3 >= threshold else '✗ FAIL'}")
        print(f"  - --accent-dark on pale:    {c4:.2f}:1 {'✓' if c4 >= threshold else '✗ FAIL'}\n")

        if c1 < threshold: failures.append((key, "White on --accent", c1, acc))
        if c2 < threshold: failures.append((key, "White on --accent-dark", c2, dark))
        if c3 < threshold: failures.append((key, "--accent on White", c3, acc))
        if c4 < threshold: failures.append((key, "--accent-dark on --accent-pale", c4, dark))

    if failures:
        print(f"TOTAL FAILURES: {len(failures)}")
        for lang, check, ratio, color in failures:
            print(f"  {lang}: {check} = {ratio:.2f}:1 ({color})")
        sys.exit(1)
    else:
        print("ALL CONTRAST CHECKS PASSED (>= 4.5:1 WCAG AA)!")
        sys.exit(0)

if __name__ == "__main__":
    main()
