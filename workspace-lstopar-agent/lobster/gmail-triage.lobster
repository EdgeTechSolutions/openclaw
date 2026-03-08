name: gmail-triage
description: Nightly personal Gmail triage — fetch, classify, archive, summarise to Telegram
args:
  account:
    default: "luka@stopar.si"
    description: Google account to use with gog
  window:
    default: "27h"
    description: Time window to scan (newer_than)
  telegram_chat:
    default: "8403014547"
    description: Telegram chat ID for summary
  telegram_topic:
    default: "1299"
    description: Telegram topic ID (#comm @personal)

steps:
  - id: fetch-emails
    command: >
      exec --json "gog gmail search 'newer_than:27h in:inbox' --max 200 --account luka@stopar.si --json"

  - id: check-empty
    command: >
      state.get --key fetch-emails | where 'length > 0'

  - id: classify
    approval: false
    command: >
      state.get --key fetch-emails |
      clawd.invoke --tool llm-task
        --prompt "Classify each Gmail email for Luka Stopar. Input is a JSON array. Return a JSON array where each item has: {id, threadId, subject, sender, category}. Categories (exactly one): Actionable | Informational | Updates | LinkedIn | Promotions | Invoices | Trading212 | Qogita | GoogleWorkspace | Google | Apple | Bitstamp | Wise | GitHub | Revolut | Forums | Calendar. Only return raw JSON array."
        --input-key data

  - id: archive-auto
    command: >
      state.get --key classify |
      where '.category == "Updates" or .category == "LinkedIn" or .category == "GitHub" or .category == "Revolut" or .category == "Trading212" or .category == "Qogita" or .category == "Informational"' |
      exec --json "while IFS= read -r item; do
        tid=$(echo \"$item\" | python3 -c \"import sys,json; print(json.load(sys.stdin)['threadId'])\");
        gog gmail thread modify \"$tid\" --remove INBOX --account luka@stopar.si --json;
      done"

  - id: post-summary
    command: >
      state.get --key classify |
      clawd.invoke --tool llm-task
        --prompt "Format a Telegram summary of Gmail triage results. Input is the classified email array. Group by category with emoji headers. Use gmail links: https://mail.google.com/mail/u/0/#all/{threadId} for archived, #inbox/{threadId} for kept. Return JSON with key 'message' containing the formatted Telegram text. Include counts. Mark archived categories with 🗂, inbox-kept with 🔔."
        --input-key data |
      pick '.message' |
      clawd.invoke --tool message
        --args-json '{"action": "send", "to": "8403014547", "threadId": "1299"}'
        --input-key message
