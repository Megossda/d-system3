# File: systems/social_interaction_system.py
"""Social Interaction System - Manages NPC attitudes and social encounters."""

class SocialInteractionSystem:
    """Manages social interactions and NPC attitude changes."""
    
    # Attitude hierarchy for easy comparisons
    ATTITUDE_VALUES = {
        'Hostile': 0,
        'Indifferent': 1,
        'Friendly': 2
    }
    
    @staticmethod
    def set_attitude(creature, new_attitude):
        """Set a creature's attitude with validation."""
        if new_attitude in SocialInteractionSystem.ATTITUDE_VALUES:
            old_attitude = creature.attitude
            creature.attitude = new_attitude
            if old_attitude != new_attitude:
                print(f"  > {creature.name}'s attitude changed from {old_attitude} to {new_attitude}!")
            return True
        else:
            print(f"Invalid attitude: {new_attitude}")
            return False
    
    @staticmethod
    def improve_attitude(creature, steps=1):
        """Improve a creature's attitude by the specified number of steps."""
        current_value = SocialInteractionSystem.ATTITUDE_VALUES[creature.attitude]
        new_value = min(current_value + steps, 2)  # Cap at Friendly (2)
        
        new_attitude = [k for k, v in SocialInteractionSystem.ATTITUDE_VALUES.items() if v == new_value][0]
        SocialInteractionSystem.set_attitude(creature, new_attitude)
    
    @staticmethod
    def worsen_attitude(creature, steps=1):
        """Worsen a creature's attitude by the specified number of steps."""
        current_value = SocialInteractionSystem.ATTITUDE_VALUES[creature.attitude]
        new_value = max(current_value - steps, 0)  # Cap at Hostile (0)
        
        new_attitude = [k for k, v in SocialInteractionSystem.ATTITUDE_VALUES.items() if v == new_value][0]
        SocialInteractionSystem.set_attitude(creature, new_attitude)
    
    @staticmethod
    def get_social_dc(base_dc, target_attitude, interaction_type="persuasion"):
        """
        DEPRECATED: Calculate the DC for social interactions based on NPC attitude.
        
        This method is deprecated. Use perform_d20_test() with social_interaction_type 
        parameter for integrated social DC handling.
        
        D&D 2024 rules: Friendly NPCs are easier to influence, Hostile ones are harder.
        """
        import warnings
        warnings.warn(
            "get_social_dc() is deprecated. Use perform_d20_test() with social_interaction_type parameter instead.",
            DeprecationWarning,
            stacklevel=2
        )
        
        attitude_modifiers = {
            'Friendly': -2,    # Easier to influence friendly NPCs
            'Indifferent': 0,  # Standard DC
            'Hostile': +2      # Harder to influence hostile NPCs
        }
        
        # Some interaction types might have different modifiers
        if interaction_type == "intimidation" and target_attitude == "Hostile":
            # Hostile creatures might be less affected by intimidation
            attitude_modifiers['Hostile'] = +4
        
        modifier = attitude_modifiers.get(target_attitude, 0)
        final_dc = base_dc + modifier
        
        print(f"    > Social DC: {base_dc} (base) {modifier:+d} (attitude) = {final_dc}")
        return final_dc
    
    @staticmethod
    def can_attempt_social_interaction(performer, target):
        """Check if a social interaction is possible."""
        if not target.is_alive:
            print(f"  > Cannot interact with {target.name} - they are unconscious!")
            return False
        
        # Check for conditions that prevent social interaction
        if hasattr(target, 'conditions'):
            if 'charmed' in target.conditions:
                print(f"  > {target.name} is charmed and may respond unusually...")
            if 'frightened' in target.conditions:
                print(f"  > {target.name} is frightened and may be harder to reason with...")
        
        # Check language barriers (in a full system)
        # For now, assume everyone speaks Common
        
        return True
    
    @staticmethod
    def handle_critical_social_result(roll_result, dc, interaction_type):
        """Handle critical successes and failures in social interactions."""
        if roll_result == 20:
            print(f"  > Natural 20! Exceptional {interaction_type} result!")
            return "critical_success"
        elif roll_result == 1:
            print(f"  > Natural 1! {interaction_type.title()} backfires spectacularly!")
            return "critical_failure"
        elif roll_result >= dc + 5:
            print(f"  > Outstanding {interaction_type}! (Beat DC by 5+)")
            return "great_success"
        elif roll_result < dc - 5:
            print(f"  > {interaction_type.title()} fails badly! (Missed DC by 5+)")
            return "bad_failure"
        else:
            return "normal"

class SocialEncounter:
    """Represents a complete social encounter with an NPC."""
    
    def __init__(self, npc, initial_attitude=None):
        self.npc = npc
        if initial_attitude:
            SocialInteractionSystem.set_attitude(npc, initial_attitude)
        self.interaction_history = []
    
    def start_encounter(self):
        """Begin the social encounter."""
        print(f"\n=== Social Encounter with {self.npc.name} ===")
        print(f"Initial attitude: {self.npc.attitude}")
        return self
    
    def attempt_interaction(self, performer, action, **kwargs):
        """Attempt a social interaction and record the result."""
        if not SocialInteractionSystem.can_attempt_social_interaction(performer, self.npc):
            return False
        
        # Record the attempt
        interaction = {
            'performer': performer.name,
            'action': action.name,
            'attitude_before': self.npc.attitude,
            'result': None
        }
        
        # Perform the interaction
        result = action.execute(performer, self.npc, **kwargs)
        
        # Record the outcome
        interaction['result'] = result
        interaction['attitude_after'] = self.npc.attitude
        self.interaction_history.append(interaction)
        
        return result
    
    def get_encounter_summary(self):
        """Get a summary of the social encounter."""
        if not self.interaction_history:
            return f"No interactions attempted with {self.npc.name}"
        
        first_attitude = self.interaction_history[0]['attitude_before']
        final_attitude = self.npc.attitude
        
        summary = f"\n--- Social Encounter Summary: {self.npc.name} ---"
        summary += f"\nInitial attitude: {first_attitude}"
        summary += f"\nFinal attitude: {final_attitude}"
        summary += f"\nTotal interactions: {len(self.interaction_history)}"
        
        if first_attitude != final_attitude:
            if SocialInteractionSystem.ATTITUDE_VALUES[final_attitude] > SocialInteractionSystem.ATTITUDE_VALUES[first_attitude]:
                summary += "\n✅ Attitude improved!"
            else:
                summary += "\n❌ Attitude worsened!"
        else:
            summary += "\n➖ Attitude unchanged"
        
        return summary