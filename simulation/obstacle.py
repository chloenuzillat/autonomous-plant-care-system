class Obstacle:
    """
    Represents an obstacle in the simulation environment.
    """
    
    def __init__(self, x, y, width, height):
        """
        Initialize an obstacle with its position and size.
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height