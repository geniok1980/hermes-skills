---
name: multi-agent-github-orchestration
description: "Orchestrate autonomous coding agents (Gemini CLI, Trae) via GitHub Issues — issues as tasks, labels as routing, local daemon as the agent launcher, GitHub Actions CI/CD for gatekeeping."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Multi-Agent, GitHub, Gemini, Trae, Orchestration, CI/CD, Issue-Driven]
---

# Multi-Agent GitHub Orchestration

Use GitHub Issues as a task queue and autonomous coding agents (Gemini CLI, Trae) as workers, with GitHub Actions CI/CD as the quality gate.

## When to Use

- User wants agents to pick up tasks automatically from GitHub Issues
- Multiple agents (Gemini CLI, Trae) work in parallel on different tasks
- Need CI/CD checks before code reaches main branch
- User's workflow: throw raw issue description → agent takes it → delivers PR

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER (Product Manager)                    │
│                     Creates raw Issue on GitHub                   │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                         GITHUB REPO                              │
│  Issue #42 (labels: agent-ready, gemini, high)                  │
│         │                                                       │
│         │  GitHub Actions triggers on:                           │
│         │  - issue opened/labeled (agent-notify.yml)             │
│         │  - PR merged (auto-close.yml)                          │
│         │  - PR opened (ci.yml: lint, typecheck, test, build)    │
│         └───────────────────────────────────────────────────────┤
│                                                                   │
│    ┌──────────────────────────────────────────────────────────┐   │
│    │              LOCAL MACHINE (daemon/scheduler)             │   │
│    │                                                            │   │
│    │  agent-daemon.sh --daemon --gemini-only                   │   │
│    │         │                                                 │   │
│    │         ├──► Polls GitHub API every N seconds             │   │
│    │         │    GET /repos/OWNER/REPO/issues?labels=...     │   │
│    │         │                                                 │   │
│    │         ├──► Found issue with agent-ready + gemini?       │   │
│    │         │    1. Mark issue: agent-ready → in-progress    │   │
│    │         │    2. git checkout -b agent/42-task            │   │
│    │         │    3. Spawn: gemini "Fix issue #42..."         │   │
│    │         │    4. Wait for completion                      │   │
│    │         │    5. git push + gh pr create                  │   │
│    │         │                                                 │   │
│    │         └──► Found issue with agent-ready + trae?         │   │
│    │              (same pattern, different agent)               │   │
│    └──────────────────────────────────────────────────────────┘   │
│                               │                                  │
│                               ▼                                  │
│    ┌──────────────────────────────────────────────────────────┐   │
│    │                    AGENT (Gemini CLI / Trae)              │   │
│    │                                                            │   │
│    │  1. Reads CLAUDE.md for project conventions               │   │
│    │  2. Finds relevant code                                   │   │
│    │  3. Implements fix/feature                                │   │
│    │  4. Runs tests (bun run test)                             │   │
│    │  5. Commits: "fix: issue #42"                            │   │
│    │  6. Pushes branch                                         │   │
│    │  7. Creates PR: "Closes #42"                             │   │
│    └──────────────────────────────────────────────────────────┘   │
│                               │                                  │
│                               ▼                                  │
│    ┌──────────────────────────────────────────────────────────┐   │
│    │                    PULL REQUEST                           │   │
│    │                                                            │   │
│    │  Title: "Agent: Issue #42"                               │   │
│    │  Body: "Closes #42"                                       │   │
│    │  CI/CD: lint ✓ typecheck ✓ test ✓ build ✓                │   │
│    │  Review: maintainer approves                              │   │
│    │  Merge: main ← agent/42-task                              │   │
│    └──────────────────────────────────────────────────────────┘   │
│                               │                                  │
│                               ▼                                  │
│    ┌──────────────────────────────────────────────────────────┐   │
│    │                    GitHub Actions                          │   │
│    │  auto-close.yml: PR merged → issue #42 closed             │   │
│    └──────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────┘
```

## Critical Architecture Decision

**GitHub Actions CANNOT run local CLI agents.** Gemini CLI and Trae are installed locally on the developer's machine — they are not available in the GitHub Actions runner environment. Any workflow that tries to `gemini "..."` directly in a GitHub Action step will fail with "command not found".

The correct architecture is a **local daemon script** that:
1. Runs on the user's machine (or a always-on server)
2. Polls GitHub API for new agent-ready issues
3. Spawns local agents (Gemini CLI, Trae)
4. Commits and creates PRs via the GitHub API

## Labels Reference

| Label | Meaning |
|-------|---------|
| `agent-ready` | Task waiting for an agent to pick up |
| `in-progress` | Agent is actively working on this |
| `gemini` | Assigned to Gemini CLI agent |
| `trae` | Assigned to Trae agent |
| `either` | Any available agent can pick up |
| `needs-review` | PR created, awaiting review |
| `bug` | Bug report |
| `enhancement` | Feature request |

## Issue Lifecycle

```
1. User creates Issue → labels: agent-ready + gemini/trae
2. Daemon finds issue → marks in-progress
3. Agent spawns → works → commits → pushes → PR created
4. CI runs on PR → must pass all checks
5. Maintainer reviews and merges
6. auto-close.yml fires → Issue #42 closed automatically
```

## Quick Start

### 1. Configure GitHub Token (for daemon)

The daemon reads the GitHub token from the local git remote URL:
```bash
git remote get-url origin
# https://ghp_xxx@github.com/OWNER/REPO.git
# The daemon extracts: ghp_xxx
```

### 2. Start the Daemon

```bash
# Single cycle (for cron)
./scripts/agent-daemon.sh --once --gemini-only

