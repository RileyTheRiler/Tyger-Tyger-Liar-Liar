---
name: narrative-design
description: Generate narrative documentation for multi-perspective psychological horror games. Use when creating scene breakdowns, branching dialogue, event timelines, or character arcs for games with perspective-based storytelling (like Kaltvik's Believer/Skeptic/Haunted system). Supports both human-readable markdown and structured YAML for game engine integration.
---

# Narrative Design Documentation

Generate consistent narrative documentation for psychological horror games with multiple-perspective storytelling.

## Core Conventions

### The Three Perspectives

Each archetype perceives identical events completely differently:

| Archetype | Code | Perception Filter | Evidence Interpretation |
|-----------|------|-------------------|------------------------|
| THE BELIEVER | `[B]` | Supernatural is real | Anomalies confirm the otherworldly |
| THE SKEPTIC | `[S]` | Rational explanations exist | Anomalies are misperception/manipulation |
| THE HAUNTED | `[H]` | Personal trauma colors reality | Anomalies echo past wounds |

### Baseline Reality

Use `## THE EVENT` to document what objectively occurs before perspective filters apply. This is the raw sensory data before interpretation.

### Character Mapping

When protagonists have names, map them in document headers:

```yaml
perspectives:
  believer: "Marcus Chen"
  skeptic: "Dr. Elena Vasquez"  
  haunted: "Jamie Okafor"
```

## Document Types

### 1. Scene Breakdown

Structure for documenting a single scene across all perspectives:

```markdown
# SCENE: [Scene Name]
Location: [Where]
Time: [When]
Triggers: [What brings player here]

## THE EVENT
[Objective sensory description - what cameras would record]

## THE BELIEVER
### Perception
[What they notice, how they interpret it]
### Available Actions
[Unique choices available to this archetype]
### Skill Checks
[Relevant skills and DCs]

## THE SKEPTIC
[Same structure]

## THE HAUNTED
[Same structure]

## Convergence Points
[Where perspectives must align for plot progression]
```

### 2. Branching Dialogue

Use YAML for dialogue trees with perspective variants:

```yaml
dialogue_node:
  id: "ranger_station_001"
  speaker: "Ranger Mills"
  
  prompt:
    event: "Mills looks up from paperwork, expression guarded."
    believer: "You sense something ancient watching through his eyes."
    skeptic: "Classic defensive body language—he's hiding something."
    haunted: "His face flickers, just for a moment, into someone else's."
  
  responses:
    - id: "direct"
      text: "We need to talk about what happened at the lake."
      requirements: {skill: "Authority", dc: 8}
      next: "ranger_station_002"
      
    - id: "sympathetic"
      text: "You look like you haven't slept in days."
      requirements: {skill: "Empathy", dc: 6}
      next: "ranger_station_003"
      perspective_variants:
        haunted:
          text: "I know that look. I've worn it myself."
          requirements: {skill: "Empathy", dc: 4}  # Easier for Haunted
```

### 3. Event Timeline

Document the objective sequence with perception overlays:

```markdown
# TIMELINE: [Arc Name]

## Hour 0: The Arrival
### THE EVENT
Team arrives at Kaltvik research station. Snow heavy. Radio works.

### PERCEPTION MATRIX
| Detail | Believer | Skeptic | Haunted |
|--------|----------|---------|---------|
| Static on radio | Spirit interference | Atmospheric conditions | Sounds like whispered names |
| Empty bunks | Previous team fled | Reassigned | Someone was taken from each one |

## Hour 6: First Contact
[Continue pattern]
```

### 4. Character Arc Documentation

Track character development across the narrative:

```yaml
character_arc:
  name: "Marcus Chen"
  archetype: "believer"
  
  starting_state:
    belief_level: 3  # 1-5 scale
    key_trauma: "Sister's disappearance, age 12"
    coping_mechanism: "Obsessive research into unexplained phenomena"
    
  arc_beats:
    - trigger: "Discovers sister's journal in station"
      shift: "Belief strengthens but becomes personal"
      mechanical_effect: "+1 to Witness skill, -1 to Composure"
      
    - trigger: "Confronts entity wearing sister's face"
      branch_point: true
      options:
        - choice: "Embrace the vision"
          outcome: "Crossing threshold—may not return"
        - choice: "Reject and attack"
          outcome: "Entity retreats, belief shattered temporarily"
          
  possible_endpoints:
    - "Transcendence: Joins sister beyond the veil"
    - "Grief: Accepts loss, maintains belief"
    - "Skepticism: Rejects everything, loses meaning"
    - "Haunted: Becomes what he sought"
```

## Output Formats

### Markdown (.md)
Use for: Human-readable documentation, design review, writer handoffs

### YAML (.yaml)
Use for: Game engine integration, structured data, dialogue systems

### JSON (.json)
Use for: API compatibility, web-based tools, Datasworn integration

## Principles

1. **THE EVENT comes first** — Always establish objective reality before filtering
2. **No perspective is "correct"** — Each interpretation must be internally consistent and equally valid
3. **Mechanical consequences** — Perception differences should affect gameplay, not just flavor
4. **Ambiguity is sacred** — Never resolve whether supernatural elements are "real"
5. **Indigenous respect** — Show consequences of ignoring warnings, never appropriate cultural elements

## Quick Reference

See `references/perspective-matrix.md` for the full perception filter reference.
See `references/skill-integration.md` for connecting narrative to RPG mechanics.
