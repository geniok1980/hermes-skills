# Daemon Internals — agent-daemon.sh

## Overview

`agent-daemon.sh` is a bash script that polls GitHub for `agent-ready` issues and spawns local agents (Gemini CLI, Trae) to work on them. It runs on the user's machine (or a server), not in GitHub Actions.

## Key Architecture Points

### set -e KILLS THE DAEMON SILENTLY

**CRITICAL: The daemon script MUST NOT use `set -e`.**

With `set -e`, any command failure exits the entire script silently:
- `jq -r '.[]'` returns non-zero when the JSON array is empty (no matching issues) → daemon exits with no output
- `curl` failure → daemon exits
- `grep` with no match → daemon exits

**Fix:** Omit `set -e`. Add `|| true` to pipeline commands that may legitimately return empty:

```bash
# BEFORE (broken):
curl ... | jq -r '.[] | "\(.number)|\(.title)"'

# AFTER (robust):
curl ... 2>/dev/null | jq -r 'if type=="array" then .[] | "\(.number)|\(.title)" else empty end' 2>/dev/null || true
```

### `--once` Flag Parsing Bug

The naive `MODE="${1:-once}"` does NOT match `--once` (with dashes). When invoked as `agent-daemon.sh --once`, `$MODE` becomes `"--once"` which doesn't match `once)` in the case statement.

**Fix:** Parse arguments explicitly:

```bash
MODE="once"
while [[ $# -gt 0 ]]; do
    case $1 in
        --daemon) MODE="daemon"; shift ;;
        --once|once) MODE="once"; shift ;;
        *) shift ;;
    esac
done
```

### Token Extraction

```bash
get_token() {
    cd "$WORK_DIR" && git remote get-url origin | grep -oP 'ghp_[^@]+' | head -1
}
```

The daemon reads the GitHub Personal Access Token embedded in the git remote URL (`https://ghp_xxx@github.com/...`). This avoids needing a separate token file.

### Issue Discovery

```bash
get_issues() {
    local filter="$1"
    curl -s -H "Authorization: token $TOKEN" \
        "https://api.github.com/repos/$REPO/issues?state=open&labels=agent-ready" | \
        jq -r '.[] | "\(.number)|\(.title)|\(.body // "")"'
}
```

Uses `jq -r` for raw output (no quotes). Parses with `while IFS='|' read`.

### Agent Spawning (Background Job Pattern)

Two approaches:

**Option A: Background process with polling (original)**

```bash
# Start Gemini in background with timeout
timeout 600 gemini "$prompt" > /tmp/gemini-$num.log 2>&1 &
pid=$!

# Wait with progress (max 60 × 10s = 10 min)
count=0
while kill -0 $pid 2>/dev/null && [ $count -lt 60 ]; do
    sleep 10
    count=$((count + 1))
    log "Waiting for Gemini... ($count/60)"
done

# Kill if still running
if kill -0 $pid 2>/dev/null; then
    log "Timeout reached, stopping Gemini"
    kill $pid 2>/dev/null || true
fi
```

Key insight: Use `&` to background the agent, track PID, and `kill -0 $pid` to check if still alive.

**Option B: Foreground with timeout (simpler)**

```bash
timeout 300 $GEMINI_BIN -p "$prompt" --approval-mode yolo --skip-trust > /tmp/gemini-$num.log 2>&1
local exit_code=$?
```

The foreground pattern is simpler and avoids the polling loop. Output is fully buffered, so you won't see progress until the whole log is written. Use `tail -f /tmp/gemini-N.log` in a separate terminal to monitor live.

### Issue Body Reading (for better agent context)

The original daemon only passes the issue title to the agent — this is often insufficient. Read the full issue body for richer context:

```bash
get_issue_body() {
    local num=$1
    local token=$(get_token)
    curl -s -H "Authorization: token $token" \
        "https://api.github.com/repos/$REPO/issues/$num" 2>/dev/null | \
        jq -r '.body // "No description"' 2>/dev/null || echo "No description"
}

# In run_gemini():
local body=$(get_issue_body "$num")
local prompt="Task: Implement GitHub Issue #$num from $REPO.\n\nTitle: $title\n\nIssue description:\n$body\n\n..."
```

### Close vs PR Mode

The daemon can operate in two modes:

| Mode | Behavior | When to use |
|------|----------|-------------|
| **PR mode** (default) | Create PR → CI runs → merge → auto-close | When CI/CD gates are needed before merge |
| **Close mode** | Direct commit to branch + close issue | Simple repos with no CI, or when changes are safe to apply directly |

