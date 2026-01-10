## 2024-05-21 - Accessible Analog Gauges
**Learning:** Visual-only gauges (using CSS rotation) are completely invisible to screen readers.
**Action:** Wrap such components in `role="progressbar"` with `aria-valuenow` and `aria-label` to provide an equivalent non-visual experience.
