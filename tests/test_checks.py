
import sys
import os

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from mechanics import SkillSystem

def test_red_check():
    print("\n--- Testing Red Check ---")
    sys = SkillSystem()
    skill_name = "Logic"
    
    # 1. First Attempt (Fail)
    # Roll 2 (1+1) + 0 < 100
    res1 = sys.roll_check(skill_name, 100, check_type="red", check_id="red_test_1", manual_roll=2)
    print(f"Attempt 1 Result: {res1['success']} (Expected False)")
    
    # 2. Second Attempt (Should be Blocked)
    res2 = sys.roll_check(skill_name, 100, check_type="red", check_id="red_test_1", manual_roll=12)
    print(f"Attempt 2 Blocked: {res2.get('blocked')} (Expected True)")
    
    # 3. Increase Skill & Try Again (Should still be Blocked)
    sys.increase_skill(skill_name, 5)
    res3 = sys.roll_check(skill_name, 100, check_type="red", check_id="red_test_1", manual_roll=12)
    print(f"Attempt 3 (Higher Skill) Blocked: {res3.get('blocked')} (Expected True)")

def test_white_check():
    print("\n--- Testing White Check ---")
    sys = SkillSystem()
    skill_name = "Logic"
    
    # 1. First Attempt (Fail)
    # Skill = 0. Roll 2. Total 2. Diff 10.
    res1 = sys.roll_check(skill_name, 10, check_type="white", check_id="white_test_1", manual_roll=2)
    print(f"Attempt 1 Result: {res1['success']} (Expected False)")
    print(f"Skill at attempt: {res1['skill_level_at_attempt']}")
    
    # 2. Retry without skill increase (Should be Blocked)
    res2 = sys.roll_check(skill_name, 10, check_type="white", check_id="white_test_1", manual_roll=12)
    print(f"Attempt 2 (Same Skill) Blocked: {res2.get('blocked')} (Expected True)")
    
    # 3. Increase Skill and Retry (Should be Allowed)
    print("Increasing Logic skill...")
    sys.increase_skill(skill_name, 1) # Base becomes 1
    # Skill = 1. Roll 10. Total 11 >= 10. Success.
    res3 = sys.roll_check(skill_name, 10, check_type="white", check_id="white_test_1", manual_roll=10)
    print(f"Attempt 3 (Higher Skill) Blocked: {res3.get('blocked')} (Expected False)")
    print(f"Attempt 3 Result: {res3['success']} (Expected True)")
    
    # 4. Retry after Success (Should report 'Already Succeeded')
    res4 = sys.roll_check(skill_name, 10, check_type="white", check_id="white_test_1", manual_roll=2)
    print(f"Attempt 4 (After Success): {res4.get('msg')} (Expected 'Already succeeded.')")

if __name__ == "__main__":
    test_red_check()
    test_white_check()
