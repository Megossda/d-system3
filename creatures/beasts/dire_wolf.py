# File: creatures/beasts/dire_wolf.py
"""Implementation of the Dire Wolf enemy."""
from creatures.base import Creature
from core.utils import roll_dice
from systems.d20_system import perform_d20_test
from systems.condition_system import add_condition
from systems.attack_system import AttackSystem

class DireWolf(Creature):
    """A Dire Wolf enemy, based on the 2024 PHB."""

    def __init__(self):
        hp = roll_dice("3d10+6")
        wolf_proficiencies = {'perception', 'stealth', 'bite'}
        super().__init__(
            name="Dire Wolf",
            level=0,
            ac=14,
            hp=hp,
            speed=50,
            stats={'str': 17, 'dex': 15, 'con': 15, 'int': 3, 'wis': 12, 'cha': 7},
            cr=1,
            proficiencies=wolf_proficiencies
        )

    def has_pack_tactics(self, combat_context=None):
        """Checks if Pack Tactics is active."""
        print(f"  > {self.name} benefits from Pack Tactics!")
        return True

    def bite(self, target, combat_context=None, attacker_is_within_5_feet=True):
        """Performs the Bite melee attack using the new attack system."""
        print(f"\n--- {self.name}'s Turn: Bite Attack ---")
        
        # Define the bite weapon data
        bite_weapon = {
            'name': 'bite',
            'damage': '1d10',  # Base damage, Str mod will be added automatically
            'ability': 'str',
            'proficient': True,
            'damage_type': 'piercing',
            'special_effects': ['knockdown']  # Bite knocks targets prone
        }
        
        # Use the global attack system with pack tactics advantage
        # We need to modify the attack system call to include pack tactics
        hit = self._bite_with_pack_tactics(target, bite_weapon, attacker_is_within_5_feet)
        
        return hit
    
    def _bite_with_pack_tactics(self, target, weapon_data, attacker_is_within_5_feet):
        """Custom bite attack that includes pack tactics advantage."""
        print(f"--- {self.name} attacks {target.name} with Pack Tactics ---")
        
        # Make the attack roll with pack tactics advantage
        hit = perform_d20_test(
            creature=self,
            ability_name='str',
            check_type='bite',  # Uses bite proficiency
            target=target,
            is_attack_roll=True,
            has_advantage=self.has_pack_tactics(),  # Pack tactics gives advantage
            attacker_is_within_5_feet=attacker_is_within_5_feet
        )
        
        if hit:
            # Calculate damage manually to match the original implementation
            base_damage = roll_dice(weapon_data['damage'])
            str_mod = self.get_ability_modifier('str')
            
            # Check for critical hit
            from systems.d20_system import was_last_roll_critical
            is_crit = was_last_roll_critical()
            
            if is_crit:
                # Double the dice for critical hits
                crit_damage = roll_dice(weapon_data['damage'])  # Roll damage dice again
                total_damage = base_damage + crit_damage + str_mod
                print(f"  > CRITICAL HIT! {total_damage} {weapon_data['damage_type']} damage!")
            else:
                total_damage = base_damage + str_mod
                print(f"  > {total_damage} {weapon_data['damage_type']} damage!")
            
            target.take_damage(total_damage)
            
            # Apply knockdown effect
            add_condition(target, 'prone')
            print(f"  > {target.name} is knocked prone!")
            
            return True
        else:
            print(f"  > {self.name}'s bite misses!")
            return False

    def attempt_to_hide(self):
        """Performs a Dexterity (Stealth) check."""
        print(f"\n--- {self.name}'s Action: Attempt to Hide ---")
        return perform_d20_test(
            creature=self,
            ability_name='dex',
            check_type='stealth',
            dc=15
        )