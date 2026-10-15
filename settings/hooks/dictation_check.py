#!/usr/bin/env python3
"""UserPromptSubmit hook: flag a prompt that reads as dictated, so Claude reads it as speech-to-text.

No transcript field records voice or keyboard input, so this weighs the text itself: speech marks (uh/um, repeated
words, spoken phrases, spelled-out numbers) against typing marks (lowercase i, contractions without apostrophes,
lowercase sentence starts, " - " dashes, brackets, abbreviations, paths and code). Fillers inside brackets or quotes
are mentions, not speech. Pasted blocks are judged apart from the user's own words. It prints a short [dictation]
note only when speech clearly wins and nothing otherwise, so typed prompts cost no tokens. Errors print nothing.
Clean dictation with no uh or um passes unflagged, since it reads like typing.

Names speech-to-text tends to garble in your work (people, products, places) can go in the DICTATION_TERMS
environment variable, comma-separated; the note then tells Claude that odd words may be garbled forms of them.
Test: echo '{"prompt": "Um, so, uh, the the file is, uh, in the folder"}' | python3 dictation_check.py
"""
import json
import os
import re
import sys

TERMS = os.environ.get("DICTATION_TERMS", "").strip()

FILLERS = {"uh", "uhh", "uhm", "um", "umm", "erm", "hmm", "mm"}
NO_APOSTROPHE = {"ive", "im", "thats", "dont", "cant", "didnt", "doesnt", "isnt", "arent", "wasnt", "werent",
                 "youre", "youve", "theyre", "whats", "theres", "heres", "couldnt", "shouldnt", "wouldnt",
                 "havent", "hasnt", "wont", "weve", "theyve", "youll", "thatll", "wouldve", "couldve"}
TYPED_ABBR = {"vs", "ss", "pls", "plz", "thx", "btw", "imo", "fyi", "eg", "ie", "etc", "pdf", "ppt", "pptx",
              "docx", "xlsx", "html", "csv", "api", "url", "md", "py", "js", "qc"}
NOT_SENTENCE_END = {"vs", "etc", "eg", "ie", "approx", "incl", "cf", "no"}
SPOKEN = re.compile(r"\b(?:you know|sort of|kind of|i mean|i guess|yeah|okay so|so yeah|let me think)\b", re.I)
NUMBER_WORDS = re.compile(
    r"\b(?:twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)[ -](?:one|two|three|four|five|six|seven|eight|nine)\b"
    r"|\b(?:one|two|three|four|five|six|seven|eight|nine|ten|twelve|fifteen|twenty|thirty|forty|fifty|hundred)"
    r" (?:percent|hundred|thousand|million|billion|dollars|euros|pounds|hours|minutes|days|weeks|months|years)\b", re.I)
TECH = re.compile(r"```|`|https?://|~/|/Users/|/home/|\w\.(?:md|py|js|json|html|pdf|pptx?|docx|xlsx|csv|txt)\b"
                  r"|->|=>|\w_\w|[{}\[\]|#=<>]")
WORD = re.compile(r"[A-Za-z0-9]+(?:['’][A-Za-z]+)?")
PASTED = re.compile(r"<pasted_content[^>]*>(.*?)</pasted_content[^>]*>", re.S)


def marks(text):
    """Speech and typing marks in one stretch of text: (speech, typing, fillers, repeats)."""
    plain = re.sub(r"```.*?```|`[^`\n]*`|https?://\S+", " ", text, flags=re.S)
    said = re.sub(r"\([^()]*\)|\"[^\"\n]*\"|“[^”\n]*”", " ", plain)  # brackets and quotes mention, not say
    fillers = repeats = 0
    for line in said.splitlines():
        words = [w.lower() for w in WORD.findall(line)]
        fillers += sum(w in FILLERS for w in words)
        words = [w for w in words if w not in FILLERS]
        repeats += sum(a == b and not a.isdigit() for a, b in zip(words, words[1:]))
        repeats += sum(words[i:i + 2] == words[i + 2:i + 4] for i in range(len(words) - 3))
    speech = 2 * fillers + 1.5 * repeats + 0.5 * len(SPOKEN.findall(said)) + len(NUMBER_WORDS.findall(said))

    words = WORD.findall(plain)
    lower_i = len(re.findall(r"(?<![\w'’.])i(?:['’](?:m|ve|d|ll))?(?![\w'’]|\.\w)", plain))
    no_apostrophe = (sum(w.lower() in NO_APOSTROPHE for w in words)
                     + len(re.findall(r"(?:^|[.!?]\s+)Lets\b", plain)))
    lower_starts = 0
    for m in re.finditer(r"(?:^|(\S*)[.!?][ \t]+|\n[ \t]*)[a-z]", plain):
        before = (m.group(1) or "").lower()
        if "." not in before and "/" not in before and before not in NOT_SENTENCE_END:
            lower_starts += 1
    typing = (3 * lower_i + 2 * no_apostrophe + 2 * lower_starts + len(re.findall(r"\S - \S", plain))
              + text.count("(") + sum(w in TYPED_ABBR for w in words) + min(len(TECH.findall(text)), 6))
    return speech, typing, fillers, repeats


def verdict(text):
    """(fillers, repeats, typing) when the text reads as dictated, else None."""
    speech, typing, fillers, repeats = marks(text)
    if (fillers >= 2 or (fillers and repeats >= 2)) and speech >= 6 and speech >= 2 * typing:
        return fillers, repeats, typing
    return None


def note(prompt):
    if not re.search(r"\b(?:uh+|uhm|um+|erm|hmm|mm)\b", prompt, re.I):
        return ""  # no fillers at all: typed, or dictation too clean to tell
    pasted = "\n".join(PASTED.findall(prompt))
    own, from_paste = verdict(PASTED.sub(" ", prompt)), verdict(pasted) if pasted else None
    if not (own or from_paste):
        return ""
    if own and from_paste:
        subject = "This prompt, pasted part included, reads as dictated"
    elif own:
        subject = "This prompt reads as dictated"
    else:
        subject = "The pasted text reads as dictated or transcribed"
    hits = [h for h in (own, from_paste) if h]
    repeats = sum(h[1] for h in hits)
    evidence = f"{sum(h[0] for h in hits)} uh/um, {repeats} repeated word{'' if repeats == 1 else 's'}"
    if not any(h[2] for h in hits):
        evidence += ", no typing marks"
    # the opening line shows the user the hook worked and lets them catch a misread ask
    opening = "Read as dictation: <the ask in a sentence>" if own else "Read the pasted text as dictation"
    terms = f" Odd words may be garbled forms of {TERMS}." if TERMS else ""
    return (f"[dictation] {subject} ({evidence}). Read it for intent: skip fillers and false starts, and where "
            "the speaker corrects themselves, the last version stands. Speech-to-text mishears words, so be "
            "critical of what the task hinges on: names, numbers and amounts, dates, file and project names, "
            "technical terms, homophones (billed/built, fifteen/fifty) and negatives (can/can't). Open your "
            f"reply with one line, \"{opening}\", adding any word you corrected from context (\"built\" read "
            "as \"billed\"). Where a doubtful word would change what you do, quote it and ask before acting on "
            f"it; pass over harmless slips.{terms}")


if __name__ == "__main__":
    try:
        text = note(json.load(sys.stdin).get("prompt") or "")
        if text:
            print(text)
    except Exception:
        pass
