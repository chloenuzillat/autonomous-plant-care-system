from pi.navigation.map import Map, Position

class PathPlanner:
    """
    Calculates path through a Map without knowing how the robot moves.
    """

    def __init__(self, map: Map):
        self.map = Map

    def find_path(self, start: Position, target: Position) -> list[Position]:
        if not self.map.is_traversable(start):
            return []

        if not self.map.is_traversable(target):
            return []

        open_set = {start}
        came_from = {}

        g_score = {start: 0}
        f_score = {start: self._heuristic(start, target)}

        while open_set:
            current = min()