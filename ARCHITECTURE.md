# Architecture

## Flow

```text
Webhook: New Lead
        |
        v
Validate & Prepare
        |
        v
Is Data Valid?
        |
        +--> Validation Error Response
        |
        v
Refresh Zoho Token
        |
        v
Prepare Payload
        |
        v
Create Zoho Lead
        |
        v
Enrich with CRM Data
        |
        v
Telegram Notification
        |
        v
Log to Google Sheets
        |
        v
Success Response
```

## Input Schema

The webhook expects a JSON payload:

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+15551234567",
  "message": "I need CRM automation for incoming leads.",
  "source": "Landing Page"
}
```

## Validation

The `Validate & Prepare` node:

- Reads either the direct JSON payload or the nested webhook `body`.
- Requires `name`.
- Requires `email`.
- Validates email format.
- Splits full name into first and last name.
- Adds an ISO timestamp.

## Zoho CRM

The `Refresh Zoho Token` node exchanges a refresh token for an access token.

The `Create Zoho Lead` node sends the lead payload to:

```text
https://www.zohoapis.com/crm/v2/Leads
```

## Telegram

The workflow prepares a human-readable HTML message with lead details and Zoho lead ID, then sends it through the Telegram Bot API.

## Google Sheets

The workflow logs the processed lead through a Google Apps Script Web App.

Expected Sheet columns:

```text
timestamp | name | email | phone | message | source
```

## Response

Successful response:

```json
{
  "status": "success",
  "message": "Lead successfully processed",
  "zohoLeadId": "1234567890"
}
```

Validation error response:

```json
{
  "status": "error",
  "message": "Input validation failed",
  "errors": ["Field email is required"]
}
```
