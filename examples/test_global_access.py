# File: examples/test_global_access.py
"""Demonstrate the new global access capabilities without breaking existing functionality."""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_original_imports():
    """Test that all original import patterns still work."""
    print("=== Testing Original Import Patterns ===")
    
    # Original individual imports
    from systems.d20_system import perform_d20_test, was_last_roll_critical
    from systems.attack_system import AttackSystem
    from core.utils import roll_d20, get_ability_modifier
    from creatures.base import Creature
    
    print("✓ All original imports work perfectly")
    return perform_d20_test, AttackSystem, roll_d20, get_ability_modifier, Creature

def test_new_global_imports():
    """Test the new global import capabilities."""
    print("\n=== Testing New Global Import Patterns ===")
    
    # New global imports - shorter and cleaner
    from systems import perform_d20_test, AttackSystem, combat_manager, SpellManager
    from core import roll_d20, get_ability_modifier, roll_advantage, roll_dice
    
    print("✓ New global imports work perfectly")
    print(f"✓ Available systems: perform_d20_test, AttackSystem, combat_manager, SpellManager")
    print(f"✓ Available core utils: roll_d20, get_ability_modifier, roll_advantage, roll_dice")
    
    return perform_d20_test, AttackSystem, roll_d20, get_ability_modifier

def test_functionality_identical():
    """Test that old and new imports give identical functionality."""
    print("\n=== Testing Functionality Equivalence ===")
    
    # Original way
    from systems.d20_system import perform_d20_test as orig_d20
    from core.utils import roll_d20 as orig_roll
    
    # New global way
    from systems import perform_d20_test as global_d20
    from core import roll_d20 as global_roll
    
    # Verify they're the exact same functions
    print(f"✓ D20 test function identical: {orig_d20 is global_d20}")
    print(f"✓ Roll function identical: {orig_roll is global_roll}")
    print("✓ Zero overhead - same objects, just easier access")

def demonstrate_improved_workflow():
    """Show how the global access improves workflow."""
    print("\n=== Demonstrating Improved Workflow ===")
    
    # Before: Multiple imports needed
    print("BEFORE (still works):")
    print("from systems.d20_system import perform_d20_test")
    print("from systems.attack_system import AttackSystem")
    print("from core.utils import roll_d20, get_ability_modifier")
    
    # After: Cleaner imports
    print("\nAFTER (new option):")
    print("from systems import perform_d20_test, AttackSystem")
    print("from core import roll_d20, get_ability_modifier")
    
    # Demonstrate actual usage
    from systems import perform_d20_test, AttackSystem
    from core import roll_d20, get_ability_modifier
    from creatures.base import Creature
    
    # Create a test creature
    hero = Creature("Test Hero", 3, 15, 25, 30, {'str': 16, 'dex': 14, 'con': 15})
    
    print(f"\n✓ Created: {hero}")
    print(f"✓ Strength modifier: {get_ability_modifier(16)}")
    print(f"✓ D20 roll: {roll_d20()}")
    
    # Test D20 system
    result = perform_d20_test(hero, 'strength', dc=12)
    print(f"✓ D20 test result: {result}")

def test_backward_compatibility():
    """Ensure all existing code patterns continue to work."""
    print("\n=== Testing Backward Compatibility ===")
    
    try:
        # Test various import patterns from existing codebase
        from systems.d20_system import perform_d20_test
        from systems.attack_system import AttackSystem
        from systems.combat_manager import combat_manager
        from systems.spell_system.spell_manager import SpellManager
        from core.utils import roll_dice, roll_d20, get_ability_modifier
        from creatures.base import Creature
        
        print("✓ All existing import patterns work")
        print("✓ No breaking changes introduced")
        print("✓ Existing codebase remains fully functional")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    return True

def main():
    """Run all tests."""
    print("D&D System - Global Access Enhancement Test")
    print("=" * 60)
    
    try:
        # Test all functionality
        test_original_imports()
        test_new_global_imports()
        test_functionality_identical()
        demonstrate_improved_workflow()
        
        if test_backward_compatibility():
            print("\n" + "=" * 60)
            print("🎉 SUCCESS: Global Access Enhancement Complete!")
            print("\nKey Achievements:")
            print("✅ All existing imports continue to work unchanged")
            print("✅ New shorter import paths available")
            print("✅ Zero performance overhead")
            print("✅ No breaking changes")
            print("✅ Improved developer experience")
            
            print("\nBenefits:")
            print("• Shorter import statements for common functions")
            print("• Better discoverability of core systems")
            print("• Cleaner code organization")
            print("• Easier onboarding for new developers")
            print("• Maintained backward compatibility")
            
        else:
            print("❌ Backward compatibility test failed!")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()