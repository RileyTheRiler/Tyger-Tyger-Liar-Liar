# Bolt's Journal - Performance Learnings

## 2024-10-24 - Frontend Terminal Optimization
**Learning:** `React.memo` is critical for append-only log components like `Terminal.jsx` to prevent O(N) re-renders of all previous entries on every update.
**Action:** Inspect similar list-based components (`ChoiceGrid`, `InputConsole` history) for this pattern.

**Learning:** Implicit dependencies (like `VHSEffect` in `App.jsx`) can cause runtime crashes in production/verification even if linting passes or doesn't flag them as missing modules in some environments.
**Action:** Always verify the full component tree renders in a simulated environment (Playwright) before assuming "code looks correct".
