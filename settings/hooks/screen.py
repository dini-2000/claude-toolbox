#!/usr/bin/env python3
"""Screen something for malware before installing or running it. safe_get.py uses its pattern and
package checks; it also runs on its own.

    screen.py pypi <name> [version]    a Python package (pip install)
    screen.py npm <name> [version]     a JavaScript package (npm install, npx)
    screen.py winget <Id>              a Windows app from winget
    screen.py github <owner/repo>      a project on GitHub (clone it, then screen.py code <folder>)
    screen.py code <file or folder>    downloaded or cloned code, or a skill: flags risky lines to read
    screen.py file <file or folder>    a download (installer, zip): SHA-256 and a Microsoft Defender scan

Packages are checked against OSV (osv.dev), which carries the OpenSSF list of malicious packages and
known security flaws, and for age, users and a link to their source code. The last line is the verdict:
OK, CAUTION (read the reasons, then decide) or STOP (don't install it). Exit code 0, 1 or 2 to match.
A check that can't run gives CAUTION, never a silent OK. Needs only Python's standard library.
"""
import glob
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

LEVEL = ("OK", "CAUTION", "STOP")
worst = 0


def info(text):
    print("  " + text)


def flag(level, text):
    global worst
    worst = max(worst, level)
    print(f"{LEVEL[level]}: {text}")


def fetch(url, body=None):
    """JSON from a URL (POST when body is given); None on 404. Falls back to curl on certificate errors."""
    data = json.dumps(body).encode() if body is not None else None
    head = {"User-Agent": "claude-toolbox-screen", "Accept": "application/json"}
    if data:
        head["Content-Type"] = "application/json"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=head), timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise
    except urllib.error.URLError as e:
        if "CERTIFICATE" not in str(e).upper():
            raise
        args = ["curl", "-sSL", "-m", "30", "-A", head["User-Agent"], "-w", "\n%{http_code}"]
        if data:
            args += ["-H", "Content-Type: application/json", "-d", data.decode()]
        out = subprocess.run(args + [url], capture_output=True, text=True, timeout=45).stdout
        text, _, code = out.rpartition("\n")
        if code == "404":
            return None
        if code != "200":
            raise RuntimeError(f"HTTP {code}")
        return json.loads(text)


def try_fetch(url, what, body=None):
    try:
        return fetch(url, body), True
    except Exception as e:
        flag(1, f"couldn't check {what} ({type(e).__name__}); check it by hand")
        return None, False


def quiet_fetch(url):
    try:
        return fetch(url)
    except Exception:
        return None


def age_days(iso):
    return (datetime.now(timezone.utc) - datetime.fromisoformat(iso.replace("Z", "+00:00"))).days


def osv(ecosystem, name, version=None):
    q = {"package": {"name": name, "ecosystem": ecosystem}}
    if version:
        q["version"] = version
    d, ok = try_fetch("https://api.osv.dev/v1/query", "the OSV malware database", q)
    if not ok:
        return
    vulns = (d or {}).get("vulns", [])
    bad = [v for v in vulns if v["id"].startswith("MAL-")
           or re.search(r"\bmalware\b|\bmalicious\b", v.get("summary") or "", re.I)]
    for v in bad[:3]:
        flag(2, f"reported as malware in the OSV database: {v['id']} {(v.get('summary') or '').strip()[:90]}")
    other = [v for v in vulns if v not in bad]
    if other:
        flag(1, f"{len(other)} known security flaw(s) in {'version ' + version if version else 'this package'}: "
             + ", ".join(v["id"] for v in other[:3]) + (" and more" if len(other) > 3 else "")
             + ". A newer version may fix them.")
    elif not bad:
        info("OSV database: no malware reports" + (f" and no known flaws in {version}." if version else "."))


def source_link(urls):
    found = [u for u in urls if isinstance(u, str) and re.search(r"github\.com|gitlab\.com|bitbucket\.org|codeberg\.org", u)]
    if found:
        info("source code: " + re.sub(r"^git\+", "", found[0]))
    else:
        flag(1, "no link to its source code, so nobody can easily check what it does")


