#!/usr/bin/env python3
"""stop-slop lint: names the AI tells in prose Claude saves. Needs the stop-slop skill in ~/.claude/skills.

PostToolUse on Write, Edit and MultiEdit: .md, .html, .htm and .txt files; the whole file after a Write, the lines
just edited after an Edit. Clean text prints nothing, so clean work costs no tokens, and the lint never blocks a save.
Skipped as working files: anything under ~/.claude, hidden folders, node_modules, and CLAUDE.md, NOTES.md, MEMORY.md,
SKILL.md and HANDOFF.md.
Reading: HTML as its visible text, Markdown without its code. Text in double quotes (quoted sources, the user's own
words) is skipped.
Patterns: em dashes and dash stand-ins; every quoted phrase in ~/.claude/skills/stop-slop/references/phrases.md, read
fresh each run ([X] matches a short span, the Adverbs section's single words match as words); and the binary
contrasts of references/structures.md, coded below because that file describes them in prose. Errors print nothing.

Command line, for any .md, .html or .txt file: python3 stop_slop_lint.py <file>... prints "clean" or each tell with
the text around it, and exits 1 when it finds any.
Test: echo '{"tool_name": "Write", "tool_input": {"file_path": "/tmp/a.md"}}' | python3 stop_slop_lint.py
"""
import html
import json
import os
import re
import sys

HOME = os.path.realpath(os.path.expanduser("~"))
PHRASES = os.path.join(HOME, ".claude/skills/stop-slop/references/phrases.md")
PROSE = {".md", ".html", ".htm", ".txt"}
SKIP_NAME = re.compile(r"^(CLAUDE|NOTES|MEMORY|SKILL|HANDOFF)\.md$", re.I)
SKIP_DIRS = {"node_modules", "__pycache__", "site-packages"}
BIG = 3_000_000
KEEP = "quoted sources, names and fixed terms stay as they are."
Q = "['’]"
GAP = r"[^.!?\n]{1,60}?"
NOT = rf"(?:\b(?:is|are|was|were)\s+not|\b(?:isn|aren|wasn|weren){Q}t|(?:^|(?<=[.!?]\s))not)\b"
STRUCTURES = [
    ('"not X, it\'s Y"', NOT + rf"[^.;:\n]{{1,60}}?[,;]\s+(?:it|this|that|they){Q}(?:s|re)\b"),
    ('"not X. It\'s Y."', NOT + rf"[^.!?\n]{{1,60}}?\.\s+(?:it|this|that){Q}s\b"),
    ('"not just X but Y"', r"\bnot (?:just|only|merely)\b[^.;\n]{1,80}?\bbut\b"),
    ('"not because X"', r"\bnot because\b"),
    ('"the answer isn\'t X"', rf"\bthe (?:answer|question|problem|point|issue|goal) (?:isn{Q}t|is not)\b"),
    ('"stops being X, starts being Y"', r"\bstops being\b[^.;\n]{1,60}?\bstarts being\b"),
    ('"doesn\'t mean X, but Y"', rf"\bdoesn{Q}t mean\b[^.;\n]{{1,60}}?\bbut\b"),
    ('"X rather than Y"', r"\brather than\b"),
    ('"here\'s how"', rf"\bhere{Q}s how\b"),
]
DASHES = [("em dash", "—"), ("spaced en dash", " – "), ('" -- " as a dash', " -- "),
          ('" - " as a dash', r"(?<=[A-Za-z,)]) - (?=[A-Za-z(])")]
TAG = re.compile(r"<!--|<(script|style)\b|<[^>]*>", re.I)
QUOTED = re.compile("\"[^\"\\n]{1,300}\"|\u201c[^\u201d\\n]{1,300}\u201d")
CURLY = str.maketrans("‘’“”", "''\"\"")


def placeholder(t):
    return re.fullmatch(r"\[?[XY]\]?[.,:]?", t) is not None


def phrase_re(p, section):
    toks = re.sub(r"(\.\.\.|…)$", "", p.strip()).split()
    while toks and placeholder(toks[0]):
        toks.pop(0)
    while toks and placeholder(toks[-1]):
        toks.pop()
    if not toks:
        return None, None
    if len(toks) == 1 and re.fullmatch(r"[A-Za-z]+", toks[0]):
        return ("adverb" if section.startswith("adverb") else "word"), re.compile(rf"\b{toks[0]}\b", re.I)
    if toks[-1].endswith(".") and len(toks) <= 2:                    # "Period." only as a sentence of its own
        return "phrase", re.compile(r"(?:^|(?<=[.!?]\s))" + r"\s+".join(map(re.escape, toks)) + r"(?=\s|$)")
    if len(toks) > 1:
        toks[-1] = toks[-1].rstrip(".:,")
    body = r"\s+".join(GAP if placeholder(t) else re.sub(Q, lambda m: Q, re.escape(t)) for t in toks)
    return "phrase", re.compile((r"(?<![\w'’])" if re.match(r"\w", toks[0]) else "") + body
                                + (r"(?!\w)" if re.search(r"\w$", toks[-1]) else ""), re.I)


