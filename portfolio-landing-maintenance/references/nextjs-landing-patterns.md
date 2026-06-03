# Next.js Landing Page Patterns (Tailwind CSS v4)

Used for the rkdash.geniok.ru landing page (Next.js 16, Tailwind CSS v4, shadcn/ui).

## Architecture

- Landing page is a client component (`'use client'`) at `src/app/page.tsx`
- Navigation links use `href="#section-id"` for smooth same-page scrolling
- It lives alongside the dashboard at `/dashboard/*` - no auth required
- Metadata set in root `layout.tsx`

## Structure

A marketing landing page typically has these sections:

1. **Nav** — fixed top, logo + links + CTA button, mobile hamburger
2. **Hero** — full-screen, headline, subtitle, CTA buttons, stat counters
3. **Features** — grid of cards (icon + title + short description)
4. **AI Demo** — split: text explaining AI + mock chat UI showing interaction
5. **How it works** — numbered steps with description
6. **Integrations** — partner logos/cards with feature tags
7. **Pricing** — side-by-side tariff cards with feature lists and example calculation
8. **CTA** — final call to action
9. **Footer** — logo + links + copyright

## Dark Theme CSS Patterns (Tailwind v4)

```tsx
// Page wrapper
<div className="min-h-screen bg-[#0a0a0f] text-white">

// Card pattern
<div className="rounded-xl border border-white/5 bg-white/5 p-6 
                transition-all hover:border-white/10 hover:bg-white/[0.07]">

// Gradient accent text
<span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 
               bg-clip-text text-transparent">

// Glow backgrounds (pointer-events-none, absolute)
<div className="absolute left-1/2 top-1/4 h-[600px] w-[600px] -translate-x-1/2 
                -translate-y-1/2 rounded-full bg-indigo-500/10 blur-[120px]" />

// Feature tag pills
<span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 
               text-xs text-zinc-300">

// CTA button (white on dark)
className="inline-flex h-12 items-center justify-center rounded-xl 
           bg-white px-8 text-sm font-medium text-black 
           transition-all hover:bg-zinc-200"

// Secondary CTA (outlined)
className="inline-flex h-12 items-center justify-center rounded-xl 
           border border-white/10 bg-white/5 px-8 text-sm font-medium 
           text-zinc-300 transition-all hover:bg-white/10"
```

## Pricing Section

Two-column grid with tariff cards. The "popular" card gets:
- Gradient border (`border-indigo-500/30`) 
- Badge at top-right corner (`absolute -top-3 right-6 rounded-full bg-gradient-to-r from-indigo-500 to-purple-600`)
- Gradient CTA button (`bg-gradient-to-r from-indigo-500 to-purple-600`)
- Example calculation block for multi-tier pricing

## AI Chat Mock

A mockup showing user ↔ AI interaction:
- User messages: indigo avatar, rounded message box with light background
- AI messages: purple avatar, purple-tinted message box
- Code/list formatting inside AI responses
- Recommendation line with 💡 emoji
- Action confirmation with ✅ emoji
- Last message fades out (`opacity-60`) to hint at scrollability

## Mobile Navigation

- Hamburger button visible only on `md:hidden`
- Dropdown menu below nav with all links + CTA
- State managed with `useState` (no external library needed)
- Smooth open/close toggle (MenuIcon ↔ XIcon SVG swap)

## Tailwind v4 Notes

- Uses `@import 'tailwindcss'` syntax (no tailwind.config.js)
- Color palette via CSS custom properties in themes
- Custom colors use `bg-[#hex]` syntax or CSS variables
- No `@apply` directive for component styles (inline classes preferred)
- Responsive: `sm:` (640px), `md:` (768px), `lg:` (1024px) breakpoints
