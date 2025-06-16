# File: actions/dash_action.py
"""Implementation of the Dash action."""

class DashAction:
    """Represents the Dash action."""
    def __init__(self):
        self.name = "Dash"

    def execute(self, performer):
        """
        The performer gains extra movement equal to their current speed
        (after any modifiers are applied).
        """
        print(f"\n--- {performer.name}'s Action: Dash ---")
        
        # --- THIS IS THE FIX ---
        # The extra movement gained is equal to the creature's current speed,
        # which might be affected by other conditions or effects.
        # For our current system, this is still the base speed, but the logic
        # is now compliant with the glossary rule for future expansion.
        extra_movement = performer.speed
        
        performer.movement_for_turn += extra_movement
        print(f"  > {performer.name} gains {extra_movement} feet of extra movement.")
        print(f"  > Total movement for this turn: {performer.movement_for_turn} feet.")
        return True