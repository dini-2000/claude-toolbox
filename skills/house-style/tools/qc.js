/* QC for House Style decks. tools/qc.py injects it into an isolated copy of a built deck; it never ships.
   It turns motion to static, measures every slide at its stage size (the format's own pixels, short side 1080) and
   writes JSON into pre#pc-qc: per slide the issues found, facts for the summary, and every line of text with its
   colour, which qc.py checks for contrast against the printed page. Checks: icons, content past the slide edge,
   content taller than the body, containers that cut content off, text outside the margins, text over other text,
   chart labels that touch, text spilling out of its box, boxes over boxes, empty parts, pictures (loaded, embedded,
   sharp enough), title length, small text, charts drawn; plus fonts and script errors for the whole deck. */
(function () {
  var out = { slides: [], errors: window.__pcErrs || [], loaded: [], failed: [] };
  function finish() {
    var pre = document.createElement('pre'); pre.id = 'pc-qc'; pre.hidden = true;
    pre.textContent = JSON.stringify(out); document.body.appendChild(pre);
  }
  function txt(el) { return el ? (el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 60) : ''; }
  function cls(el) {
    var c = el.getAttribute && el.getAttribute('class');
    return el.tagName.toLowerCase() + (c ? '.' + c.trim().split(/\s+/).join('.') : '');
  }
  // Any CSS colour (hex, rgb, oklch, color-mix ...) to [r, g, b, a] through a 1 px canvas
  var cv = document.createElement('canvas'); cv.width = cv.height = 1;
  var cx = cv.getContext('2d', { willReadFrequently: true }), memo = {};
  function rgba(css) {
    if (!css || css === 'none' || css === 'transparent') return [0, 0, 0, 0];
    if (memo[css]) return memo[css];
    cx.clearRect(0, 0, 1, 1); cx.fillStyle = 'rgba(0,0,0,0)'; cx.fillStyle = css; cx.fillRect(0, 0, 1, 1);
    var d = cx.getImageData(0, 0, 1, 1).data;
    return (memo[css] = [d[0], d[1], d[2], +(d[3] / 255).toFixed(3)]);
  }
  // The box a run of text belongs to: SVG text is its own block; inline boxes climb to their container
  function blockOf(el) {
    var t = el.closest('svg') && el.closest('text');
    if (t) return t;
    while (el && el.parentElement) {
      var d = getComputedStyle(el).display;
      if (d !== 'inline' && d !== 'contents') return el;
      el = el.parentElement;
    }
    return el;
  }
  function isBox(el, c) {
    if (/^(inline|contents)$/.test(c.display) || el.closest('svg')) return false;
    if (rgba(c.backgroundColor)[3] > 0.05 || c.backgroundImage !== 'none' || c.boxShadow !== 'none') return true;
    return ['Top', 'Right', 'Bottom', 'Left'].some(function (s) {
      return parseFloat(c['border' + s + 'Width']) > 0 && c['border' + s + 'Style'] !== 'none' && rgba(c['border' + s + 'Color'])[3] > 0.05;
    });
  }
  var PLACED = /^(absolute|fixed)$/;
  var TYPE = ['.pc-title', '.pc-kicker', '.pc-sub', '.pc-lead', '.pc-list > li', '.pc-card p', '.pc-stat', '.pc-label', '.pc-chip', '.pc-source', '.pc-table td'];

  function measure() {
    var deck = document.querySelector('.pc-deck');
    var dc = getComputedStyle(deck);
    var W = parseFloat(dc.getPropertyValue('--W')) || 1920, H = parseFloat(dc.getPropertyValue('--H')) || 1080;
    out.W = W; out.H = H;
    out.format = deck.dataset.format || '16x9'; out.theme = deck.dataset.theme || ''; out.palette = deck.dataset.palette || '';
    out.mode = deck.dataset.mode || 'light'; out.motion = deck.dataset.motion || 'basic';
    document.fonts.forEach(function (f) {
      var id = f.family.replace(/^["']|["']$/g, '') + ' ' + f.weight + (f.style === 'italic' ? ' italic' : '');
      if (f.status === 'loaded') out.loaded.push(id); else if (f.status === 'error') out.failed.push(id);
    });
    var slides = [].slice.call(deck.querySelectorAll(':scope > .pc-slide'));
    slides.forEach(function (s, idx) {
      slides.forEach(function (o) { o.style.visibility = o === s ? 'visible' : 'hidden'; });
      var R = s.getBoundingClientRect(), k = R.width / W || 1;
      function rel(r) { return { x: (r.left - R.left) / k, y: (r.top - R.top) / k, r: (r.right - R.left) / k, b: (r.bottom - R.top) / k }; }
      var sc = getComputedStyle(s);
      var pad = { t: parseFloat(sc.paddingTop), r: parseFloat(sc.paddingRight), b: parseFloat(sc.paddingBottom), l: parseFloat(sc.paddingLeft) };
      var res = { n: idx + 1, label: s.dataset.n || String(idx + 1), title: txt(s.querySelector('.pc-title, h1, h2')), issues: [], info: {}, lines: [] };
      var said = {};
      function issue(kind, msg, el) {
        if (said[kind + msg]) return; said[kind + msg] = 1;
        res.issues.push({ kind: kind, msg: msg, text: txt(el) });
      }
      var all = [].slice.call(s.querySelectorAll('*')).filter(function (el) { return !el.closest('.pc-notes'); });
      var css = new Map(); all.forEach(function (el) { css.set(el, getComputedStyle(el)); });
      function shown(el) { var c = css.get(el); return c && c.display !== 'none' && c.visibility !== 'hidden'; }
      function clipped(el) {      // inside a container that cuts its content off (reported by that container)
        for (var p = el.parentElement; p && p !== s; p = p.parentElement) {
          var c = css.get(p); if (c && (c.overflowX !== 'visible' || c.overflowY !== 'visible')) return true;
        }
        return false;
      }

      // 1. Icons draw a Lucide symbol at a real size
      var icons = s.querySelectorAll('.pc-icon');
      res.info.icons = icons.length;
      icons.forEach(function (ic) {
        var name = ic.dataset.icon || '(no name)', svg = ic.querySelector('svg'), b = rel(ic.getBoundingClientRect());
        if (ic.hasAttribute('data-missing') || !svg || !svg.childElementCount) issue('icon', 'icon "' + name + '" draws nothing (not a Lucide name?)', ic.parentElement);
        else if (b.r - b.x < 12 || b.b - b.y < 12) issue('icon', 'icon "' + name + '" is only ' + Math.round(b.r - b.x) + ' px', ic.parentElement);
      });

      // 2. Content past the slide edge is cut off without warning (the theme's art is drawn by pseudo-elements and
      //    may bleed on purpose, so only real elements count; the outermost offender is named once)
      var off = [];
      all.forEach(function (el) {
        if (el.closest('svg') && el.tagName.toLowerCase() !== 'svg') return;
        if (!shown(el) || off.some(function (o) { return o.contains(el); }) || clipped(el)) return;
        var r = el.getBoundingClientRect(); if (r.width < 1 || r.height < 1) return;
        var b = rel(r), past = [];
        if (b.b > H + 1) past.push(Math.round(b.b - H) + ' px past the bottom');
        if (b.r > W + 1) past.push(Math.round(b.r - W) + ' px past the right');
        if (b.x < -1) past.push(Math.round(-b.x) + ' px past the left');
        if (b.y < -1) past.push(Math.round(-b.y) + ' px past the top');
        if (past.length) { off.push(el); issue('off-slide', cls(el) + ' runs ' + past.join(', ') + ' edge', el); }
      });

      // 3. Content taller or wider than the body that holds it
      // Measured from the boxes, not scrollHeight: a font whose ascent and descent outrun a tight line height
      // (Source Serif at 1.1) adds scrollable overflow that draws nothing, and a bottom-aligned body overflows upward,
      // which scrollHeight never counts. Inline text, absolute pieces and anything inside a clipping box are left out.
      s.querySelectorAll('.pc-body').forEach(function (bd) {
        var B = rel(bd.getBoundingClientRect()), lo = B.y, hi = B.b, rx = B.r;
        bd.querySelectorAll('*').forEach(function (e) {
          var c = css.get(e); if (!c || !shown(e) || e.ownerSVGElement) return;
          if (c.display === 'inline' && !/^(svg|img|video|canvas)$/i.test(e.tagName)) return;
          if (c.position === 'absolute' || c.position === 'fixed') return;
          for (var p = e.parentElement; p && p !== bd; p = p.parentElement) {
            var pc = css.get(p); if (pc && (pc.overflowX !== 'visible' || pc.overflowY !== 'visible')) return;
          }
          var r = e.getBoundingClientRect(); if (!r.width && !r.height) return;
          var q = rel(r); lo = Math.min(lo, q.y); hi = Math.max(hi, q.b); rx = Math.max(rx, q.r);
        });
        var dy = Math.round(B.y - lo + hi - B.b), dx = Math.round(rx - B.r);
        if (dy > 6) issue('overflow', 'the content is ' + dy + ' px taller than the space under the title', bd);
        if (dx > 6) issue('overflow', 'the content is ' + dx + ' px wider than the body', bd);
      });

      // 4. Containers that cut off their own content (code, cards, media)
      all.forEach(function (el) {
        if (el.closest('svg') || !shown(el) || /^(IMG|VIDEO|CANVAS|IFRAME)$/.test(el.tagName)) return;
        var c = css.get(el); if (c.overflowX === 'visible' && c.overflowY === 'visible') return;
        var dx = el.scrollWidth - el.clientWidth, dy = el.scrollHeight - el.clientHeight;
        if (dx > 2 || dy > 2) issue('clipped', cls(el) + ' cuts off ' + (dx > 2 ? dx + ' px of width' : '') + (dx > 2 && dy > 2 ? ' and ' : '') + (dy > 2 ? dy + ' px of height' : ''), el);
      });

      // Every line of text, in stage px
      var lines = [], walker = document.createTreeWalker(s, NodeFilter.SHOW_TEXT, null), tn;
      while ((tn = walker.nextNode())) {
        if (!tn.nodeValue.trim()) continue;
        var pe = tn.parentElement;
        if (!pe || pe.closest('.pc-notes, script, style, title, desc')) continue;
        var c = css.get(pe) || getComputedStyle(pe);
        if (c.display === 'none' || c.visibility === 'hidden' || parseFloat(c.opacity) < 0.05) continue;
        var inSvg = !!pe.closest('svg');
        var fg = rgba(inSvg ? c.fill : c.color), tf = c.webkitTextFillColor;
        if (!inSvg && tf && rgba(tf)[3] < 0.05) fg = null;        // painted text (count-up, gradient text): no colour to test
        // Display type set tight (stats, hero titles) has glyph boxes taller than its lines: measure the line it takes
        var lhPx = !inSvg && /px$/.test(c.lineHeight) ? parseFloat(c.lineHeight) : 0;
        var rg = document.createRange(); rg.selectNodeContents(tn);
        [].forEach.call(rg.getClientRects(), function (cr) {
          if (cr.width < 0.5 || cr.height < 0.5) return;
          var b = rel(cr), trim = lhPx ? (b.b - b.y - lhPx) / 2 : 0;
          if (trim > 0) { b.y += trim; b.b -= trim; }
          lines.push({ x: b.x, y: b.y, r: b.r, b: b.b, h: b.b - b.y, el: pe, blk: blockOf(pe), svg: inSvg, fg: fg,
                       fs: parseFloat(c.fontSize) || cr.height / k, wt: parseInt(c.fontWeight, 10) || 400 });
        });
      }
      res.info.lines = lines.length;
      res.info.minFont = lines.length ? Math.round(Math.min.apply(null, lines.map(function (L) { return L.fs; })) * 10) / 10 : null;
      lines.forEach(function (L) {
        if (L.fs < 16) issue('small-text', 'text at ' + (Math.round(L.fs * 10) / 10) + ' px is too small to read on a screen', L.el);
      });

      // 5. Text outside the margins (the running head, page number, pictures and slides that fill the frame aside)
      var free = s.matches('.pc-bleed, .pc-cover') ? null : '.pc-chrome, .pc-num, .pc-media, figure.pc-chart svg, .pc-vs, [data-qc-free]';
      if (free) lines.forEach(function (L) {
        if (L.el.closest(free) || clipped(L.el)) return;
        var m = [];
        if (L.x < pad.l - 2) m.push('left'); if (L.r > W - pad.r + 2) m.push('right');
        if (L.b > H - pad.b * 0.45) m.push('bottom');
        if (m.length) issue('margin', 'text in the ' + m.join(' and ') + ' margin', L.el);
      });

      // 6. Text over text from another block; chart labels closer than 4 px on the same row
      for (var a = 0; a < lines.length; a++) for (var z = a + 1; z < lines.length; z++) {
        var A = lines[a], B = lines[z];
        if (A.blk === B.blk || A.blk.contains(B.blk) || B.blk.contains(A.blk)) continue;
        var ix = Math.min(A.r, B.r) - Math.max(A.x, B.x), iy = Math.min(A.b, B.b) - Math.max(A.y, B.y);
        if (ix > 2 && iy > Math.max(3, 0.2 * Math.min(A.h, B.h)))
          issue('text-overlap', 'runs over "' + txt(B.blk).slice(0, 40) + '"', A.blk);
        else if (A.svg && B.svg && A.el.closest('svg') === B.el.closest('svg') && iy > 0.5 * Math.min(A.h, B.h) && ix > -4)
          issue('crowded', 'chart labels touch: "' + txt(A.blk).slice(0, 24) + '" and "' + txt(B.blk).slice(0, 24) + '"', A.blk);
      }

      // 7. Text spilling out of the box it sits in (anything with a fill, an edge or a shadow)
      var boxes = all.filter(function (el) { return el !== s && shown(el) && isBox(el, css.get(el)); });
      boxes.forEach(function (bx) {
        var bb = rel(bx.getBoundingClientRect()), n = 0;
        lines.forEach(function (L) {
          var v = Math.max(2, L.h * 0.3);   // tight line spacing lets tall type stand a little past its own box
          if (bx.contains(L.el) && (L.x < bb.x - 2 || L.r > bb.r + 2 || L.y < bb.y - v || L.b > bb.b + v)) n++;
        });
        if (n) issue('spill', n + ' line' + (n > 1 ? 's' : '') + ' of text spill out of ' + cls(bx), bx);
      });

      // 8. Boxes over boxes (badges, running heads and other placed parts overlap on purpose)
      var flow = boxes.filter(function (el) { return !PLACED.test(css.get(el).position) && !el.closest('.pc-chrome, .pc-num, .pc-vs'); });
      for (var i = 0; i < flow.length; i++) for (var j = i + 1; j < flow.length; j++) {
        var P = flow[i], Q = flow[j];
        if (P.contains(Q) || Q.contains(P)) continue;
        var p = rel(P.getBoundingClientRect()), q = rel(Q.getBoundingClientRect());
        var ox = Math.min(p.r, q.r) - Math.max(p.x, q.x), oy = Math.min(p.b, q.b) - Math.max(p.y, q.y);
        if (ox > 2 && oy > 2) issue('box-overlap', cls(P) + ' overlaps ' + cls(Q) + ' by ' + Math.round(ox) + ' x ' + Math.round(oy) + ' px', P);
      }

      // 9. Empty parts
      s.querySelectorAll('h1, h2, h3, h4, p, li, th, figcaption, .pc-stat, .pc-label, .pc-kicker, .pc-chip').forEach(function (el) {
        if (el.closest('.pc-notes') || !shown(el)) return;
        if (!el.textContent.trim() && !el.querySelector('svg, img, video, canvas')) issue('empty', cls(el) + ' is empty', el.parentElement);
      });

      // 10. Pictures: loaded, embedded, and not stretched past their own pixels
      s.querySelectorAll('img').forEach(function (im) {
        var srcRef = im.getAttribute('src') || '';
        if (!im.complete || !im.naturalWidth) { issue('picture', 'picture did not load: ' + srcRef.slice(0, 60), im); return; }
        if (!/^data:/.test(srcRef)) issue('not-embedded', 'picture not inside the file: ' + srcRef.slice(0, 60), im);
        if (/^data:image\/svg|\.svg(\?|#|$)/i.test(srcRef)) return;
        var b = rel(im.getBoundingClientRect()), fit = css.get(im) ? css.get(im).objectFit : 'fill';
        var need = fit === 'cover' ? Math.max((b.r - b.x) / im.naturalWidth, (b.b - b.y) / im.naturalHeight)
                                   : Math.min((b.r - b.x) / im.naturalWidth, (b.b - b.y) / im.naturalHeight);
        if (need > 1.5) issue('low-res', 'picture shown at ' + need.toFixed(1) + ' times its own size (' + im.naturalWidth + ' x ' + im.naturalHeight + ' px), so it will look soft', im);
      });
      [s].concat(all).forEach(function (el) {
        [null, '::before', '::after'].forEach(function (ps) {
          var bi = getComputedStyle(el, ps).backgroundImage || '';
          (bi.match(/url\((['"]?)(.*?)\1\)/g) || []).forEach(function (u) {
            if (!/^url\((['"]?)data:/.test(u)) issue('not-embedded', 'picture not inside the file: ' + u.slice(0, 60), el);
          });
        });
      });

      // 11. Titles: report the line count; past three lines is too long
      var tl = s.querySelector('.pc-title');
      if (tl && shown(tl)) {
        var tc = css.get(tl), lh = parseFloat(tc.lineHeight) || parseFloat(tc.fontSize) * 1.15;
        res.info.titleLines = Math.round(tl.getBoundingClientRect().height / k / lh);
        if (res.info.titleLines > (parseFloat(getComputedStyle(deck).getPropertyValue('--title-lines')) || 3)) issue('title', 'the title runs to ' + res.info.titleLines + ' lines', tl);
      }

      // 12. Charts are drawn
      s.querySelectorAll('figure.pc-chart').forEach(function (f) {
        if (!f.querySelector(':scope > svg')) issue('chart', 'chart not drawn (' + (f.dataset.type || 'no data-type') + ')', f);
      });

      // Facts for the summary: notes, code fitting, type sizes
      var nt = s.querySelector('.pc-notes');
      res.info.notes = nt ? (nt.textContent.trim().split(/\s+/).filter(Boolean).length) : 0;
      s.querySelectorAll('pre.pc-code').forEach(function (pc) {
        var f = []; if (pc.dataset.fit) f.push('on its own row');
        if (pc.style.fontSize) f.push('font ' + pc.style.fontSize);
        if (f.length) res.info.code = f.join(', ');
      });
      res.info.type = {};
      TYPE.forEach(function (sel) {
        s.querySelectorAll(sel).forEach(function (el) {
          if (el.closest('.pc-notes') || !shown(el)) return;
          var fs = Math.round(parseFloat(css.get(el).fontSize));
          var list = res.info.type[sel] = res.info.type[sel] || [];
          if (list.indexOf(fs) < 0) list.push(fs);
        });
      });

      // Lines for qc.py's contrast check: [x, y, right, bottom, r, g, b, a, size, weight, text]
      var seen = {};
      lines.forEach(function (L) {
        if (!L.fg || L.fg[3] < 0.05) return;
        var key = Math.round(L.x) + ',' + Math.round(L.y);
        if (seen[key]) return; seen[key] = 1;
        res.lines.push([Math.round(L.x), Math.round(L.y), Math.round(L.r), Math.round(L.b), L.fg[0], L.fg[1], L.fg[2], L.fg[3],
                        Math.round(L.fs * 10) / 10, L.wt, txt(L.el).slice(0, 40)]);
      });
      out.slides.push(res);
    });
    slides.forEach(function (o) { o.style.visibility = ''; });
  }

  addEventListener('load', function () {
    if (!window.PCDeck) { out.errors.push('The runtime did not start'); return finish(); }
    try { PCDeck.set({ motion: 'static' }); } catch (e) { out.errors.push('QC: ' + e); }
    PCDeck.ready().then(function () { return new Promise(function (r) { setTimeout(r, 300); }); })
      .then(function () { try { measure(); } catch (e) { out.errors.push('QC: ' + (e && e.stack || e)); } })
      .then(finish, function (e) { out.errors.push('QC: ' + e); finish(); });
  });
})();
