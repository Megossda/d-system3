# File: core/utils.py
""" Core utility functions, including the global dice rolling system. """
import random
import re
import math

def get_ability_modifier(score):
    """Calculates the ability modifier for a given score."""
    return (score - 10) // 2

def roll_dice(dice_notation):
    """
    Rolls dice based on standard D&D notation (e.g., '3d8+5', '1d20-1').
    This function is based on the rules provided in the 2024 Player's Handbook.
    """
    # Regex to parse dice notation like "1d20+5" or "8d6"
    match = re.match(r'(\d+)d(\d+)([+-]\d+)?', dice_notation.lower().strip())
    
    if not match:
        raise ValueError(f"Invalid dice notation: '{dice_notation}'")

    num_dice = int(match.group(1))
    die_type = int(match.group(2))
    modifier_str = match.group(3)

    modifier = int(modifier_str) if modifier_str else 0

    # Roll the specified number of dice and sum the results
    total = sum(random.randint(1, die_type) for _ in range(num_dice))

    return total + modifier

def roll_d20():
    """Rolls a single 20-sided die."""
    return random.randint(1, 20)

def roll_d100():
    """Rolls percentile dice (d100)."""
    return random.randint(1, 100)

def roll_d3():
    """Simulates rolling a d3 by rolling a d6 and dividing by 2, rounded up."""
    # As per PHB rules for simulating dice 
    return math.ceil(random.randint(1, 6) / 2)