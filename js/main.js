/* ==========================================================================
   Wellfit Designs — page features
   Boots the motion engine and navigation, then wires up: back-to-top,
   FAQ accordion, project filters, the project lightbox and the social-link placeholders.
   ========================================================================== */
(function () {
  'use strict';

  var WF = (window.WF = window.WF || {});
  var root = document.documentElement;
  var prefersReduced = function () { return !!WF.reduced; };

  /* ---------- Back to top ---------- */
  function setupToTop() {
    document.querySelectorAll('[data-to-top]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        if (WF.scroll) WF.scroll.scrollTo(0); else window.scrollTo(0, 0);
        var skip = document.querySelector('.skip-link');
        var main = document.getElementById('main');
        if (main) setTimeout(function () { main.focus({ preventScroll: true }); }, prefersReduced() ? 0 : 900);
        if (skip) skip.blur();
      });
    });
  }

  /* ---------- FAQ: <details> with an eased height animation ---------- */
  function setupFaq() {
    document.querySelectorAll('.faq__item').forEach(function (item) {
      var summary = item.querySelector('summary');
      var panel = item.querySelector('.faq__a');
      if (!summary || !panel || !panel.animate) return;
      var anim = null;
      summary.addEventListener('click', function (e) {
        if (prefersReduced()) return;
        e.preventDefault();
        var closing = !!item.dataset.closing;
        var opening = item.open && !closing;
        // start any interrupted animation from where it visually is
        var from = anim ? panel.getBoundingClientRect().height : null;
        if (anim) anim.cancel();
        item.dataset.closing = '';
        if (!item.open || closing) {
          item.open = true;
          var h = panel.scrollHeight;
          anim = panel.animate([{ height: (from === null ? 0 : from) + 'px', opacity: from === null ? 0 : 1 }, { height: h + 'px', opacity: 1 }], { duration: 520, easing: 'cubic-bezier(.16,1,.3,1)' });
        } else if (opening) {
          var start = from === null ? panel.offsetHeight : from;
          anim = panel.animate([{ height: start + 'px', opacity: 1 }, { height: '0px', opacity: 0 }], { duration: 420, easing: 'cubic-bezier(.65,0,.35,1)' });
          item.dataset.closing = '1';
          anim.onfinish = function () { item.open = false; item.dataset.closing = ''; };
        }
        anim.addEventListener('finish', function () { anim = null; if (WF.refresh) WF.refresh(); });
      });
    });
  }

  /* ---------- Services page: highlight the section in view ---------- */
  function setupScrollSpy() {
    var links = document.querySelectorAll('[data-spy]');
    if (!links.length || !('IntersectionObserver' in window)) return;
    var byId = {};
    links.forEach(function (a) { byId[a.getAttribute('data-spy')] = a; });
    var visible = {};
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { visible[en.target.id] = en.isIntersecting ? en.intersectionRatio : 0; });
      var best = null;
      var bestRatio = 0;
      Object.keys(visible).forEach(function (id) { if (visible[id] > bestRatio) { bestRatio = visible[id]; best = id; } });
      if (!best) return;
      links.forEach(function (a) {
        var on = a.getAttribute('data-spy') === best;
        a.classList.toggle('is-active', on);
        if (on) a.setAttribute('aria-current', 'location'); else a.removeAttribute('aria-current');
      });
    }, { rootMargin: '-30% 0px -50% 0px', threshold: [0, 0.25, 0.5, 0.75, 1] });
    Object.keys(byId).forEach(function (id) { var el = document.getElementById(id); if (el) io.observe(el); });
  }

  /* ---------- Project filters ---------- */
  function setupFilters() {
    var group = document.querySelector('[data-filters]');
    var grid = document.querySelector('[data-portfolio]');
    if (!group || !grid) return;
    var live = document.querySelector('[data-filter-status]');
    var cards = Array.prototype.slice.call(grid.querySelectorAll('[data-category]'));
    group.addEventListener('click', function (e) {
      var btn = e.target.closest('[data-filter]');
      if (!btn) return;
      var value = btn.getAttribute('data-filter');
      group.querySelectorAll('[data-filter]').forEach(function (b) { b.setAttribute('aria-pressed', b === btn ? 'true' : 'false'); });
      var shown = 0;
      cards.forEach(function (card, i) {
        var match = value === 'all' || card.getAttribute('data-category') === value;
        card.classList.toggle('is-hidden', !match);
        card.classList.remove('is-filtering');
        if (match) {
          shown++;
          if (!prefersReduced()) {
            void card.offsetWidth;
            card.style.animationDelay = (shown - 1) * 0.06 + 's';
            card.classList.add('is-filtering');
          }
          // make sure filtered-in cards are visible even if their reveal never fired
          card.classList.add('is-in');
        }
      });
      if (live) live.textContent = 'Showing ' + shown + ' ' + (shown === 1 ? 'project' : 'projects') + '.';
      if (WF.refresh) WF.refresh();
    });
  }

  /* ---------- Lightbox for genuine project photographs ---------- */
  function setupLightbox() {
    var box = document.querySelector('[data-lightbox]');
    if (!box) return;
    var stage = box.querySelector('.lightbox__stage');
    var title = box.querySelector('.lightbox__title');
    var counter = box.querySelector('[data-lightbox-count]');
    var caption = box.querySelector('[data-lightbox-caption]');
    var prev = box.querySelector('[data-lightbox-prev]');
    var next = box.querySelector('[data-lightbox-next]');
    var closeBtn = box.querySelector('[data-lightbox-close]');
    var items = [];
    var index = 0;
    var opener = null;
    var hideTimer = null;

    var render = function () {
      var it = items[index];
      stage.innerHTML = '';
      var pic = document.createElement('picture');
      var s1 = document.createElement('source');
      s1.type = 'image/avif';
      s1.srcset = it.avif;
      var s2 = document.createElement('source');
      s2.type = 'image/webp';
      s2.srcset = it.webp;
      var img = document.createElement('img');
      img.src = it.webp;
      img.alt = it.alt;
      img.width = it.w;
      img.height = it.h;
      img.decoding = 'async';
      img.addEventListener('load', function () { img.classList.add('is-loaded'); });
      pic.appendChild(s1);
      pic.appendChild(s2);
      pic.appendChild(img);
      stage.appendChild(pic);
      if (img.complete) img.classList.add('is-loaded');
      counter.textContent = (index + 1) + ' / ' + items.length;
      caption.textContent = it.caption || '';
      prev.disabled = items.length < 2;
      next.disabled = items.length < 2;
    };
    var open = function (btn) {
      try { items = JSON.parse(btn.getAttribute('data-gallery')); } catch (err) { return; }
      if (!items.length) return;
      opener = btn;
      index = 0;
      title.textContent = btn.getAttribute('data-title') || '';
      clearTimeout(hideTimer);
      render();
      box.hidden = false;
      requestAnimationFrame(function () { box.classList.add('is-open'); });
      document.body.style.overflow = 'hidden';
      if (WF.scroll) WF.scroll.lock();
      setTimeout(function () { closeBtn.focus(); }, 50);
    };
    var close = function () {
      box.classList.remove('is-open');
      document.body.style.overflow = '';
      if (WF.scroll) WF.scroll.unlock();
      hideTimer = setTimeout(function () { box.hidden = true; stage.innerHTML = ''; }, prefersReduced() ? 0 : 500);
      if (opener) opener.focus({ preventScroll: true });
    };
    var go = function (d) { index = (index + d + items.length) % items.length; render(); };

    document.querySelectorAll('[data-gallery]').forEach(function (btn) {
      btn.addEventListener('click', function () { open(btn); });
    });
    closeBtn.addEventListener('click', close);
    prev.addEventListener('click', function () { go(-1); });
    next.addEventListener('click', function () { go(1); });
    box.addEventListener('click', function (e) { if (e.target === box || e.target === stage) close(); });
    document.addEventListener('keydown', function (e) {
      if (box.hidden) return;
      if (e.key === 'Escape') close();
      else if (e.key === 'ArrowRight') go(1);
      else if (e.key === 'ArrowLeft') go(-1);
      else if (e.key === 'Tab') {
        var f = Array.prototype.slice.call(box.querySelectorAll('button:not([disabled])'));
        if (!f.length) return;
        if (e.shiftKey && document.activeElement === f[0]) { e.preventDefault(); f[f.length - 1].focus(); }
        else if (!e.shiftKey && document.activeElement === f[f.length - 1]) { e.preventDefault(); f[0].focus(); }
      }
    });
    var sx = null;
    stage.addEventListener('pointerdown', function (e) { sx = e.clientX; });
    stage.addEventListener('pointerup', function (e) {
      if (sx === null) return;
      var dx = e.clientX - sx;
      sx = null;
      if (Math.abs(dx) > 50 && items.length > 1) go(dx < 0 ? 1 : -1);
    });
  }

  /* ---------- Social links: placeholders until real profile URLs replace href="#" ---------- */
  function setupSocial() {
    document.querySelectorAll('a[data-social][href="#"]').forEach(function (a) {
      a.setAttribute('aria-disabled', 'true');
      a.addEventListener('click', function (e) { e.preventDefault(); });
    });
  }

  /* ---------- Boot ---------- */
  var boot = function () {
    WF.booted = true;
    if (WF.initMotion) WF.initMotion();
    if (WF.initNavigation) WF.initNavigation();
    setupToTop();
    setupFaq();
    setupScrollSpy();
    setupFilters();
    setupLightbox();
    setupSocial();
    var ready = function () { root.classList.add('is-ready'); };
    if (document.fonts && document.fonts.ready) {
      Promise.race([document.fonts.ready, new Promise(function (r) { setTimeout(r, 700); })]).then(ready);
    } else ready();
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
