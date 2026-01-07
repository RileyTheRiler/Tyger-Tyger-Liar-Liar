## 2024-10-24 - StatusHUD and Input Accessibility
**Learning:** Visual-only gauges (like rotating CSS elements) are completely invisible to screen readers unless explicitly marked with `role="progressbar"` and `aria-valuenow`. Similarly, terminal-style inputs often lack labels for "immersion" but need `aria-label` to be usable.
**Action:** Always add ARIA attributes to custom visual components that convey data, even if they look "retro" or "diegetic".

## 2024-10-24 - ESLint and Framer Motion
**Learning:** The project's ESLint config (or lack of `eslint-plugin-react`) flags `motion` imports as unused when used as `<motion.div>`.
**Action:** Alias imports as `import { motion as Motion }` and use `<Motion.div>` to satisfy the linter without disabling rules.
