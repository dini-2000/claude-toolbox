#!/usr/bin/env python3
"""Save before a limit: get Claude to write down where a task stands before the chat is compacted or a usage limit
ends the session, so the next session (or the same one after a summary) can pick up without losing work.

The handover file is HANDOFF.md in the folder Claude Code runs in (set SAVE_BEFORE_LIMIT_FILE to use another name).

  save_before_limit.py          PostToolUse and UserPromptSubmit.
      Context: after each tool call it reads the chat's size from the transcript. At 85% of the point where Claude
      Code compacts the chat (CLAUDE_CODE_AUTO_COMPACT_WINDOW or autoCompactWindow in ~/.claude/settings.json, less
      the 33K Claude Code keeps free; 167K by default) it asks Claude once to bring the handover file up to date.
      It asks again only after the chat has dropped below 60%, as it does after a compaction.
      Usage (Claude desktop app only, where Claude can read its plan's usage with mcp__ccd_session_mgmt__get_usage):
      it asks Claude to check usage now and then, more often as usage rises (every 30 minutes or 40 tool calls below
      50%, down to every 2 minutes or 3 calls above 88%), and at 90% and 97% of the 5-hour or weekly limit asks for
      the handover save and tells the user.
  save_before_limit.py cutoff   StopFailure, matcher rate_limit: a usage limit has ended a turn. It adds a dated
      line to the handover file, or starts one from the last request in the transcript when there is none.

State lives in the temp folder, one small file per session. Errors print nothing.
Tests:
  echo '{"hook_event_name": "PostToolUse", "session_id": "t1", "tool_name": "Read", "transcript_path": "/nonexistent"}' | python3 save_before_limit.py
  echo '{"hook_event_name": "StopFailure", "session_id": "t1", "cwd": "/tmp/x"}' | python3 save_before_limit.py cutoff
"""
import json
import os
import re
import sys
import tempfile
import time

FILE = os.environ.get("SAVE_BEFORE_LIMIT_FILE", "HANDOFF.md")
SETTINGS = os.path.expanduser("~/.claude/settings.json")
STATE = os.path.join(tempfile.gettempdir(), "save-before-limit")
USAGE_TOOL = "mcp__ccd_session_mgmt__get_usage"
DESKTOP = os.environ.get("CLAUDE_CODE_ENTRYPOINT") == "claude-desktop"
BUFFER, DEFAULT_WINDOW = 33_000, 200_000
SAVE_AT, REARM_BELOW = 0.85, 0.60
WARN = (90, 97)
BANDS = [(50, 30, 40), (75, 15, 20), (88, 5, 8), (101, 2, 3)]   # below this %: check every N minutes or M tool calls
SAVE_WHAT = ("done so far, files changed, the next step, decisions with their reasons, approaches tried and dropped, "
             "open questions")


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f)
    os.replace(tmp, path)


def compact_point():
    raw = os.environ.get("CLAUDE_CODE_AUTO_COMPACT_WINDOW") or (load(SETTINGS) or {}).get("autoCompactWindow")
    try:
        t = str(raw).strip().lower()
        n = float(t[:-1]) * (1_000 if t.endswith("k") else 1_000_000) if t[-1:] in ("k", "m") else float(t)
        return int(n * 1000 if n <= 1000 else n) - BUFFER          # a bare 100 to 1000 means thousands
    except Exception:
        return DEFAULT_WINDOW - BUFFER


def tail(transcript, size=400_000):
    try:
        with open(transcript, "rb") as f:
            f.seek(max(0, os.path.getsize(transcript) - size))
            return f.read().decode("utf-8", "replace").splitlines()
    except Exception:
        return []


