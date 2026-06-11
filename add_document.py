#!/usr/bin/env python3
r"""Scaffolding helper for adding a new document to the bamsucks current-site-source archive.

Required deliverable per the approved plan. Stdlib only (pathlib, argparse, textwrap, html).

Usage example (for the current Utah batch or future files; --pdf-name points to the clean name already in the source dir):
  python add_document.py \
    --source "C:\Users\danie\Downloads\utah\Item12_ExhibitJ_NoticeOfTrespass.pdf" \
    --slug "bricks-minifigs-v-reckless-ben-exhibit-j-notice-trespass" \
    --title "Exhibit J - Notice of Trespass, Harassment, and Prohibition" \
    --sub "6L" \
    --date "2025-12 (filed 2026-05-28)" \
    --pages "6" \
    --type "Exhibit - Notice of Trespass (letter)" \
    --doc-source "BAM Franchising, Inc. / Bricks & Minifigs Corporate (exhibit in Case 260402353)" \
    --people "BAM Franchising, Inc. to Benjamin Paul Schneider (Reckless Ben)" \
    --desc "Exhibit J to the complaint in Utah Case No. 260402353: formal notice of trespass, harassment, and prohibition from all Bricks & Minifigs locations directed to Reckless Ben, citing disruptive conduct and prior correspondence." \
    --pdf-name "Bricks-and-Minifigs-v-Reckless-Ben-Utah-Case-260402353-Exhibit-J-Notice-Of-Trespass.pdf"

The script:
- Copies/renames the source PDF to the proper root-level name (or --dry-run).
- Creates slug/ directory + a scaffold index.html (full reader structure + TODO markers for lede/excerpt/facts customization).
- Prints a ready-to-paste <li> catalog block (exact style for group 6).
- Prints reminders for: preview PNG, archive.js GROUP_DATA, sitemap.xml, re-running _build_topic_pages.py.

Never mutates index.html, archive.js, or sitemap.xml itself.
"""

from __future__ import annotations

import argparse
import html
import shutil
import textwrap
from pathlib import Path
from typing import Dict

ROOT = Path(__file__).resolve().parent
PREVIEWS = ROOT / "previews"

