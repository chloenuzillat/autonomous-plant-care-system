class Environment:
    """
    Represents the simulation environment with specified dimensions.
    """

    def __init__(self, width, height):
        """
        Initialize the environment with a given width and height.

        :param width: Width of the environment
        :param height: Height of the environment
        """
        self.width = width
        self.height = height