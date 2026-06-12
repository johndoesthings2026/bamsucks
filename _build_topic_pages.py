#!/usr/bin/env python3
"""Generate SEO topic hub pages from index.html archive groups."""

from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "index.html"
TOPICS_DIR = ROOT / "topics"

SMALL_CLAIMS_CONTEXT = (
    'YouTuber Benjamin Paul Schneider ("Reckless Ben") and the Mansell family successfully won '
    "a series of small claims court lawsuits in Oregon against the Keizer/Salem franchise of "
    "Bricks and Minifigs. Because Oregon caps small claims cases at $10,000 per filing, the group "
    "reportedly split the claim and won multiple parallel $10,000 suits to recoup the value of a "
    "$200,000 Star Wars LEGO collection that they alleged was wrongfully withheld during a store "
    "ownership transition."
)

UTAH_COMPLAINT_CONTEXT = (
    "In late 2023, the original franchise owner of the Salem–Keizer, Oregon store, Chrystal Law/Gorman, "
    "entered into a consignment agreement with Bryan Mansell. Mansell placed his 83-year-old father's "
    "collection—comprising roughly 780 sets and 1,200 minifigures—on display and up for sale at the store "
    "to help fund his grandchildren's college education."
)

NAV = [
    ("bricks-minifigs-franchise-documents", "Franchise FDD"),
    ("legally-mine", "Ammon McNeff / Legally Mine"),
    ("bricks-minifigs-financing-records", "Financing records"),
    ("chrystal-law-bricks-minifigs", "Chrystal Law"),
    ("american-fork-police-reckless-ben", "AFPD & Reckless Ben"),
    ("reckless-ben-utah-lawsuit", "Reckless Ben Utah lawsuit"),
    ("reckless-ben-small-claims", "Reckless Ben small claims"),
    ("reckless-ben-case-261000376", "Provo Case"),
]