**PR mode** (daemon creates PR, issue closes on merge):
```bash
git push -u origin "$branch"
gh pr create --title "Agent: Issue #$num" --body "Closes #$num" --base "$BRANCH"
```

**Close mode** (daemon closes issue after push, no PR):
```bash
git push -u origin "$branch"
curl -s -X PATCH -H "Authorization: token $token" \
    -H "Content-Type: application/json" \
    "https://api.github.com/repos/$REPO/issues/$num" \
    -d '{"state":"closed","labels":["completed"]}'
```

Note: In close mode, the branch with changes stays on GitHub but is never merged to main — a maintainer must merge manually or via merge workflow.

### Gemini CLI Path Discovery

Agents may not be in `PATH`. Check multiple locations:

```bash
if command -v gemini &>/dev/null || [ -x "/root/.hermes/node/bin/gemini" ]; then
    local gemini_cmd="gemini"
    command -v gemini &>/dev/null || gemini_cmd="/root/.hermes/node/bin/gemini"
fi
```

Known paths:
- `/root/.hermes/node/bin/gemini` — Hermes Agent's bundled location
- `gemini` — in PATH after install

### Branch Management

```bash
branch="agent/$num-task"

# Check if branch exists on remote
if git show-ref --quiet "origin/$branch" 2>/dev/null; then
    git checkout "$branch" 2>/dev/null || git checkout -b "$branch"
    git pull origin "$branch" 2>/dev/null || true
else
    git checkout -b "$branch" 2>/dev/null || git checkout "$branch"
fi
```

### Issue Claiming

Before spawning agent, mark issue as in-progress:

```bash
claim_issue() {
    local num=$1
    curl -s -X PATCH -H "Authorization: token $TOKEN" \
        -H "Content-Type: application/json" \
        "https://api.github.com/repos/$REPO/issues/$num" \
        -d '{"labels":["in-progress"],"assignees":["github-actions[bot]"]}' >/dev/null 2>&1
}
```

### Log Files

The daemon writes output to:
- `/tmp/gemini-$num.log` — Gemini output per issue
- `/tmp/trae-$num.log` — Trae output per issue

Monitor with: `tail -f /tmp/gemini-1.log`

## Daemon Modes

### `--once` (for cron)
```bash
*/5 * * * * /root/clawhost/scripts/agent-daemon.sh --once --gemini-only >> /var/log/agent-daemon.log 2>&1
```

### `--daemon` (continuous loop)
```bash
./scripts/agent-daemon.sh --daemon --gemini-only
```

Uses `$POLL_INTERVAL` (default 300 seconds) between cycles.

## Process State Checks

```bash
# Check if process is alive
kill -0 $pid 2>/dev/null && echo "alive" || echo "dead"

# Grep running processes (exclude grep itself)
ps aux | grep -E "gemini|agent-daemon" | grep -v grep
```

## Common Issues

### Agent in Plan Mode
Gemini CLI may enter "Plan Mode" and wait for confirmation before making changes. This blocks the daemon.

**Solution:** Hermes can directly implement the fix using terminal/file tools, bypassing the agent.

**Pattern:** When user asks "check if bug is fixed", the agent may be waiting. Hermes implements directly:

```bash
# 1. Read the relevant code file
# 2. Identify the fix needed
# 3. Use patch() to apply changes
# 4. Commit: git add -A && git commit -m "fix: issue #N"
# 5. Push: git push
# 6. Create PR via API
```

### Git Push Requires Upstream Set
```bash
git push -u origin HEAD  # -u sets upstream tracking
```

### PR Creation from Branch
```bash
gh pr create --title "Agent: Issue #$num" --body "Closes #$num" --base "$BRANCH"
```

Or via API:
```bash
curl -s -X POST -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  "https://api.github.com/repos/$REPO/pulls" \
  -d "{\"title\":\"Agent: Issue #$num\",\"body\":\"Closes #$num\",\"head\":\"agent/$num-task\",\"base\":\"$BRANCH\"}"
```

## Configuration Variables

```bash
REPO="geniok1980/clawhost-private"   # GitHub repo
BRANCH="Production"                   # Target branch for PRs
WORK_DIR="/root/clawhost"            # Working directory
POLL_INTERVAL=300                    # Seconds between checks
MAX_RETRIES=3                       # (reserved for future use)
```

## Verification

```bash
# Run once and see output
./scripts/agent-daemon.sh --once --gemini-only

# Check Gemini is available
which gemini || ls -la /root/.hermes/node/bin/gemini

# Check active processes
ps aux | grep gemini

# Monitor log
tail -f /tmp/gemini-1.log
```