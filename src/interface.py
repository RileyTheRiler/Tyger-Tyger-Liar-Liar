
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"

    # Semantic Colors
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"

    # Specific Game Semantic

    # Exact colors are less relevant for web (handled by frontend CSS), keeping for CLI compat
    SANITY = "\033[36m" # Cyan
    REALITY = "\033[35m" # Magenta
    SKILL = "\033[33m" # Yellow
    ITEM = "\033[32m" # Green

def print_separator(char="=", length=60, color=Colors.CYAN, printer=print):
    printer(f"{color}{char * length}{Colors.RESET}")

def print_boxed_title(text, width=60, color=Colors.CYAN, printer=print):
    text = text.upper()
    printer(f"\n{color}" + "╔" + "═" * (width - 2) + "╗")
    
    # Handle multi-line if needed, but usually just one line for titles
    padding = (width - 2 - len(text)) // 2
    extra = (width - 2 - len(text)) % 2
    printer("║" + " " * padding + f"{Colors.WHITE}{Colors.BOLD}{text}{Colors.RESET}{color}" + " " * (padding + extra) + "║")
    
    printer("╚" + "═" * (width - 2) + "╝" + f"{Colors.RESET}")

def print_numbered_list(title, items, offset=0, color=Colors.GREEN, printer=print):
    if not items:
        return
    
    printer(f"\n{Colors.BOLD}[{title}]{Colors.RESET}")
    for idx, item in enumerate(items):
        if isinstance(item, str):
            printer(f" {color}{idx + offset + 1}. {item}{Colors.RESET}")
        elif isinstance(item, dict):
            text = item.get("text", "...")
            enabled = item.get("enabled", True)
            reason = item.get("reason", "")
            status = "" if enabled else f" {Colors.RED}(LOCKED: {reason}){Colors.RESET}"
            item_color = color if enabled else Colors.RED
            printer(f" {item_color}{idx + offset + 1}. {text}{status}{Colors.RESET}")

def format_skill_result(result, printer=print):
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
    
    color = Colors.GREEN if success else Colors.RED
    status = ">> SUCCESS <<" if success else ">> FAILURE <<"

    printer(f"\n{Colors.SKILL}[ CHECK: {skill} ]{Colors.RESET}")
    printer(f" Roll: {roll} (2d6) {mod_sign}{mod} [Skill]{inv_str} = {total} vs DC {dc}")
    if desc:
        printer(f" {desc}")
    
    printer(f" {color}{status}{Colors.RESET}")
