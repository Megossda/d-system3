# File: spells/level1/cure_wounds.py
"""Cure Wounds 1st-level spell - healing magic."""

from spells.spells_base import BaseSpell
from core.utils import roll_dice

class CureWounds(BaseSpell):
    """Cure Wounds 1st-level spell that heals a creature."""

    def __init__(self):
        super().__init__(
            name="Cure Wounds",
            level=1,
            school="Abjuration",  # Fixed: Should be Abjuration, not Evocation
            casting_time="1 Action",
            range_type="Touch",
            components="V, S"
        )

    def cast(self, caster, targets, spell_level, action_type="ACTION"):
        """Cast Cure Wounds - heal a target."""
        target = targets if not isinstance(targets, list) else targets[0]
        
        if not target:
            print(f"** {self.name} requires a target! **")
            return False

        if not target.is_alive:
            print(f"** {self.name} cannot heal the dead! **")
            return False

        print(f"** {caster.name} touches {target.name} with healing magic! **")

        # Calculate healing based on spell level
        # D&D 2024: 2d8 at 1st level, +2d8 per level above 1st
        base_dice_count = 2  # 2d8 at base level
        scaling_dice_per_level = 2  # +2d8 per level above 1st
        
        additional_levels = max(0, spell_level - 1)
        total_dice = base_dice_count + (additional_levels * scaling_dice_per_level)
        
        healing_dice = f"{total_dice}d8"

        # Add spellcasting modifier
        spellcasting_modifier = caster.get_spellcasting_modifier()
        base_healing = roll_dice(healing_dice)
        total_healing = base_healing + spellcasting_modifier

        print(f"** Healing: {base_healing} ({healing_dice}) + {spellcasting_modifier} (modifier) = {total_healing} HP **")

        # Apply healing
        old_hp = target.current_hp
        target.current_hp = min(target.max_hp, target.current_hp + total_healing)
        actual_healing = target.current_hp - old_hp

        print(f"** {target.name} recovers {actual_healing} HP! ({old_hp}/{target.max_hp} → {target.current_hp}/{target.max_hp}) **")

        return True

# Create the instance
cure_wounds = CureWounds()