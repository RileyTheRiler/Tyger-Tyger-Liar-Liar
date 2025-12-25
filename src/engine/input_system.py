
import re
from typing import List, Tuple, Optional, Dict
from typing import List, Tuple, Optional

class InputMode:
    DIALOGUE = "DIALOGUE"
    INVESTIGATION = "INVESTIGATION"

class CommandParser:
    def __init__(self, parser_memory=None):
        self.parser_memory = parser_memory
        self.verbs = {
            "EXAMINE": ["examine", "look", "inspect", "see", "check", "study", "observe", "analyze", "x"],
            "TAKE": ["take", "grab", "pick up", "get", "seize", "collect", "bag", "gather", "pickup"],
            "USE": ["use", "operate", "trigger", "activate", "shine", "turn on"],
            "ASK": ["ask", "interrogate", "question", "talk", "speak", "query"],
            "CONNECT": ["connect", "link", "tie", "match", "correlate", "compare"],
            "GO": ["go", "walk", "move", "travel"],
            "SWITCH": ["switch"],
            "HELP": ["help", "?"],
            "INVENTORY": ["inventory", "inv", "i", "items", "pockets"],
            "SEARCH": ["search", "scan", "look around", "survey"],
            "PHOTOGRAPH": ["photograph", "photo", "snap", "pic", "capture"],
            "EQUIP": ["equip", "wear", "hold", "draw", "wield"],
            "UNEQUIP": ["unequip", "remove", "stow", "sheathe", "holster"],
            "ANALYZE": ["analyze", "study", "research", "test", "investigate"],
            "COMBINE": ["combine", "merge", "mix", "use with"],
            
            # Week 13: Combat Commands
            "FIGHT": ["fight", "attack", "strike", "hit", "shoot"],
            "DODGE": ["dodge", "evade", "duck", "weave"],
            "FLEE": ["flee", "run", "escape", "retreat"],
            "INTIMIDATE": ["intimidate", "threaten", "menace"],
            "REASON": ["reason", "persuade", "convince", "negotiate"],
            
            # Week 13: Injury Commands
            "INJURIES": ["injuries", "wounds", "damage", "health"],
            "TREAT": ["treat", "heal", "bandage", "medicate"],
            "REST": ["rest", "sleep", "recover"],
            
            # Week 13: Chase Commands
            "SPRINT": ["sprint", "dash", "bolt"],
            "VAULT": ["vault", "jump", "leap", "climb"],
            "HIDE": ["hide", "conceal", "duck"],
            "SURRENDER": ["surrender", "give up", "yield"]
        }
        
        # Reverse mapping for faster lookup
        self.verb_map = {}
        for canonical, synonyms in self.verbs.items():
            for syn in synonyms:
                self.verb_map[syn] = canonical

    def set_memory(self, parser_memory):
        """Inject parser memory after initialization if needed."""
        self.parser_memory = parser_memory

    def normalize(self, input_str: str) -> List[Tuple[Optional[str], Optional[str]]]:
        """
        Parses the input string into a list of (verb, target) tuples.
        Supports command chaining with 'then', 'and', or '.'.
        """
        if not input_str:
            return []

        # Validate input
        if not isinstance(input_str, str):
            return []

        # Log to memory if available
        if self.parser_memory:
            self.parser_memory.add_command(input_str)

        # Split into multiple commands
        # We need to be careful not to split inside a target if "and" is part of the name
        # But for now, we assume explicit delimiters.
        # Clean: "look at desk then take book" -> ["look at desk", "take book"]
        clean_input = input_str.lower().strip()
        
        # Regex split on delimiters
        raw_commands = re.split(r'\s+then\s+|\s+and\s+|\s*\.\s*', clean_input)
        
        results = []
        for cmd in raw_commands:
            if not cmd.strip():
                continue
            verb, target = self._parse_single_command(cmd.strip())
            results.append((verb, target))
            
        return results

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculates Levenshtein distance between two strings."""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def _fuzzy_match_verb(self, input_word: str) -> Tuple[Optional[str], float]:
        """
        Attempts to find a matching verb using fuzzy string matching.
        Returns (canonical_verb, score) where score is similarity (0-1).
        """
        best_verb = None
        best_dist = float('inf')
        input_len = len(input_word)

        if input_len < 3: # Don't fuzzy match very short words
            return None, 0.0

        for syn, canonical in self.verb_map.items():
            dist = self._levenshtein_distance(input_word, syn)
            if dist < best_dist:
                best_dist = dist
                best_verb = canonical

        # Calculate similarity score
        # Using a simple cutoff: allow 1 error for length 3-4, 2 for 5+
        max_allowed = 1 if input_len <= 4 else 2

        # Frequency Bonus (Learning)
        freq_bonus = 0.0
        if self.parser_memory:
             # Check exact input word frequency
             freq = self.parser_memory.get_keyword_frequency(input_word)
             if freq > 2:
                 freq_bonus = 0.5 # Allow slightly more errors for frequent words
                 max_allowed += 1

        if best_dist <= max_allowed:
            return best_verb, 1.0 - (best_dist / max(input_len, 1)) + freq_bonus

        return None, 0.0

    def _parse_single_command(self, clean_input: str) -> Tuple[Optional[str], Optional[str]]:
        """Internal helper to parse a single normalized command string."""
        clean_input = re.sub(r'\s+', ' ', clean_input).strip()
        
        # Verb matching (Exact)
        best_verb = None
        best_len = 0
        
        # 1. Try exact matching first (existing logic)
        for syn, canonical in self.verb_map.items():
            # Check for exact match or start of string
            if clean_input == syn or clean_input.startswith(syn + " "):
                if len(syn) > best_len:
                    best_len = len(syn)
                    best_verb = canonical
                    
        if best_verb:
            # Extract target
            raw_target = clean_input[best_len:].strip()
            return self._finalize_command(best_verb, raw_target)

        # 2. Try fuzzy matching on the first word
        parts = clean_input.split(maxsplit=1)
        first_word = parts[0]

        fuzzy_verb, score = self._fuzzy_match_verb(first_word)
        if fuzzy_verb:
            raw_target = parts[1] if len(parts) > 1 else ""
            return self._finalize_command(fuzzy_verb, raw_target)

        # 3. If no verb found, return input as target for dynamic inference
        return None, clean_input

    def _finalize_command(self, verb: str, raw_target: str) -> Tuple[Optional[str], Optional[str]]:
        """Cleans up the target and returns the final tuple."""
        # Remove "at", "to", "the", "a", "an" from the START of the target
        if raw_target:
            raw_target = re.sub(r'^(at|to|the|a|an)\s+', '', raw_target).strip()

        return verb, raw_target if raw_target else None
