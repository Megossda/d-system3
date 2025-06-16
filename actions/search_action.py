# File: actions/search_action.py
"""Implementation of the Search action."""
from systems.d20_system import perform_d20_test

class SearchAction:
    """Represents the Search action, which uses various Wisdom skills."""
    def __init__(self):
        self.name = "Search"

    def execute(self, performer, skill_to_use, dc_to_beat=15):
        """
        The performer makes a Wisdom check using a specific skill (Insight, Medicine,
        Perception, or Survival) to find something.
        NOTE: Action economy is handled by ActionExecutionSystem, not here.
        """
        # The Search action is a Wisdom check using one of its associated skills.
        # Our global d20_system will handle the roll and check for proficiency.
        was_successful = perform_d20_test(
            creature=performer,
            ability_name='wis',
            check_type=skill_to_use.lower(), # e.g., 'perception'
            dc=dc_to_beat
        )
        
        if was_successful:
            print(f"  > {performer.name} found something!")
        else:
            print(f"  > {performer.name} found nothing.")

        return was_successful