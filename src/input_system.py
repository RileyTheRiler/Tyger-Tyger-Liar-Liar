
import re

class InputMode:
    DIALOGUE = "DIALOGUE"
    INVESTIGATION = "INVESTIGATION"
    COMBAT = "COMBAT"

class CommandParser:
    def __init__(self):
        self.verbs = {
            "EXAMINE": ["examine", "look", "inspect", "see", "check", "study", "observe", "analyze", "x"],
            "TAKE": ["take", "grab", "pick up", "get", "seize", "collect"],
            "USE": ["use", "operate", "trigger", "activate", "shine", "turn on"],
            "ASK": ["ask", "interrogate", "question", "talk", "speak", "query"],
            "CONNECT": ["connect", "link", "tie", "match", "correlate", "compare"],
            "GO": ["go", "walk", "move", "run", "travel"],
            "SWITCH": ["switch"],
            "HELP": ["help", "?"],
            "INVENTORY": ["inventory", "inv", "i", "items", "bag", "pockets"]
        }
        
        # Reverse mapping for faster lookup
        self.verb_map = {}
        for canonical, synonyms in self.verbs.items():
            for syn in synonyms:
                self.verb_map[syn] = canonical

    def normalize(self, input_str):
        """
        Parses the input string into a (verb, target) tuple.
        Example: "look at the door" -> ("EXAMINE", "door")
        """
        clean_input = input_str.lower().strip()
        
        # Remove common articles/prepositions that might clutter parsing
        # (Very basic, can be improved)
        clean_input = re.sub(r'\b(at|to|the|a|an)\b', ' ', clean_input).strip()
        clean_input = re.sub(r'\s+', ' ', clean_input) # collapse spaces

        parts = clean_input.split(' ', 1)
        if not parts:
            return None, None
        
        verb_candidate = parts[0]
        target = parts[1] if len(parts) > 1 else None
        
        # Check for multi-word verbs (e.g. "pick up")
        # This is a bit tricky with split, but for now let's try exact matches of first word
        # Improvement: Check if the verb phrases exist in the start of the string
        
        # Let's try to find the longest matching verb synonym at the start
        best_verb = None
        best_len = 0
        
        for syn, canonical in self.verb_map.items():
            # Check if input starts with this synonym
            # We add a space to syn to ensure we don't match "use" in "useful" unless it's the whole word
            if clean_input == syn or clean_input.startswith(syn + " "):
                if len(syn) > best_len:
                    best_len = len(syn)
                    best_verb = canonical
                    
        if best_verb:
            # Extract target
            raw_target = clean_input[best_len:].strip()
            
            # Special case for standalone verbs (like "look" -> "EXAMINE", None)
            if not raw_target and best_verb == "EXAMINE":
                return "EXAMINE", None
                
            return best_verb, raw_target if raw_target else None

        return None, None
