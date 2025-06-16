# File: spells/level1/magic_missile.py
"""Magic Missile 1st-level spell - auto-hit force damage."""

from spells.spells_base import BaseSpell
from systems.spell_system.advanced_spell_system import AdvancedSpellSystem
from core.utils import roll_dice

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
        """Cast Magic Missile - auto-hit force damage."""
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

        # Apply damage to each target
        for target, missile_count in missiles_per_target.items():
            if not target.is_alive:
                print(f"** Missiles aimed at {target.name} fizzle (target defeated) **")
                continue

            print(f"** {missile_count} missile(s) strike {target.name}! **")
            
            # Each missile does 1d4+1 force damage
            total_damage = 0
            for missile in range(missile_count):
                missile_damage = roll_dice("1d4") + 1
                total_damage += missile_damage
                print(f"   Missile {missile + 1}: {missile_damage} force damage")
            
            print(f"** Total: {total_damage} force damage to {target.name} **")
            
            # Apply damage with resistance system (Magic Missile does fixed damage, not dice)
            if hasattr(target, 'take_damage_with_resistance'):
                target.take_damage_with_resistance(total_damage, "force", caster)
            else:
                # Fallback - apply damage directly with resistance calculation
                from systems.damage_resistance_system import DamageResistanceSystem
                final_damage = DamageResistanceSystem.calculate_damage(target, total_damage, "force", caster)
                target.take_damage(final_damage, caster)

        return True

# Create the instance
magic_missile = MagicMissile()