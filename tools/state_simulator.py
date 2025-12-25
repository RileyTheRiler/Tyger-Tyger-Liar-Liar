
import sys
import os
import random

# Add src to path
sys.path.append(os.path.abspath("src"))

# Mocking necessary parts if standard imports fail or to isolate tests,
# but here we want integration testing with game.py
from game import Game
from ui.interface import Colors

class StateSimulator:
    def __init__(self):
        self.game = Game()
        self.game.debug_mode = True # Enable debug for suggestions
        # Redirect print
        self.captured_output = []
        self.game.print = self._mock_print

    def _mock_print(self, text=""):
        self.captured_output.append(str(text))

    def run(self):
        print("--- State Simulator ---")
        print("Inject mental states and view parser reactions.")
        print("Commands:")
        print("  sanity <val>   - Set Sanity (0-100)")
        print("  reality <val>  - Set Reality (0-100)")
        print("  sim <input>    - Simulate player input")
        print("  quit           - Exit")

        while True:
            try:
                self.captured_output = []
                user_input = input("\nSIM> ").strip()
                if not user_input: continue

                parts = user_input.split(maxsplit=1)
                cmd = parts[0].lower()

                if cmd == "quit":
                    break
                elif cmd == "sanity":
                    if len(parts) > 1:
                        try:
                            val = float(parts[1])
                            self.game.player_state["sanity"] = val
                            print(f"Set SANITY to {val}")
                        except ValueError:
                            print("Invalid number")
                    else:
                        print(f"Current SANITY: {self.game.player_state['sanity']}")

                elif cmd == "reality":
                    if len(parts) > 1:
                        try:
                            val = float(parts[1])
                            self.game.player_state["reality"] = val
                            print(f"Set REALITY to {val}")
                        except ValueError:
                            print("Invalid number")
                    else:
                        print(f"Current REALITY: {self.game.player_state['reality']}")

                elif cmd == "sim":
                    if len(parts) > 1:
                        sim_input = parts[1]
                        print(f"--- Simulating: '{sim_input}' ---")
                        # We simulate the step
                        # The step method clears output, processes input, etc.
                        # We need to capture the output generated during process_command specifically
                        # logic inside game.step is complex, let's call process_command directly or the parser handler logic

                        # Use step to get full effects (including disassociation check)
                        # We need to mock output buffer clear too if step calls it
                        self.game.output.clear = lambda: None

                        self.game.step(sim_input)

                        for line in self.captured_output:
                            # Filter out UI noise if needed, but showing all is good
                            print(line)

                        # Analyze for specific reactions
                        if "You try to speak, but nothing comes out" in "".join(self.captured_output):
                            print(f"\n[ANALYSIS] >> DISASSOCIATION TRIGGERED (Low Sanity Effect)")

                        if "feel the need to scream" in "".join(self.captured_output):
                            print(f"\n[ANALYSIS] >> EMOTIONAL BLOCK (Sanity too high)")

                        if "scream into the void" in "".join(self.captured_output):
                            print(f"\n[ANALYSIS] >> CATHARSIS TRIGGERED (Low Sanity Action)")

                    else:
                        print("Usage: sim <command>")
                else:
                    print("Unknown command. Try 'sanity', 'reality', 'sim', or 'quit'.")

            except (EOFError, KeyboardInterrupt):
                break

if __name__ == "__main__":
    sim = StateSimulator()
    sim.run()
