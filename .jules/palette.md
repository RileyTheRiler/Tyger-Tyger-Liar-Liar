## PALETTE'S JOURNAL
This journal records CRITICAL UX/accessibility learnings.

Format: `## YYYY-MM-DD - [Title]
**Learning:** [UX/a11y insight]
**Action:** [How to apply next time]`

## 2024-05-22 - Custom Gauge Accessibility
**Learning:** Custom visual meters (like analog gauges) are invisible to screen readers without explicit semantics. They require `role="progressbar"` (or `meter`) along with `aria-valuenow`, `aria-valuemin`, and `aria-valuemax` to convey their state.
**Action:** Always wrap custom data visualizations in a container with appropriate ARIA roles and labels.
