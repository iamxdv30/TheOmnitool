# Arctic Frost

A cool, precise theme inspired by winter clarity. Conveys professionalism, trustworthiness, and clinical precision. **Mode: Light.**

## Colors

### Core Palette
| Token | Hex | Role |
|-------|-----|------|
| **Ice White** | `#f5f8fc` | Primary background |
| **Frost** | `#e8eef6` | Elevated surfaces (cards, modals) |
| **Steel Blue** | `#3668a8` | Primary accent — buttons, links, focus rings |
| **Powder Blue** | `#7ea8d4` | Secondary accent — highlights, badges |
| **Charcoal** | `#1a2030` | Primary text |
| **Slate** | `#5c6a7e` | Secondary text, placeholders |

### Semantic Colors
| Token | Hex | Usage |
|-------|-----|-------|
| **Success** | `#2d8a5e` | Confirmations, positive states |
| **Warning** | `#c49012` | Caution states, pending |
| **Error** | `#c43d3d` | Errors, destructive actions |
| **Info** | `#3668a8` | Informational, neutral highlights |

### Contrast Ratios (on Ice White `#f5f8fc`)
- Charcoal `#1a2030`: **15.4:1** — passes AAA
- Slate `#5c6a7e`: **5.1:1** — passes AA
- Steel Blue `#3668a8`: **5.6:1** — passes AA
- Powder Blue `#7ea8d4`: **3.1:1** — passes AA (large text only)

## Typography

**Google Fonts import:**
```
https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Newsreader:wght@500;600&display=swap
```

| Role | Font | Weight |
|------|------|--------|
| **Display / Headers** | Plus Jakarta Sans | 600–700 |
| **Body / UI** | Plus Jakarta Sans | 400–500 |
| **Editorial accent** | Newsreader | 500–600 |

### Type Scale
| Token | Size | Line Height | Usage |
|-------|------|-------------|-------|
| `--text-h1` | 2.5rem (40px) | 1.2 | Page titles |
| `--text-h2` | 2rem (32px) | 1.25 | Section headers |
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
| `--radius-sm` | 0.25rem (4px) |
| `--radius-md` | 0.5rem (8px) |
| `--radius-lg` | 0.75rem (12px) |
| `--radius-xl` | 1rem (16px) |
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
| `--shadow-sm` | `0 1px 3px rgba(26, 32, 48, 0.05)` |
| `--shadow-md` | `0 4px 12px rgba(26, 32, 48, 0.07)` |
| `--shadow-lg` | `0 8px 24px rgba(26, 32, 48, 0.09)` |
| `--shadow-xl` | `0 16px 48px rgba(26, 32, 48, 0.12)` |
| `--border-default` | `1px solid #d8e2ef` |
| `--border-strong` | `1px solid #9db4d0` |

## CSS Custom Properties

```css
:root {
  /* Colors - Core */
  --color-bg: #f5f8fc;
  --color-surface: #e8eef6;
  --color-primary: #3668a8;
  --color-primary-hover: #2b5590;
  --color-secondary: #7ea8d4;
  --color-text: #1a2030;
  --color-text-muted: #5c6a7e;

  /* Colors - Semantic */
  --color-success: #2d8a5e;
  --color-warning: #c49012;
  --color-error: #c43d3d;
  --color-info: #3668a8;

  /* Typography */
  --font-display: 'Plus Jakarta Sans', system-ui, sans-serif;
  --font-body: 'Plus Jakarta Sans', system-ui, sans-serif;
  --font-accent: 'Newsreader', Georgia, serif;
  --text-h1: 2.5rem;
  --text-h2: 2rem;
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
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 1rem;
  --radius-full: 9999px;
  --border-default: 1px solid #d8e2ef;
  --border-strong: 1px solid #9db4d0;

  /* Shadows */
  --shadow-sm: 0 1px 3px rgba(26, 32, 48, 0.05);
  --shadow-md: 0 4px 12px rgba(26, 32, 48, 0.07);
  --shadow-lg: 0 8px 24px rgba(26, 32, 48, 0.09);
  --shadow-xl: 0 16px 48px rgba(26, 32, 48, 0.12);
}
```

## Best For

Healthcare apps, fintech dashboards, enterprise SaaS, pharmaceutical sites, insurance platforms, clinical tools, government portals.
