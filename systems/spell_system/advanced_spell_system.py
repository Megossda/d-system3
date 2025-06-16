# File: systems/spell_system/advanced_spell_system.py
"""Advanced Spell System - Handles attack roll spells and advanced spell mechanics."""

from systems.d20_system import perform_d20_test
from systems.damage_resistance_system import DamageResistanceSystem
from core.utils import roll_dice

class SpellAttackType:
    """Types of spell attacks."""
    MELEE = "melee"
    RANGED = "ranged"

class SpellTargetType:
    """How spells target creatures."""
    SINGLE = "single"
    MULTIPLE = "multiple"
    AREA = "area"
    SELF = "self"

class AdvancedSpellSystem:
    """Handles advanced spell mechanics beyond basic save-or-suck spells."""
    
    @staticmethod
    def make_spell_attack_roll(caster, target, spell, attack_type=SpellAttackType.RANGED):
        """
        Make a spell attack roll against a target.
        
        Args:
            caster: The creature casting the spell
            target: The target of the spell attack
            spell: The spell being cast
            attack_type: Melee or ranged spell attack
            
        Returns:
            dict: Attack result information
        """
        print(f"--- {caster.name} makes a {attack_type} spell attack with {spell.name} ---")
        
        # Check if caster has spellcasting ability
        if not hasattr(caster, 'spellcasting_ability'):
            print(f"  > {caster.name} is not a spellcaster!")
            return {'hit': False, 'critical': False}
        
        # Make the attack roll using d20 system
        hit = perform_d20_test(
            creature=caster,
            ability_name=caster.spellcasting_ability,
            check_type=None,  # Spell attacks don't use skill proficiency
            target=target,
            is_attack_roll=True
        )
        
        # Check for critical hit (natural 20)
        from systems.d20_system import was_last_roll_critical
        is_critical = was_last_roll_critical()
        
        if hit:
            if is_critical:
                print(f"  > CRITICAL HIT! {spell.name} strikes {target.name}!")
            else:
                print(f"  > {spell.name} hits {target.name}!")
        else:
            print(f"  > {spell.name} misses {target.name}!")
        
        return {'hit': hit, 'critical': is_critical}
    
    @staticmethod
    def deal_spell_damage(target, damage_dice, damage_type, caster, is_critical=False, spell_level=1):
        """
        Deal spell damage with proper scaling and critical hit handling.
        
        Args:
            target: The target taking damage
            damage_dice: Base damage dice (e.g., "1d10")
            damage_type: Type of damage
            caster: The caster of the spell
            is_critical: Whether this is a critical hit
            spell_level: Level the spell was cast at
        """
        # Roll base damage
        base_damage = roll_dice(damage_dice)
        
        # Handle critical hits (double dice, not modifiers)
        if is_critical:
            crit_damage = roll_dice(damage_dice)  # Roll damage dice again
            total_damage = base_damage + crit_damage
            print(f"  > CRITICAL SPELL DAMAGE: {total_damage} {damage_type} damage! ({damage_dice} + {damage_dice})")
        else:
            total_damage = base_damage
            print(f"  > SPELL DAMAGE: {total_damage} {damage_type} damage ({damage_dice})")
        
        # Apply damage with resistance system
        if hasattr(target, 'take_damage_with_resistance'):
            target.take_damage_with_resistance(total_damage, damage_type, caster)
        else:
            # Fallback to basic damage if resistance system not patched
            DamageResistanceSystem.calculate_damage(target, total_damage, damage_type, caster)
            target.take_damage(total_damage, caster)
        
        return total_damage
    
    @staticmethod
    def scale_spell_damage(base_dice, spell_level, scaling_dice_per_level):
        """
        Scale spell damage based on spell level.
        
        Args:
            base_dice: Base damage dice at lowest level
            spell_level: Level the spell was cast at
            scaling_dice_per_level: Additional dice per level above base
            
        Returns:
            str: Scaled damage dice notation
        """
        if spell_level <= 1:
            return base_dice
        
        # Extract dice information
        import re
        match = re.match(r'(\d+)d(\d+)', base_dice)
        if not match:
            return base_dice
        
        base_num_dice = int(match.group(1))
        die_size = match.group(2)
        
        # Add scaling dice
        additional_levels = spell_level - 1
        total_dice = base_num_dice + (additional_levels * scaling_dice_per_level)
        
        return f"{total_dice}d{die_size}"
    
    @staticmethod
    def handle_spell_concentration(caster, spell):
        """Handle spell concentration mechanics."""
        if not hasattr(spell, 'requires_concentration') or not spell.requires_concentration:
            return True
        
        # Check if caster is already concentrating
        if hasattr(caster, 'concentrating_on') and caster.concentrating_on:
            old_spell = caster.concentrating_on
            print(f"  > {caster.name} loses concentration on {old_spell.name}")
        
        # Start concentrating on new spell
        caster.concentrating_on = spell
        print(f"  > {caster.name} begins concentrating on {spell.name}")
        return True
    
    @staticmethod
    def make_concentration_save(caster, damage_taken):
        """Make a Constitution save to maintain concentration."""
        if not hasattr(caster, 'concentrating_on') or not caster.concentrating_on:
            return True  # Not concentrating
        
        # DC is 10 or half the damage taken, whichever is higher
        dc = max(10, damage_taken // 2)
        
        print(f"--- {caster.name} makes a Concentration save (DC {dc}) ---")
        
        success = perform_d20_test(
            creature=caster,
            ability_name='con',
            check_type=None,  # Constitution saves don't use skills
            dc=dc,
            is_saving_throw=True
        )
        
        if success:
            print(f"  > {caster.name} maintains concentration!")
        else:
            spell_name = caster.concentrating_on.name
            caster.concentrating_on = None
            print(f"  > {caster.name} loses concentration on {spell_name}!")
        
        return success

# Advanced spell effects
class SpellEffect:
    """Represents ongoing spell effects."""
    def __init__(self, spell, caster, targets, duration_rounds):
        self.spell = spell
        self.caster = caster
        self.targets = targets if isinstance(targets, list) else [targets]
        self.duration_rounds = duration_rounds
        self.rounds_remaining = duration_rounds
    
    def tick_round(self):
        """Process the effect for one round."""
        self.rounds_remaining -= 1
        
        if self.rounds_remaining <= 0:
            self.end_effect()
            return False
        
        return True
    
    def end_effect(self):
        """End the spell effect."""
        print(f"  > {self.spell.name} effect ends")
        if hasattr(self.caster, 'concentrating_on') and self.caster.concentrating_on == self.spell:
            self.caster.concentrating_on = None

class SpellEffectManager:
    """Manages ongoing spell effects."""
    
    def __init__(self):
        self.active_effects = []
    
    def add_effect(self, spell_effect):
        """Add a new spell effect."""
        self.active_effects.append(spell_effect)
        print(f"  > {spell_effect.spell.name} effect added (duration: {spell_effect.duration_rounds} rounds)")
    
    def process_round(self):
        """Process all effects for one round."""
        effects_to_remove = []
        
        for effect in self.active_effects:
            if not effect.tick_round():
                effects_to_remove.append(effect)
        
        # Remove expired effects
        for effect in effects_to_remove:
            self.active_effects.remove(effect)
    
    def remove_effects_by_caster(self, caster):
        """Remove all effects cast by a specific caster."""
        effects_to_remove = [effect for effect in self.active_effects if effect.caster == caster]
        
        for effect in effects_to_remove:
            effect.end_effect()
            self.active_effects.remove(effect)

# Global spell effect manager
spell_effects = SpellEffectManager()