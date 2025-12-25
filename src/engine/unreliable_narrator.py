"""
Unreliable Narrator System - Week 15
Handles hallucinations, false choices, and competing internal voices.
"""

import json
import os
import random
from typing import Dict, List, Optional, Tuple


class HallucinationEngine:
    """Manages hallucinated content injection based on psychological state."""
    
    def __init__(self):
        """Initialize the hallucination engine."""
        self.visual_hallucinations = []
        self.auditory_hallucinations = []
        self.memory_drifts = []
        self.competing_voices = {}
    
    def load_hallucination_templates(self, directory_path: str):
        """
        Load hallucination templates from JSON files.
        
        Args:
            directory_path: Path to hallucinations directory
        """
        if not os.path.exists(directory_path):
            print(f"[HallucinationEngine] Warning: Hallucinations directory not found: {directory_path}")
            return
        
        # Load visual hallucinations
        visual_path = os.path.join(directory_path, "visual.json")
        if os.path.exists(visual_path):
            with open(visual_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.visual_hallucinations = data.get("hallucinations", [])
                print(f"[HallucinationEngine] Loaded {len(self.visual_hallucinations)} visual hallucinations")
        
        # Load auditory hallucinations
        auditory_path = os.path.join(directory_path, "auditory.json")
        if os.path.exists(auditory_path):
            with open(auditory_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.auditory_hallucinations = data.get("hallucinations", [])
                print(f"[HallucinationEngine] Loaded {len(self.auditory_hallucinations)} auditory hallucinations")
        
        # Load memory drifts
        memory_path = os.path.join(directory_path, "memory_drift.json")
        if os.path.exists(memory_path):
            with open(memory_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.memory_drifts = data.get("drifts", [])
                print(f"[HallucinationEngine] Loaded {len(self.memory_drifts)} memory drifts")
    
    def get_visual_hallucination(self, sanity_tier: int, context: str = "") -> Optional[str]:
        """
        Get a visual hallucination appropriate for the sanity tier.
        
        Args:
            sanity_tier: Current sanity tier (0-4)
            context: Optional context to filter hallucinations
            
        Returns:
            Hallucination text or None
        """
        if sanity_tier > 1:  # Only trigger for sanity < 25
            return None
        
        # Filter by tier
        candidates = [
            h for h in self.visual_hallucinations
            if h.get("min_tier", 0) <= sanity_tier <= h.get("max_tier", 4)
        ]
        
        # Filter by context if provided
        if context:
            context_matches = [h for h in candidates if context.lower() in h.get("contexts", [])]
            if context_matches:
                candidates = context_matches
        
        if candidates:
            hallucination = random.choice(candidates)
            return hallucination.get("text", "")
        
        return None
    
    def get_auditory_hallucination(self, sanity_tier: int, context: str = "") -> Optional[str]:
        """
        Get an auditory hallucination appropriate for the sanity tier.
        
        Args:
            sanity_tier: Current sanity tier (0-4)
            context: Optional context to filter hallucinations
            
        Returns:
            Hallucination text or None
        """
        if sanity_tier > 2:  # Only trigger for sanity < 50
            return None
        
        # Filter by tier
        candidates = [
            h for h in self.auditory_hallucinations
            if h.get("min_tier", 0) <= sanity_tier <= h.get("max_tier", 4)
        ]
        
        # Filter by context if provided
        if context:
            context_matches = [h for h in candidates if context.lower() in h.get("contexts", [])]
            if context_matches:
                candidates = context_matches
        
        if candidates:
            hallucination = random.choice(candidates)
            return hallucination.get("text", "")
        
        return None
    
    def inject_false_choice(self, choices: List[Dict], sanity_tier: int, instability: bool) -> List[Dict]:
        """
        Inject hallucinated false choices into the choice list.
        
        Args:
            choices: Original choice list
            sanity_tier: Current sanity tier
            instability: Whether player is unstable
            
        Returns:
            Modified choice list with potential false choices
        """
        if sanity_tier > 1 and not instability:
            return choices  # No false choices for sanity >= 25 and stable
        
        # Determine how many false choices to add
        if sanity_tier == 0:
            num_false = random.randint(1, 3)
        elif sanity_tier == 1:
            num_false = random.randint(0, 2)
        elif instability:
            num_false = random.randint(0, 1)
        else:
            return choices
        
        false_choices = [
            {
                "text": "Whistle at the aurora",
                "next": None,
                "hallucinated": True,
                "effect": "You try to whistle, but no sound comes out. It was never an option."
            },
            {
                "text": "Trust the voice in the static",
                "next": None,
                "hallucinated": True,
                "effect": "The voice fades as you reach for it. There was no voice."
            },
            {
                "text": "Follow the shadow figure",
                "next": None,
                "hallucinated": True,
                "effect": "You blink and the figure is gone. It was never there."
            },
            {
                "text": "Drink the blue fluid",
                "next": None,
                "hallucinated": True,
                "effect": "Your hand passes through empty air. There is no fluid here."
            },
            {
                "text": "Answer the phone that isn't ringing",
                "next": None,
                "hallucinated": True,
                "effect": "Silence. The phone never rang."
            }
        ]
        
        # Add random false choices
        modified_choices = choices.copy()
        for _ in range(min(num_false, len(false_choices))):
            if false_choices:
                false_choice = random.choice(false_choices)
                false_choices.remove(false_choice)
                # Insert at random position
                insert_pos = random.randint(0, len(modified_choices))
                modified_choices.insert(insert_pos, false_choice)
        
        return modified_choices
    
    def get_competing_voices(self, text: str, sanity_tier: int, instability: bool) -> List[Dict]:
        """
        Generate competing internal voice commentary.
        
        Args:
            text: The narrative text being presented
            sanity_tier: Current sanity tier
            instability: Whether player is unstable
            
        Returns:
            List of voice interjections
        """
        if not instability and sanity_tier > 1:
            return []
        
        voices = []
        
        # Reason vs Instinct conflict
        if "evidence" in text.lower() or "clue" in text.lower():
            if random.random() < 0.3:
                voices.append({
                    "skill": "Reason",
                    "text": "This doesn't add up. Something is wrong with the logic."
                })
                voices.append({
                    "skill": "Instinct",
                    "text": "Stop overthinking. Trust your gut."
                })
        
        # Paranoia interjections
        if sanity_tier <= 1 and random.random() < 0.4:
            paranoid_thoughts = [
                "They're watching you through the walls.",
                "This is a trap. Everything is a trap.",
                "You can't trust your own memories anymore.",
                "The Entity knows you're here.",
                "Your thoughts aren't your own."
            ]
            voices.append({
                "skill": "Paranoia",
                "text": random.choice(paranoid_thoughts)
            })
        
        # Subconscious warnings
        if instability and random.random() < 0.25:
            subconscious_warnings = [
                "You've seen this before. In the dream that wasn't a dream.",
                "This moment has already happened. Or will happen. Time is wrong here.",
                "You're forgetting something important. Something vital.",
                "The blue fluid remembers what you've forgotten."
            ]
            voices.append({
                "skill": "Subconscious",
                "text": random.choice(subconscious_warnings)
            })
        
        return voices
    
    def apply_unreliable_feedback(self, feedback: str, success: bool, sanity_tier: int) -> str:
        """
        Potentially modify feedback to be unreliable.
        
        Args:
            feedback: Original feedback text
            success: Whether the check actually succeeded
            sanity_tier: Current sanity tier
            
        Returns:
            Modified feedback (may be inverted or corrupted)
        """
        if sanity_tier > 1:
            return feedback  # No unreliability for sanity >= 25
        
        # Chance to invert success/failure feedback
        if sanity_tier == 1 and random.random() < 0.15:
            if success:
                return feedback.replace("Success", "Failure").replace("succeeded", "failed")
            else:
                return feedback.replace("Failure", "Success").replace("failed", "succeeded")
        
        # Chance to corrupt the text
        if sanity_tier == 0 and random.random() < 0.25:
            words = feedback.split()
            corrupted_words = []
            for word in words:
                if random.random() < 0.3:
                    corrupted_words.append("█" * len(word))
                else:
                    corrupted_words.append(word)
            return " ".join(corrupted_words)
        
        return feedback
    
    def get_memory_drift(self, context: str = "") -> Optional[str]:
        """
        Get a false memory insertion.
        
        Args:
            context: Optional context for the memory
            
        Returns:
            Memory drift text or None
        """
        if not self.memory_drifts:
            return None
        
        candidates = self.memory_drifts
        
        # Filter by context if provided
        if context:
            context_matches = [m for m in candidates if context.lower() in m.get("contexts", [])]
            if context_matches:
                candidates = context_matches
        
        if candidates:
            drift = random.choice(candidates)
            return drift.get("text", "")
        
        return None
    
    def should_hallucinate(self, sanity_tier: int, hallucination_type: str) -> bool:
        """
        Determine if a hallucination should occur based on sanity tier.
        
        Args:
            sanity_tier: Current sanity tier (0-4)
            hallucination_type: "visual", "auditory", or "memory"
            
        Returns:
            True if hallucination should occur
        """
        if hallucination_type == "visual":
            if sanity_tier <= 0:
                return random.random() < 0.6
            elif sanity_tier == 1:
                return random.random() < 0.3
            return False
        
        elif hallucination_type == "auditory":
            if sanity_tier <= 0:
                return random.random() < 0.7
            elif sanity_tier == 1:
                return random.random() < 0.4
            elif sanity_tier == 2:
                return random.random() < 0.2
            return False
        
        elif hallucination_type == "memory":
            if sanity_tier <= 1:
                return random.random() < 0.25
            return False
        
        return False
