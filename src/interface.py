
def print_separator(char="=", length=60):
    print(char * length)

def print_boxed_title(text, width=60):
    text = text.upper()
    print("\n" + "╔" + "═" * (width - 2) + "╗")
    
    # Handle multi-line if needed, but usually just one line for titles
    padding = (width - 2 - len(text)) // 2
    extra = (width - 2 - len(text)) % 2
    print("║" + " " * padding + text + " " * (padding + extra) + "║")
    
    print("╚" + "═" * (width - 2) + "╝")

def print_numbered_list(title, items, offset=0):
    if not items:
        return
    
    print(f"\n[{title}]")
    for idx, item in enumerate(items):
        if isinstance(item, str):
            print(f" {idx + offset + 1}. {item}")
        elif isinstance(item, dict):
            text = item.get("text", "...")
            enabled = item.get("enabled", True)
            reason = item.get("reason", "")
            status = "" if enabled else f" (LOCKED: {reason})"
            print(f" {idx + offset + 1}. {text}{status}")

def format_skill_result(result):
    skill = result.get("skill", "???").upper()
    roll = result.get("roll", 0)
    mod = result.get("modifier", 0)
    inv = result.get("inventory_mod", 0)
    total = result.get("total", 0)
    dc = result.get("difficulty", 0)
    success = result.get("success", False)
    
    mod_sign = "+" if mod >= 0 else ""
    inv_sign = "+" if inv > 0 else ""
    inv_str = f" {inv_sign}{inv} [Inv]" if inv != 0 else ""
    
    desc = result.get("description", "")
    
    print(f"\n[ CHECK: {skill} ]")
    print(f" Roll: {roll} (2d6) {mod_sign}{mod} [Skill]{inv_str} = {total} vs DC {dc}")
    if desc:
        print(f" {desc}")
    
    if success:
        print(" >> SUCCESS <<")
    else:
        print(" >> FAILURE <<")
