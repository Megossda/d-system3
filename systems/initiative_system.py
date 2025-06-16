# File: systems/initiative_system.py
"""Initiative System - Manages combat turn order according to D&D 2024 rules."""

from systems.d20_system import perform_d20_test
from core.utils import roll_d20

class InitiativeResult:
    """Represents a creature's initiative roll result."""
    def __init__(self, creature, initiative_count, was_surprised=False):
        self.creature = creature
        self.initiative_count = initiative_count
        self.was_surprised = was_surprised
    
    def __str__(self):
        surprise_text = " (Surprised)" if self.was_surprised else ""
        return f"{self.creature.name}: {self.initiative_count}{surprise_text}"

class InitiativeSystem:
    """Manages initiative rolling and turn order."""
    
    @staticmethod
    def roll_initiative_for_creature(creature, surprised=False):
        """
        Roll initiative for a single creature.
        
        Args:
            creature: The creature rolling initiative
            surprised: Whether the creature is surprised (disadvantage)
        
        Returns:
            InitiativeResult: The creature's initiative result
        """
        print(f"--- {creature.name} rolls Initiative ---")
        
        # Surprised creatures have disadvantage on initiative
        has_disadvantage = surprised
        if surprised:
            print(f"  > {creature.name} is surprised and has disadvantage!")
        
        # Roll initiative using d20 system (Dexterity check)
        # Note: Initiative is a Dexterity ability check, not a skill check
        if has_disadvantage:
            roll1, roll2 = roll_d20(), roll_d20()
            d20_result = min(roll1, roll2)
            print(f"  > Rolling with Disadvantage: got {roll1}, {roll2}. Using {d20_result}")
        else:
            d20_result = roll_d20()
            print(f"  > Rolling 1d20: got {d20_result}")
        
        # Calculate initiative count: d20 + Dex modifier
        dex_modifier = creature.get_ability_modifier('dex')
        initiative_count = d20_result + dex_modifier
        
        print(f"  > Initiative: {d20_result} (roll) + {dex_modifier} (Dex) = {initiative_count}")
        
        return InitiativeResult(creature, initiative_count, surprised)
    
    @staticmethod
    def roll_initiative_for_group(creatures, surprised_creatures=None):
        """
        Roll initiative for a group of creatures.
        
        Args:
            creatures: List of creatures to roll for
            surprised_creatures: Set of creatures that are surprised
        
        Returns:
            List[InitiativeResult]: All initiative results
        """
        surprised_creatures = surprised_creatures or set()
        results = []
        
        print("=== ROLLING INITIATIVE ===")
        
        for creature in creatures:
            is_surprised = creature in surprised_creatures
            result = InitiativeSystem.roll_initiative_for_creature(creature, is_surprised)
            results.append(result)
        
        return results
    
    @staticmethod
    def determine_turn_order(initiative_results):
        """
        Determine turn order from initiative results, handling ties.
        
        Args:
            initiative_results: List of InitiativeResult objects
        
        Returns:
            List[InitiativeResult]: Sorted by initiative order (highest first)
        """
        print("\n=== DETERMINING TURN ORDER ===")
        
        # Sort by initiative count (descending), then by creature name for consistent tie-breaking
        sorted_results = sorted(
            initiative_results,
            key=lambda x: (x.initiative_count, x.creature.name),
            reverse=True
        )
        
        print("Turn order:")
        for i, result in enumerate(sorted_results, 1):
            surprise_text = " (Surprised)" if result.was_surprised else ""
            print(f"  {i}. {result.creature.name} (Initiative {result.initiative_count}){surprise_text}")
        
        return sorted_results
    
    @staticmethod
    def handle_surprise(ambushers, targets):
        """
        Determine which creatures are surprised in combat.
        
        Args:
            ambushers: List of creatures attempting to surprise
            targets: List of potential surprised creatures
        
        Returns:
            Set: Creatures that are surprised
        """
        surprised_creatures = set()
        
        print("\n=== CHECKING FOR SURPRISE ===")
        
        for ambusher in ambushers:
            for target in targets:
                # In a full system, this would involve Stealth vs Perception checks
                # For now, we'll use a simple system
                if hasattr(ambusher, 'is_hidden') and ambusher.is_hidden:
                    print(f"  > {target.name} is surprised by {ambusher.name}!")
                    surprised_creatures.add(target)
                else:
                    print(f"  > {target.name} notices {ambusher.name} - no surprise")
        
        return surprised_creatures

