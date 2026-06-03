---
name: github-repo-management
description: "Clone/create/fork repos; manage remotes, releases."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GitHub, Repositories, Git, Releases, Secrets, Configuration]
    related_skills: [github-auth, github-pr-workflow, github-issues]
---

# GitHub Repository Management

Create, clone, fork, configure, and manage GitHub repositories. Each section shows `gh` first, then the `git` + `curl` fallback.

## Prerequisites

- Authenticated with GitHub (see `github-auth` skill)

### Setup

```bash
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  AUTH="gh"
else
  AUTH="git"
  if [ -z "$GITHUB_TOKEN" ]; then
    if [ -f ~/.hermes/.env ] && grep -q "^GITHUB_TOKEN=" ~/.hermes/.env; then
      GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" ~/.hermes/.env | head -1 | cut -d= -f2 | tr -d '\\n\\r')
    elif grep -q "github.com" ~/.git-credentials 2>/dev/null; then
      GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | sed 's|https://[^:]*:\\([^@]*\\)@.*|\\1|')
    fi
  fi
fi

# Fallback: extract token from the current repo's remote URL
# Works when token is embedded in the URL (https://TOKEN@github.com/...)
if [ -z "$GITHUB_TOKEN" ]; then
  REMOTE_URL=$(git remote get-url origin 2>/dev/null)
  # Write to temp file first (more reliable than subshell in some bash contexts)
  echo "$REMOTE_URL" | grep -oP 'ghp_[^@]+' > /tmp/ghtoken.txt 2>/dev/null
  read -r GITHUB_TOKEN < /tmp/ghtoken.txt 2>/dev/null
  rm -f /tmp/ghtoken.txt
fi

# Get your GitHub username (needed for several operations)
if [ "$AUTH" = "gh" ]; then
  GH_USER=$(gh api user --jq '.login')
else
  GH_USER=$(curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user | python3 -c "import sys,json; print(json.load(sys.stdin)['login'])")
fi
```

If you're inside a repo already:

```bash
REMOTE_URL=$(git remote get-url origin)
OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)
```

---

## 1. Cloning Repositories

Cloning is pure `git` — works identically either way:

```bash
# Clone via HTTPS (works with credential helper or token-embedded URL)
git clone https://github.com/owner/repo-name.git

# Clone into a specific directory
git clone https://github.com/owner/repo-name.git ./my-local-dir

# Shallow clone (faster for large repos)
git clone --depth 1 https://github.com/owner/repo-name.git

# Clone a specific branch
git clone --branch develop https://github.com/owner/repo-name.git

# Clone via SSH (if SSH is configured)
git clone git@github.com:owner/repo-name.git
```

**With gh (shorthand):**

```bash
gh repo clone owner/repo-name
gh repo clone owner/repo-name -- --depth 1
```

## 2. Creating Repositories

**With gh:**

```bash
# Create a public repo and clone it
gh repo create my-new-project --public --clone

# Private, with description and license
gh repo create my-new-project --private --description "A useful tool" --license MIT --clone

# Under an organization
gh repo create my-org/my-new-project --public --clone

# From existing local directory
cd /path/to/existing/project
gh repo create my-project --source . --public --push
```

**With git + curl:**

```bash
# Create the remote repo via API
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user/repos \
  -d '{
    "name": "my-new-project",
    "description": "A useful tool",
    "private": false,
    "auto_init": true,
    "license_template": "mit"
  }'

# Clone it
git clone https://github.com/$GH_USER/my-new-project.git
cd my-new-project

# -- OR -- push an existing local directory to the new repo
cd /path/to/existing/project
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/$GH_USER/my-new-project.git
git push -u origin main
```

To create under an organization:

```bash
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/orgs/my-org/repos \
  -d '{"name": "my-new-project", "private": false}'
```

### Public Showcase Repo for a Private Project

When a project's actual code lives in a **private** repo but you want a public presence,
create a separate **showcase repo** with just documentation:

