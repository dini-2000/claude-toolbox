#!/usr/bin/env python3
"""safe_get: everything from the internet comes in through here, into quarantine, and is screened before use.

  safe_get.py plan <spec>... [--name N] [--venv DIR] [--python X.Y] [--max-mb N]   look it up; downloads nothing
  safe_get.py fetch <job> --yes "<the user's words>"      download into quarantine, check fingerprints, screen
  safe_get.py screen <job or path>                        screen a job again, or any file or folder, read-only
  safe_get.py intake <path>... [--copy]                   quarantine and screen files that came another way
  safe_get.py clear <job> <file or glob>... --reason "<what you read>" [--user "<the user's words>"]
  safe_get.py release <job> [<dest>] [--root SUBDIR] [--only GLOB] [--move] [--overwrite]
  safe_get.py install <job>                               install a screened pypi or brew job
  safe_get.py jobs                                        recent jobs and their verdicts

Specs: github:owner/repo[@ref][:path or glob]   url:https://...[#sha256=<hex>]   pypi:name[==version]
       npm:name[@version]   brew:formula
Scripts: sys.path.insert(0, "<this folder>"); from safe_get import download, download_many;
         download(url, dest_dir) or download_many([(url, relpath, sha256 or None), ...], dest_dir, name).
         Bytes that arrive inside an API response (a generated image): save_bytes(data, "name.png", dest_dir,
         source="<service and model>") or save_bytes_many([(data, relpath), ...], dest_dir, source).

A job is ~/Quarantine.noindex/<date>-<name>/ (Spotlight skips .noindex): plan.json, files/, verdicts.json, report.md.
Downloads are https only (redirects too), capped in size, written without execute permission and, on macOS,
with the quarantine flag, and checked against a published fingerprint where one exists (git blob SHA, PyPI sha256, npm
integrity, Homebrew sha256, a GitHub release digest, or #sha256=); a file that fails is discarded. Screening reads
files and runs nothing: ClamAV when installed, the malware patterns and package checks of screen.py
(beside this file) and checks by type (programs and installers, PDF actions, Office macros and remote
templates, archive paths and bombs, wheel RECORDs, hidden characters, injected instructions). Release and install
refuse anything not passed or cleared, and both are logged in ledger.tsv in the quarantine folder.
Exit codes: 0 passed, 1 something to read, 2 blocked (the user decides), 3 failed.
Environment: SAFE_GET_QUARANTINE, SAFE_GET_LEDGER, SAFE_GET_CLAMSCAN, SAFE_GET_FRESHCLAM. pypi specs need uv,
brew specs Homebrew, and the deeper PDF checks PyMuPDF; each is optional.
"""
import argparse
import base64
import bisect
import collections
import concurrent.futures as cf
import contextlib
import csv
import datetime
import fnmatch
import gzip
import hashlib
import importlib.util
import io
import json
import os
import platform
import plistlib
import re
import shlex
import shutil
import stat
import subprocess
import sys
import tarfile
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
QROOT = os.path.expanduser(os.environ.get("SAFE_GET_QUARANTINE", "~/Quarantine.noindex"))
LEDGER = os.environ.get("SAFE_GET_LEDGER", os.path.join(QROOT, "ledger.tsv"))
KIT = os.path.join(HERE, "screen.py")
UV = shutil.which("uv") or os.path.expanduser("~/.local/bin/uv")
BREW = shutil.which("brew") or "/opt/homebrew/bin/brew"
CLAMSCAN = os.environ.get("SAFE_GET_CLAMSCAN") or shutil.which("clamscan") or "/opt/homebrew/bin/clamscan"
FRESHCLAM = os.environ.get("SAFE_GET_FRESHCLAM") or shutil.which("freshclam") or "/opt/homebrew/bin/freshclam"
CLAMSTAMP = os.path.join(QROOT, ".freshclam_checked")  # when freshclam last checked for new signatures
CLAM_EVERY = 4 * 3600  # ClamAV publishes new signatures several times a day; its own default checks every 2 hours
CMD = f"{shlex.quote(sys.executable)} {shlex.quote(os.path.abspath(__file__))}"
UA = "safe-get/1 (Claude Code)"
MB = 1 << 20
LEVELS = ("pass", "review", "block")
UV_ENV = dict(os.environ, UV_PYTHON_DOWNLOADS="never", UV_NO_CONFIG="1")
BREW_ENV = dict(os.environ, HOMEBREW_NO_ANALYTICS="1", HOMEBREW_NO_ENV_HINTS="1", HOMEBREW_NO_AUTO_UPDATE="1",
                HOMEBREW_NO_INSTALL_UPGRADE="1", HOMEBREW_NO_INSTALLED_DEPENDENTS_CHECK="1")
BOTTLE_TAGS = ("arm64_tahoe", "arm64_sequoia", "arm64_sonoma", "arm64_ventura", "arm64_monterey", "arm64_big_sur", "all")


class Fail(Exception):
    pass


def now():
    return datetime.datetime.now().strftime("%d %b %Y %H:%M")


def human(n):
    if n is None:
        return "size unknown"
    return f"{n / MB:.1f} MB" if n >= MB // 10 else f"{max(1, round(n / 1024))} KB"


def session():
    return os.environ.get("CLAUDE_CODE_SESSION_ID", "")[:8] or "-"


def run(cmd, timeout=120, env=None, cwd=None):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env, cwd=cwd)
    except (OSError, subprocess.TimeoutExpired) as e:
        return subprocess.CompletedProcess(cmd, 127, "", f"{type(e).__name__}: {e}")


# ---------------------------------------------------------------- web: https only, redirects included

class HttpsOnly(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not newurl.lower().startswith("https://"):
            raise urllib.error.URLError("refused a redirect away from https: " + newurl[:120])
        new = super().redirect_request(req, fp, code, msg, headers, newurl)
        if new is not None and urllib.parse.urlparse(newurl).netloc != urllib.parse.urlparse(req.full_url).netloc:
            for k in [k for k in new.headers if k.lower() in ("authorization", "cookie")]:
                del new.headers[k]
        return new


OPENER = urllib.request.build_opener(HttpsOnly)


def http(url, method="GET", headers=None, timeout=60):
    if not url.lower().startswith("https://"):
        raise Fail("https only: " + url[:120])
    h = {"User-Agent": UA}
    h.update(headers or {})
    return OPENER.open(urllib.request.Request(url, method=method, headers=h), timeout=timeout)


def get_json(url, headers=None):
    h = {"Accept": "application/json"}
    h.update(headers or {})
    try:
        with http(url, headers=h) as r:
            return json.loads(r.read(64 * MB))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        if e.code in (403, 429) and "api.github.com" in url:
            raise Fail("GitHub's limit of 60 look-ups an hour without sign-in is used up; try again within the hour")
        raise Fail(f"{url[:100]}: HTTP {e.code}")


def head_size(url, headers=None):
    """Size from the headers, following redirects; None when the server won't say."""
    for method, extra in (("HEAD", {}), ("GET", {"Range": "bytes=0-0"})):
        try:
            h = dict(headers or {}, **extra)
            with http(url, method=method, headers=h, timeout=30) as r:
                cr = r.headers.get("Content-Range") or ""
                n = cr.rpartition("/")[2] if "/" in cr else r.headers.get("Content-Length")
                return (int(n) if n and n.isdigit() else None), r.geturl(), r.headers
        except urllib.error.HTTPError as e:
            if e.code not in (400, 403, 405, 501):
                raise Fail(f"{url[:100]}: HTTP {e.code}")
    return None, url, {}


# ---------------------------------------------------------------- jobs

def jpath(d, *a):
    return os.path.join(d, *a)


def load(d, name, default=None):
    try:
        with open(jpath(d, name)) as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def save(d, name, obj):
    tmp = jpath(d, name + ".tmp")
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1)
    os.replace(tmp, jpath(d, name))


def all_jobs():
    if not os.path.isdir(QROOT):
        return []
    js = [jpath(QROOT, x) for x in os.listdir(QROOT) if os.path.exists(jpath(QROOT, x, "plan.json"))]
    return sorted(js, key=lambda x: os.path.getmtime(jpath(x, "plan.json")), reverse=True)


def job_dir(job):
    if job in ("last", "latest"):
        js = all_jobs()
        if js:
            return js[0]
        raise Fail("no jobs yet")
    p = os.path.abspath(os.path.expanduser(job))
    if os.path.exists(jpath(p, "plan.json")):
        return p
    if os.path.exists(jpath(QROOT, job, "plan.json")):
        return jpath(QROOT, job)
    hits = [x for x in all_jobs() if job in os.path.basename(x)]
    if len(hits) == 1:
        return hits[0]
    names = ", ".join(os.path.basename(x) for x in hits[:5])
    raise Fail(f"no single job matches {job!r}" + (f" ({names})" if hits else "") + f"; list them: {CMD} jobs")


def new_job(name, files=True):
    os.makedirs(QROOT, mode=0o700, exist_ok=True)
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-.")[:40] or "job"
    base = jpath(QROOT, datetime.date.today().isoformat() + "-" + slug)
    d, n = base, 1
    while os.path.exists(d):
        n += 1
        d = f"{base}-{n}"
    os.makedirs(jpath(d, "files") if files else d, mode=0o700)
    return d


def safe_rel(path):
    p = path.replace("\\", "/")
    parts = [x for x in p.split("/") if x not in ("", ".")]
    if p.startswith("/") or not parts or ".." in parts or any("\x00" in x for x in parts):
        raise Fail("unsafe path: " + path[:120])
    return "/".join(parts)


def inside(base, rel):
    dest = os.path.abspath(os.path.join(base, safe_rel(rel)))
    if not dest.startswith(os.path.abspath(base) + os.sep):
        raise Fail("unsafe path: " + rel[:120])
    return dest


HIDDEN_NAME = re.compile("[\x00-\x1f\x7f\u200b-\u200f\u202a-\u202e\u2066-\u2069\ufeff]")


def clean_name(name):
    name = HIDDEN_NAME.sub("", os.path.basename(name.replace("\\", "/"))).strip()
    return re.sub(r"\s+", " ", name).lstrip(".")[:150] or "download"


def mark(paths, recursive=False):
    """Set macOS's quarantine flag, so Gatekeeper checks anything here before it first runs."""
    v = "0081;%08x;safe_get;%s" % (int(time.time()), str(uuid.uuid4()).upper())
    paths = list(paths)
    for i in range(0, len(paths), 200):
        run(["/usr/bin/xattr"] + (["-r"] if recursive else []) + ["-w", "com.apple.quarantine", v] + paths[i:i + 200],
            timeout=120)


def xattr(path, name, hexa=False):
    r = run(["/usr/bin/xattr", "-px" if hexa else "-p", name, path], timeout=30)
    return r.stdout.strip() if r.returncode == 0 else None


def where_from(path):
    h = xattr(path, "com.apple.metadata:kMDItemWhereFroms", hexa=True)
    try:
        return [str(x) for x in plistlib.loads(bytes.fromhex(re.sub(r"\s+", "", h)))] if h else []
    except Exception:
        return []


def ledger(rows):
    new = not os.path.exists(LEDGER)
    with open(LEDGER, "a") as f:
        if new:
            f.write("when\tjob\tfile\tsource\tversion\tsha256\tlicence\tverdict\tdestination\n")
        for r in rows:
            f.write("\t".join(str(x if x is not None else "-").replace("\t", " ").replace("\n", " ") for x in r) + "\n")


# ---------------------------------------------------------------- screen.py (beside this file), used as is

_KIT = None


def kit():
    global _KIT
    if _KIT is None:
        try:
            spec = importlib.util.spec_from_file_location("kit_screen", KIT)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            _KIT = mod
        except Exception:
            _KIT = False
    return _KIT or None


def kit_flags(lines):
    return [x.strip() for x in lines if x.startswith(("CAUTION:", "STOP:"))]


def kit_run(*args):
    """screen.py pypi / npm in a process of its own (it keeps its verdict in a global)."""
    if not os.path.exists(KIT):
        return ["CAUTION: screen.py is missing, so " + " ".join(args) + " went unchecked"]
    r = run([sys.executable, KIT, *args], timeout=180)
    return kit_flags(r.stdout.splitlines())


def kit_github(repo, info):
    k = kit()
    if not k:
        return []
    orig, buf = k.fetch, io.StringIO()
    k.fetch = lambda url, body=None: info if url.rstrip("/").endswith("/repos/" + repo) else orig(url, body)
    k.worst = 0
    try:
        with contextlib.redirect_stdout(buf):
            k.github(repo)
    except Exception as e:
        return [f"CAUTION: screen.py's GitHub check stopped ({type(e).__name__})"]
    finally:
        k.fetch = orig
    return kit_flags(buf.getvalue().splitlines())


# ---------------------------------------------------------------- plan

