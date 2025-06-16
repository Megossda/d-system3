# File: actions/dash_action.py
"""Implementation of the Dash action."""

class DashAction:
    """Represents the Dash action."""
    def __init__(self):
        self.name = "Dash"

    def execute(self, performer):
        """
        The performer gains extra movement equal to their current speed.
        NOTE: Action economy is handled by ActionExecutionSystem, not here.
        """
        # The extra movement gained is equal to the creature's current speed
        extra_movement = performer.speed
        
        performer.movement_for_turn += extra_movement
        print(f"  > {performer.name} gains {extra_movement} feet of extra movement.")
        print(f"  > Total movement for this turn: {performer.movement_for_turn} feet.")
        return True