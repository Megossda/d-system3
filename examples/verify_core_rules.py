import sys
import os

# This line ensures the script can find the other project files
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the functions we are testing from our global system
from core.utils import get_ability_modifier, roll_dice, roll_d100, roll_d3

def run_verification():
    """Runs a series of tests to verify core rule implementations."""
    
    print("--- Verifying Core D&D Rules Engine ---")

    # --- Test 1: Ability Modifiers ---
    print("\n[1] Testing Ability Score to Modifier conversion:")
    # Test cases based on the PHB table 
    test_scores = {1: -5, 8: -1, 10: 0, 11: 0, 15: 2, 17: 3, 20: 5}
    all_modifiers_correct = True
    for score, expected_mod in test_scores.items():
        calculated_mod = get_ability_modifier(score)
        status = "OK" if calculated_mod == expected_mod else "FAIL"
        if status == "FAIL":
            all_modifiers_correct = False
        print(f"  - Score {score}: Expected Modifier {expected_mod}, Got {calculated_mod} -> {status}")
    
    if all_modifiers_correct:
        print("  => VERIFICATION PASSED: Ability modifiers are 100% compliant.")
    else:
        print("  => VERIFICATION FAILED: Mismatch in ability modifier calculation.")

    # --- Test 2: Dice Notation Rolling ---
    print("\n[2] Testing Dice Notation (e.g., '3d6+5'):")
    # We can't test the exact random result, but we can check if it's in the valid range.
    roll_notation = "2d8+5"
    result = roll_dice(roll_notation)
    min_possible = (2 * 1) + 5
    max_possible = (2 * 8) + 5
    status = "OK" if min_possible <= result <= max_possible else "FAIL"
    print(f"  - Rolling '{roll_notation}': Got {result} (Range: {min_possible}-{max_possible}) -> {status}")
    
    if status == "OK":
        print(f"  => VERIFICATION PASSED: Dice notation rolling is working.")
    else:
        print(f"  => VERIFICATION FAILED: Dice notation roll was out of range.")
        
    # --- Test 3: Special Dice Rolls ---
    print("\n[3] Testing Special Dice (d100 and d3):")
    
    # d100 Test
    d100_result = roll_d100()
    d100_status = "OK" if 1 <= d100_result <= 100 else "FAIL"
    print(f"  - Rolling d100: Got {d100_result} -> {d100_status}")

    # d3 Test
    d3_result = roll_d3()
    d3_status = "OK" if 1 <= d3_result <= 3 else "FAIL"
    print(f"  - Rolling d3: Got {d3_result} -> {d3_status}")

    if d100_status == "OK" and d3_status == "OK":
        print("  => VERIFICATION PASSED: Special dice are working correctly.")
    else:
        print("  => VERIFICATION FAILED: An error occurred with special dice.")

    print("\n--- Verification Complete ---")


if __name__ == "__main__":
    run_verification()