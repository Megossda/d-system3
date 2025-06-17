import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from creatures.base import Creature
from systems.positioning_system import battlefield, Position, CreatureSize
from systems.attack_system import AttackSystem

print("=== Range Testing ===")

# Clear battlefield
battlefield.creature_positions.clear()
battlefield.creature_sizes.clear()

# Set up creatures
archer = Creature("Archer", 3, 15, 25, 30, {'dex': 16})
target = Creature("Target", 1, 12, 10, 30, {'str': 10})

# Place them on battlefield
battlefield.place_creature(archer, Position(0, 0))
battlefield.place_creature(target, Position(20, 0))  # 100 feet away

print(f"Distance: {battlefield.calculate_distance(battlefield.get_position(archer), battlefield.get_position(target))} feet")

# Try melee attack (should fail - out of range)
melee = {'name': 'sword', 'damage': '1d8', 'ability': 'str', 'damage_type': 'slashing'}
print("\nMelee attack at 100 feet:")
result1 = AttackSystem.make_weapon_attack(archer, target, melee)
print(f"Result: {result1}")

# Try ranged attack (should work)
bow = {'name': 'longbow', 'damage': '1d8', 'ability': 'dex', 'damage_type': 'piercing'}
print("\nLongbow attack at 100 feet:")
result2 = AttackSystem.make_weapon_attack(archer, target, bow)
print(f"Result: {result2}")

print("\n=== Test Complete ===")