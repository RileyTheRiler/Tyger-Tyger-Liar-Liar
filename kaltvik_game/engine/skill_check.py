import random

def roll_skill_check(skill_name, skill_level, difficulty, white_id=None, is_red=False, state=None):
    """
    Rolls a skill check: 2d6 + skill_level vs difficulty.
    - white_id: A unique ID for tracking white checks.
    - is_red: If True, it's a red check (cannot be retried, but doesn't lock if failed like white). 
      Actually, prompt says: "white/red checks (retry/no retry)".
      Usually:
      - White: Can be retried later (if skill increases). If it has a white_id, we track its success.
      - Red: Cannot be retried.
      Wait, the prompt snippet says:
      "if white_id and white_id in state.checked_whites: return ('locked', None)"
      And: "if white_id and not is_red: state.checked_whites.add(white_id)"
      This implies that for white checks, if successful OR attempted, it gets locked? 
      Actually, "retry/no retry" usually means:
      White = Retryable if you haven't succeeded yet (or if some condition is met).
      Red = One shot.
      
      The prompt logic:
      if result == "success": ...
      elif result == "fail": ...
      elif result == "locked": print("You’ve already tried this.")
      
      So if it's in `checked_whites`, it's "locked".
      The snippet adds to `checked_whites` if `not is_red`.
    """
    if white_id and state and white_id in state.checked_whites:
        return ("locked", None)

    die1 = random.randint(1, 6)
    die2 = random.randint(1, 6)
    roll_total = die1 + die2
    total = roll_total + skill_level
    success = total >= difficulty

    # Logic from prompt: White checks (not is_red) get added to checked_whites immediately?
    # Actually, usually you lock a white check UPON FAILURE until you level up.
    # But I will follow the provided logic:
    if white_id and state and not is_red:
        state.checked_whites.add(white_id)

    return ("success" if success else "fail", roll_total)
