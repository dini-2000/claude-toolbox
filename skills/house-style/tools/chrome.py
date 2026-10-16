"""Headless Chrome for the kit's tools: find the browser, read a page's DOM after its scripts ran, print a deck to PDF.

Pages are run from a hidden temporary copy beside the deck, so its relative links resolve as they do for the deck.
(A <base> tag would break the runtime's history.replaceState.) Headless Chrome does not fire beforeprint, so
print_pdf() injects a script that fires it once the deck is ready; the runtime then ends builds and draws anything
still undrawn.
"""
import glob
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

FLAGS = ['--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check', '--disable-extensions',
         '--hide-scrollbars', '--mute-audio', '--allow-file-access-from-files', '--run-all-compositor-stages-before-draw']

# Collects script errors, including the runtime's console.error calls, from the start of the page.
ERRORS = ('<script>window.__pcErrs=[];addEventListener("error",function(e){__pcErrs.push(String(e.message)+" @"+e.lineno)});'
          '(function(){var ce=console.error;console.error=function(){__pcErrs.push([].map.call(arguments,String).join(" "));'
          'return ce.apply(console,arguments)}})();</script>')

PRINT_READY = ('<script>addEventListener("load",function(){var fire=function(){dispatchEvent(new Event("beforeprint"))};fire();'
               'if(window.PCDeck&&PCDeck.ready)PCDeck.ready().then(fire)});</script>')


def find_chrome():
    cands = [os.environ.get('CHROME_PATH', '')]
    cands += ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
              os.path.expanduser('~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'),
              '/Applications/Chromium.app/Contents/MacOS/Chromium',
              '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
              r'C:\Program Files\Google\Chrome\Application\chrome.exe',
              r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
              os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe'),
              r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
              r'C:\Program Files\Microsoft\Edge\Application\msedge.exe']
    for name in ('google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser', 'chrome', 'msedge'):
        cands.append(shutil.which(name) or '')
    for root in ('~/.cache/ms-playwright', '~/Library/Caches/ms-playwright', '%LOCALAPPDATA%/ms-playwright'):
        root = os.path.expandvars(os.path.expanduser(root))
        cands += sorted(glob.glob(root + '/chromium-*/chrome-linux*/chrome'), reverse=True)
        cands += sorted(glob.glob(root + '/chromium-*/chrome-mac*/Chromium.app/Contents/MacOS/Chromium'), reverse=True)
        cands += sorted(glob.glob(root + '/chromium-*/chrome-win*/chrome.exe'), reverse=True)
    for c in cands:
        if c and os.path.isfile(c):
            return c
    return None


def need_chrome():
    c = find_chrome()
    if not c:
        sys.exit('Could not find Google Chrome, Chromium or Edge. Install Chrome, or set CHROME_PATH to the browser program.')
    return c


def inject(text, head='', body='', first=''):
    """Put `first` at the start of <head>, `head` before </head> and `body` before </body>."""
    if first:
        m = re.search(r'<head\b[^>]*>', text, re.I)
        text = text[:m.end()] + first + text[m.end():] if m else first + text
    if head:
        m = re.search(r'</head\s*>', text, re.I)
        text = text[:m.start()] + head + text[m.start():] if m else head + text
    if body:
        m = None
        for m in re.finditer(r'</body\s*>', text, re.I):
            pass
        text = text[:m.start()] + body + text[m.start():] if m else text + body
    return text


def temp_beside(src, text, tag):
    p = Path(src).resolve().parent / ('.pc-%s-%d.html' % (tag, os.getpid()))
    p.write_text(text, encoding='utf-8')
    return p


def _stop(proc):
    if proc.poll() is not None:
        return
    try:
        if os.name == 'posix':
            os.killpg(proc.pid, signal.SIGTERM)
        else:
            proc.terminate()
        proc.wait(5)
    except Exception:
        proc.kill()


