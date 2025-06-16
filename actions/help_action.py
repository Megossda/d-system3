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
        NOTE: Action economy is handled by ActionExecutionSystem, not here.
        """
        # A full implementation would check the 5-foot range here.
        ally.help_effects['attack_advantage_against'] = target_enemy
        print(f"  > {performer.name} distracts {target_enemy.name}, preparing to help {ally.name}.")
        return True

    def assist_ability_check(self, performer, target_ally, skill_or_tool):
        """
        The performer assists an ally with a specific skill or tool check.
        Rule: "Choose one of your skill or tool proficiencies..."
        NOTE: Action economy is handled by ActionExecutionSystem, not here.
        """
        # A full implementation would check if the performer is proficient in the skill.
        target_ally.help_effects['ability_check_advantage_on'] = skill_or_tool.lower()
        print(f"  > {performer.name} prepares to help {target_ally.name} with their next '{skill_or_tool}' check.")
        return True
    
    def execute(self, performer, target=None, help_type="attack", ally=None, skill=None):
        """
        Execute the Help action with different variants.
        NOTE: Action economy is handled by ActionExecutionSystem, not here.
        """
        if help_type == "attack" and target and ally:
            return self.assist_attack_roll(performer, target, ally)
        elif help_type == "ability" and ally and skill:
            return self.assist_ability_check(performer, ally, skill)
        else:
            print(f"  > {performer.name} helps an ally (generic help).")
            return True