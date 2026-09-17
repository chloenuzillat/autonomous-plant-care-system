from simulation.config import (ROBOT_RADIUS, PLANT_LENGTH, PLANT_INIT_POS, PLANT_SPECIES_ID,
                               USER_PLANT_ID, MOCK_DB_PATH)
from simulation.simulated_robot import SimulatedRobot
from simulation.environment import Environment
from simulation.obstacle import Obstacle
from simulation.plant import Plant
from data.environmental_sensors.store import (init_db, add_plant_info, add_user_plant_log,
                                              read_user_plant_log)
from pathlib import Path
import pygame
import math
import csv

MOCK_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "environmental_sensors" / "mock_data"
MOCK_PLANT_INFO_CSV = MOCK_DATA_DIR / "mock_plant_info.csv"
MOCK_USER_PLANT_LOG_CSV = MOCK_DATA_DIR / "mock_user_plant_log.csv"

# add_plant_info stamps last_updated itself, and rejects outright any record
# carrying a key it does not know, so the CSV's own column has to be dropped.
IGNORED_COLUMNS = {"last_updated"}

# These two columns are keys, not measurements; every other numeric column is a
# reading and belongs in the database as a float.
ID_COLUMNS = {"plant_id", "user_plant_id"}


def load_mock_database(db_path=MOCK_DB_PATH):
    """
    Create the mock sensor database and fill it from the mock CSVs.

    The simulation reads diagnostics straight out of a database, so it needs one
    that exists and has readings in it. This is its own file under
    simulation/mock_db, kept apart from the real database in data/, because
    everything in it was generated rather than measured.

    Safe to call on every run: species rows are upserted, and readings are only
    inserted for plants that have none logged yet, so nothing is duplicated.

    :param db_path: Where the mock database file lives
    """
    init_db(db_path)

    # csv hands back strings for everything, so each field is converted to what
    # its column expects; an empty field means the reading was never taken.
    tables = {}
    for csv_path in (MOCK_PLANT_INFO_CSV, MOCK_USER_PLANT_LOG_CSV):
        rows = []
        with open(csv_path, newline="", encoding="utf-8") as handle:
            for raw_row in csv.DictReader(handle):
                row = {}
                for column, value in raw_row.items():
                    if column in IGNORED_COLUMNS:
                        continue

                    value = (value or "").strip()
                    if not value:
                        row[column] = None
                    elif column in ID_COLUMNS:
                        row[column] = int(value)
                    else:
                        try:
                            row[column] = float(value)
                        except ValueError:
                            row[column] = value
                rows.append(row)
        tables[csv_path] = rows

    for species in tables[MOCK_PLANT_INFO_CSV]:
        add_plant_info(db_path, species)

    readings = tables[MOCK_USER_PLANT_LOG_CSV]

    # Worked out up front, because the first insert would make every later row
    # for that same plant look like it had already been loaded.
    already_loaded = {reading["user_plant_id"] for reading in readings
                      if read_user_plant_log(reading["user_plant_id"], db_path)}

    for reading in readings:
        if reading["user_plant_id"] not in already_loaded:
            add_user_plant_log(db_path, reading)


def format_reading(value, unit, decimals=1):
    """
    Format one sensor reading for the status line.

    Every reading column is nullable, so a plant that was never measured for
    something has to render as a placeholder rather than blowing up on format.

    :param value: The reading, or None if it was never taken
    :param unit: Unit to append
    :param decimals: Decimal places to show
    :return: The formatted reading
    """
    if value is None:
        return f"--{unit}"

    return f"{value:.{decimals}f}{unit}"


def format_status(encoder_data, diagnostics):
    """
    Build the one-line status written under the simulation window.

    Kept to a single short line on purpose: it is rewritten in place with a
    carriage return, which only returns to the start of the current row, so
    anything long enough to wrap would leave pieces of itself behind.

    :param encoder_data: Encoder values from the robot
    :param diagnostics: Latest reading for the touched plant, or {} for none
    :return: The status line
    """
    status = (f"L: {encoder_data['left_encoder']:.2f} | "
              f"R: {encoder_data['right_encoder']:.2f}")

    if not diagnostics:
        return status

    return (f"{status} | plant {diagnostics['user_plant_id']}: "
            f"{format_reading(diagnostics['lux_reading'], ' lux', 0)}, "
            f"{format_reading(diagnostics['temp_reading'], 'C')}, "
            f"{format_reading(diagnostics['humidity_reading'], '% RH', 0)}, "
            f"soil {format_reading(diagnostics['soil_moisture_pct'], '%', 0)}")


