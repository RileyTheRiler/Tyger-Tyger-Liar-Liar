# Palette's Journal

This journal tracks critical UX/accessibility learnings.

## 2024-05-22 - Accessibility of Custom Visualizations
**Learning:** Custom UI components like gauges or charts often lack semantic meaning for screen readers, relying entirely on visual interpretation.
**Action:** Always wrap custom visualizations with `role="progressbar"` or similar ARIA roles, and provide `aria-valuenow`, `aria-valuemin`, `aria-valuemax`, and `aria-label` to ensure the data is accessible non-visually.
