# File: spells/cantrips/acid_splash.py
"""Acid Splash cantrip."""

from spells.spells_base import BaseSpell
# --- FIX ---
# We now import the more powerful 'roll_dice' function
from core.utils import roll_dice
from systems.spell_system.spell_manager import SpellManager


class AcidSplash(BaseSpell):
    """Acid Splash cantrip."""

    def __init__(self):
        super().__init__(
            name="Acid Splash",
            level=0,
            school="Evocation",
            damage_type="Acid",
            save_type="dex"
        )

    def cast(self, caster, targets, spell_level, action_type="ACTION"):
        """Cast Acid Splash."""
        if not targets:
            print(f"** {self.name} requires a target point! **")
            return False

        if not isinstance(targets, list):
            targets = [targets]

        # Determine the number of damage dice based on caster level 
        num_damage_dice = self._get_cantrip_damage_dice(caster.level)
        damage_notation = f"{num_damage_dice}d6" # e.g., "2d6"

        print(f"** Acidic bubble explodes in a 5-foot-radius sphere! **")

        for target in targets:
            if not target or not target.is_alive:
                continue

            print(f"--- {target.name} makes a Dexterity saving throw ---")

            if SpellManager.make_spell_save(target, caster, self, "dex"):
                print(f"** {target.name} succeeds and takes no damage! **")
            else:
                # --- FIX ---
                # Use the new global dice system to roll for damage
                total_damage = roll_dice(damage_notation)
                
                print(f"** {target.name} fails and takes {total_damage} acid damage! ({damage_notation}) **")
                SpellManager.deal_spell_damage(target, total_damage, "Acid", caster)

        return True

    def _get_cantrip_damage_dice(self, caster_level):
        """Cantrip damage scales with level."""
        if caster_level >= 17:
            return 4
        elif caster_level >= 11:
            return 3
        elif caster_level >= 5:
            return 2
        else:
            return 1

# Create the instance
acid_splash = AcidSplash()