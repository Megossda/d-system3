# File: systems/condition_system.py
"""Enhanced condition system with duration tracking and D&D 2024 condition effects."""

import time
from typing import Dict, Optional, Any
from enum import Enum
import logging

logger = logging.getLogger('ConditionSystem')

class DurationType(Enum):
    """Types of condition durations."""
    ROUNDS = "rounds"
    MINUTES = "minutes" 
    HOURS = "hours"
    SAVE_ENDS = "save_ends"
    PERMANENT = "permanent"
    UNTIL_DISPELLED = "until_dispelled"

# Global condition tracking
_creature_conditions = {}
_current_combat_round = 0

class ConditionEffects:
    """Official D&D 2024 condition effects and their mechanical impacts."""
    
    INCAPACITATED = {
        'name': 'Incapacitated',
        'effects': {
            'no_actions': True,           # Can't take any action, Bonus Action, or Reaction
            'breaks_concentration': True,  # Concentration is broken
            'no_speech': True,            # Can't speak
            'initiative_disadvantage': True  # Disadvantage on Initiative if Incapacitated when rolling
        },
        'description': "You can't take actions, lose concentration, can't speak, and have Initiative disadvantage if incapacitated when rolling."
    }
    
    PRONE = {
        'name': 'Prone',
        'effects': {
            'restricted_movement': True,   # Only crawl or spend half Speed to stand
            'attack_disadvantage': True,   # Disadvantage on attack rolls
            'incoming_attack_advantage': True,  # Advantage if attacker within 5ft, disadvantage otherwise
        },
        'description': "Restricted movement, disadvantage on attacks, advantage for nearby attackers."
    }
    
    # Add more conditions as needed
    STUNNED = {
        'name': 'Stunned',
        'effects': {
            'incapacitated': True,        # Has all Incapacitated effects
            'no_movement': True,          # Can't move
            'auto_fail_str_dex_saves': True,  # Automatically fail Strength and Dexterity saves
            'incoming_attack_advantage': True  # Attack rolls against you have Advantage
        },
        'description': "Incapacitated, can't move, auto-fail Str/Dex saves, incoming attacks have advantage."
    }
    
    UNCONSCIOUS = {
        'name': 'Unconscious',
        'effects': {
            'incapacitated': True,        # Has all Incapacitated effects
            'prone': True,                # Also has Prone condition
            'no_movement': True,          # Can't move
            'no_awareness': True,         # Unaware of surroundings
            'auto_fail_str_dex_saves': True,  # Auto-fail Str/Dex saves
            'incoming_attack_advantage': True,  # Attacks have advantage
            'critical_hits_close': True   # Hits within 5 feet are critical hits
        },
        'description': "Incapacitated, prone, unaware, auto-fail saves, nearby hits are critical."
    }

def add_condition(target, condition_name, duration_type=None, duration_value=None, 
                 save_dc=None, save_ability=None, source=None, source_name=None):
    """
    Adds a condition to the target creature with duration tracking and D&D 2024 effects.
    
    Args:
        target: The creature to affect
        condition_name: Name of the condition
        duration_type: DurationType enum or None for permanent
        duration_value: Duration amount (rounds, minutes, etc.)
        save_dc: DC for save-to-end conditions
        save_ability: Ability for saves ('con', 'wis', etc.)
        source: The source object (spell, ability, etc.)
        source_name: Human-readable source name
    """
    if not hasattr(target, 'conditions'):
        target.conditions = set()
    
    condition_name = condition_name.lower()
    
    # Initialize enhanced tracking
    if target not in _creature_conditions:
        _creature_conditions[target] = {}
    
    # Set defaults based on condition type
    condition_defaults = {
        'stunned': {'duration_type': DurationType.SAVE_ENDS, 'save_ability': 'con'},
        'poisoned': {'duration_type': DurationType.SAVE_ENDS, 'save_ability': 'con'},
        'frightened': {'duration_type': DurationType.SAVE_ENDS, 'save_ability': 'wis'},
        'charmed': {'duration_type': DurationType.SAVE_ENDS, 'save_ability': 'wis'},
        'paralyzed': {'duration_type': DurationType.SAVE_ENDS, 'save_ability': 'con'},
        'blinded': {'duration_type': DurationType.SAVE_ENDS, 'save_ability': 'con'},
        'deafened': {'duration_type': DurationType.SAVE_ENDS, 'save_ability': 'con'},
        'restrained': {'duration_type': DurationType.PERMANENT},
        'grappled': {'duration_type': DurationType.PERMANENT},
        'prone': {'duration_type': DurationType.PERMANENT},
        'incapacitated': {'duration_type': DurationType.ROUNDS, 'duration_value': 1},
        'unconscious': {'duration_type': DurationType.PERMANENT}
    }
    
    defaults = condition_defaults.get(condition_name, {})
    if duration_type is None:
        duration_type = defaults.get('duration_type', DurationType.PERMANENT)
    if duration_value is None:
        duration_value = defaults.get('duration_value', 0)
    if save_ability is None:
        save_ability = defaults.get('save_ability')
    if source_name is None:
        source_name = getattr(source, 'name', 'Unknown')
    
    # Store enhanced condition data
    _creature_conditions[target][condition_name] = {
        'duration_type': duration_type,
        'duration_value': duration_value,
        'save_dc': save_dc,
        'save_ability': save_ability,
        'source': source,
        'source_name': source_name,
        'applied_time': time.time(),
        'applied_round': _current_combat_round
    }
    
    # Legacy compatibility
    target.conditions.add(condition_name)
    
    # Print notification
    duration_text = _get_duration_text(condition_name, target)
    print(f"  > {target.name} gains {condition_name.upper()} condition ({duration_text})")
    if source_name != "Unknown":
        print(f"    Source: {source_name}")
    
    # Apply immediate effects
    _apply_condition_effects(target, condition_name)
    
    # Handle concentration breaking conditions
    from systems.concentration_system import ConcentrationSystem
    ConcentrationSystem.handle_condition_change(target, condition_name, True)

