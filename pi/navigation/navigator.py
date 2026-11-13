import math
import time

from pi.navigation.map import Map, Position
from pi.navigation.path_planner import PathPlanner
from pi.robot.robot import Robot

class Navigator:
    def __init__(self, robot: Robot, map: Map):
        self.robot = robot
        self.map = map
        self.planner = PathPlanner(map)

        self.forward_speed = 40
        self.turn_speed = 30
        self.position_tolerance = 0.2
        self.angle_tolerance = 5
        self.update_interval = 0.1

    def navigate_to(self, target: Position):
        x, y = self.robot.get_position()

        start = self.map.world_to_cell(x, y)

        path = self.planner.find_path(start, target)

        if not path:
            self.robot.stop()
            return False

        try:
            for waypoint in path[1:]:
                if not self.move_to_waypoint(waypoint):
                    return False
        finally:
            self.robot.stop()

        return True

    def move_to_waypoint(self, waypoint: Position) -> bool:
        target_x, target_y = self.map.cell_to_world(waypoint)
        start_time = time.monotonic()
        timeout = 30.0

        while time.monotonic() - start_time < timeout:
            x, y = self.robot.get_position()

            dx = target_x - x
            dy = target_y - y

            distance = math.hypot(dx, dy)

            if distance <= self.position_tolerance:
                self.robot.stop()
                return True

            desired_heading = math.degrees(math.atan2(dy, dx))
            current_heading = self.robot.get_orientation()

            angle_error = (
                                  (desired_heading - current_heading + 180) % 360
                          ) - 180

            if abs(angle_error) > self.angle_tolerance:
                if angle_error > 0:
                    self.robot.move(self.turn_speed, -self.turn_speed)
                else:
                    self.robot.move(-self.turn_speed, self.turn_speed)
            else:
                self.robot.move(
                    self.forward_speed,
                    self.forward_speed
                )

            time.sleep(self.update_interval)

        self.robot.stop()
        return False