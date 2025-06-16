# File: systems/condition_system.py
"""Enhanced condition system with official D&D 2024 condition effects."""

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

def add_condition(target, condition_name):
    """
    Adds a condition to the target creature with proper D&D 2024 effects.
    """
    if not hasattr(target, 'conditions'):
        target.conditions = set()
    
    condition_name = condition_name.lower()
    
    if condition_name not in target.conditions:
        target.conditions.add(condition_name)
        print(f"  > {target.name} now has the {condition_name.upper()} condition!")
        
        # Apply immediate effects
        _apply_condition_effects(target, condition_name)
    else:
        print(f"  > {target.name} already has the {condition_name.upper()} condition.")

def remove_condition(target, condition_name):
    """
    Removes a condition from the target creature and cleans up effects.
    """
    if not hasattr(target, 'conditions'):
        return
    
    condition_name = condition_name.lower()
    
    if condition_name in target.conditions:
        target.conditions.remove(condition_name)
        print(f"  > {target.name} no longer has the {condition_name.upper()} condition.")
        
        # Remove effects
        _remove_condition_effects(target, condition_name)

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