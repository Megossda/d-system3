# File: actions/spell_actions.py
"""Spell casting actions."""

# This is a placeholder for a real Action class
class Action:
    def __init__(self, name):
        self.name = name

class CastSpellAction(Action):
    """Generic spell casting action."""

    def __init__(self, spell, targets=None, spell_level=None):
        super().__init__(f"Cast {spell.name}")
        self.spell = spell
        self.targets = targets
        self.spell_level = spell_level

    def execute(self, performer, target=None, action_type="ACTION"):
        """
        Execute spell casting.
        NOTE: Action economy is handled by ActionExecutionSystem, not here.
        """
        from systems.spell_system.spell_manager import SpellManager

        spell_targets = self.targets if self.targets is not None else target

        return SpellManager.cast_spell(
            caster=performer,
            spell=self.spell,
            targets=spell_targets,
            spell_level=self.spell_level,
            action_type=action_type
        )