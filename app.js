/* Vidcomply — interactions */
(function () {
  'use strict';

  /* nav background on scroll */
  var nav = document.getElementById('nav');
  function onScroll() {
    if (window.scrollY > 24) nav.classList.add('scrolled');
    else nav.classList.remove('scrolled');
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* scroll reveal — manual viewport check (robust across environments) */
  var revealEls = [].slice.call(document.querySelectorAll('.reveal'));
  function settle(el) {
    // After the transition window, hard-lock the end state inline so a
    // throttled/offscreen iframe that froze the transition still ends visible.
    setTimeout(function () {
      el.style.transition = 'none';
      el.style.opacity = '1';
      el.style.transform = 'none';
    }, 820);
  }
  function checkReveal() {
    var vh = window.innerHeight || document.documentElement.clientHeight;
    for (var i = revealEls.length - 1; i >= 0; i--) {
      var el = revealEls[i];
      var r = el.getBoundingClientRect();
      if (r.top < vh * 0.92 && r.bottom > 0) {
        el.classList.add('in');
        settle(el);
        revealEls.splice(i, 1);
      }
    }
  }
  window.addEventListener('scroll', checkReveal, { passive: true });
  window.addEventListener('resize', checkReveal);
  window.__vcCheckReveal = checkReveal;
  checkReveal();
  requestAnimationFrame(checkReveal);
  setTimeout(checkReveal, 300);

  /* workflow tabs */
  var rail = document.getElementById('flowRail');
  if (rail) {
    var tabs = rail.querySelectorAll('.flow-tab');
    var panels = document.querySelectorAll('.flow-panel');
    tabs.forEach(function (tab) {
      tab.addEventListener('click', function () {
        var idx = tab.getAttribute('data-flow');
        tabs.forEach(function (t) { t.classList.remove('active'); });
        tab.classList.add('active');
        panels.forEach(function (p) {
          if (p.getAttribute('data-panel') === idx) { p.classList.add('active', 'in'); }
          else { p.classList.remove('active'); }
        });
      });
    });
  }

  /* generate audio waveform bars */
  document.querySelectorAll('#audioTracks .wave').forEach(function (wave, wi) {
    var n = 56;
    var seed = wi * 7.3 + 1;
    for (var i = 0; i < n; i++) {
      var bar = document.createElement('i');
      var t = i / n;
      // pseudo-random but deterministic amplitude
      var a = Math.abs(Math.sin(seed + i * 0.6) * Math.cos(seed * 0.5 + i * 0.27));
      var h = 14 + a * 86;
      // muted/room tracks: lower amplitude
      if (wave.parentElement.classList.contains('muted')) h = 8 + a * 22;
      else if (!wave.parentElement.classList.contains('lead') && wi > 2) h = 10 + a * 40;
      bar.style.height = h + '%';
      wave.appendChild(bar);
    }
  });

  /* count-up stats — triggered via manual viewport check */
  var counters = [].slice.call(document.querySelectorAll('[data-count]'));
  function animateCount(el) {
    var target = parseFloat(el.getAttribute('data-count'));
    var suffix = el.getAttribute('data-suffix') || '';
    var dur = 1100, start = null;
    function step(ts) {
      if (!start) start = ts;
      var p = Math.min((ts - start) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      var val = Math.round(target * eased);
      el.textContent = val + suffix;
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  function checkCounters() {
    var vh = window.innerHeight || document.documentElement.clientHeight;
    for (var i = counters.length - 1; i >= 0; i--) {
      var el = counters[i];
      var r = el.getBoundingClientRect();
      if (r.top < vh * 0.85 && r.bottom > 0) {
        animateCount(el);
        counters.splice(i, 1);
      }
    }
  }
  window.addEventListener('scroll', checkCounters, { passive: true });
  checkCounters();
  setTimeout(checkCounters, 300);

  /* orchestration progress bars — fill to data-fill% on load (hero centerpiece) */
  function fillBars() {
    var bars = [].slice.call(document.querySelectorAll('.orch-bar i[data-fill]'));
    var pcts = [].slice.call(document.querySelectorAll('.orch-pct[data-pct]'));
    bars.forEach(function (b) {
      setTimeout(function () { b.style.width = b.getAttribute('data-fill') + '%'; }, 450);
      setTimeout(function () { b.style.transition = 'none'; b.style.width = b.getAttribute('data-fill') + '%'; }, 1700);
    });
    pcts.forEach(function (el) {
      var target = parseInt(el.getAttribute('data-pct'), 10), start = null, dur = 1100;
      function step(ts) {
        if (!start) start = ts;
        var p = Math.min((ts - start) / dur, 1);
        el.textContent = Math.round(target * (1 - Math.pow(1 - p, 3))) + '%';
        if (p < 1) requestAnimationFrame(step);
      }
      setTimeout(function () { requestAnimationFrame(step); el.textContent = target + '%'; }, 450);
    });
  }
  window.__vcFillBars = fillBars;
  fillBars();
  /* reel strip: jump-to-tab links activate the target workflow tab */
  document.querySelectorAll('[data-jump-flow]').forEach(function (link) {
    link.addEventListener('click', function () {
      var idx = link.getAttribute('data-jump-flow');
      var tab = document.querySelector('.flow-tab[data-flow="' + idx + '"]');
      if (tab) setTimeout(function () { tab.click(); }, 350);
    });
  });

  /* evaluation license requests */
  var licenseApi = 'https://0op17ziqec.execute-api.eu-west-1.amazonaws.com/license/request';
  document.querySelectorAll('[data-license-form]').forEach(function (form) {
    var emailInput = form.querySelector('[data-license-email]');
    var submit = form.querySelector('[data-license-submit]');
    var msg = form.querySelector('[data-license-msg]');

    form.addEventListener('submit', function (event) {
      event.preventDefault();
      if (!emailInput || !submit || !msg) return;

      var email = emailInput.value.trim();
      if (!email) return;

      submit.disabled = true;
      submit.textContent = 'Sending...';
      msg.textContent = '';
      msg.className = 'trial-msg';

      fetch(licenseApi, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ email: email })
      }).then(function (response) {
        if (response.ok) {
          msg.textContent = 'Check your inbox. The key is on its way.';
          msg.className = 'trial-msg ok';
          emailInput.value = '';
          submit.textContent = 'Sent';
          return;
        }
        return response.json().catch(function () { return {}; }).then(function (data) {
          throw new Error(data.error || 'Something went wrong. Try again.');
        });
      }).catch(function (error) {
        msg.textContent = error.message || 'Could not connect. Check your connection and try again.';
        msg.className = 'trial-msg err';
        submit.disabled = false;
        submit.textContent = 'Request key';
      });
    });
  });
})();
