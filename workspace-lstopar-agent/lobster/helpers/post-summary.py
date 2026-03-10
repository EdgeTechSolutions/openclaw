#!/usr/bin/env python3
"""
Post Gmail triage summary to Telegram.
Reads classified JSON from stdin, formats and sends via CLAWD_URL.
"""
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime
from collections import defaultdict

# Category emoji mapping
CATEGORY_EMOJI = {
    "Actionable": "✉️",
    "Informational": "ℹ️",
    "Updates": "🔔",
    "LinkedIn": "💼",
    "Promotions": "🏷️",
    "Invoices": "📄",
    "Trading212": "📈",
    "Qogita": "📦",
    "GoogleWorkspace": "Workspace",
    "Google": "🔍",
    "Apple": "🍎",
    "Bitstamp": "💰",
    "Wise": "💸",
    "GitHub": "🐙",
    "Revolut": "💳",
    "Forums": "💬",
    "Calendar": "📅",
}

ARCHIVE_EMOJI = "🗂"
INBOX_EMOJI = "🔔"


def main():
    input_data = sys.stdin.read()
    if not input_data.strip():
        return
    
    try:
        emails = json.loads(input_data)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)
    
    if not isinstance(emails, list):
        emails = emails.get("archived", []) + emails.get("kept", [])
    
    # Group by category
    by_category = defaultdict(list)
    for email in emails:
        cat = email.get("category", "Other")
        by_category[cat].append(email)
    
    # Count archived vs kept
    archived_count = sum(1 for e in emails if e.get("autoArchive"))
    kept_count = len(emails) - archived_count
    
    # Build message
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [f"📬 Gmail Triage — {now}"]
    lines.append("")
    lines.append(f"📊 {len(emails)} processed | {ARCHIVE_EMOJI} {archived_count} archived | {INBOX_EMOJI} {kept_count} kept")
    lines.append("")
    
    # Order categories: actionable first, then by count
    ordered_cats = sorted(
        by_category.keys(),
        key=lambda c: (0 if c == "Actionable" else 1, -len(by_category[c]))
    )
    
    for cat in ordered_cats:
        cat_emails = by_category[cat]
        emoji = CATEGORY_EMOJI.get(cat, "📁")
        archived_in_cat = sum(1 for e in cat_emails if e.get("autoArchive"))
        status = f"{ARCHIVE_EMOJI} archived" if archived_in_cat == len(cat_emails) else INBOX_EMOJI
        
        lines.append(f"━━━━━━━━━━━━━━━━━━━━━")
        lines.append(f"{emoji} {cat} ({len(cat_emails)}) — {status}")
        lines.append("━━━━━━━━━━━━━━━━━━━━━")
        
        for email in cat_emails[:10]:  # Max 10 per category
            subject = email.get("subject", "No subject")[:50]
            sender = email.get("sender", "Unknown")[:30]
            thread_id = email.get("threadId") or email.get("id", "")
            
            # Gmail link
            link = f"https://mail.google.com/mail/u/0/#all/{thread_id}" if email.get("autoArchive") else f"https://mail.google.com/mail/u/0/#inbox/{thread_id}"
            
            lines.append(f"• [{subject}]({link})")
            lines.append(f"  _{sender}_")
        
        if len(cat_emails) > 10:
            lines.append(f"  _… and {len(cat_emails) - 10} more_")
        lines.append("")
    
    lines.append("#gmail #triage")
    
    message = "\n".join(lines)
    
    # Send to Telegram via CLAWD_URL
    clawd_url = os.environ.get("CLAWD_URL", "").rstrip("/")
    clawd_token = os.environ.get("CLAWD_TOKEN", "")
    
    if not clawd_url:
        print("Error: CLAWD_URL not set", file=sys.stderr)
        sys.exit(1)
    
    endpoint = f"{clawd_url}/tools/invoke"
    
    payload = {
        "tool": "message",
        "action": "send",
        "args": {
            "action": "send",
            "channel": "telegram",
            "to": "8403014547",
            "threadId": "1299",
            "message": message
        }
    }
    
    headers = {"Content-Type": "application/json"}
    if clawd_token:
        headers["Authorization"] = f"Bearer {clawd_token}"
    
    try:
        req = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as e:
        print(f"Error: Failed to send Telegram message: {e}", file=sys.stderr)
        sys.exit(1)
    
    if result.get("ok"):
        print("✅ Summary sent to Telegram topic 1299")
    else:
        error_msg = result.get("error", {}).get("message", "Unknown error")
        print(f"Error: Failed to send message: {error_msg}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
