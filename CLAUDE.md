# Park Row Magazine

Website of Park Row Magazine, a cinema magazine run by a group of friends. Live at https://parkrowmagazine.com (public, no password).
Static HTML/CSS, no framework, no build step. Site text is in English.

## Publishing

- **Never commit or push to `main` directly.** Every change goes through a pull request that the site owner (GitHub `Thairones`) reviews and merges:
  1. `git pull` on `main` first, then create a branch named after the change (`git switch -c add-constellations-to-home`).
  2. Commit, push the branch, and open a pull request against `main` (`gh pr create`, or the link GitHub prints after the push).
  3. Vercel will mark the pull request's deployment as "Error" when the commit author isn't the owner: the Vercel project is on the free Hobby plan, which can't add other members. This is expected; don't try to fix it. The owner makes the preview from his side. Check the change locally instead and describe it clearly in the pull request.
  4. Do not merge it yourself. The owner merges it, and only then does the change go live. The owner must merge with "Create a merge commit" (not "Squash and merge"), so the commit that reaches `main` is in his name and Vercel deploys it.
- Merging into `main` deploys to production automatically (Vercel is connected to this repo). Check the page locally before opening the pull request.
- Local preview: `node .claude/serve.cjs` (configured in `.claude/launch.json`), then http://localhost:4173.
- `vercel.json` turns on clean URLs (`/issues`, `/articles/anima-of-animals`) and caches jpg/ttf for one day: when you replace an image, give the new file a new name rather than overwriting it.
- `.vercelignore` keeps `archive/`, `captures/`, `tools/`, `.claude/` and this file off the site.

## Files

- `index.html` home, `issues.html` table of contents, `gallery.html` all images, `about.html`, `articles/*.html` one page per article.
- `css/park-row.css` the only stylesheet. `js/intro.js` the "click to enter" street-sign intro on the home page.
- `fonts/`: Via Appia (PARK ROW / MAGAZINE title), Augustus (big section titles like ISSUES, GALLERY), Old Newspaper Types. Overpass and Special Elite come from Google Fonts.
- `img/<article>/` the images of each article.

## Art direction (the editors care a lot about this)

- Always dark: background `#121110`, text `#efe6d3`. There is no light mode.
- Article text in Times New Roman. Interface and nav in Overpass. "PARK ROW" and "MAGAZINE" in Via Appia, uppercase.
- Flat and minimal, like a professional printed magazine. No effects (shadows, gradients, glows), no borders or outlines around images, nothing that "looks AI-made".
- Centering is checked to the pixel: the masthead, the big `.giant` titles between their double rules, ISSUES exactly under MAGAZINE. After any change near them, measure; don't eyeball it.
- Home page = "stories" strips: wide image, title, author on the right, first lines, then a "....." link.
- Captions name the film as `<em>Title</em> (year) by Director`. Nightgame stills have no caption, by request.
- Speaker names in interviews and roundtables are bold: `<strong>Chaz Mullis:</strong>`.

## Current state (launch of Issue #1, Nov 2026)

- Home shows only "A Cold Approach to Phoenix" and "Anima of Animals", under the line "Park Row Issue #1 coming soon!" (typewriter font, no box). When the PDF of the issue is ready, turn that line into a link to the PDF; the PDF matters more than reading on the site. The PDF button on `issues.html` (`href="#"`) also needs the link.
- Issues and Gallery list only those two articles. The other articles are finished and online but not linked anywhere yet:
  `to-utopia` (Introduction: To Utopia, by the Park Row Editors), `to-the-cleared-walkway` (Zoey M. Hogan), `the-constellations` (Timothé Legrand-Hug), `we-still-bow-to-the-old-gods` (Jean-Luc Jacques), `cinema-without-a-world` (the Park Row Editors).
  The full versions of the home, Issues and Gallery from before the launch are in `archive/avant-lancement-2026-11-01/`.
- Full order of Issue #1: Introduction: To Utopia; To The Cleared Walkway; The Constellations; We Still Bow to the Old Gods; Cinema Without a World; A Cold Approach to Phoenix; then "Miscellaneous": Anima of Animals.
- The old password lock is kept in `archive/verrou-mot-de-passe/middleware.js`. Moving it back to the root re-locks the whole site (credentials live only in Vercel environment variables, never in the code).

## Gallery

`gallery.html` is generated: edit the `ISSUES` list in `tools/build_gallery.py`, then run `python tools/build_gallery.py`.
The script also puts `id="img-N"` anchors on the article figures so each thumbnail opens its image in the article, so run it again after editing or regenerating any article.

## Article generators

`tools/articles-pdf/` holds the Python scripts (PyMuPDF) that built the articles from the editors' PDFs. They are kept as references: their file paths point to the original PC and must be adjusted. Notes:
- `pdf_oblique.py` detects the fake italic in Word-exported PDFs (skewed text matrix).
- PDF images with transparency need their SMask: `pymupdf.Pixmap(base, mask)`.
- Generated pages are then edited by hand; regenerating overwrites those edits.
