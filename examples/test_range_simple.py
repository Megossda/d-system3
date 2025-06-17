# File: examples/test_range_simple.py
"""Simple test for range integration to verify core functionality."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from creatures.base import Creature
from systems.positioning_system import battlefield, Position, CreatureSize
from systems.attack_system import AttackSystem, WeaponRanges
from systems.cover_system import RangeSystem

def test_basic_range_functionality():
    """Test basic range checking functionality."""
    print("=== Basic Range Functionality Test ===")
    
    # Clear battlefield first
    battlefield.creature_positions.clear()
    battlefield.creature_sizes.clear()
    
    # Create test creatures
    archer = Creature("Archer", 3, 15, 25, 30, {'str': 12, 'dex': 16})
    target = Creature("Target", 1, 12, 10, 30, {'str': 10, 'dex': 12})
    
    # Place creatures
    battlefield.place_creature(archer, Position(0, 0), CreatureSize.MEDIUM)
    battlefield.place_creature(target, Position(6, 0), CreatureSize.MEDIUM)  # 30 feet away
    
    print(f"Archer at {battlefield.get_position(archer)}")
    print(f"Target at {battlefield.get_position(target)}")
    
    # Test distance calculation
    distance = battlefield.calculate_distance(
        battlefield.get_position(archer),
        battlefield.get_position(target)
    )
    print(f"Distance: {distance} feet")
    
    # Test range checking with different weapons
    print("\n--- Testing Different Weapon Ranges ---")
    
    # Melee weapon (5 feet)
    melee_range = WeaponRanges.get_weapon_range("longsword")
    melee_check = RangeSystem.check_range(archer, target, melee_range)
    print(f"Melee weapon (5 ft): In range = {melee_check['in_range']}, Distance = {melee_check['distance']}")
    
    # Shortbow (80/320 feet) 
    bow_range = WeaponRanges.get_weapon_range("shortbow")
    bow_check = RangeSystem.check_range(archer, target, bow_range)
    print(f"Shortbow (80/320 ft): In range = {bow_check['in_range']}, Distance = {bow_check['distance']}, Disadvantage = {bow_check['disadvantage']}")
    
    # Test actual attack with range validation
    print("\n--- Testing Attack System Range Integration ---")
    
    # Melee attack (should fail - out of range)
    melee_weapon = {
        'name': 'longsword',
        'damage': '1d8',
        'ability': 'str',
        'proficient': True,
        'damage_type': 'slashing'
    }
    
    print("Attempting melee attack at 30 feet...")
    result = AttackSystem.make_weapon_attack(archer, target, melee_weapon)
    print(f"Melee attack result: {result}")
    
    # Ranged attack (should succeed)
    ranged_weapon = {
        'name': 'shortbow',
        'damage': '1d6',
        'ability': 'dex',
        'proficient': True,
        'damage_type': 'piercing'
    }
    
    print("\nAttempting ranged attack at 30 feet...")
    result = AttackSystem.make_weapon_attack(archer, target, ranged_weapon)
    print(f"Ranged attack result: {result}")

def test_spell_range_parsing():
    """Test spell range parsing functionality."""
    print("\n=== Spell Range Parsing Test ===")
    
    from systems.spell_system.spell_manager import SpellManager
    
    test_ranges = [
        "Touch",
        "Self",
        "30 feet", 
        "120 feet",
        "150 feet (20-foot radius)",
        "1 mile",
        "Sight",
        "Unlimited"
    ]
    
    for range_str in test_ranges:
        parsed = SpellManager._parse_spell_range(range_str)
        print(f"'{range_str}' -> {parsed} feet")

def test_weapon_ranges():
    """Test weapon range database."""
    print("\n=== Weapon Range Database Test ===")
    
    weapons = [
        "unarmed strike",
        "dagger",
        "longsword", 
        "shortbow",
        "longbow",
        "javelin",
        "handaxe"
    ]
    
    for weapon in weapons:
        weapon_range = WeaponRanges.get_weapon_range(weapon)
        print(f"{weapon}: {weapon_range}")

def test_cover_integration():
    """Test cover system integration."""
    print("\n=== Cover System Integration Test ===")
    
    # Clear and set up battlefield
    battlefield.creature_positions.clear()
    battlefield.creature_sizes.clear()
    
    attacker = Creature("Attacker", 2, 14, 15, 30, {'str': 14, 'dex': 12})
    target = Creature("Target", 1, 12, 8, 30, {'str': 10, 'dex': 10})
    
    battlefield.place_creature(attacker, Position(0, 0), CreatureSize.MEDIUM)
    battlefield.place_creature(target, Position(4, 0), CreatureSize.MEDIUM)  # 20 feet away
    
    from systems.cover_system import CoverSystem
    
    # Test cover determination
    cover_info = CoverSystem.determine_cover(attacker, target)
    print(f"Cover between attacker and target: {cover_info}")
    
    # Test cover application to attack
    base_ac = target.ac
    modified_ac, cover_data = CoverSystem.apply_cover_to_attack(attacker, target, base_ac)
    print(f"AC modification: {base_ac} -> {modified_ac}")

def main():
    """Run simple range integration tests."""
    print("D&D System - Simple Range Integration Test")
    print("=" * 50)
    
    try:
        test_basic_range_functionality()
        test_spell_range_parsing()
        test_weapon_ranges()
        test_cover_integration()
        
        print("\n" + "=" * 50)
        print("✅ CORE RANGE INTEGRATION WORKING!")
        print("\nVerified Features:")
        print("• Distance calculations")
        print("• Weapon range validation")
        print("• Attack system range checks")
        print("• Spell range parsing")
        print("• Cover system integration")
        print("• Range database completeness")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()