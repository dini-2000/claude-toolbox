# Settings

Hooks that change how Claude Code works in every session. Each is a Python script that `install.py` copies to `~/.claude/hooks/claude-toolbox/` and lists in `~/.claude/settings.json`.

| Setting | Tier | What it does |
|---|---|---|
| `stop-slop` | essential | Keeps Claude's writing plain: loads the stop-slop checks at session start, reminds Claude of them on writing requests, and lints the prose files Claude saves. |
| `save-before-limit` | essential | Asks Claude to write down where a task stands before the chat is compacted or a usage limit ends the session. |
| `dictation-check` | optional | Flags prompts that read as speech-to-text, so Claude reads them for intent and checks the words a mishearing would change. |
| `security-guidance` | optional | Stops an edit the first time it brings one of 12 common security mistakes into a file. Needs the `security-guidance` skill. |
| `download-guard` | optional | Sends Claude's downloads and installs through `safe_get.py`, which checks fingerprints, quarantines and screens each file before use. Built and tested on macOS. |

## Turning them on and off

`setup.sh` asks which ones you want, or takes `--settings=essentials`, `--settings=all` or `--settings=none`. To change them later, run `install.py` from the repo folder:

```bash
python3 settings/install.py list
python3 settings/install.py on essentials
python3 settings/install.py on dictation-check
python3 settings/install.py off save-before-limit
python3 settings/install.py off all
```

`on` and `off` take setting names or `essentials`, `optional` and `all`. Before each change, `install.py` copies `settings.json` to `settings.json.bak-<date>-<time>`. It never touches hooks you added yourself, and running `on` twice replaces its entries instead of adding a second copy. Restart Claude Code afterwards so it reads the new settings.

On Windows, use whichever of `python3`, `python` or `py -3` works. `setup.sh` passes the one it found to `install.py`, which writes it into each hook command.

## stop-slop

Needs the `stop-slop` skill, which is in the essentials. It adds three hooks:

- At session start, Claude gets the Quick Checks from the skill: a short list of the tells that make text read as machine-written, to run on every draft.
- When a prompt asks for writing (an email, a report, a summary, slides, a reply and so on), Claude gets a one-line reminder to run the checks.
- After Claude saves a `.md`, `.html` or `.txt` file, a lint scans the whole file after a write, or only the edited lines after an edit. It looks for em dashes, the phrases in the skill's `references/phrases.md` and the contrasts described in `references/structures.md`, and tells Claude what it found and where. Clean text prints nothing, and the lint never blocks a save. It skips working files: anything under `~/.claude`, hidden folders, `node_modules`, and files named `CLAUDE.md`, `NOTES.md`, `MEMORY.md`, `SKILL.md` or `HANDOFF.md`. It also skips code blocks and text in double quotes, since quoted words belong to someone else.

The lint also runs on any file from a terminal, and exits with 1 when it finds something:

```bash
python3 ~/.claude/hooks/claude-toolbox/stop_slop_lint.py README.md
```

## save-before-limit

A long task can stop without warning in two ways. Claude Code compacts the chat when it nears the context limit, so older turns survive only as a summary, and a plan's usage limit can end the session mid-step. This setting has Claude save its progress to `HANDOFF.md`, in the folder Claude Code runs in, before either happens. The save lists what is done, the files changed, the next step, decisions with their reasons, approaches dropped and open questions.

- **Context.** After each tool call, the hook reads the chat's size from the transcript. At 85% of the point where Claude Code compacts, it asks Claude once to bring `HANDOFF.md` up to date. That point is the auto-compact window less the 33K tokens Claude Code keeps free: 167K by default, or taken from `CLAUDE_CODE_AUTO_COMPACT_WINDOW` or `autoCompactWindow` in `settings.json` when you set one. The hook asks again only after the chat has dropped below 60% of that point, as it does after a compaction.
- **Usage, in the Claude desktop app.** Only the desktop app lets Claude read the plan's usage. There, the hook asks Claude to check it now and then, more often as usage rises: every 30 minutes or 40 tool calls below 50%, down to every 2 minutes or 3 tool calls above 88%. At 90% and again at 97% of the 5-hour or weekly limit, it asks Claude for the save and shows you a notice. In the terminal, the hook watches context only.
- **Cut-off.** When a usage limit ends a turn, the hook adds a dated line to `HANDOFF.md`. If there is no such file, it starts one with your last request, so the next session knows what was under way.

