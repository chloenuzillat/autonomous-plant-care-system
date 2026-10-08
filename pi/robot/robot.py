class Robot:
    """
    High-level interface for controlling a differential-drive robot.
    """

    def move(self, left_speed, right_speed):
        """
        Set the speed of the left and right wheels.

        Positive values move the wheels forward.
        Negative values move the wheels backward.

        :param left_speed: Left wheel speed.
        :param right_speed: Right wheel speed.
        """
        raise NotImplementedError

    def stop(self):
        """
        Stop both wheels.
        """
        raise NotImplementedError

    def get_position(self):
        """
        Get the current robot position.

        :return: (x, y)
        """
        raise NotImplementedError

    def get_orientation(self):
        """
        Get the current robot orientation in degrees.
        """
        raise NotImplementedError

    def get_encoder_data(self):
        """
        Get the current left and right encoder values.
        """
        raise NotImplementedError