def plan_github(p, spec):
    m = re.match(r"^([\w.-]+/[\w.-]+?)(?:\.git)?(?:@([^:]+))?(?::(.+))?$", spec)
    if not m:
        raise Fail(f"github spec {spec!r}: use github:owner/repo[@ref][:path or glob]")
    repo, ref, sel = m.group(1), m.group(2), (m.group(3) or "").strip("/")
    info = get_json(f"https://api.github.com/repos/{repo}", {"Accept": "application/vnd.github+json"})
    if not info:
        raise Fail(f"no public GitHub project at {repo}")
    repo = info.get("full_name") or repo
    sha = resolve_ref(repo, ref)
    entries, glob = None, any(c in sel for c in "*?[")
    # list just the folder that holds the selection, so a big project needs no full listing: the selection itself
    # when it is a folder, else its parent (GitHub answers 422 for a file); the full listing covers the rest
    tries = [re.split(r"[*?[]", sel)[0].rpartition("/")[0]] if glob else [sel, sel.rpartition("/")[0]]
    for folder in [f for f in tries if f]:
        try:
            sub = get_json(f"https://api.github.com/repos/{repo}/git/trees/{sha}:{urllib.parse.quote(folder)}?recursive=1")
        except Fail:
            continue
        if sub and not sub.get("truncated"):
            entries = [dict(e, path=folder + "/" + e["path"]) for e in sub.get("tree", [])]
            break
    if entries is None:
        t = get_json(f"https://api.github.com/repos/{repo}/git/trees/{sha}?recursive=1")
        if not t:
            raise Fail(f"no file list for {repo} at {sha[:12]}")
        if t.get("truncated"):
            raise Fail(f"{repo} is too big for one listing; name a folder: github:{repo}@{sha[:12]}:<folder>")
        entries = t.get("tree", [])
    if sel:
        entries = [e for e in entries if (fnmatch.fnmatchcase(e["path"], sel) if glob
                                          else e["path"] == sel or e["path"].startswith(sel + "/"))]
    links = [e["path"] for e in entries if e.get("mode") == "120000"]
    subs = [e["path"] for e in entries if e.get("type") == "commit"]
    blobs = [e for e in entries if e.get("type") == "blob" and e.get("mode") != "120000"]
    if not blobs:
        raise Fail(f"nothing matches {sel!r} in {repo} at {sha[:12]}")
    lic = (info.get("license") or {}).get("spdx_id") or "none stated"
    seen, total = set(), 0
    for e in blobs:
        rel = safe_rel(f"{repo}/{e['path']}")
        if rel.lower() in seen:
            p["warnings"].append(f"{e['path']}: same name as another file apart from capitals; skipped")
            continue
        seen.add(rel.lower())
        total += e.get("size") or 0
        p["items"].append({"src": f"github:{repo}@{sha[:12]}:{e['path']}", "url": "https://raw.githubusercontent.com/"
                           f"{repo}/{sha}/{urllib.parse.quote(e['path'])}", "path": rel, "size": e.get("size"),
                           "expect": {"algo": "git-blob", "value": e["sha"]}, "version": sha[:12], "licence": lic})
    if links:
        p["warnings"].append(f"{len(links)} symbolic link(s) left out, e.g. {links[0]}")
    if subs:
        p["warnings"].append(f"{len(subs)} submodule(s) (other projects) not included, e.g. {subs[0]}")
    p["warnings"] += [f"{repo}: {x}" for x in kit_github(repo, info)]
    p["summary"].append(f"github:{repo} at commit {sha[:12]} ({sel or 'all files'}): {len(seen)} files, "
                        f"{human(total)}; licence {lic}; {info.get('stargazers_count', 0):,} stars, "
                        f"last change {str(info.get('pushed_at'))[:10]}")
    p.setdefault("github", []).append(repo)


def resolve_ref(repo, ref):
    if ref and re.fullmatch(r"[0-9a-f]{40}", ref):
        return ref
    r = run(["git", "ls-remote", f"https://github.com/{repo}.git", ref or "HEAD"], timeout=60,
            env=dict(os.environ, GIT_TERMINAL_PROMPT="0"))
    rows = [x.split("\t") for x in r.stdout.splitlines() if "\t" in x]
    want = ["HEAD"] if not ref else [f"refs/tags/{ref}^{{}}", f"refs/heads/{ref}", f"refs/tags/{ref}", ref]
    for w in want:
        for sha, name in rows:
            if name == w:
                return sha
    if rows:
        raise Fail(f"{ref} in {repo} is ambiguous; name one of: " + ", ".join(n for _, n in rows[:4]))
    if ref and re.fullmatch(r"[0-9a-f]{7,39}", ref):
        try:
            with http(f"https://api.github.com/repos/{repo}/commits/{ref}",
                      headers={"Accept": "application/vnd.github.sha"}) as resp:
                sha = resp.read(100).decode().strip()
            if re.fullmatch(r"[0-9a-f]{40}", sha):
                return sha
        except Exception:
            pass
    raise Fail(f"no branch, tag or commit {ref or 'HEAD'} in {repo}")


def plan_url(p, spec):
    url, _, frag = spec.partition("#")
    m = re.match(r"sha256=([0-9a-fA-F]{64})$", frag)
    expect = {"algo": "sha256", "value": m.group(1).lower()} if m else None
    if not url.lower().startswith("https://"):
        raise Fail("https only: " + url[:100])
    size, final, hdrs = head_size(url)
    if not final.lower().startswith("https://"):
        raise Fail("the address moved away from https: " + final[:100])
    disp = (hdrs.get("Content-Disposition") or "") if hdrs else ""
    dm = re.search(r"filename\*=(?:UTF-8'')?([^;]+)|filename=\"?([^\";]+)", disp, re.I)
    raw = urllib.parse.unquote((dm.group(1) or dm.group(2)).strip()) if dm else \
        urllib.parse.unquote(urllib.parse.urlparse(final).path.rsplit("/", 1)[-1])
    name = clean_name(raw)
    if name != raw.strip() and HIDDEN_NAME.search(raw):
        p["warnings"].append(f"{name}: its name as sent hides characters, a common disguise ({raw!r})")
    gh = re.match(r"https://github\.com/([\w.-]+/[\w.-]+)/releases/download/([^/]+)/([^/?#]+)$", url)
    if gh and not expect:
        rel = get_json(f"https://api.github.com/repos/{gh.group(1)}/releases/tags/{gh.group(2)}")
        for a in (rel or {}).get("assets", []):
            if a.get("name") == urllib.parse.unquote(gh.group(3)) and str(a.get("digest", "")).startswith("sha256:"):
                expect = {"algo": "sha256", "value": a["digest"][7:].lower(), "from": "GitHub's release digest"}
    ctype = ((hdrs.get("Content-Type") if hdrs else "") or "").split(";")[0].strip()
    ext = os.path.splitext(name)[1].lower()
    if not expect:
        p["warnings"].append(f"{name}: no published fingerprint to check it against, so only the screen vouches for it")
    if ctype == "text/html" and ext not in (".html", ".htm", ""):
        p["warnings"].append(f"{name}: the server answers with a web page, maybe a sign-in or error page")
    if ext in BLOCK_EXT or ext in (".zip", ".tgz", ".gz") and re.search(r"(?i)(setup|install|\.app)", name):
        p["warnings"].append(f"{name}: a program or installer; Claude never runs it, and only the user's word "
                             "releases it from quarantine")
    rel = name
    while any(i["path"].lower() == rel.lower() for i in p["items"]):
        rel = "_" + rel
    p["items"].append({"src": "url:" + url, "url": url, "path": rel, "size": size, "expect": expect,
                       "version": "-", "licence": "-", "final": final})
    host = urllib.parse.urlparse(final).netloc
    p["summary"].append(f"url: {name} from {host}, {human(size)}" + (f" ({ctype})" if ctype else "") +
                        ("; fingerprint: " + expect.get("from", "given") if expect else ""))


def venv_python(venv):
    try:
        cfg = open(jpath(venv, "pyvenv.cfg")).read()
    except OSError:
        return None
    m = re.search(r"^\s*(?:version_info|version)\s*=\s*(\d+\.\d+)", cfg, re.M)
    return m.group(1) if m else None


def default_python():
    r = run([UV, "python", "find", "--no-python-downloads"], env=UV_ENV, timeout=60)
    path = r.stdout.strip()
    r = run([path, "-c", "import sys; print('%d.%d' % sys.version_info[:2])"], timeout=30) if path else r
    return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else "3.12"


def uv_platform():
    """uv's name for this computer's platform, so the lock picks wheels that install here."""
    arch = "aarch64" if platform.machine().lower() in ("arm64", "aarch64") else "x86_64"
    if sys.platform == "darwin":
        return arch + "-apple-darwin"
    if sys.platform == "win32":
        return arch + "-pc-windows-msvc"
    return arch + "-unknown-linux-gnu"


def plat_score(plat):
    """How well a wheel's platform tag fits this computer: 0 = not at all."""
    if plat == "any":
        return 1
    arm = platform.machine().lower() in ("arm64", "aarch64")
    if sys.platform == "darwin":
        m = re.match(r"macosx_(\d+)_(\d+)_(\w+)$", plat)
        mac = int((platform.mac_ver()[0] or "99").split(".")[0])
        if not m or int(m.group(1)) > mac:
            return 0
        return 3 if m.group(3) == ("arm64" if arm else "x86_64") else 2 if m.group(3) == "universal2" else 0
    if sys.platform.startswith("linux"):
        m = re.match(r"(?:manylinux\d*(?:_\d+_\d+)?|linux)_(\w+)$", plat)
        return 3 if m and m.group(1) == ("aarch64" if arm else "x86_64") else 0
    if sys.platform == "win32":
        return 3 if plat == ("win_arm64" if arm else "win_amd64") else 0
    return 0


def wheel_score(fn, pyver):
    """How well a wheel fits CPython pyver on this computer: 0 = not at all."""
    parts = fn[:-4].split("-")
    if len(parts) < 5:
        return 0
    major, minor = (int(x) for x in pyver.split(".")[:2])
    cp, best = f"cp{major}{minor}", 0
    for py in parts[-3].split("."):
        for abi in parts[-2].split("."):
            for plat in parts[-1].split("."):
                ps = plat_score(plat)
                if not ps:
                    continue
                if abi == "none" and py in ("py3", f"py{major}{minor}", cp, f"py{major}"):
                    s = 1
                elif abi == "abi3" and re.fullmatch(r"cp3(\d+)", py) and int(py[3:]) <= minor:
                    s = 2
                elif abi == cp and py == cp:
                    s = 3
                else:
                    continue
                best = max(best, ps * 10 + s)
    return best


def licence_of(info):
    lic = (info.get("license_expression") or info.get("license") or "").strip()
    if not lic or len(lic) > 60:
        cls = [c.split("::")[-1].strip() for c in info.get("classifiers") or [] if c.startswith("License ::")]
        lic = cls[0] if cls else (lic[:40] + "..." if lic else "none stated")
    return lic


