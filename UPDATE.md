# Updating from the older install

This is for anyone who installed this collection (then called `claude-skills`) before the curated layout: your `~/.claude/skills` holds ~536 skills, every one of them in Claude's skill list, a `[skill-router]` hook echoes the same reminder on every prompt, and `~/.claude/CLAUDE.md` carries a routing block telling Claude to run a routing pass before answering anything.

On Windows, run the commands below in Git Bash, and use `python` or `py -3` where one says `python3`.

You are on the old setup if either of these prints something:

```bash
grep -c "skill-router" ~/.claude/settings.json; ls ~/.claude/skills | wc -l
```

A count near 536 means the old skill set. What changes: five skills stay in Claude's list and the rest cost nothing until used, the per-prompt echo gives way to a quick skill search Claude runs at the start of substantive tasks, and ~49,000 tokens of descriptions stop loading in every session.

---

## The update

Move the old folder aside, clone the repo to a folder of its own and run `setup.sh` from there. This works whether you cloned the old collection into `~/.claude/skills` or copied it in with the old `install.sh`:

```bash
mv ~/.claude/skills ~/.claude/skills.old        # keep it until you are happy
git clone https://github.com/dini-2000/claude-toolbox.git claude-toolbox
cd claude-toolbox && ./setup.sh --all
```

The skills sit in the repo's `skills/` folder, and `setup.sh` copies them into `~/.claude/skills`, so the clone is no longer the skills folder itself. `setup.sh` also removes the old echo hook (and the `skill_hint.py` hint hook, if your copy had it) and replaces the routing block in `~/.claude/CLAUDE.md` between its markers. If you edited skills, read "If you edited skills yourself" below.

Then move any skills of your own back in from `~/.claude/skills.old`, and delete that folder when you are done.

**If you cloned `claude-toolbox` to a folder of its own** and `git pull` refuses to merge, the history on GitHub was rewritten. Reset your clone to it:

```bash
cd claude-toolbox
git fetch origin
git reset --hard origin/main
./setup.sh
```

**Restart your Claude Code session.** The skill list and the `CLAUDE.md` block only load when a session starts.

---

## Check it worked

```bash
find ~/.claude/skills -maxdepth 2 -name SKILL.md | wc -l             # 587, plus any of your own
grep -c "skill_hint.py" ~/.claude/settings.json                      # 0, the hint hook is retired
grep -c "\[skill-router\] Before answering" ~/.claude/settings.json  # 0, the old echo is gone
python3 ~/.claude/skills/skill-router/find.py "SOC 2 audit"          # soc2-compliance first
```

In a new session, ask Claude which skills it can see: you want `skill-router`, `stop-slop`, `context-optimization`, `systematic-debugging` and `verification-before-completion`, and nothing else from the pack. Then try a prompt like "prepare us for a SOC 2 audit": Claude should run the skill search before starting and name `soc2-compliance`.

---

## What to remove, by hand

- **The old hooks.** `setup.sh` takes them out. To check yourself, look in `~/.claude/settings.json` for a `UserPromptSubmit` entry whose command starts with `echo '[skill-router] Before answering` or runs `skill_hint.py`.
- **The memory-parity file**, if you ran the old `setup.sh --with-memory`. Delete `skill-selection.md` from each `~/.claude/projects/*/memory/` folder and the line pointing at it in that folder's `MEMORY.md`. It duplicates the `CLAUDE.md` block, and its wording is the version this update replaces.
- **The Excel MCP server**, if you registered it and never used it: `claude mcp remove excel`. The `xlsx` skill covers spreadsheets. Keep it if you use it.
- **massgen**, unless you actively use it. The old `setup.sh` installed it as an extra. It is now purely optional, for people who want to pay to experiment with APIs: it needs Python 3.11 or newer and your own keys for OpenAI, Anthropic, Gemini, xAI and others, billed separately from your Claude subscription, and Claude Code's own subagents cover most of the same ground.

  ```bash
  uv tool uninstall massgen 2>/dev/null || pipx uninstall massgen 2>/dev/null || python3 -m pip uninstall -y massgen
  ```

  You can add it back any time with `./setup.sh --with-massgen`.

