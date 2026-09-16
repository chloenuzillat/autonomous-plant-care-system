from simulation.config import ROBOT_RADIUS
from simulation.simulated_robot import SimulatedRobot
from simulation.environment import Environment
from simulation.obstacle import Obstacle
import pygame
import math

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

def draw_obstacle(screen, obstacle):
    """
    Draw the obstacle on the given Pygame screen.
    """
    pygame.draw.rect(screen, (0, 0, 0), (obstacle.x, obstacle.y, obstacle.width, obstacle.height))

def main():
    """
    Main function to run the simulation.
    """
    environment = Environment(800, 600)

    obstacle1 = Obstacle(200, 150, 100, 50)
    obstacle2 = Obstacle(500, 300, 75, 150)

    environment.add_obstacle(obstacle1)
    environment.add_obstacle(obstacle2)

    robot = SimulatedRobot(environment)

    pygame.init()

    screen = pygame.display.set_mode((environment.width, environment.height))
    pygame.display.set_caption("Autonomous Plant Care System")

    clock = pygame.time.Clock()

    running = True

    MOVEMENT_SPEED = 50
    TURN_SPEED = 50

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

        encoder_data = robot.get_encoder_data()

        print(
            f"\rLeft encoder: {encoder_data['left_encoder']:.2f} | "
            f"Right encoder: {encoder_data['right_encoder']:.2f}",
            end="",
            flush=True
        )

        screen.fill((255, 255, 255))

        for obstacle in environment.get_obstacles():
            draw_obstacle(screen, obstacle)

        draw_robot(screen, robot)

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()