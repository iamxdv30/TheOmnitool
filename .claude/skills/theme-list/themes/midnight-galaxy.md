# Midnight Galaxy

A dramatic, cosmic theme with deep purples and ethereal highlights. Mysterious, immersive, and unforgettable. **Mode: Dark.**

## Colors

### Core Palette
| Token | Hex | Role |
|-------|-----|------|
| **Deep Space** | `#0d0a18` | Primary background |
| **Nebula** | `#1a1530` | Elevated surfaces (cards, modals) |
| **Violet** | `#8b5cf6` | Primary accent — buttons, links, focus rings |
| **Lavender** | `#c4b5fd` | Secondary accent — highlights, badges |
| **Star White** | `#ede9fe` | Primary text |
| **Mist** | `#9590b0` | Secondary text, placeholders |

### Semantic Colors
| Token | Hex | Usage |
|-------|-----|-------|
| **Success** | `#34d399` | Confirmations, positive states |
| **Warning** | `#fbbf24` | Caution states, pending |
| **Error** | `#fb7185` | Errors, destructive actions |
| **Info** | `#818cf8` | Informational, neutral highlights |

### Contrast Ratios (on Deep Space `#0d0a18`)
- Star White `#ede9fe`: **16.1:1** — passes AAA
- Mist `#9590b0`: **6.6:1** — passes AA
- Lavender `#c4b5fd`: **10.4:1** — passes AAA
- Violet `#8b5cf6`: **5.1:1** — passes AA

## Typography

**Google Fonts import:**
```
https://fonts.googleapis.com/css2?family=Clash+Display:wght@500;600;700&family=Satoshi:wght@400;500;700&display=swap
```

| Role | Font | Weight |
|------|------|--------|
| **Display / Headers** | Clash Display | 500–700 |
| **Body / UI** | Satoshi | 400–500–700 |

> **Note:** Clash Display and Satoshi are available via [Fontshare](https://www.fontshare.com/) (free for personal and commercial use). Alternatively, substitute with Google Fonts: `Space Grotesk` (display) + `General Sans` or `DM Sans` (body).

### Type Scale
| Token | Size | Line Height | Usage |
|-------|------|-------------|-------|
| `--text-h1` | 2.75rem (44px) | 1.1 | Page titles |
| `--text-h2` | 2.125rem (34px) | 1.2 | Section headers |
| `--text-h3` | 1.5rem (24px) | 1.3 | Card titles |
| `--text-h4` | 1.25rem (20px) | 1.35 | Subsections |
| `--text-h5` | 1.125rem (18px) | 1.4 | Labels |
| `--text-h6` | 1rem (16px) | 1.4 | Small headings |
| `--text-body` | 1rem (16px) | 1.6 | Body text |
| `--text-small` | 0.875rem (14px) | 1.5 | Secondary text |
| `--text-caption` | 0.75rem (12px) | 1.4 | Captions, metadata |

## Spacing & Layout

**Base unit:** 4px

| Token | Value |
|-------|-------|
| `--space-1` | 0.25rem (4px) |
| `--space-2` | 0.5rem (8px) |
| `--space-3` | 0.75rem (12px) |
| `--space-4` | 1rem (16px) |
| `--space-6` | 1.5rem (24px) |
| `--space-8` | 2rem (32px) |
| `--space-12` | 3rem (48px) |
| `--space-16` | 4rem (64px) |
| `--space-24` | 6rem (96px) |

| Token | Value |
|-------|-------|
| `--radius-sm` | 0.5rem (8px) |
| `--radius-md` | 0.75rem (12px) |
| `--radius-lg` | 1rem (16px) |
| `--radius-xl` | 1.5rem (24px) |
| `--radius-full` | 9999px |

| Token | Value |
|-------|-------|
| `--container-sm` | 640px |
| `--container-md` | 768px |
| `--container-lg` | 1024px |
| `--container-xl` | 1280px |

## Elevation & Depth

| Token | Value |
|-------|-------|
| `--shadow-sm` | `0 1px 2px rgba(0, 0, 0, 0.4)` |
| `--shadow-md` | `0 4px 12px rgba(0, 0, 0, 0.45)` |
| `--shadow-lg` | `0 8px 24px rgba(0, 0, 0, 0.5)` |
| `--shadow-xl` | `0 16px 48px rgba(0, 0, 0, 0.55)` |
| `--shadow-glow` | `0 0 24px rgba(139, 92, 246, 0.25)` |
| `--border-default` | `1px solid rgba(139, 92, 246, 0.15)` |
| `--border-strong` | `1px solid rgba(139, 92, 246, 0.3)` |

## CSS Custom Properties

```css
:root {
  /* Colors - Core */
  --color-bg: #0d0a18;
  --color-surface: #1a1530;
  --color-primary: #8b5cf6;
  --color-primary-hover: #7c3aed;
  --color-secondary: #c4b5fd;
  --color-text: #ede9fe;
  --color-text-muted: #9590b0;

  /* Colors - Semantic */
  --color-success: #34d399;
  --color-warning: #fbbf24;
  --color-error: #fb7185;
  --color-info: #818cf8;

  /* Typography */
  --font-display: 'Clash Display', system-ui, sans-serif;
  --font-body: 'Satoshi', system-ui, sans-serif;
  --text-h1: 2.75rem;
  --text-h2: 2.125rem;
  --text-h3: 1.5rem;
  --text-h4: 1.25rem;
  --text-h5: 1.125rem;
  --text-h6: 1rem;
  --text-body: 1rem;
  --text-small: 0.875rem;
  --text-caption: 0.75rem;

  /* Spacing */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  --space-12: 3rem;
  --space-16: 4rem;
  --space-24: 6rem;

  /* Borders & Radius */
  --radius-sm: 0.5rem;
  --radius-md: 0.75rem;
  --radius-lg: 1rem;
  --radius-xl: 1.5rem;
  --radius-full: 9999px;
  --border-default: 1px solid rgba(139, 92, 246, 0.15);
  --border-strong: 1px solid rgba(139, 92, 246, 0.3);

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.4);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.45);
  --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.5);
  --shadow-xl: 0 16px 48px rgba(0, 0, 0, 0.55);
  --shadow-glow: 0 0 24px rgba(139, 92, 246, 0.25);
}
```

## Best For

Entertainment platforms, gaming sites, creative agency portfolios, music apps, nightlife venues, immersive experiences, metaverse projects.
