
import sys
import os
import json

# Add src to path
sys.path.append(os.path.abspath("src"))

from engine.input_system import CommandParser

def debug_parser():
    parser = CommandParser()
    print("--- Parser Debugger ---")
    print("Type commands to see how they are parsed. Type 'quit' to exit.")
    print("Type '/synonym <canonical> <synonym>' to temporarily add a synonym for testing.")

    while True:
        try:
            raw = input("> ")
            if raw.lower() in ["quit", "exit"]:
                break

            if raw.startswith("/synonym"):
                parts = raw.split()
                if len(parts) == 3:
                    canonical, synonym = parts[1], parts[2]
                    current = parser.scene_synonyms
                    if canonical not in current:
                        current[canonical] = []
                    current[canonical].append(synonym)
                    parser.set_scene_synonyms(current)
                    print(f"Added synonym: '{synonym}' -> '{canonical}'")
                else:
                    print("Usage: /synonym <canonical> <synonym>")
                continue

            print(f"Input: '{raw}'")

            # 1. Normalization
            results = parser.normalize(raw)
            if not results:
                print(" -> No valid verbs found.")

            for i, (verb, target) in enumerate(results):
                print(f" -> Command {i+1}:")
                print(f"    Verb:   {verb}")
                print(f"    Target: {target}")

        except (EOFError, KeyboardInterrupt):
            break

if __name__ == "__main__":
    debug_parser()
