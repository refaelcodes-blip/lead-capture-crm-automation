# Troubleshooting

Common errors and their fixes. If you hit something not listed here, open an issue with the full error text and which node it came from.

---

## Zoho

### `invalid_client`

**Symptom:** the 🔑 Refresh Zoho Token node returns `{ "error": "invalid_client" }` and the 📦 Prepare Payload node throws "Failed to get access_token from Zoho".

**Cause:** Zoho couldn't match your `client_id` + `client_secret` combo.

**Fix — check these in order:**

1. **Wrong regional domain.** This is the most common cause. Zoho is region-locked: a Client ID from `api-console.zoho.com` does **not** work against `accounts.zoho.eu`.

   Log into [zoho.com](https://zoho.com) and check the browser URL:

   | URL contains | Use API Console at | Use accounts URL |
   |---|---|---|
   | `zoho.com` | `api-console.zoho.com` | `accounts.zoho.com` |
   | `zoho.eu` | `api-console.zoho.eu` | `accounts.zoho.eu` |
   | `zoho.in` | `api-console.zoho.in` | `accounts.zoho.in` |
   | `zoho.com.au` | `api-console.zoho.com.au` | `accounts.zoho.com.au` |
   | `zoho.jp` | `api-console.zoho.jp` | `accounts.zoho.jp` |

   Update the URL in the 🔑 Refresh Zoho Token node to match your region. Also update the 📊 Create Zoho Lead URL (`zohoapis.com` → `zohoapis.eu`, etc.).

2. **Placeholder values still in the node.** Open the node and verify `client_id` and `client_secret` aren't still `YOUR_ZOHO_CLIENT_ID`.

3. **Whitespace.** Copying credentials sometimes drags invisible whitespace. Re-paste fresh from the Zoho API Console.

4. **Wrong client type.** The workflow assumes a **Self Client**. If you created a "Server-based" or "Client-based" application, `invalid_client` will also fire — the OAuth flow is different. Go back to the API Console → **ADD CLIENT** → **Self Client**.

5. **Client Secret was regenerated.** If you ever clicked "Regenerate Client Secret" in the console, the old one is instantly dead. Grab the new one.

---

### `invalid_code`

**Symptom:** when running the one-time `curl` to exchange an authorization code for a refresh token, Zoho returns `invalid_code`.

**Cause:** authorization codes are valid for **10 minutes** and for **one use only**.

**Fix:** go back to API Console → Self Client → Generate Code tab, create a fresh code, and run the curl within 10 minutes. Don't re-run the same curl twice — the second attempt will always fail.

---

### `INVALID_TOKEN` from Create Zoho Lead

**Symptom:** Token refresh succeeds, but the actual lead creation returns `INVALID_TOKEN`.

**Cause:** the access token's scope doesn't include `ZohoCRM.modules.ALL` (or `.CREATE` on Leads specifically).

**Fix:** when generating the authorization code, make sure **Scope** is set to `ZohoCRM.modules.ALL`. Then re-run the curl to get a new refresh token with the correct scope, and paste it into n8n.

---

### `DUPLICATE_DATA` from Create Zoho Lead

**Symptom:** `{ "code": "DUPLICATE_DATA", "message": "duplicate data" }`.

**Cause:** Zoho has a unique constraint on email for Leads (or Contacts, depending on your layout).

**Fix — two options:**

1. **Skip duplicates silently.** Add `?trigger=[]&duplicate_check_fields=[Email]` to the Create Zoho Lead URL and handle the duplicate response in 🔗 Enrich.
2. **Upsert.** Change the method to `PUT` and use Zoho's upsert endpoint: `POST https://www.zohoapis.{region}/crm/v2/Leads/upsert`.

---

## Telegram

### `Bad Request: chat not found`

**Cause:** either the bot has never been interacted with by that chat, or the `chat_id` is wrong.

**Fix:**

1. **For a personal DM:** open Telegram, search for your bot by username, and send it `/start`. Then retry.
2. **For a group:** add the bot to the group and send at least one message. Verify the chat ID by visiting `https://api.telegram.org/bot<TOKEN>/getUpdates` — group IDs are negative numbers like `-1001234567890`.

---

### `Unauthorized` / `401`

**Cause:** wrong bot token, or the bot was revoked.

**Fix:** in @BotFather, send `/mybots` → pick your bot → **API Token**. Copy the token and re-paste it into the URL of the 📨 Telegram Notification node.

---

### Message sent but no emoji / formatting

**Cause:** `parse_mode` is missing or mis-set.

**Fix:** verify `parse_mode: 'HTML'` is in the JSON body (built in 📦 Prepare Payload). If using Markdown, switch to `MarkdownV2` and escape reserved characters (`_`, `*`, `[`, `]`, `(`, `)`, `~`, `` ` ``, `>`, `#`, `+`, `-`, `=`, `|`, `{`, `}`, `.`, `!`).

---

## Google Sheets

### New rows don't appear

**Cause (almost always):** the Apps Script is deployed with "Only myself" access, so n8n's request gets redirected to a Google login page and the `doGet` never runs.

**Fix:**

1. Open the Apps Script project
2. **Deploy → Manage deployments** → pencil icon on the active deployment
3. Set **Who has access** to **Anyone**
4. Click **Deploy** → copy the new URL if it changed

---

### 302 redirect / HTML page returned instead of JSON

Same cause as above — the script rejected the unauthenticated request and redirected to a sign-in page. Fix by setting access to "Anyone".

---

### Rows appear but columns are empty

**Cause:** the Apps Script is reading different parameter names than n8n is sending.

**Fix:** open the Apps Script editor and verify the `doGet` reads the same keys n8n sends: `timestamp`, `name`, `email`, `phone`, `message`, `source`. The code in [SETUP.md §3.2](SETUP.md) matches the workflow — if you edited either side, re-align them.

---

### Dates look weird in the sheet

**Cause:** Google Sheets auto-formats ISO strings inconsistently across locales.

**Fix:** in the sheet, select column A → **Format → Number → Date time** (or **Plain text** if you want the raw ISO string preserved).

---

## n8n

### Webhook returns 404

**Cause:** the workflow isn't **active**, or you're using the test URL instead of the production URL (or vice versa).

**Fix:**

- **For testing from curl:** click **Execute workflow** in the canvas first, then fire your curl within 120 seconds. Only the **Test URL** works in this mode.
- **For production (forms, external callers):** toggle the **Active** switch in the top-right. Use the **Production URL** — it works 24/7.

---

### "Workflow could not be activated"

**Cause:** usually a missing credential reference or an invalid expression.

**Fix:** open each node (red ones first) and verify all fields are filled. Check the bottom of the canvas for a specific error hint.

---

### Response is `timeout`

**Cause:** one of the external APIs hung. Zoho OAuth endpoints have been known to time out during regional outages.

**Fix:**

- Check [Zoho status](https://status.zoho.com), [Telegram status](https://core.telegram.org/api/obtaining_api_id#status), and [Google Workspace status](https://www.google.com/appsstatus).
- Add a **Retry on Fail** setting to the HTTP node (n8n node settings → Settings → Retry on Fail, 3 tries with 1s wait).

---

## Security

### Rotating compromised credentials

If you accidentally committed real credentials to Git (it happens), rotate them **immediately** — git history preserves everything, and bots scan public repos for secrets within minutes.

**Zoho:**
1. API Console → your Self Client → **Client Secret** tab → **Regenerate Client Secret**
2. This invalidates all existing refresh tokens. Generate a new authorization code and exchange for a fresh refresh token.

**Telegram:**
1. Message @BotFather → `/mybots` → pick your bot → **API Token** → **Revoke current token**
2. Paste the new token into n8n.

**Google Apps Script:**
1. In Apps Script: **Deploy → Manage deployments** → **Archive** the old deployment
2. Create a new deployment — you'll get a new URL with a new deployment ID
3. Update n8n

**Also:** use `git filter-repo` or [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/) to scrub the leaked credentials from git history, then force-push. For public repos, also assume the old credentials are compromised forever — rotation is non-optional.

---

## Still stuck?

- Re-read [SETUP.md](SETUP.md) — 9 times out of 10 it's a skipped step
- Check the n8n [Executions tab](https://docs.n8n.io/workflows/executions/) — each failed run has full input/output at every node
- Open the 🔑 Refresh Zoho Token node and click **Execute step** in isolation to see the raw error
- Open an issue on GitHub with: the node name, the full error JSON, and your region (no credentials, please)
