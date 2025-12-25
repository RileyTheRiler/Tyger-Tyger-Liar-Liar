
import re
from typing import List, Tuple, Optional

class InputMode:
    DIALOGUE = "DIALOGUE"
    INVESTIGATION = "INVESTIGATION"

class CommandParser:
    def __init__(self):
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

    def _parse_single_command(self, clean_input: str) -> Tuple[Optional[str], Optional[str]]:
        """Internal helper to parse a single normalized command string."""
        clean_input = re.sub(r'\s+', ' ', clean_input).strip()
        
        # Verb matching
        best_verb = None
        best_len = 0
        
        for syn, canonical in self.verb_map.items():
            # Check for exact match or start of string
            # IMPORTANT: Ensure that we match whole words for short verbs like "go" vs "golf"
            if clean_input == syn or clean_input.startswith(syn + " "):
                if len(syn) > best_len:
                    best_len = len(syn)
                    best_verb = canonical
                    
        if best_verb:
            # Extract target
            raw_target = clean_input[best_len:].strip()
            
            # Remove "at", "to", "the", "a", "an" from the START of the target
            # But NOT if the verb is USE (we need "on") or TALK (we usually strip "to" anyway)
            if raw_target:
                raw_target = re.sub(r'^(at|to|the|a|an)\s+', '', raw_target).strip()
            
            return best_verb, raw_target if raw_target else None

        return None, None
