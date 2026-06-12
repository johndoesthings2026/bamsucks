# Bricks and Minifigs Sucks — Public Archive

>if you are Ammon Mcneff don't sue me please

## Do you want to contribute?

If you want to upload a legal/police/exhibit document follow this:

1. Use `python add_document.py ...`  to scaffold everything.
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
- make sure just to max for seo and update the sitemap

Not allowed: 
- Letting a llm to generate node js slop
- opinions

![Ammon](ammon.png)
