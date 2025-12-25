"""
Debug Controls for Psychological Systems - Week 15
Provides debugging tools for testing psychological state manipulation.
"""


class PsychDebugger:
    """Debug interface for psychological systems."""
    
    def __init__(self, game):
        """
        Initialize the debugger.
        
        Args:
            game: Reference to the Game instance
        """
        self.game = game
        self.enabled = False
        self.show_hallucinations = False
    
    def toggle_enabled(self):
        """Toggle debug mode on/off."""
        self.enabled = not self.enabled
        return self.enabled
    
    def set_sanity(self, value: float):
        """
        Manually set sanity value.
        
        Args:
            value: Sanity value (0-100)
        """
        value = max(0, min(100, value))
        old_value = self.game.player_state["sanity"]
        self.game.player_state["sanity"] = value
        return f"Sanity: {old_value:.0f} → {value:.0f}"
    
    def set_mental_load(self, value: int):
        """
        Manually set mental load value.
        
        Args:
            value: Mental Load value (0-100)
        """
        value = max(0, min(100, value))
        old_value = self.game.player_state["mental_load"]
        self.game.player_state["mental_load"] = value
        return f"Mental Load: {old_value} → {value}"
    
    def set_fear_level(self, value: int):
        """
        Manually set fear level.
        
        Args:
            value: Fear Level value (0-100)
        """
        value = max(0, min(100, value))
        old_value = self.game.player_state["fear_level"]
        self.game.player_state["fear_level"] = value
        return f"Fear Level: {old_value} → {value}"
    
    def reset_psychological_state(self):
        """Reset all psychological variables to default."""
        self.game.player_state["sanity"] = 100.0
        self.game.player_state["mental_load"] = 0
        self.game.player_state["fear_level"] = 0
        self.game.player_state["disorientation"] = False
        self.game.player_state["instability"] = False
        self.game.player_state["hallucination_history"] = []
        return "Psychological state reset to defaults"
    
    def force_breakdown(self):
        """Force a psychological breakdown."""
        self.game.player_state["sanity"] = 0
        self.game.player_state["mental_load"] = 100
        self.game.player_state["instability"] = True
        return "Forced breakdown state"
    
    def force_hallucination(self, hallucination_type="visual"):
        """
        Force a hallucination to occur.
        
        Args:
            hallucination_type: "visual", "auditory", or "memory"
        """
        tier = self.game.psych_state.get_sanity_tier()
        
        if hallucination_type == "visual":
            hallucination = self.game.hallucination_engine.get_visual_hallucination(tier)
        elif hallucination_type == "auditory":
            hallucination = self.game.hallucination_engine.get_auditory_hallucination(tier)
        elif hallucination_type == "memory":
            hallucination = self.game.hallucination_engine.get_memory_drift()
        else:
            return f"Unknown hallucination type: {hallucination_type}"
        
        if hallucination:
            return f"[{hallucination_type.upper()} HALLUCINATION]\n{hallucination}"
        else:
            return f"No {hallucination_type} hallucinations available for current sanity tier ({tier})"
    
    def toggle_fear_events(self):
        """Toggle fear events on/off."""
        new_state = self.game.fear_manager.toggle_enabled()
        return f"Fear events: {'ENABLED' if new_state else 'DISABLED'}"
    
    def reset_fear_cooldowns(self):
        """Reset all fear event cooldowns."""
        self.game.fear_manager.reset_cooldowns()
        return "All fear event cooldowns reset"
    
    def trigger_fear_event(self, event_id: str):
        """
        Force trigger a specific fear event.
        
        Args:
            event_id: ID of the fear event to trigger
        """
        effects = self.game.fear_manager.force_trigger_event(event_id)
        if effects:
            return f"Triggered fear event: {event_id}\nEffects: {effects}"
        else:
            return f"Fear event not found: {event_id}"
    
    def list_fear_events(self):
        """List all available fear events and their status."""
        statuses = self.game.fear_manager.get_all_events_status()
        if not statuses:
            return "No fear events loaded"
        
        lines = ["=== FEAR EVENTS ==="]
        for status in statuses:
            lines.append(f"\n{status['id']}: {status['name']}")
            lines.append(f"  Cooldown: {status['cooldown_minutes']} minutes")
            if status.get('last_triggered'):
                lines.append(f"  Last triggered: {status['last_triggered']}")
                lines.append(f"  Can trigger again in: {status.get('can_trigger_again_in', 0):.1f} minutes")
            else:
                lines.append("  Never triggered")
        
        return "\n".join(lines)
    
    def toggle_hallucination_overlay(self):
        """Toggle visual indicators for hallucinated content."""
        self.show_hallucinations = not self.show_hallucinations
        return f"Hallucination overlay: {'ON' if self.show_hallucinations else 'OFF'}"
    
    def get_debug_info(self):
        """Get comprehensive debug information about psychological state."""
        ps = self.game.player_state
        tier = self.game.psych_state.get_sanity_tier()
        tier_name = self.game.psych_state.get_sanity_tier_name()
        load_level = self.game.psych_state.get_mental_load_level()
        load_penalty = self.game.psych_state.get_mental_load_penalty()
        
        lines = [
            "=== PSYCHOLOGICAL DEBUG INFO ===",
            f"Sanity: {ps['sanity']:.1f}/100 (Tier {tier}: {tier_name})",
            f"Mental Load: {ps['mental_load']}/100 ({load_level})",
            f"  → Skill Penalty: {load_penalty}",
            f"  → Load Multiplier: {self.game.psych_state.get_mental_load_multiplier()}x",
            f"Fear Level: {ps['fear_level']}/100",
            f"Disorientation: {ps['disorientation']}",
            f"Instability: {ps['instability']}",
            f"Hallucinations Seen: {len(ps['hallucination_history'])}",
            "",
            "Hallucination Capabilities:",
            f"  Can hallucinate (any): {self.game.psych_state.is_hallucinating()}",
            f"  Can have visual: {self.game.psych_state.can_have_visual_hallucinations()}",
            f"  Can have auditory: {self.game.psych_state.can_have_auditory_hallucinations()}",
            f"  Skill misfire chance: {'Yes' if self.game.psych_state.should_skill_misfire() else 'No'}",
            "",
            f"Fear Events: {'ENABLED' if self.game.fear_manager.enabled else 'DISABLED'}",
            f"Debug Mode: {'ON' if self.enabled else 'OFF'}",
            f"Hallucination Overlay: {'ON' if self.show_hallucinations else 'OFF'}",
            "=" * 33
        ]
        
        return "\n".join(lines)
