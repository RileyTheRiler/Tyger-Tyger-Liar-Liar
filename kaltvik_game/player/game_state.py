class GameState:
    def __init__(self):
        self.current_scene = "intro_scene"
        self.flags = {}
        self.inventory = []
        
        # Attributes (0–6 scale)
        self.attributes = {
            "reason": 3,
            "intuition": 2,
            "constitution": 2,
            "presence": 3
        }

        # Skills (0–6 scale)
        self.skills = {
            # Reason
            "Logic": 2, "Forensics": 1, "Research": 0, "Skepticism": 1, 
            "Medicine": 0, "Technology": 0, "Occult Knowledge": 0,
            # Intuition
            "Pattern Recognition": 1, "Paranormal Sensitivity": 0, "Profiling": 1, 
            "Instinct": 2, "Subconscious": 0, "Manipulation": 1, "Perception": 2,
            # Constitution
            "Endurance": 1, "Fortitude": 1, "Firearms": 0, "Athletics": 1, 
            "Stealth": 1, "Reflexes": 1, "Survival": 0, "Hand-to-Hand Combat": 0,
            # Presence
            "Authority": 1, "Charm": 2, "Wits": 1, "Composure": 1, 
            "Empathy": 3, "Interrogation": 1, "Deception": 1
        }

        self.checked_whites = set()  # Track used white checks

        
        # The Board (Theories/Thoughts)
        self.board = {
            "slots": 2,  # max concurrent theories
            "active": [],  # currently internalizing: [{"id": "theory_id", "remaining_time": hours}]
            "completed": [],  # finished, applied: ["theory_id"]
            "rejected": []  # manually removed: ["theory_id"]
        }