# Continuous daemon
./scripts/agent-daemon.sh --daemon --gemini-only

# Cron job: every 5 minutes
*/5 * * * * /root/clawhost/scripts/agent-daemon.sh --once --gemini-only >> /var/log/agent-daemon.log 2>&1
```

### 3. Create an Issue for an Agent

On GitHub, create an issue with labels:
- `agent-ready` — required for the daemon to pick it up
- `gemini` or `trae` — which agent should handle it
- `high` / `medium` / `low` — priority (optional)

### 4. Agent Takes It

The daemon detects the new issue, spawns the agent, and the agent creates a PR.

## Repo-Specific Agent Configurations

Different repos may have different agent setups. Two common patterns:

### Pattern A: Local Daemon (clawhost-private)

- **Daemon:** `scripts/agent-daemon.sh` runs on the server, polls GitHub every 5 minutes
- **Branch convention:** feature branch from `Production`, then PR → merge
- **Token:** extracted from `git remote get-url origin` (ghp_ token in remote URL)
- **Agent types:** Gemini CLI and/or Trae CLI (installed locally)
- **Repo:** `geniok1980/clawhost-private`

### Pattern B: GitHub Actions (ai-photostudio)

- **Workflow:** `.github/workflows/gemini-agent.yml` triggered on `issues: [opened, labeled]`
- **Branch convention:** `agent/N-task` branch from `main`, then PR → merge
- **Token:** GitHub Actions token (automatic, no manual config)
- **GEMINI_API_KEY:** must be set as a repo secret in GitHub Settings
- **Repo:** `geniok1980/ai-photostudio`

### How to choose

| Factor | Local Daemon | GitHub Actions |
|--------|-------------|----------------|
| Setup complexity | Medium (install daemon, extract token) | Low (add workflow YAML) |
| Reliability | Depends on server uptime | Depends on GitHub runners |
| Agent binaries | Gemini CLI must be installed locally | Agent runs in workflow (if binary available) |
| Best for | Active daily development (instant pickup) | Occasional tasks (5-10min delay acceptable) |

When the user sends an issue link, first check which repo it belongs to, then use the appropriate workflow for formatting and handoff.

The user prefers to:
1. Create a raw Issue on GitHub (rough description)
2. Send Hermes the issue link
3. **Hermes formats it properly** with labels, structured description, and instructions
4. **Agent picks it up automatically** via the daemon

This means Hermes acts as the task formatter/editor between the user and the agent queue.

## Procedures

### Format an Issue for Agent (Hermes's Role)

When user sends an issue link, do the following via GitHub API:

```bash
# 1. View the issue
gh issue view N --json title,body,labels

