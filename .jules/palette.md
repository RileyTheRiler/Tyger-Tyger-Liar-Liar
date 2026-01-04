## 2024-10-27 - Visual-only Gauge Pattern
**Learning:** Purely visual components like analog gauges often completely exclude screen reader users if they don't carry ARIA roles.
**Action:** When creating custom visual meters (like gauges, dials, health bars), always wrap them in a container with `role="progressbar"` (or `meter`), `aria-valuenow`, and a proper `aria-label`. Hide the internal visual clutter from screen readers using `aria-hidden="true"`.
