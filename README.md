# discord-reminder-bot

Weekly Discord reminder using GitHub Actions + Webhook.

## Files

- `config.json`: Reminder settings (`title`, `message`, `mention`, `enabled`)
- `scripts/send_reminder.py`: Loads config and sends Discord webhook notification
- `.github/workflows/remind.yml`: Weekly schedule + manual trigger workflow

## Setup

1. Set `DISCORD_WEBHOOK_URL` in GitHub repository secrets.
2. Update `config.json` values for your reminder content.
3. Keep `"enabled": true` to send reminders.

## Schedule

- Runs every Saturday at 21:00 JST.
- In GitHub Actions cron (UTC): `0 12 * * 6`.

## Manual test

Run from repo root:

```bash
python scripts/send_reminder.py
```

- If `enabled` is `false`, the script exits successfully without sending.
- If `DISCORD_WEBHOOK_URL` is missing, the script exits with an error.
- Message format: `[title]: message` (prefixes mention when configured).
