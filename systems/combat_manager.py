# File: systems/combat_manager.py
"""Combat Manager - Orchestrates complete D&D combat encounters."""

from systems.initiative_system import InitiativeTracker, InitiativeSystem
from systems.action_economy import ActionEconomyManager

class CombatState:
    """Represents the current state of a combat encounter."""
    def __init__(self):
        self.participants = []
        self.teams = {}  # team_name -> list of creatures
        self.environmental_effects = []
        self.combat_log = []
    
    def add_participant(self, creature, team_name="neutral"):
        """Add a creature to combat on a specific team."""
        self.participants.append(creature)
        if team_name not in self.teams:
            self.teams[team_name] = []
        self.teams[team_name].append(creature)
    
    def get_living_participants(self):
        """Get all living participants."""
        return [creature for creature in self.participants if creature.is_alive]
    
    def get_teams_status(self):
        """Get status of all teams."""
        status = {}
        for team_name, creatures in self.teams.items():
            living = [c for c in creatures if c.is_alive]
            status[team_name] = {
                'total': len(creatures),
                'living': len(living),
                'creatures': [c.name for c in living]
            }
        return status

class CombatManager:
    """Central system for managing D&D combat encounters."""
    
    def __init__(self):
        self.initiative_tracker = InitiativeTracker()
        self.combat_state = None
        self.auto_advance = False
    
    def setup_combat(self, participant_teams, surprised_creatures=None):
        """
        Set up a new combat encounter.
        
        Args:
            participant_teams: Dict of team_name -> list of creatures
            surprised_creatures: Set of surprised creatures
        
        Returns:
            CombatState: The initialized combat state
        """
        print("=== SETTING UP COMBAT ===")
        
        # Initialize combat state
        self.combat_state = CombatState()
        all_participants = []
        
        # Add all participants to combat state
        for team_name, creatures in participant_teams.items():
            print(f"Team '{team_name}': {[c.name for c in creatures]}")
            for creature in creatures:
                self.combat_state.add_participant(creature, team_name)
                all_participants.append(creature)
        
        # Start initiative tracking
        first_creature = self.initiative_tracker.start_combat(all_participants, surprised_creatures)
        
        # Start the first creature's turn
        if first_creature:
            self._start_creature_turn(first_creature)
        
        return self.combat_state
    
    def get_current_creature(self):
        """Get the creature whose turn it currently is."""
        return self.initiative_tracker.get_current_creature()
    
    def advance_turn(self):
        """
        Advance to the next creature's turn.
        
        Returns:
            Creature: The next creature to act, or None if combat ends
        """
        if not self.initiative_tracker.combat_active:
            return None
        
        # End current creature's turn
        current_creature = self.get_current_creature()
        if current_creature:
            self._end_creature_turn(current_creature)
        
        # Skip dead creatures and advance
        self.initiative_tracker.skip_dead_creatures()
        
        # Check if combat should end
        if self._check_combat_end():
            return None
        
        # Move to next turn
        next_creature = self.initiative_tracker.next_turn()
        
        if next_creature:
            self._start_creature_turn(next_creature)
        
        return next_creature
    
    def end_combat(self, reason="Combat concluded"):
        """End the current combat encounter."""
        print(f"\n{reason}")
        
        if self.combat_state:
            self._print_combat_summary()
        
        self.initiative_tracker.end_combat()
        self.combat_state = None
    
    def _start_creature_turn(self, creature):
        """Start a creature's turn."""
        print(f"\n{'='*60}")
        print(f"🎯 {creature.name}'s Turn (Round {self.initiative_tracker.round_number})")
        print(f"{'='*60}")
        
        # Use the creature's existing start_turn method
        creature.start_turn()
        
        # Show current status
        self._print_turn_status(creature)
    
    def _end_creature_turn(self, creature):
        """End a creature's turn."""
        # Clean up any end-of-turn effects
        ActionEconomyManager.cleanup_dead_creatures()
        
        # Log turn completion
        self.combat_state.combat_log.append(f"Round {self.initiative_tracker.round_number}: {creature.name} completed their turn")
    
    def _check_combat_end(self):
        """Check if combat should end based on team status."""
        if not self.combat_state:
            return True
        
        teams_status = self.combat_state.get_teams_status()
        living_teams = [team for team, status in teams_status.items() if status['living'] > 0]
        
        if len(living_teams) <= 1:
            # Combat ends when only one team (or no teams) remain
            if len(living_teams) == 1:
                winner = living_teams[0]
                self.end_combat(f"🏆 Team '{winner}' wins!")
            else:
                self.end_combat("💀 All participants defeated!")
            return True
        
        return False
    
    def _print_turn_status(self, creature):
        """Print the current turn status."""
        print(f"Current HP: {creature.current_hp}/{creature.max_hp}")
        
        if hasattr(creature, 'conditions') and creature.conditions:
            print(f"Conditions: {', '.join(creature.conditions)}")
        
        # Show initiative order context
        print(f"\n{self.initiative_tracker.get_turn_summary()}")
    
    def _print_combat_summary(self):
        """Print a summary of the combat encounter."""
        print("\n=== COMBAT SUMMARY ===")
        
        teams_status = self.combat_state.get_teams_status()
        for team_name, status in teams_status.items():
            print(f"Team '{team_name}': {status['living']}/{status['total']} survivors")
            if status['living'] > 0:
                print(f"  Survivors: {', '.join(status['creatures'])}")
        
        print(f"Combat lasted {self.initiative_tracker.round_number} rounds")
    
    def get_combat_status(self):
        """Get detailed status of the current combat."""
        if not self.combat_state or not self.initiative_tracker.combat_active:
            return "No active combat"
        
        status = {
            'round': self.initiative_tracker.round_number,
            'current_creature': self.get_current_creature().name if self.get_current_creature() else None,
            'teams': self.combat_state.get_teams_status(),
            'turn_order': [result.creature.name for result in self.initiative_tracker.turn_order if result.creature.is_alive]
        }
        
        return status
    
    def force_end_combat(self):
        """Force combat to end immediately."""
        self.end_combat("Combat forcibly ended")

# Singleton instance for global access
combat_manager = CombatManager()