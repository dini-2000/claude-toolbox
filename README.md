# Claude Toolbox

A one-stop collection of the best Claude Code skills, settings and optimizations, set up so they cost almost nothing until used. It holds 587 skills from 15 open-source collections, an essentials pack for anyone getting started, and settings that keep Claude's writing plain, save its progress before a usage limit and screen what it downloads.

The skills belong to their original creators (see [Credits](#credits)). This repo collects them, fills in the files they were missing, fixes what was broken and packages the lot so one install sets it up.

---

## Start here

New to skills? Install the **essentials**: 26 skills for planning, building, debugging, reviewing, research and writing, plus the two essential settings. You can add the rest later.

Want everything? Install **all 587**. Only five sit in Claude's skill list; the rest stay on disk until a task needs them, so a full install costs about as much context as the essentials.

## Install

Clone the repo to a folder of its own and run `setup.sh` from there:

```bash
git clone https://github.com/dini-2000/claude-toolbox.git claude-toolbox
cd claude-toolbox && ./setup.sh
```

`setup.sh` asks two questions: the essentials or every skill, and which settings to turn on. It copies the skills into `~/.claude/skills` next to any you already have. To answer up front, pass flags:

```bash
./setup.sh --essentials --settings=essentials
./setup.sh --all --settings=all
```

On Windows, run these in Git Bash, which comes with [Git for Windows](https://git-scm.com/downloads/win). `setup.sh` needs Python 3 and finds it as `python3`, `python` or `py -3`; where this page says `python3`, use whichever of those works.

Already running an older copy of this collection? Follow [UPDATE.md](UPDATE.md): it removes the skills that were dropped and the per-prompt hooks older copies installed.

Restart Claude Code, then check that the skill search works:

```bash
python3 ~/.claude/skills/skill-router/find.py "plan a new feature"   # writing-plans first
python3 ~/.claude/skills/skill-router/find.py "SOC 2 audit"          # soc2-compliance first (full install)
```

### What `setup.sh` does

- Copies the skills you chose into `~/.claude/skills`, and trims the skill index to match.
- Writes a block into `~/.claude/CLAUDE.md` between markers: short writing rules, token-saving rules, and a pointer to the on-demand skills. `--no-rules` keeps only the pointer.
- Turns on the settings you chose, after backing up `~/.claude/settings.json`.
- Removes the per-prompt hooks that older copies added.
- Downloads nothing. `--with-massgen` is the one optional extra; `--uninstall` removes the block and the hooks.

---

## The essentials

The list lives in [`essentials.txt`](essentials.txt). Edit it before running `setup.sh --essentials` to make your own pack.

| Area | Skills |
|---|---|
| Finding skills, writing and context | `skill-router`, `stop-slop`, `context-optimization` |
| Planning and building | `brainstorming`, `grill-me`, `writing-plans`, `executing-plans`, `subagent-driven-development`, `using-git-worktrees`, `test-driven-development`, `systematic-debugging`, `verification-before-completion`, `requesting-code-review`, `receiving-code-review`, `finishing-a-development-branch` |
| Code quality | `karpathy-coder`, `code-reviewer`, `focused-fix`, `codebase-onboarding` |
| Front end and testing | `frontend-design`, `webapp-testing` |
| Research and documents | `deep-research`, `research-summarizer`, `doc-coauthoring` |
| Extending Claude | `write-a-skill`, `mcp-builder` |

The full install adds skills for finance and market data, strategy and board advice, SEO and marketing, sales, product, cloud and DevOps, security and compliance, design, data and more. [`skills/skill-router/INDEX.md`](skills/skill-router/INDEX.md) lists them all by area.

## Settings

Hooks that run in every session. [`settings/README.md`](settings/README.md) explains each one and how to turn it on or off.

| Setting | Tier | What it does |
|---|---|---|
| `stop-slop` | essential | Keeps Claude's writing plain: the stop-slop checks at session start, a reminder on writing requests, and a lint on the prose files Claude saves. |
| `save-before-limit` | essential | Has Claude save its progress to `HANDOFF.md` before the chat is compacted or a usage limit ends the session. |
| `dictation-check` | optional | Flags prompts that read as speech-to-text, so Claude reads them for intent. |
| `security-guidance` | optional | Stops an edit the first time it brings in one of 12 common security mistakes. |
| `download-guard` | optional | Sends Claude's downloads and installs through `safe_get.py`, which checks fingerprints, quarantines and screens each file before use. Built and tested on macOS. |

---

## How the skills stay cheap

A plain skills folder puts every skill's description into Claude's context in every session. For about 500 skills that comes to roughly 49,000 tokens, and Claude Code cuts the list off once it outgrows its budget, so many skills end up invisible anyway. This collection works the other way round.

**1. Always on, about 870 tokens per session.** Five skills stay in Claude's list (about 300 tokens of descriptions): `skill-router`, `stop-slop`, `context-optimization`, `systematic-debugging` and `verification-before-completion`. The `CLAUDE.md` block adds about 570 tokens of writing and token rules that apply to every reply, and the rule for the skill check below.

**2. A brief check per task, about 250 tokens.** At the start of a substantive task (research, analysis, a document, deck or build), the block asks Claude to run `skill-router/find.py` with three to six key terms, batched with its first tool calls. The script ranks the catalog on your machine in about 50 ms and prints the five closest skills and how much of the task the best one covers. Below 45% it says no skill covers the task, and Claude carries on without one unless a skill's method clearly helps. Follow-ups, quick questions and chores skip the check.

**3. The index, read only when needed.** `skill-router/catalog.tsv` holds one line per skill, for `find.py` to rank and for grep. `skill-router/INDEX.md` groups the skills by area and lists each one's section headings.

You can still call any skill directly as `/name`. To put a skill in Claude's list for good, delete the `disable-model-invocation: true` line from its `SKILL.md`. Keep that set small: it is the only part that costs context in every session.

---

## What differs from the sources

`_build/build_pack.py` builds the tree and checks its own work.

- **Missing files restored.** The source collections often shipped a skill's `SKILL.md` without the scripts, references and assets it names. This repo adds 2,191 of those files, each taken from the skill's own upstream repo at the commit its text was written against, checked against git's hash and screened for malware. [`_build/vendor/MANIFEST.tsv`](_build/vendor/MANIFEST.tsv) lists every one with its source, along with the files of the collections taken whole. No skill points at a file that isn't there.
- **Two families and a hook restored whole.** The `agenthub` family (parallel agents working in git worktrees) and the `autoresearch` family (an experiment loop that keeps what improves a metric) come straight from upstream, along with `security-guidance`. Their `/hub:x` and `/ar:x` commands are installed as `/hub-x` and `/ar-x`, so none replaces a Claude Code command. Upstream's `run_experiment.py` hard-resets whatever branch is checked out after a failed run; the copy here first checks that it is on an `autoresearch/` branch with every tracked change committed.
- **Three collections taken whole.** 14 skills from `mattpocock/skills`, 23 from `addyosmani/agent-skills` and 69 from `trailofbits/skills` come unchanged from upstream at pinned commits, screened like the rest. Trail of Bits' plugin-level files that some of its skills need (agent prompts, the `ct_analyzer` package, a README) sit inside those skills, and `differential-review`, `sharp-edges` and `dimensional-analysis` run their agents as general-purpose subagents when Trail of Bits' plugin isn't installed.
- **No skill pre-approves tools.** The build removes `allowed-tools` from every skill's frontmatter, so Claude Code asks you before a skill runs commands, as it would for any other task.
- **Agent files added.** 25 skills link to agent definitions (`agents/cs-*.md`) that never came with them. They are here, unchanged from upstream.
- **Fixes**, each listed with its base commit in [`_build/fixes/SOURCES.md`](_build/fixes/SOURCES.md): `banner-design`, `brand`, `design-system` and `epic-design` completed with the helpers their texts describe, and links to omitted skills replaced in `executing-plans`, `demo-video`, `full-page-screenshot`, `universal-scraping-architect` and `engineering-advanced-skills`, and links that pointed outside their skill fixed in `performance-optimization`, `security-and-hardening` and `yara-rule-authoring`.
- **15 skills omitted**, each with its reason in [`_build/omitted.tsv`](_build/omitted.tsv): stale copies of Anthropic's `docx`, `pdf`, `pptx`, `xlsx` and `skill-creator` (install Anthropic's maintained versions instead); an outdated `claude-api`; the six-skill self-improving family, which rewrites `MEMORY.md` and `CLAUDE.md` in competition with Claude Code's own memory; `using-superpowers`, which tells Claude it has no choice but to invoke a skill; and `notebooklm` and `browser-automation`, which rely on hiding automation from websites. A further 40 skills from the three collections taken whole were left out, with reasons in the same file: names that would replace Claude Code commands or skills already here, near-duplicates, skills that only work through their plugin's agents, commands or hooks, a Dockerfile that pipes install scripts into bash, and a few too narrow for a general collection.
- **41 duplicates dropped**: 12 byte-identical copies, and 29 pairs doing the same job with the fuller one kept, such as `seo-local` over `local-seo-manager`. Skills that only sit near each other, like `pw` and its sub-commands, stay.
- **`stop-slop` completed** with its reference files and MIT licence from `hardikpandya/stop-slop`, plus one fix: an example used an em dash, which the skill itself bans.
- **9 Playwright commands renamed** `pw-*`, since `init` and `review` would otherwise replace `/init` and `/review`.
- **Frontmatter repaired.** 12 descriptions held an unquoted `": "`, which is invalid YAML, and Claude Code ends frontmatter at the first `---` even inside a quoted value. The build quotes the first and refuses to ship the second.
- **`disable-model-invocation: true`** on every skill except the five always-on ones, and cross-references rewritten for the renamed commands.

### Good to know

- 13 skills save notes under `~/.claude`. The catalog flags them as `saves-to-~/.claude`.
- Some skills need an API key or a paid data source (the `sec-*` and `earnings-*` families use Octagon, for instance), and some scripts need Node.js, `uv` or tools such as Semgrep and CodeQL. Each skill says so.
- This is for Claude Code: the CLI, the desktop app and the IDE extensions. claude.ai chat has no local filesystem and can't use these skills.
- Skills are heuristics written for the average case. The router and the `CLAUDE.md` block both tell Claude to adapt or skip one when its own approach is better, and never to let a skill override your instructions.

---

## Optional extra: massgen

`setup.sh` describes this and installs nothing unless you ask:

> massgen (PyPI: `massgen`) is a third-party CLI that runs several LLM agents in parallel on one problem and reconciles their answers. It needs Python 3.11 or newer and your own API keys for the providers it calls (OpenAI, Anthropic, Gemini, xAI and others), billed separately from any Claude subscription. Claude Code's own subagents cover most of the same ground.

```bash
./setup.sh --with-massgen
```

## Updating

```bash
cd claude-toolbox && git pull && ./setup.sh
```

To rebuild from a fresh upstream collection, put the raw `<name>/SKILL.md` folders somewhere and run:

```bash
python3 _build/build_pack.py <raw pack dir>                     # stage and validate only
python3 _build/build_pack.py <raw pack dir> --repo=<this repo>  # write the built tree here
python3 _build/build_pack.py <raw pack dir> --install           # install straight to ~/.claude/skills
```

It needs `python3` and `/usr/bin/ruby` for the YAML check, and stops before writing if any skill fails validation. With `--repo` it replaces only the skill folders in `skills/` and the build files under `_build/`.

## Uninstall

```bash
cd claude-toolbox && ./setup.sh --uninstall
for d in skills/*/; do rm -rf "$HOME/.claude/skills/$(basename "$d")"; done
rm -rf ~/.claude/hooks/claude-toolbox
```

Run these from the clone. The first line removes the `CLAUDE.md` block and the settings' hook entries. The second removes each skill this repo installed and leaves skills of your own in place. The third removes the hook scripts.

## Credits

The skills belong to their original authors, under their own licences:

`anthropics/skills` · `obra/superpowers` · `mattpocock/skills` · `addyosmani/agent-skills` · `trailofbits/skills` · `hardikpandya/stop-slop` · `coreyhaines31/marketingskills` · `nextlevelbuilder/ui-ux-pro-max-skill` · `remotion-dev/skills` · `muratcankoylan/agent-skills-for-context-engineering` · `AgriciDaniel/claude-seo` · `kepano/obsidian-skills` · `borghei/claude-skills` · `OctagonAI/skills` · `alirezarezvani/claude-skills`

Some skills in those collections adapt other people's work, and their `SKILL.md` names the original: Matt Pocock for `caveman`, `grill-me`, `grill-with-docs` and `write-a-skill`, adapted from his earlier versions, with `skills-handoff` based on his `handoff`; and, from the Pro Hub Challenge in `AgriciDaniel/claude-seo`, Lutfiya Miller for `seo-cluster`, Dan Colta for `seo-drift`, Matej Marjanovic for `seo-ecommerce` and Florian Schmitz for `seo-sxo`, with puneetindersingh for `seo-content-brief`.

[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) gives each source's licence text and the commits the files came from. Trail of Bits' skills are under CC BY-SA 4.0, so the adapted copies here stay under that licence. Check a source's licence before you redistribute its work.

The toolbox's own work is under the MIT licence in [LICENSE](LICENSE): `setup.sh`, the essentials pack, the `skill-router` search, the build scripts in `_build/`, and the settings in `settings/`. Those are the download guard (`download_guard.py`, with the `safe_get.py` downloader and the `screen.py` checks), save-before-limit, the dictation check and the stop-slop hooks, which apply the rules from `hardikpandya/stop-slop`.
