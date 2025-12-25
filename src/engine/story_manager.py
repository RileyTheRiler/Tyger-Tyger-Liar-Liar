from datetime import datetime
from typing import List, Dict, Callable

class StoryManager:
    """
    Manages the narrative timeline and triggered events based on game time.
    """
    def __init__(self, time_system, population_system, player_state, output_buffer=None):
        self.time_system = time_system
        self.population_system = population_system
        self.player_state = player_state
        self.output = output_buffer
        
        # Register listener
        self.time_system.add_listener(self.check_timeline_events)
        
        self.triggered_events = set()
        
        # Restore triggered events from save if available
        if "triggered_story_events" in self.player_state:
            self.triggered_events = set(self.player_state["triggered_story_events"])
        else:
            self.player_state["triggered_story_events"] = []

    def check_timeline_events(self, minutes_passed: int):
        """Called whenever time passes in the game."""
        current_data = self.time_system.get_date_data()
        day = current_data["days_passed"] + 1 # Day 1 is 0 days passed
        hour = current_data["datetime"].hour
        
        # --- DAY 2 EVENTS ---
        if day == 2:
            # 09:00 AM - Old Tom Disappears
            if hour >= 9 and "day2_tom_missing" not in self.triggered_events:
                self._trigger_old_tom_missing()

        # --- DAY 3 EVENTS ---
        if day == 3:
            # 22:00 PM - The Green Pulse
            if hour >= 22 and "day3_green_pulse" not in self.triggered_events:
                self._trigger_green_pulse()

        # --- DAY 4 EVENTS ---
        if day == 4:
            # 14:00 PM - The Circle
            if hour >= 14 and "day4_birds_found" not in self.triggered_events:
                self._trigger_the_circle()

    def _trigger_old_tom_missing(self):
        """
        Event: Maintenance worker Old Tom goes missing.
        Effect: Population -1, Global Flag Set, Notification.
        """
        self.triggered_events.add("day2_tom_missing")
        self.player_state["triggered_story_events"].append("day2_tom_missing")
        
        # Set Flag for dialogue reactivity
        if "flags" not in self.player_state:
            self.player_state["flags"] = {}
        self.player_state["flags"]["old_tom_missing"] = True
        
        # Population Effect
        if self.population_system:
            self.population_system.record_disappearance(
                description="Old Tom (Maintenance) was not at his post. Tools found abandoned.",
                count=1,
                npc_id="npc_old_tom"
            )
            
        # Narrative Notification
        if self.output:
            from ui.interface import Colors
            self.output.print(f"\n{Colors.RED}*** TIMELINE UPDATE: DAY 2 ***{Colors.RESET}")
            self.output.print("Word spreads from the Maintenance Shed. Old Tom didn't report in.")
            self.output.print(f"{Colors.YELLOW}Journal Updated: 'The Disappearance'{Colors.RESET}\n")

    def _trigger_green_pulse(self):
        """
        Event: The Green Pulse (Aurora Event).
        Effect: limit visibility, weather change, audio hum.
        """
        self.triggered_events.add("day3_green_pulse")
        self.player_state["triggered_story_events"].append("day3_green_pulse")
        
        # Set Weather
        if self.time_system:
            self.time_system.set_weather("aurora_storm")
            
        # Narrative Notification
        if self.output:
            from ui.interface import Colors
            self.output.print(f"\n{Colors.CYAN}*** TIMELINE UPDATE: DAY 3 ***{Colors.RESET}")
            self.output.print("The sky above Kaltvik tears open. A sickening green light floods the valley.")
            self.output.print("Electronic devices begin to hum in unison.")
            self.output.print(f"{Colors.YELLOW}Journal Updated: 'The Green Pulse'{Colors.RESET}\n")

    def _trigger_the_circle(self):
        """
        Event: Dead birds found arranged in concentric circles around the Town Square statue.
        Effect: Flag Set, Notification.
        """
        self.triggered_events.add("day4_birds_found")
        self.player_state["triggered_story_events"].append("day4_birds_found")
        
        # Set Flag for dialogue reactivity
        if "flags" not in self.player_state:
            self.player_state["flags"] = {}
        self.player_state["flags"]["day4_birds_found"] = True

        # Narrative Notification
        if self.output:
            from ui.interface import Colors
            self.output.print(f"\n{Colors.MAGENTA}*** TIMELINE UPDATE: DAY 4 ***{Colors.RESET}")
            self.output.print("A crowd gathers in the Town Square. A ring of black feathers surrounds the statue.")
            self.output.print("Hundreds of starlings. Necks broken. Arranged perfectly.")
            self.output.print(f"{Colors.YELLOW}Journal Updated: 'The Circle'{Colors.RESET}\n")

    def restore_state(self):
        """Syncs local state with player state after load."""
        if "triggered_story_events" in self.player_state:
            self.triggered_events = set(self.player_state["triggered_story_events"])
