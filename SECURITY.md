# Security Policy

## Public Template Only

This repository is designed to be safe to publish. It does not intentionally contain real credentials, tokens, account IDs, or private deployment URLs.

Do not commit:

- Gmail OAuth credentials
- Gemini API keys
- Telegram bot tokens
- Telegram chat IDs
- Google Apps Script deployment URLs
- SMTP passwords or Gmail App Passwords
- `tokens.txt`
- real `config.json`
- exported n8n credential files

## Local Configuration

Use:

```text
config/config.example.json
```

as a template, then create your own untracked local file:

```text
config/config.json
```

## Reporting

If you find a secret in the repository history, rotate the exposed credential immediately and rewrite the repository history before continuing public use.
