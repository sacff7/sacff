#!/usr/bin/env python3
"""Build icd.html and rsvp.html, reusing index.html's header and footer verbatim
so the pages can never drift apart.

Run after changing the header or footer:   python3 tools-build-pages.py
"""
import re

SRC = 'index.html'
s = open(SRC, encoding='utf-8').read()

header = re.search(r'<!-- =+ HEADER =+ -->\n(<header.*?</header>)', s, re.S).group(1)
footer = re.search(r'<!-- =+ FOOTER =+ -->\n(<footer.*?</footer>)', s, re.S).group(1)


def relink(block, current=None):
    """#anchor -> index.html#anchor, and mark whichever nav link is this page."""
    block = re.sub(r'href="#(?!top")([a-z-]+)"', r'href="index.html#\1"', block)
    block = block.replace('href="#top"', 'href="index.html"')
    block = block.replace(' class="is-current"', '')
    if current == 'icd':
        block = block.replace('<a class="nav-event" href="icd.html">',
                              '<a class="nav-event is-current" href="icd.html" aria-current="page">')
    elif current == 'gallery':
        block = block.replace('<a href="gallery.html">',
                              '<a class="is-current" href="gallery.html" aria-current="page">', 1)
    return block


# ICD and its RSVP page both sit under the Indian Christian Day nav item.
HEADER, FOOTER = relink(header, 'icd'), relink(footer, 'icd')
GAL_HEADER, GAL_FOOTER = relink(header, 'gallery'), relink(footer, 'gallery')

# --------------------------------------------------------------- shared facts
VENUE_MAP = ('https://www.google.com/maps/search/?api=1&amp;query='
             'St.+Thomas+Syro+Malabar+Catholic+Church%2C+8333+Braun+Rd%2C'
             '+San+Antonio%2C+TX+78254')

# Google Form. GFORM_VIEW is the canonical public respondent link (kept as a
# fallback); GFORM_POST is the endpoint a form submission is POSTed to.
GFORM_ID = '1FAIpQLScMOsVZuYhxIJ0074iGPoYH7TvH1j9S90DprQ2VRr4Z8OR_fA'
GFORM_VIEW = f'https://docs.google.com/forms/d/e/{GFORM_ID}/viewform'
GFORM_POST = f'https://docs.google.com/forms/d/e/{GFORM_ID}/formResponse'

# Field ids read straight out of the live form's FB_PUBLIC_LOAD_DATA_ —
# never guessed. Re-read them if the questions are ever edited.
F_ATTEND = 'entry.1905292663'   # checkboxes, required: Yes / No / Maybe
F_DETAILS = 'entry.974158068'   # paragraph, required: names, phone, email, city
F_COUNT = 'entry.1175855864'    # linear scale 1-10, required
F_DONATE = 'entry.176170972'    # multiple choice, required: Yes / No / Maybe

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#0d2b56">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="assets/logo-icon-180.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600;700&family=Inter:wght@400;500;600;700&family=Dancing+Script:wght@600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="styles.css">
</head>
<body>

<a class="skip-link" href="#main">Skip to content</a>

<!-- ============================== HEADER ============================== -->
"""

TAIL = """
</main>

<!-- ============================== FOOTER ============================== -->
{footer}

