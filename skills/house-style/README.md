# House Style: reference

The kit makes three things from one set of themes: slide decks, paged documents (PDF) and graphics (social posts,
banners, posters, invitations, cards). `SKILL.md` gives the workflow; this file lists what the kit holds.
`samples/showcase.html` (29 slides) uses nearly every deck part, `guide/structures.json` gives each slide layout's
markup, `samples/docs/` holds a report, a paper, a proposal, a letter, a one-pager, an event programme, a CV, an
invoice and a newsletter, and `samples/graphics/` holds posts, a banner, a link preview, a poster, an invitation, a
business card and a certificate.

## The deck
```html
<div class="pc-deck" data-theme="meridian" data-palette="cobalt" data-mode="light" data-format="16x9"
     data-motion="basic" data-title="Deck title">
  <section class="pc-slide pc-cover"> ... <div class="pc-notes"><p>Speaker notes</p></div></section>
  <section class="pc-slide"> ... </section>
</div>
```
The page links `engine/core.css`, the theme's `tokens.css` and `theme.css`, `icons/lucide.js` and `engine/runtime.js`
(copy the head of `samples/showcase.html`). `tools/build.py` turns it into one self-contained file.

A content slide has a kicker, a title and a body: `<p class="pc-kicker">`, `<h2 class="pc-title">`,
`<div class="pc-body">` (add `pc-body--center` or `pc-body--end` to place it). Plain `<p>` is body text,
`pc-lead` a larger lead paragraph, `pc-muted` and `pc-source` smaller text. `pc-slide--large` and `pc-slide--xl`
step up the body type of a sparse slide, never its title.

