import glob
import re

student_files = glob.glob("manuals/**/index.html", recursive=True)

updated_count = 0

for filepath in student_files:
    if filepath == "manuals/founder-portal.html":
        continue

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    # 1. Update eyebrow tag styling
    content = re.sub(
        r'style="background:#e2e8f0; font-size:0\.85rem; padding:4px 10px; border-radius:4px; font-weight:700; display:inline-block; margin-bottom:8px;"',
        'style="background: var(--cosy-manuals-accent-light, #f9edf0); color: var(--cosy-manuals-accent, #6b202b); border: 1px solid var(--cosy-manuals-accent-border, rgba(107, 32, 43, 0.22)); font-size: 0.85rem; padding: 4px 10px; border-radius: 20px; font-weight: 700; display: inline-block; margin-bottom: 8px;"',
        content
    )

    # 2. Update outcome banner border & bg
    content = re.sub(
        r'style="background:#f4fbf7; border-left:4px solid #1c8f56; padding:14px 18px; margin-bottom:24px; border-radius:6px;"',
        'style="background: var(--cosy-color-cream, #fdfcf8); border: 1px solid var(--cosy-color-border, rgba(74, 107, 80, 0.12)); border-left: 4px solid var(--cosy-manuals-accent, #6b202b); padding: 14px 18px; margin-bottom: 24px; border-radius: var(--cosy-radius-sm, 8px);"',
        content
    )

    # 3. Update hardcoded button/card accents (#1c8f56, #2563eb, #4f46e5)
    content = re.sub(
        r'border-top:\s*4px solid #(?:1c8f56|2563eb|4f46e5);',
        'border-top: 4px solid var(--cosy-manuals-accent, #6b202b);',
        content
    )
    content = re.sub(
        r'background:\s*#(?:1c8f56|2563eb|4f46e5);',
        'background: var(--cosy-manuals-accent, #6b202b);',
        content
    )

    # 4. Replace student portal footers
    old_footer_pattern = r'<footer style="text-align:center; color:#94a3b8; font-size:0\.85rem; border-top:1px solid #e2e8f0; padding-top:16px;\s*">\s*&copy; COSYmanuals\. Direct Student Course Resource\.\s*</footer>'
    new_footer = '''<footer class="cosy-ecosystem-footer-note" role="contentinfo" aria-label="COSY Ecosystem Membership">
  <div class="cosy-footer-note-inner">
    <span class="cosy-footer-note-brand">🌐 Part of the COSY Family</span>
    <span class="cosy-footer-note-desc">COSYmanuals · Direct Student Reference Manuals & Coursebooks</span>
  </div>
</footer>'''

    content = re.sub(old_footer_pattern, new_footer, content)

    # Also handle generic main-footer if present
    content = re.sub(
        r'<footer class="main-footer">\s*<p>&copy; COSYlanguages\. Private Manual Resource\.</p>\s*</footer>',
        new_footer,
        content
    )

    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        updated_count += 1

print(f"Updated {updated_count} student landing pages / language index hubs.")
