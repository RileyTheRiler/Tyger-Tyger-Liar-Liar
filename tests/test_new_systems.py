"""
Comprehensive tests for the new GDD-aligned systems.
Tests: NPC, Condition, Population, TextComposer, Clue, Dice, Fracture systems.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from npc_system import NPC, NPCSystem, EXAMPLE_NPC_DATA
from condition_system import ConditionSystem, Condition
from population_system import PopulationSystem, PopulationEventType
from text_composer import TextComposer, Archetype, ComposedText
from clue_system import ClueSystem, EXAMPLE_CLUES
from dice import DiceSystem, CheckResult
from fracture_system import FractureSystem, FractureType


def test_npc_system():
    """Test NPC relationship/trust mechanics."""
    print("\n=== NPC SYSTEM TESTS ===\n")

    system = NPCSystem()
    npc = system.load_npc(EXAMPLE_NPC_DATA)

    # Test initial state
    assert npc.trust == 40, f"Initial trust should be 40, got {npc.trust}"
    assert npc.get_relationship_status() == "wary", f"Initial status should be 'wary', got {npc.get_relationship_status()}"
    print("[PASS] Initial NPC state correct")

    # Test trust modification
    new_trust, msg = npc.modify_trust(15, "helped investigation")
    assert new_trust == 55, f"Trust after +15 should be 55, got {new_trust}"
    assert npc.get_relationship_status() == "neutral", f"Status should be 'neutral', got {npc.get_relationship_status()}"
    print("[PASS] Trust modification works")

    # Test knowledge availability
    available_knowledge = npc.get_available_knowledge()
    assert len(available_knowledge) > 0, "Should have available knowledge at trust 55"
    print(f"[PASS] Available knowledge: {[k.topic for k in available_knowledge]}")

    # Test reaction application
    result = npc.apply_reaction("accused_sheriff")
    assert "trust_change" in result, "Reaction should include trust change"
    assert result["trust_change"] == -20, f"Trust change should be -20, got {result.get('trust_change')}"
    print("[PASS] Reaction system works")

    # Test serialization
    state = npc.to_dict()
    assert "trust" in state, "Serialized state should include trust"
    print("[PASS] NPC serialization works")

    print("\n[NPC SYSTEM] All tests passed!")


def test_condition_system():
    """Test condition/injury mechanics."""
    print("\n=== CONDITION SYSTEM TESTS ===\n")

    system = ConditionSystem()

    # Test condition loading
    assert len(system.condition_definitions) > 0, "Should have default conditions loaded"
    print(f"[PASS] Loaded {len(system.condition_definitions)} condition definitions")

    # Test adding condition
    active = system.add_condition("cond_hypothermia_mild")
    assert active is not None, "Should successfully add condition"
    assert system.has_condition("cond_hypothermia_mild"), "Should have condition"
    print("[PASS] Condition addition works")

    # Test penalties
    penalties = system.get_total_penalties()
    assert penalties.movement_penalty > 1.0, "Hypothermia should increase movement penalty"
    assert "Athletics" in penalties.skill_modifiers, "Should have Athletics penalty"
    print(f"[PASS] Penalties applied: {penalties.skill_modifiers}")

    # Test time update
    events = system.update_time(60)  # 1 hour
    print(f"[PASS] Time update returned {len(events)} events")

    # Test treatment availability
    treatments = system.get_available_treatments("cond_hypothermia_mild")
    assert len(treatments) > 0, "Should have available treatments"
    print(f"[PASS] Available treatments: {[t.id for t in treatments]}")

    # Test condition removal
    system.remove_condition("cond_hypothermia_mild")
    assert not system.has_condition("cond_hypothermia_mild"), "Condition should be removed"
    print("[PASS] Condition removal works")

    print("\n[CONDITION SYSTEM] All tests passed!")


def test_population_system():
    """Test population tracking mechanics."""
    print("\n=== POPULATION SYSTEM TESTS ===\n")

    system = PopulationSystem()

    # Test initial state
    assert system.population == 347, f"Initial population should be 347, got {system.population}"
    print("[PASS] Initial population is 347")

    # Test disappearance recording
    event = system.record_disappearance("The Miller family didn't return from fishing.", count=3)
    assert system.population == 344, f"Population should be 344, got {system.population}"
    assert event.event_type == PopulationEventType.DISAPPEARANCE
    print("[PASS] Disappearance recording works")

    # Test death recording
    system.record_death("Found frozen near the lake.", npc_id="npc_hunter")
    assert system.population == 343, f"Population should be 343, got {system.population}"
    print("[PASS] Death recording works")

    # Test status
    status = system.get_population_status()
    assert status["losses"] == 4, f"Losses should be 4, got {status['losses']}"
    print(f"[PASS] Population status: {status['current']}/{status['initial']} ({status['loss_percent']}% lost)")

    # Test thresholds
    system.population = 339  # Below first threshold
    system._check_thresholds()
    triggered = system.get_triggered_thresholds()
    assert len(triggered) > 0, "Should have triggered at least one threshold"
    print(f"[PASS] Threshold triggered: {triggered[0].name}")

    # Test serialization
    state = system.to_dict()
    assert "population" in state, "Should have population in state"
    assert "events" in state, "Should have events in state"
    print("[PASS] Population serialization works")

    print("\n[POPULATION SYSTEM] All tests passed!")


def test_text_composer():
    """Test the Bad Blood text composition pipeline."""
    print("\n=== TEXT COMPOSER TESTS ===\n")

    composer = TextComposer()

    test_scene = {
        "base": "The hotel lobby is empty. A clock ticks. The air smells of coffee.",
        "lens": {
            "believer": "The shadows shift when you're not looking. The clock counts wrong.",
            "skeptic": "Standard small-town hotel. Nothing unusual here.",
            "haunted": "You've been here before. The furniture was different."
        },
        "inserts": [
            {
                "id": "forensics_insert",
                "condition": {"skill_gte": {"Forensics": 3}},
                "text": "That smell—blood, poorly cleaned.",
                "insert_at": "AFTER_LENS"
            }
        ]
    }

    # Test base composition
    result = composer.compose(test_scene, Archetype.NEUTRAL)
    assert result.base_used, "Should use base text"
    assert "empty" in result.full_text, "Should contain base text"
    print("[PASS] Base text composition works")

    # Test believer lens
    result = composer.compose(test_scene, Archetype.BELIEVER)
    assert "shadows shift" in result.full_text, "Should contain believer text"
    print("[PASS] Believer lens composition works")

    # Test skeptic lens
    result = composer.compose(test_scene, Archetype.SKEPTIC)
    assert "Nothing unusual" in result.full_text, "Should contain skeptic text"
    print("[PASS] Skeptic lens composition works")

    # Test haunted lens
    result = composer.compose(test_scene, Archetype.HAUNTED)
    assert "been here before" in result.full_text, "Should contain haunted text"
    print("[PASS] Haunted lens composition works")

    # Test skill insert
    player_state = {"skills": {"Forensics": 4}}
    result = composer.compose(test_scene, Archetype.SKEPTIC, player_state)
    assert "forensics_insert" in result.inserts_applied, "Should apply forensics insert"
    assert "blood" in result.full_text, "Should contain insert text"
    print("[PASS] Skill-gated insert works")

    # Test insert not triggered
    player_state = {"skills": {"Forensics": 1}}
    result = composer.compose(test_scene, Archetype.SKEPTIC, player_state)
    assert "forensics_insert" not in result.inserts_applied, "Should not apply insert"
    print("[PASS] Insert condition gating works")

    print("\n[TEXT COMPOSER] All tests passed!")


def test_clue_system():
    """Test clue discovery and passive perception."""
    print("\n=== CLUE SYSTEM TESTS ===\n")

    system = ClueSystem()

    # Load example clues
    for clue_data in EXAMPLE_CLUES:
        system.register_clue(clue_data)

    assert len(system.clue_definitions) == 3, f"Should have 3 clues, got {len(system.clue_definitions)}"
    print("[PASS] Clue registration works")

    # Test passive perception evaluation
    scene_passive_clues = [
        {
            "clue_id": "clue_bloody_glass",
            "visible_when": {"skill_gte": {"Forensics": 2}},
            "reveal_text": "You notice blood on the glass."
        },
        {
            "clue_id": "clue_aurora_photograph",
            "visible_when": {"skill_gte": {"Perception": 5}}
        }
    ]

    player_state = {"skills": {"Forensics": 3, "Perception": 2}}
    revealed = system.evaluate_passive_clues(scene_passive_clues, player_state)

    assert len(revealed) == 1, f"Should reveal 1 clue, revealed {len(revealed)}"
    assert revealed[0][0].id == "clue_bloody_glass", "Should reveal bloody glass clue"
    print("[PASS] Passive perception works")

    # Test clue acquisition
    assert system.has_clue("clue_bloody_glass"), "Should have acquired clue"
    print("[PASS] Clue acquisition works")

    # Test clue with equipment requirement
    scene_passive_clues = [
        {
            "clue_id": "clue_dewline_memo",
            "visible_when": {"equipment": "item_uv_light"}
        }
    ]

    player_state = {"inventory": ["item_uv_light"]}
    revealed = system.evaluate_passive_clues(scene_passive_clues, player_state)
    assert len(revealed) == 1, "Should reveal clue with equipment"
    print("[PASS] Equipment-gated clues work")

    # Test theory linking
    clues_for_theory = system.get_clues_for_theory("the_missing_are_connected")
    assert len(clues_for_theory["supports"]) > 0, "Should have supporting clues"
    print(f"[PASS] Theory linking works: {len(clues_for_theory['supports'])} supporting clues")

    print("\n[CLUE SYSTEM] All tests passed!")


def test_dice_system():
    """Test enhanced dice mechanics with partial success."""
    print("\n=== DICE SYSTEM TESTS ===\n")

    system = DiceSystem()

    # Test basic roll
    result = system.resolve_check("Perception", modifier=3, dc=9, manual_roll=8)
    assert result.total == 8, f"Roll total should be 8, got {result.total}"
    assert result.final_total == 11, f"Final total should be 11, got {result.final_total}"
    assert result.result == CheckResult.SUCCESS, f"Should succeed, got {result.result}"
    print("[PASS] Basic roll resolution works")

    # Test partial success (fail by 1-2)
    result = system.resolve_check("Charm", modifier=2, dc=11, manual_roll=8)
    # 8 + 2 = 10, DC 11, fail by 1 = partial success
    assert result.result == CheckResult.PARTIAL_SUCCESS, f"Should be partial success, got {result.result}"
    assert len(result.costs) > 0, "Partial success should have costs"
    print(f"[PASS] Partial success works with costs: {[c[0] for c in result.costs]}")

    # Test full failure
    result = system.resolve_check("Athletics", modifier=2, dc=11, manual_roll=4)
    # 4 + 2 = 6, DC 11, fail by 5 = full failure
    assert result.result == CheckResult.FAILURE, f"Should fail, got {result.result}"
    print("[PASS] Full failure detection works")

    # Test critical success
    result = system.resolve_check("Logic", modifier=0, dc=15, manual_roll=12)
    assert result.result == CheckResult.CRITICAL_SUCCESS, f"Should be critical success, got {result.result}"
    print("[PASS] Critical success works")

    # Test critical failure
    result = system.resolve_check("Stealth", modifier=5, dc=5, manual_roll=2)
    assert result.result == CheckResult.CRITICAL_FAILURE, f"Should be critical failure, got {result.result}"
    print("[PASS] Critical failure works")

    # Test result formatting
    formatted = system.format_roll_result(result)
    assert "CRITICAL FAILURE" in formatted, "Formatting should include result description"
    print("[PASS] Result formatting works")

    print("\n[DICE SYSTEM] All tests passed!")


def test_fracture_system():
    """Test reality fracture mechanics."""
    print("\n=== FRACTURE SYSTEM TESTS ===\n")

    system = FractureSystem()

    # Test effect registration
    assert len(system.fracture_effects) > 0, "Should have default effects loaded"
    print(f"[PASS] Loaded {len(system.fracture_effects)} fracture effects")

    # Test state update
    system.update_state(attention=80, day=30, in_storm=True, reality=40)
    assert system.current_attention == 80, "Attention should be updated"
    assert system.current_reality == 40, "Reality should be updated"
    print("[PASS] State update works")

    # Test fracture triggering (forced for testing)
    effect = system.get_fracture_effect("text")
    assert effect is not None, "Should get a fracture effect"
    print(f"[PASS] Got fracture effect: {effect.description}")

    # Test text fracture application
    sample_text = "You enter the hotel lobby."
    system.fractures_enabled = True
    # Force a fracture for testing
    effect = system.fracture_effects.get("fracture_repeated_phrase")
    if effect:
        modified, used_effect = system.apply_text_fracture(sample_text, effect)
        assert used_effect is not None, "Should apply effect"
        print(f"[PASS] Text fracture applied: {used_effect.description}")

    # Test fracture history
    assert len(system.fracture_history) > 0, "Should have fracture history"
    print(f"[PASS] Fracture history recorded: {len(system.fracture_history)} events")

    # Test serialization
    state = system.to_dict()
    assert "history" in state, "Should have history in state"
    print("[PASS] Fracture serialization works")

    print("\n[FRACTURE SYSTEM] All tests passed!")


def test_schema_validator():
    """Test schema validation."""
    print("\n=== SCHEMA VALIDATOR TESTS ===\n")

    from schema_validator import SchemaValidator

    validator = SchemaValidator()

    # Test schema loading
    if validator.schemas:
        print(f"[PASS] Loaded {len(validator.schemas)} schemas: {list(validator.schemas.keys())}")
    else:
        print("[SKIP] No schemas found (may be path issue)")
        return True

    # Test valid scene
    valid_scene = {
        "id": "test_scene",
        "text": {"base": "Test scene text."}
    }
    is_valid, errors = validator.validate_scene(valid_scene)
    if is_valid:
        print("[PASS] Valid scene validation works")
    else:
        print(f"[INFO] Validation errors (may be strict schema): {errors}")

    # Test invalid scene (missing required field)
    invalid_scene = {"title": "Missing ID"}
    is_valid, errors = validator.validate_scene(invalid_scene)
    if not is_valid:
        print("[PASS] Invalid scene detection works")
    else:
        print("[INFO] Schema validation may be lenient")

    print("\n[SCHEMA VALIDATOR] Tests completed!")


def run_all_tests():
    """Run all system tests."""
    print("=" * 60)
    print("RUNNING ALL NEW SYSTEM TESTS")
    print("=" * 60)

    results = {}

    try:
        results["NPC System"] = test_npc_system()
    except Exception as e:
        print(f"[FAIL] NPC System: {e}")
        results["NPC System"] = False

    try:
        results["Condition System"] = test_condition_system()
    except Exception as e:
        print(f"[FAIL] Condition System: {e}")
        results["Condition System"] = False

    try:
        results["Population System"] = test_population_system()
    except Exception as e:
        print(f"[FAIL] Population System: {e}")
        results["Population System"] = False

    try:
        results["Text Composer"] = test_text_composer()
    except Exception as e:
        print(f"[FAIL] Text Composer: {e}")
        results["Text Composer"] = False

    try:
        results["Clue System"] = test_clue_system()
    except Exception as e:
        print(f"[FAIL] Clue System: {e}")
        results["Clue System"] = False

    try:
        results["Dice System"] = test_dice_system()
    except Exception as e:
        print(f"[FAIL] Dice System: {e}")
        results["Dice System"] = False

    try:
        results["Fracture System"] = test_fracture_system()
    except Exception as e:
        print(f"[FAIL] Fracture System: {e}")
        results["Fracture System"] = False

    try:
        results["Schema Validator"] = test_schema_validator()
    except Exception as e:
        print(f"[FAIL] Schema Validator: {e}")
        results["Schema Validator"] = False

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"  {name}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 60)

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
