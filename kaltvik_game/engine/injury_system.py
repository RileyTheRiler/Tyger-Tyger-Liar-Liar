from utils.formatter import display_text
from engine.skill_check import roll_skill_check

# Injury Locations and their typical penalties (for reference or future expansion)
INJURY_EFFECTS = {
    "leg": {"Athletics": -2, "Stealth": -1},
    "arm": {"Hand-to-Hand Combat": -2, "Firearms": -2},
    "head": {"Logic": -1, "Perception": -2},
    "torso": {"Endurance": -2, "Fortitude": -2},
    "general": {"All": -1} # Special case handling needed
}

def apply_injury(state, location, severity, effect=None):
    """
    Adds an injury to the state.
    location: str (leg, arm, head, etc)
    severity: str (minor, moderate, severe)
    effect: dict {Skill: Penalty} (optional override)
    """
    
    if effect is None:
        effect = INJURY_EFFECTS.get(location, {})
        
    injury = {
        "location": location,
        "severity": severity,
        "effect": effect
    }
    
    state.injuries.append(injury)
    display_text(f"\n[INJURY] You have sustained a {severity} injury to your {location}!")
    
    # Check for Systemic Collapse if too many injuries
    if len(state.injuries) >= 3: # Arbitrary threshold for now
        display_text("[WARNING] Your body is failing. You are on the verge of collapse.")
        check_trauma(state, force=True)

def heal_injury(state, location=None):
    """
    Removes injuries. If location is None, removes the oldest/first.
    """
    if not state.injuries:
        display_text("You have no injuries to heal.")
        return

    if location:
        # Find specific injury
        for i, inj in enumerate(state.injuries):
            if inj["location"] == location:
                removed = state.injuries.pop(i)
                display_text(f"Your {removed['location']} injury has been treated.")
                return
        display_text(f"No injury found on {location}.")
    else:
        # Heal first
        removed = state.injuries.pop(0)
        display_text(f"Your {removed['location']} injury has been treated.")

def check_trauma(state, force=False):
    """
    Rolls Fortitude to resist breakdown.
    Triggered by extreme events or injury overload.
    """
    if not force:
        # standard check
        pass
    
    # Simple threshold check
    display_text("\n[TRAUMA CHECK] Holding it together...")
    
    skill = "Fortitude"
    dc = 10 + len(state.injuries) * 2
    skill_level = state.skills.get(skill, 0)
    
    result, roll = roll_skill_check(skill, skill_level, dc)
    
    if result == "success":
        display_text("SUCCESS. You grit your teeth and push through the pain.")
    else:
        display_text("FAILURE. Darkness takes you.")
        handle_systemic_collapse(state)

def handle_systemic_collapse(state):
    """
    The 'Death' alternative.
    """
    display_text("\n*** SYSTEMIC COLLAPSE ***")
    display_text("The world fades. Time passes without you.")
    
    # 1. Advance Time (loss)
    hours_lost = 24
    if hasattr(state, 'advance_time'): # Future proofing if we add this method to state
        state.advance_time(hours_lost)
    else:
        # Manually advance theories if needed, or just narrative text
        display_text(f"(You lose {hours_lost} hours of investigation time.)")
        
    # 2. Add Scar / Permanent trait? (Future)
    
    # 3. Move to Hospital
    # Save current scene to return to? Or just dump in hospital?
    state.current_scene = "hospital_recovery"
    
    # 4. Clear Injuries? Or leave some as scars?
    # Let's clear acute injuries but maybe leave one as 'treated'
    state.injuries = [] 
    state.combat_state = None # End combat forced
    
    display_text("You wake up in a sterile room. The smell of antiseptic is overwhelming.")
