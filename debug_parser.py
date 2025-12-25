import sys
import os

sys.path.append(os.path.abspath("src"))
from engine.input_system import CommandParser

p = CommandParser()

def check(inp):
    print(f"\nScanning: '{inp}'")
    try:
        res = p.normalize(inp)
        print(f"Result: {res}")
    except Exception as e:
        print(f"ERROR: {e}")

check("look at desk then take book")
check("talk to priest")
check("use camera on blood")
