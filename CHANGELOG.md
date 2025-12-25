# Changelog

## [1.1.0] - Week 30: Game-Wide Systems Integration

### Added
- **Core Loop Integration**:
    - Instantiated `ClueSystem` and `FractureSystem` in `game.py`.
    - Integrated `NPCSystem`, `PopulationSystem`, `ClueSystem`, and `FractureSystem` into the main runtime loop.
- **Save/Load System**:
    - Enhanced `save_game` to persist state for all major subsystems (`npc_system`, `population_system`, `clue_system`, `fracture_system`).
    - Enhanced `load_game` to restore full world state.
    - Added versioning to save files (v1.1).
- **Debug Harness**:
    - Added new debug commands:
        - `setskill <skill> <value>`: Directly modify skill levels.
        - `give <item_id>`: Add items to inventory.
        - `toggletheory <theory_id>`: Unlock/activate/lock theories.
        - `trigger <event_id>`: Manually trigger events/flags.
        - `record <filename>`: Start recording inputs to a log file.
        - `playback <filename>`: Execute inputs from a log file.
    - Refactored debug command processing into `process_debug_command`.

### Changed
- **Game Architecture**:
    - `Game` class now properly initializes all systems on startup.
    - `run` loop refactored to support replay playback mode.
- **System Improvements**:
    - `SkillSystem`: Added `set_skill_value` for debug manipulation.
    - `Board`: Added `to_dict` serialization method.
    - `InventorySystem`: Fixed `Item` serialization/deserialization to handle dynamic attributes like `temperature`.
    - `Player State`: Improved serialization for `Enum` (Archetype) and `set` types.

### Fixed
- Fixed missing `run` method in `game.py`.
- Fixed type errors in `input_system.py`.
- Fixed data loading issue in `clue_system.py`.
- Fixed multiple serialization bugs preventing save/load of complex objects.
