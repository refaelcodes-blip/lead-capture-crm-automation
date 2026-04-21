# Email / Lead Intake Automation

An n8n workflow template for automated lead intake from Gmail and REST webhooks.

The workflow receives an email or webhook payload, normalizes the input, classifies the message with an LLM, extracts structured lead fields, routes qualified leads, sends a Telegram notification, and logs the result to Google Sheets.

## What It Shows

- Gmail Trigger for new unread emails
- Manual webhook for REST API lead submissions
- LLM classification with structured JSON output
- Local fallback classification when the LLM API is rate-limited
- Conditional routing with an `Is Lead?` node
- Telegram lead notifications
- Google Sheets logging through Google Apps Script
- Python SMTP test script for generating test lead emails

## Repository Structure

```text
workflows/
  lead-intake-automation.json
scripts/
  google-sheets-apps-script.js
  send_test_lead.py
config/
  config.example.json
docs/
  subtitles/
  youtube/
```

## Quick Start

1. Import `workflows/lead-intake-automation.json` into n8n.
2. Create credentials in n8n for Gmail OAuth2, Gemini HTTP Header Auth, and Telegram.
3. Deploy `scripts/google-sheets-apps-script.js` as a Google Apps Script Web App.
4. Replace the placeholder Google Apps Script `/exec` URL in the `Google Sheets Webhook` node.
5. Activate the workflow.
6. Send a new unread test email to the Gmail account connected to the trigger.

See [SETUP.md](SETUP.md) for the full setup guide.

## Security

This repository is a public-safe template. It intentionally does not include:

- Gmail credentials
- Gemini API keys
- Telegram bot tokens
- Telegram chat IDs
- Google Apps Script deployment IDs
- SMTP app passwords
- `tokens.txt`
- real `config.json`

Use `config/config.example.json` as a template and keep your real local config untracked.

## Testing

Copy the example config:

```powershell
Copy-Item config\config.example.json config\config.json
```

Edit `config/config.json` locally, then send a test lead email:

```powershell
python scripts\send_test_lead.py --config config\config.json --count 1
```

If your local Python certificate store has SMTP TLS verification issues, use `--insecure` only for local testing:

```powershell
python scripts\send_test_lead.py --config config\config.json --insecure
```

## License

MIT