- **The 70 dropped skills**, if you are cleaning up by hand instead of with git: 15 omitted, 41 duplicates and 14 older copies replaced by upstream's complete folders, each with its reason in [`_build/omitted.tsv`](_build/omitted.tsv). Three of the replacements (`agenthub`, `autoresearch-agent` and `security-guidance`) keep their names, so the loop below skips any name the clone still installs. Run it from the clone to prune the rest in one pass:

  ```bash
  tail -n +2 _build/omitted.tsv | cut -f1 | while read -r s; do [ -d "skills/$s" ] || rm -rf "$HOME/.claude/skills/$s"; done
  ```

  The duplicates are pairs where two source packs shipped the same skill, and the fuller one stays: `seo-local` over `local-seo-manager`, `pricing-strategy` over `pricing` and `pricing-strategist`, `analytics-tracking` over `analytics`, `postmortem` over `post-mortem`, `mcp-builder` over `mcp-server-builder`, and so on. Skills that only sit near each other, like the Octagon finance endpoints or `pw` and its sub-commands, were left in place. Remove `loop`, `run`, `resume`, `status`, `init`, `review` and `claude-api` even if you keep everything else, since a personal skill replaces Claude Code's own command or skill of the same name. `loop`, `run` and `resume` now come complete as `ar-loop`, `hub-run` and `ar-resume`; `init` and `review` are the Playwright commands, now `pw-init` and `pw-review`; `status` belonged to the self-improving family, and `claude-api` was outdated. The loop above covers all but `init` and `review`, which the old pack shipped under those names; if yours came from it, remove them with `rm -rf ~/.claude/skills/init ~/.claude/skills/review`.

## What to keep

- **Your own skills.** Only the pack's folders are managed; anything else in `~/.claude/skills` is left alone by `setup.sh`.
- **Anthropic's own `docx`, `pdf`, `pptx` and `xlsx`**, which come from the app or your account, not from here. The pack's stale copies were dropped so they stop shadowing them.

---

## What is always on now, and how to change it

Two things load in every session, about 870 tokens together:

1. **Five skills** stay in Claude's list, so it can pick them itself: `skill-router` (finds the rest), `stop-slop` (prose), `context-optimization` (token and context work), `systematic-debugging` (bugs), `verification-before-completion` (before claiming something is done).
2. **A block in `~/.claude/CLAUDE.md`**, between `<!-- skill-router:start -->` and `<!-- skill-router:end -->`: condensed writing rules, token rules, and a pointer to the on-demand skills. Edit it freely; `setup.sh` only rewrites what is between those markers. Run `./setup.sh --no-rules` if you want the pointer without the writing and token rules.

Everything else is on demand: `disable-model-invocation: true` in its frontmatter keeps it out of Claude's list, while you can still run it as `/name` and Claude can still load it by reading the file.

**To make a skill always on**, delete that line from its `SKILL.md`:

```bash
sed -i '' '/^disable-model-invocation: true$/d' ~/.claude/skills/<name>/SKILL.md   # macOS
sed -i    '/^disable-model-invocation: true$/d' ~/.claude/skills/<name>/SKILL.md   # Linux, Git Bash
```

**To take one back out**, append the line to its frontmatter, above the closing `---`.

Keep that set small. Every skill in it pays its description in every session, which is the problem this layout exists to fix. If a domain matters to you often, it is usually better to leave it on demand and let the per-task search find it.

**To tune the search**, change the `0.45` coverage bar at the end of `~/.claude/skills/skill-router/find.py`: below it, the search tells Claude that no skill covers the task. `_build/build_pack.py` writes that file, so change it there too before a rebuild.

**Settings.** This version also ships optional hooks: plain-writing checks, a save before usage limits, a dictation check, security warnings on edits and a download guard. `setup.sh` asks about them; [`settings/README.md`](settings/README.md) explains each one, and `python3 settings/install.py on essentials` turns on the two essential ones from the clone.

---

## If you edited skills yourself

Your edited copies stay in `~/.claude/skills.old`. `setup.sh` replaces this repo's skill folders each time it runs, so keep an edited skill under a name of its own: copy its folder into `~/.claude/skills` under a new folder name and change the `name:` line in its `SKILL.md` to match.

Skills you wrote yourself are better kept outside this repo, in their own folder under `~/.claude/skills`, where nothing here touches them.

## Going back

```bash
cd claude-toolbox && ./setup.sh --uninstall   # removes the CLAUDE.md block and the toolbox's hooks
mv ~/.claude/skills ~/.claude/skills.new && mv ~/.claude/skills.old ~/.claude/skills
```

If the old folder was a clone, run its own `setup.sh` again to put its routing block back.
