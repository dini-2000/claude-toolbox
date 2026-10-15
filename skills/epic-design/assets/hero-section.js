/* =========================================================================
   hero-section.js: the epic-design motion engine
   Load it after GSAP and ScrollTrigger, all three with defer (see
   hero-section.html):
     https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js
     https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/ScrollTrigger.min.js
     hero-section.js

   What it runs (names from references/):
   - depth parallax for every .layer, strength from the --depth-N-factor
     tokens in hero-section.css (motion-system.md, Pattern 1)
   - a pinned hero (Pattern 2) whose exit follows the scroll: the title
     splits apart, the companions scatter (depth-system.md), the product
     grows and fades
   - an elastic drop with an impact shake for the product (Pattern 9)
   - a split-converge headline for [data-animate="converge"]
     (text-animations.md, Technique 1). The engine splits the words itself:
     SplitText is not published on the CDN for GSAP 3.12.5.
   - one-shot reveals for the other data-animate values (motion-system.md,
     IntersectionObserver Activation)
   - three modes: full; lite for touch screens and low-power devices
     (performance.md); calm for the OS reduced-motion setting or the
     visitor's Motion toggle (accessibility.md), which fades and never moves

   Transform owners. A running CSS animation beats GSAP's inline transform,
   so an element never has both. Each moving part has its own element:
     .layer (parallax) > .product-stage (scroll exit) > .drop-wrapper (drop
       and shake, both GSAP) > .product-hero.float-loop (CSS float)
     .layer > .companion (scatter) > .deco.float-loop (CSS float)
     .hero-head (exit fade) > h1 > .title-half (exit split) > .word (entrance)

   Without GSAP the page keeps the layout the CSS gives it: complete, still.
   ========================================================================= */
