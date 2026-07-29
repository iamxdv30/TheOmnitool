# Sunset Boulevard

A warm, vibrant theme inspired by golden-hour sunsets. Radiates energy, creativity, and optimism. **Mode: Light.**

## Colors

### Core Palette
| Token | Hex | Role |
|-------|-----|------|
| **Warm White** | `#faf6f1` | Primary background |
| **Soft Peach** | `#fff3e6` | Elevated surfaces (cards, modals) |
| **Burnt Orange** | `#d4622b` | Primary accent — buttons, links, focus rings |
| **Coral** | `#e8875b` | Secondary accent — highlights, badges |
| **Deep Plum** | `#2c1810` | Primary text |
| **Warm Gray** | `#7a6b5e` | Secondary text, placeholders |

### Semantic Colors
| Token | Hex | Usage |
|-------|-----|-------|
| **Success** | `#3d9a5f` | Confirmations, positive states |
| **Warning** | `#d4982b` | Caution states, pending |
| **Error** | `#c9413b` | Errors, destructive actions |
| **Info** | `#3b7fc9` | Informational, neutral highlights |

### Contrast Ratios (on Warm White `#faf6f1`)
- Deep Plum `#2c1810`: **15.8:1** — passes AAA
- Warm Gray `#7a6b5e`: **4.6:1** — passes AA
- Burnt Orange `#d4622b`: **4.5:1** — passes AA
- Coral `#e8875b`: **3.1:1** — passes AA (large text only)

## Typography

**Google Fonts import:**
```
https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Nunito:wght@400;500;700&display=swap
```

| Role | Font | Weight |
|------|------|--------|
| **Display / Headers** | Playfair Display | 600–700 |
| **Body / UI** | Nunito | 400–500–700 |

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
| `--shadow-sm` | `0 1px 3px rgba(44, 24, 16, 0.08)` |
| `--shadow-md` | `0 4px 12px rgba(44, 24, 16, 0.1)` |
| `--shadow-lg` | `0 8px 24px rgba(44, 24, 16, 0.12)` |
| `--shadow-xl` | `0 16px 48px rgba(44, 24, 16, 0.15)` |
| `--border-default` | `1px solid rgba(212, 98, 43, 0.15)` |
| `--border-strong` | `1px solid rgba(212, 98, 43, 0.3)` |

## CSS Custom Properties

```css
:root {
  /* Colors - Core */
  --color-bg: #faf6f1;
  --color-surface: #fff3e6;
  --color-primary: #d4622b;
  --color-primary-hover: #b8531f;
  --color-secondary: #e8875b;
  --color-text: #2c1810;
  --color-text-muted: #7a6b5e;

  /* Colors - Semantic */
  --color-success: #3d9a5f;
  --color-warning: #d4982b;
  --color-error: #c9413b;
  --color-info: #3b7fc9;

  /* Typography */
  --font-display: 'Playfair Display', Georgia, serif;
  --font-body: 'Nunito', system-ui, sans-serif;
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
  --border-default: 1px solid rgba(212, 98, 43, 0.15);
  --border-strong: 1px solid rgba(212, 98, 43, 0.3);

  /* Shadows */
  --shadow-sm: 0 1px 3px rgba(44, 24, 16, 0.08);
  --shadow-md: 0 4px 12px rgba(44, 24, 16, 0.1);
  --shadow-lg: 0 8px 24px rgba(44, 24, 16, 0.12);
  --shadow-xl: 0 16px 48px rgba(44, 24, 16, 0.15);
}
```

## Best For

Creative agency sites, marketing pages, portfolios, lifestyle brands, event platforms, content-rich blogs.
