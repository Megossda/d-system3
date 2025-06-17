# File: systems/damage_resistance_system.py
"""Damage Resistance System - Manages resistances, vulnerabilities, and immunities."""

class DamageType:
    """Standard D&D damage types."""
    # Physical damage types
    BLUDGEONING = "bludgeoning"
    PIERCING = "piercing"
    SLASHING = "slashing"
    
    # Energy damage types
    ACID = "acid"
    COLD = "cold"
    FIRE = "fire"
    LIGHTNING = "lightning"
    THUNDER = "thunder"
    
    # Magical damage types
    FORCE = "force"
    NECROTIC = "necrotic"
    RADIANT = "radiant"
    PSYCHIC = "psychic"
    
    # Special damage types
    POISON = "poison"
    
    @classmethod
    def get_all_types(cls):
        """Get all damage types."""
        return [
            cls.BLUDGEONING, cls.PIERCING, cls.SLASHING,
            cls.ACID, cls.COLD, cls.FIRE, cls.LIGHTNING, cls.THUNDER,
            cls.FORCE, cls.NECROTIC, cls.RADIANT, cls.PSYCHIC, cls.POISON
        ]

class DamageResistanceSystem:
    """Manages damage resistances, vulnerabilities, and immunities."""
    
    @staticmethod
    def add_resistance(creature, damage_type):
        """Add damage resistance to a creature."""
        if not hasattr(creature, 'damage_resistances'):
            creature.damage_resistances = set()
        creature.damage_resistances.add(damage_type.lower())
        print(f"  > {creature.name} gains resistance to {damage_type} damage")
    
    @staticmethod
    def add_vulnerability(creature, damage_type):
        """Add damage vulnerability to a creature."""
        if not hasattr(creature, 'damage_vulnerabilities'):
            creature.damage_vulnerabilities = set()
        creature.damage_vulnerabilities.add(damage_type.lower())
        print(f"  > {creature.name} gains vulnerability to {damage_type} damage")
    
    @staticmethod
    def add_immunity(creature, damage_type):
        """Add damage immunity to a creature."""
        if not hasattr(creature, 'damage_immunities'):
            creature.damage_immunities = set()
        creature.damage_immunities.add(damage_type.lower())
        print(f"  > {creature.name} gains immunity to {damage_type} damage")
    
    @staticmethod
    def remove_resistance(creature, damage_type):
        """Remove damage resistance from a creature."""
        if hasattr(creature, 'damage_resistances'):
            creature.damage_resistances.discard(damage_type.lower())
            print(f"  > {creature.name} loses resistance to {damage_type} damage")
    
    @staticmethod
    def calculate_damage(creature, base_damage, damage_type, source=None):
        """
        Calculate final damage after applying resistances, vulnerabilities, and immunities.
        
        Args:
            creature: The target creature
            base_damage: The base damage amount
            damage_type: The type of damage
            source: The source of the damage (for logging)
            
        Returns:
            int: Final damage after all modifiers
        """
        if base_damage <= 0:
            return 0
        
        damage_type = damage_type.lower()
        final_damage = base_damage
        source_text = f" from {source.name}" if source else ""
        
        print(f"  > Calculating {base_damage} {damage_type} damage to {creature.name}{source_text}")
        
        # Check immunity first (completely negates damage)
        if hasattr(creature, 'damage_immunities') and damage_type in creature.damage_immunities:
            print(f"    > {creature.name} is immune to {damage_type} damage! (0 damage)")
            return 0
        
        # Check resistance (halves damage, rounded down)
        if hasattr(creature, 'damage_resistances') and damage_type in creature.damage_resistances:
            final_damage = final_damage // 2
            print(f"    > {creature.name} resists {damage_type} damage! ({base_damage} → {final_damage})")
        
        # Check vulnerability (doubles damage)
        if hasattr(creature, 'damage_vulnerabilities') and damage_type in creature.damage_vulnerabilities:
            final_damage = final_damage * 2
            print(f"    > {creature.name} is vulnerable to {damage_type} damage! ({base_damage} → {final_damage})")
        
        # Handle special cases where creature has both resistance and vulnerability
        # (This shouldn't normally happen, but just in case)
        if (hasattr(creature, 'damage_resistances') and damage_type in creature.damage_resistances and
            hasattr(creature, 'damage_vulnerabilities') and damage_type in creature.damage_vulnerabilities):
            final_damage = base_damage  # They cancel out
            print(f"    > Resistance and vulnerability cancel out! ({final_damage} damage)")
        
        return max(0, final_damage)
    
    @staticmethod
    def get_resistances_summary(creature):
        """Get a summary of creature's damage resistances, vulnerabilities, and immunities."""
        summary = {}
        
        if hasattr(creature, 'damage_resistances') and creature.damage_resistances:
            summary['resistances'] = sorted(list(creature.damage_resistances))
        
        if hasattr(creature, 'damage_vulnerabilities') and creature.damage_vulnerabilities:
            summary['vulnerabilities'] = sorted(list(creature.damage_vulnerabilities))
        
        if hasattr(creature, 'damage_immunities') and creature.damage_immunities:
            summary['immunities'] = sorted(list(creature.damage_immunities))
        
        return summary
    
    @staticmethod
    def apply_environmental_effects(creature, environment_type):
        """Apply environmental damage resistances (like underwater fire resistance)."""
        if environment_type == "underwater":
            DamageResistanceSystem.add_resistance(creature, DamageType.FIRE)
            print(f"  > {creature.name} gains fire resistance while underwater")
        elif environment_type == "fire_plane":
            DamageResistanceSystem.add_resistance(creature, DamageType.FIRE)
            DamageResistanceSystem.add_vulnerability(creature, DamageType.COLD)
            print(f"  > {creature.name} gains fire resistance but cold vulnerability on the Fire Plane")
    
    @staticmethod
    def remove_environmental_effects(creature, environment_type):
        """Remove environmental damage resistances."""
        if environment_type == "underwater":
            DamageResistanceSystem.remove_resistance(creature, DamageType.FIRE)
        elif environment_type == "fire_plane":
            DamageResistanceSystem.remove_resistance(creature, DamageType.FIRE)
            if hasattr(creature, 'damage_vulnerabilities'):
                creature.damage_vulnerabilities.discard(DamageType.COLD)