def dump_dom(html_path, size=(1920, 1080), budget=15000, timeout=120):
    """The page's DOM after its scripts ran for `budget` ms of virtual time."""
    with tempfile.TemporaryDirectory(prefix='pc-chrome-') as prof:
        args = [need_chrome()] + FLAGS + ['--window-size=%d,%d' % size, '--virtual-time-budget=%d' % budget,
                                          '--user-data-dir=' + prof, '--dump-dom', Path(html_path).as_uri()]
        kw = {'start_new_session': True} if os.name == 'posix' else {}
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, **kw)
        try:
            out, _ = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            _stop(proc)
            sys.exit('Chrome did not finish reading %s in %d seconds' % (html_path, timeout))
        finally:
            _stop(proc)
    return out.decode('utf-8', 'replace')


def pdf_ready(path, expect=None):
    try:
        with open(path, 'rb') as f:
            f.seek(-1024, 2)
            if b'%%EOF' not in f.read():
                return False
        import fitz
        with fitz.open(path) as d:
            return d.page_count > 0 and (expect is None or d.page_count == expect)
    except Exception:
        return False


def _print_pdf(src_html, pdf_path, expect=None, timeout=180, head='', outline=False):
    """Print a deck with headless Chrome, firing beforeprint first. Chrome sometimes writes the PDF and then never
    exits, so this waits for a complete PDF and then stops it. `head` is extra markup for <head> (a style for one
    print variant, say). `outline` adds bookmarks from the headings (documents)."""
    src_html, pdf_path = Path(src_html).resolve(), Path(pdf_path).resolve()
    text = inject(src_html.read_text(encoding='utf-8'), first=ERRORS, head=head, body=PRINT_READY)
    tmp = temp_beside(src_html, text, 'print-%s' % pdf_path.stem)
    if pdf_path.exists():
        pdf_path.unlink()
    try:
        with tempfile.TemporaryDirectory(prefix='pc-chrome-') as prof:
            args = [need_chrome()] + FLAGS + ['--no-pdf-header-footer', '--window-size=1920,1080',
                                              '--virtual-time-budget=15000', '--user-data-dir=' + prof]
            args += ['--generate-pdf-document-outline'] if outline else []
            args += ['--print-to-pdf=%s' % pdf_path, tmp.as_uri()]
            kw = {'start_new_session': True} if os.name == 'posix' else {}
            proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **kw)
            t0, last, stable = time.time(), -1, 0
            try:
                while time.time() - t0 < timeout:
                    done = proc.poll() is not None
                    size = os.path.getsize(pdf_path) if pdf_path.exists() else -1
                    stable = stable + 1 if size > 0 and size == last else 0
                    last = size
                    if (stable >= 3 or done) and pdf_ready(pdf_path, expect):
                        return pdf_path
                    if done and size <= 0:
                        break
                    time.sleep(0.4)
            finally:
                _stop(proc)
    finally:
        tmp.unlink(missing_ok=True)
    if not pdf_ready(pdf_path):
        sys.exit('Chrome did not produce a PDF for %s' % src_html)
    return pdf_path



