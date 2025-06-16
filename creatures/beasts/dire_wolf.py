# File: creatures/beasts/dire_wolf.py
"""Implementation of the Dire Wolf enemy."""
from creatures.base import Creature
from core.utils import roll_dice
from systems.d20_system import perform_d20_test
from systems.condition_system import add_condition

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

    # --- THIS IS THE FIX ---
    # The 'bite' method now accepts the 'attacker_is_within_5_feet' argument.
    def bite(self, target, combat_context=None, attacker_is_within_5_feet=False):
        """Performs the Bite melee attack using the global D20 system."""
        print(f"\n--- {self.name}'s Turn: Bite Attack ---")
        
        is_hit = perform_d20_test(
            creature=self,
            ability_name='str',
            check_type='bite',
            target=target,
            has_advantage=self.has_pack_tactics(combat_context),
            is_attack_roll=True,
            # It now correctly passes this information to the d20 system.
            attacker_is_within_5_feet=attacker_is_within_5_feet
        )

        if is_hit:
            damage = roll_dice("1d10") + self.get_ability_modifier('str')
            target.take_damage(damage)
            add_condition(target, 'prone')

    def attempt_to_hide(self):
        """Performs a Dexterity (Stealth) check."""
        print(f"\n--- {self.name}'s Action: Attempt to Hide ---")
        perform_d20_test(
            creature=self,
            ability_name='dex',
            check_type='stealth',
            dc=15
        )