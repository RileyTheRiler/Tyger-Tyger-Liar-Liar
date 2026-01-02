## 2024-05-22 - [React.memo Optimization]
**Learning:** Implemented `React.memo` for `TerminalEntry` components.
**Action:** This optimization ensures O(1) rendering for new terminal entries instead of O(N), significantly reducing React reconciliation overhead as the game history grows. This is critical for text-heavy games where history is append-only.
