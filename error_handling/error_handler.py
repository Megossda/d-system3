# File: error_handling/error_handler.py
"""Comprehensive error handling for D&D systems."""

import logging
import traceback
from functools import wraps

class DnDError(Exception):
    """Base exception for D&D system errors."""
    pass

class SpellcastingError(DnDError):
    """Errors related to spellcasting."""
    pass

class CombatError(DnDError):
    """Errors related to combat operations."""
    pass

class ActionError(DnDError):
    """Errors related to action execution."""
    pass

class DnDErrorHandler:
    """Centralized error handling for D&D systems."""
    
    @staticmethod
    def safe_execute(operation_name, fallback_result=False):
        """Decorator for safe execution of critical operations."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger = logging.getLogger('DnDSystem')
                    logger.error(f"Error in {operation_name}: {e}")
                    logger.debug(f"Traceback: {traceback.format_exc()}")
                    
                    # Print user-friendly error message
                    print(f"  > ERROR: {operation_name} failed - {str(e)}")
                    
                    return fallback_result
            return wrapper
        return decorator

    @staticmethod
    def validate_creature(creature, operation="operation"):
        """Validate creature state before operations."""
        if not creature:
            raise DnDError(f"No creature provided for {operation}")
        
        if not hasattr(creature, 'is_alive'):
            raise DnDError(f"Creature {getattr(creature, 'name', 'Unknown')} missing 'is_alive' attribute")
        
        if not hasattr(creature, 'name'):
            raise DnDError(f"Creature missing 'name' attribute")
        
        return True

    @staticmethod
    def validate_spell_components(caster, spell, spell_level):
        """Validate spell casting components."""
        if not hasattr(caster, 'spellcasting_ability'):
            raise SpellcastingError(f"{caster.name} has no spellcasting ability")
        
        if not hasattr(spell, 'level'):
            raise SpellcastingError(f"Spell {getattr(spell, 'name', 'Unknown')} missing level information")
        
        if spell_level < spell.level:
            raise SpellcastingError(f"Cannot cast {spell.name} (level {spell.level}) using a {spell_level}-level slot")
        
        return True

    @staticmethod
    def validate_attack_data(attacker, target, weapon_data=None):
        """Validate attack parameters."""
        DnDErrorHandler.validate_creature(attacker, "attacking")
        DnDErrorHandler.validate_creature(target, "being attacked")
        
        if not attacker.is_alive:
            raise CombatError(f"{attacker.name} cannot attack - not alive")
        
        if not target.is_alive:
            raise CombatError(f"{target.name} cannot be attacked - not alive")
        
        if weapon_data:
            required_keys = ['name', 'damage', 'ability', 'damage_type']
            missing_keys = [key for key in required_keys if key not in weapon_data]
            if missing_keys:
                raise CombatError(f"Weapon data missing keys: {missing_keys}")
        
        return True

    @staticmethod
    def handle_damage_application(target, damage, damage_type="bludgeoning", source=None):
        """Safely apply damage with validation."""
        DnDErrorHandler.validate_creature(target, "damage application")
        
        if damage < 0:
            print(f"  > Warning: Negative damage ({damage}) converted to 0")
            damage = 0
        
        if damage == 0:
            print(f"  > No damage dealt to {target.name}")
            return
        
        # Apply damage using the most appropriate method available
        try:
            if hasattr(target, 'take_damage_with_resistance'):
                target.take_damage_with_resistance(damage, damage_type, source)
            else:
                # Try global damage resistance system
                try:
                    from systems.damage_resistance_system import DamageResistanceSystem
                    final_damage = DamageResistanceSystem.calculate_damage(target, damage, damage_type, source)
                    target.take_damage(final_damage, source)
                except ImportError:
                    # Fallback to basic damage
                    target.take_damage(damage, source)
        except Exception as e:
            logger = logging.getLogger('DnDSystem')
            logger.error(f"Error applying damage: {e}")
            print(f"  > ERROR: Could not apply damage - {str(e)}")