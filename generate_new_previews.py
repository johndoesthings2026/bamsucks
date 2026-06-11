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

print("\nDone. Previews now have faithful first-page renders for the newly added documents.")