def draw_robot(screen, robot):
    """
    Draw the robot and the direction indicator on the given Pygame screen.
    """
    x, y = robot.get_position()
    orientation = robot.get_orientation()

    robot_size = ROBOT_RADIUS
    direction_length = 30

    pygame.draw.circle(screen, (118, 173, 100), (int(x), int(y)), robot_size)

    angle = math.radians(orientation)

    end_x = x + direction_length * math.cos(angle)
    end_y = y - direction_length * math.sin(angle)

    pygame.draw.line(screen, (118, 173, 100), (int(x), int(y)), (int(end_x), int(end_y)), 4)

def draw_plant(screen, plant):
    """
    Draw the plant on the given Pygame screen. 
    """
    x, y = plant.get_position()

    pygame.draw.rect(screen, (0, 255, 0), (x, y, plant.w, plant.h))
    
def draw_obstacle(screen, obstacle):
    """
    Draw the obstacle on the given Pygame screen.
    """
    pygame.draw.rect(screen, (0, 0, 0), (obstacle.x, obstacle.y, obstacle.width, obstacle.height))

def main():
    """
    Main function to run the simulation.
    """
    # Diagnostics are read straight out of the sensor database, so it has to
    # exist and hold readings before the loop runs.
    load_mock_database()

    environment = Environment(800, 600)

    obstacle1 = Obstacle(200, 150, 100, 50)
    obstacle2 = Obstacle(500, 300, 75, 150)

    plant1 = Plant(PLANT_SPECIES_ID[0], PLANT_INIT_POS[0][0], PLANT_INIT_POS[0][1], USER_PLANT_ID[0], PLANT_LENGTH, PLANT_LENGTH)
    plant2 = Plant(PLANT_SPECIES_ID[1], PLANT_INIT_POS[1][0], PLANT_INIT_POS[1][1], USER_PLANT_ID[1], PLANT_LENGTH, PLANT_LENGTH)

    environment.add_obstacle(obstacle1)
    environment.add_obstacle(obstacle2)

    environment.add_plant(plant1)
    environment.add_plant(plant2)

    robot = SimulatedRobot(environment)

    pygame.init()

    screen = pygame.display.set_mode((environment.width, environment.height))
    pygame.display.set_caption("Autonomous Plant Care System")

    clock = pygame.time.Clock()

    running = True

    MOVEMENT_SPEED = 50
    TURN_SPEED = 50

    # Widest status written so far. Every later one is padded out to it, because
    # a carriage return only moves the cursor -- it does not erase what a longer
    # line left on the row.
    status_width = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        left_wheel_speed = 0
        right_wheel_speed = 0

        if keys[pygame.K_w]:
            left_wheel_speed = MOVEMENT_SPEED
            right_wheel_speed = MOVEMENT_SPEED
        elif keys[pygame.K_s]:
            left_wheel_speed = -MOVEMENT_SPEED
            right_wheel_speed = -MOVEMENT_SPEED
        elif keys[pygame.K_a]:
            left_wheel_speed = -TURN_SPEED
            right_wheel_speed = TURN_SPEED
        elif keys[pygame.K_d]:
            left_wheel_speed = TURN_SPEED
            right_wheel_speed = -TURN_SPEED

        robot.move(left_wheel_speed, right_wheel_speed)

        status = format_status(robot.get_encoder_data(), robot.get_diagnostics())
        status_width = max(status_width, len(status))

        print("\r" + status.ljust(status_width), end="", flush=True)

        screen.fill((255, 255, 255))

        for obstacle in environment.get_obstacles():
            draw_obstacle(screen, obstacle)

        for plant in environment.get_plants():
            draw_plant(screen, plant)
        draw_robot(screen, robot)

        pygame.display.flip()

        clock.tick(60)

    # The status line was never terminated, so close it off rather than leaving
    # the shell prompt to land on top of it.
    print()

    pygame.quit()

if __name__ == "__main__":
    main()