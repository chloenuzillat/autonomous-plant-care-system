from simulation.config import GRID_WIDTH, GRID_HEIGHT


class Environment:
    """
    Represents the simulation environment with specified dimensions.
    """

    def __init__(self, width=GRID_WIDTH, height=GRID_HEIGHT):
        """
        Initialize the environment with a given width and height.

        Defaults come from simulation/config.py so the environment, the renderer
        and anything reasoning about positions describe the same floor plan.

        :param width: Width of the environment
        :param height: Height of the environment
        """
        self.width = width
        self.height = height
        self.obstacles = []  # List to hold obstacles in the environment
        self.plants = []  # List to hold plants in the environment

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

    def add_plant(self, plant):
        """
        Add a plant to the environment.

        :param plant: An instance of the Plant class
        """
        self.plants.append(plant)

    def get_plants(self):
        """
        Get the list of plants in the environment.

        :return: List of plants
        """
        return self.plants