Surfaces: `data-surface` on a slide is `base` (default), `alt`, `accent`, `inverse` (the theme's other mode) or
`image`. `pc-inverse` on any element gives that element the other mode. Every component works on every surface.

## Layouts
Slide classes: `pc-cover`, `pc-section` (with `<p class="pc-section-num">`), `pc-statement` (one sentence in
`pc-say`), `pc-split` (a picture beside the text; `pc-split--left` swaps sides), `pc-bleed` (a picture fills the
slide, text over a scrim), `pc-closing` (with a `pc-contact` list and an optional QR code). The other layouts are
content slides built from components. `guide/structures.json` lists all 22: cover, agenda, section, stats, big number,
chart, statement, timeline, before and after, split, bleed, code, checklist, table, steps, funnel, cards, quote,
compare, tiers, people, closing.

## Components
| Class | Markup |
|---|---|
| Bullets | `ul.pc-list` / `ol.pc-list` |
| Cards | `div.pc-grid.pc-cols-3 > div.pc-card` (`pc-cols-2` to `-4`, `pc-cols-3-2`; `pc-grid--stretch`, `--center`) |
| Stats row | `div.pc-stats > div` with `span.pc-stat` and `p.pc-stat-text`, `style="--n:4"` |
| Big number | `div.pc-big` with `span.pc-stat` and a `pc-stack` of `pc-lead` and `dl.pc-facts` |
| Facts list | `dl.pc-facts > div > dt + dd` |
| Checklist | `ul.pc-checks > li.is-done / .is-todo / .is-no` |
| Steps | `ol.pc-steps > li > b + p` |
| Timeline | `ol.pc-timeline > li > b + text` (`is-now`, `is-planned`) |
| Comparison | `div.pc-compare` with two or three columns; `pc-vs` puts a badge between two |
| Before and after | `div.pc-ba > div + div` |
| Funnel | `ol.pc-funnel > li style="--v:100"` |
| Tiers | cards side by side; `is-hl` and `data-badge="Most popular"` mark one |
| People | portrait tiles with name and role |
| Quote | `figure.pc-quote > blockquote + figcaption` (`span.pc-avatar` for initials) |
| Table | `table.pc-table` (`is-num` cells right-aligned with tabular figures, `tr.pc-total`) |
| Progress bars | `div.pc-bars > div style="--v:72" > span + b` |
| Chips and status | always with words, never colour alone |
| Callout | a boxed note in the accent |
| Code | `pre.pc-code data-lang="python" > code` (the runtime colours it and moves it to its own row if too wide) |
| Annotated screenshot | `figure.pc-shot.pc-shot--browser > img + b.pc-pin style="--x:30;--y:42"` |
| Logo strip | a row of logos or badges |
| Picture | `div.pc-media > img style="--fx:50%;--fy:30%"` (focal point for cropping and drift) |
| Icon | `<i class="pc-icon" data-icon="carrot"></i>` (Lucide names; `pc-icon--lg`) |
| Hand-drawn mark | `<span class="pc-mark" data-mark="underline">` (also circle, box, highlight, strike, cross) |
| Drop cap | `pc-dropcap` on a paragraph |
Narrow formats fold wide grids so text keeps a readable measure; `pc-keep` stops that.

## Charts
`<figure class="pc-chart" data-type="column" data-labels="Apr,May,Jun" data-values="120,310,540">`, or a child
`<table>` the runtime reads (and keeps for screen readers). Types: `bar`, `column`, `grouped`, `stacked`, `line`,
`area`, `donut`, `waterfall`, `progress`. Charts are SVG in theme colours with direct labels, redraw on any theme or
format change, and print finished. `data-summary` becomes the chart's spoken description. SKILL.md has a table for
choosing one.

## Motion
`data-motion` on the deck: `static`, `basic` (default) or `complex`. Builds: `data-build="rise"` on an element, or
`data-build-each="rise"` on a container for its children one by one; also `fade`, `pop`, `wipe`, `grow`, `draw` and
`converge` (a title's words slide in from both sides). Complex motion adds count-up figures, the converging cover
title with the rest of the cover rising after it, and a slow zoom on `pc-media--bg` and `pc-media--side` pictures
(`data-drift="no"` opts out). Reduced-motion settings, print, the PDF and the PowerPoint get finished slides.

## Presenting
Right, Space or PageDown go forward; Left or PageUp back; Home and End; `P` opens the presenter window (current and
next slide, notes, timer); `O` the overview; `L` the laser; `N` the notes panel; `B` and `W` blank the screen; Esc
closes overlays. `#5` in the address opens slide 5. Download (bottom corner) gives PDF and PowerPoint in a published
deck. Without scripts (Quick Look, some mail previews) the slides show stacked, drawn as they print.

## Documents
A document is one HTML file with `class="pc-deck pc-doc"` on its `<html>` element, printed to a PDF:
```html
<html lang="en" class="pc-deck pc-doc" data-theme="seminar" data-palette="green" data-mode="light"
      data-type="report" data-page="a4" data-notes="side" data-title="..." data-short-title="Running head">
<head> <link> engine/doc.css and themes/<id>/tokens.css; <script> icons/lucide.js </head>
<body>
  <section class="pc-cover" data-cover="band"> kicker, h1, pc-sub, pc-meta </section>
  <nav class="pc-toc" data-depth="2"></nav>
  <section class="pc-chapter"><h1 id="summary">Summary</h1> ... </section>
</body>
```
`tools/md_to_doc.py` writes this from Markdown with a front matter block (its docstring gives the syntax), so most
documents start as Markdown. `tools/build.py` adds the theme's document art (`themes/<id>/doc.css`), fonts, icons
and the runtime; `tools/doc_pdf.py` prints it.

- **Types** (`data-type`): report, paper, proposal, guide, casestudy, letter, memo, onepager, newsletter, cv,
  invoice, agenda, programme. Each sets margins, notes, chapter breaks and cover defaults; letters, CVs, invoices
  and newsletters have their own parts (`pc-letterhead`, `pc-cv-head`, `pc-inv-head` and `pc-inv-totals`,
  `pc-masthead`). The samples show each one.
- **Pages**: `data-page` a4, letter, a5, legal or b5, `data-orient="landscape"`. Each chapter's running head is its title,
  beside the document's `data-short-title` (or its title); the cover and contents carry no head or number.
- **Covers** (`data-cover`): band, type, minimal, full and split (full and split take a picture).
- **Contents and cross-references**: `nav.pc-toc` fills itself, and `<a class="pc-ref" href="#id">` shows the page
  of its target. `doc_pdf.py` prints twice so both carry real page numbers, and the PDF gets bookmarks, title,
  author and subject.
- **Notes**: `<span class="pc-note">` in running text; `data-notes="side"` (in the outer margin), `"end"` or
  `"foot"` (at the page foot, laid out by Paged.js).
- **Parts**: chapter openers (`div.pc-opener` with a `pc-opener-num`: a page of its own with a big number;
  `openers: page` in Markdown), numbered headings (`data-numbered` on `<html>`), lead
  paragraph (`pc-lead`), drop cap, pull quote (`pc-pull`), callouts (`pc-callout` note, tip, warning, key, with an
  icon and a word), sidebar, key figures (`pc-keyfigs`), facts list, two and three columns (`pc-cols-2`), wide
  figures (`pc-wide`), numbered figures and tables (`figure.pc-fig`, `table` with a caption), booktabs tables,
  charts (`pc-chart`, the deck markup), timeline, steps, checklist, code, agenda, references (`pc-refs`), appendix
  (lettered), signature block, QR codes. Deck components such as cards (`pc-grid`) work too.
- **Screen view**: opened in a browser, a built document shows as a column of pages; the PDF is what you share.
- **Credits**: a theme ported from another project credits it in the PDF properties and a closing line.

## Graphics
A graphic is a deck with `data-medium="graphic"`: each slide is one design (a post, a banner, the front of a card),
with every slide layout, component, chart and theme art, and no page numbers or notes. Set the format to the
platform:

| Format | Size | For |
|---|---|---|
| `1x1` | 1080 x 1080 | square post |
| `4x5` | 1080 x 1350 | portrait post |
| `9x16` | 1080 x 1920 | story, reel cover |
| `16x9` | 1920 x 1080 | video thumbnail |
| `191x100` | 1200 x 627 | link preview, LinkedIn or Facebook post |
| `3x1` | 1500 x 500 | X header |
| `4x1` | 1584 x 396 | LinkedIn banner |
| `a4p`, `a4l` | A4 | flyer and poster; prints at A5, A4, A3 or A2 |
| `5x7` | 127 x 178 mm | invitation |
| `letter-p` | US Letter | flyer |
| `card` | 85 x 55 mm | business card (front and back as two slides) |

`tools/export_graphic.py` writes each slide as a PNG at the platform size and at 2x (`--jpg` adds JPGs), and a PDF.
X and LinkedIn crop a profile picture over the lower left of a banner: add `pc-clear-left` to the slide to keep words
out of the left third. On banners the theme art shrinks to 60% so it stays clear of the text.

**Print.** `--print` writes `<name>-print.pdf` at the real size with 3 mm bleed (`--bleed`): the background and art
run into the bleed, the content keeps its place inside the trim, and every page carries its TrimBox and BleedBox.
`--size` prints a4p or a4l at a5, a4, a3, a2 or letter, or at any size in mm of the same shape (`--size 500x707mm`).
`--press` adds `<name>-press.pdf` for a print shop: CMYK on a press profile (`--profile fogra39`, `gracol`,
`uncoated` or the shop's own `.icc`), PDF/X-4, and with `--marks` crop marks. Ask the shop for its bleed and
profile.

## QR codes
`<img class="pc-qr-code" data-qr="https://example.org/join" alt="Join the garden">` in any deck, document or graphic
becomes a QR code when built, in near-black on white with its quiet zone, so phones read it on any theme. On a slide, size it
with `style="--qr-size: 300px"` on its `figure.pc-qr`; in a document it is 24 mm square unless its own style sets
`width` and `height`. `data-qr-level="q"` gives stronger error
correction where a logo or wear may cover part of it. `tools/qr.py "<text>" -o code.svg` writes one as a file.

## Themes
Sixty themes in 17 categories. Each has three or more palettes and a light and a dark mode, and each carries its
own art (shapes, patterns, frames) for decks and for documents. The picker groups them by category; a theme listed
under "also" shows in that category too.

| Category | Themes | Also |
|---|---|---|
| academic | Litera (bookish serif, calm blue), Seminar (running heads, numbered figures and tables), Thesis (Garamond, double-ruled title page) | Journal, Lab |
| bold | Bauhaus (primary colours, circles and quarter discs), Bloom (big friendly shapes, dotted fields), Brite (thick outlines, hard shadows, loud fills), Grid (Swiss, visible column grid, huge numerals) | League |
| business | Boardroom (serif action titles, navy rail), Meridian (progress line with the section name), Sandstone (warm paper, slate and burnt orange), United (orange and aubergine bands) | Annual |
| creative | Collage (cut paper on kraft, handwriting), Gallery (wall labels, matted pictures), Quartz (frosted glass over a violet glow), Studio (wide display face, mono captions) | Risograph |
| dark | Dracula (the code colours), Night (near-black, amber glow), Noir (spotlight glow, cinema bars) | Aurora, Lanterns, Vapor |
| editorial | Broadsheet (front-page headline, column rules), Folio (folio lines, italic section numerals, drop caps), Journal (news sans over a serif, coral) | Letterpress, Litera |
| education | Chalk (board texture, marks that draw on), Gaia (cream paper, sky blue, stripes), Minty (mint and pink, gentle blobs) | Blocks, Sketchy |
| engineering | Blueprint (drawing grid, title block), Field Manual (stencil caps, hazard stripes), Lab (rings and dots, mono for units), Schematic (graph paper, corner marks, red mark-up) | |
| events | Confetti (dots, stars and bursts), Lanterns (indigo night, lantern glows), Occasion (centred invitation, gold double rules), Wedding (blush paper, frames and leaf sprigs) | |
| finance | Annual (Baskerville figures, quarter discs), Flatly (flat midnight and turquoise), Ledger (ticker strip, accounting rules), Quant (dense, mono figures, faint grid) | |
| kids | Blocks (toy bricks, thick outlines), Crayon (handwritten titles, stars and squiggles), Sketchy (sketched headings, doodles) | Confetti, Pop |
| luxury | Atelier (high-contrast serif, gold hairline frames), Lux (black, white and gold, spaced capitals), Marble (Bodoni, faint veining) | Noir, Wedding |
| minimal | Mono (black and white, hairlines), Simple (one deep blue), Uncover (centred, one blue rule), Zen (light sans, one brush ring) | |
| retro | Letterpress (wood type, slab titles), Risograph (two inks, halftone), Seventies (rainbow arcs), Vapor (synthwave sun over a grid) | |
| startup | Launch (navy, violet glow), League (tall condensed capitals, sporty bar), Pop (colour blocks, cut-out shapes), Superhero (navy, hot orange, sunburst) | |
| tech | Aurora (northern-light glows, frosted cards), Signal (dot grid, status bar, block cursor), Solar (Solarized colours, sun of rays) | Dracula, Launch, Night, Quant |
| wellness | Grove (pebbles and leaves, soft shadows), Sky (pale blue, gentle wave), Tide (foam and navy, layered waves) | Minty |

`themes/themes.json` holds each theme's summary, uses, palettes and fonts. Custom themes from `tools/make_theme.py`
sit beside these, marked "Your theme" in the picker.

## Formats
Decks: `16x9` 1920 x 1080, `4x3` 1440 x 1080, `1x1` 1080 x 1080, `4x5` 1080 x 1350, `9x16` 1080 x 1920, `a4p`
1080 x 1527, `a4l` 1527 x 1080. Graphics add `191x100`, `3x1`, `4x1`, `5x7`, `letter-p` and `card` (table above).
Type sizes are set per format; long display titles step down to keep to three lines (four on 9:16), figures in a
stats row step down to fit their cells, and hyphenated words in titles stay on one line. Documents have pages
instead (`data-page`).

## Tools
| Tool | What it does |
|---|---|
| `tools/pick_style.py` | serves the style picker for a brief (`--medium`, `--kind`, `--title`, `--suggest`) and prints the pick as JSON (`--build` rebuilds it and every preview) |
| `tools/md_to_deck.py` | Markdown outline to a deck source (syntax in its docstring; example `samples/outline.md`) |
| `tools/md_to_doc.py` | Markdown with front matter to a document source (examples in `samples/docs/*.md`) |
| `tools/build.py` | deck, document or graphic source to one self-contained HTML, with style overrides (`--theme`, `--palette`, `--mode`, `--format`, `--motion`) |
| `tools/qc.py` | builds and checks a deck in one or more formats (`--formats all`), with contact sheets |
| `tools/doc_pdf.py` | prints a document to its PDF with page numbers, bookmarks and properties (`--print --marks` for a press copy) |
| `tools/qc_doc.py` | checks a document and its PDF and draws a contact sheet of every page |
| `tools/export_graphic.py` | PNG, JPG and PDF of every design at platform size; `--print`, `--size`, `--bleed`, `--press`, `--marks` |
| `tools/print_ready.py` | turns a PDF into a CMYK PDF/X-4 press file with trim and bleed boxes and crop marks |
| `tools/qr.py` | QR codes (build.py inlines them; the command writes one as an SVG) |
| `tools/to_pptx.py` | the 1:1 PowerPoint converter for decks (`--check`, `--powerpoint`, `--keep`) |
| `tools/publish.py` | QC, then one-file HTML with the PDF and PowerPoint inside it, both saved beside it (`--check`, `--png`); stops on QC issues |
| `tools/make_theme.py` | a custom theme copied from a reference (PowerPoint theme or file, PDF, picture; `--office` lists the Office themes on a Mac), or from a logo, brand guidelines, design tokens, flags or a style spec (`--spec style.json --out <job>/style`, a job's own theme used with `--theme-dir`); checks it in every format (`--check` again) |
| `tools/motifs.py` | the shapes, patterns and frames theme art is made of, and the art recipe format |
| `tools/build_themes.py` | rebuilds every theme's tokens and `themes/themes.json`, moving colours that fail contrast |
| `tools/selftest.py` | checks the kit works on this computer (decks, outline, PowerPoint, a graphic and its print) and draws an overview of every theme |
| `tools/fetch_assets.py`, `build_icons.py` | add fonts and icons (downloads: ask the user first) |
| `tools/add_fonts.py` | add font families already on the Mac (a folder of `<Family>-<Style>.ttf` files with OFL licences) |

## Known limits
- Sinhala and Tamil: basic support only. Decks with either script need the extra checks in SKILL.md.
- Google Slides shows PowerPoints in Arial; the layout holds, the type differs. Share the PDF for an exact copy.
- Complex motion is for the screen; its PDF and PowerPoint show finished slides.
- Videos play in the HTML only; PDF and PowerPoint show the poster frame.
- Documents are PDFs: there is no Word copy. Page numbers count from the cover (no roman front matter).
- Press files follow PDF/X-4, but no free validator certifies them: the print shop's preflight has the last word.

## Licences
The kit's own code, themes and samples: MIT. What it holds from others:
- Fonts: 84 families from Google Fonts, 83 under the SIL Open Font License 1.1 and Roboto Slab under Apache 2.0;
  each family's licence file sits in `fonts/`.
- Icons: Lucide, ISC licence.
- Themes ported from open projects, all MIT, each credited in its `theme.json` and in what it builds (the last
  slide's speaker notes of a deck; the PDF properties and a closing line of a document):
  - Bootswatch by Thomas Park: Brite, Flatly, Journal, Litera, Lux, Minty, Quartz, Sandstone, Sketchy, Superhero,
    United, Vapor; Solar also uses Ethan Schoonover's Solarized colours (MIT).
  - reveal.js by Hakim El Hattab and contributors: League, Night, Simple, Sky.
  - Marp by the Marp team: Gaia, Uncover.
  - Dracula by Zeno Rocha and contributors: Dracula.
- Palettes from open colour schemes, all MIT: Nord by Arctic Ice Studio and Sven Greb (Aurora's Nord palette),
  Catppuccin by the Catppuccin team (Dracula's Catppuccin palette), Rosé Pine by the Rosé Pine team (Zen's Rosé
  Pine palette).
- Paged.js 0.4.3 (MIT) lays out documents with footnotes at the page foot: `tools/vendor/pagedjs/`.
- segno (BSD 3-clause) draws QR codes: `tools/vendor/segno-LICENSE.txt`.
- Print profiles in `assets/icc/`: Coated FOGRA39 (VIGC) and GRACoL 2013 (Idealliance), free to use, embed and
  share; PSO Uncoated v3 FOGRA52 (ECI) may be used and embedded but not passed on, so the kit does not include it.
- The Markdown splitting and notes syntax follow md-slides (MIT).
