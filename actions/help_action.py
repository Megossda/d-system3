# File: actions/help_action.py
"""Implementation of the Help action, with its two distinct uses."""

class HelpAction:
    """Represents the Help action."""
    def __init__(self):
        self.name = "Help"

    def assist_attack_roll(self, performer, target_enemy, ally):
        """
        The performer distracts an enemy, granting an ally advantage on their next attack.
        Rule: "You momentarily distract an enemy within 5 feet of you..."
        """
        # A full implementation would check the 5-foot range here.
        print(f"\n--- {performer.name}'s Action: Help (Assist Attack) ---")
        ally.help_effects['attack_advantage_against'] = target_enemy
        print(f"  > {performer.name} distracts {target_enemy.name}, preparing to help {ally.name}.")

    def assist_ability_check(self, performer, target_ally, skill_or_tool):
        """
        The performer assists an ally with a specific skill or tool check.
        Rule: "Choose one of your skill or tool proficiencies..."
        """
        # A full implementation would check if the performer is proficient in the skill.
        print(f"\n--- {performer.name}'s Action: Help (Assist Check) ---")
        target_ally.help_effects['ability_check_advantage_on'] = skill_or_tool.lower()
        print(f"  > {performer.name} prepares to help {target_ally.name} with their next '{skill_or_tool}' check.")