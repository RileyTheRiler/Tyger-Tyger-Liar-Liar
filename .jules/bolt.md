## 2024-05-22 - Terminal Rendering Optimization
**Learning:** `React.memo` is critical for list items in append-only lists like terminals. Without it, every new line causes *all* previous lines to re-render, leading to O(N) rendering performance where N is history length.
**Action:** Always wrap list item components in `React.memo` when the list grows over time and items are immutable.
