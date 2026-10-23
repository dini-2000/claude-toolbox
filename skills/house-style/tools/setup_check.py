#!/usr/bin/env python3
"""Check that this computer has what the kit's tools need, and say how to get anything missing.

    python3 tools/setup_check.py          (on Windows: py tools/setup_check.py)

To make files: Python 3.9 or later, the Python packages PyMuPDF, python-pptx and Pillow, and Google Chrome (or
Chromium or Edge). To test them: LibreOffice, which tests every PowerPoint the kit makes (--check), and on a Mac
Microsoft PowerPoint, which checks decks in PowerPoint itself (--powerpoint) and needs no Office licence for it.
It also says whether Claude Code finds the kit from any folder: the kit sits in Claude's skills folder, or a
SKILL.md there names this folder. It installs nothing: Claude asks the person first, then runs the commands it
prints. The exit status is 1 when anything needed to make or test files is missing.
"""
import importlib
import os
import platform
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.dirname(HERE)
SYSTEM = platform.system()
PY = 'py' if SYSTEM == 'Windows' else 'python3'
SKILLS = os.path.join(os.path.expanduser('~'), '.claude', 'skills')
with open(os.path.join(KIT, 'SKILL.md'), encoding='utf-8') as _f:
    _skill = _f.read()
SKILL_NAME = re.search(r'^name: *(\S+)', _skill, re.M).group(1)      # the skills folder the kit goes in
TITLE = re.search(r'^# (.+)$', _skill, re.M).group(1)
PACKAGES = [('fitz', 'PyMuPDF', 'pymupdf'), ('pptx', 'python-pptx', 'python-pptx'), ('PIL', 'Pillow', 'pillow')]
GET = {
    'chrome': {'Darwin': 'brew install --cask google-chrome, or https://www.google.com/chrome/',
               'Windows': 'winget install Google.Chrome, or https://www.google.com/chrome/'},
    'libreoffice': {'Darwin': 'brew install --cask libreoffice, or https://www.libreoffice.org/download/',
                    'Windows': 'winget install TheDocumentFoundation.LibreOffice, or https://www.libreoffice.org/download/'},
}
LINUX = {'chrome': 'https://www.google.com/chrome/ or your package manager (chromium)',
         'libreoffice': 'your package manager (libreoffice)'}


def how(tool):
    return GET[tool].get(SYSTEM, LINUX[tool])


def find_chrome():
    sys.path.insert(0, HERE)
    try:
        from chrome import find_chrome as find
        return find()
    except SystemExit:
        return None


def find_soffice():
    cands = [os.environ.get('SOFFICE_PATH', ''), shutil.which('soffice') or '', shutil.which('libreoffice') or '',
             '/Applications/LibreOffice.app/Contents/MacOS/soffice',
             os.path.expanduser('~/Applications/LibreOffice.app/Contents/MacOS/soffice'),
             r'C:\Program Files\LibreOffice\program\soffice.exe',
             r'C:\Program Files (x86)\LibreOffice\program\soffice.exe']
    return next((c for c in cands if c and os.path.isfile(c)), None)


def find_powerpoint():
    for c in ('/Applications/Microsoft PowerPoint.app', os.path.expanduser('~/Applications/Microsoft PowerPoint.app')):
        if os.path.isdir(c):
            return c
    return None


def saved():
    """Where Claude Code finds the kit from: the kit inside the skills folder, or a skill there that names it."""
    real = lambda p: os.path.normcase(os.path.realpath(p))  # noqa: E731
    if real(KIT).startswith(real(SKILLS) + os.sep):
        return KIT
    home = os.path.expanduser('~')
    names = {KIT, '~' + KIT[len(home):] if KIT.startswith(home) else KIT}
    if not os.path.isdir(SKILLS):
        return None
    for d in sorted(os.listdir(SKILLS)):
        f = os.path.join(SKILLS, d, 'SKILL.md')
        try:
            text = open(f, encoding='utf-8').read()
        except OSError:
            continue
        if any(n in text for n in names):
            return f
    return None


def main():
    rows, missing, untested = [], [], []

    def row(state, name, detail, group=missing):
        rows.append((state, name, detail))
        if state == 'MISSING' and group is not None:
            group.append(name)

    v = sys.version_info
    row('ok' if v >= (3, 9) else 'MISSING', 'Python', '%d.%d.%d%s' % (v.major, v.minor, v.micro, '' if v >= (3, 9)
        else ': needs 3.9 or later, from https://www.python.org/downloads/'))
    absent = []
    for mod, name, pip in PACKAGES:
        try:
            m = importlib.import_module(mod)
            row('ok', name, str(getattr(m, '__version__', None) or getattr(m, 'VersionBind', None) or ''))
        except ImportError:
            absent.append(pip)
            row('MISSING', name, '%s -m pip install %s' % (PY, pip))
    c = find_chrome()
    row('ok' if c else 'MISSING', 'Google Chrome', c or 'not found: ' + how('chrome'))
    s = find_soffice()
    row('ok' if s else 'MISSING', 'LibreOffice', s or 'not found (it tests every PowerPoint the kit makes): '
        + how('libreoffice'), untested)
    if SYSTEM == 'Darwin':
        p = find_powerpoint()
        row('ok' if p else 'MISSING', 'Microsoft PowerPoint', p or 'not found (it checks decks in PowerPoint itself, '
            'with no Office licence needed): the Mac App Store, or brew install --cask microsoft-powerpoint', untested)

    where = saved()
    print('%s set-up check (%s, Python at %s)' % (TITLE, {'Darwin': 'macOS'}.get(SYSTEM, SYSTEM), sys.executable))
    for state, name, detail in rows:
        print('  %-9s %-21s %s' % (state, name, detail))
    print('Kit folder: %s' % KIT)
    print('Claude Code finds the kit from any folder: %s' % ('yes (%s)' % where if where else 'no (copy the kit to %s)'
          % os.path.join(SKILLS, SKILL_NAME)))
    if len(absent) > 1:
        print('All missing packages at once: %s -m pip install %s' % (PY, ' '.join(absent)))
    if absent:
        print('If pip refuses with "externally-managed-environment", install them in a virtual environment, or add '
              '--user (and, for a Homebrew Python, --break-system-packages).')
    print('To make files: %s.' % ('all present' if not missing else 'missing ' + ', '.join(missing)))
    print('To test them: %s.' % ('all present' if not untested else 'missing ' + ', '.join(untested)))
    if SYSTEM != 'Darwin':
        print('The check in PowerPoint runs only on a Mac: here, check decks in Google Slides through Claude in Chrome '
              'if they go to people who open them there.')
    return 1 if missing or untested else 0


if __name__ == '__main__':
    sys.exit(main())
