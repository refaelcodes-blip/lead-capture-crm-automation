# Troubleshooting

## Only The Gmail Trigger Lights Up

If you manually execute the Gmail Trigger node, n8n may show only the trigger node as successful.

For the full Gmail path, keep the workflow active, send a new unread email to the connected inbox, wait for polling, and inspect the latest `trigger` execution in the Executions view.

## Google Sheets Does Not Update

Check these items:

- The Apps Script Web App URL ends with `/exec`.
- The deployment access is set to `Anyone`.
- The `Google Sheets Webhook` node uses `POST` with JSON body.
- The Sheet has headers: `timestamp`, `name`, `email`, `phone`, `message`, `source`, `intent`, `priority`.
- The execution actually reaches the `Google Sheets Webhook` node.

## Empty Rows In Google Sheets

The included Apps Script ignores empty payloads. If you see empty rows, redeploy the latest version of `scripts/google-sheets-apps-script.js`.

## Gemini Returns Quota Errors

The workflow has fallback classification. A Gemini quota error should not stop the whole execution.

If the LLM node returns `429`, the response may show:

```json
{
  "classification_mode": "heuristic_fallback"
}
```

## Telegram Does Not Send

Check:

- Telegram credential is attached to the node.
- Bot token is valid.
- Chat ID is correct.
- The bot has permission to message the target chat.

## Python SMTP Test Fails With TLS Certificate Error

Use this only for local testing:

```powershell
python scripts\send_test_lead.py --config config\config.json --insecure
```

For production-like testing, fix the local Python or Windows certificate store instead of using `--insecure`.

## Python SMTP Test Sends But Gmail Trigger Does Not Run

Make sure `TEST_TO_EMAIL` in `config/config.json` is the same Gmail inbox connected to the n8n Gmail Trigger credential.

Also confirm the email is unread and wait for the polling interval.
