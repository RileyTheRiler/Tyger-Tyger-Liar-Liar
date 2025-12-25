# Writer's Guide

## 1. Stylebook for Lens Variations

The **Lens System** filters reality based on the protagonist's dominant worldview. You must write variations that reflect these distinct psychological states.

### The Archetypes

#### 1. The Believer (Intuition > Logic)
*   **Tone**: Paranoid, superstitious, sensitive, metaphor-heavy.
*   **Focus**: Sensations, atmosphere, "unseen" connections, intent behind chaos.
*   **Keywords**: *Watching, hunger, ancient, wrong, rhythm, shadow.*
*   **Example**: "The static isn't random. It's a language. The darkness between the trees is breathing."

#### 2. The Skeptic (Logic > Intuition)
*   **Tone**: Clinical, rational, detached, dismissive of the supernatural.
*   **Focus**: Physical evidence, environmental factors, human psychology, material reality.
*   **Keywords**: *Hysteria, hallucination, physics, trauma, oxidation, pattern-seeking.*
*   **Example**: "Pareidolia. Your brain is trying to find faces in the noise. It's just wind and stress."

#### 3. The Haunted (Trauma Dominant)
*   **Tone**: Nostalgic (painful), cyclical, weary, personal.
*   **Focus**: Memories, guilt, deja vu, blurring of past and present.
*   **Keywords**: *Again, remember, echo, guilt, fault, mirror.*
*   **Example**: "You've been here before. Or maybe you never left. The smell of ash reminds you of *her*."

#### 4. Neutral (Balanced)
*   **Tone**: Objective, observant, journalistic.
*   **Focus**: Facts as they appear, standard sensory input.
*   **Example**: "The wind howls through the trees. The radio emits a steady static."

### Writing Scene Data
In your scene JSON:
```json
"text": {
  "base": "Objective description of the room.",
  "lens": {
    "believer": "Subjective interpretation for believers.",
    "skeptic": "Subjective interpretation for skeptics.",
    "haunted": "Subjective interpretation for the haunted."
  }
}
```

---

## 2. Internal Skill Voice Formatting

Skills are characters in the protagonist's head. They chime in to offer advice or observation.

### Formatting
*   **Color**: Use system colors if possible (Blue=Reason, Purple=Intuition, Red=Constitution, Yellow=Presence).
*   **Syntax**: `[Skill Name]: *The text of the thought.*`
*   **Bold**: **[Skill Name]**

### Tone Guide

#### Reason (Blue)
*   **Logic**: Cold, computational. "The numbers don't add up."
*   **Forensics**: Clinical, morbid curiosity. "Post-mortem lividity suggests movement."
*   **Skepticism**: Cynical, debunking. "They are lying. Look at the twitch."

#### Intuition (Purple)
*   **Paranormal Sensitivity**: Whispering, fearful, abstract. "The air tastes like ozone and dread."
*   **Instinct**: Urgent, animalistic. "RUN. NOW."
*   **Empathy**: Emotional, overwhelming. "You can feel their grief like a weight."

#### Constitution (Red)
*   **Endurance**: Stoic, masochistic. "Pain is just data. Keep moving."
*   **Reflexes**: Twitchy, fast. "Duck. Left. Now."

#### Presence (Yellow)
*   **Authority**: Commanding, arrogant. "Make them listen. You are in charge."
*   **Deception**: Sly, manipulative. "Tell them what they want to hear."

---

## 3. Sanity-Triggered Scene Distortion

As **Sanity** drops and **Reality** fractures, the text itself should become unreliable.

### Tiers of Madness

#### Tier 1: Unsettled (Sanity 50-74)
*   **Effect**: Minor sensory intrusions.
*   **Technique**: Add parenthetical doubts.
*   **Example**: "The door is locked. (Did you hear a latch click?)"

#### Tier 2: Hysteria (Sanity 25-49)
*   **Effect**: Word replacement, increased paranoia.
*   **Technique**: Swap neutral nouns for organic/hostile ones.
    *   *Door* -> *Mouth*
    *   *Window* -> *Eye*
    *   *Shadow* -> *Void*
*   **Example**: "The **mouth** is locked. The **void** in the corner is watching."

#### Tier 3: Psychosis (Sanity 1-24)
*   **Effect**: Full hallucinations, text corruption, 4th wall breaks.
*   **Technique**:
    *   **Zalgo/Static**: "The docr is lcxked."
    *   **Direct Address**: "THEY SEE YOU READING THIS."
    *   **Reversal**: ".dekcol si rood ehT"
    *   **Redaction**: "The door is [REDACTED]."

### Implementation
The `TextComposer` and `Game.apply_reality_distortion` handle this programmatically, but writers can script specific hallucinations using the `hallucinations/` data files or conditional inserts with `sanity_lt` (less than) checks.