<script src="script.js"></script>
</body>
</html>
"""

CONTACTS = [
    ('Praveen Kanapala', '859 619 2726', '+18596192726'),
    ('Rector Arya', '210 668 5436', '+12106685436'),
    ('Binu George', '954 558 6952', '+19545586952'),
    ('Lizu Thomas', '210 527 7319', '+12105277319'),
    ('Murali Swamidass', '224 877 1791', '+12248771791'),
    ('Prabhakar Mumoorthy', '210 995 5749', '+12109955749'),
]

PROGRAMME = [
    ('Music &amp; Culture Programs',
     'M20 3.2a1 1 0 0 0-1.2-1l-8 1.7a1 1 0 0 0-.8 1v10.4A3.8 3.8 0 0 0 8.4 15 3.7 3.7 0 0 0 4.6 18.6 3.7 3.7 0 0 0 8.4 22.2 3.7 3.7 0 0 0 12.2 18.6V7.7l6-1.3v6.5a3.8 3.8 0 0 0-1.6-.4 3.7 3.7 0 1 0 3.8 3.7V3.2Z'),
    ('Inspiring Presentations',
     'M12 2a3 3 0 0 0-3 3v6a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Zm7 9a7 7 0 0 1-6 6.9V21h3v2H8v-2h3v-3.1A7 7 0 0 1 5 11h2a5 5 0 0 0 10 0h2Z'),
    ('Heritage Displays',
     'M12 1.8 3 7v2h18V7l-9-5.2Zm-1 1.9h2v1.6h1.6v2H13v1.7h-2V7.3H9.4v-2H11V3.7ZM5 11v8H3v2h18v-2h-2v-8h-2v8h-3v-8h-2v8H8v-8H5Z'),
    ('Food &amp; Fellowship',
     'M7 2v8a3 3 0 0 0 2 2.8V22h2V12.8A3 3 0 0 0 13 10V2h-2v8H9.5V2h-2v8H7V2Zm10 0c-1.7 0-3 2-3 4.5 0 2 .9 3.7 2 4.3V22h2V10.8c1.1-.6 2-2.3 2-4.3C20 4 18.7 2 17 2Z'),
]

ICON_PHONE = ('M6.6 10.8a12.6 12.6 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.6 '
              '1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1 '
              '11.4 11.4 0 0 0 .6 3.6 1 1 0 0 1-.25 1Z')
ICON_TICK = 'M9 16.2 4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4L9 16.2Z'
ICON_CAL = ('M7 2v2H5a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2h-2V2h-2v2H9V2H7Zm12 8v9H5v-9h14Z')
ICON_CLOCK = 'M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2Zm1 5h-2v6l5 3 1-1.7-4-2.3Z'
ICON_PIN = ('M12 2a7 7 0 0 0-7 7c0 5.3 7 13 7 13s7-7.7 7-13a7 7 0 0 0-7-7Zm0 9.5A2.5 2.5 0 1 1 '
            '14.5 9 2.5 2.5 0 0 1 12 11.5Z')
ICON_HEART = 'M12 21s-8-4.9-8-10.4A5.1 5.1 0 0 1 12 6.6a5.1 5.1 0 0 1 8 4c0 5.5-8 10.4-8 10.4Z'


# ================================================================== icd.html
icd = HEAD.format(
    title='Indian Christian Day 2026 — SACFF, San Antonio',
    desc=('Indian Christian Day 2026 (Yeshu Bhakti Divas), San Antonio Texas Chapter. '
          'Saturday, September 26, 2026 at St. Thomas Syro Malabar Catholic Church. '
          'Music, presentations, heritage displays, food and fellowship. All are welcome.'),
) + HEADER + f"""

<main id="main">

<!-- ============================ ICD BANNER ============================ -->
<section class="icd-hero" aria-labelledby="icd-title">
  <div class="shell icd-hero-inner">
    <div class="icd-hero-copy">
      <p class="eyebrow">Uniting in faith <i>•</i> Embracing our heritage</p>
      <h1 id="icd-title">Indian Christian Day<br>2026</h1>
      <p class="icd-sub">Yeshu Bhakti Divas <i aria-hidden="true">·</i> San Antonio, Texas Chapter</p>
      <p class="icd-script" aria-hidden="true">Celebrating a 2000-year-old legacy</p>
      <p class="icd-lede">Honoring the legacy of St. Thomas and the Indian Christian
        heritage that continues to shine with Christ’s love, service and hope.</p>
      <div class="icd-actions">
        <a class="btn btn-gold" href="rsvp.html">
          <svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="{ICON_TICK}"/></svg>
          RSVP for this event
        </a>
        <a class="btn btn-light" href="{VENUE_MAP}"
           target="_blank" rel="noopener noreferrer">Get directions</a>
      </div>
    </div>
    <p class="icd-datecard" aria-hidden="true">
      <span>Saturday</span><strong>26</strong><span>Sep 2026</span>
    </p>
  </div>
</section>

<!-- ============================== DETAILS ============================= -->
<section class="icd-facts" aria-label="Event details">
  <div class="shell icd-fact-grid">
    <div class="icd-fact">
      <p class="icd-fact-label">Date</p>
      <p class="icd-fact-main"><time datetime="2026-09-26">Saturday, September 26, 2026</time></p>
    </div>
    <div class="icd-fact">
      <p class="icd-fact-label">Time</p>
      <p class="icd-fact-main">5:00 PM <span>Tea &amp; displays</span></p>
      <p class="icd-fact-main">6:00 PM <span>Programme &amp; dinner</span></p>
    </div>
    <div class="icd-fact">
      <p class="icd-fact-label">Venue</p>
      <p class="icd-fact-main">St. Thomas Syro Malabar Catholic Church</p>
      <p class="icd-fact-sub">8333 Braun Rd<br>San Antonio, TX 78254</p>
      <a class="contact-map" href="{VENUE_MAP}"
         target="_blank" rel="noopener noreferrer">Get directions <span aria-hidden="true">→</span></a>
    </div>
  </div>
