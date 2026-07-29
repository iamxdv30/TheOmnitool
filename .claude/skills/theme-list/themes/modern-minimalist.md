# Modern Minimalist

A clean, sharp theme built on refined neutrals. Maximum clarity, zero noise. Lets content and data speak. **Mode: Light.**

## Colors

### Core Palette
| Token | Hex | Role |
|-------|-----|------|
| **White** | `#ffffff` | Primary background |
| **Cool Gray 50** | `#f7f8fa` | Elevated surfaces (cards, modals) |
| **Graphite** | `#18181b` | Primary accent — buttons, key UI |
| **Steel** | `#52525b` | Secondary accent — icons, active states |
| **Near Black** | `#09090b` | Primary text |
| **Zinc** | `#71717a` | Secondary text, placeholders |

### Semantic Colors
| Token | Hex | Usage |
|-------|-----|-------|
| **Success** | `#16a34a` | Confirmations, positive states |
| **Warning** | `#ca8a04` | Caution states, pending |
| **Error** | `#dc2626` | Errors, destructive actions |
| **Info** | `#2563eb` | Informational, neutral highlights |

### Contrast Ratios (on White `#ffffff`)
- Near Black `#09090b`: **19.6:1** — passes AAA
- Zinc `#71717a`: **4.7:1** — passes AA
- Graphite `#18181b`: **17.2:1** — passes AAA
- Steel `#52525b`: **7.1:1** — passes AAA

## Typography

**Google Fonts import:**
```
https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&family=Geist+Mono:wght@400;500&display=swap
```

| Role | Font | Weight |
|------|------|--------|
| **Display / Headers** | Geist | 600–700 |
| **Body / UI** | Geist | 400–500 |
| **Monospace** | Geist Mono | 400–500 |

### Type Scale
| Token | Size | Line Height | Usage |
|-------|------|-------------|-------|
| `--text-h1` | 2.25rem (36px) | 1.2 | Page titles |
| `--text-h2` | 1.875rem (30px) | 1.25 | Section headers |
| `--text-h3` | 1.5rem (24px) | 1.3 | Card titles |
| `--text-h4` | 1.25rem (20px) | 1.35 | Subsections |
| `--text-h5` | 1.125rem (18px) | 1.4 | Labels |
| `--text-h6` | 1rem (16px) | 1.4 | Small headings |
| `--text-body` | 0.9375rem (15px) | 1.6 | Body text |
| `--text-small` | 0.8125rem (13px) | 1.5 | Secondary text |
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
| `--radius-md` | 0.375rem (6px) |
| `--radius-lg` | 0.5rem (8px) |
| `--radius-xl` | 0.75rem (12px) |
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
| `--shadow-sm` | `0 1px 2px rgba(0, 0, 0, 0.04)` |
| `--shadow-md` | `0 2px 8px rgba(0, 0, 0, 0.06)` |
| `--shadow-lg` | `0 4px 16px rgba(0, 0, 0, 0.08)` |
| `--shadow-xl` | `0 8px 32px rgba(0, 0, 0, 0.1)` |
| `--border-default` | `1px solid #e4e4e7` |
| `--border-strong` | `1px solid #a1a1aa` |

## CSS Custom Properties

```css
:root {
  /* Colors - Core */
  --color-bg: #ffffff;
  --color-surface: #f7f8fa;
  --color-primary: #18181b;
  --color-primary-hover: #27272a;
  --color-secondary: #52525b;
  --color-text: #09090b;
  --color-text-muted: #71717a;

  /* Colors - Semantic */
  --color-success: #16a34a;
  --color-warning: #ca8a04;
  --color-error: #dc2626;
  --color-info: #2563eb;

  /* Typography */
  --font-display: 'Geist', system-ui, sans-serif;
  --font-body: 'Geist', system-ui, sans-serif;
  --font-mono: 'Geist Mono', ui-monospace, monospace;
  --text-h1: 2.25rem;
  --text-h2: 1.875rem;
  --text-h3: 1.5rem;
  --text-h4: 1.25rem;
  --text-h5: 1.125rem;
  --text-h6: 1rem;
  --text-body: 0.9375rem;
  --text-small: 0.8125rem;
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
  --radius-md: 0.375rem;
  --radius-lg: 0.5rem;
  --radius-xl: 0.75rem;
  --radius-full: 9999px;
  --border-default: 1px solid #e4e4e7;
  --border-strong: 1px solid #a1a1aa;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.04);
  --shadow-md: 0 2px 8px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 4px 16px rgba(0, 0, 0, 0.08);
  --shadow-xl: 0 8px 32px rgba(0, 0, 0, 0.1);
}
```

## Best For

Developer tools, admin panels, data dashboards, SaaS apps, documentation sites, productivity tools, API platforms.
