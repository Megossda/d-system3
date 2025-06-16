# File: spells/level1/magic_missile.py
"""Magic Missile 1st-level spell - standardized damage system."""

from spells.spells_base import BaseSpell
from core.utils import roll_dice
from error_handling import DnDErrorHandler

class MagicMissile(BaseSpell):
    """Magic Missile 1st-level spell that automatically hits targets."""

    def __init__(self):
        super().__init__(
            name="Magic Missile",
            level=1,
            school="Evocation",
            damage_type="Force",
            casting_time="1 Action",
            range_type="120 feet",
            components="V, S"
        )

    def cast(self, caster, targets, spell_level, action_type="ACTION"):
        """Cast Magic Missile - auto-hit force damage with standardized damage system."""
        if not targets:
            print(f"** {self.name} requires at least one target! **")
            return False

        # Ensure targets is a list
        if not isinstance(targets, list):
            targets = [targets]

        # Calculate number of missiles based on spell level
        num_missiles = 3 + (spell_level - 1)  # 3 missiles at 1st level, +1 per level
        
        print(f"** {caster.name} fires {num_missiles} glowing magical darts! **")

        # Distribute missiles among targets
        missiles_per_target = {}
        for i in range(num_missiles):
            target = targets[i % len(targets)]  # Cycle through targets
            if target not in missiles_per_target:
                missiles_per_target[target] = 0
            missiles_per_target[target] += 1

        # Apply damage to each target using STANDARDIZED damage system
        for target, missile_count in missiles_per_target.items():
            if not target.is_alive:
                print(f"** Missiles aimed at {target.name} fizzle (target defeated) **")
                continue

            print(f"** {missile_count} missile(s) strike {target.name}! **")
            
            # Calculate total damage for all missiles hitting this target
            total_damage = 0
            damage_breakdown = []
            
            for missile in range(missile_count):
                missile_damage = roll_dice("1d4") + 1  # Each missile: 1d4+1
                total_damage += missile_damage
                damage_breakdown.append(str(missile_damage))
            
            print(f"   Missiles: {' + '.join(damage_breakdown)} = {total_damage} force damage")
            
            # FIXED: Use standardized damage system
            self._apply_force_damage(target, total_damage, caster)

        return True

    def _apply_force_damage(self, target, damage, caster):
        """Apply force damage using the standardized damage system."""
        # Use centralized damage handling from error_handling system
        DnDErrorHandler.handle_damage_application(target, damage, "force", caster)

    def get_spell_description(self):
        """Get the full spell description."""
        return {
            'name': self.name,
            'level': '1st',
            'casting_time': self.casting_time,
            'range': self.range_type,
            'components': self.components,
            'school': self.school,
            'damage_type': self.damage_type,
            'description': (
                "You create three glowing darts of magical force. Each dart hits a creature "
                "of your choice that you can see within range. A dart deals 1d4 + 1 force "
                "damage to its target. The darts all strike simultaneously, and you can "
                "direct them to hit one creature or several."
            ),
            'higher_level': (
                "When you cast this spell using a spell slot of 2nd level or higher, "
                "the spell creates one more dart for each slot level above 1st."
            )
        }

# Create the instance
magic_missile = MagicMissile()