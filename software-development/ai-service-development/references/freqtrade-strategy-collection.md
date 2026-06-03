# Freqtrade Strategy Collection Workflow

How to search, clone, and bundle top Freqtrade strategies from GitHub into a single collection repo.

## Sources (ordered by stars)

| Repo | Stars | Why include |
|------|-------|-------------|
| `freqtrade/freqtrade-strategies` | 5,206 | Official strategies repo |
| `iterativv/NostalgiaForInfinity` | 3,259 | Most popular single strategy (42 files) |
| `Rikj000/MoniGoMani` | 1,025 | ML framework (reference only, not just strategies) |
| `ssssi/freqtrade_strs` | 649 | ClucHAnix + custom strategies (22 files) |
| `nateemma/strategies` | 425 | NN/ML strategies — biggest collection (381 files) |
| `paulcpk/freqtrade-strategies-that-work` | 326 | "Strategies that work" — 5 proven |
| `PeetCrypto/freqtrade-stuff` | 325 | Crowdsourced collection (429 files) |
| `werkkrew/freqtrade-strategies` | 299 | Curated + archived strategies (122 files) |

## Clone command

```bash
cd ~/ai-agent-services && mkdir -p freqtrade-strategies && cd freqtrade-strategies
git clone --depth 1 https://github.com/paulcpk/freqtrade-strategies-that-work.git strategies-that-work
git clone --depth 1 https://github.com/iterativv/NostalgiaForInfinity.git nostalgia-for-infinity
git clone --depth 1 https://github.com/freqtrade/freqtrade-strategies.git official-strategies
git clone --depth 1 https://github.com/PeetCrypto/freqtrade-stuff.git peet-crypto
git clone --depth 1 https://github.com/ssssi/freqtrade_strs.git ssssi-strategies
git clone --depth 1 https://github.com/nateemma/strategies.git nateemma-strategies
git clone --depth 1 https://github.com/werkkrew/freqtrade-strategies.git werkkrew-strategies
```

## Push to own GitHub

```bash
cd ~/ai-agent-services/freqtrade-strategies
# Remove .git dirs from submodules so files become regular files
find . -name ".git" -type d -exec rm -rf {} + 2>/dev/null
git init
git add -A
git commit -m "Initial: collection of top Freqtrade strategies"
gh repo create geniok1980/freqtrade-strategies --public --source=. --remote=origin --push
```

If `gh repo create` fails with "Name already exists on this account", the repo was created on GitHub but the push didn't happen. Fix:
```bash
git remote add origin https://github.com/geniok1980/freqtrade-strategies.git
git branch -m master main   # if needed
git push -u origin main --force
```

> Note: GitHub may normalize the repo name to `Freqtrade-Strategies` (capital S). Adjust remote URL accordingly.
