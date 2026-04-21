# Setup Guide

## 1. Import The Workflow

Import this file into n8n:

```text
workflows/lead-capture-crm-automation.json
```

Keep the workflow inactive until every placeholder is configured.

## 2. Configure The Webhook

The workflow starts with:

```text
Webhook: New Lead
```

Production endpoint after activation:

```text
https://YOUR_N8N/webhook/lead-capture
```

Test endpoint while listening in the editor:

```text
https://YOUR_N8N/webhook-test/lead-capture
```

## 3. Configure Zoho CRM

Create or open a Zoho Self Client app in the Zoho API Console.

Replace these placeholders in the `Refresh Zoho Token` node:

```text
YOUR_ZOHO_CLIENT_ID
YOUR_ZOHO_CLIENT_SECRET
YOUR_ZOHO_REFRESH_TOKEN
```

The node sends a `refresh_token` grant request to:

```text
https://accounts.zoho.com/oauth/v2/token
```

The resulting `access_token` is used by the `Create Zoho Lead` node.

## 4. Configure Telegram

Set these values in your n8n environment or replace the placeholders locally:

```text
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

The Telegram node sends a formatted lead notification after Zoho CRM processing.

## 5. Configure Google Sheets

Create a Google Sheet with this header row:

```text
timestamp | name | email | phone | message | source
```

Open:

```text
Extensions -> Apps Script
```

Paste the contents of:

```text
scripts/google-sheets-apps-script.js
```

Deploy as a Web App:

```text
Deploy -> New deployment -> Web app
Execute as: Me
Who has access: Anyone
```

Copy the Web App URL ending in `/exec` and paste it into the `Log to Google Sheets` node.

## 6. Test The Workflow

Send a lead payload:

```powershell
Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:5678/webhook/lead-capture' -ContentType 'application/json' -Body (@{
  name='John Doe'
  email='john@example.com'
  phone='+15551234567'
  message='I need CRM automation for incoming leads.'
  source='Landing Page'
} | ConvertTo-Json)
```

Expected result:

```json
{
  "status": "success",
  "message": "Lead successfully processed"
}
```

## 7. Validation Errors

If `name` or `email` is missing, or if email format is invalid, the workflow returns a validation error response and does not call Zoho, Telegram, or Google Sheets.
