# The Omnitool Design System

This document records the design system implemented by the Next.js frontend. It is descriptive, not aspirational: every value below comes from the current CSS, installed Tailwind theme, font setup, shared UI components, or repeated page layouts.

## Source of truth

- `frontend/src/app/globals.css` defines the application color tokens, theme switching, base typography, glass surfaces, glows, focus treatment, selection, and scrollbar styling.
- `frontend/src/app/layout.tsx` loads the fonts and applies the default dark theme before hydration.
- `frontend/src/components/ui/` defines the shared buttons, inputs, cards, badges, labels, alerts, and search fields.
- `frontend/node_modules/tailwindcss/theme.css` supplies Tailwind v4's spacing, type, radius, shadow, container, and breakpoint values.
- Layout conventions are evidenced in `frontend/src/app/` and `frontend/src/components/layout/`.
- There is no `tailwind.config.js` in the repository. Tailwind v4 is imported from CSS with `@import "tailwindcss"`, and application tokens are registered through `@theme inline` in `globals.css`.
- `surface-600` is referenced by a few feature-level controls but is not defined in `globals.css`; it is therefore not part of the source-of-truth palette and should not be used for new UI unless a token is explicitly added.

## 1. Visual Theme & Atmosphere

The interface uses a **Sage Tech** visual language: botanical sage greens and mint are paired with deep teal accents, green-tinted surfaces, restrained glow effects, translucent glass panels, and an optional 3D ambient background. The result is calm and organic while retaining a technical, high-performance character.

The product supports light and dark themes, with **dark as the initial theme** when no persisted preference exists. Both themes preserve semantic token names, so component roles remain stable while their values change.

Core atmospheric treatments:

- **Base canvas:** `surface-900`; content panels use `surface-800`; dividers and borders use `surface-700`.
- **Glass:** 50% `surface-800`, `12px` backdrop blur, and a 20% primary border.
- **Strong glass:** 70% `surface-800`, `16px` backdrop blur, and a 30% primary border.
- **Primary glow:** `0 0 20px` at 30% `primary-glow`, plus `0 0 40px` at 20% `primary`.
- **Secondary glow:** `0 0 20px` at 30% `secondary`, plus `0 0 40px` at 10% `secondary`.
- **Motion:** theme colors transition over `300ms`; shared controls and cards transition over `200ms`; pressable filled/outline buttons scale to `0.98` while active.
- **Accessibility:** focus-visible uses a `2px` `primary-glow` outline with a `2px` offset. Shared controls use a two-pixel ring, two-pixel offset, and `surface-900` ring-offset color. Reduced-motion preferences collapse animations and transitions to `0.01ms` and one iteration.
- **Selection:** 40% primary over transparency with high-emphasis text.
- **Scrollbar:** `8px` wide/high; `surface-900` track; `surface-700` thumb with `4px` radius; primary thumb on hover.

## 2. Color Palette & Roles

Use semantic tokens rather than embedding theme-specific values in components.

### Semantic theme colors

| Role / token | Light theme | Dark theme | Intended use |
|---|---:|---:|---|
| `primary` | `#4A6E49` | `#588157` | Primary actions, active states, branded emphasis |
| `primary-hover` | `#385237` | `#4A6E49` | Primary action hover |
| `primary-glow` | `#588157` | `#A3B18A` | High-emphasis branding, focus, glow CTA |
| `secondary` | `#58A67B` | `#9CDFB9` | Secondary actions and mint emphasis |
| `secondary-hover` | `#418C63` | `#7BCFA0` | Secondary action hover |
| `accent` | `#456268` | `#577A81` | Deep-teal supporting accent and search icon |
| `accent-hover` | `#2F4448` | `#456268` | Accent hover treatment |
| `surface-900` | `#F5F7F5` | `#080B09` | App/page background and dark-on-color text |
| `surface-800` | `#FFFFFF` | `#1D2E1C` | Cards, fields, raised surfaces |
| `surface-700` | `#E0E8E0` | `#2A3F29` | Borders, dividers, muted fills |
| `success` | `#2D8A5E` | `#9CDFB9` | Success borders, rings, badges, alerts |
| `warning` | `#B08D25` | `#E9C46A` | Warning badges, alerts, locked status |
| `danger` | `#A8383B` | `#815758` | Destructive actions, errors, required marks |
| `info` | `#3C6E79` | `#577A81` | Informational badges and alerts |
| `text-high` | `#1A1D1A` | `#EDF2ED` | Primary text and high-contrast icons |
| `text-muted` | `#588157` | `#88A687` | Supporting text, placeholders, inactive navigation |