def remove_condition(target, condition_name, reason="Removed"):
    """
    Removes a condition from the target creature and cleans up effects.
    """
    if not hasattr(target, 'conditions'):
        return False
    
    condition_name = condition_name.lower()
    
    if condition_name in target.conditions:
        # Remove from enhanced tracking
        if target in _creature_conditions and condition_name in _creature_conditions[target]:
            del _creature_conditions[target][condition_name]
        
        # Remove from legacy tracking
        target.conditions.remove(condition_name)
        print(f"  > {target.name} no longer has {condition_name.upper()} condition ({reason})")
        
        # Remove effects
        _remove_condition_effects(target, condition_name)
        return True
    return False

def has_condition(target, condition_name):
    """
    Checks if a target has a specific condition.
    """
    if not hasattr(target, 'conditions'):
        return False
    return condition_name.lower() in target.conditions

def _apply_condition_effects(target, condition_name):
    """Apply the mechanical effects of a condition."""
    
    if condition_name == 'incapacitated':
        # Break concentration
        if hasattr(target, 'concentrating_on') and target.concentrating_on:
            print(f"    > {target.name} loses concentration on {target.concentrating_on.name}!")
            target.concentrating_on = None
    
    elif condition_name == 'prone':
        # Restrict movement - handled in movement system
        pass
    
    elif condition_name == 'stunned':
        # Stunned includes incapacitated effects
        if not has_condition(target, 'incapacitated'):
            add_condition(target, 'incapacitated')
    
    elif condition_name == 'unconscious':
        # Unconscious includes both incapacitated and prone
        if not has_condition(target, 'incapacitated'):
            add_condition(target, 'incapacitated')
        if not has_condition(target, 'prone'):
            add_condition(target, 'prone')

def _remove_condition_effects(target, condition_name):
    """Remove the mechanical effects of a condition."""
    
    if condition_name == 'unconscious':
        # Don't automatically remove incapacitated/prone - they might be from other sources
        # In a full system, you'd track condition sources
        pass

def check_condition_prevents_action(target, action_type="action"):
    """
    Check if any conditions prevent the target from taking a specific action.
    
    Args:
        target: The creature attempting the action
        action_type: Type of action ("action", "bonus_action", "reaction", "movement")
    
    Returns:
        tuple: (prevented: bool, reason: str)
    """
    if not hasattr(target, 'conditions') or not target.conditions:
        return False, ""
    
    # Check for incapacitated (prevents all actions)
    if has_condition(target, 'incapacitated'):
        if action_type in ['action', 'bonus_action', 'reaction']:
            return True, f"{target.name} is incapacitated and cannot take actions"
    
    # Check for stunned (prevents movement too)
    if has_condition(target, 'stunned'):
        if action_type == 'movement':
            return True, f"{target.name} is stunned and cannot move"
    
    # Check for unconscious (prevents everything)
    if has_condition(target, 'unconscious'):
        if action_type in ['action', 'bonus_action', 'reaction', 'movement']:
            return True, f"{target.name} is unconscious and cannot act"
    
    return False, ""

