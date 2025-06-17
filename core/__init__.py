# File: core/__init__.py
"""Core utilities for global access - essential dice and utility functions."""

from .utils import (
    roll_dice, roll_d20, roll_d6, roll_d8, roll_d10, roll_d12,
    roll_advantage, roll_disadvantage, get_ability_modifier,
    roll_hit_die, is_valid_dice_notation, parse_dice_notation
)

__all__ = [
    'roll_dice', 'roll_d20', 'roll_d6', 'roll_d8', 'roll_d10', 'roll_d12',
    'roll_advantage', 'roll_disadvantage', 'get_ability_modifier',
    'roll_hit_die', 'is_valid_dice_notation', 'parse_dice_notation'
]