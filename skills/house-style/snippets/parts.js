/* snippets/parts.js: draws the parts in parts.css (pcx-hbar, pcx-share, pcx-flow, data-tip). Load it after
   the slides and before engine/runtime.js, so the runtime then draws the icons it adds and runs the builds:
   data-build="draw" on a pcx-hbar grows its bars like a native chart's. Flow routes are measured after layout and
   redrawn when fonts load, a map or node changes size, a slide is shown and before printing.
   window.PCXParts.redraw() redraws every flow map. */
(function () {
  'use strict';
  var SVGNS = 'http://www.w3.org/2000/svg';
  var FLOW_SPEED = { main: [22, 36.7], 'new': [22, 36.7], partial: [14, 27.5], emerging: [9, 24.4] };  // dash period px, px per s
  var reduced = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : { matches: false };
  var flows = [];

  function el(tag, cls, html) { var e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function icon(name) { return name ? '<i class="pc-icon" data-icon="' + esc(name) + '"></i>' : ''; }
  function decimals(s) { var m = String(s).match(/\.(\d+)/); return m ? m[1].length : 0; }
  function fmt(v, dp) { return Number(v).toLocaleString('en-GB', { minimumFractionDigits: dp, maximumFractionDigits: dp }); }
  function rows(c) { return Array.prototype.filter.call(c.children, function (r) { return r.hasAttribute('data-v'); }); }
  function deckOf(n) { return n.closest('.pc-deck') || document.body; }
  function still(n) { return deckOf(n).getAttribute('data-motion') === 'static'; }

  // ---------------------------------------------------------------- horizontal bars: estimates, highlights, a target line
  function drawHbar(c) {
    if (c.getAttribute('data-done')) return;
    var rs = rows(c), vals = rs.map(function (r) { return parseFloat(r.getAttribute('data-v')); });
    var target = c.hasAttribute('data-target') ? parseFloat(c.getAttribute('data-target')) : NaN, hasT = !isNaN(target);
    var max = parseFloat(c.getAttribute('data-max')) || Math.max.apply(null, hasT ? vals.concat(target) : vals) * 1.1;
    var unit = c.getAttribute('data-unit') || '';
    var dpAll = c.hasAttribute('data-dp') ? +c.getAttribute('data-dp') : null;
    if (hasT) c.classList.add('pcx-hbar--target');
    var span = hasT ? 100 : 80;                  // % of the track at max: without a target, room is left for the value
    var frag = document.createDocumentFragment();
    rs.forEach(function (r, i) {
      var mod = (r.classList.contains('is-hl') ? ' pcx-hbar-row--hl' : '') + (r.classList.contains('is-est') ? ' pcx-hbar-row--est' : '');
      var lab = el('div', 'pcx-hbar-label' + mod, r.innerHTML);
      var track = el('div', 'pcx-hbar-track' + mod);
      var bar = el('span', 'pcx-hbar-bar ch-hbar');                   // ch-hbar and ch-lab join the engine's draw build
      bar.style.width = (Math.max(0, vals[i]) / max * span).toFixed(2) + '%';
      bar.style.setProperty('--k', i);
      var val = el('span', 'pcx-hbar-val ch-lab');
      val.textContent = r.getAttribute('data-show') || fmt(vals[i], dpAll != null ? dpAll : decimals(r.getAttribute('data-v'))) + unit;
      val.style.setProperty('--k', i);
      if (r.hasAttribute('data-tip')) track.setAttribute('data-tip', r.getAttribute('data-tip'));
      track.appendChild(bar);
      frag.appendChild(lab);
      frag.appendChild(track);
      if (hasT) {
        var tick = el('i', 'pcx-hbar-target ch-lab' + (i === 0 ? ' is-first' : '') + (i === rs.length - 1 ? ' is-last' : ''));
        tick.style.left = (Math.max(0, target) / max * span).toFixed(2) + '%';
        tick.style.setProperty('--k', rs.length);
        track.appendChild(tick);
        if (i === 0) {                           // the label sits above the line, clear of the first bar
          var tl = el('span', 'pcx-hbar-target-label ch-lab', esc(c.getAttribute('data-target-label') ||
            'Target ' + fmt(target, dpAll != null ? dpAll : decimals(c.getAttribute('data-target'))) + unit));
          tl.style.left = tick.style.left;
          tl.style.setProperty('--k', rs.length);
          track.appendChild(tl);
        }
        val.className += mod;
        frag.appendChild(val);
      } else {
        val.className += mod;
        track.appendChild(val);
      }
    });
    c.innerHTML = '';
    c.appendChild(frag);
    c.setAttribute('data-done', '1');
  }

  // ---------------------------------------------------------------- share bar: one whole in up to five labelled parts
  function drawShare(c) {
    if (c.getAttribute('data-done')) return;
    var rs = rows(c), vals = rs.map(function (r) { return Math.max(0, parseFloat(r.getAttribute('data-v')) || 0); });
    var sum = vals.reduce(function (a, v) { return a + v; }, 0) || 1, n = rs.length;
    var unit = c.getAttribute('data-unit') || '';
    var dpAll = c.hasAttribute('data-dp') ? +c.getAttribute('data-dp') : null;
    var total = parseFloat(c.getAttribute('data-total')) || (unit.trim() === '%' ? 100 : 0);
    if (n > 5) console.warn('pcx-share: a share bar shows five parts at most; put the smallest together as "Other" (' + n + ' given)');
    if (total && Math.abs(sum - total) > total * 0.015)
      console.warn('pcx-share: the parts add up to ' + fmt(sum, 1) + unit + ', not ' + fmt(total, 0) + unit);
    var bar = el('div', 'pcx-share-bar'), keys = el('div', 'pcx-share-keys'), cum = 0;
    rs.forEach(function (r, i) {
      var mod = (r.classList.contains('is-hl') ? ' is-hl' : '') + (r.classList.contains('is-est') ? ' is-est' : '');
      var seg = el('span', 'pcx-share-seg' + mod), key = el('div', 'pcx-share-key' + mod);
      var f = vals[i] / sum, w = '(100% - ' + 2 * (n - 1) + 'px) * ' + f.toFixed(5);   // a part's width; parts sit 2 px apart
      seg.style.flexGrow = f.toFixed(5);
      if (r.hasAttribute('data-tip')) seg.setAttribute('data-tip', r.getAttribute('data-tip'));
      if (i === n - 1 && n > 1 && f < 0.12) key.classList.add('is-end');      // a small last part: labelled at the end
      else key.style.marginLeft = 'calc((100% - ' + 2 * (n - 1) + 'px) * ' + cum.toFixed(5) + ' + ' + 2 * i + 'px)';
      key.style.maxWidth = 'max(calc(' + w + ' - 10px), 5.5em)';
      var b = document.createElement('b');
      b.textContent = r.getAttribute('data-show') || fmt(vals[i], dpAll != null ? dpAll : decimals(r.getAttribute('data-v'))) + unit;
      key.appendChild(b);
      key.appendChild(el('span', 'pcx-share-name', r.innerHTML));
      bar.appendChild(seg);
      keys.appendChild(key);
      cum += f;
    });
    c.innerHTML = '';
    c.appendChild(bar);
    c.appendChild(keys);
    c.setAttribute('data-done', '1');
  }

  // ---------------------------------------------------------------- flow maps
  function initFlow(f) {
    var map = f.querySelector('.pcx-flow-map'), cols = f.querySelector('.pcx-flow-cols');
    var panel = f.querySelector('.pcx-flow-panel');
    if (!map || !cols || f.getAttribute('data-done')) return;
    var journeys = Array.prototype.slice.call(f.querySelectorAll('.pcx-flow-journey'));
    var nodes = {}, colOf = {};
    cols.querySelectorAll('.pcx-flow-col').forEach(function (c, ci) {
      c.querySelectorAll('.pcx-flow-node').forEach(function (n) { colOf[n.getAttribute('data-n')] = ci; });
    });
    f.querySelectorAll('.pcx-flow-node').forEach(function (n) {
      nodes[n.getAttribute('data-n')] = n;
      n.innerHTML = icon(n.getAttribute('data-icon')) + '<span>' + n.innerHTML + '</span>';
    });
    // routes: "a>b>c | a>d>c:partial"; styles main (default), lane, partial, new, emerging
    var plan = journeys.map(function (j) {
      return { id: j.getAttribute('data-j'), routes: (j.getAttribute('data-routes') || '').split('|').map(function (s) {
        var parts = s.trim().split(':');
        var ids = parts[0].split('>').map(function (x) { return x.trim(); }).filter(Boolean);
        ids.forEach(function (id) { if (!nodes[id]) console.warn('pcx-flow: a route names an unknown node:', id); });
        return { ids: ids.filter(function (id) { return nodes[id]; }), style: (parts[1] || 'main').trim() };
      }).filter(function (r) { return r.ids.length > 1; }) };
    });
    var band = plan.some(function (j) { return j.routes.some(function (r) {
      return r.style === 'lane' && r.ids.some(function (id, i) { return i && Math.abs(colOf[id] - colOf[r.ids[i - 1]]) > 1; }); }); });
    f.classList.toggle('has-band', band);          // room above the nodes for a lane that skips columns
    var chips = el('div', 'pcx-flow-chips', '<span class="pcx-flow-chips-label">' + esc(f.getAttribute('data-chips-label') || 'Follow a journey') + '</span>');
    journeys.forEach(function (j) {
      var b = el('button', 'pcx-flow-chip', icon(j.getAttribute('data-icon')) + '<span>' + esc(j.getAttribute('data-name') || j.getAttribute('data-j')) + '</span>');
      b.type = 'button';
      b.setAttribute('data-j', j.getAttribute('data-j'));
      b.setAttribute('aria-pressed', 'false');
      chips.appendChild(b);
    });
    map.insertBefore(chips, map.firstChild);
    var heads = el('div', 'pcx-flow-heads');
    cols.querySelectorAll('.pcx-flow-col').forEach(function (c) { heads.appendChild(el('div', 'pcx-flow-head', esc(c.getAttribute('data-title') || ''))); });
    map.insertBefore(heads, cols);
    var svg = document.createElementNS(SVGNS, 'svg');
    svg.setAttribute('class', 'pcx-flow-svg');
    svg.setAttribute('aria-hidden', 'true');
    cols.insertBefore(svg, cols.firstChild);

    function draw() {
      if (!cols.offsetWidth) return;
      var cr = cols.getBoundingClientRect(), k = cr.width / cols.offsetWidth || 1;   // the slide is scaled to the window
      var W = cols.offsetWidth, H = cols.offsetHeight;
      svg.setAttribute('width', W);
      svg.setAttribute('height', H);
      svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
      function box(id) {
        var r = nodes[id].getBoundingClientRect();
        var b = { l: (r.left - cr.left) / k, t: (r.top - cr.top) / k, r: (r.right - cr.left) / k, b: (r.bottom - cr.top) / k };
        b.cx = (b.l + b.r) / 2; b.cy = (b.t + b.b) / 2;
        return b;
      }
      function edge(a, b, style) {
        var A = box(a), B = box(b), x1, y1, x2, y2;
        if (style === 'lane' && Math.abs(colOf[b] - colOf[a]) > 1) {   // a lane that skips columns runs along the top band
          var fw = colOf[b] > colOf[a], sx = fw ? A.r : A.l, ex = fw ? B.l : B.r, dir = fw ? 1 : -1, yb = 13;
          return 'M' + sx.toFixed(1) + ' ' + A.cy.toFixed(1) + ' C' + (sx + 40 * dir).toFixed(1) + ' ' + A.cy.toFixed(1) + ' ' +
                 (sx + 12 * dir).toFixed(1) + ' ' + yb + ' ' + (sx + 60 * dir).toFixed(1) + ' ' + yb + ' L' + (ex - 60 * dir).toFixed(1) + ' ' + yb +
                 ' C' + (ex - 12 * dir).toFixed(1) + ' ' + yb + ' ' + (ex - 40 * dir).toFixed(1) + ' ' + B.cy.toFixed(1) + ' ' + ex.toFixed(1) + ' ' + B.cy.toFixed(1);
        }
        if (B.l >= A.r - 1 || A.l >= B.r - 1) {        // different columns: side to side, an S-curve
          var fwd = B.l >= A.r - 1;
          x1 = fwd ? A.r : A.l; y1 = A.cy; x2 = fwd ? B.l : B.r; y2 = B.cy;
          var dx = (x2 - x1) / 2;
          return 'M' + x1.toFixed(1) + ' ' + y1.toFixed(1) + ' C' + (x1 + dx).toFixed(1) + ' ' + y1.toFixed(1) + ' ' +
                 (x2 - dx).toFixed(1) + ' ' + y2.toFixed(1) + ' ' + x2.toFixed(1) + ' ' + y2.toFixed(1);
        }
        var down = B.t >= A.b;                         // the same column: bottom to top
        y1 = down ? A.b : A.t; y2 = down ? B.t : B.b;
        return 'M' + A.cx.toFixed(1) + ' ' + y1.toFixed(1) + ' L' + B.cx.toFixed(1) + ' ' + y2.toFixed(1);
      }
      var net = {}, out = '';
      plan.forEach(function (j) {
        j.routes.forEach(function (r) {
          for (var i = 0; i < r.ids.length - 1; i++) {
            var key = r.ids[i] + '>' + r.ids[i + 1];
            if (!net[key] || r.style === 'lane') net[key] = r.style === 'lane';
          }
        });
      });
      Object.keys(net).forEach(function (key) {           // a faint network of every link, lanes as wide bands
        var ab = key.split('>');
        out += '<path class="pcx-flow-net' + (net[key] ? ' pcx-flow-net--lane' : '') + '" d="' + edge(ab[0], ab[1], net[key] ? 'lane' : '') + '"/>';
      });
      plan.forEach(function (j) {
        out += '<g class="pcx-flow-j" data-j="' + esc(j.id) + '">';
        j.routes.slice().sort(function (a, b) { return (b.style === 'lane') - (a.style === 'lane'); }).forEach(function (r) {
          var d = '';
          for (var i = 0; i < r.ids.length - 1; i++) d += edge(r.ids[i], r.ids[i + 1], r.style) + ' ';
          out += '<path class="pcx-route pcx-route--' + esc(r.style) + '" data-style="' + esc(r.style) + '" d="' + d.trim() + '"/>';
        });
        out += '</g>';
      });
      svg.innerHTML = out;
      svg.querySelectorAll('g.pcx-flow-j').forEach(function (g) { g.classList.toggle('is-on', g.getAttribute('data-j') === f.getAttribute('data-cur')); });
    }

    function select(id) {
      f.setAttribute('data-cur', id || '');
      f.classList.toggle('is-sel', !!id);
      chips.querySelectorAll('.pcx-flow-chip').forEach(function (c) {
        var on = c.getAttribute('data-j') === id;
        c.classList.toggle('is-on', on);
        c.setAttribute('aria-pressed', on ? 'true' : 'false');
      });
      svg.querySelectorAll('g.pcx-flow-j').forEach(function (g) { g.classList.toggle('is-on', g.getAttribute('data-j') === id); });
      var lit = {};
      plan.forEach(function (j) { if (j.id === id) j.routes.forEach(function (r) { r.ids.forEach(function (x) { lit[x] = 1; }); }); });
      Object.keys(nodes).forEach(function (k) { nodes[k].classList.toggle('is-on', !!lit[k]); });
      journeys.forEach(function (j) { j.classList.toggle('is-on', j.getAttribute('data-j') === id); });
      var intro = panel && panel.querySelector('.pcx-flow-intro');
      if (intro) intro.classList.toggle('is-on', !id);
    }
    chips.addEventListener('click', function (e) {
      var b = e.target.closest('.pcx-flow-chip');
      if (!b || still(f)) return;                          // a static deck keeps the journey it prints with
      e.stopPropagation();
      var id = b.getAttribute('data-j');
      select(f.getAttribute('data-cur') === id ? '' : id);   // click the active one again to clear
    });
    var queued = false;
    function later() { if (!queued) { queued = true; requestAnimationFrame(function () { queued = false; draw(); }); } }
    if (window.ResizeObserver) {
      var ro = new ResizeObserver(later);
      ro.observe(cols);
      Object.keys(nodes).forEach(function (k) { ro.observe(nodes[k]); });
    }
    f._pcxDraw = draw;
    f.setAttribute('data-done', '1');
    flows.push(f);
    draw();
    select(f.hasAttribute('data-default') ? f.getAttribute('data-default') : (plan[0] ? plan[0].id : ''));
  }

  function drawAll() { flows.forEach(function (f) { f._pcxDraw(); }); }

  function animate(t) {          // dashes moved by script on the slide in view: CSS animations on SVG can stay frozen
    flows.forEach(function (f) {
      var s = f.closest('.pc-slide');
      if (!s || !s.classList.contains('is-active') || still(f) || reduced.matches) return;
      f.querySelectorAll('g.pcx-flow-j.is-on path.pcx-route').forEach(function (p) {
        var sp = FLOW_SPEED[p.getAttribute('data-style')];
        if (sp) p.style.strokeDashoffset = (-(t / 1000 * sp[1]) % sp[0]).toFixed(2);
      });
    });
    requestAnimationFrame(animate);
  }

  // ---------------------------------------------------------------- hover tips on [data-tip] (off in a static deck)
  function tips(deck) {
    var tip = el('div', 'pcx-tip');
    tip.hidden = true;
    tip.setAttribute('role', 'tooltip');
    deck.appendChild(tip);
    deck.addEventListener('pointermove', function (e) {
      var t = !still(deck) && e.target.closest && e.target.closest('.pc-slide [data-tip]');
      if (!t) { tip.hidden = true; return; }
      tip.textContent = t.getAttribute('data-tip');
      tip.hidden = false;
      var x = e.clientX + 16, y = e.clientY + 16, w = tip.offsetWidth, h = tip.offsetHeight;
      if (x + w > window.innerWidth - 8) x = e.clientX - w - 12;
      if (y + h > window.innerHeight - 8) y = e.clientY - h - 12;
      tip.style.left = x + 'px';
      tip.style.top = y + 'px';
    });
    deck.addEventListener('pointerleave', function () { tip.hidden = true; });
  }

  // Design/tools/build.py stores each part as drawn, for viewers without scripts, with its source in a
  // <template class="pcx-src">: put the source back, then draw it live.
  document.querySelectorAll('template.pcx-src').forEach(function (t) {
    var part = t.parentNode, src = t.content.firstElementChild;
    if (part && src) part.replaceWith(document.importNode(src, true));
  });
  document.querySelectorAll('.pcx-hbar').forEach(drawHbar);
  document.querySelectorAll('.pcx-share').forEach(drawShare);
  document.querySelectorAll('.pcx-flow').forEach(initFlow);
  document.querySelectorAll('.pc-deck').forEach(function (d) { if (d.querySelector('[data-tip]')) tips(d); });
  if (flows.length) {
    document.addEventListener('pc:slide', function (e) {
      var s = e.detail && e.detail.slide;
      flows.forEach(function (f) { if (!s || s.contains(f)) f._pcxDraw(); });
    });
    window.addEventListener('beforeprint', function () {
      drawAll();
      flows.forEach(function (f) { f.querySelectorAll('path.pcx-route').forEach(function (p) { p.style.strokeDashoffset = ''; }); });
    });
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(drawAll);
    window.addEventListener('load', drawAll);
    requestAnimationFrame(animate);
  }
  window.PCXParts = { redraw: drawAll };
})();
