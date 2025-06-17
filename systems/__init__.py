# File: systems/__init__.py
"""Central systems registry for global access - commonly used systems."""

# Core systems - most frequently used
from .d20_system import perform_d20_test, was_last_roll_critical
from .attack_system import AttackSystem, WeaponRanges
from .combat_manager import combat_manager
from .spell_system.spell_manager import SpellManager
from .condition_system import add_condition, remove_condition, has_condition

# Range and positioning systems
from .positioning_system import battlefield, Position, CreatureSize
from .cover_system import RangeSystem, CoverSystem

# Concentration system
from .concentration_system import ConcentrationSystem

# Enhanced condition system functions
from .condition_system import DurationType, process_end_of_turn_saves, update_condition_durations, set_combat_round, cleanup_creature, describe_conditions

__all__ = [
    'perform_d20_test', 'was_last_roll_critical',
    'AttackSystem', 'WeaponRanges',
    'combat_manager', 
    'SpellManager',
    'add_condition', 'remove_condition', 'has_condition',
    'battlefield', 'Position', 'CreatureSize',
    'RangeSystem', 'CoverSystem',
    'ConcentrationSystem',
    'DurationType', 'process_end_of_turn_saves', 'update_condition_durations', 'set_combat_round', 'cleanup_creature', 'describe_conditions'
]