# NeuralDeep Skills Catalog Design Reference

Extracted from https://neuraldeep.ru/skills on 2026-05-28.

## Color System

| Token | Value | Purpose |
|-------|-------|---------|
| `--accent` | `#0f8` | Primary accent (teal/green) - *use site's own accent when replicating* |
| Body bg | `#0a0a0a` | Base page background |
| Card bg | `#18181b` | Card/skill-row background |
| Card border | `#27272a` | Card border color |
| Text | `#ededed` | Primary text color |
| Text secondary | `#8888aa` | Muted/secondary text |
| Card hover bg | `#1e1e24` | Background on row hover |

## Card / Row Structure

```css
.skill-row {
  display: grid;
  grid-template-columns: 40px 2fr 1fr 80px;  /* #, Name+desc, Author, Stars */
  gap: 12px;
  padding: 14px 16px;
  border-radius: 8px;
  background: #18181b;
  border: 1px solid #27272a;
  transition: all .2s;
  align-items: center;
  cursor: pointer;
  text-decoration: none;
  position: relative;
  overflow: hidden;
}
```

### Shimmer Shine Effect

```css
.skill-row::after {
  content: "";
  pointer-events: none;
  background: linear-gradient(105deg,
    rgba(0,0,0,0) 40%,
    rgba(255,255,255,.03) 45%,
    rgba(255,255,255,.06) 50%,
    rgba(255,255,255,.03) 55%,
    rgba(0,0,0,0) 60%);
  transition: transform .6s;
  position: absolute;
  inset: 0;
  transform: translateX(-100%);
}
.skill-row:hover::after {
  transform: translateX(100%);
}
.skill-row:hover {
  background: #1e1e24;
  border-color: rgba(124,92,252,.3); /* or accent with opacity */
}
```

### Category Tag Colors

| Category | Tag class | Color |
|----------|-----------|-------|
| AI/ML/Agents | `.skill-cat-tag.ai` | `#e879f9` (purple) |
| DevOps | `.skill-cat-tag.ops` | `#3178c6` (blue) |
| Data | `.skill-cat-tag.data` | `#34d399` (green) |
| Creative | `.skill-cat-tag.creative` | `#e879f9` (purple) |
| GitHub | `.skill-cat-tag.github` | `#ffffff` (white) |
| MCP | `.skill-cat-tag.mcp` | `#fb923c` (orange) |
| RU/Regional | `.skill-cat-tag.ru` | `#f97316` (orange) |
| Dev | `.skill-cat-tag.dev` | `#22d3ee` (cyan) |

### Agent Badges (top of catalog)

```css
.agent-badge {
  font-size: 12px;
  font-weight: 600;
  padding: 6px 14px;
  border-radius: 20px;
  background: rgba(124,92,252,.12);
  color: var(--accent2);
  border: 1px solid rgba(124,92,252,.2);
  transition: all .2s;
}
```

### Filter Buttons

```css
.filter-btn {
  font-size: 12px;
  font-weight: 600;
  padding: 8px 16px;
  border-radius: 8px;
  background: #18181b;
  border: 1px solid #27272a;
  color: #8888aa;
  cursor: pointer;
  transition: all .2s;
  font-family: inherit;
}
.filter-btn:hover {
  border-color: rgba(124,92,252,.3);
  color: #e8e8f0;
}
.filter-btn.active {
  background: rgba(124,92,252,.15);
  border-color: var(--accent);
  color: var(--accent);
}
```

## Page Layout

- Container: `max-width: 1200px; margin: 0 auto; padding: 0 24px;`
- Font: `Geist, "Geist Fallback"` (on geniok.ru: `Inter`)
- Header area: logo left ("nd NeuralDeep") → nav links → GitHub login button
- Content: left sidebar (tagline, supported agents) → main content (search + filters + table)
- Table header: `#` / `Навык` / `Автор` / `★` with sort indicators

## JavaScript Filter Pattern

```javascript
// Simplified filter logic for catalog pages
function applyFilter() {
  const activeBtn = document.querySelector('.filter-btn.active');
  const search = document.getElementById('skillSearch').value.toLowerCase();
  const isAll = !activeBtn || activeBtn.textContent === 'Все';
  const catMatch = activeBtn ? activeBtn.textContent.match(/^(.+?)\s*\(/) : null;
  const catName = catMatch ? catMatch[1] : '';

  document.querySelectorAll('.skill-row').forEach(row => {
    const rowCat = row.getAttribute('data-category');
    const name = row.textContent.toLowerCase();
    const matchCat = isAll || catMap[catName] === rowCat;
    const matchSearch = !search || name.includes(search);
    row.style.display = matchCat && matchSearch ? 'grid' : 'none';
  });
}

// Attach on DOMContentLoaded
document.querySelectorAll('.filter-btn').forEach(btn => {
  btn.addEventListener('click', function() {
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    this.classList.add('active');
    applyFilter();
  });
});
document.getElementById('skillSearch').addEventListener('input', applyFilter);
```

## Key Differences When Replicating for a Personal Site

| NeuralDeep | geniok.ru replica |
|------------|-------------------|
| Accent `#0f8` (green) | Used site's `#7c5cfc` (purple) |
| Font Geist | Font Inter |
| Sidebar + main layout | Single column full-width |
| Has login/auth | No auth, static catalog |
| Links to GitHub repos for install | Links to geniok1980/skills repository |
