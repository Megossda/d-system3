# File: examples/test_critical_hits.py
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from creatures.beasts.dire_wolf import DireWolf
from creatures.base import Creature
from systems.attack_system import AttackSystem

def test_critical_hits():
    """Test critical hit mechanics by making many attacks."""
    
    print("=== TESTING CRITICAL HIT SYSTEM ===\n")
    
    # Create a tough target that won't die easily
    target = Creature(
        name="Training Dummy",
        level=10,
        ac=10,  # Low AC so we hit often
        hp=200,  # High HP so it survives
        speed=0,
        stats={'str': 10, 'dex': 10, 'con': 20, 'int': 1, 'wis': 1, 'cha': 1}
    )
    
    attacker = Creature(
        name="Fighter",
        level=5,
        ac=16,
        hp=45,
        speed=30,
        stats={'str': 18, 'dex': 12, 'con': 14, 'int': 10, 'wis': 11, 'cha': 10},
        proficiencies={'longsword', 'athletics'}
    )
    
    longsword = {
        'name': 'longsword',
        'damage': '1d8',
        'ability': 'str',
        'proficient': True,
        'damage_type': 'slashing'
    }
    
    print("Making 10 attacks to test for critical hits...")
    print("(Looking for Natural 20s that deal extra damage)\n")
    
    crits = 0
    hits = 0
    
    for i in range(10):
        print(f"--- Attack {i+1} ---")
        if AttackSystem.make_weapon_attack(attacker, target, longsword):
            hits += 1
            # Check if it was a crit by looking at the damage output
            # (This is a simple test - in a real system you'd check the roll directly)
        print()
    
    print(f"Results: {hits} hits out of 10 attacks")
    print(f"Target remaining HP: {target.current_hp}/200")
    
    print("\n=== Testing Dire Wolf with Pack Tactics ===")
    dire_wolf = DireWolf()
    
    # Reset target
    target.current_hp = 200
    
    print("Dire Wolf gets advantage from pack tactics, increasing crit chance...")
    
    for i in range(5):
        print(f"--- Dire Wolf Attack {i+1} ---")
        dire_wolf.bite(target)
        print()
    
    print(f"Target remaining HP after wolf attacks: {target.current_hp}/200")
    
    print("\n=== CRITICAL HIT TEST COMPLETE ===")
    print("Look for 'CRITICAL HIT!' messages above!")

if __name__ == "__main__":
    test_critical_hits()