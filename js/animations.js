/* ==========================================================================
   Wellfit Designs — motion engine
   Vanilla JS, no dependencies. Provides:
   • inertial smooth scrolling for mouse wheels / trackpads (native scrolling on touch)
   • one requestAnimationFrame loop for all scroll-linked effects
   • reveals (fade, mask, split words), parallax, the arch-opening hero,
     a pinned horizontal project rail, word-fill statements, process/timeline
     progress, a velocity-aware marquee, magnetic buttons and hover previews.
   Everything is skipped when the visitor prefers reduced motion.
   ========================================================================== */
(function () {
  'use strict';

  var WF = (window.WF = window.WF || {});
  var root = document.documentElement;
  var mqReduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  var mqFine = window.matchMedia('(hover: hover) and (pointer: fine)');
  var mqPin = window.matchMedia('(min-width: 1025px) and (min-height: 560px)');

  WF.reduced = mqReduce.matches;

  var clamp = function (v, a, b) { return Math.min(b, Math.max(a, v)); };
  var lerp = function (a, b, t) { return a + (b - a) * t; };
  var easeOutCubic = function (t) { return 1 - Math.pow(1 - t, 3); };
  var easeInOutCubic = function (t) { return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };
  var maxScroll = function () { return Math.max(0, root.scrollHeight - window.innerHeight); };

  /* ------------------------------------------------------------------------
     Smooth scroll — eases the window's own scroll position, so position:sticky,
     anchors, find-in-page and assistive tech keep working normally.
     ------------------------------------------------------------------------ */
  function SmoothScroll() {
    this.enabled = !WF.reduced && mqFine.matches;
    this.current = this.target = window.scrollY;
    this.factor = 0.095;            // share of the remaining distance covered per 60fps frame
    this.running = false;
    this.locked = false;
    this.tween = null;
    this._raf = this._raf.bind(this);
    var self = this;
    var cancel = function () { if (self.tween) { self.tween = null; self.running = false; self.current = self.target = window.scrollY; } };
    window.addEventListener('touchstart', cancel, { passive: true });
    window.addEventListener('keydown', function (e) {
      if (/^(Arrow(Up|Down)|Page(Up|Down)|Home|End| |Spacebar)$/.test(e.key)) cancel();
    });
    window.addEventListener('mousedown', cancel);
    if (!this.enabled) return;
    root.classList.add('has-smooth-scroll');
    window.addEventListener('wheel', this._onWheel.bind(this), { passive: false });
    window.addEventListener('scroll', this._onNativeScroll.bind(this), { passive: true });
  }

  SmoothScroll.prototype._scrollableParent = function (node, dy) {
    while (node && node !== document.body && node.nodeType === 1) {
      if (node.hasAttribute('data-native-scroll')) return node;
      var style = window.getComputedStyle(node);
      if (/(auto|scroll)/.test(style.overflowY) && node.scrollHeight > node.clientHeight + 1) {
        if ((dy < 0 && node.scrollTop > 0) || (dy > 0 && node.scrollTop + node.clientHeight < node.scrollHeight - 1)) return node;
      }
      node = node.parentNode;
    }
    return null;
  };

  SmoothScroll.prototype._onWheel = function (e) {
    if (WF.reduced || this.locked || e.ctrlKey || e.metaKey || e.defaultPrevented) return;
    if (Math.abs(e.deltaX) > Math.abs(e.deltaY)) return;          // let horizontal gestures through
    if (this._scrollableParent(e.target, e.deltaY)) return;        // nested scroll areas scroll natively
    e.preventDefault();
    var unit = e.deltaMode === 1 ? 36 : e.deltaMode === 2 ? window.innerHeight : 1;
    if (this.tween) this.tween = null;
    if (!this.running) this.current = window.scrollY;
    this.target = clamp(this.target + e.deltaY * unit, 0, maxScroll());
    this._start();
  };

  SmoothScroll.prototype._onNativeScroll = function () {
    // keyboard, scrollbar drags, find-in-page, scripts: adopt the native position.
    // While easing, our own scrollTo lands within a pixel of `current`; anything
    // further away came from somewhere else, so stop easing and follow it.
    var y = window.scrollY;
    if (!this.running || Math.abs(y - this.current) > 3) {
      this.running = false;
      this.tween = null;
      this.current = this.target = y;
    }
  };

  SmoothScroll.prototype._start = function () {
    if (this.running) return;
    this.running = true;
    this.last = performance.now();
    requestAnimationFrame(this._raf);
  };

  SmoothScroll.prototype._raf = function (now) {
    var dt = Math.min(64, now - this.last);
    this.last = now;
    if (this.tween) {
      var tw = this.tween;
      var t = clamp((now - tw.start) / tw.duration, 0, 1);
      this.current = this.target = lerp(tw.from, tw.to, easeInOutCubic(t));
      if (t >= 1) { this.tween = null; this.running = false; if (tw.done) tw.done(); }
    } else {
      var k = 1 - Math.pow(1 - this.factor, dt / 16.667);
      this.current = lerp(this.current, this.target, k);
      if (Math.abs(this.target - this.current) < 0.4) { this.current = this.target; this.running = false; }
    }
    window.scrollTo(0, this.current);
    if (this.running) requestAnimationFrame(this._raf);
  };

  /** Animated programmatic scroll (anchors, back-to-top). Works with or without smoothing. */
  SmoothScroll.prototype.scrollTo = function (y, opts) {
    opts = opts || {};
    var to = clamp(typeof y === 'number' ? y : 0, 0, maxScroll());
    if (WF.reduced) { window.scrollTo(0, to); if (opts.done) opts.done(); return; }
    var from = window.scrollY;
    var duration = opts.duration || clamp(Math.abs(to - from) * 0.55, 700, 1700);
    this.tween = { from: from, to: to, start: performance.now(), duration: duration, done: opts.done };
    this.current = from;
    this.running = false;
    this._start();
  };

  SmoothScroll.prototype.lock = function () { this.locked = true; this.tween = null; this.running = false; };
  SmoothScroll.prototype.unlock = function () { this.locked = false; this.current = this.target = window.scrollY; };

  WF.scroll = new SmoothScroll();

  /* ------------------------------------------------------------------------
     Frame loop + measurement
     ------------------------------------------------------------------------ */
  var effects = [];
  var listeners = [];
  var state = { y: window.scrollY, lastY: window.scrollY, vh: window.innerHeight, vw: window.innerWidth, velocity: 0, dirty: true };

  WF.onScroll = function (fn) { listeners.push(fn); };
  WF.addEffect = function (fx) { effects.push(fx); if (fx.measure) fx.measure(state); state.dirty = true; return fx; };

  function docTop(el) { var r = el.getBoundingClientRect(); return r.top + window.scrollY; }

  function measure() {
    state.vh = window.innerHeight;
    state.vw = window.innerWidth;
    for (var i = 0; i < effects.length; i++) if (effects[i].measure) effects[i].measure(state);
    state.dirty = true;
  }
  WF.refresh = function () { measure(); };

  var lastFrame = performance.now();
  function frame(now) {
    var dt = Math.min(64, now - lastFrame) || 16.667;
    lastFrame = now;
    var y = window.scrollY;
    var dy = y - state.lastY;
    state.velocity = lerp(state.velocity, dy / (dt / 16.667), 0.18);
    state.y = y;
    state.dt = dt;
    var moved = dy !== 0 || state.dirty;
    for (var i = 0; i < effects.length; i++) {
      var fx = effects[i];
      if (fx.always || moved) fx.update(state);
    }
    if (dy !== 0 || state.dirty) for (var j = 0; j < listeners.length; j++) listeners[j](y, dy, state);
    state.lastY = y;
    state.dirty = false;
    requestAnimationFrame(frame);
  }

  /* ------------------------------------------------------------------------
     Split text helpers
     ------------------------------------------------------------------------ */
  function splitWords(el, wrapClass) {
    if (el.__split) return el.__split;
    var words = [];
    var counter = 0;
    (function walk(node) {
      var kids = Array.prototype.slice.call(node.childNodes);
      kids.forEach(function (child) {
        if (child.nodeType === 3) {
          var parts = child.textContent.split(/(\s+)/);
          var frag = document.createDocumentFragment();
          parts.forEach(function (part) {
            if (!part) return;
            if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(part)); return; }
            if (wrapClass === 'fill') {
              var s = document.createElement('span');
              s.className = 'fill-word';
              s.textContent = part;
              frag.appendChild(s);
              words.push(s);
            } else {
              var outer = document.createElement('span');
              outer.className = 'split-word';
              var inner = document.createElement('span');
              inner.className = 'split-inner';
              inner.style.setProperty('--i', counter++);
              inner.textContent = part;
              outer.appendChild(inner);
              frag.appendChild(outer);
              words.push(inner);
            }
          });
          child.parentNode.replaceChild(frag, child);
        } else if (child.nodeType === 1 && !/^(BR|SVG|IMG)$/i.test(child.tagName)) {
          walk(child);
        }
      });
    })(el);
    el.__split = words;
    return words;
  }

  /* ------------------------------------------------------------------------
     Reveals (IntersectionObserver)
     ------------------------------------------------------------------------ */
  function setupReveals() {
    document.querySelectorAll('[data-stagger]').forEach(function (group) {
      var step = parseFloat(group.getAttribute('data-stagger')) || 0.08;
      var base = parseFloat(group.getAttribute('data-stagger-base')) || 0;
      Array.prototype.forEach.call(group.querySelectorAll('[data-reveal]'), function (el, i) {
        if (!el.style.getPropertyValue('--d')) el.style.setProperty('--d', (base + i * step).toFixed(2) + 's');
      });
    });
    document.querySelectorAll('[data-split]').forEach(function (el) { splitWords(el); });

    var targets = document.querySelectorAll('[data-reveal], [data-split]');
    if (WF.reduced || !('IntersectionObserver' in window)) {
      targets.forEach(function (el) { el.classList.add('is-in'); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-in');
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -10% 0px', threshold: 0.12 });
    targets.forEach(function (el) {
      if (el.hasAttribute('data-reveal-manual')) return;
      io.observe(el);
    });
    document.addEventListener('focusin', function (e) {
      var node = e.target;
      while (node && node !== document.body) {
        if (node.matches && node.matches('[data-reveal], [data-split]') && !node.classList.contains('is-in')) {
          node.classList.add('is-in');
          io.unobserve(node);
        }
        node = node.parentNode;
      }
    });
  }

  /* ------------------------------------------------------------------------
     Parallax: [data-parallax="0.12"] moves an element against the scroll.
     On .media wrappers the image is over-scaled so edges never show.
     ------------------------------------------------------------------------ */
  function setupParallax() {
    document.querySelectorAll('[data-parallax]').forEach(function (el) {
      var speed = parseFloat(el.getAttribute('data-parallax')) || 0.12;
      var target = el.matches('.media') ? el.querySelector('img') : el;
      if (!target) return;
      var isMedia = target !== el;
      if (isMedia && !WF.reduced) target.style.scale = '1.16';
      var fx = { top: 0, h: 0 };
      fx.measure = function () {
        var prev = target.style.translate;
        if (!isMedia) target.style.translate = '';
        fx.top = docTop(el);
        fx.h = el.offsetHeight;
        if (!isMedia) target.style.translate = prev;
        fx.max = isMedia ? fx.h * 0.075 : fx.h * 0.1;
      };
      fx.update = function (s) {
        if (WF.reduced) { target.style.translate = ''; return; }
        if (fx.top + fx.h < s.y - 200 || fx.top > s.y + s.vh + 200) return;
        var mobile = s.vw < 700 ? 0.5 : 1;
        var offset = (s.y + s.vh / 2) - (fx.top + fx.h / 2);
        var y = clamp(offset * speed * mobile, -fx.max, fx.max);
        target.style.translate = '0 ' + y.toFixed(1) + 'px';
      };
      WF.addEffect(fx);
    });
  }

  /* ------------------------------------------------------------------------
     Hero: the arch window opens to full-bleed while the section is pinned.
     ------------------------------------------------------------------------ */
  function setupHero() {
    var hero = document.querySelector('[data-hero]');
    if (!hero) return;
    var sticky = hero.querySelector('.hero__sticky');
    var slot = hero.querySelector('[data-hero-slot]');
    var fx = { pinned: hero.classList.contains('is-pinned') }; // may be pre-set inline to avoid a layout shift

    function setPinned(on) {
      if (on === fx.pinned) return;
      fx.pinned = on;
      hero.classList.toggle('is-pinned', on);
      if (!on) ['--ct', '--cr', '--cb', '--cl', '--crt', '--crb', '--zoom', '--shift-x', '--copy-o', '--copy-y', '--st-o', '--st-y', '--shade']
        .forEach(function (p) { hero.style.removeProperty(p); });
    }

    fx.measure = function (s) {
      setPinned(!WF.reduced && mqPin.matches);
      if (!fx.pinned) return;
      fx.top = docTop(hero);
      fx.h = hero.offsetHeight;
      var sr = sticky.getBoundingClientRect();
      var r = slot.getBoundingClientRect();
      fx.inset = { t: r.top - sr.top, l: r.left - sr.left, r: sr.right - r.right, b: sr.bottom - r.bottom };
      fx.radius = r.width / 2;
      // keep the picture's focal point (data-focal, 0..1 across the image) centred in the arch while it is small
      var img = hero.querySelector('.hero__media img');
      var focal = parseFloat(hero.getAttribute('data-focal')) || 0.5;
      var iw = (img && img.naturalWidth) || 16, ih = (img && img.naturalHeight) || 9;
      var cw = sr.width, ch = sr.height;
      var scale = Math.max(cw / iw, ch / ih);
      var W = iw * scale;
      var focalX = (cw - W) * 0.42 + focal * W;
      fx.shift = clamp((r.left - sr.left + r.width / 2) - focalX, -fx.inset.r, fx.inset.l);
    };
    fx.update = function (s) {
      if (!fx.pinned) return;
      var range = Math.max(1, fx.h - s.vh);
      var p = clamp((s.y - fx.top) / range, 0, 1);
      var open = easeInOutCubic(clamp(p / 0.62, 0, 1));
      var k = 1 - open;
      var st = hero.style;
      st.setProperty('--ct', (fx.inset.t * k).toFixed(1) + 'px');
      st.setProperty('--cr', (fx.inset.r * k).toFixed(1) + 'px');
      st.setProperty('--cb', (fx.inset.b * k).toFixed(1) + 'px');
      st.setProperty('--cl', (fx.inset.l * k).toFixed(1) + 'px');
      st.setProperty('--crt', (fx.radius * k).toFixed(1) + 'px');
      st.setProperty('--crb', (24 * k).toFixed(1) + 'px');
      st.setProperty('--zoom', (1.1 - 0.1 * open).toFixed(4));
      st.setProperty('--shift-x', ((fx.shift || 0) * k).toFixed(1) + 'px');
      var c = clamp(p / 0.26, 0, 1);
      st.setProperty('--copy-o', (1 - c).toFixed(3));
      st.setProperty('--copy-y', (-70 * easeOutCubic(clamp(p / 0.34, 0, 1))).toFixed(1) + 'px');
      st.setProperty('--shade', (clamp((p - 0.28) / 0.4, 0, 1) * 0.95).toFixed(3));
      var t = easeOutCubic(clamp((p - 0.52) / 0.3, 0, 1));
      st.setProperty('--st-o', t.toFixed(3));
      st.setProperty('--st-y', ((1 - t) * 48).toFixed(1) + 'px');
    };
    hero.addEventListener('focusin', function (e) {
      if (!fx.pinned || !e.target.closest('.hero__copy')) return;
      if (window.scrollY > fx.top + 4) {
        if (WF.scroll) WF.scroll.scrollTo(fx.top, { duration: 500 }); else window.scrollTo(0, fx.top);
      }
    });
    WF.addEffect(fx);
  }

  /* ------------------------------------------------------------------------
     Horizontal rail (featured projects): vertical scroll drives the track.
     ------------------------------------------------------------------------ */
  function setupRails() {
    document.querySelectorAll('[data-rail]').forEach(function (rail) {
      var track = rail.querySelector('.rail__track');
      var viewport = rail.querySelector('.rail__viewport');
      var fx = { pinned: false };
      fx.measure = function (s) {
        var on = !WF.reduced && mqPin.matches;
        if (on !== fx.pinned) {
          fx.pinned = on;
          rail.classList.toggle('is-pinned', on);
          if (!on) { track.style.transform = ''; rail.style.removeProperty('--rail-h'); }
        }
        if (!fx.pinned) return;
        fx.distance = Math.max(0, track.scrollWidth - viewport.clientWidth);
        rail.style.setProperty('--rail-h', (fx.distance + s.vh * 1.15).toFixed(0) + 'px');
        fx.top = docTop(rail);
        fx.h = rail.offsetHeight;
      };
      fx.update = function (s) {
        if (!fx.pinned) return;
        var range = Math.max(1, fx.h - s.vh);
        var p = clamp((s.y - fx.top) / range, 0, 1);
        var eased = clamp((p - 0.06) / 0.88, 0, 1);
        track.style.transform = 'translate3d(' + (-fx.distance * eased).toFixed(1) + 'px,0,0)';
        rail.style.setProperty('--rail-p', eased.toFixed(3));
      };
      // keyboard users: bring a focused card into view by scrolling the page, not the clipped viewport
      viewport.addEventListener('focusin', function (e) {
        if (!fx.pinned) return;
        viewport.scrollLeft = 0;
        var card = e.target.closest('.project-card');
        if (!card || !fx.distance) return;
        var want = clamp((card.offsetLeft - viewport.clientWidth * 0.1) / fx.distance, 0, 1);
        var range = Math.max(1, fx.h - window.innerHeight);
        var y = fx.top + (want * 0.88 + 0.06) * range;
        if (WF.scroll) WF.scroll.scrollTo(y, { duration: 600 }); else window.scrollTo(0, y);
      });
      WF.addEffect(fx);
    });
  }

  /* ------------------------------------------------------------------------
     Word-fill statements, process line, timeline
     ------------------------------------------------------------------------ */
  function setupProgressEffects() {
    document.querySelectorAll('[data-fill]').forEach(function (el) {
      var words = splitWords(el, 'fill');
      if (WF.reduced) { words.forEach(function (w) { w.classList.add('is-lit'); }); return; }
      var fx = {};
      fx.measure = function () { fx.top = docTop(el); fx.h = el.offsetHeight; };
      fx.update = function (s) {
        var start = fx.top - s.vh * 0.82;
        var end = fx.top + fx.h - s.vh * 0.42;
        var p = clamp((s.y - start) / Math.max(1, end - start), 0, 1);
        var lit = Math.round(p * words.length);
        for (var i = 0; i < words.length; i++) words[i].classList.toggle('is-lit', i < lit);
      };
      WF.addEffect(fx);
    });

    document.querySelectorAll('[data-progress]').forEach(function (el) {
      var prop = el.getAttribute('data-progress') || '--p';
      var steps = el.querySelectorAll('[data-progress-step]');
      if (WF.reduced) {
        el.style.setProperty(prop, 1);
        steps.forEach(function (st) { st.classList.add('is-active'); });
        return;
      }
      var fx = {};
      fx.measure = function () { fx.top = docTop(el); fx.h = el.offsetHeight; };
      fx.update = function (s) {
        var start = fx.top - s.vh * 0.75;
        var end = fx.top + fx.h - s.vh * 0.55;
        var p = clamp((s.y - start) / Math.max(1, end - start), 0, 1);
        el.style.setProperty(prop, p.toFixed(3));
        for (var i = 0; i < steps.length; i++) steps[i].classList.toggle('is-active', p >= (i + 0.35) / steps.length);
      };
      WF.addEffect(fx);
    });
  }

  /* ------------------------------------------------------------------------
     Marquee — drifts continuously, speeds up and follows scroll direction.
     ------------------------------------------------------------------------ */
  function setupMarquees() {
    document.querySelectorAll('[data-marquee]').forEach(function (m) {
      var track = m.querySelector('.marquee__track');
      var group = track && track.querySelector('.marquee__group');
      if (!track || !group || WF.reduced) return;
      var fx = { always: true, x: 0, dir: -1, visible: true, width: 0, paused: false, hover: false };
      var toggle = m.querySelector('.marquee__toggle');
      if (toggle) {
        toggle.hidden = false;
        toggle.addEventListener('click', function () {
          fx.paused = !fx.paused;
          toggle.setAttribute('aria-pressed', fx.paused ? 'true' : 'false');
          toggle.setAttribute('aria-label', fx.paused ? 'Play moving text' : 'Pause moving text');
          m.classList.toggle('is-paused', fx.paused);
        });
      }
      m.addEventListener('pointerenter', function () { fx.hover = true; });
      m.addEventListener('pointerleave', function () { fx.hover = false; });
      if ('IntersectionObserver' in window) {
        new IntersectionObserver(function (e) { fx.visible = e[0].isIntersecting; }).observe(m);
      }
      fx.measure = function () { fx.width = group.getBoundingClientRect().width; };
      fx.update = function (s) {
        if (!fx.visible || !fx.width || fx.paused || fx.hover) return;
        if (Math.abs(s.velocity) > 0.4) fx.dir = s.velocity > 0 ? -1 : 1;
        var speed = 0.045 + Math.min(0.9, Math.abs(s.velocity) * 0.035);
        fx.x += fx.dir * speed * s.dt;
        if (fx.x <= -fx.width) fx.x += fx.width;
        if (fx.x > 0) fx.x -= fx.width;
        track.style.transform = 'translate3d(' + fx.x.toFixed(2) + 'px,0,0)';
      };
      WF.addEffect(fx);
    });
  }

  /* ------------------------------------------------------------------------
     Pointer niceties (fine pointers only): magnetic buttons, hover preview
     ------------------------------------------------------------------------ */
  function setupPointer() {
    if (WF.reduced || !mqFine.matches) return;

    document.querySelectorAll('[data-magnetic]').forEach(function (el) {
      var strength = parseFloat(el.getAttribute('data-magnetic')) || 0.28;
      el.addEventListener('pointermove', function (e) {
        var r = el.getBoundingClientRect();
        var x = (e.clientX - (r.left + r.width / 2)) * strength;
        var y = (e.clientY - (r.top + r.height / 2)) * strength * 1.2;
        el.style.transform = 'translate3d(' + clamp(x, -12, 12).toFixed(1) + 'px,' + clamp(y, -10, 10).toFixed(1) + 'px,0)';
      });
      el.addEventListener('pointerleave', function () { el.style.transform = ''; });
    });

    var list = document.querySelector('[data-hover-preview]');
    var preview = document.querySelector('.svc-preview');
    if (list && preview) {
      var imgs = preview.querySelectorAll('img');
      var pos = { x: 0, y: 0, tx: 0, ty: 0, active: false };
      var running = false;
      var tick = function () {
        pos.x = lerp(pos.x, pos.tx, 0.14);
        pos.y = lerp(pos.y, pos.ty, 0.14);
        var tilt = clamp((pos.tx - pos.x) * 0.04, -6, 6);
        preview.style.transform = 'translate3d(' + pos.x.toFixed(1) + 'px,' + pos.y.toFixed(1) + 'px,0) translate(-50%,-50%) rotate(' + tilt.toFixed(2) + 'deg) scale(' + (pos.active ? 1 : 0.85) + ')';
        if (pos.active || Math.abs(pos.tx - pos.x) > 0.5) requestAnimationFrame(tick); else running = false;
      };
      list.addEventListener('pointermove', function (e) {
        pos.tx = e.clientX + 40;
        pos.ty = e.clientY;
        if (!running) { running = true; if (!pos.active) { pos.x = pos.tx; pos.y = pos.ty; } requestAnimationFrame(tick); }
      });
      list.querySelectorAll('[data-preview-index]').forEach(function (row) {
        row.addEventListener('pointerenter', function () {
          var idx = parseInt(row.getAttribute('data-preview-index'), 10);
          imgs.forEach(function (im, i) { im.classList.toggle('is-active', i === idx); });
          pos.active = true;
          preview.classList.add('is-visible');
        });
      });
      var hidePreview = function () {
        pos.active = false;
        preview.classList.remove('is-visible');
        imgs.forEach(function (im) { im.classList.remove('is-active'); });
      };
      list.addEventListener('pointerleave', hidePreview);
      document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && pos.active) hidePreview(); });
    }
  }

  /* ------------------------------------------------------------------------
     Image fade-in once decoded, scroll progress bar
     ------------------------------------------------------------------------ */
  function setupImages() {
    document.querySelectorAll('img[data-fade]').forEach(function (img) {
      var done = function () { img.classList.add('is-loaded'); };
      if (img.complete && img.naturalWidth) done();
      else { img.addEventListener('load', done, { once: true }); img.addEventListener('error', done, { once: true }); }
    });
  }

  function setupProgressBar() {
    var bar = document.querySelector('.scroll-progress span');
    if (!bar) return;
    WF.onScroll(function (y) {
      var m = maxScroll();
      bar.style.setProperty('--progress', m > 0 ? (y / m).toFixed(4) : 0);
    });
  }

  /* ------------------------------------------------------------------------
     Boot
     ------------------------------------------------------------------------ */
  WF.initMotion = function () {
    setupImages();
    setupReveals();
    setupParallax();
    setupHero();
    setupRails();
    setupProgressEffects();
    setupMarquees();
    setupPointer();
    setupProgressBar();
    measure();
    requestAnimationFrame(frame);

    var resizeTimer;
    window.addEventListener('resize', function () {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(measure, 120);
    });
    window.addEventListener('load', measure);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(measure);
    if ('ResizeObserver' in window) {
      var lastH = 0;
      new ResizeObserver(function () {
        var h = document.body.scrollHeight;
        if (Math.abs(h - lastH) > 2) { lastH = h; measure(); }
      }).observe(document.body);
    }
    var onMotionChange = function () { WF.reduced = mqReduce.matches; measure(); };
    if (mqReduce.addEventListener) mqReduce.addEventListener('change', onMotionChange);
    if (mqPin.addEventListener) mqPin.addEventListener('change', measure);
  };
})();
