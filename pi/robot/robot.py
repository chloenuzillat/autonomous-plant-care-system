class Robot:
    """
    High-level interface for controlling a robot. This class provides methods to move the robot, stop it, and retrieve its position and orientation.
    """

    def move(self, left_speed, right_speed):
        """
        Move the robot by setting the speed of the left and right motors.

        :param left_speed: Speed of the left motor
        :param right_speed: Speed of the right motor
        """

    def stop(self):
        """
        Stop the robot by setting both motor speeds to zero.
        """

    def get_position(self):
        """
        Get the current position of the robot.

        :return: A tuple (x, y) representing the robot's position
        """

    def get_orientation(self):
        """
        Get the current orientation of the robot.

        :return: The orientation angle in degrees
        """

    def get_encoder_data(self):
        """
        Get the encoder data from the sensors.
        """