# 2. Add appropriate labels
gh issue edit N --add-label agent-ready --add-label gemini --add-label high

# 3. Add structured comment with agent instructions
gh issue comment N --body "## 🤖 Agent Task

## Problem
[extracted from issue body]

## Steps
1. Read CLAUDE.md
2. Find relevant code
3. Implement fix
4. Test: bun run test
5. Commit and push
6. Create PR: Closes #N

## Acceptance Criteria
- [ ] Fix implemented
- [ ] Tests pass
- [ ] PR created"
```

### Check Agent Status

```bash
# View issues in progress
gh issue list --label in-progress

# View all agent-ready tasks
gh issue list --label agent-ready

# View PRs from agents
gh pr list --author github-actions[bot]

# View agent daemon logs
tail -f /tmp/gemini-N.log
```

## File Inventory

### Scripts

| File | Purpose |
|------|---------|
| `scripts/agent-daemon.sh` | Local daemon that polls GitHub and spawns agents |
| `scripts/agent-daemon.service` | systemd service unit |
| `scripts/agent-daemon.cron` | cron configuration |
| `scripts/agent_orchestrator.py` | Python alternative orchestrator |

### GitHub Files

| File | Purpose |
|------|---------|
| `.github/workflows/gemini-agent.yml` | GitHub Action (triggers on issue, but cannot run Gemini — legacy, kept for notifications) |
| `.github/workflows/trae-agent.yml` | Same for Trae |
| `.github/workflows/ci.yml` | CI: lint, typecheck, test, build |
| `.github/workflows/auto-close.yml` | Auto-close issue when PR merged |
| `.github/workflows/agent-notify.yml` | Log notifications on new agent tasks |
| `.github/ISSUE_TEMPLATE/agent-task.yml` | Issue template for agent tasks |
| `.github/ISSUE_TEMPLATE/bug-report.yml` | Bug report template |
| `.github/ISSUE_TEMPLATE/feature-request.yml` | Feature request template |
| `.github/AGENT_WORKFLOW.md` | Instructions for agents reading the repo directly |

## Limitations

- **Agents must be installed locally** — Gemini CLI and Trae run on the user's machine, not in GitHub Actions
- **Token permissions** — the git-embedded token needs `repo` scope to create branches, commits, and PRs
- **No live progress tracking** — daemon logs to `/tmp/gemini-N.log`; monitor with `tail -f`
- **Timeout** — daemon kills agents after 600 seconds (10 minutes) per task

## Pitfalls

1. **GitHub Actions cannot run Gemini CLI** — this is a sandboxing constraint, not a configuration issue. The workaround is the local daemon architecture.
2. **Token embedded in remote URL** — `ghp_` tokens expire. If the daemon starts failing with 403, regenerate the token and update the git remote.
3. **Labels must be exact** — the daemon checks for `agent-ready` AND `gemini`/`trae` as exact label names. Typos will cause silent skip.
4. **Issue number extraction from git remote** — use `git remote get-url origin | grep -oP 'ghp_[^@]+' | head -1`. Do NOT parse the token from environment variables in workflows.
5. **PR base branch** — the daemon defaults to `Production` branch. Adjust `BRANCH` variable in `agent-daemon.sh` if the default branch differs.
6. **`set -e` breaks the daemon silently** — never use `set -e` in the daemon script. `jq` returns non-zero on empty results, which causes the entire script to exit with no output. See `references/daemon-internals.md` for the fix.
7. **`--once` flag must be parsed properly** — `MODE="${1:-once}"` does NOT match `--once` (with dashes). Use explicit arg parsing with a while loop. See `references/daemon-internals.md`.
8. **Gemini CLI may not be in PATH** — Hermes bundles it at `/root/.hermes/node/bin/gemini`. Hardcode the path or check multiple locations.
9. **Foreground timeout is simpler than background polling** — the foreground pattern (`timeout 300 gemini -p ...`) avoids the polling loop. Output is buffered so monitor with `tail -f /tmp/gemini-N.log`.
10. **Complex task prompts trigger Plan Mode** — Gemini CLI enters Plan Mode when given multi-phase feature descriptions (e.g., "Phase 1: X, Phase 2: Y, Phase 3: Z"). This blocks write operations. Mitigations:
    - Give atomic single-file tasks when using Gemini CLI via the daemon
    - For complex multi-phase features, implement directly with Hermes tools (patch, write_file, terminal) instead of spawning Gemini CLI
    - Or break the feature into separate Issues, one per atomic change
11. **Zero-width Unicode characters in patches corrupt builds** — tools like `patch` or copy-paste can introduce invisible Unicode characters (U+200B zero-width space, etc.) into source code. The build fails with cryptic `Expected ")" but found "​"` errors. Fix: `sed -i 's/\\xe2\\x80\\x8b//g' file.ts` or rewrite the line without the invisible character.

## Verification

```bash
# Test daemon finds issues
./scripts/agent-daemon.sh --once --gemini-only

