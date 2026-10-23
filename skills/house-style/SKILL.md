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
graphic, `samples/creative/` is a Creative-mode job (a style spec with a drawn emblem, a deck and a report in it),
and `guide/structures.json` gives each slide layout's markup.

Run the tools from this kit folder and give files by their full path. On Windows, type `py` in place of `python3`.

## First use
The first time the kit is used on a computer (no file named `.first-use-done` in this kit folder, the folder this
file is in), give the person the welcome below before any work, in these words or close to them, then set the kit
up as the steps after it say. When both are done, create that empty file so later chats skip them; if the folder
cannot be written to, give the welcome once in each chat. Give the welcome again whenever someone asks what the kit
can do. If the person asked for something, start on it once the set-up is done.

> With this kit I can make three kinds of work, in one of 60 themes or a look designed for you:
> - **Presentations**: an HTML deck you present in the browser, with a PDF and an editable PowerPoint (.pptx) that
>   also opens in Google Slides. Slides can carry charts, key figures, timelines, maps, flags, QR codes, code and
>   speaker notes, with motion in the HTML deck if you want it.
> - **Documents**: reports, papers, proposals, guides, letters, memos, CVs, invoices, newsletters, one-pagers,
>   agendas and event programmes, as PDFs ready to print.
> - **Graphics**: social posts, stories, banners, link previews, flyers, posters, invitations, business cards and
>   certificates, as PNG, JPG or a print shop's PDF.
>
> You can attach what I should work from, such as notes, a draft, figures, an outline or an existing deck, and a
> reference for the look, such as a deck, document, brand guide, logo or screenshot in the style you want. From a
> reference I take the style only. I can move a deck to another theme slide for slide or redesign it, and save a
> look for a project so later pieces match. When a piece needs a picture, icon or map the kit lacks, I fetch one
> safely from the web once you agree, or make one to match the theme. Before you get a file, I check every slide
> and page, and the PowerPoint against the deck.
>
> First I set a few things up, once, and ask before I install or change anything. I need:
> - **Tools to make the files**: Python packages and Google Chrome.
> - **LibreOffice**, to test every line of each PowerPoint against the deck.
> - **PowerPoint**, on a Mac, to check each deck in PowerPoint itself. No Office licence is needed for this.
> - **The kit saved**, so it is here in every chat.
>
> Optional: **Google Slides**, if your decks go to people who open them there. For Slides you add Claude in Chrome,
> the browser extension, to a Chrome signed in to your Google account; I upload each deck to one folder of your
> Drive, "Deck checks", and leave the rest of your Drive alone.
>
> If something can't be set up, I tell you which check your work loses. Then tell me what you need. I choose a look
> that suits each piece and name it when I deliver, unless you want to pick a theme yourself or have me design
> something new.

Set-up, the first time. Go through the steps in order. Ask before installing anything or changing a setting, and
explain each step in a line. Steps 1 to 4 are needed for a good result (step 4 on a Mac only). Step 5 is optional:
offer it in a question of its own. If the person cannot or will not do a step, say in a line which check their work loses, and do the
step later if they ask.

1. Run `python3 tools/setup_check.py`. It lists what the tools need and what is missing, with the command or link
   for each: Python packages and Google Chrome to make files, and LibreOffice and, on a Mac, PowerPoint to test
   them (no Office licence needed). Offer to install missing Python packages and run the command on a yes. Apps the person installs, or
   you install with the command it gives once they agree. Run it again until "To make files" and "To test them"
   both say all present.
2. Save the kit for later use. When the check says Claude Code does not find the kit from any folder (it arrived as
   a zip in the chat, or sits in Downloads or a temporary folder), offer to copy the whole kit folder to
   `~/.claude/skills/<name>`, where `<name>` is the `name:` at the top of this file (on Windows,
   `%USERPROFILE%\.claude\skills\<name>`). On a yes, copy it, work from that copy, and create `.first-use-done`
   there. Claude Code then loads the kit from any folder whenever someone asks for a deck, document or graphic.
3. Run `python3 tools/selftest.py --quick -o <a scratch folder>` (a few minutes) and look at its `overview.png`. It
   builds and checks one theme in every format, an outline deck, its PowerPoint and graphics, so a fault on this
   computer shows before real work.
