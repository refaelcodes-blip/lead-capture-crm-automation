# Setup Guide

This guide walks you through configuring all five credentials required to run the workflow. Budget **15–20 minutes** total.

> **Before you start:** make sure you've already imported `lead-capture-crm-automation.json` into n8n. If not, open n8n → Workflows → **Import from File**.

---

## Placeholders you'll replace

During setup you'll fill in these values inside the workflow:

| Placeholder | Where it lives | Where you get it |
|---|---|---|
| `YOUR_ZOHO_CLIENT_ID` | 🔑 Refresh Zoho Token node | Zoho API Console |
| `YOUR_ZOHO_CLIENT_SECRET` | 🔑 Refresh Zoho Token node | Zoho API Console |
| `YOUR_ZOHO_REFRESH_TOKEN` | 🔑 Refresh Zoho Token node | One-time OAuth exchange |
| `YOUR_TELEGRAM_BOT_TOKEN` | 📨 Telegram Notification node (URL) | @BotFather |
| `YOUR_TELEGRAM_CHAT_ID` | 📦 Prepare Payload node (JS code) | @userinfobot |
| `YOUR_GOOGLE_APPS_SCRIPT_ID` | 📊 Log to Google Sheets node (URL) | Apps Script deployment |

---

## 1. Zoho CRM

Zoho uses OAuth 2.0. You'll register a "Self Client" app, then exchange a one-time authorization code for a long-lived refresh token.

### 1.1 Pick the right regional domain ⚠️

This is the #1 source of `invalid_client` errors. Zoho is region-locked — credentials from `zoho.com` do **not** work on `zoho.eu`.

