# File: systems/opportunity_attack_system.py
"""Global system for handling Opportunity Attacks."""

def check_for_opportunity_attack(mover, observer):
    """
    Checks if an observer can make an opportunity attack against a mover.
    """
    print(f"\n--- Checking Opportunity Attack ---")
    print(f"  > {mover.name} is moving away from {observer.name}.")

    # Rule: You don't provoke an Opportunity Attack if you take the Disengage action.
    if mover.is_disengaging:
        print(f"  > {mover.name} is Disengaging. No opportunity attack is provoked.")
        return False
    
    # In a full system, you would check reach, visibility, etc.
    # For now, we assume if not disengaging, an attack is provoked.
    print(f"  > {observer.name} can make an opportunity attack!")
    return True