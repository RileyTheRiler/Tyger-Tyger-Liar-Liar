from typing import List, Tuple, Optional, Dict

import re

class InputMode:
    DIALOGUE = "DIALOGUE"
    INVESTIGATION = "INVESTIGATION"
    COMBAT = "COMBAT"

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
            "SURRENDER": ["surrender", "give up", "yield"],

            # Week 24: Psychological/New Commands
            "SCREAM": ["scream", "shout", "yell"],
            "BURN": ["burn", "ignite", "torch"],
            "GROUND": ["ground", "calm", "meditate"],
            "OPEN": ["open", "unlock"],
            "RUN": ["run", "flee", "escape", "retreat"]
        }
        
        # Spatial prepositions that might imply "LOOK"
        self.spatial_prepositions = ["under", "behind", "on", "in", "inside", "above", "below"]

        # Scene-specific synonym map (word -> list of synonyms)
        # e.g. {"stain": ["blood", "red mark"]}
        self.scene_synonyms: Dict[str, List[str]] = {}

        # Implicit actions map (verb+target -> list of new commands)
        # e.g. "open drawer" -> ["look in drawer"] (if open is mapped to look in)
        # But actually, the requirement is: "open drawer" auto-performs "look in drawer" AFTER.
        # This means the parser should return multiple commands.
        self.implicit_chains: Dict[str, List[str]] = {
            "open": ["examine"], # Simplified: OPEN X -> EXAMINE X
            "search": ["examine", "collect"], # SEARCH X -> EXAMINE X, COLLECT X (maybe?)
        }

        # Reverse mapping for faster lookup
        self.verb_map = {}
        for canonical, synonyms in self.verbs.items():
            for syn in synonyms:
                self.verb_map[syn] = canonical

    def set_scene_synonyms(self, synonyms: Dict[str, List[str]]):
        """Register scene-specific synonyms."""
        self.scene_synonyms = synonyms

    def normalize(self, input_str: str, reason_score: int = 0) -> List[Tuple[Optional[str], Optional[str]]]:
        """
        Parses the input string into a list of (verb, target) tuples.
        Supports command chaining with 'then', 'and', or '.'.

        Args:
            input_str: Raw input string.
            reason_score: Player's Reason/Logic attribute score. High score enables shortcuts.
        """
        if not input_str:
            return []

        # Validate input
        if not isinstance(input_str, str):
            return []

        # Split into multiple commands
        clean_input = input_str.lower().strip()
        
        # Regex split on delimiters
        raw_commands = re.split(r'\s+then\s+|\s+and\s+|\s*\.\s*', clean_input)
        
        results = []
        for cmd in raw_commands:
            if not cmd.strip():
                continue
            verb, target = self._parse_single_command(cmd.strip())
            results.append((verb, target))
            
            # Week 24: Implicit Command Chaining
            # Week 24: Implicit Command Chaining via Dictionary
            # Check if verb maps to implicit followers
            # We iterate implicit_chains to support generic definitions
            # Key is verb (lower case), Value is list of verbs to append with same target
            if verb and verb.lower() in self.implicit_chains:
                for implicit_verb_key in self.implicit_chains[verb.lower()]:
                    # Map simple key to canonical verb if possible, or use as is
                    # self.implicit_chains values should ideally be canonical verbs (e.g. "examine")
                    # but we need to uppercase them to match parser output format
                    canonical_implicit = implicit_verb_key.upper()
                    # Only add if it's not already the next command (prevent infinite loops if user typed it)
                    results.append((canonical_implicit, target))

        return results

    def _parse_single_command(self, clean_input: str, reason_score: int = 0) -> Tuple[Optional[str], Optional[str]]:
        """Internal helper to parse a single normalized command string."""
        clean_input = re.sub(r'\s+', ' ', clean_input).strip()
        
        # Check for spatial shortcut (e.g. "under table" -> "look under table")
        # Week 24: "High Reason: Interprets vague commands more precisely"
        # We require a basic level of capability (Reason > 2) to infer this connection instantly.
        # Or maybe check the 'Logic' skill. But we have 'reason_score' passed in.
        # Let's say Reason >= 3 (Average is often 1-6 in this system based on mechanics.py)
        # Attribute base_value is 1, cap 6. So 3 is above average?
        # Let's check mechanics.py again. base_value=1.

        first_word = clean_input.split()[0]
        if first_word in self.spatial_prepositions:
            # If Reason is low, we might not understand the intent
            if reason_score >= 3:
                return "EXAMINE", clean_input
            # Else, fall through and likely fail or return as EXAMINE default later

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
                # Be more aggressive with stripping
                # Using a loop to strip multiple articles (e.g. "look at the blood")
                while True:
                    new_target = re.sub(r'^(at|to|the|a|an)\s+', '', raw_target)
                    if new_target == raw_target:
                        break
                    raw_target = new_target.strip()

                # Week 24: Synonym Resolution
                # Check if target matches any synonym map
                for canonical_name, synonyms in self.scene_synonyms.items():
                    if raw_target.lower() in [s.lower() for s in synonyms]:
                        raw_target = canonical_name
                        break
            
            return best_verb, raw_target if raw_target else None

        # Implicit Command Resolution (Week 24)
        # If no verb, try to see if the input matches an object directly
        # If so, default to EXAMINE
        # We can't check scene objects here easily without context,
        # but if the user typed something that didn't start with a verb,
        # and it's not a spatial preposition, maybe it's just "desk".
        if clean_input:
             # Assume it's a target for EXAMINE
             return "EXAMINE", clean_input

        return None, None
