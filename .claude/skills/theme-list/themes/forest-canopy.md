# Forest Canopy

A natural, grounded theme built on deep greens and warm earth tones. Evokes trust, growth, and environmental consciousness. **Mode: Light.**

## Colors

### Core Palette
| Token | Hex | Role |
|-------|-----|------|
| **Warm Ivory** | `#f8f6f0` | Primary background |
| **Parchment** | `#efeade` | Elevated surfaces (cards, modals) |
| **Forest Green** | `#2d5a27` | Primary accent — buttons, links, focus rings |
| **Sage** | `#7d9471` | Secondary accent — highlights, badges |
| **Dark Earth** | `#1c1a17` | Primary text |
| **Olive Gray** | `#6b6a5e` | Secondary text, placeholders |

### Semantic Colors
| Token | Hex | Usage |
|-------|-----|-------|
| **Success** | `#2e8b57` | Confirmations, positive states |
| **Warning** | `#c4960c` | Caution states, pending |
| **Error** | `#b5382a` | Errors, destructive actions |
| **Info** | `#3a7bb8` | Informational, neutral highlights |

### Contrast Ratios (on Warm Ivory `#f8f6f0`)
- Dark Earth `#1c1a17`: **17.1:1** — passes AAA
- Olive Gray `#6b6a5e`: **4.8:1** — passes AA
- Forest Green `#2d5a27`: **7.2:1** — passes AAA
- Sage `#7d9471`: **3.4:1** — passes AA (large text)

## Typography

**Google Fonts import:**
```
https://fonts.googleapis.com/css2?family=Lora:wght@500;600;700&family=Work+Sans:wght@400;500;600&display=swap
```

| Role | Font | Weight |
|------|------|--------|
| **Display / Headers** | Lora | 500–700 |
| **Body / UI** | Work Sans | 400–500–600 |

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
| `--shadow-sm` | `0 1px 3px rgba(28, 26, 23, 0.06)` |
| `--shadow-md` | `0 4px 12px rgba(28, 26, 23, 0.08)` |
| `--shadow-lg` | `0 8px 24px rgba(28, 26, 23, 0.1)` |
| `--shadow-xl` | `0 16px 48px rgba(28, 26, 23, 0.12)` |
| `--border-default` | `1px solid rgba(45, 90, 39, 0.12)` |
| `--border-strong` | `1px solid rgba(45, 90, 39, 0.25)` |

## CSS Custom Properties

```css
:root {
  /* Colors - Core */
  --color-bg: #f8f6f0;
  --color-surface: #efeade;
  --color-primary: #2d5a27;
  --color-primary-hover: #234a1e;
  --color-secondary: #7d9471;
  --color-text: #1c1a17;
  --color-text-muted: #6b6a5e;

  /* Colors - Semantic */
  --color-success: #2e8b57;
  --color-warning: #c4960c;
  --color-error: #b5382a;
  --color-info: #3a7bb8;

  /* Typography */
  --font-display: 'Lora', Georgia, serif;
  --font-body: 'Work Sans', system-ui, sans-serif;
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
  --border-default: 1px solid rgba(45, 90, 39, 0.12);
  --border-strong: 1px solid rgba(45, 90, 39, 0.25);

  /* Shadows */
  --shadow-sm: 0 1px 3px rgba(28, 26, 23, 0.06);
  --shadow-md: 0 4px 12px rgba(28, 26, 23, 0.08);
  --shadow-lg: 0 8px 24px rgba(28, 26, 23, 0.1);
  --shadow-xl: 0 16px 48px rgba(28, 26, 23, 0.12);
}
```

## Best For

Sustainability platforms, wellness apps, organic product sites, environmental orgs, outdoor brands, farm-to-table, nature-focused content.
