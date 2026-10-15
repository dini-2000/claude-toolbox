#!/usr/bin/env python3
"""stop-slop, always on. Needs the stop-slop skill in ~/.claude/skills.

SessionStart (startup, resume, compact): prints the Quick Checks from ~/.claude/skills/stop-slop/SKILL.md, read fresh
(about 250 tokens), with a pointer to the full pass. The phrase and structure lists stay on disk until a full pass.
UserPromptSubmit: when the prompt asks for prose for a reader (an email, note, draft, letter, post, document, slides,
reply, summary), prints one line asking for the Quick Checks. Other prompts print nothing, so they cost no tokens.
Errors print nothing.

Tests:
  echo '{"hook_event_name": "SessionStart", "source": "startup"}' | python3 stop_slop.py
  echo '{"hook_event_name": "UserPromptSubmit", "prompt": "draft a reply email to Sam"}' | python3 stop_slop.py
  echo '{"hook_event_name": "UserPromptSubmit", "prompt": "what time is it"}' | python3 stop_slop.py   (nothing)
"""
import json
import os
import re
import sys

SKILL = os.path.expanduser("~/.claude/skills/stop-slop")
FULL = ("the full pass: ~/.claude/skills/stop-slop/SKILL.md with references/phrases.md and references/structures.md, "
        "reading them if they are not in context")
LINT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stop_slop_lint.py")

PROSE = re.compile(
    r"\b(e-?mails?|notes?|draft\w*|letters?|posts?|repl(?:y|ies)|messages?|memos?|documents?|docs?|reports?|"
    r"papers?|slides?|decks?|summar(?:y|ies|ise|ize)|writ(?:e|ing)|write-?up|rewrit\w*|reword\w*|phrasing|"
    r"wording|tone|captions?|bio|proposals?|briefs?|minutes|announcement|cover letter|linkedin)\b", re.I)


def quick_checks():
    with open(os.path.join(SKILL, "SKILL.md"), encoding="utf-8") as f:
        m = re.search(r"\n## Quick Checks\s*\n(.*?)(?=\n## |\Z)", f.read(), re.S)
    return m.group(1).strip() if m else ""


def session_note():
    checks = quick_checks()
    if not checks:
        return None
    lint = (f" A lint hook names the tells it finds in the prose files you save; for any other file, run "
            f'python3 "{LINT}" <file> before delivering it.') if os.path.exists(LINT) else ""
    return ("[stop-slop, always on] Run these Quick Checks on all prose for the user (chat replies, documents, "
            f"emails, notes and slides) and fix each hit before presenting it. For a deliverable, run {FULL}.{lint}"
            f"\n\n{checks}")


def prompt_note(prompt):
    prompt = (prompt or "").lstrip()
    if prompt.startswith("<") or not PROSE.search(prompt):
        return None
    return ("[stop-slop] This asks for prose for a reader: run the Quick Checks in ~/.claude/skills/stop-slop/SKILL.md "
            f"on the draft (read it if they are not in context) and fix every hit before presenting it; for a "
            f"document, email or slides, run {FULL}.")


def main():
    try:
        hook = json.load(sys.stdin)
        event = hook.get("hook_event_name") or ""
        if event == "SessionStart":
            text = session_note()
        elif event == "UserPromptSubmit":
            text = prompt_note(hook.get("prompt"))
        else:
            text = None
        if text:
            print(text)
    except Exception:
        pass


if __name__ == "__main__":
    main()
