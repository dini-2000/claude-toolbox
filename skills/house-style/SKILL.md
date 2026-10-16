---
name: house-style
description: Design and build slide decks, paged PDF documents and graphics with this kit (talks, lessons, pitches, reports, papers, proposals, letters, CVs, invoices, newsletters, social posts, banners, posters, invitations, business cards), in one of 60 themes or a custom brand theme. Decks ship as one HTML file with its PDF and an editable PowerPoint; documents as print-quality PDFs; graphics as PNG, JPG and print-ready PDF with bleed.
disable-model-invocation: true
---

# House Style

This folder is House Style, a design kit for three media that share one set of themes:
- **Decks**: slides in HTML, with the PDF and an editable PowerPoint that matches it 1:1.
- **Documents**: paged PDFs (reports, papers, proposals, guides, letters, memos, CVs, invoices, one-pagers,
  newsletters, agendas, event programmes) with covers, contents, running heads, notes and page numbers.
- **Graphics**: one design per slide, sized for a platform (posts, stories, banners, link previews) or for print
  (flyers, posters, invitations, business cards, certificates).

`README.md` is the reference for the markup, components, themes, formats and tools. `samples/showcase.html` uses
nearly every deck part, `samples/docs/` and `samples/graphics/` give a working example of each document type and
graphic, and `guide/structures.json` gives each slide layout's markup.

Run the tools from this kit folder and give files by their full path. On Windows, type `py` in place of `python3`.

