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
