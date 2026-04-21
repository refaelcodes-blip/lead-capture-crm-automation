# Setup Guide

## 1. Import The Workflow

Open n8n and import:

```text
workflows/lead-intake-automation.json
```

The workflow is inactive by default. Configure all credentials before activating it.

## 2. Configure Gmail Trigger

Create a Gmail OAuth2 credential in n8n and attach it to the `Gmail Trigger` node.

The template is configured to poll unread emails. For testing, send a new unread email to the connected Gmail inbox and wait for the polling interval.

## 3. Configure Gemini

Create an HTTP Header Auth credential in n8n:

```text
Header name: x-goog-api-key
Header value: YOUR_GEMINI_API_KEY
```

Attach it to the `LLM Classify & Extract` node.

The workflow includes fallback classification so a Gemini quota error does not break the entire lead intake flow.

## 4. Configure Telegram

Create a Telegram credential in n8n and attach it to the `Telegram Notify` node.

Set the chat ID in one of two ways:

- Replace `YOUR_TELEGRAM_CHAT_ID` in the Telegram node.
- Or set the `TELEGRAM_CHAT_ID` environment variable for your n8n instance.

## 5. Configure Google Sheets

Create a Google Sheet with these headers in row 1:

```text
timestamp | name | email | phone | message | source | intent | priority
```

Open the Sheet, then go to:

```text
Extensions -> Apps Script
```

Paste the contents of:

```text
scripts/google-sheets-apps-script.js
```

Deploy it as a Web App:

```text
Deploy -> New deployment -> Web app
Execute as: Me
Who has access: Anyone
```

Copy the Web App URL ending in `/exec` and paste it into the `Google Sheets Webhook` node.

## 6. Test The Webhook Path

Use the production webhook URL after activating the workflow:

```powershell
Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:5678/webhook/lead-capture' -ContentType 'application/json' -Body (@{
  name='John Doe'
  email='john@test.com'
  phone='+1-555-123-4567'
  message='We need n8n automation for lead routing, Gmail intake, and CRM sync.'
  source='Website Test'
} | ConvertTo-Json)
```

For live editor testing, use the n8n test webhook URL while the workflow is listening:

```text
http://127.0.0.1:5678/webhook-test/lead-capture
```

## 7. Test The Gmail Path With Python

Copy the example config:

```powershell
Copy-Item config\config.example.json config\config.json
```

Edit `config/config.json` locally and add your SMTP test sender details.

Send one test email:

```powershell
python scripts\send_test_lead.py --config config\config.json
```

Send three test emails:

```powershell
python scripts\send_test_lead.py --config config\config.json --count 3 --delay-sec 5
```

## 8. View Executions

Production Gmail trigger runs usually appear in n8n as saved executions, not as a live animation on the canvas.

Open:

```text
Executions -> latest trigger execution
```

Then inspect each node's input and output data.
