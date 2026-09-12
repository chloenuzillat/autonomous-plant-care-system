from pi.robot import Robot

class SimulatedRobot(Robot):
    """
    A simulated robot that can move in a 2D plane.
    """

    def __init__(self):
        self.x = 0
        self.y = 0
        self.orientation = 0 # in degrees, 0 is facing right, 90 is facing up

    def get_position(self):
        """
        Get the current position of the simulated robot.

        :return: A tuple (x, y) representing the robot's position
        """
        return (self.x, self.y)

    def get_orientation(self):
        """
        Get the current orientation of the simulated robot.

        :return: The orientation angle in degrees
        """
        return self.orientation