import fitz
from pathlib import Path
import sys

ROOT = Path(".")
PREVIEWS = ROOT / "previews"
PREVIEWS.mkdir(exist_ok=True)

# Exact mapping: slug (used for folder + preview name) -> PDF filename on disk
# These are the ones we added from Downloads/utah
mappings = [
    ("bricks-minifigs-v-reckless-ben-exhibit-a-consignment-agreement",
     "Bricks-and-Minifigs-v-Reckless-Ben-Utah-Case-260402353-Exhibit-A-Consignment-Agreement.pdf"),
    ("bricks-minifigs-v-reckless-ben-exhibit-b-sold-sets-mansell-investigation",
     "Bricks-and-Minifigs-v-Reckless-Ben-Utah-Case-260402353-Exhibit-B-Sold-Sets-Mansell-Investigation.pdf"),
    ("bricks-minifigs-v-reckless-ben-exhibit-g-community-note-salem-store",
     "Bricks-and-Minifigs-v-Reckless-Ben-Utah-Case-260402353-Exhibit-G-Community-Note-Salem-Store.pdf"),
    ("bricks-minifigs-v-reckless-ben-exhibit-i-incident-log",
     "Bricks-and-Minifigs-v-Reckless-Ben-Utah-Case-260402353-Exhibit-I-Incident-Log.pdf"),
    ("bricks-minifigs-v-reckless-ben-exhibit-j-notice-trespass",
     "Bricks-and-Minifigs-v-Reckless-Ben-Utah-Case-260402353-Exhibit-J-Notice-Of-Trespass.pdf"),
    ("bricks-minifigs-v-reckless-ben-exhibit-k-threat-email",
     "Bricks-and-Minifigs-v-Reckless-Ben-Utah-Case-260402353-Exhibit-K-Threat-Email.pdf"),
    ("bricks-minifigs-v-reckless-ben-ex-parte-motion-tro-preliminary-injunction",
     "Bricks-and-Minifigs-v-Reckless-Ben-Utah-Case-260402353-Ex-Parte-Motion-TRO-Preliminary-Injunction.pdf"),
    ("bricks-minifigs-v-reckless-ben-tro-entered-june-02-2026",
     "Bricks-and-Minifigs-v-Reckless-Ben-Utah-Case-260402353-Temporary-Restraining-Order-TRO-Entered-June-02-2026.pdf"),
    ("bricks-minifigs-v-reckless-ben-case-proceedings-summary-05-28-2026",
     "Bricks-and-Minifigs-v-Reckless-Ben-Utah-Case-260402353-Case-Proceedings-Summary-05-28-2026.pdf"),
]

matrix = fitz.Matrix(2, 2)  # 2x zoom for clear, usable thumbnails (matches typical existing preview quality)

for slug, pdf_name in mappings:
    pdf_path = ROOT / pdf_name
    out_path = PREVIEWS / f"{slug}-page-1.png"

    if not pdf_path.exists():
        print(f"SKIP: PDF not found -> {pdf_name}")
        continue

    try:
        doc = fitz.open(pdf_path)
        if len(doc) == 0:
            print(f"SKIP: empty PDF -> {pdf_name}")
            doc.close()
            continue

        page = doc[0]
        pix = page.get_pixmap(matrix=matrix)
        pix.save(out_path)
        doc.close()
        print(f"OK: {slug}-page-1.png  (from {pdf_name}, {pix.width}x{pix.height})")
    except Exception as e:
        print(f"ERROR rendering {slug}: {e}")

# === Scalable extension for McNeff (and future) PDFs ===
# Auto-generate for any mcneff-*.pdf that doesn't have a preview yet.
# This makes it easy to keep all pages complete without manual list maintenance.
print("\n=== Auto-generating for McNeff-style PDFs (scalable) ===")
for pdf_path in sorted(ROOT.glob("mcneff-v-mcneff-*.pdf")):
    slug = pdf_path.stem
    out_path = PREVIEWS / f"{slug}-page-1.png"
    if out_path.exists():
        print(f"SKIP (exists): {slug}")
        continue
    try:
        doc = fitz.open(pdf_path)
        if len(doc) == 0:
            print(f"SKIP: empty PDF -> {pdf_path.name}")
            doc.close()
            continue
        page = doc[0]
        pix = page.get_pixmap(matrix=matrix)
        pix.save(out_path)
        doc.close()
        print(f"OK (auto): {slug}-page-1.png  ({pix.width}x{pix.height})")
    except Exception as e:
        print(f"ERROR (auto) {slug}: {e}")

# === Even more general scalable pass: any PDF whose basename matches a reader slug ===
# This covers FDD, UCC, Legally Mine, order-alternative-service, etc. that have
# a matching /slug/index.html but were not in the hardcoded list.
# Uses fuzzy matching: exact stem, or slug contained in pdf name, or key parts match.
print("\n=== General auto pass for any PDF matching a reader slug (fully scalable, fuzzy) ===")
reader_slugs = {p.parent.name for p in ROOT.glob("*/index.html") if (p.parent / "index.html").exists()}
for pdf_path in sorted(ROOT.glob("*.pdf")):
    pdf_stem = pdf_path.stem.lower()
    matched_slug = None
    for slug in reader_slugs:
        slug_l = slug.lower()
        if pdf_stem == slug_l:
            matched_slug = slug
            break
        if slug_l in pdf_stem or pdf_stem in slug_l:
            matched_slug = slug
            break
        # Key parts: e.g. for long "Bricks-...-Order-Granting-Alternative-Service" match short slug
        key_parts = [p for p in slug_l.split('-') if len(p) > 3]
        if key_parts and all(k in pdf_stem for k in key_parts[:3]):  # first few significant words
            matched_slug = slug
            break
    if not matched_slug:
        continue
    slug = matched_slug
    out_path = PREVIEWS / f"{slug}-page-1.png"
    if out_path.exists():
        continue
    try:
        doc = fitz.open(pdf_path)
        if len(doc) == 0:
            print(f"SKIP: empty PDF -> {pdf_path.name}")
            doc.close()
            continue
        page = doc[0]
        pix = page.get_pixmap(matrix=matrix)
        pix.save(out_path)
        doc.close()
        print(f"OK (fuzzy general auto): {slug}-page-1.png  ({pix.width}x{pix.height}) from {pdf_path.name}")
    except Exception as e:
        print(f"ERROR (fuzzy general) {slug}: {e}")

print("\nDone. All targeted previews generated. Run this script again after adding new PDFs or reader pages.")