TOPICS = [
    {
        "slug": "bricks-minifigs-franchise-documents",
        "title": "Bricks and Minifigs Franchise Documents | FDD Archive",
        "description": "Bricks and Minifigs franchise disclosure documents (FDD): 2023 and 2026 FDD PDFs, franchise fees, startup investment, and NASAA state registration history for Bricks and Minifigs, Inc.",
        "h1": "Bricks and Minifigs franchise documents",
        "lede": "Franchise Disclosure Documents (FDD) and state registration records for the Bricks and Minifigs store franchise model — including 2023 and 2026 disclosures, investment ranges, ongoing fees, and multi-state franchise registration listings.",
        "keywords": "Bricks and Minifigs FDD, franchise disclosure document, BAM Franchising, franchise fees, NASAA registration, 2023 FDD, 2026 FDD",
        "extract": {"group": "1"},
    },
    {
        "slug": "legally-mine",
        "title": "Ammon McNeff / Legally Mine",
        "description": "Everything related to Ammon McNeff and Legally Mine, including the federal case McNeff v. McNeff (2:21-cv-00048-DAO) and Legally Mine LLC records (Utah UCC filings and Ohio bar order).",
        "h1": "Ammon McNeff / Legally Mine",
        "lede": "Everything related to Ammon McNeff and Legally Mine: the federal court case McNeff v. McNeff plus Legally Mine LLC Utah UCC filings and the Ohio Supreme Court order.",
        "keywords": "Ammon McNeff, Legally Mine LLC, Daniel McNeff, McNeff v McNeff, Legally Mine federal case, unauthorized practice of law, Ohio bar order, Utah UCC, District of Utah, PACER, 2:21-cv-00048",
        "extract": {"item_ids": [
            "utah-ucc-legally-mine-summary-item",
            "utah-ucc-legally-mine-detail-item",
            "legally-mine-ohio-upl-order-2025-0037-item",
            "mcneff-v-mcneff-2-21-cv-00048-doc-1-civil-cover-sheet-item",
            "mcneff-v-mcneff-2-21-cv-00048-doc-2-complaint-item",
            "mcneff-v-mcneff-2-21-cv-00048-doc-2-1-civil-cover-sheet-item",
            "mcneff-v-mcneff-2-21-cv-00048-doc-2-2-exhibit-a-item",
            "mcneff-v-mcneff-2-21-cv-00048-doc-2-3-exhibit-b-item",
            "mcneff-v-mcneff-2-21-cv-00048-doc-2-4-exhibit-c-item",
            "mcneff-v-mcneff-2-21-cv-00048-doc-2-5-exhibit-d-item",
            "mcneff-v-mcneff-2-21-cv-00048-doc-2-6-exhibit-e-item",
            "mcneff-v-mcneff-2-21-cv-00048-doc-2-7-exhibit-f-item",
            "mcneff-v-mcneff-2-21-cv-00048-doc-3-order-to-propose-schedule-item",
            "mcneff-v-mcneff-2-21-cv-00048-doc-12-filing-item",
        ]},
    },
    {
        "slug": "bricks-minifigs-financing-records",
        "title": "Bricks and Minifigs Financing Records | Utah UCC Filings",
        "description": "Utah UCC financing statement summary and detailed filings for Bricks and Minifigs, Inc. — debtor records, filing dates, lapse dates, and secured-party information from Utah state records.",
        "h1": "Bricks and Minifigs financing records",
        "lede": "Utah Uniform Commercial Code (UCC) financing records for Bricks and Minifigs, Inc., including summary and detailed filing exports showing debtor information, filing status, and secured-party details.",
        "keywords": "Bricks and Minifigs UCC, BAM Franchising financing, Utah UCC filing, secured transactions, franchise financing",
        "extract": {"group": "2", "item_ids": [
            "utah-ucc-bam-franchising-summary-item",
            "utah-ucc-bam-franchising-detail-item",
        ]},
    },

    {
        "slug": "chrystal-law-bricks-minifigs",
        "title": "Chrystal Law Bricks and Minifigs Lawsuit | Case 260200029",
        "description": "Chrystal Law and Benjamin Gorman lawsuit against Bricks and Minifigs in Utah Business and Chancery Court Case No. 260200029 — complaint, LEGO email exhibit, franchise agreement, termination letter, and motion to compel arbitration.",
        "h1": "Chrystal Law / Bricks and Minifigs lawsuit",
        "lede": "Utah Business and Chancery Court Case No. 260200029: Chrystal Law and Benjamin Gorman complaint against Bricks and Minifigs and Bricks and Minifigs Salem 1, with exhibits and a motion to stay and compel mediation/arbitration.",
        "keywords": "Chrystal Law, Benjamin Gorman, Bricks and Minifigs Salem 1, franchise termination, Case 260200029, Utah Business and Chancery Court, wrongful termination",
        "extract": {"group": "4"},
    },
    {
        "slug": "american-fork-police-reckless-ben",
        "title": "American Fork Police & Reckless Ben Records",
        "description": "American Fork Police Department records involving Reckless Ben (Benjamin Schneider): trespass, harassment, and stalking incident reports, probable cause statement, booking sheet, and search warrant 3352981 tied to the Bricks and Minifigs dispute.",
        "h1": "American Fork Police Department & Reckless Ben records",
        "lede": "Police records from American Fork, Utah (March 2026) involving Reckless Ben / Benjamin Schneider — incident reports 26AF01974, 26AF02007, and 26AF02033, probable cause affidavit, booking sheet, search warrant 3352981, and linked body-camera archive.",
        "keywords": "American Fork Police Department, Reckless Ben, Benjamin Schneider, stalking, harassment, trespass, search warrant 3352981, Utah police records, Bricks and Minifigs",
        "extract": {"group": "5"},
    },
    {
        "slug": "reckless-ben-utah-lawsuit",
        "title": "Reckless Ben Utah Lawsuit | Bricks and Minifigs Case 260402353",
        "description": "Bricks and Minifigs v. Reckless Ben (Benjamin Schneider), Bryan Mansell, and Victor Nguyen — Utah Fourth District Court Case No. 260402353 verified complaint, TRO, errata, filing receipt, docket, and alternative service order.",
        "h1": "Reckless Ben Utah lawsuit (Case 260402353)",
        "lede": "Utah Fourth Judicial District Court Case No. 260402353: Bricks and Minifigs, Ammon McNeff, Matt McNeff, Joshua Johnson, and Brandon Best v. Reckless Ben, Bryan Mansell, Victor Nguyen, and others — complaint, temporary restraining order, errata, docket screenshots, and ex parte service order.",
        "keywords": "Reckless Ben lawsuit, Benjamin Schneider, Bricks and Minifigs v Reckless Ben, Case 260402353, Bryan Mansell, Victor Nguyen, Utah TRO, verified complaint, Provo District Court",
        "extract": {"group": "6"},
        "doc_insertions": {
            "verified-complaint": UTAH_COMPLAINT_CONTEXT,
        },
    },
    {
        "slug": "reckless-ben-case-261000376",
        "title": "Reckless Ben Provo Misdemeanor Case 261000376",
        "description": "Reckless Ben Provo Misdemeanor Case 261000376 court documents involving Reckless Ben (Benjamin Schneider). Separate case records including the docket events list, Information and Indictment, and Advisement of Rights form from the Bricks and Minifigs dispute.",
        "h1": "Reckless Ben Provo Misdemeanor Case 261000376",
        "lede": "Public court documents from the Reckless Ben Provo Misdemeanor Case 261000376 involving YouTuber Reckless Ben (Benjamin Paul Schneider). This separate case includes the docket events list, the Information and Indictment, and the Advisement of Rights form.",
        "keywords": "Reckless Ben 261000376, Benjamin Schneider 261000376, Provo Misdemeanor Case 261000376, docket events, Information and Indictment, Advisement of Rights, Bricks and Minifigs, Reckless Ben court records",
        "extract": {"group": "8"},
    },
    {
        "slug": "reckless-ben-small-claims",
        "title": "Reckless Ben Small Claims | Oregon Court Records",
        "description": "Oregon small claims court records for Reckless Ben (Benjamin Schneider) v. L2 Bricks, LLC and v. Joshua Johnson — cases 25SC26531, 25SC30722, and 26SC06134 with complaints, judgments, motions, and hearing notices.",
        "h1": "Reckless Ben Oregon small claims records",
        "lede": "Oregon circuit court small claims filings by Benjamin Schneider (Reckless Ben) against L2 Bricks, LLC and Joshua Johnson. Three dockets — 25SC26531, 25SC30722, and 26SC06134 — with court-filed PDFs indexed below by case.",
        "keywords": "Reckless Ben small claims, Benjamin Schneider, Oregon small claims court, L2 Bricks LLC, Joshua Johnson, 25SC26531, 25SC30722, 26SC06134, Bricks and Minifigs dispute",
        "extract": {"group": "7"},
        "extra_context": SMALL_CLAIMS_CONTEXT,
        "related": [
            ("25SC26531 · Reckless Ben v. L2 Bricks", "reckless-ben-small-claims/25sc26531-l2-bricks"),
            ("25SC30722 · Reckless Ben v. L2 Bricks (2nd)", "reckless-ben-small-claims/25sc30722-l2-bricks"),
            ("26SC06134 · Reckless Ben v. Joshua Johnson", "reckless-ben-small-claims/26sc06134-joshua-johnson"),
        ],
    },
    {
        "slug": "reckless-ben-small-claims/25sc26531-l2-bricks",
        "title": "25SC26531 | Reckless Ben v. L2 Bricks Small Claims",
        "description": "Oregon small claims Case 25SC26531: Benjamin Schneider (Reckless Ben) v. L2 Bricks, LLC — amended claim, small claim complaint, judgment dismissal, and entry-of-judgment notices.",
        "h1": "25SC26531 — Reckless Ben v. L2 Bricks, LLC",
        "lede": "Oregon small claims court file 25SC26531: Benjamin Schneider, also known as Reckless Ben, against L2 Bricks, LLC. Includes amended claim, original small claim complaint, housecleaning dismissal judgment, and entry-of-judgment notices.",
        "keywords": "25SC26531, Reckless Ben v L2 Bricks, Benjamin Schneider small claims, L2 Bricks LLC Oregon, Bricks and Minifigs Oregon court, small claim complaint, housecleaning dismissal",
        "extract": {"group": "7", "case": "7.A"},
        "extra_context": SMALL_CLAIMS_CONTEXT,
        "parent": "reckless-ben-small-claims",
    },
    {
        "slug": "reckless-ben-small-claims/25sc30722-l2-bricks",
        "title": "25SC30722 | Reckless Ben v. L2 Bricks Small Claims (2nd)",
        "description": "Oregon small claims Case 25SC30722: Benjamin Schneider (Reckless Ben) v. L2 Bricks, LLC — second docket with complaints, default motions, proof of service, order denials, judgments, and court letters.",
        "h1": "25SC30722 — Reckless Ben v. L2 Bricks, LLC (second case)",
        "lede": "Second Oregon small claims filing 25SC30722: Benjamin Schneider (Reckless Ben) against L2 Bricks, LLC. Eleven court-filed PDFs including small claim complaint, default-order motions, proof of service, order denials, judgments, and correspondence.",
        "keywords": "25SC30722, Reckless Ben small claims, Benjamin Schneider L2 Bricks, Oregon circuit court, default order, proof of service, Bricks and Minifigs dispute Oregon",
        "extract": {"group": "7", "case": "7.B"},
        "extra_context": SMALL_CLAIMS_CONTEXT,
        "parent": "reckless-ben-small-claims",
    },
    {
        "slug": "reckless-ben-small-claims/26sc06134-joshua-johnson",
        "title": "26SC06134 | Reckless Ben v. Joshua Johnson Small Claims",
        "description": "Oregon small claims Case 26SC06134: Benjamin Schneider (Reckless Ben) v. Joshua Johnson — claim, small claim response, mediation notices, hearing notices, and consent filings.",
        "h1": "26SC06134 — Reckless Ben v. Joshua Johnson",
        "lede": "Oregon small claims court file 26SC06134: Benjamin Schneider, also known as Reckless Ben, against Joshua Johnson. Fifteen court-filed PDFs including claim, response, mediation no-agreement notice, multiple hearing notices, and consent filings.",
        "keywords": "26SC06134, Reckless Ben v Joshua Johnson, Benjamin Schneider small claims, Joshua Johnson Oregon court, Bricks and Minifigs, mediation hearing notice, small claim response",
        "extract": {"group": "7", "case": "7.C"},
        "extra_context": SMALL_CLAIMS_CONTEXT,
        "parent": "reckless-ben-small-claims",
    },
]


