# Ocean Depths

A professional, calming maritime theme built on deep navy and teal. Conveys trust, stability, and sophistication. **Mode: Dark.**

## Colors

### Core Palette
| Token | Hex | Role |
|-------|-----|------|
| **Deep Navy** | `#0f1923` | Primary background |
| **Slate Navy** | `#1a2d42` | Elevated surfaces (cards, modals) |
| **Teal** | `#2a9d8f` | Primary accent — buttons, links, focus rings |
| **Seafoam** | `#a8dadc` | Secondary accent — highlights, badges, borders |
| **Cream** | `#f1faee` | Primary text |
| **Muted Blue** | `#7b9eb5` | Secondary text, placeholders |

### Semantic Colors
| Token | Hex | Usage |
|-------|-----|-------|
| **Success** | `#34d399` | Confirmations, positive states |
| **Warning** | `#fbbf24` | Caution states, pending |
| **Error** | `#f87171` | Errors, destructive actions |
| **Info** | `#60a5fa` | Informational, neutral highlights |

### Contrast Ratios (on Deep Navy `#0f1923`)
- Cream `#f1faee`: **15.2:1** — passes AAA
- Muted Blue `#7b9eb5`: **6.1:1** — passes AA
- Seafoam `#a8dadc`: **10.4:1** — passes AAA
- Teal `#2a9d8f`: **5.3:1** — passes AA

## Typography

**Google Fonts import:**
```
https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Source+Serif+4:wght@600;700&display=swap
```

| Role | Font | Weight |
|------|------|--------|
| **Display / Headers** | Source Serif 4 | 600–700 |
| **Body / UI** | DM Sans | 400–500–700 |

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
| `--shadow-sm` | `0 1px 2px rgba(0, 0, 0, 0.3)` |
| `--shadow-md` | `0 4px 12px rgba(0, 0, 0, 0.35)` |
| `--shadow-lg` | `0 8px 24px rgba(0, 0, 0, 0.4)` |
| `--shadow-xl` | `0 16px 48px rgba(0, 0, 0, 0.45)` |
| `--border-default` | `1px solid rgba(168, 218, 220, 0.15)` |
| `--border-strong` | `1px solid rgba(168, 218, 220, 0.3)` |

## CSS Custom Properties

```css
:root {
  /* Colors - Core */
  --color-bg: #0f1923;
  --color-surface: #1a2d42;
  --color-primary: #2a9d8f;
  --color-primary-hover: #34b8a8;
  --color-secondary: #a8dadc;
  --color-text: #f1faee;
  --color-text-muted: #7b9eb5;

  /* Colors - Semantic */
  --color-success: #34d399;
  --color-warning: #fbbf24;
  --color-error: #f87171;
  --color-info: #60a5fa;

  /* Typography */
  --font-display: 'Source Serif 4', Georgia, serif;
  --font-body: 'DM Sans', system-ui, sans-serif;
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
  --border-default: 1px solid rgba(168, 218, 220, 0.15);
  --border-strong: 1px solid rgba(168, 218, 220, 0.3);

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.35);
  --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.4);
  --shadow-xl: 0 16px 48px rgba(0, 0, 0, 0.45);
}
```

## Best For

Corporate dashboards, SaaS platforms, financial tools, data visualization, professional consulting sites, enterprise applications.
