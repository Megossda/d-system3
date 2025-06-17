# File: error_handling/error_handler.py
"""Enhanced error handling for D&D systems with improved robustness and features."""

import logging
import traceback
import functools
import time
from typing import Optional, Any, Dict, List
from enum import Enum

class ErrorSeverity(Enum):
    """Error severity levels for better categorization."""
    MINOR = "minor"        # Non-critical errors that don't affect gameplay
    MODERATE = "moderate"  # Errors that affect specific features
    MAJOR = "major"        # Errors that affect core gameplay
    CRITICAL = "critical"  # Errors that could break the system

class DnDError(Exception):
    """Base exception for D&D system errors with enhanced features."""
    def __init__(self, message: str, severity: ErrorSeverity = ErrorSeverity.MODERATE, 
                 context: Optional[Dict] = None, recovery_suggestion: Optional[str] = None):
        super().__init__(message)
        self.severity = severity
        self.context = context or {}
        self.recovery_suggestion = recovery_suggestion
        self.timestamp = time.time()

class SpellcastingError(DnDError):
    """Errors related to spellcasting with spell-specific context."""
    def __init__(self, message: str, spell_name: Optional[str] = None, 
                 caster_name: Optional[str] = None, **kwargs):
        context = kwargs.get('context', {})
        context.update({
            'spell_name': spell_name,
            'caster_name': caster_name,
            'system': 'spellcasting'
        })
        super().__init__(message, context=context, **kwargs)

class CombatError(DnDError):
    """Errors related to combat operations with combat context."""
    def __init__(self, message: str, attacker_name: Optional[str] = None, 
                 target_name: Optional[str] = None, **kwargs):
        context = kwargs.get('context', {})
        context.update({
            'attacker_name': attacker_name,
            'target_name': target_name,
            'system': 'combat'
        })
        super().__init__(message, context=context, **kwargs)

class ActionError(DnDError):
    """Errors related to action execution with action context."""
    def __init__(self, message: str, action_name: Optional[str] = None, 
                 performer_name: Optional[str] = None, **kwargs):
        context = kwargs.get('context', {})
        context.update({
            'action_name': action_name,
            'performer_name': performer_name,
            'system': 'actions'
        })
        super().__init__(message, context=context, **kwargs)

class ErrorMetrics:
    """Tracks error statistics for system health monitoring."""
    def __init__(self):
        self.error_counts = {severity: 0 for severity in ErrorSeverity}
        self.error_history = []
        self.max_history = 1000
        
    def record_error(self, error: DnDError):
        """Record an error for metrics tracking."""
        self.error_counts[error.severity] += 1
        
        error_record = {
            'timestamp': error.timestamp,
            'severity': error.severity.value,
            'message': str(error),
            'context': error.context
        }
        
        self.error_history.append(error_record)
        
        # Keep history size manageable
        if len(self.error_history) > self.max_history:
            self.error_history.pop(0)
    
    def get_error_summary(self) -> Dict:
        """Get summary of error statistics."""
        recent_errors = [e for e in self.error_history if time.time() - e['timestamp'] < 3600]  # Last hour
        
        return {
            'total_errors': sum(self.error_counts.values()),
            'errors_by_severity': {s.value: count for s, count in self.error_counts.items()},
            'recent_errors_count': len(recent_errors),
            'most_recent_error': self.error_history[-1] if self.error_history else None
        }

