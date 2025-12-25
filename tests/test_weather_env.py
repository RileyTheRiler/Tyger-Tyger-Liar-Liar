import unittest
from unittest.mock import MagicMock
from src.weather_system import WeatherSystem
from src.environmental_system import EnvironmentalSystem
from src.ambient_system import AmbientSystem
from src.time_system import TimeSystem

class TestWeatherSystem(unittest.TestCase):
    def setUp(self):
        self.weather = WeatherSystem()

    def test_initial_condition(self):
        self.assertEqual(self.weather.current_condition_key, "clear")

    def test_update_decrements_timer(self):
        self.weather.next_shift_time = 60
        self.weather.update(30)
        self.assertEqual(self.weather.next_shift_time, 30)

    def test_shift_weather(self):
        self.weather.next_shift_time = 0
        self.weather.update(10)
        # Should have reset timer
        self.assertTrue(self.weather.next_shift_time > 0)

    def test_force_condition(self):
        self.weather._shift_weather(force_condition="snow")
        self.assertEqual(self.weather.current_condition_key, "snow")
        self.assertEqual(self.weather.get_current_condition().name, "Light Snow")

    def test_wind_chill(self):
        self.weather.temperature = 0
        self.weather.wind_speed = 0
        self.assertEqual(self.weather.calculate_wind_chill(), 0)

        self.weather.temperature = -10
        self.weather.wind_speed = 20
        wc = self.weather.calculate_wind_chill()
        self.assertTrue(wc < -10)

class TestEnvironmentalSystem(unittest.TestCase):
    def setUp(self):
        self.time_sys = MagicMock()
        self.weather_sys = WeatherSystem()
        self.player_state = {"sanity": 50, "reality": 100}
        self.env_sys = EnvironmentalSystem(self.time_sys, self.weather_sys, self.player_state)

    def test_process_event(self):
        msg = self.env_sys.process_event("glitch")
        self.assertTrue("geometry" in msg)

    def test_ritual(self):
        result = self.env_sys.perform_ritual("shrine")
        self.assertTrue(result["success"])
        self.assertEqual(self.player_state["sanity"], 65)

    def test_ritual_invalid_location(self):
        result = self.env_sys.perform_ritual("nowhere")
        self.assertFalse(result["success"])

class TestAmbientSystem(unittest.TestCase):
    def setUp(self):
        self.weather_sys = WeatherSystem()
        self.player_state = {"sanity": 100}
        self.ambient_sys = AmbientSystem(self.weather_sys, self.player_state)

    def test_get_sensory_response(self):
        resp = self.ambient_sys.get_sensory_response("listen", [])
        self.assertTrue(len(resp) > 0)

    def test_sanity_cues(self):
        self.player_state["sanity"] = 20
        # It's random, so we can't easily assert it *will* return something,
        # but we can call it without error.
        self.ambient_sys.check_reactive_cues()

if __name__ == '__main__':
    unittest.main()
