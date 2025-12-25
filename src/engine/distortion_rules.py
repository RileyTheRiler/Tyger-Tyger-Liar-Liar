import random
import hashlib
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class DistortionRule(ABC):
    """Abstract base class for all distortion rules."""
    
    @abstractmethod
    def apply(self, text: str, intensity: float, seed: int) -> str:
        """
        Apply the distortion to the text.
        
        Args:
            text: The text to distort.
            intensity: A float from 0.0 to 1.0 representing stress/distortion level.
            seed: An integer seed for deterministic RNG.
            
        Returns:
            The distorted text.
        """
        pass

class WordSubstitutionRule(DistortionRule):
    """Replaces words with unsettling alternatives based on intensity."""
    
    def __init__(self):
        self.replacements = {
            "door": ["mouth", "barrier", "lid"],
            "window": ["eye", "lens", "hole"],
            "light": ["glare", "radiation", "burning gaze"],
            "shadow": ["void", "stain", "living darkness"],
            "tree": ["claw", "spire", "reaching limb"],
            "sky": ["lid", "abyss", "ceiling"],
            "wall": ["skin", "membrane", "barrier"],
            "floor": ["flesh", "ground", "depths"],
            "hope": ["delusion", "lie", "trap"],
            "memory": ["scar", "ghost", "tape"],
            "friend": ["stranger", "agent", "actor"],
            "enemy": ["truth", "reflection", "self"]
        }
        
    def apply(self, text: str, intensity: float, seed: int) -> str:
        if intensity < 0.2:
            return text
            
        rng = random.Random(seed)
        words = text.split()
        new_words = []
        
        # Chance to replace increases with intensity
        # Max chance at 1.0 intensity is 40%
        replace_chance = (intensity - 0.1) * 0.4
        
        for word in words:
            lower_word = word.lower().strip('.,!?')
            clean_word = word.strip('.,!?')
            suffix = word[len(clean_word):] if len(word) > len(clean_word) else ""
            prefix = word[:len(word)-len(clean_word)-len(suffix)] if len(word) > len(clean_word) else "" # Rough punct handling
            
            # Better punctuation handling
            import string
            prefix = ""
            suffix = ""
            while word and word[0] in string.punctuation:
                prefix += word[0]
                word = word[1:]
            while word and word[-1] in string.punctuation:
                suffix = word[-1] + suffix
                word = word[:-1]
                
            lower_word = word.lower()
            
            if lower_word in self.replacements and rng.random() < replace_chance:
                replacement = rng.choice(self.replacements[lower_word])
                if word.isupper():
                    replacement = replacement.upper()
                elif word and word[0].isupper():
                    replacement = replacement.capitalize()
                new_words.append(f"{prefix}{replacement}{suffix}")
            else:
                new_words.append(f"{prefix}{word}{suffix}")
                
        return " ".join(new_words)

class SentenceFragmentationRule(DistortionRule):
    """Breaks sentences into fragments or repeats them."""
    
    def apply(self, text: str, intensity: float, seed: int) -> str:
        if intensity < 0.4:
            return text
            
        rng = random.Random(seed + 1) # Different seed offset
        
        # Max chance 30%
        frag_chance = (intensity - 0.3) * 0.3
        
        if rng.random() > frag_chance:
            return text
            
        sentences = text.split(". ")
        new_sentences = []
        
        for sent in sentences:
            if rng.random() < 0.3:
                # Fragment
                words = sent.split()
                if len(words) > 3:
                    cut = rng.randint(1, len(words)-1)
                    new_sentences.append(" ".join(words[:cut]) + "...")
                else:
                    new_sentences.append(sent)
            else:
                new_sentences.append(sent)
                
        return ". ".join(new_sentences)

class RepetitionRule(DistortionRule):
    """Repeats words or phrases obsessively."""
    
    def apply(self, text: str, intensity: float, seed: int) -> str:
        if intensity < 0.6:
            return text
            
        rng = random.Random(seed + 2)
        repeat_chance = (intensity - 0.5) * 0.2 # Max 20%
        
        if rng.random() > repeat_chance:
            return text
            
        words = text.split()
        if not words:
            return text
            
        # Choose a word to obsessive over
        target_idx = rng.randint(0, len(words)-1)
        target_word = words[target_idx]
        
        # Insert it elsewhere
        insert_idx = rng.randint(0, len(words))
        words.insert(insert_idx, f"{target_word}.")
        words.insert(insert_idx, f"{target_word}")
        
        return " ".join(words)

