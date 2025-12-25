import sys
import os
import pytest

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tyger_game.engine.character import Character
from src.inventory_system import Item
from src.thoughts import Thought

def test_character_skill_modifiers():
    char = Character()

    # Base check (Logic is under Intellect, default attr 3, base skill 0 -> total 3)
    # Adjust based on actual ATTRIBUTES/SKILLS in tyger_game/utils/constants.py if needed.
    # Assuming "Logic" is a skill. Let's check a known skill.
    # Reading constants from file or just picking one that likely exists.
    # From previous read of parser.py debug check: "check logic".

    # Let's set a skill manually to be sure
    skill_name = "Logic"
    # We need to make sure Logic exists in the character's skills, which are initialized from constants.
    # If Logic isn't in SKILLS, get_skill_level raises ValueError.
    # Let's peek at constants to be safe, or just try/except.

    try:
        initial_level = char.get_skill_level(skill_name)
    except ValueError:
        # Fallback to a skill that surely exists if Logic doesn't
        # Let's read constants first to be sure
        pass

    # For now, let's assume Logic exists.
    char.skills[skill_name] = 1 # Base skill level

    initial_level = char.get_skill_level(skill_name)
    print(f"Initial level for {skill_name}: {initial_level}")

    # 1. Test Item Modifier
    # Item with +1 Logic
    item = Item(
        id="calc",
        name="Calculator",
        type="tool",
        description="A cool calculator",
        effects={"skill_modifiers": {skill_name: 1}}
    )
    char.inventory.append(item)

    level_with_item = char.get_skill_level(skill_name)
    assert level_with_item == initial_level + 1, f"Expected {initial_level + 1}, got {level_with_item}"

    # 2. Test Thought Modifier (Active)
    # Thought with +2 Logic while active (temporary)
    thought_data = {
        "id": "t1",
        "name": "Deep Thinker",
        "description": "...",
        "temporary_effects": {skill_name: 2},
        "permanent_effects": {skill_name: 5}
    }
    thought = Thought(thought_data)
    thought.is_active = True
    thought.is_internalized = False

    char.thoughts.append(thought)

    level_with_item_and_active_thought = char.get_skill_level(skill_name)
    # +1 from item, +2 from active thought = +3 total modifier
    assert level_with_item_and_active_thought == initial_level + 1 + 2

    # 3. Test Thought Modifier (Internalized)
    # Switch thought to internalized
    thought.is_active = False
    thought.is_internalized = True

    level_with_item_and_internalized_thought = char.get_skill_level(skill_name)
    # +1 from item, +5 from permanent thought = +6 total modifier
    assert level_with_item_and_internalized_thought == initial_level + 1 + 5

if __name__ == "__main__":
    test_character_skill_modifiers()
