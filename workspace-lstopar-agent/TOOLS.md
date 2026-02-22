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

## SSH

- home-server → 192.168.1.100, user: admin

## TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
