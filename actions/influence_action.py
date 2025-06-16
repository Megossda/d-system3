# File: actions/influence_action.py
"""Implementation of the Influence action."""
from systems.d20_system import perform_d20_test

class InfluenceAction:
    """Represents the Influence action, which uses various Charisma or Wisdom skills."""
    def __init__(self):
        self.name = "Influence"

    def execute(self, performer, target, skill_to_use, dc_to_beat=15):
        """The performer makes a check to influence a target using a specific skill."""
        print(f"\n--- {performer.name}'s Action: Influence ({skill_to_use.title()}) on {target.name} ---")
        
        ability = 'wis' if skill_to_use.lower() == 'animal_handling' else 'cha'
        
        was_successful = perform_d20_test(
            creature=performer,
            ability_name=ability,
            check_type=skill_to_use.lower(),
            dc=dc_to_beat,
            target=target,
            is_influence_check=True # Explicitly flag this as an influence check
        )
        
        if was_successful:
            print(f"  > {performer.name}'s attempt to influence {target.name} succeeded!")
        else:
            print(f"  > {performer.name}'s attempt to influence {target.name} failed.")

        return was_successful