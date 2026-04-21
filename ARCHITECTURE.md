# Architecture

## Flow

```text
Gmail Trigger
        |
        v
Webhook (Manual Lead) -> Normalize Input
                              |
                              v
                     LLM Classify & Extract
                              |
                              v
                     Build Structured Lead
                              |
                              v
                            Is Lead?
                              |
                              v
                      Telegram Notify
                              |
                              v
                    Google Sheets Webhook
                              |
                              v
                    Build Webhook Response
```

## Input Sources

The workflow supports two input paths:

- Gmail Trigger for new unread emails.
- Manual webhook for REST API lead submissions.

`Normalize Input` converts both formats into one shared structure:

```json
{
  "triggerType": "gmail",
  "source": "gmail",
  "subject": "Need CRM automation",
  "from": "lead@example.com",
  "body": "Message body",
  "receivedAt": "2026-04-21T00:00:00.000Z",
  "messageId": "message-id"
}
```

## LLM Classification

`LLM Classify & Extract` asks Gemini to return strict JSON:

```json
{
  "is_lead": true,
  "intent": "inquiry",
  "priority": "medium",
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1-555-123-4567",
  "company": "Example Co",
  "budget": "$3,000 - $5,000",
  "services": ["n8n automation", "CRM integration"],
  "summary": "Lead needs Gmail intake and CRM sync.",
  "language": "en",
  "confidence": 0.8
}
```

## Fallback Logic

If the LLM API returns an error or quota limit, `Build Structured Lead` still extracts key lead fields using local heuristics.

This keeps the workflow operational even when the external AI service is temporarily unavailable.

## Outputs

Qualified leads are sent to:

- Telegram, for immediate notification.
- Google Sheets, for persistent lead logging.

The webhook path also returns a compact JSON response:

```json
{
  "status": "ok",
  "is_lead": true,
  "intent": "inquiry",
  "priority": "medium",
  "source": "Website Test",
  "classification_mode": "heuristic_fallback"
}
```
