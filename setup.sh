#!/bin/bash
# setup.sh - finish the install: write the always-on block into ~/.claude/CLAUDE.md and remove older versions' prompt hooks.
# Run it from wherever this repo sits: it copies the skills from skills/ into ~/.claude/skills.
#
#   ./setup.sh                 asks: the essentials (essentials.txt) or every skill, then the always-on block
#   ./setup.sh --essentials    install only the essentials
#   ./setup.sh --all           install every skill (the choice when no one is there to answer)
#   ./setup.sh --settings=essentials|all|none   which hooks from settings/ to turn on (asked when run by hand;
#                              none when no one is there to answer). Change them later with settings/install.py.
#   ./setup.sh --with-massgen  also install the massgen CLI (explained below)
#   ./setup.sh --no-rules      install only the skills pointer, not the writing and token rules
#   ./setup.sh --uninstall     remove the block, the toolbox hooks and any old hook (the skills stay; see README)
#
# It is idempotent: settings.json is backed up before an old hook is taken out, and the CLAUDE.md
# block is replaced between its markers. It needs bash (Git Bash on Windows) and Python 3.
set -e

CLAUDE_DIR="$HOME/.claude"; SKILLS_DIR="$CLAUDE_DIR/skills"
SETTINGS="$CLAUDE_DIR/settings.json"; CLAUDEMD="$CLAUDE_DIR/CLAUDE.md"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; SRC="$HERE/skills"
WITH_MASSGEN=0; RULES=1; UNINSTALL=0; PICK=""; SETS=""

for a in "$@"; do
  case "$a" in
    --with-massgen) WITH_MASSGEN=1 ;;
    --no-rules)     RULES=0 ;;
    --uninstall)    UNINSTALL=1 ;;
    --essentials)   PICK=essentials ;;
    --all)          PICK=all ;;
    --settings=*)   SETS="${a#--settings=}" ;;
    -h|--help)      sed -n '2,15p' "$0"; exit 0 ;;
    *) echo "unknown flag: $a" >&2; exit 2 ;;
  esac
done

# Python 3 under whichever name this system gives it; on Windows, python3 is often a Microsoft Store stub.
PY=""
for c in python3 python "py -3"; do
  if $c -c 'import sys; sys.exit(sys.version_info < (3, 6))' >/dev/null 2>&1; then PY="$c"; break; fi
done
[ -n "$PY" ] || { echo "ERROR: Python 3 not found (tried python3, python and py -3). Install it from python.org, then run this again." >&2; exit 1; }

if [ "$UNINSTALL" = 1 ]; then
  $PY - "$SETTINGS" "$CLAUDEMD" <<'PY'