# A compact but complete reader scaffold template.
# Adapted from the structure of bricks-minifigs-v-reckless-ben-tro/index.html and the police example.
# Keep the shared inline <style> verbatim for consistency.
READER_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} | Notice</title>
  <meta name="description" content="{description}">
  <meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large">
  <meta name="theme-color" content="#ffffff">
  <link rel="canonical" href="https://bamsucks.com/{slug}/">
  <link rel="icon" href="/favicon.ico" sizes="any">
  <link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png">
  <link rel="icon" href="/favicon-16.png" sizes="16x16" type="image/png">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <link rel="manifest" href="/site.webmanifest">
  <meta property="og:site_name" content="Bricks and Minifigs Sucks">
  <meta property="og:title" content="{og_title}">
  <meta property="og:description" content="{description}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="https://bamsucks.com/{slug}/">
  <meta property="og:image" content="/previews/{slug}-page-1.png">
  <meta property="og:image:alt" content="First page preview of {title}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{og_title}">
  <meta name="twitter:description" content="{description}">
  <meta name="twitter:image" content="/previews/{slug}-page-1.png">
  <script src="/archive.js?v=pattern26" defer></script>
  <style>
    :root {{
      color-scheme: light;
      --ink: #1c1c1c;
      --muted: #555;
      --line: #d7d7d7;
      --link: #153e75;
      --link-hover: #0f2d55;
      --bg-soft: #f8f8f8;
      --max: 1280px;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: #fff;
      color: var(--ink);
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.55;
      overflow-x: hidden;
      position: relative;
    }}
    main {{
      width: min(calc(100% - 32px), var(--max));
      margin: 0 auto;
      padding: 20px 0 32px;
      position: relative;
      z-index: 1;
    }}
    h1, h2 {{ line-height: 1.15; margin: 0; }}
    h1 {{ font-size: 1.85rem; margin-bottom: 6px; }}
    h2 {{
      font-size: 1.05rem;
      margin: 0 0 10px;
      padding-bottom: 6px;
      border-bottom: 1px solid var(--line);
    }}
    p {{ margin: 0 0 14px; }}
    a {{ color: var(--link); text-underline-offset: 2px; }}
    a:hover, a:focus {{ color: var(--link-hover); }}
    .lede {{ max-width: 920px; color: var(--muted); font-size: 1rem; }}
    .top-links {{
      display: flex;
      flex-wrap: wrap;
      gap: 16px;
      margin: 12px 0 18px;
      padding-bottom: 12px;
      border-bottom: 1px solid var(--line);
      font-weight: 700;
    }}
    .reader {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) 330px;
      gap: 18px;
      align-items: start;
    }}
    .pdf-pane,
    .side {{
      border: 1px solid var(--line);
      background: #fff;
    }}
    .side {{
      padding: 14px;
      position: sticky;
      top: 14px;
    }}
    .doc-preview {{
      display: block;
      width: 100%;
      max-height: 280px;
      object-fit: contain;
      margin: 0 0 12px;
      border: 1px solid var(--line);
      background: var(--bg-soft);
    }}
    .facts {{
      display: grid;
      gap: 8px;
      margin: 12px 0 0;
    }}
    .fact {{
      border: 1px solid var(--line);
      padding: 9px;
      background: #fff;
    }}
    .fact span {{
      display: block;
      color: var(--muted);
      font-size: 0.9rem;
      margin-bottom: 3px;
    }}
    .viewer {{
      width: 100%;
      height: calc(100vh - 150px);
      min-height: 700px;
      border: 0;
      background: var(--bg-soft);
      display: block;
    }}
    .actions {{
      display: flex;
      flex-direction: column;
      gap: 14px;
      margin: 14px 0;
      font-weight: 700;
    }}
    .actions a {{
      border: 1px solid var(--line);
      padding: 9px 10px;
      background: var(--bg-soft);
    }}
    details {{
      border: 1px solid var(--line);
      padding: 10px;
      background: #fff;
      margin-top: 12px;
    }}
    summary {{
      cursor: pointer;
      font-weight: 700;
      color: var(--link);
    }}
    .text-block {{
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      margin-top: 14px;
      color: var(--ink);
      font-size: 0.9rem;
      max-height: 380px;
      overflow: auto;
    }}
    .notice {{
      margin-top: 30px;
      padding-top: 16px;
      border-top: 1px solid var(--line);
      color: var(--muted);
      font-size: 0.96rem;
    }}
    footer {{ margin-top: 22px; color: var(--muted); font-size: 0.94rem; }}
    @media (max-width: 860px) {{
      main {{ width: min(calc(100% - 24px), var(--max)); padding-top: 24px; }}
      h1 {{ font-size: 1.85rem; }}
      .reader {{ grid-template-columns: 1fr; }}
      .side {{ position: static; }}
      .viewer {{ height: 72vh; min-height: 520px; }}
    }}
  </style>
  <script type="application/ld+json">{{"@context":"https://schema.org","@graph":[{{"@type":"WebPage","@id":"https://bamsucks.com/{slug}/#webpage","url":"https://bamsucks.com/{slug}/","name":{json_name},"description":{json_desc},"isPartOf":{{"@id":"https://bamsucks.com/#website"}},"breadcrumb":{{"@id":"https://bamsucks.com/{slug}/#breadcrumb"}},"primaryEntity":{{"@id":"https://bamsucks.com/{slug}/#document"}},"image":"/previews/{slug}-page-1.png","inLanguage":"en-US","dateModified":"2026-06-10"}},{{"@type":"DigitalDocument","@id":"https://bamsucks.com/{slug}/#document","name":{json_name},"description":{json_desc},"url":"https://bamsucks.com/{slug}/","encodingFormat":"text/html","isBasedOn":"https://bamsucks.com/{pdf_name}","image":"/previews/{slug}-page-1.png","about":[{{"@type":"Thing","name":"Bricks and Minifigs dispute"}},{{"@type":"Thing","name":"Utah court filing"}}],"mentions":[{{"@type":"Person","name":"Benjamin Paul Schneider / Reckless Ben"}}],"inLanguage":"en-US","dateModified":"2026-06-10"}},{{"@type":"BreadcrumbList","@id":"https://bamsucks.com/{slug}/#breadcrumb","itemListElement":[{{"@type":"ListItem","position":1,"name":"Home","item":"https://bamsucks.com/"}},{{"@type":"ListItem","position":2,"name":{json_name},"item":"https://bamsucks.com/{slug}/"}}]}}]}}</script>
