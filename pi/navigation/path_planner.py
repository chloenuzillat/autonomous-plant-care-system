from pi.navigation.map import Map, Position

class PathPlanner:
    """
    Calculates a path through a Map without knowing how the robot moves.
    """

    def __init__(self, map: Map):
        self.map = map

    def find_path(self, start: Position, target: Position) -> list[Position]:
        if not self.map.is_traversable(start):
            return []

        if not self.map.is_traversable(target):
            return []

        open_set = {start}
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, target)}

        while open_set:
            current = min(open_set, key=lambda position: f_score.get(position,float("inf")))

            if current == target:
                return self.reconstruct_path(came_from, current)

            open_set.remove(current)

            for neighbor in self.map.get_neighbors(current):
                tentative_g_score = (g_score[current] + self.distance(current, neighbor))

                if tentative_g_score < g_score.get(neighbor, float("inf")):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = (tentative_g_score + self.heuristic(neighbor, target))
                    open_set.add(neighbor)

        # No valid path exists.
        return []

    def reconstruct_path(self, came_from: dict[Position, Position], current: Position) -> list[Position]:
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)

        path.reverse()
        return path

    def heuristic(self, a: Position, b: Position) -> float:
        return abs(a.x - b.x) + abs(a.y - b.y)

    def distance(self, a: Position, b: Position) -> float:
        return abs(a.x - b.x) + abs(a.y - b.y)