def pypi(name, version=None):
    d, ok = try_fetch(f"https://pypi.org/pypi/{urllib.parse.quote(name)}/json", "PyPI")
    if not ok:
        return osv("PyPI", name, version)
    if d is None:
        flag(2, f"no package called {name} on PyPI: check the spelling (packages taken down as malware vanish too)")
        return osv("PyPI", name)
    i = d["info"]
    version = version or i.get("version")
    info(f"{i.get('name')} {i.get('version')} (latest): {(i.get('summary') or '').strip()[:100]}")
    uploads = [f["upload_time_iso_8601"] for files in (d.get("releases") or {}).values()
               for f in files if f.get("upload_time_iso_8601")]
    if uploads:
        days = age_days(min(uploads))
        info(f"first released {min(uploads)[:10]} ({days} days ago), {len(d.get('releases') or {})} versions")
        if days < 90:
            flag(1, f"new package: first released {days} days ago")
    source_link(list((i.get("project_urls") or {}).values()) + [i.get("home_page")])
    if d.get("urls") and not any(f.get("packagetype") == "bdist_wheel" for f in d["urls"]):
        info("no ready-built version (wheel): pip runs the package's own setup code to install it")
    norm = re.sub(r"[-_.]+", "-", name).lower()
    s = quiet_fetch(f"https://pypistats.org/api/packages/{norm}/recent")
    week = ((s or {}).get("data") or {}).get("last_week")
    if week is None:
        info("download numbers unavailable")
    else:
        info(f"{week:,} downloads last week")
        if week < 1000:
            flag(1, f"few people use it ({week:,} downloads last week)")
    osv("PyPI", i.get("name") or name, version)


def npm(name, version=None):
    path = urllib.parse.quote(name, safe="@")
    m, ok = try_fetch(f"https://registry.npmjs.org/{path}/{urllib.parse.quote(version or 'latest')}", "npm")
    if not ok:
        return osv("npm", name, version)
    if m is None:
        flag(2, f"no package called {name}{'@' + version if version else ''} on npm: check the spelling "
                "(packages taken down as malware vanish too)")
        return osv("npm", name)
    info(f"{m.get('name')} {m.get('version')}: {(m.get('description') or '').strip()[:100]}")
    if m.get("deprecated"):
        flag(1, f"marked as no longer maintained: {str(m['deprecated'])[:100]}")
    repo = m.get("repository")
    source_link([repo.get("url") if isinstance(repo, dict) else repo, m.get("homepage")])
    s = quiet_fetch(f"https://api.npmjs.org/downloads/point/last-week/{name}")
    week = (s or {}).get("downloads")
    if week is None:
        info("download numbers unavailable")
    else:
        info(f"{week:,} downloads last week")
        if week < 1000:
            flag(1, f"few people use it ({week:,} downloads last week)")
    scripts = {k: v for k, v in (m.get("scripts") or {}).items() if k in ("preinstall", "install", "postinstall")}
    for k, v in scripts.items():
        text = f"runs code while installing ({k}: {str(v)[:80]})"
        if week is not None and week >= 10000:
            info(text + ": common in popular packages")
        else:
            flag(1, text + ": install with --ignore-scripts first and read that script")
    osv("npm", name, m.get("version"))


