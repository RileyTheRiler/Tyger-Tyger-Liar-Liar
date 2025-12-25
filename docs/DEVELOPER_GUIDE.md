# Developer Guide

## 1. Adding a New Theory

Theories are central to the "Bad Blood" narrative engine, influencing player stats, dialogue options, and perception of the world.

### Step 1: Define the Theory in JSON
Add a new entry to `data/theories.json`. The key is the theory ID (e.g., `trust_no_one`).

```json
"trust_no_one": {
    "name": "Trust No One",
    "category": "conspiracy",
    "description": "You've uncovered patterns of surveillance...",
    "requirements": {
        "clues_required": [],
        "flags_required": [],
        "scenes_visited": [],
        "theories_active": [],
        "min_skill": {}
    },
    "internalize_time_hours": 6,
    "effects": {
        "Perception": 1,
        "Wits": 2,
        "Empathy": -2,
        "Composure": -1
    },
    "hidden_effects": false,
    "conflicts_with": ["protect_innocent"],
    "auto_locks": [],
    "on_internalize_effects": [
        {
            "type": "set_flag",
            "target": "worldview_paranoid",
            "value": true
        },
        {
            "type": "modify_sanity",
            "value": -5
        }
    ],
    "unlocks": {
        "dialogue_options": ["confront_surveillance"],
        "scene_inserts": ["paranoid_observation"],
        "check_bonuses": { "Skepticism": 1 }
    },
    "lens_bias": "skeptic",
    "active_case": false,
    "critical_for_endgame": true,
    "degradation_rate": 15,
    "status": "available"
}
```

### Key Fields:
*   **requirements**: Conditions that must be met for the theory to become "available" (unlocked).
*   **effects**: Passive skill modifiers applied when the theory is active.
*   **conflicts_with**: List of theory IDs that cannot be held simultaneously.
*   **unlocks**: New content enabled by this theory (dialogue, scene inserts).
*   **lens_bias**: Influences the narrative lens (`skeptic`, `believer`, `haunted`, `neutral`).

### Step 2: Verify Loading
The `Board` class in `src/engine/board.py` automatically loads theories from `data/theories.json`. No code changes are required unless you're adding new effect types.

---

## 2. Scene File Format & Dynamic Inserts

Scenes are JSON files located in `data/scenes/`. They define the narrative, choices, and conditional text.

### Structure (`scene.schema.json`)
```json
{
  "id": "scene_hotel_lobby",
  "text": {
    "base": "The lobby is empty. Dust motes dance in the light.",
    "lens": {
      "believer": "The dust moves against the draft. Something is breathing here.",
      "skeptic": "Just an old building with poor ventilation.",
      "haunted": "You've waited in this lobby before. For hours."
    },
    "inserts": [
      {
        "id": "notice_blood",
        "condition": { "skill_gte": { "Forensics": 3 } },
        "text": "A faint copper smell hits you. Blood, recently cleaned.",
        "insert_at": "AFTER_BASE"
      }
    ]
  },
  "choices": [
    {
      "label": "Check the desk",
      "next_scene": "scene_hotel_desk"
    }
  ]
}
```

### Dynamic Inserts Logic
The `TextComposer` (`src/engine/text_composer.py`) assembles the final text.
1.  **Base Text**: The core objective description.
2.  **Lens Overlay**: Appended or integrated based on the player's archetype (Believer/Skeptic/Haunted).
3.  **Inserts**: Conditional text blocks injected at specific points.

**Insert Positions:**
*   `AFTER_BASE`: Immediately after the base text.
*   `AFTER_LENS`: After the lens-specific text.
*   `BEFORE_CHOICES`: At the very end of the narrative block.
*   `MID_PARAGRAPH`: (Advanced) Requires specific markers.
*   `AFTER_PARAGRAPH:n`: Inserted after the n-th paragraph (0-indexed).

**Conditions:**
*   `skill_gte`: `{"SkillName": Level}`
*   `flag_set`: `"flag_name"`
*   `theory_active`: `"theory_id"`
*   `trust_gte`: `{"npc_id": Level}`
*   `thermal_mode`: `true/false` (matches player thermal optics state)

---

## 3. Parser Hook Structure

The game supports text input for investigation.

### Input Flow
1.  **Normalization**: `CommandParser.normalize` (`src/engine/input_system.py`) splits input into `(VERB, TARGET)`.
2.  **Handling**: `Game.process_command` (`game.py`) routes the command.
3.  **Verb Execution**: `Game.handle_parser_command` executes logic (e.g., `EXAMINE`, `TAKE`).

### Adding a New Command
1.  **Define Verb**: Add synonyms to `CommandParser.verbs` in `src/engine/input_system.py`.
    ```python
    "DANCE": ["dance", "jig"]
    ```
2.  **Implement Handler**: Add a case in `Game.handle_parser_command` in `game.py`.
    ```python
    elif verb == "DANCE":
        self.print("You dance wildly. The Entity judges you.")
    ```

### Scene-Specific Triggers
Scenes can define special interactions via the generic `USE` or `EXAMINE` commands, or by checking flags in custom logic if you extend `SceneManager`. Currently, `parser_triggers` are not standard in the schema but can be simulated by `objects` with `interactions` in the scene data.

```json
"objects": {
  "strange_device": {
    "interactions": {
      "use": "You press the button. It hums."
    }
  }
}
```

---

## 4. Tagging Evidence & Linking Cases

Evidence is managed by the `InventoryManager` (`src/engine/inventory_system.py`) and `ClueSystem` (`src/engine/clue_system.py`).

### Defining Evidence (`data/evidence.json`)
```json
{
    "id": "bloody_shard",
    "name": "Bloody Glass Shard",
    "description": "Sharp. Dangerous.",
    "type": "physical",
    "location": "porch",
    "case_id": "murder_in_the_woods",
    "related_skills": ["Forensics"],
    "tags": ["blood", "violence"],
    "links_to_theories": [
        { "theory_id": "trust_no_one", "relation": "supports" }
    ]
}
```

### Linking to Cases/Theories
*   **Case ID**: The `case_id` field connects this piece of evidence to a broader investigative case (e.g., `"general"`, `"murder_in_the_woods"`).
*   **Theory Links**: `links_to_theories` explicitly connects evidence to specific board theories. When evidence is collected, `Board.add_evidence_to_theory` uses these links to update theory progress (Evidence Count vs. Contradictions).
*   **Tags**: Use generic tags (`blood`, `occult`) to group evidence for retrieval or passive checks.
