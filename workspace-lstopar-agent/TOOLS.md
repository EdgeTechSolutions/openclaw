# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- API credentials and authentication methods
- Any environment-specific details

---

## Sandbox NPM Installs

- **Always install skill CLIs via npm inside the sandbox**, not on the host
- Local prefix: `~/.npm-global` → persists at `/workspace/.npm-global/` (bind-mounted)
- Command: `mkdir -p ~/.npm-global && npm config set prefix ~/.npm-global && npm install -g <package>`
- Add to PATH: `export PATH="/workspace/.npm-global/bin:$PATH"`
- Installed: `confluence-cli`
- **After installing a skill**: always install its CLI tool via npm too, then ask the user for any required credentials/API keys

## Temp Files in Sandbox

- The `write` tool is sandboxed to the workspace — can't write to `/tmp`
- **Always write temp files to `/workspace/tmp/`** (gitignored, writable by both `write` tool and `exec`)
- `/workspace/tmp/` persists across container restarts but is excluded from git
- Example: `write("tmp/confluence-update.md", content)` then reference from exec

## Confluence CLI

- **Never use `--format markdown`** — it breaks JSON code blocks (HTML entity escaping)
- **Always convert markdown → Confluence storage format (XHTML)** using the converter script at `/workspace/tmp/md-to-confluence.cjs`
- Workflow:
  1. Write content as markdown to a `.md` file
  2. Convert: `NODE_PATH=/workspace/.npm-global/lib/node_modules node /workspace/tmp/md-to-confluence.cjs input.md output.html`
  3. Upload: `confluence update <pageId> --file output.html --format storage`
- The converter handles: code blocks → `<ac:structured-macro>` with CDATA, blockquotes → info macros, tables, etc.
- Requires `marked` npm package (installed at `/workspace/.npm-global/lib/node_modules/marked`)

## Sending Large Media (Videos, Large Images) via Telegram

The `message` tool can't send local workspace files directly. Workaround:
1. Upload to **litterbox.catbox.moe** (24h temp hosting):
   ```bash
   curl -s -F "reqtype=fileupload" -F "time=24h" -F "fileToUpload=@/path/to/file.mp4" https://litterbox.catbox.moe/resources/internals/api.php
   ```
2. Send the returned URL via `message(action=send, media=<url>)`

For images: freeimage.host works (see existing pattern). For video: use litterbox.

## SSH

- home-server → 192.168.1.100, user: admin

## TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
