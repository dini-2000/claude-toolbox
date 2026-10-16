/* Notes at the foot of the page for kit documents (data-notes="foot"). tools/doc_pdf.py adds this script after
   Paged.js (tools/vendor/pagedjs, MIT), loaded with window.PagedConfig = { auto: false }. Once the runtime is ready,
   the page's style sheets go to Paged.js with every :is(), :where(), :has() and :not() list written out in full,
   because Paged.js splits selectors at every comma. window.PC_PAGED resolves when the pages are laid out. */
(function () {
  'use strict';
  var Q = /["']/;

  function scan(s, from, onChar) {           // walks s, skipping strings, comments and url(...)
    for (var i = from, q = null; i < s.length; i++) {
      var c = s[i];
      if (q) { if (c === '\\') i++; else if (c === q) q = null; continue; }
      if (Q.test(c)) { q = c; continue; }
      if (c === '/' && s[i + 1] === '*') { var e = s.indexOf('*/', i + 2); i = e < 0 ? s.length : e + 1; continue; }
      if (c === 'u' && s.substr(i, 4) === 'url(' && !Q.test(s[i + 4])) { var k = s.indexOf(')', i); i = k < 0 ? s.length : k; continue; }
      if (onChar(c, i) === false) return i;
    }
    return s.length;
  }

  function split(s) {                        // a selector list at its top-level commas
    var d = 0, out = [], start = 0;
    scan(s, 0, function (c, i) {
      if (c === '(' || c === '[') d++;
      else if (c === ')' || c === ']') d--;
      else if (c === ',' && d === 0) { out.push(s.slice(start, i)); start = i + 1; }
    });
    out.push(s.slice(start));
    return out.map(function (x) { return x.trim(); }).filter(Boolean);
  }

  function args(s, open) {                   // the arguments of the parenthesis at `open`, and where it closes
    var d = 0, out = [], start = open + 1, end = s.length;
    scan(s, open, function (c, i) {
      if (c === '(' || c === '[') d++;
      else if (c === ')' || c === ']') { if (--d === 0) { out.push(s.slice(start, i)); end = i; return false; } }
      else if (c === ',' && d === 1) { out.push(s.slice(start, i)); start = i + 1; }
    });
    return [end, out];
  }

  function expand(sel) {
    var re = /:(is|where|has|not)\(/g, m;
    while ((m = re.exec(sel))) {
      var r = args(sel, m.index + m[0].length - 1), list = r[1];
      if (list.length < 2) continue;
      var head = sel.slice(0, m.index), tail = sel.slice(r[0] + 1), fn = m[1];
      if (fn === 'not') return expand(head + list.map(function (a) { return ':not(' + a.trim() + ')'; }).join('') + tail);
      return list.reduce(function (all, a) { return all.concat(expand(head + ':' + fn + '(' + a.trim() + ')' + tail)); }, []);
    }
    return [sel];
  }

  function flatten(css) {
    var out = '', last = 0, start = 0;
    scan(css, 0, function (c, i) {
      if (c === ';' || c === '}') start = i + 1;
      else if (c === '{') {
        var pre = css.slice(start, i), t = pre.trim();
        if (t && t[0] !== '@' && t.indexOf('(') >= 0) {
          var list = split(t).reduce(function (all, s) { return all.concat(expand(s)); }, []);
          out += css.slice(last, start) + '\n' + list.join(',\n') + ' {';
          last = i + 1;
        }
        start = i + 1;
      }
    });
    return out + css.slice(last);
  }

  function run() {
    var styles = Array.prototype.slice.call(document.querySelectorAll('style:not([data-pagedjs-inserted-styles])'));
    var css = styles.map(function (s) { return s.textContent; }).join('\n');
    styles.forEach(function (s) { s.remove(); });
    // the embedded fonts stay in a sheet of their own: parsing megabytes of font data slows Paged.js to a crawl
    var faces = document.createElement('style');
    faces.setAttribute('data-pagedjs-ignore', '');
    css = css.replace(/@font-face\s*\{[^}]*\}/g, function (f) { faces.appendChild(document.createTextNode(f + '\n')); return ''; });
    document.head.appendChild(faces);
    // Paged.js matches rules inside the body only, and ours start at <html class="pc-deck pc-doc" data-...>,
    // so the content goes into a copy of that element
    var wrap = document.createElement('div');
    Array.prototype.forEach.call(document.documentElement.attributes, function (a) {
      if (a.name !== 'lang' && a.name !== 'style') wrap.setAttribute(a.name, a.value);
    });
    wrap.classList.add('pc-paged-root');
    while (document.body.firstChild) wrap.appendChild(document.body.firstChild);
    document.body.appendChild(wrap);
    // named pages the runtime set as inline styles (chapter running heads) become rules, which Paged.js reads
    Array.prototype.forEach.call(wrap.querySelectorAll('[style*="page"]'), function (e) {
      if (!e.style.page || e.style.page === 'auto') return;
      e.setAttribute('data-pc-page', e.style.page);
      css += '\n[data-pc-page="' + e.style.page + '"] { page: ' + e.style.page + '; }';
    });
    var sheet = {};
    sheet[location.href] = flatten(css);
    return window.PagedPolyfill.preview(undefined, [sheet]);
  }

  window.PC_PAGED = (window.PCDeck && PCDeck.ready ? PCDeck.ready() : Promise.resolve()).then(run);
  window.PC_PAGED.catch(function (e) { (window.__pcErrs = window.__pcErrs || []).push('Paged.js: ' + (e && e.message || e)); });
  window.PCFlattenCSS = flatten;
})();
