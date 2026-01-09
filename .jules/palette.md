# Palette's UX Journal

## 2024-05-22 - Custom Visualization Accessibility
**Learning:** Custom data visualizations (like analog gauges) are completely invisible to screen readers if they rely solely on CSS transforms.
**Action:** Always wrap custom visual components in standard ARIA roles (e.g., `role="progressbar"`) with explicit value attributes.
