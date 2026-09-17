"""Map geometry for the simulated floor plan. Import this instead of hardcoding sizes.

One source of truth for the world the robot drives in: the simulation renders it
and the database stores positions in it, so both must agree on these numbers.
Units are grid cells (1 cell == 1 pixel on screen), with (0, 0) at the top-left
and y growing downward.

Constants only. The collision maths that uses them lives on SimulatedRobot
(``is_within_bounds`` / ``check_obstacle_collision`` / ``is_reachable``).

Importable from anywhere in the repo, not just the simulation package:

    from simulation.config import GRID_WIDTH, GRID_HEIGHT, ROBOT_RADIUS
"""

from pathlib import Path

# Sensor readings the simulation shows are generated, not measured, so they are
# kept in their own database here rather than mixed into the real one in data/.
MOCK_DB_DIR = Path(__file__).resolve().parent / "mock_db"
MOCK_DB_PATH = MOCK_DB_DIR / "plant_robot.db"

MOCK_DB_DIR.mkdir(parents=True, exist_ok=True)

GRID_WIDTH = 800
GRID_HEIGHT = 600

# The robot is drawn and collision-checked as a circle of this radius, so its
# centre can never be closer than ROBOT_RADIUS to a wall or an obstacle.
ROBOT_RADIUS = 20


# Static obstacles as (x, y, width, height) with (x, y) the top-left corner.
OBSTACLES = [
    (200, 150, 100, 50),
    (500, 300, 75, 150),
]

#Plant is draw as a square
PLANT_LENGTH = 15

PLANT_INIT_POS = [(80,80), (740,540)]

# plant_info.plant_id of the species standing at each PLANT_INIT_POS, in the same
# order: Snake Plant at (80, 80), Sweet Basil at (740, 540). Matches the two-plant
# layout in data/environmental_sensors/mock_data/mock_user_plant_log.csv.
PLANT_SPECIES_ID = [1, 7]
USER_PLANT_ID = [1,2]