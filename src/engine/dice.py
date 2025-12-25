"""
Dice System - 2d6 resolution engine with manual roll support and partial success.
Per Canon & Constraints: 2d6 + (attribute + skill + modifiers) vs DC.

Difficulty Bands:
- DC 7: Easy
- DC 9: Standard
- DC 11: Hard
- DC 13: Extreme

Partial Success (fail by 1-2): Success with cost.
"""

import random
from typing import Dict, Optional, Callable, Tuple
from enum import Enum
from dataclasses import dataclass, field


class CheckResult(Enum):
    CRITICAL_SUCCESS = "critical_success"
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    CRITICAL_FAILURE = "critical_failure"


class DifficultyClass(Enum):
    TRIVIAL = 5
    EASY = 7
    STANDARD = 9
    HARD = 11
    EXTREME = 13
    LEGENDARY = 15


@dataclass
class RollResult:
    """Complete result of a dice roll and check."""
    d1: int
    d2: int
    total: int
    modifier: int
    final_total: int
    dc: int
    result: CheckResult
    margin: int  # Positive = succeeded by, Negative = failed by
    is_double: bool
    is_manual: bool
    description: str = ""
    costs: list = field(default_factory=list)  # Costs for partial success


class DiceSystem:
    """
    Manages dice rolling with manual roll option and partial success mechanics.
    """

    def __init__(self):
        self.manual_mode = False
        self.roll_history: list = []
        self.manual_roll_callback: Optional[Callable[[], int]] = None

        # Modifiers from game state
        self.stress_modifier = 0
        self.attention_modifier = 0
        self.logs = []

        # Partial success costs
        self.partial_success_costs = {
            "time": "This takes longer than expected. (+15 minutes)",
            "attention": "Something notices your attempt. (+5 Attention)",
            "trust": "Your methods raise suspicion. (-5 Trust)",
            "injury": "You strain yourself in the attempt. (Minor injury)",
            "resource": "You expend resources in the attempt.",
            "noise": "You make noise. Others may have heard.",
            "evidence": "You leave traces of your investigation."
        }

    def set_manual_mode(self, enabled: bool, callback: Callable[[], int] = None):
        """
        Enable or disable manual dice mode.

        Args:
            enabled: Whether to use manual mode
            callback: Optional function to call to get the roll value (2-12)
        """
        self.manual_mode = enabled
        self.manual_roll_callback = callback
        print(f"[DICE] Manual roll mode: {'ON' if enabled else 'OFF'}")

    def roll_2d6(self, manual_roll: int = None) -> Dict:
        """
        Roll 2d6 and return raw dice result.
        Supports manual override.
        """
        if manual_roll is not None:
            # Validate manual roll
            manual_roll = max(2, min(12, manual_roll))
            d1 = manual_roll // 2
            d2 = manual_roll - d1
            # Adjust for valid dice values
            if d1 < 1:
                d1 = 1
                d2 = manual_roll - 1
            if d2 < 1:
                d2 = 1
                d1 = manual_roll - 1

            return {
                "d1": d1,
                "d2": d2,
                "total": manual_roll,
                "is_double": d1 == d2,
                "is_critical_success": manual_roll == 12,
                "is_critical_failure": manual_roll == 2,
                "is_manual": True
            }

        if self.manual_mode:
            if self.manual_roll_callback:
                roll_value = self.manual_roll_callback()
            else:
                # Prompt for input (can be overridden)
                roll_value = self._prompt_manual_roll()
            return self.roll_2d6(manual_roll=roll_value)

        d1 = random.randint(1, 6)
        d2 = random.randint(1, 6)
        total = d1 + d2

        return {
            "d1": d1,
            "d2": d2,
            "total": total,
            "is_double": d1 == d2,
            "is_critical_success": total == 12,
            "is_critical_failure": total == 2,
            "is_manual": False
        }

    def _prompt_manual_roll(self) -> int:
        """Prompt for manual roll input. Override for different UI."""
        while True:
            try:
                value = input("[DICE] Enter your roll (2-12): ")
                roll = int(value)
                if 2 <= roll <= 12:
                    return roll
                print("Please enter a value between 2 and 12.")
            except ValueError:
                print("Please enter a valid number.")

    def resolve_check(self, skill_name: str, modifier: int, dc: int,
                      check_type: str = "white", manual_roll: int = None,
                      allow_partial: bool = True) -> RollResult:
        """
        Resolve a complete skill check with partial success support.

        Args:
            skill_name: Name of the skill being checked
            modifier: Total modifier (attribute + skill + bonuses)
            dc: Difficulty class
            check_type: "white" (retryable) or "red" (permanent)
            manual_roll: Override dice value if provided
            allow_partial: Whether partial success is possible

        Returns:
            RollResult with complete check information
        """
        # Integrate with GameState if provided separately or locally
        effective_modifier = modifier + self.stress_modifier + self.attention_modifier

        # Roll dice
        dice = self.roll_2d6(manual_roll)
        roll_total = dice["total"]
        final_total = roll_total + effective_modifier
        margin = final_total - dc

        # Determine result
        if dice["is_critical_success"]:
            result = CheckResult.CRITICAL_SUCCESS
            description = "CRITICAL SUCCESS! Perfect execution."
        elif dice["is_critical_failure"]:
            result = CheckResult.CRITICAL_FAILURE
            description = "CRITICAL FAILURE! Everything goes wrong."
        elif margin >= 0:
            result = CheckResult.SUCCESS
            description = f"Success by {margin}."
        elif margin >= -2 and allow_partial:
            result = CheckResult.PARTIAL_SUCCESS
            description = f"Partial success. You achieve your goal, but at a cost."
        else:
            result = CheckResult.FAILURE
            description = f"Failure by {abs(margin)}."

        # Determine costs for partial success
        costs = []
        if result == CheckResult.PARTIAL_SUCCESS:
            costs = self._determine_partial_costs(skill_name, abs(margin))

        roll_result = RollResult(
            d1=dice["d1"],
            d2=dice["d2"],
            total=roll_total,
            modifier=effective_modifier,
            final_total=final_total,
            dc=dc,
            result=result,
            margin=margin,
            is_double=dice["is_double"],
            is_manual=dice["is_manual"],
            description=description,
            costs=costs
        )

        # Record in history and logs
        log_entry = {
            "skill": skill_name,
            "roll": roll_total,
            "modifier": effective_modifier,
            "dc": dc,
            "result": result.value,
            "margin": margin,
            "check_type": check_type,
            "description": description
        }
        self.roll_history.append(log_entry)
        self.logs.append(log_entry)
        
        # Consistent Console Logging
        print(f"\n[CHECK] {skill_name.upper()} (DC {dc})")
        print(f"Outcome: {result.value.replace('_', ' ').upper()} (margin {margin:+d})")
        if costs:
            for c_type, c_desc in costs:
                print(f"  > Cost: {c_desc}")

        return roll_result

    def _determine_partial_costs(self, skill_name: str, failure_margin: int) -> list:
        """Determine what costs apply for a partial success."""
        import random

        # Map skills to likely costs
        skill_costs = {
            "Stealth": ["noise", "attention"],
            "Forensics": ["time", "evidence"],
            "Athletics": ["injury", "time"],
            "Charm": ["trust", "time"],
            "Interrogation": ["trust", "attention"],
            "Firearms": ["resource", "noise"],
            "Research": ["time"],
            "Survival": ["resource", "injury"],
            "default": ["time", "attention"]
        }

        possible_costs = skill_costs.get(skill_name, skill_costs["default"])

        # More severe failure = more costs
        num_costs = 1 if failure_margin == 1 else 2

        selected = random.sample(possible_costs, min(num_costs, len(possible_costs)))
        return [(cost, self.partial_success_costs.get(cost, cost)) for cost in selected]

    def set_stress_modifier(self, modifier: int):
        """Set stress-based roll modifier (typically negative)."""
        self.stress_modifier = modifier

    def set_attention_modifier(self, modifier: int):
        """Set attention-based roll modifier (swingier at high attention)."""
        self.attention_modifier = modifier

    def get_dc_description(self, dc: int) -> str:
        """Get human-readable DC description."""
        if dc <= 5:
            return "Trivial"
        elif dc <= 7:
            return "Easy"
        elif dc <= 9:
            return "Standard"
        elif dc <= 11:
            return "Hard"
        elif dc <= 13:
            return "Extreme"
        else:
            return "Legendary"

    def format_roll_result(self, result: RollResult, show_dice: bool = True) -> str:
        """Format a roll result for display."""
        lines = []

        if show_dice:
            dice_str = f"[{result.d1}][{result.d2}]" if not result.is_manual else f"[{result.total}] (manual)"
            lines.append(f"Roll: {dice_str} = {result.total}")
            lines.append(f"Modifier: {result.modifier:+d}")
            lines.append(f"Total: {result.final_total} vs DC {result.dc}")
            lines.append("")

        # Result line
        result_symbols = {
            CheckResult.CRITICAL_SUCCESS: "++",
            CheckResult.SUCCESS: "+",
            CheckResult.PARTIAL_SUCCESS: "~",
            CheckResult.FAILURE: "-",
            CheckResult.CRITICAL_FAILURE: "--"
        }
        symbol = result_symbols.get(result.result, "?")
        lines.append(f"[{symbol}] {result.description}")

        # Costs for partial success
        if result.costs:
            lines.append("\nCosts:")
            for cost_type, cost_desc in result.costs:
                lines.append(f"  - {cost_desc}")

        return "\n".join(lines)


