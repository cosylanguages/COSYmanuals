#!/usr/bin/env python3
"""
Contrast Checker for COSYmanuals
--------------------------------
Audits text-to-background contrast ratios for primary hero elements across
all level index pages (`manuals/*/*/*/index.html`) and marathon index pages (`marathons/**/index.html`).

Uses Playwright with headless Chromium and a temporary local HTTP server (`python -m http.server`)
to evaluate actual rendered computed styles, resolve background gradients/layers with alpha blending,
and calculate WCAG 2.1 relative luminance contrast ratios.

Usage:
    python3 scripts/check_contrast.py

Prerequisites:
    pip install playwright
    playwright install chromium

Exit Codes:
    0: All checked headings and kickers meet or exceed the 4.5:1 WCAG AA contrast ratio.
    1: One or more elements fell below the 4.5:1 WCAG AA contrast ratio.
"""

import glob
import http.server
import os
import re
import socket
import socketserver
import sys
import threading
import time
from playwright.sync_api import sync_playwright


def find_free_port() -> int:
    """Finds an available TCP port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def rel_luminance(r: int, g: int, b: int) -> float:
    """Calculates WCAG 2.1 relative luminance for an RGB tuple (0-255)."""
    def srgb_linear(c: float) -> float:
        c_norm = c / 255.0
        return c_norm / 12.92 if c_norm <= 0.04045 else ((c_norm + 0.055) / 1.055) ** 2.4

    r_lin = srgb_linear(r)
    g_lin = srgb_linear(g)
    b_lin = srgb_linear(b)
    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin


def contrast_ratio(rgb1: tuple, rgb2: tuple) -> float:
    """Calculates WCAG 2.1 contrast ratio between two RGB colors."""
    l1 = rel_luminance(*rgb1)
    l2 = rel_luminance(*rgb2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def parse_css_color(color_str: str) -> tuple:
    """Parses an 'rgb(r, g, b)' or '#hex' string into an (r, g, b) tuple."""
    if not color_str:
        return (255, 255, 255)
    m = re.search(r'rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)', color_str)
    if m:
        return (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    if color_str.startswith('#'):
        h = color_str.lstrip('#')
        if len(h) == 3:
            h = ''.join(c * 2 for c in h)
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    return (255, 255, 255)


# In-browser JavaScript function to compute element foreground and blended background
JS_EVAL = """
() => {
    function parseRgba(str) {
        if (!str) return null;
        const m = str.match(/rgba?\\(\\s*(\\d+)\\s*,\\s*(\\d+)\\s*,\\s*(\\d+)(?:\\s*,\\s*([\\d.]+))?\\s*\\)/);
        if (m) {
            return {
                r: parseInt(m[1]),
                g: parseInt(m[2]),
                b: parseInt(m[3]),
                a: m[4] !== undefined ? parseFloat(m[4]) : 1.0
            };
        }
        return null;
    }

    function getSolidBg(el) {
        let curr = el;
        let layers = [];
        while (curr && curr !== document && curr !== document.documentElement) {
            const style = window.getComputedStyle(curr);
            const bgImg = style.backgroundImage;
            if (bgImg && bgImg !== 'none') {
                const matches = bgImg.match(/rgba?\\([^)]+\\)|#[0-9a-fA-F]{3,8}/g);
                if (matches && matches.length > 0) {
                    const parsed = parseRgba(matches[0]);
                    if (parsed) {
                        layers.push(parsed);
                        if (parsed.a === 1.0) break;
                    }
                }
            }
            const bgColor = style.backgroundColor;
            if (bgColor && bgColor !== 'transparent') {
                const parsed = parseRgba(bgColor);
                if (parsed && parsed.a > 0) {
                    layers.push(parsed);
                    if (parsed.a === 1.0) break;
                }
            }
            curr = curr.parentElement;
        }

        let finalRgb = { r: 255, g: 255, b: 255 };
        for (let i = layers.length - 1; i >= 0; i--) {
            const layer = layers[i];
            finalRgb = {
                r: Math.round(layer.a * layer.r + (1 - layer.a) * finalRgb.r),
                g: Math.round(layer.a * layer.g + (1 - layer.a) * finalRgb.g),
                b: Math.round(layer.a * layer.b + (1 - layer.a) * finalRgb.b)
            };
        }
        return `rgb(${finalRgb.r}, ${finalRgb.g}, ${finalRgb.b})`;
    }

    const h1 = document.querySelector('h1');
    const kicker = document.querySelector('.hero-kicker');

    return {
        h1Color: h1 ? window.getComputedStyle(h1).color : null,
        h1Bg: h1 ? getSolidBg(h1) : null,
        kickerColor: kicker ? window.getComputedStyle(kicker).color : null,
        kickerBg: kicker ? getSolidBg(kicker) : null
    };
}
"""


def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    os.chdir(repo_root)

    manual_pages = sorted(glob.glob('manuals/*/*/*/index.html'))
    marathon_pages = sorted(glob.glob('marathons/**/index.html', recursive=True))
    all_pages = manual_pages + marathon_pages

    if not all_pages:
        print("No index pages found matching manuals/*/*/*/index.html or marathons/**/index.html.")
        sys.exit(0)

    port = find_free_port()
    handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(('127.0.0.1', port), handler)
    server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    server_thread.start()

    failing_items = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            for page_path in all_pages:
                url = f"http://127.0.0.1:{port}/{page_path}"
                page.goto(url)
                styles = page.evaluate(JS_EVAL)

                # Check h1 contrast
                if styles['h1Color']:
                    fg = parse_css_color(styles['h1Color'])
                    bg = parse_css_color(styles['h1Bg'])
                    cr = contrast_ratio(fg, bg)
                    if cr < 4.5:
                        failing_items.append({
                            'path': page_path,
                            'element': 'h1',
                            'contrast': cr,
                            'fg': styles['h1Color'],
                            'bg': styles['h1Bg']
                        })

                # Check .hero-kicker contrast if present
                if styles['kickerColor']:
                    fg = parse_css_color(styles['kickerColor'])
                    bg = parse_css_color(styles['kickerBg'])
                    cr = contrast_ratio(fg, bg)
                    if cr < 4.5:
                        failing_items.append({
                            'path': page_path,
                            'element': '.hero-kicker',
                            'contrast': cr,
                            'fg': styles['kickerColor'],
                            'bg': styles['kickerBg']
                        })

            browser.close()
    finally:
        httpd.shutdown()

    print(f"Checked {len(all_pages)} index pages.")
    print(f"Total elements failing WCAG AA (contrast < 4.5:1): {len(failing_items)}")

    if failing_items:
        print("\n" + "=" * 95)
        print(f"{'PAGE PATH':<50} | {'ELEMENT':<12} | {'CONTRAST':<10} | {'FG COLOR':<18} | {'BG COLOR':<18}")
        print("-" * 95)
        for item in failing_items:
            print(f"{item['path']:<50} | {item['element']:<12} | {item['contrast']:>5.2f}:1     | {item['fg']:<18} | {item['bg']:<18}")
        print("=" * 95)
        sys.exit(1)
    else:
        print("\nAll hero headings and kickers meet or exceed the 4.5:1 WCAG AA contrast threshold!")
        sys.exit(0)


if __name__ == '__main__':
    main()