### Fixed colors and deliberate exceptions

These values are hard-coded in current components and do not switch by theme:

- White: `#FFFFFF` — hero search background (`bg-white`).
- Black: `#000000` — elevated-card shadow base at 20% opacity.
- Glow-button hover: `#8FA67A`.
- Danger-button hover: `#6A4748`.
- Hero search glow:
  - Resting: `rgba(163, 177, 138, 0.35)` at `25px`, plus `rgba(88, 129, 87, 0.2)` at `50px`.
  - Focused: `rgba(163, 177, 138, 0.5)` at `30px`, plus `rgba(88, 129, 87, 0.3)` at `60px`.
- 3D scene lights/shapes use `#A3B18A`, `#577A81`, `#9CDFB9`, and `#588157`.

### Opacity conventions

- Hover tint: primary at 10%.
- Interactive border hover: primary at 50%.
- Interactive shadow: primary at 10%.
- Status badge background: semantic status at 10%; border at 30%.
- Status alert background: semantic status at 10%; full-color semantic border/text.
- Disabled controls: 50% opacity.
- Elevated-card shadow: black at 20%.

## 3. Typography Rules

### Font families

| Role | Family | Fallback | Usage |
|---|---|---|---|
| Display | Space Grotesk | `system-ui, sans-serif` | All `h1`–`h6`, card titles, brand marks, buttons, prominent metrics |
| Body | Inter | `system-ui, sans-serif` | Body copy, inputs, labels, navigation, descriptions |
| Monospace | `ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace` | `monospace` | Timestamps, internal names, compact metadata |

Space Grotesk and Inter are loaded from `next/font/google`, Latin subset, with `display: "swap"`. Body text is antialiased.

### Implemented type scale

The frontend uses Tailwind v4's installed scale plus one compact custom size:

| Utility | Font size | Line height | Current role examples |
|---|---:|---:|---|
| `text-[10px]` | `10px` | normal/inherited | Compact uppercase usage labels |
| `text-xs` | `0.75rem` / `12px` | `1rem` / `16px` | Badges, metadata, helper text |
| `text-sm` | `0.875rem` / `14px` | `1.25rem` / `20px` | Labels, descriptions, table headings |
| `text-base` | `1rem` / `16px` | `1.5rem` / `24px` | Default body and medium controls |
| `text-lg` | `1.125rem` / `18px` | `1.75rem` / `28px` | Large controls and lead copy |
| `text-xl` | `1.25rem` / `20px` | `1.75rem` / `28px` | Card titles and section titles |
| `text-2xl` | `1.5rem` / `24px` | `2rem` / `32px` | Metrics and secondary page headings |
| `text-3xl` | `1.875rem` / `30px` | `2.25rem` / `36px` | Standard page title |
| `text-4xl` | `2.25rem` / `36px` | `2.5rem` / `40px` | Marketing/dashboard hero title |
| `text-5xl` | `3rem` / `48px` | `1` | Responsive dashboard/about hero |
| `text-6xl` | `3.75rem` / `60px` | `1` | Medium-screen home hero |
| `text-7xl` | `4.5rem` / `72px` | `1` | Large-screen home hero |

### Weight, tracking, and leading

- Regular: `400`.
- Medium: `500` — controls, labels, navigation, badges.
- Semibold: `600` — card titles and compact labels.
- Bold: `700` — page titles, major headings, brand.
- Tight tracking: `-0.025em`; used with card and alert titles.
- Wider tracking: `0.05em`; widest: `0.1em`; used on uppercase metadata.
- Tight leading: `1.25`; relaxed leading: `1.625`; explicit `leading-none` is used for compact titles.

Typography hierarchy should follow the implemented patterns:

- Marketing hero: display, bold, `36px` mobile → `60px` at `48rem` → `72px` at `64rem`.
- Dashboard/about hero: display, bold, `36px` mobile → `48px` at `40rem`.
- Tool/admin page title: display, bold, `30px`.
- Section/card title: display, semibold/bold, `20px`.
- Body: Inter, regular, `16px`.
- Supporting copy: Inter, regular, `14px`, `text-muted`.