# Convenience function for backwards compatibility
def roll_2d6(manual_roll: int = None) -> Dict:
    """
    Rolls 2d6 and returns a dictionary with results.
    Handles manual overrides for testing/debug.
    """
    system = DiceSystem()
    return system.roll_2d6(manual_roll)


def get_roll_description(roll_data: Dict) -> str:
    """Returns a flavor description of the natural roll."""
    total = roll_data["total"]

    if total == 12:
        return "CRITICAL SUCCESS! A perfect perception of reality."
    if total == 2:
        return "CRITICAL FAILURE! The logic collapses into static."
    if roll_data["is_double"]:
        return f"Doubles ({roll_data['d1']}s). A moment of heightened resonance."

    return ""


if __name__ == "__main__":
    # Test the enhanced dice system
    system = DiceSystem()

    print("=== DICE SYSTEM TEST ===\n")

    # Test normal roll
    print("Normal check (DC 9):")
    result = system.resolve_check("Perception", modifier=3, dc=9)
    print(system.format_roll_result(result))

    print("\n" + "=" * 40 + "\n")

    # Test with manual roll
    print("Manual roll (value=8, DC 9, modifier +2):")
    result = system.resolve_check("Stealth", modifier=2, dc=9, manual_roll=8)
    print(system.format_roll_result(result))

    print("\n" + "=" * 40 + "\n")

    # Test critical success
    print("Critical success (roll=12):")
    result = system.resolve_check("Logic", modifier=0, dc=13, manual_roll=12)
    print(system.format_roll_result(result))

    print("\n" + "=" * 40 + "\n")

    # Test partial success
    print("Partial success (DC 11, roll=8, modifier +2 = 10, fail by 1):")
    result = system.resolve_check("Charm", modifier=2, dc=11, manual_roll=8)
    print(system.format_roll_result(result))

    print("\n" + "=" * 40 + "\n")

    # Test full failure
    print("Full failure (DC 11, roll=4, modifier +2 = 6, fail by 5):")
    result = system.resolve_check("Athletics", modifier=2, dc=11, manual_roll=4)
    print(system.format_roll_result(result))
