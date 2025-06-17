# File: __init__.py
"""
D&D System - Complete 5e 2024 Rules Implementation
Global access point for all D&D mechanics and systems.
"""

# Core utilities - globally accessible
from core import (
    roll_dice, roll_d20, roll_d6, roll_d8, roll_d10, roll_d12,
    roll_advantage, roll_disadvantage, get_ability_modifier,
    roll_hit_die, is_valid_dice_notation, parse_dice_notation
)

# Base classes
from creatures.base import Creature

# System managers - including range and positioning
from systems import (
    # Core systems
    perform_d20_test, was_last_roll_critical,
    AttackSystem, WeaponRanges,
    add_condition, remove_condition, has_condition,
    
    # Combat systems
    combat_manager,
    
    # Spell systems
    SpellManager,
    
    # Range and positioning systems
    battlefield, Position, CreatureSize,
    RangeSystem, CoverSystem,
    
    # Concentration system
    ConcentrationSystem,
    
    # Enhanced condition system
    DurationType
)

# Global imports for convenience
__all__ = [
    # Dice and utilities
    'roll_dice', 'roll_d20', 'roll_d6', 'roll_d8', 'roll_d10', 'roll_d12',
    'roll_advantage', 'roll_disadvantage', 'get_ability_modifier', 'roll_hit_die',
    
    # Base classes
    'Creature',
    
    # Core system functions
    'perform_d20_test', 'was_last_roll_critical',
    'add_condition', 'remove_condition', 'has_condition',
    
    # System managers
    'AttackSystem', 'WeaponRanges', 'combat_manager', 'SpellManager',
    
    # Range and positioning
    'battlefield', 'Position', 'CreatureSize', 'RangeSystem', 'CoverSystem',
    
    # Concentration
    'ConcentrationSystem',
    
    # Enhanced conditions
    'DurationType'
]

# Version info
__version__ = "1.0.0"
__author__ = "D&D System"
__description__ = "Complete D&D 5e 2024 rules implementation with range integration"