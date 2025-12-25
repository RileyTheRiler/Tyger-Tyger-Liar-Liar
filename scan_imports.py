import os

search_str = "inventory_system"
exclude = ["verify_episode_loading.py", "debug_import.py", "manual_verify.py"]

print(f"Scanning for '{search_str}' imports in .py files...")

found = False
for root, dirs, files in os.walk("."):
    if "__pycache__" in dirs:
        dirs.remove("__pycache__")
    
    for file in files:
        if file.endswith(".py") and file not in exclude:
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines):
                        if "import inventory_system" in line or "from inventory_system" in line:
                            print(f"[FOUND] {path}:{i+1}: {line.strip()}")
                            found = True
            except Exception as e:
                print(f"Error reading {path}: {e}")

if not found:
    print("No imports found (unexpected).")
