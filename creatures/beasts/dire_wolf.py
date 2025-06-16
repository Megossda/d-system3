# File: creatures/beasts/dire_wolf.py
"""Implementation of the Dire Wolf enemy with official D&D 2024 stats."""
from creatures.base import Creature
from core.utils import roll_dice
from systems.d20_system import perform_d20_test, was_last_roll_critical
from systems.condition_system import add_condition, has_condition
from systems.attack_system import AttackSystem

class DireWolf(Creature):
    """
    A Dire Wolf enemy, based on the official D&D 2024 Player's Handbook.
    Large Beast, Unaligned
    AC 14, HP 22 (3d10 + 6), Speed 50 ft.
    CR 1 (XP 200; PB +2)
    """

    def __init__(self, use_average_hp=False):
        # HP: 22 (3d10 + 6) - Roll unless specifically requested to use average
        if use_average_hp:
            hp = 22  # Use average HP for consistent encounters
        else:
            hp = roll_dice("3d10+6")  # Roll HP as per D&D rules
            print(f"  > {self.__class__.__name__} rolled {hp} HP (3d10+6)")
        
        # Official proficiencies: Perception +5, Stealth +4
        wolf_proficiencies = {
            'perception',   # +5 total (Wis +1, Prof +2, +2 extra = +5)
            'stealth',      # +4 total (Dex +2, Prof +2 = +4)
            'bite'          # Attack proficiency
        }
        
        super().__init__(
            name="Dire Wolf",
            level=0,  # Uses CR instead
            ac=14,
            hp=hp,
            speed=50,
            # Official ability scores: STR 17, DEX 15, CON 15, INT 3, WIS 12, CHA 7
            stats={'str': 17, 'dex': 15, 'con': 15, 'int': 3, 'wis': 12, 'cha': 7},
            cr=1,
            proficiencies=wolf_proficiencies
        )
        
        # Set creature size
        self.size = "Large"
        
        # Special senses
        self.darkvision = 60
        self.passive_perception = 15
        
        # Languages: None (represented as empty set)
        self.languages = set()

    def has_pack_tactics(self, target=None, allies_in_combat=None):
        """
        Pack Tactics: The wolf has Advantage on an attack roll against a creature 
        if at least one of the wolf's allies is within 5 feet of the creature 
        and the ally doesn't have the Incapacitated condition.
        
        Args:
            target: The creature being attacked
            allies_in_combat: List of potential allies (optional, for full implementation)
        """
        # In a full implementation, this would check the battlefield for allies
        # For now, we'll assume pack tactics is active if not explicitly disabled
        
        # Check if any allies are within 5 feet of the target and not incapacitated
        if allies_in_combat and target:
            from systems.positioning_system import battlefield
            if hasattr(battlefield, 'get_creatures_in_range'):
                target_pos = battlefield.get_position(target)
                if target_pos:
                    nearby_creatures = battlefield.get_creatures_in_range(target, 5)
                    for creature, distance in nearby_creatures:
                        # Check if it's an ally of the dire wolf and not incapacitated
                        if (creature != self and creature != target and 
                            not has_condition(creature, 'incapacitated')):
                            print(f"  > {self.name} gains Pack Tactics advantage ({creature.name} is within 5 feet of {target.name})!")
                            return True
        
        # Simplified version: assume pack tactics unless specifically disabled
        # Remove this line when implementing full battlefield positioning
        print(f"  > {self.name} benefits from Pack Tactics!")
        return True

    def make_bite_attack(self, target):
        """
        Bite Attack: Melee Attack Roll: +5, reach 5 ft. 
        Hit: 8 (1d10 + 3) Piercing damage. 
        If the target is a Large or smaller creature, it has the Prone condition.
        """
        print(f"\n--- {self.name}'s Bite Attack ---")
        
        if not target or not target.is_alive:
            print(f"  > Invalid target for bite attack!")
            return False
        
        # Check for Pack Tactics advantage
        has_pack_tactics = self.has_pack_tactics(target)
        
        # Make attack roll: +5 = +3 (Str) + 2 (Prof)
        hit = perform_d20_test(
            creature=self,
            ability_name='str',
            check_type='bite',  # Uses bite proficiency
            target=target,
            is_attack_roll=True,
            has_advantage=has_pack_tactics,
            attacker_is_within_5_feet=True  # Bite is melee with 5 ft reach
        )
        
        if hit:
            # Check for critical hit
            is_crit = was_last_roll_critical()
            
            # Calculate damage: 8 (1d10 + 3) piercing damage
            base_damage = roll_dice("1d10")
            str_modifier = 3  # STR 17 = +3 modifier
            
            if is_crit:
                # Critical hit: double the dice, not the modifier
                crit_damage = roll_dice("1d10")
                total_damage = base_damage + crit_damage + str_modifier
                print(f"  > CRITICAL HIT! {total_damage} piercing damage! (1d10 + 1d10 + 3)")
            else:
                total_damage = base_damage + str_modifier
                print(f"  > {total_damage} piercing damage! (1d10 + 3)")
            
            # Apply damage using the enhanced damage system if available
            if hasattr(target, 'take_damage_with_resistance'):
                target.take_damage_with_resistance(total_damage, 'piercing', self)
            else:
                target.take_damage(total_damage, self)
            
            # Special effect: Prone condition for Large or smaller creatures
            if self._target_is_large_or_smaller(target):
                add_condition(target, 'prone')
                print(f"  > {target.name} is knocked prone by the bite!")
            else:
                print(f"  > {target.name} is too large to be knocked prone")
            
            return True
        else:
            print(f"  > {self.name}'s bite misses {target.name}!")
            return False

    def _target_is_large_or_smaller(self, target):
        """Check if target is Large or smaller (for prone effect)."""
        # Default to True unless target is explicitly Huge or Gargantuan
        target_size = getattr(target, 'size', 'Medium')
        large_or_smaller = ['Tiny', 'Small', 'Medium', 'Large']
        return target_size in large_or_smaller

    def attempt_stealth_check(self, dc=15):
        """
        Make a Stealth check. Stealth +4 = Dex +2, Prof +2
        """
        print(f"\n--- {self.name} attempts to hide (Stealth) ---")
        return perform_d20_test(
            creature=self,
            ability_name='dex',
            check_type='stealth',
            dc=dc
        )

    def make_perception_check(self, dc=15):
        """
        Make a Perception check. Perception +5 = Wis +1, Prof +2, +2 special
        """
        print(f"\n--- {self.name} makes a Perception check ---")
        # Note: The +5 includes a +2 special bonus beyond normal calculation
        return perform_d20_test(
            creature=self,
            ability_name='wis',
            check_type='perception',
            dc=dc
        )

    def get_stats_summary(self):
        """Get a summary of the dire wolf's official stats."""
        return {
            'name': self.name,
            'size': 'Large',
            'type': 'Beast',
            'alignment': 'Unaligned',
            'ac': self.ac,
            'hp': f"{self.current_hp}/{self.max_hp}",
            'speed': f"{self.speed} ft.",
            'abilities': self.stats,
            'skills': 'Perception +5, Stealth +4',
            'senses': f"Darkvision {self.darkvision} ft., Passive Perception {self.passive_perception}",
            'languages': 'None',
            'cr': f"{self.cr} (XP 200; PB +2)",
            'traits': ['Pack Tactics'],
            'actions': ['Bite (+5, 1d10+3 piercing, prone on hit)']
        }

    def __str__(self):
        """Enhanced string representation with official stats."""
        return (f"{self.name} (Large Beast) - "
                f"AC {self.ac}, HP {self.current_hp}/{self.max_hp}, "
                f"Speed {self.speed} ft., CR {self.cr}")


