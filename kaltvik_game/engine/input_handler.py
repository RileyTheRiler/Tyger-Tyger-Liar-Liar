def get_player_input(scene, context_objects):
    raw = input(">> ").strip().lower()
    
    if raw.isdigit():
        idx = int(raw) - 1
        if "options" in scene and 0 <= idx < len(scene["options"]):
            return ("choice", idx)
        else:
            print("Invalid choice number.")
            return ("invalid", None)
    
    else:
        # Parser mode
        return parse_command(raw, context_objects)

def parse_command(command, objects):
    words = command.split()
    if not words:
        return ("invalid", None)
    
    verb = words[0]
    
    # Handle "look at object" or just "examine object"
    if verb == "look" and len(words) > 1 and words[1] == "at":
        target = " ".join(words[2:])
        verb = "examine"
    elif verb in ["examine", "look", "inspect"]:
        target = " ".join(words[1:]) if len(words) > 1 else ""
        verb = "examine"
    else:
        target = " ".join(words[1:]) if len(words) > 1 else ""

    if verb == "examine":
        if target in objects:
            return ("examine", target)
        elif not target:
            print(f"What do you want to examine?")
        else:
            print(f"You don't see any '{target}' here.")
        return ("invalid", None)
    
    elif verb in ["character", "stats", "sheet"]:
        return ("character", None)
    
    elif verb in ["theories", "board"]:
        return ("theories", None)
    
    elif verb == "internalize":
        if len(words) < 2:
            print("Usage: internalize [theory_id]")
            return ("invalid", None)
        return ("internalize", words[1])
        
    elif verb == "abandon":
        if len(words) < 2:
            print("Usage: abandon [theory_id]")
            return ("invalid", None)
        return ("abandon", words[1])

    elif verb == "advance":
        if len(words) < 2:
            print("Usage: advance [hours]")
            return ("invalid", None)
        try:
            hours = int(words[1])
            return ("advance", hours)
        except ValueError:
            print("Hours must be a number.")
            return ("invalid", None)

    elif verb == "roll":

        # roll [skill] [dc]
        if len(words) < 3:
            print("Usage: roll [skill] [dc]")
            return ("invalid", None)
        skill = words[1]
        try:
            dc = int(words[2])
            return ("roll", (skill, dc))
        except ValueError:
            print("DC must be a number.")
            return ("invalid", None)
            
    elif verb == "check":
        # check [skill]
        if len(words) < 2:
            print("Usage: check [skill]")
            return ("invalid", None)
        return ("check", words[1])

    elif verb in ["use", "take", "open"]:
        return ("action", (verb, target))
    
    else:
        print(f"Don't know how to '{command}'.")
        return ("invalid", None)

