#!/usr/bin/env python3
"""
Archive emails that are in auto-archive categories.
Reads classified JSON from stdin, archives matching emails using gogcli.
Outputs summary of archived emails.
"""
import json
import subprocess
import sys

AUTO_ARCHIVE_CATEGORIES = {
    "Updates", "LinkedIn", "GitHub", "Revolut", "Trading212",
    "Qogita", "Informational", "Promotions", "GoogleWorkspace",
    "Google", "Apple", "Bitstamp", "Wise", "Forums", "Calendar"
}

GOGCLI_PATH = "/workspace/.npm-global/bin/gogcli"
ACCOUNT = "luka@stopar.si"

def main():
    input_data = sys.stdin.read()
    if not input_data.strip():
        print("[]")
        return
    
    try:
        emails = json.loads(input_data)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)
    
    archived = []
    errors = []
    
    for email in emails:
        if email.get("autoArchive"):
            thread_id = email.get("threadId") or email.get("id")
            if not thread_id:
                continue
            
            try:
                result = subprocess.run(
                    [GOGCLI_PATH, "gmail", "thread", "modify", thread_id, 
                     "--remove", "INBOX", "--account", ACCOUNT, "--json"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    archived.append(email)
                else:
                    errors.append({
                        "threadId": thread_id,
                        "error": result.stderr or result.stdout
                    })
            except subprocess.TimeoutExpired:
                errors.append({"threadId": thread_id, "error": "Timeout"})
            except Exception as e:
                errors.append({"threadId": thread_id, "error": str(e)})
    
    output = {
        "archived": archived,
        "errors": errors,
        "archivedCount": len(archived),
        "errorCount": len(errors)
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
