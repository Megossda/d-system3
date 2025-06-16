# File: spells/level3/fireball.py
"""Fireball 3rd-level spell - area of effect fire damage."""

from spells.spells_base import BaseSpell
from systems.spell_system.spell_manager import SpellManager
from core.utils import roll_dice

class Fireball(BaseSpell):
    """Fireball 3rd-level spell that creates a fiery explosion."""

    def __init__(self):
        super().__init__(
            name="Fireball",
            level=3,
            school="Evocation",
            damage_type="Fire",
            casting_time="1 Action",
            range_type="150 feet (20-foot radius)",
            components="V, S, M (a ball of bat guano and sulfur)",
            duration="Instantaneous",
            save_type="dex"
        )

    def cast(self, caster, targets, spell_level, action_type="ACTION"):
        """Cast Fireball - area effect Dexterity save for fire damage."""
        if not targets:
            print(f"** {self.name} requires at least one target! **")
            return False

        # Ensure targets is a list for area effect
        if not isinstance(targets, list):
            targets = [targets]

        print(f"** {caster.name} hurls a bright streak that explodes in a fiery blast! **")
        print(f"** A 20-foot radius sphere erupts with flame! **")

        # Calculate damage based on spell level
        # D&D 2024: 8d6 at 3rd level, +1d6 per level above 3rd
        base_dice_count = 8  # 8d6 at base level
        scaling_dice_per_level = 1  # +1d6 per level above 3rd
        
        additional_levels = max(0, spell_level - 3)
        total_dice = base_dice_count + (additional_levels * scaling_dice_per_level)
        
        damage_dice = f"{total_dice}d6"
        print(f"** Fireball damage: {damage_dice} fire damage **")

        # Each creature in area makes a Dex save
        for target in targets:
            if not target or not target.is_alive:
                continue

            print(f"--- {target.name} makes a Dexterity saving throw ---")

            if SpellManager.make_spell_save(target, caster, self, "dex"):
                # Success: Half damage
                damage = roll_dice(damage_dice) // 2  # Half damage, rounded down
                print(f"** {target.name} succeeds and takes {damage} fire damage! (half of {damage_dice}) **")
            else:
                # Failure: Full damage
                damage = roll_dice(damage_dice)
                print(f"** {target.name} fails and takes {damage} fire damage! ({damage_dice}) **")
            
            # Apply damage with resistance system
            if hasattr(target, 'take_damage_with_resistance'):
                target.take_damage_with_resistance(damage, "fire", caster)
            else:
                # Fallback - apply damage with resistance calculation
                from systems.damage_resistance_system import DamageResistanceSystem
                final_damage = DamageResistanceSystem.calculate_damage(target, damage, "fire", caster)
                target.take_damage(final_damage, caster)

        # Environmental effect: ignite flammable objects
        print(f"** Flammable objects in the area catch fire! **")

        return True

# Create the instance
fireball = Fireball()