</section>

<!-- ============================= PROGRAMME ============================ -->
<section class="icd-programme" aria-labelledby="icd-prog-title">
  <div class="shell">
    <div class="founders-head">
      <h2 class="section-title" id="icd-prog-title">Celebrating a Timeless Faith</h2>
      <p class="lede">A faith that crossed oceans — the same faith, new generations,
        a brighter tomorrow.</p>
    </div>
    <ul class="icd-prog-grid">
{chr(10).join(f'''      <li>
        <span class="pillar-ico" aria-hidden="true">
          <svg viewBox="0 0 24 24"><path d="{d}"/></svg>
        </span>
        <h3>{t}</h3>
      </li>''' for t, d in PROGRAMME)}
    </ul>
  </div>
</section>

<!-- ============================== VIDEO =============================== -->
<section class="icd-video-band" aria-labelledby="icd-video-title">
  <div class="shell icd-video-shell">
    <div class="founders-head">
      <h2 class="section-title" id="icd-video-title">A Faith That Crossed Oceans</h2>
      <p class="lede">Watch the story of Indian Christian Day — the journey of
        St. Thomas and the heritage we gather to celebrate.</p>
    </div>
    <figure class="icd-video">
      <!-- No autoplay: it carries sound and runs nearly four minutes, so it
           plays only when asked. preload="metadata" fetches a few KB of header
           rather than the whole 25 MB on page load. -->
      <video controls playsinline preload="metadata"
             poster="assets/icd-video-poster.jpg"
             width="816" height="464">
        <source src="assets/icd-2026-video.mp4" type="video/mp4">
        <p>Your browser cannot play this video.
          <a href="assets/icd-2026-video.mp4" download>Download it instead (25 MB)</a>.</p>
      </video>
      <figcaption>Indian Christian Day 2026 <i aria-hidden="true">·</i> 3 min 45 sec
        <i aria-hidden="true">·</i> has sound</figcaption>
    </figure>
  </div>
</section>

<!-- ============================== FLYER =============================== -->
<section class="icd-flyer-band" aria-labelledby="icd-flyer-title">
  <div class="shell icd-flyer-grid">
    <div>
      <h2 class="section-title" id="icd-flyer-title">The Invitation</h2>
      <p class="lede">All are welcome — families, youth, children and friends from every
        church and community. Please share this with anyone who would love to come.</p>
      <ul class="about-points">
        <li><strong>Growing in faith</strong> — a celebration rooted in Christ.</li>
        <li><strong>Sharing in love</strong> — across churches, languages and generations.</li>
        <li><strong>Serving together</strong> — one heritage, one hope.</li>
      </ul>
      <p class="icd-links">
        <a href="https://indianchristianday.com" target="_blank" rel="noopener noreferrer">indianchristianday.com</a>
        <i aria-hidden="true">·</i>
        <a href="mailto:indianchristianday@gmail.com">indianchristianday@gmail.com</a>
      </p>
    </div>
    <figure class="icd-flyer">
      <picture>
        <source srcset="assets/icd-flyer.webp" type="image/webp">
        <img src="assets/icd-flyer.jpg" width="900" height="1350"
             alt="Indian Christian Day 2026 flyer: Yeshu Bhakti Divas, San Antonio Texas Chapter, Saturday September 26 2026, 5:00 PM tea and displays, 6:00 PM programme and dinner, at St. Thomas Syro Malabar Catholic Church, 8333 Braun Rd, San Antonio, TX 78254"
             loading="lazy" decoding="async">
      </picture>
      <figcaption>Tap or download to share the full flyer.</figcaption>
    </figure>
  </div>
</section>

