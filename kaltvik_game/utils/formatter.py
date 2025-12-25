import time
import sys

def display_text(text, delay=0.02):
    """
    Displays text with optional character-by-character animation and line breaks.
    """
    print("\n", end="")
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        if delay:
            time.sleep(delay)
    print("\n")

def highlight_objects(text, objects):
    """
    Auto-detect keywords in scene text and surround them with markdown bold.
    """
    if not objects:
        return text
    
    # Sort keys by length descending to avoid partial matches (e.g., 'aurora' before 'aurora borealis')
    sorted_keys = sorted(objects.keys(), key=len, reverse=True)
    
    for key in sorted_keys:
        # Simple case-insensitive replacement (preserving original case could be complex)
        # For now, we follow the spec which is simple replace
        import re
        pattern = re.compile(re.escape(key), re.IGNORECASE)
        text = pattern.sub(f"**{key}**", text)
        
    return text
