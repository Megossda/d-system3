# File: systems/action_economy.py
"""Action Economy System - Tracks actions, bonus actions, movement, and reactions per turn."""

class ActionEconomy:
    """Manages action economy for a creature during combat."""
    
    def __init__(self, creature):
        self.creature = creature
        self.reset_turn()
    
    def reset_turn(self):
        """Reset action economy at the start of a turn."""
        self.action_used = False
        self.bonus_action_used = False
        self.reaction_used = False
        self.movement_used = 0
        self.free_object_interaction_used = False
        
        # Reset movement to creature's speed
        self.creature.movement_for_turn = self.creature.speed
        
        print(f"  > {self.creature.name}'s action economy reset for new turn")
    
    def can_take_action(self):
        """Check if the creature can take an action."""
        return not self.action_used and self.creature.is_alive
    
    def can_take_bonus_action(self):
        """Check if the creature can take a bonus action."""
        return not self.bonus_action_used and self.creature.is_alive
    
    def can_take_reaction(self):
        """Check if the creature can take a reaction."""
        return not self.reaction_used and self.creature.is_alive
    
    def can_move(self, distance):
        """Check if the creature can move the specified distance."""
        remaining_movement = self.creature.movement_for_turn - self.movement_used
        return remaining_movement >= distance and self.creature.is_alive
    
    def use_action(self, action_name="Action"):
        """Use the creature's action."""
        if not self.can_take_action():
            print(f"  > {self.creature.name} cannot take an action (already used or incapacitated)")
            return False
        
        self.action_used = True
        print(f"  > {self.creature.name} uses their Action: {action_name}")
        return True
    
    def use_bonus_action(self, action_name="Bonus Action"):
        """Use the creature's bonus action."""
        if not self.can_take_bonus_action():
            print(f"  > {self.creature.name} cannot take a bonus action (already used or incapacitated)")
            return False
        
        self.bonus_action_used = True
        print(f"  > {self.creature.name} uses their Bonus Action: {action_name}")
        return True
    
    def use_reaction(self, reaction_name="Reaction"):
        """Use the creature's reaction."""
        if not self.can_take_reaction():
            print(f"  > {self.creature.name} cannot take a reaction (already used or incapacitated)")
            return False
        
        self.reaction_used = True
        print(f"  > {self.creature.name} uses their Reaction: {reaction_name}")
        return True
    
    def use_movement(self, distance, movement_type="move"):
        """Use movement."""
        if not self.can_move(distance):
            remaining = self.creature.movement_for_turn - self.movement_used
            print(f"  > {self.creature.name} cannot move {distance} feet (only {remaining} feet remaining)")
            return False
        
        self.movement_used += distance
        remaining = self.creature.movement_for_turn - self.movement_used
        print(f"  > {self.creature.name} moves {distance} feet ({movement_type}). {remaining} feet remaining.")
        return True
    
    def use_free_object_interaction(self, interaction="interact with object"):
        """Use the free object interaction."""
        if self.free_object_interaction_used:
            print(f"  > {self.creature.name} has already used their free object interaction this turn")
            return False
        
        self.free_object_interaction_used = True
        print(f"  > {self.creature.name} uses their free object interaction: {interaction}")
        return True
    
    def get_status(self):
        """Get the current action economy status."""
        status = {
            'action': 'Used' if self.action_used else 'Available',
            'bonus_action': 'Used' if self.bonus_action_used else 'Available', 
            'reaction': 'Used' if self.reaction_used else 'Available',
            'movement': f"{self.movement_used}/{self.creature.movement_for_turn} feet used",
            'free_interaction': 'Used' if self.free_object_interaction_used else 'Available'
        }
        return status
    
    def print_status(self):
        """Print the current action economy status."""
        status = self.get_status()
        print(f"\n--- {self.creature.name}'s Action Economy ---")
        for resource, state in status.items():
            print(f"  {resource.replace('_', ' ').title()}: {state}")


class ActionEconomyManager:
    """Global manager for action economy across all creatures."""
    
    _creature_economies = {}
    
    @classmethod
    def get_economy(cls, creature):
        """Get or create action economy for a creature."""
        if creature not in cls._creature_economies:
            cls._creature_economies[creature] = ActionEconomy(creature)
        return cls._creature_economies[creature]
    
    @classmethod
    def start_turn(cls, creature):
        """Start a creature's turn and reset their action economy."""
        economy = cls.get_economy(creature)
        economy.reset_turn()
        return economy
    
    @classmethod
    def can_take_action(cls, creature, action_type="action"):
        """Check if a creature can take a specific type of action."""
        economy = cls.get_economy(creature)
        
        if action_type.lower() == "action":
            return economy.can_take_action()
        elif action_type.lower() == "bonus_action":
            return economy.can_take_bonus_action()
        elif action_type.lower() == "reaction":
            return economy.can_take_reaction()
        else:
            return False
    
    @classmethod
    def use_action(cls, creature, action_name, action_type="action"):
        """Use an action for a creature."""
        economy = cls.get_economy(creature)
        
        if action_type.lower() == "action":
            return economy.use_action(action_name)
        elif action_type.lower() == "bonus_action":
            return economy.use_bonus_action(action_name)
        elif action_type.lower() == "reaction":
            return economy.use_reaction(action_name)
        else:
            print(f"Unknown action type: {action_type}")
            return False
    
    @classmethod
    def use_movement(cls, creature, distance, movement_type="move"):
        """Use movement for a creature."""
        economy = cls.get_economy(creature)
        return economy.use_movement(distance, movement_type)
    
    @classmethod
    def print_all_economies(cls):
        """Print action economy status for all tracked creatures."""
        print("\n=== ACTION ECONOMY STATUS ===")
        for creature, economy in cls._creature_economies.items():
            if creature.is_alive:
                economy.print_status()
    
    @classmethod
    def cleanup_dead_creatures(cls):
        """Remove action economies for dead creatures."""
        dead_creatures = [creature for creature in cls._creature_economies.keys() if not creature.is_alive]
        for creature in dead_creatures:
            del cls._creature_economies[creature]