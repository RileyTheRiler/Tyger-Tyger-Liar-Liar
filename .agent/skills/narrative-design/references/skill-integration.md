# Skill Integration Reference

Connect narrative elements to the 2d6 + modifier RPG system with 4 attributes and 29 skills.

## Attribute Overview

| Attribute | Focus | Archetype Affinity |
|-----------|-------|-------------------|
| INTELLECT | Analysis, knowledge, deduction | THE SKEPTIC |
| PRESENCE | Social, authority, perception | Neutral |
| PHYSIQUE | Body, endurance, action | Neutral |
| PSYCHE | Intuition, trauma, the uncanny | THE BELIEVER / THE HAUNTED |

## Perspective-Skill Synergies

### THE BELIEVER Advantages
- **Witness** (PSYCHE): +2 when perceiving supernatural phenomena
- **Folklore** (INTELLECT): +1 when recognizing mythological patterns
- **Communion** (PSYCHE): Unique skill—attempt contact with entities

### THE SKEPTIC Advantages
- **Analysis** (INTELLECT): +2 when examining physical evidence
- **Interrogation** (PRESENCE): +1 when detecting deception
- **Research** (INTELLECT): +1 when accessing records, databases

### THE HAUNTED Advantages
- **Trauma Bond** (PSYCHE): +2 when relating to suffering NPCs
- **Survival** (PHYSIQUE): +1 from hypervigilance
- **Suppression** (PSYCHE): Unique skill—resist flashback triggers

## Skill Check Integration in Scenes

### Dialogue Skill Checks

```yaml
dialogue_option:
  text: "You're lying. I can see it in your eyes."
  skill: "Interrogation"
  attribute: "PRESENCE"
  dc: 8
  perspective_modifiers:
    skeptic: -2  # Easier for skeptics
    haunted: +1  # Harder when projecting
  success: "NPC breaks, reveals partial truth"
  failure: "NPC becomes hostile, conversation ends"
  critical_success: "Full confession plus additional intel"
  critical_failure: "NPC attacks or flees"
```

### Perception Skill Checks

```yaml
perception_check:
  trigger: "Entering the abandoned research wing"
  skill: "Awareness"
  attribute: "PRESENCE"
  dc: 6
  perspective_reveals:
    believer:
      success: "Symbols scratched into doorframe—warning or invitation"
      failure: "Something feels wrong but unclear"
    skeptic:
      success: "Recent tool marks on lock—someone's been here"
      failure: "Standard abandoned facility"
    haunted:
      success: "The same layout as the hospital. The same smell."
      failure: "Disorienting déjà vu, nothing specific"
```

### Investigation Skill Checks

```yaml
investigation_check:
  location: "Victim's desk"
  skill: "Research"
  attribute: "INTELLECT"
  dc: 7
  time_cost: 1_hour
  findings:
    all_perspectives:
      - "Calendar marked with increasing frequency"
      - "Photos of northern lights"
    believer_bonus: "Journal entries about 'the calling'"
    skeptic_bonus: "Financial records showing large withdrawals"
    haunted_bonus: "Hidden photo of family—reminds you of yours"
```

## The Board Integration

Board entries (replacing Disco Elysium's Thought Cabinet) should connect to skills:

```yaml
board_entry:
  id: "theory_parasitic_intelligence"
  name: "Parasitic Intelligence Theory"
  
  discovery_trigger:
    skill: "Pattern Recognition"
    dc: 9
    context: "After examining three or more disappearance sites"
  
  internalization:
    time: 4_hours
    during_effect: "-1 to Composure (obsessive focus)"
    
  completed_effect:
    believer: "+2 to Witness when seeking entity patterns"
    skeptic: "+1 to Analysis when examining victims"
    haunted: "+1 to Suppression (finally, an explanation)"
    
  unlearning:
    trigger: "Contradictory evidence or traumatic encounter"
    effect: "Theory removed, -1 Morale for 24 hours"
```

## Difficulty Class Guidelines

| DC | Difficulty | Example |
|----|------------|---------|
| 4 | Trivial | Noticing something openly visible |
| 6 | Easy | Convincing a friendly NPC |
| 8 | Moderate | Standard investigation check |
| 10 | Challenging | Detecting hidden evidence |
| 12 | Hard | Breaking a hostile NPC |
| 14 | Very Hard | Feats requiring exceptional ability |
| 16+ | Nearly Impossible | Only with extensive preparation/bonuses |

## Consequence Integration

Skill failures should have narrative weight:

### Minor Failure (Miss by 1-2)
- Partial information
- Time cost
- NPC becomes wary

### Standard Failure (Miss by 3-4)
- No useful information
- Resource cost (supplies, goodwill)
- Minor narrative consequence

### Critical Failure (Natural 2, or miss by 5+)
- Harmful misinformation
- Significant resource loss
- Lasting narrative consequence
- Potential injury or trauma

## Perspective-Locked Skill Checks

Some checks only appear for specific archetypes:

```yaml
locked_check:
  archetype: "haunted"
  trigger: "Seeing the entity's true form"
  skill: "Suppression"
  dc: 10
  success: "You stay present. The flashback recedes."
  failure: "The past overwhelms the present. Lose next action."
  note: "Believer sees revelation, Skeptic sees hallucination—no check needed"
```
