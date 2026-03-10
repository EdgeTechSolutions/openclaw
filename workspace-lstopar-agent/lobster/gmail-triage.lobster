name: gmail-triage
description: Nightly personal Gmail triage — fetch, classify, archive, summarise to Telegram

args:
  account:
    default: "luka@stopar.si"
    description: Google account to use with gogcli
  window:
    default: "27h"
    description: Time window to scan (newer_than)

steps:
  - id: fetch-emails
    command: /workspace/.npm-global/bin/gogcli gmail search "newer_than:27h in:inbox" --max 200 --account luka@stopar.si --json

  - id: classify
    command: python3 /workspace/lobster/helpers/classify-emails.py
    stdin: $fetch-emails.stdout

  - id: archive
    command: python3 /workspace/lobster/helpers/archive-emails.py
    stdin: $classify.stdout

  - id: post-summary
    command: python3 /workspace/lobster/helpers/post-summary.py
    stdin: $classify.stdout