def load_index() -> str:
    return INDEX.read_text(encoding="utf-8")


def group_markers(html_text: str) -> list[re.Match[str]]:
    return list(re.finditer(r'<li class="group"[^>]*data-group="(\d+)"', html_text))


def extract_group(html_text: str, group: str) -> str:
    markers = group_markers(html_text)
    target = next((m for m in markers if m.group(1) == group), None)
    if not target:
        raise ValueError(f"Group {group} not found")
    idx = markers.index(target)
    if idx + 1 < len(markers):
        block_end = markers[idx + 1].start()
    else:
        end_match = re.search(
            r"</li>\s*</ol>\s*<p class=\"archive-empty\"",
            html_text[target.start():],
            re.DOTALL,
        )
        if not end_match:
            raise ValueError(f"Group list end not found after group {group}")
        block_end = target.start() + end_match.start() + len("</li>")
    block = html_text[target.start():block_end]
    inner_match = re.match(r"<li class=\"group\"[^>]*>(.*)</li>\s*$", block, re.DOTALL)
    if not inner_match:
        raise ValueError(f"Group {group} block malformed")
    return inner_match.group(1)


def extract_items(group_html: str, item_ids: list[str]) -> str:
    chunks = []
    for item_id in item_ids:
        pattern = rf'<li id="{re.escape(item_id)}"[^>]*>.*?</li>'
        match = re.search(pattern, group_html, re.DOTALL)
        if not match:
            raise ValueError(f"Item {item_id} not found")
        chunks.append(match.group(0))
    return "\n".join(chunks)