</head>
<body>
  <main>
    <header>
      <h1>{h1}</h1>
      <p class="lede">{lede}</p>
      <nav class="top-links" aria-label="Document navigation">
        <a href="/{pdf_name}" target="_blank" rel="noopener noreferrer">Open PDF</a>
      </nav>
    </header>

    <div class="reader">
      <section id="pdf" class="pdf-pane" aria-label="Original PDF">
        <iframe class="viewer" src="/{pdf_name}" title="{title} PDF"></iframe>
      </section>

      <aside class="side" aria-label="Document details">
        <h2>Details</h2>
        <img class="doc-preview" src="/previews/{slug}-page-1.png" alt="First page preview of {title}" loading="lazy">
        <!-- TODO: customize this short contextual paragraph (1-2 sentences). Case number is included for SEO. -->
        <p>This document is part of Utah Case No. 260402353 filings in the Bricks and Minifigs v. Reckless Ben civil case (Fourth Judicial District Court, Utah County).</p>
        <div class="actions">
          <a href="/{pdf_name}" target="_blank" rel="noopener noreferrer">Open PDF</a>
          <a href="/{pdf_name}" download>Download PDF</a>
        </div>
        <div class="facts">
        <div class="fact"><span>Document type</span>{doc_type}</div>
        <div class="fact"><span>Date</span>{date}</div>
        <div class="fact"><span>Source</span>{source}</div>
        <div class="fact"><span>People / entities</span>{people}</div>
        <div class="fact"><span>Pages</span>{pages} pages</div>
        <div class="fact"><span>Original file</span>{pdf_name}</div>
        </div>
        <details>
          <summary>Searchable text</summary>
          <p>Clean extracted text or OCR excerpt. Sensitive OCR fields are redacted or omitted.</p>
          <!-- TODO: paste cleaned first-page(s) excerpt here with ===== PAGE X ===== markers and redactions as needed -->
          <div class="text-block">TODO: Insert excerpt from PDF text extraction (first 1-3 pages recommended). Use the format from existing readers (e.g. police or TRO examples).</div>
        </details>
      </aside>
    </div>

    <section class="notice">
      <p>The complaint and police documents contain allegations and records, not final findings unless a court order says so. Read each source according to its own terms.</p>
    </section>

    <footer>
      <p><a href="/sitemap.xml">Sitemap</a> - <a href="/robots.txt">Robots</a></p>
    </footer>
  </main>
<script defer src="https://static.cloudflareinsights.com/beacon.min.js/v833ccba57c9e4d2798f2e76cebdd09a11778172276447" integrity="sha512-57MDmcccJXYtNnH+ZiBwzC4jb2rvgVCEokYN+L/nLlmO8rfYT/gIpW2A569iJ/3b+0UEasghjuZH/ma3wIs/EQ==" data-cf-beacon='{{"version":"2024.11.0","token":"1103e50e2a60420388bbab2b52f5986f","r":1,"server_timing":{{"name":{{"cfCacheStatus":true,"cfEdge":true,"cfExtPri":true,"cfL4":true,"cfOrigin":true,"cfSpeedBrain":true}},"location_startswith":null}}}}' crossorigin="anonymous"></script>
</body>
</html>
"""

def json_str(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'

def build_catalog_li(args: argparse.Namespace, pdf_name: str) -> str:
    sub = args.sub
    title = args.title
    desc = args.desc
    meta = f"Utah Case No. 260402353 - {args.pages}-page PDF"
    # Use hyphenated id (compatible with existing entries like "ex-parte-order")
    item_id = args.slug
    return f"""              <li id="{item_id}">
                <span class="sub-number">{sub}</span>
                <div>
            <a class="doc-title" href="/{args.slug}/">{html.escape(title)}</a>
            <div class="doc-meta">{html.escape(meta)}</div>
            <p class="doc-desc">{html.escape(desc)}</p>
            <div class="doc-actions">
              <a href="/{args.slug}/">Read page</a>
              <a href="/{pdf_name}" target="_blank" rel="noopener noreferrer">Open PDF</a>
              <a href="/{pdf_name}" download>Download</a>
            </div>
          </div>
              </li>
