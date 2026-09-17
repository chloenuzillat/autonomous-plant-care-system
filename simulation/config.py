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
PLANT_LENGTH = 10

PLANT_INIT_POS = [(80,80), (740,540)]