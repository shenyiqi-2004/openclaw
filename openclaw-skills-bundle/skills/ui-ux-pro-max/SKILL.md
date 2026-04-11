# UI/UX Pro Max — Design Intelligence

Comprehensive design intelligence skill for web/mobile UI decisions, powered by searchable databases of 67+ UI styles, 161 color palettes, 57 font pairings, 99 UX guidelines, and 25 chart types.

## When to Use

**Invoked automatically** when the task involves:
- Building landing pages, dashboards, SaaS products, e-commerce, mobile apps
- Choosing or justifying color palettes, typography, spacing, layout systems
- Creating or reviewing UI components (buttons, modals, forms, cards, tables, charts)
- Accessibility audits, WCAG compliance checks
- Design system creation or extension
- UI/UX feedback, quality control, or professional polish pass

## Quick Search

```bash
# Design system generator (start here for new projects)
python3 skills/ui-ux-pro-max/scripts/search.py "<product type> <industry> <keywords>" --design-system -p "Project Name"

# Domain-specific search
python3 skills/ui-ux-pro-max/scripts/search.py "<keyword>" --domain <domain> -n 3

# Stack-specific guidelines
python3 skills/ui-ux-pro-max/scripts/search.py "<keyword>" --stack <stack>
```

**Domains:** `style` | `color` | `typography` | `landing` | `chart` | `ux` | `product` | `icons` | `react` | `web` | `google-fonts`
**Stacks:** `react` | `nextjs` | `vue` | `svelte` | `astro` | `swiftui` | `react-native` | `flutter` | `shadcn` | `html-tailwind` | `laravel`

## Priority Rule Summary

| Priority | Category | Impact |
|----------|----------|--------|
| 1 | Accessibility | CRITICAL — 4.5:1 contrast, alt text, keyboard nav, ARIA |
| 2 | Touch & Interaction | CRITICAL — 44×44pt min touch target, loading feedback |
| 3 | Performance | HIGH — WebP/AVIF, lazy loading, CLS < 0.1 |
| 4 | Style Selection | HIGH — Match style to product type, SVG icons (no emoji) |
| 5 | Layout & Responsive | HIGH — Mobile-first, no horizontal scroll, 8dp spacing |
| 6 | Typography & Color | MEDIUM — 16px base, semantic color tokens |
| 7 | Animation | MEDIUM — 150-300ms, ease-in-out, prefers-reduced-motion |
| 8 | Forms & Feedback | MEDIUM — Labels, inline errors, progressive disclosure |
| 9 | Navigation Patterns | HIGH — ≤5 bottom nav items, predictable back behavior |
| 10 | Charts & Data | LOW — Legends, tooltips, accessible colors |

## Pre-Delivery Checklist

- [ ] No emoji as icons — use SVG (Phosphor / Heroicons)
- [ ] Touch targets ≥44×44pt
- [ ] Color contrast ≥4.5:1 (AA) in both light and dark mode
- [ ] Animation duration 150-300ms, respects reduced-motion
- [ ] Form errors near fields, not just at top
- [ ] Safe areas respected (notch, Dynamic Island, gesture bar)
- [ ] Skeleton/shimmer for async content >300ms
