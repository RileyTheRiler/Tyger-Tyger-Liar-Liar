import sys
import os
import unittest

# Ensure src is in path
sys.path.append(os.path.abspath("src"))

from engine.input_system import CommandParser

class TestWeek9Parser(unittest.TestCase):
    def setUp(self):
        self.parser = CommandParser()

    def test_basic_normalization(self):
        # Existing functionality
        self.assertEqual(self.parser.normalize("look at desk")[0], ("EXAMINE", "desk"))
        self.assertEqual(self.parser.normalize("take the book")[0], ("TAKE", "book"))


    def test_command_chaining_then(self):
        # "look at desk then take book"
        input_str = "look at desk then take book"
        results = self.parser.normalize(input_str)
        print(f"DEBUG: 'look at desk then take book' -> {results}")
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], ("EXAMINE", "desk"))
        self.assertEqual(results[1], ("TAKE", "book"))

    def test_command_chaining_and(self):
        input_str = "use key and go north"
        results = self.parser.normalize(input_str)
        print(f"DEBUG: 'use key and go north' -> {results}")
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], ("USE", "key"))
        self.assertEqual(results[1], ("GO", "north"))

    def test_command_chaining_period(self):
        input_str = "examine body. search room"
        results = self.parser.normalize(input_str)
        print(f"DEBUG: 'examine body. search room' -> {results}")
        # search room now triggers implicit commands (EXAMINE, COLLECT)
        # So we expect more than 2 results.
        # Original test expected exact match, but logic changed.
        self.assertTrue(len(results) >= 2)
        self.assertEqual(results[0], ("EXAMINE", "body"))
        self.assertEqual(results[1], ("SEARCH", "room"))

    def test_subcommand_use_on(self):
        input_str = "use camera on blood"
        results = self.parser.normalize(input_str)
        print(f"DEBUG: 'use camera on blood' -> {results}")
        self.assertEqual(results[0], ("USE", "camera on blood"))

    def test_subcommand_talk_to(self):
        input_str = "talk to priest"
        results = self.parser.normalize(input_str)
        print(f"DEBUG: 'talk to priest' -> {results}")
        verb, target = results[0]
        self.assertIn(verb, ["ASK", "TALK"])
        self.assertEqual(target, "priest")

if __name__ == '__main__':
    unittest.main()
