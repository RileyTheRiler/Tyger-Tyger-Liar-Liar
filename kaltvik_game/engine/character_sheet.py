REASON_SKILLS = [
    "Logic", "Forensics", "Research", "Skepticism", 
    "Medicine", "Technology", "Occult Knowledge"
]
INTUITION_SKILLS = [
    "Pattern Recognition", "Paranormal Sensitivity", "Profiling", 
    "Instinct", "Subconscious", "Manipulation", "Perception"
]
CONSTITUTION_SKILLS = [
    "Endurance", "Fortitude", "Firearms", "Athletics", 
    "Stealth", "Reflexes", "Survival", "Hand-to-Hand Combat"
]
PRESENCE_SKILLS = [
    "Authority", "Charm", "Wits", "Composure", 
    "Empathy", "Interrogation", "Deception"
]

def show_character_sheet(state):
    print("\n====================================")
    print("         CHARACTER SHEET            ")
    print("====================================")
    
    print("\n[ATTRIBUTES]")
    for attr, val in state.attributes.items():
        print(f"  {attr.title()}: {val}")

    print("\n[SKILLS]")
    grouped = categorize_skills(state.skills)
    for category, skills in grouped.items():
        print(f"\n--- {category.upper()} ---")
        for skill, val in skills:
            print(f"  {skill}: {val}")
    print("\n====================================")

def categorize_skills(skills):
    return {
        "Reason": [(s, v) for s, v in skills.items() if s in REASON_SKILLS],
        "Intuition": [(s, v) for s, v in skills.items() if s in INTUITION_SKILLS],
        "Constitution": [(s, v) for s, v in skills.items() if s in CONSTITUTION_SKILLS],
        "Presence": [(s, v) for s, v in skills.items() if s in PRESENCE_SKILLS]
    }