def plan_pypi(p, d, reqs, venv, python):
    venv = os.path.abspath(os.path.expanduser(venv or ".venv"))
    pyver = python or venv_python(venv) or default_python()
    with open(jpath(d, "requirements.in"), "w") as f:
        f.write("\n".join(reqs) + "\n")
    r = run([UV, "pip", "compile", "requirements.in", "-o", "requirements.txt", "--generate-hashes", "--no-build",
             "--no-header", "--no-annotate", "--quiet", "--python-version", pyver, "--python-platform",
             uv_platform()], timeout=300, env=UV_ENV, cwd=d)
    if r.returncode:
        raise Fail("couldn't work out the packages: " + " ".join(r.stderr.split())[-400:])
    pins = []
    for line in open(jpath(d, "requirements.txt")).read().replace("\\\n", " ").splitlines():
        m = re.match(r"\s*([A-Za-z0-9._-]+)(?:\[[^\]]*\])?==([^\s;]+)", line)
        if m:
            pins.append((m.group(1), m.group(2), set(re.findall(r"--hash=sha256:([0-9a-f]{64})", line))))

    def one(pin):
        name, ver, hashes = pin
        j = get_json(f"https://pypi.org/pypi/{name}/{ver}/json")
        if not j:
            raise Fail(f"PyPI has no {name} {ver}")
        files = [f for f in j.get("urls", []) if f.get("packagetype") == "bdist_wheel"
                 and f.get("digests", {}).get("sha256") in hashes]
        files = sorted(files, key=lambda f: wheel_score(f["filename"], pyver), reverse=True)
        if not files or not wheel_score(files[0]["filename"], pyver):
            raise Fail(f"{name} {ver} has no ready-built wheel for this computer and Python {pyver}; building it from "
                       "source runs its own setup code, so that isn't supported")
        f = files[0]
        return f, name, ver, licence_of(j.get("info") or {}), [f"{name}: {x}" for x in kit_run("pypi", name, ver)]

    with cf.ThreadPoolExecutor(8) as ex:
        got = list(ex.map(one, pins))
    total, lines = 0, []
    for f, name, ver, lic, warns in got:
        sha = f["digests"]["sha256"]
        total += f.get("size") or 0
        lines.append(f"{name}=={ver} --hash=sha256:{sha}")
        p["items"].append({"src": f"pypi:{name}=={ver}", "url": f["url"], "path": "pypi/" + clean_name(f["filename"]),
                           "size": f.get("size"), "expect": {"algo": "sha256", "value": sha}, "version": ver,
                           "licence": lic, "pkg": "pypi"})
        p["warnings"] += warns
    with open(jpath(d, "install.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")
    p["pypi"] = {"venv": venv, "python": pyver}
    names = ", ".join(f"{n} {v}" for _, n, v, _, _ in got[:12]) + (" ..." if len(got) > 12 else "")
    p["summary"].append(f"pypi: {' '.join(reqs)} for Python {pyver} into {venv}: {len(got)} wheels ({names}), "
                        f"{human(total)}; licences " + ", ".join(sorted({g[3] for g in got}))[:200])


def plan_npm(p, spec):
    m = re.match(r"^(@?[^@\s]+)(?:@(.+))?$", spec)
    if not m:
        raise Fail(f"npm spec {spec!r}: use npm:name[@version]")
    name, ver = m.group(1), m.group(2) or "latest"
    j = get_json(f"https://registry.npmjs.org/{urllib.parse.quote(name, safe='@')}/{urllib.parse.quote(ver)}")
    if not j:
        raise Fail(f"npm has no {name}@{ver}")
    dist, ver = j.get("dist") or {}, j.get("version", ver)
    integ = str(dist.get("integrity") or "")
    expect = {"algo": "sha512", "value": integ[7:]} if integ.startswith("sha512-") else \
        ({"algo": "sha1", "value": dist["shasum"]} if dist.get("shasum") else None)
    size, _, _ = head_size(dist["tarball"])
    lic = j.get("license") if isinstance(j.get("license"), str) else "see package"
    p["items"].append({"src": f"npm:{name}@{ver}", "url": dist["tarball"], "size": size, "expect": expect,
                       "path": "npm/" + clean_name(f"{name.replace('/', '-').lstrip('@')}-{ver}.tgz"),
                       "version": ver, "licence": lic, "pkg": "npm"})
    hooks = [k for k in ("preinstall", "install", "postinstall", "prepare") if k in (j.get("scripts") or {})]
    if hooks:
        p["warnings"].append(f"{name}: runs code when installed ({', '.join(hooks)}); installs here skip it "
                             "(--ignore-scripts)")
    deps = list((j.get("dependencies") or {}).keys())
    if deps:
        p["warnings"].append(f"{name}: needs {len(deps)} other package(s) ({', '.join(deps[:6])}), not included; "
                             "plan them too, or install from a lockfile with --ignore-scripts")
    p["warnings"] += [f"{name}: {x}" for x in kit_run("npm", name, ver)]
    p["summary"].append(f"npm: {name} {ver}, {human(size)} packed ({dist.get('fileCount', '?')} files); licence {lic}")
    p["npm"] = p.get("npm", []) + [f"{name}@{ver}"]


def plan_brew(p, names):
    if not os.path.exists(BREW):
        raise Fail("Homebrew isn't installed")
    r = run([BREW, "install", "--dry-run", *names], timeout=300, env=BREW_ENV)
    if r.returncode:
        raise Fail("brew couldn't plan it: " + " ".join((r.stderr or r.stdout).split())[-300:])
    out = r.stdout
    todo = []
    # each list holds names, now followed by their versions ("clamav 1.5.4 json-c 0.18"), on one line or several
    for block in re.findall(r"==> Would install \d+ (?:formula|formulae|dependenc\w+)[^\n]*:\n((?:(?!==>).*(?:\n|$))+)", out):
        toks, i = block.split(), 0
        while i < len(toks):
            name, i = toks[i], i + 1
            if i < len(toks) and re.fullmatch(r"\d[\w.+~-]*", toks[i]):
                i += 1
            if name not in todo:
                todo.append(name)
    if not todo:
        raise Fail("nothing to install (already installed?): " + " ".join(out.split())[-200:])
    r = run([BREW, "info", "--json=v2", *todo], timeout=120, env=BREW_ENV)
    if r.returncode:
        raise Fail("brew info failed: " + " ".join(r.stderr.split())[-200:])
    formulae = {f["name"]: f for f in json.loads(r.stdout).get("formulae", [])}
    total, lics = 0, set()
    for n in todo:
        f = formulae.get(n) or next((x for x in formulae.values() if n in (x.get("full_name"), x.get("name"))), None)
        if not f:
            raise Fail(f"brew has no formula {n}")
        files = ((f.get("bottle") or {}).get("stable") or {}).get("files") or {}
        tag = next((t for t in BOTTLE_TAGS if t in files), None)
        if not tag:
            raise Fail(f"{n} has no ready-built bottle for this computer; building from source isn't supported")
        ver = f["versions"]["stable"]
        rebuild = ((f.get("bottle") or {}).get("stable") or {}).get("rebuild") or 0
        size, _, _ = head_size(files[tag]["url"], {"Authorization": "Bearer QQ=="})
        total += size or 0
        lic = f.get("license") or "none stated"
        lics.add(lic)
        p["items"].append({"src": f"brew:{n}", "url": files[tag]["url"], "size": size, "pkg": "brew", "name": n,
                           "path": f"brew/{n}--{ver}.{tag}.bottle{'.%d' % rebuild if rebuild else ''}.tar.gz",
                           "expect": {"algo": "sha256", "value": files[tag]["sha256"]}, "version": ver,
                           "licence": lic, "bottles": {t: x["sha256"] for t, x in files.items()}})
        if f.get("deprecated") or f.get("disabled"):
            p["warnings"].append(f"{n}: marked deprecated or disabled by Homebrew")
        if f.get("post_install_defined"):
            p["warnings"].append(f"{n}: runs its Homebrew post-install step (reviewed homebrew-core code) when installed")
    deps = [n for n in todo if n not in names]
    p["brew"] = {"formulae": names, "todo": todo}
    p["summary"].append(f"brew: {' '.join(names)} with {len(deps)} dependenc{'y' if len(deps) == 1 else 'ies'} not "
                        f"yet installed ({', '.join(deps) or 'none'}): {len(todo)} bottles, {human(total)}; "
                        f"licences {', '.join(sorted(lics))}")


def cmd_plan(specs, name=None, venv=None, python=None, max_mb=300):
    groups = collections.OrderedDict((k, []) for k in ("github", "url", "pypi", "npm", "brew"))
    for s in specs:
        kind, sep, rest = s.partition(":")
        if s.lower().startswith("https://"):
            kind, rest = "url", s
        elif kind == "http" or s.lower().startswith("url:http:"):
            raise Fail("https only: " + s[:100])
        elif not sep or kind not in groups:
            raise Fail(f"unknown spec {s!r}: use github:, url:, pypi:, npm: or brew:")
        groups[kind].append(rest.strip())
    first = next(((k, v[0]) for k, v in groups.items() if v))
    auto = {"github": lambda x: x.split("@")[0].split(":")[0].split("/")[-1],
            "url": lambda x: clean_name(urllib.parse.urlparse(x).path.rsplit("/", 1)[-1]).rsplit(".", 1)[0],
            "pypi": lambda x: re.split(r"[=<>!~\[ ;]", x)[0], "npm": lambda x: x.lstrip("@").split("@")[0],
            "brew": lambda x: x}[first[0]](first[1])
    d = new_job(name or auto)
    p = {"job": os.path.basename(d), "kind": "fetch", "created": now(), "session": session(), "specs": specs,
         "max_file": max_mb * MB, "items": [], "summary": [], "warnings": [], "approved": None}
    try:
        for x in groups["github"]:
            plan_github(p, x)
        for x in groups["url"]:
            plan_url(p, x)
        if groups["pypi"]:
            plan_pypi(p, d, groups["pypi"], venv, python)
        for x in groups["npm"]:
            plan_npm(p, x)
        if groups["brew"]:
            plan_brew(p, groups["brew"])
        big = [i for i in p["items"] if (i.get("size") or 0) > p["max_file"]]
        if big:
            raise Fail(f"{big[0]['path']} is {human(big[0]['size'])}, over the {max_mb} MB cap; plan again with "
                       f"--max-mb if the user agrees")
    except BaseException:
        shutil.rmtree(d, ignore_errors=True)
        raise
    save(d, "plan.json", p)
    total = sum(i.get("size") or 0 for i in p["items"])
    unknown = sum(1 for i in p["items"] if i.get("size") is None)
    print(f"Plan {p['job']} (nothing downloaded yet)")
    for s in p["summary"]:
        print("  " + s)
    print("  Warning signs: " + ("none" if not p["warnings"] else ""))
    for w in p["warnings"][:25]:
        print("    " + w)
    if len(p["warnings"]) > 25:
        print(f"    ... {len(p['warnings']) - 25} more in {jpath(d, 'plan.json')}")
    print(f"  In all: {len(p['items'])} file(s), {human(total)}" + (f" ({unknown} of unknown size)" if unknown else "")
          + f", into quarantine at {d}")
    print("Ask the user (one yes covers this batch), naming what, where from and the size. On their yes:")
    print(f"  {CMD} fetch {p['job']} --yes \"<their words>\"")
    return 0


# ---------------------------------------------------------------- fetch

def new_hash(expect, size):
    a = (expect or {}).get("algo")
    if a == "git-blob":
        return hashlib.sha1(b"blob %d\0" % (size or 0))
    return hashlib.new(a) if a in ("sha256", "sha512", "sha1") else None


def hash_ok(expect, h):
    if expect["algo"] == "sha512":
        return base64.b64encode(h.digest()).decode() == expect["value"]
    return h.hexdigest() == expect["value"].lower()


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(MB), b""):
            h.update(b)
    return h.hexdigest()


def fetch_item(base, it, cap):
    dest = inside(base, it["path"])
    if it.get("sha256") and os.path.isfile(dest) and sha256_of(dest) == it["sha256"]:
        return it, "ok"
    os.makedirs(os.path.dirname(dest), mode=0o700, exist_ok=True)
    tmp, err, exp = dest + ".part", "?", it.get("expect")
    for attempt in range(3):
        err = "?"
        if os.path.lexists(tmp):
            os.remove(tmp)
        try:
            h256, hx, n = hashlib.sha256(), new_hash(exp, it.get("size")), 0
            fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
            with os.fdopen(fd, "wb") as f, http(it["url"], headers=it.get("headers"), timeout=120) as r:
                while True:
                    b = r.read(MB)
                    if not b:
                        break
                    n += len(b)
                    if n > cap:
                        raise Fail(f"bigger than the {cap // MB} MB cap; stopped")
                    h256.update(b)
                    f.write(b)
                    if hx:
                        hx.update(b)
            break
        except Fail as e:
            err = str(e)
            break
        except urllib.error.HTTPError as e:
            err = f"HTTP {e.code}"
            if e.code in (401, 403, 404, 410):
                break
        except urllib.error.URLError as e:
            err = f"URLError: {str(e.reason)[:120]}"
            if "refused a redirect" in err:
                break
        except Exception as e:
            err = f"{type(e).__name__}: {str(e)[:100]}"
        time.sleep(1 + 2 * attempt)
    else:
        n = None
    if n is None or err != "?":
        if os.path.lexists(tmp):
            os.remove(tmp)
        return it, "not downloaded: " + err
    if hx and not hash_ok(exp, hx):
        os.remove(tmp)
        return it, "fingerprint doesn't match; discarded"
    os.replace(tmp, dest)
    it["sha256"], it["got"] = h256.hexdigest(), n
    return it, "ok"


def brew_fetch(d, p, items):
    names = [i["name"] for i in items]
    r = run([BREW, "fetch", "--formula", *names], timeout=3600, env=BREW_ENV)
    problems = []
    for it in items:
        c = run([BREW, "--cache", "--formula", it["name"]], timeout=60, env=BREW_ENV).stdout.strip()
        if r.returncode and not os.path.exists(c):
            problems.append((it["path"], "brew fetch failed: " + " ".join(r.stderr.split())[-200:]))
            continue
        tag = re.search(r"\.([a-z0-9_]+)\.bottle\.", os.path.basename(c))
        want = it.get("bottles", {}).get(tag.group(1)) if tag else None
        if not want or not os.path.isfile(c):
            problems.append((it["path"], f"brew's download wasn't found ({c})"))
            continue
        got = sha256_of(c)
        if got != want:
            problems.append((it["path"], "fingerprint doesn't match Homebrew's; not copied"))
            continue
        it["path"] = "brew/" + os.path.basename(c)
        it["cache"], it["sha256"], it["got"] = os.path.realpath(c), got, os.path.getsize(c)
        dest = inside(jpath(d, "files"), it["path"])
        os.makedirs(os.path.dirname(dest), mode=0o700, exist_ok=True)
        shutil.copyfile(it["cache"], dest)
        os.chmod(dest, 0o644)
    return problems


def do_fetch(d, p):
    base, cap = jpath(d, "files"), p.get("max_file", 300 * MB)
    plain = [i for i in p["items"] if i.get("pkg") != "brew"]
    bottles = [i for i in p["items"] if i.get("pkg") == "brew"]
    problems = []
    with cf.ThreadPoolExecutor(8) as ex:
        for it, status in ex.map(lambda i: fetch_item(base, i, cap), plain):
            if status != "ok":
                problems.append((it["path"], status))
    if bottles:
        problems += brew_fetch(d, p, bottles)
    got = [i for i in p["items"] if i.get("sha256")]
    mark([inside(base, i["path"]) for i in got])
    p["fetched"] = {"when": now(), "ok": len(got), "problems": problems}
    save(d, "plan.json", p)
    return problems


