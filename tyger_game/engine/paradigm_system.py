from typing import Dict, List, Optional, Callable
from tyger_game.engine.character import Character
from tyger_game.ui.interface import print_text, Colors

class Paradigm:
    def __init__(self, pid: str, name: str, problem_text: str, solution_text: str, 
                 internalization_time: int, 
                 temp_effect: Callable[[Character], None], 
                 perm_effect: Callable[[Character], None],
                 alignment_shift: Dict[str, int]):
        self.id = pid
        self.name = name
        self.problem_text = problem_text
        self.solution_text = solution_text
        self.internalization_time = internalization_time # in update ticks or hours
        self.temp_effect = temp_effect
        self.perm_effect = perm_effect
        self.alignment_shift = alignment_shift

# --- Paradigm Definitions (Hardcoded for now) ---

def effect_simulation_temp(char: Character):
    # -2 to Presence checks (simplified as just a note for now)
    pass

def effect_simulation_perm(char: Character):
    char.modify_reality(-5) # Disconnect from reality
    # Allow Save Scum (Mechanic to be implemented)

PARADIGM_DB = {
    "simulation_hypothesis": Paradigm(
        pid="simulation_hypothesis",
        name="The Simulation Hypothesis",
        problem_text="If the universe is code, then nothing is solid. The table is data...",
        solution_text="You haven't found the admin console, but you've realized the code is sloppy...",
        internalization_time=6,
        temp_effect=effect_simulation_temp,
        perm_effect=effect_simulation_perm,
        alignment_shift={"skeptic": 1, "chaos": 2}
    ),
    "bicameral_mind": Paradigm(
        pid="bicameral_mind",
        name="The Bicameral Mind",
        problem_text="Ancient man didn't think; he heard commands...",
        solution_text="The gods are silent, but the frequency is still open...",
        internalization_time=4,
        temp_effect=lambda c: None,
        perm_effect=lambda c: None,
        alignment_shift={"believer": 2, "chaos": 1}
    )
}

class ParadigmManager:
    @staticmethod
    def get_paradigm(pid: str) -> Optional[Paradigm]:
        return PARADIGM_DB.get(pid)

    @staticmethod
    def start_internalizing(character: Character, pid: str) -> bool:
        if pid not in PARADIGM_DB:
            return False
        
        # specific structure for stored thought
        thought_data = {
            "id": pid,
            "status": "internalizing",
            "progress": 0,
            "completed": False
        }
        character.paradigms.append(thought_data)
        
        # Apply immediate debug text
        para = PARADIGM_DB[pid]
        print_text(f"Internalizing: {para.name}", Colors.WARNING)
        print_text(para.problem_text, Colors.CYAN)
        return True

    @staticmethod
    def advance_time(character: Character, hours: int):
        """Updates progress on all internalizing thoughts."""
        for p_data in character.paradigms:
            if p_data["status"] == "internalizing":
                p_data["progress"] += hours
                
                para = PARADIGM_DB.get(p_data["id"])
                if para and p_data["progress"] >= para.internalization_time:
                    ParadigmManager.complete_thought(character, p_data)

    @staticmethod
    def complete_thought(character: Character, p_data: dict):
        p_data["status"] = "completed"
        p_data["completed"] = True
        
        para = PARADIGM_DB.get(p_data["id"])
        if para:
            print_text(f"Thought Policy Added: {para.name}", Colors.GREEN)
            print_text(para.solution_text, Colors.HEADER)
            
            # Apply permanent effects
            para.perm_effect(character)
            
            # Apply Alignment Shift
            from tyger_game.engine.alignment_system import AlignmentSystem
            for axis, val in para.alignment_shift.items():
                AlignmentSystem.modify_alignment(character, axis, val)