def extract_case(group_html: str, case: str) -> str:
    start_pat = rf'<li id="[^"]*" data-case="{re.escape(case)}"'
    start = re.search(start_pat, group_html)
    if not start:
        raise ValueError(f"Case {case} not found")
    next_case = re.search(r'<li id="[^"]*" data-case="', group_html[start.end():])
    block_end = start.end() + next_case.start() if next_case else group_html.find("</ol>", start.start())
    if block_end < 0:
        raise ValueError(f"Case {case} block end not found")
    return group_html[start.start():block_end].strip()


def extract_subdocs(group_html: str, body: str) -> str:
    spec = body["extract"]
    if "case" in spec:
        return extract_case(group_html, spec["case"])
    if "item_ids" in spec:
        return extract_items(group_html, spec["item_ids"])
    subdocs_match = re.search(r"<ol class=\"subdocs\">(.*?)</ol>", group_html, re.DOTALL)
    if not subdocs_match:
        raise ValueError("subdocs not found")
    return subdocs_match.group(1).strip()


def build_nav(current_slug: str) -> str:
    parts = []
    current = current_slug.split("/")[0]
    for slug, label in NAV:
        is_current = slug == current
        if slug == "legally-mine" and current in ("legally-mine", "ammon-mcneff-federal-case"):
            is_current = True
        cls = ' class="is-current"' if is_current else ""
        parts.append(f'<a href="/topics/{slug}/"{cls}>{html.escape(label)}</a>')
    return "\n      ".join(parts)