## 4. Component Stylings

### Buttons

Shared base:

- Inline flex, centered, `8px` gap.
- Space Grotesk, weight `500`.
- `200ms` transition.
- Focus: two-pixel `primary-glow` ring, two-pixel offset on `surface-900`.
- Disabled: no pointer events and 50% opacity.

Sizes:

| Size | Height | Horizontal padding | Type | Radius |
|---|---:|---:|---:|---:|
| Small | `32px` | `12px` | `14px` | `6px` |
| Medium (default) | `40px` | `16px` | `16px` | `8px` |
| Large | `48px` | `24px` | `18px` | `8px` |
| Icon | `40px × 40px` | — | — | `8px` |

Variants:

- **Primary:** primary fill, high-emphasis text, primary-hover fill on hover, `0.98` active scale.
- **Glow:** primary-glow fill, surface-900 text, `#8FA67A` hover, primary glow shadow, `0.98` active scale.
- **Outline:** one-pixel primary border, transparent fill, primary text, 10% primary hover fill, `0.98` active scale.
- **Ghost:** transparent fill, muted text; surface-800 fill and high-emphasis text on hover.
- **Secondary:** secondary fill, surface-900 text, secondary-hover fill, `0.98` active scale.
- **Danger:** danger fill, high-emphasis text, `#6A4748` hover, `0.98` active scale.

### Inputs and textareas

Shared treatment:

- Full width, surface-800 fill, high-emphasis text, muted placeholder.
- One-pixel border and `200ms` transition.
- Default border is surface-700; hover border is primary at 50%.
- Focus: no native outline; two-pixel semantic ring and two-pixel surface-900 offset.
- Error: danger border/ring. Success: success border/ring.
- Disabled: not-allowed cursor and 50% opacity.

Input sizes match button heights:

| Size | Height | Horizontal padding | Type | Radius |
|---|---:|---:|---:|---:|
| Small | `32px` | `12px` | `14px` | `6px` |
| Medium (default) | `40px` | `16px` | `16px` | `8px` |
| Large | `48px` | `16px` | `18px` | `8px` |

Textarea sizes:

| Size | Minimum height | Padding | Type | Radius |
|---|---:|---:|---:|---:|
| Small | `80px` | `8px` | `14px` | `6px` |
| Medium (default) | `120px` | `12px` | `16px` | `8px` |
| Large | `160px` | `16px` | `18px` | `8px` |

Textareas do not resize. Labels are `14px`, weight `500`, high-emphasis text; required marks use danger.

Search fields add leading search and trailing clear icons. The default search is `44px` high with an `8px` radius. The hero search is `56px` high with a `16px` radius, white fill, 30% primary border, `18px` text, and the fixed sage glow documented above.

### Cards

Shared base: `12px` radius and `200ms` transition.

Padding variants:

- None: `0`.
- Small: `12px`.
- Medium (default): `16px`.
- Large: `24px`.
- Extra large: `32px`.

Surface variants:

- **Default:** surface-800 fill and one-pixel surface-700 border.
- **Glass:** 50% surface-800, `12px` backdrop blur, one-pixel 20% primary border.
- **Glass strong:** 70% surface-800, `16px` backdrop blur, one-pixel 30% primary border.
- **Elevated:** default surface/border plus Tailwind large shadow (`0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)`) tinted with black at 20%.
- **Interactive:** default surface/border; pointer cursor; 50% primary border and primary-at-10% large shadow on hover.

Card anatomy:

- Header: vertical stack, `6px` internal spacing, `16px` bottom padding.
- Title: Space Grotesk, `20px`, weight `600`, line-height `1`, tight tracking, high-emphasis text.
- Description: `14px`, muted text.
- Footer: horizontal alignment with `16px` top padding.

### Badges and alerts

- **Badge:** inline-flex pill, `4px` gap, full radius, one-pixel border, `10px` horizontal and `2px` vertical padding, `12px` text, weight `500`.
- **Default badge:** surface-800 fill, surface-700 border, muted text.
- **Semantic badge:** 10% semantic fill, 30% semantic border, full semantic text.
- **Alert:** full width, `8px` radius, one-pixel border, `16px` padding, `12px` gap, top-aligned icon/content.
- **Semantic alert:** 10% semantic fill with full semantic border and text. Error maps to danger.

