# File: systems/positioning_system.py
"""Positioning System - Manages creature positions, range, and grid-based movement."""

import math

class Position:
    """Represents a position on the battlefield."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __str__(self):
        return f"({self.x}, {self.y})"
    
    def __eq__(self, other):
        return isinstance(other, Position) and self.x == other.x and self.y == other.y
    
    def __hash__(self):
        """Make Position hashable so it can be used as dict keys."""
        return hash((self.x, self.y))
    
    def __repr__(self):
        return f"Position({self.x}, {self.y})"

class CreatureSize:
    """Creature size categories and their space requirements."""
    TINY = {"name": "Tiny", "squares": 1, "reach": 0}  # Special case
    SMALL = {"name": "Small", "squares": 1, "reach": 5}
    MEDIUM = {"name": "Medium", "squares": 1, "reach": 5}
    LARGE = {"name": "Large", "squares": 4, "reach": 5}  # 2x2
    HUGE = {"name": "Huge", "squares": 9, "reach": 10}   # 3x3
    GARGANTUAN = {"name": "Gargantuan", "squares": 16, "reach": 15}  # 4x4

class TerrainType:
    """Types of terrain that affect movement."""
    NORMAL = {"name": "Normal", "cost_multiplier": 1}
    DIFFICULT = {"name": "Difficult", "cost_multiplier": 2}
    IMPASSABLE = {"name": "Impassable", "cost_multiplier": float('inf')}

class PositioningSystem:
    """Manages creature positions, movement, and spatial relationships."""
    
    def __init__(self, grid_size=5):
        self.grid_size = grid_size  # Feet per square (D&D standard is 5)
        self.creature_positions = {}  # creature -> Position
        self.terrain_map = {}  # Position -> TerrainType
        self.creature_sizes = {}  # creature -> CreatureSize
    
    def place_creature(self, creature, position, size=CreatureSize.MEDIUM):
        """Place a creature at a specific position."""
        if self.is_position_valid(position, size):
            self.creature_positions[creature] = position
            self.creature_sizes[creature] = size
            print(f"  > {creature.name} placed at {position}")
            return True
        else:
            print(f"  > Cannot place {creature.name} at {position} - position occupied or invalid")
            return False
    
    def move_creature(self, creature, new_position):
        """Move a creature to a new position."""
        if creature not in self.creature_positions:
            print(f"  > {creature.name} is not on the battlefield!")
            return False
        
        old_position = self.creature_positions[creature]
        creature_size = self.creature_sizes.get(creature, CreatureSize.MEDIUM)
        
        if self.is_position_valid(new_position, creature_size, exclude_creature=creature):
            # Calculate movement cost
            distance = self.calculate_distance(old_position, new_position)
            movement_cost = self.calculate_movement_cost(old_position, new_position)
            
            print(f"  > {creature.name} moves from {old_position} to {new_position}")
            print(f"  > Distance: {distance} feet, Movement cost: {movement_cost} feet")
            
            # Update position
            self.creature_positions[creature] = new_position
            return movement_cost
        else:
            print(f"  > Cannot move {creature.name} to {new_position} - position blocked")
            return False
    
    def get_position(self, creature):
        """Get a creature's current position."""
        return self.creature_positions.get(creature)
    
    def calculate_distance(self, pos1, pos2):
        """Calculate distance between two positions in feet."""
        # Use grid-based distance (counting squares)
        dx = abs(pos1.x - pos2.x)
        dy = abs(pos1.y - pos2.y)
        
        # D&D 2024 uses simplified diagonal movement
        # Each square costs 5 feet, even diagonally
        squares = max(dx, dy)
        return squares * self.grid_size
    
    def calculate_movement_cost(self, start_pos, end_pos):
        """Calculate the movement cost including terrain effects."""
        # For now, use basic distance
        # In a full system, this would check terrain along the path
        base_distance = self.calculate_distance(start_pos, end_pos)
        
        # Check if end position has difficult terrain
        end_terrain = self.terrain_map.get(end_pos, TerrainType.NORMAL)
        if end_terrain == TerrainType.DIFFICULT:
            return base_distance * 2
        elif end_terrain == TerrainType.IMPASSABLE:
            return float('inf')
        
        return base_distance
    
    def is_position_valid(self, position, creature_size, exclude_creature=None):
        """Check if a position is valid for a creature of given size."""
        # Check if any other creature occupies this space
        for creature, occupied_pos in self.creature_positions.items():
            if creature == exclude_creature:
                continue
            if occupied_pos == position:
                return False
        
        # Check for impassable terrain
        terrain = self.terrain_map.get(position, TerrainType.NORMAL)
        if terrain == TerrainType.IMPASSABLE:
            return False
        
        return True
    
    def get_creatures_in_range(self, creature, range_feet):
        """Get all creatures within a specified range."""
        if creature not in self.creature_positions:
            return []
        
        creature_pos = self.creature_positions[creature]
        creatures_in_range = []
        
        for other_creature, other_pos in self.creature_positions.items():
            if other_creature == creature:
                continue
            
            distance = self.calculate_distance(creature_pos, other_pos)
            if distance <= range_feet:
                creatures_in_range.append((other_creature, distance))
        
        return creatures_in_range
    
    def are_adjacent(self, creature1, creature2):
        """Check if two creatures are adjacent (within 5 feet)."""
        creatures_in_range = self.get_creatures_in_range(creature1, 5)
        return any(creature == creature2 for creature, distance in creatures_in_range)
    
    def get_creatures_within_reach(self, creature):
        """Get all creatures within the attacker's reach."""
        creature_size = self.creature_sizes.get(creature, CreatureSize.MEDIUM)
        reach = creature_size["reach"]
        
        return self.get_creatures_in_range(creature, reach)
    
    def set_terrain(self, position, terrain_type):
        """Set terrain type at a position."""
        self.terrain_map[position] = terrain_type
        print(f"  > Terrain at {position} set to {terrain_type['name']}")
    
    def get_battlefield_status(self):
        """Get a summary of the current battlefield."""
        status = "=== BATTLEFIELD STATUS ===\n"
        
        for creature, position in self.creature_positions.items():
            size_name = self.creature_sizes[creature]["name"]
            hp_status = f"{creature.current_hp}/{creature.max_hp}"
            status += f"{creature.name} ({size_name}): {position} - {hp_status} HP\n"
        
        return status
    
    def check_opportunity_attacks(self, moving_creature, old_position, new_position):
        """Check which creatures can make opportunity attacks."""
        opportunity_attackers = []
        
        # Find creatures that had the mover in reach at start of movement
        for creature, pos in self.creature_positions.items():
            if creature == moving_creature or not creature.is_alive:
                continue
            
            # Check if creature was within reach at start
            old_distance = self.calculate_distance(pos, old_position)
            creature_size = self.creature_sizes.get(creature, CreatureSize.MEDIUM)
            reach = creature_size["reach"]
            
            if old_distance <= reach:
                # Check if creature is no longer within reach
                new_distance = self.calculate_distance(pos, new_position)
                if new_distance > reach:
                    # This creature can make an opportunity attack
                    opportunity_attackers.append(creature)
        
        return opportunity_attackers