class RedactionRule(DistortionRule):
    """Redacts text blocks."""
    
    def apply(self, text: str, intensity: float, seed: int) -> str:
        if intensity < 0.8:
            return text
            
        rng = random.Random(seed + 3)
        redact_chance = (intensity - 0.7) * 0.5 # Max 50% chance at very high stress
        
        sentences = text.split(". ")
        new_sentences = []
        
        for sent in sentences:
            if rng.random() < redact_chance:
                 new_sentences.append("█" * len(sent))
            else:
                 new_sentences.append(sent)
                 
        return ". ".join(new_sentences)
        
class HallucinationInsertRule(DistortionRule):
    """Inserts hallucinated sentences."""
    
    def __init__(self):
        self.hallucinations = [
            "THEY ARE WATCHING YOU.",
            "IT IS INSIDE THE WALLS.",
            "DON'T TRUST THE MIRROR.",
            "YOU ARE NOT ALONE.",
            "THE BLUE FLUID IS HUNGRY.",
            "WAKE UP.",
            "THIS IS NOT REAL."
        ]
        
    def apply(self, text: str, intensity: float, seed: int) -> str:
         if intensity < 0.5:
             return text
             
         rng = random.Random(seed + 4)
         
         # Chance scales
         chance = (intensity - 0.4) * 0.25
         
         if rng.random() < chance:
             insert = rng.choice(self.hallucinations)
             # Try to insert between sentences
             sentences = text.split(". ")
             if len(sentences) > 1:
                 idx = rng.randint(0, len(sentences)-1)
                 sentences.insert(idx, insert)
                 return ". ".join(sentences)
             else:
                 return text + " " + insert
         
         return text


class DistortionManager:
    """Manages the application of distortion rules based on game state."""
    
    def __init__(self):
        self.rules: List[DistortionRule] = [
            WordSubstitutionRule(),
            SentenceFragmentationRule(),
            RepetitionRule(),
            RedactionRule(),
            HallucinationInsertRule()
        ]
        
    def generate_seed(self, text: str, game_state: Dict[str, Any]) -> int:
        """Generate a deterministic seed based on text content and game time/state."""
        # Use text hash + game time to ensure same text looks different at different times
        # but same text at same time looks same (idempotent for redraws)
        
        text_hash = int(hashlib.md5(text.encode('utf-8')).hexdigest(), 16)
        
        # Try to get time from game state
        time_val = 0
        if "time" in game_state:
             # If it's the TimeSystem object or similar
             ts = game_state["time"]
             if hasattr(ts, "current_time"):
                 time_val = ts.current_time
             elif isinstance(ts, int):
                 time_val = ts
                 
        # Also mix in sanity to ensure shift when sanity changes even if time doesn't
        sanity = game_state.get("sanity", 100)
        
        return text_hash + time_val + int(sanity)

    def calculate_distortion_intensity(self, game_state: Dict[str, Any]) -> float:
        """
        Calculate global distortion intensity (0.0 to 1.0).
        Based on Sanity (low = high distortion) and Reality (low = high distortion).
        """
        sanity = game_state.get("sanity", 100)
        reality = game_state.get("reality", 100)
        
        # Normalize to 0-1 (100 -> 0, 0 -> 1)
        sanity_factor = max(0, (100 - sanity) / 100.0)
        reality_factor = max(0, (100 - reality) / 100.0)
        
        # Use the maximum stressor
        base_intensity = max(sanity_factor, reality_factor)
        
        # Boost if fear level is high (if Week 15 psych state exists)
        psych_state = game_state.get("psychological_state") 
        # Note: game_state passed here might be the flat player_state dict or the full game object get_game_state()
        # Let's assume it's a dict that might contain 'fear_level'
        fear = game_state.get("fear_level", 0)
        fear_factor = min(1.0, fear / 100.0) * 0.3 # adds up to 0.3
        
        final_intensity = min(1.0, base_intensity + fear_factor)
        return final_intensity

    def apply_distortions(self, text: str, game_state: Dict[str, Any]) -> str:
        """
        Apply all active distortion rules to the text.
        """
        intensity = self.calculate_distortion_intensity(game_state)
        
        # If no stress, return fast
        if intensity <= 0.05:
            return text
            
        seed = self.generate_seed(text, game_state)
        
        current_text = text
        for i, rule in enumerate(self.rules):
            # Pass a modified seed to each rule so they don't sync up weirdly
            rule_seed = seed + i * 1000
            current_text = rule.apply(current_text, intensity, rule_seed)
            
        return current_text
