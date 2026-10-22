# Contributing to COSYmanuals

## Repository boundaries

- Public catalog metadata and open schemas may be committed.
- Full gated manual body text belongs in the protected Supabase `manual_content` table, not in Git history.
- Local Markdown drafts belong in the gitignored `drafts/` directory.
- Curriculum and vocabulary mirrors are read-only. Propose changes in the canonical source repository and sync them here after approval.
- Never commit credentials, tokens, learner data, or local environment files.

## Local requirements

Use a supported Node.js LTS release with built-in `node:test` support. No third-party package installation is required for the validation scripts in this repository.

## Validation commands

Run these from the repository root:

```bash
node scripts/validate-catalog.mjs
node --test
node scripts/check-internal-links.mjs manuals
```

The link checker initially runs in report-only mode so legacy link debt can be measured without hiding the baseline. After existing findings are resolved, use `--strict` in CI to fail on broken local links and assets.

## Manual content review checklist

For each manual change:

- Confirm the target CEFR level and prerequisites.
- State learning outcomes in learner-friendly language.
- Explain rules accurately, then show natural examples and common errors.
- Include meaningful practice with answers or feedback where appropriate.
- Use consistent terminology, language tags, heading hierarchy, and navigation.
- Ensure links work, controls are keyboard accessible, and interactive content has a non-interactive alternative.
- Check mobile layout, contrast, focus visibility, and zoom/reflow.
- Check print styles: legible type, adequate margins, no clipped tables, no dark backgrounds that waste ink, and no navigation-only controls in the printed output.
- Ask a proficient speaker/teacher to review language accuracy before claiming pedagogical approval.

## Publishing gated content

1. Confirm the matching catalog metadata exists and is correct.
2. Review the draft locally and run validation.
3. Run the publisher in dry-run mode first.
4. Only then, in an approved trusted environment, publish with the required Supabase credentials.
5. Verify the published manual through a test account and review the access-control model in `SECURITY_REVIEW.md`.

Do not publish gated body text as part of a code review or pull request.