def enrich_subdocs(subdocs_html: str, insertions: dict[str, str] | None) -> str:
    if not insertions:
        return subdocs_html
    enriched = subdocs_html
    for item_id, note in insertions.items():
        extra = f'<p class="doc-context">{html.escape(note)}</p>'
        pattern = rf'(<li id="{re.escape(item_id)}"[^>]*>.*?<p class="doc-desc">.*?</p>)'
        enriched, count = re.subn(pattern, rf"\1\n                  {extra}", enriched, count=1, flags=re.DOTALL)
        if count != 1:
            raise ValueError(f"Could not insert context for {item_id}")
    return enriched


def build_related(related: list[tuple[str, str]] | None) -> str:
    if not related:
        return ""
    links = "\n".join(
        f'        <li><a href="/topics/{slug}/">{html.escape(label)}</a></li>'
        for label, slug in related
    )
    return f"""
    <section class="case-related" aria-label="Related cases">
      <h2>Small Claims cases</h2>
      <ul>
{links}
      </ul>
    </section>"""


def build_page(topic: dict, subdocs_html: str) -> str:
    slug = topic["slug"]
    canonical = f"https://bamsucks.com/topics/{slug}/"
    current_root = slug.split("/")[0]
    parent_link = ""
    if topic.get("parent"):
        parent_link = f'\n      <a href="/topics/{topic["parent"]}/">← All Reckless Ben small claims</a>'

    related_html = build_related(topic.get("related"))
    extra_context_html = ""
    if topic.get("extra_context"):
        extra_context_html = (
            f'      <p class="topic-intro">{html.escape(topic["extra_context"])}</p>\n'
        )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(topic["title"])}</title>
  <meta name="description" content="{html.escape(topic["description"])}">
  <meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
  <meta name="theme-color" content="#ffffff">
  <link rel="canonical" href="{canonical}">
  <link rel="icon" href="/favicon.ico" sizes="any">
  <link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png">
  <link rel="icon" href="/favicon-16.png" sizes="16x16" type="image/png">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <link rel="manifest" href="/site.webmanifest">
  <meta property="og:site_name" content="Bricks and Minifigs Archive">
  <meta property="og:title" content="{html.escape(topic["h1"])}">
  <meta property="og:description" content="{html.escape(topic["description"])}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="https://bamsucks.com/social-card-v3.png">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{html.escape(topic["h1"])}">
  <meta name="twitter:description" content="{html.escape(topic["description"])}">
  <meta name="twitter:image" content="https://bamsucks.com/social-card-v3.png">
  <link rel="stylesheet" href="/topics.css">
  <script src="/archive.js?v=pattern38" defer></script>
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "CollectionPage",
    "name": {json_str(topic["h1"])},
    "description": {json_str(topic["description"])},
    "url": {json_str(canonical)},
    "isPartOf": {{
      "@type": "WebSite",
      "name": "Bricks and Minifigs Archive",
      "url": "https://bamsucks.com/"
    }}
  }}
  </script>
