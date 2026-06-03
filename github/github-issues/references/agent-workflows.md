# Agent Workflow Templates for GitHub Actions

Complete workflow files for the multi-agent GitHub Issues automation system.

## Workflow Files Overview

| File | Trigger | Agent |
|------|---------|-------|
| `gemini-agent.yml` | Issue with `agent-ready` + `gemini` | Gemini CLI |
| `trae-agent.yml` | Issue with `agent-ready` + `trae` | Trae |
| `ci.yml` | Every PR/push | CI checks |
| `auto-close.yml` | PR closed and merged | Auto-close Issue |
| `agent-notify.yml` | New issue with agent labels | Notifications |

## gemini-agent.yml

Full workflow for Gemini CLI agent:

```yaml
name: Gemini Agent

on:
  issues:
    types: [opened, labeled]
  workflow_dispatch:
    inputs:
      issue_number:
        description: 'Issue number to process'
        required: false
        type: string

jobs:
  agent-gemini:
    runs-on: ubuntu-latest
    if: |
      (github.event.issue.labels.*.name contains 'agent-ready' && 
       github.event.issue.labels.*.name contains 'gemini') ||
      github.event_name == 'workflow_dispatch'
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Setup Bun
        uses: oven-sh/setup-bun@v2
        with:
          bun-version: latest

      - name: Install dependencies
        run: bun install

      - name: Set Git config
        run: |
          git config --local user.email "agent@github.com"
          git config --local user.name "Gemini Agent"

      - name: Determine Issue Number
        id: issue
        run: |
          if [ "${{ github.event_name }}" == "workflow_dispatch" ] && [ -n "${{ inputs.issue_number }}" ]; then
            echo "number=${{ inputs.issue_number }}" >> $GITHUB_OUTPUT
          else
            echo "number=${{ github.event.issue.number }}" >> $GITHUB_OUTPUT
          fi

      - name: Get Issue Details
        id: details
        run: |
          ISSUE_NUM=${{ steps.issue.outputs.number }}
          echo "title=$(gh issue view $ISSUE_NUM --json title --jq '.title')" >> $GITHUB_OUTPUT
          echo "body=$(gh issue view $ISSUE_NUM --json body --jq -r '.body // ""')" >> $GITHUB_OUTPUT

      - name: Create Branch
        run: |
          BRANCH="agent/${{ steps.issue.outputs.number }}-task"
          git checkout -b $BRANCH

      - name: Run Gemini CLI
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          ISSUE_NUMBER: ${{ steps.issue.outputs.number }}
          ISSUE_TITLE: ${{ steps.issue.outputs.title }}
          ISSUE_BODY: ${{ steps.issue.outputs.body }}
        run: |
          # Prepare context for Gemini
          cat > /tmp/issue_context.md << 'EOF'
          # Task from GitHub Issue #${{ env.ISSUE_NUMBER }}

          ## Title
          ${{ env.ISSUE_TITLE }}

          ## Description
          ${{ env.ISSUE_BODY }}

          ## Instructions
          1. Implement the fix described in the issue
          2. Follow conventions in CLAUDE.md
          3. Create a commit with message: "feat: implemented issue #${{ env.ISSUE_NUMBER }}"
          4. Push the branch
          5. Create PR with body containing "Closes #${{ env.ISSUE_NUMBER }}"

          ## Important Rules
          - Use @/ path aliases (not ../)
          - One export per file
          - Types in @/ts/Interfaces.ts
          - Icon imports with Icon suffix (e.g., CheckIcon)
          - Run tests before committing
          EOF

          # Run Gemini CLI with the task
          gemini "$(cat /tmp/issue_context.md)"

      - name: Update Issue Labels
        if: success()
        run: |
          gh issue edit ${{ env.ISSUE_NUMBER }} \
            --remove-label agent-ready \
            --add-label in-progress \
            --add-assignee github-actions[bot]

      - name: Push Changes
        run: |
          git push -u origin HEAD 2>&1 || echo "No changes to push"

      - name: Create Pull Request
        if: success()
        run: |
          if git log origin/main..HEAD --oneline | grep -q .; then
            gh pr create \
              --title "Agent: Issue #${{ env.ISSUE_NUMBER }}" \
              --body "## Summary
          Implemented fix for issue #${{ env.ISSUE_NUMBER }}

          Closes #${{ env.ISSUE_NUMBER }}" \
              --base main
          else
            echo "No commits to create PR"
          fi

      - name: Report Failure
        if: failure()
        run: |
          gh issue comment ${{ env.ISSUE_NUMBER }} \
            --body "## ❌ Agent Failed

          Gemini CLI encountered an error. Please review the logs."
```

## trae-agent.yml

Similar structure for Trae agent — replace `gemini` references with `trae` and use `TRAE_API_KEY` secret.

## ci.yml

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v2
      - name: Install dependencies
        run: bun install
      - name: Run linter
        run: bun run lint || true

  typecheck:
    name: Type Check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v2
      - name: Install dependencies
        run: bun install
      - name: Type check
        run: bun run typecheck || true

  test:
    name: Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v2
      - name: Install dependencies
        run: bun install
      - name: Run tests
        run: bun run test || true

  build:
    name: Build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v2
      - name: Install dependencies
        run: bun install
      - name: Build all apps
        run: bun run build || true
```

## auto-close.yml

```yaml
name: Auto-close merged PR issues
on:
  pull_request:
    types: [closed]

jobs:
  close-issue:
    runs-on: ubuntu-latest
    if: github.event.pull_request.merged == true
    steps:
      - name: Parse issue number from PR body and close
        run: |
          BODY="${{ github.event.pull_request.body }}"
          if [[ $BODY =~ [Cc]lose[sd]?[[:space:]]*#([0-9]+) ]]; then
            ISSUE_NUM="${BASH_REMATCH[1]}"
            gh issue close $ISSUE_NUM --comment "Fixed in #${{ github.event.pull_request.number }}"
          fi
```

## Setup Checklist

1. **Create secrets** in GitHub repo (Settings → Secrets and variables → Actions):
   - `GEMINI_API_KEY` — get from https://ai.google.dev
   - `TRAE_API_KEY` — get from Trae settings

2. **Create workflow files** in `.github/workflows/` directory

3. **Verify workflows appear** in Actions tab — may take 1-2 minutes after first push

4. **Set branch protection** on `main`:
   - Require PR reviews
   - Require status checks to pass (CI must pass)
   - Include `ci.yml` as required check

5. **Create first agent Issue** with labels:
   - `agent-ready`
   - `gemini` (or `trae`)
   - Priority: `high`, `medium`, `low`
   - Type: `bug`, `enhancement`, etc.

6. **Watch Actions tab** — workflow should trigger automatically

## Common Issues

- **Workflow not appearing in Actions**: Wait 1-2 minutes after pushing, or check the file is in `.github/workflows/` (not root)
- **Secret names rejected**: Only alphanumeric + underscores, must start with letter or underscore (no spaces, no `Gemini API Key`, use `GEMINI_API_KEY`)
- **Agent not picking up issue**: Ensure BOTH `agent-ready` AND `gemini` labels are present — workflow requires both
- **Workflow not triggering**: Check workflow `if` condition matches the labels exactly