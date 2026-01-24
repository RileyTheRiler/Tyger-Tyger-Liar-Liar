# Bolt's Journal - Performance Learnings

## 2024-10-24 - Frontend Terminal Optimization
**Learning:** `React.memo` is critical for append-only log components like `Terminal.jsx` to prevent O(N) re-renders of all previous entries on every update.
**Action:** Inspect similar list-based components (`ChoiceGrid`, `InputConsole` history) for this pattern.

**Learning:** Implicit dependencies (like `VHSEffect` in `App.jsx`) can cause runtime crashes in production/verification even if linting passes or doesn't flag them as missing modules in some environments.
**Action:** Always verify the full component tree renders in a simulated environment (Playwright) before assuming "code looks correct".

## 2024-05-22 - [Particle System Performance]
**Learning:** Recreating `Particle` classes inside `useEffect` causes massive memory churn and re-initialization on every render, leading to dropped frames in the `ParticleCanvas` component.
**Action:** Define helper classes outside the component or `useEffect` scope to ensure they are created once and reused, optimizing the animation loop.

## 2024-05-23 - [React Component Re-renders]
**Learning:** Large list components like `Terminal` can cause significant main thread blocking if every item re-renders when the list updates.
**Action:** Use `React.memo` on list items (`TerminalEntry`) to prevent unnecessary re-renders of unchanged items when new items are added to the list.

## 2024-05-24 - [CSS vs JS Animation Loops]
**Learning:** Using `setInterval` with `setState` for purely visual "jitter" effects (like in `AnalogGauge`) forces full React component re-renders every 100ms, consuming main thread resources.
**Action:** Move continuous visual loops to CSS keyframes and `transform` properties to offload animation to the compositor thread and eliminate re-renders.

## 2024-10-25 - [React Hook Purity & Hydration]
**Learning:** Using `Math.random()` inside `useMemo` or during render causes layout thrashing and "Hydration Mismatch" errors because the server/initial render doesn't match the client's subsequent renders.
**Action:** Use a deterministic pseudo-random number generator (PRNG) with a stable seed (like ID or index) for "random" visual variations in React components.

## 2024-10-25 - [Verification Dependencies]
**Learning:** A syntax error in a seemingly unrelated component (`StatusHUD.jsx`) can break the entire build process, preventing verification of the target component (`MindMap.jsx`).
**Action:** When verification scripts fail with timeouts or white screens, check the browser console logs (via Playwright) for global runtime errors before assuming the issue lies in the component being tested.

## 2024-10-25 - [Verifying High-Frequency Animations]
**Learning:** High-frequency animations implemented via `requestAnimationFrame` and refs bypass React's render cycle, making them invisible to standard component testing.
**Action:** Verify these optimizations by using Playwright to sample DOM node styles (e.g. `transform`, `opacity`) over a short interval to confirm values are changing, rather than relying on snapshot tests.
