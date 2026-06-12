import re
from pathlib import Path
import glob

root = Path(".")
print("=== COMPREHENSIVE AUDIT FOR BROKEN READER PAGES ===\n")

# 1. Collect slugs from homepage (index.html) - li ids and Read page hrefs
idx = (root / "index.html").read_text(encoding="utf-8", errors="ignore")
homepage_slugs = set(re.findall(r'<li[^>]*id=["\']?([a-z0-9-]+(?:-exhibit-|-doc-|-cover-sheet|-order-|-filing-)[^"\'>]*)["\']?', idx, re.I))
homepage_slugs |= set(re.findall(r'href=["\']?/( [a-z0-9-]+ (?:-exhibit-|-doc-|-cover-sheet|-order-|-filing-)[a-z0-9-]* )/["\']?[^>]*>Read page', idx, re.I))
homepage_slugs = {s.strip() for s in homepage_slugs if s.strip()}

# 2. From archive.js GROUP_DATA
js = (root / "archive.js").read_text(encoding="utf-8", errors="ignore")
group_slugs = set(re.findall(r'slug:\s*["\']([^"\']+)', js))
group_slugs = {s for s in group_slugs if not s.endswith('.pdf')}

# 3. From sitemap (reader urls, not pdfs)
smap = (root / "sitemap.xml").read_text(encoding="utf-8", errors="ignore")
sitemap_slugs = set(re.findall(r'<loc>https://bamsucks.com/([a-z0-9-]+(?:-exhibit-|-doc-|-cover-sheet|-order-|-filing-)[^<]*)/</loc>', smap, re.I))

# 4. From topics pages
topics_slugs = set()
for t in glob.glob("topics/**/*.html", recursive=True):
    tc = Path(t).read_text(encoding="utf-8", errors="ignore")
    topics_slugs |= set(re.findall(r'href=["\']?/( [a-z0-9-]+ (?:-exhibit-|-doc-|-cover-sheet|-order-|-filing-)[a-z0-9-]* )/["\']?[^>]*>Read page', tc, re.I))

all_slugs = sorted(homepage_slugs | group_slugs | sitemap_slugs | topics_slugs)
print(f"Total unique potential reader slugs found across sources: {len(all_slugs)}\n")

missing_reader = []
missing_preview = []
pdf_link_issues = []
sitemap_issues = []

for slug in all_slugs:
    reader_path = root / slug / "index.html"
    preview_path = root / "previews" / f"{slug}-page-1.png"

    has_reader = reader_path.exists()
    has_preview = preview_path.exists()

    if not has_reader:
        missing_reader.append(slug)
    if not has_preview:
        missing_preview.append(slug)

    # If has reader, check the PDF it references exists
    if has_reader:
        rcontent = reader_path.read_text(encoding="utf-8", errors="ignore")
        pdf_refs = re.findall(r'href=["\']?/( [^"\'>]+\.pdf )["\']?', rcontent, re.I)
        pdf_refs += re.findall(r'src=["\']?/( [^"\'>]+\.pdf )["\']?', rcontent, re.I)
        for pref in set(pdf_refs):
            p = pref.strip()
            if not (root / p).exists():
                pdf_link_issues.append((slug, p))

# Check sitemap for McNeff or recent ones with bad image titles (from previous issues)
bad_title_pattern = r'<image:title>Legally Mine|unauthorized practice'
if re.search(bad_title_pattern, smap, re.I):
    sitemap_issues.append("Some sitemap image:title still have wrong copy-paste (e.g. Legally Mine for McNeff)")

print("=== MISSING READER index.html (folder exists in listings but no /slug/index.html) ===")
if missing_reader:
    for m in missing_reader:
        print(f"  MISSING READER: {m}/index.html")
else:
    print("  None found. Good.")

print(f"\n=== MISSING PREVIEW PNGs (reader exists but no sidebar/details image) ===")
if missing_preview:
    for m in missing_preview[:20]:
        print(f"  MISSING PREVIEW: previews/{m}-page-1.png")
    if len(missing_preview) > 20:
        print(f"  ... and {len(missing_preview)-20} more")
else:
    print("  None found. Good.")

print(f"\n=== PDF LINK ISSUES (reader references a PDF that doesn't exist on disk) ===")
if pdf_link_issues:
    for slug, pdf in pdf_link_issues[:10]:
        print(f"  {slug} -> {pdf}")
else:
    print("  None found. Good.")

print(f"\n=== SITEMAP ISSUES ===")
if sitemap_issues:
    for i in sitemap_issues:
        print(f"  {i}")
else:
    print("  None obvious from quick scan.")

print(f"\n=== SUMMARY ===")
print(f"Missing readers: {len(missing_reader)}")
print(f"Missing previews: {len(missing_preview)}")
print(f"PDF link problems: {len(pdf_link_issues)}")
print("Run this audit again after fixes. Use generate_new_previews.py for missing PNGs (it now auto-handles McNeff).")
print("For missing readers, use add_document.py or copy a template from a working one (e.g. a similar McNeff or BAM exhibit).")
