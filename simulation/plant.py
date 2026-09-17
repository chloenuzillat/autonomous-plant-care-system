from simulation.config import PLANT_LENGTH, MOCK_DB_PATH
from data.environmental_sensors.store import read_user_plant_log
class Plant:
    """
    Represents a single potted plant standing in the simulation environment.

    This is one physical houseplant, not a species. The care ranges it should be
    kept in live in the plant_info table, which is global species reference data
    shared by every plant of that species; `species_id` is the link to that row.
    """

    def __init__(self, species_id, x, y, user_plant_id, w=PLANT_LENGTH, h=PLANT_LENGTH):
        """
        Initialize a plant with its species and its position in the environment.

        The pot is a rectangle, so it is described by a corner and two side
        lengths rather than a radius.

        :param species_id: plant_info.plant_id of this plant's species
        :param x: X position of the pot's centre, in grid cells
        :param y: Y position of the pot's centre, in grid cells
        :param w: Width of the pot, in grid cells
        :param h: Height of the pot, in grid cells
        :param user_plant_id: User specific plant id
        """
        self.species_id = species_id
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.user_plant_id = user_plant_id

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

    def get_Diagnostics(self) -> dict:
        """
        Get the most recent sensor reading logged for this plant.

        Readings are looked up by user_plant_id, not species_id: the user can own
        several plants of the same species, and this one only wants its own.

        :return: The latest reading as a dict, or {} if this plant has none
        """
        return read_user_plant_log(self.user_plant_id, MOCK_DB_PATH)
    def is_within_bounds(self, x, y) -> None:
        """
        Checks if the given position of plant is within bounds
        
        :param x: X position of pot's centre
        :param y: Y Position of pot's centre
        """
        return (self.w <= x <= self.environment.width - self.w
                and self.h <= y <= self.environment.height - self.h)