def winget(pid):
    if os.name != "nt":
        flag(1, "winget is Windows only")
        return
    try:
        r = subprocess.run(["winget", "show", "--id", pid, "-e", "--accept-source-agreements"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)
    except Exception as e:
        flag(1, f"couldn't run winget ({type(e).__name__})")
        return
    lines = [l.strip() for l in r.stdout.splitlines() if l.strip()]
    if r.returncode in (0x8A150014, -1978335212) or "No package found" in r.stdout:   # winget's "no package" code
        flag(2, f"no app with the ID {pid} in winget: find the exact ID with: winget search <name>")
        return
    if r.returncode != 0:
        flag(1, f"winget couldn't show {pid} (code {r.returncode}): {' '.join(lines[-2:])[:150]}")
        return
    keys = ("Found ", "Version:", "Publisher:", "Publisher Url:", "Homepage:", "License:", "Installer Url:")
    shown = [l for l in lines if l.startswith(keys)]
    for line in shown or lines[:8]:                    # labels are translated when Windows isn't in English
        info(line[:150])
    info("winget's catalogue is checked by Microsoft, and winget verifies the installer's SHA-256 before running it.")


def github(repo):
    repo = re.sub(r"\.git$", "", re.sub(r"^(https?://)?(www\.)?github\.com/", "", repo.strip())).strip("/")
    d, ok = try_fetch(f"https://api.github.com/repos/{repo}", "GitHub")
    if not ok:
        return
    if d is None:
        flag(2, f"no public GitHub project at {repo}")
        return
    stars, lic = d.get("stargazers_count", 0), (d.get("license") or {}).get("spdx_id") or "none"
    info(f"{d['full_name']}: {(d.get('description') or '').strip()[:100]}")
    info(f"{stars:,} stars, created {d['created_at'][:10]}, last change {d['pushed_at'][:10]}, licence {lic}")
    if d.get("fork"):
        flag(1, f"a copy (fork) of {(d.get('parent') or {}).get('full_name', 'another project')}: prefer the original")
    if stars < 50:
        flag(1, f"few people use it ({stars} stars)")
    if age_days(d["created_at"]) < 90:
        flag(1, f"new project: created {age_days(d['created_at'])} days ago")
    if d.get("archived"):
        flag(1, "archived: no longer maintained")
    info("Next: clone it, then run: screen.py code <folder>")


# (level, what it means, pattern). Markdown (skills, instructions) gets CAUTION at most, since it only
# tells Claude what to do; the same line in a script runs.
RULES = [
    (2, "downloads something and runs it",
     r"(curl|wget)\b[^|\n]*\|\s*(sudo\s+)?(ba|z)?sh\b"
     r"|(iwr|irm|Invoke-WebRequest|Invoke-RestMethod)\b[^\n]*\|\s*(iex|Invoke-Expression)\b"
     r"|DownloadString\s*\(|DownloadFile\s*\([^\n]*(Start-Process|\.exe)"
     r"|powershell(\.exe)?\b[^\n]*\s-e(nc|ncodedcommand)?\s+[A-Za-z0-9+/=]{40,}"),
    (2, "runs hidden (encoded) code",
     r"\b(exec|eval)\s*\([^\n]{0,40}(b64decode|base64|decompress|fromhex|rot.?13|marshal\.loads|unhexlify)"
     r"|\beval\s*\(\s*(atob|unescape|Buffer\.from|String\.fromCharCode)"
     r"|new\s+Function\s*\([^\n]{0,40}(atob|Buffer\.from)"
     r"|FromBase64String[^\n]*\b(iex|Invoke-Expression)\b|\b(iex|Invoke-Expression)\b[^\n]*FromBase64String"),
    (2, "reads saved passwords, browser data or keys",
     r"[\\/](Login Data|Local State|Web Data)\b|['\"](Login Data|Local State|Web Data)['\"]|Mozilla[\\/]+Firefox[\\/]+Profiles|key4\.db|logins\.json|wallet\.dat"
     r"|Local Storage[\\/]+leveldb|\.ssh[\\/]+id_|\.aws[\\/]+credentials|CryptUnprotectData|win32crypt"
     r"|find-generic-password|[\\/]Exodus[\\/]|nkbihfbeogaeaoehlefnkodbefgpgknn"),
    (2, "switches off security or covers its tracks",
     r"(Set|Add)-MpPreference|DisableRealtimeMonitoring|DisableAntiSpyware|netsh\s+(adv)?firewall\s+set[^\n]*\b(off|disable)"
     r"|vssadmin[^\n]*delete\s+shadows|wevtutil\s+cl\b|bcdedit[^\n]*recoveryenabled\s+no|spctl\s+--master-disable"
     r"|csrutil\s+disable"),
    (2, "opens a remote-control connection",
     r"/dev/tcp/\d|\bnc(at)?\b[^\n]*\s-e\s+\S*(ba)?sh|pty\.spawn\(\s*['\"]/bin/(ba)?sh"),
    (1, "sends data to a chat app or paste site",
     r"discord(app)?\.com/api/webhooks|api\.telegram\.org/bot|pastebin\.com/raw|webhook\.site|transfer\.sh|ngrok"),
    (1, "starts itself at every start-up",
     r"CurrentVersion\\+Run\b|schtasks(\.exe)?\s+/create|Register-ScheduledTask|Programs\\+Startup|LaunchAgents"
     r"|LaunchDaemons|crontab\s+-|@reboot"),
    (1, "talks to a bare internet address",
     r"https?://(?!127\.|0\.0\.0\.0|10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.)\d{1,3}(\.\d{1,3}){3}\b"),
    (1, "scrambled code (obfuscation)",
     r"(\\x[0-9a-fA-F]{2}){40,}|_0x[0-9a-f]{4,6}\b[^\n]{0,200}_0x[0-9a-f]{4,6}\b[^\n]{0,200}_0x[0-9a-f]{4,6}\b"),
    (1, "a long encoded blob", r"(?<![A-Za-z0-9+/,])(?<!base64,)[A-Za-z0-9+/]{400,}={0,2}"),
    (1, "tells Claude to hide things or drop its rules",
     r"(?i)ignore (all |any )?(previous|prior|earlier|above) instructions|do not (tell|inform|show) the user"
     r"|without (telling|asking|informing) the user|(turn|switch) off (the )?(auto mode|safety|permission)"),
]
CODE = {".py", ".pyw", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".sh", ".bash", ".zsh", ".ps1", ".psm1",
        ".bat", ".cmd", ".vbs", ".rb", ".pl", ".php", ".go", ".rs", ".java", ".cs", ".lua", ".applescript"}
DOCS = {".md", ".txt", ".mdc"}
PROGRAMS = {".exe", ".dll", ".scr", ".msi", ".com", ".pif", ".jar", ".apk", ".dmg", ".pkg", ".so", ".dylib"}
RULES = [(level, label, re.compile(rx)) for level, label, rx in RULES]
SKIP = {".git", "__pycache__", ".venv", "venv", ".mypy_cache", ".pytest_cache", ".next", ".cache"}
# "Never download files without asking the user" is a safety rule, not an attack: a hit on
# "without asking the user" is skipped when never / don't / do not / must not / should not governs
# its own clause (no punctuation or and / then / but / so / or in between, at most 6 words).
WITHOUT_USER = re.compile(r"(?i)without (telling|asking|informing) the user")
NEGATED = re.compile(r"(?i)\b(never|don'?t|do not|must not|should not)\b(\s+(?!(and|then|but|so|or)\b)[\w'/-]+){0,6}\s+$")


def negated(rx, line):
    hits = list(rx.finditer(line))
    return bool(hits) and all(WITHOUT_USER.fullmatch(m.group(0)) and NEGATED.search(line[:m.start()]) for m in hits)


def code(path):
    path = os.path.abspath(path)
    if not os.path.exists(path):
        flag(2, f"not found: {path}")
        return
    files = [path] if os.path.isfile(path) else []
    for root, dirs, fs in os.walk(path) if not files else ():
        dirs[:] = [d for d in dirs if d not in SKIP]
        files += [os.path.join(root, f) for f in fs]
    base = path if os.path.isdir(path) else os.path.dirname(path)
    hits, programs, scanned = {}, [], 0
    for f in files[:20000]:
        ext = os.path.splitext(f)[1].lower()
        name = os.path.basename(f)
        if ext in PROGRAMS:
            programs.append(os.path.relpath(f, base))
            continue
        is_doc = ext in DOCS
        if not (ext in CODE or is_doc or name in ("package.json", "setup.py", "setup.cfg", "pyproject.toml", "Makefile")
                or (not ext and os.path.getsize(f) < 200_000)):
            continue
        try:
            if os.path.getsize(f) > 3_000_000:
                continue
            with open(f, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except Exception:
            continue
        if "\x00" in text[:4096]:
            continue
        scanned += 1
        rel = os.path.relpath(f, base)
        if name == "package.json":
            for k in ("preinstall", "install", "postinstall"):
                if re.search(rf'"{k}"\s*:', text):
                    hits.setdefault((1, "runs code while installing (package.json)"), []).append(f"{rel}: {k}")
        if name == "setup.py" and re.search(r"urllib|requests\.|socket\.|subprocess|os\.system", text):
            hits.setdefault((1, "setup.py runs commands or goes online while installing"), []).append(rel)
        for n, line in enumerate(text.splitlines(), 1):
            if len(line) > 5000:
                line = line[:5000]
            for level, label, rx in RULES:
                if rx.search(line) and not negated(rx, line):
                    lv = min(level, 1) if is_doc else level
                    hits.setdefault((lv, label), []).append(f"{rel}:{n}: {line.strip()[:110]}")
    info(f"scanned {scanned} file(s) of code and instructions")
    if programs:
        flag(1, f"contains {len(programs)} ready-made program file(s), e.g. {programs[0]}: scan them with "
                "screen.py file <folder>")
    for (level, label), where in sorted(hits.items(), key=lambda kv: -kv[0][0]):
        flag(level, f"{label} ({len(where)} place(s)); read these lines:")
        for w in where[:3]:
            info(w)
    if not hits and not programs:
        info("no signs of malware in the code")


HAND_SCAN = ("Ask the user to right-click it in File Explorer, click Show more options (Windows 11), then Scan "
             "with Microsoft Defender; if the computer has another antivirus, its own scan option instead.")


def file(path):
    path = os.path.abspath(path)
    if not os.path.exists(path):
        flag(2, f"not found: {path}")
        return
    if os.path.isfile(path):
        h = hashlib.sha256()
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        info(f"SHA-256 {h.hexdigest()}: if the maker's download page lists one, they should match")
    if os.name != "nt":
        flag(1, "no command-line virus scanner on this computer; rely on the source checks")
        return
    found = sorted(glob.glob(r"C:\ProgramData\Microsoft\Windows Defender\Platform\*\MpCmdRun.exe"))
    exe = found[-1] if found else r"C:\Program Files\Windows Defender\MpCmdRun.exe"
    try:
        r = subprocess.run([exe, "-Scan", "-ScanType", "3", "-File", path],
                           capture_output=True, text=True, errors="replace", timeout=1800)
    except Exception as e:
        flag(1, f"Microsoft Defender couldn't scan it ({type(e).__name__}). {HAND_SCAN}")
        return
    out = " ".join((r.stdout + " " + r.stderr).split())
    if re.search(r"found\s+[1-9]\d*\s+threat", out, re.I) or r.returncode == 2:
        flag(2, "Microsoft Defender found a threat: " + out[-200:])
    elif r.returncode == 0:
        info("Microsoft Defender: no threats found.")
    else:
        flag(1, f"Microsoft Defender's scan didn't finish (code {r.returncode}): {out[-150:]}. {HAND_SCAN}")


CMDS = {"pypi": pypi, "npm": npm, "winget": winget, "github": github, "code": code, "file": file}


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # Windows would use its own code page
    except Exception:
        pass
    if len(sys.argv) < 3 or sys.argv[1] not in CMDS:
        print(__doc__)
        sys.exit(1)
    kind, target = sys.argv[1], sys.argv[2]
    print(f"Screening {kind} {target}")
    try:
        CMDS[kind](target, *sys.argv[3:4])
    except Exception as e:
        flag(1, f"the check stopped early ({type(e).__name__}: {str(e)[:100]}); check it by hand")
    print("Verdict: " + LEVEL[worst] + (" (no warning signs found)", " (read the reasons above, then decide)",
                                        " (don't install it; tell the user what was found)")[worst])
    sys.exit(worst)


if __name__ == "__main__":
    main()
