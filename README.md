# Lead Capture + CRM Automation

An n8n workflow template for receiving website leads, validating required fields, creating Zoho CRM leads, notifying a manager in Telegram, and logging every lead to Google Sheets.

This repository is a public-safe template. It does not include real tokens, account IDs, app passwords, API keys, or deployment URLs.

## What It Does

- Receives new leads through an n8n webhook.
- Validates required fields such as name and email.
- Refreshes a Zoho OAuth access token.
- Creates a lead in Zoho CRM.
- Enriches the execution data with the Zoho lead ID.
- Sends a Telegram notification to a manager or sales team.
- Logs the lead to Google Sheets through a Google Apps Script Web App.
- Returns a success or validation-error response to the webhook caller.

## Repository Structure

```text
workflows/
  lead-capture-crm-automation.json
scripts/
  google-sheets-apps-script.js
config/
  config.example.json
```

## Quick Start

1. Import `workflows/lead-capture-crm-automation.json` into n8n.
2. Replace Zoho placeholders in the `Refresh Zoho Token` node.
3. Set your Telegram bot token and chat ID.
4. Deploy `scripts/google-sheets-apps-script.js` as a Google Apps Script Web App.
5. Replace the placeholder `/exec` URL in the `Log to Google Sheets` node.
6. Activate the workflow.
7. Send a test lead to the webhook endpoint.

See [SETUP.md](SETUP.md) for the full setup guide.

## Test Payload

```bash
curl -X POST https://YOUR_N8N/webhook/lead-capture \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+15551234567",
    "message": "I need CRM automation for incoming leads.",
    "source": "Landing Page"
  }'
```

## Security

Do not commit real credentials. Keep secrets in n8n credentials, environment variables, or a private secrets manager.

The sanitized workflow uses placeholders such as:

- `YOUR_ZOHO_CLIENT_ID`
- `YOUR_ZOHO_CLIENT_SECRET`
- `YOUR_ZOHO_REFRESH_TOKEN`
- `YOUR_TELEGRAM_BOT_TOKEN`
- `YOUR_TELEGRAM_CHAT_ID`
- `https://script.google.com/macros/s/YOUR_DEPLOYMENT_ID/exec`

## License

MIT
