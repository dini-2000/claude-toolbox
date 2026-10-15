# fixes/: what each file is based on

Setup lays these files over the fetched skills, after `vendor/`. A SKILL.md here replaces the skill's text, and setup adds `disable-model-invocation: true` to it. Modified files keep their original licence (THIRD_PARTY_NOTICES.md). When an upstream skill changes, start again from its new text and re-apply only the changes listed here that upstream still lacks.

Upstreams: nextlevelbuilder/ui-ux-pro-max-skill at 477bcb28 (3 Oct 2026) for banner-design, brand and design-system; alirezarezvani/claude-skills at 19392f7a (26 Aug 2026) for epic-design and autoresearch-agent; the pack's own built text for executing-plans (obra/superpowers), demo-video, engineering-advanced-skills, full-page-screenshot and universal-scraping-architect (alirezarezvani/claude-skills).

| File | Based on | Change |
|------|----------|--------|
| autoresearch-agent/scripts/run_experiment.py | upstream 19392f7a | Stops before evaluating unless the checked-out branch is an autoresearch/ experiment branch, tracked files are committed, and HEAD is not already in results.tsv. Upstream hard-resets HEAD~1 on whatever branch is checked out |
| banner-design/SKILL.md | upstream 477bcb28 | Step 4 and Available Resources name `scripts/export-banner.py`; Windows note for it |
| banner-design/scripts/export-banner.py | new | Exports HTML banners at exact pixel sizes with headless Chrome, Chromium or Edge; checks the size; JPEG when a PNG is over `--max-size` |
| brand/SKILL.md | upstream 477bcb28 | None (the pack's copy was older) |
| brand/scripts/sync-brand-to-tokens.cjs | upstream 477bcb28 | Brand name from the guidelines' title instead of "ClaudeKit Marketing - Primary"; starts from design-system's starter tokens when the project has none |
| demo-video/SKILL.md | the pack's text | Cross-reference points at `pw` instead of the omitted browser-automation |
| design-system/SKILL.md | upstream cc3d1be7, plus 477bcb28's "Script Paths" section | Source of Truth table gives each file's origin; step e says when animations run; Chart.js example reads `--color-primary`; the reference deck is `generate-slide.py --demo` |
| design-system/scripts/generate-slide.py | upstream 477bcb28 | Finds the project folder as the skill's other scripts do; links the tokens and animation CSS relative to its output; dark deck; glow classes named primary and accent; uses the animate-* classes with a viewport observer and count-up; notes on missing CSS; `.text-secondary` uses `--color-foreground-secondary` (`--color-secondary` is a surface colour); badges fit their text; centred slides are centred above the footer; space between content and footer; literal ✓ and ◆ (html-token-validator.py reads `&#9670;` as a hex colour); reads `--json` input as UTF-8 |
| design-system/templates/design-tokens-starter.json | upstream 477bcb28 | Adds the tokens generate-slide.py uses: violet, font families, sizes 5xl and 6xl, weights, line heights, glow shadows, easing, gradients, accent and surface colours, `button.primary`, `slide.*`, dark surfaces |
| design-system/templates/slide-animations.css | new | The eight animate-* classes data/slide-layouts.csv names, with the slides skill's names and timings; run on `.active` or `.is-visible`; reduced motion and print handled |
| engineering-advanced-skills/SKILL.md | the pack's text | Drops the Browser Automation row (that skill is omitted) |
| epic-design/assets/hero-section.{html,css,js} | new | The boilerplate SKILL.md points to, built from its references; GSAP 3.12.5 + ScrollTrigger; motion toggle, reduced motion, lite mode on small devices |
| epic-design/references/text-animations.md | upstream 19392f7a | Notes that SplitText is on jsDelivr from GSAP 3.13.0, not 3.12.5, and that CSS cannot set aria-hidden |
| executing-plans/SKILL.md | the pack's text | Points at `references/`, where vendor/ puts using-superpowers' per-platform tool files (that skill is omitted) |
| full-page-screenshot/SKILL.md | the pack's text | Cross-reference points at `pw` instead of the omitted browser-automation |
| universal-scraping-architect/SKILL.md | the pack's text | Related skill is `pw` instead of the omitted browser-automation |