def get_condition_attack_modifiers(attacker, target):
    """
    Get attack roll modifiers based on conditions.
    
    Returns:
        dict: {'advantage': bool, 'disadvantage': bool, 'auto_hit': bool, 'auto_crit': bool}
    """
    modifiers = {
        'advantage': False,
        'disadvantage': False,
        'auto_hit': False,
        'auto_crit': False
    }
    
    if not hasattr(target, 'conditions') or not hasattr(attacker, 'conditions'):
        return modifiers
    
    # Attacker conditions
    if has_condition(attacker, 'prone'):
        modifiers['disadvantage'] = True  # Prone attackers have disadvantage
    
    # Target conditions
    if has_condition(target, 'prone'):
        # Check if attacker is within 5 feet (simplified - in full system check positioning)
        # For now, assume melee attacks are within 5 feet
        attacker_close = True  # This would check positioning in full system
        
        if attacker_close:
            modifiers['advantage'] = True
        else:
            modifiers['disadvantage'] = True
    
    if has_condition(target, 'unconscious'):
        modifiers['advantage'] = True
        # Check if within 5 feet for auto-crit
        attacker_close = True  # This would check positioning in full system
        if attacker_close:
            modifiers['auto_crit'] = True
    
    if has_condition(target, 'stunned'):
        modifiers['advantage'] = True
    
    return modifiers

def get_condition_save_modifiers(creature, save_type):
    """
    Get saving throw modifiers based on conditions.
    
    Returns:
        dict: {'advantage': bool, 'disadvantage': bool, 'auto_fail': bool, 'auto_succeed': bool}
    """
    modifiers = {
        'advantage': False,
        'disadvantage': False,
        'auto_fail': False,
        'auto_succeed': False
    }
    
    if not hasattr(creature, 'conditions'):
        return modifiers
    
    # Auto-fail conditions
    if has_condition(creature, 'stunned') or has_condition(creature, 'unconscious'):
        if save_type.lower() in ['str', 'dex', 'strength', 'dexterity']:
            modifiers['auto_fail'] = True
    
    return modifiers

def get_initiative_modifiers(creature):
    """
    Get initiative roll modifiers based on conditions.
    
    Returns:
        dict: {'advantage': bool, 'disadvantage': bool}
    """
    modifiers = {'advantage': False, 'disadvantage': False}
    
    if not hasattr(creature, 'conditions'):
        return modifiers
    
    # Incapacitated when rolling initiative
    if has_condition(creature, 'incapacitated'):
        modifiers['disadvantage'] = True
    
    return modifiers

def can_take_reactions(creature):
    """Check if a creature can take reactions based on conditions."""
    prevented, reason = check_condition_prevents_action(creature, "reaction")
    return not prevented

def get_movement_restrictions(creature):
    """
    Get movement restrictions based on conditions.
    
    Returns:
        dict: Movement restriction information
    """
    restrictions = {
        'can_move': True,
        'crawl_only': False,
        'half_speed_to_stand': False,
        'no_movement': False
    }
    
    if not hasattr(creature, 'conditions'):
        return restrictions
    
    if has_condition(creature, 'prone'):
        restrictions['crawl_only'] = True
        restrictions['half_speed_to_stand'] = True
    
    if has_condition(creature, 'stunned') or has_condition(creature, 'unconscious'):
        restrictions['no_movement'] = True
        restrictions['can_move'] = False
    
    return restrictions

def describe_condition_effects(creature):
    """Get a description of all active condition effects."""
    if not hasattr(creature, 'conditions') or not creature.conditions:
        return f"{creature.name} has no active conditions."
    
    descriptions = []
    for condition in creature.conditions:
        condition_data = getattr(ConditionEffects, condition.upper(), None)
        if condition_data:
            descriptions.append(f"{condition.title()}: {condition_data['description']}")
        else:
            descriptions.append(f"{condition.title()}: Unknown condition")
    
    return f"{creature.name} conditions:\n" + "\n".join(f"  • {desc}" for desc in descriptions)

