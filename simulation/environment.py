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
        self.obstacles = []  # List to hold obstacles in the environment

    def add_obstacle(self, obstacle):
        """
        Add an obstacle to the environment.

        :param obstacle: An instance of the Obstacle class
        """
        self.obstacles.append(obstacle)

    def get_obstacles(self):
        """
        Get the list of obstacles in the environment.

        :return: List of obstacles
        """
        return self.obstacles