# Canon & Constraints

> **This document sits above all other design documents.**
> Every system, scene, and content piece must respect these non-negotiables.

---

## Core Setting Constraints

### The 67-Day Polar Night
- The game takes place during 67 consecutive days of darkness in Kaltvik, an isolated Arctic community
- The polar night is not just aesthetic—it drives pacing, psychological pressure, and systemic dread
- All time mechanics, weather systems, and atmospheric descriptions must reinforce the oppressive darkness

### The 347 Resonance
- The town population starts at exactly **347**
- Population decrements are permanent, visible, and consequential
- Every death/disappearance affects trust, resources, and available interactions
- The number 347 has thematic significance—do not arbitrarily change it

### Isolation as Mechanic
- No outside help is coming
- Communication with the outside world is unreliable, compromised, or cut off
- Every resource is finite; every ally is local; every threat is internal or unknowable

---

## The Unreliable Lens (Primary Mechanic)

### Three Archetypes
| Archetype | Interpretation | Skill Bias |
|-----------|---------------|------------|
| **Believer** | Sees supernatural causation, patterns of the otherworldly | Paranormal Sensitivity, Instinct |
| **Skeptic** | Sees rational explanations, human conspiracy, scientific cause | Logic, Skepticism |
| **Haunted** | Sees personal guilt, trauma projection, self-doubt | Empathy, Subconscious |

### Implementation Rules
1. **Not Flavor—Structure**: The lens system alters scene text, available insights, NPC interpretations, and clue meaning
2. **No Ground Truth Revealed Early**: The game never confirms which lens is "correct" until endgame (if ever)
3. **Lens Affects Perception**: Same evidence produces different interpretations without changing base facts
4. **Text Layering Required**: Every major scene must define:
   - `text.base` (objective anchor)
   - `text.lens.believer`
   - `text.lens.skeptic`
   - `text.lens.haunted`
5. **Fallback Behavior**: If a lens variant is missing, use base + predefined micro-overlays

---

## Atmosphere-First Writing

### "Withhold the Monster" Principle
- The antagonist (supernatural, human, or ambiguous) is rarely seen directly
- Dread comes from implication, evidence of passage, and NPC reaction
- Direct confrontation is reserved for major story beats only
- Show aftermath, not action; suggest presence, not appearance

### Controlled Information Reveal
- Players earn information through skill gates, not exploration spam
- Clues appear in narrative text when skill thresholds are met
- The Board visualizes player knowledge—it does not grant new knowledge
- Every mystery has multiple plausible explanations based on lens

### Sensory Anchoring
Every scene must include:
1. One **sensory detail** (cold, sound, smell, texture)
2. One **mundane detail made threatening** (a clock, a menu, a door)
3. One **ambiguity hook** (interpretation without confirmation)

---

## Investigation Constraints

### No Pixel Hunting
- Investigation is **skill-gated** and **text-forward**
- Players do not click around hoping to find hidden objects
- Passive Perception checks reveal clues automatically when thresholds are met
- Equipment (camera, UV light, tape recorder) unlocks specific clue categories

### Skill-Based Discovery
```
Scene loads → Evaluate passive perception →
  If skill >= threshold OR equipment present →
    Append clue text to narrative + Add clue to Board
```

### Clue Properties
- Every clue has a **reliability score** (0.0 to 1.0)
- Clues link to **theories** (supports, contradicts, or associates)
- Clues have **tags** for auto-linking: `aurora`, `dewline`, `missing`, `medical`, `folklore`, `government`

---

## Trust System

### Visible and Trackable
- NPC trust is displayed numerically (0-100 scale)
- Trust affects dialogue options, information access, and alliance availability
- Trust can decrease permanently based on player choices

### Trust Mechanics
- **Fear Score** (optional per NPC): Some NPCs fear the player rather than trust them
- Trust gates unlock critical story branches
- Broken trust creates permanent consequences (NPCs refuse to help, share misinformation, or actively oppose)

### The Board Displays Relationships
- NPC nodes show current trust level
- Relationship edges indicate: `trusts`, `fears`, `suspicious_of`, `allied_with`

---

## Combat Constraints

