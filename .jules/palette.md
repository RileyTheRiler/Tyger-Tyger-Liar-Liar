## 2024-05-23 - StatusHUD Accessibility Pattern
**Learning:** Analog gauges are visually rich but inaccessible by default. Translating them to `role="progressbar"` with `aria-valuenow` provides a clear semantic equivalent. Also, aliasing `motion` to `Motion` (PascalCase) satisfies the `no-unused-vars` linter rule while keeping the component used.
**Action:** When creating custom visual meters, always wrap them in a container with `role="progressbar"` and hide the visual parts with `aria-hidden="true"` to reduce noise for screen readers. Alias framer-motion imports to PascalCase.
## PALETTE'S JOURNAL
This journal records CRITICAL UX/accessibility learnings.

Format: `## YYYY-MM-DD - [Title]
**Learning:** [UX/a11y insight]
**Action:** [How to apply next time]`

## 2024-05-22 - Custom Gauge Accessibility
**Learning:** Custom visual meters (like analog gauges) are invisible to screen readers without explicit semantics. They require `role="progressbar"` (or `meter`) along with `aria-valuenow`, `aria-valuemin`, and `aria-valuemax` to convey their state.
**Action:** Always wrap custom data visualizations in a container with appropriate ARIA roles and labels.
## 2024-05-22 - Accessibility in Status HUD
**Learning:** Analog gauges are visually appealing but completely inaccessible to screen readers.
**Action:** Use `role="progressbar"` with `aria-valuenow`, `aria-valuemin`, and `aria-valuemax` to make them announceable. Adding a "hidden" digital readout or using `aria-label` is crucial for context.

## 2024-05-22 - Input Console Labels
**Learning:** Terminal-style inputs often omit labels for immersion, which fails WCAG criteria.
**Action:** Use `aria-label` to provide context without breaking the visual aesthetic. Dynamic labels (e.g., "System busy") provide excellent feedback for non-sighted users.