</head>
<body>
  <main>
    <nav class="top-links" aria-label="Site navigation">
      <a href="/" data-go-back-home>← Go back home</a>{parent_link}
    </nav>

    <header>
      <h1>{html.escape(topic["h1"])}</h1>
{extra_context_html}      <p class="lede">{html.escape(topic["lede"])}</p>
      <p class="topic-keywords"><strong>Related searches:</strong> {html.escape(topic["keywords"])}</p>
    </header>

    <nav class="topic-nav" aria-label="Browse archive topics">
      {build_nav(current_root if "/" not in slug else topic.get("parent", current_root))}
    </nav>

    <section aria-label="Documents">
      <h2>Documents in this topic</h2>
      <ol class="subdocs">
{subdocs_html}
      </ol>
    </section>
{related_html}
    <section class="notice">
      <p>Court filings and public records may contain allegations or registry data. Read each source according to its own terms. This page indexes publicly available documents; it is not a finding of liability or wrongdoing.</p>
    </section>

    <footer>
      <p>Part of the <a href="/">Bricks and Minifigs dispute archive</a>. Last updated <time datetime="2026-06-12">June 12, 2026</time>.</p>
      <p><a href="/sitemap.xml">Sitemap</a> · <a href="/robots.txt">Robots</a></p>
    </footer>
  </main>
</body>
</html>
"""


def json_str(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def build_topics_index() -> str:
    cards = []
    for topic in TOPICS:
        if "/" in topic["slug"]:
            continue
        cards.append(
            f"""      <li>
        <a href="/topics/{topic["slug"]}/"><strong>{html.escape(topic["h1"])}</strong></a>
        <p>{html.escape(topic["lede"])}</p>
      </li>"""
        )
    cards_html = "\n".join(cards)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Archive Topics | Bricks and Minifigs, Reckless Ben, Legally Mine</title>
  <meta name="description" content="Browse the Bricks and Minifigs dispute archive by topic: franchise FDD documents, Legally Mine records, Utah UCC financing, Ammon McNeff federal case, Chrystal Law lawsuit, American Fork Police records, Reckless Ben Utah lawsuit, and Oregon small claims.">
  <meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">
  <link rel="canonical" href="https://bamsucks.com/topics/">
  <link rel="stylesheet" href="/topics.css">
  <script src="/archive.js?v=pattern38" defer></script>
  <style>
    .topic-list {{ list-style: none; padding: 0; margin: 0; display: grid; gap: 16px; }}
    .topic-list li {{ border: 1px solid var(--line); padding: 16px; }}
    .topic-list strong {{ font-size: 1.05rem; }}
    .topic-list p {{ margin: 8px 0 0; color: var(--muted); font-size: 0.96rem; }}
  </style>
</head>
<body>
  <main>
    <nav class="top-links"><a href="/" data-go-back-home>← Go back home</a></nav>
    <h1>Archive topics</h1>
    <p class="lede">Topic landing pages for franchise documents, Legally Mine and financing records, federal and state court filings, American Fork Police Department records, the Reckless Ben Utah lawsuit, and Oregon small claims involving Benjamin Schneider.</p>
    <ul class="topic-list">
{cards_html}
    </ul>
    <footer>
      <p>Last updated <time datetime="2026-06-12">June 12, 2026</time>. <a href="/sitemap.xml">Sitemap</a></p>
    </footer>
  </main>
</body>
</html>
"""


def main() -> None:
    html_text = load_index()
    group_cache: dict[str, str] = {}

    for topic in TOPICS:
        spec = topic["extract"]
        if "group" in spec:
            group = spec["group"]
            if group not in group_cache:
                group_cache[group] = extract_group(html_text, group)
            group_html = group_cache[group]
        else:
            # merged topics like legally-mine + ammon-mcneff: collect html from relevant groups
            for g in ["2", "3"]:
                if g not in group_cache:
                    group_cache[g] = extract_group(html_text, g)
            group_html = group_cache["2"] + "\n" + group_cache["3"]
        subdocs = extract_subdocs(group_html, topic)
        subdocs = enrich_subdocs(subdocs, topic.get("doc_insertions"))
        page = build_page(topic, subdocs)
        out_dir = TOPICS_DIR / topic["slug"]
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "index.html").write_text(page, encoding="utf-8", newline="\n")
        print(f"Wrote topics/{topic['slug']}/index.html")

    (TOPICS_DIR / "index.html").write_text(build_topics_index(), encoding="utf-8", newline="\n")
    print("Wrote topics/index.html")


if __name__ == "__main__":
    main()