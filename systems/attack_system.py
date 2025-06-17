# File: systems/attack_system.py (ENHANCED VERSION)
"""Global attack system with enhanced error handling."""

from systems.d20_system import perform_d20_test, was_last_roll_critical
from core.utils import roll_dice
from systems.cover_system import RangeSystem, CoverSystem
from systems.positioning_system import battlefield
import logging

# Set up logging
logger = logging.getLogger('AttackSystem')

class WeaponRanges:
    """Standard weapon ranges for D&D 2024."""
    
    # Melee weapons (5 feet reach)
    MELEE_STANDARD = 5
    MELEE_REACH = 10  # Reach weapons like pikes, whips
    
    # Ranged weapons (normal_range, long_range)
    DART = (20, 60)
    HANDAXE = (20, 60)
    JAVELIN = (30, 120)
    LIGHT_HAMMER = (20, 60)
    SPEAR = (20, 60)
    DAGGER = (20, 60)
    
    SHORTBOW = (80, 320)
    LONGBOW = (150, 600)
    LIGHT_CROSSBOW = (80, 320)
    HEAVY_CROSSBOW = (100, 400)
    HAND_CROSSBOW = (30, 120)
    
    SLING = (30, 120)
    BLOWGUN = (25, 100)
    NET = (5, 15)  # Special weapon
    
    @staticmethod
    def get_weapon_range(weapon_name):
        """Get range for a weapon by name."""
        weapon_ranges = {
            # Melee weapons
            'unarmed strike': WeaponRanges.MELEE_STANDARD,
            'dagger': WeaponRanges.MELEE_STANDARD,  # Can be thrown
            'club': WeaponRanges.MELEE_STANDARD,
            'handaxe': WeaponRanges.MELEE_STANDARD,  # Can be thrown
            'javelin': WeaponRanges.MELEE_STANDARD,  # Can be thrown
            'light hammer': WeaponRanges.MELEE_STANDARD,  # Can be thrown
            'mace': WeaponRanges.MELEE_STANDARD,
            'quarterstaff': WeaponRanges.MELEE_STANDARD,
            'sickle': WeaponRanges.MELEE_STANDARD,
            'spear': WeaponRanges.MELEE_STANDARD,  # Can be thrown
            'battleaxe': WeaponRanges.MELEE_STANDARD,
            'flail': WeaponRanges.MELEE_STANDARD,
            'longsword': WeaponRanges.MELEE_STANDARD,
            'morningstar': WeaponRanges.MELEE_STANDARD,
            'rapier': WeaponRanges.MELEE_STANDARD,
            'scimitar': WeaponRanges.MELEE_STANDARD,
            'shortsword': WeaponRanges.MELEE_STANDARD,
            'warhammer': WeaponRanges.MELEE_STANDARD,
            'greataxe': WeaponRanges.MELEE_STANDARD,
            'greatsword': WeaponRanges.MELEE_STANDARD,
            'maul': WeaponRanges.MELEE_STANDARD,
            
            # Reach weapons
            'glaive': WeaponRanges.MELEE_REACH,
            'halberd': WeaponRanges.MELEE_REACH,
            'pike': WeaponRanges.MELEE_REACH,
            'whip': WeaponRanges.MELEE_REACH,
            
            # Thrown weapons (when thrown)
            'dagger_thrown': WeaponRanges.DAGGER,
            'handaxe_thrown': WeaponRanges.HANDAXE,
            'javelin_thrown': WeaponRanges.JAVELIN,
            'light_hammer_thrown': WeaponRanges.LIGHT_HAMMER,
            'spear_thrown': WeaponRanges.SPEAR,
            'dart': WeaponRanges.DART,
            
            # Ranged weapons
            'shortbow': WeaponRanges.SHORTBOW,
            'longbow': WeaponRanges.LONGBOW,
            'light crossbow': WeaponRanges.LIGHT_CROSSBOW,
            'heavy crossbow': WeaponRanges.HEAVY_CROSSBOW,
            'hand crossbow': WeaponRanges.HAND_CROSSBOW,
            'sling': WeaponRanges.SLING,
            'blowgun': WeaponRanges.BLOWGUN,
            'net': WeaponRanges.NET,
        }
        
        return weapon_ranges.get(weapon_name.lower(), WeaponRanges.MELEE_STANDARD)

class AttackSystem:
    """Centralized system for handling all attack types with enhanced error handling and range validation."""
    
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
            
            # Range validation
            weapon_name = weapon_data.get('name', 'unarmed strike')
            weapon_range = weapon_data.get('range', WeaponRanges.get_weapon_range(weapon_name))
            
            # Check if target is in range
            range_check = RangeSystem.check_range(attacker, target, weapon_range)
            if not range_check['in_range']:
                print(f"  > {target.name} is out of range! (Distance: {range_check['distance']} feet, Max range: {weapon_range})")
                return False
            
            # Check for long range disadvantage
            has_range_disadvantage = range_check['disadvantage']
            if has_range_disadvantage:
                print(f"  > Attack at long range (Distance: {range_check['distance']} feet) - disadvantage on attack roll")
            
            # Check for close combat disadvantage on ranged attacks
            is_ranged_weapon = isinstance(weapon_range, tuple) or weapon_range > 5
            has_close_combat_disadvantage = False
            if is_ranged_weapon:
                has_close_combat_disadvantage = RangeSystem.check_close_combat_disadvantage(attacker)
            
            # Apply cover
            target_ac = target.ac
            cover_ac, cover_info = CoverSystem.apply_cover_to_attack(attacker, target, target_ac)
            if cover_ac is None:  # Total cover
                return False
            target_ac = cover_ac
            
            # Determine proficiency
            weapon_name = weapon_data.get('name', 'weapon')
            is_proficient = weapon_data.get('proficient', False) or weapon_name.lower() in attacker.proficiencies
            
            # Determine total disadvantage
            has_disadvantage = has_range_disadvantage or has_close_combat_disadvantage
            
            # Make the attack roll with range and cover considerations
            hit = perform_d20_test(
                creature=attacker,
                ability_name=weapon_data.get('ability', 'str'),
                check_type=weapon_name.lower() if is_proficient else None,
                target=target,
                ac=target_ac,  # Use cover-modified AC
                is_attack_roll=True,
                has_disadvantage=has_disadvantage,
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
            
            # Parse spell range
            spell_range = AttackSystem._parse_spell_range(spell.range_type)
            
            # Check if target is in range
            range_check = RangeSystem.check_range(caster, target, spell_range)
            if not range_check['in_range']:
                print(f"  > {target.name} is out of range! (Distance: {range_check['distance']} feet, Spell range: {spell.range_type})")
                return {'hit': False, 'critical': False}
            
            # Apply cover for spell attacks
            target_ac = target.ac
            cover_ac, cover_info = CoverSystem.apply_cover_to_attack(caster, target, target_ac)
            if cover_ac is None:  # Total cover
                return {'hit': False, 'critical': False}
            target_ac = cover_ac
            
            hit = perform_d20_test(
                creature=caster,
                ability_name=caster.spellcasting_ability,
                check_type=None,
                target=target,
                ac=target_ac,  # Use cover-modified AC
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
        
        # Extract number from range string
        import re
        numbers = re.findall(r'\d+', range_string)
        if numbers:
            return int(numbers[0])
        
        # Default fallback
        return 30