class DnDErrorHandler:
    """Enhanced centralized error handling for D&D systems."""
    
    _metrics = ErrorMetrics()
    _error_callbacks = []  # For custom error handling
    
    @staticmethod
    def safe_execute(operation_name: str, fallback_result=False, 
                    severity: ErrorSeverity = ErrorSeverity.MODERATE,
                    suppress_errors: bool = False, max_retries: int = 0):
        """Enhanced decorator for safe execution with retries and better error handling."""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                
                for attempt in range(max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except DnDError as e:
                        # D&D specific errors - handle specially
                        last_exception = e
                        DnDErrorHandler._handle_dnd_error(e, operation_name)
                        
                        if attempt < max_retries:
                            logger = logging.getLogger('DnDSystem')
                            logger.warning(f"Retrying {operation_name} (attempt {attempt + 2}/{max_retries + 1})")
                            continue
                        break
                    except Exception as e:
                        # Convert generic exceptions to DnD errors
                        dnd_error = DnDError(
                            f"Unexpected error in {operation_name}: {str(e)}",
                            severity=severity,
                            context={'operation': operation_name, 'original_error': type(e).__name__},
                            recovery_suggestion=f"Try restarting the {operation_name} operation"
                        )
                        last_exception = dnd_error
                        DnDErrorHandler._handle_dnd_error(dnd_error, operation_name)
                        
                        if attempt < max_retries:
                            logger = logging.getLogger('DnDSystem')
                            logger.warning(f"Retrying {operation_name} after error (attempt {attempt + 2}/{max_retries + 1})")
                            continue
                        break
                
                # All retries failed
                if not suppress_errors and last_exception:
                    if last_exception.recovery_suggestion:
                        print(f"  > RECOVERY SUGGESTION: {last_exception.recovery_suggestion}")
                
                return fallback_result
            return wrapper
        return decorator

    @staticmethod
    def _handle_dnd_error(error: DnDError, operation_name: str):
        """Internal method to handle D&D specific errors."""
        logger = logging.getLogger('DnDSystem')
        
        # Log based on severity
        if error.severity == ErrorSeverity.CRITICAL:
            logger.critical(f"CRITICAL ERROR in {operation_name}: {error}")
        elif error.severity == ErrorSeverity.MAJOR:
            logger.error(f"MAJOR ERROR in {operation_name}: {error}")
        elif error.severity == ErrorSeverity.MODERATE:
            logger.error(f"Error in {operation_name}: {error}")
        else:
            logger.warning(f"Minor issue in {operation_name}: {error}")
        
        # Add context to log if available
        if error.context:
            logger.debug(f"Error context: {error.context}")
        
        # Record metrics
        DnDErrorHandler._metrics.record_error(error)
        
        # User-friendly message
        severity_prefix = {
            ErrorSeverity.CRITICAL: "CRITICAL",
            ErrorSeverity.MAJOR: "ERROR",
            ErrorSeverity.MODERATE: "ERROR",
            ErrorSeverity.MINOR: "WARNING"
        }
        print(f"  > {severity_prefix[error.severity]}: {operation_name} - {str(error)}")
        
        # Call any registered error callbacks
        for callback in DnDErrorHandler._error_callbacks:
            try:
                callback(error, operation_name)
            except Exception as callback_error:
                logger.error(f"Error in error callback: {callback_error}")

    @staticmethod
    def validate_creature(creature, operation="operation"):
        """Enhanced creature validation with detailed error reporting."""
        if not creature:
            raise DnDError(
                f"No creature provided for {operation}",
                severity=ErrorSeverity.MAJOR,
                context={'operation': operation},
                recovery_suggestion="Ensure a valid creature object is passed to the operation"
            )
        
        # Check for required attributes with specific error messages
        required_attrs = ['is_alive', 'name', 'current_hp', 'max_hp']
        missing_attrs = []
        
        for attr in required_attrs:
            if not hasattr(creature, attr):
                missing_attrs.append(attr)
        
        if missing_attrs:
            raise DnDError(
                f"Creature {getattr(creature, 'name', 'Unknown')} missing required attributes: {missing_attrs}",
                severity=ErrorSeverity.MAJOR,
                context={
                    'operation': operation,
                    'creature_name': getattr(creature, 'name', 'Unknown'),
                    'missing_attributes': missing_attrs
                },
                recovery_suggestion="Ensure the creature object is properly initialized with all required attributes"
            )
        
        # Validate creature state
        if hasattr(creature, 'current_hp') and hasattr(creature, 'max_hp'):
            if creature.current_hp < 0:
                raise DnDError(
                    f"Creature {creature.name} has negative HP ({creature.current_hp})",
                    severity=ErrorSeverity.MODERATE,
                    context={
                        'creature_name': creature.name,
                        'current_hp': creature.current_hp,
                        'max_hp': creature.max_hp
                    },
                    recovery_suggestion="Reset creature HP to 0 or restore to valid value"
                )
            
            if creature.current_hp > creature.max_hp:
                # This is usually not an error, but worth logging
                logger = logging.getLogger('DnDSystem')
                logger.warning(f"{creature.name} has HP ({creature.current_hp}) above maximum ({creature.max_hp})")
        
        return True

    @staticmethod
    def validate_spell_components(caster, spell, spell_level):
        """Enhanced spell validation with recovery suggestions."""
        try:
            DnDErrorHandler.validate_creature(caster, "spellcasting")
        except DnDError as e:
            # Re-raise with spellcasting context
            raise SpellcastingError(
                str(e),
                caster_name=getattr(caster, 'name', 'Unknown'),
                severity=e.severity,
                recovery_suggestion="Ensure the caster is a valid, living creature"
            )
        
        if not hasattr(caster, 'spellcasting_ability'):
            raise SpellcastingError(
                f"{caster.name} has no spellcasting ability",
                caster_name=caster.name,
                severity=ErrorSeverity.MAJOR,
                recovery_suggestion="Add spellcasting ability using SpellcastingManager.add_spellcasting()"
            )
        
        if not hasattr(spell, 'level'):
            raise SpellcastingError(
                f"Spell {getattr(spell, 'name', 'Unknown')} missing level information",
                spell_name=getattr(spell, 'name', 'Unknown'),
                caster_name=caster.name,
                severity=ErrorSeverity.MAJOR,
                recovery_suggestion="Ensure the spell object has a valid level attribute"
            )
        
        if spell_level < spell.level:
            raise SpellcastingError(
                f"Cannot cast {spell.name} (level {spell.level}) using a {spell_level}-level slot",
                spell_name=spell.name,
                caster_name=caster.name,
                context={'spell_level': spell.level, 'slot_level': spell_level},
                severity=ErrorSeverity.MODERATE,
                recovery_suggestion=f"Use a spell slot of level {spell.level} or higher"
            )
        
        return True

    @staticmethod
    def validate_attack_data(attacker, target, weapon_data=None):
        """Enhanced attack validation with detailed error context."""
        try:
            DnDErrorHandler.validate_creature(attacker, "attacking")
            DnDErrorHandler.validate_creature(target, "being attacked")
        except DnDError as e:
            # Re-raise as combat error
            raise CombatError(
                str(e),
                attacker_name=getattr(attacker, 'name', 'Unknown'),
                target_name=getattr(target, 'name', 'Unknown'),
                severity=e.severity
            )
        
        if not attacker.is_alive:
            raise CombatError(
                f"{attacker.name} cannot attack - not alive",
                attacker_name=attacker.name,
                target_name=target.name,
                severity=ErrorSeverity.MODERATE,
                recovery_suggestion="Ensure the attacker is alive before attempting attacks"
            )
        
        if not target.is_alive:
            raise CombatError(
                f"{target.name} cannot be attacked - not alive",
                attacker_name=attacker.name,
                target_name=target.name,
                severity=ErrorSeverity.MINOR,  # This is often expected behavior
                recovery_suggestion="Choose a living target for the attack"
            )
        
        if weapon_data:
            required_keys = ['name', 'damage', 'ability', 'damage_type']
            missing_keys = [key for key in required_keys if key not in weapon_data]
            if missing_keys:
                raise CombatError(
                    f"Weapon data missing keys: {missing_keys}",
                    attacker_name=attacker.name,
                    target_name=target.name,
                    context={'missing_keys': missing_keys, 'weapon_data': weapon_data},
                    severity=ErrorSeverity.MAJOR,
                    recovery_suggestion=f"Add missing weapon data keys: {missing_keys}"
                )
        
        return True

    @staticmethod
    def handle_damage_application(target, damage, damage_type="bludgeoning", source=None):
        """Enhanced damage application with comprehensive validation."""
        try:
            DnDErrorHandler.validate_creature(target, "damage application")
        except DnDError as e:
            # Don't re-raise, just log and return - damage application should be permissive
            logger = logging.getLogger('DnDSystem')
            logger.warning(f"Damage application to invalid target: {e}")
            return
        
        # Validate damage amount
        if damage < 0:
            logger = logging.getLogger('DnDSystem')
            logger.warning(f"Negative damage ({damage}) converted to 0")
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
            # Create a detailed error for damage application failure
            damage_error = DnDError(
                f"Failed to apply damage to {target.name}: {str(e)}",
                severity=ErrorSeverity.MAJOR,
                context={
                    'target_name': target.name,
                    'damage': damage,
                    'damage_type': damage_type,
                    'source_name': getattr(source, 'name', 'Unknown') if source else None
                },
                recovery_suggestion="Check target's damage handling methods and ensure HP tracking is working"
            )
            DnDErrorHandler._handle_dnd_error(damage_error, "damage application")

    @staticmethod
    def register_error_callback(callback):
        """Register a callback function to be called when errors occur."""
        DnDErrorHandler._error_callbacks.append(callback)

    @staticmethod
    def get_error_metrics() -> Dict:
        """Get current error metrics for system health monitoring."""
        return DnDErrorHandler._metrics.get_error_summary()

    @staticmethod
    def reset_error_metrics():
        """Reset error metrics (useful for testing or after handling issues)."""
        DnDErrorHandler._metrics = ErrorMetrics()

    @staticmethod
    def create_context_manager(operation_name: str, **context):
        """Create a context manager for error handling with automatic context."""
        class ErrorContext:
            def __init__(self, op_name, ctx):
                self.operation_name = op_name
                self.context = ctx
                self.start_time = time.time()
            
            def __enter__(self):
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                if exc_type:
                    operation_time = time.time() - self.start_time
                    if isinstance(exc_val, DnDError):
                        exc_val.context.update(self.context)
                        exc_val.context['operation_duration'] = operation_time
                        DnDErrorHandler._handle_dnd_error(exc_val, self.operation_name)
                    else:
                        error = DnDError(
                            f"Error in {self.operation_name}: {str(exc_val)}",
                            context={**self.context, 'operation_duration': operation_time},
                            recovery_suggestion=f"Review the {self.operation_name} operation for issues"
                        )
                        DnDErrorHandler._handle_dnd_error(error, self.operation_name)
                    return True  # Suppress the exception
        
        return ErrorContext(operation_name, context)