class _DevTools:
    """A minimal DevTools (CDP) client over a websocket, standard library only, for prints that must wait on the page."""

    def __init__(self, port, path):
        import base64
        import socket
        self.s = socket.create_connection(('127.0.0.1', port), timeout=240)
        key = base64.b64encode(os.urandom(16)).decode()
        self.s.sendall(('GET %s HTTP/1.1\r\nHost: 127.0.0.1:%d\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n'
                        'Sec-WebSocket-Key: %s\r\nSec-WebSocket-Version: 13\r\n\r\n' % (path, port, key)).encode())
        self.buf, self.n = b'', 0
        while b'\r\n\r\n' not in self.buf:
            self.buf += self._more()
        head, self.buf = self.buf.split(b'\r\n\r\n', 1)
        if b' 101 ' not in head.split(b'\r\n', 1)[0]:
            raise OSError('Chrome refused the DevTools connection')

    def _more(self):
        chunk = self.s.recv(1 << 20)
        if not chunk:
            raise OSError('Chrome closed the DevTools connection')
        return chunk

    def _take(self, n):
        while len(self.buf) < n:
            self.buf += self._more()
        out, self.buf = self.buf[:n], self.buf[n:]
        return out

    def _message(self):
        import json
        import struct
        msg = b''
        while True:
            b1, b2 = self._take(2)
            n = b2 & 127
            if n == 126:
                n = struct.unpack('>H', self._take(2))[0]
            elif n == 127:
                n = struct.unpack('>Q', self._take(8))[0]
            if b2 & 128:
                self._take(4)
            data, op = self._take(n), b1 & 15
            if op == 8:
                raise OSError('Chrome closed the DevTools connection')
            if op in (9, 10):
                continue
            msg += data
            if b1 & 128:
                return json.loads(msg)

    def call(self, method, session=None, **params):
        import json
        import struct
        self.n += 1
        body = {'id': self.n, 'method': method, 'params': params}
        if session:
            body['sessionId'] = session
        data = json.dumps(body).encode()
        n = len(data)
        head = bytes([0x81]) + (bytes([0x80 | n]) if n < 126 else bytes([0x80 | 126]) + struct.pack('>H', n) if n < 65536
                                 else bytes([0x80 | 127]) + struct.pack('>Q', n))
        mask = os.urandom(4)
        self.s.sendall(head + mask + bytes(b ^ mask[i & 3] for i, b in enumerate(data)))
        while True:
            m = self._message()
            if m.get('id') == self.n:
                if 'error' in m:
                    raise RuntimeError('%s: %s' % (method, m['error'].get('message')))
                return m.get('result', {})


def _print_pdf_wait(src_html, pdf_path, wait, head='', tail='', outline=False, timeout=240):
    """Print through DevTools once the promise named by `wait` (a JavaScript expression) settles. For pages whose
    layout runs past headless Chrome's virtual time, such as Paged.js. `tail` is extra markup before </body>."""
    import base64
    src_html, pdf_path = Path(src_html).resolve(), Path(pdf_path).resolve()
    text = inject(src_html.read_text(encoding='utf-8'), first=ERRORS, head=head, body=PRINT_READY + tail)
    tmp = temp_beside(src_html, text, 'print-%s' % pdf_path.stem)
    try:
        with tempfile.TemporaryDirectory(prefix='pc-chrome-') as prof:
            args = [need_chrome()] + FLAGS + ['--window-size=1920,1080', '--remote-debugging-port=0',
                                              '--user-data-dir=' + prof, 'about:blank']
            kw = {'start_new_session': True} if os.name == 'posix' else {}
            proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **kw)
            try:
                port_file, t0 = Path(prof) / 'DevToolsActivePort', time.time()
                while not (port_file.exists() and len(port_file.read_text().split()) >= 2):
                    if time.time() - t0 > 30 or proc.poll() is not None:
                        sys.exit('Chrome did not open its DevTools port')
                    time.sleep(0.1)
                port, path = port_file.read_text().split()[:2]
                cdp = _DevTools(int(port), path)
                target = cdp.call('Target.createTarget', url='about:blank')['targetId']
                sid = cdp.call('Target.attachToTarget', targetId=target, flatten=True)['sessionId']
                cdp.call('Page.enable', session=sid)
                cdp.call('Emulation.setDeviceMetricsOverride', session=sid, width=1920, height=1080, deviceScaleFactor=1, mobile=False)
                cdp.call('Page.navigate', session=sid, url=tmp.as_uri())
                expr = ('new Promise(function (ok) { var go = function () { Promise.resolve(%s).then(function () { ok(true); }, '
                        'function (e) { (window.__pcErrs = window.__pcErrs || []).push(String(e)); ok(false); }); }; '
                        'document.readyState === "complete" ? go() : addEventListener("load", go); })' % wait)
                t0 = time.time()
                while True:
                    try:
                        r = cdp.call('Runtime.evaluate', session=sid, expression=expr, awaitPromise=True, returnByValue=True)
                        break
                    except RuntimeError:
                        if time.time() - t0 > timeout:
                            raise
                        time.sleep(0.2)   # the page was still navigating
                pdf = cdp.call('Page.printToPDF', session=sid, printBackground=True, preferCSSPageSize=True,
                               generateDocumentOutline=bool(outline), marginTop=0, marginBottom=0, marginLeft=0, marginRight=0)
                pdf_path.write_bytes(base64.b64decode(pdf['data']))
            finally:
                _stop(proc)
    finally:
        tmp.unlink(missing_ok=True)
    return pdf_path


