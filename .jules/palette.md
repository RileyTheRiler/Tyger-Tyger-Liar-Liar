## 2024-10-24 - Accessibility in Retro UI
**Learning:** Retro visual elements (analog gauges, flickering text) often rely purely on visual cues, making them inaccessible by default. Standard semantic HTML structures are often lost in "div soup" needed for complex CSS animations.
**Action:** When creating custom visual components (like gauges), always wrap them in a container with the appropriate ARIA role (`progressbar`) and values (`aria-valuenow`). This separates the visual representation (the needle rotation) from the semantic meaning (the value).
