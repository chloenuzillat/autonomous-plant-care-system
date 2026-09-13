from pi.robot.robot import Robot

import math

class SimulatedRobot(Robot):
    """
    A simulated robot that can move in a 2D plane.
    """

    def __init__(self, environment):
        self.environment = environment
        self.x = environment.width / 2
        self.y = environment.height / 2
        self.orientation = 0 # in degrees, 0 is facing right, 90 is facing up
        self.left_encoder = 0
        self.right_encoder = 0

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

            new_x = self.x + distance * math.cos(angle)
            new_y = self.y - distance * math.sin(angle)

            if self.is_within_bounds(new_x, new_y) and not self.check_obstacle_collision(new_x, new_y):
                self.x = new_x
                self.y = new_y

                self.left_encoder += left_speed * 0.1
                self.right_encoder += right_speed * 0.1
        else:
            turn_rate = (right_speed - left_speed) * 0.1
            self.orientation = (self.orientation + turn_rate) % 360

            average_speed = (left_speed + right_speed) / 2
            distance = average_speed * 0.1
            angle = math.radians(self.orientation)

            new_x = self.x + distance * math.cos(angle)
            new_y = self.y - distance * math.sin(angle)

            if self.is_within_bounds(new_x, new_y) and not self.check_obstacle_collision(new_x, new_y):
                self.x = new_x
                self.y = new_y

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
    
    def is_within_bounds(self, x, y):
        """
        Check if the robot is within the bounds of the environment.
        """
        radius = 20
        return (radius <= x <= self.environment.width - radius and radius <= y <= self.environment.height - radius)

    def check_obstacle_collision(self, x, y):
        """
        Check if the robot collides with any obstacles in the environment.
        """
        radius = 20

        for obstacle in self.environment.get_obstacles():
            closest_x = max(obstacle.x, min(x, obstacle.x + obstacle.width))
            closest_y = max(obstacle.y, min(y, obstacle.y + obstacle.height))

            distance_x = x - closest_x
            distance_y = y - closest_y
            distance_squared = distance_x ** 2 + distance_y ** 2

            if distance_squared < radius ** 2:
                return True
        return False

    def get_encoder_data(self):
        """
        Get the encoder data for the left and right wheels.

        :return: A dictionary with the encoder values
        """
        return {"left_encoder": self.left_encoder, "right_encoder": self.right_encoder}