# Action classes for proper ActionExecutor integration
class DireWolfBiteAction:
    """Official Dire Wolf bite action for ActionExecutor integration."""
    
    def __init__(self):
        self.name = "Bite"
    
    def execute(self, performer, target=None):
        """
        Execute the official dire wolf bite attack.
        NOTE: Action economy is handled by ActionExecutionSystem, not here.
        """
        if not target:
            print(f"  > {performer.name} needs a target to bite!")
            return False
        
        if not isinstance(performer, DireWolf):
            print(f"  > ERROR: {performer.name} is not a Dire Wolf!")
            return False
        
        return performer.make_bite_attack(target)


class DireWolfStealthAction:
    """Dire Wolf stealth action for ActionExecutor integration."""
    
    def __init__(self, dc=15):
        self.name = "Hide (Stealth)"
        self.dc = dc
    
    def execute(self, performer, **kwargs):
        """
        Execute a stealth check.
        NOTE: Action economy is handled by ActionExecutionSystem, not here.
        """
        if not isinstance(performer, DireWolf):
            print(f"  > ERROR: {performer.name} is not a Dire Wolf!")
            return False
        
        dc = kwargs.get('dc', self.dc)
        return performer.attempt_stealth_check(dc)


# Example usage with proper ActionExecutor integration
def dire_wolf_tactical_example():
    """
    Example showing proper dire wolf usage with all official mechanics.
    """
    from systems.action_execution_system import ActionExecutor
    from systems.condition_system import add_condition, has_condition
    
    # Create dire wolf and targets
    dire_wolf = DireWolf()
    
    adventurer = Creature(
        name="Human Fighter",
        level=3,
        ac=16,
        hp=25,
        speed=30,
        stats={'str': 16, 'dex': 12, 'con': 14, 'int': 10, 'wis': 13, 'cha': 12}
    )
    adventurer.size = "Medium"  # Medium creature, can be knocked prone
    
    giant = Creature(
        name="Hill Giant",
        level=5,
        ac=13,
        hp=60,
        speed=40,
        stats={'str': 21, 'dex': 8, 'con': 19, 'int': 5, 'wis': 9, 'cha': 6}
    )
    giant.size = "Huge"  # Huge creature, cannot be knocked prone by bite
    
    print("=== DIRE WOLF TACTICAL COMBAT EXAMPLE ===")
    print(f"Dire Wolf stats: {dire_wolf.get_stats_summary()}")
    
    # Turn 1: Attack the fighter (should knock prone)
    print(f"\n--- Turn 1: {dire_wolf.name} vs {adventurer.name} ---")
    dire_wolf.start_turn()
    
    bite_action = DireWolfBiteAction()
    result = ActionExecutor.action(dire_wolf, bite_action, target=adventurer)
    print(f"Bite result: {result.success}")
    
    # Check if fighter is now prone
    if has_condition(adventurer, 'prone'):
        print(f"  > {adventurer.name} is now prone!")
    
    # Turn 2: Try to hide
    print(f"\n--- Turn 2: {dire_wolf.name} attempts stealth ---")
    dire_wolf.start_turn()
    
    stealth_action = DireWolfStealthAction(dc=12)
    stealth_result = ActionExecutor.action(dire_wolf, stealth_action)
    print(f"Stealth result: {stealth_result.success}")
    
    # Turn 3: Attack the giant (should not knock prone)
    print(f"\n--- Turn 3: {dire_wolf.name} vs {giant.name} (Huge) ---")
    dire_wolf.start_turn()
    
    bite_result = ActionExecutor.action(dire_wolf, bite_action, target=giant)
    print(f"Bite vs giant result: {bite_result.success}")
    
    # Check prone status
    if has_condition(giant, 'prone'):
        print(f"  > {giant.name} is knocked prone (unexpected!)")
    else:
        print(f"  > {giant.name} is too large to be knocked prone (correct)")
    
    print(f"\n--- Final Status ---")
    print(f"Dire Wolf: {dire_wolf}")
    print(f"Fighter: {adventurer.name} - {adventurer.current_hp}/{adventurer.max_hp} HP" + 
          (" (Prone)" if has_condition(adventurer, 'prone') else ""))
    print(f"Giant: {giant.name} - {giant.current_hp}/{giant.max_hp} HP")


if __name__ == "__main__":
    dire_wolf_tactical_example()