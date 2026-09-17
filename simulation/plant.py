class Plant:
    """
    Represents a single potted plant standing in the simulation environment.

    This is one physical houseplant, not a species. The care ranges it should be
    kept in live in the plant_info table, which is global species reference data
    shared by every plant of that species; `species_id` is the link to that row.
    """

    def __init__(self, species_id, x, y, radius=15, name='Unk'):
        """
        Initialize a plant with its species and its position in the environment.

        :param species_id: plant_info.plant_id of this plant's species
        :param x: X position of the pot's centre, in grid cells
        :param y: Y position of the pot's centre, in grid cells
        :param radius: Radius of the pot, in grid cells
        :param name: Optional label for this individual plant, e.g. "kitchen fern"
        """
        self.species_id = species_id
        self.x = x
        self.y = y
        self.radius = radius
        self.name = name

    def get_position(self):
        """
        Get the current position of the plant.

        :return: A tuple (x, y) representing the plant's position
        """
        return (self.x, self.y)

    def set_position(self, x, y):
        """
        Move the plant to a new position.

        The robot relocating a plant is the only thing that should call this.

        :param x: New X position of the pot's centre
        :param y: New Y position of the pot's centre
        """
        self.x = x
        self.y = y
