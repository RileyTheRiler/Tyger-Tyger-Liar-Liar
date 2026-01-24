## 2024-03-22 - [React + Framer Motion Linter Conflict]
**Learning:** The `eslint-plugin-react` rule `no-unused-vars` can falsely flag `motion` as unused when it is only used in JSX (e.g., `<motion.div>`) if the linter configuration is strict or the plugin version is older.
**Action:** Use the project convention of aliasing `motion` to `Motion` (`import { motion as Motion } from 'framer-motion'`) which bypasses the rule by matching the allowed `^[A-Z_]` pattern for unused vars.

## 2024-03-22 - [Critical Game State Accessibility]
**Learning:** Analog gauges that rely solely on visual rotation (CSS transforms) are completely invisible to screen readers.
**Action:** Always add `role="progressbar"`, `aria-label`, and `aria-valuenow` to any component that displays a value visually without text. This turns a "decorative div" into a functional data point for all users.
## 2024-05-23 - StatusHUD Accessibility Pattern
**Learning:** Analog gauges are visually rich but inaccessible by default. Translating them to `role="progressbar"` with `aria-valuenow` provides a clear semantic equivalent. Also, aliasing `motion` to `Motion` (PascalCase) satisfies the `no-unused-vars` linter rule while keeping the component used.
**Action:** When creating custom visual meters, always wrap them in a container with `role="progressbar"` and hide the visual parts with `aria-hidden="true"` to reduce noise for screen readers. Alias framer-motion imports to PascalCase.
## PALETTE'S JOURNAL
This journal records CRITICAL UX/accessibility learnings.

Format: `## YYYY-MM-DD - [Title]
**Learning:** [UX/a11y insight]
**Action:** [How to apply next time]`

## 2024-05-22 - Custom Gauge Accessibility
**Learning:** Custom visual meters (like analog gauges) are invisible to screen readers without explicit semantics. They require `role="progressbar"` (or `meter`) along with `aria-valuenow`, `aria-valuemin`, and `aria-valuemax` to convey their state.
**Action:** Always wrap custom data visualizations in a container with appropriate ARIA roles and labels.
## 2024-05-22 - Accessibility in Status HUD
**Learning:** Analog gauges are visually appealing but completely inaccessible to screen readers.
**Action:** Use `role="progressbar"` with `aria-valuenow`, `aria-valuemin`, and `aria-valuemax` to make them announceable. Adding a "hidden" digital readout or using `aria-label` is crucial for context.

## 2024-05-22 - Input Console Labels
**Learning:** Terminal-style inputs often omit labels for immersion, which fails WCAG criteria.
**Action:** Use `aria-label` to provide context without breaking the visual aesthetic. Dynamic labels (e.g., "System busy") provide excellent feedback for non-sighted users.
## 2026-01-24 - [Title Screen Accessibility]
**Learning:** Decorative text like `[START_INVESTIGATION]` is noisy for screen readers. Also, custom buttons often lack visible focus states for keyboard users.
**Action:** Use `aria-label` for the clean action name, hide the decorative text with `aria-hidden="true"`, and ensure `:focus-visible` styles match `:hover` styles for consistency.
