from pi.robot.robot import Robot

import math

class SimulatedRobot(Robot):
    """
    A simulated robot that can move in a 2D plane.
    """

    def __init__(self):
        self.x = 50
        self.y = 50
        self.orientation = 0 # in degrees, 0 is facing right, 90 is facing up

    def move(self, left_speed, right_speed):
        """
        Move the simulated robot based on the speeds of the left and right motors.

        For equal wheel speeds, the robot moves forward or backward in its current orientation.
        For different wheel speeds, the robots turns in place or along a curved path.

        :param left_speed: Speed of the left motor.
        :param right_speed: Speed of the right motor.
        """
        if left_speed == right_speed:
            distance = left_speed * 0.1
            angle = math.radians(self.orientation)

            self.x += distance * math.cos(angle)
            self.y += distance * math.sin(angle)
        else:
            turn_rate = (right_speed - left_speed) * 0.1
            self.orientation = (self.orientation + turn_rate) % 360

            average_speed = (left_speed + right_speed) / 2
            distance = average_speed * 0.1
            angle = math.radians(self.orientation)

            self.x += distance * math.cos(angle)
            self.y += distance * math.sin(angle)

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