def cmd_fetch(job, yes):
    d = job_dir(job)
    p = load(d, "plan.json")
    if p.get("kind") != "fetch":
        raise Fail("this job holds files that came another way; screen or release it instead")
    if not (yes or "").strip():
        raise Fail('needs the user\'s yes, in their words: --yes "<what they said>"')
    p["approved"] = {"words": yes.strip(), "when": now(), "session": session()}
    save(d, "plan.json", p)
    problems = do_fetch(d, p)
    got = p["fetched"]["ok"]
    print(f"Fetched {got} of {len(p['items'])} file(s) into {jpath(d, 'files')}" +
          (f"; {len(problems)} problem(s):" if problems else ", every fingerprint checked where one was published"))
    for path, why in problems[:15]:
        print(f"  {path}: {why}")
    if not got:
        return 3
    code = screen_job(d)
    return max(code, 1) if problems else code


# ---------------------------------------------------------------- screen: kinds and names

PROGRAM_KINDS = {"macho": "a Mac program", "elf": "a Linux program", "windows-exe": "a Windows program",
                 "pkg": "a Mac installer package", "dmg": "a Mac disk image", "java-class": "a Java program",
                 "applescript": "a compiled AppleScript"}
BLOCK_EXT = {".app", ".workflow", ".action", ".terminal", ".fileloc", ".scpt", ".scptd", ".jar", ".class", ".exe",
             ".dll", ".scr", ".msi", ".com", ".pif", ".lnk", ".hta", ".wsf", ".jse", ".vbe", ".reg", ".cpl", ".inf",
             ".sys", ".ocx", ".gadget", ".msix", ".appx", ".deb", ".rpm", ".appimage", ".iso", ".img", ".vhd",
             ".vhdx", ".dmg", ".pkg", ".mpkg", ".kext", ".prefpane", ".saver", ".qlgenerator", ".mdimporter", ".xpc",
             ".appex", ".plugin", ".bundle", ".xll", ".apk"}
REVIEW_EXT = {".command", ".tool", ".bat", ".cmd", ".ps1", ".psm1", ".vbs"}
BUNDLES = {".app", ".bundle", ".framework", ".plugin", ".kext", ".pkg", ".mpkg", ".workflow", ".action", ".appex",
           ".xpc", ".prefpane", ".saver", ".qlgenerator", ".mdimporter", ".scptd"}
CODE_EXT = {".py", ".pyw", ".pyi", ".pth", ".ipynb", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".sh", ".bash",
            ".zsh", ".fish", ".ps1", ".psm1", ".bat", ".cmd", ".vbs", ".rb", ".pl", ".php", ".go", ".rs", ".java",
            ".cs", ".lua", ".applescript", ".command", ".tool", ".swift", ".c", ".h", ".cc", ".cpp", ".m", ".r",
            ".jl", ".kt", ".scala", ".groovy", ".gradle", ".mk", ".cmake", ".nix", ".vue", ".svelte"}
CODE_NAMES = {"Makefile", "makefile", "GNUmakefile", "Dockerfile", "Rakefile", "Gemfile", "Vagrantfile", "setup.py",
              "conftest.py", "Brewfile", "Justfile", "justfile", "package.json", "pyproject.toml", "setup.cfg"}
MARKUP_EXT = {".html", ".htm", ".xhtml", ".svg", ".xml", ".xsl", ".xslt", ".plist"}
PROSE_EXT = {".md", ".mdc", ".markdown", ".txt", ".rst", ".text"}
DATA_EXT = {".csv", ".tsv", ".json", ".jsonl", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf", ".css", ".scss",
            ".less", ".tex", ".bib", ".srt", ".vtt", ".log", ".sql", ".graphql", ".proto", ".env", ".properties",
            ".lock", ".template", ".j2", ".jinja", ".map", ".webmanifest", ".editorconfig", ".gitignore"}
ARCHIVE_EXT = {".zip", ".tar", ".gz", ".tgz", ".bz2", ".tbz", ".xz", ".txz", ".zst", ".7z", ".rar", ".jar", ".whl",
               ".egg", ".apk", ".dmg", ".pkg", ".iso", ".cab", ".xpi", ".crx", ".nupkg", ".vsix"}
EXPECT = {".pdf": {"pdf"}, ".png": {"png"}, ".jpg": {"jpeg"}, ".jpeg": {"jpeg"}, ".gif": {"gif"}, ".webp": {"webp"},
          ".ico": {"ico", "png"}, ".bmp": {"bmp"}, ".tif": {"tiff"}, ".tiff": {"tiff"}, ".ttf": {"font"},
          ".otf": {"font"}, ".woff": {"font"}, ".woff2": {"font"}, ".ttc": {"font"}, ".zip": {"zip"},
          ".docx": {"zip"}, ".xlsx": {"zip"}, ".pptx": {"zip"}, ".docm": {"zip"}, ".xlsm": {"zip"}, ".pptm": {"zip"},
          ".odt": {"zip"}, ".ods": {"zip"}, ".odp": {"zip"}, ".epub": {"zip"}, ".whl": {"zip"}, ".jar": {"zip"},
          ".doc": {"ole", "rtf"}, ".xls": {"ole"}, ".ppt": {"ole"}, ".msg": {"ole"}, ".rtf": {"rtf"},
          ".gz": {"gzip"}, ".tgz": {"gzip"}, ".bz2": {"bzip2"}, ".xz": {"xz"}, ".zst": {"zstd"}, ".7z": {"7z"},
          ".rar": {"rar"}, ".tar": {"tar"}, ".mp4": {"media"}, ".mov": {"media"}, ".m4a": {"media"},
          ".heic": {"media"}, ".mp3": {"media"}}
DOCLIKE = set(EXPECT) - ARCHIVE_EXT | PROSE_EXT | DATA_EXT | MARKUP_EXT | {".jpg", ".jpeg", ".png"}
DOUBLE_EXT = re.compile(r"(?i)\.(pdf|docx?|xlsx?|pptx?|rtf|txt|csv|jpe?g|png|gif|heic|mp[34]|mov|zip)[\s._-]*\."
                        r"(app|command|tool|exe|scr|bat|cmd|com|pif|js|jse|vbs|vbe|wsf|hta|jar|pkg|mpkg|dmg|sh|scpt|"
                        r"terminal|workflow|lnk)$")


WEAK_MAGIC = {"bmp", "font", "media", "gif", "windows-exe"}  # letters a text file could start with


def sniff(head, name=""):
    kind = sniff_magic(head, name)
    if kind in WEAK_MAGIC and b"\x00" not in head[:8192]:
        return "text"
    return kind


