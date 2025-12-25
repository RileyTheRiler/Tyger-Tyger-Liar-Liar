
import unittest
from src.encounter_runner import EncounterRunner
from src.mechanics import SkillSystem
from src.dice import DiceSystem

class MockSkillSystem:
    def __init__(self):
        self.skills = {"Reflexes": 0, "Composure": 0}
        self.last_check_result = True

    def get_skill_total(self, skill):
        return 0

    def roll_check(self, skill, dc, manual_roll=None):
        return {"success": self.last_check_result, "total": dc + 1}

    def add_xp(self, amount):
        pass

class TestEncounterRunner(unittest.TestCase):
    def setUp(self):
        self.player_state = {"sanity": 100, "reality": 100}
        self.skill_system = MockSkillSystem()
        self.dice_system = DiceSystem()
        self.runner = EncounterRunner(self.player_state, self.skill_system, self.dice_system)

        self.encounter_data = {
            "id": "test_enc",
            "name": "Test Beast",
            "description": "A scary beast.",
            "initial_threat": 5,
            "initiative_score": 0,
            "actions": {
                "ATTACK": {
                    "skill": "Combat",
                    "difficulty": 10,
                    "success_effect": {"threat_damage": 2, "message": "Hit!"},
                    "fail_effect": {"message": "Miss!"}
                },
                "RUN": {
                    "skill": "Athletics",
                    "difficulty": 10,
                    "success_effect": {"escape": True, "message": "Escaped!"}
                }
            },
            "entity_moves": [
                {
                    "threshold": 0,
                    "message": "It growls.",
                    "effects": {"sanity": -1}
                }
            ]
        }
        self.runner.load_encounter(self.encounter_data)

    def test_initialization(self):
        self.assertEqual(self.runner.state.threat_level, 5)
        self.assertEqual(self.runner.active_encounter["name"], "Test Beast")

    def test_player_attack_success(self):
        self.skill_system.last_check_result = True
        result = self.runner.process_turn("ATTACK")

        self.assertIn("Hit!", result["messages"][0])
        self.assertEqual(self.runner.state.threat_level, 3) # 5 - 2

    def test_player_run_success(self):
        self.skill_system.last_check_result = True
        result = self.runner.process_turn("RUN")

        self.assertEqual(result["status"], "ended")
        self.assertEqual(result["result"], "escaped")

    def test_entity_reaction(self):
        self.skill_system.last_check_result = False # Fail attack so entity acts
        result = self.runner.process_turn("ATTACK")

        self.assertIn("It growls.", result["messages"][1])
        self.assertEqual(self.player_state["sanity"], 99) # 100 - 1

if __name__ == '__main__':
    unittest.main()
