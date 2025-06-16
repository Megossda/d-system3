# File: systems/attack_system.py
"""Global attack system for all types of attacks."""

from systems.d20_system import perform_d20_test
from core.utils import roll_dice

class AttackSystem:
    """Centralized system for handling all attack types."""
    
    @staticmethod
    def make_weapon_attack(attacker, target, weapon_data, attacker_is_within_5_feet=True):
        """
        Make a weapon attack using the global d20 system.
        
        Args:
            attacker: The creature making the attack
            target: The target being attacked
            weapon_data: Dict with weapon info like {'damage': '1d8+3', 'ability': 'str', 'proficient': True}
            attacker_is_within_5_feet: For melee/ranged positioning rules
        """
        print(f"\n--- {attacker.name} attacks {target.name} ---")
        
        # Determine if the attacker is proficient with this weapon
        weapon_name = weapon_data.get('name', 'weapon')
        is_proficient = weapon_data.get('proficient', False) or weapon_name.lower() in attacker.proficiencies
        
        # Make the attack roll using the d20 system
        hit = perform_d20_test(
            creature=attacker,
            ability_name=weapon_data.get('ability', 'str'),
            check_type=weapon_name.lower() if is_proficient else None,  # Only add proficiency if proficient
            target=target,
            is_attack_roll=True,
            attacker_is_within_5_feet=attacker_is_within_5_feet
        )
        
        if hit:
            # Calculate damage
            damage_roll = weapon_data.get('damage', '1d6')
            ability_mod = attacker.get_ability_modifier(weapon_data.get('ability', 'str'))
            
            # Check for critical hit (nat 20)
            is_crit = AttackSystem._was_critical_hit()
            
            damage = AttackSystem._calculate_damage(damage_roll, ability_mod, is_crit)
            damage_type = weapon_data.get('damage_type', 'bludgeoning')
            
            AttackSystem._deal_damage(target, damage, damage_type, attacker, is_crit)
            
            # Handle any special weapon effects
            special_effects = weapon_data.get('special_effects', [])
            for effect in special_effects:
                AttackSystem._apply_weapon_effect(effect, attacker, target)
                
            return True
        else:
            print(f"  > {attacker.name}'s attack misses!")
            return False
    
    @staticmethod
    def make_spell_attack(caster, target, spell, spell_level=None):
        """
        Make a spell attack using the global d20 system.
        """
        print(f"\n--- {caster.name} makes a spell attack with {spell.name} ---")
        
        hit = perform_d20_test(
            creature=caster,
            ability_name=caster.spellcasting_ability,
            check_type=None,  # Spell attacks don't use skill proficiency, just spellcasting modifier
            target=target,
            is_attack_roll=True
        )
        
        if hit:
            # This would be handled by the specific spell's damage calculation
            print(f"  > {spell.name} hits {target.name}!")
            return True
        else:
            print(f"  > {spell.name} misses {target.name}!")
            return False
    
    @staticmethod
    def make_unarmed_attack(attacker, target):
        """Make an unarmed strike attack."""
        unarmed_data = {
            'name': 'Unarmed Strike',
            'damage': '1+0',  # 1 + Str mod
            'ability': 'str',
            'proficient': True,  # Everyone is proficient with unarmed strikes
            'damage_type': 'bludgeoning'
        }
        
        return AttackSystem.make_weapon_attack(attacker, target, unarmed_data)
    
    @staticmethod
    def _calculate_damage(damage_dice, ability_modifier, is_critical=False):
        """Calculate damage from dice notation and modifiers."""
        if is_critical:
            # For crits, double the dice but not the ability modifier
            import re
            match = re.match(r'(\d+)d(\d+)([+-]\d+)?', damage_dice.lower().strip())
            if match:
                num_dice = int(match.group(1)) * 2  # Double the dice
                die_type = match.group(2)
                dice_modifier = match.group(3) or ""
                crit_dice = f"{num_dice}d{die_type}{dice_modifier}"
                base_damage = roll_dice(crit_dice)
            else:
                # If it's not standard dice notation, just double it
                base_damage = roll_dice(damage_dice) * 2
        else:
            base_damage = roll_dice(damage_dice)
        
        total_damage = base_damage + ability_modifier
        return max(1, total_damage)  # Minimum 1 damage
    
    @staticmethod
    def _deal_damage(target, damage, damage_type, attacker, is_critical=False):
        """Deal damage to target with proper messaging."""
        if is_critical:
            print(f"  > CRITICAL HIT! {damage} {damage_type} damage!")
        else:
            print(f"  > {damage} {damage_type} damage!")
        
        # Apply any resistances/vulnerabilities here in the future
        final_damage = AttackSystem._apply_resistances(target, damage, damage_type)
        
        target.take_damage(final_damage, attacker=attacker)
    
    @staticmethod
    def _apply_resistances(target, damage, damage_type):
        """Apply damage resistances/vulnerabilities/immunities."""
        # For now, just return the damage unchanged
        # In the future, check target.resistances, target.vulnerabilities, etc.
        return damage
    
    @staticmethod
    def _was_critical_hit():
        """Check if the last d20 roll was a natural 20."""
        from systems.d20_system import was_last_roll_critical
        return was_last_roll_critical()
    
    @staticmethod
    def _apply_weapon_effect(effect, attacker, target):
        """Apply special weapon effects like poison, knockdown, etc."""
        if effect == 'knockdown':
            from systems.condition_system import add_condition
            add_condition(target, 'prone')
            print(f"  > {target.name} is knocked prone!")
        elif effect == 'poison':
            print(f"  > {target.name} must save against poison!")
            # This would trigger a Constitution save
        # Add more effects as needed