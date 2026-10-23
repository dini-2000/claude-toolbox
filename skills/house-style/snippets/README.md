# Snippets: parts the engine lacks

A deck moves from one theme to another by changing its theme options alone (SKILL.md, "Changing a deck's theme").
A deck from a PowerPoint, a PDF or another kit is rebuilt slide by slide in the engine's parts (`pc-`). Most slides
have an engine part that carries the same message. For the few that do not, this folder has parts that take any
theme's colours, fonts and corners:

- `parts.css`: bars with estimates and a target line (`pcx-hbar`), the share bar (`pcx-share`), the flow map
  (`pcx-flow`), chart titles and notes (`pcx-chart-title`, `pcx-note`), zebra table rows (`pcx-zebra`), status chips
  with a mark (`pcx-status`, `pcx-chip--no`, `--planned`, `--emerging`), a dotted edge for planned items
  (`pcx-planned`), inline code, keys and mono figures, and hover tips (`data-tip`).
- `parts.js`: draws those parts. Load it after the slides and before `engine/runtime.js`.

```html
<link rel="stylesheet" href="../themes/meridian/theme.css">      <!-- the theme, as README.md says -->
<link rel="stylesheet" href="../snippets/parts.css">
...
<script src="../snippets/parts.js"></script>
<script src="../engine/runtime.js"></script>
```

`tools/build.py` inlines both files, so the built deck stands alone, and draws each `pcx-hbar`, `pcx-share` and
`pcx-flow` into the no-script copy. Each file's comments list the attributes a part takes.

Use them with the engine's own parts first: a bar chart with highlighted rows only is `figure.pc-chart`
`data-type="bar"` with `data-highlight`; one bar of many parts can be a `stacked` chart; status chips use
`pc-chip pc-chip--good pcx-status` and `pc-chip--warn pcx-status` for in and partial, and `pc-chip pcx-chip--no
pcx-status`, `pcx-chip--planned` or `pcx-chip--emerging` for the rest; planned cards are `pc-card pcx-planned`.
