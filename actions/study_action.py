# File: actions/study_action.py
"""Implementation of the Study action."""
from systems.d20_system import perform_d20_test

class StudyAction:
    """Represents the Study action, which uses various Intelligence skills."""
    def __init__(self):
        self.name = "Study"

    def execute(self, performer, skill_to_use, dc_to_beat=15):
        """
        The performer makes an Intelligence check using a specific skill (Arcana, History, etc.)
        to recall or analyze information.
        NOTE: Action economy is handled by ActionExecutionSystem, not here.
        """
        # The Study action is an Intelligence check using one of its associated skills.
        was_successful = perform_d20_test(
            creature=performer,
            ability_name='int',
            check_type=skill_to_use.lower(), # e.g., 'history'
            dc=dc_to_beat
        )
        
        if was_successful:
            print(f"  > {performer.name} recalls a key piece of information!")
        else:
            print(f"  > {performer.name} cannot recall anything useful.")

        return was_successful