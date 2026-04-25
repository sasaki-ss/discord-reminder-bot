#!/usr/bin/env python3
"""Send a weekly reminder to Discord via webhook."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / "config.json"
REQUEST_TIMEOUT_SECONDS = 10


def fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def load_config(path: Path) -> dict[str, Any]:
    try:
        raw_text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"config file not found: {path}") from exc

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError("config must be a JSON object")

    required_fields = ("title", "message", "mention", "enabled")
    missing = [field for field in required_fields if field not in data]
    if missing:
        raise ValueError(f"missing required config keys: {', '.join(missing)}")

    if not isinstance(data["title"], str):
        raise ValueError("config.title must be a string")
    if not isinstance(data["message"], str):
        raise ValueError("config.message must be a string")
    if not isinstance(data["mention"], str):
        raise ValueError("config.mention must be a string")
    if not isinstance(data["enabled"], bool):
        raise ValueError("config.enabled must be a boolean")

    return data


def build_content(title: str, message: str, mention: str) -> str:
    title_clean = " ".join(title.split())
    message_clean = " ".join(message.split())

    if title_clean:
        body = f"[{title_clean}]: {message_clean}"
    else:
        body = message_clean

    mention_clean = mention.strip()
    if mention_clean:
        return f"{mention_clean} {body}".strip()
    return body.strip()


def post_discord_message(webhook_url: str, content: str) -> None:
    payload = {"content": content}
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        webhook_url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            # Explicit UA helps avoid gateway/WAF edge-cases with default urllib UA.
            "User-Agent": "discord-reminder-bot/1.0",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            status = response.getcode()
            # Discord webhook usually returns 204 No Content.
            if status < 200 or status >= 300:
                raise RuntimeError(f"Discord webhook returned unexpected status: {status}")
    except urllib.error.HTTPError as exc:
        details = ""
        try:
            error_body = exc.read().decode("utf-8", errors="replace").strip()
            if error_body:
                details = f" response={error_body}"
        except Exception:
            # Best-effort only; keep original HTTP code even if body decode fails.
            details = ""
        raise RuntimeError(f"Discord webhook HTTP error: {exc.code}{details}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Discord webhook request failed: {exc.reason}") from exc


def main() -> int:
    try:
        config = load_config(CONFIG_PATH)
    except ValueError as exc:
        return fail(str(exc))

    if not config["enabled"]:
        print("Reminder is disabled. Skipping message send.")
        return 0

    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()
    if not webhook_url:
        return fail("DISCORD_WEBHOOK_URL is not set")

    content = build_content(
        title=config["title"],
        message=config["message"],
        mention=config["mention"],
    )

    if not content.strip():
        return fail("message content is empty after formatting")

    try:
        post_discord_message(webhook_url=webhook_url, content=content)
    except RuntimeError as exc:
        return fail(str(exc))

    print("Reminder sent successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
