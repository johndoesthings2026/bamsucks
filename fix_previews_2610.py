import fitz
from pathlib import Path

ROOT = Path(".")
PREVIEWS = ROOT / "previews"
PREVIEWS.mkdir(exist_ok=True)

pdfs = [
    ("Reckless-Ben-Utah-Case-261000376-Docket-Events.pdf", "reckless-ben-utah-case-261000376-docket-events"),
    ("Reckless-Ben-Utah-Case-261000376-Information-and-Indictment.pdf", "reckless-ben-utah-case-261000376-information-and-indictment"),
    ("Reckless-Ben-Utah-Case-261000376-Advisement-of-Rights.pdf", "reckless-ben-utah-case-261000376-advisement-of-rights"),
]

matrix = fitz.Matrix(2, 2)

print("=== Page counts and preview generation for 261000376 ===")
for pdf_name, slug in pdfs:
    pdf_path = ROOT / pdf_name
    if not pdf_path.exists():
        print(f"SKIP: {pdf_name} not found")
        continue
    try:
        doc = fitz.open(pdf_path)
        n_pages = len(doc)
        print(f"{pdf_name}: {n_pages} pages")
        
        out_path = PREVIEWS / f"{slug}-page-1.png"
        if out_path.exists():
            print(f"  preview already exists: {out_path.name}")
        else:
            page = doc[0]
            pix = page.get_pixmap(matrix=matrix)
            pix.save(out_path)
            print(f"  generated preview: {out_path.name} ({pix.width}x{pix.height})")
        doc.close()
    except Exception as e:
        print(f"ERROR for {pdf_name}: {e}")

print("\nDone.")