/**
 * SACFF website form handler.
 *
 * One web app, two jobs:
 *   form=contact  ->  emails CONFIG.NOTIFY_EMAIL, and logs a row for safekeeping
 *   form=prayer   ->  appends a row to the "Prayer Requests" sheet, and emails
 *                     a notification so nothing sits unnoticed
 *
 * This script is CONTAINER-BOUND: it lives inside the Google Sheet, so the
 * spreadsheet it writes to is the one it belongs to, in that account's Drive.
 * Setup instructions: see README.md in this folder.
 */

const CONFIG = {
  NOTIFY_EMAIL: 'sacff7@gmail.com',
  PRAYER_SHEET: 'Prayer Requests',
  CONTACT_SHEET: 'Contact Messages',
  MAX_FIELD_LENGTH: 5000,     // trim runaway input before it reaches the sheet
  NOTIFY_ON_PRAYER: true,     // set false to log prayer requests silently
};

const HEADERS = {
  'Prayer Requests': ['Received', 'Name', 'Email / Phone', 'Category',
                      'Request', 'Sharing', 'Status', 'Notes'],
  'Contact Messages': ['Received', 'Name', 'Email', 'About', 'Message', 'Replied'],
};

/** Browser POSTs land here. */
function doPost(e) {
  try {
    const p = (e && e.parameter) || {};

    // Honeypot: only bots fill a hidden field. Answer 200 so they don't retry.
    if (p.website) return json({ ok: true });

    const kind = String(p.form || '').toLowerCase();
    if (kind === 'prayer') return handlePrayer(p);
    if (kind === 'contact') return handleContact(p);
    return json({ ok: false, error: 'Unknown form type' });
  } catch (err) {
    console.error(err);
    return json({ ok: false, error: String(err) });
  }
}

/** Visiting the /exec URL in a browser confirms the deployment is live. */
function doGet() {
  return json({ ok: true, service: 'SACFF form handler', time: new Date().toISOString() });
}

// ---------------------------------------------------------------- handlers

function handlePrayer(p) {
  const name = clean(p.name) || 'Anonymous';
  const contact = clean(p.contact);
  const category = clean(p.category);
  const request = clean(p.request);
  const sharing = clean(p.sharing);

  if (!request) return json({ ok: false, error: 'Request is empty' });

  sheet(CONFIG.PRAYER_SHEET).appendRow([
    new Date(), name, contact, category, request, sharing, 'New', '',
  ]);

  if (CONFIG.NOTIFY_ON_PRAYER) {
    const confidential = /confidential/i.test(sharing);
    MailApp.sendEmail({
      to: CONFIG.NOTIFY_EMAIL,
      subject: 'Prayer request' + (confidential ? ' (confidential)' : '') + ' — ' + name,
      replyTo: looksLikeEmail(contact) ? contact : CONFIG.NOTIFY_EMAIL,
      body: [
        'A new prayer request came in through sacff.org.',
        '',
        'From:     ' + name,
        'Contact:  ' + (contact || '(not given)'),
        'About:    ' + category,
        'Sharing:  ' + sharing,
        '',
        'Request:',
        request,
        '',
        '— Logged in the Prayer Requests sheet.',
      ].join('\n'),
    });
  }

  return json({ ok: true });
}

function handleContact(p) {
  const name = clean(p.name);
  const email = clean(p.email);
  const topic = clean(p.topic);
  const message = clean(p.message);

  if (!message) return json({ ok: false, error: 'Message is empty' });

  MailApp.sendEmail({
    to: CONFIG.NOTIFY_EMAIL,
    subject: 'Website enquiry — ' + (topic || 'SACFF'),
    replyTo: looksLikeEmail(email) ? email : CONFIG.NOTIFY_EMAIL,
    body: [
      'A message came in through the sacff.org contact form.',
      '',
      'Name:   ' + name,
      'Email:  ' + email,
      'About:  ' + topic,
      '',
      message,
    ].join('\n'),
  });

  // Also logged, so a message is never lost to a full or filtered mailbox.
  sheet(CONFIG.CONTACT_SHEET).appendRow([new Date(), name, email, topic, message, '']);

  return json({ ok: true });
}

// ----------------------------------------------------------------- helpers

/** Returns the named sheet, creating it with frozen headers on first use. */
function sheet(name) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sh = ss.getSheetByName(name);
  if (!sh) {
    sh = ss.insertSheet(name);
    const head = HEADERS[name];
    if (head) {
      sh.appendRow(head);
      sh.getRange(1, 1, 1, head.length).setFontWeight('bold');
      sh.setFrozenRows(1);
      sh.setColumnWidth(head.indexOf('Request') + 1 || 5, 420);
    }
  }
  return sh;
}

/**
 * Trims, caps length, and defuses anything the spreadsheet would evaluate as a
 * formula — a leading = + - @ turns user text into a live cell otherwise.
 */
function clean(v) {
  let s = String(v == null ? '' : v).trim();
  if (s.length > CONFIG.MAX_FIELD_LENGTH) {
    s = s.slice(0, CONFIG.MAX_FIELD_LENGTH) + '… (truncated)';
  }
  if (/^[=+\-@\t\r]/.test(s)) s = "'" + s;
  return s;
}

function looksLikeEmail(s) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(String(s || '').trim());
}

function json(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
