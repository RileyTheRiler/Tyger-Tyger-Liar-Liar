## 2024-05-22 - [Particle System Performance]
**Learning:** Recreating `Particle` classes inside `useEffect` causes massive memory churn and re-initialization on every render, leading to dropped frames in the `ParticleCanvas` component.
**Action:** Define helper classes outside the component or `useEffect` scope to ensure they are created once and reused, optimizing the animation loop.

## 2024-05-23 - [React Component Re-renders]
**Learning:** Large list components like `Terminal` can cause significant main thread blocking if every item re-renders when the list updates.
**Action:** Use `React.memo` on list items (`TerminalEntry`) to prevent unnecessary re-renders of unchanged items when new items are added to the list.

## 2024-05-24 - [CSS vs JS Animation Loops]
**Learning:** Using `setInterval` with `setState` for purely visual "jitter" effects (like in `AnalogGauge`) forces full React component re-renders every 100ms, consuming main thread resources.
**Action:** Move continuous visual loops to CSS keyframes and `transform` properties to offload animation to the compositor thread and eliminate re-renders.
