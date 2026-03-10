#!/usr/bin/env python3
"""
Classify Gmail emails using the llm-task tool via CLAWD_URL.
Reads JSON email data from stdin, outputs classified JSON to stdout.
"""
import json
import os
import sys
import urllib.request
import urllib.error

AUTO_ARCHIVE_CATEGORIES = {
    "Updates", "LinkedIn", "GitHub", "Revolut", "Trading212", 
    "Qogita", "Informational", "Promotions", "GoogleWorkspace", 
    "Google", "Apple", "Bitstamp", "Wise", "Forums", "Calendar"
}

def main():
    # Read emails from stdin
    input_data = sys.stdin.read()
    if not input_data.strip():
        print("[]")
        return
    
    try:
        data = json.loads(input_data)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)
    
    emails = data.get("threads", [])
    if not emails:
        print("[]")
        return
    
    # Build prompt for classification
    email_list = []
    for e in emails:
        email_list.append({
            "id": e.get("id"),
            "threadId": e.get("id"),
            "subject": e.get("subject", "")[:100],
            "sender": e.get("from", ""),
            "labels": e.get("labels", [])
        })
    
    prompt = f"""Classify each Gmail email for Luka Stopar. Input is a JSON array. Return a JSON array where each item has: id, threadId, subject, sender, category.

Categories (use exactly one per email):
- Actionable (requires Luka's response or action)
- Informational (FYI, confirmations, receipts)
- Updates (notifications from tools/services)
- LinkedIn (LinkedIn notifications)
- Promotions (marketing, sales pitches)
- Invoices (bills, invoices, payment confirmations)
- Trading212 (Trading 212 notifications)
- Qogita (Qogita/wholesale related)
- GoogleWorkspace (Google service notifications)
- Google (Other Google notifications)
- Apple (Apple notifications)
- Bitstamp (Bitstamp exchange notifications)
- Wise (Wise transfer notifications)
- GitHub (GitHub notifications)
- Revolut (Revolut notifications)
- Forums (forum/community notifications)
- Calendar (calendar invites, Zoom links)

Input emails:
{json.dumps(email_list, indent=2)}

Return ONLY a raw JSON array, no markdown formatting."""

    # Call llm-task via CLAWD_URL
    clawd_url = os.environ.get("CLAWD_URL", "").rstrip("/")
    clawd_token = os.environ.get("CLAWD_TOKEN", "")
    
    if not clawd_url:
        print("Error: CLAWD_URL not set", file=sys.stderr)
        sys.exit(1)
    
    endpoint = f"{clawd_url}/tools/invoke"
    
    payload = {
        "tool": "llm-task",
        "action": "invoke",
        "args": {
            "prompt": prompt,
            "artifacts": [],
            "artifactHashes": []
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
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as e:
        print(f"Error: Failed to call llm-task: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid response from llm-task: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Unwrap the response
    if result.get("ok") and "result" in result:
        inner = result["result"]
        # Check for nested ok/result envelope
        if isinstance(inner, dict) and inner.get("ok") and "result" in inner:
            classified = inner["result"]
        elif isinstance(inner, dict) and "output" in inner:
            output = inner.get("output", {})
            if isinstance(output, dict) and "data" in output:
                classified = output["data"]
            else:
                classified = output
        else:
            classified = inner
    else:
        error_msg = result.get("error", {}).get("message", "Unknown error")
        print(f"Error: llm-task failed: {error_msg}", file=sys.stderr)
        sys.exit(1)
    
    # Handle string response that might be JSON
    if isinstance(classified, str):
        try:
            classified = json.loads(classified)
        except json.JSONDecodeError:
            pass
    
    # Ensure we have a list
    if not isinstance(classified, list):
        if isinstance(classified, dict) and "data" in classified:
            classified = classified["data"]
        else:
            print(f"Error: Unexpected classification format: {type(classified)}", file=sys.stderr)
            sys.exit(1)
    
    # Add autoArchive flag
    for item in classified:
        cat = item.get("category", "")
        item["autoArchive"] = cat in AUTO_ARCHIVE_CATEGORIES
    
    print(json.dumps(classified, indent=2))


if __name__ == "__main__":
    main()
