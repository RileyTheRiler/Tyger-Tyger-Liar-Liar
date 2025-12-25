
import pytest
import sys
import os

# Ensure src and its subdirectories are in path
sys.path.append(os.path.abspath("src"))
sys.path.append(os.path.abspath("src/engine"))

from engine.parser_hallucination import ParserHallucinationEngine

class TestParserHallucination:
    def test_initialization(self):
        engine = ParserHallucinationEngine()
        assert len(engine.ghost_verbs) > 0

    def test_check_hallucination_trigger(self):
        engine = ParserHallucinationEngine()
        # Should return boolean
        result = engine.check_hallucination_trigger(0)
        assert isinstance(result, bool)

    def test_generate_ghost_commands(self):
        engine = ParserHallucinationEngine()
        cmds = engine.generate_ghost_commands(2)
        assert len(cmds) == 2
        assert all(cmd in engine.ghost_verbs for cmd in cmds)

    def test_intercept_command(self):
        engine = ParserHallucinationEngine()
        # LOOK has defined overrides
        result = engine.intercept_command("LOOK", "wall")
        # Since it returns random choice, just check it returns a string
        assert isinstance(result, str)
        assert len(result) > 0

        # Unknown verb should return None
        assert engine.intercept_command("XYZ", "wall") is None

    def test_get_hallucinated_choices(self):
        engine = ParserHallucinationEngine()
        base_choices = [{"text": "real choice"}]
        fake = engine.get_hallucinated_choices(base_choices)
        assert len(fake) > 0
        assert fake[0]["type"] == "hallucination"
