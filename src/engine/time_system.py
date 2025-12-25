from datetime import datetime, timedelta
from typing import List, Callable, Dict, Any

class TimeSystem:
    def __init__(self, start_date_str: str = "1995-10-14 08:00"):
        # Parse start date
        self.current_time = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M")
        self.start_time = self.current_time
        
        # Listeners (callbacks that take minutes_passed as int)
        self.listeners: List[Callable[[int], None]] = []
        
        # Scheduled Events: List of dicts { 'time': datetime, 'callback': func, 'desc': str }
        self.scheduled_events: List[Dict[str, Any]] = []
        
        self.weather = "clear"
        self.day_cycle_events = {
             0: "Midnight. The static is loudest now.",
             6: "Dawn breaks, grey and cold.",
             12: "Noon. shadows are suspiciously long.",
             18: "Dusk. The aurora begins to wake.",
        }

    def set_weather(self, weather_type: str):
        self.weather = weather_type

    def add_listener(self, callback: Callable[[int], None]):
        self.listeners.append(callback)

    def advance_time(self, minutes: int):
        """Advances time by X minutes, checking for triggers and notifying listeners."""
        # We advance in chunks if necessary, but for now simple addition
        old_time = self.current_time
        self.current_time += timedelta(minutes=minutes)
        
        # Check triggers
        self.check_triggers(old_time, self.current_time)
        
        # Check day cycle updates
        self._check_day_cycle(old_time, self.current_time)

        # Notify listeners
        for listener in self.listeners:
            listener(minutes)

    def schedule_event(self, delay_minutes: int, callback: Callable[[], None], description: str):
        trigger_time = self.current_time + timedelta(minutes=delay_minutes)
        self.scheduled_events.append({
            "time": trigger_time,
            "callback": callback,
            "desc": description
        })
        # Sort by time so we process earliest first
        self.scheduled_events.sort(key=lambda x: x["time"])

    def check_triggers(self, previous_time: datetime, new_time: datetime):
        # We need to process events that happened between previous_time and new_time
        # Use a while loop to handle events that might trigger other events?
        # For simplicity, just iterate copy of list
        
        remaining_events = []
        fired_events = []
        
        for event in self.scheduled_events:
            if event["time"] <= new_time:
                fired_events.append(event)
            else:
                remaining_events.append(event)
        
        self.scheduled_events = remaining_events
        
        for event in fired_events:
            # You might want to print a debug log here
            # print(f"[DEBUG] Event triggered: {event['desc']}")
            if event["callback"]:
                event["callback"]()

    def _check_day_cycle(self, old_time: datetime, new_time: datetime):
        # Simple check for hour crossings
        if old_time.hour != new_time.hour:
            # If we crossed an hour boundary
            hour = new_time.hour
            if hour in self.day_cycle_events:
                # We could broadcast this, but for now we'll just store it as "last_time_event"
                # The game loop can poll or we can add a specific listener for narrative events
                pass

    def get_time_string(self) -> str:
        # Format: "Oct 14, 08:00 AM" or similar
        return self.current_time.strftime("%b %d, %I:%M %p") + f" | Weather: {self.weather}"

    def get_date_data(self) -> Dict[str, Any]:
        delta = self.current_time - self.start_time
        return {
            "datetime": self.current_time,
            "days_passed": delta.days,
            "day_of_week": self.current_time.strftime("%A")
        }
    
    def to_dict(self) -> dict:
        """Serialize time system to dictionary."""
        return {
            "current_time": self.current_time.strftime("%Y-%m-%d %H:%M"),
            "start_time": self.start_time.strftime("%Y-%m-%d %H:%M"),
            "weather": self.weather
            # Note: We don't serialize callbacks/listeners as they need to be re-registered
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'TimeSystem':
        """Deserialize time system from dictionary."""
        system = TimeSystem(start_date_str=data.get("start_time", "1995-10-14 08:00"))
        system.current_time = datetime.strptime(data["current_time"], "%Y-%m-%d %H:%M")
        system.weather = data.get("weather", "clear")
        return system
