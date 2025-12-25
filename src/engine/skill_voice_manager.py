import random
from typing import Dict, List, Optional, Any

class SkillVoiceManager:
    """
    Manages the 'internal voices' of the investigator's skills.
    Assigns literary archetypes to different skill groups/attributes.
    """

    VOICE_TEMPLATES = {
        "REASON": {
            "archetype": "The Analytical Detective (Christie/X-Files)",
            "color": "#4287f5", # Blue
            "templates": [
                "Logic dictates a sequence. This is the first link.",
                "Discrepancies found. The data does not align with the testimony.",
                "A rational mind would conclude that {subject} is a variable, not a constant.",
                "Scientific dismissal: The phenomenon is consistent with localized tectonic shifts. Nothing more.",
                "The motive is missing. Without motive, there is only noise."
            ]
        },
        "INTUITION": {
            "archetype": "The Sensitive (Lovecraft)",
            "color": "#9b59b6", # Purple
            "templates": [
                "The air here is thick with a geometry that should not exist.",
                "Something beneath the skin of reality is pulsing. Can't you feel it?",
                "The silence isn't empty. It's crowded with things that shouldn't have names.",
                "Your endocrine system is screaming. Fight or flight, but there's nowhere to hide.",
                "The stars above Kaltvik look... wrong. They're watching, not shining."
            ]
        },
        "PRESENCE": {
            "archetype": "The Hardboiled (Hammett)",
            "color": "#f1c40f", # Yellow
            "templates": [
                "He's sweating. Not the heat. The guilt.",
                "Watch the hands. The words are just a distraction.",
                "Don't show your cards. Keep the face neutral, the heart cold.",
                "The atmosphere is a layer of cheap perfume over a rotting corpse.",
                "Inaction is its own kind of choice. You're making it right now."
            ]
        },
        "CONSTITUTION": {
            "archetype": "The Professional (Fieldcraft/X-Files)",
            "color": "#e74c3c", # Red
            "templates": [
                "Vitals stable. But the adrenaline is starting to pool.",
                "Exits identified. Path of least resistance is behind you.",
                "The body is a tool. This environment is corrosive to the tool.",
                "Standard procedure for anomalous contact: Observe, record, survive.",
                "Muscle memory is the only truth in this woods."
            ]
        }
    }

    SANITY_CORRUPTION = {
        "tier_1": [ # Low sanity
            "The {subject} is screaming at you.",
            "Everything is {adjective}. Everything is wrong.",
            "Can you hear the whispering in the {subject}?",
            "Don't look too closely. The {subject} looks back."
        ],
        "tier_0": [ # Breakdown
            "ERROR: REALITY OVERFLOW",
            "THE TYGER IS HERE",
            "347. 347. 347.",
            "REDACTED REDACTED REDACTED"
        ]
    }

    DISSONANCE_TEMPLATES = [
        "The math is wrong. The count is wrong.",
        "Someone is missing. Someone is extra.",
        "347 is the constant. Deviations are dangerous.",
        "The herd is thinning/expanding inappropriately.",
        "Can you feel the weight of the missing souls?"
    ]

    def __init__(self):
        pass

    def get_interjection(self, attribute: str, context: str, sanity_tier: int = 4, dissonance: float = 0.0) -> Optional[Dict[str, str]]:
        """
        Get a personality-driven interjection for a given attribute.
        """
        if attribute not in self.VOICE_TEMPLATES:
            return None

        voice_data = self.VOICE_TEMPLATES[attribute]
        
        # Priority 1: Dissonance (if high enough)
        if dissonance > 0.3 and random.random() < dissonance:
             text = random.choice(self.DISSONANCE_TEMPLATES)
             # Stylize based on attribute
             if attribute == "REASON":
                 text = f"Statistical Anomaly Detected: {text}"
             elif attribute == "INTUITION":
                 text = f"Wrong. It feels wrong. {text}"
        
        # Priority 2: Sanity Corruption
        elif sanity_tier <= 1:
            corruption_msg = random.choice(self.SANITY_CORRUPTION[f"tier_{sanity_tier}"])
            # Inject context keywords into corruption if possible
            keywords = context.split()[:3]
            subject = keywords[0] if keywords else "everything"
            adj = "bleeding" if sanity_tier == 0 else "wrong"
            
            text = corruption_msg.format(subject=subject, adjective=adj)
        else:
            text = random.choice(voice_data["templates"])
            # Simple context injection if {subject} placeholder exists
            if "{subject}" in text:
                keywords = [w for w in context.split() if len(w) > 4][:1]
                subject = keywords[0] if keywords else "the situation"
                text = text.format(subject=subject)

        return {
            "skill": attribute,
            "text": text,
            "color": voice_data["color"],
            "archetype": voice_data["archetype"]
        }

    def get_skill_specific_voice(self, skill_name: str, attribute: str, context: str, sanity_tier: int = 4, dissonance: float = 0.0) -> Optional[Dict[str, str]]:
        """
        More granular voice for specific skills.
        """
        # For now, we fall back to attribute but we could add skill-specific templates
        interjection = self.get_interjection(attribute, context, sanity_tier, dissonance)
        if interjection:
            interjection["skill"] = skill_name.upper()
        return interjection
