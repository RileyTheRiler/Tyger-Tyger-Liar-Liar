import sys
import os

print("CWD:", os.getcwd())
sys.path.append(os.path.abspath("src"))
sys.path.append(os.path.abspath("src/engine"))

try:
    print("Attempting to import mechanics...")
    import mechanics
    print("Mechanics imported.")
    
    print("Attempting to import inv_manager...")
    import inv_manager
    print("Inventory System imported:", inv_manager)
    
    print("Attempting to import game...")
    import game
    print("Game imported.")
    
except ImportError as e:
    print("ImportError:", e)
except Exception as e:
    print("Error:", e)
    import traceback
    traceback.print_exc()