4. PowerPoint's permission, on a Mac. Run `python3 tools/to_pptx.py samples/showcase.html -o <a scratch
   folder>/showcase.pptx --check --powerpoint`. The first run asks the person to let the app control PowerPoint and, in PowerPoint, to click Grant Access for the
   kit's `tools/powerpoint-check` folder; both are needed once.
5. Google Slides, through Claude in Chrome. The person adds the Claude in Chrome extension to Chrome, connects it to
   Claude, and signs that Chrome in to their Google account. Check that the browser tools answer and which Google
   account Drive shows, then create the folder "Deck checks" in their Drive. The Google Drive connector cannot do
   this check, since it passes files through the chat and a deck is far too large; if it is connected, it can still
   find, read and clear the copies in that folder.

Then say in one line what is ready and which checks the work will get (for example, LibreOffice and PowerPoint, but
not Google Slides).

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
For a deck, ask which files the person wants, with the first option recommended: **HTML, PowerPoint and PDF**
(the HTML presents in any browser with motion and design touches the others cannot carry, and its Download button
gives the PDF and PowerPoint at any time); **PowerPoint** with its PDF; **PDF** only; or **HTML** only. Whatever the
answer, publish as below, which writes all three, and hand over the files asked for, the main one first.
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

## Attached files
People attach two kinds of file, sometimes both in one request: sources for the content and references for the look.
Tell them apart from the request, and ask in one line when a file could be either.
- **Sources** (notes, drafts, reports, figures, spreadsheets, outlines, existing decks) give the content. Read each
  in full and build from it, keeping its figures, names, dates and sources as given; point out gaps and never fill
  them with guesses. Read PDFs and pictures directly, a PowerPoint with python-pptx, and a Word file after converting
  it to PDF with LibreOffice (`soffice --headless --convert-to pdf`) or, on a Mac, to text with `textutil -convert txt`.
- **References** (a deck, a document, a brand guide, a logo, a screenshot or a photo) give the look only: colours,
  type, layout, spacing and the feel of the artwork. Never reuse a reference's words, figures, pictures or logos
  unless the person asks. A reference names the style, so skip the look question. Make the look with
  `tools/make_theme.py` ("A theme of its own"): `--reference`, `--logo` or `--brand`. Offer to save it as the
  project's style.
- An existing deck to put in another theme follows "Changing a deck's theme".

## Changing a deck's theme
When someone gives you a deck (HTML, PowerPoint or PDF) to put in another theme, or asks for an existing deck in a
new look, ask one question unless they have said:
1. **Same slides, new theme** (recommended, and the default for any theme change): every slide keeps its message,
   order, words, figures, sources and notes.
2. **Redesign in the new theme**: keep the message and the facts, and plan the slides afresh with the theme's own
   layouts.
3. **Keep its design**: correct and tidy the deck in its current look.
For the same slides in a new theme:
- Between two of the kit's themes, change the theme options (`data-theme`, `data-palette`, `data-mode`,
  `data-format`, or `--theme` on `build.py` and `publish.py`). The markup stays as it is.
- From a PowerPoint, a PDF or another kit's deck, rebuild each slide in the engine's parts. Use the new theme's own
  part wherever one carries the same message (its charts, bars, facts, timeline, chips and tables), and the parts in
  `snippets/` (README there) for the few the engine lacks: bars with estimates or a target, a share bar, a flow map,
  status chips, planned items.
- A part may take the new theme's own form, and the theme's signature details are welcome, as long as each slide
  says the same thing and follows good design practice: one message per slide, values labelled, enough contrast, no
  meaning carried by colour alone. Where a slide's words describe its look ("the blue bar"), change the words to
  match the new drawing.
- Run the QC and look at each new slide beside its original.

## Detail in every theme
Give every deck the care `samples/showcase.html` shows: icons where they help, values labelled on charts, small
charts inside tiles, status chips with words, a sources line and page numbers, plus the theme's own signature parts
(its motifs, rules, numerals, frames and artwork). A deck from `md_to_deck.py` is a first draft: add this detail
before the QC.

## A theme of its own
`tools/make_theme.py <id> --base <theme>` puts new colours and fonts on a built theme's layout and artwork, moves any
colour that fails contrast (and says so), and the picker then lists the theme first as "Your theme". A custom theme
works for documents and graphics too. Ways in:
- **Copy a reference**: `--reference <file>` takes the colours, fonts and light or dark ground of a PowerPoint theme
  or file (`.thmx`, `.potx`, `.pptx`, including its colour variants as extra palettes), a PDF of a deck, or a
  picture of a slide. On a Mac with PowerPoint, `--office` lists the Office themes it installed, and
  `--reference "office:Ion"` copies one.
- **A template's own artwork**: add `--art` to a PowerPoint reference to lay its cover, content and section artwork
  behind slides in the template's format (16:9 or 4:3) and mode. Text colours are tuned against the art under each
  text box, text stays inside the template's own text boxes, and a layout whose text would fail contrast is left
  out with a warning (Office Berlin fails at 3.7:1). `--credit "Template: <name> by <author>, <licence>"` stores
  the credit in the theme, never in the work. The kit's package
  leaves custom themes out, so a template's artwork never ships with the kit.
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

## Drawn art (the craft loop)
For a logo, emblem, icon or a piece of cover art the motifs don't have. Draw it from exact shapes, look at it at every
size, and refine it before anyone else sees it.
1. **One idea.** Write one line on what the mark stands for and where it goes (app icon, slide corner, document
   cover). One idea per mark, one or two colours, nothing that echoes a known brand's mark.
2. **Draw on a grid** with `tools/mark.py` (its docstring has the shapes): true circles and arcs, corners rounded
   with real arcs, strokes turned into outlines, text from a kit font as outlines. Keep key points on the grid or its
   halves, and keep stroke widths and gaps equal across the mark. Draw three or four candidates that differ in idea.
3. **Run the loop**: `python3 tools/art_loop.py a.svg b.svg ... -o <job>/art/loop --round 1` (add `--word "Name"
   --font <family> --weight 600` for a lockup, `--theme <id>` for the theme's grounds). It draws a sheet (256 px on
   light and dark, 64 to 16 px, one colour, pixel views, an app icon, a browser tab, the lockup), a 1024 px render and
   a construction view of each, and flags off-centre weight, parts too thin or gaps too narrow for 16 px, colours
   under 3:1 on either ground, near-misses of symmetry, and strokes. Look at the sheet and read the report.
4. **Refine at least twice** before showing anything. Each round fixes what the sheet shows: a shape that reads as
   something else, a join that leaves a notch, a part lost at 16 px. Optical corrections: round shapes slightly
   larger than square ones (`overshoot`), the weight's centre on or just above the middle, equal gaps, thinner
   horizontals where strokes cross. Drop candidates that fail; keep the round's files.
5. **Show two or three finalists** on the last sheet, say which you prefer and why, then `--export` the chosen one
   (PNGs from 16 to 1024 px and a favicon).
6. **Put it in a theme**: `mark.save_shape(shape, 'x.svg', 24)` writes a one-colour shape, and a style spec's
   `"art": {"shapes": {"x": "art/x.svg"}}` makes `x` a motif in any colour token, light and dark. A mark with holes
   cut through overlapping parts goes in as two shapes laid on each other: the solid in `accent`, the cut-out parts in
   `bg` (`samples/creative/` does this with its emblem).

When a mark needs free-drawn curves (a figure, calligraphy, a mascot) or more finish than geometry gives, suggest
Claude Design at claude.ai/design with a ready prompt: the idea, the use, the colours, "flat vector, one or two
colours, works at 16 px", and the candidates so far. Bring its SVG back through `art_loop.py` for the size and
one-colour tests.

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
5. When the deck goes to people who open it in Google Slides, or after a change to the converter, check it there too
   (Claude in Chrome, set up in First use): upload the PowerPoint to the "Deck checks" folder, open it in Slides, look
   at every slide against the HTML, then move the upload to the bin.
Google Slides ignores fonts embedded in a PowerPoint. It shows a deck's Google font where it has the same family and
Arial where it does not, so the type can look a little different there, but every line and shape stays in place. For
an exact copy anywhere, share the PDF.

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
- No credits in the work: never credit the kit's themes, fonts, icons, skills or their licences on slides, in notes,
  documents, graphics or file properties (a PDF names only the kit as its creator). Their licences ask nothing of
  the work made with them; the kit keeps them in `README.md` and each theme's `theme.json`, and the build carries a
  ported theme's notice in a hidden comment.
  The one exception is a CC BY asset fetched for the piece: credit it in the slide's sources line.
- Use only icon names the kit holds (Lucide; the runtime warns about unknown names and QC reports them).
- Pictures come from the user, the kit, or as "Flags, maps and other assets" says.

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
somewhere unusual); LibreOffice for `--check`; PowerPoint on a Mac for `--powerpoint`. Paged.js and segno
come with the kit (`tools/vendor/`). If a tool is missing, say so and give the install command; do not fall back to
another method. `python3 tools/setup_check.py` lists what is present and what is missing; on a new computer, go
through First use, above (`python3 tools/selftest.py` without `--quick` checks every theme).

## Fonts and icons
84 font families, all free to embed and share (SIL Open Font License, Roboto Slab Apache 2.0; licences in `fonts/`,
sources in `fonts/fonts.json`), and Lucide icons (ISC). A deck, document or graphic embeds only the faces and icons
it uses. PowerPoints embed the fonts too and keep their Google names, so Google Slides can use its own copies where
it has them.

## Flags, maps and other assets
Look in the kit first: Lucide icons (`icons/`), the flags of 270 countries and regions, a world map and maps of Sri
Lanka's districts and provinces (`assets/README.md` says how to use them), theme art (`tools/motifs.py`, the craft
loop), 84 font families and QR codes (`tools/qr.py`).

When nothing in the kit fits, fetch the asset safely from the web, or generate or build one. To fetch one, take it
from a well-known source whose licence lets the person use it and pass it on: public domain, CC0, MIT, ISC, Apache or
the SIL Open Font License. Skip anything without a stated licence. Tell the person what it is, where it comes from,
its size and its licence, and download it only on their yes, through their screened download step if they have one.
Otherwise fetch only over HTTPS and only picture, PDF or font files, never run anything downloaded, and read an SVG
as text before using it: no scripts, event handlers, links to other sites or embedded pages. Keep the file in the
project's folder with its licence beside it.

To generate or build one, draw it as SVG in the theme's tokens (an icon in Lucide's style: 24 by 24, a 2 px stroke,
round caps and joins, no fill), build it from the kit's parts or `tools/mark.py`, or, after asking, use an image tool
the person has connected. Emblems, logos, flags and borders come from their owners or a trusted dataset, never
redrawn from memory, and another organisation's logo goes in only with the person's agreement.
