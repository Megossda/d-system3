# File: systems/condition_system.py
"""Global system for managing creature conditions."""

def add_condition(target, condition):
    """Adds a condition to the target creature if it doesn't already have it."""
    if not hasattr(target, 'conditions'):
        target.conditions = set()

    if condition not in target.conditions:
        target.conditions.add(condition)
        print(f"  > {target.name} now has the {condition.upper()} condition!")

def remove_condition(target, condition):
    """Removes a condition from the target creature."""
    if hasattr(target, 'conditions') and condition in target.conditions:
        target.conditions.remove(condition)
        print(f"  > {target.name} no longer has the {condition.upper()} condition.")

def has_condition(target, condition):
    """Checks if a target has a specific condition."""
    return hasattr(target, 'conditions') and condition in target.conditions