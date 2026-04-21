# Troubleshooting

## Webhook Does Not Trigger

Check:

- The workflow is active for production `/webhook/...` URLs.
- You are using `/webhook-test/...` only while n8n is listening for a test event.
- The request method is `POST`.
- The request body is valid JSON.

## Validation Error Response

The workflow requires:

- `name`
- `email`

The email must look like a valid email address.

## Zoho Token Refresh Fails

Check:

- `YOUR_ZOHO_CLIENT_ID` was replaced.
- `YOUR_ZOHO_CLIENT_SECRET` was replaced.
- `YOUR_ZOHO_REFRESH_TOKEN` was replaced.
- The refresh token belongs to the correct Zoho data center.

If you use a non-US Zoho data center, update the Zoho API host accordingly.

## Zoho Lead Is Not Created

Check the execution output of:

```text
Create Zoho Lead
```

The node has `neverError` enabled, so Zoho API errors may appear in node output rather than stopping the workflow.

## Telegram Notification Does Not Send

Check:

- `TELEGRAM_BOT_TOKEN` is set or the placeholder was replaced locally.
- `TELEGRAM_CHAT_ID` is set or the placeholder was replaced locally.
- The bot has permission to send messages to the target chat.

## Google Sheets Does Not Update

Check:

- The Apps Script Web App URL ends with `/exec`.
- The Web App access is set to `Anyone`.
- The Google Sheet has the expected header row.
- The execution reaches `Log to Google Sheets`.

## Empty Rows In Google Sheets

Deploy the latest version of:

```text
scripts/google-sheets-apps-script.js
```

The included script ignores empty payloads.