def context_now(transcript):
    """Tokens the chat sent at its last main-thread API call, from the transcript's tail; None if unknown."""
    for line in reversed(tail(transcript)):
        if '"usage"' not in line or '"assistant"' not in line:
            continue
        try:
            e = json.loads(line)
        except Exception:
            continue
        u = (e.get("message") or {}).get("usage") or {}
        if e.get("type") != "assistant" or e.get("isSidechain") or not u:
            continue
        n = sum(u.get(k) or 0 for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
        if n:
            return n + (u.get("output_tokens") or 0)
    return None


def find_key(obj, key, depth=0):
    """The dict under `key` in a tool response, however it is wrapped (JSON text, lists, content blocks)."""
    if depth > 6:
        return None
    if isinstance(obj, str):
        s = obj.strip()
        if s.startswith("{") and f'"{key}"' in s:
            try:
                return find_key(json.loads(s), key, depth + 1)
            except Exception:
                return None
        return None
    if isinstance(obj, dict):
        if isinstance(obj.get(key), dict):
            return obj[key]
        obj = list(obj.values())
    if isinstance(obj, list):
        for v in obj:
            found = find_key(v, key, depth + 1)
            if found:
                return found
    return None


def usage_text(windows):
    return ", ".join(f"{w['label']} {w['pct']:.0f}%" for w in windows if isinstance(w.get("pct"), (int, float)))


def reply(event, text, notice=None):
    out = {"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}
    if notice:
        out["systemMessage"] = notice
    print(json.dumps(out))


def check(hook):
    sid, event = hook.get("session_id") or "", hook.get("hook_event_name") or ""
    if not sid or hook.get("agent_id") or event not in ("PostToolUse", "UserPromptSubmit"):
        return
    path = os.path.join(STATE, re.sub(r"[^\w-]", "", sid)[:40] + ".json")
    st = load(path) or {}
    now, notes, notice = time.time(), [], None

    if DESKTOP:
        if event == "PostToolUse" and hook.get("tool_name") == USAGE_TOOL:
            plan = find_key(hook.get("tool_response"), "plan") or {}
            if plan.get("status") == "ok":
                st["windows"] = [{"label": w.get("label") or "limit", "pct": w.get("percentUsed")}
                                 for w in plan.get("windows") or []]
                st.update(read_at=now, calls=0, nudged=None)
                ctx = find_key(hook.get("tool_response"), "context") or {}
                if ctx.get("contextWindow") and ctx.get("autoCompactsAtPercent"):
                    st["compact_at"] = int(ctx["contextWindow"] * ctx["autoCompactsAtPercent"] / 100)
        elif event == "PostToolUse":
            st["calls"] = st.get("calls", 0) + 1
        pcts = [w["pct"] for w in st.get("windows") or [] if isinstance(w.get("pct"), (int, float))]
        top = max(pcts) if pcts else None
        level = max([w for w in WARN if top is not None and top >= w], default=None)
        if level and level not in st.get("warned", []):
            st.setdefault("warned", []).append(level)
            notes.append(f"Usage at {usage_text(st['windows'])}: a limit may end this session soon. At the next pause "
                         f"in the work, bring {FILE} up to date ({SAVE_WHAT}), then tell the user where things stand.")
            notice = f"Usage at {usage_text(st['windows'])}. Claude will save its progress to {FILE}."
        elif top is None or top < WARN[-1]:
            minutes, calls = next((m, c) for limit, m, c in BANDS if (top or 0) < limit)
            due = top is None or now - st.get("read_at", 0) >= minutes * 60 or st.get("calls", 0) >= calls
            nudged = st.get("nudged")
            if due and (nudged is None or st.get("calls", 0) - nudged >= 10 or event == "UserPromptSubmit"):
                st["nudged"] = st.get("calls", 0)
                notes.append(f"Usage check due. Call {USAGE_TOOL} with your next tool call (load it with ToolSearch "
                             f"\"select:{USAGE_TOOL}\" first if needed). Mention the result to the user only at 90% or more.")

    if event == "PostToolUse":
        ctx, point = context_now(hook.get("transcript_path") or ""), st.get("compact_at") or compact_point()
        if ctx:
            if ctx < REARM_BELOW * point:
                st["armed"] = True
            elif ctx >= SAVE_AT * point and st.get("armed", True):
                st["armed"] = False
                notes.append(f"Context {ctx // 1000}K of the {point // 1000}K compact point: this chat will be "
                             f"summarised soon. If a task is under way, bring {FILE} up to date now ({SAVE_WHAT}), so "
                             "nothing is lost. Nothing pending: carry on.")
    save(path, st)
    if notes:
        reply(event, "\n\n".join(notes), notice)


def cutoff(hook):
    folder = hook.get("cwd") or os.getcwd()
    path = os.path.join(folder, FILE)
    stamp = time.strftime("%d %b %Y %H:%M")
    if os.path.exists(path):
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"\n- {stamp}: a usage limit ended the session here. Check the files the next step names before "
                    "redoing anything: the last steps may have finished without being written down.\n")
        return
    ask = ""
    for line in reversed(tail(hook.get("transcript_path") or "")):
        try:
            e = json.loads(line)
        except Exception:
            continue
        if e.get("type") != "user" or e.get("isSidechain"):
            continue
        c = (e.get("message") or {}).get("content")
        if isinstance(c, list):
            c = " ".join(b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text")
        if isinstance(c, str) and c.strip() and not c.lstrip().startswith("<"):
            ask = c.strip()[:1500]
            break
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# Handoff\n\n{stamp}: a usage limit ended the session before Claude wrote a handover.\n\n"
                f"## Last request\n{ask or '(not found in the transcript)'}\n\n"
                "## Next\nRead the request above, check what is already on disk, and carry on from there.\n")


def main():
    try:
        hook = json.load(sys.stdin)
        cutoff(hook) if sys.argv[1:2] == ["cutoff"] else check(hook)
    except Exception:
        pass


if __name__ == "__main__":
    main()