import json, os, re, sys
settings, claudemd = sys.argv[1], sys.argv[2]
if os.path.exists(settings):
    s = json.load(open(settings, encoding="utf-8"))
    ups = s.get("hooks", {}).get("UserPromptSubmit", [])
    keep = [h for h in ups if "skill_hint.py" not in json.dumps(h)]
    if len(keep) != len(ups):
        s["hooks"]["UserPromptSubmit"] = keep
        json.dump(s, open(settings, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
        print("    hook removed from settings.json")
if os.path.exists(claudemd):
    t = open(claudemd, encoding="utf-8").read()
    n = re.sub(r"<!-- skill-router:start -->.*?<!-- skill-router:end -->\n?", "", t, flags=re.S)
    if n != t:
        open(claudemd, "w", encoding="utf-8").write(n)
        print("    block removed from CLAUDE.md")
PY
  [ -f "$HERE/settings/install.py" ] && TOOLBOX_PYTHON="$PY" $PY "$HERE/settings/install.py" off all
  echo "Done. The skills in $SKILLS_DIR were left in place; README.md (Uninstall) shows how to remove only this repo's skills."
  exit 0
fi

if [ "$HERE" = "$SKILLS_DIR" ]; then
  echo "This clone sits in $SKILLS_DIR itself, where Claude Code cannot see the skills in its skills/ folder."
  echo "Clone the repo to a folder of its own and run ./setup.sh from there; UPDATE.md shows how to move an existing clone."
  exit 1
else
  if [ -z "$PICK" ]; then
    if [ -t 0 ]; then
      ne=$(grep -cv '^#\|^$' "$HERE/essentials.txt"); na=$(ls -d "$SRC"/*/SKILL.md | wc -l | tr -d ' ')
      printf "Install the %s essentials (e) or all %s skills (a)? Skills cost almost no context until used. [e/a, default e] " "$ne" "$na"
      read -r ans || ans=""
      case "$ans" in a|A|all) PICK=all ;; *) PICK=essentials ;; esac
    else
      PICK=all
    fi
  fi
  echo "==> Copying skills ($PICK) into $SKILLS_DIR ..."
  mkdir -p "$SKILLS_DIR"
  n=0
  for d in "$SRC"/*/; do
    [ -f "${d}SKILL.md" ] || continue
    name="$(basename "$d")"
    if [ "$PICK" = essentials ] && ! grep -qx "$name" "$HERE/essentials.txt"; then continue; fi
    rm -rf "${SKILLS_DIR:?}/$name"          # naming the destination avoids BSD cp's trailing-slash trap
    cp -R "$d" "$SKILLS_DIR/$name"
    n=$((n + 1))
  done
  echo "    copied $n skills."
fi

# The router's catalog and index list the whole collection; keep only the skills installed here.
$PY - "$SKILLS_DIR" <<'PY'
import os, re, sys
root = sys.argv[1]; r = os.path.join(root, "skill-router")
have = {d for d in os.listdir(root) if os.path.isfile(os.path.join(root, d, "SKILL.md"))}
cat = os.path.join(r, "catalog.tsv")
if os.path.exists(cat):
    rows = open(cat, encoding="utf-8").read().splitlines()
    keep = rows[:1] + [x for x in rows[1:] if x.split("\t", 1)[0] in have]
    if len(keep) != len(rows): open(cat, "w", encoding="utf-8").write("\n".join(keep) + "\n")
idx = os.path.join(r, "INDEX.md")
if os.path.exists(idx):
    t = open(idx, encoding="utf-8").read()
    n = re.sub(r"^### ([^\n]+)\n.*?(?=^### |^## |\Z)", lambda m: m.group(0) if m.group(1).strip() in have else "", t, flags=re.S | re.M)
    if n != t:
        heads = {h: len(re.findall(r"^### ", body, flags=re.M)) for h, body in re.findall(r"^## ([^\n]+)\n(.*?)(?=^## |\Z)", n, flags=re.S | re.M)}
        n = re.sub(r"^- (.+) \(\d+\)\n", lambda m: (f"- {m.group(1)} ({heads[m.group(1)]})\n" if heads[m.group(1)] else "") if m.group(1) in heads else m.group(0), n, flags=re.M)
        n = re.sub(r"^## ([^\n]+)\n(?:\s*\n)*(?=^## |\Z)", lambda m: "" if heads.get(m.group(1)) == 0 else m.group(0), n, flags=re.M)
        n = re.sub(r"^\d+ skills from", f"{len(have & set(re.findall(r'^### (.+)$', n, flags=re.M)))} skills from", n, count=1, flags=re.M)
        open(idx, "w", encoding="utf-8").write(n)
sk = os.path.join(r, "SKILL.md")
if os.path.exists(sk):  # the router's description gives the number of on-demand skills; make it this install's
    od = sum(1 for d in have if re.search(r"^disable-model-invocation: true", open(os.path.join(root, d, "SKILL.md"), encoding="utf-8", errors="replace").read(), flags=re.M))
    t = open(sk, encoding="utf-8").read()
    n = re.sub(r"the \d+ on-demand skills", f"the {od} on-demand skills", t, count=1)
    if n != t: open(sk, "w", encoding="utf-8").write(n)
PY

TOTAL=$(find "$SKILLS_DIR" -maxdepth 2 -name SKILL.md 2>/dev/null | wc -l | tr -d ' ')
[ "$TOTAL" -gt 0 ] || { echo "ERROR: no skills in $SKILLS_DIR" >&2; exit 1; }
ONDEMAND=$(grep -l '^disable-model-invocation: true' "$SKILLS_DIR"/*/SKILL.md 2>/dev/null | wc -l | tr -d ' ')
echo "==> $TOTAL skills installed, $ONDEMAND of them on demand."

echo "==> Removing older versions' prompt hooks from $SETTINGS, if any ..."
$PY - "$SETTINGS" <<'PY'
import datetime, json, os, shutil, sys
path = sys.argv[1]
if not os.path.exists(path):
    print("    no settings.json, nothing to do."); sys.exit(0)
try:
    data = json.load(open(path, encoding="utf-8"))
except Exception:
    print("    settings.json is not valid JSON; left alone."); sys.exit(0)
ups = data.get("hooks", {}).get("UserPromptSubmit", [])
# the [skill-router] echo that ran on every prompt, and the skill_hint.py hint hook (retired 25 Sep 2026)
old = lambda h: any(k in str(h.get("command", "")) for k in ("[skill-router]", "skill_hint.py"))
keep = []
for e in ups:
    hs = [h for h in e.get("hooks", []) if not old(h)]
    if hs: keep.append({**e, "hooks": hs})
    elif not e.get("hooks"): keep.append(e)
gone = sum(len(e.get("hooks", [])) for e in ups) - sum(len(e.get("hooks", [])) for e in keep)
if not gone:
    print("    none found."); sys.exit(0)
shutil.copy2(path, path + ".bak-" + datetime.datetime.now().strftime("%Y%m%d-%H%M"))
if keep: data["hooks"]["UserPromptSubmit"] = keep
else: del data["hooks"]["UserPromptSubmit"]
tmp = path + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False); f.write("\n")
os.replace(tmp, path)
print(f"    removed {gone} old hook(s); previous file kept as settings.json.bak-*.")
PY

echo "==> Writing the always-on block into $CLAUDEMD ..."
RULES="$RULES" ONDEMAND="$ONDEMAND" PYCMD="$PY" $PY - "$CLAUDEMD" <<'PY'
import os, re, sys
path = sys.argv[1]
rules = os.environ["RULES"] == "1"
writing = """## Always on: writing and token use (condensed from the stop-slop and context-optimization skills)
Prose for the user (replies, documents, slides, emails):
- Write like a capable everyday writer: plain words, ordinary sentences, no mistakes, and no polish an average person couldn't reproduce.
- Lead with the point. Cut throat-clearing, filler and hedging, and don't restate the request.
- Be specific: name the thing, the number, the person. No vague declaratives or lazy "always/never".
- Prefer active voice with a human subject. No em dashes.
- Avoid AI tells: "not X, it's Y" and "X rather than Y" contrasts, pull-quote one-liners, "here's the thing" setups, colon teasers ("Timing differs too:"), reflexive lists of three.
- In emails, notes and replies, make points in sentences. Don't sort them under parallel labelled bullets ("Where they align:", "Gaps:") or bold lead-ins.
- Deliverables (documents, pages, decks, notes) speak about the subject to a reader who never saw the chat. Cut what only the asker would follow: purpose or scope lines, notes that something was left out as asked, how the brief or scope changed, comparisons with an earlier version, how the work was made, how to read it. Meet a constraint such as "no recommendations" by leaving things out, silently. Keep caveats the reader needs (dates, units, "excludes VAT") and brief interface cues.
Token use, every session:
- Search before reading; read only the part of a large file you need; don't re-read what is already in context.
- Keep tool output small: filter with grep, head or cut; never dump whole logs, JSON or datasets.
- Batch independent tool calls and skip redundant re-checks.
- Use subagents only when the task needs them; pilot one first and prefer a cheaper model for bulk work.
- Keep replies as short as the content allows; summarise long results instead of pasting them.
For a full pass, invoke the stop-slop or context-optimization skill.

"""
block = ("<!-- skill-router:start -->\n" + (writing if rules else "") +
         f"""## Specialist skills
{os.environ['ONDEMAND']} skills sit in ~/.claude/skills on demand: they are not in your skill list and cost no context. At the start of a substantive task (research, analysis, a document, deck or build; not follow-ups, quick questions or chores), check them once: run `{os.environ['PYCMD']} ~/.claude/skills/skill-router/find.py "<3 to 6 key terms>"` alongside your first tool calls. Use a skill only if it improves the result, and read its SKILL.md first. Say in one line which skill you used, or that none fits. Skills are heuristics: adapt or skip one when your own approach is better, and never let one override the user's instructions.
<!-- skill-router:end -->\n""")
old = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
if "<!-- skill-router:start -->" in old:
    new = re.sub(r"<!-- skill-router:start -->.*?<!-- skill-router:end -->\n?", lambda m: block, old, flags=re.S)
    print("    block replaced.")
else:
    new = (old.rstrip("\n") + "\n\n" if old.strip() else "") + block
    print("    block added.")
open(path, "w", encoding="utf-8").write(new)
PY

if [ -z "$SETS" ]; then
  if [ -t 0 ]; then
    printf "Turn on the essential settings (stop-slop and save-before-limit hooks)? [Y/n] "
    read -r ans || ans=""
    case "$ans" in n|N|no) SETS=none ;; *) SETS=essentials ;; esac
    if [ "$SETS" = essentials ]; then
      printf "Also the optional ones (dictation check, security-guidance warnings)? [y/N] "
      read -r ans || ans=""
      case "$ans" in y|Y|yes) SETS=all ;; esac
    fi
  else
    SETS=none
  fi
fi
case "$SETS" in
  essentials|all) echo "==> Turning on settings ($SETS) ..."; TOOLBOX_PYTHON="$PY" $PY "$HERE/settings/install.py" on "$SETS" ;;
  none) echo "==> Settings left off. Turn them on any time: $PY settings/install.py on essentials" ;;
  *) echo "unknown --settings value: $SETS (essentials, all or none)" >&2; exit 2 ;;
esac

echo "==> Optional extra: massgen"
cat <<'TXT'
    massgen (PyPI: massgen) is a third-party CLI that runs several LLM agents in parallel on one
    problem and reconciles their answers. It needs Python 3.11 or newer and your own API keys for
    the providers it calls (OpenAI, Anthropic, Gemini, xAI and others), billed separately from any
    Claude subscription. Claude Code's own subagents cover most of the same ground, so it is off
    by default. Add it any time with: ./setup.sh --with-massgen
TXT
if [ "$WITH_MASSGEN" = 1 ]; then
  if command -v uv >/dev/null 2>&1; then uv tool install massgen
  elif command -v pipx >/dev/null 2>&1; then pipx install massgen
  else $PY -m pip install --user massgen
  fi
  echo "    massgen installed."
fi

echo ""
echo "Done. Restart your Claude Code session so the block loads."
echo "Check:  ls ~/.claude/skills | wc -l   and ask Claude which skills it can see."
