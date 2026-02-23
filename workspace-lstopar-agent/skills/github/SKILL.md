# GitHub Skill

Uses the `gh` CLI to interact with GitHub repositories, issues, and pull requests.

## Installation

The `gh` CLI is already installed on the host (`/usr/bin/gh`). No additional installation needed.

## Authentication

Run:
```bash
gh auth login
```

Follow the prompts to authenticate with GitHub.

## Usage

```bash
# List repositories
gh repo list

# View repository
gh repo view EdgeTechSolutions/AITools

# List issues
gh issue list --repo EdgeTechSolutions/AITools

# List pull requests
gh pr list --repo EdgeTechSolutions/AITools

# Create issue
gh issue create --repo EdgeTechSolutions/AITools --title "Bug" --body "Description"
```

## Notes

- The `gh` CLI is installed on the host, not in the sandbox
- Authentication is stored in `~/.config/gh/` on the host
- This skill is a wrapper around the `gh` CLI