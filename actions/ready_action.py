# File: actions/ready_action.py
"""Implementation of the Ready action with concentration support."""

class ReadyAction:
    """Represents the Ready action with D&D 2024 concentration rules."""
    def __init__(self):
        self.name = "Ready"

    def execute(self, performer, trigger_description, action_to_ready, target=None):
        """
        The performer readies an action to be used in response to a trigger.
        Handles spell concentration according to D&D 2024 rules.
        """
        # Handle spell readying with concentration
        if hasattr(action_to_ready, 'spell') and action_to_ready.spell:
            spell = action_to_ready.spell
            
            # Check if it's a concentration spell
            if hasattr(spell, 'concentration') and spell.concentration:
                from systems.concentration_system import ConcentrationSystem
                
                print(f"  > {performer.name} readies {spell.name} (concentration required)")
                
                # Start concentration for readied spell (until next turn)
                if not ConcentrationSystem.start_concentration(
                    performer, f"Readied {spell.name}", 6.0,  # 6 seconds = 1 round
                    getattr(action_to_ready, 'spell_level', 1),
                    {'readied_spell': True, 'spell': spell, 'target': target}
                ):
                    print(f"  > {performer.name} cannot maintain concentration to ready {spell.name}")
                    return False
        
        # Initialize readied_action if it doesn't exist
        if not hasattr(performer, 'readied_action'):
            performer.readied_action = {}
        
        performer.readied_action['trigger'] = trigger_description
        performer.readied_action['action'] = action_to_ready
        performer.readied_action['target'] = target
        
        print(f"  > {performer.name} is now waiting for: '{trigger_description}'")
        print(f"  > They will respond by using the '{action_to_ready.name}' action.")
        return True
    
    @staticmethod
    def trigger_readied_action(performer, trigger_met=True):
        """
        Trigger a readied action when the condition is met.
        
        Args:
            performer: The creature with the readied action
            trigger_met: Whether the trigger condition was met
            
        Returns:
            bool: True if action was triggered successfully
        """
        if not hasattr(performer, 'readied_action') or not performer.readied_action:
            return False
        
        if not trigger_met:
            return False
        
        try:
            from systems.concentration_system import ConcentrationSystem
            
            readied_data = performer.readied_action
            action = readied_data.get('action')
            target = readied_data.get('target')
            
            print(f"  > {performer.name}'s readied action triggers!")
            
            # Execute the readied action
            from systems.action_execution_system import ActionExecutionSystem, ActionType
            success = ActionExecutionSystem.execute_action(
                performer, action, ActionType.REACTION, target
            )
            
            # Clear the readied action
            performer.readied_action = {}
            
            # If it was a concentration spell, concentration transfers to the actual spell effect
            if hasattr(action, 'spell') and action.spell:
                spell = action.spell
                if hasattr(spell, 'concentration') and spell.concentration:
                    # The concentration now applies to the actual spell effect
                    duration = getattr(spell, 'duration', '1 minute')
                    duration_seconds = ConcentrationSystem.parse_duration(duration)
                    
                    ConcentrationSystem.start_concentration(
                        performer, spell.name, duration_seconds,
                        getattr(action, 'spell_level', 1),
                        {'spell': spell, 'target': target}
                    )
            
            return success
            
        except Exception as e:
            print(f"  > ERROR: Could not trigger readied action - {str(e)}")
            return False