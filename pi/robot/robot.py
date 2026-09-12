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
        # Code to set the motor speeds would go here
        raise NotImplementedError("Motor control not implemented yet.")

    def stop(self):
        """
        Stop the robot by setting both motor speeds to zero.
        """
        raise NotImplementedError("Motor control not implemented yet.")

    def get_position(self):
        """
        Get the current position of the robot.

        :return: A tuple (x, y) representing the robot's position
        """
        raise NotImplementedError("Position tracking not implemented yet.")

    def get_orientation(self):
        """
        Get the current orientation of the robot.

        :return: The orientation angle in degrees
        """
        raise NotImplementedError("Orientation tracking not implemented yet.")