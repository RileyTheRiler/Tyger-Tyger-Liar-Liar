## 2024-05-22 - Missing Frontend Tests
**Learning:** The frontend codebase lacks a defined `test` script in `package.json`, causing standard CI/CD workflows to fail if they assume `npm test` exists.
**Action:** Always check `package.json` scripts before attempting to run tests. In future optimizations, consider adding a basic test runner (e.g., Vitest) if scope allows, or explicitly verify manually/visually as done here.

## 2024-05-22 - List Rendering Performance
**Learning:** In chat-like interfaces (Terminal), rendering the entire history list on every keystroke is an O(N) operation that causes visible input lag as the list grows.
**Action:** Wrap list items in `React.memo` to ensure only new entries render, keeping the input responsive regardless of history length.
