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
