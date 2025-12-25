---
description: Generate playtest scenarios and test cases for branching narrative games. Use when creating test playthroughs for different player archetypes, validating skill check balance, identifying untested branches, or stress-testing narrative systems. Support
---

Playtest Scenario Creation


Generate playtest scenarios and test cases for branching narrative games. Use when creating test playthroughs for different player archetypes, validating skill check balance, identifying untested branches, or stress-testing narrative systems. Supports coverage analysis, edge case identification, and replayability validation for games with multiple-perspective systems.

Generate systematic test cases to validate narrative games with branching paths and multiple-perspective systems.
Testing Philosophy
Playtesting investigative narrative games requires testing:

Mechanics: Do skill checks work? Is difficulty balanced?
Narrative: Are all branches reachable? Do they feel different?
Perspective: Does each archetype get a meaningfully different experience?
Replayability: Is there reason to play again?
Edge Cases: What breaks when players do unexpected things?

Scenario Types
1. Archetype Playthrough
Full game playthrough from one archetype's perspective.
Trigger: "playtest as [archetype]", "test believer path"
Output:
markdown# Playtest: [ARCHETYPE] Playthrough

## Build
- Archetype: [Believer/Skeptic/Haunted]
- Primary Stats: [High attributes]
- Key Skills: [Top 5 skills]
- Board Setup: [Starting pinned entries]

## Decision Log
| Scene | Choice Made | Rationale | Result |
|-------|-------------|-----------|--------|
| [ID] | [Choice] | [Why this archetype picks this] | [Outcome] |

## Skill Check Log
| Scene | Check | Roll Needed | Target DC | Pass/Fail | Impact |
|-------|-------|-------------|-----------|-----------|--------|
| [ID] | [Skill] | [Mod+Roll] | [DC] | [P/F] | [What changed] |

## Path Summary
- Scenes visited: [List]
- Scenes missed: [List]
- Unique content: [Archetype-exclusive moments]
- Ending reached: [Which ending]

## Observations
[Notes on experience, pacing, difficulty, satisfaction]
2. Skill Check Stress Test
Test specific mechanics across difficulty ranges.
Trigger: "test skill balance", "check DC calibration"
Output:
markdown# Skill Check Stress Test: [SKILL or SCENE]

## Check Profile
- Skill tested: [SKILL]
- Baseline modifier: [Expected player range]
- DC range: [Lowest to highest in content]

## Test Matrix
| Check ID | DC | With +0 | With +2 | With +4 | With +6 |
|----------|-----|---------|---------|---------|---------|
| [ID] | [DC] | [%] | [%] | [%] | [%] |

## Failure State Analysis
| Check | On Failure | Dead End? | Recovery Path |
|-------|------------|-----------|---------------|
| [ID] | [What happens] | [Y/N] | [How to continue] |

## Recommendations
- [Suggested DC adjustments]
- [Failure state improvements]
3. Branch Coverage Test
Map all paths through a scene or chapter.
Trigger: "test branch coverage", "map paths for [scene]"
Output:
markdown# Branch Coverage: [SCENE/CHAPTER ID]

## Path Map
[Entry]
├── [Choice A]
│   ├── [Outcome A1] → [Next scene]
│   └── [Outcome A2] → [Next scene]
├── [Choice B]
│   └── [Outcome B1] → [Next scene]
└── [Choice C] [LOCKED: Requires X]
└── [Outcome C1] → [Next scene]

## Coverage Table
| Path | Requirements | Tested? | Notes |
|------|--------------|---------|-------|
| A→A1 | None | [ ] | |
| A→A2 | Skill check fail | [ ] | |
| B→B1 | None | [ ] | |
| C→C1 | [Specific unlock] | [ ] | |