# Should output: "Found task: #N - Title" or "No pending tasks"

# Check Gemini is reachable
which gemini || ls /root/.hermes/node/bin/gemini

# Check active processes
ps aux | grep -E "gemini|agent-daemon" | grep -v grep
```

## References

- `references/github-api-patterns.md` — GitHub API patterns for issue/PR management
- `references/daemon-internals.md` — Detailed daemon architecture and internals
- `references/ci-cd-setup.md` — CI/CD gatekeeping configuration

## Hermes Intervention Pattern (Critical)

**Problem:** Agents (Gemini CLI) can enter "Plan Mode" — they analyze the issue, propose a plan, but cannot write files or run shell commands because tools like `write_file`, `run_shell_command`, and `exit_plan_mode` are blocked. The daemon waits indefinitely.
  - **Detection:** Look in `/tmp/gemini-N.log` for `[LocalAgentExecutor] Blocked call: Unauthorized tool call: 'write_file'` and the agent asking "Do you agree with this strategy?".
  - **Root cause:** Gemini CLI enters Plan Mode when the task prompt is too complex or contains multiple phases. A single atomic task (e.g., "fix this one file") usually avoids Plan Mode; a multi-feature prompt with phases 1-2-3 triggers it.

**Solution:** When agent is stuck in Plan Mode, Hermes should directly implement the fix using terminal/file tools. Do NOT try to restart Gemini CLI with a different prompt — the Plan Mode is a sandboxing constraint, not a prompt-tuning issue.

**Pattern for Direct Implementation:**

```bash
# 1. Identify the relevant code file
read_file(path/to/file.ts)

# 2. Find the bug and fix it
patch file.ts "old code" "new code"

# 3. Commit and push
git add -A && git commit -m "fix: issue #N" && git push origin agent/N-task

# 4. Create PR via API
curl -s -X POST -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  "https://api.github.com/repos/$REPO/pulls" \
  -d "{\"title\":\"Agent: Issue #N\",\"body\":\"Closes #N\",\"head\":\"agent/N-task\",\"base\":\"Production\"}"

# 5. Close the issue
curl -s -X PATCH -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  "https://api.github.com/repos/$REPO/issues/N" \
  -d '{"state": "closed"}'
```

**When to use:**
- User asks "is the bug fixed?" → check status, implement if not
- Agent enters Plan Mode → wait 60s, then Hermes takes over
- User says "just fix it" → direct implementation

## Troubleshooting

### GitHub Actions Cannot Run Gemini CLI
This is a sandboxing constraint — GitHub Actions runners don't have access to locally installed CLI tools.

**Workaround:** The daemon runs on the local machine and polls GitHub for work. Actions workflows are used for notifications and CI gates only, not for spawning agents.

### workflow_dispatch Returns "Not Found"
Workflow must be on the target branch before it can be triggered.

**Fix:** Push workflow files first, wait ~1 minute for GitHub to sync, then dispatch.

### Labels Not Triggering Daemon
Label names must be exact (`agent-ready`, not `agent ready` or `Agent-Ready`).

**Fix:** Use the GitHub API to add labels programmatically to ensure correct names.

### Token Expired (403 Forbidden)
GitHub PATs embedded in git remotes expire periodically.

**Fix:** Regenerate token, update remote:
```bash
git remote set-url origin https://ghp_NEWTOKEN@github.com/owner/repo.git
```