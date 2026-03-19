---
name: github
description: Work with GitHub from OpenClaw using gh, GitHub API calls, release monitoring, repository search, SSH troubleshooting, and GitHub-to-skill packaging helpers. Use when the task involves repos, PRs, issues, CI, release checks, repository discovery, or GitHub-related setup and repair.
---

# GitHub

Use this as the single GitHub skill for OpenClaw.

## Main capabilities

- PR, issue, and workflow operations via `gh`
- Repository search and comparison
- Release monitoring and breaking-change checks
- SSH connectivity diagnosis for GitHub access
- Converting GitHub repos into skill scaffolds

## Standard operations

### Pull requests and CI
```bash
gh pr checks 55 --repo owner/repo
gh run list --repo owner/repo --limit 10
gh run view <run-id> --repo owner/repo --log-failed
```

### Advanced API queries
```bash
gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'
```

### Repository search
Use the merged helper script:
```bash
python3 scripts/github_search.py search "whatsapp bot automation"
python3 scripts/github_search.py details owner repo
```

### Release monitoring
Use the merged helper script:
```bash
bash scripts/check-releases.sh
```
Or query the API directly:
```bash
curl -s https://api.github.com/repos/openclaw/openclaw/releases/latest | jq '.tag_name, .body, .published_at'
```

### SSH fix
If GitHub SSH fails on port 22, test and switch to 443:
```bash
ssh -T git@github.com
ssh -T -p 443 git@ssh.github.com
```
Then configure `~/.ssh/config` to use `ssh.github.com:443` for `github.com`.

### Repo to skill packaging
Use the merged helper scripts:
```bash
python3 scripts/fetch_github_info.py <repo-url>
python3 scripts/create_github_skill.py <repo-url>
```

## Rules

- Prefer `gh` for normal repo work.
- Use the search script when discovery or comparison is the real task.
- Use release monitoring only when version tracking matters.
- Use SSH repair only when connectivity is broken.
- Use repo-to-skill packaging only when the goal is explicitly to turn a repo into a skill.

## OpenClaw guidance

- Use this skill as the single GitHub entry point.
- Do not keep separate `github-search`, `github-release-monitor`, `github-ssh-fix`, or `github-to-skills` skills active beside it.
