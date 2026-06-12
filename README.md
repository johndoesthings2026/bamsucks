# Bricks and Minifigs Sucks — Public Archive

![Ammon](ammon.png)
>if you are Ammon Mcneff don't sue me please

## Do you want to contribute?

> this applies only to adding new documents

**1. Scaffold the files using `python add_document.py`**

It:
Copies your source PDF into the project root with a clean, consistent filename.
Creates a new folder `your-slug/` containing a fully functional reader page skeleton (`index.html`).
Prints the exact HTML block you need to paste into the main catalog in `index.html`.

Run it with the metadata for the new document. All the possible flags and an up-to-date example are documented in the giant comment block at the top of the file. A realistic command looks like this:

```bash
python add_document.py \
  --source "C:\Users\you\Downloads\Some-New-Filing.pdf" \
  --slug "bricks-minifigs-v-reckless-ben-exhibit-new-filing" \
  --title "Exhibit ZZ - New Important Filing Title" \
  --sub "6ZZ" \
  --date "2026-04 (filed 2026-06)" \
  --pages "5" \
  --type "Exhibit - Court Filing" \
  --doc-source "Fourth Judicial District Court, Utah" \
  --people "Bricks and Minifigs entities vs. Reckless Ben et al." \
  --desc "Short neutral description of what this document is and why it matters for the public record."
```

The script will **never** touch `index.html`, `archive.js`, or `sitemap.xml` itself. It only creates the new folder + PDF and tells you exactly what to do next.

**2. Follow every single reminder the script prints (especially the archive.js one)**

The script will output several "=== REMINDERS ===" blocks. The most important one for navigation is the GROUP_DATA entry.

Copy the line it gives you (something like `{num: "6ZZ", slug: "bricks-minifigs-v-reckless-ben-exhibit-new-filing", title: "..."}`) and paste it into the correct `GROUP_DATA` object inside `archive.js`.

This is what makes the automatic "Previous" and "Next" arrows + the numbered group navigation bar appear on the new reader page. Without this step the page will be an orphan in the navigation.

Also follow the reminders about the catalog `<li>` block (paste it into the right group in `index.html`) and any other files it mentions.

**3. Generate the preview image and run the health check**

```bash
python generate_new_previews.py
python add_document.py --check
```

- `generate_new_previews.py` creates the first-page thumbnail PNG that appears in the sidebar of the reader and in social media previews. It has both hardcoded mappings and smart auto-detection, so in most cases you don't need to edit it.
- `--check` scans the entire homepage catalog and reports any document that is listed in the catalog but is missing either its reader folder or its preview PNG. This catches the most common "I forgot one step" mistakes.

Fix anything `--check` reports before moving on.

**4. Manually update `sitemap.xml` (this is the SEO step)**

Open the root `sitemap.xml` and add two new `<url>` entries:

- One for the HTML reader page: `https://bamsucks.com/<your-slug>/`
- One for the PDF itself: `https://bamsucks.com/<clean-pdf-filename.pdf>`

If the preview PNG now exists, also add an `<image:image>` block inside the reader page's `<url>` entry.

Minimal example of what to add (adjust the values):

```xml
<url>
  <loc>https://bamsucks.com/bricks-minifigs-v-reckless-ben-exhibit-new-filing/</loc>
  <lastmod>2026-06-12</lastmod>
  <changefreq>monthly</changefreq>
  <priority>0.6</priority>
  <image:image>
    <image:loc>https://bamsucks.com/previews/bricks-minifigs-v-reckless-ben-exhibit-new-filing-page-1.png</image:loc>
  </image:image>
</url>
<url>
  <loc>https://bamsucks.com/Your-Clean-PDF-Name.pdf</loc>
  <lastmod>2026-06-12</lastmod>
</url>
```

**Why this matters for SEO**: Google and other search engines use the sitemap to discover new pages faster than just crawling. The `<image:image>` references are how document preview images can start appearing in Google Images results for the relevant case names and document titles.

**5. Rebuild the topic hubs**

After you have pasted the new catalog entry into `index.html`, run:

```bash
python _build_topic_pages.py
```

This script re-reads the main catalog and regenerates all the high-level topic hub pages (`/topics/...`) plus the topics index.

If your new document should appear inside one of the existing topic hubs (or you are creating a brand new hub), you will also need to add or update an object in the `TOPICS` array inside `_build_topic_pages.py`. Look at the existing entries for the pattern.

**6. Write titles, descriptions, and text with SEO and tone in mind**

- The `add_document.py` scaffold already produces decent starting text that includes the case number and parties. Polish it so it reads naturally while still containing the important keywords (case numbers, "Reckless Ben", "Bricks and Minifigs", document type, location).
- Good example title/description: "Exhibit ZZ - Order Granting Alternative Service (Case 260402353)" + a one-sentence neutral summary.
- Bad: overly clickbaity or editorializing language.
- Keep every piece of custom text in the neutral public-records voice used everywhere else on the site (see the existing disclaimers and ledes). The archive's credibility depends on this.

The site already uses topic hubs, internal linking, and JSON-LD structured data. When you follow the existing patterns, the new page automatically benefits from the same discoverability systems.

**7. Test everything locally, then submit your changes**

Start a local static server from the project root:
```bash
python -m http.server 8080
```
(or use one of the `serve-*.bat` files if you prefer).

Click through:
- The new catalog entry on the homepage (search/filter should find it)
- The reader page itself (PDF loads in the iframe, preview appears, facts are correct)
- The Previous/Next navigation in the top bar
- The relevant topic hub (if you added it there)
- Mobile view

When everything works, open a Pull Request (preferred) or, if you are helping directly, just share the complete set of changed files (new reader folder + updated `index.html`, `archive.js`, `sitemap.xml`, any changes to `_build_topic_pages.py`, and the new preview PNG).

Other helpful contributions:
- Improving reader page text excerpts / OCR cleanup in the "Searchable text" sections.
- Better mobile styles, accessibility, or keyboard navigation.
- Adding more topic context, related links, or cross-references between cases.
- Improving the Python generators or adding tests for `--check`.
- Documentation improvements.
- make sure just to max for seo and update the sitemap

What is not allowed: 
- Letting a llm generate node js slop
- writing opinions on people mentioned like Ammon