class InitiativeTracker:
    """Tracks initiative order and manages turn progression."""
    
    def __init__(self):
        self.turn_order = []
        self.current_turn_index = 0
        self.round_number = 1
        self.combat_active = False
    
    def start_combat(self, creatures, surprised_creatures=None):
        """
        Start combat by rolling initiative and setting turn order.
        
        Args:
            creatures: List of all creatures in combat
            surprised_creatures: Set of surprised creatures
        """
        print("\n🗡️  COMBAT BEGINS! 🗡️")
        
        # Roll initiative for all creatures
        initiative_results = InitiativeSystem.roll_initiative_for_group(creatures, surprised_creatures)
        
        # Determine turn order
        self.turn_order = InitiativeSystem.determine_turn_order(initiative_results)
        
        # Reset combat state
        self.current_turn_index = 0
        self.round_number = 1
        self.combat_active = True
        
        print(f"\n⚔️  ROUND {self.round_number} BEGINS! ⚔️")
        return self.get_current_creature()
    
    def get_current_creature(self):
        """Get the creature whose turn it currently is."""
        if not self.combat_active or not self.turn_order:
            return None
        return self.turn_order[self.current_turn_index].creature
    
    def get_current_initiative_result(self):
        """Get the current creature's initiative result."""
        if not self.combat_active or not self.turn_order:
            return None
        return self.turn_order[self.current_turn_index]
    
    def next_turn(self):
        """
        Advance to the next creature's turn.
        
        Returns:
            Creature: The next creature to act, or None if combat ends
        """
        if not self.combat_active:
            return None
        
        # Move to next creature
        self.current_turn_index += 1
        
        # Check if we've gone through all creatures (end of round)
        if self.current_turn_index >= len(self.turn_order):
            self.current_turn_index = 0
            self.round_number += 1
            print(f"\n⚔️  ROUND {self.round_number} BEGINS! ⚔️")
        
        # Check if combat should continue
        if self._should_end_combat():
            self.end_combat()
            return None
        
        return self.get_current_creature()
    
    def end_combat(self):
        """End the current combat."""
        print("\n🏁 COMBAT ENDS! 🏁")
        self.combat_active = False
        self.turn_order = []
        self.current_turn_index = 0
        self.round_number = 1
    
    def _should_end_combat(self):
        """Check if combat should end (all creatures on one side defeated)."""
        # In a full system, this would check team affiliations
        # For now, just check if any creatures are dead
        alive_creatures = [result.creature for result in self.turn_order if result.creature.is_alive]
        return len(alive_creatures) <= 1
    
    def get_turn_summary(self):
        """Get a summary of the current combat state."""
        if not self.combat_active:
            return "No active combat"
        
        current = self.get_current_creature()
        summary = f"Round {self.round_number} - {current.name}'s turn"
        
        # Show remaining creatures in turn order
        remaining_turns = []
        for i in range(self.current_turn_index + 1, len(self.turn_order)):
            creature = self.turn_order[i].creature
            if creature.is_alive:
                remaining_turns.append(creature.name)
        
        if remaining_turns:
            summary += f"\nRemaining this round: {', '.join(remaining_turns)}"
        
        return summary
    
    def skip_dead_creatures(self):
        """Skip any dead creatures in the turn order."""
        while (self.combat_active and 
               self.current_turn_index < len(self.turn_order) and 
               not self.get_current_creature().is_alive):
            print(f"  > Skipping {self.get_current_creature().name} (defeated)")
            self.current_turn_index += 1
            
            # Handle end of round
            if self.current_turn_index >= len(self.turn_order):
                self.current_turn_index = 0
                self.round_number += 1
                print(f"\n⚔️  ROUND {self.round_number} BEGINS! ⚔️")
                break