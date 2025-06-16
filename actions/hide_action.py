# File: actions/hide_action.py
"""Implementation of the Hide action."""
from systems.d20_system import perform_d20_test

class HideAction:
    """Represents the Hide action."""
    def __init__(self):
        self.name = "Hide"

    def execute(self, performer, dc_to_beat=15):
        """
        The performer makes a Dexterity (Stealth) check against a given DC.
        This calls the global d20_system to resolve the check.
        NOTE: Action economy is handled by ActionExecutionSystem, not here.
        """
        # The Hide action is a Dexterity (Stealth) check.
        # We call our global system to handle the roll and proficiency.
        was_successful = perform_d20_test(
            creature=performer,
            ability_name='dex',
            check_type='stealth', # The system will check for 'stealth' proficiency
            dc=dc_to_beat
        )
        
        if was_successful:
            print(f"  > {performer.name} is now hidden!")
        else:
            print(f"  > {performer.name} failed to hide.")

        return was_successful