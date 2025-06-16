# File: systems/spell_system/spell_manager.py
"""Spell Manager - Central hub for all spell operations."""

# --- FIX ---
# Corrected the import path to get the functions from 'core.utils'
from core.utils import roll_d20, get_ability_modifier


class SpellManager:
    """Central manager for all spell casting operations."""

    @staticmethod
    def cast_spell(caster, spell, targets=None, spell_level=None, action_type="ACTION"):
        """Universal spell casting interface."""
        if not SpellManager._can_cast_spell(caster, spell, spell_level):
            return False

        if spell_level is None:
            spell_level = spell.level

        # Consume spell slot for non-cantrips
        if spell.level > 0:
            if not SpellManager._consume_spell_slot(caster, spell_level):
                print(f"{caster.name} doesn't have a level {spell_level} spell slot!")
                return False

        print(f"{action_type}: {caster.name} casts {spell.name}!")
        return spell.cast(caster, targets, spell_level, action_type)

    @staticmethod
    def _can_cast_spell(caster, spell, spell_level):
        """Check if caster can cast the spell."""
        if not hasattr(caster, 'spell_slots'):
            return False
        if hasattr(caster, 'prepared_spells') and spell not in caster.prepared_spells:
            return False
        return True

    @staticmethod
    def _consume_spell_slot(caster, spell_level):
        """Consume a spell slot of the given level."""
        if caster.spell_slots.get(spell_level, 0) > 0:
            caster.spell_slots[spell_level] -= 1
            return True
        return False

    @staticmethod
    def make_spell_attack(caster, target, spell):
        """Make a spell attack using global systems."""
        # This will require a real combat system eventually. For now, it does nothing.
        pass

    @staticmethod
    def make_spell_save(target, caster, spell, save_type):
        """Make a saving throw against a spell."""
        # In a real test, you'd use a mock here. For now, we assume failure.
        save_dc = caster.get_spell_save_dc()
        # In a real system, you'd roll a d20 for the target and compare to save_dc
        print(f"  > {target.name} needs to beat a DC of {save_dc} for a {save_type.upper()} save.")
        return False

    @staticmethod
    def deal_spell_damage(target, damage, damage_type, caster, is_crit=False):
        """Deal spell damage to a target."""
        if is_crit:
            damage *= 2
            print(f"CRITICAL SPELL DAMAGE: {damage} {damage_type} damage!")
        else:
            print(f"SPELL DAMAGE: {damage} {damage_type} damage")
        target.take_damage(damage, attacker=caster)