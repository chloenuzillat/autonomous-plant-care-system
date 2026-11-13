from dataclasses import dataclass


@dataclass(frozen=True)
class Position:
    x: int
    y: int

class Map:
    """Represents the navigable area used by the robot's path planner."""

    def __init__(
            self,
            width: int,
            height: int,
            cell_size: float,
            origin_x: float = 0.0,
            origin_y: float = 0.0
    ):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.origin_x = origin_x
        self.origin_y = origin_y

        self.robot_position = None
        self.target_positions = []

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

    def get_neighbors(self, position: Position) -> list[Position]:
        candidates = [
            Position(position.x + 1, position.y),
            Position(position.x - 1, position.y),
            Position(position.x, position.y + 1),
            Position(position.x, position.y - 1),
        ]

        return [
            neighbor
            for neighbor in candidates
            if self.is_traversable(neighbor)
        ]

    def cell_to_world(self, position: Position) -> tuple[float, float]:
        return (
            self.origin_x + (position.x + 0.5) * self.cell_size,
            self.origin_y + (position.y + 0.5) * self.cell_size
        )

    def world_to_cell(self, x: float, y: float) -> Position:
        return Position(
            int((x - self.origin_x) // self.cell_size),
            int((y - self.origin_y) // self.cell_size)
        )