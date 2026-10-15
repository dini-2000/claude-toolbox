#!/usr/bin/env python3
"""Search the on-demand skills by a task's key terms (catalog.tsv next to this file).

    python3 ~/.claude/skills/skill-router/find.py "DCF valuation of a listed bank"

Prints the five closest skills and says when none fits well."""
import math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
STOP = set("""a able about above account accounts across actually after again against ain all almost already alright also always am an and any anybody anyone anything are aren around as ask asks at bad based basically be because been before being below best better between big bit both but by came can case cases certain chat chats claude come comes coming couldn covering covers current currently day days did didn do does doesn doing don done down during e e.g each early easy eight either else end enough etc even ever every everyone everything example examples fact feel feels felt few first five for former four from full further g gave general get gets getting give given gives giving goes going gone good got great guess guidance guide hadn half handoff handover hard has hasn have haven having he help helps her here hers herself high him himself his hmm how i if in include includes including instead into is isn it its itself just keep keeping keeps kept kind knew know knows large last late later latter least less let lets level levels like literally little ll long look looked looking looks lot lots low made main make makes making many may maybe me mean means meant mentions mightn month months more most much must mustn my myself need needed needing needn needs neither never new next nine no nor not nothing now of off often okay old on once one only or other our ours ourselves out over own part particular parts per phrases please point points possible pretty previous probably provide provides put puts putting quite rather re real really recent recently right said same saw say says second see seem seemed seems seen sees session sessions seven several shan she short should shouldn simple six skill skills small so some somebody someone something sometimes soon sort start step steps still stuff such sure take taken takes taking task tasks tell tells ten than thank thanks that the their theirs them themselves then there these they thing things think thinks third this those thought three through time times to today token tokens told tomorrow too took tried tries trigger triggers try trying twice two uh um umm under until up use used user users uses using ve very via want wanted wanting wants was wasn way ways we week weeks well went were weren what when where whether which while who whole whom why will with within without won work wouldn yeah year years yes yesterday yet you your yours yourself yourselves""".split())
SUFFIXES = (("ational", "ate"), ("ization", "ize"), ("isation", "ize"), ("ations", "ate"), ("ation", "ate"), ("ysis", "yze"),
            ("yses", "yze"), ("ytics", "yze"), ("ytic", "yze"), ("ies", "y"), ("ied", "y"), ("ing", ""), ("ers", "er"),
            ("ed", ""), ("es", "e"), ("s", ""))


def stem(w):
    if len(w) <= 4 or (w.endswith(("ss", "us", "is")) and not w.endswith("ysis")): return w
    for a, b in SUFFIXES:
        if w.endswith(a) and len(w) - len(a) >= 3:
            w = w[:-len(a)] + b
            break
    if w.endswith("ise"): w = w[:-3] + "ize"
    return w[:-1] if w.endswith("e") and len(w) > 4 else w


def words(text):
    return [stem(w) for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOP and len(w) > 2]


def grams(ws):
    return set(ws) | {a + " " + b for a, b in zip(ws, ws[1:])}


def joined(text):
    """A word and the number beside it as one term, the way skill names write them: SOC 2 -> soc2, ISO 27001 -> iso27001, 10-K -> 10k."""
    raw = re.findall(r"[a-z0-9]+", text.lower())
    return {a + b for a, b in zip(raw, raw[1:])
            if (a.isalpha() and b.isdigit() and a not in STOP) or (a.isdigit() and b.isalpha() and len(b) <= 2)}


def load():
    skills, df = {}, {}
    with open(os.path.join(HERE, "catalog.tsv"), encoding="utf-8") as f:
        next(f)
        for line in f:
            name, flags, desc = line.rstrip("\n").split("\t", 2)
            if "auto" in flags: continue
            parts = [stem(p) for p in name.split("-") if p not in STOP]
            skills[name] = {"terms": grams(words(desc)) | joined(desc) | set(parts), "name": parts, "flags": flags, "desc": desc}
    for s in skills.values():
        for t in s["terms"]: df[t] = df.get(t, 0) + 1
    return skills, {t: math.log((len(skills) + 1) / (c + 0.5)) for t, c in df.items()}


def rank(q, skills, idf, typed=frozenset()):
    """(score, name, matched terms) for every skill sharing a term with the query term set q, best first. On equal scores the
    skill whose name the query spells out (typed: the query's words as written) comes first, then the shorter description,
    so a bundle index that lists a skill does not outrank it."""
    out = []
    for name, s in skills.items():
        m = q & s["terms"]
        if not m: continue
        score = sum(idf[t] * (2 if t in s["name"] else 1) for t in m) + (4 if s["name"] and all(p in q for p in s["name"]) else 0)
        parts = name.split("-")
        out.append((-round(score, 1), -sum(p in typed for p in parts) / len(parts), len(s["terms"]), name, m))
    return [(-score, name, m) for score, _, _, name, m in sorted(out, key=lambda x: x[:3])]


def main():
    query = " ".join(sys.argv[1:])
    skills, idf = load()
    q = grams(words(query)) | {t for t in joined(query) if t in idf}
    if not q: sys.exit('usage: find.py "<key terms of the task>"')
    typed = set(re.findall(r"[a-z0-9]+", query.lower())) | joined(query)
    top = rank(q, skills, idf, typed)[:5]
    if not top: return print("No skill shares a term with this task: none fits.")
    unknown = max(idf.values())
    weight = sum(idf.get(t, unknown) for t in q if " " not in t)
    cover = sum(idf[t] for t in top[0][2] if " " not in t) / weight
    print("Closest skills (read ~/.claude/skills/<name>/SKILL.md before using one):")
    for score, name, m in top:
        s = skills[name]
        first = re.split(r"(?<=[.!?])\s", s["desc"], 1)[0][:150]
        print(f"- {name}{' [' + s['flags'] + ']' if s['flags'] else ''}: {first}")
    print(f"Best match covers {cover:.0%} of the terms." + (" Weak: no skill covers most of this task. Use one only if its method clearly helps; otherwise say none fits and carry on." if cover < 0.45 else ""))


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):  # a Windows pipe uses the ANSI code page, which cannot print some descriptions' arrows
        sys.stdout.reconfigure(encoding="utf-8")
    main()
