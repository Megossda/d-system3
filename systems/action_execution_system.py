# File: systems/action_execution_system.py
"""Centralized Action Execution System - Manages ALL action execution in the game."""

from systems.action_economy import ActionEconomyManager

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