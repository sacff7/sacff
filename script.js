/* SACFF — small progressive enhancements. The page is fully usable without JS. */
(function () {
  'use strict';

  /* =====================================================================
     FORM DELIVERY — configure this one line, then everything below works.

     Paste the Apps Script web-app URL you get at the end of the setup in
     google-apps-script/README.md. It handles both forms:
       · Contact form     -> emails sacff7@gmail.com
       · Prayer requests  -> appends a row to the Google Sheet (+ notifies)

     Until it is filled in, the contact form falls back to opening the
     visitor's own mail app addressed to sacff7@gmail.com, and the prayer
     form explains that it isn't connected yet. Nothing is silently lost.
     ===================================================================== */
  var ENDPOINT = 'https://script.google.com/macros/s/AKfycbwtV8sMDc72dqmhk-UMJCNBMzpBAU700DLtEM3lZhKGLHTRchq6uTCOVXEQyWq1YhNa/exec';                       // <-- paste the /exec URL here
  var CONTACT_EMAIL = 'sacff7@gmail.com';

  /* ---------------------------------------------------- mobile nav toggle */
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('site-nav');

  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    });

    nav.addEventListener('click', function (e) {
      if (e.target.closest('a')) closeNav();
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closeNav();
    });
  }

  function closeNav() {
    if (!nav || !nav.classList.contains('is-open')) return;
    nav.classList.remove('is-open');
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-label', 'Open menu');
  }

  /* --------------------------------------------- back to top of the page
     `#top` is the sticky header, which is pinned to the viewport and so is
     never out of view. A plain fragment jump to it therefore barely moves:
     from the foot of the page the logo scrolled 88px — the scroll-padding —
     and stopped. These links scroll the window itself instead.

     This is what the logo does on mobile, where the nav is behind the
     hamburger and the crest is the obvious way home. */
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  document.addEventListener('click', function (e) {
    var a = e.target.closest('a[href="#top"]');
    if (!a) return;
    e.preventDefault();
    closeNav();
    window.scrollTo({ top: 0, behavior: reduceMotion.matches ? 'auto' : 'smooth' });
    // Don't leave "#top" in the address bar for a position that is just 0.
    if (location.hash) {
      history.replaceState(null, '', location.pathname + location.search);
    }
  });

  /* ------------------------------------- highlight the section in view */
  var links = Array.prototype.slice.call(
    document.querySelectorAll('.site-nav a[href^="#"]')
  );
  var sections = links
    .map(function (a) { return document.querySelector(a.getAttribute('href')); })
    .filter(Boolean);

  /* The Home link points at #top — the sticky header — which sits at the very
     top of the document and so can never cross the mid-viewport band below.
     Watching the hero instead is what makes Home light up again when someone
     returns to the top (by logo, by nav, or by scrolling). */
  var hero = document.querySelector('.hero');

  if ('IntersectionObserver' in window && sections.length) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var id = entry.target === hero ? '#top' : '#' + entry.target.id;
        links.forEach(function (a) {
          a.classList.toggle('is-current', a.getAttribute('href') === id);
        });
      });
    }, { rootMargin: '-45% 0px -50% 0px' });

    sections.forEach(function (s) { observer.observe(s); });
    if (hero) observer.observe(hero);
  }

  /* ===================== recurring event dates =========================
     The three services fall on fixed Saturdays of every month (1st, 2nd and
     4th), so each card works out its own next date on load and the page can
     never advertise a service that has already happened.

     Only cards carrying data-recurs are touched. One-off events — Indian
     Christian Day — have no such attribute and are left exactly as authored.
     The dates written into the HTML stay truthful on their own, so if this
     script never runs a visitor still sees a sensible date.
     ===================================================================== */
  var SATURDAY = 6;
  var MONTH_ABBR = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
                    'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'];

  /** The nth Saturday of a given month. Month may be 12+ to roll into next year. */
  function nthSaturday(year, month, n) {
    var first = new Date(year, month, 1);
    var lead = (SATURDAY - first.getDay() + 7) % 7;
    return new Date(year, month, 1 + lead + (n - 1) * 7);
  }

  /** Next nth Saturday that hasn't passed — the day itself still counts. */
  function nextNthSaturday(n, from) {
    var today = new Date(from.getFullYear(), from.getMonth(), from.getDate());
    var d = nthSaturday(today.getFullYear(), today.getMonth(), n);
    if (d < today) d = nthSaturday(today.getFullYear(), today.getMonth() + 1, n);
    return d;
  }

  function pad2(n) { return (n < 10 ? '0' : '') + n; }

  function isoDay(d) {
    return d.getFullYear() + '-' + pad2(d.getMonth() + 1) + '-' + pad2(d.getDate());
  }

  var recurring = Array.prototype.slice
    .call(document.querySelectorAll('.event-card[data-recurs]'))
    .map(function (card) {
      return { card: card, n: parseInt(card.getAttribute('data-recurs'), 10) };
    })
    .filter(function (x) { return x.n >= 1 && x.n <= 4; });

  if (recurring.length) {
    var today = new Date();

    recurring.forEach(function (x) {
      x.date = nextNthSaturday(x.n, today);

      var time = x.card.querySelector('time');
      if (time) {
        var at = x.card.getAttribute('data-at');
        time.setAttribute('datetime', isoDay(x.date) + (at ? 'T' + at : ''));
        // en-US explicitly, so the format matches the design whatever the
        // visitor's own locale happens to be.
        time.textContent = x.date.toLocaleDateString('en-US', {
          weekday: 'short', month: 'short', day: 'numeric', year: 'numeric',
        });
      }

      var chip = x.card.querySelector('.date-chip');
      if (chip) {
        var mon = chip.querySelector('span');
        var day = chip.querySelector('strong');
        if (mon) mon.textContent = MONTH_ABBR[x.date.getMonth()];
        if (day) day.textContent = pad2(x.date.getDate());
      }
    });

    // Recomputed dates fall out of the authored order every month, so re-sort
    // the cards — "Upcoming Events" should read soonest first.
    var grid = recurring[0].card.parentNode;
    recurring
      .slice()
      .sort(function (a, b) { return a.date - b.date; })
      .forEach(function (x) { grid.appendChild(x.card); });
  }

  /* ========================== form submission ========================== */
  var loadedAt = Date.now();

  document.querySelectorAll('[data-endpoint-form]').forEach(function (form) {
    var kind = form.getAttribute('data-endpoint-form');   // 'contact' | 'prayer'
    var status = form.querySelector('.form-status');
    var button = form.querySelector('button[type="submit"]');
    var original = button ? button.textContent : '';

    form.addEventListener('submit', function (e) {
      e.preventDefault();

      if (!form.checkValidity()) {
        say('Please complete the highlighted fields.', 'error');
        var bad = form.querySelector(':invalid');
        if (bad) bad.focus();
        return;
      }

      // Spam checks: honeypot filled, or submitted implausibly fast.
      var trap = form.querySelector('.hp input');
      if ((trap && trap.value) || Date.now() - loadedAt < 2500) {
        say('Thank you — your message has been received.');
        form.reset();
        return;
      }

      if (!ENDPOINT) { unconfigured(); return; }

      var data = new URLSearchParams(new FormData(form));
      data.set('form', kind);
      data.set('page', location.href);

      busy(true);
      // URL-encoded keeps this a "simple" request, so no CORS preflight —
      // which Apps Script web apps do not answer.
      fetch(ENDPOINT, { method: 'POST', body: data })
        .then(function (r) { return r.json().catch(function () { return { ok: r.ok }; }); })
        .then(function (res) {
          if (!res || res.ok === false) throw new Error(res && res.error);
          say(kind === 'prayer'
            ? 'Your request has been received. We will be praying with you.'
            : 'Thank you. Someone from the fellowship will be in touch.');
          form.reset();
        })
        .catch(function () {
          say(kind === 'prayer'
            ? 'Sorry — that did not send. Please email ' + CONTACT_EMAIL + ' instead.'
            : 'Sorry — that did not send.', 'error');
          if (kind === 'contact') mailtoFallback();
        })
        .then(function () { busy(false); });
    });

    function busy(on) {
      if (!button) return;
      button.disabled = on;
      button.textContent = on ? 'Sending…' : original;
    }

    function say(msg, state) {
      if (!status) return;
      if (state) status.dataset.state = state; else delete status.dataset.state;
      status.textContent = msg;
    }

    function unconfigured() {
      if (kind === 'contact') {
        say('Opening your mail app…');
        mailtoFallback();
      } else {
        say('This form is not connected yet. Please email ' + CONTACT_EMAIL +
            ' with your request.', 'error');
      }
    }

    // Hands the message to the visitor's own mail client, pre-filled. Used when
    // no endpoint is configured or the request fails, so nothing is lost.
    function mailtoFallback() {
      var get = function (n) {
        var el = form.querySelector('[name="' + n + '"]');
        return el ? el.value : '';
      };
      var body =
        'Name: ' + get('name') + '\n' +
        'Email: ' + get('email') + '\n' +
        'About: ' + get('topic') + '\n\n' + get('message');
      window.location.href = 'mailto:' + CONTACT_EMAIL +
        '?subject=' + encodeURIComponent('Website enquiry — ' + (get('topic') || 'SACFF')) +
        '&body=' + encodeURIComponent(body);
    }
  });

  /* ============================== giving ==============================
     PayPal JS SDK, using SACFF's own client id (a public identifier, not a
     secret). The SDK is only fetched once the Giving section is scrolled into
     view, so visitors who never reach it aren't served a third-party script.
     Zelle and cheque details need no JavaScript at all and always show.
     ==================================================================== */
  var PAYPAL_CLIENT_ID = 'AUyMT9V09ADxRrDnhj4X1_0ZK78guY8LfQPa-PaWnZRoi3F2ULvY9zaDvjov4BHVH4jA6gk5a2vN1wZ9';

  var giveSection = document.getElementById('giving');
  var amountInput = document.getElementById('give-amount');
  var payContainer = document.getElementById('paypal-buttons');
  var giveStatus = document.getElementById('give-status');

  /* The same `data-paypal` attribute the CSS reads. While it is anything other
     than "on", the SDK is never requested at all — no third-party script, no
     cookies, and no way to start a payment against an account that can't
     settle it. The "Coming soon" panel is already in the markup. */
  var paypalOn = !!giveSection && giveSection.dataset.paypal === 'on';

  if (paypalOn && amountInput && payContainer) {
    // Preset buttons just fill the amount field, which stays the single source
    // of truth — createOrder reads it at click time, so no button re-render.
    document.querySelectorAll('.amount-presets button').forEach(function (b) {
      b.addEventListener('click', function () {
        amountInput.value = b.getAttribute('data-amount');
        markActivePreset();
        amountInput.dispatchEvent(new Event('input'));
      });
    });
    amountInput.addEventListener('input', markActivePreset);
    markActivePreset();

    if ('IntersectionObserver' in window) {
      var payObserver = new IntersectionObserver(function (entries, obs) {
        if (entries.some(function (e) { return e.isIntersecting; })) {
          obs.disconnect();
          loadPayPal();
        }
      }, { rootMargin: '200px' });
      payObserver.observe(giveSection);
    } else {
      loadPayPal();
    }
  }

  function markActivePreset() {
    document.querySelectorAll('.amount-presets button').forEach(function (b) {
      var on = b.getAttribute('data-amount') === String(amountInput.value);
      b.classList.toggle('is-active', on);
      b.setAttribute('aria-pressed', String(on));
    });
  }

  /** Returns the amount as a PayPal-safe decimal string, or null if invalid. */
  function giftAmount() {
    var n = parseFloat(amountInput.value);
    if (!isFinite(n) || n < 1 || n > 25000) return null;
    return n.toFixed(2);
  }

  function loadPayPal() {
    var s = document.createElement('script');
    s.src = 'https://www.paypal.com/sdk/js?client-id=' + PAYPAL_CLIENT_ID +
            '&currency=USD&components=buttons&disable-funding=venmo,paylater,applepay';
    s.onload = renderPayPal;
    s.onerror = function () {
      payContainer.innerHTML = '<p class="paypal-placeholder">Card giving is ' +
        'unavailable right now — please use Zelle or a cheque.</p>';
    };
    document.head.appendChild(s);
  }

  function renderPayPal() {
    if (!window.paypal || !window.paypal.Buttons) return;
    payContainer.innerHTML = '';

    window.paypal.Buttons({
      style: { layout: 'vertical', color: 'gold', shape: 'rect', label: 'donate' },

      createOrder: function (data, actions) {
        var value = giftAmount();
        if (!value) {
          tell('Please enter an amount between $1 and $25,000.', 'error');
          return Promise.reject(new Error('invalid amount'));
        }
        tell('');
        return actions.order.create({
          purchase_units: [{
            amount: { value: value, currency_code: 'USD' },
            description: 'Donation to San Antonio Christian Family Fellowship',
          }],
          application_context: { shipping_preference: 'NO_SHIPPING' },
        });
      },

      onApprove: function (data, actions) {
        return actions.order.capture().then(function (details) {
          var first = '';
          try { first = details.payer.name.given_name; } catch (e) {}
          tell('Thank you' + (first ? ', ' + first : '') +
               '. Your gift has been received — God bless you.');
        });
      },

      onCancel: function () { tell('No payment was taken.'); },

      onError: function () {
        tell('Something went wrong with the payment. Please try Zelle or a cheque, ' +
             'or email rectorarya@gmail.com.', 'error');
      },
    }).render('#paypal-buttons');
  }

  function tell(msg, state) {
    if (!giveStatus) return;
    if (state) giveStatus.dataset.state = state; else delete giveStatus.dataset.state;
    giveStatus.textContent = msg;
  }

  /* =============================== RSVP ===============================
     The RSVP page posts straight to the Google Form's formResponse endpoint,
     aimed at a hidden iframe — Google allows the post but not a cross-origin
     read, so the iframe's load event is the only completion signal available.

     The form asks for names, phone, email and city as one paragraph answer;
     this collects them as four fields and joins them before sending.
     ==================================================================== */
  var rsvpForm = document.getElementById('rsvp-form');

  if (rsvpForm) {
    var rsvpDone = document.getElementById('rsvp-done');
    var rsvpSink = document.getElementById('gform-sink');
    var rsvpDetails = document.getElementById('rsvp-details');
    var rsvpStatus = rsvpForm.querySelector('.form-status');
    var rsvpButton = rsvpForm.querySelector('button[type="submit"]');
    var rsvpSent = false;

    var val = function (id) {
      var el = document.getElementById(id);
      return el ? el.value.trim() : '';
    };

    rsvpForm.addEventListener('submit', function (e) {
      if (!rsvpForm.checkValidity()) {
        e.preventDefault();
        rsvpStatus.dataset.state = 'error';
        rsvpStatus.textContent = 'Please complete the highlighted fields.';
        var bad = rsvpForm.querySelector(':invalid');
        if (bad) bad.focus();
        return;
      }

      // Google's single paragraph question, assembled from the four inputs.
      rsvpDetails.value =
        'Name(s): ' + val('rsvp-name') +
        ' | Phone: ' + val('rsvp-phone') +
        ' | Email: ' + val('rsvp-email') +
        ' | City: ' + val('rsvp-city');

      rsvpSent = true;
      delete rsvpStatus.dataset.state;
      rsvpStatus.textContent = 'Sending your RSVP…';
      if (rsvpButton) {
        rsvpButton.disabled = true;
        rsvpButton.textContent = 'Sending…';
      }
      // Not prevented: the browser posts the form into the hidden iframe.
    });

    // Fires once the post to Google has completed. The initial about:blank load
    // is ignored via the rsvpSent flag.
    rsvpSink.addEventListener('load', function () {
      if (!rsvpSent) return;
      showRsvpThanks();
    });

    // If the iframe never loads (blocked frame, offline), don't leave the
    // visitor staring at "Sending…" forever.
    rsvpForm.addEventListener('submit', function () {
      setTimeout(function () {
        if (rsvpSent && !rsvpDone.hidden) return;
        if (rsvpSent) showRsvpThanks();
      }, 6000);
    });

    function showRsvpThanks() {
      rsvpSent = false;
      var count = val('rsvp-count');
      var attend = rsvpForm.querySelector('input[name^="entry."]:checked');
      var summary = document.getElementById('rsvp-done-summary');
      if (summary) {
        summary.textContent =
          (attend && attend.value === 'Yes'
            ? 'We have you down for ' + count + (count === '1' ? ' person' : ' people')
            : 'Thank you for letting us know') +
          ', under ' + val('rsvp-name') + '.';
      }
      rsvpForm.hidden = true;
      rsvpDone.hidden = false;
      rsvpDone.scrollIntoView({ block: 'center' });
      rsvpDone.setAttribute('tabindex', '-1');
      rsvpDone.focus();
    }
  }

  /* ========================= copy-to-clipboard =========================
     Zelle has no public deep link, so a donor always types the recipient and
     memo into their own banking app by hand. These buttons remove that typing
     (and the mistyping) — the closest thing to a one-tap Zelle payment that
     any website can actually offer.
     ==================================================================== */
  document.querySelectorAll('.copy-btn').forEach(function (btn) {
    var original = btn.textContent;
    var timer;

    btn.addEventListener('click', function () {
      var text = btn.getAttribute('data-copy') || '';

      done(copy(text));

      function done(ok) {
        clearTimeout(timer);
        btn.textContent = ok ? 'Copied' : 'Press ⌘C';
        btn.classList.toggle('is-copied', ok);
        timer = setTimeout(function () {
          btn.textContent = original;
          btn.classList.remove('is-copied');
        }, 2000);
      }
    });
  });

  /** Clipboard API where available, with a selection fallback for old/HTTP. */
  function copy(text) {
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text);
      return true;
    }
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.setAttribute('readonly', '');
    ta.style.cssText = 'position:fixed;top:-1000px;opacity:0';
    document.body.appendChild(ta);
    ta.select();
    var ok = false;
    try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
    document.body.removeChild(ta);
    return ok;
  }

  /* ============================== gallery ==============================
     A native <dialog> does the heavy lifting — Escape to close, focus
     trapping and the backdrop are the browser's job, not ours. Only the
     large JPEG for the photo being viewed is ever fetched.
     ==================================================================== */
  var galData = document.getElementById('gallery-data');
  var lb = document.getElementById('lightbox');

  if (galData && lb && typeof lb.showModal === 'function') {
    var shots = JSON.parse(galData.textContent);
    var lbImg = document.getElementById('lb-img');
    var lbCap = document.getElementById('lb-cap');
    var at = 0;
    var opener = null;

    function show(i) {
      at = (i + shots.length) % shots.length;      // wraps both ways
      var p = shots[at];
      lbImg.src = 'assets/gallery/' + p.slug + '.jpg';
      lbImg.width = p.lw;
      lbImg.height = p.lh;
      lbImg.alt = p.alt;
      lbCap.textContent = p.alt + '  (' + (at + 1) + ' of ' + shots.length + ')';
      preload(at + 1);                             // next one feels instant
    }

    function preload(i) {
      var p = shots[(i + shots.length) % shots.length];
      var im = new Image();
      im.src = 'assets/gallery/' + p.slug + '.jpg';
    }

    document.getElementById('gal-grid').addEventListener('click', function (e) {
      var btn = e.target.closest('.shot');
      if (!btn) return;
      opener = btn;
      show(parseInt(btn.getAttribute('data-i'), 10));
      lb.showModal();
      lock(true);
    });

    // showModal() dims the page but does not stop it scrolling underneath, so
    // a swipe over the backdrop would otherwise move the grid behind the photo.
    function lock(on) {
      document.documentElement.classList.toggle('lb-open', on);
    }

    // Not every engine fires <dialog>'s `close` event (this was verified in
    // testing), so cleanup runs from an explicit hide() rather than relying on
    // it. `cancel` covers the Escape key, which the browser handles itself.
    function hide() {
      lb.close();
      lbImg.removeAttribute('src');   // drop the large JPEG
      lock(false);
      if (opener) opener.focus();     // most engines restore focus anyway
    }

    lb.addEventListener('click', function (e) {
      var act = e.target.closest('[data-lb]');
      if (act) {
        var a = act.getAttribute('data-lb');
        if (a === 'close') hide();
        if (a === 'prev') show(at - 1);
        if (a === 'next') show(at + 1);
        return;
      }
      // Clicking the dark surround closes; clicking the photo does not.
      if (!e.target.closest('.lb-figure')) hide();
    });

    lb.addEventListener('cancel', function () {
      lbImg.removeAttribute('src');
      lock(false);
      if (opener) opener.focus();
    });

    lb.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft') { e.preventDefault(); show(at - 1); }
      if (e.key === 'ArrowRight') { e.preventDefault(); show(at + 1); }
    });

  }

  /* ------------------------------------------- newsletter (still a stub) */
  document.querySelectorAll('.subscribe').forEach(function (form) {
    var status = form.parentNode.querySelector('.form-status');
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!status) return;
      if (!form.checkValidity()) {
        status.dataset.state = 'error';
        status.textContent = 'Please enter a valid email address.';
        return;
      }
      delete status.dataset.state;
      status.textContent = 'Thank you — you’re on the list.';
      form.reset();
    });
  });

  /* ------------------------------------------------------ footer year */
  var year = document.getElementById('year');
  if (year) year.textContent = String(new Date().getFullYear());
})();
