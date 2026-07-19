# Botanical Garden

A fresh, vibrant theme bursting with garden-inspired life. Energetic yet natural, playful yet grounded. **Mode: Light.**

## Colors

### Core Palette
| Token | Hex | Role |
|-------|-----|------|
| **Soft Cream** | `#faf9f3` | Primary background |
| **Warm Sand** | `#f0eddf` | Elevated surfaces (cards, modals) |
| **Fern Green** | `#3a7d52` | Primary accent — buttons, links, focus rings |
| **Marigold** | `#d4920b` | Secondary accent — highlights, badges, CTAs |
| **Rich Earth** | `#1e1a14` | Primary text |
| **Warm Stone** | `#6d6456` | Secondary text, placeholders |

### Semantic Colors
| Token | Hex | Usage |
|-------|-----|-------|
| **Success** | `#2d8a4e` | Confirmations, positive states |
| **Warning** | `#d4920b` | Caution states, pending |
| **Error** | `#c43830` | Errors, destructive actions |
| **Info** | `#3874a8` | Informational, neutral highlights |

### Contrast Ratios (on Soft Cream `#faf9f3`)
- Rich Earth `#1e1a14`: **17.0:1** — passes AAA
- Warm Stone `#6d6456`: **4.9:1** — passes AA
- Fern Green `#3a7d52`: **5.0:1** — passes AA
- Marigold `#d4920b`: **3.8:1** — passes AA (large text, bold body)

## Typography

**Google Fonts import:**
```
https://fonts.googleapis.com/css2?family=Bitter:wght@500;600;700&family=Karla:wght@400;500;600&display=swap
```

| Role | Font | Weight |
|------|------|--------|
| **Display / Headers** | Bitter | 500–700 |
| **Body / UI** | Karla | 400–500–600 |

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
| `--radius-sm` | 0.375rem (6px) |
| `--radius-md` | 0.625rem (10px) |
| `--radius-lg` | 1rem (16px) |
| `--radius-xl` | 1.25rem (20px) |
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
| `--shadow-sm` | `0 1px 3px rgba(30, 26, 20, 0.06)` |
| `--shadow-md` | `0 4px 12px rgba(30, 26, 20, 0.08)` |
| `--shadow-lg` | `0 8px 24px rgba(30, 26, 20, 0.1)` |
| `--shadow-xl` | `0 16px 48px rgba(30, 26, 20, 0.13)` |
| `--border-default` | `1px solid rgba(58, 125, 82, 0.12)` |
| `--border-strong` | `1px solid rgba(58, 125, 82, 0.25)` |

## CSS Custom Properties

```css
:root {
  /* Colors - Core */
  --color-bg: #faf9f3;
  --color-surface: #f0eddf;
  --color-primary: #3a7d52;
  --color-primary-hover: #2e6542;
  --color-secondary: #d4920b;
  --color-text: #1e1a14;
  --color-text-muted: #6d6456;

  /* Colors - Semantic */
  --color-success: #2d8a4e;
  --color-warning: #d4920b;
  --color-error: #c43830;
  --color-info: #3874a8;

  /* Typography */
  --font-display: 'Bitter', Georgia, serif;
  --font-body: 'Karla', system-ui, sans-serif;
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
  --radius-sm: 0.375rem;
  --radius-md: 0.625rem;
  --radius-lg: 1rem;
  --radius-xl: 1.25rem;
  --radius-full: 9999px;
  --border-default: 1px solid rgba(58, 125, 82, 0.12);
  --border-strong: 1px solid rgba(58, 125, 82, 0.25);

  /* Shadows */
  --shadow-sm: 0 1px 3px rgba(30, 26, 20, 0.06);
  --shadow-md: 0 4px 12px rgba(30, 26, 20, 0.08);
  --shadow-lg: 0 8px 24px rgba(30, 26, 20, 0.1);
  --shadow-xl: 0 16px 48px rgba(30, 26, 20, 0.13);
}
```

## Best For

Food & drink sites, garden centers, recipe apps, farm-to-table restaurants, natural product stores, plant shops, cooking blogs.
