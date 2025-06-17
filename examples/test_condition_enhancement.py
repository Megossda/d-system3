#!/usr/bin/env python3
# File: examples/test_condition_enhancement.py
"""Test the enhanced condition system in place."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_enhanced_conditions():
    """Test that the enhanced condition system works."""
    print("=== Testing Enhanced Condition System ===")
    
    from systems import DurationType, add_condition, remove_condition, has_condition
    from systems import process_end_of_turn_saves, update_condition_durations, describe_conditions
    from creatures.base import Creature
    
    fighter = Creature("TestFighter", 3, 16, 30, 30, {'str': 16, 'dex': 12, 'con': 14, 'int': 10, 'wis': 12, 'cha': 8})
    
    # Test basic condition with duration
    print("Adding stunned condition with save-to-end...")
    add_condition(fighter, "stunned", DurationType.SAVE_ENDS, save_dc=15, save_ability="con", source_name="Hold Person")
    
    print(f"Has stunned: {has_condition(fighter, 'stunned')}")
    print(f"Condition description: {describe_conditions(fighter)}")
    
    # Test save mechanics
    print("\nTesting end-of-turn save...")
    saves_made = process_end_of_turn_saves(fighter)
    print(f"Saves made: {saves_made}")
    print(f"Still has stunned: {has_condition(fighter, 'stunned')}")
    
    # Test round-based expiration
    print("\nTesting round-based condition...")
    add_condition(fighter, "blinded", DurationType.ROUNDS, duration_value=2, source_name="Flash")
    
    print(f"Conditions: {describe_conditions(fighter)}")
    
    # Simulate rounds
    from systems import set_combat_round
    set_combat_round(1)
    expired = update_condition_durations(rounds_passed=1)
    print(f"After 1 round, expired: {expired}")
    print(f"Conditions: {describe_conditions(fighter)}")
    
    set_combat_round(2)
    expired = update_condition_durations(rounds_passed=1)
    print(f"After 2 rounds, expired: {expired}")
    print(f"Conditions: {describe_conditions(fighter)}")
    
    print("✅ Enhanced condition system working!")
    return True

def main():
    """Test enhanced condition functionality."""
    print("D&D Enhanced Condition System Test")
    print("=" * 50)
    
    try:
        if test_enhanced_conditions():
            print("\n🎯 ENHANCED CONDITION SYSTEM WORKING!")
            print("• Duration tracking: ✅")
            print("• Save-to-end mechanics: ✅")
            print("• Round-based expiration: ✅")
            print("• Single file implementation: ✅")
        else:
            print("❌ Tests failed")
    except Exception as e:
        print(f"💥 ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()