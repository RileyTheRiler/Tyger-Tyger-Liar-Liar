## 2024-05-22 - Accessibility in Status HUD
**Learning:** Analog gauges are visually appealing but completely inaccessible to screen readers.
**Action:** Use `role="progressbar"` with `aria-valuenow`, `aria-valuemin`, and `aria-valuemax` to make them announceable. Adding a "hidden" digital readout or using `aria-label` is crucial for context.

## 2024-05-22 - Input Console Labels
**Learning:** Terminal-style inputs often omit labels for immersion, which fails WCAG criteria.
**Action:** Use `aria-label` to provide context without breaking the visual aesthetic. Dynamic labels (e.g., "System busy") provide excellent feedback for non-sighted users.
