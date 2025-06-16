# File: systems/character_abilities/spellcasting.py
"""Global spellcasting abilities system with improved validation."""

from core.utils import get_ability_modifier
from actions.spell_actions import CastSpellAction

class SpellcastingManager:
    """Manages spellcasting abilities for any creature."""

    @staticmethod
    def add_spellcasting(creature, spellcasting_ability='cha', spell_slots=None, prepared_spells=None):
        """Add spellcasting capabilities to any creature with proper validation."""
        creature.spellcasting_ability = spellcasting_ability
        creature.spell_slots = spell_slots or {}
        creature.prepared_spells = prepared_spells or []
        creature.concentrating_on = None

        # Add robust spellcasting calculation methods with proper error handling
        def get_spellcasting_modifier():
            """Get the spellcasting ability modifier with validation."""
            try:
                ability_score = creature.stats.get(creature.spellcasting_ability, 10)
                return get_ability_modifier(ability_score)
            except (AttributeError, KeyError):
                print(f"Warning: {creature.name} has invalid spellcasting ability '{creature.spellcasting_ability}'. Using 0.")
                return 0

        def get_spell_save_dc():
            """Calculate spell save DC with proper validation."""
            try:
                # Ensure proficiency bonus exists
                if not hasattr(creature, 'proficiency_bonus'):
                    # Calculate proficiency bonus from level if missing
                    level = getattr(creature, 'level', 1)
                    creature.proficiency_bonus = SpellcastingManager._calculate_proficiency_bonus(level)
                
                spellcasting_mod = get_spellcasting_modifier()
                dc = 8 + creature.proficiency_bonus + spellcasting_mod
                return dc
            except Exception as e:
                print(f"Error calculating spell save DC for {creature.name}: {e}. Using default DC 13.")
                return 13

        def get_spell_attack_bonus():
            """Calculate spell attack bonus with proper validation."""
            try:
                # Ensure proficiency bonus exists
                if not hasattr(creature, 'proficiency_bonus'):
                    level = getattr(creature, 'level', 1)
                    creature.proficiency_bonus = SpellcastingManager._calculate_proficiency_bonus(level)
                
                spellcasting_mod = get_spellcasting_modifier()
                bonus = creature.proficiency_bonus + spellcasting_mod
                return bonus
            except Exception as e:
                print(f"Error calculating spell attack bonus for {creature.name}: {e}. Using default +5.")
                return 5

        # Attach the methods to the creature
        creature.get_spellcasting_modifier = get_spellcasting_modifier
        creature.get_spell_save_dc = get_spell_save_dc
        creature.get_spell_attack_bonus = get_spell_attack_bonus

        # Validate the setup
        SpellcastingManager._validate_spellcasting_setup(creature)

    @staticmethod
    def _calculate_proficiency_bonus(level):
        """Calculate proficiency bonus from character level."""
        if level <= 4: 
            return 2
        elif level <= 8: 
            return 3
        elif level <= 12: 
            return 4
        elif level <= 16: 
            return 5
        elif level <= 20: 
            return 6
        else: 
            return 7

    @staticmethod
    def _validate_spellcasting_setup(creature):
        """Validate that spellcasting was set up correctly."""
        issues = []
        
        # Check spellcasting ability
        if not hasattr(creature, 'spellcasting_ability'):
            issues.append("Missing spellcasting_ability")
        elif creature.spellcasting_ability not in creature.stats:
            issues.append(f"Invalid spellcasting ability '{creature.spellcasting_ability}'")
        
        # Check proficiency bonus
        if not hasattr(creature, 'proficiency_bonus'):
            issues.append("Missing proficiency_bonus")
        
        # Check stats
        if not hasattr(creature, 'stats') or not creature.stats:
            issues.append("Missing or empty stats")
        
        if issues:
            print(f"Warning: Spellcasting setup issues for {creature.name}: {', '.join(issues)}")
        else:
            # Test the methods work
            try:
                dc = creature.get_spell_save_dc()
                attack = creature.get_spell_attack_bonus()
                mod = creature.get_spellcasting_modifier()
                print(f"  > {creature.name} spellcasting: DC {dc}, Attack +{attack}, Modifier +{mod}")
            except Exception as e:
                print(f"Error testing spellcasting methods for {creature.name}: {e}")

    @staticmethod
    def add_spell_to_creature(creature, spell):
        """Add a spell to a creature's repertoire."""
        if not hasattr(creature, 'prepared_spells'):
            SpellcastingManager.add_spellcasting(creature)

        if spell not in creature.prepared_spells:
            creature.prepared_spells.append(spell)
            print(f"** {creature.name} learned {spell.name}! **")

    @staticmethod
    def add_spell_action(creature, spell, targets=None):
        """Add a spell casting action to creature's available actions."""
        if not hasattr(creature, 'available_actions'):
            creature.available_actions = []
        
        spell_action = CastSpellAction(spell, targets)
        creature.available_actions.append(spell_action)

    @staticmethod
    def has_spell_slot(creature, spell_level):
        """Check if creature has an available spell slot of the given level."""
        if not hasattr(creature, 'spell_slots'):
            return False
        return creature.spell_slots.get(spell_level, 0) > 0

    @staticmethod
    def use_spell_slot(creature, spell_level):
        """Use a spell slot of the given level."""
        if SpellcastingManager.has_spell_slot(creature, spell_level):
            creature.spell_slots[spell_level] -= 1
            print(f"  > {creature.name} uses a level {spell_level} spell slot")
            return True
        else:
            print(f"  > {creature.name} has no level {spell_level} spell slots remaining!")
            return False

    @staticmethod
    def get_available_spell_slots(creature):
        """Get a summary of available spell slots."""
        if not hasattr(creature, 'spell_slots'):
            return "No spell slots"
        
        slot_summary = []
        for level, count in sorted(creature.spell_slots.items()):
            if count > 0:
                slot_summary.append(f"Level {level}: {count}")
        
        return ", ".join(slot_summary) if slot_summary else "No spell slots remaining"

    @staticmethod
    def restore_spell_slots(creature, slot_restoration=None):
        """Restore spell slots (for long rest, etc.)."""
        if not hasattr(creature, 'spell_slots'):
            return
        
        if slot_restoration is None:
            # Full restoration (long rest)
            max_slots = SpellcastingManager._get_max_spell_slots_by_level(creature.level)
            creature.spell_slots = max_slots.copy()
            print(f"  > {creature.name} recovers all spell slots!")
        else:
            # Partial restoration
            for level, count in slot_restoration.items():
                if level in creature.spell_slots:
                    creature.spell_slots[level] = min(
                        creature.spell_slots[level] + count,
                        SpellcastingManager._get_max_spell_slots_by_level(creature.level).get(level, 0)
                    )

    @staticmethod
    def _get_max_spell_slots_by_level(caster_level):
        """Get maximum spell slots by caster level (simplified)."""
        # This is a simplified version - in a full system, this would vary by class
        if caster_level >= 1:
            return {1: 2}
        if caster_level >= 3:
            return {1: 4, 2: 2}
        if caster_level >= 5:
            return {1: 4, 2: 3, 3: 2}
        # Add more levels as needed
        return {}