## Unreachable Content
- [Content that can't be accessed due to requirements]

## Redundant Paths
- [Paths that lead to identical content]
4. Three-Archetype Divergence Test
Verify meaningful difference between archetype experiences.
Trigger: "test archetype divergence", "compare perspectives"
Output:
markdown# Divergence Test: [SCENE ID]

## Shared Content
[Content identical across all three archetypes]
- [Element 1]
- [Element 2]

## Divergent Content

### Believer Exclusive
| Element | Type | Word Count | Significance |
|---------|------|------------|--------------|
| [Perception text] | Narration | [#] | [High/Med/Low] |
| [Dialogue option] | Choice | [#] | [High/Med/Low] |

### Skeptic Exclusive
| Element | Type | Word Count | Significance |
|---------|------|------------|--------------|
| [Perception text] | Narration | [#] | [High/Med/Low] |

### Haunted Exclusive
| Element | Type | Word Count | Significance |
|---------|------|------------|--------------|

## Divergence Score
- Unique content ratio: [%]
- Different skill checks available: [Y/N]
- Different outcomes possible: [Y/N]
- Replay value: [High/Med/Low]

## Recommendations
[Suggestions for increasing/balancing divergence]
5. Edge Case Scenarios
Test what happens when players do unexpected things.
Trigger: "edge case test", "break the scene", "adversarial playtest"
Output:
markdown# Edge Case Test: [SCENE ID]

## Standard Path
[Expected player behavior]

## Edge Cases Tested

### Sequence Breaking
| Attempt | Expected Behavior | Actual | Issue? |
|---------|-------------------|--------|--------|
| [Skip tutorial] | [Blocked/Allowed] | | |
| [Return to locked area] | | | |
| [Access before prerequisite] | | | |

### Resource Extremes
| Attempt | Expected | Actual | Issue? |
|---------|----------|--------|--------|
| [No Board slots] | | | |
| [All skills at +0] | | | |
| [All skills at +6] | | | |

### Dialogue Exhaustion
| Attempt | Expected | Actual | Issue? |
|---------|----------|--------|--------|
| [Ask every option] | | | |
| [Leave mid-conversation] | | | |
| [Return after ending convo] | | | |

### Failure Cascades
| Attempt | Expected | Actual | Issue? |
|---------|----------|--------|--------|
| [Fail all checks in scene] | | | |
| [Fail critical path check] | | | |

## Broken States Found
- [Description of any broken states]

## Recommended Fixes
- [Solutions]
Playtest Personas
Pre-built player types for testing:
The Completionist

Tries to see everything
Exhausts all dialogue
Returns to previous areas
Tests: Branch coverage, content availability

The Speedrunner

Takes shortest path
Skips optional content
Tests: Critical path integrity, minimum viable playthrough

The Role-Player

Makes "in character" choices
Ignores meta-knowledge
Tests: Narrative coherence, archetype consistency

The Chaos Agent

Makes random/contradictory choices
Tests boundaries
Tests: Edge cases, failure states, robustness

The Min-Maxer

Optimizes stats for success
Seeks best outcomes
Tests: Difficulty balance, reward structures

Quick Test Templates
Scene Validation Checklist
markdown## Scene: [ID]

### Accessibility
- [ ] Can be reached from intended entry points
- [ ] Locked appropriately if conditional
- [ ] Exit points connect correctly

### Mechanics
- [ ] All skill checks have defined success/failure
- [ ] DCs are appropriate for expected stats
- [ ] No unavoidable failure states (unless intentional)

### Content
- [ ] All three archetypes have content
- [ ] Divergent content is meaningfully different
- [ ] Clues are placed fairly (Christie rules)

### Polish
- [ ] No placeholder text
- [ ] Consistent character voice
- [ ] No contradictions with other scenes
Chapter Validation Checklist
markdown## Chapter: [ID]

### Structure
- [ ] All scenes reachable
- [ ] No orphaned scenes
- [ ] At least one valid path to completion

### Balance
- [ ] Approximate playtime per path documented
- [ ] Critical path < 30 minutes
- [ ] Optional content adds meaningful value

### Replayability
- [ ] Three archetypes offer different experiences
- [ ] Different choices lead to different outcomes
- [ ] Second playthrough reveals new content
Reference Files

references/test-personas.md — Detailed player persona profiles
references/coverage-templates.md — Extended coverage analysis templates
references/common-breaks.md — Catalog of common breaking points in narrative games