(function () {
  'use strict';

  const root = document.documentElement;
  const toggle = document.querySelector('.motion-toggle');
  const gsap = window.gsap;
  const ScrollTrigger = window.ScrollTrigger;

  if (!gsap || !ScrollTrigger) {
    root.classList.remove('motion-pending');
    return;
  }
  gsap.registerPlugin(ScrollTrigger);

  /* Settings ---------------------------------------------------------------- */
  const DEFAULT_FACTORS = [0.10, 0.25, 0.50, 0.80, 1.00, 1.20];
  const PARALLAX_PERCENT = -15;          // yPercent at factor 1 (Pattern 1)
  const REVEAL_STAGGER = 0.12;           // seconds between reveals that enter together
  const STORAGE_KEY = 'motionPreference'; // 'on' or 'off', as in accessibility.md
  const OBSERVE = { threshold: 0.15, rootMargin: '0px 0px -50px 0px' };

  // Start states and tweens for data-animate (motion-system.md, triggerAnimation)
  const REVEALS = {
    'fade-up':     { from: { y: 60, opacity: 0 },      tween: { duration: 0.8, ease: 'power3.out' } },
    'fade-in':     { from: { opacity: 0 },             tween: { duration: 1.0, ease: 'power2.out' } },
    'scale-in':    { from: { scale: 0.8, opacity: 0 }, tween: { duration: 0.7, ease: 'back.out(1.7)' } },
    'slide-left':  { from: { x: -80, opacity: 0 },     tween: { duration: 0.8, ease: 'power3.out' } },
    'slide-right': { from: { x: 80, opacity: 0 },      tween: { duration: 0.8, ease: 'power3.out' } },
  };

  // Companions scatter on the hero's exit (depth-system.md)
  const SCATTER = {
    '.companion-right': { x: 80, y: -50, scale: 1.3 },
    '.companion-left':  { x: -70, y: 40, scale: 1.25 },
    '.companion-lower': { x: 30, y: 80, scale: 1.1 },
  };

  const reduceQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
  const coarseQuery = window.matchMedia('(pointer: coarse)');
  let savedPref = null;   // used when localStorage is blocked
  let ctx = null;

  /* Preference and mode ----------------------------------------------------- */
  function readPref() {
    try { return localStorage.getItem(STORAGE_KEY) || savedPref; } catch (e) { return savedPref; }
  }
  function writePref(value) {
    savedPref = value;
    try { localStorage.setItem(STORAGE_KEY, value); } catch (e) { /* private window */ }
  }

  // calm: the visitor turned motion off, or the OS asks for less and they
  // have not turned it on. lite: touch screen or 4 cores or fewer.
  function pickMode() {
    const pref = readPref();
    if (pref === 'off' || (reduceQuery.matches && pref !== 'on')) return 'calm';
    if (coarseQuery.matches || (navigator.hardwareConcurrency || 8) <= 4) return 'lite';
    return 'full';
  }

  function readFactors() {
    const style = getComputedStyle(root);
    return DEFAULT_FACTORS.map(function (fallback, depth) {
      const value = parseFloat(style.getPropertyValue('--depth-' + depth + '-factor'));
      return Number.isFinite(value) ? value : fallback;
    });
  }

  /* Split headline ------------------------------------------------------------
     Screen readers get the full text once, from a visually hidden copy; the
     moving word spans are hidden from them. Words split at the midpoint, or
     where the author marks them with .word-left and .word-right spans. */
  function splitHeadline(el) {
    if (el.dataset.split === 'done') return;
    const text = el.textContent.replace(/\s+/g, ' ').trim();
    const words = function (nodes) {
      return nodes.flatMap(function (n) { return n.textContent.trim().split(/\s+/).filter(Boolean); });
    };
    let left;
    let right;
    if (el.querySelector('.word-left, .word-right')) {
      left = words(Array.from(el.querySelectorAll('.word-left')));
      right = words(Array.from(el.querySelectorAll('.word-right')));
    } else {
      const all = text.split(' ');
      const mid = Math.max(1, Math.floor(all.length / 2));
      left = all.slice(0, mid);
      right = all.slice(mid);
    }

    const label = document.createElement('span');
    label.className = 'sr-only';
    label.textContent = text;
    const parts = [label];
    [['title-left', left], ['title-right', right]].forEach(function (pair) {
      if (!pair[1].length) return;
      const half = document.createElement('span');
      half.className = 'title-half ' + pair[0];
      half.setAttribute('aria-hidden', 'true');
      pair[1].forEach(function (word) {
        const span = document.createElement('span');
        span.className = 'word';
        span.textContent = word;
        half.appendChild(span);
      });
      parts.push(half);
    });
    el.replaceChildren.apply(el, parts);
    el.removeAttribute('aria-label');
    el.dataset.split = 'done';
  }

  /* Reveals ------------------------------------------------------------------- */
  function endState(from) {
    const end = {};
    Object.keys(from).forEach(function (key) {
      end[key] = (key === 'scale' || key === 'opacity') ? 1 : 0;
    });
    return end;
  }

  function convergeStart(title) {
    gsap.set(title.querySelectorAll('.title-left .word'), { x: function () { return -1.2 * window.innerWidth; }, opacity: 0 });
    gsap.set(title.querySelectorAll('.title-right .word'), { x: function () { return 1.2 * window.innerWidth; }, opacity: 0 });
  }

  // Outer words set off first on both sides, as in Technique 1
  function convergeIn(title, delay) {
    const vars = { x: 0, opacity: 1, duration: 1.1, ease: 'power3.out', delay: delay };
    gsap.to(title.querySelectorAll('.title-left .word'), Object.assign({ stagger: 0.03 }, vars));
    gsap.to(title.querySelectorAll('.title-right .word'), Object.assign({ stagger: { each: 0.03, from: 'end' } }, vars));
  }

  // Elements that enter the viewport together reveal one after another.
  // Tweens made later, in the observer, join the context through ctx.add,
  // so a mode change reverts them with everything else.
  function watchReveals(els, start, play) {
    els.forEach(start);
    const observer = new IntersectionObserver(function (entries) {
      let n = 0;
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        observer.unobserve(entry.target);
        const delay = n++ * REVEAL_STAGGER;
        ctx.add(function () { play(entry.target, delay); });
      });
    }, OBSERVE);
    els.forEach(function (el) { observer.observe(el); });
    return function () { observer.disconnect(); };
  }

  /* Full and lite motion ------------------------------------------------------ */
  function buildMotion(lite) {
    const factors = readFactors();
    const cleanups = [];

    gsap.utils.toArray('.scene').forEach(function (scene) {
      // .is-active turns on will-change and runs the float loops (CSS)
      ScrollTrigger.create({ trigger: scene, start: 'top bottom', end: 'bottom top', toggleClass: 'is-active' });

      // Pattern 2: the scene is --scene-height tall, so its inner frame stays
      // pinned until the scene's bottom reaches the bottom of the viewport
      const inner = scene.querySelector('.scene-inner');
      if (scene.hasAttribute('data-pin') && inner) {
        ScrollTrigger.create({
          trigger: scene, start: 'top top', end: 'bottom bottom',
          pin: inner, pinSpacing: false, anticipatePin: 1,
        });
      }

      // Pattern 1: deeper layers drift less. Lite leaves the big blurred
      // layers and the particles still (performance.md).
      scene.querySelectorAll('.layer[data-depth]').forEach(function (layer) {
        const depth = parseInt(layer.dataset.depth, 10);
        if (!(depth in factors) || (lite && (depth === 0 || depth === 1 || depth === 5))) return;
        gsap.to(layer, {
          yPercent: PARALLAX_PERCENT * factors[depth],
          ease: 'none',
          scrollTrigger: { trigger: scene, start: 'clamp(top bottom)', end: 'bottom top', scrub: true },
        });
      });

      if (scene.hasAttribute('data-pin')) heroExit(scene);
      elasticDrop(scene);
    });

    // Converge titles and data-animate reveals
    cleanups.push(watchReveals(gsap.utils.toArray('[data-animate="converge"]'), convergeStart,
      function (title, delay) { convergeIn(title, delay + 0.15); }));
    cleanups.push(watchReveals(
      gsap.utils.toArray('[data-animate]').filter(function (el) { return REVEALS[el.dataset.animate]; }),
      function (el) { gsap.set(el, REVEALS[el.dataset.animate].from); },
      function (el, delay) {
        const r = REVEALS[el.dataset.animate];
        gsap.to(el, Object.assign(endState(r.from), r.tween, { delay: delay }));
      }));

    // Pin positions are measured once. When content above them changes height
    // (fonts, images, a content-visibility section rendering for real),
    // measure again.
    let lastHeight = root.scrollHeight;
    let timer = 0;
    const resize = new ResizeObserver(function () {
      clearTimeout(timer);
      timer = setTimeout(function () {
        if (root.scrollHeight !== lastHeight) {
          lastHeight = root.scrollHeight;
          ScrollTrigger.refresh();
        }
      }, 200);
    });
    resize.observe(document.body);
    cleanups.push(function () { resize.disconnect(); clearTimeout(timer); });

    return function () { cleanups.forEach(function (fn) { fn(); }); };
  }

  // The hero's exit, scrubbed across its pinned scroll (progress 0 to 1)
  function heroExit(scene) {
    const q = gsap.utils.selector(scene);
    const tl = gsap.timeline({
      defaults: { ease: 'none' },
      scrollTrigger: { trigger: scene, start: 'top top', end: 'bottom bottom', scrub: 1, invalidateOnRefresh: true },
    });
    const add = function (selector, vars, at) {
      const targets = q(selector);
      if (targets.length) tl.to(targets, vars, at);
    };
    add('.product-stage', { scale: 1.12, duration: 0.55 }, 0);                  // hold, growing slightly
    add('.title-left', { x: function () { return -0.6 * window.innerWidth; }, duration: 0.3, ease: 'power3.in' }, 0.6);
    add('.title-right', { x: function () { return 0.6 * window.innerWidth; }, duration: 0.3, ease: 'power3.in' }, 0.6);
    add('.hero-head', { opacity: 0, duration: 0.3 }, 0.6);
    add('.hero-foot', { y: -40, opacity: 0, duration: 0.25 }, 0.55);
    Object.keys(SCATTER).forEach(function (selector) {
      add(selector, Object.assign({ opacity: 0, duration: 0.35 }, SCATTER[selector]), 0.6);
    });
    add('.product-stage', { scale: 1.6, yPercent: -12, opacity: 0, duration: 0.45, ease: 'power2.in' }, 0.55);
    add('.glow-blob', { opacity: 0, duration: 0.4 }, 0.6);
  }

  // Pattern 9. The drop and the shake are both GSAP's, so they can share
  // .drop-wrapper; the float loop sits on the image inside it. The drop
  // waits for the image to decode, so it never lands as an empty box.
  function elasticDrop(scene) {
    const wrapper = scene.querySelector('.drop-wrapper');
    if (!wrapper) return;
    const tl = gsap.timeline({ paused: true });
    tl.from(wrapper, { y: -180, opacity: 0, scale: 1.1, duration: 1.3, ease: 'elastic.out(1, 0.65)' }, 0.3)
      .to(wrapper, {
        keyframes: [
          { rotation: -2,   duration: 0.08 },
          { rotation: 2,    duration: 0.08 },
          { rotation: -1.5, duration: 0.07 },
          { rotation: 1,    duration: 0.07 },
          { rotation: 0,    duration: 0.10 },
        ],
        ease: 'power1.inOut',
      }, '-=0.35');
    const img = wrapper.querySelector('img');
    const play = function () { tl.play(); };
    if (img && img.decode) img.decode().then(play, play); else play();
  }

  /* Calm: opacity only, nothing moves (accessibility.md) --------------------- */
  function buildCalm() {
    return watchReveals(gsap.utils.toArray('[data-animate]'),
      function (el) { gsap.set(el, { opacity: 0 }); },
      function (el) { gsap.to(el, { opacity: 1, duration: 0.3, ease: 'none' }); });
  }

  /* Apply a mode -------------------------------------------------------------- */
  function apply() {
    const mode = pickMode();
    if (ctx) ctx.revert();   // kills tweens, pins and observers; restores inline styles
    root.classList.toggle('motion-on', mode !== 'calm');
    root.classList.toggle('perf-lite', mode === 'lite');
    root.classList.toggle('no-motion', mode === 'calm');
    ctx = gsap.context(function () {
      return mode === 'calm' ? buildCalm() : buildMotion(mode === 'lite');
    });
    ScrollTrigger.refresh();
    if (toggle) toggle.setAttribute('aria-pressed', String(mode !== 'calm'));
    root.classList.remove('motion-pending');
  }

  // Accept the skeleton in SKILL.md, Step 5, as written: layers straight in
  // the section, and --scene-height marking the scroll length. Pinning needs
  // a frame inside the section, so add one, and treat --scene-height as data-pin.
  gsap.utils.toArray('.scene').forEach(function (scene) {
    if (!scene.querySelector(':scope > .scene-inner')) {
      const inner = document.createElement('div');
      inner.className = 'scene-inner';
      while (scene.firstChild) inner.appendChild(scene.firstChild);
      scene.appendChild(inner);
    }
    if (/--scene-height/.test(scene.getAttribute('style') || '')) scene.setAttribute('data-pin', '');
  });
  gsap.utils.toArray('[data-animate="converge"]').forEach(splitHeadline);

  if (toggle) {
    toggle.hidden = false;
    toggle.addEventListener('click', function () {
      writePref(toggle.getAttribute('aria-pressed') === 'true' ? 'off' : 'on');
      apply();
    });
  }
  // Follow the OS setting live, unless the visitor has chosen
  reduceQuery.addEventListener('change', function () { if (!readPref()) apply(); });

  // Smooth scrolling for in-page links while motion is on. CSS
  // `scroll-behavior: smooth` would also slow ScrollTrigger's own measuring
  // jumps and misplace the pins, so it is done per click instead. Focus
  // moves to the target, as a normal jump would move it. The skip link
  // keeps the browser's instant jump.
  document.addEventListener('click', function (event) {
    const link = event.target.closest('a[href^="#"]:not(.skip-link)');
    if (!link || !root.classList.contains('motion-on')) return;
    const target = document.getElementById(decodeURIComponent(link.hash.slice(1)));
    if (!target) return;
    event.preventDefault();
    target.scrollIntoView({ behavior: 'smooth' });
    if (!target.hasAttribute('tabindex')) target.setAttribute('tabindex', '-1');
    target.focus({ preventScroll: true });
    history.pushState(null, '', link.hash);
  });

  apply();
})();
