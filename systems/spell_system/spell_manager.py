# File: systems/spell_system/spell_manager.py (ENHANCED VERSION)
"""Spell Manager - Enhanced with comprehensive error handling."""

from core.utils import roll_d20, get_ability_modifier
from systems.d20_system import perform_d20_test
from systems.cover_system import RangeSystem, CoverSystem
from systems.positioning_system import battlefield
import logging

# Set up logging
logger = logging.getLogger('SpellSystem')

class SpellManager:
    """Central manager for all spell casting operations with enhanced error handling."""

    @staticmethod
    def cast_spell(caster, spell, targets=None, spell_level=None, action_type="ACTION"):
        """Universal spell casting interface with enhanced error handling."""
        try:
            # Input validation
            if not caster:
                logger.error("No caster provided for spell casting")
                print("  > ERROR: No caster provided!")
                return False
            
            if not spell:
                logger.error("No spell provided for casting")
                print("  > ERROR: No spell provided!")
                return False
            
            if not hasattr(caster, 'is_alive') or not caster.is_alive:
                print(f"  > {caster.name} cannot cast spells (not alive)")
                return False
            
            # Validate spellcasting ability
            if not hasattr(caster, 'spellcasting_ability'):
                logger.warning(f"{caster.name} has no spellcasting ability")
                print(f"  > {caster.name} is not a spellcaster!")
                return False
            
            # Validate spell slot system
            if not SpellManager._can_cast_spell(caster, spell, spell_level):
                return False

            if spell_level is None:
                spell_level = spell.level

            # Consume spell slot for non-cantrips
            if spell.level > 0:
                if not SpellManager._consume_spell_slot(caster, spell_level):
                    print(f"  > {caster.name} doesn't have a level {spell_level} spell slot!")
                    return False

            # Range validation for targeted spells
            if targets and SpellManager._requires_range_check(spell):
                spell_range = SpellManager._parse_spell_range(spell.range_type)
                
                # Check each target individually
                for target in (targets if isinstance(targets, list) else [targets]):
                    if target == caster:  # Self-targeting is always valid
                        continue
                        
                    range_check = RangeSystem.check_range(caster, target, spell_range)
                    if not range_check['in_range']:
                        print(f"  > {target.name} is out of range! (Distance: {range_check['distance']} feet, Spell range: {spell.range_type})")
                        return False
                    
                    # Check for total cover (other cover types are handled in attack rolls)
                    if hasattr(spell, 'school') and spell.school in ['evocation', 'conjuration']:  # Spells that can be blocked by total cover
                        cover_info = CoverSystem.determine_cover(caster, target)
                        if not cover_info['can_target']:
                            print(f"  > {target.name} has total cover and cannot be targeted!")
                            return False

            print(f"{action_type}: {caster.name} casts {spell.name}!")
            
            # Handle concentration spells
            if hasattr(spell, 'concentration') and spell.concentration:
                from systems.concentration_system import ConcentrationSystem
                duration = getattr(spell, 'duration', '1 minute')
                duration_seconds = ConcentrationSystem.parse_duration(duration)
                
                # Start concentration
                if not ConcentrationSystem.start_concentration(
                    caster, spell.name, duration_seconds, spell_level, 
                    {'spell': spell, 'targets': targets}
                ):
                    print(f"  > {caster.name} could not maintain concentration on {spell.name}")
                    return False
            
            # Cast the spell with error handling
            return spell.cast(caster, targets, spell_level, action_type)
            
        except Exception as e:
            logger.error(f"Error in spell casting: {e}")
            print(f"  > ERROR: Spell casting failed - {str(e)}")
            return False

    @staticmethod
    def _can_cast_spell(caster, spell, spell_level):
        """Check if caster can cast the spell with enhanced validation."""
        try:
            if not hasattr(caster, 'spell_slots'):
                logger.warning(f"{caster.name} has no spell slots")
                return False
            
            if hasattr(caster, 'prepared_spells') and spell not in caster.prepared_spells:
                print(f"  > {spell.name} is not prepared by {caster.name}")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error checking spell casting ability: {e}")
            return False

    @staticmethod
    def _consume_spell_slot(caster, spell_level):
        """Consume a spell slot with enhanced error handling."""
        try:
            if not hasattr(caster, 'spell_slots'):
                return False
            
            if caster.spell_slots.get(spell_level, 0) > 0:
                caster.spell_slots[spell_level] -= 1
                logger.info(f"{caster.name} used level {spell_level} spell slot")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error consuming spell slot: {e}")
            return False

    @staticmethod
    def make_spell_attack(caster, target, spell):
        """Make a spell attack with enhanced error handling."""
        try:
            # Input validation
            if not caster or not target or not spell:
                logger.error("Missing parameters for spell attack")
                return {'hit': False, 'critical': False}
            
            if not target.is_alive:
                print(f"  > {target.name} is already defeated")
                return {'hit': False, 'critical': False}
            
            # Validate spellcasting ability
            if not hasattr(caster, 'spellcasting_ability'):
                logger.error(f"{caster.name} has no spellcasting ability for spell attack")
                print(f"  > ERROR: {caster.name} has no spellcasting ability!")
                return {'hit': False, 'critical': False}
            
            # Perform the attack
            from systems.attack_system import AttackSystem
            return AttackSystem.make_spell_attack(caster, target, spell)
            
        except Exception as e:
            logger.error(f"Error in spell attack: {e}")
            print(f"  > ERROR: Spell attack failed - {str(e)}")
            return {'hit': False, 'critical': False}

    @staticmethod
    def make_spell_save(target, caster, spell, save_type):
        """Make a saving throw against a spell with enhanced error handling."""
        try:
            # Input validation
            if not target or not target.is_alive:
                logger.warning("Invalid target for spell save")
                return False
            
            if not caster or not hasattr(caster, 'get_spell_save_dc'):
                logger.error("Invalid caster for spell save")
                return False
                
            save_dc = caster.get_spell_save_dc()
            print(f"  > {target.name} must make a {save_type.upper()} saving throw against DC {save_dc}")
            
            # Use the global d20_system to handle the saving throw
            success = perform_d20_test(
                creature=target,
                ability_name=save_type.lower(),
                check_type=None,  # Saving throws don't use skill proficiencies
                dc=save_dc,
                is_saving_throw=True
            )
            
            if success:
                print(f"  > {target.name} succeeds on the {save_type.upper()} save!")
            else:
                print(f"  > {target.name} fails the {save_type.upper()} save!")
                
            return success
            
        except Exception as e:
            logger.error(f"Error in spell save: {e}")
            print(f"  > ERROR: Spell save failed - {str(e)}")
            # On error, assume save succeeds (benefit of the doubt)
            return True

    @staticmethod
    def deal_spell_damage(target, damage, damage_type, caster, is_crit=False):
        """Deal spell damage to a target with enhanced error handling."""
        try:
            # Input validation
            if not target or not target.is_alive:
                logger.warning("Invalid target for spell damage")
                return
            
            if damage < 0:
                logger.warning(f"Negative damage value: {damage}")
                damage = 0
            
            if damage == 0:
                print(f"  > No damage dealt to {target.name}")
                return
            
            if is_crit:
                damage *= 2
                print(f"CRITICAL SPELL DAMAGE: {damage} {damage_type} damage!")
            else:
                print(f"SPELL DAMAGE: {damage} {damage_type} damage")
            
            # Apply damage using best available method
            if hasattr(target, 'take_damage_with_resistance'):
                target.take_damage_with_resistance(damage, damage_type, caster)
            else:
                target.take_damage(damage, attacker=caster)
                
        except Exception as e:
            logger.error(f"Error dealing spell damage: {e}")
            print(f"  > ERROR: Could not apply spell damage - {str(e)}")
    
    @staticmethod
    def _requires_range_check(spell):
        """Determine if a spell requires range checking."""
        if not hasattr(spell, 'range_type'):
            return False
        
        range_lower = spell.range_type.lower()
        
        # Self-targeting spells don't need range checks
        if 'self' in range_lower:
            return False
        
        # All other spells with ranges need checking
        return True
    
    @staticmethod
    def _parse_spell_range(range_string):
        """Parse a spell's range string into a usable range value."""
        if not range_string:
            return 5  # Default to touch
        
        range_lower = range_string.lower()
        
        # Handle special cases
        if 'touch' in range_lower:
            return 5  # Touch spells require 5-foot reach
        elif 'self' in range_lower:
            return 0  # Self-targeting
        elif 'sight' in range_lower:
            return 1000  # Very long range for practical purposes
        elif 'unlimited' in range_lower:
            return float('inf')
        
        # Extract number from range string (first number found)
        import re
        numbers = re.findall(r'\d+', range_string)
        if numbers:
            base_range = int(numbers[0])
            # Handle unit conversions
            if 'mile' in range_lower:
                return base_range * 5280  # Convert miles to feet
            return base_range
        
        # Default fallback
        return 30