class CoverSystem:
    """Manages cover calculations between creatures."""
    
    @staticmethod
    def calculate_cover(attacker_pos, target_pos, positioning_system):
        """
        Calculate cover between attacker and target.
        
        Returns:
            str: 'none', 'half', 'three_quarters', or 'total'
        """
        # This is a simplified cover system
        # A full implementation would trace line of sight through the grid
        
        # Check for creatures providing cover
        cover_level = 'none'
        
        # Look for creatures between attacker and target
        for creature, creature_pos in positioning_system.creature_positions.items():
            if creature_pos == attacker_pos or creature_pos == target_pos:
                continue
            
            # Simple check: if a creature is roughly between attacker and target
            if CoverSystem._is_roughly_between(attacker_pos, target_pos, creature_pos):
                # Creature provides at least half cover
                cover_level = 'half'
                break
        
        return cover_level
    
    @staticmethod
    def _is_roughly_between(pos1, pos2, check_pos):
        """Check if check_pos is roughly between pos1 and pos2."""
        # Simplified: check if the creature is within 1 square of the line
        # A proper implementation would use line intersection algorithms
        
        # For now, just check if it's in the general area
        min_x = min(pos1.x, pos2.x)
        max_x = max(pos1.x, pos2.x)
        min_y = min(pos1.y, pos2.y)
        max_y = max(pos1.y, pos2.y)
        
        return (min_x <= check_pos.x <= max_x and min_y <= check_pos.y <= max_y)
    
    @staticmethod
    def get_cover_bonus(cover_level):
        """Get AC and save bonuses for cover level."""
        cover_bonuses = {
            'none': {'ac': 0, 'dex_save': 0},
            'half': {'ac': 2, 'dex_save': 2},
            'three_quarters': {'ac': 5, 'dex_save': 5},
            'total': {'ac': float('inf'), 'dex_save': float('inf')}  # Can't be targeted
        }
        return cover_bonuses.get(cover_level, cover_bonuses['none'])

# Global positioning system instance
battlefield = PositioningSystem()