# Access Control Architecture & Roster Specification

## 🔒 Overview & Access Model Principles

`COSYmanuals` serves as a private, direct-link repository for language course manuals. Access control must remain **100% free and sustainable** with **zero personal data harvesting**.

---

## 🛠️ Architecture Trade-Offs for Founder Decision

GitHub repo permissions operate at the repository boundary; true path-scoped read ACLs on a single private repository are not supported natively by GitHub. Therefore, the founder needs to weigh two free-tier access options:

### **Option (a): Single Shared Private Repository with Founder Manual Review**
- **Structure:** All manuals reside in this single private `COSYmanuals` repository.
- **Access Flow:** Teachers and students are invited as Read-Only Collaborators or access via direct links.
- **Pros:** Minimal repository sprawl; single place to manage changes and updates.
- **Cons:** Teachers have technical repository read access across languages; founder manually manages collaborators per request.

### **Option (b): Language-Scoped Private Repositories** *(Implemented Default Architecture)*
- **Structure:** Split manuals into target language repositories (e.g. `COSYmanuals-en`, `COSYmanuals-fr`, `COSYmanuals-ru`).
- **Access Flow:** A teacher for English is added as a collaborator **only** to `COSYmanuals-en`.
- **Pros:** Strict language boundary isolation matching the access requirement.
- **Cons:** Managing updates across separate repos requires workflow synchronization scripts.

---

## 🛡️ Optional Rendered Site Gate (Cloudflare Workers / GitHub OAuth Device Flow)

If a rendered public-facing or web-hosted version (GitHub Pages) is desired:
1. **GitHub OAuth Device Flow / App:** Users authenticate via GitHub without requiring password storage.
2. **Cloudflare Worker Gate (Free Tier):** A small Cloudflare Worker checks the logged-in user against `config/roster.example.json`.
3. **No Database Required:** Access logic reads from the roster file stored directly in the repository.

---

## 🙈 Zero Data Harvesting Guarantee

The roster schema (`config/roster.example.json`) stores only:
- GitHub usernames (or opaque student IDs)
- Assigned language codes and course levels

No emails, full names, IP addresses, or personal tracking metadata are stored or processed.

---

## 🧑‍🏫 Student Direct-Link Distribution
Teachers share direct markdown/web links to assigned level manuals with contracted students. Students do not need repository write access.
