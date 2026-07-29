# Tech Innovation

A bold, electric theme with high-energy contrast. Cutting-edge, futuristic, and unapologetically digital. **Mode: Dark.**

## Colors

### Core Palette
| Token | Hex | Role |
|-------|-----|------|
| **Void** | `#0a0a0f` | Primary background |
| **Dark Surface** | `#161620` | Elevated surfaces (cards, modals) |
| **Electric Blue** | `#3b82f6` | Primary accent — buttons, links, focus rings |
| **Cyan** | `#22d3ee` | Secondary accent — highlights, badges, glow effects |
| **White** | `#f0f0f5` | Primary text |
| **Cool Gray** | `#8b8fa3` | Secondary text, placeholders |

### Semantic Colors
| Token | Hex | Usage |
|-------|-----|-------|
| **Success** | `#22c55e` | Confirmations, positive states |
| **Warning** | `#eab308` | Caution states, pending |
| **Error** | `#ef4444` | Errors, destructive actions |
| **Info** | `#3b82f6` | Informational, neutral highlights |

### Contrast Ratios (on Void `#0a0a0f`)
- White `#f0f0f5`: **17.8:1** — passes AAA
- Cool Gray `#8b8fa3`: **6.4:1** — passes AA
- Electric Blue `#3b82f6`: **5.2:1** — passes AA
- Cyan `#22d3ee`: **10.8:1** — passes AAA

## Typography

**Google Fonts import:**
```
https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap
```

| Role | Font | Weight |
|------|------|--------|
| **Display / Headers** | Sora | 600–700 |
| **Body / UI** | Sora | 400–500 |
| **Monospace** | JetBrains Mono | 400–500 |

### Type Scale
| Token | Size | Line Height | Usage |
|-------|------|-------------|-------|
| `--text-h1` | 2.5rem (40px) | 1.15 | Page titles |
| `--text-h2` | 2rem (32px) | 1.2 | Section headers |
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
| `--shadow-sm` | `0 1px 2px rgba(0, 0, 0, 0.4)` |
| `--shadow-md` | `0 4px 12px rgba(0, 0, 0, 0.5)` |
| `--shadow-lg` | `0 8px 24px rgba(0, 0, 0, 0.5)` |
| `--shadow-xl` | `0 16px 48px rgba(0, 0, 0, 0.6)` |
| `--shadow-glow` | `0 0 20px rgba(59, 130, 246, 0.3)` |
| `--border-default` | `1px solid rgba(59, 130, 246, 0.15)` |
| `--border-strong` | `1px solid rgba(59, 130, 246, 0.35)` |

## CSS Custom Properties

```css
:root {
  /* Colors - Core */
  --color-bg: #0a0a0f;
  --color-surface: #161620;
  --color-primary: #3b82f6;
  --color-primary-hover: #2563eb;
  --color-secondary: #22d3ee;
  --color-text: #f0f0f5;
  --color-text-muted: #8b8fa3;

  /* Colors - Semantic */
  --color-success: #22c55e;
  --color-warning: #eab308;
  --color-error: #ef4444;
  --color-info: #3b82f6;

  /* Typography */
  --font-display: 'Sora', system-ui, sans-serif;
  --font-body: 'Sora', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', ui-monospace, monospace;
  --text-h1: 2.5rem;
  --text-h2: 2rem;
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
  --radius-sm: 0.375rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 1rem;
  --radius-full: 9999px;
  --border-default: 1px solid rgba(59, 130, 246, 0.15);
  --border-strong: 1px solid rgba(59, 130, 246, 0.35);

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.4);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.5);
  --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.5);
  --shadow-xl: 0 16px 48px rgba(0, 0, 0, 0.6);
  --shadow-glow: 0 0 20px rgba(59, 130, 246, 0.3);
}
```

## Best For

Tech startup sites, AI/ML platforms, developer tools, gaming dashboards, crypto/web3 apps, digital product launches, hackathon projects.
