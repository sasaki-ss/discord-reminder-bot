# discord-reminder-bot

GitHub Actions と Discord Webhook を使って、毎週土曜 21:00（JST）に通知を送るシンプルなリマインドBotです。

## 構成ファイル

- `config.json`
  - 通知設定を保持します（`title`, `message`, `mention`, `enabled`）。
- `scripts/send_reminder.py`
  - `config.json` を読み込み、Discord Webhook へ通知を送信します。
- `.github/workflows/remind.yml`
  - 定期実行（cron）と手動実行（`workflow_dispatch`）を定義します。

## セットアップ

1. GitHub リポジトリの Secrets に `DISCORD_WEBHOOK_URL` を登録します。
2. `config.json` の内容を用途に合わせて編集します。
3. 通知を有効化する場合は `"enabled": true` にします。

## 実行スケジュール

- 毎週土曜 21:00（JST）に実行
- GitHub Actions の cron（UTC）: `0 12 * * 6`

## 手動実行（ローカル）

リポジトリ直下で実行:

```bash
python scripts/send_reminder.py
```

`scripts` ディレクトリからでも実行可能:

```bash
python .\send_reminder.py
```

事前に Webhook URL を環境変数へ設定してください（PowerShell）:

```powershell
$env:DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
```

## 動作仕様

- `"enabled": false` の場合は送信せず正常終了します。
- `DISCORD_WEBHOOK_URL` が未設定の場合はエラー終了します。
- 通知フォーマットは次の1行です。
  - `mention [title]: message`
  - `mention` が空文字の場合は `[title]: message` になります。
- 日本語のタイトル・メッセージにも対応しています（UTF-8）。
