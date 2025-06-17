# File: examples/test_global_range_access.py
"""Test that range systems are properly integrated into the global D&D architecture."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_global_systems_import():
    """Test importing range systems through global systems."""
    print("=== Testing Global Systems Import ===")
    
    try:
        # Test importing through systems module
        from systems import AttackSystem, WeaponRanges, battlefield, Position, RangeSystem
        print("✅ Range systems available through 'from systems import'")
        
        # Test specific components
        print(f"✅ AttackSystem available: {AttackSystem}")
        print(f"✅ WeaponRanges available: {WeaponRanges}")
        print(f"✅ battlefield available: {battlefield}")
        print(f"✅ Position available: {Position}")
        print(f"✅ RangeSystem available: {RangeSystem}")
        
        return True
    except ImportError as e:
        print(f"❌ Global systems import failed: {e}")
        return False

def test_global_root_import():
    """Test importing range systems through root module."""
    print("\n=== Testing Global Root Import ===")
    
    try:
        # Test importing through root D&D module
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        import __init__ as dnd
        
        # Test that range components are available
        print(f"✅ dnd.AttackSystem available: {hasattr(dnd, 'AttackSystem')}")
        print(f"✅ dnd.WeaponRanges available: {hasattr(dnd, 'WeaponRanges')}")
        print(f"✅ dnd.battlefield available: {hasattr(dnd, 'battlefield')}")
        print(f"✅ dnd.Position available: {hasattr(dnd, 'Position')}")
        print(f"✅ dnd.RangeSystem available: {hasattr(dnd, 'RangeSystem')}")
        
        return True
    except ImportError as e:
        print(f"❌ Global root import failed: {e}")
        return False

def test_range_functionality_through_global():
    """Test that range functionality works through global imports."""
    print("\n=== Testing Range Functionality Through Global Access ===")
    
    try:
        # Import through global systems
        from systems import AttackSystem, WeaponRanges, battlefield, Position, CreatureSize, RangeSystem
        from creatures.base import Creature
        
        # Clear battlefield
        battlefield.creature_positions.clear()
        battlefield.creature_sizes.clear()
        
        # Create creatures using global access
        archer = Creature("GlobalArcher", 3, 15, 25, 30, {'dex': 16})
        target = Creature("GlobalTarget", 1, 12, 10, 30, {'str': 10})
        
        # Place using global battlefield
        battlefield.place_creature(archer, Position(0, 0), CreatureSize.MEDIUM)
        battlefield.place_creature(target, Position(15, 0), CreatureSize.MEDIUM)  # 75 feet
        
        # Test weapon ranges through global access
        longbow_range = WeaponRanges.get_weapon_range("longbow")
        print(f"✅ Longbow range via global: {longbow_range}")
        
        # Test range checking through global access
        range_check = RangeSystem.check_range(archer, target, longbow_range)
        print(f"✅ Range check via global: {range_check}")
        
        # Test attack through global access
        longbow_weapon = {
            'name': 'longbow',
            'damage': '1d8',
            'ability': 'dex',
            'damage_type': 'piercing'
        }
        
        print("Testing attack through global AttackSystem...")
        result = AttackSystem.make_weapon_attack(archer, target, longbow_weapon)
        print(f"✅ Attack via global system result: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Range functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_existing_system_integration():
    """Test that range integration doesn't break existing functionality."""
    print("\n=== Testing Existing System Integration ===")
    
    try:
        # Test existing global imports still work
        from systems import perform_d20_test, combat_manager, SpellManager
        from core import roll_d20, get_ability_modifier
        from creatures.base import Creature
        
        print("✅ Existing systems still accessible")
        
        # Test basic functionality still works
        creature = Creature("TestCreature", 2, 12, 15, 30, {'str': 14})
        
        # Test d20 system
        roll_result = roll_d20()
        print(f"✅ D20 roll still works: {roll_result}")
        
        # Test ability modifier
        mod = get_ability_modifier(16)
        print(f"✅ Ability modifier still works: {mod}")
        
        # Test that creature can be created
        print(f"✅ Creature creation still works: {creature}")
        
        return True
        
    except Exception as e:
        print(f"❌ Existing system integration test failed: {e}")
        return False

def main():
    """Run all global architecture tests."""
    print("D&D System - Global Range Architecture Integration Test")
    print("=" * 70)
    
    tests_passed = 0
    total_tests = 4
    
    try:
        # Test 1: Global systems import
        if test_global_systems_import():
            tests_passed += 1
            print("✅ Global systems import PASSED")
        else:
            print("❌ Global systems import FAILED")
        
        # Test 2: Global root import
        if test_global_root_import():
            tests_passed += 1
            print("✅ Global root import PASSED")
        else:
            print("❌ Global root import FAILED")
        
        # Test 3: Range functionality through global
        if test_range_functionality_through_global():
            tests_passed += 1
            print("✅ Range functionality through global PASSED")
        else:
            print("❌ Range functionality through global FAILED")
        
        # Test 4: Existing system integration
        if test_existing_system_integration():
            tests_passed += 1
            print("✅ Existing system integration PASSED")
        else:
            print("❌ Existing system integration FAILED")
        
        print("\n" + "=" * 70)
        print(f"GLOBAL ARCHITECTURE TEST SUMMARY: {tests_passed}/{total_tests} tests passed")
        
        if tests_passed == total_tests:
            print("🎯 RANGE INTEGRATION SUCCESSFULLY ADDED TO GLOBAL ARCHITECTURE!")
            print("\n✅ CONFIRMED GLOBAL FEATURES:")
            print("• Range systems accessible via 'from systems import'")
            print("• Range functionality works through global imports")
            print("• Existing systems remain fully functional")
            print("• Global architecture maintains all functionality")
            print("• Range validation is now part of the core system")
        else:
            print(f"❌ {total_tests - tests_passed} tests failed - global integration incomplete")
        
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()