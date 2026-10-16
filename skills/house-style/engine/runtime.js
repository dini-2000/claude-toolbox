/* House Style runtime: navigation, builds, charts, hand-drawn marks, icons, code colouring, notes, overview,
   presenter window, reading view and the Download menu. One deck per page: <div class="pc-deck"> holding
   <section class="pc-slide"> children. Works from file:// with no network.
   API: window.PCDeck = { show, next, prev, count, index, set({theme, palette, mode, format, motion}), redraw,
   exportPdf, exportPptx, prepareForPrint }. Each slide change fires "pc:slide" on the deck ({index, slide}). */
(function () {
  'use strict';
  const doc = document, win = window;
  const deck = doc.querySelector('.pc-deck');
  if (!deck || deck.dataset.pcReady) return;
  deck.dataset.pcReady = '1';
  const slides = Array.from(deck.querySelectorAll(':scope > .pc-slide'));
  const N = slides.length;
  /* A document (<html class="pc-deck pc-doc">) has pages, not slides: it gets the charts, icons, marks, code colours,
     contents and notes, and none of the slide controls (docInit, at the end) */
  const isDoc = deck.classList.contains('pc-doc');
  if (!N && !isDoc) return;

  /* ---------- helpers ---------- */
  const SVGNS = 'http://www.w3.org/2000/svg';
  const UA = navigator.userAgent;
  const paperPrint = /AppleWebKit/.test(UA) && !/Chrome|Chromium|Edg|OPR/.test(UA);
  const reduced = win.matchMedia('(prefers-reduced-motion: reduce)');
  const el = (tag, cls, html) => { const e = doc.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; };
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const sv = (tag, attrs, parent) => {
    const e = doc.createElementNS(SVGNS, tag);
    for (const k in attrs) if (attrs[k] != null) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  };
  const cssv = (node, name) => getComputedStyle(node).getPropertyValue(name).trim();
  const px = (node, name) => parseFloat(cssv(node, name)) || 0;
  const ms = (node, name) => { const v = cssv(node, name), n = parseFloat(v) || 0; return /ms$/.test(v) ? n : /s$/.test(v) ? n * 1000 : n; };
  const f1 = v => Math.round(v * 10) / 10;
  const decimals = s => { const m = String(s).match(/\.(\d+)/); return m ? m[1].length : 0; };
  const fmt = (v, dp, group = true) => v.toLocaleString('en-GB', { minimumFractionDigits: dp, maximumFractionDigits: dp, useGrouping: group });
  const num = s => parseFloat(String(s).replace(/−/g, '-').replace(/[^\d.\-]/g, ''));
  const frames = n => new Promise(res => {
    let left = n, done = false;
    const fin = () => { if (!done) { done = true; res(); } };
    const step = () => (--left <= 0 ? fin() : requestAnimationFrame(step));
    requestAnimationFrame(step); setTimeout(fin, 80 * n);
  });
  const deckTitle = () => deck.dataset.title || doc.title || '';
  const slideTitle = (s, i) => { const t = s.querySelector('.pc-title, .pc-say, h1, h2'); return (t && t.textContent.trim()) || 'Slide ' + (i + 1); };

  let cur = -1, W = 1920, H = 1080, reading = false, notesOpen = false;
  if (!deck.dataset.motion) deck.dataset.motion = 'basic';
  deck.classList.add('pc-js');
  if (!isDoc && !deck.hasAttribute('tabindex')) deck.tabIndex = -1;

  /* ---------- slide annotations the themes read ---------- */
  function annotate() {
    const title = deckTitle();
    let section = '', sec = 0, sub = 0;
    slides.forEach((s, i) => {
      const prev = section, isSec = s.classList.contains('pc-section');
      if (s.dataset.section != null) section = s.dataset.section;
      else if (isSec) { const t = s.querySelector('.pc-title'); section = t ? t.textContent.trim() : ''; }
      // data-sec-n numbers slides by section ("2" on a section opener, "2.3" after it) for themes that show it
      if (isSec || (s.dataset.section != null && section !== prev)) { sec++; sub = 0; }
      if (!isSec && sec) sub++;
      if (sec && !s.classList.contains('pc-cover')) s.dataset.secN = isSec ? String(sec) : sec + '.' + sub; else delete s.dataset.secN;
      const p = N > 1 ? i / (N - 1) : 0;
      s.style.setProperty('--progress', p.toFixed(4));
      s.dataset.n = s.dataset.label || String(i + 1);
      if (p > .6) s.dataset.side = 'left'; else delete s.dataset.side;
      if (s.classList.contains('pc-cover')) delete s.dataset.sectionName; else s.dataset.sectionName = section;
      s.dataset.deckTitle = title;
      s.dataset.of = String(N);
      s.dataset.cycle = String(i % 6);
      let n = s.querySelector(':scope > .pc-num');
      if (!n) { n = el('span', 'pc-num'); n.setAttribute('aria-hidden', 'true'); s.appendChild(n); }
      n.textContent = s.dataset.n;
      if (!s.hasAttribute('aria-label')) { s.setAttribute('role', 'group'); s.setAttribute('aria-roledescription', 'slide'); s.setAttribute('aria-label', (i + 1) + ' of ' + N + ': ' + slideTitle(s, i)); }
    });
  }

  /* ---------- scale to fit ---------- */
  // print formats print at their real size; the rest print a page the size of the slide
  const PAGE_MM = { a4p: '210mm 297mm', a4l: '297mm 210mm', '5x7': '127mm 177.8mm', 'letter-p': '8.5in 11in', card: '85mm 55mm' };
  function fit() {
    W = px(deck, '--W') || 1920; H = px(deck, '--H') || 1080;
    const fmtId = deck.dataset.format, page = deck.dataset.page || PAGE_MM[fmtId] || W + 'px ' + H + 'px';   // data-page: a print size of its own (export_graphic.py)
    if (pageStyle.dataset.size !== page) { pageStyle.dataset.size = page; pageStyle.textContent = '@page { size: ' + page + '; margin: 0; }'; }
    const nh = notesOpen ? notesPanel.offsetHeight : 0;
    deck.style.setProperty('--notes-h', nh + 'px');
    deck.style.setProperty('--scale', Math.min(win.innerWidth / W, (win.innerHeight - nh) / H));
    const cw = (deck.clientWidth || win.innerWidth) - 32;
    deck.style.setProperty('--read-scale', Math.max(.05, Math.min(1, cw / W, (win.innerHeight - 64) / H)));
    if (!overview.hidden) sizeThumbs();
    fitTitles();
    fitStats();
    fitCode();
  }

  /* A hyphenated word in a title stays on one line ("co-op", never "co-" then "op"): it goes in a nowrap span, once */
  const keptWhole = new WeakSet();
  function keepHyphens(t) {
    if (keptWhole.has(t)) return;
    keptWhole.add(t);
    const walk = doc.createTreeWalker(t, NodeFilter.SHOW_TEXT), texts = [];
    while (walk.nextNode()) if (/[^\s-]-[^\s-]/.test(walk.currentNode.data) && !walk.currentNode.parentNode.closest('svg, .pc-nobr')) texts.push(walk.currentNode);
    texts.forEach(n => {
      const frag = doc.createDocumentFragment();
      n.data.split(/(\s+)/).forEach(p => {
        if (!p) return;
        if (p.length > 18 || !/[^\s-]-[^\s-]/.test(p)) { frag.appendChild(doc.createTextNode(p)); return; }
        const w = el('span', 'pc-nobr'); w.textContent = p; frag.appendChild(w);
      });
      n.parentNode.replaceChild(frag, n);
    });
  }

  /* Display titles (cover, section, closing) keep to three lines (--title-lines: four on 9:16): a longer one steps
     down through --k-hero on its slide, to 72% of its size at most. data-k-hero keeps the author's own factor, so a
     format change starts afresh */
  function fitTitles() {
    deck.querySelectorAll(':scope > .pc-slide :is(.pc-title, .pc-say)').forEach(keepHyphens);
    const most = parseFloat(getComputedStyle(deck).getPropertyValue('--title-lines')) || 3;
    deck.querySelectorAll(':scope > .pc-slide:is(.pc-cover, .pc-section, .pc-closing)').forEach(s => {
      const t = s.querySelector('.pc-title');
      if (!t) return;
      if (s.dataset.kHero === undefined) s.dataset.kHero = s.style.getPropertyValue('--k-hero').trim();
      const own = s.dataset.kHero;
      if (own) s.style.setProperty('--k-hero', own); else s.style.removeProperty('--k-hero');
      const base = parseFloat(own) || parseFloat(getComputedStyle(s).getPropertyValue('--k-hero')) || 1;   // the theme's own factor
      const lines = () => {
        const cs = getComputedStyle(t), lh = /px$/.test(cs.lineHeight) ? parseFloat(cs.lineHeight) : parseFloat(cs.fontSize) * 1.1;
        return t.offsetHeight / lh;
      };
      for (let k = .96; k > .71 && lines() > most + .3; k -= .04) s.style.setProperty('--k-hero', +(base * k).toFixed(3));
    });
  }

  /* Stat figures keep to their cells: a slide whose widest figure is wider than its cell steps down through --k-stat,
     to 70% of its size at most, so a row's figures stay one size. data-k-stat keeps the author's own factor */
  function fitStats() {
    deck.querySelectorAll(':scope > .pc-slide').forEach(s => {
      const st = s.querySelectorAll(':is(.pc-stats, .pc-big) .pc-stat');
      if (!st.length) return;
      if (s.dataset.kStat === undefined) s.dataset.kStat = s.style.getPropertyValue('--k-stat').trim();
      const own = s.dataset.kStat;
      if (own) s.style.setProperty('--k-stat', own); else s.style.removeProperty('--k-stat');
      const base = parseFloat(own) || parseFloat(getComputedStyle(s).getPropertyValue('--k-stat')) || 1;   // a theme may set its own
      // a figure never spills its box; in a row of stats it also keeps 5% of its cell clear, so it never runs into the
      // next one (measured on the text: a big figure's box is only as wide as its text)
      const wide = e => {
        if (e.scrollWidth > e.clientWidth + 1) return true;
        if (!e.closest('.pc-stats')) return false;
        const r = doc.createRange(); r.selectNodeContents(e);
        return r.getBoundingClientRect().width > e.getBoundingClientRect().width * .95;
      };
      const over = () => Array.from(st).some(wide);
      for (let k = .95; k > .49 && over(); k -= .05) s.style.setProperty('--k-stat', +(base * k).toFixed(3));   // wide faces in a row of four need down to half
    });
  }

  /* Code keeps its lines whole. A block that would lose more than 15% of its size beside other columns moves onto a
     row of its own (data-fit="stack") when the slide has the height for it; whatever is still too wide gets a smaller
     font, down to 60% of the token size */
  function fitCode() {
    const shrink = p => {
      const avail = p.clientWidth, need = p.scrollWidth;
      if (!avail || need <= avail + 1) return 1;
      const cs = getComputedStyle(p), pad = parseFloat(cs.paddingLeft) + parseFloat(cs.paddingRight);
      return Math.max(.6, (avail - pad) / (need - pad));
    };
    deck.querySelectorAll('pre.pc-code').forEach(p => {
      p.style.fontSize = ''; delete p.dataset.fit;
      let k = shrink(p);
      const grid = p.parentElement, body = p.closest('.pc-body');
      if (k < .85 && body && grid.matches('.pc-grid:not(.pc-keep)') && getComputedStyle(grid).gridTemplateColumns.split(' ').length > 1) {
        p.dataset.fit = 'stack';
        if (body.scrollHeight > body.clientHeight + 1) delete p.dataset.fit;
        else k = shrink(p);
      }
      if (k < 1) p.style.fontSize = (parseFloat(getComputedStyle(p).fontSize) * k * .98).toFixed(2) + 'px';
    });
  }

  /* ---------- icons: <i class="pc-icon" data-icon="name"> (Lucide, from window.PC_ICONS) ---------- */
  function drawIcons(root) {
    const set = win.PC_ICONS || {};
    root.querySelectorAll('.pc-icon[data-icon]').forEach(i => {
      const name = i.dataset.icon;
      if (i.dataset.drawn === name) return;
      if (!set[name]) { i.dataset.missing = ''; return; }
      i.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">' + set[name] + '</svg>';
      i.dataset.drawn = name; delete i.dataset.missing;
      if (!i.hasAttribute('aria-label')) i.setAttribute('aria-hidden', 'true');
    });
  }

  /* ---------- code colouring: <pre class="pc-code" data-lang="python"><code>...</code></pre> ---------- */
  const KW = {
    js: 'async await break case catch class const continue default delete do else export extends finally for from function if import in instanceof let new of return static super switch this throw try typeof var void while yield null true false undefined interface type enum implements public private protected readonly',
    py: 'and as assert async await break class continue def del elif else except finally for from global if import in is lambda None nonlocal not or pass raise return True False try while with yield self match case',
    sql: 'select from where and or not insert into values update set delete create table view index join left right inner outer full on group by order having limit offset as distinct union all case when then else end null is in like between exists with asc desc primary key foreign references default',
    sh: 'if then else elif fi for while until do done case esac function in return local export echo exit set unset',
    css: 'important',
    generic: 'if else for while do return break continue switch case default function class struct enum const let var new delete true false null nil none public private protected static void int float double bool char string import package using namespace fn func def go defer type interface impl trait match mut pub use self this try catch throw finally async await yield'
  };
  const ALIAS = { javascript: 'js', ts: 'js', typescript: 'js', jsx: 'js', tsx: 'js', json: 'js', python: 'py', bash: 'sh', shell: 'sh', zsh: 'sh', console: 'sh', postgres: 'sql', mysql: 'sql', sqlite: 'sql', scss: 'css' };
  const COMMENT = { py: /#[^\n]*/, sh: /#[^\n]*/, r: /#[^\n]*/, yaml: /#[^\n]*/, toml: /#[^\n]*/, sql: /--[^\n]*|\/\*[\s\S]*?\*\//, css: /\/\*[\s\S]*?\*\//, html: /<!-{2}[\s\S]*?-->/, xml: /<!-{2}[\s\S]*?-->/ };
  const STR = /"(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])*'|`(?:\\.|[^`\\])*`/.source;
  const NUMRX = /\b\d[\d_]*(?:\.\d+)?(?:[eE][+-]?\d+)?\b/.source;
  function highlight(pre) {
    if (pre.dataset.lit) return;
    pre.dataset.lit = '1';
    const lang = (pre.dataset.lang || '').toLowerCase();
    if (!lang || lang === 'text' || lang === 'none') return;
    const key = ALIAS[lang] || lang;
    const ci = key === 'sql';
    const kw = new Set((KW[key] || KW.generic).split(' '));
    const rx = new RegExp('(' + (COMMENT[key] || /\/\/[^\n]*|\/\*[\s\S]*?\*\//).source + ')|(' + STR + ')|(' + NUMRX + ')|([A-Za-z_$][\\w$]*)(?=\\s*\\()|(@?[A-Za-z_$][\\w$]*)', 'g');
    const walk = doc.createTreeWalker(pre, NodeFilter.SHOW_TEXT);
    const nodes = [];
    while (walk.nextNode()) nodes.push(walk.currentNode);
    nodes.forEach(t => {
      const src = t.nodeValue;
      let out = '', last = 0, m;
      rx.lastIndex = 0;
      while ((m = rx.exec(src))) {
        if (!m[0]) { rx.lastIndex++; continue; }
        out += esc(src.slice(last, m.index)); last = rx.lastIndex;
        let cls = m[1] ? 't-c' : m[2] ? 't-s' : m[3] ? 't-n' : '';
        const word = m[4] || m[5];
        if (word) {
          const w = ci ? word.toLowerCase() : word;
          if (kw.has(w)) cls = 't-k';
          else if (m[4]) cls = 't-f';
          else if (/^@|^[A-Z][a-z]/.test(word)) cls = 't-p';
        }
        out += cls ? '<span class="' + cls + '">' + esc(m[0]) + '</span>' : esc(m[0]);
      }
      out += esc(src.slice(last));
      const holder = doc.createElement('span');
      holder.innerHTML = out;
      t.replaceWith(...Array.from(holder.childNodes));
    });
  }

  /* ---------- hand-drawn marks: <span class="pc-mark" data-mark="circle">word</span> ---------- */
  function seeded(str) {
    let h = 1779033703 ^ str.length;
    for (let i = 0; i < str.length; i++) { h = Math.imul(h ^ str.charCodeAt(i), 3432918353); h = (h << 13) | (h >>> 19); }
    return () => { h = Math.imul(h ^ (h >>> 16), 2246822507); h = Math.imul(h ^ (h >>> 13), 3266489909); h ^= h >>> 16; return (h >>> 0) / 4294967296; };
  }
  function smooth(pts) {
    let d = 'M' + f1(pts[0][0]) + ',' + f1(pts[0][1]);
    for (let i = 0; i < pts.length - 1; i++) {
      const p0 = pts[i - 1] || pts[i], p1 = pts[i], p2 = pts[i + 1], p3 = pts[i + 2] || p2;
      d += 'C' + f1(p1[0] + (p2[0] - p0[0]) / 6) + ',' + f1(p1[1] + (p2[1] - p0[1]) / 6) + ' ' +
        f1(p2[0] - (p3[0] - p1[0]) / 6) + ',' + f1(p2[1] - (p3[1] - p1[1]) / 6) + ' ' + f1(p2[0]) + ',' + f1(p2[1]);
    }
    return d;
  }
  function markPaths(type, w, h, rnd) {
    const j = a => (rnd() * 2 - 1) * a;
    const line = (x0, y0, x1, y1, bow) => {
      const mx = (x0 + x1) / 2, my = (y0 + y1) / 2 + j(bow);
      return 'M' + f1(x0) + ',' + f1(y0) + 'Q' + f1(mx + j(w * .05)) + ',' + f1(my) + ' ' + f1(x1) + ',' + f1(y1);
    };
    switch (type) {
      case 'underline': return [line(w * (.03 + j(.01)), h * (.9 + j(.02)), w * (.97 + j(.01)), h * (.86 + j(.02)), h * .06)];
      case 'strike': return [line(w * .03, h * (.58 + j(.03)), w * .97, h * (.5 + j(.03)), h * .04)];
      case 'cross': return [line(w * .06, h * .16, w * .94, h * .86, h * .05), line(w * .07, h * .86, w * .93, h * .17, h * .05)];
      case 'highlight': return [line(w * .03, h * (.6 + j(.02)), w * .97, h * (.56 + j(.02)), h * .02)];
      case 'box': {
        const p = [[w * .03, h * .08], [w * .97, h * .05], [w * .975, h * .94], [w * .025, h * .96], [w * .045, h * .02]];
        return ['M' + p.map(q => f1(q[0] + j(w * .008)) + ',' + f1(q[1] + j(h * .03))).join('L')];
      }
      default: {
        const cx = w / 2, cy = h * .52, rx = w * .49, ry = h * .47, pts = [];
        const a0 = Math.PI * (1.1 + j(.05)), turn = Math.PI * 2.16;
        for (let k = 0; k <= 22; k++) {
          const a = a0 + turn * k / 22, s = 1 + j(.035) + (k > 18 ? .05 : 0);
          pts.push([cx + Math.cos(a) * rx * s, cy + Math.sin(a) * ry * s]);
        }
        return [smooth(pts)];
      }
    }
  }
  function drawMarks(root) {
    root.querySelectorAll('.pc-mark[data-mark]').forEach(m => {
      const old = m.querySelector(':scope > svg.pc-mark-svg');
      if (old) old.remove();
      const w = m.offsetWidth * 1.12, h = m.offsetHeight * 1.36;
      if (!w || !h) return;
      const type = m.dataset.mark;
      const svg = sv('svg', { class: 'pc-mark-svg', viewBox: '0 0 ' + f1(w) + ' ' + f1(h), 'aria-hidden': 'true', focusable: 'false' });
      const rnd = seeded(type + ':' + m.textContent);
      markPaths(type, w, h, rnd).forEach((d, k) => {
        const p = sv('path', { d, class: 'ch-draw', pathLength: 1 }, svg);
        if (type === 'highlight') p.style.strokeWidth = f1(h * .5) + 'px';
        if (k) p.style.setProperty('--k', k * 4);
      });
      m.appendChild(svg);
    });
  }

  /* ---------- charts: <figure class="pc-chart" data-type="column" data-labels="..." data-values="..."> or a child <table> ---------- */
  const NAMES = { column: 'Column chart', bar: 'Bar chart', grouped: 'Grouped column chart', stacked: 'Stacked column chart', line: 'Line chart', area: 'Area chart', donut: 'Donut chart', waterfall: 'Waterfall chart', progress: 'Progress' };
  function splitList(s, sep) {
    s = String(s == null ? '' : s).trim();
    if (!s) return [];
    return s.split(sep || (s.includes(';') ? ';' : ',')).map(x => x.trim());
  }
  function chartData(fig) {
    const raw = [];
    let labels = [], series = [];
    const table = fig.querySelector('table');
    if (table) {
      const rows = Array.from(table.rows).filter(r => r.cells.length);
      const head = rows.shift();
      series = Array.from(head.cells).slice(1).map(c => ({ name: c.textContent.trim(), values: [] }));
      rows.forEach(r => {
        const cells = Array.from(r.cells);
        labels.push(cells[0].textContent.trim());
        series.forEach((s, k) => { const t = cells[k + 1] ? cells[k + 1].textContent.trim() : ''; raw.push(t); s.values.push(num(t)); });
      });
      table.classList.add('pc-sr-only');
    } else {
      labels = splitList(fig.dataset.labels);
      const names = splitList(fig.dataset.series, String(fig.dataset.series || '').includes('|') ? '|' : null);
      series = String(fig.dataset.values || '').split('|').map((v, k) => {
        const vals = splitList(v); raw.push(...vals);
        return { name: names[k] || '', values: vals.map(num) };
      });
    }
    const n = Math.max(labels.length, ...series.map(s => s.values.length));
    while (labels.length < n) labels.push('');
    series.forEach(s => { while (s.values.length < n) s.values.push(NaN); });
    const dp = fig.dataset.dp != null ? +fig.dataset.dp : Math.min(3, Math.max(0, ...raw.map(decimals)));
    return { labels, series, n, dp };
  }
  function niceTicks(lo, hi, count) {
    const span = hi - lo || Math.abs(hi) || 1, raw = span / (count || 5), mag = Math.pow(10, Math.floor(Math.log10(raw)));
    const step = [1, 2, 2.5, 5, 10].map(m => m * mag).find(st => span / st <= (count || 5)) || 10 * mag;
    const a = Math.floor(lo / step + 1e-9) * step, b = Math.ceil(hi / step - 1e-9) * step;
    const ticks = [];
    for (let v = a; v <= b + step / 2; v += step) ticks.push(+v.toFixed(10));
    return { lo: a, hi: b, step, ticks };
  }
  function hexLum(hex) {
    const m = String(hex).trim().match(/^#([0-9a-f]{6})$/i);
    if (!m) return null;
    const c = [0, 2, 4].map(i => parseInt(m[1].slice(i, i + 2), 16) / 255).map(v => v <= .04045 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4));
    return .2126 * c[0] + .7152 * c[1] + .0722 * c[2];
  }
  function inkOn(fig, n) {
    const L = hexLum(cssv(fig, '--c' + n));
    if (L == null) return '#ffffff';
    return (1.05 / (L + .05)) >= 4.5 ? '#ffffff' : '#111111';
  }

  function chartCtx(fig, svg, d) {
    const type = (fig.dataset.type || 'column').toLowerCase();
    const c = {
      fig, svg, d, type,
      pre: fig.dataset.prefix || '', suf: fig.dataset.suffix != null ? fig.dataset.suffix : (type === 'progress' && !fig.dataset.max ? '%' : ''),
      dp: d.dp, fs: px(fig, '--fs-text') || px(fig, '--fs-small') || 26, fsl: px(fig, '--fs-label') || 19,
      radius: Math.min(px(fig, '--radius-sm'), 12), hl: -1, w: 0, h: 0
    };
    const hlv = fig.dataset.highlight;
    if (hlv != null && hlv !== '') {
      const pool = (type === 'line' || type === 'area') && d.series.length > 1 ? d.series.map(s => s.name) : d.labels;
      c.hl = pool.findIndex(x => x.toLowerCase() === hlv.toLowerCase());
      if (c.hl < 0 && /^\d+$/.test(hlv) && +hlv >= 1 && +hlv <= pool.length) c.hl = +hlv - 1;
    }
    return c;
  }
  const fmtv = (c, v, sign) => (v < 0 ? '−' : sign && v > 0 ? '+' : '') + c.pre + fmt(Math.abs(v), c.dp) + c.suf;
  function tw(c, str, size, cls) {
    const t = sv('text', { x: 0, y: -2000, class: cls || null }, c.svg);
    t.style.fontSize = size + 'px'; t.textContent = str;
    const w = t.getComputedTextLength(); t.remove(); return w;
  }
  function wrap(c, str, max, size) {
    if (!str || tw(c, str, size) <= max) return [str || ''];
    const out = []; let line = '';
    str.split(/\s+/).forEach(wd => {
      const t = line ? line + ' ' + wd : wd;
      if (!line || tw(c, t, size) <= max) line = t; else { out.push(line); line = wd; }
    });
    if (line) out.push(line);
    return out;
  }
  /* Category labels wrap at spaces; a word wider than its slot shrinks the whole axis's labels, down to 72% */
  // room for a category label in its band, leaving at least 10 px between neighbours (a wide face on a narrow page filled the band)
  const room = band => band - Math.max(10, band * .06);
  function catWrap(c, labels, max, stagger) {
    let size = c.fs, cats = labels.map(l => wrap(c, l, max, size));
    const widest = () => Math.max(0, ...cats.flat().map(ln => tw(c, ln, size)));
    let w = widest();
    if (w > max) { size = Math.max(c.fs * .72, c.fs * max / w); cats = labels.map(l => wrap(c, l, max, size)); }
    // a word still wider than its band at the smallest size: labels alternate between two rows, so each has two bands of room
    let rows2 = false;
    if (stagger && labels.length > 2 && widest() > max) {
      rows2 = true; size = c.fs; cats = labels.map(l => wrap(c, l, max * 2, size));
      w = widest(); if (w > max * 2) { size = Math.max(c.fs * .72, c.fs * max * 2 / w); cats = labels.map(l => wrap(c, l, max * 2, size)); }
    }
    const L = Math.max(1, ...cats.map(l => l.length));
    cats.size = size; cats.shift = rows2 ? L * size * 1.18 : 0; cats.rows = rows2 ? L * 2 : L;
    return cats;
  }
  function text(c, x, y, str, o) {
    o = o || {};
    const t = sv('text', { x: f1(x), y: f1(y), 'text-anchor': o.anchor || 'middle', class: o.cls || null }, c.svg);
    t.style.fontSize = f1(o.size || c.fs) + 'px';
    if (o.fill) t.style.fill = o.fill;
    if (o.k != null) t.style.setProperty('--k', o.k);
    if (str != null) t.textContent = str;
    return t;
  }
  function mtext(c, x, y, lines, o) {
    const t = text(c, x, y, null, o);
    lines.forEach((ln, k) => { const s = sv('tspan', { x: f1(x), dy: k ? '1.18em' : 0 }, t); s.textContent = ln; });
    return t;
  }
  function barPath(x, y, w, h, r, side) {
    r = Math.max(0, Math.min(r, w / 2, h / 2, side === 'right' || side === 'left' ? h / 2 : w / 2));
    const X = f1(x), Y = f1(y), R = f1(x + w), B = f1(y + h);
    if (!r) return 'M' + X + ',' + Y + 'H' + R + 'V' + B + 'H' + X + 'Z';
    const q = f1(r);
    if (side === 'bottom') return 'M' + X + ',' + Y + 'V' + f1(y + h - r) + 'Q' + X + ',' + B + ' ' + f1(x + r) + ',' + B + 'H' + f1(x + w - r) + 'Q' + R + ',' + B + ' ' + R + ',' + f1(y + h - r) + 'V' + Y + 'Z';
    if (side === 'right') return 'M' + X + ',' + Y + 'H' + f1(x + w - r) + 'Q' + R + ',' + Y + ' ' + R + ',' + f1(y + r) + 'V' + f1(y + h - r) + 'Q' + R + ',' + B + ' ' + f1(x + w - r) + ',' + B + 'H' + X + 'Z';
    if (side === 'left') return 'M' + R + ',' + Y + 'H' + f1(x + r) + 'Q' + X + ',' + Y + ' ' + X + ',' + f1(y + r) + 'V' + f1(y + h - r) + 'Q' + X + ',' + B + ' ' + f1(x + r) + ',' + B + 'H' + R + 'Z';
    return 'M' + X + ',' + B + 'V' + f1(y + r) + 'Q' + X + ',' + Y + ' ' + f1(x + q) + ',' + Y + 'H' + f1(x + w - r) + 'Q' + R + ',' + Y + ' ' + R + ',' + f1(y + r) + 'V' + B + 'Z';
  }
  function bar(c, x, y, w, h, side, fill, k, cls) {
    const p = sv('path', { d: barPath(x, y, w, h, c.radius, side), class: cls }, c.svg);
    p.style.fill = fill; p.style.setProperty('--k', k);
    return p;
  }
  function arcPath(cx, cy, r, a1, a2) {
    const pt = a => f1(cx + r * Math.cos(a)) + ',' + f1(cy + r * Math.sin(a));
    if (a2 - a1 >= Math.PI * 2 - 1e-6) return 'M' + pt(a1) + 'A' + f1(r) + ',' + f1(r) + ' 0 1 1 ' + pt(a1 + Math.PI) + 'A' + f1(r) + ',' + f1(r) + ' 0 1 1 ' + pt(a1 + Math.PI * 2 - 1e-4);
    return 'M' + pt(a1) + 'A' + f1(r) + ',' + f1(r) + ' 0 ' + (a2 - a1 > Math.PI ? 1 : 0) + ' 1 ' + pt(a2);
  }
  function legend(items) {
    const lg = el('div', 'ch-legend');
    lg.setAttribute('aria-hidden', 'true');
    items.forEach(it => {
      const s = el('span'), sw = el('i');
      sw.style.background = it.color;
      s.append(sw, doc.createTextNode(it.label));
      if (it.value) { const b = el('b'); b.textContent = it.value; s.appendChild(b); }
      lg.appendChild(s);
    });
    return lg;
  }
  const colour = (c, j) => 'var(--c' + (j % 6 + 1) + ')';

  function drawColumns(c) {
    const { d } = c, S = d.series.length, n = d.n;
    const vals = d.series.flatMap(s => s.values).filter(isFinite);
    let lo = Math.min(0, ...vals), hi = Math.max(0, ...vals);
    if (hi === lo) hi = lo + 1;
    let axis = c.fig.hasAttribute('data-axis'), tk = null, left = 0;
    const plan = () => {
      if (axis) { tk = niceTicks(lo, hi, 5); lo = tk.lo; hi = tk.hi; left = Math.max(...tk.ticks.map(v => tw(c, fmtv(c, v), c.fsl))) + 18; }
      const band = (c.w - left) / n;
      const inner = band * (S > 1 ? .8 : .62), gap = S > 1 ? Math.max(4, inner * .03) : 0;
      const bw = Math.min((inner - gap * (S - 1)) / S, S > 1 ? 120 : 210);
      return { band, gap, bw };
    };
    let g = plan();
    let vsize = c.fs;
    const widest = Math.max(...vals.map(v => tw(c, fmtv(c, v), c.fs, 'ch-val')));
    if (widest > g.bw + g.gap * .8) vsize = Math.max(c.fsl * .85, c.fs * (g.bw + g.gap * .8) / widest);
    const showVals = !c.fig.hasAttribute('data-no-values') && widest * vsize / c.fs <= g.bw + g.gap + 4;
    if (!showVals && !axis) { axis = true; g = plan(); }
    const cats = catWrap(c, d.labels, room(g.band), true);
    const lines = cats.rows;
    const bottom = lines * cats.size * 1.18 + 12, top = showVals ? vsize * 1.5 : c.fsl;
    const negRoom = lo < 0 && showVals ? vsize * 1.5 : 0;
    const pb = c.h - bottom - negRoom;
    const y = v => top + (hi - v) / (hi - lo) * (pb - top);
    const y0 = y(0);
    if (axis) tk.ticks.forEach(v => {
      sv('line', { x1: left, x2: c.w, y1: f1(y(v)), y2: f1(y(v)), class: 'ch-grid' }, c.svg);
      text(c, left - 14, y(v) + c.fsl * .35, fmtv(c, v), { anchor: 'end', size: c.fsl, cls: 'ch-tick' });
    });
    let k = 0;
    d.labels.forEach((lab, i) => {
      const groupW = g.bw * S + g.gap * (S - 1), gx = left + g.band * i + (g.band - groupW) / 2;
      d.series.forEach((s, j) => {
        const v = s.values[i];
        if (!isFinite(v)) return;
        const x = gx + j * (g.bw + g.gap), yv = y(v), neg = v < 0;
        const fill = S === 1 && c.hl >= 0 ? (i === c.hl ? 'var(--c1)' : 'var(--chart-muted)') : colour(c, j);
        bar(c, x, Math.min(yv, y0), g.bw, Math.abs(y0 - yv), neg ? 'bottom' : 'top', fill, k, 'ch-bar' + (neg ? ' ch-neg' : ''));
        if (showVals) text(c, x + g.bw / 2, neg ? yv + vsize * 1.05 : yv - vsize * .4, fmtv(c, v), { cls: 'ch-val ch-lab', size: vsize, k });
        k++;
      });
      mtext(c, left + g.band * i + g.band / 2, c.h - bottom + cats.size + 4 + (i % 2 ? cats.shift : 0), cats[i], { size: cats.size });
    });
    sv('line', { x1: left, x2: c.w, y1: f1(y0), y2: f1(y0), class: 'ch-axis' }, c.svg);
  }

  function drawBars(c) {
    const { d } = c, S = d.series.length, n = d.n;
    const vals = d.series.flatMap(s => s.values).filter(isFinite);
    let lo = Math.min(0, ...vals), hi = Math.max(0, ...vals);
    if (hi === lo) hi = lo + 1;
    const labW = Math.min(c.w * .34, Math.max(...d.labels.map(l => tw(c, l, c.fs))));
    const cats = d.labels.map(l => wrap(c, l, labW, c.fs));
    const left = labW + 24;
    const valW = c.fig.hasAttribute('data-no-values') ? 0 : Math.max(...vals.map(v => tw(c, fmtv(c, v), c.fs, 'ch-val'))) + 16;
    const negW = lo < 0 ? valW : 0;
    const x = v => left + negW + (v - lo) / (hi - lo) * (c.w - left - negW - valW);
    const x0 = x(0), row = c.h / n;
    const thick = Math.min(row * (S > 1 ? .8 : .62), S > 1 ? 50 * S : 76), gap = S > 1 ? 4 : 0;
    const bh = (thick - gap * (S - 1)) / S;
    let k = 0;
    d.labels.forEach((lab, i) => {
      const cy = row * i + row / 2;
      mtext(c, labW, cy - (cats[i].length - 1) * c.fs * .59 + c.fs * .35, cats[i], { anchor: 'end' });
      d.series.forEach((s, j) => {
        const v = s.values[i];
        if (!isFinite(v)) return;
        const by = cy - thick / 2 + j * (bh + gap), xv = x(v), neg = v < 0;
        const fill = S === 1 && c.hl >= 0 ? (i === c.hl ? 'var(--c1)' : 'var(--chart-muted)') : colour(c, j);
        const p = bar(c, Math.min(xv, x0), by, Math.abs(xv - x0), bh, neg ? 'left' : 'right', fill, k, 'ch-hbar');
        if (neg) p.style.transformOrigin = '100% 50%';
        if (valW) text(c, neg ? xv - 12 : xv + 12, by + bh / 2 + c.fs * .35, fmtv(c, v), { anchor: neg ? 'end' : 'start', cls: 'ch-val ch-lab', k });
        k++;
      });
    });
    sv('line', { x1: f1(x0), x2: f1(x0), y1: 0, y2: c.h, class: 'ch-axis' }, c.svg);
  }

  function drawStacked(c) {
    const { d } = c, n = d.n;
    const totals = d.labels.map((_, i) => d.series.reduce((a, s) => a + Math.max(0, s.values[i] || 0), 0));
    const hi = Math.max(...totals) || 1;
    const band = c.w / n, bw = Math.min(band * .62, 210);
    const cats = catWrap(c, d.labels, room(band), true);
    const lines = cats.rows;
    const bottom = lines * cats.size * 1.18 + 12, top = c.fs * 1.5, pb = c.h - bottom;
    const y = v => top + (hi - v) / hi * (pb - top);
    const inks = d.series.map((_, j) => inkOn(c.fig, j % 6 + 1));
    let k = 0;
    d.labels.forEach((lab, i) => {
      const x = band * i + (band - bw) / 2;
      let acc = 0;
      const segs = d.series.map((s, j) => ({ j, v: Math.max(0, s.values[i] || 0) })).filter(sg => sg.v > 0);
      segs.forEach((sg, q) => {
        const y1 = y(acc + sg.v), y2 = y(acc);
        bar(c, x, y1, bw, y2 - y1, q === segs.length - 1 ? 'top' : 'none', colour(c, sg.j), k, 'ch-bar');
        const lbl = fmtv(c, sg.v);
        if (y2 - y1 >= c.fsl * 1.7 && tw(c, lbl, c.fsl, 'ch-seg') <= bw - 12) text(c, x + bw / 2, (y1 + y2) / 2 + c.fsl * .35, lbl, { size: c.fsl, cls: 'ch-seg ch-lab', fill: inks[sg.j], k });
        acc += sg.v; k++;
      });
      text(c, x + bw / 2, y(totals[i]) - c.fs * .4, fmtv(c, totals[i]), { cls: 'ch-val ch-lab', k });
      mtext(c, band * i + band / 2, c.h - bottom + cats.size + 4 + (i % 2 ? cats.shift : 0), cats[i], { size: cats.size });
    });
    sv('line', { x1: 0, x2: c.w, y1: f1(pb), y2: f1(pb), class: 'ch-axis' }, c.svg);
  }

  function drawLines(c, area) {
    const { d } = c, S = d.series.length, n = d.n;
    const vals = d.series.flatMap(s => s.values).filter(isFinite);
    let lo = Math.min(...vals), hi = Math.max(...vals);
    if (area || c.fig.dataset.zero === 'yes') lo = Math.min(0, lo);
    if (hi === lo) { hi += 1; lo -= lo > 0 ? 1 : 0; }
    const tk = niceTicks(lo, hi, 5);
    lo = tk.lo; hi = tk.hi;
    const tdp = Math.max(c.dp, decimals(tk.step));
    const tick = v => (v < 0 ? '−' : '') + c.pre + fmt(Math.abs(v), tdp) + c.suf;
    const left = Math.max(...tk.ticks.map(v => tw(c, tick(v), c.fsl))) + 18;
    const lastIdx = s => { for (let i = n - 1; i >= 0; i--) if (isFinite(s.values[i])) return i; return -1; };
    const ends = d.series.map(s => { const i = lastIdx(s); return { i, v: s.values[i], name: s.name }; });
    const endW = Math.max(...ends.map(e => tw(c, fmtv(c, e.v), c.fs, 'ch-val') + (S > 1 && e.name ? tw(c, e.name, c.fs) + 10 : 0)));
    const right = endW + 28;
    const pw = c.w - left - right;
    const labW = Math.max(...d.labels.map(l => tw(c, l, c.fs)));
    const every = Math.max(1, Math.ceil((labW + 24) / (pw / Math.max(1, n - 1))));
    const bottom = c.fs * 1.18 + 14, top = c.fsl;
    const pb = c.h - bottom;
    const inset = n > 1 ? Math.min(labW / 2 + 8, pw / (n - 1) / 2) : 0;
    const x = i => left + (n > 1 ? inset + i * (pw - 2 * inset) / (n - 1) : pw / 2);
    const y = v => top + (hi - v) / (hi - lo) * (pb - top);
    tk.ticks.forEach(v => {
      sv('line', { x1: left, x2: f1(left + pw), y1: f1(y(v)), y2: f1(y(v)), class: v === 0 && lo < 0 ? 'ch-axis' : 'ch-grid' }, c.svg);
      text(c, left - 14, y(v) + c.fsl * .35, tick(v), { anchor: 'end', size: c.fsl, cls: 'ch-tick' });
    });
    d.labels.forEach((l, i) => { if (i % every === 0 || i === n - 1 && (n - 1) % every >= every / 2) text(c, x(i), pb + c.fs + 6, l, {}); });
    const dots = c.fig.hasAttribute('data-dots') || n <= 8;
    const order = d.series.map((s, j) => j).sort((a, b) => (a === c.hl) - (b === c.hl));
    const labels = [];
    order.forEach(j => {
      const s = d.series[j], muted = c.hl >= 0 && j !== c.hl;
      const stroke = muted ? 'var(--chart-muted)' : c.hl >= 0 ? 'var(--c1)' : colour(c, j);
      let path = '', started = false, first = -1, last = -1;
      s.values.forEach((v, i) => {
        if (!isFinite(v)) { started = false; return; }
        path += (started ? 'L' : 'M') + f1(x(i)) + ',' + f1(y(v)); started = true;
        if (first < 0) first = i; last = i;
      });
      if (!path) return;
      if (area) {
        const a = sv('path', { d: path + 'L' + f1(x(last)) + ',' + f1(y(Math.max(lo, 0))) + 'L' + f1(x(first)) + ',' + f1(y(Math.max(lo, 0))) + 'Z', class: 'ch-area ch-lab' }, c.svg);
        a.style.fill = stroke; a.style.setProperty('--k', j);
      }
      const p = sv('path', { d: path, class: 'ch-line ch-draw', pathLength: 1 }, c.svg);
      p.style.stroke = stroke; p.style.setProperty('--k', j);
      if (muted) p.style.strokeWidth = '4px';
      s.values.forEach((v, i) => {
        if (!isFinite(v) || (!dots && i !== last)) return;
        const dot = sv('circle', { cx: f1(x(i)), cy: f1(y(v)), r: muted ? 6 : 9, class: 'ch-dot ch-lab' }, c.svg);
        dot.style.fill = stroke; dot.style.setProperty('--k', j);
      });
      labels.push({ j, y: y(s.values[last]), x: x(last), v: s.values[last], name: s.name, muted });
    });
    labels.sort((a, b) => a.y - b.y);
    const gap = c.fs * 1.25;
    for (let q = 1; q < labels.length; q++) if (labels[q].y - labels[q - 1].y < gap) labels[q].y = labels[q - 1].y + gap;
    const over = labels.length ? labels[labels.length - 1].y - pb : 0;
    if (over > 0) labels.forEach(l => { l.y -= over; });
    labels.forEach(l => {
      const t = text(c, l.x + 18, l.y + c.fs * .35, null, { anchor: 'start', k: l.j });
      t.classList.add('ch-lab');
      const v = sv('tspan', { class: 'ch-val' }, t); v.textContent = fmtv(c, l.v);
      if (S > 1 && l.name) { const nm = sv('tspan', { dx: 10 }, t); nm.textContent = l.name; }
      if (l.muted) t.style.opacity = .8;
    });
  }

  function drawDonut(c) {
    const s = c.d.series[0], vals = s.values.map(v => (isFinite(v) && v > 0 ? v : 0));
    const total = vals.reduce((a, b) => a + b, 0) || 1;
    const size = Math.min(c.w, c.h), cx = c.w / 2, cy = c.h / 2;
    const thick = size * (+c.fig.dataset.thickness || .17), r = size / 2 - thick / 2 - 2;
    const gapA = vals.filter(v => v).length > 1 ? Math.min(.05, 4 / r) : 0;
    let a = -Math.PI / 2, k = 0;
    vals.forEach((v, i) => {
      if (!v) return;
      const sweep = v / total * Math.PI * 2;
      const p = sv('path', { d: arcPath(cx, cy, r, a + gapA / 2, a + sweep - gapA / 2), class: 'ch-arc ch-draw', pathLength: 1 }, c.svg);
      p.style.stroke = c.hl >= 0 && i !== c.hl ? 'var(--chart-muted)' : colour(c, i);
      p.style.strokeWidth = f1(thick) + 'px';
      p.style.setProperty('--k', k++);
      a += sweep;
    });
    if (c.fig.dataset.center !== 'none') {
      const big = c.fig.dataset.total || fmtv(c, vals.reduce((x, y) => x + y, 0));
      const cap = c.fig.dataset.center || '';
      /* The figure fits the hole by its measured width (wide faces and currency signs), and the caption sits below
         the figure's own box, whatever the face's descent */
      let bs = Math.min(size * .17, (r - thick / 2) * 2 * .8 / Math.max(1, big.length * .6));
      const room = (r - thick / 2) * 2 * .78, bw = tw(c, big, bs, 'ch-mid ch-lab');
      if (bw > room) bs *= room / bw;
      const fig = text(c, cx, cy + (cap ? -bs * .08 : bs * .35), big, { cls: 'ch-mid ch-lab', size: bs, k: k });
      let capY = cy + bs * .22 + c.fs * .95;
      try { const b = fig.getBBox(); capY = Math.max(capY, b.y + b.height + c.fs * .92); } catch (e) { /* not drawn yet */ }
      if (cap) mtext(c, cx, capY, wrap(c, cap, (r - thick / 2) * 1.5, c.fs), { cls: 'ch-lab', k: k });
    }
  }

  function drawProgress(c) {
    const s = c.d.series[0], n = c.d.n, max = +c.fig.dataset.max || 100;
    const cell = c.w / n;
    const cats = catWrap(c, c.d.labels, cell * .9);
    const lines = Math.max(0, ...cats.map(l => (l[0] ? l.length : 0)));
    const labH = lines ? lines * cats.size * 1.18 + 18 : 0;
    const size = Math.min(cell * .8, c.h - labH - 4, 480), thick = size * .11, r = size / 2 - thick / 2;
    const cy = (c.h - labH - size) / 2 + size / 2;
    s.values.forEach((v, i) => {
      const cx = cell * i + cell / 2;
      const tr = sv('circle', { cx: f1(cx), cy: f1(cy), r: f1(r), class: 'ch-track' }, c.svg);
      tr.style.strokeWidth = f1(thick) + 'px';
      const part = Math.max(0, Math.min(1, (v || 0) / max));
      if (part > 0) {
        // A full ring is a circle turned to start at the top, so it has no seam
        const p = part >= 1 ? sv('circle', { cx: f1(cx), cy: f1(cy), r: f1(r), transform: 'rotate(-90 ' + f1(cx) + ' ' + f1(cy) + ')', class: 'ch-arc ch-draw', pathLength: 1 }, c.svg)
          : sv('path', { d: arcPath(cx, cy, r, -Math.PI / 2, -Math.PI / 2 + part * Math.PI * 2), class: 'ch-arc ch-draw', pathLength: 1, 'stroke-linecap': 'round' }, c.svg);
        p.style.stroke = c.hl >= 0 && i !== c.hl ? 'var(--chart-muted)' : c.fig.dataset.colors === 'series' ? colour(c, i) : 'var(--c1)';
        p.style.strokeWidth = f1(thick) + 'px';
        p.style.setProperty('--k', i);
      }
      const lbl = isFinite(v) ? fmtv(c, v) : '';
      const bs = Math.min(size * .24, (r - thick / 2) * 2 * .78 / Math.max(1, lbl.length * .58));
      text(c, cx, cy + bs * .35, lbl, { cls: 'ch-mid ch-lab', size: bs, k: i });
      if (cats[i][0]) mtext(c, cx, cy + size / 2 + 18 + cats.size * .8, cats[i], { size: cats.size });
    });
  }

  function drawWaterfall(c) {
    const s = c.d.series[0], labels = c.d.labels.slice();
    const totals = new Set(splitList(c.fig.dataset.totals || '1').map(t => +t - 1));
    let run = 0;
    const bars = s.values.map((v, i) => {
      v = isFinite(v) ? v : 0;
      if (totals.has(i)) { run = v; return { from: 0, to: v, v, total: true }; }
      const from = run; run += v; return { from, to: run, v, total: false };
    });
    if (c.fig.dataset.end) { labels.push(c.fig.dataset.end); bars.push({ from: 0, to: run, v: run, total: true }); }
    const n = bars.length;
    const lo = Math.min(0, ...bars.map(b => Math.min(b.from, b.to))), hi = Math.max(0, ...bars.map(b => Math.max(b.from, b.to))) || 1;
    const band = c.w / n, bw = Math.min(band * .64, 200);
    const cats = catWrap(c, labels, room(band), true);
    const lines = cats.rows;
    const bottom = lines * cats.size * 1.18 + 12, top = c.fs * 1.5, pb = c.h - bottom - (lo < 0 ? c.fs * 1.5 : 0);
    const y = v => top + (hi - v) / (hi - lo) * (pb - top);
    bars.forEach((b, i) => {
      const x = band * i + (band - bw) / 2;
      const y1 = y(Math.max(b.from, b.to)), y2 = y(Math.min(b.from, b.to));
      const down = !b.total && b.v < 0, neg = b.total && b.v < 0;
      const fill = b.total ? 'var(--chart-total, var(--c1))' : b.v >= 0 ? 'var(--positive)' : 'var(--negative)';
      bar(c, x, y1, bw, Math.max(1, y2 - y1), down || neg ? 'bottom' : 'top', fill, i, 'ch-bar' + (down || neg ? ' ch-neg' : ''));
      const lab = b.total ? fmtv(c, b.v) : fmtv(c, b.v, true);
      text(c, x + bw / 2, down || neg ? y2 + c.fs * 1.05 : y1 - c.fs * .4, lab, { cls: 'ch-val ch-lab', k: i });
      if (i < n - 1) {
        const ln = sv('line', { x1: f1(x + bw), x2: f1(x + band), y1: f1(y(b.to)), y2: f1(y(b.to)), class: 'ch-grid ch-lab', 'stroke-dasharray': '6 6' }, c.svg);
        ln.style.setProperty('--k', i);
      }
      mtext(c, band * i + band / 2, c.h - bottom + cats.size + 4 + (i % 2 ? cats.shift : 0), cats[i], { size: cats.size });
    });
    sv('line', { x1: 0, x2: c.w, y1: f1(y(0)), y2: f1(y(0)), class: 'ch-axis' }, c.svg);
  }

  function summarise(c) {
    if (c.fig.dataset.summary) return c.fig.dataset.summary;
    const parts = c.d.series.map(s => (s.name ? s.name + ': ' : '') + c.d.labels.map((l, i) => (l ? l + ' ' : '') + (isFinite(s.values[i]) ? fmtv(c, s.values[i]) : 'no value')).join(', '));
    return (NAMES[c.type] || 'Chart') + '. ' + parts.join('. ') + '.';
  }

  function drawChart(fig) {
    fig.querySelectorAll(':scope > svg, :scope > .ch-legend').forEach(nd => nd.remove());
    fig.classList.remove('ch-side');
    const d = chartData(fig);
    if (!d.n || !d.series.length) return;
    const svg = sv('svg', { role: 'img', focusable: 'false' });
    const after = fig.querySelector(':scope > figcaption, :scope > table');
    fig.insertBefore(svg, after);
    const c = chartCtx(fig, svg, d);
    const S = d.series.length;
    let type = c.type === 'grouped' ? 'column' : c.type;
    if (!NAMES[type]) type = 'column';
    let lg = null;
    if (type === 'donut') {
      const vals = d.series[0].values.map(v => (isFinite(v) && v > 0 ? v : 0)), tot = vals.reduce((a, b) => a + b, 0) || 1;
      lg = legend(d.labels.map((l, i) => ({ label: l, color: c.hl >= 0 && i !== c.hl ? 'var(--chart-muted)' : colour(c, i), value: c.fig.dataset.legend === 'value' ? fmtv(c, vals[i]) : fmt(vals[i] / tot * 100, 0) + '%' })));
    } else if (S > 1 && (type === 'column' || type === 'bar' || type === 'stacked')) {
      lg = legend(d.series.map((s, j) => ({ label: s.name || 'Series ' + (j + 1), color: colour(c, j) })));
    }
    if (lg) fig.insertBefore(lg, after);
    if (type === 'donut' && fig.clientWidth >= 820 && !fig.hasAttribute('data-legend-below')) {
      fig.classList.add('ch-side');
      svg.style.width = '0px'; svg.style.height = '0px';
      let avail = fig.clientHeight;
      if (avail < 240) avail = Math.min(fig.clientWidth * .42, 560);
      const size = Math.floor(Math.min(avail, fig.clientWidth * .5));
      svg.style.width = size + 'px'; svg.style.height = size + 'px';
      c.w = c.h = size;
    } else {
      svg.style.flex = '1 1 auto'; svg.style.height = '0px';
      let h = svg.clientHeight;
      c.w = svg.clientWidth || fig.clientWidth;
      if (h < 80) h = Math.round(c.w * (+fig.dataset.ratio || (type === 'donut' || type === 'progress' ? .42 : .5)));
      svg.style.flex = 'none'; svg.style.height = h + 'px';
      c.h = h;
    }
    svg.setAttribute('viewBox', '0 0 ' + f1(c.w) + ' ' + f1(c.h));
    svg.setAttribute('aria-label', summarise(c));
    ({ column: drawColumns, bar: drawBars, stacked: drawStacked, line: drawLines, area: x => drawLines(x, true), donut: drawDonut, waterfall: drawWaterfall, progress: drawProgress })[type](c);
  }

  function drawAll() {
    const wasReading = deck.classList.contains('is-reading');
    const rebuild = cur >= 0 && slides[cur].classList.contains('is-building');
    if (rebuild) endBuild();                // marks measure the text as it stands, not words flying in
    if (wasReading) deck.classList.remove('is-reading');
    slides.forEach(s => s.querySelectorAll('figure.pc-chart').forEach(fig => { try { drawChart(fig); } catch (e) { console.error('Chart not drawn:', e); fig.dataset.error = e.message; } }));
    slides.forEach(drawMarks);
    if (wasReading) deck.classList.add('is-reading');
    if (rebuild) build(slides[cur]);
  }

  /* ---------- builds ---------- */
  let buildTimer = 0, counters = [];
  const ITEMS = '[data-build], [data-build-each] > *';
  function endBuild() {
    clearTimeout(buildTimer);
    counters.forEach(cancelAnimationFrame); counters = [];
    deck.querySelectorAll(':scope > .pc-slide.is-building').forEach(s => {
      if (s.getAnimations) s.getAnimations({ subtree: true }).forEach(a => { if (a.transitionProperty) a.finish(); });
      s.classList.remove('is-building', 'pc-snap');
    });
    deck.querySelectorAll(':scope > .pc-slide .pc-pre').forEach(e => e.classList.remove('pc-pre'));
    deck.querySelectorAll(':scope > .pc-slide .pc-auto').forEach(e => e.classList.remove('pc-auto'));
    deck.querySelectorAll(':scope > .pc-slide .pc-counting').forEach(e => { e.classList.remove('pc-counting'); e.removeAttribute('data-pc-now'); });
    unsplit();
  }
  /* Converge: a title's words go in spans for the build only, the first half flying in from the left and the rest from
     the right, the words nearest the middle first so none passes another. endBuild puts the title back exactly as it was. */
  const splits = new Map();
  function splitWords(e) {
    if (splits.has(e)) return;
    splits.set(e, e.innerHTML);
    const walk = doc.createTreeWalker(e, NodeFilter.SHOW_TEXT), texts = [], words = [];
    while (walk.nextNode()) if (!walk.currentNode.parentNode.closest('svg')) texts.push(walk.currentNode);
    texts.forEach(t => {
      const frag = doc.createDocumentFragment();
      t.data.split(/([ \t\n\r]+)/).forEach(p => {
        if (!p) return;
        if (/^[ \t\n\r]+$/.test(p)) { frag.appendChild(doc.createTextNode(p)); return; }
        const w = el('span', 'pc-w'); w.textContent = p; words.push(w); frag.appendChild(w);
      });
      t.parentNode.replaceChild(frag, t);
    });
    const mid = Math.max(1, Math.floor(words.length / 2));
    words.forEach((w, k) => { w.style.setProperty('--side', k < mid ? -1 : 1); w.style.setProperty('--w', k < mid ? mid - 1 - k : k - mid); });
    e.classList.add('pc-converge');
  }
  function unsplit() {
    splits.forEach((html, e) => { e.innerHTML = html; e.classList.remove('pc-converge'); });
    splits.clear();
  }
  function countable(e) {
    if (e.dataset.count === 'no' || e.children.length) return null;
    const m = e.textContent.match(/\d[\d,]*(?:\.\d+)?/);
    if (!m || /^(1[89]|20|21)\d\d$/.test(m[0])) return null;
    return m;
  }
  function countUp(e, m, delay) {
    const t = e.textContent, target = parseFloat(m[0].replace(/,/g, '')), dp = decimals(m[0]), group = m[0].includes(',');
    const pre = t.slice(0, m.index), post = t.slice(m.index + m[0].length);
    const D = 1100, t0 = performance.now() + delay;
    e.classList.add('pc-counting');
    e.dataset.pcNow = pre + fmt(0, dp, group) + post;
    const tick = now => {
      const p = Math.max(0, Math.min(1, (now - t0) / D));
      e.dataset.pcNow = pre + fmt(target * (1 - Math.pow(1 - p, 3)), dp, group) + post;
      if (p < 1) counters.push(requestAnimationFrame(tick));
      else { e.classList.remove('pc-counting'); e.removeAttribute('data-pc-now'); }
    };
    counters.push(requestAnimationFrame(tick));
  }
  function build(slide) {
    endBuild();
    const motion = deck.dataset.motion;
    if (motion === 'static' || reduced.matches || reading) return;
    const items = Array.from(slide.querySelectorAll(ITEMS)).filter(e => !e.closest('.pc-notes'));
    const stats = motion === 'complex' ? Array.from(slide.querySelectorAll('.pc-stat')).map(e => [e, countable(e)]).filter(p => p[1]) : [];
    // Complex motion builds a cover on its own: the title converges, then its kicker, subtitle and meta rise in
    const cover = motion === 'complex' && slide.classList.contains('pc-cover') ? slide.querySelector(':scope > .pc-title:not([data-build])') : null;
    const autos = cover ? Array.from(slide.querySelectorAll(':scope > :is(.pc-kicker, .pc-sub, .pc-lead, .pc-meta):not([data-build])')) : [];
    const conv = items.filter(e => e.dataset.build === 'converge').concat(cover ? [cover] : []);
    if (!items.length && !stats.length && !conv.length) return;
    const stagger = ms(deck, '--stagger') || 60, dur = ms(deck, '--dur') || 400, draw = ms(deck, '--dur-draw') || 700;
    items.forEach((e, k) => e.style.setProperty('--i', k));
    conv.forEach(splitWords);
    const after = items.length + Math.ceil(dur * 1.2 / stagger);
    autos.forEach((e, k) => { e.style.setProperty('--i', after + k); e.classList.add('pc-auto'); });
    const moving = items.concat(cover ? [cover] : [], autos);
    slide.classList.add('pc-snap', 'is-building');
    moving.forEach(e => e.classList.add('pc-pre'));
    void slide.offsetWidth;
    slide.classList.remove('pc-snap');
    void slide.offsetWidth;
    moving.forEach(e => e.classList.remove('pc-pre'));
    let maxK = 0;
    slide.querySelectorAll('[data-build="draw"] [style*="--k"]').forEach(e => { maxK = Math.max(maxK, parseFloat(e.style.getPropertyValue('--k')) || 0); });
    stats.forEach(([e, m]) => {
      const host = e.closest(ITEMS);
      countUp(e, m, host ? (parseFloat(host.style.getPropertyValue('--i')) || 0) * stagger + dur * .3 : 0);
    });
    const words = conv.reduce((n, e) => Math.max(n, e.querySelectorAll('.pc-w').length), 0);
    const last = Math.max(items.length + maxK, autos.length ? after + autos.length : 0);
    buildTimer = setTimeout(endBuild, last * stagger + Math.max(dur * 1.4, draw + dur * 1.6, conv.length ? 150 + words * 15 + dur * 2.4 : 0) + 1300);
  }

  /* ---------- interface ---------- */
  const pageStyle = doc.getElementById('pc-page') || el('style');
  if (!pageStyle.id) { pageStyle.id = 'pc-page'; (doc.head || doc.documentElement).appendChild(pageStyle); }
  const ui = el('div', 'pc-ui');
  ui.setAttribute('role', 'toolbar'); ui.setAttribute('aria-label', 'Slide controls');
  const count = el('span', 'pc-ui-count');
  count.setAttribute('aria-live', 'polite');
  const menu = el('div', 'pc-menu'); menu.hidden = true; menu.id = 'pc-download-menu';
  const notesPanel = el('div', 'pc-notes-panel'); notesPanel.hidden = true; notesPanel.setAttribute('aria-label', 'Speaker notes');
  const laser = el('div', 'pc-laser');
  const blackout = el('div', 'pc-blackout');
  const progressBar = el('div', 'pc-progress');
  const overview = el('div', 'pc-overview'); overview.hidden = true; overview.setAttribute('aria-label', 'All slides');
  const toastEl = el('div', 'pc-toast'); toastEl.hidden = true; toastEl.setAttribute('role', 'status');
  const tip = el('div', 'pc-tip'); tip.hidden = true; tip.setAttribute('role', 'dialog'); tip.setAttribute('aria-label', 'Keyboard shortcuts');
  tip.innerHTML = '<h2>Keyboard shortcuts</h2><dl>' + [
    ['<kbd>→</kbd> <kbd>Space</kbd>', 'Next slide'], ['<kbd>←</kbd>', 'Previous slide'], ['<kbd>Home</kbd> <kbd>End</kbd>', 'First or last slide'],
    ['Number, <kbd>Enter</kbd>', 'Go to that slide'], ['<kbd>P</kbd>', 'Presenter view in a new window'], ['<kbd>O</kbd>', 'All slides'],
    ['<kbd>N</kbd>', 'Speaker notes'], ['<kbd>R</kbd>', 'Reading view'], ['<kbd>F</kbd>', 'Full screen'], ['<kbd>L</kbd>', 'Laser pointer'],
    ['<kbd>B</kbd> <kbd>W</kbd>', 'Black or white screen'], ['<kbd>Esc</kbd>', 'Close']
  ].map(r => '<dt>' + r[0] + '</dt><dd>' + r[1] + '</dd>').join('') + '</dl>';
  const btn = (label, title, fn, wide, aria) => {
    const b = el('button', '', label); b.type = 'button'; b.title = title;
    if (aria) b.setAttribute('aria-label', aria);
    if (wide) b.dataset.wide = '';
    b.addEventListener('click', ev => { ev.stopPropagation(); fn(); });
    ui.appendChild(b); return b;
  };
  btn('‹', 'Previous slide', () => prev(), false, 'Previous slide');
  ui.appendChild(count);
  btn('›', 'Next slide', () => next(), false, 'Next slide');
  btn('Notes', 'Speaker notes (N)', () => toggleNotes(), true);
  btn('Slides', 'All slides (O)', () => toggleOverview(), true);
  btn('Present', 'Presenter view in a new window (P)', () => openPresenter(), true);
  const readBtn = btn('Read', 'Reading view: every slide in one scrolling page (R)', () => setReading(!reading));
  const dlBtn = btn('Download', 'Download the slides', () => toggleMenu());
  dlBtn.setAttribute('aria-haspopup', 'true'); dlBtn.setAttribute('aria-controls', menu.id); dlBtn.setAttribute('aria-expanded', 'false');
  btn('?', 'Keyboard shortcuts (?)', () => toggleTip(), true, 'Keyboard shortcuts');
  if (!isDoc) deck.append(progressBar, ui, menu, notesPanel, laser, blackout, overview, toastEl, tip);

  let toastTimer = 0;
  function toast(msg, dur) {
    toastEl.textContent = msg; toastEl.hidden = false;
    clearTimeout(toastTimer); toastTimer = setTimeout(() => { toastEl.hidden = true; }, dur || 7000);
  }

  /* ---------- downloads ---------- */
  const stored = { pdf: doc.getElementById('pc-pdf'), pptx: doc.getElementById('pc-pptx') };
  const FORMAT = { '16x9': '16:9', '4x3': '4:3', '1x1': 'square', '4x5': '4:5 portrait', '9x16': '9:16 portrait', a4p: 'A4 portrait', a4l: 'A4 landscape',
    '191x100': 'link preview', '3x1': '3:1 banner', '4x1': '4:1 banner', '5x7': '5 x 7 in', 'letter-p': 'US Letter', card: 'business card' };
  const complexNote = () => (deck.dataset.motion === 'complex' ? ' Check it before presenting or sharing: the animations do not carry over.' : '');
  function buildMenu() {
    const complex = deck.dataset.motion === 'complex';
    menu.innerHTML = '';
    if (complex) menu.appendChild(el('div', 'pc-menu-warn', '<b>Not well optimised for static viewing</b><br>This deck uses complex animations of content, which a PDF or PowerPoint cannot show. Check the downloaded file before presenting or sharing it.'));
    const item = (label, small, fn) => {
      const b = el('button', '', esc(label) + '<small>' + esc(small) + '</small>'); b.type = 'button';
      b.addEventListener('click', ev => { ev.stopPropagation(); closeMenu(); fn(); });
      menu.appendChild(b);
    };
    if (stored.pdf) item('PDF', complex ? 'Each slide as it prints, without its animations' : 'The slides exactly as they look, for reading and printing', exportPdf);
    else item('PDF', 'Opens the print window: choose Save as PDF', exportPdf);
    if (stored.pptx) item('PowerPoint', complex ? 'Editable, without the HTML animations' : 'Editable. Opens in PowerPoint and Google Slides', exportPptx);
  }
  function toggleMenu(open) {
    open = open == null ? menu.hidden : open;
    if (open) buildMenu();
    menu.hidden = !open; dlBtn.setAttribute('aria-expanded', String(open));
    if (open) { const b = menu.querySelector('button'); if (b) b.focus(); }
  }
  const closeMenu = () => toggleMenu(false);
  function fileName(ext) {
    return (deckTitle() || 'Slides').replace(/[\\/:*?"<>|]+/g, ' ').replace(/\s+/g, ' ').trim().slice(0, 120) + ext;
  }
  function saveStored(node, type, ext, msg) {
    try {
      const bin = atob(node.textContent.replace(/\s+/g, ''));
      const bytes = new Uint8Array(bin.length);
      for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
      const url = URL.createObjectURL(new Blob([bytes], { type }));
      const a = el('a'); a.href = url; a.download = node.dataset.name || fileName(ext);
      doc.body.appendChild(a); a.click(); a.remove();
      setTimeout(() => URL.revokeObjectURL(url), 60000);
      toast(msg + complexNote());
    } catch (err) { toast('The download did not start (' + err.message + '). Try again, or use another browser.'); }
  }
  function prepareForPrint() {
    endBuild(); closeOverlays();
    slides.forEach(s => s.querySelectorAll('figure.pc-chart').forEach(f => { if (!f.querySelector(':scope > svg')) drawChart(f); }));
  }
  function exportPdf() {
    if (stored.pdf) return saveStored(stored.pdf, 'application/pdf', '.pdf', 'PDF saved to your downloads, one page per slide.');
    if (paperPrint) return toast('This browser prints on its own paper size, which cuts the slides off. Open this file in Chrome, Edge or Firefox to save the PDF.', 10000);
    toast('In the print window choose "Save as PDF". Each slide prints on its own ' + (FORMAT[deck.dataset.format] || '16:9') + ' page.' + complexNote(), 10000);
    prepareForPrint();
    setTimeout(() => win.print(), 60);
  }
  function exportPptx() {
    if (stored.pptx) return saveStored(stored.pptx, 'application/vnd.openxmlformats-officedocument.presentationml.presentation', '.pptx', 'PowerPoint saved to your downloads. It opens in PowerPoint and Google Slides.');
    toast('This copy has no PowerPoint file inside it. Ask for the published version of the deck.');
  }

  /* ---------- notes, laser, blackout, tips ---------- */
  const notesOf = i => { const n = slides[i].querySelector('.pc-notes'); return n && n.innerHTML.trim() ? n.innerHTML : '<p>No notes for this slide.</p>'; };
  function toggleNotes(open) {
    notesOpen = open == null ? !notesOpen : open;
    notesPanel.hidden = !notesOpen; deck.classList.toggle('is-notes', notesOpen);
    if (notesOpen) notesPanel.innerHTML = notesOf(cur);
    fit();
  }
  function toggleLaser(on) { deck.classList.toggle('is-laser', on == null ? !deck.classList.contains('is-laser') : on); }
  deck.addEventListener('mousemove', e => { if (deck.classList.contains('is-laser')) { laser.style.left = e.clientX + 'px'; laser.style.top = e.clientY + 'px'; } });
  function setBlackout(kind) {
    const on = !!kind && !(deck.classList.contains('is-blackout') && blackout.classList.contains('is-white') === (kind === 'white'));
    deck.classList.toggle('is-blackout', on); blackout.classList.toggle('is-white', on && kind === 'white');
    renderPresenter();
  }
  function toggleTip(open) { tip.hidden = !(open == null ? tip.hidden : open); }
  function closeOverlays() {
    toggleMenu(false); toggleTip(false); toggleLaser(false);
    if (!overview.hidden) toggleOverview(false);
    if (deck.classList.contains('is-blackout')) setBlackout(null);
  }

  /* ---------- overview ---------- */
  function cleanClone(c) {
    c.classList.remove('is-active', 'is-building', 'pc-snap');
    c.removeAttribute('id');
    c.querySelectorAll('[id]').forEach(e => e.removeAttribute('id'));
    c.querySelectorAll('.pc-pre').forEach(e => e.classList.remove('pc-pre'));
    c.querySelectorAll('.pc-counting').forEach(e => { e.classList.remove('pc-counting'); e.removeAttribute('data-pc-now'); });
    c.setAttribute('aria-hidden', 'true'); c.inert = true;
    return c;
  }
  function sizeThumbs() {
    const b = overview.querySelector('button');
    if (!b) return;
    const ts = b.clientWidth / W;
    overview.style.setProperty('--ts', ts);
    overview.querySelectorAll('.pc-thumb').forEach(t => { t.style.height = f1(H * ts) + 'px'; });
  }
  function toggleOverview(open) {
    open = open == null ? overview.hidden : open;
    if (open) {
      endBuild();
      overview.innerHTML = '';
      slides.forEach((s, i) => {
        const b = el('button'); b.type = 'button';
        b.setAttribute('aria-label', 'Slide ' + (i + 1) + ': ' + slideTitle(s, i));
        if (i === cur) { b.classList.add('is-current'); b.setAttribute('aria-current', 'true'); }
        const th = el('div', 'pc-thumb'); th.appendChild(cleanClone(s.cloneNode(true)));
        const lab = el('span'); lab.textContent = String(i + 1);
        b.append(th, lab);
        b.addEventListener('click', ev => { ev.stopPropagation(); toggleOverview(false); show(i); });
        overview.appendChild(b);
      });
      overview.hidden = false;
      sizeThumbs();
      const here = overview.children[cur];
      if (here) { here.focus(); here.scrollIntoView({ block: 'center' }); }
    } else {
      overview.hidden = true; overview.innerHTML = '';
      deck.focus({ preventScroll: true });
    }
  }
  function overviewKey(e) {
    const btns = Array.from(overview.children), at = btns.indexOf(doc.activeElement);
    const cols = Math.max(1, btns.filter(b => b.offsetTop === btns[0].offsetTop).length);
    const go = i => { const b = btns[Math.max(0, Math.min(btns.length - 1, i))]; if (b) { b.focus(); b.scrollIntoView({ block: 'nearest' }); } };
    const k = e.key;
    if (k === 'Escape' || k === 'o' || k === 'O') toggleOverview(false);
    else if (k === 'ArrowRight') go(at + 1);
    else if (k === 'ArrowLeft') go(at - 1);
    else if (k === 'ArrowDown') go(at + cols);
    else if (k === 'ArrowUp') go(at - cols);
    else if (k === 'Home') go(0);
    else if (k === 'End') go(btns.length - 1);
    else return;
    e.preventDefault();
  }

  /* ---------- reading view ---------- */
  let observer = null;
  function setReading(on) {
    reading = !!on;
    endBuild(); closeOverlays();
    deck.classList.toggle('is-reading', reading);
    readBtn.textContent = reading ? 'Slides' : 'Read';
    readBtn.title = reading ? 'Back to one slide at a time (R)' : 'Reading view: every slide in one scrolling page (R)';
    fit();
    if (reading) {
      if (!observer && 'IntersectionObserver' in win) {
        observer = new IntersectionObserver(entries => {
          if (!reading) return;
          entries.forEach(en => { if (en.isIntersecting) { const i = slides.indexOf(en.target); if (i >= 0 && i !== cur) mark(i); } });
        }, { root: deck, threshold: .55 });
        slides.forEach(s => observer.observe(s));
      }
      slides[cur].scrollIntoView({ block: 'start' });
      deck.focus({ preventScroll: true });
    } else {
      deck.scrollTop = 0;
      show(cur, { force: true, quiet: true });
    }
  }

  /* ---------- navigation ---------- */
  function mark(i) {
    cur = i;
    count.textContent = (i + 1) + ' / ' + N;
    deck.style.setProperty('--p', N > 1 ? i / (N - 1) : 1);
    progressBar.style.setProperty('--p', N > 1 ? i / (N - 1) : 1);
    if (notesOpen) notesPanel.innerHTML = notesOf(i);
    try { history.replaceState(null, '', '#' + (i + 1)); } catch (e) { /* file:// in some browsers */ }
    renderPresenter();
    deck.dispatchEvent(new CustomEvent('pc:slide', { detail: { index: i, slide: slides[i] }, bubbles: true }));
  }
  function show(i, opts) {
    opts = opts || {};
    i = Math.max(0, Math.min(N - 1, i | 0));
    if (reading) { slides[i].scrollIntoView({ block: 'start', behavior: reduced.matches ? 'auto' : 'smooth' }); mark(i); return; }
    if (i === cur && !opts.force) return;
    const prevI = cur;
    slides.forEach((s, k) => s.classList.toggle('is-active', k === i));
    mark(i);
    if (!opts.quiet && (prevI < 0 || i > prevI)) build(slides[i]); else endBuild();
  }
  const next = () => show(cur + 1);
  const prev = () => show(cur - 1);

  let digits = '', digitTimer = 0;
  function onKey(e) {
    if (e.defaultPrevented || e.metaKey || e.ctrlKey || e.altKey) return;
    const t = e.target;
    if (t && (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName))) return;
    if (!overview.hidden) return overviewKey(e);
    const k = e.key;
    if (deck.classList.contains('is-blackout') && !/^(Shift|Meta|Control|Alt)$/.test(k)) { setBlackout(null); e.preventDefault(); return; }
    if (/^\d$/.test(k)) { digits += k; clearTimeout(digitTimer); digitTimer = setTimeout(() => { digits = ''; }, 1500); e.preventDefault(); return; }
    if (k === 'Enter' && digits) { show(parseInt(digits, 10) - 1); digits = ''; e.preventDefault(); return; }
    if (reading && /^(ArrowRight|ArrowLeft|ArrowDown|ArrowUp|PageDown|PageUp| |Spacebar)$/.test(k)) return;
    switch (k) {
      case 'ArrowRight': case 'ArrowDown': case 'PageDown': case ' ': case 'Spacebar':
        if (e.shiftKey && (k === ' ' || k === 'Spacebar')) prev(); else next(); break;
      case 'ArrowLeft': case 'ArrowUp': case 'PageUp': prev(); break;
      case 'Home': show(0); break;
      case 'End': show(N - 1); break;
      case 'p': case 'P': openPresenter(); break;
      case 'o': case 'O': if (!reading) toggleOverview(true); break;
      case 'n': case 'N': toggleNotes(); break;
      case 'l': case 'L': toggleLaser(); break;
      case 'b': case 'B': case '.': setBlackout('black'); break;
      case 'w': case 'W': case ',': setBlackout('white'); break;
      case 'r': case 'R': setReading(!reading); break;
      case 'f': case 'F': fullscreen(); break;
      case '?': toggleTip(); break;
      case 'Escape':
        if (!menu.hidden || !tip.hidden || deck.classList.contains('is-laser')) closeOverlays();
        else if (notesOpen) toggleNotes(false);
        else return;
        break;
      default: return;
    }
    e.preventDefault();
  }
  function fullscreen() {
    try {
      if (doc.fullscreenElement) doc.exitFullscreen();
      else if (doc.documentElement.requestFullscreen) doc.documentElement.requestFullscreen();
    } catch (e) { /* not allowed here */ }
  }
  if (!isDoc) {
    doc.addEventListener('keydown', onKey);
    doc.addEventListener('click', e => { if (!menu.hidden && !menu.contains(e.target)) closeMenu(); });
    let tx = null, ty = 0, uiTimer = 0;
    deck.addEventListener('touchstart', e => {
      if (e.touches.length === 1) { tx = e.touches[0].clientX; ty = e.touches[0].clientY; } else tx = null;
      ui.classList.add('is-shown'); clearTimeout(uiTimer); uiTimer = setTimeout(() => ui.classList.remove('is-shown'), 3500);
    }, { passive: true });
    deck.addEventListener('touchend', e => {
      if (tx == null || reading || !overview.hidden) return;
      const dx = e.changedTouches[0].clientX - tx, dy = e.changedTouches[0].clientY - ty;
      tx = null;
      if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.5) { if (dx < 0) next(); else prev(); }
    }, { passive: true });
  }

  /* ---------- presenter window ---------- */
  let pres = null, pv = null;
  const PV_CSS = 'html,body{margin:0;height:100%;background:#111317;color:#e9ebef;font:15px/1.45 system-ui,sans-serif}' +
    '.pv{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(0,1fr);grid-template-rows:auto minmax(0,1fr) auto;gap:14px;height:100%;padding:14px 16px;box-sizing:border-box}' +
    '.pv-bar,.pv-nav{grid-column:1/-1;display:flex;align-items:center;gap:12px;flex-wrap:wrap}.pv-sp{flex:1}' +
    '.pv-time{font:600 30px/1 system-ui,sans-serif;font-variant-numeric:tabular-nums}.pv-clock{color:#aab0bb;font-variant-numeric:tabular-nums}' +
    '.pv-count{font-weight:600}.pv-state{padding:3px 10px;border-radius:99px;background:#5a1d1d;color:#ffd6d6}.pv-state:empty{display:none}' +
    '.pv button{all:unset;cursor:pointer;padding:7px 12px;border-radius:8px;background:#22262e;color:#f1f2f4}.pv button:hover,.pv button:focus-visible{background:#2f3540}' +
    '.pv-cur,.pv-next{position:relative;min-height:0;display:flex;align-items:flex-start;justify-content:center}' +
    '.pv-side{display:flex;flex-direction:column;gap:8px;min-height:0}.pv-next{flex:0 0 auto;justify-content:flex-start}.pv-label{color:#8d94a0;font-size:12px;letter-spacing:.08em;text-transform:uppercase}' +
    '.pv-notes{flex:1;min-height:0;overflow:auto;padding:14px 18px;border-radius:10px;background:#1a1d23;font-size:var(--pv-fs,22px);line-height:1.5}.pv-notes p{margin:0 0 .7em}' +
    '.pv-frame{position:relative;overflow:hidden;border-radius:6px;background:#000;box-shadow:0 0 0 1px #2a2e36;flex:none}' +
    '.pv-frame>.pc-deck{position:absolute;inset:0;overflow:hidden;background:transparent}' +
    '.pv-frame .pc-slide{left:0;top:0;transform:scale(var(--ts));transform-origin:0 0;visibility:visible}' +
    '.pv-end{display:grid;place-items:center;color:#8d94a0;background:#1a1d23}';
  function openPresenter() {
    if (pres && !pres.closed) { pres.focus(); return; }
    pres = win.open('', 'pc-presenter', 'width=1280,height=800');
    if (!pres) { toast('The browser blocked the presenter window. Allow pop-ups for this file, then press P again.', 9000); return; }
    const pd = pres.document;
    pd.open();
    pd.write('<!doctype html><html lang="en"><head><meta charset="utf-8"><title></title></head><body></body></html>');
    pd.close();
    pd.title = 'Presenter: ' + (deckTitle() || 'Slides');
    const base = pd.createElement('base'); base.href = location.href; pd.head.appendChild(base);
    doc.querySelectorAll('style, link[rel="stylesheet"]').forEach(n => pd.head.appendChild(pd.importNode(n, true)));
    const st = pd.createElement('style'); st.textContent = PV_CSS; pd.head.appendChild(st);
    pd.body.innerHTML = '<div class="pv"><header class="pv-bar"><span class="pv-count"></span><span class="pv-state"></span><span class="pv-sp"></span>' +
      '<span class="pv-time" aria-label="Time since the presenter view opened">00:00</span><button type="button" data-act="pause">Pause</button><button type="button" data-act="reset">Reset</button>' +
      '<span class="pv-clock"></span></header><section class="pv-cur" aria-label="Current slide"></section><aside class="pv-side"><div class="pv-label">Next</div>' +
      '<div class="pv-next"></div><div class="pv-label">Notes</div><div class="pv-notes" aria-live="polite"></div></aside>' +
      '<footer class="pv-nav"><button type="button" data-act="prev">‹ Previous</button><button type="button" data-act="next">Next ›</button><span class="pv-sp"></span>' +
      '<button type="button" data-act="smaller" aria-label="Smaller notes">A−</button><button type="button" data-act="bigger" aria-label="Bigger notes">A+</button>' +
      '<button type="button" data-act="black">Black screen</button></footer></div>';
    pv = { t0: Date.now(), paused: 0, pausedAt: 0, fs: 22, q: s => pd.querySelector(s) };
    pd.addEventListener('keydown', onKey);
    pd.addEventListener('click', e => {
      const a = e.target.closest && e.target.closest('[data-act]');
      if (!a) return;
      const act = a.dataset.act;
      if (act === 'prev') prev();
      else if (act === 'next') next();
      else if (act === 'black') setBlackout('black');
      else if (act === 'reset') { pv.t0 = Date.now(); pv.paused = 0; if (pv.pausedAt) pv.pausedAt = Date.now(); }
      else if (act === 'pause') {
        if (pv.pausedAt) { pv.paused += Date.now() - pv.pausedAt; pv.pausedAt = 0; a.textContent = 'Pause'; }
        else { pv.pausedAt = Date.now(); a.textContent = 'Resume'; }
      } else if (act === 'smaller' || act === 'bigger') {
        pv.fs = Math.max(14, Math.min(40, pv.fs + (act === 'bigger' ? 2 : -2)));
        pv.q('.pv-notes').style.setProperty('--pv-fs', pv.fs + 'px');
      }
    });
    pres.addEventListener('resize', renderPresenter);
    const tick = () => {
      if (!pres || pres.closed) return;
      const s = Math.floor(((pv.pausedAt || Date.now()) - pv.t0 - pv.paused) / 1000);
      const hh = Math.floor(s / 3600), mm = Math.floor(s / 60) % 60, ss = s % 60;
      pv.q('.pv-time').textContent = (hh ? hh + ':' + String(mm).padStart(2, '0') : String(mm).padStart(2, '0')) + ':' + String(ss).padStart(2, '0');
      pv.q('.pv-clock').textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };
    pres.setInterval(tick, 500); tick();
    renderPresenter();
  }
  function frameFor(host, i, maxW, maxH) {
    const pd = pres.document;
    host.innerHTML = '';
    const ts = Math.max(.05, Math.min(maxW / W, maxH / H));
    const fr = pd.createElement('div'); fr.className = 'pv-frame';
    fr.style.width = f1(W * ts) + 'px'; fr.style.height = f1(H * ts) + 'px';
    if (i >= N) { fr.classList.add('pv-end'); fr.textContent = 'End of the deck'; host.appendChild(fr); return; }
    const dk = pd.createElement('div'); dk.className = 'pc-deck';
    ['theme', 'palette', 'mode', 'format'].forEach(a => { if (deck.dataset[a]) dk.dataset[a] = deck.dataset[a]; });
    dk.dataset.motion = 'static';
    dk.style.setProperty('--ts', ts);
    dk.appendChild(pd.importNode(cleanClone(slides[i].cloneNode(true)), true));
    fr.appendChild(dk); host.appendChild(fr);
  }
  function renderPresenter() {
    if (!pres || pres.closed || !pv || cur < 0) return;
    const q = pv.q, curHost = q('.pv-cur'), nextHost = q('.pv-next'), side = q('.pv-side');
    if (!curHost) return;
    frameFor(curHost, cur, curHost.clientWidth, curHost.clientHeight);
    frameFor(nextHost, cur + 1, side.clientWidth, side.clientHeight * .42);
    q('.pv-notes').innerHTML = notesOf(cur);
    q('.pv-count').textContent = 'Slide ' + (cur + 1) + ' of ' + N;
    q('.pv-state').textContent = deck.classList.contains('is-blackout') ? (blackout.classList.contains('is-white') ? 'White screen' : 'Black screen') : '';
  }
  win.addEventListener('pagehide', () => { if (pres && !pres.closed) pres.close(); });

  /* ---------- theme, palette, mode, format and motion switching ---------- */
  function set(opts) {
    opts = opts || {};
    ['theme', 'palette', 'mode', 'format', 'motion'].forEach(k => {
      if (!(k in opts)) return;
      if (opts[k] == null || opts[k] === '') delete deck.dataset[k]; else deck.dataset[k] = opts[k];
    });
    if (!deck.dataset.motion) deck.dataset.motion = 'basic';
    endBuild(); fit(); drawAll(); renderPresenter();
    if (doc.fonts && doc.fonts.ready) doc.fonts.ready.then(() => { fit(); drawAll(); renderPresenter(); });
  }

  /* ---------- documents: notes, heading numbers, contents, page numbers, then the shared drawing ---------- */
  function docInit() {
    /* titles keep hyphenated words whole; a table of 15 rows or fewer moves whole to the next page rather than leave a
       row or two behind; a paper (white paper or brief) runs its chapters on without page breaks unless data-break="page" */
    doc.querySelectorAll('.pc-cover h1, .pc-chapter :is(h1, h2, h3), .pc-pull, .pc-masthead h1').forEach(keepHyphens);
    doc.querySelectorAll('table').forEach(t => t.classList.toggle('pc-keep', t.querySelectorAll('tbody tr').length <= 15));
    /* a page break marker that lands just past a full page would leave a blank page, so the break moves on to the
       element that follows it (the next chapter when the marker ends one) */
    doc.querySelectorAll('.pc-pagebreak').forEach(pb => {
      let p = pb, n = pb.nextElementSibling;
      while (!n && p.parentElement && p.parentElement !== doc.body) { p = p.parentElement; n = p.nextElementSibling; }
      if (n && n.tagName !== 'SCRIPT') n.style.breakBefore = 'page';
      pb.hidden = true;
    });
    if (['paper', 'programme', 'agenda'].includes(deck.dataset.type) && !deck.dataset.break) deck.dataset.break = 'none';
    const used = new Set(Array.from(doc.querySelectorAll('[id]'), e => e.id));
    const slug = t => t.toLowerCase().normalize('NFKD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 40) || 'part';
    const idFor = h => {
      if (!h.id) { const b = slug(h.dataset.toc || h.textContent); let id = b, k = 2; while (used.has(id)) id = b + '-' + k++; used.add(id); h.id = id; }
      return h.id;
    };
    /* notes: <span class="pc-fn">text</span> where the reference goes; data-notes="side" puts them beside the text,
       "foot" at the foot of the page (Paged.js lays those out: tools/doc_pdf.py loads it for such documents) */
    const fns = Array.from(doc.querySelectorAll('.pc-fn'));
    if (fns.length) {
      const side = deck.dataset.notes === 'side', foot = deck.dataset.notes === 'foot';
      let list = null;
      if (!side && !foot) {
        let box = doc.querySelector('.pc-endnotes');
        if (!box) {
          box = el('section', 'pc-chapter pc-endnotes', '<h1>' + esc(deck.dataset.notesTitle || 'Notes') + '</h1>');
          box.dataset.unnumbered = '';
          const before = doc.querySelector('.pc-chapter.pc-appendix, .pc-back');
          before ? before.parentNode.insertBefore(box, before) : (doc.querySelector('main') || doc.body).appendChild(box);
        }
        list = box.querySelector('ol') || box.appendChild(el('ol'));
      }
      fns.forEach((fn, i) => {
        if (foot) {   // Paged.js numbers the calls; the note numbers are written here (its marker counter repeats on a page)
          fn.classList.add('pc-footnote');
          return fn.insertAdjacentHTML('afterbegin', '<b class="pc-fn-n">' + (i + 1) + '.</b> ');
        }
        const k = i + 1, ref = el('sup', 'pc-fnref');
        fn.parentNode.insertBefore(ref, fn);
        if (side) {
          ref.textContent = k;
          fn.classList.add('pc-sidenote');
          fn.insertAdjacentHTML('afterbegin', '<b class="pc-fn-n">' + k + '</b>');
        } else {
          ref.id = 'fnref-' + k; ref.innerHTML = '<a href="#fn-' + k + '">' + k + '</a>';
          const li = el('li', null, fn.innerHTML); li.id = 'fn-' + k; list.appendChild(li); fn.remove();
        }
      });
    }
    /* heading numbers into data-n; the contents entries on the way */
    const numbered = deck.hasAttribute('data-numbered');
    const entries = [];
    let n1 = 0, app = 0;
    doc.querySelectorAll('.pc-chapter').forEach(ch => {
      const h1 = ch.querySelector('h1');
      if (!h1) return;
      const isApp = ch.classList.contains('pc-appendix');
      const n = isApp ? String.fromCharCode(65 + app++) : numbered && !ch.hasAttribute('data-unnumbered') ? String(++n1) : '';
      if (n) {
        h1.dataset.n = isApp ? 'Appendix ' + n : n;
        const on = ch.querySelector('.pc-opener-num');
        if (on && !on.textContent.trim()) on.textContent = isApp ? n : n.padStart(2, '0');
      }
      if (!ch.hasAttribute('data-notoc')) entries.push({ h: h1, lvl: 1, n: isApp ? (n ? 'Appendix ' + n : '') : n });
      let n2 = 0, n3 = 0;
      ch.querySelectorAll('h2, h3').forEach(h => {
        if (h.closest('.pc-toc, .pc-callout, .pc-sidebar, .pc-card, figure, .pc-cover, .pc-keyfigs')) return;
        if (h.tagName === 'H2') { n2++; n3 = 0; } else n3++;
        const hn = n && !h.hasAttribute('data-unnumbered') ? n + '.' + n2 + (h.tagName === 'H3' ? '.' + n3 : '') : '';
        if (hn) h.dataset.n = hn;
        if (h.tagName === 'H2' && !ch.hasAttribute('data-notoc')) entries.push({ h, lvl: 2, n: hn });
      });
    });
    /* pages: data-page (a4, a5, letter, legal or "150x210" in mm), data-orient="landscape", data-margins="top right bottom left"
       in mm; each chapter gets a named page whose running head carries its title (Chrome has no string-set) */
    const SIZES = { a4: [210, 297], a5: [148, 210], a3: [297, 420], letter: [215.9, 279.4], legal: [215.9, 355.6] };
    const MARGINS = { letter: '22 22 22 22', memo: '22 22 22 22', cv: '14 14 14 14', invoice: '18 18 18 18', onepager: '14 15 14 15',
      newsletter: '14 14 16 14', certificate: '0 0 0 0', agenda: '20 20 20 20', programme: '14 15 14 15' };
    const type = deck.dataset.type || 'report';
    const pg = (deck.dataset.page || 'a4').toLowerCase();
    let [pw, ph] = SIZES[pg] || (pg.match(/^(\d+(?:\.\d+)?)x(\d+(?:\.\d+)?)$/) || [0, 210, 297]).slice(1).map(Number);
    if (deck.dataset.orient === 'landscape') [pw, ph] = [ph, pw];
    /* bleed (mm on each side) for a press file: the page grows by it and so do the margins, so the text keeps its place
       while covers and full pages run on to the edge; the PDF step sets window.PC_BLEED for its print pass */
    const bleed = Math.max(0, +(win.PC_BLEED || deck.dataset.bleed || 0) || 0);
    pw += 2 * bleed; ph += 2 * bleed;
    const [mt, mr, mb, ml] = (deck.dataset.margins || MARGINS[type] || '24 20 22 20').trim().split(/\s+/).map(v => +v + bleed);
    const cssStr = s => '"' + String(s).replace(/\\/g, '\\\\').replace(/"/g, '\\"').replace(/\s+/g, ' ').trim() + '"';
    const heads = deck.dataset.head !== 'none' && !MARGINS[type];
    const shortTitle = deck.dataset.shortTitle || deck.dataset.title || doc.title || '';
    let rules = '@page { size: ' + pw + 'mm ' + ph + 'mm; margin: ' + mt + 'mm ' + mr + 'mm ' + mb + 'mm ' + ml + 'mm; }\n' +
      ':root { --bleed: ' + bleed + 'mm; --page-w: ' + pw + 'mm; --page-h: ' + ph + 'mm; --m-t: ' + mt + 'mm; --m-r: ' + mr + 'mm; --m-b: ' + mb + 'mm; --m-l: ' + ml + 'mm;' +
      (heads ? ' --doc-title-head: ' + cssStr(shortTitle) + ';' : ' --doc-title-head: "";') + ' }\n';
    /* a named page always starts a new page, so chapters that run on (data-break="none") share the running head of the
       chapter that opened their page; a whole document that runs on has the short title alone */
    const flowAll = deck.dataset.break === 'none';
    if (heads && !flowAll) doc.querySelectorAll('.pc-chapter').forEach((ch, i) => {
      const h1 = ch.querySelector('h1');
      if (!h1) return;
      const prev = ch.previousElementSibling;
      if (ch.dataset.break === 'none' && prev && prev.style.page) { ch.style.page = prev.style.page; return; }
      const n = h1.dataset.n || '', t = (h1.dataset.head || h1.dataset.toc || h1.textContent).trim();
      ch.style.page = 'pc-ch-' + (i + 1);
      rules += '@page pc-ch-' + (i + 1) + ' { @top-left { content: ' + cssStr((n ? n + (/^Appendix/.test(n) ? ': ' : ' ') : '') + t) + ' } }\n';
    });
    /* Chrome gives the first page the default page whatever the first element asks for, so a cover that opens the document
       gets its full-bleed page through :first */
    const first = doc.body && doc.body.firstElementChild;
    if (first && first.matches('.pc-cover, .pc-fullpage'))
      rules += '@page :first { margin: 0; @top-left { content: none } @top-right { content: none } @bottom-right { content: none } }\n';
    if (type === 'onepager' || type === 'certificate') rules += '@page { @bottom-right { content: none } }\n';
    if (/^(letter|memo|cv|invoice)$/.test(type)) rules += '@page { @bottom-right { content: "Page " counter(page) " of " counter(pages) } }\n@page :first { @bottom-right { content: none } }\n';
    let pageCss = doc.getElementById('pc-doc-pages');
    if (!pageCss) { pageCss = el('style'); pageCss.id = 'pc-doc-pages'; (doc.head || doc.documentElement).appendChild(pageCss); }
    pageCss.textContent = rules;
    /* contents: an empty <nav class="pc-toc" data-depth="2"></nav> is filled from the chapters */
    doc.querySelectorAll('.pc-toc').forEach(toc => {
      if (toc.querySelector('ol')) return;
      const depth = +toc.dataset.depth || 2, ol = el('ol');
      entries.filter(e => e.lvl <= depth).forEach(e => {
        const li = el('li', 'pc-toc-' + e.lvl), a = el('a');
        a.href = '#' + idFor(e.h);
        a.innerHTML = (e.n ? '<span class="pc-toc-n">' + esc(e.n) + '</span>' : '') +
          '<span class="pc-toc-t">' + esc((e.h.dataset.toc || e.h.textContent).trim()) + '</span><span class="pc-toc-dots"></span>';
        li.appendChild(a); ol.appendChild(li);
      });
      if (!toc.querySelector('h1, h2, .pc-toc-title')) toc.prepend(el('h2', 'pc-toc-title', esc(toc.dataset.title || 'Contents')));
      toc.appendChild(ol);
    });
    /* page numbers for the contents and cross-references: the PDF step's second pass sets window.PC_PAGES {id: page} */
    const pages = win.PC_PAGES || {};
    doc.querySelectorAll('.pc-toc a[href^="#"], a.pc-ref[href^="#"]').forEach(a => {
      const id = decodeURIComponent(a.getAttribute('href').slice(1));
      if (pages[id] != null) a.dataset.pg = pages[id];
    });
    drawIcons(deck);
    doc.querySelectorAll('pre.pc-code').forEach(highlight);
    /* key figures keep 5% of their cell clear: a row too wide for the column (four figures beside sidenotes, say) gets
       one smaller size for all its figures, down to 55% */
    const fitKeyfigs = () => doc.querySelectorAll('.pc-keyfigs').forEach(row => {
      row.style.removeProperty('--d-stat');
      const st = Array.from(row.querySelectorAll('.pc-stat'));
      if (!st.length) return;
      const ratio = Math.max(...st.map(e => {
        const r = doc.createRange(); r.selectNodeContents(e);
        const cell = (e.parentElement || e).getBoundingClientRect().width;
        return cell ? r.getBoundingClientRect().width / (cell * .95) : 1;
      }));
      if (ratio > 1) row.style.setProperty('--d-stat', parseFloat(getComputedStyle(st[0]).fontSize) * Math.max(.55, 1 / ratio) + 'px');
    });
    const draw = () => {
      fitKeyfigs();
      doc.querySelectorAll('figure.pc-chart').forEach(fig => { try { drawChart(fig); } catch (e) { console.error('Chart not drawn:', e); fig.dataset.error = e.message; } });
      drawMarks(deck);
    };
    draw();
    const faces = () => !doc.fonts ? Promise.resolve() : Promise.all(Array.from(doc.fonts)
      .filter(f => f.status === 'unloaded' && /^U\+0+-10FFFF$/i.test(f.unicodeRange || 'U+0-10FFFF'))
      .map(f => f.load().catch(() => null))).then(() => doc.fonts.ready);
    let rt = 0;
    win.addEventListener('load', () => { drawIcons(deck); draw(); });
    win.addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(draw, 150); });
    win.PCDeck = { document: true, count: 0, redraw: draw, ready: () => faces().then(() => { draw(); return frames(2); }) };
  }

  /* ---------- start ---------- */
  if (isDoc) { docInit(); return; }
  annotate();
  drawIcons(deck);
  deck.querySelectorAll('pre.pc-code').forEach(highlight);
  fit();
  drawAll();
  const startAt = parseInt(location.hash.slice(1), 10);
  show(isNaN(startAt) ? 0 : startAt - 1);
  /* Chrome loads a face only when shown text uses it, so a hidden code slide would print in a fallback font.
     Load every face that covers all of Unicode (the script faces with a unicode-range load when used). */
  const loadFaces = () => !doc.fonts ? Promise.resolve() : Promise.all(Array.from(doc.fonts)
    .filter(f => f.status === 'unloaded' && /^U\+0+-10FFFF$/i.test(f.unicodeRange || 'U+0-10FFFF'))
    .map(f => f.load().catch(() => null))).then(() => doc.fonts.ready);
  loadFaces().then(() => { fit(); drawAll(); });
  win.addEventListener('load', () => { drawIcons(deck); fit(); drawAll(); });
  win.addEventListener('resize', fit);
  win.addEventListener('beforeprint', prepareForPrint);
  /* Embedded in the style picker: the parent page may change the look and the slide, and hears about slide changes */
  if (win.parent !== win) {
    const ok = v => typeof v === 'string' && /^[a-z0-9-]{0,24}$/.test(v);
    win.addEventListener('message', e => {
      const m = e.data;
      if (!m || typeof m !== 'object') return;
      if (m.pc === 'set' && m.opts && typeof m.opts === 'object') {
        const o = {};
        ['palette', 'mode', 'format', 'motion'].forEach(k => { if (k in m.opts && ok(m.opts[k])) o[k] = m.opts[k]; });
        set(o);
      } else if (m.pc === 'show' && Number.isInteger(m.n)) show(Math.max(0, Math.min(N - 1, m.n - 1)));
      else if (m.pc === 'ui') doc.documentElement.classList.toggle('pc-bare', !m.show);   /* the picker has its own controls */
      else if (m.pc === 'title' && typeof m.text === 'string' && m.text.trim()) {   /* the picker shows the user's own title on the cover */
        const h = deck.querySelector(':scope > .pc-slide.pc-cover .pc-title');
        if (h) { h.textContent = m.text.trim().slice(0, 140); fit(); }
      }
    });
    deck.addEventListener('pc:slide', e => win.parent.postMessage({ pc: 'slide', n: e.detail.index + 1, count: N }, '*'));
    win.parent.postMessage({ pc: 'ready', count: N, theme: deck.dataset.theme }, '*');
  }
  win.addEventListener('hashchange', () => { const n = parseInt(location.hash.slice(1), 10); if (!isNaN(n) && n - 1 !== cur) show(n - 1); });
  if (W > H && win.matchMedia('(pointer: coarse) and (max-width: 760px) and (orientation: portrait)').matches) setReading(true);

  win.PCDeck = {
    show: i => show(i), next, prev, count: N, get index() { return cur; }, set, redraw: drawAll,
    exportPdf, exportPptx, prepareForPrint, ready: () => loadFaces().then(() => frames(2))
  };
})();
