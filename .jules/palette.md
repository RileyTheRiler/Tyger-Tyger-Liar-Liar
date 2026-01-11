# Palette's Journal - UX & Accessibility Learnings

## 2024-05-22 - [Accessible Status Gauges & React Component Aliasing]
**Learning:**
1. **Component Verification:** To verify specific UI states (like low sanity visuals) without playing through the game, mocking API endpoints (like `/api/start`) in Playwright is essential.
2. **Linter vs. Library:** `framer-motion`'s `motion.div` syntax triggers `no-unused-vars` in this project's ESLint config. Aliasing to PascalCase (e.g., `const Motion = motion.div`) is a clean workaround that satisfies the linter while preserving functionality.
3. **Implicit Dependencies:** Visual components like `VHSEffect` must be explicitly imported. The build process didn't catch the missing import, emphasizing the need for runtime verification (even simple smoke tests).

**Action:**
- Always alias `motion` components to PascalCase variables when using `framer-motion` in this repo.
- Use API mocking in verification scripts to isolate UI components.