```bash
# 1. Create the public showcase repo (with auto_init to get a README)
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user/repos \
  -d '{
    "name": "project-name",
    "description": "Brand Name — elevator pitch",
    "private": false,
    "auto_init": true
  }'

# 2. Overwrite the auto-generated README with full documentation
#    First, get the existing README's SHA (required for update):
read -r GITHUB_TOKEN < /tmp/ghtoken.txt
readme_sha=$(curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/geniok1980/project-name/contents/README.md \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('sha',''))")

# 3. Push the new README using the SHA
readme_b64=$(python3 -c "import base64; print(base64.b64encode(open('README.md','rb').read()).decode())")
curl -s -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  https://api.github.com/repos/geniok1980/project-name/contents/README.md \
  -d "{
    \"message\": \"docs: add full README\",
    \"content\": \"$readme_b64\",
    \"sha\": \"$readme_sha\",
    \"branch\": \"main\"
  }"

# 4. Update the landing page / profile README to link to the showcase repo
#    Never link to the private code repo from public pages.
```

**Key points:**\n- The showcase repo contains **documentation only** — no code, no build artifacts\n- The landing page and profile README link to the showcase repo, not the private one\n- `auto_init=true` creates an initial commit, so file updates need the `sha` parameter\n- To update repo visibility later: `curl -X PATCH -d '{"private": false}'` or `{"private": true}`\n- **README is a draft** — After creating the showcase repo and writing the README, present it to the user for review. README content (strategy descriptions, exchange names, tech stack, ML roles) is domain-specific and the user will almost certainly want corrections. Don't consider the README final until the user explicitly approves it.

### From a Template

**With gh:**

```bash
gh repo create my-new-app --template owner/template-repo --public --clone
```

**With curl:**

```bash
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/owner/template-repo/generate \
  -d '{"owner": "'"$GH_USER"'", "name": "my-new-app", "private": false}'
```

## 3. Forking Repositories

**With gh:**

```bash
gh repo fork owner/repo-name --clone
```

**With git + curl:**

```bash
# Create the fork via API
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/owner/repo-name/forks

# Wait a moment for GitHub to create it, then clone
sleep 3
git clone https://github.com/$GH_USER/repo-name.git
cd repo-name

# Add the original repo as "upstream" remote
git remote add upstream https://github.com/owner/repo-name.git
```

### Keeping a Fork in Sync

```bash
# Pure git — works everywhere
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

**With gh (shortcut):**

```bash
gh repo sync $GH_USER/repo-name
```

## 4. Repository Information

**With gh:**

```bash
gh repo view owner/repo-name
gh repo list --limit 20
gh search repos "machine learning" --language python --sort stars
```

**With curl:**

```bash
# View repo details
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO \
  | python3 -c "
