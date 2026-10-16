/* ==========================================================================
   Wellfit Designs — page features
   Boots the motion engine and navigation, then wires up: back-to-top,
   FAQ accordion, project filters, the project lightbox and the enquiry form.
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
        if (anim) anim.cancel();
        if (!item.open) {
          item.open = true;
          var h = panel.scrollHeight;
          anim = panel.animate([{ height: '0px', opacity: 0 }, { height: h + 'px', opacity: 1 }], { duration: 520, easing: 'cubic-bezier(.16,1,.3,1)' });
        } else {
          var start = panel.offsetHeight;
          anim = panel.animate([{ height: start + 'px', opacity: 1 }, { height: '0px', opacity: 0 }], { duration: 420, easing: 'cubic-bezier(.65,0,.35,1)' });
          anim.onfinish = function () { item.open = false; };
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
      setTimeout(function () { box.hidden = true; stage.innerHTML = ''; }, prefersReduced() ? 0 : 500);
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

  /* ---------- Enquiry form: validation + delivery ---------- */
  function setupForm() {
    var form = document.querySelector('[data-enquiry-form]');
    if (!form) return;
    form.setAttribute('novalidate', '');
    var status = form.querySelector('.form-status');
    var submit = form.querySelector('[type="submit"]');
    var endpoint = (form.getAttribute('data-endpoint') || '').trim();
    var mailTo = form.getAttribute('data-email') || 'projects@wellfitdesigns.com';
    var fields = Array.prototype.slice.call(form.querySelectorAll('input, select, textarea')).filter(function (f) {
      return f.name && f.type !== 'hidden' && !f.closest('[aria-hidden="true"]');
    });

    var errorFor = function (field) {
      var id = field.getAttribute('aria-describedby');
      if (!id) return null;
      var ids = id.split(/\s+/);
      for (var i = 0; i < ids.length; i++) {
        var el = document.getElementById(ids[i]);
        if (el && el.classList.contains('field__error')) return el;
      }
      return null;
    };
    var messageFor = function (field) {
      var v = field.validity;
      var label = field.getAttribute('data-label') || 'This field';
      if (v.valueMissing) return field.type === 'radio' ? 'Please choose an option.' : label + ' is required.';
      if (v.typeMismatch && field.type === 'email') return 'Please enter a valid email address, for example name@company.com.';
      if (v.patternMismatch && field.type === 'tel') return 'Please enter a valid phone number using digits, spaces, + or -.';
      if (v.tooShort) return label + ' should be at least ' + field.minLength + ' characters.';
      if (v.tooLong) return label + ' should be at most ' + field.maxLength + ' characters.';
      return field.validationMessage || 'Please check this field.';
    };
    var validate = function (field) {
      if (field.type === 'radio') {
        var groupFields = form.querySelectorAll('input[name="' + field.name + '"]');
        var ok = Array.prototype.some.call(groupFields, function (r) { return r.checked; }) || !groupFields[0].required;
        var err = document.getElementById(field.name + '-error');
        groupFields.forEach(function (r) { r.setAttribute('aria-invalid', ok ? 'false' : 'true'); });
        if (err) err.textContent = ok ? '' : 'Please choose an option.';
        return ok;
      }
      if (field.value && typeof field.value === 'string' && field.tagName !== 'SELECT') field.value = field.value.replace(/^\s+/, '');
      var valid = field.checkValidity();
      field.setAttribute('aria-invalid', valid ? 'false' : 'true');
      var err2 = errorFor(field);
      if (err2) err2.textContent = valid ? '' : messageFor(field);
      return valid;
    };
    var show = function (kind, html) {
      status.className = 'form-status form-status--' + kind + ' is-visible';
      status.innerHTML = html;
    };

    fields.forEach(function (f) {
      f.addEventListener('blur', function () { if (f.value || f.dataset.touched) validate(f); f.dataset.touched = '1'; });
      f.addEventListener('input', function () { if (f.getAttribute('aria-invalid') === 'true') validate(f); });
      f.addEventListener('change', function () { if (f.type === 'radio' || f.tagName === 'SELECT') validate(f); });
    });

    var collect = function () {
      var fd = new FormData(form);
      var get = function (k) { return (fd.get(k) || '').toString().trim(); };
      return {
        name: get('name'), company: get('company'), phone: get('phone'), email: get('email'),
        type: get('project_type'), location: get('location'), area: get('area'),
        description: get('description'), contact: get('contact_method'), trap: get('website')
      };
    };

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var firstBad = null;
      var seen = {};
      fields.forEach(function (f) {
        if (f.type === 'radio') { if (seen[f.name]) return; seen[f.name] = true; }
        if (!validate(f) && !firstBad) firstBad = f;
      });
      if (firstBad) {
        show('error', 'Please check the highlighted fields and try again.');
        firstBad.focus();
        return;
      }
      var d = collect();
      if (d.trap) return; // honeypot filled: silently ignore automated submissions

      if (endpoint) {
        submit.disabled = true;
        show('info', 'Sending your enquiry…');
        fetch(endpoint, { method: 'POST', headers: { Accept: 'application/json' }, body: new FormData(form) })
          .then(function (res) {
            if (!res.ok) throw new Error('HTTP ' + res.status);
            show('success', '<strong>Thank you.</strong> Your enquiry has been received and our team will be in touch to discuss the next steps.');
            form.reset();
          })
          .catch(function () {
            show('error', 'Sorry, your enquiry could not be sent just now. Please email <a href="mailto:' + mailTo + '">' + mailTo + '</a> or call <a href="tel:+971521424500">+971 52 142 4500</a>.');
          })
          .then(function () { submit.disabled = false; });
        return;
      }

      // No form backend configured: hand the enquiry to the visitor's email app.
      var lines = [
        'Full name: ' + d.name,
        d.company ? 'Company: ' + d.company : null,
        'Phone: ' + d.phone,
        'Email: ' + d.email,
        'Project type: ' + d.type,
        'Project location: ' + d.location,
        d.area ? 'Approximate project area: ' + d.area : null,
        'Preferred contact method: ' + d.contact,
        '',
        'Project description:',
        d.description
      ].filter(function (l) { return l !== null; });
      var subject = 'Project enquiry – ' + d.type + ' – ' + d.name;
      var href = 'mailto:' + mailTo + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(lines.join('\n'));
      show('info', '<strong>Almost done.</strong> Your email app should open with this enquiry pre-filled — please press <em>Send</em> there to complete it. If nothing opened, email <a href="mailto:' + mailTo + '">' + mailTo + '</a> or call <a href="tel:+971521424500">+971 52 142 4500</a>.');
      window.location.href = href;
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
    setupForm();
    var ready = function () { root.classList.add('is-ready'); };
    if (document.fonts && document.fonts.ready) {
      Promise.race([document.fonts.ready, new Promise(function (r) { setTimeout(r, 700); })]).then(ready);
    } else ready();
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
