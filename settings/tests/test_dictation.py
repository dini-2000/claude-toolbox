"""Offline checks for dictation_check.py on made-up prompts: python3 settings/tests/test_dictation.py"""
import importlib.util, json, os, subprocess, sys

HOOK = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "hooks", "dictation_check.py")
spec = importlib.util.spec_from_file_location("dh", HOOK)
dh = importlib.util.module_from_spec(spec); spec.loader.exec_module(dh)

CLEAN = ("I need two slides for the meeting on Friday. So the first one shows how the payment moves from the bank to "
         "the ministry, and the second one shows the fees. And then we need a short note that goes with it, you know, "
         "something the team can read before they come in. So maybe keep it to one page and use the figures from last week.")
CASES = [
    ("filler dictation", "Um, so, uh, the the file is, uh, in the folder", "uh/um"),
    ("clean dictation", CLEAN, "no uh/um, but"),
    ("typed", "can you fix the deck - slide 3 has the wrong figure and i think the chart (bottom left) is off too", None),
    ("typed, careful", "Please update the summary with the new figures. The totals on page two are out of date. "
                       "Keep the same layout and send me the file when it is ready. I will check it tonight.", None),
    ("short clean", "So send it to the team. And then tell me when it is done.", None),
    ("mentions fillers", "typed prompts sometimes say \"uh, um\" in quotes - that should not count", None),
    ("other chat", "<cross-session-message from=\"x\" name=\"Other chat\">\n" + CLEAN + "\n</cross-session-message>", None),
    ("app notice", "<task-notification>\n" + CLEAN + "\n</task-notification>", None),
    ("pasted dictation", "check this transcript: <pasted_content id=\"a\">Um, so, uh, the the plan is, uh, ready"
                         "</pasted_content id=\"a\">", "pasted text"),
    ("pasted clean", "summarise this: <pasted_content id=\"a\">" + CLEAN + "</pasted_content id=\"a\">", None),
]

fails = 0
for name, prompt, want in CASES:
    got = dh.note(prompt)
    ok = (not got) if want is None else (want in got)
    fails += not ok
    print("ok  " if ok else "FAIL", name, "|", got[:110] if got else "(nothing)")
run = subprocess.run([sys.executable, HOOK], input=json.dumps({"prompt": CLEAN}), capture_output=True, text=True)
ok = run.stdout.startswith("[dictation] This prompt reads as dictated (no uh/um") and run.returncode == 0
fails += not ok
print("ok  " if ok else "FAIL", "hook as a command")
for bad in ("", "not json", "{\"prompt\": null}"):
    run = subprocess.run([sys.executable, HOOK], input=bad, capture_output=True, text=True)
    ok = run.stdout == "" and run.returncode == 0
    fails += not ok
    print("ok  " if ok else "FAIL", "bad input", repr(bad))
print(f"{len(CASES) + 4 - fails} of {len(CASES) + 4} passed")
sys.exit(1 if fails else 0)
