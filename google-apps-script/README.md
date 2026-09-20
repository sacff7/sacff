# Connecting the forms to sacff7@gmail.com

The website is static — there is no server to send mail. This folder holds a free
Google Apps Script that does both jobs, running under the SACFF Google account
itself. No third-party service, no monthly cost, no data leaving Google.

- **Contact form** → emails `sacff7@gmail.com` (and logs a backup row)
- **Prayer requests** → appends a row to a Google Sheet in that account's Drive

**You have to do this part**, because it needs a login to `sacff7@gmail.com`.
It takes about ten minutes, once.

---

## 1. Create the spreadsheet

1. Sign in to Google as **sacff7@gmail.com**.
2. Go to <https://sheets.new> — a blank spreadsheet opens in that account's Drive.
3. Name it something like **SACFF Website Submissions**.

Don't add any column headings. The script creates the sheets and headers itself
the first time each form is used.

## 2. Add the script

1. In that spreadsheet: **Extensions → Apps Script**.
2. Delete the placeholder `myFunction` code in `Code.gs`.
3. Paste in the entire contents of [`Code.gs`](Code.gs) from this folder.
4. Click **Save** (💾).

It matters that the script is created *from inside the spreadsheet* — that's what
ties it to this sheet.

## 3. Deploy it as a web app

1. **Deploy → New deployment**.
2. Click the gear next to "Select type" and choose **Web app**.
3. Fill in:
   - **Description:** `SACFF website forms`
   - **Execute as:** **Me (sacff7@gmail.com)**
   - **Who has access:** **Anyone**
4. **Deploy**.
5. Google asks you to authorise it. You will see a warning screen — this is normal
   for your own script: click **Advanced → Go to (project name)**, then **Allow**.
   It needs permission to send email as you and to edit this spreadsheet.
6. Copy the **Web app URL**. It ends in `/exec`.

> **"Who has access: Anyone"** sounds alarming but is required — website visitors
> aren't signed in to Google. It lets anyone *send* to the script; it does not let
> anyone read the sheet or your mail.

## 4. Paste the URL into the site

Open [`../script.js`](../script.js), find this line near the top, and paste the
URL between the quotes:

```js
var ENDPOINT = '';                       // <-- paste the /exec URL here
```

Then commit and push. That's it.

## 5. Check it works

1. Paste the `/exec` URL into a browser. You should see
   `{"ok":true,"service":"SACFF form handler",...}`.
2. On the live site, send yourself a test through **both** forms.
3. Confirm the email arrives at `sacff7@gmail.com` and that two tabs have appeared
   in the spreadsheet: **Prayer Requests** and **Contact Messages**.

Wait ~3 seconds before submitting a test — the form rejects anything submitted
faster than that as a bot.

---

## After you change `Code.gs`

A saved edit does **not** go live on its own. You must
**Deploy → Manage deployments → ✏️ → Version: New version → Deploy**.
The URL stays the same.

## Excel rather than Google Sheets

You asked for an Excel sheet. A Google Sheet is the right thing to write to — a
real `.xlsx` file in Drive can't have rows appended to it without opening it.
The Sheet gives you the same result and more:

- **File → Download → Microsoft Excel (.xlsx)** whenever you want the Excel file
- several people can watch it at once, on phones included
- **Tools → Notification settings** will email you the moment a row is added

## Notes on the prayer requests

- The sheet has **Status** and **Notes** columns so the prayer team can track what
  has been prayed over and followed up.
- The form asks whether a request may be shared by name or should stay
  confidential to the prayer team; that answer is recorded in the **Sharing**
  column. Please honour it — people disclose serious things here.
- Anything a visitor types that begins with `=`, `+`, `-` or `@` is prefixed with
  an apostrophe before it's stored, so the spreadsheet treats it as text rather
  than running it as a formula.
- Only share this spreadsheet with people who should read pastoral requests.
  Access is controlled in the sheet's own **Share** button, not by this script.

## Limits

Free Gmail accounts can send roughly **100 emails a day** via Apps Script. Far
beyond anything this site will generate, but if a notification ever fails to
arrive the row is still in the spreadsheet.

## Alternatives, if you'd rather not run a script

| Option | Email | Sheet | Notes |
| --- | --- | --- | --- |
| **Apps Script** (this) | ✅ | ✅ | Free, self-owned, one setup |
| Google Form embedded | ❌ | ✅ | Zero code, but hard to style to match the site |
| Formspree free tier | ✅ | ❌ | 50 submissions/month, needs Zapier for the sheet |
| Netlify Forms | ✅ | ❌ | Requires moving hosting off GitHub Pages |