# Enhanced condition system functions
def process_end_of_turn_saves(creature):
    """Process end-of-turn saving throws for save-to-end conditions."""
    if creature not in _creature_conditions:
        return 0
    
    conditions_to_remove = []
    saves_made = 0
    
    for condition_name, condition_data in _creature_conditions[creature].items():
        if (condition_data['duration_type'] == DurationType.SAVE_ENDS and 
            condition_data['save_ability'] and condition_data['save_dc']):
            
            print(f"  > {creature.name} makes a {condition_data['save_ability'].upper()} save to end {condition_name.upper()} (DC {condition_data['save_dc']})")
            
            from systems.d20_system import perform_d20_test
            success = perform_d20_test(
                creature=creature,
                ability_name=condition_data['save_ability'],
                check_type=f"{condition_data['save_ability']}_save",
                dc=condition_data['save_dc'],
                is_saving_throw=True
            )
            
            if success:
                conditions_to_remove.append(condition_name)
                saves_made += 1
                print(f"  > {creature.name} successfully saves against {condition_name.upper()}!")
            else:
                print(f"  > {creature.name} fails the save against {condition_name.upper()}")
    
    # Remove conditions that were successfully saved against
    for condition_name in conditions_to_remove:
        remove_condition(creature, condition_name, "Successful save")
    
    return saves_made

def update_condition_durations(rounds_passed=0):
    """Update all condition durations and remove expired ones."""   
    global _current_combat_round
    if rounds_passed > 0:
        _current_combat_round += rounds_passed
    
    current_time = time.time()
    expired_conditions = []
    
    for creature, conditions in _creature_conditions.items():
        for condition_name, condition_data in conditions.items():
            if _is_condition_expired(condition_data, current_time, _current_combat_round):
                expired_conditions.append((creature, condition_name))
    
    # Remove expired conditions
    removed_count = 0
    for creature, condition_name in expired_conditions:
        remove_condition(creature, condition_name, "Duration expired")
        removed_count += 1
    
    return removed_count

def set_combat_round(round_number):
    """Set the current combat round for duration tracking."""   
    global _current_combat_round
    _current_combat_round = round_number

def get_combat_round():
    """Get the current combat round."""   
    return _current_combat_round

def cleanup_creature(creature):
    """Remove all condition tracking for a creature."""   
    if creature in _creature_conditions:
        del _creature_conditions[creature]

def describe_conditions(creature):
    """Get a description of all conditions with durations."""   
    if creature not in _creature_conditions:
        return "No conditions"
    
    descriptions = []
    for condition_name, condition_data in _creature_conditions[creature].items():
        duration = _get_duration_text(condition_name, creature)
        source = f" (from {condition_data['source_name']})" if condition_data['source_name'] != "Unknown" else ""
        descriptions.append(f"{condition_name.upper()}: {duration}{source}")
    
    return "; ".join(descriptions) if descriptions else "No conditions"

def _get_duration_text(condition_name, creature):
    """Get human-readable duration text for a condition."""   
    if creature not in _creature_conditions or condition_name not in _creature_conditions[creature]:
        return "Unknown duration"
    
    condition_data = _creature_conditions[creature][condition_name]
    duration_type = condition_data['duration_type']
    duration_value = condition_data['duration_value']
    
    if duration_type == DurationType.PERMANENT:
        return "Permanent"
    elif duration_type == DurationType.UNTIL_DISPELLED:
        return "Until dispelled"
    elif duration_type == DurationType.SAVE_ENDS:
        return "Until save succeeds"
    elif duration_type == DurationType.ROUNDS:
        remaining = max(0, condition_data['applied_round'] + duration_value - _current_combat_round)
        return f"{remaining} rounds"
    elif duration_type == DurationType.MINUTES:
        remaining = max(0, (condition_data['applied_time'] + duration_value * 60) - time.time())
        return f"{remaining/60:.1f} minutes"
    elif duration_type == DurationType.HOURS:
        remaining = max(0, (condition_data['applied_time'] + duration_value * 3600) - time.time())
        return f"{remaining/3600:.1f} hours"
    
    return "Unknown"

def _is_condition_expired(condition_data, current_time, current_round):
    """Check if a condition has expired."""   
    duration_type = condition_data['duration_type']
    duration_value = condition_data['duration_value']
    
    if duration_type == DurationType.PERMANENT or duration_type == DurationType.UNTIL_DISPELLED:
        return False
    elif duration_type == DurationType.SAVE_ENDS:
        return False  # Only expires on successful save
    elif duration_type == DurationType.ROUNDS:
        return current_round >= (condition_data['applied_round'] + duration_value)
    elif duration_type == DurationType.MINUTES:
        return current_time >= (condition_data['applied_time'] + duration_value * 60)
    elif duration_type == DurationType.HOURS:
        return current_time >= (condition_data['applied_time'] + duration_value * 3600)
    
    return False