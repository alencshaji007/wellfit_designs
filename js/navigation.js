/* ==========================================================================
   Wellfit Designs — navigation
   Header states, accessible mobile menu, in-page anchors and the curtain
   transition between pages. Depends on animations.js (WF.scroll / WF.onScroll).
   ========================================================================== */
(function () {
  'use strict';

  var WF = (window.WF = window.WF || {});
  var root = document.documentElement;

  /* ---------- Header: solid after scrolling, hides on the way down ---------- */
  function setupHeader() {
    var header = document.querySelector('.site-header');
    if (!header) return;
    var lastDir = 0;
    var travelled = 0;
    var update = function (y, dy) {
      header.classList.toggle('is-scrolled', y > 24);
      if (root.classList.contains('menu-open')) { header.classList.remove('is-hidden'); return; }
      var dir = dy > 0 ? 1 : dy < 0 ? -1 : lastDir;
      travelled = dir === lastDir ? travelled + Math.abs(dy) : Math.abs(dy);
      lastDir = dir;
      if (y < 160) header.classList.remove('is-hidden');
      else if (dir > 0 && travelled > 60) header.classList.add('is-hidden');
      else if (dir < 0 && travelled > 30) header.classList.remove('is-hidden');
    };
    if (WF.onScroll) WF.onScroll(update);
    update(window.scrollY, 0);
    header.addEventListener('focusin', function () { header.classList.remove('is-hidden'); });
  }

  /* ---------- Mobile menu ---------- */
  function setupMenu() {
    var toggle = document.querySelector('.menu-toggle');
    var menu = document.getElementById('site-menu');
    if (!toggle || !menu) return;
    var lastFocus = null;
    var setBackgroundInert = function (on) {
      document.querySelectorAll('main, .site-footer, .skip-link').forEach(function (el) {
        if (on) el.setAttribute('inert', ''); else el.removeAttribute('inert');
      });
    };

    var closeBtn = menu.querySelector('[data-menu-close]');
    var focusables = function () {
      return Array.prototype.slice.call(menu.querySelectorAll('a[href], button:not([disabled])'));
    };
    var open = function () {
      lastFocus = document.activeElement;
      root.classList.add('menu-open');
      menu.classList.add('is-open');
      menu.removeAttribute('inert');
      setBackgroundInert(true);
      toggle.setAttribute('aria-expanded', 'true');
      toggle.setAttribute('aria-label', 'Close menu');
      document.body.style.overflow = 'hidden';
      if (WF.scroll) WF.scroll.lock();
      var first = closeBtn || menu.querySelector('a[href]');
      if (first) setTimeout(function () { first.focus({ preventScroll: true }); }, 350);
    };
    var close = function (restoreFocus) {
      root.classList.remove('menu-open');
      menu.classList.remove('is-open');
      menu.setAttribute('inert', '');
      setBackgroundInert(false);
      toggle.setAttribute('aria-expanded', 'false');
      toggle.setAttribute('aria-label', 'Open menu');
      document.body.style.overflow = '';
      if (WF.scroll) WF.scroll.unlock();
      if (restoreFocus !== false && lastFocus && lastFocus.focus) lastFocus.focus({ preventScroll: true });
    };
    menu.setAttribute('inert', '');
    if (closeBtn) closeBtn.addEventListener('click', function () { close(); });
    toggle.addEventListener('click', function () {
      if (menu.classList.contains('is-open')) close(); else open();
    });
    document.addEventListener('keydown', function (e) {
      if (!menu.classList.contains('is-open')) return;
      if (e.key === 'Escape') { e.preventDefault(); close(); return; }
      if (e.key === 'Tab') {
        var items = focusables();
        var first = items[0];
        var last = items[items.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
      }
    });
    menu.addEventListener('click', function (e) {
      if (e.target.closest('a[href]')) close(false);
    });
    var wide = window.matchMedia('(min-width: 1101px)');
    var onWide = function (mq) { if (mq.matches && menu.classList.contains('is-open')) close(false); };
    if (wide.addEventListener) wide.addEventListener('change', onWide); else if (wide.addListener) wide.addListener(onWide);
  }

  /* ---------- In-page anchors: eased scroll that clears the fixed header ---------- */
  function scrollToHash(hash, updateHistory) {
    if (!hash || hash === '#') return false;
    var target;
    try { target = document.querySelector(decodeURIComponent(hash)); } catch (err) { return false; }
    if (!target) return false;
    var header = document.querySelector('.site-header');
    var offset = (header ? header.offsetHeight : 0) + 16;
    var top = 0;
    for (var n = target; n; n = n.offsetParent) top += n.offsetTop;   // offsetTop ignores reveal transforms
    var y = top - offset;
    var done = function () {
      if (!target.hasAttribute('tabindex') && !/^(A|BUTTON|INPUT|SELECT|TEXTAREA)$/.test(target.tagName)) target.setAttribute('tabindex', '-1');
      target.focus({ preventScroll: true });
    };
    if (WF.scroll) WF.scroll.scrollTo(y, { done: done });
    else { window.scrollTo(0, y); done(); }
    if (updateHistory) {
      if (location.hash === hash) history.replaceState(null, '', hash);
      else history.pushState(null, '', hash);
    }
    return true;
  }
  WF.scrollToHash = scrollToHash;

  /* ---------- Page curtain transitions ---------- */
  function isInternalPage(a) {
    if (!a || a.target === '_blank' || a.hasAttribute('download') || a.getAttribute('rel') === 'external') return false;
    var href = a.getAttribute('href');
    if (!href || href.charAt(0) === '#' || /^(mailto:|tel:|javascript:)/i.test(href)) return false;
    var url;
    try { url = new URL(a.href, location.href); } catch (err) { return false; }
    if (url.origin !== location.origin && location.protocol !== 'file:') return false;
    if (url.pathname === location.pathname && url.search === location.search && url.hash) return false;
    return /(\.html?$|\/$)/i.test(url.pathname);
  }

  function setupTransitions() {
    // reveal the page if we arrived through a curtain transition
    if (root.classList.contains('is-entering')) {
      requestAnimationFrame(function () {
        requestAnimationFrame(function () { root.classList.add('is-entered'); });
      });
      setTimeout(function () { root.classList.remove('is-entering', 'is-entered'); }, 1300);
    }
    window.addEventListener('pageshow', function (e) {
      if (e.persisted) root.classList.remove('is-leaving', 'is-entering', 'is-entered');
    });

    document.addEventListener('click', function (e) {
      if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      var a = e.target.closest('a[href]');
      if (!a) return;
      // same-page anchors
      var url;
      try { url = new URL(a.href, location.href); } catch (err) { return; }
      if (url.hash && url.pathname === location.pathname && url.search === location.search) {
        if (scrollToHash(url.hash, true)) e.preventDefault();
        return;
      }
      if (WF.reduced || !isInternalPage(a)) return;
      e.preventDefault();
      try { sessionStorage.setItem('wf-nav', '1'); } catch (err) { /* storage unavailable */ }
      root.classList.add('is-leaving');
      setTimeout(function () { window.location.href = a.href; }, 720);
    });
  }

  WF.initNavigation = function () {
    setupHeader();
    setupMenu();
    setupTransitions();
    // honour a hash on arrival once layout has settled
    if (location.hash) {
      window.addEventListener('load', function () { setTimeout(function () { scrollToHash(location.hash, false); }, 60); });
    }
  };
})();