To pick up, start a new session in the same folder and ask Claude to read `HANDOFF.md` and carry on. To use another file name, set the `SAVE_BEFORE_LIMIT_FILE` environment variable, for example in the `env` block of `settings.json`.

## dictation-check

Speech-to-text prompts carry fillers, false starts and misheard words. The hook weighs signs of speech (uh and um, repeated words, spoken phrases, numbers spelled out) against signs of typing (abbreviations, paths, code, brackets, a lowercase "i"). When speech clearly wins, Claude is asked to read the prompt for intent, to treat names, numbers, dates and negatives with care, and to open its reply with one line restating the ask, so you can catch a mishearing before work starts. Typed prompts print nothing and cost no tokens. Clean dictation without uh or um reads like typing and passes unflagged.

If speech-to-text often garbles particular names (people, products, places), list them, comma-separated, in the `DICTATION_TERMS` environment variable. The note then tells Claude that odd words may be garbled forms of them.

## security-guidance

The `security-guidance` skill holds this hook; `install.py` points `settings.json` at the skill's own script, so turn the setting on only with that skill installed. Before Claude edits or writes a file, the hook checks the new text for 12 risky patterns, including shell command injection, `eval` and `new Function`, `innerHTML` and `document.write`, `dangerouslySetInnerHTML`, unsafe `pickle` loads, SQL built with string formatting, and untrusted input in GitHub Actions workflows. The first time in a session that one of them goes into a given file, the hook stops that edit and tells Claude the risk. Claude can then fix the code, or make the same edit again, which goes through. Set `ENABLE_SECURITY_REMINDER=0` to silence it for a while without removing it. The skill's `SKILL.md` lists every pattern.

## download-guard

Three scripts: `download_guard.py` (the hook), `safe_get.py` (the downloader) and `screen.py` (pattern and package checks). Before Claude runs a shell command, the hook looks for downloads and installs that skip screening: `curl` or `wget` saving a file, `git clone`, `pip`, `uv`, `npm`, `brew` and other installers, Python scripts that fetch and save binary files, and copies out of `~/Downloads`. It stops the command and names the `safe_get.py` command to use instead. A few things it blocks outright: a download piped into a shell, running or mounting a downloaded file, installer packages, removing macOS's quarantine flag and turning Gatekeeper off. Reads that print to the screen, `git pull`, `fetch` and `push`, and `safe_get.py` itself go through. After Claude uses a browser tool, the hook names any new files in `~/Downloads` and the command that screens them.

`safe_get.py` works in steps, so you see what comes in before anything uses it:

```bash
python3 ~/.claude/hooks/claude-toolbox/safe_get.py plan pypi:requests==2.32.3   # look it up, download nothing
python3 ~/.claude/hooks/claude-toolbox/safe_get.py fetch <job> --yes "<your go-ahead>"
python3 ~/.claude/hooks/claude-toolbox/safe_get.py release <job> <folder>       # or: install <job>
python3 ~/.claude/hooks/claude-toolbox/safe_get.py intake ~/Downloads/file.pdf  # files that came another way
```

`plan` takes `github:owner/repo[@ref][:path]`, `url:https://...`, `pypi:name==version`, `npm:name@version` and `brew:formula`. `fetch` downloads over https only into `~/Quarantine.noindex/<date>-<name>/`, checks each file against its published fingerprint (git blob SHA, PyPI sha256, npm integrity, Homebrew sha256 or a GitHub release digest) and screens it without running anything: ClamAV when installed, `screen.py`'s checks, and checks by file type for programs, PDF actions, Office macros, archive tricks, hidden characters and text that gives instructions to an AI. `release` and `install` refuse anything that has not passed or been cleared, and both are logged in `ledger.tsv` in the quarantine folder.

Optional extras: ClamAV (`clamscan`) for malware signatures, PyMuPDF for deeper PDF checks, `uv` for `pypi:` specs and Homebrew for `brew:` specs. Without ClamAV the report notes that no signature scan ran; without PyMuPDF the PDF checks search the raw file instead. Set `SAFE_GET_QUARANTINE` or `SAFE_GET_DOWNLOADS` to move the quarantine or the downloads folder. The tests are in `settings/tests/`. `screen.py` and the tests hold samples of the attacks they catch, written as text and never run, so a malware scanner run over this repo may flag them.

## Removing them

`python3 settings/install.py off all`, or `./setup.sh --uninstall`, takes the entries out of `settings.json`. The scripts stay in `~/.claude/hooks/claude-toolbox/` until you delete that folder.
