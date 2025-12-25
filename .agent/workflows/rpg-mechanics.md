---
description: Generate and balance RPG mechanics for a 2d6+modifier system with 29 skills across 4 attributes. Use when creating skill checks with DCs, Board entries (hybrid evidence/psychological pinboard mechanic), NPC/encounter stat blocks, or balancing progres
---



RPG Mechanics Generation

Generate and balance RPG mechanics for a 2d6+modifier system with 29 skills across 4 attributes. Use when creating skill checks with DCs, Board entries (hybrid evidence/psychological pinboard mechanic), NPC/encounter stat blocks, or balancing progression systems. Designed for investigative psychological horror RPGs influenced by Disco Elysium's mechanics and X-Files aesthetics.

Generate balanced, thematically appropriate RPG mechanics for investigative psychological horror games.
Core System: 2d6 + Modifier
Roll: 2d6 + Skill Modifier + Situational Modifiers
Result: Compare to Difficulty Class (DC)
Probability Reference
2d6 ResultProbabilityDC Guidance22.78%Auto-fail threshold69.72%Desperate (untrained)716.67%Peak probability813.89%Routine (trained)108.33%Challenging122.78%Near-impossible
Standard DC Scale
DCDifficultyWhen to Use6TrivialTrained character, low stakes, establish competence8EasyBaseline professional task10ModerateStandard challenge, some risk12HardRequires specialization or preparation14Very HardExpert-level, significant consequences16ExtremeCampaign-defining moments only18+LegendaryShould be near-impossible; requires stacking advantages
Modifier Ranges
ModifierMeaning-2 to -1Weakness / Untrained0Average / No training+1 to +2Competent / Some training+3 to +4Professional / Experienced+5 to +6Expert / Specialist+7+Masterful / Rare
Skill Check Generation
Trigger: "create a skill check", "what's the DC for", "design a check"
Format
markdown#### [CHECK NAME]
**Skill**: [SKILL NAME]  
**DC**: [NUMBER]  
**Context**: [When/why this check occurs]

**Success**: [Mechanical and narrative outcome]
**Failure**: [Mechanical and narrative outcome]
**Critical Success (12+)**: [Optional: exceptional outcome]
**Critical Failure (Snake Eyes)**: [Optional: catastrophic outcome]

**Modifiers**:
- +2: [Advantageous condition]
- -2: [Disadvantageous condition]
Design Principles

Failure should be interesting — Never "nothing happens." Failure reveals information, creates complications, or costs resources.
Match DC to fiction — A locked door is DC 8 for a locksmith, DC 14 for a journalist.
Perspective matters — Same check, different skills: Believer uses FOLKLORE, Skeptic uses DEDUCTION, Haunted uses INSTINCT.
Stack sparingly — Don't require multiple checks for one action unless dramatically appropriate.

The Board
The Board replaces Disco Elysium's Thought Cabinet with a hybrid evidence/psychological system. It's a pinboard in the protagonist's mind (and physically in their workspace) where external clues and internal states coexist and interact.
Board Entry Types
TypeIconDescriptionEvidence📌Physical clue, document, testimonyTheory🔗Connection between evidence piecesObsession🌀Recurring thought that won't let goTrauma Echo💔Past event bleeding into presentBelief⚓Core conviction (can be shaken)
Board Entry Template
yamlboard_entry:
  id: "[unique_id]"
  type: "[evidence|theory|obsession|trauma_echo|belief]"
  name: "[Display Name]"
  
  # Discovery
  discovered_in: "[scene_id]"
  discovery_condition: "[How player finds/develops this]"
  
  # Content
  description: "[What it represents]"
  internal_voice: "[Which skill 'owns' this thought]"
  
  # Mechanics
  status: "[pinned|unpinned|resolved|suppressed]"
  slots_required: 1  # Board has limited slots
  
  # Effects while pinned
  effects_pinned:
    skill_modifiers:
      - skill: "[SKILL]"
        modifier: [+/-N]
    unlock_dialogue: ["dialogue_option_id"]
    unlock_actions: ["action_id"]
    perception_filter: "[How this colors what they notice]"
  
  # Resolution
  resolution_conditions:
    - "[What must happen to resolve this]"
  effects_resolved:
    permanent_modifier:
      skill: "[SKILL]"
      modifier: [+/-N]
    unlock: "[What becomes available]"
    narrative: "[How the character changes]"
  
  # Connections
  connects_to: ["other_entry_id"]
  conflicts_with: ["other_entry_id"]  # Can't pin both
Board Slot Economy

Starting slots: 3-4 (depending on archetype)
Maximum slots: 6-8 (gained through progression)
Slot cost: Most entries cost 1; major theories/traumas cost 2

Design Principles

Entries have costs and benefits — Pinning an obsession might give +2 to related checks but -1 to unrelated focus.
Connections create bonuses — Linked evidence provides insight checks.
Trauma echoes are double-edged — Power through pain, but risk spiraling.
Resolution changes you — Resolved entries leave permanent marks.

NPC/Encounter Stat Blocks
Trigger: "create an NPC", "stat block for", "design an encounter"
NPC Template
markdown## [NPC NAME]

**Role**: [Witness / Suspect / Ally / Antagonist / Victim]
**Archetype Read**: 
- Believer sees: [Supernatural role]
- Skeptic sees: [Rational role]
- Haunted sees: [Psychological projection]

### Stats
| Attribute | Value | Key Skills |
|-----------|-------|------------|
| Intellect | [1-6] | [Relevant skills] |
| Psyche | [1-6] | [Relevant skills] |
| Physique | [1-6] | [Relevant skills] |
| Motorics | [1-6] | [Relevant skills] |

### Social
- **Attitude**: [Hostile/Suspicious/Neutral/Friendly/Devoted]
- **Wants**: [What they're trying to achieve]
- **Fears**: [What they're avoiding]
- **Secret**: [What they're hiding]

### Interaction DCs
| Action | Skill | DC | Notes |
|--------|-------|-----|-------|
| Read intentions | Empathy | [DC] | |
| Intimidate | Authority | [DC] | |
| Persuade | Suggestion | [DC] | |
| Catch in lie | Drama | [DC] | |

### Dialogue Hooks
- **Opens up about**: [Topic that lowers guard]
- **Shuts down about**: [Topic that raises defenses]
- **Triggered by**: [What causes emotional reaction]
Progression Systems
Core Philosophy
Progression represents uncovering suppressed abilities, not learning new ones. The protagonist isn't growing—they're remembering who they were, or discovering who they've become.
Experience Triggers
TriggerXP ValueExampleResolve Board entry10-25Close a theory loopSurvive trauma check5-15Face echo without breakingCritical success5Natural 12Meaningful failure5Failure that advances storyChapter completion25-50Major milestone
Advancement Costs
ImprovementCostLimit+1 Skill10 × new rankMax +6+1 Board slot30Max 8Unlock suppressed ability50Narrative gated
Reference Files

references/skill-checks.md — Pre-built checks organized by situation
references/board-entries.md — Example entries for common narrative beats
references/probability-tables.md — Full 2d6 probability breakdowns