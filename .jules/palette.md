## 2024-10-14 - Accessible Retro Gauges
**Learning:** Retro/sci-fi UI elements often rely purely on visual metaphors (needles, bars) which are completely invisible to screen readers.
**Action:** When implementing custom visual gauges (like `AnalogGauge`), always wrap them in `role="progressbar"` with `aria-valuenow`, `aria-valuemin`, and `aria-valuemax` to ensure the data is communicated, while hiding the decorative visual parts with `aria-hidden="true"`.
