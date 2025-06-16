# File: systems/d20_system.py
"""Global system for handling all D20 Tests."""
from core.utils import roll_d20
from systems.condition_system import has_condition

def perform_d20_test(
    creature,
    ability_name,
    check_type=None,
    target=None,
    dc=None,
    ac=None,
    has_advantage=False,
    has_disadvantage=False,
    is_saving_throw=False,
    attacker_is_within_5_feet=False,
    is_attack_roll=False,
    is_influence_check=False # --- NEW --- Flag to identify an influence check
):
    """
    Performs a generic D20 Test with full social attitude mechanics.
    """
    # --- NEW: SOCIAL INTERACTION RULE ---
    # Check the target's attitude if this is an influence check.
    if is_influence_check and target:
        if target.attitude == 'Friendly':
            print(f"  > Target ({target.name}) is Friendly, granting Advantage.")
            has_advantage = True
        elif target.attitude == 'Hostile':
            print(f"  > Target ({target.name}) is Hostile, imposing Disadvantage.")
            has_disadvantage = True
            
    # ... (Advantage/Disadvantage logic is unchanged) ...
    if target and has_condition(target, 'prone'):
        if attacker_is_within_5_feet:
            print(f"  > Target ({target.name}) is Prone and attacker is within 5ft, imposing Advantage.")
            has_advantage = True
        else:
            print(f"  > Target ({target.name}) is Prone and attacker is at range, imposing Disadvantage.")
            has_disadvantage = True

    if has_condition(creature, 'prone'):
        print(f"  > {creature.name} is Prone and has Disadvantage on the attack roll.")
        has_disadvantage = True

    can_benefit_from_dodge = creature.is_dodging and not has_condition(creature, 'incapacitated') and creature.speed > 0
    if can_benefit_from_dodge and is_saving_throw and ability_name.lower() == 'dex':
        print(f"  > {creature.name} is Dodging, gaining Advantage on the Dexterity save.")
        has_advantage = True

    if target and target.is_dodging and not has_condition(target, 'incapacitated') and target.speed > 0:
        print(f"  > Target ({target.name}) is Dodging, imposing Disadvantage on the attack.")
        has_disadvantage = True
        
    if target and creature.help_effects.get('attack_advantage_against') == target:
        print(f"  > {creature.name} has help attacking {target.name}, gaining Advantage.")
        has_advantage = True
        creature.help_effects['attack_advantage_against'] = None

    if check_type and creature.help_effects.get('ability_check_advantage_on') == check_type.lower():
        print(f"  > {creature.name} has help with a '{check_type}' check, gaining Advantage.")
        has_advantage = True
        creature.help_effects['ability_check_advantage_on'] = None

    target_number = dc if dc is not None else (target.ac if target else ac)
    if target_number is None:
        raise ValueError("A D20 Test requires either a DC or an AC.")

    # Roll the d20
    # ... (rolling logic is unchanged) ...
    if has_advantage and not has_disadvantage:
        roll1, roll2 = roll_d20(), roll_d20()
        d20_result = max(roll1, roll2)
        print(f"  > Rolling with Advantage: got {roll1}, {roll2}. Using {d20_result}")
    elif has_disadvantage and not has_advantage:
        roll1, roll2 = roll_d20(), roll_d20()
        d20_result = min(roll1, roll2)
        print(f"  > Rolling with Disadvantage: got {roll1}, {roll2}. Using {d20_result}")
    else:
        if has_advantage and has_disadvantage:
            print("  > Advantage & Disadvantage cancel. Rolling normally.")
        d20_result = roll_d20()
        print(f"  > Rolling 1d20: got {d20_result}")

    # Handle special attack roll outcomes
    if is_attack_roll:
        if d20_result == 20:
            print("  > Natural 20! Automatic Hit!")
            return True
        if d20_result == 1:
            print("  > Natural 1! Automatic Miss!")
            return False

    # Calculate final total
    is_proficient = check_type and check_type.lower() in creature.proficiencies
    proficiency_bonus = creature.proficiency_bonus if is_proficient else 0
    ability_modifier = creature.get_ability_modifier(ability_name)
    total = d20_result + ability_modifier + proficiency_bonus
    
    prof_text = f"+ {proficiency_bonus} (prof)" if is_proficient else "+ 0 (no prof)"
    print(f"  > Total: {d20_result} (roll) + {ability_modifier} ({ability_name}) {prof_text} = {total}")

    # Compare to the target number
    if total >= target_number:
        print(f"  > Success! ({total} vs DC/AC {target_number})")
        return True
    else:
        print(f"  > Failure. ({total} vs DC/AC {target_number})")
        return False