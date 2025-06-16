# File: actions/attack_action.py
"""Implementation of the Attack action."""
from systems.attack_system import AttackSystem

class AttackAction:
    """Represents the Attack action."""
    def __init__(self, weapon_data=None):
        self.name = "Attack"
        self.weapon_data = weapon_data or {
            'name': 'Unarmed Strike',
            'damage': '1+0',
            'ability': 'str',
            'proficient': True,
            'damage_type': 'bludgeoning'
        }

    def execute(self, performer, target):
        """
        Execute an attack.
        NOTE: Action economy is handled by ActionExecutionSystem, not here.
        """
        if not target:
            print(f"  > {performer.name} needs a target to attack!")
            return False
        
        # Just do the attack - no resource management
        if self.weapon_data['name'].lower() == 'unarmed strike':
            return AttackSystem.make_unarmed_attack(performer, target)
        else:
            return AttackSystem.make_weapon_attack(performer, target, self.weapon_data)

class WeaponAttackAction(AttackAction):
    """Specific weapon attack action."""
    def __init__(self, weapon_name, damage_dice, ability='str', damage_type='slashing'):
        weapon_data = {
            'name': weapon_name,
            'damage': damage_dice,
            'ability': ability,
            'proficient': True,
            'damage_type': damage_type
        }
        super().__init__(weapon_data)
        self.name = f"Attack with {weapon_name}"

class UnarmedAttackAction(AttackAction):
    """Unarmed strike action."""
    def __init__(self):
        super().__init__()
        self.name = "Unarmed Strike"