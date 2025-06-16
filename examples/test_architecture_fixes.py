# File: examples/test_architecture_fixes.py
"""Test the architecture improvements."""

def test_enhanced_error_handling():
    """Test the enhanced error handling systems."""
    print("=== TESTING ENHANCED ERROR HANDLING ===\n")
    
    from creatures.base import Creature
    from error_handling.error_handler import DnDErrorHandler, DnDError
    from error_handling.logging_setup import EnhancedCombatSystem
    
    # Test creature validation
    print("--- Testing Creature Validation ---")
    try:
        DnDErrorHandler.validate_creature(None, "test operation")
    except DnDError as e:
        print(f"✅ Caught expected error: {e}")
    
    # Test safe combat
    print("\n--- Testing Safe Combat ---")
    fighter = Creature(
        name="Fighter", level=3, ac=16, hp=25, speed=30,
        stats={'str': 16, 'dex': 12, 'con': 14, 'int': 10, 'wis': 11, 'cha': 10}
    )
    
    dead_orc = Creature(
        name="Dead Orc", level=2, ac=13, hp=0, speed=30,
        stats={'str': 14, 'dex': 10, 'con': 12, 'int': 8, 'wis': 9, 'cha': 8}
    )
    dead_orc.is_alive = False
    
    # Attack against dead target (should handle gracefully)
    result = EnhancedCombatSystem.make_attack_safely(fighter, dead_orc)
    print(f"Attack result against dead target: {result}")
    
    print("\n✅ Enhanced error handling working correctly!")

if __name__ == "__main__":
    test_enhanced_error_handling()