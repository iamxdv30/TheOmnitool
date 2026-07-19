---
name: frontend-design
description: Create distinctive, production-grade frontend interfaces with high design quality. Use this skill when the user asks to build web components, pages, artifacts, posters, or applications (examples include websites, landing pages, dashboards, React components, HTML/CSS layouts, or when styling/beautifying any web UI). Generates creative, polished code and UI design that avoids generic AI aesthetics.
author: XDEV
license: All rights reserved
---

This skill guides creation of distinctive, production-grade frontend interfaces that avoid generic "AI slop" aesthetics. Implement real working code with exceptional attention to aesthetic details, accessibility, performance, and creative choices.

The user provides frontend requirements: a component, page, application, or interface to build. They may include context about the purpose, audience, or technical constraints.

## Design Thinking

Before coding, understand the context and commit to a BOLD aesthetic direction:
- **Purpose**: What problem does this interface solve? Who uses it?
- **Tone**: Pick an extreme: brutally minimal, maximalist chaos, retro-futuristic, organic/natural, luxury/refined, playful/toy-like, editorial/magazine, brutalist/raw, art deco/geometric, soft/pastel, industrial/utilitarian, etc. There are so many flavors to choose from. Use these for inspiration but design one that is true to the aesthetic direction.
- **Audience & Context**: A developer tool demands clarity over ornamentation. A marketing page rewards spectacle. A data dashboard needs density. Let the context drive the intensity.
- **Constraints**: Technical requirements (framework, performance, accessibility, device targets).
- **Differentiation**: What makes this UNFORGETTABLE? What's the one thing someone will remember?

**CRITICAL**: Choose a clear conceptual direction and execute it with precision. Bold maximalism and refined minimalism both work — the key is intentionality, not intensity.

Then implement working code (HTML/CSS/JS, React, Vue, Svelte, etc.) that is:
- Production-grade and functional
- Visually striking and memorable
- Cohesive with a clear aesthetic point-of-view
- Meticulously refined in every detail
- Accessible and responsive by default

## Frontend Aesthetics Guidelines

### Typography
Choose fonts with intention. Pair a distinctive display font with a refined body font. Avoid defaulting to the same font across every project — variety keeps designs fresh.

- **Be intentional, not exotic for its own sake.** A system font stack is the right call for a data-heavy dashboard or dev tool. A hand-drawn script is right for a children's app. The sin is *not thinking about it*, not picking any particular font.
- Use a clear type scale (e.g., modular or custom) with consistent sizing, weight, and line-height ratios.
- Load custom fonts efficiently: `font-display: swap`, preload critical fonts, subset where possible.

### Color & Theme
Commit to a cohesive palette. Use CSS custom properties for consistency and theme switching.

- Dominant colors with sharp accents outperform timid, evenly-distributed palettes.
- **Dark/light mode**: Define a full semantic token set (`--color-surface`, `--color-text-primary`, `--color-accent`, etc.) and swap values at the root. Never hard-code colors in components.
- Ensure sufficient contrast ratios: 4.5:1 for body text, 3:1 for large text and UI elements (WCAG AA).

### Motion & Interaction
Use animations for delight and orientation, not decoration.

- Prioritize CSS-only solutions for HTML projects. Use Motion (Framer Motion) or framework equivalents when available.
- Focus on high-impact moments: one well-orchestrated page load with staggered reveals (`animation-delay`) creates more delight than scattered micro-interactions.
- Use `prefers-reduced-motion` media query to disable or simplify animations for users who need it.
- Keep animations under 300ms for interactions, up to 800ms for entrances. Use `will-change` and `transform`/`opacity` for GPU-accelerated performance.
- Scroll-triggered reveals, hover states that surprise, and meaningful transitions between states.

### Spatial Composition & Layout
Unexpected layouts create memorability. Asymmetry, overlap, diagonal flow, grid-breaking elements, generous negative space OR controlled density.

- **Responsive by default**: Design mobile-first or ensure layouts degrade gracefully. Test at 320px, 768px, 1024px, and 1440px+ mentally. Use fluid typography (`clamp()`) and container queries where appropriate.
- Use CSS Grid and Flexbox. Avoid fixed pixel widths for layout containers.
- Give content room to breathe — or pack it tight. Both work when intentional.

