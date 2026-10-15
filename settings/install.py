#!/usr/bin/env python3
"""Turn Claude Toolbox settings on or off in ~/.claude/settings.json.

  python3 settings/install.py list
  python3 settings/install.py on  stop-slop save-before-limit     (or: essentials, optional, all)
  python3 settings/install.py off dictation-check                 (or: all)

`on` copies the hook scripts to ~/.claude/hooks/claude-toolbox/ and adds their entries; `off` removes the entries.
settings.json is backed up before any change (settings.json.bak-<date>), and entries you added yourself are left
alone. Restart Claude Code afterwards so it reads the new settings.
"""
import datetime
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CLAUDE = os.path.expanduser("~/.claude")
SETTINGS = os.path.join(CLAUDE, "settings.json")
DEST = os.path.join(CLAUDE, "hooks", "claude-toolbox")
PY = os.environ.get("TOOLBOX_PYTHON", "python3")


def hook(script, *args):
    return f'{PY} "{os.path.join(DEST, script)}"' + "".join(f" {a}" for a in args)


SECURITY = os.path.join(CLAUDE, "skills", "security-guidance", "hooks", "security_reminder_hook.py")
SETS = {
    "stop-slop": ("essential", "Quick Checks at session start, a reminder on prose requests, a lint on saved prose",
                  ["stop_slop.py", "stop_slop_lint.py"],
                  [("SessionStart", None, hook("stop_slop.py")), ("UserPromptSubmit", None, hook("stop_slop.py")),
                   ("PostToolUse", "Write|Edit|MultiEdit", hook("stop_slop_lint.py"))]),
    "save-before-limit": ("essential", "asks Claude to save HANDOFF.md before compaction or a usage limit",
                          ["save_before_limit.py"],
                          [("PostToolUse", None, hook("save_before_limit.py")),
                           ("UserPromptSubmit", None, hook("save_before_limit.py")),
                           ("StopFailure", "rate_limit", hook("save_before_limit.py", "cutoff"))]),
    "dictation-check": ("optional", "flags prompts that read as speech-to-text, so Claude reads them for intent",
                        ["dictation_check.py"], [("UserPromptSubmit", None, hook("dictation_check.py"))]),
    "security-guidance": ("optional", "warns before Claude writes common security mistakes (needs the security-guidance skill)",
                          [], [("PreToolUse", "Edit|Write|MultiEdit", f'{PY} "{SECURITY}"')]),
    "download-guard": ("optional", "sends downloads and installs through safe_get.py, which quarantines and screens them",
                       ["download_guard.py", "safe_get.py", "screen.py"],
                       [("SessionStart", None, hook("download_guard.py")), ("PreToolUse", "Bash", hook("download_guard.py")),
                        ("PostToolUse", "mcp__Claude_Browser__.*|mcp__claude-in-chrome__.*", hook("download_guard.py"))]),
}


def marks(name):
    """What identifies this setting's commands, whichever Python name they were written with."""
    scripts = {os.path.join("claude-toolbox", f) for f in SETS[name][2]}
    return scripts or {os.path.join("security-guidance", "hooks", "security_reminder_hook.py")}


def ours(cmd, name):
    return any(m in cmd for m in marks(name))


def pick(names):
    out = []
    for n in names:
        if n == "all":
            out += list(SETS)
        elif n in ("essentials", "optional"):
            out += [k for k, v in SETS.items() if v[0] == n.rstrip("s")]
        elif n in SETS:
            out.append(n)
        else:
            sys.exit(f"unknown setting: {n} (try: list)")
    return list(dict.fromkeys(out))


def load():
    if not os.path.exists(SETTINGS):
        return {}
    try:
        return json.load(open(SETTINGS, encoding="utf-8"))
    except Exception:
        sys.exit("settings.json is not valid JSON; fix it first, nothing changed.")


def write(data):
    if os.path.exists(SETTINGS):
        bak = SETTINGS + ".bak-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        if not os.path.exists(bak):                        # two changes in one second keep the older copy
            shutil.copy2(SETTINGS, bak)
    os.makedirs(CLAUDE, exist_ok=True)
    tmp = SETTINGS + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, SETTINGS)


def remove(data, names):
    hooks, gone = data.get("hooks") or {}, 0
    for event in list(hooks):
        keep = []
        for e in hooks[event]:
            hs = [h for h in e.get("hooks", []) if not any(ours(h.get("command", ""), n) for n in names)]
            gone += len(e.get("hooks", [])) - len(hs)
            if hs or not e.get("hooks"):
                keep.append({**e, "hooks": hs})
        if keep:
            hooks[event] = keep
        else:
            del hooks[event]
    if not hooks:
        data.pop("hooks", None)
    return gone


def on(names):
    if "security-guidance" in names and not os.path.exists(SECURITY):
        print("security-guidance: skipped, the security-guidance skill is not installed.")
        names = [n for n in names if n != "security-guidance"]
    os.makedirs(DEST, exist_ok=True)
    for n in names:
        for f in SETS[n][2]:
            shutil.copy2(os.path.join(HERE, "hooks", f), os.path.join(DEST, f))
    data = load()
    remove(data, names)                                    # replace, never duplicate
    hooks = data.setdefault("hooks", {})
    for n in names:
        for event, matcher, cmd in SETS[n][3]:
            entry = {"hooks": [{"type": "command", "command": cmd, "timeout": 15}]}
            if matcher:
                entry = {"matcher": matcher, **entry}
            hooks.setdefault(event, []).append(entry)
    write(data)
    for n in names:
        print(f"    on: {n} ({SETS[n][1]})")


def off(names):
    data = load()
    gone = remove(data, names)
    if gone:
        write(data)
    print(f"    removed {gone} hook entr{'y' if gone == 1 else 'ies'}" + (" (settings.json backed up)" if gone else ""))


def show():
    cmds = [h.get("command", "") for es in (load().get("hooks") or {}).values() for e in es for h in e.get("hooks", [])]
    for n, (tier, what, _, entries) in SETS.items():
        state = "on" if any(ours(c, n) for c in cmds) else "off"
        print(f"  {n:<18} {tier:<9} {state:<3}  {what}")


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__.strip())
    elif args[0] == "list":
        show()
    elif args[0] in ("on", "off") and args[1:]:
        (on if args[0] == "on" else off)(pick(args[1:]))
    else:
        sys.exit("usage: install.py list | on <names> | off <names>")


if __name__ == "__main__":
    main()
