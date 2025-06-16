# File: spells/cantrips/fire_bolt.py
"""Fire Bolt cantrip - D&D 2024 official implementation."""

from spells.spells_base import BaseSpell
from systems.attack_system import AttackSystem
from core.utils import roll_dice

class FireBolt(BaseSpell):
    """
    Fire Bolt cantrip - D&D 2024 official implementation.
    
    Level: Cantrip
    Casting Time: 1 Action
    Range/Area: 120 ft.
    Components: V, S
    Duration: Instantaneous
    School: Evocation
    Attack/Save: Ranged Spell Attack
    Damage/Effect: Fire
    """

    def __init__(self):
        super().__init__(
            name="Fire Bolt",
            level=0,
            school="Evocation",
            damage_type="Fire",
            casting_time="1 Action",
            range_type="120 feet",
            components="V, S",
            duration="Instantaneous"
        )

    def cast(self, caster, targets, spell_level, action_type="ACTION"):
        """
        Cast Fire Bolt - ranged spell attack that deals fire damage.
        
        Official Description:
        "You hurl a mote of fire at a creature or an object within range. 
        Make a ranged spell attack against the target. On a hit, the target 
        takes 1d10 Fire damage. A flammable object hit by this spell starts 
        burning if it isn't being worn or carried."
        """
        # Fire Bolt targets a single creature or object
        target = targets if not isinstance(targets, list) else targets[0]
        
        if not target:
            print(f"** {self.name} requires a target! **")
            return False

        print(f"** {caster.name} hurls a mote of fire at {target.name}! **")

        # Make ranged spell attack using the global attack system
        attack_result = AttackSystem.make_spell_attack(caster, target, self)

        if attack_result['hit']:
            # Determine damage dice based on caster level (Cantrip Upgrade)
            damage_dice = self._get_cantrip_damage_dice(caster.level)
            
            # Calculate damage
            base_damage = roll_dice(damage_dice)
            
            # Handle critical hits (double dice damage)
            if attack_result['critical']:
                crit_damage = roll_dice(damage_dice)  # Roll damage dice again
                total_damage = base_damage + crit_damage
                print(f"** CRITICAL HIT! {total_damage} fire damage! ({damage_dice} + {damage_dice}) **")
            else:
                total_damage = base_damage
                print(f"** {total_damage} fire damage! ({damage_dice}) **")
            
            # Apply damage with resistance system
            self._apply_fire_damage(target, total_damage, caster)
            
            # Handle flammable objects
            self._handle_flammable_objects(target)
            
            return True
        else:
            # Attack missed
            return False

    def _get_cantrip_damage_dice(self, caster_level):
        """
        Official Cantrip Upgrade scaling:
        - Level 1-4: 1d10
        - Level 5-10: 2d10  
        - Level 11-16: 3d10
        - Level 17-20: 4d10
        """
        if caster_level >= 17:
            return "4d10"
        elif caster_level >= 11:
            return "3d10"
        elif caster_level >= 5:
            return "2d10"
        else:
            return "1d10"

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

    def _handle_flammable_objects(self, target):
        """
        Handle the flammable object rule:
        "A flammable object hit by this spell starts burning if it isn't being worn or carried."
        """
        # Check if target is an object (not a creature)
        if hasattr(target, 'is_object') and target.is_object:
            # Check if it's flammable and not worn/carried
            if (hasattr(target, 'is_flammable') and target.is_flammable and
                not getattr(target, 'is_worn', False) and 
                not getattr(target, 'is_carried', False)):
                
                print(f"** {target.name} catches fire! **")
                
                # Add burning condition if system supports it
                try:
                    from systems.condition_system import add_condition
                    add_condition(target, 'burning')
                except ImportError:
                    # Just add a simple property
                    target.is_burning = True
        else:
            # Target is a creature - no special flammable object effects
            pass

    def get_spell_description(self):
        """Get the full spell description."""
        return {
            'name': self.name,
            'level': 'Cantrip',
            'casting_time': self.casting_time,
            'range': self.range_type,
            'components': self.components,
            'duration': self.duration,
            'school': self.school,
            'attack_save': 'Ranged Spell Attack',
            'damage_effect': self.damage_type,
            'description': (
                "You hurl a mote of fire at a creature or an object within range. "
                "Make a ranged spell attack against the target. On a hit, the target "
                "takes 1d10 Fire damage. A flammable object hit by this spell starts "
                "burning if it isn't being worn or carried."
            ),
            'cantrip_upgrade': (
                "The damage increases by 1d10 when you reach levels 5 (2d10), "
                "11 (3d10), and 17 (4d10)."
            ),
            'spell_tags': ['Damage']
        }

# Create the instance
fire_bolt = FireBolt()