### Backgrounds & Visual Depth
Create atmosphere rather than defaulting to flat solid colors.

- Gradient meshes, noise textures, geometric patterns, layered transparencies, dramatic shadows, decorative borders, grain overlays — all valid tools.
- **Performance-aware**: Heavy SVG filters, blur effects, and large background images have real cost. Prefer CSS-native effects over image-based ones. Test perceived performance.

### Images, Icons & Assets
- Use SVGs for icons and illustrations (scalable, styleable, small).
- Provide meaningful `alt` text for images. Decorative images get `alt=""`.
- Use `loading="lazy"` for below-fold images.
- Prefer an icon system (Lucide, Phosphor, Heroicons, or custom SVG sprites) over one-off icon images.
- When placeholder images are needed, use services like Unsplash or generate contextual SVG illustrations — never leave broken image links or generic gray boxes.

### Content & Copy
- Use realistic, contextual placeholder content — not "Lorem ipsum" or "Click here". Real-feeling text exposes layout issues and makes prototypes more convincing.
- Microcopy matters: button labels, empty states, error messages, and tooltips should feel human and specific to the product.

## Accessibility (Non-Negotiable)

Accessibility is not an afterthought — it's a baseline for "production-grade":

- **Semantic HTML first**: Use `<nav>`, `<main>`, `<section>`, `<button>`, `<a>`, headings in order. Divs are for layout, not interaction.
- **Keyboard navigation**: Every interactive element must be reachable and operable via keyboard. Visible focus indicators that match the design (not the ugly browser default, but not invisible either).
- **ARIA only when HTML isn't enough**: Prefer native semantics. Use `aria-label`, `aria-describedby`, `role` attributes only when native HTML falls short.
- **Color is not the only signal**: Don't rely on color alone to convey meaning — pair with icons, text, or patterns.

## Component Architecture

When building reusable components (React, Vue, Svelte, Web Components, etc.):

- **Props over magic**: Components should accept clear, typed props. Avoid hidden internal state that callers can't control.
- **Composition over configuration**: Prefer slot/children patterns over mega-components with 20 boolean props. Small composable pieces beat monoliths.
- **Variants, not forks**: Use a `variant` prop (e.g., `"primary" | "outline" | "ghost"`) instead of creating separate components for visual variations.
- **Separation of concerns**: Style, behavior, and data fetching should be separable. A `<Card>` component shouldn't fetch its own data.

## Performance Awareness

Beautiful code that takes 5 seconds to load isn't production-grade:

- **Font loading**: Limit to 2-3 font files. Use `font-display: swap` and preload critical weights.
- **Animation perf**: Animate only `transform` and `opacity` where possible. Avoid animating `width`, `height`, `top`, `left`, or `box-shadow`.
- **Bundle awareness**: Avoid importing entire libraries for one utility. Tree-shake. Code-split heavy components.
- **Image optimization**: Use modern formats (WebP/AVIF), appropriate sizes, and lazy loading.

## Anti-Patterns to Avoid

NEVER use generic AI-generated aesthetics:
- Overused font families applied thoughtlessly (any font becomes cliche if it's your default for everything)
- Cliched color schemes (particularly purple-to-blue gradients on white backgrounds)
- Predictable layouts and component patterns (hero → features grid → testimonials → CTA)
- Cookie-cutter design that lacks context-specific character
- "Lorem ipsum" placeholder text in delivered work
- Inaccessible designs disguised as "creative" (invisible focus rings, contrast failures, div-button soup)

Interpret creatively and make unexpected choices that feel genuinely designed for the context. No two designs should look the same. Vary between light and dark themes, different fonts, different aesthetics. NEVER converge on the same choices across generations.

**IMPORTANT**: Match implementation complexity to the aesthetic vision. Maximalist designs need elaborate code with extensive animations and effects. Minimalist or refined designs need restraint, precision, and careful attention to spacing, typography, and subtle details. Elegance comes from executing the vision well.

Remember: Claude is capable of extraordinary creative work. Don't hold back — show what can truly be created when thinking outside the box and committing fully to a distinctive vision.
