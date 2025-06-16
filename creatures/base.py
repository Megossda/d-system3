# File: creatures/base.py
"""Base class for all creatures in the game."""
from core.utils import get_ability_modifier

class Creature:
    """A base representation of a creature."""
    
    def __init__(self, name, level, ac, hp, speed, stats, cr=0, proficiencies=None, attitude='Indifferent'):
        self.name = name
        self.level = level
        self.ac = ac
        self.max_hp = hp
        self.current_hp = hp
        self.speed = speed
        self.stats = stats
        self.cr = cr
        self.is_alive = True
        self.conditions = set()
        self.proficiencies = proficiencies or set()
        self.is_dodging = False
        self.is_disengaging = False
        
        self.help_effects = {
            'attack_advantage_against': None,
            'ability_check_advantage_on': None
        }
        
        self.movement_for_turn = speed
        
        self.readied_action = {
            'trigger': None,
            'action': None,
            'target': None
        }
        
        # --- NEW ---
        # Add an attribute for social attitude, defaulting to Indifferent.
        self.attitude = attitude
        
        self.proficiency_bonus = self._get_proficiency_bonus_from_level(level if level > 0 else cr)

    def start_turn(self):
        """Resets temporary turn-based effects."""
        self.movement_for_turn = self.speed
        self.is_dodging = False
        self.is_disengaging = False
        self.readied_action = {'trigger': None, 'action': None, 'target': None}
        print(f"\n--- {self.name}'s Turn Begins ---")
        print(f"  > Movement for turn reset to {self.movement_for_turn} feet.")

    def _get_proficiency_bonus_from_level(self, level):
        """Calculates proficiency bonus from level or CR."""
        if level <= 4: return 2
        elif level <= 8: return 3
        elif level <= 12: return 4
        elif level <= 16: return 5
        elif level <= 20: return 6
        return 7

    def get_ability_modifier(self, ability):
        """Gets the modifier for a given ability score."""
        return get_ability_modifier(self.stats.get(ability.lower(), 10))

    def take_damage(self, amount, attacker=None):
        """Reduces the creature's HP by the given amount."""
        self.current_hp -= amount
        print(f"  > {self.name} takes {amount} damage, remaining HP: {self.current_hp}/{self.max_hp}")
        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_alive = False
            print(f"  > {self.name} has been defeated!")
            
    def __str__(self):
        return f"{self.name} (AC: {self.ac}, HP: {self.current_hp}/{self.max_hp}, Attitude: {self.attitude})"