<!-- =========================== RSVP + GIVING ========================== -->
<section class="icd-rsvp" id="rsvp" aria-labelledby="icd-rsvp-title">
  <div class="shell">
    <div class="founders-head">
      <h2 class="section-title" id="icd-rsvp-title">RSVP &amp; Contact</h2>
      <p class="lede">Please let us know you are coming — it helps us plan the food and
        seating. Or call any of the organisers below with a question about the day.</p>
    </div>

    <div class="rsvp-panel">
      <div>
        <h3>RSVP online</h3>
        <p>Takes a minute. Tell us how many are coming so there's a place at the table
          for everyone.</p>
      </div>
      <a class="btn btn-gold" href="rsvp.html">
        <svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="{ICON_TICK}"/></svg>
        Open the RSVP form
      </a>
    </div>

    <p class="rsvp-or">or call an organiser</p>

    <ul class="icd-contact-grid">
{chr(10).join(f'''      <li class="person">
        <p class="person-name">{n}</p>
        <a class="person-link" href="tel:{t}">
          <svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="{ICON_PHONE}"/></svg>
          <span>{p}</span>
        </a>
      </li>''' for n, p, t in CONTACTS)}
    </ul>

    <div class="icd-support">
      <div class="give-card">
        <p class="give-badge">No fees</p>
        <h3>Support the day by Zelle</h3>
        <dl class="give-detail">
          <div><dt>Recipient</dt><dd>SACFF</dd></div>
          <div><dt>Recipient phone</dt><dd><a href="tel:+12103520159">(210) 352-0159</a><button class="copy-btn" type="button" data-copy="2103520159" aria-label="Copy the Zelle recipient number">Copy</button></dd></div>
          <div>
            <dt>Memo / reason for payment</dt>
            <dd class="give-memo">Indian Christian Day 2026<button class="copy-btn" type="button" data-copy="Indian Christian Day 2026" aria-label="Copy the payment memo">Copy</button></dd>
          </div>
        </dl>
        <p class="give-note"><strong>Sponsor status</strong> is offered for contributions
          of <strong>$250 or more</strong>. A cheque is just as welcome — card and PayPal
          giving is coming soon.</p>
        <a class="btn btn-gold btn-give btn-block give-card-cta" href="index.html#give">
          <svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="{ICON_HEART}"/></svg>
          Give / Free-will offering towards ICD Event
          <span aria-hidden="true">→</span>
        </a>
      </div>
      <blockquote class="icd-motto">
        <p>Growing in faith.<br>Sharing in love.<br>Serving together.</p>
      </blockquote>
    </div>
  </div>
</section>
""" + TAIL.format(footer=FOOTER)

open('icd.html', 'w', encoding='utf-8').write(icd)
print(f'wrote icd.html   ({len(icd)} bytes)')


# ================================================================= rsvp.html
def radio(field, name, options, first_checked=True):
    out = []
    for i, o in enumerate(options):
        chk = ' checked' if (first_checked and i == 0) else ''
        req = ' required' if i == 0 else ''
        out.append(f'          <label><input type="radio" name="{field}" '
                   f'value="{o}"{chk}{req}> {o}</label>')
    return '\n'.join(out)


rsvp = HEAD.format(
    title='RSVP — Indian Christian Day 2026 | SACFF',
    desc=('RSVP for Indian Christian Day 2026 (Yeshu Bhakti Divas), Saturday '
          'September 26 2026 at St. Thomas Syro Malabar Catholic Church, San Antonio.'),
) + HEADER + f"""

<main id="main">

<!-- ============================ RSVP BANNER =========================== -->
<section class="icd-hero rsvp-hero" aria-labelledby="rsvp-title">
  <div class="shell">
    <p class="eyebrow">Indian Christian Day 2026 <i>•</i> Yeshu Bhakti Divas</p>
    <h1 id="rsvp-title">RSVP</h1>
    <p class="icd-lede">Let us know you are coming — it helps us plan the food and the
      seating. It takes under a minute.</p>
    <ul class="rsvp-facts">
      <li><svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="{ICON_CAL}"/></svg>
        <time datetime="2026-09-26">Saturday, September 26, 2026</time></li>
      <li><svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="{ICON_CLOCK}"/></svg>
        5:00 PM tea &amp; displays <i aria-hidden="true">·</i> 6:00 PM programme &amp; dinner</li>
      <li><svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="{ICON_PIN}"/></svg>
        St. Thomas Syro Malabar Catholic Church, 8333 Braun Rd, San Antonio, TX 78254</li>
    </ul>
  </div>
</section>

