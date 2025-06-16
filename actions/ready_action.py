# File: actions/ready_action.py
"""Implementation of the Ready action."""

class ReadyAction:
    """Represents the Ready action."""
    def __init__(self):
        self.name = "Ready"

    def execute(self, performer, trigger_description, action_to_ready, target=None):
        """
        The performer readies an action to be used in response to a trigger.
        NOTE: Action economy is handled by ActionExecutionSystem, not here.
        """
        performer.readied_action['trigger'] = trigger_description
        performer.readied_action['action'] = action_to_ready
        performer.readied_action['target'] = target
        
        print(f"  > {performer.name} is now waiting for: '{trigger_description}'")
        print(f"  > They will respond by using the '{action_to_ready.name}' action.")
        return True