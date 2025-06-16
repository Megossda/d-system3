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
        
        # Social attitude for influence checks
        self.attitude = attitude
        
        self.proficiency_bonus = self._get_proficiency_bonus_from_level(level if level > 0 else cr)

    def start_turn(self):
        """Resets temporary turn-based effects and action economy."""
        # Reset temporary combat states
        self.is_dodging = False
        self.is_disengaging = False
        self.readied_action = {'trigger': None, 'action': None, 'target': None}
        
        # Use the action economy system to manage turn start
        from systems.action_economy import ActionEconomyManager
        economy = ActionEconomyManager.start_turn(self)
        
        print(f"\n--- {self.name}'s Turn Begins ---")
        return economy

    def can_take_action(self, action_type="action"):
        """Check if this creature can take a specific type of action."""
        from systems.action_economy import ActionEconomyManager
        return ActionEconomyManager.can_take_action(self, action_type)

    def use_action(self, action_name, action_type="action"):
        """Use an action, tracking it in the action economy system."""
        from systems.action_economy import ActionEconomyManager
        return ActionEconomyManager.use_action(self, action_name, action_type)

    def move(self, distance, movement_type="move"):
        """Move a certain distance, tracking it in the action economy system."""
        from systems.action_economy import ActionEconomyManager
        return ActionEconomyManager.use_movement(self, distance, movement_type)

    def get_action_economy_status(self):
        """Get the current action economy status."""
        from systems.action_economy import ActionEconomyManager
        economy = ActionEconomyManager.get_economy(self)
        return economy.get_status()

    def print_action_economy(self):
        """Print the current action economy status."""
        from systems.action_economy import ActionEconomyManager
        economy = ActionEconomyManager.get_economy(self)
        economy.print_status()

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
            
            # Clean up action economy when creature dies
            from systems.action_economy import ActionEconomyManager
            ActionEconomyManager.cleanup_dead_creatures()
            
    def __str__(self):
        return f"{self.name} (AC: {self.ac}, HP: {self.current_hp}/{self.max_hp}, Attitude: {self.attitude})"