<!-- ============================= RSVP FORM ============================ -->
<section class="rsvp-form-band" aria-labelledby="rsvp-form-title">
  <div class="shell rsvp-form-shell">
    <h2 class="sr-only" id="rsvp-form-title">RSVP form</h2>

    <form class="rsvp-form" id="rsvp-form" method="post"
          action="{GFORM_POST}" target="gform-sink">
      <noscript>
        <p class="form-note form-note--warn">This form needs JavaScript to send your
          answers. Please use the
          <a href="{GFORM_VIEW}" target="_blank" rel="noopener noreferrer">Google
          form</a> instead.</p>
      </noscript>

      <fieldset class="field choice">
        <legend>Will you attend on September 26? <span class="req">*</span></legend>
{radio(F_ATTEND, 'attend', ['Yes', 'No', 'Maybe'])}
      </fieldset>

      <div class="field-row">
        <div class="field">
          <label for="rsvp-name">Name(s) <span class="req">*</span></label>
          <input id="rsvp-name" type="text" autocomplete="name" required
                 placeholder="e.g. Thomas &amp; Mary George">
        </div>
        <div class="field">
          <label for="rsvp-phone">Phone <span class="req">*</span></label>
          <input id="rsvp-phone" type="tel" autocomplete="tel" required
                 placeholder="(210) 555-0123">
        </div>
      </div>

      <div class="field-row">
        <div class="field">
          <label for="rsvp-email">Email <span class="req">*</span></label>
          <input id="rsvp-email" type="email" autocomplete="email" required
                 placeholder="you@example.com">
        </div>
        <div class="field">
          <label for="rsvp-city">City <span class="req">*</span></label>
          <input id="rsvp-city" type="text" autocomplete="address-level2" required
                 placeholder="San Antonio">
        </div>
      </div>

      <div class="field">
        <label for="rsvp-count">How many are coming, adults and children? <span class="req">*</span></label>
        <select id="rsvp-count" name="{F_COUNT}" required>
{chr(10).join(f'          <option value="{i}"{" selected" if i == 2 else ""}>{i}</option>' for i in range(1, 11))}
        </select>
        <p class="amount-hint">Choose up to 10. For a larger group, please call an organiser.</p>
      </div>

      <fieldset class="field choice">
        <legend>Would you like to give a free-will offering towards the event?
          <span class="req">*</span></legend>
{radio(F_DONATE, 'donate', ['Yes', 'No', 'Maybe'])}
        <p class="amount-hint">If yes, send it by Zelle to <strong>(210) 352-0159</strong>
          (SACFF), memo <strong>Indian Christian Day 2026</strong>. Sponsor status for
          $250 or more. Nothing is collected on this page.</p>
      </fieldset>

      <!-- Google Forms puts names, phone, email and city in one paragraph answer.
           The four inputs above are collected separately for the visitor's sake and
           combined into this hidden field on submit. -->
      <input type="hidden" name="{F_DETAILS}" id="rsvp-details">

      <button class="btn btn-gold btn-block" type="submit">
        <svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="{ICON_TICK}"/></svg>
        Send my RSVP
      </button>
      <p class="form-status" role="status" aria-live="polite"></p>
      <p class="rsvp-fallback">Trouble with this form? You can also
        <a href="{GFORM_VIEW}" target="_blank" rel="noopener noreferrer">open the
        original Google form</a>.</p>
    </form>

    <!-- Google Forms cannot be read cross-origin, so the post is aimed at this
         hidden frame and its load event is what confirms delivery. -->
    <iframe name="gform-sink" id="gform-sink" title="RSVP submission target" hidden></iframe>

    <div class="rsvp-done" id="rsvp-done" hidden>
      <span class="rsvp-done-tick" aria-hidden="true">
        <svg viewBox="0 0 24 24"><path d="{ICON_TICK}"/></svg>
      </span>
      <h2>Thank you — your RSVP is in.</h2>
      <p id="rsvp-done-summary"></p>
      <p class="rsvp-done-note">We look forward to seeing you on Saturday,
        September 26. If anything changes, call an organiser and we'll update it.</p>
      <p class="rsvp-give-primary">
        <a class="btn btn-gold btn-give" href="index.html#give">
          <svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="{ICON_HEART}"/></svg>
          Give / Free-will offering towards ICD Event
          <span aria-hidden="true">→</span>
        </a>
      </p>
      <p class="rsvp-give-note">Add memo <strong>Indian Christian Day 2026</strong>.
        Sponsor status for <strong>$250 or more</strong>.</p>
      <p class="icd-actions">
        <a class="btn btn-ghost" href="icd.html">Back to event details</a>
        <a class="btn btn-ghost" href="{VENUE_MAP}" target="_blank"
           rel="noopener noreferrer">Get directions</a>
      </p>
    </div>
  </div>
