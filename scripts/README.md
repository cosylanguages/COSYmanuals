# COSYmanuals Maintenance & Verification Scripts

This directory contains automated audit, linting, and utility scripts for maintaining dataset integrity, relative CSS references, and WCAG AA contrast standards across COSYmanuals.

---

## 1. Contrast Checker (`check_contrast.py`)

Audits text-to-background contrast ratios for primary hero elements (`h1` and `.hero-kicker`) across all level index pages (`manuals/*/*/*/index.html`) and marathon index pages (`marathons/**/index.html`).

Uses Playwright with headless Chromium and a local HTTP server (`python -m http.server`) to calculate actual rendered computed styles and WCAG 2.1 relative luminance contrast ratios.

### Prerequisites

```bash
pip install playwright
playwright install chromium
```

### Usage

```bash
python3 scripts/check_contrast.py
```

### Behavior

- Evaluates `h1` and `.hero-kicker` text colors against blended background layers (including CSS gradients and alpha channels).
- Prints a summary table of any elements failing the WCAG AA minimum threshold of **4.5:1**.
- Exits with status code `0` if all elements pass, or `1` if any element fails.

---

## 2. CSS Link Checker (`check_css_links.py`)

Scans all `.html` files in `manuals/` and `marathons/` to ensure all `<link rel="stylesheet" href="...">` target files exist relative to the HTML document's location.

### Usage

```bash
python3 scripts/check_css_links.py
```

### Behavior

- Resolves relative stylesheet paths.
- Exits with status code `0` if all stylesheet references exist, or `1` if broken references are found.