"""

def main() -> None:
    p = argparse.ArgumentParser(
        description="Scaffold a new document entry for the bamsucks archive (group 6 / Utah case by default)."
    )
    p.add_argument("--source", required=True, help="Path to the raw PDF in Downloads/utah (or elsewhere)")
    p.add_argument("--slug", required=True, help="Kebab-case slug for folder + URLs (e.g. bricks-minifigs-v-reckless-ben-exhibit-j-notice-trespass)")
    p.add_argument("--title", required=True, help="Human title for h1 / catalog (e.g. Exhibit J - Notice of Trespass, Harassment, and Prohibition)")
    p.add_argument("--sub", required=True, help="Sub-number in group, e.g. 6H")
    p.add_argument("--date", required=True, help="Document date string for facts (e.g. 2025-12 (filed 2026-05-28) or June 02, 2026)")
    p.add_argument("--pages", required=True, help="Page count string (e.g. 6 or 24)")
    p.add_argument("--type", dest="doc_type", required=True, help="Document type for facts sidebar (e.g. Exhibit - Notice of Trespass (letter))")
    p.add_argument("--doc-source", dest="doc_source", required=True, help="Source string for facts (e.g. Fourth Judicial District Court... or BAM Franchising...)")
    p.add_argument("--people", required=True, help="People/entities string for facts")
    p.add_argument("--desc", required=True, help="Short catalog description (also used for lede starter and meta). Case number will be emphasized for SEO.")
    p.add_argument("--pdf-name", dest="pdf_name", default=None, help="Exact root PDF filename to use in links/iframe (e.g. the clean name already copied to the source dir). If omitted, a name is derived.")
    p.add_argument("--dry-run", action="store_true", help="Print actions and snippets but do not copy files or create dirs")
    p.add_argument("--target-dir", default=str(ROOT), help="Override target current-site-source root (for testing)")

    args = p.parse_args()

    target_root = Path(args.target_dir).resolve()
    source = Path(args.source).expanduser().resolve()
    if not source.exists():
        p.error(f"Source not found: {source}")

    # SEO: always emphasize the case number that people search for
    case_label = "Utah Case No. 260402353"
    case_no = "260402353"
    base_desc = args.desc
    if case_no not in base_desc and case_no not in args.title:
        seo_desc = f"{case_label}: {base_desc}"
    else:
        seo_desc = base_desc

    # Determine exact PDF filename for all references (links, iframe, isBasedOn, sitemap, etc.)
    if args.pdf_name:
        dest_pdf_name = args.pdf_name
    else:
        # Derive a clean name (single .pdf)
        dest_pdf_name = args.slug.replace("bricks-minifigs-v-reckless-ben-", "Bricks-and-Minifigs-v-Reckless-Ben-Utah-Case-260402353-")
        if not dest_pdf_name.lower().endswith('.pdf'):
            dest_pdf_name += '.pdf'
        # Fallback cleaner for exhibit/motion/tro
        if "exhibit" in args.slug.lower() or "motion" in args.slug.lower() or "tro" in args.slug.lower():
            clean = args.title.replace(" ", "-").replace(",", "").replace("(", "").replace(")", "").replace("/", "-")
            dest_pdf_name = "-".join(w for w in clean.split("-") if w)
            if not dest_pdf_name.lower().endswith('.pdf'):
                dest_pdf_name += '.pdf'

    slug_dir = target_root / args.slug
    preview_name = f"{args.slug}-page-1.png"

    print("=== bamsucks add_document (required scaffolder) ===")
    print(f"Source: {source}")
    print(f"Dest PDF name (root): {dest_pdf_name}")
    print(f"Slug / folder: {args.slug}")
    print(f"Target root: {target_root}")
    print(f"Dry run: {args.dry_run}")
    print()

    if not args.dry_run:
        slug_dir.mkdir(parents=True, exist_ok=True)
        dest_pdf = target_root / dest_pdf_name
        if dest_pdf.exists():
            print(f"WARNING: {dest_pdf} already exists — not overwriting (using existing for references).")
        else:
            shutil.copy2(source, dest_pdf)
            print(f"Copied PDF -> {dest_pdf}")
        # Write scaffold reader
        reader_path = slug_dir / "index.html"
        facts_html = f"""        <div class="fact"><span>Document type</span>{html.escape(args.doc_type)}</div>
        <div class="fact"><span>Date</span>{html.escape(args.date)}</div>
        <div class="fact"><span>Source</span>{html.escape(args.doc_source)}</div>
        <div class="fact"><span>People / entities</span>{html.escape(args.people)}</div>
        <div class="fact"><span>Pages</span>{html.escape(args.pages)} pages</div>
        <div class="fact"><span>Original file</span>{html.escape(dest_pdf_name)}</div>"""
        # SEO-optimized lede starter (case number emphasized)
        lede = seo_desc[:320] + ("..." if len(seo_desc) > 320 else "")
        rendered = READER_TEMPLATE.format(
            title=html.escape(args.title),
            description=html.escape(seo_desc),
            og_title=html.escape(args.title),
            h1=html.escape(args.title),
            lede=html.escape(lede),
            slug=args.slug,
            pdf_name=html.escape(dest_pdf_name),
            doc_type=html.escape(args.doc_type),
            date=html.escape(args.date),
            source=html.escape(args.doc_source),
            people=html.escape(args.people),
            pages=html.escape(args.pages),
            json_name=json_str(args.title),
            json_desc=json_str(seo_desc),
            facts_html=facts_html,
        )
        facts_block = f"""        <div class="facts">
{facts_html}
        </div>"""
        rendered = rendered.replace(
            """        <div class="facts">
        <div class="fact"><span>Document type</span>TODO</div>
        <div class="fact"><span>Date</span>TODO</div>
        <div class="fact"><span>Source</span>TODO</div>
        <div class="fact"><span>People / entities</span>TODO</div>
        <div class="fact"><span>Pages</span>TODO pages</div>
        <div class="fact"><span>Original file</span>TODO</div>
        </div>""",
            facts_block
        )
        reader_path.write_text(rendered, encoding="utf-8", newline="\n")
        print(f"Wrote reader scaffold -> {reader_path}")
        print(f"Reminder: create preview -> {PREVIEWS / preview_name} (screenshot page 1 of the PDF)")
    else:
        print("[dry-run] Would copy PDF and write slug/index.html scaffold + print snippets.")

    # Always print the catalog block (even in dry-run)
    catalog_li = build_catalog_li(args, dest_pdf_name)
    print("\n=== READY-TO-PASTE CATALOG <li> (paste inside the group 6 <ol class=\"subdocs\">) ===")
    print(catalog_li)

    print("\n=== REMINDERS ===")
    print(f"1. Manually create the preview PNG: {PREVIEWS / preview_name}")
    print("2. Edit archive.js → add to GROUP_DATA['case-260402353'].items :")
    print(f"   {{num: \"{args.sub}\", slug: \"{args.slug}\", title: \"{args.title}\"}},")
    print("3. Edit sitemap.xml → add <url> for /" + args.slug + "/ (with <image:image>) and /" + dest_pdf_name)
    print("4. (After pasting the <li> into index.html) run:  python _build_topic_pages.py")
    print("5. Fill the TODO markers in the new reader (lede paragraph, text-block excerpt, any extra sidebar p).")
    print("6. Test locally with serve-current.bat (or python -m http.server 8080 from the source dir).")
    print("\nDone. The script performed no mutations to index.html, archive.js, or sitemap.xml.")

if __name__ == "__main__":
    main()