</section>
""" + TAIL.format(footer=FOOTER)

open('rsvp.html', 'w', encoding='utf-8').write(rsvp)
print(f'wrote rsvp.html  ({len(rsvp)} bytes)')


# =============================================================== gallery.html
import json

photos = json.loads(open('gallery-manifest.json', encoding='utf-8').read())

tiles = '\n'.join(f"""      <li>
        <button class="shot" type="button" data-i="{i}"
                aria-label="Open photo {i + 1} of {len(photos)}: {p['alt']}">
          <picture>
            <source srcset="assets/gallery/{p['slug']}-t.webp" type="image/webp">
            <img src="assets/gallery/{p['slug']}-t.jpg"
                 width="{p['w']}" height="{p['h']}" alt="{p['alt']}"
                 loading="lazy" decoding="async">
          </picture>
        </button>
      </li>""" for i, p in enumerate(photos))

gallery = HEAD.format(
    title='Photo Gallery — SACFF, San Antonio',
    desc=('Photographs of San Antonio Christian Family Fellowship — worship '
          'services, Bible study, children’s programmes, Christmas, '
          'picnics and celebrations together.'),
) + GAL_HEADER + f"""

<main id="main">

<!-- =========================== GALLERY INTRO ========================== -->
<section class="gal-hero" aria-labelledby="gal-title">
  <div class="shell gal-hero-inner">
    <p class="eyebrow">Prayer <i>•</i> Word <i>•</i> Worship <i>•</i> Fellowship</p>
    <h1 id="gal-title">Photo Gallery</h1>
    <p class="icd-lede">{len(photos)} photographs of our life together — Saturday
      services and Bible study, the children's programmes, Christmas in one
      another's homes, picnics by the river, and the whole fellowship gathered.</p>
  </div>
</section>

<!-- ============================== GALLERY ============================= -->
<section class="gal-band" aria-label="Photographs">
  <div class="shell">
    <ul class="gal-grid" id="gal-grid">
{tiles}
    </ul>
    <p class="gal-note">Tap any photograph to see it larger. Use the arrow keys
      to move between them.</p>
  </div>
</section>

<!-- Lightbox. A native <dialog> so Escape, focus trapping and the backdrop all
     come from the browser rather than hand-rolled JavaScript. -->
<dialog class="lb" id="lightbox" aria-label="Photo viewer">
  <button class="lb-close" type="button" data-lb="close" aria-label="Close viewer">&times;</button>
  <button class="lb-nav lb-prev" type="button" data-lb="prev" aria-label="Previous photo">&#8249;</button>
  <figure class="lb-figure">
    <img id="lb-img" alt="">
    <figcaption id="lb-cap"></figcaption>
  </figure>
  <button class="lb-nav lb-next" type="button" data-lb="next" aria-label="Next photo">&#8250;</button>
</dialog>

<script id="gallery-data" type="application/json">{json.dumps(
    [{'slug': p['slug'], 'alt': p['alt'], 'lw': p['lw'], 'lh': p['lh']}
     for p in photos])}</script>
""" + TAIL.format(footer=FOOTER)

open('gallery.html', 'w', encoding='utf-8').write(gallery)
print(f'wrote gallery.html ({len(gallery)} bytes, {len(photos)} photos)')


# ===================================================== cache-bust the assets
# A stale styles.css is the classic "works locally, broken on GitHub Pages"
# failure: the HTML updates but a CDN or browser keeps serving yesterday's CSS,
# so new rules silently do nothing. Stamping a content hash into the URL means
# every change produces a new URL that nothing can have cached.
import hashlib

def digest(path):
    return hashlib.sha1(open(path, 'rb').read()).hexdigest()[:10]

stamps = {'styles.css': digest('styles.css'), 'script.js': digest('script.js')}
print('\ncache-busting stamps:')
for f, h in stamps.items():
    print(f'  {f:<12} ?v={h}')

for page in ('index.html', 'icd.html', 'rsvp.html', 'gallery.html'):
    txt = open(page, encoding='utf-8').read()
    n = 0
    for f, h in stamps.items():
        txt, k = re.subn(r'(?<=["\'])' + re.escape(f) + r'(?:\?v=[0-9a-f]+)?(?=["\'])',
                         f'{f}?v={h}', txt)
        n += k
    open(page, 'w', encoding='utf-8').write(txt)
    print(f'  stamped {page} ({n} references)')
print('\nGoogle Form field ids used:')
for label, fid in [('attend', F_ATTEND), ('details', F_DETAILS),
                   ('count', F_COUNT), ('donate', F_DONATE)]:
    print(f'  {label:<8} {fid}')
