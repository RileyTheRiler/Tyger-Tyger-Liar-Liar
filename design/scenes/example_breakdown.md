# Scene Breakdown: The Frozen Diner

**ID**: `scene_diner_frozen`
**Location**: `diner_interior`
**Time**: Day 5, Night Block
**Prerequisites**: `event_green_pulse` occurred

---

## The Incident [OBSERVED]
The player enters the Diner. It is empty. The heating is off. On table 4, there is a cup of coffee that has frozen mid-spill, creating a brown icicle arching to the floor. The jukebox is playing a slowed-down track.

---

## Perspectives

### [BELIEVER]
*   **Perception**: Time stopped here. The freeze was instant—supernatural. The jukebox isn't slow; it's counting down.
*   **Internal Monologue**: *[INSTINCT - DC 10] Don't touch it. The cold is viral. It jumps.*
*   **Key Clue**: The frost patterns on the window form a map of the town.

### [SKEPTIC]
*   **Perception**: Furnace failure. Flash freeze due to open door. The coffee spill happened, then froze over hours. Jukebox motor is failing due to cold.
*   **Internal Monologue**: *[LOGIC - DC 9] thermodynamics. Liquid loses heat. Motor loses torque. Simple.*
*   **Key Clue**: The thermostat is smashed, set to lowest setting.

### [HAUNTED]
*   **Perception**: It's the waiting room all over again. Cold coffee. Empty chairs. The music sounds like the lullaby box.
*   **Internal Monologue**: *[PARANOIA - DC 11] They left because of you. You walked in, and they vanished.*
*   **Key Clue**: The lipstick mark on the cup looks like hers.

---

## Branching & Choices

### Convergence Point
Examining the **Kitchen Door**. It is locked from the *outside*.

### Decision Tree
1.  **Inspect the Coffee**
    *   *Touch*: Cold damage.
    *   *Analyze*: "It froze in seconds." (Believer/Skeptic clash)
2.  **Fix the Jukebox**
    *   *Repair Check*: Success stops the noise. Failure breaks it (silence is worse).
3.  **Breach Kitchen**
    *   *Force*: Loud noise. Attracts attention.
    *   *Pick Lock*: Quiet entry.

---

## Implementation Notes
*   **Audio**: `jukebox_slow.mp3` layered with `wind_loop`.
*   **Board Updates**: Add `Theory: Flash Current` if Believer. Add `Theory: Sabotage` if Skeptic.
