# File: systems/cover_system.py
"""Cover System - Implements D&D 2024 cover rules for AC and save bonuses."""

from systems.positioning_system import battlefield

class CoverType:
    """D&D 2024 cover types and their effects."""
    NONE = {
        'name': 'No Cover',
        'ac_bonus': 0,
        'dex_save_bonus': 0,
        'can_target': True
    }
    
    HALF = {
        'name': 'Half Cover',
        'ac_bonus': 2,
        'dex_save_bonus': 2,
        'can_target': True
    }
    
    THREE_QUARTERS = {
        'name': 'Three-Quarters Cover',
        'ac_bonus': 5,
        'dex_save_bonus': 5,
        'can_target': True
    }
    
    TOTAL = {
        'name': 'Total Cover',
        'ac_bonus': 0,  # Can't be targeted directly
        'dex_save_bonus': 0,
        'can_target': False
    }

class CoverSystem:
    """Manages cover calculations and effects."""
    
    @staticmethod
    def determine_cover(attacker, target):
        """
        Determine the level of cover a target has against an attacker.
        
        Args:
            attacker: The attacking creature
            target: The target creature
            
        Returns:
            dict: Cover type information
        """
        attacker_pos = battlefield.get_position(attacker)
        target_pos = battlefield.get_position(target)
        
        if not attacker_pos or not target_pos:
            # If positioning isn't tracked, assume no cover
            return CoverType.NONE
        
        print(f"  > Checking cover: {attacker.name} at {attacker_pos} targeting {target.name} at {target_pos}")
        
        # Check for creatures providing cover
        cover_level = CoverSystem._check_creature_cover(attacker_pos, target_pos)
        
        # Check for environmental cover (terrain, objects)
        env_cover = CoverSystem._check_environmental_cover(attacker_pos, target_pos)
        
        # Use the highest level of cover
        final_cover = CoverSystem._get_highest_cover(cover_level, env_cover)
        
        print(f"  > {target.name} has {final_cover['name']} against {attacker.name}")
        return final_cover
    
    @staticmethod
    def _check_creature_cover(attacker_pos, target_pos):
        """Check if other creatures provide cover."""
        from systems.positioning_system import CreatureSize
        
        # Look for creatures between attacker and target
        for creature, creature_pos in battlefield.creature_positions.items():
            # Skip the attacker and target themselves
            if creature_pos == attacker_pos or creature_pos == target_pos:
                continue
            
            # Check if this creature is between attacker and target
            if CoverSystem._is_between_positions(attacker_pos, target_pos, creature_pos):
                creature_size = battlefield.creature_sizes.get(creature, CreatureSize.MEDIUM)
                
                # Determine cover level based on creature size
                if creature_size in [CreatureSize.LARGE, CreatureSize.HUGE, CreatureSize.GARGANTUAN]:
                    return CoverType.THREE_QUARTERS  # Large+ creatures provide substantial cover
                else:
                    return CoverType.HALF  # Medium/Small creatures provide half cover
        
        return CoverType.NONE
    
    @staticmethod
    def _check_environmental_cover(attacker_pos, target_pos):
        """Check for environmental cover (terrain, objects)."""
        # This is a simplified version
        # In a full system, you'd have actual terrain objects on the map
        
        # For now, we'll check if there's "difficult terrain" that might provide cover
        # This is placeholder logic - replace with actual environmental objects
        
        return CoverType.NONE
    
    @staticmethod
    def _is_between_positions(pos1, pos2, check_pos):
        """
        Check if check_pos is between pos1 and pos2.
        Uses a simplified line-of-sight calculation.
        """
        # If positions are the same, nothing is "between" them
        if pos1 == pos2:
            return False
        
        # Check if check_pos is roughly on the line between pos1 and pos2
        # This is a simplified version - a full implementation would use proper line intersection
        
        # Calculate bounding box
        min_x = min(pos1.x, pos2.x)
        max_x = max(pos1.x, pos2.x)
        min_y = min(pos1.y, pos2.y)
        max_y = max(pos1.y, pos2.y)
        
        # Check if the position is within the bounding rectangle
        if not (min_x <= check_pos.x <= max_x and min_y <= check_pos.y <= max_y):
            return False
        
        # For diagonal or straight lines, check if it's actually blocking
        # Simplified: if it's adjacent to the line path, it provides cover
        return True
    
    @staticmethod
    def _get_highest_cover(cover1, cover2):
        """Get the highest level of cover between two cover types."""
        cover_priority = [CoverType.NONE, CoverType.HALF, CoverType.THREE_QUARTERS, CoverType.TOTAL]
        
        cover1_index = next((i for i, c in enumerate(cover_priority) if c == cover1), 0)
        cover2_index = next((i for i, c in enumerate(cover_priority) if c == cover2), 0)
        
        return cover_priority[max(cover1_index, cover2_index)]
    
    @staticmethod
    def apply_cover_to_attack(attacker, target, base_ac):
        """
        Apply cover bonuses to a target's AC for an attack.
        
        Args:
            attacker: The attacking creature
            target: The target creature
            base_ac: The target's base AC
            
        Returns:
            tuple: (modified_ac, cover_info)
        """
        cover = CoverSystem.determine_cover(attacker, target)
        
        if not cover['can_target']:
            print(f"  > {target.name} has Total Cover and cannot be targeted!")
            return None, cover
        
        modified_ac = base_ac + cover['ac_bonus']
        
        if cover['ac_bonus'] > 0:
            print(f"  > Cover grants +{cover['ac_bonus']} AC bonus (AC {base_ac} → {modified_ac})")
        
        return modified_ac, cover
    
    @staticmethod
    def apply_cover_to_save(target, base_save_bonus, save_type='dex'):
        """
        Apply cover bonuses to a saving throw.
        
        Args:
            target: The creature making the save
            base_save_bonus: The creature's base save bonus
            save_type: Type of save ('dex' for Dexterity saves)
            
        Returns:
            int: Modified save bonus
        """
        # For cover saves, we need to know who's causing the effect
        # This is simplified - in practice you'd pass the effect source
        
        # For now, assume the creature has some level of cover
        # This would be properly calculated in a real combat scenario
        cover_bonus = 0  # Placeholder
        
        return base_save_bonus + cover_bonus

