---
name: theme-factory
description: Design token library for frontend development. Provides 10 curated themes with complete color palettes, typography, spacing, and component tokens. Use alongside the frontend-design skill — when building any frontend interface, offer theme selection to establish the visual foundation before writing code. Can also generate custom themes on-the-fly.
author: XDEV
license: All rights reserved
---

# Theme Factory

A curated library of design token systems for frontend development. Each theme provides a complete visual foundation — colors, typography, spacing, shadows, and component defaults — ready to be applied when building interfaces with the frontend-design skill.

## Purpose

When the frontend-design skill is active and you're building a UI from scratch, use this skill to establish the visual foundation before writing code. Each theme includes:

- Complete color system with semantic roles (primary, surface, text, states)
- Typography scale with carefully paired web fonts
- Spacing and sizing scales
- Border, shadow, and radius tokens
- CSS custom property format — ready to drop into any framework
- WCAG AA contrast compliance documented per theme
- Dark or light mode designation

## Workflow

When building a frontend interface:

1. **Offer theme selection**: Present the 10 available themes with their one-line descriptions. Mention the option to generate a custom theme.
2. **Wait for selection**: Get explicit confirmation of the chosen theme.
3. **Load the theme**: Read the selected theme file from `themes/` directory.
4. **Apply tokens to code**: Use the theme's CSS custom properties, font imports, and token values throughout the implementation. Every color, font-size, spacing value, and shadow should reference the theme tokens.
5. **Adapt to context**: The theme provides the foundation — the frontend-design skill provides the creativity. Themes set the palette; layout, composition, and interaction design remain creative decisions.

## Available Themes

| # | Theme | Mode | Vibe | Best For |
|---|-------|------|------|----------|
| 1 | **Ocean Depths** | Dark | Professional, calming | Corporate, finance, SaaS dashboards |
| 2 | **Sunset Boulevard** | Light | Warm, energetic | Creative agencies, marketing, portfolios |
| 3 | **Forest Canopy** | Light | Natural, grounded | Sustainability, wellness, organic brands |
| 4 | **Modern Minimalist** | Light | Clean, sharp | Dev tools, data apps, admin panels |
| 5 | **Golden Hour** | Light | Warm, inviting | Hospitality, food, lifestyle, e-commerce |
| 6 | **Arctic Frost** | Light | Cool, precise | Healthcare, fintech, enterprise SaaS |
| 7 | **Desert Rose** | Light | Soft, elegant | Fashion, beauty, wedding, boutique |
| 8 | **Tech Innovation** | Dark | Bold, electric | Startups, AI/ML, developer tools, gaming |
| 9 | **Botanical Garden** | Light | Fresh, vibrant | Food & drink, garden, natural products |
| 10 | **Midnight Galaxy** | Dark | Dramatic, cosmic | Entertainment, gaming, creative agencies |

## Theme File Structure

Each theme in `themes/` follows this structure:

```
# Theme Name
One-line description. Mode: dark|light.

## Colors
Core palette (4-6 colors) with hex codes and roles.
Semantic colors: success, warning, error, info.
Surface/background hierarchy.
Text colors with contrast ratios.

## Typography
Google Fonts import URL.
Display + body font pairing.
Type scale: h1–h6, body, small, caption with sizes and line-heights.

## Spacing & Layout
Spacing scale (4px base).
Border-radius tokens.
Container max-widths.

## Elevation & Depth
Shadow scale (sm, md, lg, xl).
Border colors.

## CSS Custom Properties
Complete :root {} block ready to paste.
```

## Custom Theme Generation

When no preset fits, generate a custom theme:

1. Ask for: mood/vibe keywords, target audience, dark or light preference, any brand colors.
2. Generate a theme following the exact structure of the preset themes.
3. Include all sections: colors, typography (pick from Google Fonts), spacing, shadows, and the full CSS custom properties block.
4. Verify contrast ratios meet WCAG AA (4.5:1 body text, 3:1 large text/UI).
5. Present for review before applying.

## Integration with frontend-design

This skill provides the **what** (tokens, values, palette). The frontend-design skill provides the **how** (layout, composition, animation, creativity). Together:

- Theme Factory sets: colors, fonts, spacing, shadows, radii
- Frontend Design decides: layout, motion, spatial composition, component architecture, interactivity

Never let the theme constrain creativity — it's a palette, not a cage.