def fix_masks(pdf_path):
    """Chrome draws a CSS-masked box twice: first under an inverted mask of the whole box (which should show nothing),
    then under the real mask. Quartz (Preview, Safari, Quick Look) mis-draws the first pass, so parts of the box show
    unmasked, and MuPDF leaves a hairline round the box. Give that first pass an empty mask, so it draws nothing in
    any reader. Returns the number of passes fixed."""
    import fitz
    d = fitz.open(pdf_path)
    empty, n = None, 0
    for x in range(1, d.xref_length()):
        try:
            o = d.xref_object(x, compressed=True)
        except Exception:
            continue
        m = re.search(r'/SMask<</Type/Mask/S/Alpha/G (\d+) 0 R/TR (\d+) 0 R>>', o)
        if not m or not o.startswith('<</Type/ExtGState'):
            continue
        g, tr = int(m.group(1)), int(m.group(2))
        try:
            if d.xref_stream(tr).strip() != b'{1 exch sub}':
                continue
            body = d.xref_stream(g)
        except Exception:
            continue
        box = re.search(r'/BBox\[([^\]]+)\]', d.xref_object(g, compressed=True))
        rect = re.search(rb'([-\d.]+) ([-\d.]+) ([-\d.]+) ([-\d.]+) re\s*f\s*$', body)
        if b'Do' in body or b'sh' in body.split() or not (box and rect):
            continue
        bx = [float(v) for v in box.group(1).split()]
        rx, ry, rw, rh = (float(v) for v in rect.groups())
        if abs(rx - bx[0]) > 1 or abs(ry - bx[1]) > 1 or abs(rx + rw - bx[2]) > 1 or abs(ry + rh - bx[3]) > 1:
            continue
        if empty is None:
            empty = d.get_new_xref()
            d.update_object(empty, '<</Type/XObject/Subtype/Form/BBox[0 0 1 1]/Group<</Type/Group/S/Transparency>>>>')
            d.update_stream(empty, b' ')
        d.update_object(x, o[:m.start()] + '/SMask<</Type/Mask/S/Alpha/G %d 0 R>>' % empty + o[m.end():])
        n += 1
    if n:
        d.saveIncr()
    d.close()
    return n


def print_pdf(src_html, pdf_path, expect=None, timeout=180, head='', outline=False):
    """Print with headless Chrome (see _print_pdf), then fix its masks for every PDF reader."""
    out = _print_pdf(src_html, pdf_path, expect, timeout, head, outline)
    fix_masks(out)
    return out


def print_pdf_wait(src_html, pdf_path, wait, head='', tail='', outline=False, timeout=240):
    """Print once the page's `wait` promise resolves (see _print_pdf_wait), then fix its masks."""
    out = _print_pdf_wait(src_html, pdf_path, wait, head, tail, outline, timeout)
    fix_masks(out)
    return out


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[2].endswith('.pdf'):
        print(print_pdf(sys.argv[1], sys.argv[2]))
    else:
        sys.exit('python3 tools/chrome.py DECK.html OUT.pdf   (prints the deck with headless Chrome)')
