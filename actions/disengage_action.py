# File: actions/disengage_action.py
"""Implementation of the Disengage action."""

class DisengageAction:
    """Represents the Disengage action."""
    def __init__(self):
        self.name = "Disengage"

    def execute(self, performer):
        """
        The performer takes the Disengage action, preventing Opportunity Attacks.
        """
        print(f"\n--- {performer.name}'s Action: Disengage ---")
        performer.is_disengaging = True
        print(f"  > {performer.name}'s movement will not provoke opportunity attacks this turn.")
        return True