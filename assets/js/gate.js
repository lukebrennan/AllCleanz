/* Preview passcode screen.
 * A deterrent for the pre-launch preview, not real security: the page content
 * still reaches the browser. Remove this file, its <script> tags and the inline
 * gate snippet in each page's <head> when the site goes live. */
(function () {
  'use strict';

  var root = document.documentElement;
  if (!root.classList.contains('gate-locked')) return;

  var STORAGE_KEY = 'allcleanz-preview';
  // SHA-256 of the lowercased passcode, so the passcode itself is not in the source
  var PASS_HASH = 'ca7f9e607643a366736caec95f2636a1e1430681e585d9894677bf5943ecf9a6';

  function sha256Hex(text) {
    var bytes = new TextEncoder().encode(text);
    return crypto.subtle.digest('SHA-256', bytes).then(function (buf) {
      return Array.prototype.map.call(new Uint8Array(buf), function (b) {
        return ('0' + b.toString(16)).slice(-2);
      }).join('');
    });
  }

  var gate = document.createElement('div');
  gate.className = 'gate';
  gate.setAttribute('role', 'dialog');
  gate.setAttribute('aria-modal', 'true');
  gate.setAttribute('aria-labelledby', 'gate-title');
  gate.innerHTML =
    '<form class="gate__card" novalidate>' +
      '<img class="gate__logo" src="assets/img/logo-header.webp" alt="All Cleanz" width="424" height="106">' +
      '<h1 id="gate-title" class="gate__title">Website preview</h1>' +
      '<p class="gate__text">This new website is a private preview. Enter the passcode to take a look.</p>' +
      '<label class="gate__label" for="gate-pass">Passcode</label>' +
      '<input class="gate__input" id="gate-pass" name="passcode" type="password" autocomplete="off" autocapitalize="none" spellcheck="false" required>' +
      '<p class="gate__error" id="gate-error" role="alert" hidden>That passcode isn&rsquo;t right. Please try again.</p>' +
      '<button class="btn btn--primary btn--lg gate__submit" type="submit">View the site</button>' +
    '</form>';
  document.body.appendChild(gate);

  var form = gate.querySelector('form');
  var input = gate.querySelector('#gate-pass');
  var error = gate.querySelector('#gate-error');
  input.setAttribute('aria-describedby', 'gate-error');
  input.focus();

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var attempt = input.value.trim().toLowerCase();
    if (!attempt) {
      input.focus();
      return;
    }
    sha256Hex(attempt).then(function (hash) {
      if (hash === PASS_HASH) {
        try { localStorage.setItem(STORAGE_KEY, '1'); } catch (err) { /* private mode: unlock for this visit only */ }
        root.classList.remove('gate-locked');
        gate.remove();
      } else {
        error.hidden = false;
        input.setAttribute('aria-invalid', 'true');
        input.select();
      }
    });
  });

  input.addEventListener('input', function () {
    error.hidden = true;
    input.removeAttribute('aria-invalid');
  });
})();