Log into [zoho.com](https://zoho.com) and check your browser's address bar:

| Your URL shows | Use this API Console | Use this accounts URL |
|---|---|---|
| `zoho.com` | https://api-console.zoho.com | `https://accounts.zoho.com/oauth/v2/token` |
| `zoho.eu` | https://api-console.zoho.eu | `https://accounts.zoho.eu/oauth/v2/token` |
| `zoho.in` | https://api-console.zoho.in | `https://accounts.zoho.in/oauth/v2/token` |
| `zoho.com.au` | https://api-console.zoho.com.au | `https://accounts.zoho.com.au/oauth/v2/token` |
| `zoho.jp` | https://api-console.zoho.jp | `https://accounts.zoho.jp/oauth/v2/token` |

The default workflow uses `.com`. If your account is in a different region, **also update the URL** in the `🔑 Refresh Zoho Token` node.

### 1.2 Create a Self Client

1. Open your regional API Console (see table above)
2. Click **ADD CLIENT** → choose **Self Client**
3. Confirm → you'll see a screen with two tabs: **Client Secret** and **Generate Code**
4. Copy **Client ID** and **Client Secret** — you'll paste these into n8n shortly

### 1.3 Generate a refresh token

Still in the Self Client view:

1. Switch to the **Generate Code** tab
2. Enter scope: `ZohoCRM.modules.ALL`
3. Time Duration: **10 Minutes**
4. Scope Description: anything (e.g., "n8n lead automation")
5. Click **CREATE** → you'll get a temporary **code**

You have 10 minutes to exchange this code for a refresh token. Open a terminal and run:

```bash
# Replace .eu with your region, and fill in your values
curl -X POST https://accounts.zoho.eu/oauth/v2/token \
  -d "grant_type=authorization_code" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "code=YOUR_GENERATED_CODE" \
  -d "redirect_uri=https://www.google.com"
```

The response will look like:

```json
{
  "access_token": "1000.xxx...",
  "refresh_token": "1000.yyy...",
  "api_domain": "https://www.zohoapis.eu",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

**Copy the `refresh_token` value** — it's long-lived and what n8n will use to get fresh access tokens on every run.

### 1.4 Paste into n8n

Open the **🔑 Refresh Zoho Token** node and fill in the Body Fields:

- `client_id` → your Client ID
- `client_secret` → your Client Secret
- `refresh_token` → the token from the curl response above
- `grant_type` → `refresh_token` (already set)

If you're not on `.com`, also change the URL to your region's accounts domain.

### 1.5 Verify `api_domain`

Also non-`.com` users: open the **📊 Create Zoho Lead** node and change the URL from `https://www.zohoapis.com/crm/v2/Leads` to match your region (e.g., `zohoapis.eu`).

---

## 2. Telegram

### 2.1 Create a bot

1. Open Telegram → message [@BotFather](https://t.me/BotFather)
2. Send `/newbot`
3. Pick a display name (e.g., "My CRM Notifier")
4. Pick a username ending in `bot` (e.g., `my_crm_notifier_bot`)
5. BotFather replies with an **HTTP API token** like `1234567890:AAExxxxxxxxxxxxxxxxxxxxxxx`
6. Copy the token

### 2.2 Get your chat ID

The bot can only send messages to a chat where it has permission. Simplest setup — DM the bot yourself:

1. Search for your bot's username in Telegram and send it any message (e.g., `/start`)
2. Message [@userinfobot](https://t.me/userinfobot) → it replies with your numeric user ID

If you want notifications to go to a **group** instead:

1. Add the bot to the group
2. Send any message in the group
3. Visit `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` in a browser
4. Look for `"chat":{"id":-100123456789,...}` — group IDs start with `-100`

### 2.3 Paste into n8n

**Bot token:** Open the **📨 Telegram Notification** node. In the URL field replace `{{YOUR_TELEGRAM_BOT_TOKEN}}`:

```
https://api.telegram.org/bot1234567890:AAExxxxxxxxxxxxxxxxxxxxxxx/sendMessage
```

**Chat ID:** Open the **📦 Prepare Payload** node. Scroll to the Telegram block in the JS code and replace the placeholder:

```javascript
const telegramBody = JSON.stringify({
  chat_id:    '123456789',   // ← your chat ID
  parse_mode: 'HTML',
  text:       tgText
});
```

---

## 3. Google Sheets (via Apps Script)

Instead of using n8n's native Google Sheets node (which requires OAuth), this workflow posts to a Google Apps Script web app. It's simpler, more portable, and doesn't tie your workflow to a specific Google account.

### 3.1 Create the sheet

1. Go to [sheets.google.com](https://sheets.google.com) → create a new spreadsheet
2. Name it (e.g., "Lead Log")
3. In row 1, add these headers exactly:

   | A | B | C | D | E | F |
   |---|---|---|---|---|---|
   | timestamp | name | email | phone | message | source |

### 3.2 Create the Apps Script

1. In the same sheet: **Extensions → Apps Script**
2. Delete the default code, paste this:

   ```javascript
   function doGet(e) {
     const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
     const p = e.parameter;
     sheet.appendRow([
       p.timestamp || new Date().toISOString(),
       p.name      || '',
       p.email     || '',
       p.phone     || '',
       p.message   || '',
       p.source    || ''
     ]);
     return ContentService
       .createTextOutput(JSON.stringify({ ok: true }))
       .setMimeType(ContentService.MimeType.JSON);
   }
   ```

3. Click **Save** (disk icon)

### 3.3 Deploy as web app

1. Click **Deploy → New deployment**
2. Gear icon → select **Web app**
3. Configuration:
   - **Description:** `n8n lead logger`
   - **Execute as:** *Me*
   - **Who has access:** *Anyone* (this is required for n8n to POST without auth)
4. Click **Deploy**
5. Grant permissions when prompted (you may need to click "Advanced → Go to project (unsafe)" — this is normal for your own scripts)
6. Copy the **Web app URL**. It looks like:
   ```
   https://script.google.com/macros/s/AKfycbxxxxxxxxxxxxxxxxxxxxxx/exec
   ```

The long string after `/s/` and before `/exec` is your **Deployment ID**.

### 3.4 Paste into n8n

Open the **📊 Log to Google Sheets** node. Replace `YOUR_GOOGLE_APPS_SCRIPT_ID` in the URL with the deployment ID:

```
https://script.google.com/macros/s/AKfycbxxxxxxxxxxxxxxxxxxxxxx/exec
```

---

## 4. First test

1. In n8n, make sure the workflow is **saved**
2. Click the **Webhook: New Lead** node → switch to the **Webhook URLs** section
3. Copy the **Test URL** (this activates the webhook for ~120 seconds after you click Execute)
4. Click **Execute workflow** at the bottom of the canvas
5. In a terminal, send a test request:

   ```bash
   curl -X POST <TEST_URL> \
     -H 'Content-Type: application/json' \
     -d '{"name":"Jane Test","email":"jane@example.com","phone":"+1234567890","message":"Testing the pipeline","source":"Manual test"}'
   ```

6. Watch the canvas — each node should light up green
7. Verify:
   - ✅ Zoho CRM shows a new lead "Jane Test"
   - ✅ Telegram gets a notification
   - ✅ Google Sheet has a new row
   - ✅ curl prints a success JSON with a `zohoLeadId`

If any node errors, jump to [Troubleshooting](TROUBLESHOOTING.md).

---

## 5. Go to production

Once the test works:

1. **Switch to Production URL** — the Test URL only works for one request. Copy the **Production URL** from the Webhook node and use that in your form.
2. **Activate the workflow** — toggle **Active** in the top-right of the canvas.
3. **Point your form at the webhook** — typical setups:
   - HTML form with JS `fetch` to the webhook URL
   - Landing page builder (Webflow, Framer, Carrd) → use their Form Webhook integration
   - Form service (Tally, Typeform) → add a Webhook destination
4. **Add honeypot / captcha** if you're getting bot traffic.

---

## 6. Security checklist

Before going live:

- [ ] Workflow JSON in your repo contains **only placeholders**, no real credentials
- [ ] If you ever committed real tokens, rotate them: [TROUBLESHOOTING.md#rotating-compromised-credentials](TROUBLESHOOTING.md#rotating-compromised-credentials)
- [ ] Add a simple shared-secret header check in the Webhook node if the form is public
- [ ] Rate-limit the webhook at your reverse proxy (nginx, Cloudflare) if exposed to the open internet
- [ ] Set up an **Error Workflow** in n8n so you get alerted if this flow breaks

---

Next: read [ARCHITECTURE.md](ARCHITECTURE.md) to understand how the pieces fit together, or jump to [TROUBLESHOOTING.md](TROUBLESHOOTING.md) if something's not working.
