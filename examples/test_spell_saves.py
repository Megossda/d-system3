# File: examples/test_spell_saves.py
# Test script to verify the spell save fix works
import sys
import os

# Add the project root to Python path (go up one directory from examples/)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from creatures.base import Creature
from systems.character_abilities.spellcasting import SpellcastingManager
from spells.cantrips.acid_splash import acid_splash

# Create a test wizard with spellcasting
wizard = Creature(
    name="Test Wizard",
    level=5,
    ac=12,
    hp=30,
    speed=30,
    stats={'str': 10, 'dex': 14, 'con': 14, 'int': 16, 'wis': 12, 'cha': 10},
    proficiencies={'arcana', 'history'}  # No saving throw proficiencies
)

# Add spellcasting ability
SpellcastingManager.add_spellcasting(wizard, 'int')
SpellcastingManager.add_spell_to_creature(wizard, acid_splash)

# Create a test target with Dex save proficiency
rogue = Creature(
    name="Test Rogue",
    level=3,
    ac=14,
    hp=25,
    speed=30,
    stats={'str': 8, 'dex': 16, 'con': 12, 'int': 10, 'wis': 13, 'cha': 12},
    proficiencies={'stealth', 'acrobatics', 'dex_save'}  # Has Dex save proficiency
)

# Create a target without save proficiency
fighter = Creature(
    name="Test Fighter",
    level=3,
    ac=16,
    hp=30,
    speed=30,
    stats={'str': 16, 'dex': 12, 'con': 14, 'int': 10, 'wis': 11, 'cha': 10},
    proficiencies={'athletics', 'intimidation'}  # No save proficiencies
)

print("=== TESTING SPELL SAVE SYSTEM ===\n")

print(f"Wizard's spell save DC: {wizard.get_spell_save_dc()}")
print(f"Wizard's spell attack bonus: {wizard.get_spell_attack_bonus()}\n")

print("--- Test 1: Acid Splash vs Rogue (has Dex save proficiency) ---")
acid_splash.cast(wizard, [rogue], 0)

print("\n--- Test 2: Acid Splash vs Fighter (no save proficiency) ---")
acid_splash.cast(wizard, [fighter], 0)

print("\n--- Test 3: Multiple targets ---")
acid_splash.cast(wizard, [rogue, fighter], 0)

print("\n=== TEST COMPLETE ===")
print("You should see actual d20 rolls now instead of automatic failures!")