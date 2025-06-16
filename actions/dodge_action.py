# File: actions/dodge_action.py
"""Implementation of the Dodge action."""

class DodgeAction:
    """Represents the Dodge action."""
    def __init__(self):
        self.name = "Dodge"

    def execute(self, performer):
        """Sets the performer's state to dodging."""
        print(f"\n--- {performer.name}'s Action: Dodge ---")
        performer.is_dodging = True
        print(f"  > {performer.name} is now dodging. Attacks against them have disadvantage.")