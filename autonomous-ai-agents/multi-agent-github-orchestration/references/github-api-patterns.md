# GitHub API Patterns for Multi-Agent Orchestration

Reference patterns for managing GitHub Issues and PRs via API.

## Authentication

Extract token from git remote URL (used by `agent-daemon.sh`):

```bash
TOKEN=$(git remote get-url origin | grep -oP 'ghp_[^@]+' | head -1)
```

Or use `gh` CLI (pre-installed in GitHub Actions runners):

```bash
gh auth login --hostname github.com --git-protocol https
echo "$GH_TOKEN" | gh auth login --hostname github.com
```

## Base URL

```
https://api.github.com/repos/{owner}/{repo}
```

## Common Operations

### Get Issue Details

```bash
curl -s -H "Authorization: token $TOKEN" \
  "https://api.github.com/repos/$REPO/issues/$NUM" | \
  jq '{number: .number, title: .title, state: .state, labels: [.labels[].name]}'
```

### List Issues with Labels

```bash
# Agent-ready issues
curl -s -H "Authorization: token $TOKEN" \
  "https://api.github.com/repos/$REPO/issues?state=open&labels=agent-ready" | \
  jq -r '.[] | "\(.number)|\(.title)"'

# Issues filtered by multiple labels
curl -s -H "Authorization: token $TOKEN" \
  "https://api.github.com/repos/$REPO/issues?state=open&labels=agent-ready,gemini"
```

### Update Issue Labels

```bash
# Add labels and assignee
curl -s -X PATCH \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  "https://api.github.com/repos/$REPO/issues/$NUM" \
  -d '{"labels": ["bug", "gemini", "agent-ready", "high"], "assignees": ["username"]}'

# Remove one label, add another
gh issue edit $NUM --remove-label agent-ready --add-label in-progress
```

### Add Comment

```bash
curl -s -X POST \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  "https://api.github.com/repos/$REPO/issues/$NUM/comments" \
  -d '{"body": "## Agent Task\n\nInstructions..."}'
```

### Create Pull Request

```bash
curl -s -X POST \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  "https://api.github.com/repos/$REPO/pulls" \
  -d '{
    "title": "Agent: Issue #42",
    "body": "Closes #42",
    "head": "agent/42-task",
    "base": "Production"
  }' | jq -r '.html_url'
```

### List PRs

```bash
# By state
curl -s -H "Authorization: token $TOKEN" \
  "https://api.github.com/repos/$REPO/pulls?state=all" | \
  jq -r '.[] | {number: .number, title: .title, state: .state, head: .head.ref}'

# By branch head
gh pr list --head "agent/42-task" --json number,title
```

### Close Issue

```bash
curl -s -X PATCH \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  "https://api.github.com/repos/$REPO/issues/$NUM" \
  -d '{"state": "closed"}'
```

### Trigger Workflow Dispatch

Note: Requires workflow ID, not workflow name.

```bash
# Get workflow ID first
curl -s -H "Authorization: token $TOKEN" \
  "https://api.github.com/repos/$REPO/actions/workflows" | \
  jq -r '.workflows[] | {name: .name, id: .id}'

# Dispatch (note: often "Not Found" — workflow must be on target branch)
curl -s -X POST \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  "https://api.github.com/repos/$REPO/actions/workflows/{WORKFLOW_ID}/dispatch" \
  -d '{"ref": "Production", "inputs": {"issue_number": "42"}}'
```

## JQ Tips

```bash
# Extract array of label names
jq -r '.labels[].name'

# Extract single value
jq -r '.title'

# Multi-line output with pipe separator
jq -r '.[] | "\(.number)|\(.title)"'

# Check if array contains value
jq -r '.labels[].name' | grep -q "agent-ready"
# or
jq -r '.labels | any(.name == "agent-ready")'

# Escape newlines in body for GitHub API
body=$(jq -r '.body // ""' <<< "$json")
body_escaped="${body//$'\n'/\\n}"
```

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Not Found` on workflow dispatch | Workflow not on target branch yet | Push workflow first, wait for sync |
| `403 Forbidden` | Token expired or missing `repo` scope | Regenerate token, update git remote |
| `422 Unprocessable Entity` | Invalid label name or branch ref | Check label exists, branch name format |

## Workflow Run Log Download

```bash
curl -s -H "Authorization: token $TOKEN" \
  "https://api.github.com/repos/$REPO/actions/runs" | \
  jq -r '.workflow_runs[] | {id: .id, name: .name, status: .status, conclusion: .conclusion}'
```

Get specific run details:
```bash
curl -s -H "Authorization: token $TOKEN" \
  "https://api.github.com/repos/$REPO/actions/runs/{RUN_ID}" | \
  jq '{id: .id, status: .status, conclusion: .conclusion, html_url: .html_url}'
```