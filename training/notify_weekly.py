#!/usr/bin/env python3
"""
notify_weekly.py — Run on a schedule (weekly systemd timer) alongside the
continuous --optimize-forever service. Validates the Optuna study's current
best params against the held-out set; if that holdout score beats the last
one we notified about, saves current_params.json and sends a Telegram
message + the file. If not, sends a short status-only message.

Requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in the environment.
"""

import json
import mimetypes
import os
import sys
import urllib.request
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from optimizer.fitness import HOLDOUT_DIR, evaluate_parameters
from optimizer.search import get_study, save_best_params

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MARKER_PATH = os.path.join(SCRIPT_DIR, ".last_notified_score")
CURRENT_PARAMS_PATH = os.path.join(SCRIPT_DIR, "current_params.json")


def _load_last_notified():
    if os.path.exists(MARKER_PATH):
        with open(MARKER_PATH, encoding="utf-8") as f:
            return float(f.read().strip())
    return None


def _save_last_notified(score):
    with open(MARKER_PATH, "w", encoding="utf-8") as f:
        f.write(str(score))


def send_telegram_message(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = json.dumps({"chat_id": chat_id, "text": text}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    urllib.request.urlopen(req, timeout=15)


def send_telegram_document(token, chat_id, file_path, caption):
    boundary = uuid.uuid4().hex
    url = f"https://api.telegram.org/bot{token}/sendDocument"
    content_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    parts = [
        f'--{boundary}\r\nContent-Disposition: form-data; name="chat_id"\r\n\r\n{chat_id}\r\n',
        f'--{boundary}\r\nContent-Disposition: form-data; name="caption"\r\n\r\n{caption}\r\n',
        f'--{boundary}\r\nContent-Disposition: form-data; name="document"; '
        f'filename="{os.path.basename(file_path)}"\r\nContent-Type: {content_type}\r\n\r\n',
    ]
    body = "".join(parts).encode("utf-8") + file_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")

    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
    )
    urllib.request.urlopen(req, timeout=30)


def main():
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]

    study = get_study()
    if not study.trials:
        print("No completed trials yet, skipping this check.")
        return

    train_score = study.best_value
    params = study.best_params
    trial_count = len(study.trials)

    print(f"Validating current best (train={train_score:.4f}, {trial_count} trials so far) against holdout...")
    holdout_score, _ = evaluate_parameters(params, data_dir=HOLDOUT_DIR)
    last_notified = _load_last_notified()
    print(f"Holdout score: {holdout_score:.4f} (last notified: {last_notified})")

    if last_notified is not None and holdout_score <= last_notified:
        send_telegram_message(
            token, chat_id,
            f"Weekly training check: no improvement yet.\n"
            f"Current holdout score: {holdout_score:.4f} (still below last notified {last_notified:.4f}).\n"
            f"{trial_count} trials completed so far.",
        )
        print("No improvement. Sent status-only message.")
        return

    save_best_params(params, train_score, holdout_score)
    _save_last_notified(holdout_score)

    delta = f"+{holdout_score - last_notified:.4f}" if last_notified is not None else "first result"
    send_telegram_message(
        token, chat_id,
        f"🎉 Training improved!\n"
        f"Holdout score: {holdout_score:.4f} ({delta})\n"
        f"Train score: {train_score:.4f}\n"
        f"{trial_count} trials completed so far.\n"
        f"Sending current_params.json now — test it before trusting it.",
    )
    send_telegram_document(token, chat_id, CURRENT_PARAMS_PATH, "Updated current_params.json")
    print("Improvement detected. Saved current_params.json and notified via Telegram.")


if __name__ == "__main__":
    main()
