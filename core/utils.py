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

def roll_d4():
    """Rolls a single 4-sided die."""
    return random.randint(1, 4)

def roll_d6():
    """Rolls a single 6-sided die."""
    return random.randint(1, 6)

def roll_d8():
    """Rolls a single 8-sided die."""
    return random.randint(1, 8)

def roll_d10():
    """Rolls a single 10-sided die."""
    return random.randint(1, 10)

def roll_d12():
    """Rolls a single 12-sided die."""
    return random.randint(1, 12)

# --- CONVENIENCE FUNCTIONS ---
def roll_advantage():
    """Rolls 2d20 and returns the higher result."""
    roll1, roll2 = roll_d20(), roll_d20()
    return max(roll1, roll2), (roll1, roll2)

def roll_disadvantage():
    """Rolls 2d20 and returns the lower result."""
    roll1, roll2 = roll_d20(), roll_d20()
    return min(roll1, roll2), (roll1, roll2)

def roll_hit_die(class_name):
    """Rolls the appropriate hit die for a class."""
    hit_dice = {
        'barbarian': 12,
        'fighter': 10,
        'paladin': 10,
        'ranger': 10,
        'bard': 8,
        'cleric': 8,
        'druid': 8,
        'monk': 8,
        'rogue': 8,
        'warlock': 8,
        'artificer': 8,
        'sorcerer': 6,
        'wizard': 6
    }
    
    die_size = hit_dice.get(class_name.lower(), 8)  # Default to d8
    return random.randint(1, die_size)

# --- VALIDATION FUNCTIONS ---
def is_valid_dice_notation(dice_string):
    """Checks if a string is valid dice notation."""
    pattern = r'^\d+d\d+([+-]\d+)?$'
    return bool(re.match(pattern, dice_string.lower().strip()))

def parse_dice_notation(dice_notation):
    """Parses dice notation and returns (num_dice, die_type, modifier)."""
    match = re.match(r'(\d+)d(\d+)([+-]\d+)?', dice_notation.lower().strip())
    
    if not match:
        raise ValueError(f"Invalid dice notation: '{dice_notation}'")
    
    num_dice = int(match.group(1))
    die_type = int(match.group(2))
    modifier = int(match.group(3)) if match.group(3) else 0
    
    return num_dice, die_type, modifier