### Borders, radii, shadows, and icons

- Standard border width: `1px`.
- Standard control radius: `8px`.
- Small control radius: `6px`.
- Card radius: `12px`; prominent dashboard cards may override to `16px`.
- Pill radius: full.
- Common icon sizes: `16px`, `20px`, and `24px`.
- Avoid arbitrary shadows except the documented glow treatments; cards use Tailwind's `shadow-lg` definition.

## 5. Layout Principles

### Spacing scale

Tailwind v4's installed spacing unit is `0.25rem` (`4px`). Numeric spacing utilities multiply this unit. The recurring application scale is:

| Step | Value | Common use |
|---:|---:|---|
| `0.5` | `2px` | Badge vertical padding |
| `1` | `4px` | Badge/icon gaps, compact offsets |
| `1.5` | `6px` | Compact gaps, card-header spacing |
| `2` | `8px` | Control gaps, small padding |
| `2.5` | `10px` | Badge horizontal padding |
| `3` | `12px` | Small card/input padding |
| `4` | `16px` | Default card/page-mobile padding and grid gap |
| `5` | `20px` | Hero search icon inset |
| `6` | `24px` | Large card padding and standard wide grid gap |
| `8` | `32px` | XL card/desktop content padding and larger gaps |
| `12` | `48px` | Large vertical empty-state spacing |
| `16` | `64px` | Fixed header height/top content offset and large section rhythm |
| `24` | `96px` | Marketing section vertical padding |

Use the 4px base scale. Fractional steps already present (`0.5`, `1.5`, `2.5`) are valid for compact UI; arbitrary values should remain exceptional.

### Breakpoints

| Prefix | Minimum width |
|---|---:|
| `sm` | `40rem` / `640px` |
| `md` | `48rem` / `768px` |
| `lg` | `64rem` / `1024px` |
| `xl` | `80rem` / `1280px` |
| `2xl` | `96rem` / `1536px` |

The interface is mobile-first. Add columns and wider padding at the breakpoints rather than maintaining desktop structure on small screens.

### Grid system

Implemented responsive patterns:

- Tool grid: 1 column by default, 2 at `sm`, 3 at `lg`; `16px` gaps.
- Email-template grid: 1 column by default, 2 at `sm`, 3 at `lg`, 4 at `xl`; `16px` gaps.
- Marketing features: 1 column by default, 3 at `md`; `24px` gaps.
- Two-panel content: 1 column by default, 2 at `md` or `lg`; usually `32px` gaps.
- Form fields: 1 column by default, 2 or 3 at `sm`; `16px` gaps.
- Footer: 2 columns by default, 4 at `md`; `32px` gaps.

### Containers and content widths

- Public marketing sections use Tailwind's responsive `container`, centered with `16px` horizontal padding.
- General content pages use centered maximum widths with responsive gutters: `16px` mobile, `24px` at `sm`, and `32px` at `lg` where implemented.
- Auth content is constrained to `max-w-md` (`28rem` / `448px`) and centered both horizontally and vertically with `16px` outer padding.
- Common reading/content widths:
  - `max-w-xl`: `36rem` / `576px`.
  - `max-w-2xl`: `42rem` / `672px`.
  - `max-w-4xl`: `56rem` / `896px`.
- The global header is fixed at `64px`; root main content receives `64px` top padding.
- Dashboard content uses `16px` padding on mobile and `32px` from `md`. Its sidebar offset is `80px` collapsed or `256px` expanded from `md` upward.
- Admin content uses a fixed `256px` left offset and `32px` padding.

### Composition rules

- Keep the page canvas on `surface-900`; group related information on surface-800, glass, or strong-glass cards.
- Center marketing and auth experiences; use sidebar-offset content for operational dashboard/admin views.
- Use `16px` gaps for dense component grids, `24px` for standard feature/tool layouts, and `32px` for major two-panel separation.
- Preserve a clear hierarchy: page title and lead copy, then controls/filters, then responsive content grids.
- Use responsive stacking for action groups (`flex-col` → `sm:flex-row`) and for multi-field forms.
- Keep high-emphasis glow effects selective: primary calls to action, hero search, and ambient decoration rather than every interactive element.
