# File: actions/utilize_action.py
"""Implementation of the Utilize action."""

class UtilizeAction:
    """Represents the Utilize action for using an object."""
    def __init__(self):
        self.name = "Utilize"

    def execute(self, performer, object_name):
        """
        The performer uses their action to interact with a specific object.
        The outcome would depend on the object being used.
        NOTE: Action economy is handled by ActionExecutionSystem, not here.
        """
        print(f"  > {performer.name} uses their action to interact with '{object_name}'.")
        # In a full game, this is where you would trigger the object's specific effect,
        # such as pulling a lever, drinking a potion, etc.
        return True