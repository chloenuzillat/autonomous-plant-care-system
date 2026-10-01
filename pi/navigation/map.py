from dataclasses import dataclass

from pi.navigation import cell_size


@dataclass
class Position:
    x: int
    y: int

class Map:
    """
    Represents the navigable area used by the robot's path planner.
    """

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.cell_size = cell_size

        self.robot_position = None
        self.target_positions = []

        # True = traversable, False = blocked
        self.grid = [
            [True for _ in range(width)]
            for _ in range(height)
        ]

    def is_within_bounds(self, position: Position) -> bool:
        return (
            0 <= position.x < self.width
            and 0 <= position.y < self.height
        )

    def is_traversable(self, position: Position) -> bool:
        if not self.is_within_bounds(position):
            return False

        return self.grid[position.y][position.x]

    def set_blocked(self, position: Position):
        if self.is_within_bounds(position):
            self.grid[position.y][position.x] = False

    def set_traversable(self, position: Position):
        if self.is_within_bounds(position):
            self.grid[position.y][position.x] = True

    def set_robot_position(self, position: Position):
        if self.is_within_bounds(position):
            self.robot_position = position

    def add_target(self, position: Position):
        if self.is_within_bounds(position):
            self.target_positions.append(position)