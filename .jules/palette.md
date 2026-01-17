## 2024-05-23 - StatusHUD Accessibility Pattern
**Learning:** Analog gauges are visually rich but inaccessible by default. Translating them to `role="progressbar"` with `aria-valuenow` provides a clear semantic equivalent. Also, aliasing `motion` to `Motion` (PascalCase) satisfies the `no-unused-vars` linter rule while keeping the component used.
**Action:** When creating custom visual meters, always wrap them in a container with `role="progressbar"` and hide the visual parts with `aria-hidden="true"` to reduce noise for screen readers. Alias framer-motion imports to PascalCase.