class RangeSystem:
    """Manages weapon and spell ranges."""
    
    @staticmethod
    def check_range(attacker, target, weapon_range):
        """
        Check if a target is within range of an attack.
        
        Args:
            attacker: The attacking creature
            target: The target creature
            weapon_range: Range in feet (or tuple for normal/long range)
            
        Returns:
            dict: Range information
        """
        attacker_pos = battlefield.get_position(attacker)
        target_pos = battlefield.get_position(target)
        
        if not attacker_pos or not target_pos:
            # If no positioning, assume in range
            return {'in_range': True, 'disadvantage': False, 'distance': 0}
        
        distance = battlefield.calculate_distance(attacker_pos, target_pos)
        
        # Handle single range vs normal/long range
        if isinstance(weapon_range, tuple):
            normal_range, long_range = weapon_range
            
            if distance <= normal_range:
                return {'in_range': True, 'disadvantage': False, 'distance': distance}
            elif distance <= long_range:
                return {'in_range': True, 'disadvantage': True, 'distance': distance}
            else:
                return {'in_range': False, 'disadvantage': False, 'distance': distance}
        else:
            # Single range
            in_range = distance <= weapon_range
            return {'in_range': in_range, 'disadvantage': False, 'distance': distance}
    
    @staticmethod
    def check_close_combat_disadvantage(attacker):
        """
        Check if attacker has disadvantage on ranged attacks due to close enemies.
        D&D 2024: Disadvantage when enemy within 5 feet can see you.
        """
        enemies_in_reach = battlefield.get_creatures_in_range(attacker, 5)
        
        for enemy, distance in enemies_in_reach:
            if enemy.is_alive and not any('incapacitated' in getattr(enemy, 'conditions', [])):
                print(f"  > {attacker.name} has disadvantage on ranged attacks ({enemy.name} within 5 feet)")
                return True
        
        return False