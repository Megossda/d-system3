# File: systems/concentration_system.py
"""
Concentration System - D&D 2024 Rules Implementation
Manages spell concentration, breaking triggers, and duration tracking.
"""

import time
from typing import Dict, Optional, Tuple, Any
from systems.d20_system import perform_d20_test
import logging

logger = logging.getLogger('ConcentrationSystem')

class ConcentrationEffect:
    """Represents a concentration effect being maintained."""
    
    def __init__(self, effect_name: str, caster, duration_seconds: float, 
                 spell_level: int = None, effect_data: Dict = None):
        self.effect_name = effect_name
        self.caster = caster
        self.duration_seconds = duration_seconds
        self.spell_level = spell_level or 1
        self.effect_data = effect_data or {}
        self.start_time = time.time()
        self.max_end_time = self.start_time + duration_seconds if duration_seconds > 0 else float('inf')
    
    def is_expired(self) -> bool:
        """Check if the concentration effect has expired."""
        if self.duration_seconds <= 0:  # Permanent until broken
            return False
        return time.time() >= self.max_end_time
    
    def time_remaining(self) -> float:
        """Get remaining time in seconds."""
        if self.duration_seconds <= 0:
            return float('inf')
        remaining = self.max_end_time - time.time()
        return max(0, remaining)
    
    def __str__(self):
        return f"{self.effect_name} (Caster: {self.caster.name}, Remaining: {self.time_remaining():.1f}s)"

