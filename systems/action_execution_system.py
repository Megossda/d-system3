# File: systems/action_execution_system.py
"""Centralized Action Execution System - Manages ALL action execution in the game."""

from systems.action_economy import ActionEconomyManager
from systems.cover_system import RangeSystem, CoverSystem
from systems.positioning_system import battlefield

class ActionType:
    """Constants for action types."""
    ACTION = "action"
    BONUS_ACTION = "bonus_action"
    REACTION = "reaction"
    FREE_ACTION = "free_action"

class ActionResult:
    """Result of an action execution."""
    def __init__(self, success=False, message="", action_used=False):
        self.success = success
        self.message = message
        self.action_used = action_used

class ActionExecutionSystem:
    """The central system that manages ALL action execution."""
    
    @staticmethod
    def execute_action(performer, action_instance, action_type=ActionType.ACTION, target=None, **kwargs):
        """
        Universal action execution handler.
        """
        
        # Validate the action can be performed
        if not ActionExecutionSystem._validate_action(performer, action_type):
            return ActionResult(False, f"{performer.name} cannot take a {action_type}")
        
        # Range validation for targeted actions
        if target and ActionExecutionSystem._action_requires_range_check(action_instance):
            range_check_result = ActionExecutionSystem._validate_action_range(
                performer, target, action_instance
            )
            if not range_check_result.success:
                return range_check_result
        
        # Consume the action resource FIRST
        if not ActionExecutionSystem._consume_resource(performer, action_type, action_instance.name):
            return ActionResult(False, f"{performer.name} has already used their {action_type}")
        
        # Log the action
        print(f"\n--- {performer.name}'s {action_type.replace('_', ' ').title()}: {action_instance.name} ---")
        
        try:
            # Execute the actual action
            if target:
                success = action_instance.execute(performer, target, **kwargs)
            else:
                success = action_instance.execute(performer, **kwargs)
            
            return ActionResult(success, f"{action_instance.name} {'succeeded' if success else 'failed'}", True)
            
        except Exception as e:
            # If action fails, refund the resource
            ActionExecutionSystem._refund_resource(performer, action_type)
            return ActionResult(False, f"{action_instance.name} failed: {str(e)}", False)
    
    @staticmethod
    def _validate_action(performer, action_type):
        """Validate if the action can be performed."""
        if not performer.is_alive:
            return False
        
        # Check for incapacitating conditions
        if hasattr(performer, 'conditions'):
            if 'incapacitated' in performer.conditions:
                return False
        
        return True
    
    @staticmethod
    def _consume_resource(performer, action_type, action_name):
        """Consume the appropriate action resource."""
        economy = ActionEconomyManager.get_economy(performer)
        
        if action_type == ActionType.ACTION:
            return economy.use_action(action_name)
        elif action_type == ActionType.BONUS_ACTION:
            return economy.use_bonus_action(action_name)
        elif action_type == ActionType.REACTION:
            return economy.use_reaction(action_name)
        elif action_type == ActionType.FREE_ACTION:
            return True  # Free actions don't consume resources
        
        return False
    
    @staticmethod
    def _refund_resource(performer, action_type):
        """Refund an action resource if the action failed."""
        economy = ActionEconomyManager.get_economy(performer)
        
        if action_type == ActionType.ACTION:
            economy.action_used = False
        elif action_type == ActionType.BONUS_ACTION:
            economy.bonus_action_used = False
        elif action_type == ActionType.REACTION:
            economy.reaction_used = False
    
    @staticmethod
    def _action_requires_range_check(action_instance):
        """Check if an action requires range validation."""
        # Attack actions always need range checks
        if hasattr(action_instance, 'weapon_data') or 'attack' in action_instance.name.lower():
            return True
        
        # Spell actions need range checks
        if hasattr(action_instance, 'spell') or 'spell' in action_instance.name.lower():
            return True
        
        # Actions with explicit range requirements
        if hasattr(action_instance, 'range') or hasattr(action_instance, 'requires_range_check'):
            return getattr(action_instance, 'requires_range_check', True)
        
        # Touch-based actions (help, etc.) need range checks
        touch_actions = ['help', 'grapple', 'shove', 'stabilize']
        if any(touch_action in action_instance.name.lower() for touch_action in touch_actions):
            return True
        
        return False
    
    @staticmethod
    def _validate_action_range(performer, target, action_instance):
        """Validate that an action can reach its target."""
        try:
            # Determine action range
            action_range = ActionExecutionSystem._get_action_range(action_instance)
            
            # Check range
            range_check = RangeSystem.check_range(performer, target, action_range)
            if not range_check['in_range']:
                return ActionResult(
                    False, 
                    f"{target.name} is out of range! (Distance: {range_check['distance']} feet, Required: {action_range})"
                )
            
            # Check for cover if it's a targeted offensive action
            if ActionExecutionSystem._is_offensive_action(action_instance):
                cover_info = CoverSystem.determine_cover(performer, target)
                if not cover_info['can_target']:
                    return ActionResult(
                        False,
                        f"{target.name} has total cover and cannot be targeted!"
                    )
            
            # Range check passed
            if range_check['disadvantage']:
                print(f"  > {target.name} is at long range (Distance: {range_check['distance']} feet) - may affect roll")
            
            return ActionResult(True, "Range check passed")
            
        except Exception as e:
            # If range checking fails, assume action can proceed
            print(f"  > Warning: Range check failed ({e}), proceeding with action")
            return ActionResult(True, "Range check bypassed due to error")
    
    @staticmethod
    def _get_action_range(action_instance):
        """Get the range of an action."""
        # Explicit range attribute
        if hasattr(action_instance, 'range'):
            return action_instance.range
        
        # Weapon-based actions
        if hasattr(action_instance, 'weapon_data'):
            weapon_data = action_instance.weapon_data
            if isinstance(weapon_data, dict) and 'range' in weapon_data:
                return weapon_data['range']
            elif isinstance(weapon_data, dict) and 'name' in weapon_data:
                from systems.attack_system import WeaponRanges
                return WeaponRanges.get_weapon_range(weapon_data['name'])
        
        # Spell-based actions
        if hasattr(action_instance, 'spell'):
            spell = action_instance.spell
            if hasattr(spell, 'range_type'):
                return ActionExecutionSystem._parse_spell_range(spell.range_type)
        
        # Default ranges for common actions
        action_name = action_instance.name.lower()
        if any(touch in action_name for touch in ['help', 'grapple', 'shove', 'stabilize']):
            return 5  # Touch range
        elif 'throw' in action_name:
            return (20, 60)  # Typical thrown weapon range
        
        # Default melee range
        return 5
    
    @staticmethod
    def _is_offensive_action(action_instance):
        """Check if an action is offensive and should be blocked by total cover."""
        offensive_keywords = ['attack', 'damage', 'harm', 'spell', 'fire', 'lightning', 'force']
        action_name = action_instance.name.lower()
        return any(keyword in action_name for keyword in offensive_keywords)
    
    @staticmethod
    def _parse_spell_range(range_string):
        """Parse a spell's range string - same as in SpellManager."""
        if not range_string:
            return 5
        
        range_lower = range_string.lower()
        
        if 'touch' in range_lower:
            return 5
        elif 'self' in range_lower:
            return 0
        elif 'sight' in range_lower:
            return 1000
        elif 'unlimited' in range_lower:
            return float('inf')
        
        import re
        numbers = re.findall(r'\d+', range_string)
        if numbers:
            return int(numbers[0])
        
        return 30

# Convenience wrapper
class ActionExecutor:
    """Convenience wrapper for common action executions."""
    
    @staticmethod
    def action(performer, action_instance, target=None, **kwargs):
        return ActionExecutionSystem.execute_action(performer, action_instance, ActionType.ACTION, target, **kwargs)
    
    @staticmethod
    def bonus_action(performer, action_instance, target=None, **kwargs):
        return ActionExecutionSystem.execute_action(performer, action_instance, ActionType.BONUS_ACTION, target, **kwargs)
    
    @staticmethod
    def reaction(performer, action_instance, target=None, **kwargs):
        return ActionExecutionSystem.execute_action(performer, action_instance, ActionType.REACTION, target, **kwargs)