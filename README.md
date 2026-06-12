# Bricks and Minifigs Sucks — Public Archive

**Super neutral public archive of court records, police reports, franchise documents, and related public filings from the Bricks and Minifigs / BAM Franchising disputes involving Reckless Ben (Benjamin Schneider) and others.**

> **Important disclaimer**: if you are Ammon Mcneff don't sue me please

## Do you want to contribute?

If you want to upload a legal/police/exhibit document follow this:

1. Use `python add_document.py ...` (see the detailed usage comment at the top of the file) to scaffold everything.
2. Follow the reminders the script prints. (This will remind you to add the item to `archive.js` GROUP_DATA so Previous/Next navigation works automatically on the new reader page.)
3. Run `python add_document.py --check` and `python generate_new_previews.py`.
4. **Edit `sitemap.xml`**: Add `<url>` entries for the new reader page (`/<your-slug>/`) **and** for the PDF file itself. Once the preview PNG exists, also add an `<image:image>` element inside the reader page's `<url>`.  
   **Why this matters for SEO**: Keeping the sitemap up to date helps search engines discover new documents quickly. Including the PDF + image references can get your document pages and previews into Google search results and Google Images.
5. Run `python _build_topic_pages.py` after any catalog changes on the homepage. If the document should appear in (or create) a topic hub, you may also need to add or update an entry in the `TOPICS` list inside `_build_topic_pages.py`.
6. Maximize for SEO while you work:
   - Use clear, descriptive titles and descriptions that include case numbers, party names (e.g. "Reckless Ben", "Bricks and Minifigs"), document type, and location. The `add_document.py` scaffold already guides you toward good SEO text.
   - The site relies on topic hubs, structured data (JSON-LD), and good internal linking for discoverability — keep those patterns when adding content.
   - Maintain the neutral public-records tone in any custom text you add (see the existing disclaimers).
