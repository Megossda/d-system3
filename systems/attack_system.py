# File: systems/attack_system.py (ENHANCED VERSION)
"""Global attack system with enhanced error handling."""

from systems.d20_system import perform_d20_test, was_last_roll_critical
from core.utils import roll_dice
import logging

# Set up logging
logger = logging.getLogger('AttackSystem')

class AttackSystem:
    """Centralized system for handling all attack types with enhanced error handling."""
    
    @staticmethod
    def make_weapon_attack(attacker, target, weapon_data, attacker_is_within_5_feet=True):
        """Make a weapon attack with enhanced error handling."""
        try:
            # Input validation
            if not attacker:
                logger.error("No attacker provided for weapon attack")
                print("  > ERROR: No attacker provided!")
                return False
            
            if not target:
                logger.error("No target provided for weapon attack")
                print(f"  > {attacker.name} needs a target to attack!")
                return False
            
            if not attacker.is_alive:
                print(f"  > {attacker.name} cannot attack (not alive)")
                return False
            
            if not target.is_alive:
                print(f"  > {target.name} is already defeated")
                return False
            
            # Validate weapon data
            if not weapon_data:
                logger.warning("No weapon data provided, using unarmed strike")
                weapon_data = {
                    'name': 'Unarmed Strike',
                    'damage': '1+0',
                    'ability': 'str',
                    'proficient': True,
                    'damage_type': 'bludgeoning'
                }
            
            # Validate required weapon data fields
            required_fields = ['name', 'damage', 'ability', 'damage_type']
            missing_fields = [field for field in required_fields if field not in weapon_data]
            if missing_fields:
                logger.warning(f"Weapon data missing fields: {missing_fields}")
                # Fill in defaults
                defaults = {
                    'name': 'Unknown Weapon',
                    'damage': '1d6',
                    'ability': 'str',
                    'damage_type': 'bludgeoning'
                }
                for field in missing_fields:
                    weapon_data[field] = defaults.get(field, 'unknown')
            
            print(f"\n--- {attacker.name} attacks {target.name} ---")
            
            # Determine proficiency
            weapon_name = weapon_data.get('name', 'weapon')
            is_proficient = weapon_data.get('proficient', False) or weapon_name.lower() in attacker.proficiencies
            
            # Make the attack roll
            hit = perform_d20_test(
                creature=attacker,
                ability_name=weapon_data.get('ability', 'str'),
                check_type=weapon_name.lower() if is_proficient else None,
                target=target,
                is_attack_roll=True,
                attacker_is_within_5_feet=attacker_is_within_5_feet
            )
            
            if hit:
                # Calculate and apply damage
                is_crit = was_last_roll_critical()
                damage = AttackSystem._calculate_damage(
                    weapon_data.get('damage', '1d6'), 
                    attacker.get_ability_modifier(weapon_data.get('ability', 'str')), 
                    is_crit
                )
                damage_type = weapon_data.get('damage_type', 'bludgeoning')
                
                AttackSystem._deal_damage(target, damage, damage_type, attacker, is_crit)
                
                # Handle special effects
                special_effects = weapon_data.get('special_effects', [])
                for effect in special_effects:
                    AttackSystem._apply_weapon_effect(effect, attacker, target)
                    
                return True
            else:
                print(f"  > {attacker.name}'s attack misses!")
                return False
                
        except Exception as e:
            logger.error(f"Error in weapon attack: {e}")
            print(f"  > ERROR: Attack failed - {str(e)}")
            return False
    
    @staticmethod
    def make_spell_attack(caster, target, spell, spell_level=None):
        """Make a spell attack with enhanced error handling."""
        try:
            # Input validation
            if not caster or not target or not spell:
                logger.error("Missing parameters for spell attack")
                return {'hit': False, 'critical': False}
            
            if not target.is_alive:
                print(f"  > {target.name} is already defeated")
                return {'hit': False, 'critical': False}
            
            if not hasattr(caster, 'spellcasting_ability'):
                logger.error(f"{caster.name} has no spellcasting ability")
                print(f"  > ERROR: {caster.name} has no spellcasting ability!")
                return {'hit': False, 'critical': False}
            
            print(f"\n--- {caster.name} makes a spell attack with {spell.name} ---")
            
            hit = perform_d20_test(
                creature=caster,
                ability_name=caster.spellcasting_ability,
                check_type=None,
                target=target,
                is_attack_roll=True
            )
            
            if hit:
                is_crit = was_last_roll_critical()
                if is_crit:
                    print(f"  > CRITICAL HIT! {spell.name} critically strikes {target.name}!")
                else:
                    print(f"  > {spell.name} hits {target.name}!")
                
                return {'hit': True, 'critical': is_crit}
            else:
                print(f"  > {spell.name} misses {target.name}!")
                return {'hit': False, 'critical': False}
                
        except Exception as e:
            logger.error(f"Error in spell attack: {e}")
            print(f"  > ERROR: Spell attack failed - {str(e)}")
            return {'hit': False, 'critical': False}
    
    @staticmethod
    def make_unarmed_attack(attacker, target):
        """Make an unarmed strike with enhanced error handling."""
        unarmed_data = {
            'name': 'Unarmed Strike',
            'damage': '1+0',
            'ability': 'str',
            'proficient': True,
            'damage_type': 'bludgeoning'
        }
        
        return AttackSystem.make_weapon_attack(attacker, target, unarmed_data)
    
    @staticmethod
    def _calculate_damage(damage_dice, ability_modifier, is_critical=False):
        """Calculate damage with enhanced error handling."""
        try:
            if is_critical:
                # For crits, double the dice but not the ability modifier
                import re
                match = re.match(r'(\d+)d(\d+)([+-]\d+)?', damage_dice.lower().strip())
                if match:
                    num_dice = int(match.group(1)) * 2
                    die_type = match.group(2)
                    dice_modifier = match.group(3) or ""
                    crit_dice = f"{num_dice}d{die_type}{dice_modifier}"
                    base_damage = roll_dice(crit_dice)
                else:
                    base_damage = roll_dice(damage_dice) * 2
            else:
                base_damage = roll_dice(damage_dice)
            
            total_damage = base_damage + ability_modifier
            return max(1, total_damage)  # Minimum 1 damage
            
        except Exception as e:
            logger.error(f"Error calculating damage: {e}")
            # Fallback: 1 point of damage
            return 1
    
    @staticmethod
    def _deal_damage(target, damage, damage_type, attacker, is_critical=False):
        """Deal damage with enhanced error handling."""
        try:
            if is_critical:
                print(f"  > CRITICAL HIT! {damage} {damage_type} damage!")
            else:
                print(f"  > {damage} {damage_type} damage!")
            
            # Apply damage using best available method
            if hasattr(target, 'take_damage_with_resistance'):
                target.take_damage_with_resistance(damage, damage_type, attacker)
            else:
                # Try global damage resistance system
                try:
                    from systems.damage_resistance_system import DamageResistanceSystem
                    final_damage = DamageResistanceSystem.calculate_damage(target, damage, damage_type, attacker)
                    target.take_damage(final_damage, attacker=attacker)
                except ImportError:
                    # Fallback to basic damage
                    target.take_damage(damage, attacker=attacker)
                    
        except Exception as e:
            logger.error(f"Error dealing damage: {e}")
            print(f"  > ERROR: Could not apply damage - {str(e)}")
    
    @staticmethod
    def _apply_weapon_effect(effect, attacker, target):
        """Apply weapon effects with enhanced error handling."""
        try:
            if effect == 'knockdown':
                from systems.condition_system import add_condition
                add_condition(target, 'prone')
                print(f"  > {target.name} is knocked prone!")
            elif effect == 'poison':
                print(f"  > {target.name} must save against poison!")
            # Add more effects as needed
        except Exception as e:
            logger.error(f"Error applying weapon effect {effect}: {e}")
            print(f"  > WARNING: Could not apply weapon effect - {str(e)}")
