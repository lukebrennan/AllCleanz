(function () {
  'use strict';

  var doc = document.documentElement;
  doc.classList.remove('no-js');

  var header = document.querySelector('.header');
  var nav = document.getElementById('site-nav');
  var toggle = document.querySelector('.nav-toggle');
  var mobileQuery = window.matchMedia('(max-width: 1100px)');

  /* Sticky header shadow */
  function onScroll() {
    if (header) header.classList.toggle('is-scrolled', window.scrollY > 8);
  }
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  /* Mobile menu */
  function setMenu(open) {
    if (!nav || !toggle) return;
    if (open) {
      nav.style.setProperty('--nav-top', header.getBoundingClientRect().bottom + 'px');
    }
    nav.classList.toggle('is-open', open);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    document.body.classList.toggle('nav-open', open);
  }

  if (toggle) {
    toggle.addEventListener('click', function () {
      setMenu(toggle.getAttribute('aria-expanded') !== 'true');
    });
  }

  /* Services dropdown */
  document.querySelectorAll('.has-dropdown').forEach(function (item) {
    var btn = item.querySelector('.dropdown-toggle');
    if (!btn) return;
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = !item.classList.contains('is-open');
      item.classList.toggle('is-open', open);
      btn.setAttribute('aria-expanded', String(open));
    });
  });

  document.addEventListener('click', function (e) {
    if (mobileQuery.matches) return;
    document.querySelectorAll('.has-dropdown.is-open').forEach(function (item) {
      if (!item.contains(e.target)) {
        item.classList.remove('is-open');
        item.querySelector('.dropdown-toggle').setAttribute('aria-expanded', 'false');
      }
    });
  });

  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    document.querySelectorAll('.has-dropdown.is-open').forEach(function (item) {
      item.classList.remove('is-open');
      item.querySelector('.dropdown-toggle').setAttribute('aria-expanded', 'false');
    });
    if (toggle && toggle.getAttribute('aria-expanded') === 'true') {
      setMenu(false);
      toggle.focus();
    }
  });

  /* Close the mobile menu after following an in-page link, or when resizing to desktop */
  if (nav) {
    nav.addEventListener('click', function (e) {
      var link = e.target.closest('a');
      if (link && link.getAttribute('href').charAt(0) === '#') setMenu(false);
    });
  }
  mobileQuery.addEventListener('change', function (e) {
    if (!e.matches) setMenu(false);
  });

  /* Seamless ticker: duplicate the track contents */
  var track = document.querySelector('.ticker__track');
  if (track) track.innerHTML += track.innerHTML;

  /* Reveal on scroll */
  var revealEls = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    revealEls.forEach(function (el, i) {
      el.style.transitionDelay = (i % 4) * 70 + 'ms';
      io.observe(el);
    });
  } else {
    revealEls.forEach(function (el) { el.classList.add('is-visible'); });
  }

  /* Quote form: one question per step. Not connected to an inbox yet, but the
     confirmation offers a pre-filled WhatsApp message that does reach the business. */
  var quote = document.getElementById('quote-form');
  if (quote) {
    var steps = Array.prototype.slice.call(quote.querySelectorAll('.quote__step'));
    var backBtn = quote.querySelector('.quote__back');
    var nextBtn = quote.querySelector('.quote__next');
    var submitBtn = quote.querySelector('.quote__submit');
    var quoteNav = quote.querySelector('.quote__nav');
    var bar = quote.querySelector('.quote__bar span');
    var stepNum = quote.querySelector('[data-step-num]');
    var stepTotal = quote.querySelector('[data-step-total]');
    var count = quote.querySelector('.quote__count');
    var done = quote.querySelector('.quote__done');
    // Services that are always a one off visit skip the "how often" step
    var oneOffServices = ['End of Tenancy', 'Oven Cleaning', 'Carpet & Upholstery Cleaning'];
    var current = 0;

    var value = function (name) {
      var checked = quote.querySelector('input[name="' + name + '"]:checked');
      return checked ? checked.value : '';
    };
    var activeSteps = function () {
      return steps.filter(function (step) {
        return step.dataset.step !== 'frequency' || oneOffServices.indexOf(value('service')) === -1;
      });
    };

    var show = function (index, focus) {
      var list = activeSteps();
      current = index;
      steps.forEach(function (step) { step.hidden = step !== list[index]; });
      var last = index === list.length - 1;
      backBtn.hidden = index === 0;
      nextBtn.hidden = last;
      submitBtn.hidden = !last;
      stepNum.textContent = index + 1;
      stepTotal.textContent = list.length;
      bar.style.width = ((index + 1) / list.length * 100) + '%';
      if (focus) {
        var target = list[index].querySelector('input:checked') || list[index].querySelector('input');
        if (target) target.focus();
      }
    };

    var validate = function (step) {
      var ok = true;
      var error = step.querySelector('.quote__error');
      if (step.dataset.step === 'service') ok = !!value('service');
      if (step.dataset.step === 'frequency') ok = !!value('frequency');
      if (step.dataset.step === 'property') {
        var type = value('property');
        ok = !!type && !!value(type === 'Home' ? 'size_home' : 'size_business');
      }
      if (step.dataset.step === 'details') {
        var firstInvalid = null;
        step.querySelectorAll('input, textarea').forEach(function (el) {
          var valid = el.checkValidity();
          el.closest('.field').classList.toggle('is-invalid', !valid);
          el.setAttribute('aria-invalid', String(!valid));
          if (!valid && !firstInvalid) firstInvalid = el;
        });
        if (firstInvalid) firstInvalid.focus();
        ok = !firstInvalid;
      }
      if (error) error.hidden = ok;
      return ok;
    };

    var next = function () {
      var list = activeSteps();
      if (!validate(list[current])) return;
      if (current < list.length - 1) show(current + 1, true);
    };

    nextBtn.addEventListener('click', next);
    backBtn.addEventListener('click', function () { show(current - 1, true); });

    quote.addEventListener('change', function (e) {
      var input = e.target;
      if (input.type !== 'radio') return;
      var step = input.closest('.quote__step');
      var error = step.querySelector('.quote__error');
      if (error) error.hidden = true;
      if (input.name === 'property') {
        quote.querySelectorAll('.quote__size').forEach(function (group) {
          group.hidden = group.dataset.sizeFor !== input.value;
        });
        return;
      }
      if (input.name === 'service') show(current, false);
      // Single question steps move on by themselves once answered
      if (input.name === 'service' || input.name === 'frequency' || input.name.indexOf('size_') === 0) {
        setTimeout(next, 220);
      }
    });

    quote.addEventListener('input', function (e) {
      var field = e.target.closest('.field');
      if (field && field.classList.contains('is-invalid') && e.target.checkValidity()) {
        field.classList.remove('is-invalid');
        e.target.setAttribute('aria-invalid', 'false');
      }
    });

    quote.addEventListener('submit', function (e) {
      e.preventDefault();
      var list = activeSteps();
      if (!validate(list[list.length - 1])) return;

      var type = value('property');
      var rows = [
        ['Service', value('service')],
        ['Property', type + ', ' + value(type === 'Home' ? 'size_home' : 'size_business').toLowerCase()],
        ['How often', oneOffServices.indexOf(value('service')) === -1 ? value('frequency') : 'One off'],
        ['Name', quote.elements.name.value.trim()],
        ['Email', quote.elements.email.value.trim()],
        ['Phone', quote.elements.phone.value.trim()],
        ['Area', quote.elements.area.value.trim()],
        ['Message', quote.elements.message.value.trim()]
      ].filter(function (row) { return row[1]; });

      var summary = done.querySelector('.quote__summary');
      summary.innerHTML = '';
      rows.forEach(function (row) {
        var dt = document.createElement('dt');
        var dd = document.createElement('dd');
        dt.textContent = row[0];
        dd.textContent = row[1];
        summary.appendChild(dt);
        summary.appendChild(dd);
      });
      var text = "Hi All Cleanz, I'd like a quote please.\n" + rows.map(function (row) {
        return row[0] + ': ' + row[1];
      }).join('\n');
      done.querySelector('.quote__wa').href = 'https://wa.me/447721938429?text=' + encodeURIComponent(text);

      steps.forEach(function (step) { step.hidden = true; });
      quoteNav.hidden = true;
      count.hidden = true;
      bar.style.width = '100%';
      done.hidden = false;
      done.focus();
    });

    done.querySelector('.quote__restart').addEventListener('click', function () {
      quote.reset();
      quote.querySelectorAll('.quote__size').forEach(function (group) { group.hidden = true; });
      quote.querySelectorAll('.is-invalid').forEach(function (el) { el.classList.remove('is-invalid'); });
      done.hidden = true;
      quoteNav.hidden = false;
      count.hidden = false;
      show(0, true);
    });

    show(0, false);
  }

  /* Before and after slider */
  document.querySelectorAll('.ba').forEach(function (slider) {
    var range = slider.querySelector('.ba__range');
    var setPos = function (pct) {
      pct = Math.min(100, Math.max(0, pct));
      slider.style.setProperty('--pos', pct + '%');
      range.value = Math.round(pct);
    };
    var fromPointer = function (e) {
      var rect = slider.getBoundingClientRect();
      setPos((e.clientX - rect.left) / rect.width * 100);
    };

    // The range input is kept for keyboard users; pointers (mouse, finger, pen) drive
    // the slider directly, because touch browsers only let you drag a range by its thumb
    var pointer = null; // { id, x, y, sliding }
    slider.addEventListener('pointerdown', function (e) {
      pointer = { id: e.pointerId, x: e.clientX, y: e.clientY, sliding: e.pointerType === 'mouse' };
      if (pointer.sliding) {
        slider.setPointerCapture(e.pointerId);
        fromPointer(e);
      }
    });
    slider.addEventListener('pointermove', function (e) {
      if (!pointer || e.pointerId !== pointer.id) return;
      if (!pointer.sliding) {
        // A finger only takes over once it is clearly moving sideways; vertical swipes scroll the page
        var dx = Math.abs(e.clientX - pointer.x);
        var dy = Math.abs(e.clientY - pointer.y);
        if (dy > dx && dy > 6) { pointer = null; return; }
        if (dx < 6) return;
        pointer.sliding = true;
        slider.setPointerCapture(e.pointerId);
      }
      fromPointer(e);
    });
    slider.addEventListener('pointerup', function (e) {
      // A tap (no real movement) jumps the slider to that spot
      if (pointer && !pointer.sliding && Math.abs(e.clientX - pointer.x) < 6 && Math.abs(e.clientY - pointer.y) < 6) fromPointer(e);
      pointer = null;
    });
    slider.addEventListener('pointercancel', function () { pointer = null; });

    range.addEventListener('input', function () { setPos(Number(range.value)); });
    setPos(Number(range.value));
  });

  /* Footer year */
  document.querySelectorAll('[data-year]').forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });

  /* Under construction page: show which page was requested */
  var ucName = document.querySelector('[data-uc-page]');
  if (ucName) {
    var pages = {
      'about': 'About',
      'services': 'Services',
      'clients': 'Clients',
      'testimonials': 'Testimonials',
      'join-the-team': 'Join the Team',
      'contact': 'Contact Us',
      'end-of-tenancy': 'End of Tenancy',
      'deep-clean': 'Deep Clean',
      'domestic-clean': 'Domestic Clean',
      'carpet-upholstery': 'Advanced Carpet & Upholstery Cleaning',
      'office-cleaning': 'Office Cleaning',
      'after-build-clean': 'After Build Clean',
      'party-cleaning': 'Pre & Post Party Cleaning',
      'oven-cleaning': 'Oven Cleaning',
      'fridge-cleaning': 'Fridge Cleaning',
      'window-cleaning': 'Window Cleaning',
      'bbq-cleaning': 'BBQ Cleaning',
      'jet-washing': 'Jet Washing',
      'gutter-cleaning': 'Gutter Cleaning',
      'car-valeting': 'Car Valeting'
    };
    var slug = new URLSearchParams(window.location.search).get('page');
    var name = pages[slug];
    if (name) {
      ucName.textContent = name;
      ucName.hidden = false;
      document.title = name + ' | Coming Soon | All Cleanz';
      var navLink = document.querySelector('.nav a[href="under-construction.html?page=' + slug + '"]');
      if (navLink) navLink.setAttribute('aria-current', 'page');
    }
  }
})();
