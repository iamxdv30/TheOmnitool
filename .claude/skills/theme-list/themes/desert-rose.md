# Desert Rose

A soft, elegant theme with dusty muted tones. Refined femininity without being saccharine. Sophisticated restraint. **Mode: Light.**

## Colors

### Core Palette
| Token | Hex | Role |
|-------|-----|------|
| **Blush White** | `#faf7f5` | Primary background |
| **Rose Tint** | `#f2ebe6` | Elevated surfaces (cards, modals) |
| **Deep Rose** | `#a15c6a` | Primary accent — buttons, links, focus rings |
| **Dusty Clay** | `#c49080` | Secondary accent — highlights, badges |
| **Dark Burgundy** | `#2d1a22` | Primary text |
| **Mauve Gray** | `#7a6670` | Secondary text, placeholders |

### Semantic Colors
| Token | Hex | Usage |
|-------|-----|-------|
| **Success** | `#4a8a60` | Confirmations, positive states |
| **Warning** | `#c4960c` | Caution states, pending |
| **Error** | `#b5382a` | Errors, destructive actions |
| **Info** | `#5272a8` | Informational, neutral highlights |

### Contrast Ratios (on Blush White `#faf7f5`)
- Dark Burgundy `#2d1a22`: **15.6:1** — passes AAA
- Mauve Gray `#7a6670`: **4.6:1** — passes AA
- Deep Rose `#a15c6a`: **4.5:1** — passes AA
- Dusty Clay `#c49080`: **3.2:1** — passes AA (large text only)

## Typography

**Google Fonts import:**
```
https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Jost:wght@400;500;600&display=swap
```

| Role | Font | Weight |
|------|------|--------|
| **Display / Headers** | Cormorant Garamond | 500–700 |
| **Body / UI** | Jost | 400–500–600 |

### Type Scale
| Token | Size | Line Height | Usage |
|-------|------|-------------|-------|
| `--text-h1` | 2.75rem (44px) | 1.15 | Page titles |
| `--text-h2` | 2.125rem (34px) | 1.2 | Section headers |
| `--text-h3` | 1.5rem (24px) | 1.3 | Card titles |
| `--text-h4` | 1.25rem (20px) | 1.35 | Subsections |
| `--text-h5` | 1.125rem (18px) | 1.4 | Labels |
| `--text-h6` | 1rem (16px) | 1.4 | Small headings |
| `--text-body` | 1rem (16px) | 1.7 | Body text |
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
| `--shadow-sm` | `0 1px 3px rgba(45, 26, 34, 0.05)` |
| `--shadow-md` | `0 4px 12px rgba(45, 26, 34, 0.07)` |
| `--shadow-lg` | `0 8px 24px rgba(45, 26, 34, 0.09)` |
| `--shadow-xl` | `0 16px 48px rgba(45, 26, 34, 0.12)` |
| `--border-default` | `1px solid rgba(161, 92, 106, 0.12)` |
| `--border-strong` | `1px solid rgba(161, 92, 106, 0.25)` |

## CSS Custom Properties

```css
:root {
  /* Colors - Core */
  --color-bg: #faf7f5;
  --color-surface: #f2ebe6;
  --color-primary: #a15c6a;
  --color-primary-hover: #8a4d5a;
  --color-secondary: #c49080;
  --color-text: #2d1a22;
  --color-text-muted: #7a6670;

  /* Colors - Semantic */
  --color-success: #4a8a60;
  --color-warning: #c4960c;
  --color-error: #b5382a;
  --color-info: #5272a8;

  /* Typography */
  --font-display: 'Cormorant Garamond', Georgia, serif;
  --font-body: 'Jost', system-ui, sans-serif;
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
  --radius-sm: 0.375rem;
  --radius-md: 0.5rem;
  --radius-lg: 1rem;
  --radius-xl: 1.5rem;
  --radius-full: 9999px;
  --border-default: 1px solid rgba(161, 92, 106, 0.12);
  --border-strong: 1px solid rgba(161, 92, 106, 0.25);

  /* Shadows */
  --shadow-sm: 0 1px 3px rgba(45, 26, 34, 0.05);
  --shadow-md: 0 4px 12px rgba(45, 26, 34, 0.07);
  --shadow-lg: 0 8px 24px rgba(45, 26, 34, 0.09);
  --shadow-xl: 0 16px 48px rgba(45, 26, 34, 0.12);
}
```

## Best For

Fashion e-commerce, beauty brands, wedding planners, boutique shops, interior design studios, luxury real estate, skincare sites.