def patterns():
    """(kind, label, regex) for every tell; phrases.md is read fresh so edits to the skill apply at once."""
    out = [("phrase", label, re.compile(rx)) for label, rx in DASHES]
    out += [("phrase", label, re.compile(rx, re.I)) for label, rx in STRUCTURES]
    try:
        with open(PHRASES, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except OSError:
        return out
    section = ""
    for line in lines:
        s = line.strip()
        if s.startswith("## "):
            section = s[3:].lower()
            continue
        if s.startswith("- "):
            items = re.findall(r'"([^"]+)"', s)
        elif s.startswith("|") and not re.match(r"\|\s*(Avoid|-)", s):
            cell = s.strip("|").split("|")[0].strip()
            items = [] if "(" in cell else [cell]
        else:
            continue
        for p in items:
            kind, rx = phrase_re(p, section)
            if rx:
                out.append((kind, f'"{p}"', rx))
    return out


def visible(text, is_html):
    """The text a reader sees, line by line, keeping the file's line numbers; quoted words are someone else's."""
    out, skip = [], None
    for ln in text.split("\n"):
        if not is_html:
            if ln.lstrip().startswith("```"):
                skip = None if skip else "fence"
                out.append("")
            else:
                out.append("" if skip else QUOTED.sub(" ", re.sub(r"`[^`\n]*`", " ", ln)))
            continue
        vis, i = [], 0
        while i < len(ln):
            if skip:
                end = "-->" if skip == "comment" else f"</{skip}>"
                j = ln.lower().find(end, i)
                if j < 0:
                    break
                i, skip = j + len(end), None
                continue
            m = TAG.search(ln, i)
            if not m:
                vis.append(ln[i:])
                break
            vis.append(ln[i:m.start()] + " ")
            skip = "comment" if m.group(0) == "<!--" else (m.group(1) or "").lower() or None
            i = m.end()
        out.append(QUOTED.sub(" ", html.unescape("".join(vis))))
    return out


def wanted(path):
    real = os.path.realpath(path)
    parts = real.split(os.sep)
    return (os.path.splitext(real)[1].lower() in PROSE and os.path.isfile(real)
            and not real.startswith(os.path.join(HOME, ".claude") + os.sep)
            and not any(p.startswith(".") or p in SKIP_DIRS for p in parts[:-1] if p)
            and not SKIP_NAME.match(parts[-1]))


def edited_rows(text, new_strings):
    """Line numbers holding the replacement text; Edit may have matched the file's curly quotes or spacing."""
    flat, rows = text.translate(CURLY), set()
    file_lines = flat.split("\n")
    for s in new_strings:
        s = (s or "").translate(CURLY)
        if not s.strip():
            continue
        i, found = flat.find(s), False
        while i >= 0 and len(rows) < 20000:
            a, found = flat.count("\n", 0, i) + 1, True
            rows.update(range(a, a + s.count("\n") + 1))
            i = flat.find(s, i + len(s))
        if not found:
            for part in (x.strip() for x in s.split("\n")):
                if len(part) >= 8:
                    rows.update(n for n, ln in enumerate(file_lines, 1) if part in ln)
    return rows


def scan(items, pats):
    """{(kind, label): [(line number, text, match)]} over (line number, text) pairs, in reading order."""
    first = re.compile("|".join(f"(?i:{rx.pattern})" if rx.flags & re.I else f"(?:{rx.pattern})" for _, _, rx in pats))
    hits = {}
    for where, ln in items:
        if ln.strip() and first.search(ln):
            for kind, label, rx in pats:
                m = rx.search(ln)
                if m:
                    hits.setdefault((kind, label), []).append((where, ln, m))
    return hits


def describe(hits, limit=4):
    """Each tell with up to `limit` places and the text around them."""
    def place(w, ln, m):
        a, b = max(0, m.start() - 30), m.end() + 30
        text = re.sub(r"\s+", " ", "…" * (a > 0) + ln[a:b].strip() + "…" * (b < len(ln)))
        return f'L{w} "{text}"'
    return [f"{'adverb ' if kind == 'adverb' else ''}{label}: " + "; ".join(place(*h) for h in hs[:limit])
            + (f" and {len(hs) - limit} more" if len(hs) > limit else "") for (kind, label), hs in hits.items()]


def read_lines(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    return text, visible(text, path.lower().endswith((".html", ".htm")))


def on_save(tool, inp):
    path = inp.get("file_path") or ""
    if not path or not wanted(path) or os.path.getsize(path) > BIG:
        return
    text, lines = read_lines(path)
    rows = None
    if tool != "Write":
        edits = inp.get("edits") if tool == "MultiEdit" else [inp]
        rows = edited_rows(text, [e.get("new_string") for e in edits or [] if isinstance(e, dict)])
        if not rows:
            return
    hits = scan(((n, ln) for n, ln in enumerate(lines, 1) if rows is None or n in rows), patterns())
    if not hits:
        return
    scope = "the file" if tool == "Write" else "the lines just edited"
    text = (f"[stop-slop lint] {os.path.basename(path)}: possible AI tells in {scope}: " + "; ".join(describe(hits, 3))
            + f". If the file is for a reader, fix each real one now; {KEEP}")
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": text}}))


def cli(paths):
    pats, dirty = patterns(), 0
    for path in paths:
        try:
            _, lines = read_lines(path)
        except OSError as e:
            print(f"{os.path.basename(path)}: could not read ({e})")
            continue
        hits = scan(enumerate(lines, 1), pats)
        if not hits:
            print(f"{os.path.basename(path)}: clean")
            continue
        dirty += 1
        print(f"{os.path.basename(path)}: possible AI tells. Fix each real one; {KEEP}")
        for line in describe(hits):
            print("  " + line)
    return 1 if dirty else 0


def main():
    if len(sys.argv) > 1:
        sys.exit(cli(sys.argv[1:]))
    try:
        hook = json.load(sys.stdin)
        tool = hook.get("tool_name") or ""
        if (hook.get("hook_event_name") or "PostToolUse") == "PostToolUse" and tool in ("Write", "Edit", "MultiEdit"):
            on_save(tool, hook.get("tool_input") or {})
    except Exception:
        pass


if __name__ == "__main__":
    main()
