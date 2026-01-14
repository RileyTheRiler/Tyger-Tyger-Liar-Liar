## 2024-03-22 - [React + Framer Motion Linter Conflict]
**Learning:** The `eslint-plugin-react` rule `no-unused-vars` can falsely flag `motion` as unused when it is only used in JSX (e.g., `<motion.div>`) if the linter configuration is strict or the plugin version is older.
**Action:** Use the project convention of aliasing `motion` to `Motion` (`import { motion as Motion } from 'framer-motion'`) which bypasses the rule by matching the allowed `^[A-Z_]` pattern for unused vars.

## 2024-03-22 - [Critical Game State Accessibility]
**Learning:** Analog gauges that rely solely on visual rotation (CSS transforms) are completely invisible to screen readers.
**Action:** Always add `role="progressbar"`, `aria-label`, and `aria-valuenow` to any component that displays a value visually without text. This turns a "decorative div" into a functional data point for all users.
