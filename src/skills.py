import random

class SkillSystem:
    SKILLS = [
        "Logic", "Empathy", "Perception", 
        "Volition", "Shivers", "Composure"
    ]

    @staticmethod
    def roll_check(skill_level, difficulty):
        """
        Rolls a check using 2d10 + skill_level vs difficulty.
        Returns a tuple: (success: bool, roll_total: int, natural_roll: int)
        """
        die1 = random.randint(1, 10)
        die2 = random.randint(1, 10)
        total = die1 + die2 + skill_level
        
        # Critical success (double 10s) or failure (double 1s) could be added here
        is_critical_success = (die1 == 10 and die2 == 10)
        is_critical_failure = (die1 == 1 and die2 == 1)
        
        success = False
        if is_critical_success:
            success = True
        elif is_critical_failure:
            success = False
        else:
            success = total >= difficulty
            
        return {
            "success": success,
            "total": total,
            "natural_roll": die1 + die2,
            "die1": die1,
            "die2": die2
        }

    @staticmethod
    def get_difficulty_string(difficulty):
        if difficulty <= 6: return "Trivial"
        if difficulty <= 10: return "Easy"
        if difficulty <= 12: return "Medium"
        if difficulty <= 14: return "Challenging"
        if difficulty <= 16: return "Formidable"
        if difficulty <= 18: return "Impossible"
        return "Godly"
