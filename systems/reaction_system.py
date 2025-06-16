# File: systems/reaction_system.py
"""Global system for handling reactions and triggers for readied actions."""

def check_for_triggers(event_description, potential_reactors):
    """Checks if an event triggers any readied actions from a list of creatures."""
    print(f"\n--- Event Occurred: '{event_description}' ---")
    print("  > Checking for reactions...")

    for reactor in potential_reactors:
        if reactor.readied_action.get('trigger') == event_description:
            print(f"  > {reactor.name}'s trigger matches! They use their Reaction.")
            
            action = reactor.readied_action['action']
            if hasattr(action, 'execute'):
                # Simplified execution for testing purposes.
                action.execute(reactor)

            # Clear the readied action after use.
            reactor.readied_action = {'trigger': None, 'action': None, 'target': None}
            return # Only one reaction per event in this simple model.
            
    print("  > No readied actions were triggered.")