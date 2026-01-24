## 2024-05-23 - Accessibility in Custom Text UIs
**Learning:** Custom UI implementations (like `<ul>` acting as menus) often miss standard semantic roles (`role="menuitem"`, `tabindex="0"`), making them invisible to screen readers and keyboard users.
**Action:** Always verify custom interactive elements have appropriate ARIA roles and keyboard event handlers (Focus, Enter, Space).

## 2024-05-23 - Interaction Gating
**Learning:** "Click to Start" overlays are a common pattern for AudioContext initialization but block keyboard-only users if `keydown` isn't also listened for.
**Action:** Always pair `click` listeners with `keydown` listeners for "Press Start" screens to ensure inclusivity.

## 2024-05-23 - Syncing Focus and State
**Learning:** When using custom state (like `selectedIndex`) for navigation alongside native focus (via `tabindex`), you must synchronize them. If a user Tabs to an item, the custom state must update, otherwise pressing Enter might trigger the wrong action.
**Action:** Add `focus` event listeners to interactive elements that update the application's internal selection state.
