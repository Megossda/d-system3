# File: spells/cantrips/fire_bolt.py
"""Fire Bolt cantrip - ranged spell attack."""

from spells.spells_base import BaseSpell
from systems.spell_system.advanced_spell_system import AdvancedSpellSystem, SpellAttackType

class FireBolt(BaseSpell):
    """Fire Bolt cantrip - ranged spell attack that deals fire damage."""

    def __init__(self):
        super().__init__(
            name="Fire Bolt",
            level=0,
            school="Evocation",
            damage_type="Fire",
            casting_time="1 Action",
            range_type="120 feet",
            components="V, S"
        )

    def cast(self, caster, targets, spell_level, action_type="ACTION"):
        """Cast Fire Bolt - ranged spell attack."""
        target = targets if not isinstance(targets, list) else targets[0]
        
        if not target:
            print(f"** {self.name} requires a target! **")
            return False

        print(f"** {caster.name} hurls a fiery bolt at {target.name}! **")

        # Make ranged spell attack
        attack_result = AdvancedSpellSystem.make_spell_attack_roll(
            caster, target, self, SpellAttackType.RANGED
        )

        if attack_result['hit']:
            # Determine damage dice based on caster level
            damage_dice = self._get_cantrip_damage_dice(caster.level)
            
            # Deal fire damage
            AdvancedSpellSystem.deal_spell_damage(
                target, damage_dice, "fire", caster, 
                is_critical=attack_result['critical']
            )
        
        return attack_result['hit']

    def _get_cantrip_damage_dice(self, caster_level):
        """Cantrip damage scales with level."""
        if caster_level >= 17:
            return "4d10"
        elif caster_level >= 11:
            return "3d10"
        elif caster_level >= 5:
            return "2d10"
        else:
            return "1d10"

# Create the instance
fire_bolt = FireBolt()