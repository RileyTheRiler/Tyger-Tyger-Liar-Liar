## 2024-05-22 - [Accessibility in Custom Gauges]
**Learning:** Custom visualization components (like AnalogGauge) are invisible to screen readers without explicit ARIA roles. While they provide rich visual data, they fail the basic "what is this?" test for non-visual users.
**Action:** When creating custom meters or gauges, always wrap them in a container with `role="progressbar"` (or `meter`), and provide `aria-valuenow`, `aria-valuemin`, and `aria-valuemax`. Hide the internal visual decoration with `aria-hidden="true"` to prevent confusing announcements.