## 1. Style
Claude chooses the look unless the user asks to pick it. Weigh what the kit offers for the piece (README's Themes
table groups the 60 themes by category; the layouts, components, motifs, icons and fonts) and use as much or as
little of it as suits the piece: build in a theme directly, borrow parts of one, take ideas for a design of your own,
or set the kit aside. Name the choice and why in one line at delivery. "Try it in Folio" or "darker" afterwards is a
rebuild with overrides.
- **A built theme**: choose the theme, palette and mode that suit the subject, audience and goal, and build.
- **Something new**: when no theme fits, or the user asks for it ("design something new", "surprise me", "go
  creative"), write a short concept (audience, tone, the idea behind the look, type pair, palette, motifs, pictures)
  and turn it into a style spec (A theme of its own, below). When the user asked for it, first show the cover and two
  or three inner slides or pages in it beside the theme you would otherwise pick, as the safe option; the user
  approves, steers ("warmer", "less busy") or takes the safe option, and "just go" skips this look.
- **The user picks**: only when the user asks to pick a theme or choose the style themselves ("I'll choose", "show
  me the themes"), or opens the picker with a command of their own. Then use the picker below.
In every way Claude adapts the theme to the piece without changing the theme itself: layouts and components per
slide or page, cover and section variants, the accent within the palette, a motif that suits the topic, chart styles
and density. Name these choices in one line at delivery so the user can undo any. "Keep the theme exactly" means
layouts and components only.

**The picker** (only when the user asks to pick). Run `python3 tools/pick_style.py --medium deck|document|graphic --kind <kind> --title "<title>"
--suggest <id>,<id>,<id>` as a background command, open the address it prints in the browser pane (or give it to
the user), and wait for the command to print the pick. `--kind` is a deck structure from `guide/structures.json`, a
document type (report, letter, cv ...) or a graphic format (1x1, 4x1 ...); `--suggest` names the three or four
themes that suit the content best. The page asks how to choose, what is being made, then theme (grouped by
category, suggestions first), colour, format or page (with cover and notes for documents) and motion for decks, and
shows the sample deck in each choice with the real title on its cover. The pick comes back as one line of JSON with
`how` (pick, auto or creative), `medium` and the choices. Each run is fresh: a new token, no memory of the last
project. Save the chosen style in the project's notes (theme, palette, mode, format) so later work there reuses it
without the picker. Opened from disk, the page shows a pick code for the user to paste. Without a browser, offer
the top suggestions with AskUserQuestion.

Decks get basic motion (Motion below) unless the user says otherwise or picks another in the picker; name it in
the delivery line. Ask static, basic or complex only when the user is picking the style. Documents and graphics
have no motion.

## 2. Write
Plain, specific language (Content rules below). Every medium takes `data-theme`, `data-palette`, `data-mode`.

**Deck.** Start from a structure from `guide/structures.json` (slide goals in order, each with a layout and a
surface; the picker gives one when the user picked), or the user's outline. Either copy the slides you need from `samples/showcase.html` into a new file in the deck's own folder,
with the same `<link>` and `<script>` lines pointed at this kit, and set `data-format` and `data-motion` on
`<div class="pc-deck">`; or write Markdown and run `python3 tools/md_to_deck.py talk.md -o "<folder>/talk.html"`
(`---` between slides, `<!-- notes: -->` blocks, a layout guessed from each slide or set with
`<!-- layout: name -->`; `samples/outline.md`). Read the result, then add icons, charts and pictures where they
help. One message per slide; speaker notes in `<div class="pc-notes">`.

**Document.** Write Markdown with a front matter block (title, subtitle, author, date, theme, palette, type, page,
cover, toc, notes, numbered, openers) and run `python3 tools/md_to_doc.py report.md -o "<folder>/report.html"`. Its
docstring gives the syntax: footnotes, figures with captions, tables, callouts, task lists, charts in fenced
`chart` blocks, page breaks, cross-references, and fenced divs for sidebars, columns, pull quotes, key figures,
timelines, agendas, steps, facts, signatures and references. Letters and memos read their addresses, subject and
signature from the front matter. CVs, invoices and newsletters have their own layouts: copy the nearest file in
`samples/docs/` (`cv.html`, `invoice.html`, `newsletter.html`) and edit it. Read the generated HTML and improve it
where Markdown fell short.

**Graphic.** Copy the nearest file in `samples/graphics/` (posts, banner, link preview, poster, invitation, business
card, certificate) and set `data-format` for the platform (README's Graphics table). Each `<section class="pc-slide">`
is one design; any slide layout and component works. One idea per design, large type, few words: people see a post
for a second on a phone. On X and LinkedIn banners add `pc-clear-left` to keep words clear of the profile picture.
QR codes: `<img class="pc-qr-code" data-qr="https://..." alt="...">`, which the build turns into a code (also in
decks and documents).

## 3. Check
A clean check is necessary, not sufficient: look at every slide, page and design yourself before anything goes out.
- **Deck**: `python3 tools/qc.py "<deck>.html" --formats <format> -o <out folder>` builds the one-file deck, opens
  it alone in its folder in headless Chrome and checks overflow, clipping, overlap, contrast, small text, fonts,
  icons, charts and the copy for viewers without scripts. Fix every issue, then look at every contact sheet
  (`sheet-NN.png`). Dense slides (more than six bullets or 200 words) are noted, not failed: split the slide or move
  detail to the notes, unless it is meant to be dense.
- **Document**: `python3 tools/doc_pdf.py "<doc>.html" -o "<folder>/<Name>.pdf"` builds it to
  `<folder>/dist/<name>.html` and prints it, then `python3 tools/qc_doc.py "<folder>/dist/<name>.html" <pdf>` checks the HTML and the PDF (blank pages, headings stranded at a page
  foot, fonts, links, anything wider than the text column, a nearly empty last page) and draws a contact sheet.
  Look at every page at full size where text is small.
- **Graphic**: `python3 tools/qc.py "<graphic>.html" --formats <format> -o <out>` runs the deck checks on it; then
  export (step 4) and look at every PNG at its real size.

## 4. Share
- **Deck**: `python3 tools/publish.py "<deck>.html" -o "<folder>/<Deck name>.html" --check` writes the one-file HTML
  with Download > PDF and PowerPoint inside it, and both files beside it (the same files in every browser, Safari
  and iPhone included). `--png` adds one picture per slide. Publishing runs QC first and stops on any issue: fix the
  deck and publish again. Only when you have looked at an issue and it is a false alarm, publish with
  `--accept "<why>"` and tell the user what was accepted. Publish again after any change. Then the PowerPoint QC below.
- **Document**: the PDF from `doc_pdf.py` is the deliverable, with bookmarks, page numbers and its title, author and
  subject in its properties. For a print shop, add `--print --marks` (CMYK, PDF/X-4, crop marks).
- **Graphic**: `python3 tools/export_graphic.py "<graphic>.html" -o "<folder>"` writes each design as a PNG at the
  platform size and at 2x, and a PDF; `--jpg` adds JPGs. For print, `--print` writes the real-size PDF with 3 mm
  bleed (`--size a3` and so on for posters, `--bleed` for another bleed), and `--press --marks` the CMYK PDF/X-4
  press file. Ask the user which print shop or printer it is for: shops give their bleed and colour profile
  (`--profile fogra39`, `gracol`, `uncoated` or their `.icc`); a home or office printer needs only the print PDF.

Any piece can change theme, palette, mode or format without a rewrite: `build.py`, `publish.py`, `qc.py` and
`export_graphic.py` take `--theme`, `--palette`, `--mode` and `--format` to override what the file says.

## A theme of its own
`tools/make_theme.py <id> --base <theme>` puts new colours and fonts on a built theme's layout and artwork, moves any
colour that fails contrast (and says so), and the picker then lists the theme first as "Your theme". A custom theme
works for documents and graphics too. Ways in:
- **Copy a reference**: `--reference <file>` takes the colours, fonts and light or dark ground of a PowerPoint theme
  or file (`.thmx`, `.potx`, `.pptx`, including its colour variants as extra palettes), a PDF of a deck, or a
  picture of a slide. On a Mac with PowerPoint, `--office` lists the Office themes it installed, and
  `--reference "office:Ion"` copies one.
- **A brand**: `--logo <file>` (colours read from a logo), `--brand <guidelines.md>`, `--tokens <design-tokens.json>`,
  or flags: `--accent`, `--accent-2`, `--display`, `--body`, `--light-bg`, `--dark-bg` and the rest.
- **Invent one** when no built theme suits the subject: choose the base whose artwork fits, two accent colours that
  suit the subject and read well together, and a display and body pair from `--fonts`, then make it with flags.
  Show the user the check's overview before building in it.
- **A style spec** (creative mode): `--spec style.json --out <job>/style [--formats 16x9]`. The spec is a theme.json
  in part: `base`, `name`, `fonts`, `palettes`, `defaults` and an `art` recipe. Art slots: `deck` (cover, section,
  content, statement, closing) and `doc` (cover, opener, mark), each a list of up to two motifs from
  `tools/motifs.py` placed with `at` (tl, tr, bl, br, t, b, l, r, c, full), `w`, `h` or `size`, `x`, `y`, `color`,
  `opacity`, `fade` and `fade_to`. Shapes keep their proportions inside the box; bands (wave) stretch to it unless
  the motif says `"stretch": false`. `vars` sets type sizes per slot (`{"cover": {"--k-hero": ".9"}}`), and a
  `slot@narrow` key applies on square, portrait and print formats only (`"cover@narrow": {"--cover-w": "100%"}`), for
  titles that run to four lines there. Banners draw the deck art at 60% by themselves. Keep art clear of the cover's
  meta lines and the slide number: the check fails text over art on contrast. Without `art` the base's artwork is
  copied. The style stays in the job's folder, its check in `<job>/style/check`; build in it with
  `--theme-dir <job>/style` on build.py, selftest.py, md_to_deck.py, md_to_doc.py and export_graphic.py (or set
  `PC_THEME_DIRS`, which child tools inherit). Offer to save the style for the project and name it in the project's
  notes.

Fonts: a theme uses only families the kit holds (`--fonts` lists them). A face the kit lacks is matched to the
nearest held family (Century Gothic to Poppins, Calibri to Lato, Arial to Roboto, Garamond to EB Garamond, Rockwell
to Roboto Slab), and the tool says so. A Google family can come in exactly as a download: ask the user first, naming
the font, where it comes from and its size, then add it with `tools/fetch_assets.py`.

**The check.** Every new theme is checked as soon as it is made: the showcase deck in all seven deck formats, an
outline deck, a PowerPoint and a graphic with its print PDF, in light and dark mode, with an overview sheet
(`selftest/theme-<id>/overview.png`). Read its summary, fix what it finds by remaking the theme, then look at the
overview and the contact sheets: QC finds overflow, contrast and missing fonts, not a theme that looks wrong.
`--check <id>` runs it again. Until a custom theme passes, `build.py` says so and `publish.py` will not publish in it.

## Motion (decks)
Set on the deck: `data-motion="static"`, `"basic"` or `"complex"`. No mode has slide transitions, and PowerPoints
are never animated (decks often go through Google Drive, which drops animations).
- **Static**: nothing moves. The HTML, the PDF and the PowerPoint show the same slides.
- **Basic** (the default): content builds as each slide opens. Mark what builds with `data-build` on an element or
  `data-build-each` on a container (`rise`, `fade`, `pop`, `wipe`, `grow`, `draw`, `converge`); charts draw on and
  hand-drawn marks draw themselves. Keep builds to the content that carries the slide's message.
- **Complex** (best on screen): basic plus figures that count up, a cover title whose words slide in from both sides
  and meet, the cover's other text rising after it, and a slow zoom on full-bleed and side pictures
  (`data-drift="no"` on the picture's container turns that off). People who ask their computer for less motion get
  the finished slides.
Print, the PDF and the PowerPoint show every slide finished in every mode.

## PowerPoint QC (decks, every time, before sharing)
1. Convert with `--check` (publish.py passes it on): every deck needs its LibreOffice, Arial and Google Slides tests.
   Add `--powerpoint` (a Mac with PowerPoint; a view-only copy is enough) after a change to the converter, before a
   release of the kit, or when the user asks. PowerPoint saves the file as PDF in `tools/powerpoint-check` and every
   line is compared with the HTML; the first run on a Mac shows PowerPoint's Grant File Access window for that
   folder, so ask the user to click Grant Access, once. The test quits PowerPoint when done, unless it was already
   open.
2. Every test line must pass. Report any that does not, with the slide numbers.
3. Look at every slide of the PowerPoint against the HTML (`to_pptx.py --keep <folder>` keeps the PDFs it compared).
   Fix problems in the HTML and convert again; never patch the PowerPoint by hand or rebuild slides in python-pptx.
   If the converter gets something wrong, say which slide and what, plainly.
4. After `publish.py`, open the one-file HTML, check that Download offers PDF and PowerPoint, and look at every page
   of the PDF.
Google Slides ignores fonts embedded in a PowerPoint and shows Arial, so the type looks different there, but every
line and shape stays in place. For an exact copy anywhere, share the PDF.

## Sinhala and Tamil (basic support)
The kit is built and tested for English. Sinhala and Tamil text shows correctly in the HTML and the PDF (the kit
holds Noto Sans and Noto Serif for both, and labels step up 20% for them), and the converter takes their text from
the page so the PowerPoint has the right letters. It has not been tuned further: anything that uses either script
needs more checking than usual. The converter prints a warning naming the slides with such text. Run it with
`--check --powerpoint --keep <folder>`, look at every one of those slides in PowerPoint and in Google Slides, and
tell the user plainly what differs from the HTML before it is shared.

## Content rules
- Plain, specific language, in the register of a capable everyday writer. No em dashes.
- Decks: one message per slide, and the title says it. Depth goes in the speaker notes. Documents: headings say
  what the section finds or asks, and the summary comes first. Graphics: one idea, a few words, the call to action
  and the date or address where people need them.
- Figures say what they count, where and when; estimates are labelled as estimates. Status labels carry text, never
  colour alone.
- Everything speaks about the subject to a reader who never saw the request. Leave out lines about the piece itself:
  its purpose or scope, how it was made, how to read it, what was left out as asked, how it differs from an earlier
  version. Meet a constraint by leaving things out, without saying so.
- Speaker notes give facts the slide does not show (figures, sources, names, reasoning), in the words the presenter
  would say. No coaching on how to present and no remarks on the deck. A slide with nothing to add gets no note.
- Credits: a theme or palette ported from another project names it, in the last slide's speaker notes of a deck and
  in the PDF properties and closing line of a document; the build adds both.
- Use only icon names the kit holds (Lucide; the runtime warns about unknown names and QC reports them).
- Pictures come from the user or are drawn for the piece; the kit fetches none.

## Choosing a chart
| The data | Use |
|---|---|
| One headline figure | A big number (`pc-big`) or a row of stats (`pc-stats`, `pc-keyfigs` in documents), not a chart |
| A few items compared, up to about 15 | Bar or column chart |
| Parts of one whole, up to five | Donut or stacked bar; with more parts, put the smallest together as Other |
| Change over time, four points or more | Line or area chart; with fewer points, columns or big numbers |
| How a total builds up or falls | Waterfall |
| Progress against a goal | Progress bars |
| Exact values people will look up | Table (`pc-table` on slides; a captioned table in documents) |
Label values on the chart itself and never tell items apart by colour alone. One scale per chart.

## Tools this needs
Python 3 with `pymupdf`, `python-pptx` and `Pillow`; Google Chrome (or Chromium or Edge; set `CHROME_PATH` if it is
somewhere unusual); LibreOffice for `--check`; PowerPoint on a Mac for `--powerpoint` (optional). Paged.js and segno
come with the kit (`tools/vendor/`). If a tool is missing, say so and give the install command; do not fall back to
another method. On a new computer, run `python3 tools/selftest.py --quick` once (or without `--quick` for every
theme) and look at its `overview.png`.

## Fonts and icons
84 font families, all free to embed and share (SIL Open Font License, Roboto Slab Apache 2.0; licences in `fonts/`,
sources in `fonts/fonts.json`), and Lucide icons (ISC). A deck, document or graphic embeds only the faces and icons
it uses. PowerPoints embed the fonts too and keep their Google names, so Google Slides can use its own copies where
it has them.
