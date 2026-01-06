# Bolt's Journal

## 2024-05-22 - Initial Setup
**Learning:** Performance journal initialized.
**Action:** Document critical learnings here.

## 2024-05-22 - Frontend Anti-Patterns Detected
**Learning:** Found critical React anti-patterns in `MindMap.jsx` (conditional `useMemo` call) and `ParticleCanvas.jsx` (inline class definition). `MindMap` issue effectively breaks React's hook ordering rules and risks crashes.
**Action:** These require separate bug-fix tasks. For now, focused on `Terminal.jsx` optimization as it yields the best stable performance gain for the text-heavy UI.
