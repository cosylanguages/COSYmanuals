import glob
import re

teacher_files = glob.glob("manuals/*/teacher-access.html")

for filepath in teacher_files:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

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

    # 3. Update course track card borders
    content = re.sub(
        r'border-left:4px solid #[0-9a-fA-F]{6};',
        'border-left: 4px solid var(--cosy-manuals-accent, #6b202b);',
        content
    )

    # 4. Update student manual button backgrounds (#1c8f56)
    content = re.sub(
        r'background:#1c8f56;',
        'background: var(--cosy-manuals-accent, #6b202b);',
        content
    )

    # 5. Replace footer tag
    old_footer_pattern = r'<footer style="text-align:center; color:#94a3b8; font-size:0\.85rem; border-top:1px solid #e2e8f0; padding-top:16px; margin-top:24px;">\s*&copy; COSYmanuals\. Private Teacher Access Resource\.\s*</footer>'
    new_footer = '''<footer class="cosy-ecosystem-footer-note" role="contentinfo" aria-label="COSY Ecosystem Membership">
  <div class="cosy-footer-note-inner">
    <span class="cosy-footer-note-brand">🌐 Part of the COSY Family</span>
    <span class="cosy-footer-note-desc">COSYmanuals · Private Teacher Access Portal for Online & Offline Lessons</span>
  </div>
</footer>'''

    content = re.sub(old_footer_pattern, new_footer, content)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

print(f"Updated {len(teacher_files)} teacher access portals.")
