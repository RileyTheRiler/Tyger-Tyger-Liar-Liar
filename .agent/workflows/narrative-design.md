---
description: Generate narrative design documentation for psychological horror games with multiple-perspective systems. Use when creating scene breakdowns, branching dialogue trees, event timelines, character arc documentation, or any narrative content that requir
---

Narrative Design Documentation

Generate narrative design documentation for psychological horror games with multiple-perspective systems. Use when creating scene breakdowns, branching dialogue trees, event timelines, character arc documentation, or any narrative content that requires tracking how different character archetypes perceive the same events differently. Supports both human-readable markdown and structured YAML for game engine integration. Designed for projects influenced by Disco Elysium, X-Files, and psychological horror.

Generate consistent, professional narrative design documents for psychological horror/mystery games featuring multiple-perspective storytelling.
Core Concept: The Perception Framework
All narrative documentation uses a four-layer perception system:
LayerTagPurposeObserved[OBSERVED]Clinical description of what physically occurs—no interpretation, no certainty about meaningBeliever[BELIEVER]Supernatural interpretation; sees signs, omens, entitiesSkeptic[SKEPTIC]Rational interpretation; sees psychology, coincidence, human explanationHaunted[HAUNTED]Trauma-filtered interpretation; sees personal meaning, echoes of past, dissociation
Key principle: [OBSERVED] is not "truth"—it's the closest approximation to shared reality. Even this layer should contain ambiguity.
Document Types
1. Scene Breakdown
Single moment/location with all perspective variants.
Trigger: "scene breakdown", "write a scene", "design this moment"
Structure (see references/templates.md for full template):

Scene metadata (ID, location, time, preceding/following scenes)
The Incident (observed events)
Three perspective blocks with: perception, internal dialogue, available choices, skill checks
Convergence points (where perspectives must align)
Branching consequences

2. Branching Dialogue
Conversation trees with perspective-dependent options.
Trigger: "dialogue tree", "conversation", "write dialogue for"
Output: YAML structure (see references/templates.md)

Nodes with speaker, text, conditions
Perspective-locked options
Skill check gates
Emotional state tracking

3. Event Timeline
Chronological sequence showing observed vs. perceived.
Trigger: "timeline", "sequence of events", "what happens when"
Structure: Table format with columns for time, observed event, and each perspective's interpretation.
4. Character Arc Document
Track a character's psychological journey across the game.
Trigger: "character arc", "character development", "arc for [name]"
Structure:

Arc summary and thematic throughline
Key beats (inciting incident → escalation → crisis → resolution)
Perspective-specific relationship to this character
Transformation markers

5. Chapter/Act Summary
High-level narrative structure documentation.
Trigger: "chapter summary", "act breakdown", "outline"
Structure:

Narrative goals and themes
Key scenes list
Player agency points
Perspective divergence moments
Required convergence points

Workflow

Identify document type from user request
Determine scope: scene / chapter / arc / full game
Choose format:

Markdown → for reading, editing, discussion
YAML → for structured data, game engine integration
Both → when user needs documentation + implementation


Apply templates from references/templates.md
Validate ambiguity: ensure no perspective is "correct"

Writing Principles
From the project's established influences:

Hammett: Dialogue reveals character through what's unsaid. Keep exchanges terse.
Lovecraft: Atmosphere over explanation. Describe effect, not cause.
Christie: Plant fair clues in [OBSERVED]. The player should be able to solve it.
X-Files: Institutional paranoia. Evidence is always deniable. No clean resolutions.
Disco Elysium: Skills speak as characters. Internal dialogue is a chorus, not a monologue.
Telltale: Choices matter through relationship consequences, not just plot branches.

Output Conventions
File Naming
[type]_[identifier]_[version].md
scene_lighthouse_v1.md
dialogue_sheriff-interrogation_v2.yaml
timeline_night-one_v1.md
Perspective Blocks
markdown### [BELIEVER]
**Perception**: What they see/sense/feel
**Internal**: Skill-voice dialogue (italicized, attributed)
**Choices**: Available actions from this worldview
**Checks**: Required skill checks with DCs
Skill Check Format
[SKILL NAME - DC ##] Description of what's being attempted
Success: Outcome
Failure: Outcome
Reference Files

references/templates.md — Full templates for each document type
references/skill-list.md — The 29 skills and their narrative voices (for internal dialogue)