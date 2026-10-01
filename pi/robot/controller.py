from pi.robot.robot import Robot

class RobotController:
    """
    High-level controller for robot movement.

    Translates movement commands into differential wheel speeds
    and delegates the actual movement to a Robot implementation.
    """

    MAX_SPEED = 100

    def __init__(self, robot: Robot):
        self.robot = robot

    def forward(self, speed: float):
        """Move forward at the given speed."""
        speed = self._clamp_speed(speed)
        self.robot.move(speed, speed)

    def backward(self, speed: float):
        """Move backward at the given speed."""
        speed = self._clamp_speed(speed)
        self.robot.move(-speed, -speed)

    def turn_left(self, speed: float):
        """Turn left in place at the given speed."""
        speed = self._clamp_speed(speed)
        self.robot.move(-speed, speed)

    def turn_right(self, speed: float):
        """Turn right in place at the given speed."""
        speed = self._clamp_speed(speed)
        self.robot.move(speed, -speed)

    def stop(self):
        """Stop the robot."""
        self.robot.stop()

    def _clamp_speed(self, speed: float) -> float:
        """Keep speed within the allowed range."""
        return max(-self.MAX_SPEED, min(self.MAX_SPEED, speed))