### Textual and Tactical
- Combat is **not** a separate minigame with different mechanics
- Combat uses the same 2d6 skill check system as investigation
- Every combat option has a skill check and consequence

### Environment-Forward
- Missed attacks change the environment (window breaks → cold exposure)
- Environment ticks apply pressure (visibility drops, temperature falls)
- NPC panic states affect available options

### Consequence-Heavy
- Injuries persist and impose mechanical penalties
- Ammunition is tracked and finite
- Escape is always a valid tactical option
- Death is possible but rare; failure states are more interesting than death

---

## Time and Pressure Systems

### Time Blocks
- Time is measured in **blocks**: Night, Twilight, Dawn
- Actions cost time; time advances pressure systems
- Some scenes/NPCs are only available in specific blocks

### Pressure Escalation
- **Attention Meter**: Entity awareness increases based on player actions (taboo actions, supernatural investigation)
- **Storm State**: Storms limit movement, communication, and increase danger
- **Population Decline**: Each death/disappearance raises stakes

### Time as Resource
- Investigation takes time
- Theory internalization takes time
- Travel between locations takes time
- Time pressure forces prioritization

---

## Resolution Mechanics

### 2d6 Engine
```
2d6 + (Attribute + Skill + Modifiers) vs DC
```

### Difficulty Bands
| DC | Difficulty |
|----|------------|
| 7  | Easy |
| 9  | Standard |
| 11 | Hard |
| 13 | Extreme |

### Partial Success
- Fail by 1-2: **Success with cost** (time, trust, injury, attention)
- Fail by 3+: **Full failure** with consequences
- Stress/Attention modifiers make checks swingier under pressure

### Manual Roll Option
- UI must support player-entered dice values (2-12)
- Allows tabletop-style play or accessibility needs

---

## Content Creation Constraints

### Scene Template (Required Fields)
```yaml
id: unique_identifier
location_id: where
time_cost: minutes or blocks
prereqs: [flags, items, scenes]
text:
  base: objective_anchor
  lens:
    believer: interpretation
    skeptic: interpretation
    haunted: interpretation
  inserts:
    - condition: skill >= X
      text: additional_detail
      insert_at: AFTER_BASE
choices:
  - label: text
    next_scene: target
    checks: {skill, DC}
    effects: [trust, time, attention, flags]
passive_clues:
  - clue_id: required_visibility_condition
board_updates:
  - node_type: clue|theory|npc
    action: add|link
trust_impacts:
  - npc_id: delta
```

### Tone Checklist (Per Scene)
- [ ] One sensory detail
- [ ] One mundane detail made threatening
- [ ] One ambiguity hook

### Validation Rules
- No dead-end scenes (every scene has an exit)
- Every clue created is reachable via passive perception or explicit discovery
- Missing lens text falls back correctly to base + micro-overlay
- Theory prerequisites are achievable within the game

---

## Integration from External Material

### Canon Register Categories
| Category | Definition |
|----------|------------|
| **Confirmed** | Locked into the game—cannot be contradicted |
| **Candidate** | Good idea, not yet committed—can be cut |
| **Rejected** | Conflicts with pillars or scope—do not implement |

### Promotion Criteria
Ideas may only be promoted to Confirmed if they:
1. Strengthen the Unreliable Lens mechanic
2. Increase dread without showing the monster
3. Create meaningful consequences (trust, time, attention, injury)
4. Do NOT add a new system unless it replaces an existing one

---

## System Hierarchy

```
Canon & Constraints (this document)
        │
        ├── Core Entities (Scene, Clue, Theory, NPC, Condition, Encounter)
        │
        ├── Game State (Time, Population, Attention, Flags)
        │
        ├── Player State (Skills, Injuries, Inventory, Trust Map)
        │
        └── UI (Board, Narrative Renderer, Menus)
```

**The UI is a viewer/controller for data—not the source of truth.**

---

## Immutable Principles

1. **Atmosphere over action**: Dread through implication, not jump scares
2. **Consequence over convenience**: Player choices matter permanently
3. **Interpretation over revelation**: The truth remains uncertain
4. **Integration over addition**: New systems must earn their place
5. **Text over graphics**: Narrative quality carries the experience

---

*Last updated: Implementation Phase 1*
*Version: 1.0*
