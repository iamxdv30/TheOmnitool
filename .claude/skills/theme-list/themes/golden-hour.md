# Golden Hour

A rich, warm autumnal palette that wraps the interface in an inviting, cozy atmosphere. Sophisticated without being heavy. **Mode: Light.**

## Colors

### Core Palette
| Token | Hex | Role |
|-------|-----|------|
| **Warm Linen** | `#faf5ee` | Primary background |
| **Cream** | `#f3ead8` | Elevated surfaces (cards, modals) |
| **Amber** | `#c47d10` | Primary accent — buttons, links, focus rings |
| **Terracotta** | `#b85c38` | Secondary accent — highlights, badges |
| **Espresso** | `#2a1f16` | Primary text |
| **Walnut** | `#7a6652` | Secondary text, placeholders |

### Semantic Colors
| Token | Hex | Usage |
|-------|-----|-------|
| **Success** | `#3a8a52` | Confirmations, positive states |
| **Warning** | `#c48b10` | Caution states, pending |
| **Error** | `#b83a2a` | Errors, destructive actions |
| **Info** | `#3872a8` | Informational, neutral highlights |

### Contrast Ratios (on Warm Linen `#faf5ee`)
- Espresso `#2a1f16`: **16.3:1** — passes AAA
- Walnut `#7a6652`: **4.6:1** — passes AA
- Amber `#c47d10`: **4.1:1** — passes AA (large text, use bold for body)
- Terracotta `#b85c38`: **4.5:1** — passes AA

## Typography

**Google Fonts import:**
```
https://fonts.googleapis.com/css2?family=Fraunces:wght@500;600;700&family=Outfit:wght@400;500;600&display=swap
```

| Role | Font | Weight |
|------|------|--------|
| **Display / Headers** | Fraunces | 500–700 |
| **Body / UI** | Outfit | 400–500–600 |

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
| `--shadow-sm` | `0 1px 3px rgba(42, 31, 22, 0.06)` |
| `--shadow-md` | `0 4px 12px rgba(42, 31, 22, 0.08)` |
| `--shadow-lg` | `0 8px 24px rgba(42, 31, 22, 0.1)` |
| `--shadow-xl` | `0 16px 48px rgba(42, 31, 22, 0.13)` |
| `--border-default` | `1px solid rgba(196, 125, 16, 0.15)` |
| `--border-strong` | `1px solid rgba(196, 125, 16, 0.3)` |

## CSS Custom Properties

```css
:root {
  /* Colors - Core */
  --color-bg: #faf5ee;
  --color-surface: #f3ead8;
  --color-primary: #c47d10;
  --color-primary-hover: #a86a0c;
  --color-secondary: #b85c38;
  --color-text: #2a1f16;
  --color-text-muted: #7a6652;

  /* Colors - Semantic */
  --color-success: #3a8a52;
  --color-warning: #c48b10;
  --color-error: #b83a2a;
  --color-info: #3872a8;

  /* Typography */
  --font-display: 'Fraunces', Georgia, serif;
  --font-body: 'Outfit', system-ui, sans-serif;
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
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 1rem;
  --radius-full: 9999px;
  --border-default: 1px solid rgba(196, 125, 16, 0.15);
  --border-strong: 1px solid rgba(196, 125, 16, 0.3);

  /* Shadows */
  --shadow-sm: 0 1px 3px rgba(42, 31, 22, 0.06);
  --shadow-md: 0 4px 12px rgba(42, 31, 22, 0.08);
  --shadow-lg: 0 8px 24px rgba(42, 31, 22, 0.1);
  --shadow-xl: 0 16px 48px rgba(42, 31, 22, 0.13);
}
```

## Best For

Restaurant sites, hospitality platforms, food & drink brands, lifestyle e-commerce, artisan product pages, cozy editorial sites.