class ConcentrationSystem:
    """
    Manages concentration effects according to D&D 2024 rules.
    
    Key Rules:
    - Only one concentration effect per creature
    - Concentration breaks on: damage (save), incapacitated, death, new concentration
    - Manual ending requires no action
    - Constitution saves: DC = 10 or half damage (max DC 30)
    """
    
    # Global concentration tracking
    _active_concentrations: Dict[Any, ConcentrationEffect] = {}
    
    # Duration constants (in seconds)
    DURATION_1_MINUTE = 60
    DURATION_10_MINUTES = 600
    DURATION_1_HOUR = 3600
    DURATION_8_HOURS = 28800
    DURATION_24_HOURS = 86400
    
    @classmethod
    def start_concentration(cls, caster, effect_name: str, duration_seconds: float, 
                          spell_level: int = None, effect_data: Dict = None) -> bool:
        """
        Start concentration on an effect.
        
        Args:
            caster: The creature concentrating
            effect_name: Name of the effect
            duration_seconds: How long concentration lasts (0 = until broken)
            spell_level: Spell level if applicable
            effect_data: Additional effect data
            
        Returns:
            bool: True if concentration started successfully
        """
        try:
            # Check if caster can concentrate
            if not cls.can_concentrate(caster):
                logger.warning(f"{caster.name} cannot start concentration - already concentrating")
                return False
            
            # Break existing concentration
            if cls.is_concentrating(caster):
                cls.break_concentration(caster, "New concentration effect")
            
            # Create new concentration effect
            effect = ConcentrationEffect(
                effect_name=effect_name,
                caster=caster,
                duration_seconds=duration_seconds,
                spell_level=spell_level,
                effect_data=effect_data
            )
            
            cls._active_concentrations[caster] = effect
            
            duration_text = f"{duration_seconds}s" if duration_seconds > 0 else "until broken"
            print(f"  > {caster.name} begins concentrating on {effect_name} (Duration: {duration_text})")
            
            logger.info(f"Concentration started: {caster.name} -> {effect_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting concentration: {e}")
            print(f"  > ERROR: Could not start concentration - {str(e)}")
            return False
    
    @classmethod
    def break_concentration(cls, caster, reason: str = "Unknown") -> bool:
        """
        Break concentration for a caster.
        
        Args:
            caster: The creature whose concentration to break
            reason: Reason for breaking concentration
            
        Returns:
            bool: True if concentration was broken
        """
        try:
            if caster not in cls._active_concentrations:
                return False
            
            effect = cls._active_concentrations[caster]
            effect_name = effect.effect_name
            
            # Remove from tracking
            del cls._active_concentrations[caster]
            
            print(f"  > {caster.name}'s concentration on {effect_name} broken ({reason})")
            logger.info(f"Concentration broken: {caster.name} -> {effect_name} ({reason})")
            
            # Handle effect-specific cleanup
            cls._handle_concentration_end(caster, effect, reason)
            
            return True
            
        except Exception as e:
            logger.error(f"Error breaking concentration: {e}")
            return False
    
    @classmethod
    def check_concentration_save(cls, caster, damage_taken: int) -> bool:
        """
        Check if caster maintains concentration after taking damage.
        
        Args:
            caster: The creature taking damage
            damage_taken: Amount of damage taken
            
        Returns:
            bool: True if concentration is maintained
        """
        try:
            if not cls.is_concentrating(caster):
                return True  # No concentration to break
            
            # Calculate DC: 10 or half damage (max 30)
            dc = min(30, max(10, damage_taken // 2))
            
            print(f"  > {caster.name} must make a Constitution save to maintain concentration (DC {dc})")
            
            # Make Constitution saving throw
            success = perform_d20_test(
                creature=caster,
                ability_name='con',
                check_type='constitution_save',
                dc=dc,
                is_saving_throw=True
            )
            
            if success:
                print(f"  > {caster.name} maintains concentration!")
                return True
            else:
                effect = cls._active_concentrations.get(caster)
                effect_name = effect.effect_name if effect else "unknown effect"
                cls.break_concentration(caster, f"Failed Constitution save (DC {dc})")
                return False
                
        except Exception as e:
            logger.error(f"Error in concentration save: {e}")
            # On error, break concentration for safety
            cls.break_concentration(caster, f"Error in concentration save: {str(e)}")
            return False
    
    @classmethod
    def is_concentrating(cls, caster) -> bool:
        """Check if a creature is currently concentrating."""
        return caster in cls._active_concentrations
    
    @classmethod
    def can_concentrate(cls, caster) -> bool:
        """
        Check if a creature can start concentrating.
        
        Args:
            caster: The creature to check
            
        Returns:
            bool: True if they can concentrate
        """
        try:
            # Check if incapacitated
            if hasattr(caster, 'has_condition') and caster.has_condition('incapacitated'):
                return False
            
            # Check if dead
            if hasattr(caster, 'is_alive') and not caster.is_alive:
                return False
            
            # Check if unconscious
            if hasattr(caster, 'has_condition') and caster.has_condition('unconscious'):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking concentration ability: {e}")
            return False
    
    @classmethod
    def get_concentration_effect(cls, caster) -> Optional[ConcentrationEffect]:
        """Get the current concentration effect for a caster."""
        return cls._active_concentrations.get(caster)
    
    @classmethod
    def end_concentration(cls, caster) -> bool:
        """
        Voluntarily end concentration (no action required).
        
        Args:
            caster: The creature ending concentration
            
        Returns:
            bool: True if concentration was ended
        """
        return cls.break_concentration(caster, "Voluntarily ended")
    
    @classmethod
    def update_concentrations(cls):
        """Update all active concentrations, removing expired ones."""
        expired_casters = []
        
        for caster, effect in cls._active_concentrations.items():
            # Check if expired by time
            if effect.is_expired():
                expired_casters.append(caster)
                continue
            
            # Check if caster can still concentrate
            if not cls.can_concentrate(caster):
                expired_casters.append(caster)
                continue
        
        # Remove expired concentrations
        for caster in expired_casters:
            effect = cls._active_concentrations[caster]
            reason = "Duration expired" if effect.is_expired() else "Cannot concentrate"
            cls.break_concentration(caster, reason)
    
    @classmethod
    def get_all_concentrations(cls) -> Dict[Any, ConcentrationEffect]:
        """Get all active concentration effects."""
        cls.update_concentrations()  # Clean up first
        return cls._active_concentrations.copy()
    
    @classmethod
    def clear_all_concentrations(cls):
        """Clear all concentration effects (for testing/reset)."""
        cls._active_concentrations.clear()
    
    @classmethod
    def handle_damage(cls, creature, damage_amount: int, attacker=None):
        """
        Handle damage and trigger concentration saves if needed.
        
        Args:
            creature: The creature taking damage
            damage_amount: Amount of damage
            attacker: The source of damage (optional)
        """
        if cls.is_concentrating(creature) and damage_amount > 0:
            cls.check_concentration_save(creature, damage_amount)
    
    @classmethod
    def handle_condition_change(cls, creature, condition: str, added: bool):
        """
        Handle condition changes that might break concentration.
        
        Args:
            creature: The creature whose condition changed
            condition: The condition name
            added: True if condition was added, False if removed
        """
        if not added:  # Only care about conditions being added
            return
        
        # Conditions that break concentration
        breaking_conditions = ['incapacitated', 'unconscious', 'dead', 'stunned', 'paralyzed']
        
        if condition.lower() in breaking_conditions:
            if cls.is_concentrating(creature):
                cls.break_concentration(creature, f"Gained {condition} condition")
    
    @classmethod
    def _handle_concentration_end(cls, caster, effect: ConcentrationEffect, reason: str):
        """
        Handle cleanup when concentration ends.
        
        Args:
            caster: The creature whose concentration ended
            effect: The concentration effect that ended
            reason: Why concentration ended
        """
        try:
            # Handle spell-specific cleanup
            effect_name = effect.effect_name.lower()
            
            # Remove ongoing effects based on spell type
            if 'shield' in effect_name:
                # Remove shield bonuses
                if hasattr(caster, 'remove_temporary_ac_bonus'):
                    caster.remove_temporary_ac_bonus('shield')
            
            elif 'bless' in effect_name or 'guidance' in effect_name:
                # Remove bonus dice
                if hasattr(caster, 'remove_temporary_bonus'):
                    caster.remove_temporary_bonus(effect_name)
            
            # Add more spell-specific cleanup as needed
            
        except Exception as e:
            logger.error(f"Error in concentration cleanup: {e}")
    
    @classmethod
    def parse_duration(cls, duration_string: str) -> float:
        """
        Parse a duration string into seconds.
        
        Args:
            duration_string: Duration like "1 minute", "10 minutes", "1 hour"
            
        Returns:
            float: Duration in seconds
        """
        duration_lower = duration_string.lower().strip()
        
        # Handle special cases
        if 'instantaneous' in duration_lower or 'instant' in duration_lower:
            return 0
        
        if 'permanent' in duration_lower or 'until dispelled' in duration_lower:
            return -1  # Special flag for permanent
        
        # Parse common durations
        duration_map = {
            '1 minute': cls.DURATION_1_MINUTE,
            '10 minutes': cls.DURATION_10_MINUTES,
            '1 hour': cls.DURATION_1_HOUR,
            '8 hours': cls.DURATION_8_HOURS,
            '24 hours': cls.DURATION_24_HOURS,
        }
        
        for key, seconds in duration_map.items():
            if key in duration_lower:
                return seconds
        
        # Try to extract numbers
        import re
        numbers = re.findall(r'\d+', duration_string)
        if numbers:
            num = int(numbers[0])
            if 'minute' in duration_lower:
                return num * 60
            elif 'hour' in duration_lower:
                return num * 3600
            elif 'day' in duration_lower:
                return num * 86400
        
        # Default to 1 minute for concentration spells
        logger.warning(f"Could not parse duration '{duration_string}', defaulting to 1 minute")
        return cls.DURATION_1_MINUTE