7. Test locally (any static server works), then open a PR (or just paste the full set of changes if you're helping directly).

Other helpful contributions:
- Improving reader page text excerpts / OCR cleanup in the "Searchable text" sections.
- Better mobile styles, accessibility, or keyboard navigation.
- Adding more topic context, related links, or cross-references between cases.
- Improving the Python generators or adding tests for `--check`.
- Documentation improvements.

### Quick SEO & sitemap checklist for new documents
- [ ] Reader page title + meta description contain strong keywords (case #, parties, document type)
- [ ] Preview PNG generated and referenced
- [ ] Entry added to `archive.js` GROUP_DATA (for intra-group prev/next)
- [ ] Catalog `<li>` pasted into the correct group in `index.html`
- [ ] `sitemap.xml` updated (reader + PDF + image:image where applicable)
- [ ] `python _build_topic_pages.py` re-run
- [ ] `python add_document.py --check` passes for the new item
- [ ] Test the page and the group navigation

This keeps the archive consistent, well-indexed, and easy for others to navigate.


## How site works (architecture for contributors)

The site is **pure static files**. No backend. Everything is designed so a single person (or contributors) can add documents with a semi-automated workflow and then deploy the folder as-is.

### Core pieces

1. **PDFs at root**  
   Filenames are cleaned and descriptive (e.g. `Bricks-and-Minifigs-v-Reckless-Ben-Utah-Case-260402353-Exhibit-J-Notice-Of-Trespass.pdf`).

2. **Document readers** (`slug/index.html`)  
   Every important document gets its own folder containing a self-contained reader page.  
   Layout (from `document.css`):
   - Left/main: browser `<iframe>` embedding the PDF directly (`<iframe src="/TheFile.pdf">`).
   - Right sidebar (sticky on desktop): first-page preview PNG, "Details" facts table (Document type / Date / Source / People/entities / Pages / Original file), action buttons (Open PDF / Download), and a collapsible "Searchable text" section for excerpts or OCR.
   - Heavy SEO: meta tags, Open Graph, Twitter cards, JSON-LD structured data (WebPage + DigitalDocument + BreadcrumbList).
   - Shared styles + `archive.js` for group navigation.

3. **Homepage catalog (`index.html`)**  
   Documents are organized in numbered groups marked with `data-group="N"` and individual `<li id="slug">` entries inside `<ol class="subdocs">`.  
   Some groups (especially the Oregon small claims) have nested case sub-lists (`data-case="7.A"` etc.).  
   Client-side magic in `archive.js` provides powerful live filtering by text search + topic group + sub-case, URL sync (`?q=...&group=6`), scroll memory, etc.

4. **Topic hubs (`topics/` directory + `_build_topic_pages.py`)**  
   These are generated "hub" pages for better SEO and browsing (one per major category + a topics index).  
   The Python script parses the main `index.html` using regex on the `data-group` markers and specific item IDs/cases. It pulls the relevant sub-lists, adds contextual ledes and keywords (hardcoded in the `TOPICS` list inside the script), and writes fresh `topics/slug/index.html` files.  
   Run it after you edit the catalog in `index.html`.

5. **Previews (`previews/<slug>-page-1.png`)**  
   First-page thumbnails used in sidebars and social cards.  
   Generated by `generate_new_previews.py` (uses PyMuPDF / `fitz`). The script has both explicit mappings and smart auto-detection so it can handle new PDFs without constant editing.

6. **The "add a document" workflow (`add_document.py`)** — this is how you (and contributors) grow the archive
   - Run the script with metadata for the new PDF (slug, title, sub-number in its group, date, page count, type, source, people, description, etc.).
   - It copies the PDF to the root with a clean name and scaffolds a full reader `slug/index.html` (with TODO markers for the lede paragraph and "Searchable text" excerpt).
   - It prints a ready-to-paste `<li>` block that goes into the appropriate group in the main `index.html`.
   - Reminders it prints:
     - Create the preview PNG (or just re-run `generate_new_previews.py` — it has fuzzy matching).
     - Manually add the item to the big `GROUP_DATA` object in `archive.js` (this powers the Previous/Next strip that appears automatically on every reader page).
     - Add the URL to `sitemap.xml`.
     - Paste the catalog `<li>` you got from the script into `index.html`.
     - Re-run `_build_topic_pages.py`.
     - Fill the TODOs in the new reader (custom context text, excerpt).
   - Bonus: `python add_document.py --check` audits that every document listed in the homepage/groups actually has a matching reader folder + preview. This prevents broken "Read page" links.

7. **Navigation & polish (`archive.js`)**  
   - Homepage filters + URL state.
   - On every reader page: automatically injects "Group N / Home" + a Previous/Next sequence strip (with careful mobile centering so the current document number stays in the middle of the visible strip).
   - Decorative brick-pattern side rails (thematic for LEGO/Bricks).
   - Dismissible 14-day legal notice banner (injected at the top of home + readers).
   - `GROUP_DATA` constant at the bottom is the single source of truth for ordered navigation per group/case.

8. **Styling**
   - `document.css` — global for all individual readers (two-pane layout, facts grid, etc.). Most old inline styles have been consolidated here.
   - `topics.css` — for the generated topic hubs and some catalog elements.
   - Small page-specific overrides are still present in some readers.

### Local development / testing

- Any static file server works: `python -m http.server 8080`, `npx serve .`, or the old `serve-*.bat` scripts.
- After adding documents or editing the catalog, run the Python generators as noted above.
- The `add_document.py --check` command is your friend for catching incomplete additions.

### Tech / deployment notes

- 100% static. Historically deployed to Cloudflare Pages (project "bricksminifigslawsuit", aliases bamsucks.com + www).
- Can also be hosted on GitHub Pages, Netlify, Vercel, etc. Just point at the root of this folder.
- No build step for the final site (the Python scripts are author-time tools).
- Python dependencies (only for tooling): `pymupdf` (for preview generation).



## Current state notes (this recovered snapshot)

This folder is a "recovered" version of the archive. It contains a large number of documents and readers from the ongoing collection effort.

Unnecessary / recovery-only artifacts (cloudflare deployment logs, previous homepage snapshots, old extracted source trees, etc.) have been excluded via `.gitignore` so the published Git history stays focused on the actual archive content and the tools needed to maintain it.

The Python build tools are now included in the repo because the goal is public contribution and maintenance.

All new commits in this GitHub version use a safe identity that does not expose real names.
