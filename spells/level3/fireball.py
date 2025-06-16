# File: spells/level3/fireball.py
"""Fireball 3rd-level spell - D&D 2024 official implementation."""

from spells.spells_base import BaseSpell
from systems.spell_system.spell_manager import SpellManager
from core.utils import roll_dice

class Fireball(BaseSpell):
    """
    Fireball 3rd-level spell - D&D 2024 official implementation.
    
    Level: 3rd
    Casting Time: 1 Action
    Range/Area: 150 ft. (20 ft. radius)
    Components: V, S, M (a ball of bat guano and sulfur)
    Duration: Instantaneous
    School: Evocation
    Attack/Save: DEX Save
    Damage/Effect: Fire
    """

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
        """
        Cast Fireball - area effect Dexterity save for fire damage.
        
        Official Description:
        "A bright streak flashes from you to a point you choose within range 
        and then blossoms with a low roar into a fiery explosion. Each creature 
        in a 20-foot-radius Sphere centered on that point makes a Dexterity 
        saving throw, taking 8d6 Fire damage on a failed save or half as much 
        damage on a successful one."
        """
        if not targets:
            print(f"** {self.name} requires at least one target! **")
            return False

        # Ensure targets is a list for area effect
        if not isinstance(targets, list):
            targets = [targets]

        print(f"** A bright streak flashes from {caster.name} and blossoms with a low roar into a fiery explosion! **")
        print(f"** Each creature in a 20-foot-radius sphere makes a Dexterity saving throw! **")

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
                # Success: Half damage (rounded down)
                full_damage = roll_dice(damage_dice)
                half_damage = full_damage // 2  # Half damage, rounded down
                print(f"** {target.name} succeeds and takes {half_damage} fire damage! (half of {full_damage}) **")
                damage = half_damage
            else:
                # Failure: Full damage
                damage = roll_dice(damage_dice)
                print(f"** {target.name} fails and takes {damage} fire damage! ({damage_dice}) **")
            
            # Apply damage with resistance system
            self._apply_fire_damage(target, damage, caster)

        # Handle flammable objects
        self._handle_flammable_objects(targets)

        return True

    def _apply_fire_damage(self, target, damage, caster):
        """Apply fire damage with proper resistance handling."""
        # Use the enhanced damage system if available
        if hasattr(target, 'take_damage_with_resistance'):
            target.take_damage_with_resistance(damage, "fire", caster)
        else:
            # Fallback: apply damage with resistance calculation
            try:
                from systems.damage_resistance_system import DamageResistanceSystem
                final_damage = DamageResistanceSystem.calculate_damage(target, damage, "fire", caster)
                target.take_damage(final_damage, caster)
            except ImportError:
                # No resistance system available
                target.take_damage(damage, caster)

    def _handle_flammable_objects(self, targets):
        """
        Handle the flammable object rule:
        "Flammable objects in the area that aren't being worn or carried start burning."
        """
        for target in targets:
            # Check if target is a flammable object
            if (hasattr(target, 'is_object') and target.is_object and
                hasattr(target, 'is_flammable') and target.is_flammable):
                
                # Check if it's not worn or carried
                is_worn = getattr(target, 'is_worn', False)
                is_carried = getattr(target, 'is_carried', False)
                
                if not is_worn and not is_carried:
                    print(f"** {target.name} starts burning! **")
                    
                    # Add burning condition if system supports it
                    try:
                        from systems.condition_system import add_condition
                        add_condition(target, 'burning')
                    except ImportError:
                        # Just add a simple property
                        target.is_burning = True
                else:
                    print(f"** {target.name} is worn/carried and doesn't ignite **")

    def get_spell_description(self):
        """Get the full spell description matching D&D 2024."""
        return {
            'name': self.name,
            'level': '3rd',
            'casting_time': self.casting_time,
            'range_area': self.range_type,
            'components': self.components,
            'duration': self.duration,
            'school': self.school,
            'attack_save': 'DEX Save',
            'damage_effect': self.damage_type,
            'description': (
                "A bright streak flashes from you to a point you choose within range "
                "and then blossoms with a low roar into a fiery explosion. Each creature "
                "in a 20-foot-radius Sphere centered on that point makes a Dexterity "
                "saving throw, taking 8d6 Fire damage on a failed save or half as much "
                "damage on a successful one."
            ),
            'flammable_objects': (
                "Flammable objects in the area that aren't being worn or carried start burning."
            ),
            'higher_level': (
                "Using a Higher-Level Spell Slot: The damage increases by 1d6 for each "
                "spell slot level above 3."
            ),
            'spell_tags': ['Damage']
        }

# Create the instance
fireball = Fireball()