def sniff_magic(head, name):
    if head[:4] in (b"\xfe\xed\xfa\xce", b"\xfe\xed\xfa\xcf", b"\xce\xfa\xed\xfe", b"\xcf\xfa\xed\xfe"):
        return "macho"
    if head[:4] == b"\xca\xfe\xba\xbe":
        return "java-class" if name.lower().endswith(".class") else "macho"
    if head[:4] == b"\x7fELF":
        return "elf"
    if head[:2] == b"MZ":
        return "windows-exe"
    if head[:4] == b"xar!":
        return "pkg"
    if head.startswith(b"FasdUAS"):
        return "applescript"
    if head[:2] == b"#!":
        return "script"
    if head.startswith(b"%PDF-") or b"%PDF-" in head[:1024] and name.lower().endswith(".pdf"):
        return "pdf"
    if head[:4] in (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"):
        return "zip"
    if head[:8] == b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1":
        return "ole"
    if head[:5] == b"{\\rtf":
        return "rtf"
    for magic, kind in ((b"\x1f\x8b", "gzip"), (b"BZh", "bzip2"), (b"\xfd7zXZ\x00", "xz"), (b"\x28\xb5\x2f\xfd", "zstd"),
                        (b"7z\xbc\xaf\x27\x1c", "7z"), (b"Rar!\x1a\x07", "rar"), (b"\x89PNG\r\n\x1a\n", "png"),
                        (b"\xff\xd8\xff", "jpeg"), (b"GIF8", "gif"), (b"\x00\x00\x01\x00", "ico"), (b"BM", "bmp"),
                        (b"II*\x00", "tiff"), (b"MM\x00*", "tiff"), (b"ID3", "media"), (b"OggS", "media"),
                        (b"fLaC", "media"), (b"\x00\x01\x00\x00", "font"), (b"true", "font"), (b"OTTO", "font"),
                        (b"wOFF", "font"), (b"wOF2", "font"), (b"ttcf", "font")):
        if head.startswith(magic):
            return kind
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return "webp"
    if head[4:8] == b"ftyp":
        return "media"
    if len(head) > 262 and head[257:262] == b"ustar":
        return "tar"
    if b"\x00" not in head[:8192]:
        return "text"
    return "binary"


def ext_of(name):
    low = name.lower()
    for double in (".tar.gz", ".tar.bz2", ".tar.xz", ".tar.zst"):
        if low.endswith(double):
            return "." + double.rsplit(".", 1)[1]
    return os.path.splitext(low)[1]


def name_checks(add, name):
    if re.search("[\u202a-\u202e\u2066-\u2069]", name):
        add(2, "disguised name", 0, "its name hides a right-to-left control character, a common way to disguise a program")
    elif HIDDEN_NAME.search(name):
        add(1, "odd name", 0, "its name holds invisible characters")
    if DOUBLE_EXT.search(name):
        add(2, "disguised name", 0, "two extensions: looks like a document but opens as a program")
    if re.search(r"\s{6,}\S", name):
        add(1, "odd name", 0, "a long run of spaces in its name (can push the real extension out of sight)")


def sig_info(path, kind):
    """codesign, pkgutil and Gatekeeper's verdict, read without running anything."""
    out = []
    r = run(["/usr/bin/codesign", "-dv", "--verbose=2", path], timeout=60)
    auth = re.findall(r"^Authority=(.+)$", r.stderr, re.M)
    out.append("not signed" if r.returncode else "signed by " + (auth[0] if auth else "an ad-hoc signature"))
    if kind == "pkg":
        r = run(["/usr/sbin/pkgutil", "--check-signature", path], timeout=60)
        st = re.search(r"Status: (.+)", r.stdout)
        out.append("package: " + (st.group(1).strip() if st else "no signature"))
    t = {"pkg": "install", "dmg": "open"}.get(kind, "exec")
    cmd = ["/usr/sbin/spctl", "--assess", "--type", t, "-vv"]
    if kind == "dmg":
        cmd += ["--context", "context:primary-signature"]
    r = run(cmd + [path], timeout=60)
    txt = " ".join((r.stderr + r.stdout).replace(path, "").split())
    out.append("Gatekeeper: " + (txt[:160] or "no answer").lstrip(": "))
    return "; ".join(out)


# ---------------------------------------------------------------- screen: text

CF_TAGS = re.compile("[\U000e0001\U000e0020-\U000e007f]+")
CF_BIDI = re.compile("[\u202a-\u202e\u2066-\u2069]")
CF_ZW = re.compile("[\u200b\u200c\u2060-\u2064\u180e\ufeff]")
VS_RUN = re.compile("[\ufe00-\ufe0f\U000e0100-\U000e01ef]{4,}")
INJECT = re.compile(
    r"(?i)\byou are now\b|\bnew instructions\b|\bsystem prompt\b|\bdeveloper mode\b|\bjailbreak|\bexfiltrat"
    r"|reveal (your|the) (instructions|prompt)|send (it|them|this|the [\w ]{1,20}) to https?://"
    r"|disregard (all |any |the )?(previous|prior|above|earlier)|<\|?(im_start|im_end)\|?>|\[/?INST\]")
HIDDEN_COMMENT = re.compile(r"<!--(.*?)-->", re.S)
HC_WORDS = re.compile(r"(?i)\b(claude|assistant|ai|llm|model|instruction|ignore|must|system|prompt|agent|execute|run)\b")
URL = re.compile(r"https?://([A-Za-z0-9.-]+)")
CAPS = {  # what code can do: counted, with the riskier kinds listed for reading in a script that stands alone
    "network call": (0, r"\brequests\.(get|post|put|patch|delete|request|Session)\b|urllib\.request|urlopen\(|http\.client"
                        r"|\bhttpx\b|aiohttp|\bfetch\(|\baxios\b|XMLHttpRequest|WebSocket\(|socket\.(socket|create_connection)"
                        r"|\bcurl\b|\bwget\b|Invoke-WebRequest"),
    "sends data out": (1, r"\b(requests|httpx|session|client)\.(post|put|patch)\(|method\s*[:=]\s*['\"](POST|PUT)['\"]"
                         r"|curl\b[^\n]*\s(-d|--data\S*|-F|--form|-T|--upload-file)\s"),
    "runs commands": (0, r"\bsubprocess\b|os\.system\(|os\.popen\(|os\.exec\w*\(|os\.spawn\w*\(|child_process|execSync|spawnSync"
                         r"|\bspawn\(|shell\s*=\s*True"),
    "dynamic code": (0, r"(?<![\w.])(eval|exec)\s*\(|\bcompile\(|__import__\(|importlib\.import_module\(|pickle\.loads?\("
                        r"|marshal\.loads?\(|\bctypes\b|new\s+Function\(|vm\.runIn"),
    "reads secrets from the environment": (0, r"(os\.environ|getenv|process\.env)[^\n]{0,40}(KEY|TOKEN|SECRET|PASSW|CREDENTIAL|AUTH)"),
    "touches credential files": (1, r"\.ssh\b|\.aws\b|\.netrc|\.npmrc|\.pypirc|\.docker/config|\.kube/config|\.config/gh\b"
                                    r"|Keychains|security\s+find-|\.gnupg|id_rsa|id_ed25519"),
    "changes start-up files": (1, r"\.(bashrc|zshrc|bash_profile|zprofile)\b|LaunchAgents|LaunchDaemons|crontab|launchctl"
                                  r"|systemctl\s+enable|/etc/(cron|systemd|rc\.)"),
    "deletes files": (0, r"shutil\.rmtree|os\.(remove|unlink|rmdir)\(|\brm\s+-[a-zA-Z]*[rf]|fs\.(rm|rmSync|unlink)"),
    "wipes a home or root folder": (1, r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*\s+(/|~|\$HOME|\"\$HOME\"|\*)(\s|$|/\s|/\*)"),
    "installs software": (0, r"\bpip3?\s+install\b|\bnpm\s+(i|install)\b|\bnpx\s|\bbrew\s+install\b|apt(-get)?\s+install"
                             r"|\bgem\s+install\b|\buv\s+(pip|add|tool)\b"),
    "decodes hidden data": (0, r"base64\.(b64decode|decodebytes)|\batob\(|Buffer\.from\([^)]*base64|codecs\.decode\([^)]*rot"
                               r"|zlib\.decompress|bytes\.fromhex|unhexlify|String\.fromCharCode"),
}
CAPS = {k: (lv, re.compile(rx)) for k, (lv, rx) in CAPS.items()}
HTML_ACTIVE = re.compile(r"(?i)<script\b|\son[a-z]{3,}\s*=|javascript:|<iframe\b|<object\b|<embed\b|<foreignObject\b"
                         r"|<meta[^>]+http-equiv\s*=\s*['\"]?refresh")
CSV_FORMULA = re.compile(r"""(?m)^["']?[=@+]\s*[A-Za-z]+\(|[,;\t]["']?=\s*(cmd|HYPERLINK|WEBSERVICE|IMPORTXML|DDE)""", re.I)


def text_checks(add, text, name, ext, package, dom):
    """Checks on a text file's contents. add(level, category, line, detail)."""
    if text.startswith("\ufeff"):
        text = text[1:]
    nl = [m.start() for m in re.finditer("\n", text)]

    def where(pos):
        i = bisect.bisect_left(nl, pos)
        start = nl[i - 1] + 1 if i else 0
        end = nl[i] if i < len(nl) else len(text)
        return i + 1, text[start:end].strip()[:160]

    base = os.path.basename(name)
    code = ext in CODE_EXT or base in CODE_NAMES or text.startswith("#!")
    prose = ext in PROSE_EXT or ext.startswith(".pdf") or ext.startswith(".office")
    markup = ext in MARKUP_EXT
    if text.startswith("version https://git-lfs.github.com/spec/"):
        add(1, "placeholder", 1, "a Git LFS placeholder: the real file wasn't downloaded")
    for m in CF_TAGS.finditer(text):
        run_ = m.group(0)
        if m.start() and text[m.start() - 1] == "\U0001f3f4" and len(run_) <= 8 and run_.endswith("\U000e007f"):
            continue  # a regional flag emoji, such as England's
        add(2, "hidden characters", where(m.start())[0],
            "invisible tag characters (a way to smuggle hidden instructions): " +
            "".join(chr(ord(c) - 0xE0000) for c in run_ if 0xE0020 <= ord(c) <= 0xE007E)[:120])
    for m in CF_BIDI.finditer(text):
        ln, line = where(m.start())
        add(2 if code else 1, "hidden characters", ln, f"text-direction control U+{ord(m.group(0)):04X}: {line!r}")
    zw = list(CF_ZW.finditer(text))
    if zw:
        ln, line = where(zw[0].start())
        add(1 if code else 0, "hidden characters", ln, f"{len(zw)} zero-width character(s), first: {line!r}")
    for m in VS_RUN.finditer(text):
        add(1, "hidden characters", where(m.start())[0], f"a run of {len(m.group(0))} invisible variation selectors")
    for m in INJECT.finditer(text):
        ln, line = where(m.start())
        add(0 if package else 1, "instructions to Claude", ln, line)
    if markup or prose or ext in (".plist",):
        for m in HIDDEN_COMMENT.finditer(text):
            c = m.group(1).strip()
            if HC_WORDS.search(c) and "noqa" not in c:
                add(0 if package else 1, "hidden comment", where(m.start())[0], " ".join(c.split())[:150])
    k = kit()
    if k and (code or prose or markup or ext in DATA_EXT or not ext):
        doc = (ext in getattr(k, "DOCS", PROSE_EXT) or ext in DATA_EXT or prose and not code) and base not in CODE_NAMES
        for level, label, rx in k.RULES:
            for m in rx.finditer(text):
                ln, line = where(m.start())
                if k.negated(rx, line):
                    continue
                lv = min(level, 1) if doc else level
                add(0 if package and lv == 1 else lv, label, ln, line)
    if code:
        for label, (lv, rx) in CAPS.items():
            for m in rx.finditer(text):
                ln, line = where(m.start())
                add(0 if package else lv, label, ln, line)
        if any(len(x) > 5000 for x in text.split("\n")) and not re.search(r"\.min\.|\.map$", base):
            add(0, "very long lines (packed code)", 0, "")
    if markup:
        hits = HTML_ACTIVE.findall(text)
        if hits:
            add(1 if ext == ".svg" else 0, "active content (scripts)", 0, f"{len(hits)} place(s)")
    if ext in (".csv", ".tsv"):
        for m in CSV_FORMULA.finditer(text):
            ln, line = where(m.start())
            add(1, "spreadsheet formula that runs", ln, line)
    if base == "package.json":
        try:
            scripts = json.loads(text).get("scripts") or {}
        except Exception:
            scripts = {}
        for hook in ("preinstall", "install", "postinstall", "prepare"):
            if hook in scripts:
                add(1, "runs code when installed", 0, f"package.json {hook}: {str(scripts[hook])[:120]}")
    if base == "setup.py" and re.search(r"urllib|requests\.|socket\.|subprocess|os\.system", text):
        add(1, "setup.py goes online or runs commands", 0, "it runs when the package is built from source")
    if ext == ".pth" and re.search(r"(?m)^\s*import\b", text):
        add(1, "runs at every Python start", 0, " | ".join(x.strip() for x in text.splitlines() if x.strip())[:160])
    for m in URL.finditer(text):
        dom[m.group(1).lower()] += 1


# ---------------------------------------------------------------- screen: documents and archives

PDF_KEYS = (("/Launch", 2, "starts a program or opens a file (/Launch)"), ("/JavaScript", 1, "has JavaScript"),
            ("/EmbeddedFile", 1, "carries embedded files"), ("/RichMedia", 1, "has embedded media or Flash"),
            ("/XFA", 1, "has an XFA form, which can carry scripts"), ("/SubmitForm", 1, "can send form data to a server"),
            ("/ImportData", 1, "can import data"), ("/GoToE", 1, "links into an embedded file"),
            ("/AA", 0, "automatic actions"), ("/OpenAction", 0, "an action on opening"), ("/URI", 0, "links"))


def pdf_checks(add, path, dom):
    found, names, text = collections.Counter(), [], ""
    try:
        import pymupdf as fitz  # PyMuPDF's own name; "fitz" is the old alias, which later releases may drop
    except Exception:
        try:
            import fitz
        except Exception:
            fitz = None
    if fitz:
        try:
            doc = fitz.open(path)
        except Exception as e:
            add(1, "pdf", 0, f"won't open as a PDF ({type(e).__name__}): damaged, or not really a PDF")
            return
        try:
            if doc.needs_pass:
                add(1, "pdf", 0, "password-protected, so its contents can't be checked")
            for x in range(1, doc.xref_length()):
                try:
                    s = doc.xref_object(x, compressed=False)
                except Exception:
                    continue
                for key, _, _ in PDF_KEYS + (("/JS", 1, ""),):
                    if re.search(re.escape(key) + r"(?![A-Za-z])", s):
                        found[key] += 1
            try:
                names = list(doc.embfile_names())
            except Exception:
                pass
            parts = []
            for i, page in enumerate(doc):
                if i >= 300:
                    break
                try:
                    parts.append(page.get_text())
                except Exception:
                    pass
            text = "\n".join(parts)
        finally:
            doc.close()
    else:
        with open(path, "rb") as f:
            raw = f.read(300 * MB)
        for key, _, _ in PDF_KEYS + (("/JS", 1, ""),):
            if key.encode() in raw:
                found[key] += 1
    found["/JavaScript"] += found.pop("/JS", 0)
    for key, level, what in PDF_KEYS:
        if found[key]:
            extra = f": {', '.join(names[:5])}" if key == "/EmbeddedFile" and names else ""
            add(level, "pdf", 0, what + extra)
    if text:
        text_checks(add, text, "pdf text", ".pdf-text", False, dom)


REMOTE_PARTS = {"attachedTemplate": "a template", "oleObject": "an embedded object", "frame": "a frame",
                "subDocument": "a sub-document", "control": "a control", "package": "a package"}


def office_checks(add, z, names, dom):
    for n in names:
        low = n.lower()
        if low.endswith(("vbaproject.bin", "vbadata.xml")):
            add(2, "office", 0, f"has macros ({n})")
        elif "/activex/" in low:
            add(2, "office", 0, f"has an ActiveX control ({n})")
        elif "/embeddings/" in low:
            add(1, "office", 0, f"carries an embedded file or object ({n})")
    text = []
    for n in names:
        low = n.lower()
        if low.endswith(".rels"):
            x = z.read(n)[:2 * MB].decode("utf-8", "replace")
            for m in re.finditer(r"<Relationship\b[^>]*>", x):
                r = m.group(0)
                if not re.search(r"TargetMode\s*=\s*[\"']External", r):
                    continue
                typ = (re.search(r"Type\s*=\s*[\"']([^\"']+)", r) or [None, ""])[1].rsplit("/", 1)[-1]
                tgt = (re.search(r"Target\s*=\s*[\"']([^\"']*)", r) or [None, ""])[1]
                if typ == "hyperlink":
                    add(0, "links", 0, tgt)
                elif typ in REMOTE_PARTS:
                    add(2, "office", 0, f"loads {REMOTE_PARTS[typ]} from outside the file when opened: {tgt[:100]}")
                else:
                    add(1, "office", 0, f"points outside the file ({typ}): {tgt[:100]}")
        elif low.endswith(".xml") and low.split("/")[0] in ("word", "xl", "ppt", "docprops"):
            x = z.read(n)[:30 * MB].decode("utf-8", "replace")
            if re.search(r"\bDDEAUTO\b|<w:instrText[^>]*>\s*DDE\b|\binstr\s*=\s*\"\s*DDE", x):
                add(2, "office", 0, f"runs a DDE command when opened ({n})")
            if low == "word/document.xml" and "<w:vanish/>" in x:
                add(1, "hidden text", 0, "holds text hidden from view (w:vanish); read it")
            if re.search(r"(document|slide\d*|notesSlide\d*|sharedStrings|comments|footnotes|endnotes|core|app)\.xml$", low):
                text.append(re.sub(r"<[^>]+>", " ", x))
    if text:
        text_checks(add, "\n".join(text), "document text", ".office-text", False, dom)


def member_checks(add, members, read, package, dom, wheel=False):
    """members: (name, size, packed size or None, mode, link target, type, encrypted). read(name) -> bytes."""
    total, budget, nested, programs, scripts = 0, 300 * MB, [], [], 0
    shown = collections.Counter()
    for name, size, packed, mode, link, typ, enc in members:
        total += size or 0
        bad = name.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:", name) or ".." in re.split(r"[\\/]", name)
        if bad:
            add(2, "archive", 0, f"a path that climbs out of its folder: {name[:120]}")
        if typ == "special":
            add(2, "archive", 0, f"a device or pipe entry: {name[:120]}")
        if typ in ("symlink", "hardlink"):
            # a symlink resolves from its own folder, a hard link from the archive's top; climbing is fine while it stays in
            dest = os.path.normpath(os.path.join(os.path.dirname(name) if typ == "symlink" else "", link or "."))
            if link.startswith("/") or dest == ".." or dest.startswith("../"):
                add(2, "archive", 0, f"a link pointing outside the folder: {name} -> {link[:100]}")
            else:
                add(0, "links inside the archive", 0, name)
        if mode and mode & 0o6000:
            add(1, "archive", 0, f"runs with raised privileges (setuid or setgid): {name}")
        if enc:
            add(1, "archive", 0, f"encrypted, so it can't be checked: {name}")
        if size and packed and size > 100 * MB and size / max(packed, 1) > 100:
            add(2, "archive", 0, f"a compression bomb: {name} packs {human(size)} into {human(packed)}")
        if typ != "file":
            continue
        base = name.rsplit("/", 1)[-1]
        ext = ext_of(base)
        if ext in ARCHIVE_EXT and not (package and ext in (".jar", ".whl")):
            nested.append(name)
        if ext in BLOCK_EXT or any(f"{b}/" in name.lower() for b in (".app", ".pkg", ".kext", ".prefpane")):
            programs.append(name)
        if not size or size > 5 * MB or budget <= 0:
            continue
        try:
            data = read(name)
        except Exception:
            continue
        budget -= len(data)
        kind = sniff(data[:8192], base)
        if kind in PROGRAM_KINDS:
            if ext in DOCLIKE:
                add(2, "disguised file", 0, f"{name}: {PROGRAM_KINDS[kind]} named as a {ext} file")
            else:
                programs.append(name)
            continue
        if kind in ("text", "script") and (ext in CODE_EXT | PROSE_EXT | MARKUP_EXT | DATA_EXT or base in CODE_NAMES
                                           or not ext or kind == "script"):
            scripts += ext in CODE_EXT or kind == "script"

            def madd(lv, cat, ln, det, _n=name):
                if lv and shown[(lv, cat)] >= 12:
                    lv = 0
                if lv:
                    shown[(lv, cat)] += 1
                add(lv, cat, 0, f"{_n}:{ln}: {det}" if ln else f"{_n}: {det}")
            text_checks(madd, data.decode("utf-8", "replace"), name, ext, package, dom)
    if total > 8 * 1024 * MB:
        add(2, "archive", 0, f"unpacks to {human(total)}: a compression bomb, or far too big")
    if len(members) > 200000:
        add(1, "archive", 0, f"{len(members):,} entries")
    if nested:
        add(0 if package else 1, "archives inside, not opened", 0, ", ".join(nested[:5]))
    if programs:
        add(0 if package else 2, "holds programs", 0, ", ".join(programs[:5]) +
            ("" if package else ": released only on the user's word"))
    if scripts:
        add(0, "scripts inside", 0, str(scripts))


def zip_checks(add, path, ext, package, dom):
    try:
        z = zipfile.ZipFile(path)
    except Exception as e:
        add(1, "archive", 0, f"won't open as a zip ({type(e).__name__}): damaged or disguised")
        return
    with z:
        infos = z.infolist()
        names = [i.filename for i in infos]
        if "[Content_Types].xml" in names:
            office_checks(add, z, names, dom)
            return
        wheel = ext == ".whl" or any(n.endswith(".dist-info/RECORD") for n in names)
        if (ext in (".jar", ".apk") or "META-INF/MANIFEST.MF" in names and any(n.endswith(".class") for n in names)) \
                and not package:
            add(2, "program", 0, "a Java program")
        mem = []
        for i in infos:
            mode = (i.external_attr >> 16) & 0o177777
            typ = "dir" if i.is_dir() else ("symlink" if stat.S_ISLNK(mode) else "file")
            link = z.read(i).decode("utf-8", "replace")[:300] if typ == "symlink" and i.file_size < 4096 else ""
            mem.append((i.filename, i.file_size, i.compress_size, mode & 0o7777, link, typ, bool(i.flag_bits & 1)))
        member_checks(add, mem, lambda n: z.read(n), package, dom, wheel)
        if wheel:
            wheel_record(add, z, names)


def wheel_record(add, z, names):
    rec = [n for n in names if n.endswith(".dist-info/RECORD")]
    if not rec:
        add(1, "package", 0, "a wheel without a RECORD (its list of files and fingerprints)")
        return
    listed = {}
    for row in csv.reader(io.StringIO(z.read(rec[0]).decode("utf-8", "replace"))):
        if len(row) >= 2 and row[1].startswith("sha256="):
            listed[row[0]] = row[1][7:]
    bad, missing = [], []
    for n in names:
        if n.endswith("/") or n == rec[0] or re.search(r"\.dist-info/RECORD\.(jws|p7s)$", n):
            continue
        if n not in listed:
            missing.append(n)
            continue
        h = hashlib.sha256()
        with z.open(n) as f:
            for b in iter(lambda: f.read(MB), b""):
                h.update(b)
        if base64.urlsafe_b64encode(h.digest()).rstrip(b"=").decode() != listed[n]:
            bad.append(n)
    if bad:
        add(2, "package", 0, "files changed after the package was built (RECORD mismatch): " + ", ".join(bad[:5]))
    if missing:
        add(1, "package", 0, "files missing from its RECORD: " + ", ".join(missing[:5]))


def tar_checks(add, path, kind, ext, package, dom):
    try:
        t = tarfile.open(path, "r:*")
    except Exception:
        if kind in ("gzip", "bzip2", "xz"):
            opener = {"gzip": gzip.open, "bzip2": __import__("bz2").open, "xz": __import__("lzma").open}[kind]
            try:
                with opener(path, "rb") as f:
                    data = f.read(5 * MB)
            except Exception as e:
                add(1, "archive", 0, f"won't unpack ({type(e).__name__}): damaged or disguised")
                return
            inner = sniff(data[:8192])
            add(2 if inner in PROGRAM_KINDS else 0, "compressed file", 0, f"holds {PROGRAM_KINDS.get(inner, inner)}")
            if inner == "text":
                text_checks(add, data.decode("utf-8", "replace"), path[:-len(ext)] if ext else path,
                            ext_of(os.path.basename(path)[:-len(ext)] if ext else path), package, dom)
            return
        add(1, "archive", 0, "won't open as a tar archive: damaged or disguised")
        return
    with t:
        try:
            ms = t.getmembers()
        except Exception as e:
            add(1, "archive", 0, f"damaged part way through ({type(e).__name__})")
            return
        mem = []
        for m in ms:
            typ = "file" if m.isfile() else "dir" if m.isdir() else "symlink" if m.issym() else \
                "hardlink" if m.islnk() else "special"
            mem.append((m.name, m.size, None, m.mode, m.linkname, typ, False))
        byname = {m.name: m for m in ms}
        member_checks(add, mem, lambda n: t.extractfile(byname[n]).read(5 * MB + 1), package, dom)


# ---------------------------------------------------------------- screen: one file, ClamAV, a whole job

class Hits:
    def __init__(self):
        self.findings, self.info, self.per, self.seen = [], collections.Counter(), collections.Counter(), set()

    def add(self, level, cat, line, detail):
        if level > 0 and (level, cat, line, str(detail)[:220]) in self.seen:
            return
        if level <= 0:
            self.info[cat] += 1
            return
        self.per[(level, cat)] += 1
        if self.per[(level, cat)] > 25:
            self.info[f"{cat} (more places, as above)"] += 1
            return
        self.seen.add((level, cat, line, str(detail)[:220]))
        self.findings.append([level, cat, line, str(detail)[:220]])

    @property
    def level(self):
        return max([f[0] for f in self.findings] or [0])


def screen_file(full, rel, package, dom):
    h = Hits()
    st = os.lstat(full)
    name = os.path.basename(rel)
    name_checks(h.add, name)
    if stat.S_ISLNK(st.st_mode):
        target = os.readlink(full)
        h.add(1, "link", 0, f"a link to {target[:150]}")
        return h, None
    size = st.st_size
    if size == 0:
        h.add(0, "empty files", 0, "")
        return h, None
    with open(full, "rb") as f:
        head = f.read(8192)
        tail = b""
        if size >= 512:
            f.seek(size - 512)
            tail = f.read(512)
    ext = ext_of(name)
    kind = sniff(head, name)
    if tail.startswith(b"koly"):
        kind = "dmg"
    if st.st_mode & 0o111 and kind not in PROGRAM_KINDS and kind != "script":
        h.add(0, "marked runnable", 0, "")
    if kind in PROGRAM_KINDS:
        if ext in DOCLIKE:
            h.add(2, "disguised file", 0, f"{PROGRAM_KINDS[kind]} named as a {ext} file")
        elif package:
            h.add(0, "programs", 0, "")
        else:
            h.add(2, "program", 0, f"{PROGRAM_KINDS[kind]}; Claude never runs it. {sig_info(full, kind)}")
        return h, kind
    if ext in BLOCK_EXT and not package:
        h.add(2, "program", 0, f"a {ext} file, which opens as a program or installer")
    elif ext in REVIEW_EXT and not package:
        h.add(1, "double-click script", 0, f"a {ext} file runs when opened; read all of it")
    if ext in EXPECT and kind not in EXPECT[ext] and not (kind == "script" and ext in CODE_EXT):
        looks = "a web page or text (an error or sign-in page?)" if kind == "text" else kind
        h.add(1, "not what it says", 0, f"named {ext} but looks like {looks}")
    try:
        if kind == "pdf":
            pdf_checks(h.add, full, dom)
        elif kind == "zip":
            zip_checks(h.add, full, ext, package, dom)
        elif kind in ("tar", "gzip", "bzip2", "xz"):
            tar_checks(h.add, full, kind, ext, package, dom)
        elif kind in ("zstd", "7z", "rar"):
            h.add(1, "archive", 0, f"a {kind} archive this screen can't look inside; open it only on the user's word")
        elif kind == "ole":
            with open(full, "rb") as f:
                raw = f.read(100 * MB)
            if re.search(rb"_VBA_PROJECT|\x00A\x00t\x00t\x00r\x00i\x00b\x00u\x00t|VBA\x00", raw):
                h.add(2, "office", 0, "an old-format Office file with macros")
            else:
                h.add(1, "office", 0, "an old-format Office file: macros can't be ruled out; read it as text only")
        elif kind == "rtf":
            with open(full, "rb") as f:
                raw = f.read(100 * MB)
            if re.search(rb"\\obj(data|update|ocx|emb|link)\b|\\object\b", raw):
                h.add(2, "office", 0, "an RTF file with embedded objects (a common attack route)")
            text_checks(h.add, raw.decode("latin-1"), rel, ".rtf", package, dom)
        elif kind in ("text", "script"):
            if size > 20 * MB:
                h.add(0, "text too big to read through", 0, human(size))
            else:
                with open(full, "rb") as f:
                    text_checks(h.add, f.read().decode("utf-8", "replace"), rel, ext, package, dom)
        elif kind == "binary" and ext in PROSE_EXT | DATA_EXT | CODE_EXT:
            h.add(1, "not what it says", 0, f"named {ext} but holds binary data")
    except Exception as e:
        h.add(1, "check failed", 0, f"the {kind} check stopped ({type(e).__name__}: {str(e)[:80]}); look at it by hand")
    return h, kind


def clamav(paths):
    """ClamAV over the given paths: (note, {path: signature}). freshclam checks for new signatures every 4 hours."""
    if not os.path.exists(CLAMSCAN):
        return "ClamAV: not installed, so no known-malware scan", {}
    stale = ""
    if not os.path.exists(CLAMSTAMP) or time.time() - os.path.getmtime(CLAMSTAMP) > CLAM_EVERY:
        # a stamp, not the database's age: an up-to-date check leaves the database untouched. Exit 0 is up to date
        # or updated; after a failure the next screen tries again. Its "NULL X509 store" errors are harmless: the
        # system curl it uses checks the connection itself, and the signature files carry ClamAV's own signature.
        u = run([FRESHCLAM, "--quiet", "--stdout"], timeout=900)
        if u.returncode == 0:
            os.makedirs(QROOT, mode=0o700, exist_ok=True)
            with open(CLAMSTAMP, "w"):
                pass
        else:
            stale = f", the update check failed (freshclam exit {u.returncode})"
    r = run([CLAMSCAN, "--recursive", "--infected", "--no-summary", "--stdout", "--max-filesize=500M",
             "--max-scansize=1000M", "--alert-encrypted=no", "--alert-exceeds-max=no", "--", *paths], timeout=3600)
    found = {}
    for line in r.stdout.splitlines():
        m = re.match(r"(.+): (.+) FOUND$", line)
        if m:
            found[m.group(1)] = m.group(2)
    ver = run([CLAMSCAN, "--version"], timeout=60).stdout.strip()
    m = re.match(r"ClamAV ([\d.]+)/(\d+)/(.+)", ver)
    note = (f"ClamAV {m.group(1)}, signatures of {' '.join(m.group(3).split()[1:3])}" if m else "ClamAV") + stale
    if r.returncode == 2 and not found:
        note += ": couldn't finish (" + " ".join((r.stderr or r.stdout).split())[-150:] + ")"
    else:
        note += f": {len(found)} known threat(s)" if found else ": nothing known found"
    return note, found


def walk(root):
    """Files and bundles under root: (files, bundles), relative paths."""
    if os.path.isfile(root) or os.path.islink(root):
        return [os.path.basename(root)], []
    files, bundles = [], []
    for dp, dn, fn in os.walk(root):
        links = [x for x in dn if os.path.islink(jpath(dp, x))]
        files += [os.path.relpath(jpath(dp, x), root) for x in links]
        dn[:] = sorted(x for x in dn if x not in (".git", "__pycache__") and x not in links)
        for x in dn:
            if ext_of(x) in BUNDLES:
                bundles.append(os.path.relpath(jpath(dp, x), root))
        for f in sorted(fn):
            if f in (".DS_Store",) or f.endswith(".part"):
                continue
            files.append(os.path.relpath(jpath(dp, f), root))
        if len(files) > 50000:
            break
    return files, bundles


def screen_job(d, quiet=False):
    p = load(d, "plan.json")
    root = p["path"] if p["kind"] == "screen" else jpath(d, "files")
    base = os.path.dirname(root) if os.path.isfile(root) else root
    files, bundles = walk(root)
    if not files and not bundles:
        raise Fail("nothing to screen in " + root)
    pkg_paths = {i["path"] for i in p.get("items", []) if i.get("pkg")}
    old = load(d, "verdicts.json", {})
    v = {"when": now(), "files": {}, "cleared": old.get("cleared", {}), "count": len(files), "bytes": 0}
    dom = collections.Counter()
    kinds = collections.Counter()
    for rel in files:
        full = jpath(base, rel)
        h, kind = screen_file(full, rel, rel in pkg_paths, dom)
        kinds[kind or "link"] += 1
        size = os.lstat(full).st_size
        v["bytes"] += size
        v["files"][rel] = {"level": h.level, "findings": h.findings, "info": dict(h.info), "size": size,
                           "sha256": sha256_of(full) if os.path.isfile(full) and not os.path.islink(full) else None}
    for rel in bundles:
        full = jpath(base, rel)
        x = v["files"].setdefault(rel + "/", {"level": 2, "findings": [], "info": {}, "size": 0, "sha256": None})
        x["findings"].append([2, "program", 0, f"a {ext_of(rel)} bundle; Claude never opens or runs it. "
                              + sig_info(full, "pkg" if ext_of(rel) in (".pkg", ".mpkg") else "app")])
    note, found = clamav([root])
    for path, sig in found.items():
        rel = os.path.relpath(path, base)
        rel = next((r for r in v["files"] if rel == r or rel.startswith(r.rstrip("/") + "/")), rel)
        x = v["files"].setdefault(rel, {"level": 2, "findings": [], "info": {}, "size": 0, "sha256": None})
        x["findings"].insert(0, [2, "known malware", 0, f"ClamAV: {sig}"])
        x["level"] = 2
    for rel, c in list(v["cleared"].items()):
        x = v["files"].get(rel)
        if not x or x["sha256"] != c.get("sha256") or x["level"] > c.get("level", 0):
            del v["cleared"][rel]
    v["clamav"], v["domains"], v["kinds"] = note, dom.most_common(40), dict(kinds)
    v["verdict"] = LEVELS[max([eff(v, r) for r in v["files"]] or [0])]
    save(d, "verdicts.json", v)
    write_report(d, p, v)
    if not quiet:
        print_summary(d, p, v)
    return LEVELS.index(v["verdict"])


def eff(v, rel):
    return 0 if rel in v.get("cleared", {}) else v["files"][rel]["level"]


def in_bundle(rel):
    """Inside an app or other bundle, whose files need their modes."""
    return any(ext_of(part) in BUNDLES for part in rel.replace("\\", "/").split("/")[:-1])


def print_summary(d, p, v):
    job = os.path.basename(d)
    print(f"Screened {job}: {v['count']} file(s), {human(v['bytes'])}. {v['clamav']}.")
    rows = [(rel, f) for rel, x in sorted(v["files"].items()) if eff(v, rel) for f in x["findings"]]
    blocks = [(r, f) for r, f in rows if f[0] == 2]
    reviews = [(r, f) for r, f in rows if f[0] == 1]
    if blocks:
        print(f"Blocked: only the user's word releases these ({len(blocks)}):")
        for r, f in blocks[:15]:
            print(f"  {r}{':' + str(f[2]) if f[2] else ''} [{f[1]}] {f[3][:150]}")
    if reviews:
        print(f"To read in full, then clear ({len(reviews)} place(s) in {len({r for r, _ in reviews})} file(s)):")
        for r, f in reviews[:25]:
            print(f"  {r}{':' + str(f[2]) if f[2] else ''} [{f[1]}] {f[3][:150]}")
        if len(reviews) > 25:
            print(f"  ... {len(reviews) - 25} more in the report")
    info = collections.Counter()
    for x in v["files"].values():
        info.update(x.get("info", {}))
    if info:
        print("Noted: " + "; ".join(f"{k} {n}" for k, n in info.most_common(8)))
    if v["cleared"]:
        print(f"Cleared earlier: {len(v['cleared'])} file(s)")
    print(f"Verdict: {v['verdict'].upper()}. Report: {jpath(d, 'report.md')}")
    if v["verdict"] == "pass" and p["kind"] == "screen":
        print("Nothing to release: these files were screened where they are.")
    elif v["verdict"] == "pass":
        nxt = "install" if p.get("pypi") or p.get("brew") else "release"
        print(f"Next: {CMD} {nxt} {job}" + (" <destination>" if nxt == "release" and p["kind"] == "fetch" else ""))
    elif p["kind"] != "screen":
        print(f"Next: read each file above in full; then {CMD} clear {job} <file> --reason \"<what you read>\""
              + (" --user \"<the user's words>\" for blocked files" if blocks else "") + "; then release or install")


def write_report(d, p, v):
    L = [f"# Screen of {os.path.basename(d)}", "",
         f"Screened {v['when']}: {v['count']} file(s), {human(v['bytes'])}. {v['clamav']}.",
         f"Verdict: {v['verdict']}.", ""]
    if p.get("specs"):
        L += ["Source: " + "; ".join(p["specs"])[:600]]
    if p.get("path"):
        L += [f"Screened in place: {p['path']}"]
    for it in p.get("items", [])[:20]:
        if it.get("origin"):
            L += [f"Came from {it['origin']}" + (f" (downloaded from {', '.join(it['meta']['from'][:2])})"
                                                  if it.get("meta", {}).get("from") else "")]
    if (p.get("approved") or {}).get("words"):
        L += [f"The user's yes ({p['approved']['when']}): \"{p['approved']['words']}\""]
    if p.get("summary"):
        L += ["", "## Plan"] + ["- " + s for s in p["summary"]]
    if p.get("warnings"):
        L += ["", "## Warning signs before download"] + ["- " + w for w in p["warnings"]]
    if (p.get("fetched") or {}).get("problems"):
        L += ["", "## Not downloaded"] + [f"- {a}: {b}" for a, b in p["fetched"]["problems"]]
    for level, title in ((2, "Blocked: only the user's word releases these"), (1, "To read in full, then clear")):
        rows = [(rel, f) for rel, x in sorted(v["files"].items()) for f in x["findings"] if f[0] == level]
        if rows:
            L += ["", f"## {title}"]
            for rel, f in rows:
                c = v["cleared"].get(rel)
                L += [f"- {rel}{':' + str(f[2]) if f[2] else ''} [{f[1]}] {f[3]}" +
                      (f" (cleared {c['when']}: {c['reason']})" if c else "")]
    info = collections.defaultdict(list)
    for rel, x in sorted(v["files"].items()):
        for k, n in x.get("info", {}).items():
            info[k].append((rel, n))
    if info:
        L += ["", "## Noted, nothing to do"]
        for k, rows in sorted(info.items(), key=lambda kv: -sum(n for _, n in kv[1])):
            L += [f"- {k}: {sum(n for _, n in rows)} in {len(rows)} file(s), e.g. " + ", ".join(r for r, _ in rows[:3])]
    if v.get("kinds"):
        L += ["", "File types: " + ", ".join(f"{k} {n}" for k, n in sorted(v["kinds"].items(), key=lambda kv: -kv[1]))]
    if v.get("domains"):
        L += ["", "Web addresses named in the files: " + ", ".join(f"{dm} ({n})" for dm, n in v["domains"][:30])]
    with open(jpath(d, "report.md"), "w") as f:
        f.write("\n".join(L) + "\n")


def cmd_screen(target):
    t = os.path.abspath(os.path.expanduser(target))
    if os.path.exists(jpath(t, "plan.json")) or not os.path.exists(t):
        return screen_job(job_dir(target))
    d = new_job("screen-" + clean_name(os.path.basename(t.rstrip("/"))), files=False)
    save(d, "plan.json", {"job": os.path.basename(d), "kind": "screen", "created": now(), "session": session(),
                          "path": t, "items": []})
    return screen_job(d)


# ---------------------------------------------------------------- intake, clear, release, install, jobs

def cmd_intake(paths, copy=False, name=None):
    srcs = [os.path.abspath(os.path.expanduser(x)) for x in paths]
    missing = [s for s in srcs if not os.path.lexists(s)]
    if missing:
        raise Fail("not found: " + ", ".join(missing[:5]))
    inq = [s for s in srcs if s.startswith(os.path.realpath(QROOT) + os.sep) or s.startswith(QROOT + os.sep)]
    if inq:
        raise Fail("already in quarantine: " + inq[0])
    d = new_job(name or "intake-" + clean_name(os.path.basename(srcs[0].rstrip("/"))).rsplit(".", 1)[0])
    items, used = [], set()
    for s in srcs:
        nm = os.path.basename(s.rstrip("/")) or "item"
        rel = nm
        while rel.lower() in used:
            rel = "_" + rel
        used.add(rel.lower())
        dest = jpath(d, "files", rel)
        meta = {"quarantine": xattr(s, "com.apple.quarantine"), "from": where_from(s)}
        if copy:
            (shutil.copytree(s, dest, symlinks=True) if os.path.isdir(s) and not os.path.islink(s)
             else shutil.copy2(s, dest, follow_symlinks=False))
        else:
            shutil.move(s, dest)
        if not meta["quarantine"]:
            mark([dest], recursive=os.path.isdir(dest))
        for f in ([dest] if not os.path.isdir(dest) else
                  [jpath(dp, x) for dp, _, fn in os.walk(dest) for x in fn]):
            st = os.lstat(f)
            if stat.S_ISREG(st.st_mode) and st.st_mode & 0o111 and not in_bundle(os.path.relpath(f, d)):
                os.chmod(f, st.st_mode & ~0o111)
        items.append({"src": "intake:" + s, "path": rel, "origin": s, "meta": meta, "version": "-",
                      "licence": "-", "sha256": sha256_of(dest) if os.path.isfile(dest) else None})
    save(d, "plan.json", {"job": os.path.basename(d), "kind": "intake", "created": now(), "session": session(),
                          "specs": ["intake: " + ", ".join(srcs)[:300]], "items": items, "copy": copy})
    print(("Copied " if copy else "Moved ") + f"{len(items)} item(s) into quarantine at {jpath(d, 'files')}")
    return screen_job(d)


def cmd_clear(job, pats, reason, user):
    d = job_dir(job)
    v = load(d, "verdicts.json")
    if not v:
        raise Fail(f"not screened yet: {CMD} screen {os.path.basename(d)}")
    if len((reason or "").split()) < 4:
        raise Fail('say what you read and why it is safe: --reason "<a sentence>"')
    matched = [r for r in v["files"] if any(r == x or fnmatch.fnmatchcase(r, x) for x in pats)]
    if not matched:
        raise Fail("no screened file matches " + ", ".join(pats))
    done, refused = [], []
    for rel in matched:
        x = v["files"][rel]
        if x["level"] == 0:
            continue
        if x["level"] == 2 and not (user or "").strip():
            refused.append(rel)
            continue
        v["cleared"][rel] = {"reason": reason.strip(), "user": (user or "").strip() or None, "when": now(),
                             "session": session(), "sha256": x["sha256"], "level": x["level"]}
        done.append(rel)
    v["verdict"] = LEVELS[max([eff(v, r) for r in v["files"]] or [0])]
    save(d, "verdicts.json", v)
    write_report(d, load(d, "plan.json"), v)
    print(f"Cleared {len(done)} file(s)." + (f" Still blocked, needing the user's word (--user): {', '.join(refused[:5])}"
                                              if refused else "") + f" Verdict now: {v['verdict'].upper()}.")
    return 2 if refused else LEVELS.index(v["verdict"])


def default_root(p):
    repos = p.get("github") or []
    if p["kind"] == "fetch" and len(repos) == 1 and all(i["src"].startswith("github:") for i in p["items"]):
        return repos[0]
    return ""


def cmd_release(job, dest, root=None, only=None, move=False, overwrite=False):
    d = job_dir(job)
    p, v = load(d, "plan.json"), load(d, "verdicts.json")
    if p["kind"] == "screen":
        raise Fail("these files were screened where they are; there is nothing to release")
    if not v:
        raise Fail(f"not screened yet: {CMD} screen {os.path.basename(d)}")
    files_dir = jpath(d, "files")
    root = default_root(p) if root is None else root.strip("/")
    base = inside(files_dir, root) if root else files_dir
    rels = [r for r in v["files"] if not r.endswith("/") and jpath(files_dir, r).startswith(base + os.sep)]
    if only:
        rels = [r for r in rels if fnmatch.fnmatchcase(os.path.relpath(jpath(files_dir, r), base), only)]
    if not rels:
        raise Fail("nothing to release" + (f" under {root}" if root else "") + (f" matching {only}" if only else ""))
    held = [r for r in v["files"] if eff(v, r) and (r in rels or r.endswith("/") and
                                                    any(x.startswith(r) for x in rels))]
    if held:
        raise Fail(f"{len(held)} file(s) not passed or cleared, e.g. {', '.join(held[:3])}; read them, then clear")
    byitem = {i["path"]: i for i in p.get("items", [])}
    rows, skipped = [], []
    for rel in rels:
        src = jpath(files_dir, rel)
        it = byitem.get(rel) or next((i for k, i in byitem.items() if rel.startswith(k.rstrip("/") + "/")), {})
        if dest:
            target = os.path.abspath(os.path.expanduser(dest))
            if len(rels) > 1 or os.path.isdir(target) or dest.endswith("/"):
                target = jpath(target, os.path.relpath(src, base))
        elif it.get("origin"):
            target = it["origin"] if rel == it["path"] else jpath(it["origin"], os.path.relpath(src, jpath(files_dir, it["path"])))
        else:
            raise Fail("say where to: release <job> <destination>")
        if os.path.isfile(src) and not os.path.islink(src) and v["files"][rel]["sha256"] and \
                sha256_of(src) != v["files"][rel]["sha256"]:
            skipped.append(f"{rel} (changed since it was screened)")
            continue
        if os.path.lexists(target) and not overwrite:
            skipped.append(f"{rel} ({target} exists; --overwrite to replace it)")
            continue
        os.makedirs(os.path.dirname(target), exist_ok=True)
        if os.path.islink(src):
            if os.path.lexists(target):
                os.remove(target)
            os.symlink(os.readlink(src), target)
        elif move:
            shutil.move(src, target)
        else:
            shutil.copyfile(src, target)
            os.chmod(target, os.stat(src).st_mode & 0o755 if in_bundle(rel) else 0o644)
        if not os.path.islink(target):
            mark([target])
        c = v["cleared"].get(rel)
        rows.append([now(), os.path.basename(d), rel, it.get("src", "-"), it.get("version", "-"),
                     v["files"][rel]["sha256"], it.get("licence", "-"),
                     "passed" if not c else f"cleared: {c['reason']}" + (f" (user: {c['user']})" if c.get("user") else ""),
                     target])
    ledger(rows)
    print(f"Released {len(rows)} file(s)" + (f" to {os.path.abspath(os.path.expanduser(dest))}" if dest else
                                             " to where they came from") + "; logged in ledger.tsv.")
    for s in skipped[:10]:
        print("  skipped: " + s)
    return 0 if not skipped else 1


def cmd_install(job):
    d = job_dir(job)
    p, v = load(d, "plan.json"), load(d, "verdicts.json")
    if not v:
        raise Fail(f"not screened yet: {CMD} screen {os.path.basename(d)}")
    held = [r for r in v["files"] if eff(v, r)]
    if held:
        raise Fail(f"{len(held)} file(s) not passed or cleared, e.g. {', '.join(held[:3])}; read them, then clear")
    pk = [i for i in p["items"] if i.get("pkg")]
    for i in pk:
        f = jpath(d, "files", i["path"])
        if not os.path.isfile(f) or sha256_of(f) != v["files"].get(i["path"], {}).get("sha256"):
            raise Fail(f"{i['path']} is missing or changed since it was screened; fetch and screen again")
    rows, code = [], 0
    if p.get("pypi"):
        venv, py = p["pypi"]["venv"], p["pypi"]["python"]
        if not os.path.exists(jpath(venv, "pyvenv.cfg")):
            r = run([UV, "venv", "--python", py, "--no-python-downloads", venv], env=UV_ENV, timeout=300)
            if r.returncode:
                raise Fail("couldn't make the virtual environment: " + " ".join(r.stderr.split())[-300:])
        r = run([UV, "pip", "install", "--python", venv, "--no-index", "--find-links", jpath(d, "files", "pypi"),
                 "--require-hashes", "--no-build", "-r", jpath(d, "install.txt")], env=UV_ENV, timeout=1800)
        print((r.stderr or r.stdout).strip()[-1500:])
        if r.returncode:
            raise Fail("uv couldn't install it (above); nothing outside quarantine was downloaded")
        rows += [[now(), os.path.basename(d), i["path"], i["src"], i["version"], i["sha256"], i["licence"],
                  "installed", venv] for i in pk if i["pkg"] == "pypi"]
    if p.get("brew"):
        for i in pk:
            if i["pkg"] == "brew" and (not os.path.isfile(i.get("cache", "")) or sha256_of(i["cache"]) != i["sha256"]):
                raise Fail(f"Homebrew's copy of {i['name']} changed since it was screened; fetch and screen again")
        r = run([BREW, "install", *p["brew"]["formulae"]], env=BREW_ENV, timeout=3600)
        out = (r.stdout + r.stderr).strip()
        print(out[-1500:])
        late = re.findall(r"==> Downloading (https://\S+)", out)
        if late:
            print("Note: brew downloaded more than was screened: " + ", ".join(late[:5]))
        if r.returncode:
            raise Fail("brew install failed (above)")
        rows += [[now(), os.path.basename(d), i["path"], i["src"], i["version"], i["sha256"], i["licence"],
                  "installed", "Homebrew"] for i in pk if i["pkg"] == "brew"]
    if p.get("npm"):
        tgz = [jpath(d, "files", i["path"]) for i in pk if i["pkg"] == "npm"]
        print("npm isn't installed here. Once it is, from the project folder: npm install --ignore-scripts " +
              " ".join(f'"{t}"' for t in tgz))
        code = 1
    if not (p.get("pypi") or p.get("brew") or p.get("npm")):
        raise Fail(f"nothing to install in this job; use {CMD} release {os.path.basename(d)} <destination>")
    ledger(rows)
    print(f"Installed and logged {len(rows)} package file(s).")
    return code


def cmd_jobs():
    for d in all_jobs()[:15]:
        p, v = load(d, "plan.json"), load(d, "verdicts.json") or {}
        print(f"{os.path.basename(d):40} {p.get('kind', '?'):7} {p.get('created', '')[:17]:18} "
              f"{v.get('verdict', 'not screened'):12} {'; '.join(p.get('summary') or p.get('specs') or [p.get('path', '')])[:70]}")
    return 0


# ---------------------------------------------------------------- for scripts

def download_many(items, dest_dir=None, name=None, max_mb=300):
    """items: [(https url, relative path or None, sha256 or None)]. Fetches into one quarantine job, screens it,
    and releases to dest_dir when everything passes. Returns the released (or quarantined) paths. Raises
    RuntimeError when a download fails or the screen wants a look, naming the report. The user approves the
    script's downloads before it runs."""
    try:
        its = []
        for url, rel, sha in items:
            if not url.lower().startswith("https://"):
                raise Fail("https only: " + url[:100])
            rel = safe_rel(rel or clean_name(urllib.parse.unquote(urllib.parse.urlparse(url).path.rsplit("/", 1)[-1])))
            if any(i["path"].lower() == rel.lower() for i in its):
                raise Fail("two downloads would land on " + rel)
            its.append({"src": "url:" + url, "url": url, "path": rel, "size": None, "version": "-", "licence": "-",
                        "expect": {"algo": "sha256", "value": sha.lower()} if sha else None})
        d = new_job(name or os.path.splitext(os.path.basename(sys.argv[0] or "script"))[0])
        p = {"job": os.path.basename(d), "kind": "fetch", "created": now(), "session": session(),
             "specs": ["script: " + " ".join(sys.argv)[:200]], "max_file": max_mb * MB, "items": its,
             "summary": [f"{len(its)} file(s) for {os.path.basename(sys.argv[0] or 'a script')}"], "warnings": [],
             "approved": {"words": "approved as part of the script that called download()", "when": now()}}
        save(d, "plan.json", p)
        problems = do_fetch(d, p)
        if problems:
            if not any(i.get("sha256") for i in its):
                shutil.rmtree(d, ignore_errors=True)
            raise Fail(f"{len(problems)} download(s) failed, e.g. {problems[0][0]}: {problems[0][1]}")
        with contextlib.redirect_stdout(io.StringIO()):
            level = screen_job(d, quiet=True)
        if level:
            raise Fail(f"the screen wants a look ({LEVELS[level]}): read {jpath(d, 'report.md')}, then "
                       f"{CMD} clear {p['job']} ... and {CMD} release {p['job']} <destination>")
        if not dest_dir:
            return [jpath(d, "files", i["path"]) for i in its]
        with contextlib.redirect_stdout(io.StringIO()):
            cmd_release(d, dest_dir.rstrip("/") + "/", overwrite=True)
        return [jpath(os.path.abspath(os.path.expanduser(dest_dir)), i["path"]) for i in its]
    except Fail as e:
        raise RuntimeError("safe_get: " + str(e))


def download(url, dest_dir=None, sha256=None, name=None, max_mb=300):
    """One https file through quarantine; see download_many."""
    return download_many([(url, None, sha256)], dest_dir, name, max_mb)[0]


def save_bytes_many(items, dest_dir=None, source="api", name=None, max_mb=300):
    """items: [(bytes, relative path)], for files a script gets inside an API response rather than from a URL (an
    image in a JSON reply, say). Same route as download_many: written
    into one quarantine job without execute permission and with the quarantine flag, screened (ClamAV, the file's
    type against its extension, the checks by type), released to dest_dir on a pass and logged in ledger.tsv with
    source. Name each file with the extension the response's content type gives (image/png: .png), since a mismatch
    is held. Returns the released (or quarantined) paths; raises RuntimeError when the screen wants a look."""
    try:
        its, blobs = [], []
        for data, rel in items:
            if not isinstance(data, (bytes, bytearray, memoryview)):
                raise Fail(f"bytes expected for {rel}, got {type(data).__name__} (decode base64 first)")
            data = bytes(data)
            if len(data) > max_mb * MB:
                raise Fail(f"{rel} is {human(len(data))}, over the {max_mb} MB cap")
            rel = "/".join(clean_name(x) for x in safe_rel(str(rel)).split("/"))
            if any(i["path"].lower() == rel.lower() for i in its):
                raise Fail("two files would land on " + rel)
            its.append({"src": "bytes:" + str(source)[:200], "path": rel, "size": len(data), "version": "-",
                        "licence": "-", "sha256": hashlib.sha256(data).hexdigest(), "got": len(data)})
            blobs.append(data)
        if not its:
            raise Fail("nothing to save")
        d = new_job(name or os.path.splitext(os.path.basename(sys.argv[0] or "script"))[0])
        base = jpath(d, "files")
        for it, data in zip(its, blobs):
            dest = inside(base, it["path"])
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            fd = os.open(dest, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
            with os.fdopen(fd, "wb") as f:
                f.write(data)
        mark([inside(base, i["path"]) for i in its])
        p = {"job": os.path.basename(d), "kind": "bytes", "created": now(), "session": session(),
             "specs": ["script: " + " ".join(sys.argv)[:200]], "items": its, "warnings": [],
             "summary": [f"{len(its)} file(s) from {str(source)[:80]} for {os.path.basename(sys.argv[0] or 'a script')}"],
             "approved": {"words": "approved as part of the script that called save_bytes()", "when": now()}}
        save(d, "plan.json", p)
        with contextlib.redirect_stdout(io.StringIO()):
            level = screen_job(d, quiet=True)
        if level:
            raise Fail(f"the screen wants a look ({LEVELS[level]}): read {jpath(d, 'report.md')}, then "
                       f"{CMD} clear {p['job']} ... and {CMD} release {p['job']} <destination>")
        if not dest_dir:
            return [jpath(base, i["path"]) for i in its]
        with contextlib.redirect_stdout(io.StringIO()):
            cmd_release(d, dest_dir.rstrip("/") + "/", overwrite=True)
        return [jpath(os.path.abspath(os.path.expanduser(dest_dir)), i["path"]) for i in its]
    except Fail as e:
        raise RuntimeError("safe_get: " + str(e))


def save_bytes(data, name, dest_dir=None, source="api", max_mb=300):
    """One file's bytes from an API response through quarantine; see save_bytes_many."""
    return save_bytes_many([(data, name)], dest_dir, source, None, max_mb)[0]


# ---------------------------------------------------------------- command line

def main(argv=None):
    ap = argparse.ArgumentParser(prog="safe_get.py", description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    s = sub.add_parser("plan")
    s.add_argument("specs", nargs="+")
    s.add_argument("--name")
    s.add_argument("--venv")
    s.add_argument("--python")
    s.add_argument("--max-mb", type=int, default=300)
    s = sub.add_parser("fetch")
    s.add_argument("job")
    s.add_argument("--yes", required=True)
    s = sub.add_parser("screen")
    s.add_argument("target")
    s = sub.add_parser("intake")
    s.add_argument("paths", nargs="+")
    s.add_argument("--copy", action="store_true")
    s.add_argument("--name")
    s = sub.add_parser("clear")
    s.add_argument("job")
    s.add_argument("files", nargs="+")
    s.add_argument("--reason", required=True)
    s.add_argument("--user")
    s = sub.add_parser("release")
    s.add_argument("job")
    s.add_argument("dest", nargs="?")
    s.add_argument("--root")
    s.add_argument("--only")
    s.add_argument("--move", action="store_true")
    s.add_argument("--overwrite", action="store_true")
    s = sub.add_parser("install")
    s.add_argument("job")
    sub.add_parser("jobs")
    a = ap.parse_args(argv)
    if not a.cmd:
        print(__doc__)
        return 3
    try:
        if a.cmd == "plan":
            return cmd_plan(a.specs, a.name, a.venv, a.python, a.max_mb)
        if a.cmd == "fetch":
            return cmd_fetch(a.job, a.yes)
        if a.cmd == "screen":
            return cmd_screen(a.target)
        if a.cmd == "intake":
            return cmd_intake(a.paths, a.copy, a.name)
        if a.cmd == "clear":
            return cmd_clear(a.job, a.files, a.reason, a.user)
        if a.cmd == "release":
            return cmd_release(a.job, a.dest, a.root, a.only, a.move, a.overwrite)
        if a.cmd == "install":
            return cmd_install(a.job)
        return cmd_jobs()
    except Fail as e:
        print("safe_get: " + str(e))
        return 3
    except KeyboardInterrupt:
        return 3
    except Exception as e:
        print(f"safe_get: stopped by {type(e).__name__}: {str(e)[:300]}")
        return 3


if __name__ == "__main__":
    sys.exit(main())
