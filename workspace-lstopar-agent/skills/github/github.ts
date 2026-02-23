#!/usr/bin/env node

/**
 * GitHub Skill - Wrapper around gh CLI
 * Uses the host-installed gh CLI to interact with GitHub
 */

import { execSync } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';

interface GitHubConfig {
  auth?: {
    token?: string;
    host?: string;
  };
}

class GitHubSkill {
  private ghPath: string;

  constructor() {
    this.ghPath = '/usr/bin/gh';
    if (!fs.existsSync(this.ghPath)) {
      throw new Error('gh CLI not found at /usr/bin/gh');
    }
  }

  private runCommand(cmd: string): string {
    try {
      return execSync(cmd, { encoding: 'utf8', stdio: 'pipe' });
    } catch (error: any) {
      if (error.stdout) return error.stdout;
      if (error.stderr) throw new Error(error.stderr.trim());
      throw error;
    }
  }

  /** Check if authenticated */
  authStatus(): { authenticated: boolean; host?: string } {
    try {
      const output = this.runCommand(`${this.ghPath} auth status`);
      return { authenticated: output.includes('Logged in to github.com'), host: 'github.com' };
    } catch (error) {
      return { authenticated: false };
    }
  }

  /** List repositories */
  listRepos(visibility?: 'public' | 'private' | 'all'): Array<{ name: string; url: string }> {
    const output = this.runCommand(`${this.ghPath} repo list --json nameWithOwner,url --limit 100 ${visibility ? `--${visibility}` : ''}`);
    const repos = JSON.parse(output);
    return repos.map((r: any) => ({ name: r.nameWithOwner, url: r.url }));
  }

  /** View repository */
  viewRepo(owner: string, repo: string): any {
    const output = this.runCommand(`${this.ghPath} repo view ${owner}/${repo} --json nameWithOwner,description,url,isPrivate,createdAt,pushedAt`);
    return JSON.parse(output);
  }

  /** List issues */
  listIssues(owner: string, repo: string, state?: 'open' | 'closed' | 'all'): any[] {
    const output = this.runCommand(`${this.ghPath} issue list --repo ${owner}/${repo} --json number,title,state,createdAt,updatedAt,url ${state ? `--state ${state}` : ''}`);
    return JSON.parse(output);
  }

  /** List pull requests */
  listPRs(owner: string, repo: string, state?: 'open' | 'closed' | 'all'): any[] {
    const output = this.runCommand(`${this.ghPath} pr list --repo ${owner}/${repo} --json number,title,state,createdAt,updatedAt,url ${state ? `--state ${state}` : ''}`);
    return JSON.parse(output);
  }

  /** Create issue */
  createIssue(owner: string, repo: string, title: string, body: string, labels?: string[]): any {
    const labelStr = labels ? `--label "${labels.join(',')}"` : '';
    const output = this.runCommand(`${this.ghPath} issue create --repo ${owner}/${repo} --title "${title}" --body "${body}" ${labelStr} --json number,title,url`);
    return JSON.parse(output);
  }
}

// CLI
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  const github = new GitHubSkill();

  switch (command) {
    case 'auth':
      const status = github.authStatus();
      console.log(status.authenticated ? '✅ Authenticated' : '❌ Not authenticated');
      break;

    case 'repos':
      const repos = github.listRepos(args[1] as any);
      repos.forEach(r => console.log(`- ${r.name}: ${r.url}`));
      break;

    case 'view':
      const [owner, repo] = args.slice(1);
      if (!owner || !repo) {
        console.error('Usage: github view <owner> <repo>');
        process.exit(1);
      }
      const repoInfo = github.viewRepo(owner, repo);
      console.log(JSON.stringify(repoInfo, null, 2));
      break;

    case 'issues':
      const [owner2, repo2] = args.slice(1);
      if (!owner2 || !repo2) {
        console.error('Usage: github issues <owner> <repo> [state]');
        process.exit(1);
      }
      const issues = github.listIssues(owner2, repo2, args[3] as any);
      console.log(JSON.stringify(issues, null, 2));
      break;

    case 'prs':
      const [owner3, repo3] = args.slice(1);
      if (!owner3 || !repo3) {
        console.error('Usage: github prs <owner> <repo> [state]');
        process.exit(1);
      }
      const prs = github.listPRs(owner3, repo3, args[3] as any);
      console.log(JSON.stringify(prs, null, 2));
      break;

    default:
      console.log(`Usage: github <command>

Commands:
  auth              Check authentication status
  repos [visibility]  List repositories (public/private/all)
  view <owner> <repo>  View repository details
  issues <owner> <repo> [state]  List issues
  prs <owner> <repo> [state]  List pull requests`);
  }
}

main().catch((e) => {
  console.error('Error:', e.message);
  process.exit(1);
});