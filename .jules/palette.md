## 2024-10-24 - Accessible Canvas Gauges
**Learning:** Analog gauge components rendered via CSS transforms or canvas are invisible to screen readers without explicit ARIA roles.
**Action:** Always wrap visual-only data visualizations in a container with `role="progressbar"` (or `meter`), `aria-valuenow`, and a descriptive `aria-label`. Add a `title` attribute for mouse users as a low-cost tooltip.