import sys, json
r = json.load(sys.stdin)
print(f\"Name: {r['full_name']}\")
print(f\"Description: {r['description']}\")
print(f\"Stars: {r['stargazers_count']}  Forks: {r['forks_count']}\")
print(f\"Default branch: {r['default_branch']}\")
print(f\"Language: {r['language']}\")"

# List your repos
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/user/repos?per_page=20&sort=updated" \
  | python3 -c "
import sys, json
for r in json.load(sys.stdin):
    vis = 'private' if r['private'] else 'public'
    print(f\"  {r['full_name']:40}  {vis:8}  {r.get('language', ''):10}  ★{r['stargazers_count']}\")"

# Search repos
curl -s \
  "https://api.github.com/search/repositories?q=machine+learning+language:python&sort=stars&per_page=10" \
  | python3 -c "
import sys, json
for r in json.load(sys.stdin)['items']:
    print(f\"  {r['full_name']:40}  ★{r['stargazers_count']:6}  {r['description'][:60] if r['description'] else ''}\")"
```

## 5. Repository Settings

**With gh:**

```bash
gh repo edit --description "Updated description" --visibility public
gh repo edit --enable-wiki=false --enable-issues=true
gh repo edit --default-branch main
gh repo edit --add-topic "machine-learning,python"
gh repo edit --enable-auto-merge
```

**With curl:**

```bash
curl -s -X PATCH \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO \
  -d '{
    "description": "Updated description",
    "has_wiki": false,
    "has_issues": true,
    "private": false,
    "allow_auto_merge": true
  }'

# Update topics
curl -s -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.mercy-preview+json" \
  https://api.github.com/repos/$OWNER/$REPO/topics \
  -d '{"names": ["machine-learning", "python", "automation"]}'
```

## 6. Branch Protection

```bash
# View current protection
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/branches/main/protection

# Set up branch protection
curl -s -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/branches/main/protection \
  -d '{
    "required_status_checks": {
      "strict": true,
      "contexts": ["ci/test", "ci/lint"]
    },
    "enforce_admins": false,
    "required_pull_request_reviews": {
      "required_approving_review_count": 1
    },
    "restrictions": null
  }'
```

## 7. Secrets Management (GitHub Actions)

**With gh:**

```bash
gh secret set API_KEY --body "your-secret-value"
gh secret set SSH_KEY < ~/.ssh/id_rsa
gh secret list
gh secret delete API_KEY
```

**With curl:**

Secrets require encryption with the repo's public key — more involved via API:

```bash
# Get the repo's public key for encrypting secrets
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/secrets/public-key

# Encrypt and set (requires Python with PyNaCl)
python3 -c "
from base64 import b64encode
from nacl import encoding, public
import json, sys

# Get the public key
key_id = '<key_id_from_above>'
public_key = '<base64_key_from_above>'

# Encrypt
sealed = public.SealedBox(
    public.PublicKey(public_key.encode('utf-8'), encoding.Base64Encoder)
).encrypt('your-secret-value'.encode('utf-8'))
print(json.dumps({
    'encrypted_value': b64encode(sealed).decode('utf-8'),
    'key_id': key_id
}))"

# Then PUT the encrypted secret
curl -s -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/secrets/API_KEY \
  -d '<output from python script above>'

# List secrets (names only, values hidden)
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/secrets \
  | python3 -c "
import sys, json
for s in json.load(sys.stdin)['secrets']:
    print(f\"  {s['name']:30}  updated: {s['updated_at']}\")"
```

Note: For secrets, `gh secret set` is dramatically simpler. If setting secrets is needed and `gh` isn't available, recommend installing it for just that operation.

## 8. Releases

**With gh:**

```bash
gh release create v1.0.0 --title "v1.0.0" --generate-notes
gh release create v2.0.0-rc1 --draft --prerelease --generate-notes
gh release create v1.0.0 ./dist/binary --title "v1.0.0" --notes "Release notes"
gh release list
gh release download v1.0.0 --dir ./downloads
```

**With curl:**

```bash
# Create a release
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/releases \
  -d '{
    "tag_name": "v1.0.0",
    "name": "v1.0.0",
    "body": "## Changelog\n- Feature A\n- Bug fix B",
    "draft": false,
    "prerelease": false,
    "generate_release_notes": true
  }'

# List releases
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/releases \
  | python3 -c "
import sys, json
for r in json.load(sys.stdin):
    tag = r.get('tag_name', 'no tag')
    print(f\"  {tag:15}  {r['name']:30}  {'draft' if r['draft'] else 'published'}\")"

# Upload a release asset (binary file)
RELEASE_ID=<id_from_create_response>
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Content-Type: application/octet-stream" \
  "https://uploads.github.com/repos/$OWNER/$REPO/releases/$RELEASE_ID/assets?name=binary-amd64" \
  --data-binary @./dist/binary-amd64
```

## 9. GitHub Actions Workflows

**With gh:**

```bash
gh workflow list
gh run list --limit 10
gh run view <RUN_ID>
gh run view <RUN_ID> --log-failed
gh run rerun <RUN_ID>
gh run rerun <RUN_ID> --failed
gh workflow run ci.yml --ref main
gh workflow run deploy.yml -f environment=staging
```

**With curl:**

```bash
# List workflows
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/workflows \
  | python3 -c "
import sys, json
for w in json.load(sys.stdin)['workflows']:
    print(f\"  {w['id']:10}  {w['name']:30}  {w['state']}\")"

# List recent runs
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$OWNER/$REPO/actions/runs?per_page=10" \
  | python3 -c "
import sys, json
for r in json.load(sys.stdin)['workflow_runs']:
    print(f\"  Run {r['id']}  {r['name']:30}  {r['conclusion'] or r['status']}\")"

# Download failed run logs
RUN_ID=<run_id>
curl -s -L \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/runs/$RUN_ID/logs \
  -o /tmp/ci-logs.zip
cd /tmp && unzip -o ci-logs.zip -d ci-logs

# Re-run a failed workflow
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/runs/$RUN_ID/rerun

# Re-run only failed jobs
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/runs/$RUN_ID/rerun-failed-jobs

# Trigger a workflow manually (workflow_dispatch)
WORKFLOW_ID=<workflow_id_or_filename>
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/workflows/$WORKFLOW_ID/dispatches \
  -d '{"ref": "main", "inputs": {"environment": "staging"}}'
```

## 10. Deleting Repositories

Deleting a repo is irreversible — all code, issues, PRs, and releases are gone permanently.

**With gh:**

```bash
gh repo delete owner/repo-name --yes
```

**With curl:**

```bash
curl -s -X DELETE \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO
# 204 = success, 404 = not found, 403 = insufficient permissions
```

**Delete multiple repos in a script:**

```bash
# Extract token to temp file first (reliable)
cd /path/to/repo && git remote get-url origin | grep -oP 'ghp_[^@]+' > /tmp/ghtoken.txt
read -r GH_TOKEN < /tmp/ghtoken.txt

for repo in repo1 repo2 repo3; do
  status=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE \
    -H "Authorization: token $GH_TOKEN" \
    "https://api.github.com/repos/geniok1980/$repo")
  echo "$repo: $status"  # 204 = deleted
done
**Structurally consistent READMEs** across all public projects (title + badges, features, tech stack table, demo link, contacts).

**Rebranding / rename pattern:** When a repo has a different GitHub name than the project brand (e.g. `freqwebui-free` → FreqDash), link to the actual GitHub URL but display the brand name as the link text. See `references/profile-readme-example.md` for the current profile snapshot with examples.

### Pitfalls
- **404 vs 403:** A 404 usually means the repo doesn't exist under your account. 403 means your token lacks `delete_repo` scope — generate a new token with that scope.
- **No undo:** There is no trash/recycle bin. Once deleted, the repo name can be reused immediately by anyone.
- **Forks:** Deleting a fork does NOT notify the upstream repo. Deleting the original repo leaves all forks orphaned.
- **Private→Public is irreversible for showcase:** When the user says "создай новый открытый репозиторий [проект] и опиши там возможности бота", they mean a **NEW separate public repo** with documentation only. Do NOT change the existing private repo to public. The private repo contains real code/keys. Create a showcase repo instead (see "Public Showcase Repo for a Private Project" above) and update any landing page links to point to the new public repo.
- **Token extraction from git remote:** The subshell syntax `TOKEN=*** remote get-url origin | grep -oP 'ghp_[^@]+')` can fail depending on shell context. More reliable:
  ```bash
  cd /path/to/repo
  git remote get-url origin | grep -oP 'ghp_[^@]+' > /tmp/ghtoken.txt
  read -r TOKEN < /tmp/ghtoken.txt
  ```
- **gh repo create "Name already exists on this account":** When `gh repo create --source=. --push` runs, it creates the repo on GitHub first, then sets the remote and pushes. If the remote can't be added (e.g. existing origin from a cloned template), the repo IS created on GitHub but the local push never happens. Fix:
  ```bash
  git remote remove origin  # or update if needed
  git remote add origin https://github.com/OWNER/REPO.git
  git push -u origin main   # or master, depending on default branch
  ```
  Check default branch on GitHub first: `gh repo view OWNER/REPO --json defaultBranch` or look at the repo page.
- **Submodule sources in cloned repos:** When you `git clone` a repo that was itself cloned from another source (templates, forks), the subdirectories contain `.git/` dirs pointing to the original repos. To push as regular files:
  ```bash
  find . -name ".git" -type d -exec rm -rf {} + 2>/dev/null
  find . -name ".gitignore" -delete 2>/dev/null
  git init  # re-init as a fresh repo
  ```
  This removes all submodule connections and makes everything regular files.

---

## 11. Gists

**With gh:**

```bash
gh gist create script.py --public --desc "Useful script"
gh gist list
```

**With curl:**

```bash
# Create a gist
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/gists \
  -d '{
    "description": "Useful script",
    "public": true,
    "files": {
      "script.py": {"content": "print(\"hello\")"}
    }
  }'

# List your gists
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/gists \
  | python3 -c "
import sys, json
for g in json.load(sys.stdin):
    files = ', '.join(g['files'].keys())
    print(f\"  {g['id']}  {g['description'] or '(no desc)':40}  {files}\")"
```

## Quick Reference Table

| Action | gh | git + curl |
|--------|-----|-----------|
| Clone | `gh repo clone o/r` | `git clone https://github.com/o/r.git` |
| Create repo | `gh repo create name --public` | `curl POST /user/repos` |
| Fork | `gh repo fork o/r --clone` | `curl POST /repos/o/r/forks` + `git clone` |
| Repo info | `gh repo view o/r` | `curl GET /repos/o/r` |
| Edit settings | `gh repo edit --...` | `curl PATCH /repos/o/r` |
| Delete repo | `gh repo delete o/r --yes` | `curl DELETE /repos/o/r` |
| Create release | `gh release create v1.0` | `curl POST /repos/o/r/releases` |
| List workflows | `gh workflow list` | `curl GET /repos/o/r/actions/workflows` |
| Rerun CI | `gh run rerun ID` | `curl POST /repos/o/r/actions/runs/ID/rerun` |
| Set secret | `gh secret set KEY` | `curl PUT /repos/o/r/actions/secrets/KEY` (+ encryption) |

---

## 12. GitHub Profile README

A **special repo** named after your username (e.g. `username/username`) serves as your GitHub profile README, displayed at the top of your profile page.

### Public Repo Workflow (Create → Profile → Promote)

When creating a new public repo (rkdash, clawhost, etc.), follow this end-to-end flow:

**Step 1:** Create the repo via `gh` or `curl` (see section 2).

**Step 2:** Write a structurally consistent README with: title + badges, features, tech stack table, demo link, contacts.

**Step 3:** Set repo description and topics via API or `gh repo edit`.

**Step 4:** Add the new project to the profile README's Projects section.

**Step 5 (housekeeping):** When a repo is deleted or made private, remove it from the profile README immediately. Never let the profile show stale or private projects.

**Rebranding pattern:** When the GitHub repo name differs from the project brand (e.g. `freqwebui-free` vs FreqDash), use the brand name as link text but point to the actual GitHub URL:
```markdown
🔹 [**FreqDash**](https://github.com/username/freqwebui-free) — Description here
```

### Creating the profile repo

```bash
# With gh
gh repo create $GH_USER --public --description "🌟 Profile README" --clone

# With curl
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user/repos \
  -d '{"name": "'"$GH_USER"'", "description": "Profile README", "private": false, "auto_init": true}'

# Clone it
git clone https://github.com/$GH_USER/$GH_USER.git
cd $GH_USER
```

### Setting user profile info (bio, name, location, company)

```bash
curl -s -X PATCH \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user \
  -d '{
    "name": "Your Full Name",
    "bio": "🏪 Short bio describing what you do | 🛠️ Technologies",
    "location": "City, Country",
    "company": "Your company / tagline"
  }'
```

### Profile README design elements

**Badges (shields.io):**
```markdown
![TypeScript](https://img.shields.io/badge/-TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)
![Python](https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white)
```

**GitHub stats cards (github-readme-stats):**
```markdown
<p align="center">
  <img src="https://github-readme-stats.vercel.app/api?username=$GH_USER&show_icons=true&theme=dark&hide_border=true&count_private=true" />
  <img src="https://github-readme-stats.vercel.app/api/top-langs/?username=$GH_USER&layout=compact&theme=dark&hide_border=true" />
</p>
```

**Table layout for skills/sections:**
```markdown
| Направление | Подробнее |
|---|---|
| 🏪 **Area 1** | Details about what you do |
| 💻 **Area 2** | More details |
```

**Structure recommendations:**
1. Title / greeting
2. Short intro paragraph
3. What you do (table or list)
4. Tech stack (badges)
5. Projects (links to repos)
6. GitHub stats cards
**Structurally consistent READMEs** across all public projects (title + badges, features, tech stack table, demo link, contacts).

**Rebranding / rename pattern:** When a repo has a different GitHub name than the project brand (e.g. `freqwebui-free` → FreqDash), link to the actual GitHub URL but display the brand name as the link text. See `references/profile-readme-example.md` for the current profile snapshot with examples.

### Pitfalls

- **CDN caching:** After creating/pushing the profile README, GitHub's CDN may take **minutes to hours** to show it on the profile page. The README renders correctly in the repo view immediately, but the profile Overview page lags. This is normal — no additional config needed.
- **Repo naming:** The repo MUST be named EXACTLY after the username (case-sensitive). A different name won't render as profile README.
- **Default branch:** README must be on the default branch (usually `main`).
- **Public visibility:** The profile README repo must be public for others to see it.
- **Private projects:** Never list private repos or reference private project names in the profile README. The profile is public. If a repo was recently made private or deleted, remove it from the README. The projects section should only show what you want potential clients/employers to see.

> **Reference:** See `references/profile-readme-example.md` for a complete working profile README with badges, stats cards, and table layout.
