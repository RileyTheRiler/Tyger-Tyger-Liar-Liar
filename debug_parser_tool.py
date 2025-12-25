
import sys
import os

# Add src to path
sys.path.append(os.path.abspath("src"))

from engine.input_system import CommandParser

def debug_parser():
    parser = CommandParser()
    print("Type commands to see how they are parsed. Type 'quit' to exit.")

    while True:
        try:
            cmd = input("> ")
            if cmd.lower() in ["quit", "exit"]:
                break

            results = parser.normalize(cmd)
            if not results:
                print("No valid commands found.")

            for verb, target in results:
                print(f"VERB: {verb}, TARGET: {target}")

        except (EOFError, KeyboardInterrupt):
            break

if __name__ == "__main__":
    debug_parser()