# Update the base Creature class to use damage resistance system
def enhanced_take_damage(creature, amount, damage_type="bludgeoning", attacker=None):
    """Enhanced take_damage method that applies resistances and handles concentration."""
    from systems.damage_resistance_system import DamageResistanceSystem
    from systems.concentration_system import ConcentrationSystem
    
    # Calculate final damage with resistances
    final_damage = DamageResistanceSystem.calculate_damage(creature, amount, damage_type, attacker)
    
    # Apply the damage
    creature.current_hp -= final_damage
    
    if final_damage != amount:
        print(f"  > {creature.name} takes {final_damage} {damage_type} damage (modified from {amount}), remaining HP: {creature.current_hp}/{creature.max_hp}")
    else:
        print(f"  > {creature.name} takes {final_damage} {damage_type} damage, remaining HP: {creature.current_hp}/{creature.max_hp}")
    
    # Handle concentration saves if creature took damage
    if final_damage > 0:
        ConcentrationSystem.handle_damage(creature, final_damage, attacker)
    
    if creature.current_hp <= 0:
        creature.current_hp = 0
        creature.is_alive = False
        print(f"  > {creature.name} has been defeated!")
        
        # Break concentration when creature dies
        ConcentrationSystem.break_concentration(creature, "Creature died")
        
        # Clean up action economy when creature dies
        from systems.action_economy import ActionEconomyManager
        ActionEconomyManager.cleanup_dead_creatures()

# Monkey patch the enhanced method to the Creature class
def patch_creature_damage_system():
    """Patch the Creature class to use the enhanced damage system."""
    from creatures.base import Creature
    Creature.take_damage_with_resistance = enhanced_take_damage