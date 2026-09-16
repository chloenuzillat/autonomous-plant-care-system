from simulation.config import GRID_WIDTH, GRID_HEIGHT, OBSTACLES
from simulation.obstacle import Obstacle


class Environment:
    """
    Represents the simulation environment with specified dimensions.
    """

    def __init__(self, width=GRID_WIDTH, height=GRID_HEIGHT, obstacles=None):
        """
        Initialize the environment with a given width and height.

        Defaults come from simulation/config.py so the environment, the renderer
        and the stored plant positions all describe the same floor plan.

        :param width: Width of the environment
        :param height: Height of the environment
        :param obstacles: Obstacle instances to start with, or None for the
                          default layout from config.OBSTACLES
        """
        self.width = width
        self.height = height
        self.obstacles = []  # List to hold obstacles in the environment

        if obstacles is None:
            obstacles = [Obstacle(x, y, obstacle_width, obstacle_height)
                         for x, y, obstacle_width, obstacle_height in OBSTACLES]

        for obstacle in obstacles:
            self.add_obstacle(obstacle)

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
